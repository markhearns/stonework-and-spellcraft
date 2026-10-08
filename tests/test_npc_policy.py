from copy import deepcopy
from pathlib import Path
import unittest
import game
import summoning
import dialogue

class NpcPolicyTests(unittest.TestCase):
    def test_current_cast_and_assets(self):
        state=game.new_campaign()
        summoning.initialize_person(state)
        for who,age in [('mira',22),('tamsin',20),('iona',23)]:
            self.assertEqual(state['people'][who]['adultAgeYears'],age)
            summoning.validate_npc_profile(state['people'][who], summoned=who=='iona')
            self.assertTrue((Path(__file__).parents[1]/'static'/game.ORIGINAL_ASSETS[who].lstrip('/')).exists())
        self.assertEqual(state['people']['iona']['ancestryLabel'],'Demon')
        self.assertIn('"age": 22',dialogue.dialogue_context(state,'Hello')[0]['content'])

    def test_age_and_ancestry_gate(self):
        for age in [17,26,True,'22',None]:
            with self.assertRaises(ValueError):summoning.validate_npc_profile({**summoning.PROFILE,'adultAgeYears':age},True)
        for ancestry in ['Human','Elf','Dwarf','']:
            with self.assertRaises(ValueError):summoning.validate_npc_profile({**summoning.PROFILE,'ancestryLabel':ancestry},True)
        for ancestry in ['Demon','Seraph','Elemental','Vampire']:
            summoning.validate_npc_profile({**summoning.PROFILE,'ancestryLabel':ancestry},True)

    def test_existing_identity_migration_preserves_progress_and_history(self):
        state=game.new_campaign();summoning.initialize_person(state)
        state['schemaVersion']=22
        state['people']['mira']['adultAgeYears']=32
        state['people']['iona'].update(adultAgeYears=38,ancestryLabel='Human')
        state['assetOverrides']['mira']='/user-assets/old.png'
        state['sharedFunds']=137
        before=deepcopy(state)
        game.migrate_state(state)
        self.assertEqual(state['people']['mira']['adultAgeYears'],22)
        self.assertEqual(state['people']['iona']['ancestryLabel'],'Demon')
        self.assertNotIn('mira',state['assetOverrides'])
        self.assertEqual(state['assetHistory']['mira'][-1],'/user-assets/old.png')
        for key in ['sharedFunds','dayNumber','currentDayPhase','residency']:
            self.assertEqual(state[key],before[key])
        upgraded=deepcopy(state);game.migrate_state(state);self.assertEqual(state,upgraded)
