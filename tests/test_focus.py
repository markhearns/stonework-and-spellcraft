from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, learn_for_character, RuleError, research_work, crafting_work, copying_income
from server import GameStore

class FocusTests(unittest.TestCase):
    def setUp(self): self.state=new_campaign()
    def act(self,kind,**fields): return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count): self.act('advance')
    def supplies(self):
        self.state['sharedFunds']=200
        for key in self.state['materialInventory']: self.state['materialInventory'][key]=10
        for who in ('founder','mira'):
            for principle in ('steady-hearth-wards','reference-binding','gentle-preservation','luminous-copying'):
                learn_for_character(self.state,who,principle)
    def inscribe(self,inscription,who='founder'):
        choices={'steady-hand':['sun-amber','binding-thread'],'scholarly-thread':['binding-thread','porous-clay'],'field-case':['porous-clay','binding-thread'],'copying-line':['porous-clay','sun-amber']}
        self.act('start-focus-inscription',characterId=who,inscriptionId=inscription,materials=choices[inscription]);self.advance(2)
    def prepare(self,inscriptions,who='founder',context='household'):
        self.act('configure-focus',characterId=who,context=context,inscriptions=inscriptions)

    def test_personal_knowledge_cost_validation_and_pause(self):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('start-focus-inscription',characterId='mira',inscriptionId='steady-hand',materials=['sun-amber','binding-thread'])
        self.assertEqual(self.state,before)
        self.supplies();before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('start-focus-inscription',characterId='mira',inscriptionId='steady-hand',materials=['binding-thread','porous-clay'])
        self.assertEqual(self.state,before)
        self.act('start-focus-inscription',characterId='mira',inscriptionId='steady-hand',materials=['sun-amber','binding-thread'])
        self.assertEqual(self.state['sharedFunds'],194)
        self.assertEqual(self.state['materialInventory']['sun-amber'],9)
        self.advance(); self.act('assign-resident',assignment='rest'); self.advance(3)
        self.assertEqual(self.state['focusProjects']['mira']['completedWorkPhases'],1)
        self.act('assign-resident',assignment='inscribing');self.advance()
        self.assertEqual(self.state['signatureFocuses']['mira']['inscriptions'],['steady-hand'])
        self.assertEqual(self.state['signatureFocuses']['mira']['householdLoadout'],[])
        self.assertEqual(self.state['characterDevelopment']['mira']['advancementAwards'],{})
        with self.assertRaises(RuleError): self.act('start-focus-inscription',characterId='mira',inscriptionId='steady-hand',materials=['sun-amber','binding-thread'])

    def test_upgrade_duplicate_components_capacity_and_configurations(self):
        self.supplies();self.inscribe('steady-hand');self.inscribe('scholarly-thread');self.inscribe('field-case')
        self.prepare(['steady-hand'])
        for selected in (['steady-hand','scholarly-thread'],['steady-hand','steady-hand'],['bogus']):
            with self.assertRaises(RuleError): self.prepare(selected)
        self.state['materialInventory']['porous-clay']=1
        before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('upgrade-focus',characterId='founder',materials=['porous-clay','porous-clay'])
        self.assertEqual(self.state,before)
        self.state['materialInventory']['porous-clay']=2
        funds=self.state['sharedFunds'];self.act('upgrade-focus',characterId='founder',materials=['porous-clay','porous-clay'])
        self.assertEqual(self.state['sharedFunds'],funds-18);self.advance(3)
        self.assertEqual(self.state['signatureFocuses']['founder']['capacity'],2)
        self.prepare(['steady-hand','scholarly-thread']);self.prepare(['field-case'],context='expedition')
        self.assertEqual(self.state['signatureFocuses']['founder']['householdLoadout'],['steady-hand','scholarly-thread'])
        with self.assertRaises(RuleError): self.act('upgrade-focus',characterId='founder',materials=['moon-glass','moon-glass'])
        self.act('start-expedition')
        before=deepcopy(self.state)
        for kind,fields in [('configure-focus',{'context':'household','inscriptions':[]}),('rename-focus',{'name':'Changed'}),('upgrade-focus',{'materials':['moon-glass','moon-glass']})]:
            with self.assertRaises(RuleError): self.act(kind,characterId='founder',**fields)
            self.assertEqual(self.state,before)

    def test_bonuses_match_assignments_and_do_not_accelerate_inscription(self):
        self.supplies();self.inscribe('steady-hand');self.prepare(['steady-hand'])
        self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        self.assertEqual(crafting_work(self.state),2);self.advance()
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
        self.inscribe('scholarly-thread');self.prepare(['scholarly-thread'])
        self.act('start-research');self.assertEqual(research_work(self.state),2)
        self.advance();self.assertEqual(self.state['researchCompletedPhases'],2)
        self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(self.state['researchCompletedPhases'],2)
        self.act('start-focus-inscription',characterId='founder',inscriptionId='copying-line',materials=['porous-clay','sun-amber'])
        self.advance();self.assertIsNotNone(self.state['focusProjects']['founder'])
        self.advance();self.prepare(['copying-line'])
        self.assertEqual(copying_income(self.state),6)
        before=self.state['sharedFunds'];self.advance();self.assertEqual(self.state['sharedFunds'],before)
        self.act('assign-founder',assignment='commissions');self.advance();self.assertEqual(self.state['sharedFunds'],before+6)

    def test_party_preservation_bonus_only_on_new_salvage_return_no_stack(self):
        self.supplies();self.state['miraArchiveProject']['status']='complete'
        for who in ('founder','mira'):
            self.inscribe('field-case',who);self.prepare(['field-case'],who,context='expedition')
        before=self.state['materialInventory']['binding-thread']
        self.act('start-expedition',companionId='mira');self.advance();self.act('choose-expedition-approach',approach='salvage');self.advance()
        self.assertEqual(self.state['materialInventory']['binding-thread'],before)
        self.act('return-expedition');self.advance()
        self.assertEqual(self.state['materialInventory']['binding-thread'],before+1)
        self.act('start-expedition',companionId='mira');self.advance();self.act('choose-expedition-approach',approach='survey');self.advance(2)
        self.act('return-expedition');self.advance()
        self.assertEqual(self.state['materialInventory']['binding-thread'],before+1)
        self.assertEqual(self.state['signatureFocuses']['mira']['expeditionLoadout'],['field-case'])

    def test_absence_pauses_focus_and_prevents_remote_mira_changes(self):
        self.supplies();self.state['miraArchiveProject']['status']='complete'
        self.act('start-focus-inscription',characterId='mira',inscriptionId='steady-hand',materials=['sun-amber','binding-thread'])
        self.advance();self.act('start-expedition',companionId='mira');self.advance()
        self.assertEqual(self.state['focusProjects']['mira']['completedWorkPhases'],1)
        with self.assertRaises(RuleError): self.act('rename-focus',characterId='mira',name='Changed')
        self.act('return-expedition');self.advance()
        self.assertEqual(self.state['residentAssignment'],'rest')
        self.act('assign-resident',assignment='inscribing');self.advance()
        self.assertIn('steady-hand',self.state['signatureFocuses']['mira']['inscriptions'])

    def test_schema_seven_migration_and_focus_retry(self):
        self.supplies();old=deepcopy(self.state)
        old['schemaVersion']=7;old.pop('signatureFocuses');old.pop('focusProjects')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);upgraded=store.read()
            for key in old:
                if key not in ('schemaVersion','revision'):self.assertEqual(upgraded[key],old[key],key)
            self.assertTrue((Path(directory)/f"campaign-before-schema-7-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':upgraded['revision'],'action':{'type':'start-focus-inscription','characterId':'founder','inscriptionId':'steady-hand','materials':['sun-amber','binding-thread']}}
            first=store.action(payload);self.assertEqual(store.action(payload),first)
            self.assertEqual(first['sharedFunds'],194)
            self.assertEqual(GameStore(directory).read(),first)
            self.assertEqual(public_state(first)['focusViews']['founder']['project']['completedWorkPhases'],0)
