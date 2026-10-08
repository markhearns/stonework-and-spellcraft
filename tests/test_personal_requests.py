from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign,apply_action,RuleError,public_state
from dialogue import dialogue_context
from server import GameStore

class PersonalRequestTests(unittest.TestCase):
    def setUp(self):
        self.state=new_campaign();self.key='mira-reading-folio'
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def request(self,kind,**fields):return self.act(kind,requestId=self.key,**fields)
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.request(kind,**fields)
        self.assertEqual(self.state,before)
    def unlock(self):self.state['miraArchiveProject']['status']='complete'
    def fund(self,source='shared'):
        self.unlock();self.request('accept-personal-request');self.request('fund-personal-request',fundingSource=source)
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def test_optional_acceptance_and_deferral_are_free_and_never_expire(self):
        self.reject('accept-personal-request');self.unlock();before=deepcopy(self.state)
        self.request('accept-personal-request');self.request('defer-personal-request');self.request('defer-personal-request')
        for key in ('sharedFunds','personalFunds','materialInventory','resonancePoints','dayNumber','currentDayPhase','characterDevelopment'):
            self.assertEqual(self.state[key],before[key])
        self.advance(4);self.assertEqual(self.state['personalRequests'][self.key]['status'],'deferred')
        self.request('accept-personal-request');self.assertEqual(self.state['personalRequests'][self.key]['status'],'accepted')
    def test_explicit_wallet_and_reserved_materials_are_enforced_atomically(self):
        self.unlock();self.request('accept-personal-request');self.reject('fund-personal-request',fundingSource='personal')
        self.reject('fund-personal-request',fundingSource='mira')
        self.state['materialReserveTargets']['binding-thread']=1
        self.reject('fund-personal-request',fundingSource='shared')
        self.state['materialReserveTargets']['binding-thread']=0;self.state['personalFunds']['mira']=6
        before=self.state['sharedFunds'];self.request('fund-personal-request',fundingSource='personal')
        self.assertEqual(self.state['sharedFunds'],before);self.assertEqual(self.state['personalFunds']['mira'],0)
        self.assertEqual(self.state['materialInventory']['binding-thread'],0)
    def test_partial_cancellation_refunds_exact_original_source_once(self):
        self.state['personalFunds']['mira']=6;self.fund('personal');self.advance()
        self.request('cancel-personal-request');self.assertEqual(self.state['personalFunds']['mira'],6)
        self.assertEqual(self.state['sharedFunds'],80);self.assertEqual(self.state['materialInventory']['binding-thread'],2)
        self.assertEqual(self.state['personalRequests'][self.key]['completedWorkPhases'],0)
        self.reject('cancel-personal-request');self.assertEqual(self.state['residentKeepsakes']['mira'],[])
    def test_work_pauses_completes_once_and_never_awards_relationship_or_abilities(self):
        self.fund();self.advance();self.act('assign-resident',assignment='rest');self.advance(2)
        self.assertEqual(self.state['personalRequests'][self.key]['completedWorkPhases'],1)
        self.request('resume-personal-request');before=deepcopy(self.state);self.advance()
        self.assertEqual(self.state['residentKeepsakes']['mira'],[self.key])
        self.assertEqual(self.state['displayedKeepsakes']['mira'],[])
        for key in ('characterDevelopment','resonancePoints','relationshipDescription','sharedFunds'):self.assertEqual(self.state[key],before[key])
        self.reject('fund-personal-request',fundingSource='shared');self.reject('cancel-personal-request')
        self.advance();self.assertEqual(self.state['residentKeepsakes']['mira'],[self.key])
    def test_reading_and_displaying_are_free_owner_scoped_and_repeat_safe(self):
        self.fund();self.reject('display-keepsake',displayed=True);self.reject('read-personal-note');self.advance(2)
        before=deepcopy(self.state)
        for _ in range(2):self.request('read-personal-note');self.request('display-keepsake',displayed=True)
        self.assertEqual(self.state['displayedKeepsakes']['mira'],[self.key])
        for key in ('sharedFunds','personalFunds','resonancePoints','dayNumber','currentDayPhase'):self.assertEqual(self.state[key],before[key])
        self.request('display-keepsake',displayed=False);self.assertEqual(self.state['displayedKeepsakes']['mira'],[])
        self.assertEqual(self.state['residentKeepsakes']['mira'],[self.key])
    def test_work_continues_during_scholar_travel_but_remote_planning_is_blocked(self):
        self.fund();self.act('start-expedition');self.advance()
        self.reject('cancel-personal-request');self.act('choose-expedition-approach',approach='salvage');self.advance()
        self.assertEqual(self.state['personalRequests'][self.key]['status'],'complete')
        self.reject('read-personal-note')
    def test_two_residents_keep_work_and_ownership_independent(self):
        self.state['additionalResidents']['tamsin']['status']='resident';self.state['bedroomAssignments']['tamsin']='bedchamber'
        self.state['additionalResidents']['tamsin']['personalProject']['status']='complete'
        self.state['materialInventory']['binding-thread']=3;self.state['materialInventory']['porous-clay']=1
        self.fund();self.key='tamsin-repair-case';self.request('accept-personal-request');self.request('fund-personal-request',fundingSource='shared')
        self.advance(2)
        self.assertEqual(self.state['residentKeepsakes']['mira'],['mira-reading-folio'])
        self.assertEqual(self.state['residentKeepsakes']['tamsin'],['tamsin-repair-case'])
        self.assertEqual(self.state['sharedFunds'],66)
        mira=dialogue_context(self.state,'Your project?','mira')[0]['content'];tamsin=dialogue_context(self.state,'Your project?','tamsin')[0]['content']
        self.assertIn('cloth reading folio',mira);self.assertNotIn('offcut case',mira)
        self.assertIn('offcut case',tamsin);self.assertNotIn('cloth reading folio',tamsin)
    def test_skill_bonuses_do_not_shorten_personal_work(self):
        self.state['characterSkills']['mira']['artifice']=2;self.state['characterSkills']['mira']['scholarship']=2
        self.fund();self.advance();self.assertEqual(self.state['personalRequests'][self.key]['status'],'in-progress')
        self.assertEqual(self.state['personalRequests'][self.key]['completedWorkPhases'],1)
    def test_schema_migration_funding_retry_and_reload_preserve_money(self):
        self.unlock();self.request('accept-personal-request');old=deepcopy(self.state);old['schemaVersion']=15
        for key in ('personalRequests','residentKeepsakes','displayedKeepsakes'):old.pop(key)
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=?',(json.dumps(old),))
            store=GameStore(directory);self.assertTrue((Path(directory)/'campaign-before-schema-15-to-66.sqlite3').exists())
            def payload(kind,**fields):return {'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind,'requestId':self.key,**fields}}
            store.action(payload('accept-personal-request'));fund=payload('fund-personal-request',fundingSource='shared')
            once=store.action(fund);self.assertEqual(store.action(fund),once)
            loaded=GameStore(directory).read();self.assertEqual(loaded['sharedFunds'],74)
            self.assertEqual(loaded['personalRequests'][self.key]['fundingSource'],'shared')
