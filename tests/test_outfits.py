from copy import deepcopy
import json
import unittest
import game as g
import outfit_progression as outfits
import personal_stories

class OutfitTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,tier='2',who='mira'):
        return g.apply_action(self.s,{'type':kind,'characterId':who,'tier':tier})
    def reject(self,kind,tier='2',who='mira'):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,tier,who)
        self.assertEqual(before,self.s)
    def memory(self,key):self.s['residentMoments'][key]['status']='complete'
    def test_tree_needs_new_shared_evidence(self):
        self.reject('choose-outfit');self.reject('accept-outfit-invitation')
        self.memory('mira-greenhouse');self.memory('mira-index');self.memory('mira-folio')
        before=(self.s['dayNumber'],self.s['currentDayPhase'],self.s['sharedFunds'])
        self.act('accept-outfit-invitation');self.assertIsNone(outfits.current(self.s,'mira'))
        self.reject('accept-outfit-invitation');self.reject('accept-outfit-invitation','3')
        self.memory('shared-shelf');self.act('accept-outfit-invitation','3');self.act('choose-outfit','3')
        self.assertEqual(outfits.current(self.s,'mira')['id'],'mira-outfit-3')
        self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase'],self.s['sharedFunds']))
        self.act('choose-outfit',None);self.assertIsNone(outfits.current(self.s,'mira'))
    def test_migration_preserves_overrides_styles_and_history(self):
        s=self.s;s['schemaVersion']=44;s.pop('outfitProgression',None)
        s['assetOverrides']['mira']='/user-assets/accepted.png';before=deepcopy(s)
        g.migrate_state(s);self.assertEqual(s['schemaVersion'],g.CURRENT_SCHEMA_VERSION)
        for k in ('assetOverrides','wardrobe','savedStyles','conversation','livingStories'):self.assertEqual(s[k],before[k])
        self.assertEqual(s['outfitProgression'],{})
        self.assertEqual(g.migrate_state(json.loads(json.dumps(s))),s)
    def test_rejects_unknown_visitors_and_invalid_tiers_without_mutation(self):
        for who in ('founder','unknown','sylva',None,[]):self.reject('accept-outfit-invitation',who=who)
        for tier in (None,'1','4',{},[]):self.reject('accept-outfit-invitation',tier)
    def test_selected_art_and_custom_override_survive_reload(self):
        self.memory('mira-greenhouse');self.act('accept-outfit-invitation');self.act('choose-outfit')
        self.s['assetOverrides']['mira-outfit-2']='/user-assets/chosen.png'
        self.s=g.migrate_state(json.loads(json.dumps(self.s)))
        self.assertEqual(personal_stories.portrait(self.s,'mira'),'/user-assets/chosen.png')
        self.assertEqual(g.public_state(self.s)['outfitProgressionView']['mira']['portraitId'],'mira-outfit-2')
    def test_fresh_campaign_has_no_phantom_companions(self):
        self.assertEqual(outfits.view(g.new_campaign('fresh')), {})
    def test_complete_cast_has_two_distinct_art_slots(self):
        self.assertEqual(len(outfits.CATALOGUE),16)
        ids=[look['id'] for looks in outfits.CATALOGUE.values() for look in looks.values()]
        self.assertEqual(len(set(ids)),32)
    def test_all_three_portraits_per_character_are_separate_bundled_files(self):
        import hashlib
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/'static'
        all_hashes=[]
        for who,looks in outfits.CATALOGUE.items():
            urls=[g.ORIGINAL_ASSETS[key] for key in [who,looks['2']['id'],looks['3']['id']]]
            self.assertEqual(len(set(urls)),3,who)
            all_hashes.extend(hashlib.sha256((root/url.lstrip('/')).read_bytes()).hexdigest() for url in urls)
        self.assertEqual(len(set(all_hashes)),48)
    def test_outfit_art_review_rollback_preserves_progression(self):
        self.memory('mira-greenhouse');self.act('accept-outfit-invitation');self.act('choose-outfit')
        before=deepcopy(self.s['outfitProgression'])
        g.apply_action(self.s,{'type':'accept-artwork','assetId':'mira-outfit-2','assetPath':'/user-assets/accepted.png'})
        self.assertEqual(personal_stories.portrait(self.s,'mira'),'/user-assets/accepted.png')
        g.apply_action(self.s,{'type':'rollback-artwork','assetId':'mira-outfit-2'})
        self.assertEqual(personal_stories.portrait(self.s,'mira'),g.ORIGINAL_ASSETS['mira-outfit-2'])
        self.assertEqual(self.s['outfitProgression'],before)

    def test_three_outfit_tiers_in_both_portrait_formats(self):
        from pathlib import Path
        folder=Path(__file__).resolve().parents[1]/'static/assets/portraits'
        expected={who+suffix+'.webp' for who in outfits.CATALOGUE for suffix in ('','-outfit-2','-outfit-3')}
        self.assertEqual({p.name for p in folder.iterdir() if p.is_file()},expected)
        self.assertEqual({p.name for p in (folder/'overview').iterdir() if p.is_file()},expected)
        slots={key for key,url in g.ORIGINAL_ASSETS.items() if url.startswith('/assets/portraits/')}
        self.assertEqual(slots,{prefix+name.removesuffix('.webp') for name in expected for prefix in ('','overview-')} | {who+'-bathing' for who in outfits.CATALOGUE})

    def test_retired_styling_keeps_canonical_art_and_relationship_gates(self):
        self.s['wardrobe']['outerLayer']='plum-shawl'
        self.assertEqual(personal_stories.portrait(self.s,'mira'),'/assets/portraits/mira.webp')
        self.assertEqual(outfits.view(self.s)['mira']['portraitId'],'mira')
        self.reject('choose-outfit')
        self.memory('mira-greenhouse');self.act('accept-outfit-invitation');self.act('choose-outfit')
        self.assertEqual(personal_stories.portrait(self.s,'mira'),'/assets/portraits/mira-outfit-2.webp')
