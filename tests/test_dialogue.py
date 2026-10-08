from copy import deepcopy
import io
import json
import os
import tempfile
import unittest
import uuid
import zipfile
from dialogue import ProviderSettings, DialogueService, dialogue_context
from server import GameStore
from game import RuleError

class DialogueTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=GameStore(self.temp.name);self.settings=ProviderSettings(self.temp.name)
        self.settings.save({'enabled':True,'model':'example/text-model','apiKey':'test-secret-never-export','maxOutputTokens':500})
        self.calls=[]
        def complete(settings,messages):
            self.calls.append(messages)
            return {'text':'A quiet reply. <script>not executable</script>', 'usage':{'total_tokens':21}}
        self.service=DialogueService(self.settings,complete)
    def payload(self):return {'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision'],'text':'What are you reading?'}
    def action(self,kind,**fields):return self.store.action({'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision'],'action':{'type':kind,**fields}})
    def test_draft_is_nonmutating_retries_once_and_accept_only_changes_dialogue(self):
        before=self.store.read();payload=self.payload()
        draft=self.service.generate(self.store,payload)
        self.assertEqual(draft,self.service.generate(self.store,payload));self.assertEqual(len(self.calls),1)
        self.assertEqual(self.store.read(),before)
        after=self.service.accept(self.store,{'draftId':draft['id']})
        for key in before:
            if key not in ('conversation','revision'):self.assertEqual(before[key],after[key],key)
        self.assertEqual(after['revision'],before['revision']+1)
        self.assertEqual(after['conversation'][-1]['source'],'generated')
        self.assertEqual(self.service.accept(self.store,{'draftId':draft['id']}),after)
        self.assertEqual(GameStore(self.temp.name).read(),after)
    def test_stale_scene_rejected_and_draft_ids_cannot_be_reused(self):
        payload=self.payload();draft=self.service.generate(self.store,payload)
        self.action('advance');before=self.store.read()
        with self.assertRaises(RuleError):self.service.accept(self.store,{'draftId':draft['id']})
        self.assertEqual(self.store.read(),before)
        with self.assertRaises(RuleError):self.service.generate(self.store,{**payload,'text':'A changed request'})
        with self.assertRaises(RuleError):self.service.generate(self.store,{**payload,'requestId':uuid.uuid4().hex})
        self.assertEqual(len(self.calls),1)
    def test_disabled_away_failed_and_inflight_requests_do_not_commit(self):
        self.settings.save({'enabled':False,'model':'example/text-model','apiKey':'','maxOutputTokens':500})
        with self.assertRaises(RuleError):self.service.generate(self.store,self.payload())
        self.settings.save({'enabled':True,'model':'example/text-model','apiKey':'','maxOutputTokens':500})
        self.action('start-expedition')
        with self.assertRaises(RuleError):self.service.generate(self.store,self.payload())
        self.action('return-expedition');self.action('advance')
        before=self.store.read();payload=self.payload()
        def failed(*args):raise RuntimeError('test-secret-never-export')
        failed_service=DialogueService(self.settings,failed)
        draft=failed_service.generate(self.store,payload)
        self.assertEqual(draft['status'],'failed');self.assertNotIn('test-secret',json.dumps(draft))
        self.assertEqual(failed_service.generate(self.store,payload),draft)
        self.assertEqual(self.store.read(),before)
        with self.assertRaises(RuleError):self.service.accept(self.store,{'draftId':draft['id']})
    def test_settings_secrets_are_excluded_from_context_public_state_and_backup(self):
        self.assertTrue(self.settings.public()['hasApiKey'])
        self.assertNotIn('apiKey',self.settings.public())
        self.assertEqual(os.stat(self.settings.path).st_mode & 0o777,0o600)
        self.service.generate(self.store,self.payload())
        self.assertNotIn('test-secret',json.dumps(self.calls))
        with zipfile.ZipFile(io.BytesIO(self.store.backup_archive())) as archive:
            self.assertNotIn('provider-settings.json',archive.namelist())
            for name in archive.namelist():self.assertNotIn(b'test-secret-never-export',archive.read(name))
        self.settings.save({'enabled':True,'model':'example/text-model','maxOutputTokens':500,'removeApiKey':True})
        self.assertFalse(self.settings.public()['enabled']);self.assertFalse(self.settings.public()['hasApiKey'])
    def test_settings_validation_keeps_previous_configuration(self):
        before=self.settings.read()
        for changed in ({'maxOutputTokens':True},{'maxOutputTokens':5000},{'model':'https://bad?key=x'},{'enabled':'yes'},{'apiKey':'contains space'}):
            with self.assertRaises(RuleError):self.settings.save({**before,**changed})
            self.assertEqual(self.settings.read(),before)
    def test_context_is_scoped_and_unknown_drafts_do_not_cross_campaigns(self):
        state=self.store.read();state['hiddenTruth']='never-share';state['privateNotes']='never-share'
        context=dialogue_context(state,'Hello')
        self.assertNotIn('never-share',json.dumps(context))
        self.assertNotIn('sharedFunds',json.dumps(context))
        draft=self.service.generate(self.store,self.payload())
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(RuleError):self.service.accept(GameStore(other),{'draftId':draft['id']})

    def test_spell_context_includes_only_miras_tested_work_and_ritual_status(self):
        state=self.store.read()
        state['spellbook']=[{'id':'spell-1','ownerId':'mira','name':'Mira working','formId':'root-song','status':'learned','intent':'private design note'},
            {'id':'spell-2','ownerId':'founder','name':'founder-private-design','formId':'warm-twist','status':'learned'},
            {'id':'spell-3','ownerId':'mira','name':'untested-draft','formId':'warm-twist','status':'draft'}]
        state['preparedSpells']['mira']=['spell-1']
        context=json.dumps(dialogue_context(state,'What have you learned?'))
        self.assertIn('Mira working',context);self.assertIn('concordantLesson',context)
        for text in ('private design note','founder-private-design','untested-draft'):self.assertNotIn(text,context)

    def resident_fixture(self):
        state=self.store.read();state['additionalResidents']['tamsin']['status']='resident'
        state['bedroomAssignments']['tamsin']='west-chamber';state['housingRooms']['west-chamber']['status']='complete'
        state['additionalResidents']['tamsin']['conversation']=[{'speaker':'Tamsin','text':'My own conversation only.'}]
        state['conversation']=[{'speaker':'Mira','text':'Private Mira history: do-not-share.'}]
        with self.store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))
        return state
    def test_new_resident_context_and_acceptance_do_not_mix_conversations(self):
        before=self.resident_fixture();payload={**self.payload(),'characterId':'tamsin'}
        draft=self.service.generate(self.store,payload)
        self.assertEqual(draft['characterId'],'tamsin');self.assertEqual(len(self.calls),1)
        context=json.dumps(self.calls[0]);self.assertIn('My own conversation only.',context);self.assertNotIn('do-not-share',context)
        self.assertNotIn('Trusted collaborators',context);self.assertIn('private one-bed room',context)
        self.assertEqual(self.service.generate(self.store,payload),draft)
        with self.assertRaises(RuleError):self.service.generate(self.store,{**payload,'characterId':'mira'})
        after=self.service.accept(self.store,{'draftId':draft['id']})
        self.assertEqual(after['conversation'],before['conversation'])
        self.assertEqual(after['additionalResidents']['tamsin']['conversation'][-1]['speaker'],'Tamsin')
        for key in before:
            if key not in ('additionalResidents','revision'):self.assertEqual(after[key],before[key],key)
        for key in before['additionalResidents']['tamsin']:
            if key!='conversation':self.assertEqual(after['additionalResidents']['tamsin'][key],before['additionalResidents']['tamsin'][key])
        self.assertEqual(self.service.accept(self.store,{'draftId':draft['id']}),after)
    def test_absent_candidate_and_non_npc_dialogue_are_rejected(self):
        for who in ('tamsin','founder','eris','selene',None,[]):
            with self.assertRaises(RuleError):self.service.generate(self.store,{**self.payload(),'characterId':who})
        self.assertEqual(self.calls,[])
    def test_legacy_mira_drafts_remain_recoverable_and_acceptable(self):
        payload=self.payload();draft=self.service.generate(self.store,payload)
        draft.pop('characterId')
        with self.store.connect() as db:db.execute('UPDATE dialogue_drafts SET result=? WHERE id=?',(json.dumps(draft),draft['id']))
        self.assertEqual(self.service.generate(self.store,{**payload,'characterId':'mira'}),draft)
        after=self.service.accept(self.store,{'draftId':draft['id']});self.assertEqual(after['conversation'][-1]['speaker'],'Mira')

    def test_concurrent_check_returns_processing_without_second_provider_call(self):
        import threading
        entered=threading.Event();release=threading.Event()
        calls=[]
        def slow(*args):
            calls.append(1);entered.set();release.wait(3)
            return {'text':'Finished once.','usage':{}}
        service=DialogueService(self.settings,slow);payload=self.payload();results=[]
        thread=threading.Thread(target=lambda:results.append(service.generate(self.store,payload)))
        thread.start()
        try:
            self.assertTrue(entered.wait(2))
            self.assertEqual(service.generate(self.store,payload)['status'],'processing')
        finally:release.set();thread.join()
        self.assertEqual(len(calls),1)
        self.assertEqual(service.generate(self.store,payload)['text'],'Finished once.')

    def test_http_settings_drafts_and_acceptance_use_current_campaign_only(self):
        import threading
        import urllib.request
        from server import create_server
        server=create_server('127.0.0.1',0,self.temp.name)
        server.dialogue.completion=lambda *args:{'text':'A short reply.','usage':{'total_tokens':9}}
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        def request(path,payload=None):
            req=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req) as response:return json.load(response)
        try:
            self.assertNotIn('apiKey',request('/api/provider'))
            draft=request('/api/dialogue/draft?campaign=default',self.payload())
            self.assertEqual(draft['status'],'ready')
            self.assertEqual(request('/api/dialogue/drafts')['drafts'][0]['id'],draft['id'])
            self.assertEqual(request('/api/state')['revision'],0)
            after=request('/api/dialogue/accept?campaign=default',{'draftId':draft['id']})
            self.assertEqual(after['revision'],1)
            self.assertEqual(after['conversation'][-1]['text'],'A short reply.')
            self.assertEqual(request('/api/dialogue/accept',{'draftId':draft['id']}),after)
        finally:server.shutdown();server.server_close();thread.join()

    def test_provider_transport_uses_bounded_text_request_and_usage(self):
        from unittest.mock import patch
        from dialogue import provider_completion
        response=io.BytesIO(json.dumps({'choices':[{'message':{'content':'A short answer.'}}],'usage':{'total_tokens':8,'prompt_tokens':5,'completion_tokens':3,'unexpected':'ignored'}}).encode())
        with patch('dialogue.urllib.request.urlopen',return_value=response) as transport:
            result=provider_completion(self.settings.read(),[{'role':'user','content':'Hello'}])
        request=transport.call_args.args[0];payload=json.loads(request.data)
        self.assertEqual(request.full_url,'https://openrouter.ai/api/v1/chat/completions')
        self.assertEqual(payload['max_tokens'],500)
        self.assertFalse(payload['stream']);self.assertNotIn('tools',payload)
        self.assertEqual(result['usage'],{'total_tokens':8,'prompt_tokens':5,'completion_tokens':3})
    def test_provider_transport_rejects_empty_reply_without_exposing_error_body(self):
        from unittest.mock import patch
        from dialogue import provider_completion
        with patch('dialogue.urllib.request.urlopen',return_value=io.BytesIO(b'{"choices":[]}')):
            with self.assertRaises(RuleError) as caught:provider_completion(self.settings.read(),[])
        self.assertNotIn('test-secret',str(caught.exception))

    def test_journal_draft_is_reviewed_idempotent_and_changes_only_journal(self):
        self.action('advance');before=self.store.read()
        payload={**self.payload(),'purpose':'journal'}
        draft=self.service.generate(self.store,payload)
        self.assertEqual(draft,self.service.generate(self.store,payload));self.assertEqual(len(self.calls),1)
        self.assertEqual(self.store.read(),before)
        self.assertEqual(draft['sourceResults'],before['lastPhaseSummary'])
        after=self.service.accept(self.store,{'draftId':draft['id']})
        for key in before:
            if key not in ('journal','revision'):self.assertEqual(before[key],after[key],key)
        self.assertEqual(after['journal'][-1]['source'],'generated')
        self.assertEqual(after['journal'][-1]['sourceResults'],before['lastPhaseSummary'])
        self.assertEqual(self.service.accept(self.store,{'draftId':draft['id']}),after)
        self.assertEqual(GameStore(self.temp.name).read(),after)

    def test_journal_requires_results_and_preserves_request_identity_and_revision(self):
        with self.assertRaises(RuleError):self.service.generate(self.store,{**self.payload(),'purpose':'journal'})
        self.action('advance');payload={**self.payload(),'purpose':'journal'}
        draft=self.service.generate(self.store,payload)
        with self.assertRaises(RuleError):self.service.generate(self.store,{**payload,'purpose':'dialogue'})
        self.action('advance');before=self.store.read()
        with self.assertRaises(RuleError):self.service.accept(self.store,{'draftId':draft['id']})
        self.assertEqual(before,self.store.read())

    def test_journal_context_contains_only_results_and_works_while_away(self):
        from dialogue import journal_context
        state=self.store.read();state['privateNotes']='DO-NOT-SEND';state['conversation']=[{'speaker':'You','text':'DO-NOT-SEND'}]
        state['lastPhaseSummary']=['A restful phase.']
        context=json.dumps(journal_context(state,'Keep it brief.'))
        self.assertIn('A restful phase.',context);self.assertNotIn('DO-NOT-SEND',context)
        self.assertNotIn('sharedFunds',context);self.assertNotIn('apiKey',context)
        self.action('advance');self.action('start-expedition');before=self.store.read()
        self.assertEqual(self.service.generate(self.store,{**self.payload(),'purpose':'journal'})['status'],'ready')
        self.assertEqual(before,self.store.read())

    def test_journal_http_recovery_filters_before_limiting(self):
        import threading
        import urllib.request
        from server import create_server
        self.action('advance')
        npc=self.service.generate(self.store,self.payload())
        for _ in range(9):self.service.generate(self.store,{**self.payload(),'purpose':'journal'})
        server=create_server('127.0.0.1',0,self.temp.name)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        def get(query):
            with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/dialogue/drafts?'+query) as response:return json.load(response)['drafts']
        try:
            journals=get('purpose=journal');self.assertEqual(len(journals),8)
            self.assertTrue(all(draft['purpose']=='journal' for draft in journals))
            self.assertEqual([draft['id'] for draft in get('character=mira')],[npc['id']])
            self.assertEqual(get('purpose=journal&character=mira'),[])
        finally:server.shutdown();server.server_close();thread.join()
