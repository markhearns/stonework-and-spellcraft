import unittest
import game as g
import local_encounters as local

class RecruitmentReasonsTests(unittest.TestCase):
    def test_actual_unlocks(self):
        s=g.new_campaign('fresh')
        v=local.view(s)['encounters']
        self.assertEqual(v['maren']['startBlockers'], [])
        self.assertIn('fern nursery', ' '.join(v['fenna']['startBlockers']))
        self.assertIn('conservatory', ' '.join(v['brakka']['startBlockers']))
        with self.assertRaisesRegex(g.RuleError,'fern nursery'):
            local.apply(s, {'type':'start-local-visit','encounterId':'fenna'})
    def test_pending_and_away_reasons(self):
        s=g.new_campaign('fresh')
        local.apply(s, {'type':'start-local-visit','encounterId':'maren'})
        self.assertIn('current local appointment', ' '.join(local.start_blockers(s,'fenna')))
        local.apply(s, {'type':'cancel-local-visit'})
        g.apply_action(s, {'type':'start-expedition','siteId':'old-waterworks'})
        self.assertIn('Return home', ' '.join(local.start_blockers(s,'maren')))
    def test_name_collision_readiness_matches_action(self):
        s=g.new_campaign('fresh')
        # Legacy/custom save fixture: newly created candidates reserve these names.
        s['people']['founder']['name']='Maren'
        v=local.view(s)['encounters']['maren']
        self.assertFalse(v['canStart'])
        self.assertIn('saved identity', ' '.join(v['startBlockers']))
