#!/usr/bin/env python3
"""Self-hosted prototype: standard-library HTTP server + transactional SQLite."""
from asset_aliases import ASSET_ALIASES
import household_content
import public_content
import public_workshop
import expansion_packs
import content_packs
import argparse
import base64
import hashlib
import io
import json
import mimetypes
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote, parse_qs
from dialogue import ProviderSettings, DialogueService, DIALOGUE_PROFILES, supported_dialogue
from game import text_value, RuleError, apply_action, new_campaign, public_state, migrate_state, CURRENT_SCHEMA_VERSION

ROOT = Path(__file__).resolve().parent
MAX_REQUEST_BYTES = 9_000_000

class GameStore:
    def __init__(self, directory, campaign_name=None, public_starter=None, start_type="demo"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / 'assets').mkdir(exist_ok=True)
        self.database = self.directory / 'campaign.sqlite3'
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS campaign (id INTEGER PRIMARY KEY, state TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS portrait_drafts (id TEXT PRIMARY KEY, payload TEXT NOT NULL, result TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS dialogue_drafts (id TEXT PRIMARY KEY, payload TEXT NOT NULL, result TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS expansion_packs (digest TEXT PRIMARY KEY, content TEXT NOT NULL, report TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS content_packs (digest TEXT PRIMARY KEY, content TEXT NOT NULL, report TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS actions (request_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
            initial = new_campaign(start_type)
            if public_starter:
                import public_starters
                public_starters.initialize_new_scholar(initial,public_starter)
            if campaign_name is not None:
                initial['campaignName'] = campaign_name
            db.execute('INSERT OR IGNORE INTO campaign VALUES (1, ?)', (json.dumps(initial),))
        with self.connect() as db:
            current = json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])
            if current.get('schemaVersion', 1) < CURRENT_SCHEMA_VERSION:
                backup_path = self.directory / f"campaign-before-schema-{current.get('schemaVersion', 1)}-to-{CURRENT_SCHEMA_VERSION}.sqlite3"
                if not backup_path.exists():
                    with sqlite3.connect(backup_path) as backup:
                        db.backup(backup)
                db.execute('BEGIN IMMEDIATE')
                current = json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])
                if current.get('schemaVersion', 1) < CURRENT_SCHEMA_VERSION:
                    migrate_state(current)
                    current['revision'] += 1
                    db.execute('UPDATE campaign SET state=? WHERE id=1', (json.dumps(current),))
            elif current.get('schemaVersion') > CURRENT_SCHEMA_VERSION:
                raise RuleError('This save needs a newer application version.')

    def connect(self):
        return sqlite3.connect(self.database, timeout=10)

    def read(self):
        with self.connect() as db:
            return json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])

    def action(self, payload):
        request_id = payload.get('requestId')
        if not isinstance(request_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,100}', request_id):
            raise RuleError('A valid request identifier is required.')
        if not isinstance(payload.get('action'), dict):
            raise RuleError('An action object is required.')
        encoded = json.dumps(payload, sort_keys=True)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            state = json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])
            previous = db.execute('SELECT payload FROM actions WHERE request_id=?', (request_id,)).fetchone()
            if previous:
                if previous[0] != encoded:
                    raise RuleError('This request identifier was already used for a different action.')
                return state
            if type(payload.get('expectedRevision')) is not int or payload['expectedRevision'] != state['revision']:
                raise ConflictError('The save changed in another tab. Refreshed your state; please review and try again.')
            action = payload['action']
            if action.get('type')=='accept-generated-portrait':
                row=db.execute('SELECT result FROM portrait_drafts WHERE id=?',(action.get('draftId') if isinstance(action.get('draftId'),str) else '',)).fetchone()
                if not row:raise RuleError('Choose a portrait draft from this campaign.')
                draft=json.loads(row[0])
                if draft['status']!='ready':raise RuleError('This portrait is not ready for acceptance.')
                if draft['baseRevision']!=state['revision']:raise RuleError('Your campaign changed after this portrait was requested. Review or import it through Illustration review instead.')
                action={'type':'accept-artwork','assetId':'founder','assetPath':draft['assetPath']}
                draft['status']='accepted'
                db.execute('UPDATE portrait_drafts SET result=? WHERE id=?',(json.dumps(draft),draft['id']))
            if action.get('type') == 'accept-artwork':
                asset_path = action.get('assetPath', '')
                if not isinstance(asset_path, str) or not re.fullmatch(r'/user-assets/[a-f0-9]{64}\.(png|jpg|webp)', asset_path):
                    raise RuleError('Invalid uploaded asset path.')
                if not (self.directory / 'assets' / asset_path.split('/')[-1]).is_file():
                    raise RuleError('The uploaded artwork is missing.')
            if action.get('type')=='propose-expansion-scene':
                digest=action.get('packDigest')
                if not isinstance(digest,str):raise RuleError('Choose a staged scene pack.')
                row=db.execute('SELECT content,report FROM expansion_packs WHERE digest=?',(digest,)).fetchone()
                if not row:raise RuleError('Stage the public scene pack first.')
                public_content.compose_scene(state,action,json.loads(row[0]),json.loads(row[1]))
            elif action.get('type') in household_content.PACK_ACTIONS:
                digest=(state.get('activeContentPack') or {}).get('digest')
                row=db.execute('SELECT content FROM content_packs WHERE digest=?',(digest,)).fetchone()
                if not row:raise RuleError('Activate a content pack first.')
                household_content.apply(state,action,json.loads(row[0]))
            elif action.get('type') == 'activate-content-pack':
                digest=action.get('digest')
                if not isinstance(digest,str) or action.get('contentReviewed') is not True:
                    raise RuleError('Review the pack content and validation report before activation.')
                row=db.execute('SELECT report FROM content_packs WHERE digest=?',(digest,)).fetchone()
                if not row:raise RuleError('Validate this pack in the selected campaign first.')
                report=json.loads(row[0])
                if not report['valid']:raise RuleError('Resolve pack validation errors before activation.')
                state['activeContentPack']=report['summary']
            elif action.get('type') == 'deactivate-content-pack':
                state['activeContentPack']=None
            else:
                apply_action(state, action)
            state['revision'] += 1
            db.execute('UPDATE campaign SET state=? WHERE id=1', (json.dumps(state),))
            db.execute('INSERT INTO actions VALUES (?,?)', (request_id, encoded))
            return state

    def validate_content_pack(self,payload):
        encoded=payload.get('archiveBase64')
        if payload.get('bundled') is True:
            encoded=base64.b64encode((ROOT/'static/examples/stonework-spellcraft-content-pack.zip').read_bytes()).decode()
        files=content_packs.decode_archive(encoded)
        pack,report=content_packs.validate(files)
        if report['valid']:
            with self.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                existing=db.execute('SELECT 1 FROM content_packs WHERE digest=?',(report['digest'],)).fetchone()
                if not existing and db.execute('SELECT count(*) FROM content_packs').fetchone()[0]>=12:
                    raise RuleError('This campaign retains at most twelve validated pack versions. Existing characters keep their source snapshots.')
                db.execute('INSERT OR IGNORE INTO content_packs VALUES (?,?,?)',(report['digest'],json.dumps(pack),json.dumps(report)))
        return report

    def content_pack_catalogue(self):
        with self.connect() as db:
            return {'packs':[json.loads(r[0]) for r in db.execute('SELECT report FROM content_packs ORDER BY rowid DESC')]}

    def content_pack_preview(self,digest):
        if not isinstance(digest,str):raise RuleError('Choose a validated pack.')
        with self.connect() as db:
            row=db.execute('SELECT content FROM content_packs WHERE digest=?',(digest,)).fetchone()
        if not row:raise RuleError('This pack has not been validated in this campaign.')
        return json.loads(row[0])

    def validate_expansion_pack(self,payload):
        files=content_packs.decode_archive(payload.get('archiveBase64'))
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            dependencies=[json.loads(r[0]) for r in db.execute('SELECT content FROM expansion_packs')]
            dependencies.extend(public_content.foundation_dependency(json.loads(r[0])) for r in db.execute('SELECT content FROM content_packs'))
            pack,report=expansion_packs.validate(files,dependencies)
            if report['valid']:
                for prior in dependencies:
                    if prior['manifest']['packId']!=pack['manifest']['packId'] and set(prior['entries'])&set(pack['entries']):
                        raise RuleError('A staged pack has conflicting stable IDs.')
                    if prior['manifest']['packId']==pack['manifest']['packId'] and prior['manifest']['packVersion']==pack['manifest']['packVersion'] and prior.get('sourceFiles')!=files:
                        raise RuleError('This design pack version already has different content. Use a new packVersion for revisions.')
                existing=db.execute('SELECT 1 FROM expansion_packs WHERE digest=?',(report['digest'],)).fetchone()
                if not existing and db.execute('SELECT count(*) FROM expansion_packs').fetchone()[0]>=48:
                    raise RuleError('This campaign retains at most forty-eight expansion design versions.')
                db.execute('INSERT OR IGNORE INTO expansion_packs VALUES (?,?,?)',(report['digest'],json.dumps(pack),json.dumps(report)))
        return report

    def stage_public_bundle(self):
        foundation,foundation_report,reviewed=public_content.review_bundle(ROOT/'content/stonework-and-spellcraft-public-packs.zip')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            prior=[json.loads(row[0]) for row in db.execute('SELECT content FROM expansion_packs')]
            for pack,report in reviewed:
                for old in prior:
                    if old['manifest']['packId']==pack['manifest']['packId'] and old['manifest']['packVersion']==pack['manifest']['packVersion'] and old['sourceFiles']!=pack['sourceFiles']:
                        raise RuleError('A different staged design already uses '+report['packId']+' '+report['packVersion']+'. No bundle changes were saved.')
                    if old['manifest']['packId']!=pack['manifest']['packId'] and set(old['entries'])&set(pack['entries']):raise RuleError('A staged pack has conflicting stable IDs. No bundle changes were saved.')
            existing={row[0] for row in db.execute('SELECT digest FROM expansion_packs')}
            if len(existing|{r['digest'] for _,r in reviewed})>48:raise RuleError('This campaign retains at most forty-eight expansion design versions.')
            if not db.execute('SELECT 1 FROM content_packs WHERE digest=?',(foundation_report['digest'],)).fetchone() and db.execute('SELECT count(*) FROM content_packs').fetchone()[0]>=12:raise RuleError('The foundations pack store is full.')
            db.execute('INSERT OR IGNORE INTO content_packs VALUES (?,?,?)',(foundation_report['digest'],json.dumps(foundation),json.dumps(foundation_report)))
            for pack,report in reviewed:db.execute('INSERT OR IGNORE INTO expansion_packs VALUES (?,?,?)',(report['digest'],json.dumps(pack),json.dumps(report)))
        return {'valid':True,'packs':[r for _,r in reviewed],'contentCount':sum(r['contentCount'] for _,r in reviewed),'mechanicsCount':sum(r['mechanicsCount'] for _,r in reviewed),'message':'Public packs staged for review. No game rules, inventory, identities or accepted events changed.'}

    def expansion_pack_catalogue(self):
        with self.connect() as db:
            return {'packs':[json.loads(r[0]) for r in db.execute('SELECT report FROM expansion_packs ORDER BY rowid DESC')]}

    def expansion_pack_preview(self,digest):
        if not isinstance(digest,str):raise RuleError('Choose a staged expansion design.')
        with self.connect() as db:row=db.execute('SELECT content FROM expansion_packs WHERE digest=?',(digest,)).fetchone()
        if not row:raise RuleError('This expansion design has not been staged in this campaign.')
        return json.loads(row[0])

    def backup_archive(self):
        """Consistent SQLite snapshot plus the exact artwork referenced by that snapshot."""
        output = io.BytesIO()
        with tempfile.TemporaryDirectory(prefix='castle-backup-') as directory:
            snapshot = Path(directory) / 'campaign.sqlite3'
            with self.connect() as source, sqlite3.connect(snapshot) as target:
                source.backup(target)
                state = json.loads(target.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])
            references = set(state['assetOverrides'].values())
            for history in state['assetHistory'].values(): references.update(history)
            with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
                archive.write(snapshot,'campaign.sqlite3')
                for asset in sorted(references):
                    if not asset.startswith('/user-assets/'):
                        continue
                    filename = asset.removeprefix('/user-assets/')
                    if not re.fullmatch(r'[a-f0-9]{64}\.(png|jpg|webp)',filename):
                        raise RuleError('The saved artwork contains an invalid path; the backup was not created.')
                    file = self.directory / 'assets' / filename
                    if not file.is_file() or file.is_symlink():
                        raise RuleError('A referenced illustration is missing; restore it before downloading a complete backup.')
                    archive.write(file,'assets/'+filename)
                archive.writestr('backup-info.json',json.dumps({'campaignName':state['campaignName'],
                    'schemaVersion':state['schemaVersion'],'revision':state['revision'],
                    'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']},indent=2))
                archive.writestr('RESTORE.txt',
                    'Stop the game server before restoring. Keep a separate copy of the current data first.\n'
                    'For the original campaign, replace campaign.sqlite3 and merge assets/ into the server data directory.\n'
                    'For another slot, use data/campaigns/<that slot id>/ instead. Keep the server campaign-registry.sqlite3.\n'
                    'To move this campaign alone to a fresh server, extract campaign.sqlite3 and assets/ into its empty data directory; it becomes the original slot.\n'
                    'Use this application version or newer. Restart the server; no offline time passes.\n'
                    'Only artwork needed by the saved accepted versions and rollback history is included. Bundled artwork is provided by the application.\n')
        return output.getvalue()

    def upload(self, payload):
        content = payload.get('imageData')
        if not isinstance(content, str):
            raise RuleError('An image is required.')
        match = re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)', content)
        if not match:
            raise RuleError('Only PNG, JPEG, and WebP images are supported.')
        try:
            raw = base64.b64decode(match[2], validate=True)
        except ValueError:
            raise RuleError('Invalid image data.')
        valid = {'png': raw.startswith(b'\x89PNG\r\n\x1a\n'), 'jpeg': raw.startswith(b'\xff\xd8\xff'), 'webp': raw.startswith(b'RIFF') and raw[8:12] == b'WEBP'}
        if len(raw) > 6_000_000 or not valid[match[1]]:
            raise RuleError('Use a valid PNG, JPEG, or WebP image smaller than 6 MB.')
        suffix = 'jpg' if match[1] == 'jpeg' else match[1]
        filename = hashlib.sha256(raw).hexdigest() + '.' + suffix
        destination = self.directory / 'assets' / filename
        if not destination.exists():
            # Exclusive creation prevents simultaneous uploads from truncating a file.
            try:
                with destination.open('xb') as file:
                    file.write(raw)
            except FileExistsError:
                pass
        return '/user-assets/' + filename

