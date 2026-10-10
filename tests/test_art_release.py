"""Artwork upgrades must keep old links and save-owned revisions working."""
from copy import deepcopy
import base64
import hashlib
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import uuid
import zipfile

import game
from asset_aliases import ASSET_ALIASES
from room_art import ROOM_ASSETS
from server import GameStore, create_server

ROOT = Path(__file__).resolve().parents[1]


class ArtReleaseTests(unittest.TestCase):
    def test_all_bundled_rasters_have_reviewed_live_uses(self):
        report = json.loads((ROOT/'docs/ASSETS_V074.json').read_text())
        # Later releases override an asset by path; historical manifests stay intact.
        latest = {}
        for record in report['assets']:
            latest['static/'+record['path'].lstrip('/')] = record
        for version in ('078','079','081','083','085','086','087','092'):
            for record in json.loads((ROOT/f'docs/ART_V{version}.json').read_text())['assets']:
                latest[record['path']] = record
                if version in ('078','079') and record['path'] not in json.loads((ROOT/'docs/ART_V114.json').read_text())['removed']+json.loads((ROOT/'docs/ART_V116.json').read_text())['removed']:
                    self.assertEqual(game.ORIGINAL_ASSETS[record['id']], '/'+record['path'].removeprefix('static/'))
        for record in json.loads((ROOT/'docs/art-v099/manifest.json').read_text())['assets']:
            latest[record['path']] = record
        for version in ('103','104'):
            for record in json.loads((ROOT/f'docs/ART_V{version}.json').read_text())['assets']:
                latest[record['path']]=record
        for asset in json.loads((ROOT/'docs/ART_V105.json').read_text())['assets']:
            for record in asset['files']:latest[record['path']]=record
        for record in json.loads((ROOT/'docs/ART_V107.json').read_text())['assets']:
            latest[record['path']] = record
        for record in json.loads((ROOT/'docs/ART_V108.json').read_text())['assets']:
            latest[record['path']] = record
        for record in json.loads((ROOT/'docs/ART_V110.json').read_text())['assets']:
            latest[record['path']] = record
        replacement=json.loads((ROOT/'docs/ART_V114.json').read_text())
        for old in replacement['removed']:latest.pop(old,None)
        for record in replacement['assets']:latest[record['path']]=record
        for record in json.loads((ROOT/'docs/ART_V115.json').read_text())['assets']:
            latest[record['path']] = record
        replacement=json.loads((ROOT/'docs/ART_V116.json').read_text())
        for old in replacement['removed']:latest.pop(old,None)
        for record in replacement['assets']:latest[record['path']]=record
        for version in ('117','118'):
            for record in json.loads((ROOT/f'docs/ART_V{version}.json').read_text())['assets']:latest[record['path']]=record
        expected = {ROOT/path for path in latest}
        # The v0.94 manifest records reviewed route art without digest fields.
        expected.update(ROOT/r['file'] for r in json.loads((ROOT/'docs/ART_V094.json').read_text())['assets'])
        for relative, record in latest.items():
            path = ROOT/relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'], relative)
            self.assertEqual(path.stat().st_size, record['bytes'], relative)
        actual = {p for p in (ROOT/'static/assets').rglob('*') if p.is_file()}
        self.assertEqual(actual,expected)
        self.assertEqual(len(expected),490)
        self.assertFalse(any(p.name.startswith(('v0','ui-v')) for p in (ROOT/'static/assets').iterdir()))
        for url in game.ORIGINAL_ASSETS.values():
            self.assertTrue((ROOT/'static'/url.lstrip('/')).is_file(),url)
            self.assertNotIn(url,ASSET_ALIASES)
        spells=[r for r in report['assets'] if '/spells/' in r['path']]
        self.assertEqual(len(spells),38)
        self.assertTrue(all(r['size']==[192,192] and r['alpha'] for r in spells))
        self.assertLess(sum(r['bytes'] for r in spells),sum(r['beforeBytes'] for r in spells)*.05)

    def test_all_room_slots_and_retired_urls_are_served(self):
        with tempfile.TemporaryDirectory() as directory:
            server = create_server('127.0.0.1', 0, directory)
            worker = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
            worker.start()
            try:
                for url in sorted(set(ROOM_ASSETS.values()) | set(ASSET_ALIASES) | set(game.ORIGINAL_ASSETS.values())):
                    with self.subTest(url=url):
                        with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}'+url) as response:
                            target = ROOT/'static'/ASSET_ALIASES.get(url, url).lstrip('/')
                            self.assertEqual(response.read(), target.read_bytes())
                            self.assertTrue(response.headers['Content-Type'].startswith('image/'))
                for old in ASSET_ALIASES:
                    self.assertFalse((ROOT/'static'/old.lstrip('/')).exists())
            finally:
                server.shutdown(); worker.join(timeout=5); server.server_close()

    def test_existing_overrides_and_history_are_read_only_in_public_state(self):
        s = game.new_campaign('fresh')
        s['assetOverrides'] = {'mira':'/user-assets/accepted.png','library':'/user-assets/accepted-room.webp'}
        s['assetHistory'] = {'mira':['/assets/portraits/mira.webp','/user-assets/earlier.png']}
        before = deepcopy(s)
        visible = game.public_state(s)
        self.assertEqual(s, before)
        self.assertEqual(visible['assetOverrides'], before['assetOverrides'])
        self.assertEqual(visible['assetHistory'], before['assetHistory'])
        self.assertEqual(visible['originalAssets']['gallery-suite-1'], visible['originalAssets']['gallery-suite-2'])
        self.assertEqual(visible['originalAssets']['heat-1'], '/assets/rooms/ember-chamber-family.webp')

    def test_chamber_override_is_independent_backed_up_and_reversible(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GameStore(directory, start_type='fresh')
            raw = (ROOT/'static/assets/rooms/quiet-chamber-family.webp').read_bytes()
            path = store.upload({'imageData':'data:image/webp;base64,'+base64.b64encode(raw).decode()})
            def act(action):
                return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action})
            before = store.read()
            act({'type':'accept-artwork','assetId':'echo-1','assetPath':path})
            accepted = GameStore(directory).read()
            self.assertEqual(accepted['assetOverrides']['echo-1'], path)
            self.assertNotIn('echo-2', accepted['assetOverrides'])
            with zipfile.ZipFile(io.BytesIO(store.backup_archive())) as archive:
                self.assertEqual(archive.read('assets/'+path.split('/')[-1]), raw)
            act({'type':'rollback-artwork','assetId':'echo-1'})
            final = store.read()
            self.assertEqual(final['assetOverrides']['echo-1'], ROOM_ASSETS['echo-1'])
            self.assertEqual(final['currentDayPhase'], before['currentDayPhase'])
            self.assertEqual(final['sharedFunds'], before['sharedFunds'])
