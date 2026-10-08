import base64
import copy
import io
import json
import tempfile
import threading
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

from game import RuleError
from server import GameStore, create_server
from portrait_generation import PortraitSettings, PortraitService, provider_image

PNG='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='


class PortraitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        self.store=GameStore(self.directory,start_type='fresh')
        self.settings=PortraitSettings(self.directory)
        self.settings.save({'enabled':True,'model':'fixture/image','apiKey':'test-secret'})
        self.calls=[]
        def transport(settings,prompt):self.calls.append(prompt);return PNG
        self.service=PortraitService(self.settings,transport)
        self.act({'type':'save-founder-profile','name':'Aster','age':28,'appearanceDescription':'Black hair'})

    def act(self,action,store=None):
        store=store or self.store
        return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action})

    def request(self):return {'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision']}

    def test_preview_retry_accept_and_backup_preserve_state_and_art(self):
        old=self.store.upload({'imageData':'data:image/webp;base64,'+base64.b64encode(b'RIFF0000WEBPfixture').decode()})
        self.act({'type':'accept-artwork','assetId':'founder','assetPath':old})
        before=self.store.read();request=self.request();draft=self.service.generate(self.store,request)
        self.assertEqual(draft['status'],'ready');self.assertEqual(self.store.read(),before)
        self.assertEqual(self.service.generate(self.store,request),draft);self.assertEqual(len(self.calls),1)
        self.assertEqual(PortraitService(self.settings).list(GameStore(self.directory))['drafts'][0],draft)
        accept={'requestId':uuid.uuid4().hex,'expectedRevision':before['revision'],'action':{'type':'accept-generated-portrait','draftId':draft['id']}}
        accepted=self.store.action(accept)
        self.assertEqual(self.store.action(accept),accepted)
        self.assertEqual(accepted['assetOverrides']['founder'],draft['assetPath'])
        self.assertIn(old,accepted['assetHistory']['founder'])
        self.assertEqual(accepted['sharedFunds'],before['sharedFunds'])
        self.assertEqual(accepted['dayNumber'],before['dayNumber'])
        with zipfile.ZipFile(io.BytesIO(self.store.backup_archive())) as z:
            self.assertIn('assets/'+draft['assetPath'].split('/')[-1],z.namelist())
            self.assertNotIn('portrait-provider-settings.json',z.namelist())
        self.act({'type':'rollback-artwork','assetId':'founder'})
        self.assertEqual(self.store.read()['assetOverrides']['founder'],old)

    def test_stale_and_cross_campaign_acceptance_fail(self):
        draft=self.service.generate(self.store,self.request())
        self.act({'type':'save-founder-profile','name':'Different','age':30})
        before=self.store.read()
        with self.assertRaises(RuleError):self.act({'type':'accept-generated-portrait','draftId':draft['id']})
        self.assertEqual(self.store.read(),before)
        other=GameStore(self.directory/'other',start_type='fresh')
        with self.assertRaises(RuleError):self.act({'type':'accept-generated-portrait','draftId':draft['id']},other)
        self.assertEqual(self.service.list(other)['drafts'],[])

    def test_settings_key_retention_removal_and_disabled_request(self):
        self.assertNotIn('test-secret',json.dumps(self.settings.public()))
        self.settings.save({'enabled':True,'model':'fixture/other','apiKey':''})
        self.assertEqual(self.settings.read()['apiKey'],'test-secret')
        self.settings.save({'enabled':True,'model':'fixture/other','removeApiKey':True})
        self.assertFalse(self.settings.public()['enabled']);self.assertFalse(self.settings.public()['hasApiKey'])
        with self.assertRaises(RuleError):self.service.generate(self.store,self.request())
        self.assertEqual(self.calls,[])
        self.assertEqual(self.settings.path.stat().st_mode&0o777,0o600)

    def test_failed_or_invalid_image_has_no_state_effect_and_is_not_reissued(self):
        for output in ['data:image/svg+xml;base64,AAAA','data:image/png;base64,AAAA','https://untrusted.example/image.png']:
            calls=[]
            service=PortraitService(self.settings,lambda c,p:calls.append(p) or output)
            request=self.request();before=self.store.read()
            draft=service.generate(self.store,request)
            self.assertEqual(draft['status'],'failed');self.assertEqual(self.store.read(),before)
            service.generate(self.store,request);self.assertEqual(len(calls),1)
            with self.assertRaises(RuleError):self.act({'type':'accept-generated-portrait','draftId':draft['id']})

    def test_processing_recovery_and_abandon_do_not_duplicate_requests(self):
        started=threading.Event();finish=threading.Event();calls=[];results=[]
        def transport(c,p):calls.append(p);started.set();finish.wait(3);return PNG
        service=PortraitService(self.settings,transport);request=self.request()
        worker=threading.Thread(target=lambda:results.append(service.generate(self.store,request)))
        worker.start()
        try:
            self.assertTrue(started.wait(2))
            self.assertEqual(service.generate(self.store,request)['status'],'processing')
            with self.assertRaises(RuleError):service.generate(self.store,self.request())
            self.assertEqual(service.abandon(self.store,{'draftId':request['requestId']})['status'],'abandoned')
        finally:finish.set();worker.join(4)
        self.assertEqual(len(calls),1);self.assertEqual(results[0]['status'],'abandoned')
        self.assertEqual(self.store.read()['assetOverrides'],{})

    def test_request_validation_and_identifier_collision(self):
        with self.assertRaises(RuleError):self.service.generate(self.store,{'requestId':'bad'})
        with self.assertRaises(RuleError):self.service.generate(self.store,{'requestId':uuid.uuid4().hex,'expectedRevision':-1})
        req=self.request();self.service.generate(self.store,req)
        with self.assertRaises(RuleError):self.service.generate(self.store,{**req,'extra':'changed'})
        other=GameStore(self.directory/'new',start_type='fresh')
        with self.assertRaises(RuleError):self.service.generate(other,{'requestId':uuid.uuid4().hex,'expectedRevision':other.read()['revision']})

    def test_provider_transport_is_bounded_and_uses_image_endpoint(self):
        data=PNG.split(',',1)[1]
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):self.limit=n;return json.dumps({'data':[{'b64_json':data}]}).encode()
        response=Response()
        with patch('portrait_generation.urllib.request.urlopen',return_value=response) as send:
            self.assertEqual(provider_image(self.settings.read(),'portrait'),PNG)
            req=send.call_args.args[0]
            self.assertEqual(req.full_url,'https://openrouter.ai/api/v1/images')
            body=json.loads(req.data);self.assertEqual(body['n'],1);self.assertFalse(body['stream'])
            self.assertEqual(response.limit,9_000_001)
        with patch('portrait_generation.urllib.request.urlopen',side_effect=RuntimeError('test-secret')):
            with self.assertRaises(RuleError) as raised:provider_image(self.settings.read(),'portrait')
            self.assertNotIn('test-secret',str(raised.exception))

    def test_real_http_routes_and_campaign_acceptance(self):
        import urllib.request
        server=create_server('127.0.0.1',0,self.directory);server.portraits=self.service
        worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
        def request(path,payload=None):
            req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
        try:
            self.assertTrue(request('/api/portrait-settings')['enabled'])
            draft=request('/api/portrait-draft?campaign=default',self.request())
            self.assertEqual(request('/api/portrait-drafts?campaign=default')['drafts'][0],draft)
            state=request('/api/action?campaign=default',{'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision'],'action':{'type':'accept-generated-portrait','draftId':draft['id']}})
            self.assertEqual(state['assetOverrides']['founder'],draft['assetPath'])
        finally:server.shutdown();worker.join(3);server.server_close()
