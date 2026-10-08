"""Importer integrity, stable generation, campaign isolation and approval boundaries."""
import base64
from copy import deepcopy
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
import zipfile
import content_packs as packs
import character_pool
import game
from dialogue import DialogueService,ProviderSettings
from server import GameStore,ConflictError
from examples.build_content_fixture import fixture_files


def zip_payload(files=None):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:
        for path,raw in (files or fixture_files()).items():z.writestr('fixture/'+path,raw)
    return {'archiveBase64':base64.b64encode(data.getvalue()).decode()}


def change(files,path,edit):
    obj=json.loads(files[path]);edit(obj);files[path]=json.dumps(obj)


def activate(store,report):
    return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'activate-content-pack','digest':report['digest'],'contentReviewed':True}})


class PackTests(unittest.TestCase):
    def test_fixture_counts_shortfalls_and_roundtrip(self):
        files=packs.decode_archive(zip_payload()['archiveBase64']);pack,report=packs.validate(files)
        self.assertTrue(report['valid'],report['errors']);self.assertEqual(report['recordCount'],24)
        self.assertEqual(len(pack['ancestries']),21);self.assertEqual(len(pack['shared']),11)
        self.assertTrue(any('production target' in w for w in report['warnings']))
        self.assertEqual(packs.validate(files)[1]['digest'],report['digest'])

    def test_bad_archives_never_extract(self):
        for files in [{'../manifest.json':'{}'},{'/manifest.json':'{}'},{'manifest.json':'{}','payload.py':'pass'},{'a/manifest.json':'{}','b/manifest.json':'{}'},{'manifest.json':'{}','a\\b.json':'{}'}]:
            with self.subTest(files=files),self.assertRaises(game.RuleError):packs.decode_archive(zip_payload(files)['archiveBase64'])
        for value in [None,{},'not base64','e30=']:
            with self.assertRaises(game.RuleError):packs.decode_archive(value)
        for special in ['link','bomb','duplicate']:
            data=io.BytesIO()
            with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:
                if special=='link':
                    info=zipfile.ZipInfo('manifest.json');info.external_attr=0o120777<<16;z.writestr(info,'outside')
                elif special=='bomb':z.writestr('manifest.json','a'*6_000_001)
                else:
                    z.writestr('manifest.json','{}')
                    import warnings
                    with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr('manifest.json','{}')
            with self.assertRaises(game.RuleError):packs.decode_archive(base64.b64encode(data.getvalue()).decode())

    def test_schema_and_reference_failures(self):
        mutations=[('ancestries/wolfkin.json',lambda o:o.update(arrivalMethod='summoning')),
          ('ancestries/wolfkin.json',lambda o:o['names'][0].update(name='Eris')),
          ('ancestries/wolfkin.json',lambda o:o['names'][0].update(styleTags=['undeclared'])),
          ('ancestries/wolfkin.json',lambda o:o['names'][0].update(reward=999)),
          ('ancestries/wolfkin.json',lambda o:o['names'][1].update(name=' '+o['names'][0]['name'].upper()+' ')),
          ('ancestries/wolfkin.json',lambda o:o['appearanceDescriptions'][0].update(summary='<script>alert(1)</script>')),
          ('shared/personality-nuances.json',lambda o:o['entries'][0].update(conflictsWith=['missing'])),
          ('shared/personality-nuances.json',lambda o:o['entries'][0].update(conflictsWith=['personality-002'])),
          ('shared/occupations-backgrounds.json',lambda o:o['entries'][0].update(excludedAncestries=[])),
          ('manifest.json',lambda o:o['ancestries'][0]['counts'].update(names=100)),
          ('manifest.json',lambda o:o['ancestries'][0].update(path='../outside.json'))]
        for path,edit in mutations:
            with self.subTest(path=path):
                files=fixture_files();change(files,path,edit);self.assertFalse(packs.validate(files)[1]['valid'])
        files=fixture_files();files['manifest.json']='{"schemaVersion":1,"schemaVersion":1}'
        self.assertFalse(packs.validate(files)[1]['valid'])

    def test_malformed_shapes_report_without_crashing(self):
        for path in ['manifest.json','vocabulary.json','ancestries/wolfkin.json','shared/ambitions.json']:
            for value in [None,[],1,'bad',{'schemaVersion':True},{'schemaVersion':1}]:
                files=fixture_files();files[path]=json.dumps(value)
                with self.subTest(path=path,value=value):self.assertFalse(packs.validate(files)[1]['valid'])

    def test_ensemble_conflicts_and_references(self):
        files=fixture_files()
        common=json.loads(files['shared/personality-nuances.json'])['entries'][0]
        garment={k:v for k,v in common.items() if k in packs.COMMON}
        garment.update(id='garment-001',slot='top',materials=['linen'],colours=['navy'],silhouette='Fitted.',coverage='Opaque.',anatomyAccommodations=[],occasionTags=['practical'],incompatibleSlots=[])
        ensemble={k:v for k,v in common.items() if k in packs.COMMON}
        ensemble.update(id='ensemble-001',componentIds=['garment-001'],occasionTags=['practical'],stylingNotes='Neatly arranged.',anatomyAccommodations=[])
        for kind,obj in [('clothing-component',garment),('ensemble',ensemble)]:
            filename=packs.SHARED[kind][0];change(files,'shared/'+filename+'.json',lambda o:o.update(entries=[obj]))
            change(files,'manifest.json',lambda m:[r.update(count=1) for r in m['sharedPools'] if r['poolType']==kind])
        self.assertTrue(packs.validate(files)[1]['valid'])
        change(files,'shared/ensembles.json',lambda o:o['entries'][0].update(componentIds=['garment-missing']))
        self.assertFalse(packs.validate(files)[1]['valid'])

    def test_staging_activation_isolation_backup_and_idempotency(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(Path(d)/'one');other=GameStore(Path(d)/'two');before=store.read()
            report=store.validate_content_pack(zip_payload());self.assertEqual(store.read(),before)
            self.assertEqual(len(store.content_pack_catalogue()['packs']),1)
            self.assertEqual(other.content_pack_catalogue()['packs'],[])
            with self.assertRaises(game.RuleError):activate(other,report)
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':before['revision'],'action':{'type':'activate-content-pack','digest':report['digest'],'contentReviewed':False}}
            with self.assertRaises(game.RuleError):store.action(payload)
            payload['action']['contentReviewed']=True;after=store.action(payload)
            self.assertEqual(after,store.action(payload));self.assertEqual(after['currentDayPhase'],before['currentDayPhase']);self.assertEqual(after['sharedFunds'],before['sharedFunds'])
            with self.assertRaises(ConflictError):store.action({**payload,'requestId':uuid.uuid4().hex})
            archive=zipfile.ZipFile(io.BytesIO(store.backup_archive()))
            name=next(n for n in archive.namelist() if n.endswith('campaign.sqlite3'));target=Path(d)/'restored.sqlite3';target.write_bytes(archive.read(name))
            with sqlite3.connect(target) as db:self.assertEqual(db.execute('SELECT count(*) FROM content_packs').fetchone()[0],1)
            self.assertNotIn('ancestries',game.public_state(after)['activeContentPack'])
            self.assertEqual(GameStore(Path(d)/'one').read(),after)

    def test_failed_pack_never_staged(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);files=fixture_files();files['manifest.json']='{}'
            self.assertFalse(store.validate_content_pack(zip_payload(files))['valid']);self.assertEqual(store.content_pack_catalogue()['packs'],[])

    def test_generation_paths_retries_frozen_sources_and_edits(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);report=store.validate_content_pack(zip_payload());activate(store,report)
            service=DialogueService(ProviderSettings(d),lambda *_:self.fail('Offline generation called provider'))
            for ancestry in ['Wolfkin','Demon','Golem']:
                payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'purpose':'candidate-proposal','source':'offline','poolChoices':{'contentSource':'imported','ancestry':ancestry},'text':'A visitor.'}
                draft=service.generate(store,payload);self.assertEqual(draft['status'],'ready',draft)
                self.assertEqual(service.generate(store,payload),draft)
                records=draft['generationIngredients']['records'];self.assertIn('voice',records);self.assertIn('value',records)
                self.assertEqual(draft['ruleReview']['arrivalMethod'],packs.route(next(k for k,v in packs.REGISTRY.items() if v==ancestry)))
                edits={'draftId':draft['id'],'expectedRevision':store.read()['revision'],'expectedDraftRevision':0,'edits':{'ambition':'Make useful field notes legible to a willing beginner.'}}
                updated=service.review_candidate(store,edits);self.assertEqual(updated['editRevision'],1)
                with self.assertRaises(game.RuleError):service.review_candidate(store,edits)
                with self.assertRaises(game.RuleError):service.accept(store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
                saved=service.accept(store,{'draftId':draft['id'],'expectedDraftRevision':1,'contentReviewed':True,'mechanicsReviewed':True})
                profile=saved['reviewedCandidates']['summoned-'+draft['id']]['profile'];self.assertEqual(profile['ambition'],edits['edits']['ambition']);self.assertEqual(profile['generationIngredients'],draft['generationIngredients'])
                self.assertEqual(profile['generationIngredients']['records']['voice'],records['voice'])
            old=deepcopy(store.read()['reviewedCandidates'])
            store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'deactivate-content-pack'}})
            self.assertEqual(store.read()['reviewedCandidates'],old)
            with self.assertRaises(game.RuleError):service.generate(store,{**payload,'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision']})

    def test_compatibility_exhaustion_and_stable_selection(self):
        pack,report=packs.validate(fixture_files());s=game.new_campaign();s['activeContentPack']=report['summary'];choices={'contentSource':'imported','ancestry':'Wolfkin'}
        selected=packs.select(s,'repeat',choices,pack);self.assertEqual(packs.select(s,'repeat',choices,pack),selected)
        for kind in ['name','story','appearance','background','personality','value','habit','voice','ambition','social']:self.assertIn(kind,selected['records'])
        # A hard conflict across two mandatory pools must block a character.
        pack['shared']['value-boundary'][0]['conflictsWith']=['voice-001']
        pack['shared']['conversational-voice'][0]['conflictsWith']=['boundary-001']
        with self.assertRaises(game.RuleError):packs.select(s,'x',choices,pack)
        pack,_=packs.validate(fixture_files());pack['ancestries']['wolfkin']['storySeeds'][0]['requirements']=['A completed notebook.']
        with self.assertRaises(game.RuleError):packs.select(s,'x',choices,pack)
        pack,_=packs.validate(fixture_files());pack['shared']['occupation-background'][1]['historyMode']='either'
        with self.assertRaises(game.RuleError):packs.select(s,'x',{'contentSource':'imported','ancestry':'Golem'},pack)
        for o in pack['ancestries']['wolfkin']['names']:s['people'][o['id']]={'name':o['name']}
        with self.assertRaises(game.RuleError):packs.select(s,'x',choices,pack)

    def test_locked_rules_and_no_cross_profile_context(self):
        pack,report=packs.validate(fixture_files());s=game.new_campaign();s['activeContentPack']=report['summary']
        selection=packs.select(s,'context',{'contentSource':'imported','ancestry':'Demon'},pack)
        proposal=packs.offline(selection);character_pool.validate_selection(proposal,selection)
        for key,value in [('adultAgeYears',26),('ancestryLabel','Human'),('occupation','Queen'),('capabilityPackageId','water-worker')]:
            with self.assertRaises(game.RuleError):character_pool.validate_selection({**proposal,key:value},selection)
        own={'generationIngredients':selection};context=packs.narrative_context(own)
        self.assertEqual(set(context),{'personality','value','habit','voice','ambition','social','story'})
        self.assertIsNone(packs.narrative_context(s['people']['mira']))

    def test_variety_weights_favour_less_used_traits(self):
        pack,report=packs.validate(fixture_files());s=game.new_campaign();s['activeContentPack']=report['summary']
        choices={'contentSource':'imported','ancestry':'Demon'}
        for i in range(8):
            s['reviewedCandidates'][str(i)]={'profile':{'name':'Existing '+str(i),'ancestryLabel':'Demon','generationIngredients':{'records':{'personality':pack['shared']['personality-nuance'][0]}}}}
        choices_seen=[packs.select(s,str(i),choices,pack)['records']['personality']['id'] for i in range(100)]
        self.assertGreater(choices_seen.count('personality-002'),90)

    def test_saved_draft_survives_pack_switch_and_restart(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);report=store.validate_content_pack(zip_payload());activate(store,report)
            svc=DialogueService(ProviderSettings(d))
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'purpose':'candidate-proposal','source':'offline','poolChoices':{'contentSource':'imported','ancestry':'Demon'},'text':'A visitor.'}
            draft=svc.generate(store,payload)
            files=fixture_files();change(files,'manifest.json',lambda m:m.update(packVersion='1.0.1'))
            change(files,'shared/conversational-voices.json',lambda o:o['entries'][0].update(description='An altered voice for future characters.'))
            replacement=store.validate_content_pack(zip_payload(files));activate(store,replacement)
            store=GameStore(d)
            self.assertEqual(svc.generate(store,payload),draft)
            updated=svc.review_candidate(store,{'draftId':draft['id'],'expectedRevision':store.read()['revision']})
            saved=svc.accept(store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
            person=saved['reviewedCandidates']['summoned-'+draft['id']]['profile']
            self.assertEqual(person['generationIngredients']['pack']['digest'],report['digest'])
            self.assertEqual(updated['generationIngredients'],draft['generationIngredients'])

    def test_old_save_migration_preserves_gameplay(self):
        s=game.new_campaign();s['schemaVersion']=31;s.pop('activeContentPack');before=deepcopy(s)
        game.migrate_state(s);self.assertIsNone(s['activeContentPack'])
        for k,v in before.items():
            if k!='schemaVersion':self.assertEqual(s[k],v)

class PackHTTPTests(unittest.TestCase):
    def test_http_validation_preview_activation_generation_and_isolation(self):
        import threading
        import urllib.request
        import urllib.error
        from server import create_server
        with tempfile.TemporaryDirectory() as directory:
            server=create_server('127.0.0.1',0,directory)
            worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
            def request(path,payload=None):
                req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req,timeout=5) as response:return response.status,json.load(response)
                except urllib.error.HTTPError as error:return error.code,json.load(error)
            try:
                status,report=request('/api/content-packs/validate?campaign=default',zip_payload());self.assertEqual(status,200);self.assertTrue(report['valid'])
                self.assertEqual(request('/api/content-packs?campaign=default')[1]['packs'][0]['digest'],report['digest'])
                self.assertEqual(request('/api/content-packs/preview?campaign=default',{'digest':report['digest']})[0],200)
                other=request('/api/campaigns',{'campaignId':'c-'+uuid.uuid4().hex,'name':'Other test campaign','mode':'solo'})[1]
                self.assertEqual(request('/api/content-packs/preview?campaign='+other['campaignId'],{'digest':report['digest']})[0],400)
                state=request('/api/state?campaign=default')[1]
                action={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'activate-content-pack','digest':report['digest'],'contentReviewed':True}}
                state=request('/api/action?campaign=default',action)[1]
                _,draft=request('/api/dialogue/draft?campaign=default',{'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'purpose':'candidate-proposal','source':'offline','poolChoices':{'contentSource':'imported','ancestry':'Wolfkin'},'text':'A visitor.'})
                self.assertEqual(draft['status'],'ready')
                _,edited=request('/api/candidate/review?campaign=default',{'draftId':draft['id'],'expectedRevision':state['revision'],'expectedDraftRevision':0,'edits':{'name':'Test visitor'}})
                self.assertEqual(edited['editRevision'],1)
                self.assertEqual(request('/api/dialogue/accept?campaign=default',{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})[0],400)
                self.assertEqual(request('/api/dialogue/accept?campaign=default',{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True,'expectedDraftRevision':1})[0],200)
            finally:server.shutdown();worker.join(timeout=5);server.server_close()
