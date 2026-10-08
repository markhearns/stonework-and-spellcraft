"""Real HTTP coverage for offline pool generation and owner-scoped story recovery."""
import json
import tempfile
import threading
import unittest
import urllib.request
import uuid
from server import create_server

class StoryHTTPTests(unittest.TestCase):
    def test_offline_drafts_owner_scope_and_acceptance(self):
        with tempfile.TemporaryDirectory() as d:
            server=create_server('127.0.0.1',0,d)
            worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
            def request(path,payload=None):
                data=None if payload is None else json.dumps(payload).encode()
                req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=data,headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
            try:
                state=request('/api/state');self.assertIn('Dryad',state['characterPool']['ancestries']);self.assertIn('Nymph',state['characterPool']['ancestries']);self.assertNotIn('Angel',state['characterPool']['ancestries'])
                candidate=request('/api/dialogue/draft',{'requestId':uuid.uuid4().hex,'purpose':'candidate-proposal','source':'offline','poolChoices':{'ancestry':'Nymph'},'expectedRevision':state['revision'],'text':'A new visitor.'})
                self.assertEqual(candidate['proposal']['ancestryLabel'],'Nymph')
                draft=request('/api/dialogue/draft',{'requestId':uuid.uuid4().hex,'purpose':'story-proposal','source':'offline','ownerId':'mira','packageId':'personal-folio','expectedRevision':state['revision'],'text':'Her own story.'})
                self.assertEqual(draft['status'],'ready')
                rows=request('/api/dialogue/drafts?purpose=story-proposal&owner=mira')['drafts'];self.assertEqual([r['id'] for r in rows],[draft['id']])
                self.assertEqual(request('/api/dialogue/drafts?purpose=story-proposal&owner=founder')['drafts'],[])
                request('/api/story/review',{'draftId':draft['id'],'expectedRevision':state['revision']})
                result=request('/api/dialogue/accept',{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
                self.assertEqual(len(result['personalStoryView']['stories']),1);self.assertEqual(result['sharedFunds'],state['sharedFunds'])
                self.assertNotIn('privateCastleLore',result)
            finally:server.shutdown();worker.join(5);server.server_close()
