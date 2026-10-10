"""Activity-backed mutual bonds and preservation of existing campaign history."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
import uuid

import game as g
import resident_bonds as b
import relationships
import field_patrols
from server import GameStore
import test_household_chapters as household


class ResidentBondTests(unittest.TestCase):
    def setUp(self):
        self.s = g.new_campaign()
        self.member('tamsin')
        self.member('iona')

    def member(self, who):
        household.HouseholdChapterTests.member(self, who)
        self.s['housingRooms']['garden-chamber']['status'] = 'complete'
        self.s['bedroomAssignments'][who] = 'garden-chamber'

    def act(self, kind, **fields):
        g.apply_action(self.s, dict(type=kind, **fields))

    def score(self, a='mira', c='tamsin'):
        return next(r['score'] for r in b.view(self.s)['pairs'] if r['id'] == b.pair_id(a, c))

    def test_all_resident_pairs_are_visible_without_mutation_or_player_pairs(self):
        old = deepcopy(self.s)
        view = b.view(self.s)
        self.assertEqual(self.s, old)
        self.assertEqual(len(view['pairs']), 3)
        self.assertTrue(all('founder' not in r['participants'] and r['score'] == 0 for r in view['pairs']))
        view['pairs'][0]['history'].append('external')
        self.assertEqual(self.s, old)
        self.assertEqual(b.view(g.new_campaign('fresh'))['pairs'], [])

    def test_pair_is_mutual_and_supports_all_residents_not_a_fixed_cast(self):
        for n in range(47):
            self.s['additionalResidents']['custom-' + str(n)] = {'status': 'resident'}
        self.assertEqual(len(b.view(self.s)['pairs']), 50 * 49 // 2)
        b.award(self.s, ['custom-0', 'mira', 'founder'], 'scene', 'Shared company', 2)
        self.assertEqual(self.score('mira', 'custom-0'), 2)
        self.assertEqual(b.pair_id('custom-0', 'mira'), b.pair_id('mira', 'custom-0'))
        self.assertEqual(len(b.saved(self.s)['pairs']), 1)

    def test_one_off_scene_points_repeat_protection_and_player_relationships(self):
        self.act('share-relationship', sceneId='story:table', choice='listen')
        self.assertEqual(self.score(), 2)
        self.assertEqual(self.score('mira', 'iona'), 0)
        old = deepcopy(self.s)
        relationships.remember(self.s, 'story:table', {'title': 'Repeated', 'participants': ['founder', 'mira', 'tamsin']})
        self.assertEqual(old, self.s)
        self.assertEqual(relationships.saved(self.s)['bonds']['founder|mira']['trust'], 1)
        before = deepcopy(self.s)
        g.public_state(self.s)
        g.public_state(self.s)
        self.assertEqual(self.s, before)

    def test_daily_cap_reset_maximum_and_bounded_history(self):
        for day in range(1, 28):
            self.s['dayNumber'] = day
            for n in range(12):
                b.award(self.s, ['mira', 'tamsin'], str(n), 'Actual activity', 2)
            self.assertEqual(self.score(), min(100, day * 4))
        row = b.saved(self.s)['pairs']['mira|tamsin']
        self.assertLessEqual(len(row['history']), 5)
        self.assertLessEqual(len(row['daily']['sources']), 4)
        self.assertEqual(next(r for r in b.view(self.s)['pairs'] if r['id'] == 'mira|tamsin')['level'], 5)

    def test_level_thresholds(self):
        b.award(self.s, ['mira', 'tamsin'], 'one', 'Shared activity')
        for score, level in [(0, 0), (9, 0), (10, 1), (25, 2), (45, 3), (70, 4), (99, 4), (100, 5)]:
            b.saved(self.s)['pairs']['mira|tamsin']['score'] = score
            row = next(r for r in b.view(self.s)['pairs'] if r['id'] == 'mira|tamsin')
            self.assertEqual(row['level'], level)

    def test_work_assignment_alone_gives_nothing_until_real_phase(self):
        self.act('start-research')
        for who in ('mira', 'tamsin'):
            self.act('assign-character', characterId=who, assignment='archive')
        self.assertEqual(self.score(), 0)
        before = deepcopy(self.s)
        b.phase_groups(self.s)
        self.assertEqual(self.s, before)
        self.act('advance')
        self.assertEqual(self.score(), 1)
        self.assertEqual(self.score('mira', 'iona'), 0)
        self.assertTrue(any('Resident bonding:' in line for line in self.s['lastPhaseSummary']))

    def test_gathering_and_restored_garden_build_only_matching_workers(self):
        for kind in ('hunt', 'forage', 'garden'):
            self.setUp()
            self.s['restorationStatus'] = 'complete'
            g.set_character_assignment(self.s, 'mira', kind)
            g.set_character_assignment(self.s, 'tamsin', kind)
            self.act('advance')
            self.assertEqual(self.score(), 1, kind)
            self.assertEqual(self.score('mira', 'iona'), 0, kind)

    def test_lesson_requires_both_assignments_and_survives_completion(self):
        self.s['residentKnownPrinciples'].append('clear-instruction')
        self.act('start-lesson', learnerId='tamsin', teacherId='mira', subjectKind='principle', targetId='clear-instruction')
        g.set_character_assignment(self.s, 'mira', 'commissions')
        self.act('advance')
        self.assertEqual(self.score(), 0)
        self.act('resume-lesson', learnerId='tamsin')
        # Morning isolates the lesson from the evening meal/leisure routines.
        self.s['currentDayPhase'] = 'morning'
        self.act('advance')
        self.assertEqual(self.score(), 1)
        self.assertIn('clear-instruction', g.character_principles(self.s, 'tamsin'))
        self.assertIsNone(self.s['trainingProjects']['tamsin'])

    def test_ritual_work_uses_actual_participants_and_pauses(self):
        self.s['residentKnownPrinciples'].extend(['reference-binding', 'clear-instruction'])
        self.s['additionalResidents']['tamsin']['knownPrinciples'].append('reference-binding')
        self.s['lastingRituals']['project'] = {'id': 'archive-circle', 'done': 0, 'participants': ['mira', 'tamsin']}
        for who in ('mira', 'tamsin'):
            g.set_character_assignment(self.s, who, 'ritual-circle')
        self.act('advance')
        self.assertEqual(self.score(), 1)
        g.set_character_assignment(self.s, 'tamsin', 'commissions')
        self.act('advance')
        self.assertEqual(self.score(), 1)
        self.assertEqual(self.s['lastingRituals']['project']['done'], 1)

    def test_meals_require_food_kitchen_and_home_presence(self):
        for kitchen, food, expected in [(False, 99, 0), (True, 0, 0), (True, 99, 1)]:
            self.setUp()
            self.s['currentDayPhase'] = 'evening'
            self.s['facilityProjects']['kitchen']['status'] = 'complete' if kitchen else 'not-started'
            self.s['provisions']['stock'] = food
            self.s['provisions']['auto'] = False
            for who in ('mira', 'tamsin', 'iona'):
                g.set_character_assignment(self.s, who, 'commissions')
            self.act('advance')
            self.assertEqual(self.score(), expected)
        self.setUp()
        self.s['currentDayPhase'] = 'evening'
        self.s['facilityProjects']['kitchen']['status'] = 'complete'
        self.s['provisions']['stock'] = 99
        for who in ('mira', 'tamsin', 'iona'):
            g.set_character_assignment(self.s, who, 'commissions')
        self.s['expedition'] = {'siteId': 'old-waterworks', 'stage': 'ready-to-return', 'partyIds': ['founder', 'mira']}
        g.resolve_work(self.s)
        self.assertEqual(self.score(), 0)
        self.assertEqual(self.score('tamsin', 'iona'), 1)

    def test_evening_wind_down_includes_only_selected_people(self):
        self.s['currentDayPhase'] = 'evening'
        self.act('evening-rest', choice='tea', participants=['founder', 'mira', 'tamsin'])
        self.assertEqual(self.score(), 2)
        self.assertEqual(self.score('mira', 'iona'), 0)
        old = deepcopy(self.s)
        with self.assertRaises(g.RuleError):
            self.act('evening-rest', choice='tea', participants=['founder', 'mira', 'tamsin'])
        self.assertEqual(self.s, old)

    def test_leisure_needs_same_usable_room_and_actual_rest(self):
        from unittest.mock import patch
        self.s['headquarters']['rooms']['pool'] = 'complete'
        with patch('room_life.location', side_effect=lambda s, p: 'pool' if p in ('mira', 'tamsin') else 'library'):
            snapshot = b.phase_groups(self.s)
            b.resolve_phase(self.s, snapshot, [])
            self.assertEqual(self.score(), 1)
            b.resolve_phase(self.s, snapshot, [])
            self.assertEqual(self.score(), 1)
        self.assertEqual(self.score('mira', 'iona'), 0)

    def test_expedition_travel_only_awards_party_and_not_waiting(self):
        self.s['expedition'] = {'siteId': 'old-waterworks', 'stage': 'outbound', 'partyIds': ['founder', 'mira', 'tamsin']}
        old = deepcopy(self.s)
        g.expedition_forecast(self.s)
        self.assertEqual(self.s, old)
        g.resolve_expedition(self.s)
        self.assertEqual(self.score(), 1)
        self.assertEqual(self.score('mira', 'iona'), 0)
        g.resolve_expedition(self.s)
        self.assertEqual(self.score(), 1)

    def test_patrol_travel_and_waiting(self):
        field_patrols.initialize(self.s)
        self.s['fieldPatrols']['active'] = {'stage': 'outbound', 'party': ['mira', 'tamsin'],
            'name': 'Test patrol', 'enemies': ['wolf'], 'index': 0, 'mission': None}
        field_patrols.resolve(self.s, [])
        self.assertEqual(self.score(), 1)
        field_patrols.resolve(self.s, [])
        self.assertEqual(self.score(), 1)

    def test_departure_hides_pair_without_erasing_history(self):
        b.award(self.s, ['mira', 'tamsin'], 'scene', 'Shared company', 2)
        self.s['additionalResidents']['tamsin']['status'] = 'away'
        self.assertFalse(any('tamsin' in r['participants'] for r in b.view(self.s)['pairs']))
        b.award(self.s, ['mira', 'tamsin'], 'other', 'Not together', 2)
        self.s['additionalResidents']['tamsin']['status'] = 'resident'
        self.assertEqual(self.score(), 2)

    def test_migration_seeds_real_history_and_preserves_every_other_field(self):
        relationships.remember(self.s, 'old-scene', {'title': 'Old company', 'participants': ['mira', 'tamsin', 'founder']})
        self.s.pop('residentBonds')
        self.s['schemaVersion'] = 67
        self.s['assetOverrides']['mira'] = '/user-assets/custom.webp'
        old = deepcopy(self.s)
        g.migrate_state(self.s)
        self.assertEqual(self.score(), 2)
        for key, value in old.items():
            if key != 'schemaVersion':
                self.assertEqual(self.s[key], value, key)
        after = deepcopy(self.s)
        g.migrate_state(self.s)
        self.assertEqual(after, self.s)

    def test_store_upgrade_backup_action_retry_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GameStore(directory)
            self.s.pop('residentBonds')
            self.s['schemaVersion'] = 67
            with sqlite3.connect(store.database) as db:
                db.execute('UPDATE campaign SET state=? WHERE id=1', (json.dumps(self.s),))
            store = GameStore(directory)
            self.assertTrue(Path(directory, f'campaign-before-schema-67-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
            request = {'requestId': uuid.uuid4().hex, 'expectedRevision': store.read()['revision'],
                       'action': {'type': 'share-relationship', 'sceneId': 'story:table', 'choice': 'listen'}}
            store.action(request)
            old = store.read()
            store.action(request)
            self.assertEqual(old, store.read())
            self.assertEqual(GameStore(directory).read()['residentBonds'], old['residentBonds'])


if __name__ == '__main__':
    unittest.main()
