from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, resident_moment_view, resident_friendships
from dialogue import dialogue_context
from server import GameStore

class ResidentMomentTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,key):return apply_action(self.state,{'type':kind,'momentId':key})
    def recruit(self):
        self.state['additionalResidents']['tamsin']['status']='resident'
        self.state['housingRooms']['west-chamber']['status']='complete'
        self.state['bedroomAssignments']['tamsin']='west-chamber'
    def test_contextual_topics_wait_for_actual_progress(self):
        for key in ('mira-greenhouse','mira-index','mira-folio','mira-refraction','tamsin-settling','shared-shelf'):
            self.assertFalse(resident_moment_view(self.state,key)['unlocked'])
            with self.assertRaises(RuleError):self.act('join-resident-moment',key)
        self.state['restorationStatus']='complete'
        self.assertTrue(resident_moment_view(self.state,'mira-greenhouse')['canJoin'])
        self.state['archivePrinciples'].append('gentle-refraction')
        self.assertTrue(resident_moment_view(self.state,'mira-refraction')['canJoin'])
    def test_completed_moment_changes_only_its_memory_conversation_and_journal(self):
        self.state['restorationStatus']='complete';before=deepcopy(self.state)
        self.act('join-resident-moment','mira-greenhouse')
        for key in before:
            if key not in ('residentMoments','conversation','journal','revision'):self.assertEqual(before[key],self.state[key],key)
        self.assertEqual(self.state['residentMoments']['mira-greenhouse']['completedOn'],{'dayNumber':before['dayNumber'],'phase':before['currentDayPhase']})
        saved=deepcopy(self.state);self.act('join-resident-moment','mira-greenhouse');self.assertEqual(saved,self.state)
    def test_deferred_invitations_do_not_expire_and_wait_for_presence(self):
        self.state['restorationStatus']='complete'
        self.act('defer-resident-moment','mira-greenhouse')
        for _ in range(5):apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['residentMoments']['mira-greenhouse']['status'],'deferred')
        with self.assertRaises(RuleError):self.act('join-resident-moment','mira-greenhouse')
        self.act('restore-resident-moment','mira-greenhouse')
        apply_action(self.state,{'type':'start-expedition'})
        self.assertTrue(resident_moment_view(self.state,'mira-greenhouse')['waitingForReturn'])
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('join-resident-moment','mira-greenhouse')
        self.assertEqual(before,self.state)
    def test_joint_scene_records_shared_history_without_creating_romance(self):
        self.recruit();before=deepcopy(self.state)
        self.act('join-resident-moment','shared-shelf')
        self.assertIn('laugh',resident_friendships(self.state)[0]['description'])
        self.assertEqual(self.state['resonancePoints'],before['resonancePoints'])
        self.assertEqual(self.state['relationshipDescription'],before['relationshipDescription'])
        self.assertFalse(self.state['additionalResidents']['tamsin']['sharedFlirtation'])
        for who,lines in [('mira',self.state['conversation']),('tamsin',self.state['additionalResidents']['tamsin']['conversation'])]:
            self.assertTrue(any(line.get('momentId')=='shared-shelf' for line in lines))
            self.assertIn('An argument about a shelf',json.dumps(dialogue_context(self.state,'Hello',who)))
    def test_flirt_followups_require_individual_established_interest_and_owned_keepsake(self):
        self.recruit()
        self.state['residentKeepsakes']['mira']=['mira-reading-folio']
        self.state['residentKeepsakes']['tamsin']=['tamsin-repair-case']
        for key in ('mira-close-reading','tamsin-loose-thread'):
            with self.assertRaises(RuleError):self.act('join-resident-moment',key)
        self.state['completedDevelopments'].append('shared-flirtation')
        self.act('join-resident-moment','mira-close-reading')
        self.assertFalse(resident_moment_view(self.state,'tamsin-loose-thread')['unlocked'])
        self.state['additionalResidents']['tamsin']['sharedFlirtation']=True
        before=self.state['resonancePoints'];self.act('join-resident-moment','tamsin-loose-thread')
        self.assertEqual(before,self.state['resonancePoints'])
    def test_private_moments_are_not_added_to_other_resident_context(self):
        self.recruit();self.act('join-resident-moment','tamsin-settling')
        self.assertNotIn('A door that closes',json.dumps(dialogue_context(self.state,'Hello','mira')))
        self.assertIn('A door that closes',json.dumps(dialogue_context(self.state,'Hello','tamsin')))
        self.assertEqual(resident_moment_view(self.state,'mira-index')['lines'],[])
    def test_completed_memories_can_be_read_while_away_without_replaying(self):
        self.state['restorationStatus']='complete';self.act('join-resident-moment','mira-greenhouse')
        apply_action(self.state,{'type':'start-expedition'});before=deepcopy(self.state)
        view=public_state(self.state)['residentMomentViews']['mira-greenhouse']
        self.assertTrue(view['lines']);self.assertEqual(before,self.state)
        with self.assertRaises(RuleError):self.act('defer-resident-moment','mira-greenhouse')
    def test_schema17_migration_and_request_retry_preserve_scene_once(self):
        old=deepcopy(self.state);old.pop('residentMoments');old['schemaVersion']=17;old['restorationStatus']='complete'
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            self.assertTrue((Path(directory)/f"campaign-before-schema-17-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            self.assertEqual(state['conversation'],old['conversation']);self.assertEqual(state['revision'],old['revision']+1)
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'join-resident-moment','momentId':'mira-greenhouse'}}
            after=store.action(payload);self.assertEqual(after,store.action(payload));self.assertEqual(after,GameStore(directory).read())
