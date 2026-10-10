import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from game import new_campaign, apply_action, RuleError, public_state
from server import GameStore

class ExpeditionTests(unittest.TestCase):
    def setUp(self): self.state=new_campaign()
    def act(self,kind,**fields): return apply_action(self.state,{'type':kind,**fields})
    def arrive(self,lantern=False):
        self.act('start-expedition',carryLantern=lantern);self.act('advance')
    def finish_visit(self,approach,lantern=False):
        self.arrive(lantern)
        self.act('choose-expedition-approach',approach=approach)
        while self.state['expedition']['stage']=='working': self.act('advance')
        self.act('return-expedition');self.act('advance')
    def test_choice_gate_and_no_reward_until_return(self):
        self.arrive()
        with self.assertRaises(RuleError): self.act('advance')
        self.act('choose-expedition-approach',approach='survey')
        self.act('advance')
        self.assertEqual(self.state['expedition']['remainingWorkPhases'],1)
        self.act('advance')
        self.assertNotIn('water-guidance',self.state['archivePrinciples'])
        self.act('return-expedition');self.act('advance')
        self.assertIsNone(self.state['expedition'])
        self.assertIn('water-guidance',self.state['archivePrinciples'])
        self.assertIn('water-guidance',self.state['founderKnownPrinciples'])
    def test_lantern_shortens_work_and_returns_to_display(self):
        self.state['craftedArtifacts']['warming-lantern']=1
        self.state['lanternDisplayed']=True
        self.arrive(True)
        self.assertFalse(self.state['lanternDisplayed'])
        with self.assertRaises(RuleError): self.act('display-lantern',displayed=True)
        self.act('choose-expedition-approach',approach='survey')
        self.assertEqual(self.state['expedition']['remainingWorkPhases'],1)
        self.act('advance');self.act('return-expedition');self.act('advance')
        self.assertTrue(self.state['lanternDisplayed'])
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
    def test_early_return_retains_lead_and_grants_nothing(self):
        self.arrive();self.act('choose-expedition-approach',approach='survey')
        self.act('advance');self.act('return-expedition');self.act('advance')
        self.assertEqual(self.state['waterworksDiscoveries'],[])
        self.assertEqual(self.state['archivePrinciples'],[])
        self.finish_visit('survey')
        self.assertEqual(self.state['waterworksDiscoveries'],['survey'])
    def test_revisit_remaining_lead_without_farming(self):
        self.finish_visit('salvage')
        self.assertEqual(self.state['sharedFunds'],88)
        self.assertEqual(self.state['materialInventory']['fireglass'],2)
        self.arrive()
        with self.assertRaises(RuleError): self.act('choose-expedition-approach',approach='salvage')
        self.act('choose-expedition-approach',approach='survey')
        self.act('advance');self.act('advance');self.act('return-expedition');self.act('advance')
        self.assertEqual(self.state['sharedFunds'],88)
        with self.assertRaises(RuleError): self.act('start-expedition')
        with self.assertRaises(RuleError): self.act('return-expedition')
    def test_absence_blocks_in_person_actions_but_resident_work_continues(self):
        self.act('start-research');self.act('assign-resident',assignment='archive')
        self.act('start-expedition')
        for action in ['start-restoration','start-research','start-crafting','assign-founder','accept-invitation','talk','free-text']:
            with self.assertRaises(RuleError): self.act(action)
        self.act('advance');self.act('choose-expedition-approach',approach='survey')
        self.act('advance');self.act('advance')
        self.assertEqual(self.state['researchStatus'],'complete')
        self.assertIn('steady-hearth-wards',self.state['archivePrinciples'])
        self.assertNotIn('steady-hearth-wards',self.state['founderKnownPrinciples'])
        self.act('return-expedition');self.act('advance')
        self.assertIn('steady-hearth-wards',self.state['founderKnownPrinciples'])
    def test_discovery_crafting_installation_changes_actual_garden_yield(self):
        self.finish_visit('survey')
        self.act('buy-material',materialId='porous-clay')
        self.act('start-crafting',recipeId='watering-charm',materials=['porous-clay','binding-thread'])
        self.act('advance');self.act('advance')
        with self.assertRaises(RuleError): self.act('install-watering-charm',installed=True)
        self.act('start-restoration')
        for _ in range(3):self.act('advance')
        self.act('install-watering-charm',installed=True)
        self.act('assign-resident',assignment='garden');self.act('advance')
        self.assertEqual(self.state['materialInventory']['silver-ivy'],2)
        self.act('garden-production',choice='surplus-sales')
        before=self.state['sharedFunds'];self.act('advance')
        self.assertEqual(self.state['sharedFunds'],before+6)
        self.act('install-watering-charm',installed=False)
        before=self.state['sharedFunds'];self.act('advance')
        self.assertEqual(self.state['sharedFunds'],before+4)
    def test_schema_two_migration_preserves_materials_and_research(self):
        state=new_campaign()
        for field in ('expedition','waterworksDiscoveries','lastExpeditionReport','founderKnownPrinciples','archivePrinciples','wateringCharmInstalled'):
            state.pop(field)
        state['schemaVersion']=2
        state['materialInventory'].pop('porous-clay')
        state['materialInventory']['sun-amber']=9
        state['researchStatus']='complete';state['researchCompletedPhases']=3
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(state),))
            upgraded=GameStore(directory).read()
            self.assertEqual(upgraded['schemaVersion'],66)
            self.assertEqual(upgraded['materialInventory']['sun-amber'],9)
            self.assertIn('steady-hearth-wards',upgraded['founderKnownPrinciples'])
            self.assertTrue((Path(directory)/f"campaign-before-schema-2-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").is_file())
            self.assertEqual(upgraded,GameStore(directory).read())
