from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
import game as g
import containment as c
from server import GameStore
from dialogue import dialogue_context

class ContainmentTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign();self.s['sharedFunds']=500
        for key in self.s['materialInventory']:self.s['materialInventory'][key]=30
        self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.s['binderyDiscoveries']=['salvage']
        for key in ('water-guidance','gentle-preservation'):g.learn_for_character(self.s,'founder',key)
    def act(self,kind,**fields):return g.apply_action(self.s,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(self.s,before)
    def chamber(self,key):self.act('build-containment',chamberId=key);self.advance(2)
    def admit(self,who='sabine',chamber='echo-1'):
        self.chamber(chamber);self.act('admit-containment',characterId=who,chamberId=chamber);self.advance()
    def agree(self,who='sabine'):
        for topic in ('account','plan'):self.act('talk-containment',characterId=who,topic=topic)
    def resolve(self,who='sabine'):
        self.agree(who);self.act('care-containment',characterId=who);self.advance(3)
    def released(self,who='sabine',chamber='echo-1'):
        self.admit(who,chamber);self.resolve(who);self.act('release-containment',characterId=who);self.advance()
    def test_ten_specialized_slots_are_separate_from_housing(self):
        housing=deepcopy(g.housing_summary(self.s));self.assertEqual(c.view(self.s)['maximumCapacity'],2)
        for chamber in c.CHAMBERS:self.chamber(chamber)
        self.assertEqual(c.view(self.s)['usableCapacity'],2)
        self.assertEqual(g.housing_summary(self.s),housing)
        self.reject('build-containment',chamberId='heat-6');self.reject('build-containment',chamberId='heat-1')
    def test_build_reserves_pause_cancel_refunds_once(self):
        before=self.s['sharedFunds'];materials=deepcopy(self.s['materialInventory'])
        self.act('build-containment',chamberId='heat-1');self.advance()
        self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(self.s['containment']['project']['completedWorkPhases'],1)
        self.reject('build-containment',chamberId='echo-1')
        self.act('cancel-containment');self.assertEqual(self.s['sharedFunds'],before);self.assertEqual(self.s['materialInventory'],materials)
        self.reject('cancel-containment');self.assertEqual(self.s['containment']['chambers']['heat-1']['status'],'sealed')
    def test_requirements_and_reserves_are_atomic(self):
        self.s['livingWingCompletedOn']=None;self.reject('build-containment',chamberId='heat-1')
        self.reject('admit-containment',characterId='sabine',chamberId='echo-1')
        self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.s['materialReserveTargets']['porous-clay']=30;self.reject('build-containment',chamberId='heat-1')
        self.reject('build-containment',chamberId=[])
        self.reject('admit-containment',characterId=[],chamberId='heat-1')
    def test_arrival_requires_compatible_capacity_and_never_takes_bed_or_job(self):
        self.chamber('heat-1');self.reject('admit-containment',characterId='sabine',chamberId='heat-1')
        self.chamber('echo-1');beds=deepcopy(self.s['bedroomAssignments'])
        self.act('admit-containment',characterId='sabine',chamberId='echo-1')
        self.assertEqual(self.s['containment']['cases']['sabine']['status'],'arrival-pending')
        self.assertEqual(c.view(self.s)['occupiedCapacity'],1)
        self.reject('admit-containment',characterId='sabine',chamberId='echo-1')
        self.reject('talk-containment',characterId='sabine',topic='account')
        self.advance();self.assertEqual(self.s['containment']['cases']['sabine']['status'],'contained')
        self.assertNotIn('sabine',g.household_members(self.s));self.assertEqual(self.s['bedroomAssignments'],beds)
        self.reject('assign-character',characterId='sabine',assignment='commissions')
        self.reject('train-character-build',characterId='sabine',buildKind='attribute',targetId='insight')
        with self.assertRaises(g.RuleError):dialogue_context(self.s,'Flirt with me','sabine')
    def test_normal_contact_cannot_bypass_containment_or_transfer(self):
        self.admit()
        for kind,extra in [('summoning-reopen',{}),('summoning-ask-stay',{}),('summoning-household-decision',{'decision':'invite-to-stay'}),('summoning-invite',{'roomId':'garden-chamber'}),('summoning-personal-talk',{'topic':'company'})]:
            self.reject(kind,contactId='encounter-sabine',**extra)
        self.reject('release-containment',characterId='sabine')
        self.act('transfer-containment',characterId='sabine');self.advance()
        self.reject('summoning-reopen',contactId='encounter-sabine')
        self.assertEqual(c.view(self.s)['occupiedCapacity'],0)
        self.assertIn('sabine',self.s['people'])
    def test_care_requires_account_plan_personal_knowledge_and_cost(self):
        self.admit();self.reject('care-containment',characterId='sabine');self.agree()
        before=deepcopy(self.s);self.agree();self.assertEqual(before,self.s)
        g.character_principles(self.s,'founder').remove('gentle-preservation')
        self.reject('care-containment',characterId='sabine')
        g.learn_for_character(self.s,'founder','gentle-preservation')
        self.s['materialReserveTargets']['moon-glass']=30;self.reject('care-containment',characterId='sabine')
    def test_care_uses_only_primary_budget_no_repeated_reward_or_identity_rewrite(self):
        self.admit();profile=deepcopy(self.s['people']['sabine']);self.agree()
        self.s['characterBuilds']['founder']['attributes']['insight']=3
        self.act('care-containment',characterId='sabine');self.advance()
        self.assertEqual(self.s['containment']['project']['completedWorkPhases'],1)
        self.act('assign-founder',assignment='commissions');self.advance()
        self.assertEqual(self.s['containment']['project']['completedWorkPhases'],1)
        self.act('resume-containment');self.advance(2)
        self.assertEqual(self.s['containment']['cases']['sabine']['status'],'safe')
        self.assertEqual(self.s['people']['sabine'],profile)
        self.assertEqual(g.character_sheet(self.s,'founder')['earnedAdvancement'],2)
        self.assertEqual(self.s['resonancePoints'],0)
        self.reject('care-containment',characterId='sabine');self.advance(3)
        self.assertEqual(g.character_sheet(self.s,'founder')['earnedAdvancement'],2)
    def test_safe_transfer_is_free_and_refunds_unfinished_care_no_work_required(self):
        self.admit();self.agree();money=self.s['sharedFunds'];materials=deepcopy(self.s['materialInventory'])
        self.act('care-containment',characterId='sabine');self.advance()
        self.act('transfer-containment',characterId='sabine')
        self.assertEqual(self.s['sharedFunds'],money);self.assertEqual(self.s['materialInventory'],materials)
        self.assertEqual(c.view(self.s)['occupiedCapacity'],1)
        self.reject('transfer-containment',characterId='sabine');self.advance()
        self.assertEqual(c.view(self.s)['occupiedCapacity'],0)
        self.assertEqual(g.character_sheet(self.s,'founder')['earnedAdvancement'],0)
        self.assertNotIn('sabine',self.s['bedroomAssignments'])
    def test_release_with_no_bed_money_or_romance_then_voluntary_visit_membership_return(self):
        self.admit();self.resolve();self.s['sharedFunds']=0
        self.act('release-containment',characterId='sabine');self.assertEqual(c.view(self.s)['occupiedCapacity'],1)
        self.advance();self.assertEqual(c.view(self.s)['occupiedCapacity'],0)
        self.assertNotIn('sabine',g.household_members(self.s));self.assertEqual(self.s['sharedFunds'],0)
        self.reject('release-containment',characterId='sabine')
        contact='encounter-sabine'
        for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=contact,topic=topic)
        self.reject('summoning-invite',contactId=contact,roomId='west-chamber')
        self.s['housingRooms']['west-chamber']['status']='complete'
        self.act('summoning-invite',contactId=contact,roomId='west-chamber');self.advance()
        self.act('summoning-ask-stay',contactId=contact)
        self.assertNotIn('sabine',g.household_members(self.s))
        self.act('summoning-household-decision',contactId=contact,decision='invite-to-stay')
        self.assertIn('sabine',g.household_members(self.s))
        self.assertIn('Sabine',dialogue_context(self.s,'Hello','sabine')[0]['content'])
        profile=deepcopy(self.s['people']['sabine']);self.act('summoning-depart',contactId=contact);self.advance()
        self.act('summoning-invite',contactId=contact,roomId='west-chamber');self.advance()
        self.assertEqual(self.s['people']['sabine'],profile)
        self.assertEqual(len(self.s['residency']['sabine']['arrivals']),2)
    def test_case_requires_private_normal_bed_after_independent_resolution(self):
        self.released('sabine','echo-1');self.s['housingRooms']['garden-chamber']['status']='complete'
        for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId='encounter-sabine',topic=topic)
        self.reject('summoning-invite',contactId='encounter-sabine',roomId='garden-chamber')
        self.s['housingRooms']['west-chamber']['status']='complete'
        self.act('summoning-invite',contactId='encounter-sabine',roomId='west-chamber');self.advance()
        self.assertEqual(self.s['bedroomAssignments']['sabine'],'west-chamber')
    def test_schema27_migration_preserves_previous_state_and_idempotent_work_retry(self):
        old=deepcopy(self.s);old.pop('containment');old['schemaVersion']=27
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);upgraded=store.read()
            for key,value in old.items():
                if key not in ('schemaVersion','revision'):self.assertEqual(upgraded[key],value,key)
            self.assertTrue((Path(directory)/f"campaign-before-schema-27-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':upgraded['revision'],'action':{'type':'build-containment','chamberId':'heat-1'}}
            after=store.action(payload);self.assertEqual(after,store.action(payload));self.assertEqual(after,GameStore(directory).read())
    def test_absence_and_reading_do_not_progress_or_authorize_work(self):
        self.act('build-containment',chamberId='heat-1');self.act('start-expedition')
        before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
        self.reject('resume-containment');self.reject('cancel-containment')
        g.resolve_work(self.s)
        self.assertEqual(self.s['containment']['project']['completedWorkPhases'],0)
