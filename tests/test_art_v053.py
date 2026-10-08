from copy import deepcopy
import json
from pathlib import Path
import unittest
import game
import local_encounters
import public_workshop
import public_content
from art_catalogue import ART_ASSETS, OBJECT_ART

ROOT=Path(__file__).resolve().parents[1]
class IntegratedArtTests(unittest.TestCase):
    def test_exact_catalogue_ids_and_instance_art_preserve_ownership_and_override(self):
        s=game.new_campaign('fresh')
        for i,key in enumerate(OBJECT_ART):
            self.assertIn(key,public_workshop.catalogue()['records'])
            s['publicWorkshop']['items'][str(i)]={'definitionId':key,'ownerId':'founder'}
        s['publicWorkshop']['items']['unknown']={'definitionId':'unillustrated','ownerId':'founder'}
        s['assetOverrides']['public-0']='/user-assets/accepted.png'
        before=deepcopy(s);view={'originalAssets':public_workshop.asset_slots(s),'assetOverrides':s['assetOverrides']}
        self.assertEqual(s,before)
        self.assertEqual(view['assetOverrides']['public-0'],'/user-assets/accepted.png')
        for i,key in enumerate(OBJECT_ART):self.assertEqual(public_workshop.asset_slots(s)[str('public-'+str(i))],OBJECT_ART[key])
        self.assertEqual(public_workshop.asset_slots(s)['public-unknown'],'/assets/placeholders/object-placeholder.svg')
    def test_all_new_locations_are_real_sites_and_portraits_have_slots(self):
        for key in ('old-waterworks','reedbank-waystation','hillfold-bindery','fern-nursery','quarry-shelter','ridge-cistern'):
            self.assertIn(key,game.EXPEDITION_SITES)
            self.assertEqual(game.ORIGINAL_ASSETS[key],ART_ASSETS[key])
        for key in ('tamsin','tamsin-outfit-2','elowen','nyssara','sylva'):
            self.assertIn('/portraits/',game.ORIGINAL_ASSETS[key])
    def test_nyssara_new_and_existing_profiles_are_enchanters(self):
        s=game.new_campaign('fresh');c=local_encounters.definition(s,'nyssara')
        self.assertEqual(c['profile']['role'],'Drow enchanter · 25')
        s['localEncounterCandidates']['nyssara']=deepcopy(c)
        s['people']['nyssara']=deepcopy(c['profile'])
        s['people']['nyssara']['role']='Dark elf mapmaker · 25'
        s['people']['nyssara']['ancestryLabel']='Dark elf'
        s['localEncounterCandidates']['nyssara']['profile']['role']='Dark elf mapmaker · 25'
        s['assetOverrides']['nyssara']='/user-assets/saved.png'
        s['schemaVersion']=43;before=deepcopy(s)
        game.migrate_state(s)
        self.assertEqual(s['schemaVersion'],66)
        self.assertEqual(s['people']['nyssara']['ancestryLabel'],'Drow')
        self.assertEqual(s['people']['nyssara']['role'],'Drow enchanter · 25')
        self.assertEqual(s['people']['nyssara']['identityHistory'][-1]['role'],'Dark elf mapmaker · 25')
        for key in ('assetOverrides','assetHistory','characterDevelopment','publicWorkshop','headquarters','livingStories'):
            self.assertEqual(s[key],before[key])
        once=deepcopy(s);game.migrate_state(s);self.assertEqual(s,once)
    def test_public_runtime_matches_validated_sources(self):
        _,_,packs=public_content.review_bundle(ROOT/'content/stonework-and-spellcraft-public-packs.zip')
        expected={k:{**r,'recordType':p['types'][k],'packId':report['packId']} for p,report in packs for k,r in p['entries'].items()}
        # v0.91 intentionally revised display summaries; all structured content remains source-identical.
        live=public_workshop.catalogue()['records']
        self.assertEqual({k:{f:v for f,v in r.items() if f!='summary'} for k,r in live.items()}, {k:{f:v for f,v in r.items() if f!='summary'} for k,r in expected.items()})
        self.assertTrue(all(isinstance(r['summary'],str) and r['summary'].strip() for r in live.values() if 'summary' in r))
        self.assertEqual(len(packs),16)
        self.assertNotIn('ss-private-mystery-foundations',public_workshop.catalogue()['sourceDigests'])

    def test_sylva_botanical_revision_keeps_saved_portrait_and_history(self):
        s=game.new_campaign('fresh');c=local_encounters.definition(s,'sylva')
        s['people']['sylva']=deepcopy(c['profile'])
        s['people']['sylva']['appearanceDescription']='Previous accepted identity description'
        s['assetOverrides']['sylva']='/user-assets/accepted-dryad.png'
        s['schemaVersion']=43;game.migrate_state(s)
        self.assertIn('sapwood',s['people']['sylva']['appearanceDescription'])
        self.assertIn('natural bare feet',s['people']['sylva']['appearanceDescription'])
        self.assertEqual(s['people']['sylva']['identityHistory'][-1]['appearanceDescription'],'Previous accepted identity description')
        self.assertEqual(s['assetOverrides']['sylva'],'/user-assets/accepted-dryad.png')
