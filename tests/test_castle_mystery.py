from copy import deepcopy
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
import urllib.request
import uuid
import zipfile
import game as g
import castle_mystery as m
from dialogue import dialogue_context, journal_context
from candidate_proposals import candidate_context
from server import GameStore, create_server

class CastleMysteryTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,**fields):return g.apply_action(self.s,{'type':kind,**fields})
    def ready(self):
        self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.s['miraArchiveProject']['status']='complete'
        g.learn_for_character(self.s,'founder','gentle-refraction')
    def investigate(self,key):
        self.act('start-mystery',leadId=key)
        for _ in range(m.LEADS[key]['phases']):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(before,self.s)
    def test_private_truth_and_future_evidence_never_in_public_or_unshared_prompts(self):
        secret='PRIVATE_FOUNDATION_SENTINEL'
        self.s['privateCastleLore']['foundation']=secret
        self.s['privateCastleLore']['evidence']['hearth-margin']=secret
        for result in (g.public_state(self.s), dialogue_context(self.s,'Hello'), journal_context(self.s,'Write notes'),candidate_context(self.s,'An adult visitor')):
            text=json.dumps(result)
            self.assertNotIn(secret,text)
            self.assertNotIn('privateCastleLore',text)
    def test_prerequisites_cannot_be_bypassed_and_only_personal_knowledge_counts(self):
        self.reject('start-mystery',leadId='hearth-margin')
        self.ready();self.reject('start-mystery',leadId='founding-record')
        self.reject('start-mystery',leadId='window-measure')
        self.investigate('hearth-margin');g.character_principles(self.s,'founder').remove('gentle-refraction')
        self.reject('start-mystery',leadId='window-measure')
        self.reject('start-mystery',leadId=[])
    def test_investigation_pauses_and_has_no_offline_or_bonus_work(self):
        self.ready();self.s['characterBuilds']['founder']['attributes']['insight']=3
        self.act('start-mystery',leadId='hearth-margin');self.act('advance')
        self.assertEqual(self.s['castleMystery']['project']['completedWorkPhases'],1)
        self.act('assign-founder',assignment='rest');self.act('advance')
        self.assertEqual(self.s['castleMystery']['project']['completedWorkPhases'],1)
        before=deepcopy(self.s);g.public_state(self.s);m.view(self.s);self.assertEqual(before,self.s)
        self.act('resume-mystery');self.act('advance')
        self.assertIn('hearth-margin',self.s['castleMystery']['discoveries'])
    def test_complete_history_is_consistent_no_intimacy_cost_and_awards_once(self):
        self.ready();packet=deepcopy(self.s['privateCastleLore']);funds=self.s['sharedFunds'];materials=deepcopy(self.s['materialInventory'])
        original_leads=('hearth-margin','archive-leaf','window-measure','founding-record')
        for key in original_leads:self.investigate(key)
        self.assertEqual(self.s['privateCastleLore'],packet)
        self.assertEqual(self.s['sharedFunds'],funds)
        self.assertEqual(self.s['materialInventory'],materials)
        self.assertEqual(self.s['resonancePoints'],0)
        self.assertEqual(len(self.s['castleMystery']['discoveries']),4)
        self.assertEqual(g.character_sheet(self.s,'founder')['earnedAdvancement'],4)
        for key in original_leads:
            self.assertEqual(self.s['castleMystery']['discoveries'][key]['text'],packet['evidence'][key])
            self.reject('start-mystery',leadId=key)
    def test_sharing_is_explicit_person_scoped_idempotent_and_no_reward(self):
        self.ready();self.investigate('hearth-margin')
        text=self.s['castleMystery']['discoveries']['hearth-margin']['text']
        self.assertNotIn(text,json.dumps(dialogue_context(self.s,'Hello')))
        self.reject('share-mystery',characterId='mira',leadId='founding-record')
        self.act('share-mystery',characterId='mira',leadId='hearth-margin')
        before=deepcopy(self.s)
        self.act('share-mystery',characterId='mira',leadId='hearth-margin');self.assertEqual(before,self.s)
        facts=json.loads(dialogue_context(self.s,'Hello')[0]['content'].split('Scene facts: ',1)[1])
        self.assertEqual(facts['sharedCastleEvidence'][0]['text'],text)
        self.assertEqual(m.shared_evidence(self.s,'tamsin'),[])
    def test_cancel_and_home_guard_keep_discoveries(self):
        self.ready();self.investigate('hearth-margin');self.act('start-mystery',leadId='archive-leaf');self.act('advance')
        self.act('cancel-mystery');self.assertEqual(len(self.s['castleMystery']['discoveries']),1)
        self.reject('resume-mystery');self.reject('assign-founder',assignment='mystery')
        self.act('start-expedition');self.reject('start-mystery',leadId='archive-leaf')
        self.reject('share-mystery',characterId='mira',leadId='hearth-margin')
    def test_migration_and_reload_do_not_reroll_foundation_or_advance_investigation(self):
        old=deepcopy(self.s);old.pop('privateCastleLore');old.pop('castleMystery');old['schemaVersion']=26
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);upgraded=store.read()
            self.assertTrue((Path(directory)/'campaign-before-schema-26-to-66.sqlite3').exists())
            for key,value in old.items():
                if key not in ('schemaVersion','revision'):self.assertEqual(upgraded[key],value)
            self.assertEqual(upgraded,GameStore(directory).read())
            with zipfile.ZipFile(io.BytesIO(store.backup_archive())) as archive:
                archive.extract('campaign.sqlite3',Path(directory)/'restored')
            self.assertEqual(GameStore(Path(directory)/'restored').read()['privateCastleLore'],upgraded['privateCastleLore'])
    def test_real_http_state_export_actions_and_conflicts_redact_private_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            server=create_server('127.0.0.1',0,directory)
            store=server.campaigns.get('default');state=store.read();state['privateCastleLore']['foundation']='HIDDEN_HTTP_SENTINEL'
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))
            worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
            def request(path,payload=None):
                req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=json.dumps(payload).encode() if payload else None,headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
                except urllib.error.HTTPError as error:return json.load(error)
            try:
                for path in ('/api/state','/api/export'):
                    body=request(path);self.assertNotIn('HIDDEN_HTTP_SENTINEL',json.dumps(body));self.assertNotIn('privateCastleLore',body)
                payload={'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'advance'}}
                self.assertNotIn('privateCastleLore',request('/api/action',payload))
                payload['requestId']=uuid.uuid4().hex
                self.assertNotIn('privateCastleLore',request('/api/action',payload)['state'])
            finally:server.shutdown();worker.join(timeout=5);server.server_close()
