from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
import game as g
import personal_stories as stories
from dialogue import DialogueService,ProviderSettings,dialogue_context
from server import GameStore

class PersonalStoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=GameStore(self.temp.name);self.calls=[]
        self.service=DialogueService(ProviderSettings(self.temp.name),lambda *_:self.calls.append(1))
        s=self.store.read();s['sharedFunds']=100
        for key in s['materialInventory']:s['materialInventory'][key]=10
        self.seed(s)
    def seed(self,s):
        with self.store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
    def draft(self,**changes):
        payload={'requestId':uuid.uuid4().hex,'purpose':'story-proposal','source':'offline','ownerId':'mira','packageId':'personal-folio','expectedRevision':self.store.read()['revision'],'text':'Her own work.',**changes}
        return self.service.generate(self.store,payload)
    def approve(self):
        draft=self.draft();self.assertEqual(draft['status'],'ready')
        s=self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True});return s,next(iter(s['personalStories']))
    def test_review_funding_pause_resume_completion_and_scene(self):
        before=self.store.read();s,key=self.approve();r=s['personalStories'][key]
        self.assertEqual(s['sharedFunds'],before['sharedFunds']);self.assertEqual(s['residentAssignment'],before['residentAssignment']);self.assertEqual(self.calls,[])
        g.apply_action(s,{'type':'start-personal-story','storyId':key});self.assertEqual(s['sharedFunds'],92)
        g.apply_action(s,{'type':'advance'});self.assertEqual(r['completedWorkPhases'],1)
        g.apply_action(s,{'type':'assign-resident','assignment':'rest'});g.apply_action(s,{'type':'advance'});self.assertEqual(r['completedWorkPhases'],1)
        g.apply_action(s,{'type':'resume-personal-story','storyId':key});g.apply_action(s,{'type':'advance'});self.assertEqual(r['status'],'complete')
        phase=(s['dayNumber'],s['currentDayPhase']);points=deepcopy(s['characterProgression']) if 'characterProgression' in s else deepcopy(s['advancement']) if 'advancement' in s else g.character_sheet(s,'mira')
        g.apply_action(s,{'type':'defer-story-scene','storyId':key});g.apply_action(s,{'type':'restore-story-scene','storyId':key})
        n=len(s['conversation']);g.apply_action(s,{'type':'join-story-scene','storyId':key});g.apply_action(s,{'type':'join-story-scene','storyId':key})
        self.assertEqual(len(s['conversation']),n+1);self.assertEqual((s['dayNumber'],s['currentDayPhase']),phase);self.assertEqual(r['sceneStatus'],'remembered')
        self.assertEqual(r['portraitPath'],g.ORIGINAL_ASSETS['mira']);self.assertNotIn('personal-folio',stories.available_packages(s,'mira'))
        self.assertIn(json.dumps(r['proposal']['title'])[1:-1],dialogue_context(s,'Hello','mira')[0]['content'])
    def test_cancel_refunds_once_and_no_early_scene(self):
        s,key=self.approve();funds=s['sharedFunds'];materials=deepcopy(s['materialInventory'])
        g.apply_action(s,{'type':'start-personal-story','storyId':key})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'join-story-scene','storyId':key})
        g.apply_action(s,{'type':'cancel-personal-story','storyId':key});self.assertEqual(s['sharedFunds'],funds);self.assertEqual(s['materialInventory'],materials)
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'cancel-personal-story','storyId':key})
    def test_reserves_and_unfunded_assignment(self):
        s,key=self.approve();s['materialReserveTargets']['porous-clay']=10
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'start-personal-story','storyId':key})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'assign-resident','assignment':'personal-story'})
    def test_duplicate_package_and_exact_schema(self):
        s,key=self.approve()
        with self.assertRaises(g.RuleError):stories.validate(json.dumps(stories.outline(g.new_campaign(),'mira','personal-folio')),s,'mira')
        p=stories.outline(g.new_campaign(),'mira','personal-folio');p['rewards']={'crowns':100}
        with self.assertRaises(g.RuleError):stories.validate(json.dumps(p),g.new_campaign(),'mira')
        with self.assertRaises(g.RuleError):stories.validate('{"title":"a","title":"b"}',g.new_campaign(),'mira')
    def test_recheck_stale_and_review_checkboxes(self):
        draft=self.draft()
        with self.assertRaises(g.RuleError):self.service.accept(self.store,{'draftId':draft['id']})
        s=self.store.read();g.apply_action(s,{'type':'advance'});s['revision']+=1;self.seed(s)
        with self.assertRaises(g.RuleError):self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
        checked=self.service.review_story(self.store,{'draftId':draft['id'],'expectedRevision':s['revision']});self.assertEqual(checked['proposal'],draft['proposal']);self.assertEqual(self.calls,[])
        self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
    def test_scope_and_external_players(self):
        s=self.store.read();s['privateCastleLore']['sentinel']='NEVERINPROMPT';s['conversation'].append({'speaker':'Mira','text':'PRIVATECHAT'})
        prompt=json.dumps(stories.context(s,'mira','Her work.'));self.assertNotIn('NEVERINPROMPT',prompt);self.assertNotIn('PRIVATECHAT',prompt)
        for who in ['founder','eris','selene','unknown',[]]:
            with self.assertRaises(g.RuleError):self.draft(ownerId=who)
    def test_migration_preserves_old_save(self):
        s=self.store.read();s.pop('personalStories');s['schemaVersion']=29;before=deepcopy(s);self.seed(s)
        migrated=GameStore(self.temp.name).read();self.assertEqual(migrated['personalStories'],{});self.assertEqual(migrated['sharedFunds'],before['sharedFunds'])
        self.assertTrue((Path(self.temp.name)/f"campaign-before-schema-29-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
