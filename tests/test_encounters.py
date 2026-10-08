from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, learn_for_character, copying_income
from server import GameStore

class EncounterTests(unittest.TestCase):
    def setUp(self): self.state=new_campaign()
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count):self.act('advance')
    def unlock(self):self.state['binderyDiscoveries']=['survey']
    def arrive(self,approach='survey',**fields):
        self.act('start-expedition',siteId='rainward-observatory',**fields);self.advance();self.act('choose-expedition-approach',approach=approach)
    def method(self,key):
        self.act('choose-encounter-method',methodId=key)
        while self.state['expedition']['stage']=='working':self.advance()
    def return_home(self):self.act('return-expedition');self.advance()
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def finish_manual(self):
        for key in ('drain-by-hand','clean-lenses','copy-ledger'):self.method(key)
    def test_route_unlock_decisions_and_return_only_knowledge(self):
        self.reject('start-expedition',siteId='rainward-observatory')
        self.unlock();self.arrive();self.reject('advance');self.reject('choose-encounter-method',methodId='copy-ledger')
        before=deepcopy(self.state['materialInventory']);self.finish_manual()
        self.assertNotIn('gentle-refraction',self.state['archivePrinciples']);self.assertEqual(self.state['materialInventory'],before)
        self.return_home();self.assertIn('gentle-refraction',self.state['founderKnownPrinciples'])
        self.assertNotIn('gentle-refraction',self.state['residentKnownPrinciples'])
        self.assertEqual(self.state['characterDevelopment']['founder']['advancementAwards']['rainward-observatory:survey']['points'],2)
        self.arrive('salvage');self.finish_manual();self.return_home()
        self.assertEqual(self.state['observatoryDiscoveries'],['survey','salvage']);self.reject('start-expedition',siteId='rainward-observatory')
    def test_early_return_preserves_partial_work_without_reward(self):
        self.unlock();self.arrive();self.act('choose-encounter-method',methodId='drain-by-hand');self.advance()
        progress=deepcopy(self.state['observatoryProgress']['survey']);funds=self.state['sharedFunds'];inventory=deepcopy(self.state['materialInventory'])
        self.return_home();self.assertEqual(self.state['observatoryProgress']['survey'],progress)
        self.assertEqual(self.state['sharedFunds'],funds);self.assertEqual(self.state['materialInventory'],inventory)
        self.arrive();self.assertEqual(self.state['expedition']['stage'],'working');self.assertEqual(self.state['expedition']['remainingWorkPhases'],1)
        self.advance();self.assertEqual(self.state['observatoryProgress']['survey']['completedSteps'],['rain-shutter'])
        self.method('clean-lenses');self.return_home();self.arrive();self.assertEqual(public_state(self.state)['encounterView']['step']['id'],'weather-notes')
    def test_capabilities_require_party_presence_and_personal_understanding(self):
        self.unlock();learn_for_character(self.state,'mira','water-guidance');self.arrive()
        self.reject('choose-encounter-method',methodId='guide-water')
        self.return_home();self.state['miraArchiveProject']['status']='complete';self.arrive(companionId='mira')
        self.act('choose-encounter-method',methodId='guide-water');self.assertEqual(self.state['expedition']['remainingWorkPhases'],1);self.advance()
        self.reject('choose-encounter-method',methodId='warm-lenses')
        self.method('clean-lenses');self.reject('choose-encounter-method',methodId='use-field-notes')
        self.method('copy-ledger');self.return_home()
        self.assertIn('gentle-refraction',self.state['residentKnownPrinciples'])
    def test_packed_lantern_and_prepared_field_notes_are_actual_requirements(self):
        self.unlock();self.state['craftedArtifacts']['warming-lantern']=1;self.state['lanternDisplayed']=True
        self.state['characterDevelopment']['founder']['learnedPractices'].append('field-notes')
        self.state['characterDevelopment']['founder']['preparedPractices'].append('field-notes')
        self.arrive(carryLantern=True);self.method('drain-by-hand');self.method('warm-lenses');self.method('use-field-notes')
        self.assertFalse(self.state['lanternDisplayed']);self.return_home();self.assertTrue(self.state['lanternDisplayed'])
    def test_optional_complication_is_recoverable_and_extra_lens_awards_once(self):
        self.unlock();self.arrive();self.method('drain-by-hand');self.method('open-auxiliary')
        self.assertEqual(self.state['observatoryProgress']['survey']['complication'],'misaligned-rack')
        self.reject('choose-encounter-method',methodId='copy-ledger')
        inventory=deepcopy(self.state['materialInventory']);self.return_home();self.assertEqual(self.state['materialInventory'],inventory)
        learn_for_character(self.state,'founder','gentle-preservation');self.arrive();self.method('preserve-alignment')
        self.assertIsNone(self.state['observatoryProgress']['survey']['complication'])
        self.method('copy-ledger');self.return_home();self.assertEqual(self.state['materialInventory']['moon-glass'],inventory['moon-glass']+1)
        self.act('start-expedition',siteId='rainward-observatory');self.advance();self.reject('choose-expedition-approach',approach='survey')
    def test_switching_leads_keeps_independent_checkpoints(self):
        self.unlock();self.arrive();self.method('drain-by-hand');self.return_home();self.arrive('salvage')
        self.assertEqual(public_state(self.state)['encounterView']['step']['id'],'rain-shutter')
        self.method('drain-by-hand');self.method('open-auxiliary');self.method('align-by-hand');self.method('copy-ledger')
        self.return_home();self.assertEqual(self.state['sharedFunds'],104)
        self.assertEqual(self.state['materialInventory']['moon-glass'],4)
        self.arrive('survey');self.assertEqual(public_state(self.state)['encounterView']['step']['id'],'lens-rack')
    def test_returned_discovery_unlocks_recipe_and_spell_with_personal_knowledge(self):
        self.unlock();self.arrive();self.finish_manual();self.return_home()
        self.state['materialInventory']['moon-glass']=4;self.state['materialInventory']['fireglass']=2
        self.act('start-crafting',recipeId='reading-prism',materials=['moon-glass','fireglass'],crafterId='founder')
        while self.state['craftingProject']:self.advance()
        before=copying_income(self.state);self.act('place-utility-artifact',artifactId='reading-prism',installed=True)
        self.assertEqual(copying_income(self.state),before+2)
        self.act('draft-spell',characterId='founder',formId='clarify-glass',name='Clean light',intent='Clarify glass',materials=['moon-glass','moon-glass'])
        key=self.state['spellbook'][-1]['id'];self.act('test-spell',spellId=key);self.advance(2)
        self.act('prepare-spells',characterId='founder',spellIds=[key]);before=self.state['materialInventory']['moon-glass']
        self.act('cast-spell',spellId=key);self.advance();self.assertEqual(self.state['materialInventory']['moon-glass'],before+2)
    def test_schema_ten_migration_and_encounter_retry_reload(self):
        self.unlock();old=deepcopy(self.state);old['schemaVersion']=10
        for key in ('observatoryDiscoveries','observatoryProgress'):old.pop(key)
        old['utilityArtifactPlacements'].pop('reading-prism')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory)
            self.assertTrue((Path(directory)/'campaign-before-schema-10-to-66.sqlite3').exists())
            def call(kind,**fields):return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind,**fields}})
            call('start-expedition',siteId='rainward-observatory');call('advance');call('choose-expedition-approach',approach='survey')
            request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'choose-encounter-method','methodId':'drain-by-hand'}}
            first=store.action(request);self.assertEqual(store.action(request),first);call('advance')
            self.assertEqual(GameStore(directory).read()['observatoryProgress']['survey']['pendingWork']['remainingWorkPhases'],1)

if __name__=='__main__':unittest.main()
