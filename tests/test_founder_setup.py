import copy
import json
import unittest
import game as g
import founder_setup
from dialogue import dialogue_context


class FounderSetupTests(unittest.TestCase):
    def action(self,**fields):
        return {'type':'save-founder-profile','name':'Aster','age':28,'pronouns':'they/them','background':'traveller','appearanceDescription':'Brown curls, green coat','backgroundNotes':'Keeps field notebooks',**fields}

    def test_profile_is_descriptive_and_preserves_art_and_progress(self):
        s=g.new_campaign('fresh');g.apply_action(s,{'type':'start-research'});g.apply_action(s,{'type':'advance'})
        s['assetOverrides']['founder']='/user-assets/kept.png';s['assetHistory']['founder']=['earlier']
        before=copy.deepcopy(s)
        g.apply_action(s,self.action())
        for key in s:
            if key not in ('people','soloLife','journal'):self.assertEqual(s[key],before[key],key)
        v=g.public_state(s)
        self.assertEqual(v['characterCatalog']['founder']['name'],'Aster')
        self.assertEqual(v['people']['founder']['adultAgeYears'],28)
        self.assertEqual(s['people']['founder']['personId'],'founder')
        g.apply_action(s,{'type':'finish-character-setup'})
        reloaded=g.migrate_state(json.loads(json.dumps(s)))
        self.assertTrue(reloaded['soloLife']['characterSetup']['finished'])
        self.assertEqual(founder_setup.profile(reloaded)['pronouns'],'they/them')

    def test_invalid_profile_is_atomic(self):
        s=g.new_campaign('fresh')
        for fields in [{'name':''},{'name':'x'*41},{'name':'bad\nname'},{'age':17},{'age':121},{'age':True},{'age':28.5},{'background':[]},{'background':'invented'},{'pronouns':'x'*41},{'appearanceDescription':'x'*601},{'backgroundNotes':None}]:
            before=copy.deepcopy(s)
            with self.assertRaises(g.RuleError):g.apply_action(s,self.action(**fields))
            self.assertEqual(s,before)
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'finish-character-setup'})
        g.apply_action(s,{'type':'start-expedition','siteId':'old-waterworks'})
        before=copy.deepcopy(s)
        with self.assertRaises(g.RuleError):g.apply_action(s,self.action())
        self.assertEqual(s,before)

    def test_old_saves_are_not_forced_to_restart_setup(self):
        for kind in ('fresh','demo'):
            s=g.new_campaign(kind);s['soloLife'].pop('characterSetup',None);before=copy.deepcopy(s)
            self.assertEqual(g.migrate_state(s),before)
            g.apply_action(s,self.action())
            self.assertTrue(s['soloLife']['characterSetup']['finished'])
            self.assertEqual(s['startType'],kind)

    def test_default_details_and_placeholder_remain_viable(self):
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'save-founder-profile','name':'Your scholar','age':40})
        g.apply_action(s,{'type':'finish-character-setup'})
        self.assertEqual(s['assetOverrides'],{})
        g.apply_action(s,{'type':'start-research'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['researchStatus'],'complete')

    def test_placeholder_keeps_previous_portrait_recoverable(self):
        s=g.new_campaign('fresh');s['assetOverrides']['founder']='/user-assets/prior.png'
        g.apply_action(s,{'type':'use-founder-placeholder'})
        self.assertNotIn('founder',s['assetOverrides'])
        g.apply_action(s,{'type':'rollback-artwork','assetId':'founder'})
        self.assertEqual(s['assetOverrides']['founder'],'/user-assets/prior.png')

    def test_dialogue_uses_saved_identity_without_private_background(self):
        s=g.new_campaign('demo');g.apply_action(s,self.action())
        context=dialogue_context(s,'Hello')[0]['content']
        self.assertIn('"age": 28',context);self.assertIn('"name": "Aster"',context)
        self.assertIn('they/them',context)
        self.assertNotIn('Keeps field notebooks',context)

    def test_portrait_prompt_excludes_private_story_and_uses_saved_appearance(self):
        s=g.new_campaign('fresh');g.apply_action(s,self.action())
        prompt=founder_setup.portrait_prompt(s)
        self.assertIn('Age: 28',prompt);self.assertIn('Brown curls',prompt)
        self.assertNotIn('Keeps field notebooks',prompt)
        self.assertNotIn('sharedFunds',prompt)
