import json
import tempfile
import threading
import unittest
import urllib.request
import uuid
from server import create_server
from dialogue import DialogueService
from test_content_packs import zip_payload
from examples.build_expansion_fixture import fixture_files

class ExpansionHTTPTests(unittest.TestCase):
 def test_staged_pack_and_scene_routes_are_separate_from_game_actions(self):
  with tempfile.TemporaryDirectory() as directory:
   server=create_server('127.0.0.1',0,directory)
   server.provider_settings.save({'enabled':True,'model':'fixture','apiKey':'test-only','maxOutputTokens':1500})
   worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
   def request(path,payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
   def action(a):return request('/api/action',{'requestId':uuid.uuid4().hex,'expectedRevision':request('/api/state')['revision'],'action':a})
   try:
    before=request('/api/state');r=request('/api/expansion-packs/validate',zip_payload(fixture_files()))
    self.assertTrue(r['valid']);self.assertEqual(request('/api/state'),before)
    self.assertEqual(len(request('/api/expansion-packs')['packs']),1)
    self.assertEqual(len(request('/api/expansion-packs/preview',{'digest':r['digest']})['entries']),2)
    pack=request('/api/content-packs/validate',{'bundled':True});action({'type':'activate-content-pack','digest':pack['digest'],'contentReviewed':True})
    seed=next(r for r in request('/api/household-content')['residents']['mira']['scenes'] if r['participants']=='npc-player')
    s=action({'type':'propose-content-scene','ownerId':'mira','packDigest':pack['digest'],'seedId':seed['id'],'participants':['mira'],'prerequisitesReviewed':True,'requirementEvidence':['Fixture agreement.']*len(seed['requirements'])})
    key=next(iter(s['householdScenes']));scene=s['householdScenes'][key]
    server.dialogue=DialogueService(server.provider_settings,lambda *_:{'text':json.dumps({'title':'Quiet company','invitation':'Join me?','opening':'She sets her book aside.','replies':['She respects the choice.']*len(scene['choices'])})})
    d=request('/api/dialogue/draft',{'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'purpose':'scene-proposal','sceneId':key,'text':'A light invitation.'})
    self.assertEqual(d['status'],'ready')
    self.assertEqual(len(request('/api/dialogue/drafts?purpose=scene-proposal&scene='+key)['drafts']),1)
    self.assertEqual(request('/api/dialogue/drafts?purpose=scene-proposal&scene=unknown')['drafts'],[])
    saved=request('/api/dialogue/accept',{'draftId':d['id'],'contentReviewed':True})
    self.assertEqual(saved['householdScenes'][key]['status'],'draft')
   finally:server.shutdown();worker.join(timeout=5);server.server_close()
