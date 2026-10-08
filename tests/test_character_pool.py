from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game as g
import character_pool as pool
from candidate_proposals import validate_candidate
from dialogue import DialogueService,ProviderSettings
from server import GameStore

class CharacterPoolTests(unittest.TestCase):
    def test_all_compatible_combinations_and_bounded_prose(self):
        s=g.new_campaign()
        for ancestry,d in pool.ANCESTRIES.items():
            for background in d['backgrounds']:
                for story in pool.BACKGROUNDS[background]['stories']:
                    choices={'ancestry':ancestry,'background':background,'story':story}
                    selection=pool.select(s,'a'*32,choices)
                    p,r=validate_candidate(json.dumps(pool.offline(s,selection,'a'*32)),s)
                    pool.validate_selection(p,selection)
                    self.assertEqual(r['startingSkillRanks'],0)
                    self.assertEqual(r['earnedAdvancement'],0)
                    self.assertEqual(selection,pool.select(s,'a'*32,choices))
    def test_incompatible_and_malformed_choices(self):
        for choice in [[],{'ancestry':[]},{'background':'king'},{'ancestry':'Vampire','background':'gardener'},{'background':'bookbinder','story':'water-study'},{'power':'infinite'}]:
            with self.assertRaises(g.RuleError):pool.select(g.new_campaign(),'a'*32,choice)
    def test_variety_and_identity_preservation(self):
        s=g.new_campaign();before=deepcopy(s);ancestries=set();personalities=set();skins=set()
        for n in range(100):
            selection=pool.select(s,str(n));ancestries.add(selection['ancestry']);personalities.add(selection['temperament']);skins.add(selection['appearance']['skin'])
        self.assertEqual(len(ancestries),12);self.assertEqual(len(personalities),8);self.assertGreaterEqual(len(skins),8);self.assertEqual(s,before)
    def test_offline_no_provider_retry_binding_and_approval(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);calls=[];svc=DialogueService(ProviderSettings(d),lambda *_:calls.append(1))
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':0,'purpose':'candidate-proposal','source':'offline','poolChoices':{'ancestry':'Seraph'},'text':'An optional brief.'}
            draft=svc.generate(store,payload);self.assertEqual(draft['status'],'ready');self.assertEqual(calls,[])
            self.assertEqual(svc.generate(store,payload),draft)
            with self.assertRaises(g.RuleError):svc.generate(store,{**payload,'poolChoices':{'ancestry':'Demon'}})
            with self.assertRaises(g.RuleError):svc.accept(store,{'draftId':draft['id']})
            s=svc.accept(store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
            profile=s['reviewedCandidates']['summoned-'+draft['id']]['profile']
            self.assertEqual(profile['generationIngredients'],draft['generationIngredients']);self.assertEqual(s['currentDayPhase'],'afternoon')
            self.assertEqual(svc.accept(store,{'draftId':draft['id']}),s)
    def test_provider_selected_rules_reject_drift(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d);settings=ProviderSettings(d);settings.save({'enabled':True,'model':'fixture','apiKey':'secret','maxOutputTokens':1000})
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':0,'purpose':'candidate-proposal','poolChoices':{'ancestry':'Seraph','background':'lampwright'},'text':'An adult artisan.'}
            selection=pool.select(store.read(),payload['requestId'],payload['poolChoices']);p=pool.offline(store.read(),selection,payload['requestId']);p['capabilityPackageId']='archive-reader'
            calls=[]
            def completion(settings,messages):calls.append(messages);return {'text':json.dumps(p)}
            svc=DialogueService(settings,completion);draft=svc.generate(store,payload)
            self.assertEqual(draft['status'],'failed');self.assertIn('selected ancestry',draft['error']);self.assertIn('Selected curated ingredients',calls[0][0]['content'])
            self.assertEqual(store.read()['reviewedCandidates'],{})
            svc.generate(store,payload);self.assertEqual(len(calls),1)
    def test_appearance_and_story_do_not_change_mechanics(self):
        s=g.new_campaign();selection=pool.select(s,'a'*32);p=pool.offline(s,selection,'a'*32)
        for key in ['ancestryLabel','occupation','adultAgeYears','capabilityPackageId']:
            other=deepcopy(p);other[key]='invented'
            with self.assertRaises(g.RuleError):pool.validate_selection(other,selection)
    def test_legacy_angel_terminology_migration_keeps_identity_and_art(self):
        s=g.new_campaign();s['people']['old-seraph']={'personId':'old-seraph','name':'Established name','ancestryLabel':'Angel','role':'Angel artisan · 24','generationIngredients':{'ancestry':'Angel'}}
        s['assetOverrides']['old-seraph']='/custom-assets/saved.png';s['schemaVersion']=29
        g.migrate_state(s)
        self.assertEqual(s['people']['old-seraph']['ancestryLabel'],'Seraph');self.assertEqual(s['people']['old-seraph']['name'],'Established name');self.assertEqual(s['assetOverrides']['old-seraph'],'/custom-assets/saved.png')
        self.assertEqual(s['people']['old-seraph']['generationIngredients']['ancestry'],'Seraph')
        selection=pool.select(g.new_campaign(),'a'*32,{'ancestry':'Angel'});self.assertEqual(selection['ancestry'],'Seraph')
