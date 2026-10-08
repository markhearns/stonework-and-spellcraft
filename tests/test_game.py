import base64
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import uuid
from game import ORIGINAL_ASSETS, new_campaign, apply_action, RuleError, resonance_forecast
from server import GameStore, ConflictError, create_server

class RuleTests(unittest.TestCase):
    def test_cosmetic_and_conversation_actions_do_not_advance_or_farm(self):
        state = new_campaign()
        for _ in range(5):
            for action in [
                {'type':'decorate','roomId':'common-room','furnishing':'velvet-settee'},
                {'type':'wardrobe','outerLayer':'plum-shawl'},
                {'type':'talk','topic':'flirt'},
            ]:
                apply_action(state, action)
        self.assertEqual((state['dayNumber'],state['currentDayPhase'],state['resonancePoints']), (1,'afternoon',0))
        self.assertEqual(resonance_forecast(state), 0)
        apply_action(state, {'type':'accept-invitation'})
        self.assertEqual(state['resonancePoints'],2)
        with self.assertRaises(RuleError): apply_action(state, {'type':'accept-invitation'})
        apply_action(state, {'type':'advance'})
        self.assertEqual(state['resonancePoints'],3)
        apply_action(state, {'type':'decorate','roomId':'common-room','furnishing':'reading-table'})
        apply_action(state, {'type':'advance'})
        self.assertEqual(state['resonancePoints'],3)

    def test_phase_wrap_and_research_finish_once(self):
        state = new_campaign()
        apply_action(state, {'type':'start-research'})
        with self.assertRaises(RuleError): apply_action(state, {'type':'start-research'})
        for _ in range(3): apply_action(state, {'type':'advance'})
        self.assertEqual((state['dayNumber'],state['currentDayPhase']), (2,'afternoon'))
        self.assertEqual(state['researchStatus'],'complete')
        self.assertEqual(state['sharedFunds'],60)
        apply_action(state, {'type':'advance'})
        self.assertEqual(state['researchCompletedPhases'],3)

    def test_saved_style_and_invalid_room(self):
        state = new_campaign()
        apply_action(state, {'type':'wardrobe','outerLayer':'plum-shawl'})
        apply_action(state, {'type':'save-style','name':'Tea time'})
        apply_action(state, {'type':'wardrobe','outerLayer':'none'})
        apply_action(state, {'type':'wear-style','name':'Tea time'})
        self.assertEqual(state['wardrobe']['outerLayer'],'plum-shawl')
        with self.assertRaises(RuleError): apply_action(state, {'type':'decorate','roomId':'library','furnishing':'velvet-settee'})

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = GameStore(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def request(self, action):
        return {'requestId':uuid.uuid4().hex, 'expectedRevision':self.store.read()['revision'], 'action':action}
    def test_retry_is_idempotent_and_survives_restart(self):
        request = self.request({'type':'advance'})
        first = self.store.action(request)
        self.assertEqual(first,self.store.action(request))
        reopened = GameStore(self.temp.name)
        self.assertEqual(first,reopened.read())
        self.assertEqual(first,reopened.action(request))
    def test_stale_write_and_reused_id_are_rejected(self):
        request = self.request({'type':'advance'})
        self.store.action(request)
        with self.assertRaises(ConflictError): self.store.action({**request,'requestId':uuid.uuid4().hex})
        with self.assertRaises(RuleError): self.store.action({**request,'action':{'type':'talk','topic':'home'}})
        self.assertEqual(self.store.read()['revision'],1)
    def test_failure_does_not_commit(self):
        before = self.store.read()
        with self.assertRaises(RuleError): self.store.action(self.request({'type':'decorate','roomId':'fake','furnishing':'none'}))
        self.assertEqual(before,self.store.read())
    def test_artwork_rollback_never_changes_game_time(self):
        data = (Path(__file__).resolve().parents[1]/'static/assets/portraits/mira.webp').read_bytes()
        path = self.store.upload({'imageData':'data:image/webp;base64,'+base64.b64encode(data).decode()})
        self.store.action(self.request({'type':'accept-artwork','assetId':'mira','assetPath':path}))
        accepted = self.store.read()
        self.assertEqual(accepted['assetOverrides']['mira'],path)
        self.store.action(self.request({'type':'rollback-artwork','assetId':'mira'}))
        rolled = self.store.read()
        self.assertEqual(rolled['assetOverrides']['mira'],ORIGINAL_ASSETS['mira'])
        self.assertEqual(rolled['currentDayPhase'],'afternoon')
        self.assertEqual(rolled['resonancePoints'],0)
        with self.assertRaises(RuleError): self.store.upload({'imageData':'data:image/svg+xml;base64,AAAA'})

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.server=create_server('127.0.0.1',0,self.temp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def test_actual_http_state_assets_mutation_and_export(self):
        for path in ['/','/app.js','/style.css','/assets/rooms/common-room.webp','/assets/portraits/mira.webp','/api/health']:
            with urllib.request.urlopen(self.base+path) as response:
                self.assertEqual(response.status,200)
                self.assertGreater(len(response.read()),10)
        payload={'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'advance'}}
        request=urllib.request.Request(self.base+'/api/action',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request) as response:
            self.assertEqual(json.load(response)['currentDayPhase'],'evening')
        with urllib.request.urlopen(self.base+'/api/export') as response:
            self.assertIn('attachment',response.headers['Content-Disposition'])
            self.assertEqual(json.load(response)['revision'],1)
    def test_cross_origin_and_path_traversal(self):
        request=urllib.request.Request(self.base+'/api/action',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://untrusted.example'})
        with self.assertRaises(urllib.error.HTTPError) as raised: urllib.request.urlopen(request)
        self.assertEqual(raised.exception.code,403)
        with self.assertRaises(urllib.error.HTTPError) as raised: urllib.request.urlopen(self.base+'/%2e%2e/server.py')
        self.assertEqual(raised.exception.code,404)

if __name__=='__main__': unittest.main()
