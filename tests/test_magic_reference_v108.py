"""Catalogue completeness and read-only behaviour across saved campaign states."""
from copy import deepcopy
from pathlib import Path
import unittest
import game
import lasting_rituals
import magic_reference
import public_workshop


class MagicReferenceTests(unittest.TestCase):
    def test_executable_catalogues_are_covered_without_duplicate_baseline_studies(self):
        state = game.new_campaign('fresh')
        before = deepcopy(state)
        reference = magic_reference.view(state)
        self.assertEqual(state, before)
        entries = {row['id']: row for row in reference['entries']}
        self.assertEqual(len(entries), len(reference['entries']))
        self.assertEqual(set(game.SPELL_FORMS), {key for key, row in entries.items() if row['kind'] == 'spell' and row['collection'] == 'castle'})
        self.assertTrue(set(lasting_rituals.CATALOGUE).issubset(entries))
        self.assertTrue({'concordant-lesson', 'lamplit-sight', 'lamplit-reversal'}.issubset(entries))
        workshop = {r['id'] for r in public_workshop.catalogue()['records'].values() if r['recordType'] in ('spell-construction', 'ritual-concept') and r.get('mechanicsProposalId')}
        self.assertEqual(workshop, {r['recordId'] for r in entries.values() if r['collection'] == 'workshop'})
        self.assertEqual(len(entries), 142)
        self.assertEqual(len({r['scholarNote']['quote'] for r in entries.values()}), len(entries))
        root = Path(game.__file__).parent / 'static'
        for key, row in entries.items():
            self.assertTrue((root / row['art'].lstrip('/')).is_file(), key)
            self.assertTrue(row['requirements'], key)
            self.assertTrue(row['cost'], key)
            self.assertTrue(row['scholarNote']['quote'], key)
            if key in game.SPELL_FORMS:
                self.assertEqual(row['effect'], game.SPELL_FORMS[key]['effect'])
            if key in lasting_rituals.CATALOGUE:
                self.assertEqual(row['effect'], lasting_rituals.CATALOGUE[key]['effect'])

    def test_completed_and_suspended_rituals_and_custom_art_survive_reference_read(self):
        state = game.new_campaign()
        state['lastingRituals']['completed'] = {'archive-circle': {'active': True}, 'maker-circle': {'active': False}}
        state['assetOverrides']['neris-outfit-3'] = '/user-assets/accepted-neris.webp'
        state['assetHistory']['neris-outfit-3'] = ['/user-assets/earlier-neris.webp']
        before = deepcopy(state)
        visible = game.public_state(state)
        entries = {r['id']: r for r in visible['magicReferenceView']['entries']}
        self.assertEqual(entries['archive-circle']['status'], 'Active')
        self.assertEqual(entries['maker-circle']['status'], 'Suspended')
        self.assertEqual(visible['assetOverrides'], before['assetOverrides'])
        self.assertEqual(visible['assetHistory'], before['assetHistory'])
        self.assertEqual(state, before)

    def test_reference_escapes_are_left_to_ui_and_no_workshop_rules_are_mutated(self):
        state = game.new_campaign()
        catalogue = deepcopy(public_workshop.catalogue())
        for _ in range(2):
            magic_reference.view(state)
        self.assertEqual(public_workshop.catalogue(), catalogue)


if __name__ == '__main__':
    unittest.main()
