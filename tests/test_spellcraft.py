from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, learn_for_character, RuleError, resident_room, SPELL_FORMS
from server import GameStore

class SpellcraftTests(unittest.TestCase):
    def setUp(self): self.state=new_campaign()
    def act(self,kind,**fields): return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count): self.act('advance')
    def supplies(self):
        self.state['sharedFunds']=200
        for key in self.state['materialInventory']:self.state['materialInventory'][key]=10
        for who in ('founder','mira'):
            for key in ('steady-hearth-wards','steady-growth','luminous-copying','reference-binding','clear-instruction','gentle-refraction'):learn_for_character(self.state,who,key)
        self.state['restorationStatus']='complete'
    def draft(self,form='warm-twist',who='founder',materials=None):
        materials=materials or {'warm-twist':['sun-amber','binding-thread'],'root-song':['silver-ivy','silver-ivy'],'luminous-copy':['moon-glass','moon-glass'],'clarify-glass':['moon-glass','moon-glass']}[form]
        self.act('draft-spell',characterId=who,formId=form,name='<A useful working>',intent='Make a useful thing; arbitrary extra powers have no authority.',materials=materials)
        return self.state['spellbook'][-1]['id']
    def learned(self,form='warm-twist',who='founder'):
        key=self.draft(form,who);self.act('test-spell',spellId=key);self.advance(2)
        return key
    def prepare(self,who,keys):self.act('prepare-spells',characterId=who,spellIds=keys)
    def assert_rejected(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def test_draft_is_free_and_prose_cannot_bypass_personal_knowledge(self):
        before=deepcopy(self.state);key=self.draft()
        for field in ('sharedFunds','materialInventory','dayNumber','currentDayPhase','characterDevelopment'):self.assertEqual(self.state[field],before[field])
        self.assert_rejected('test-spell',spellId=key)
        self.assert_rejected('draft-spell',characterId='founder',formId='infinite-gold',name='Gold',intent='Gold',materials=['sun-amber','binding-thread'])
        self.assert_rejected('draft-spell',characterId='founder',formId='warm-twist',name='Again',intent='Again',materials=['sun-amber','binding-thread'])
        self.act('discard-spell-draft',spellId=key);self.assertEqual(self.state['spellbook'],[])
    def test_components_properties_quantities_funds_and_facility_are_atomic(self):
        self.supplies()
        self.assert_rejected('draft-spell',characterId='founder',formId='warm-twist',name='No',intent='No',materials=['binding-thread','sun-amber'])
        key=self.draft('root-song');self.state['materialInventory']['silver-ivy']=1
        self.assert_rejected('test-spell',spellId=key)
        self.state['materialInventory']['silver-ivy']=2;self.state['sharedFunds']=3
        self.assert_rejected('test-spell',spellId=key)
        self.state['sharedFunds']=4;self.state['restorationStatus']='not-started'
        self.assert_rejected('test-spell',spellId=key)
        self.state['restorationStatus']='complete';self.act('test-spell',spellId=key)
        self.assertEqual(self.state['sharedFunds'],0);self.assertEqual(self.state['materialInventory']['silver-ivy'],0)
    def test_testing_pauses_and_does_not_produce_or_auto_prepare(self):
        self.supplies();key=self.draft();self.act('test-spell',spellId=key)
        self.advance();self.act('assign-founder',assignment='rest');self.advance(2)
        self.assertEqual(self.state['spellbook'][0]['completedWorkPhases'],1)
        self.assert_rejected('test-spell',spellId=key);self.assert_rejected('discard-spell-draft',spellId=key)
        awards=deepcopy(self.state['characterDevelopment']);inventory=deepcopy(self.state['materialInventory'])
        self.act('assign-founder',assignment='spellwork');self.advance()
        self.assertEqual(self.state['spellbook'][0]['status'],'learned')
        self.assertEqual(self.state['materialInventory'],inventory);self.assertEqual(self.state['characterDevelopment'],awards)
        self.assertEqual(self.state['preparedSpells']['founder'],[]);self.assert_rejected('cast-spell',spellId=key)
    def test_cast_commits_input_then_pauses_cancels_refunds_and_resolves_once(self):
        self.supplies();key=self.learned();self.prepare('founder',[key]);before=deepcopy(self.state)
        self.act('cast-spell',spellId=key)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],before['materialInventory']['silver-ivy']-1)
        self.assertEqual(self.state['currentDayPhase'],before['currentDayPhase'])
        self.assert_rejected('cast-spell',spellId=key);self.assert_rejected('prepare-spells',characterId='founder',spellIds=[])
        self.act('assign-founder',assignment='rest');self.advance();self.assertEqual(self.state['spellbook'][0]['castCount'],0)
        self.act('cancel-spell-casting',characterId='founder');self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.assert_rejected('cancel-spell-casting',characterId='founder')
        self.act('cast-spell',spellId=key);self.advance(3)
        self.assertEqual(self.state['spellbook'][0]['castCount'],1)
        self.assertEqual(self.state['materialInventory']['binding-thread'],before['materialInventory']['binding-thread']+2)
        self.assertEqual(self.state['founderAssignment'],'rest')
    def test_all_forms_have_exact_output_without_copying_or_preparation_bonuses(self):
        for form in ('warm-twist','root-song','luminous-copy','clarify-glass'):
            with self.subTest(form=form):
                self.state=new_campaign();self.supplies();key=self.learned(form);self.prepare('founder',[key])
                self.state['libraryIndexInstalled']=True
                self.state['characterDevelopment']['founder']['preparedPractices']=['archive-focus','careful-assembly']
                self.state['signatureFocuses']['founder']['inscriptions']=['copying-line','steady-hand']
                self.state['signatureFocuses']['founder']['householdLoadout']=['copying-line','steady-hand']
                before=deepcopy(self.state);definition=SPELL_FORMS[form]
                self.act('cast-spell',spellId=key);self.advance()
                self.assertEqual(self.state['sharedFunds'],before['sharedFunds']+definition['crownsOutput'])
                for material,amount in before['materialInventory'].items():
                    self.assertEqual(self.state['materialInventory'][material],amount-definition['castingInputs'].get(material,0)+definition['materialOutput'].get(material,0))
    def test_mira_has_own_knowledge_spells_and_casting_location(self):
        self.supplies();key=self.learned(who='mira')
        self.assert_rejected('prepare-spells',characterId='founder',spellIds=[key])
        self.prepare('mira',[key]);self.act('cast-spell',spellId=key)
        self.assertEqual(resident_room(self.state),'common-room')
        self.assertEqual(self.state['residentAssignment'],'spellwork')
        self.advance();self.assertEqual(self.state['spellbook'][0]['castCount'],1)
    def test_capacity_requires_ritual_and_preparation_is_not_shared(self):
        self.supplies();keys=[self.learned(form) for form in ('warm-twist','root-song','luminous-copy','clarify-glass')]
        self.assert_rejected('prepare-spells',characterId='founder',spellIds=keys)
        self.assert_rejected('prepare-spells',characterId='founder',spellIds=[keys[0],keys[0]])
        self.prepare('founder',keys[:2]);self.assertEqual(public_state(self.state)['spellPreparationCapacity'],2)
        self.state['spellRitual']['status']='complete';self.prepare('founder',keys[:3])
        self.assert_rejected('prepare-spells',characterId='founder',spellIds=keys)
        self.assertEqual(public_state(self.state)['spellPreparationCapacity'],3)
        self.assertEqual(self.state['preparedSpells']['mira'],[])
    def test_absence_pauses_and_rejects_cast_preparation_and_cancellation(self):
        self.supplies();key=self.learned();self.prepare('founder',[key]);self.act('cast-spell',spellId=key)
        self.act('start-expedition');self.advance()
        self.assertEqual(self.state['spellbook'][0]['castCount'],0)
        for kind,fields in [('cancel-spell-casting',{'characterId':'founder'}),('cast-spell',{'spellId':key}),('prepare-spells',{'characterId':'founder','spellIds':[]})]:self.assert_rejected(kind,**fields)
        self.act('return-expedition');self.advance();self.assertEqual(self.state['spellbook'][0]['castCount'],0)
        self.act('assign-founder',assignment='spellwork');self.advance();self.assertEqual(self.state['spellbook'][0]['castCount'],1)
    def test_ritual_requires_personal_competence_components_and_both_contributors(self):
        self.supplies();materials=['moon-glass','binding-thread','moon-glass','binding-thread']
        self.assert_rejected('start-spell-ritual',materials=materials)
        self.state['libraryIndexInstalled']=True;self.state['residentKnownPrinciples'].remove('reference-binding')
        self.assert_rejected('start-spell-ritual',materials=materials)
        learn_for_character(self.state,'mira','reference-binding');self.state['materialInventory']['moon-glass']=1
        self.assert_rejected('start-spell-ritual',materials=materials)
        self.state['materialInventory']['moon-glass']=2;funds=self.state['sharedFunds'];awards=deepcopy(self.state['characterDevelopment'])
        self.act('start-spell-ritual',materials=materials);self.assertEqual(self.state['sharedFunds'],funds-18)
        self.assert_rejected('start-spell-ritual',materials=materials)
        self.advance();self.act('assign-resident',assignment='rest');self.advance(2)
        self.assertEqual(self.state['spellRitual']['contributions'],{'founder':1,'mira':1})
        self.assertTrue(any('paused' in row for row in public_state(self.state)['nextPhaseForecast']))
        self.act('resume-spell-ritual');self.advance()
        self.assertEqual(self.state['spellRitual']['status'],'complete')
        self.assertEqual(self.state['spellRitual']['contributions'],{'founder':2,'mira':2})
        self.assertEqual(self.state['characterDevelopment'],awards)
        self.assert_rejected('resume-spell-ritual')
    def test_ritual_pauses_pending_spell_work_without_losing_it(self):
        self.supplies();self.state['libraryIndexInstalled']=True
        key=self.draft();self.act('test-spell',spellId=key);self.advance()
        self.act('start-spell-ritual',materials=['moon-glass','binding-thread','moon-glass','binding-thread']);self.advance(2)
        self.assertEqual(self.state['spellbook'][0]['completedWorkPhases'],1)
        self.assertEqual(self.state['spellWork']['founder']['spellId'],key)
        self.act('assign-founder',assignment='spellwork');self.advance();self.assertEqual(self.state['spellbook'][0]['status'],'learned')
    def test_invalid_input_shapes_are_rules_errors(self):
        for value in (None,[],{},True):
            self.assert_rejected('draft-spell',characterId=value,formId='warm-twist',name='x',intent='x',materials=['sun-amber','binding-thread'])
            self.assert_rejected('draft-spell',characterId='founder',formId=value,name='x',intent='x',materials=['sun-amber','binding-thread'])
        self.assert_rejected('prepare-spells',characterId='founder',spellIds=[{}])
    def test_schema_nine_upgrade_preserves_existing_data_and_retries(self):
        self.supplies();old=deepcopy(self.state);old['schemaVersion']=9
        for key in ('spellbook','nextSpellNumber','preparedSpells','spellWork','spellRitual'):old.pop(key)
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            for key,value in old.items():
                if key not in ('schemaVersion','revision'):self.assertEqual(state[key],value)
            self.assertEqual(state['schemaVersion'],66)
            self.assertTrue((Path(directory)/'campaign-before-schema-9-to-66.sqlite3').exists())
            request={'type':'draft-spell','characterId':'founder','formId':'warm-twist','name':'Saved working','intent':'Make cord','materials':['sun-amber','binding-thread'],'requestId':uuid.uuid4().hex,'expectedRevision':state['revision']}
            request={'requestId':request.pop('requestId'),'expectedRevision':request.pop('expectedRevision'),'action':request}
            once=store.action(request);again=store.action(request);self.assertEqual(once,again)
            request={'type':'test-spell','spellId':once['spellbook'][0]['id'],'requestId':uuid.uuid4().hex,'expectedRevision':once['revision']}
            request={'requestId':request.pop('requestId'),'expectedRevision':request.pop('expectedRevision'),'action':request}
            once=store.action(request);again=store.action(request);self.assertEqual(once,again)
            self.assertEqual(GameStore(directory).read(),once)

if __name__=='__main__':unittest.main()