class CampaignLibrary:
    """Campaign selection is explicit per request, never shared browser-session state."""
    def __init__(self, directory):
        self.directory = Path(directory)
        self.default_store = GameStore(self.directory)
        self.registry = self.directory / 'campaign-registry.sqlite3'
        with sqlite3.connect(self.registry) as db:
            db.execute('CREATE TABLE IF NOT EXISTS campaigns (id TEXT PRIMARY KEY, creation_name TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO campaigns VALUES (?,?)', ('default', self.default_store.read()['campaignName']))

    def get(self, campaign_id):
        if campaign_id == 'default':
            return self.default_store
        if not isinstance(campaign_id,str) or not re.fullmatch(r'c-[a-f0-9]{32}',campaign_id):
            raise RuleError('Unknown campaign. Choose a saved campaign from About & saves.')
        with sqlite3.connect(self.registry) as db:
            found = db.execute('SELECT id FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
        directory = self.directory / 'campaigns' / campaign_id
        if not found or not (directory / 'campaign.sqlite3').is_file():
            raise RuleError('Unknown campaign. Choose a saved campaign from About & saves.')
        return GameStore(directory)

    def list(self):
        with sqlite3.connect(self.registry) as db:
            ids = [row[0] for row in db.execute('SELECT id FROM campaigns ORDER BY rowid')]
        rows = []
        for campaign_id in ids:
            state = self.get(campaign_id).read()
            rows.append({'id':campaign_id, 'name':state['campaignName'], 'mode':state['campaignMode'],
                'dayNumber':state['dayNumber'], 'phase':state['currentDayPhase'], 'revision':state['revision'], 'startType':state.get('startType','demo'), 'testingUsed':state.get('testing',{}).get('used',False)})
        return rows

    def create(self, payload):
        campaign_id = payload.get('campaignId')
        if not isinstance(campaign_id,str) or not re.fullmatch(r'c-[a-f0-9]{32}',campaign_id):
            raise RuleError('Provide a new campaign identifier.')
        if payload.get('mode') != 'solo':
            raise RuleError('Choose a solo campaign. Co-op is deferred.')
        name = text_value(payload.get('name'),70)
        start_type=payload.get('startType','demo')
        if start_type not in ('fresh','demo'):raise RuleError('Choose a fresh beginning or demonstration household.')
        starter=payload.get('publicStarter')
        if starter is not None:public_workshop.definition(starter,'starting-package-concept')
        with sqlite3.connect(self.registry, timeout=10) as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT creation_name FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            if previous:
                saved=GameStore(self.directory / 'campaigns' / campaign_id).read()
                if previous[0] != name or saved.get('publicStarter',{}).get('recordId')!=starter or saved.get('startType','demo')!=start_type:
                    raise RuleError('That creation identifier already belongs to a different request.')
            else:
                if db.execute('SELECT COUNT(*) FROM campaigns').fetchone()[0] >= 20:
                    raise RuleError('This prototype supports up to 20 separate campaigns.')
                GameStore(self.directory / 'campaigns' / campaign_id, campaign_name=name, public_starter=starter, start_type=start_type)
                db.execute('INSERT INTO campaigns VALUES (?,?)',(campaign_id,name))
        return {'campaignId':campaign_id}


class ConflictError(ValueError):
    pass

class Handler(BaseHTTPRequestHandler):
    server_version = 'StoneworkAndSpellcraft/0.105'

    def send_bytes(self, content, mime, status=200, download=False):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store' if mime.startswith('application/json') else 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header('Referrer-Policy', 'same-origin')
        if download:
            filename = 'stonework-and-spellcraft-campaign.json' if download is True else download
            self.send_header('Content-Disposition', 'attachment; filename="'+filename+'"')
        self.end_headers()
        self.wfile.write(content)

    def json_response(self, data, status=200, download=False):
        self.send_bytes(json.dumps(data).encode(), 'application/json; charset=utf-8', status, download)

    def selected_store(self):
        values = parse_qs(urlsplit(self.path).query, keep_blank_values=True).get('campaign',['default'])
        if len(values)!=1:
            raise RuleError('Choose exactly one campaign.')
        return self.server.campaigns.get(values[0])

    def do_GET(self):
        try:
            path = unquote(urlsplit(self.path).path)
            if path == '/api/dialogue/drafts':
                character_id=parse_qs(urlsplit(self.path).query).get('character',[None])[0]
                if character_id is not None and not supported_dialogue(self.selected_store().read(),character_id):raise RuleError('Choose an available NPC conversation.')
                purpose=parse_qs(urlsplit(self.path).query).get('purpose',[None])[0]
                if purpose not in (None,'dialogue','journal','spell-proposal','candidate-proposal','story-proposal','scene-proposal'):raise RuleError('Choose a supported draft purpose.')
                owner=parse_qs(urlsplit(self.path).query).get('owner',[None])[0]
                if owner is not None and owner not in self.selected_store().read()['people']:raise RuleError('Choose a known spell owner.')
                scene_id=parse_qs(urlsplit(self.path).query).get('scene',[None])[0]
                drafts=[]
                with self.selected_store().connect() as db:
                    for row in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC'):
                        draft=json.loads(row[0])
                        draft_purpose=draft.get('purpose','dialogue')
                        if purpose is not None and purpose!=draft_purpose:continue
                        if scene_id is not None and (draft_purpose!='scene-proposal' or draft.get('sceneId')!=scene_id):continue
                        if owner is not None and (draft_purpose not in ('spell-proposal','story-proposal') or draft.get('ownerId')!=owner):continue
                        if character_id is not None and (draft_purpose!='dialogue' or draft.get('characterId','mira')!=character_id):continue
                        drafts.append(draft)
                        if len(drafts)==8:break
                return self.json_response({'drafts':drafts})
            if path == '/api/household-content':
                store=self.selected_store();state=store.read();summary=state.get('activeContentPack')
                pack=store.content_pack_preview(summary['digest']) if summary else None
                return self.json_response(household_content.catalogue(state,pack))
            if path == '/api/public-workshop/catalogue':
                import public_integration
                return self.json_response(public_integration.catalogue_view())
            if path == '/api/expansion-packs':
                return self.json_response(self.selected_store().expansion_pack_catalogue())
            if path == '/api/content-packs':
                return self.json_response(self.selected_store().content_pack_catalogue())
            if path == '/api/portrait-settings':
                return self.json_response(self.server.portrait_settings.public())
            if path == '/api/portrait-drafts':
                return self.json_response(self.server.portraits.list(self.selected_store()))
            if path == '/api/provider':
                return self.json_response(self.server.provider_settings.public())
            if path == '/api/campaigns':
                return self.json_response({'campaigns':self.server.campaigns.list()})
            if path == '/api/state':
                return self.json_response(public_state(self.selected_store().read()))
            if path == '/api/backup':
                return self.send_bytes(self.selected_store().backup_archive(), 'application/zip', download='stonework-and-spellcraft-save.zip')
            if path == '/api/export':
                return self.json_response(public_state(self.selected_store().read()), download=True)
            if path == '/api/health':
                return self.json_response({'status': 'ok', 'version': '0.105'})
            path = ASSET_ALIASES.get(path, path)
            root = self.selected_store().directory / 'assets' if path.startswith('/user-assets/') else ROOT / 'static'
            relative = path.removeprefix('/user-assets/') if path.startswith('/user-assets/') else ('index.html' if path == '/' else path.lstrip('/'))
            file = (root / relative).resolve()
            if not file.is_relative_to(root.resolve()) or not file.is_file():
                return self.json_response({'error': 'Not found.'}, 404)
            self.send_bytes(file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
        except RuleError as error:
            self.json_response({'error':str(error)},400)

    def do_POST(self):
        try:
            # Same-origin JSON-only writes prevent ordinary cross-site form attacks.
            origin = self.headers.get('Origin')
            if origin and urlsplit(origin).netloc != self.headers.get('Host'):
                return self.json_response({'error': 'Cross-origin writes are not allowed.'}, 403)
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.json_response({'error': 'Use application/json.'}, 415)
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_REQUEST_BYTES:
                return self.json_response({'error': 'Request size is invalid.'}, 413)
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise RuleError('Expected a JSON object.')
            path = urlsplit(self.path).path
            if path == '/api/expansion-packs/bundled':
                return self.json_response(self.selected_store().stage_public_bundle())
            if path == '/api/expansion-packs/validate':
                return self.json_response(self.selected_store().validate_expansion_pack(payload))
            if path == '/api/expansion-packs/preview':
                return self.json_response(self.selected_store().expansion_pack_preview(payload.get('digest')))
            if path == '/api/content-packs/validate':
                return self.json_response(self.selected_store().validate_content_pack(payload))
            if path == '/api/content-packs/preview':
                return self.json_response(self.selected_store().content_pack_preview(payload.get('digest')))
            if path == '/api/portrait-settings':
                return self.json_response(self.server.portrait_settings.save(payload))
            if path == '/api/portrait-abandon':
                return self.json_response(self.server.portraits.abandon(self.selected_store(),payload))
            if path == '/api/portrait-draft':
                return self.json_response(self.server.portraits.generate(self.selected_store(),payload))
            if path == '/api/provider':
                return self.json_response(self.server.provider_settings.save(payload))
            if path == '/api/dialogue/draft':
                return self.json_response(self.server.dialogue.generate(self.selected_store(),payload))
            if path == '/api/story/review':
                return self.json_response(self.server.dialogue.review_story(self.selected_store(),payload))
            if path == '/api/candidate/review':
                return self.json_response(self.server.dialogue.review_candidate(self.selected_store(),payload))
            if path == '/api/dialogue/accept':
                return self.json_response(public_state(self.server.dialogue.accept(self.selected_store(),payload)))
            if path == '/api/campaigns':
                return self.json_response(self.server.campaigns.create(payload))
            if path == '/api/equipment/quote':
                import armoury
                return self.json_response(armoury.quote_action(self.selected_store().read(),payload.get('action')))
            if path == '/api/action':
                return self.json_response(public_state(self.selected_store().action(payload)))
            if path == '/api/upload':
                return self.json_response({'assetPath': self.selected_store().upload(payload)})
            return self.json_response({'error': 'Not found.'}, 404)
        except ConflictError as error:
            self.json_response({'error': str(error), 'state': public_state(self.selected_store().read())}, 409)
        except (RuleError, ValueError, TypeError) as error:
            self.json_response({'error': str(error)}, 400)
        except Exception:
            self.log_error('Unexpected request failure')
            self.json_response({'error': 'The request failed. Your last committed save remains available.'}, 500)

    def log_message(self, format_string, *args):
        pass

def create_server(host, port, data_directory):
    server = ThreadingHTTPServer((host, port), Handler)
    server.campaigns = CampaignLibrary(data_directory)
    server.store = server.campaigns.default_store
    server.provider_settings = ProviderSettings(data_directory)
    server.dialogue = DialogueService(server.provider_settings)
    from portrait_generation import PortraitSettings, PortraitService
    server.portrait_settings=PortraitSettings(data_directory)
    server.portraits=PortraitService(server.portrait_settings)
    return server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stonework and Spellcraft visual prototype')
    parser.add_argument('--host', default=os.getenv('CASTLE_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('CASTLE_PORT', '8080')))
    parser.add_argument('--data-dir', default=os.getenv('CASTLE_DATA_DIR', str(ROOT / 'data')))
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.data_dir)
    print(f'Stonework and Spellcraft: http://{args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
