from copy import deepcopy
from itertools import permutations
import json
import unittest
import game as g
import headquarters as h
import house_shape as shape
import room_to_grow as grow
import test_house_shape as chapter_two

class RoomToGrowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chapter_two.HouseShapeTests.setUpClass()
        t=chapter_two.HouseShapeTests();t.setUp()
        for key,design in [('scholarship','table'),('cultivation','nursery'),('craftsmanship','production')]:t.run_chapter(key,design)
        cls.before_closing=deepcopy(t.s)
        t.act('shape-conclude');cls.beginning=deepcopy(t.s)

    def setUp(self):self.s=deepcopy(self.beginning)
    def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
    def plan(self,layout='private',communal='chapel',specialist='infirmary',priority='accommodation'):
        self.act('grow-plan',layout=layout,communal=communal,specialist=specialist,priority=priority)
    def play(self,closing='quiet'):
        phases=0
        for _ in range(160):
            before=deepcopy(self.s);v=grow.view(self.s);self.assertEqual(self.s,before)
            if v['stage']=='complete':return phases
            if v['stage']=='walkthrough':self.act('grow-inspect',area=next(x['id'] for x in v['inspections'] if not x['complete']))
            elif v['stage']=='closing':self.act('grow-finish',choice=closing)
            else:
                n=v['next'];self.assertTrue(n,n);self.assertTrue(n['action'],n);self.assertFalse(n.get('blockers'),n)
                g.apply_action(self.s,n['action']);phases+=n['action']['type']=='advance'
            self.s=g.migrate_state(json.loads(json.dumps(self.s)))
        self.fail(repr(grow.view(self.s)))

    def test_all_layouts_and_facilities_from_earned_three_chapters(self):
        for layout,community,specialist,priority in [
            ('private','chapel','infirmary','accommodation'),('shared','sauna','smithy','specialists'),
            ('mixed','chapel','command-room','community'),('mixed','sauna','infirmary','accommodation')]:
            with self.subTest(layout=layout,specialist=specialist):
                self.s=deepcopy(self.beginning);self.plan(layout,community,specialist,priority)
                budget=grow.view(self.s)['budget'];funds=self.s['sharedFunds'];people=deepcopy(self.s['bedroomAssignments']);lore=deepcopy(self.s['privateCastleLore'])
                self.play('gather')
                v=grow.view(self.s);self.assertEqual(v['stage'],'complete');self.assertEqual(v['budget']['remainingCost'],0)
                self.assertEqual(v['budget']['heldCost'],0);self.assertEqual(self.s['bedroomAssignments'],people)
                self.assertEqual(self.s['privateCastleLore'],lore);self.assertFalse(self.s['testing']['used'])
                self.assertEqual(len(v['memories']),6);self.assertTrue(v['record']['contributions'])
                before=deepcopy(self.s)
                with self.assertRaises(g.RuleError):self.act('grow-finish',choice='quiet')
                self.assertEqual(before,self.s)

    def test_all_three_undertakings_and_explicit_closing_are_required(self):
        self.s=deepcopy(self.before_closing);self.assertFalse(grow.available(self.s))
        with self.assertRaises(g.RuleError):self.plan()
        for key in shape.PATHS:
            original=self.s['houseShape']['projects'].pop(key)
            with self.assertRaises(g.RuleError):self.act('shape-conclude')
            self.s['houseShape']['projects'][key]=original
        funds=self.s['sharedFunds'];day=self.s['dayNumber'];evidence=deepcopy(self.s['castleMystery']['discoveries'])
        self.act('shape-conclude');self.assertTrue(grow.available(self.s))
        self.assertEqual(self.s['sharedFunds'],funds);self.assertEqual(self.s['dayNumber'],day);self.assertEqual(evidence,self.s['castleMystery']['discoveries'])
        self.assertEqual(sum(x['work'] for x in shape.saved(self.s)['conclusion']['contributions'].values()),18)

    def test_priorities_keep_paid_work_and_exact_budget(self):
        self.plan('mixed','sauna','smithy')
        self.s['sharedFunds']=300
        initial=grow.view(self.s)['budget'];self.act('hq-build',roomId='underground-quarters');self.act('advance')
        paid=deepcopy(h.project_for(self.s));funds=self.s['sharedFunds']
        for priority in grow.PRIORITIES:
            self.act('grow-priority',priority=priority);self.assertEqual(h.project_for(self.s),paid)
            self.assertEqual(self.s['sharedFunds'],funds);v=grow.view(self.s)
            self.assertEqual(v['next']['id'],'underground-quarters');self.assertEqual(v['budget']['heldCost'],45)
            self.assertEqual(v['budget']['remainingCost'],initial['remainingCost']-45)
        self.act('hq-pause');self.assertEqual(grow.view(self.s)['next']['action']['type'],'hq-resume')
        self.act('hq-cancel');self.assertEqual(self.s['sharedFunds'],funds+45)
        self.assertEqual(grow.view(self.s)['budget']['remainingCost'],initial['remainingCost'])
        self.assertEqual(grow.saved(self.s)['contributions']['underground-quarters']['founder']['work'],1)

    def test_real_resident_credit_and_scoped_gathering(self):
        t=chapter_two.HouseShapeTests();t.s=self.s;t.recruit();self.s=t.s
        self.plan(priority='community');t.s=self.s;t.money(100)
        self.act('hq-agree-work',workerId='maren',enabled=True)
        self.act('hq-build',roomId='chapel',workerId='maren')
        self.act('advance');self.act('advance')
        self.assertEqual(grow.saved(self.s)['contributions']['chapel']['maren']['work'],2)
        self.play('gather');self.assertTrue(grow.context(self.s,'maren'))
        self.assertEqual(len(grow.context(self.s,'maren')),1)
        self.assertIn('Maren',grow.context(self.s,'maren')[0]['text'])
        self.assertEqual(grow.context(self.s,'mira'),[])

    def test_invalid_actions_are_atomic_and_read_does_not_enroll(self):
        before=deepcopy(self.s);grow.view(self.s);self.assertEqual(before,self.s);self.assertNotIn('roomToGrow',self.s)
        for a in ({'type':'grow-plan','layout':[]},{'type':'grow-finish','choice':'quiet'}):
            with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
            self.assertEqual(before,self.s)
        self.plan();before=deepcopy(self.s)
        for a in ({'type':'grow-inspect','area':'bedrooms'},{'type':'grow-finish','choice':'quiet'},
                  {'type':'grow-priority','priority':[]},{'type':'grow-worker','workerId':'unknown'},{'type':'grow-visibility','enabled':'false'}):
            with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
            self.assertEqual(before,self.s)

    def test_already_completed_rooms_count_without_invented_work(self):
        self.plan('shared','chapel','infirmary');self.play()
        self.s.pop('roomToGrow');before=self.s['sharedFunds'];self.plan('shared','chapel','infirmary')
        self.assertEqual(grow.view(self.s)['stage'],'walkthrough');self.assertEqual(grow.view(self.s)['budget']['remainingCost'],0)
        self.assertEqual(self.play(),0);self.assertEqual(self.s['sharedFunds'],before)
        self.assertEqual(grow.saved(self.s)['contributions'],{})
        self.assertIn('already restored',grow.saved(self.s)['memories'][-1]['text'])

    def test_plan_previews_deduplicate_dependencies(self):
        for layout in grow.LAYOUTS:
            for community in grow.COMMUNAL:
                for specialist in grow.SPECIALIST:
                    costs=[]
                    for priority in grow.PRIORITIES:
                        config=dict(layout=layout,communal=community,specialist=specialist,priority=priority)
                        rows=grow.rows(self.s,config);ids=[x['id'] for x in rows]
                        self.assertEqual(len(ids),len(set(ids)))
                        for row in rows:
                            for dep in row['needs']:self.assertLess(ids.index(dep),ids.index(row['id']))
                        costs.append(grow.budget(rows)['remainingCost'])
                    self.assertEqual(len(set(costs)),1)

    def test_unrelated_funded_job_is_offered_before_new_construction(self):
        self.plan();self.s['sharedFunds']=100;self.act('hq-build',roomId='entry-hall')
        before=deepcopy(h.project_for(self.s));self.assertEqual(grow.view(self.s)['next']['id'],'other-work')
        self.assertEqual(before,h.project_for(self.s))
        self.act('grow-visibility',enabled=False);self.assertEqual(before,h.project_for(self.s))

if __name__=='__main__':unittest.main()
