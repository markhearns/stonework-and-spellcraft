from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, migrate_state
from server import GameStore

class ExpansionTests(unittest.TestCase):
    def setUp(self): self.state=new_campaign()
    def act(self, kind, **fields): return apply_action(self.state, {'type':kind,**fields})
    def restore(self):
        self.act('start-restoration')
        for _ in range(3): self.act('advance')
    def research(self):
        self.act('start-research')
        for _ in range(3): self.act('advance')
    def test_restore_gate_cost_pause_and_no_duplicate_spend(self):
        with self.assertRaises(RuleError): self.act('select-room',roomId='conservatory')
        self.act('start-restoration')
        self.assertEqual(self.state['sharedFunds'],55)
        with self.assertRaises(RuleError): self.act('start-restoration')
        self.act('advance')
        self.act('assign-founder',assignment='rest')
        self.act('advance')
        self.assertEqual(self.state['restorationCompletedPhases'],1)
        self.act('assign-founder',assignment='restoration')
        self.act('advance');self.act('advance')
        self.assertEqual(self.state['restorationStatus'],'complete')
        self.act('select-room',roomId='conservatory')
        self.assertIn('conservatory',public_state(self.state)['availableRoomIds'])
    def test_single_assignment_and_collaborative_research(self):
        self.act('start-research');self.act('start-restoration')
        self.act('assign-resident',assignment='archive')
        self.act('advance')
        self.assertEqual(self.state['researchCompletedPhases'],1)
        self.assertEqual(self.state['restorationCompletedPhases'],1)
        self.act('assign-founder',assignment='research');self.act('advance')
        self.assertEqual(self.state['researchStatus'],'complete')
        self.assertEqual(self.state['restorationCompletedPhases'],1)
    def test_garden_no_offline_no_unstaffed_no_inventory_sale(self):
        self.restore()
        self.act('advance')
        self.assertEqual(self.state['materialInventory']['silver-ivy'],0)
        self.act('assign-resident',assignment='garden')
        self.act('advance')
        self.assertEqual(self.state['materialInventory']['silver-ivy'],1)
        before=self.state['sharedFunds']
        self.act('garden-production',choice='surplus-sales')
        self.assertEqual(self.state['sharedFunds'],before)
        self.act('advance')
        self.assertEqual(self.state['sharedFunds'],before+4)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],1)
        self.assertEqual(public_state(self.state)['residentRoomId'],'conservatory')
    def test_crafting_properties_material_consumption_and_completion(self):
        with self.assertRaises(RuleError): self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        self.research()
        self.act('buy-material',materialId='fireglass');self.act('buy-material',materialId='silver-ivy')
        with self.assertRaises(RuleError): self.act('start-crafting',recipeId='warming-lantern',materials=['binding-thread','sun-amber'])
        self.act('start-crafting',recipeId='warming-lantern',materials=['fireglass','silver-ivy'])
        self.assertEqual(self.state['materialInventory']['fireglass'],0)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],0)
        with self.assertRaises(RuleError): self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        self.act('advance');self.act('assign-founder',assignment='rest');self.act('advance')
        self.assertEqual(self.state['craftingProject']['completedWorkPhases'],1)
        self.act('assign-founder',assignment='crafting');self.act('advance')
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
        self.act('display-lantern',displayed=True)
        self.assertTrue(self.state['lanternDisplayed'])
        self.act('advance')
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
    def test_purchases_are_reversible(self):
        before=self.state['sharedFunds']
        self.act('buy-material',materialId='fireglass')
        self.act('sell-material',materialId='fireglass')
        self.assertEqual(self.state['sharedFunds'],before)
        with self.assertRaises(RuleError): self.act('sell-material',materialId='fireglass')
    def test_migration_backup_retains_existing_choices(self):
        state=new_campaign()
        new_fields=['founderAssignment','residentAssignment','restorationStatus','restorationCompletedPhases','restorationRequiredPhases','gardenProductionChoice','materialInventory','craftingProject','craftedArtifacts','lanternDisplayed','lastPhaseSummary']
        for name in new_fields: state.pop(name)
        state['schemaVersion']=1;state['revision']=12
        state['roomFurnishings'].pop('conservatory')
        state['wardrobe']['outerLayer']='plum-shawl'
        state['researchStatus']='in-progress';state['researchCompletedPhases']=1
        state['resonancePoints']=7
        with tempfile.TemporaryDirectory() as directory:
            db_path=Path(directory)/'campaign.sqlite3'
            with sqlite3.connect(db_path) as db:
                db.execute('CREATE TABLE campaign (id INTEGER PRIMARY KEY, state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES (1,?)',(json.dumps(state),))
            store=GameStore(directory)
            upgraded=store.read()
            self.assertEqual(upgraded['schemaVersion'],66)
            self.assertEqual(upgraded['revision'],13)
            self.assertEqual(upgraded['founderAssignment'],'research')
            self.assertEqual(upgraded['wardrobe'],state['wardrobe'])
            self.assertEqual(upgraded['resonancePoints'],7)
            backup_path=Path(directory)/f"campaign-before-schema-1-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3"
            with sqlite3.connect(backup_path) as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign').fetchone()[0]),state)
            self.assertEqual(GameStore(directory).read(),upgraded)
    def test_rejected_crafting_is_atomic_in_store(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            before=store.read()
            with self.assertRaises(RuleError):
                store.action({'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'start-crafting','recipeId':'warming-lantern','materials':['sun-amber','binding-thread']}})
            self.assertEqual(store.read(),before)
