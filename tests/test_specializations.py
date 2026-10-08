from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, RuleError, character_sheet, work_contribution, copying_income, public_state, award_advancement
from server import GameStore

class SpecializationTests(unittest.TestCase):
    def setUp(self):
        self.state=new_campaign();award_advancement(self.state,'founder','test-milestone',20,'Test milestone')
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def prepare(self,key,prepared=True):self.act('prepare-practice',characterId='founder',practiceId=key,prepared=prepared)
    def set(self,kind,name='At the archive',who='founder'):self.act(kind,characterId=who,name=name)
    def qualify(self):
        self.state['characterSkills']['founder']['scholarship']=1
        self.state['characterDevelopment']['founder']['learnedPractices'].append('archive-focus')
    def train(self,key):
        self.act('start-training',characterId='founder',practiceId=key)
        self.act('advance');self.act('advance')
    def test_prerequisites_reserve_cost_and_learning_does_not_auto_prepare(self):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('start-training',characterId='founder',practiceId='comparative-study')
        self.assertEqual(before,self.state)
        self.qualify();available=character_sheet(self.state,'founder')['availableAdvancement']
        self.act('start-training',characterId='founder',practiceId='comparative-study')
        self.assertEqual(character_sheet(self.state,'founder')['availableAdvancement'],available-2)
        self.act('advance');self.assertNotIn('comparative-study',self.state['characterDevelopment']['founder']['learnedPractices'])
        self.act('advance');self.assertIn('comparative-study',self.state['characterDevelopment']['founder']['learnedPractices'])
        self.assertNotIn('comparative-study',self.state['characterDevelopment']['founder']['preparedPractices'])
        self.assertEqual(character_sheet(self.state,'founder')['availableAdvancement'],available-2)
    def test_research_bonus_is_personal_prepared_and_not_income_or_learning_speed(self):
        self.qualify();self.train('comparative-study')
        base=work_contribution(self.state,'founder','archive-focus');other=work_contribution(self.state,'mira','archive-focus');income=copying_income(self.state)
        self.prepare('comparative-study')
        self.assertEqual(work_contribution(self.state,'founder','archive-focus'),base+1)
        self.assertEqual(work_contribution(self.state,'mira','archive-focus'),other)
        self.assertEqual(copying_income(self.state),income)
        self.prepare('archive-focus');self.assertEqual(work_contribution(self.state,'founder','archive-focus'),base+2)
        parts=public_state(self.state)['workContributionViews']['founder']['archive-focus']
        self.assertEqual(sum(row['amount'] for row in parts),base+2)
        self.act('train-skill',characterId='founder',skillId='scholarship');self.act('advance')
        self.assertEqual(self.state['trainingProjects']['founder']['completedWorkPhases'],1)
    def test_assembly_bonus_is_scoped_to_making_and_two_slots_still_apply(self):
        self.state['characterSkills']['founder']['artifice']=1
        learned=self.state['characterDevelopment']['founder']['learnedPractices']
        for key in ('careful-assembly','archive-focus'):
            if key not in learned:learned.append(key)
        self.train('measured-assembly')
        base=work_contribution(self.state,'founder','careful-assembly');research=work_contribution(self.state,'founder','archive-focus')
        self.prepare('measured-assembly');self.prepare('careful-assembly')
        self.assertEqual(work_contribution(self.state,'founder','careful-assembly'),base+2)
        self.assertEqual(work_contribution(self.state,'founder','archive-focus'),research)
        with self.assertRaises(RuleError):self.prepare('archive-focus')
    def test_preparation_sets_are_personal_atomic_and_leave_other_loadouts_unchanged(self):
        self.qualify();self.prepare('archive-focus');self.set('save-preparation-set')
        self.prepare('archive-focus',False);before=deepcopy(self.state);self.set('load-preparation-set')
        self.assertEqual(self.state['characterDevelopment']['founder']['preparedPractices'],['archive-focus'])
        for key in before:
            if key!='characterDevelopment':self.assertEqual(before[key],self.state[key],key)
        with self.assertRaises(RuleError):self.set('load-preparation-set',who='mira')
        self.set('delete-preparation-set');self.assertEqual(self.state['characterDevelopment']['founder']['preparedPractices'],['archive-focus'])
    def test_retraining_preserves_sets_but_cannot_restore_forgotten_expertise(self):
        self.qualify();self.train('comparative-study');self.prepare('comparative-study');self.set('save-preparation-set')
        self.act('start-retraining',characterId='founder');self.act('advance');before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.set('load-preparation-set')
        self.assertEqual(before,self.state)
        self.assertIn('At the archive',self.state['practicePreparationSets']['founder'])
        self.assertTrue(public_state(self.state)['preparationSetViews']['founder']['At the archive'])
    def test_sets_cannot_change_on_expedition_and_have_a_bounded_count(self):
        for i in range(6):self.set('save-preparation-set',str(i))
        with self.assertRaises(RuleError):self.set('save-preparation-set','seventh')
        self.set('save-preparation-set','0')
        self.act('start-expedition');before=deepcopy(self.state)
        for kind in ('save-preparation-set','load-preparation-set','delete-preparation-set'):
            with self.assertRaises(RuleError):self.set(kind,'0')
            self.assertEqual(before,self.state)
    def test_residents_offer_professional_advanced_paths_without_automatic_fieldwork(self):
        self.state['additionalResidents']['tamsin']['status']='resident'
        for who in ('mira','tamsin'):
            offered=character_sheet(self.state,who)['offeredPractices']
            self.assertIn('comparative-study',offered);self.assertIn('measured-assembly',offered);self.assertNotIn('field-notes',offered)
    def test_schema18_migration_preserves_build_and_new_sets_reload(self):
        old=deepcopy(self.state);old.pop('practicePreparationSets');old['schemaVersion']=18
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            self.assertTrue((Path(directory)/'campaign-before-schema-18-to-66.sqlite3').exists())
            self.assertEqual(state['characterDevelopment'],old['characterDevelopment'])
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'save-preparation-set','characterId':'founder','name':'Unprepared'}}
            after=store.action(payload);self.assertEqual(after,store.action(payload));self.assertEqual(after,GameStore(directory).read())
