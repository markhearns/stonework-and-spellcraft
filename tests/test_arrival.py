"""Arrival choices are narrative only, persistent, optional, and upgrade-safe."""
import copy
import json
import tempfile
import unittest
import uuid

import game as g
import solo_life
from server import GameStore


class ArrivalTests(unittest.TestCase):
    def choose(self, s, stage, choice):
        g.apply_action(s, {'type':'choose-arrival','stageId':stage,'choiceId':choice})

    def test_every_branch_is_persistent_without_mechanical_effects(self):
        for purpose in ('home','study','beginning'):
            for attention in ('hearth','shelves','window'):
                s=g.new_campaign('fresh');before=copy.deepcopy(s)
                self.choose(s,'purpose',purpose)
                s=g.migrate_state(json.loads(json.dumps(s)))
                self.assertEqual(solo_life.arrival_view(s)['stage']['id'],'attention')
                self.choose(s,'attention',attention)
                g.apply_action(s,{'type':'enter-castle'})
                self.assertTrue(solo_life.arrival_view(s)['completed'])
                self.assertEqual(len(solo_life.arrival_view(s)['memories']),2)
                for key in s:
                    if key not in ('soloLife','journal'):self.assertEqual(s[key],before[key],key)
                g.apply_action(s,{'type':'start-research'})
                for _ in range(3):g.apply_action(s,{'type':'advance'})
                self.assertEqual(s['researchStatus'],'complete')

    def test_invalid_out_of_order_and_repeat_choices_are_atomic(self):
        s=g.new_campaign('fresh')
        actions=[{'type':'choose-arrival','stageId':'attention','choiceId':'window'},
                 {'type':'choose-arrival','stageId':'purpose','choiceId':[]},
                 {'type':'choose-arrival','stageId':None,'choiceId':'home'},
                 {'type':'enter-castle'}]
        for a in actions:
            before=copy.deepcopy(s)
            with self.assertRaises(g.RuleError):g.apply_action(s,a)
            self.assertEqual(s,before)
        self.choose(s,'purpose','home');before=copy.deepcopy(s)
        with self.assertRaises(g.RuleError):self.choose(s,'purpose','study')
        self.assertEqual(s,before)
        g.apply_action(s,{'type':'skip-arrival'});before=copy.deepcopy(s)
        with self.assertRaises(g.RuleError):self.choose(s,'attention','hearth')
        self.assertEqual(s,before)

    def test_skip_at_each_stage_keeps_only_actual_choices(self):
        for count in range(3):
            s=g.new_campaign('fresh')
            for stage in solo_life.ARRIVAL[:count]:self.choose(s,stage['id'],stage['choices'][0]['id'])
            g.apply_action(s,{'type':'skip-arrival'})
            v=solo_life.arrival_view(g.migrate_state(json.loads(json.dumps(s))))
            self.assertTrue(v['completed']);self.assertTrue(v['skipped'])
            self.assertEqual(len(v['memories']),count)
            self.assertEqual(s['sharedFunds'],40)
            self.assertEqual((s['dayNumber'],s['currentDayPhase']),(1,'morning'))

    def test_existing_saves_and_art_are_not_rewritten(self):
        s=g.new_campaign('fresh');del s['soloLife']['arrival']
        s['assetOverrides']['founder']='/campaign-assets/accepted.png'
        s['assetHistory']['founder']=['preserved-history']
        before=copy.deepcopy(s)
        self.assertEqual(g.migrate_state(s),before)
        self.assertIsNone(solo_life.arrival_view(s))
        self.assertIsNone(solo_life.arrival_view(g.new_campaign('demo')))
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'skip-arrival'})
        self.assertEqual(s,before)

    def test_store_retry_reload_and_revision_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d,start_type='fresh')
            s=store.read()
            request={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],
                     'action':{'type':'choose-arrival','stageId':'purpose','choiceId':'study'}}
            result=store.action(request)
            retry=store.action(request)
            self.assertEqual(result,retry)
            reloaded=GameStore(d).read()
            self.assertEqual(reloaded['soloLife']['arrival']['choices'],{'purpose':'study'})
            self.assertEqual(len([r for r in reloaded['journal'] if r['text'].startswith('Arrival —')]),1)
            stale={**request,'requestId':uuid.uuid4().hex,'action':{'type':'skip-arrival'}}
            with self.assertRaises(Exception):store.action(stale)
            self.assertEqual(store.read(),reloaded)
