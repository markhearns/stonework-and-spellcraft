"""Exercise real HTTP routes that the template harness deliberately bypasses."""
import json
import tempfile
import threading
import unittest
import urllib.request
import uuid
from server import create_server
from dialogue import DialogueService
from test_candidate_proposals import candidate_fixture

class CandidateHTTPTests(unittest.TestCase):
    def test_draft_filter_recheck_approval_and_campaign_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            server=create_server('127.0.0.1',0,directory)
            server.provider_settings.save({'enabled':True,'model':'test/model','apiKey':'fixture','maxOutputTokens':1000})
            server.dialogue=DialogueService(server.provider_settings,lambda settings,messages:{'text':json.dumps(candidate_fixture()),'usage':{}})
            worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
            def request(path,payload=None):
                data=json.dumps(payload).encode() if payload is not None else None
                req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=data,headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
            try:
                state=request('/api/state?campaign=default')
                draft=request('/api/dialogue/draft?campaign=default',{'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'purpose':'candidate-proposal','text':'An adult vampire artisan.'})
                self.assertEqual(draft['status'],'ready')
                self.assertEqual(len(request('/api/dialogue/drafts?campaign=default&purpose=candidate-proposal')['drafts']),1)
                self.assertEqual(request('/api/dialogue/drafts?campaign=default&purpose=dialogue')['drafts'],[])
                checked=request('/api/candidate/review?campaign=default',{'draftId':draft['id'],'expectedRevision':state['revision']})
                self.assertEqual(checked['proposal'],draft['proposal'])
                accepted=request('/api/dialogue/accept?campaign=default',{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
                who='summoned-'+draft['id'];self.assertIn(who,accepted['reviewedCandidates'])
                self.assertNotIn(who,accepted['people'])
                self.assertIn(who,accepted['summoningView']['candidates'])
                self.assertEqual(request('/api/health')['version'],'0.105')
            finally:
                server.shutdown();worker.join(timeout=5);server.server_close()
