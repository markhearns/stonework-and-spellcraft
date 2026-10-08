import base64
from concurrent.futures import ThreadPoolExecutor
import json
import io
import sqlite3
import zipfile
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import uuid
from server import CampaignLibrary, GameStore, RuleError, create_server

class CampaignTests(unittest.TestCase):
    def test_create_retry_rename_reload_isolation_and_mode_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            library=CampaignLibrary(directory)
            old=library.get('default').read()
            key='c-'+uuid.uuid4().hex
            payload={'campaignId':key,'name':'A second notebook','mode':'solo'}
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(library.create,[payload,payload]))
            self.assertEqual(results,[{'campaignId':key}]*2)
            self.assertEqual(len(library.list()),2)
            store=library.get(key)
            action={'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'rename-campaign','name':'A different title'}}
            store.action(action)
            self.assertEqual(library.create(payload),{'campaignId':key})
            self.assertEqual(library.get('default').read(),old)
            self.assertEqual(CampaignLibrary(directory).get(key).read()['campaignName'],'A different title')
            for bad in ({**payload,'name':'Other'},{**payload,'mode':'coop'},{**payload,'campaignId':'../elsewhere'}):
                with self.assertRaises(RuleError):library.create(bad)
            for key in ('../elsewhere','missing','c-'+uuid.uuid4().hex):
                with self.assertRaises(RuleError):library.get(key)
            self.assertEqual(len(library.list()),2)

    def test_http_campaign_scopes_cover_state_actions_exports_uploads_and_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            server=create_server('127.0.0.1',0,directory)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            def request(path,payload=None):
                req=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req) as response:return response.status,response.read()
                except urllib.error.HTTPError as error:return error.code,error.read()
            try:
                key='c-'+uuid.uuid4().hex
                self.assertEqual(request('/api/campaigns',{'campaignId':key,'name':'Second','mode':'solo'})[0],200)
                state=json.loads(request('/api/state?campaign='+key)[1])
                action={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'advance'}}
                after=json.loads(request('/api/action?campaign='+key,action)[1])
                self.assertEqual(after['currentDayPhase'],'evening')
                self.assertEqual(json.loads(request('/api/state')[1])['currentDayPhase'],'afternoon')
                # The same request id in a different campaign belongs to that campaign's journal.
                self.assertEqual(request('/api/action',action)[0],200)
                conflict={**action,'requestId':uuid.uuid4().hex}
                status,body=request('/api/action?campaign='+key,conflict)
                self.assertEqual(status,409);self.assertEqual(json.loads(body)['state']['campaignName'],'Second')
                self.assertEqual(json.loads(request('/api/export?campaign='+key)[1])['campaignName'],'Second')
                raw=(Path(__file__).resolve().parents[1]/'static/assets/portraits/aurelia.webp').read_bytes()
                status,body=request('/api/upload?campaign='+key,{'imageData':'data:image/webp;base64,'+base64.b64encode(raw).decode()})
                self.assertEqual(status,200);path=json.loads(body)['assetPath']
                self.assertEqual(request(path+'?campaign='+key),(200,raw))
                self.assertEqual(request(path)[0],404)
                accept={'requestId':uuid.uuid4().hex,'expectedRevision':1,'action':{'type':'accept-artwork','assetId':'mira','assetPath':path}}
                self.assertEqual(request('/api/action',accept)[0],400)
                self.assertEqual(request('/api/action?campaign='+key,accept)[0],200)
                status,backup=request('/api/backup?campaign='+key)
                self.assertEqual(status,200)
                with zipfile.ZipFile(io.BytesIO(backup)) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(archive.read('assets/'+path.split('/')[-1]),raw)
                    self.assertEqual(json.loads(archive.read('backup-info.json'))['campaignName'],'Second')
                    with tempfile.TemporaryDirectory() as restored:
                        archive.extractall(restored)
                        with sqlite3.connect(Path(restored)/'campaign.sqlite3') as db:
                            backup_state=json.loads(db.execute('SELECT state FROM campaign').fetchone()[0])
                        self.assertEqual(backup_state['revision'],2)
                        self.assertEqual(backup_state['assetOverrides']['mira'],path)
                        reopened=CampaignLibrary(restored)
                        self.assertEqual(reopened.get('default').read(),backup_state)
                self.assertEqual(json.loads(request('/api/state?campaign='+key)[1])['revision'],2)
                self.assertEqual(request('/api/state?campaign=default&campaign='+key)[0],400)
                self.assertEqual(request('/api/state?campaign=../../etc')[0],400)
                self.assertEqual(len(json.loads(request('/api/campaigns')[1])['campaigns']),2)
            finally:
                server.shutdown();server.server_close();thread.join()

    def test_backup_preserves_art_history_and_rejects_missing_images(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            paths=[]
            for image in ('portraits/aurelia.webp','portraits/mira.webp'):
                raw=(Path(__file__).resolve().parents[1]/'static/assets'/image).read_bytes()
                path=store.upload({'imageData':'data:image/webp;base64,'+base64.b64encode(raw).decode()})
                paths.append(path)
                store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],
                    'action':{'type':'accept-artwork','assetId':'mira','assetPath':path}})
            before=store.read()
            with zipfile.ZipFile(io.BytesIO(store.backup_archive())) as archive:
                for path in paths:self.assertIn('assets/'+path.split('/')[-1],archive.namelist())
                self.assertIn('RESTORE.txt',archive.namelist())
            self.assertEqual(store.read(),before)
            (Path(directory)/'assets'/paths[0].split('/')[-1]).unlink()
            with self.assertRaises(RuleError):store.backup_archive()
            self.assertEqual(store.read(),before)
