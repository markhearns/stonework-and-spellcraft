from copy import deepcopy
import unittest
import game as g
import opening_guide as guide
import guidance

class OpeningGuideTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign('fresh')
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def test_read_only_and_initial_room_target(self):
        before=deepcopy(self.s);v=guide.view(self.s)
        self.assertEqual(v['next']['target'],{'view':'research','roomId':'library'})
        self.assertEqual(self.s,before);self.assertEqual(len(v['milestones']),5)
    def test_income_shortfall_and_current_assignment(self):
        self.s['sharedFunds']=3;v=guide.view(self.s)['next']
        self.assertEqual(v['id'],'income');self.assertIn('5 phase(s)',v['detail'])
        self.act(**{'kind':v['action']['type'],'assignment':'commissions'});self.assertTrue(guide.view(self.s)['next']['copyingAssigned'])
        self.advance(5);self.assertEqual(guide.view(self.s)['next']['id'],'hearth')
    def test_real_fresh_path_to_living_wing_and_returned_discovery(self):
        self.act('start-research');self.advance(3)
        self.assertEqual(guide.view(self.s)['next']['id'],'lantern')
        self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'],crafterId='founder');self.advance(2)
        seen=set()
        for _ in range(70):
            n=guide.view(self.s)['next'];seen.add(n['id'])
            if n['id']=='first-expedition':break
            if n['id']=='income':
                self.act('assign-founder',assignment='commissions');self.advance()
            elif n['id'].startswith('facility:'):
                g.apply_action(self.s,n['action']);self.advance()
            elif n['id']=='kettle-materials':self.act('buy-material',materialId=n['target']['materialId'])
            elif n['id']=='kettle':
                if not self.s['craftingProject']:self.act('start-crafting',recipeId='hearth-kettle',materials=['sun-amber','porous-clay'],crafterId='founder')
                self.advance()
            elif n['id']=='install-kettle':g.apply_action(self.s,n['action'])
            elif n['id']=='wing':self.advance()
            else:self.fail(n)
        else:self.fail('Guide failed to reach first expedition')
        self.assertTrue(self.s['livingWingCompletedOn']);self.assertIn('income',seen);self.assertIn('install-kettle',seen)
        self.act('start-expedition',siteId='old-waterworks',carryLantern=True);self.advance()
        self.assertEqual(guide.view(self.s)['next']['id'],'journey')
        self.act('choose-expedition-approach',approach='survey');self.advance();self.act('return-expedition');self.advance()
        self.assertEqual(guide.view(self.s)['next']['id'],'introduction');self.assertTrue(guide.view(self.s)['milestones'][3]['complete'])
        self.act('start-local-visit',encounterId='koharu');self.advance()
        self.assertEqual(guide.view(self.s)['next']['id'],'membership');self.assertFalse(guide.view(self.s)['milestones'][4]['complete'])
    def test_headquarters_preview_tracks_active_and_paused_projects(self):
        self.act('hq-build',roomId='chapel')
        p=next(r for r in guidance.preview(self.s)['projects'] if r['id']=='headquarters')
        self.assertEqual(p['progress'],1);self.assertFalse(p['completes'])
        self.advance();p=next(r for r in guidance.preview(self.s)['projects'] if r['id']=='headquarters');self.assertTrue(p['completes'])
        self.act('assign-founder',assignment='rest');p=next(r for r in guidance.preview(self.s)['projects'] if r['id']=='headquarters');self.assertEqual(p['progress'],0)
    def test_public_trip_guidance_does_not_send_player_to_core_expeditions(self):
        self.s['publicWorkshop']['fieldTrip']={'stage':'outbound','participants':['founder']}
        self.s['founderAssignment']='public-expedition'
        self.assertEqual(guide.view(self.s)['next']['target']['view'],'publicWorkshop')

if __name__=='__main__':unittest.main()
