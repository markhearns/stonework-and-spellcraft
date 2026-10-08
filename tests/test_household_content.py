import base64
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
import content_packs
import household_content as h
import character_pool
import game as g
import personal_stories
from server import GameStore
from dialogue import DialogueService,ProviderSettings,dialogue_context

FULL=Path('static/examples/stonework-spellcraft-content-pack.zip')
PACK,REPORT=content_packs.validate(content_packs.decode_archive(base64.b64encode(FULL.read_bytes()).decode()))

class HouseholdContentTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign();self.s['activeContentPack']=REPORT['summary']
    def action(self,kind,**fields):return h.apply(self.s,{'type':kind,'ownerId':'mira','packDigest':REPORT['digest'],**fields},PACK)
    def prerequisite(self,rows):return {'prerequisitesReviewed':True,'requirementEvidence':['Reviewed in the test fixture: '+r[:200] for r in rows]}
    def scene(self,group=False):
        if group:self.s['additionalResidents']['tamsin']['status']='resident';self.s['bedroomAssignments']['tamsin']='bedchamber'
        seed=next(r for r in PACK['shared']['household-interaction'] if r['participants']==('two-npcs' if group else 'npc-player') and h.matches(self.s,'mira',r) and (not group or h.matches(self.s,'tamsin',r)))
        self.action('propose-content-scene',seedId=seed['id'],participants=['mira','tamsin'] if group else ['mira'],**self.prerequisite(seed['requirements']))
        return next(reversed(self.s['householdScenes']))
    def test_received_pack_all_counts_and_ancestries_generate(self):
        self.assertTrue(REPORT['valid']);self.assertEqual(REPORT['recordCount'],3595)
        self.assertEqual(sum(len(d['names']) for d in PACK['ancestries'].values()),2100)
        from candidate_proposals import validate_candidate
        for ancestry in content_packs.REGISTRY.values():
            for n in range(3):
                selection=character_pool.select(self.s,ancestry+str(n),{'contentSource':'imported','ancestry':ancestry},PACK)
                p,_=validate_candidate(json.dumps(character_pool.offline(self.s,selection,'x')),self.s)
                character_pool.validate_selection(p,selection)
    def test_scene_review_defer_join_and_no_rewards(self):
        before=deepcopy(self.s);key=self.scene();r=self.s['householdScenes'][key]
        with self.assertRaises(g.RuleError):self.action('join-content-scene',sceneId=key,choiceIndex=0)
        with self.assertRaises(g.RuleError):self.action('approve-content-scene',sceneId=key)
        self.action('revise-content-scene',sceneId=key,title='A quiet reading',invitation='Would you like some company?',opening='She leaves room beside the open book.',replies=['“A comfortable place to begin.”']*len(r['choices']))
        self.action('approve-content-scene',sceneId=key,contentReviewed=True)
        self.action('defer-content-scene',sceneId=key);self.action('restore-content-scene',sceneId=key)
        self.action('join-content-scene',sceneId=key,choiceIndex=0)
        with self.assertRaises(g.RuleError):self.action('join-content-scene',sceneId=key,choiceIndex=0)
        for field in ['dayNumber','currentDayPhase','sharedFunds','materialInventory','resonancePoints','founderAdvancement','residentAdvancement']:
            if field in before:self.assertEqual(self.s[field],before[field])
        self.assertEqual(len(h.context(self.s,'mira')),1);self.assertEqual(h.context(self.s,'tamsin'),[])
    def test_prerequisites_duplicates_membership_and_presence(self):
        seed=next(r for r in PACK['shared']['household-interaction'] if r['participants']=='npc-player')
        with self.assertRaises(g.RuleError):self.action('propose-content-scene',seedId=seed['id'],participants=['mira'])
        key=self.scene();r=self.s['householdScenes'][key]
        with self.assertRaises(g.RuleError):self.action('propose-content-scene',seedId=r['seed']['id'],participants=['mira'],**self.prerequisite(r['seed']['requirements']))
        self.action('approve-content-scene',sceneId=key,contentReviewed=True)
        self.s['expedition']={'companionId':'mira'}
        with self.assertRaises(g.RuleError):self.action('join-content-scene',sceneId=key,choiceIndex=0)
        self.action('defer-content-scene',sceneId=key)
        self.assertEqual(self.s['householdScenes'][key]['status'],'deferred')
    def test_group_history_and_no_private_leak(self):
        key=self.scene(True);self.action('approve-content-scene',sceneId=key,contentReviewed=True);self.action('join-content-scene',sceneId=key,choiceIndex=0)
        self.assertEqual(len(h.context(self.s,'tamsin')),1);self.assertEqual(h.context(self.s,'founder'),[])
        self.assertEqual(len(h.view(self.s)['sharedHistory']),1)
        self.assertIn('sharedHouseholdConversations',dialogue_context(self.s,'Hello','mira')[0]['content'])
    def test_declining_keeps_invitation_without_shared_memory(self):
        key=self.scene();r=self.s['householdScenes'][key]
        self.action('approve-content-scene',sceneId=key,contentReviewed=True)
        index=next(i for i,c in enumerate(r['choices']) if c['kind']=='decline')
        self.action('join-content-scene',sceneId=key,choiceIndex=index)
        self.assertEqual(r['status'],'deferred');self.assertEqual(h.context(self.s,'mira'),[])
        self.assertNotIn('completedOn',r)

    def test_styles_validation_and_snapshot_persistence(self):
        ensemble=PACK['shared']['ensemble'][0]
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.action('save-content-style',ensembleId=ensemble['id'],name='Reading')
        self.assertEqual(self.s,before)
        self.action('save-content-style',ensembleId=ensemble['id'],name='Reading',anatomyReviewed=True,residentAgreed=True)
        key=next(iter(self.s['residentStyles']['mira']))
        with self.assertRaises(g.RuleError):self.action('wear-content-style',styleId=key)
        self.action('wear-content-style',styleId=key,residentAgreed=True)
        self.assertEqual(h.wardrobe_context(self.s,'mira')['name'],'Reading')
        self.assertEqual(self.s['assetOverrides'],before['assetOverrides'])
        self.s['activeContentPack']=None
        self.assertEqual(h.wardrobe_context(self.s,'mira')['name'],'Reading')
        with self.assertRaises(g.RuleError):self.action('remove-content-style',styleId=key)
        self.action('restore-content-look');self.action('remove-content-style',styleId=key)
        self.assertIsNone(h.wardrobe_context(self.s,'mira'))
    def test_invalid_layer_coverage_and_ancestry(self):
        garments=PACK['shared']['clothing-component'];top=next(r for r in garments if r['slot']=='top');dress=next(r for r in garments if r['slot']=='dress')
        for ids in [[top['id']],[top['id'],dress['id']],[top['id'],top['id']]]:
            with self.assertRaises(g.RuleError):self.action('save-content-style',componentIds=ids,name='Bad',anatomyReviewed=True,residentAgreed=True)
        self.s['people']['mira']['ancestryLabel']='Seraph'
        with self.assertRaises(g.RuleError):self.action('save-content-style',ensembleId='ensemble-001',name='No wing openings',anatomyReviewed=True,residentAgreed=True)
    def test_story_pattern_scope_and_frozen_approval(self):
        pattern=PACK['shared']['story-development-pattern'][0]
        with self.assertRaises(g.RuleError):self.action('choose-story-pattern',patternId=pattern['id'])
        self.action('choose-story-pattern',patternId=pattern['id'],**self.prerequisite(pattern['requiredEstablishedFacts']))
        p=personal_stories.outline(self.s,'mira','personal-folio')
        self.assertIn(pattern['label'],p['title']);self.assertIn(pattern['meaningfulChoice'],p['proposedWork'])
        context=personal_stories.context(self.s,'mira','A personal study.')[0]['content'];self.assertIn('reviewedStoryPattern',context)
        draft={'id':'a'*32,'ownerId':'mira','proposal':p,'source':'offline','model':'offline','storyPattern':deepcopy(self.s['residentStoryPatterns']['mira'])}
        key=personal_stories.approve(self.s,draft);self.action('clear-story-pattern')
        self.assertEqual(self.s['personalStories'][key]['storyPattern']['pattern']['id'],pattern['id'])
    def test_sqlite_bundled_staging_atomic_retry_and_migration(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);report=store.validate_content_pack({'bundled':True})
            self.assertEqual(report['digest'],REPORT['digest']);self.assertIsNone(store.read()['activeContentPack'])
            def action(body):return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':body})
            action({'type':'activate-content-pack','digest':REPORT['digest'],'contentReviewed':True})
            seed=next(r for r in PACK['shared']['household-interaction'] if r['participants']=='npc-player')
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'propose-content-scene','ownerId':'mira','packDigest':REPORT['digest'],'seedId':seed['id'],'participants':['mira'],**self.prerequisite(seed['requirements'])}}
            saved=store.action(payload);self.assertEqual(store.action(payload),saved);self.assertEqual(GameStore(d).read(),saved)
            self.assertEqual(len(saved['householdScenes']),1)
            old=deepcopy(saved);old['schemaVersion']=32
            for k in ['householdScenes','residentStyles','residentCurrentStyles','residentStoryPatterns']:old.pop(k,None)
            g.migrate_state(old);self.assertEqual(old['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertEqual(old['activeContentPack'],saved['activeContentPack'])
