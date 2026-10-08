import unittest
from copy import deepcopy
import game as g
import guidance

class GuidanceTests(unittest.TestCase):
    def test_preview_is_nonmutating_and_matches_completed_work(self):
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'start-research'})
        g.apply_action(s,{'type':'advance'});g.apply_action(s,{'type':'advance'})
        original=deepcopy(s);v=guidance.preview(s)
        self.assertEqual(s,original)
        self.assertEqual(v['completions'][0]['id'],'hearth')
        self.assertEqual(v['projects'][0]['after'],3)
        g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['researchStatus'],'complete')
        self.assertEqual(s['soloLife']['lastCompletions'][0]['id'],'hearth')
    def test_paused_and_blocked_previews(self):
        s=g.new_campaign('fresh');g.apply_action(s,{'type':'start-research'})
        g.apply_action(s,{'type':'assign-founder','assignment':'rest'})
        v=guidance.preview(s)
        self.assertEqual(v['projects'][0]['progress'],0)
        self.assertFalse(v['completions'])
        g.apply_action(s,{'type':'start-expedition','siteId':'old-waterworks'})
        g.apply_action(s,{'type':'advance'})
        self.assertIn('Choose an expedition approach',guidance.preview(s)['blocked'])
    def test_goals_persist_without_spending_or_advancing(self):
        s=g.new_campaign('fresh');old=deepcopy(s)
        for key in ['welcome-fenna','conservatory','living-wing']:
            g.apply_action(s,{'type':'pin-goal','goalId':key,'pinned':True})
        with self.assertRaisesRegex(g.RuleError,'three pinned'):g.apply_action(s,{'type':'pin-goal','goalId':'first-lantern','pinned':True})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'pin-goal','goalId':'unknown','pinned':True})
        g.apply_action(s,{'type':'pin-goal','goalId':'welcome-fenna','pinned':True})
        g.migrate_state(s)
        self.assertEqual(s['sharedFunds'],old['sharedFunds'])
        self.assertEqual(s['currentDayPhase'],old['currentDayPhase'])
        self.assertEqual(len(s['soloLife']['pinnedGoals']),3)
        g.apply_action(s,{'type':'pin-goal','goalId':'conservatory','pinned':False})
        self.assertFalse(next(r for r in guidance.goals(s) if r['id']=='conservatory')['pinned'])
    def test_fenna_chain_and_delivered_supplies(self):
        s=g.new_campaign('fresh');get=lambda:next(r for r in guidance.goals(s) if r['id']=='welcome-fenna')
        self.assertEqual(get()['nextStep']['id'],'hearth')
        s['researchStatus']='complete'
        self.assertEqual(get()['nextStep']['id'],'spare-lantern')
        s['craftedArtifacts']['warming-lantern']=1;s['lanternDisplayed']=True
        self.assertEqual(get()['nextStep']['id'],'spare-lantern')
        s['lanternDisplayed']=False;s['materialInventory']['binding-thread']=1
        self.assertEqual(get()['nextStep']['id'],'delivery-thread')
        s['neighbourRequestProgress']['brook-lamps']['status']='delivered'
        s['craftedArtifacts']['warming-lantern']=0
        self.assertEqual(get()['nextStep']['id'],'nursery')
        self.assertEqual(get()['nextStep']['target']['siteId'],'fern-nursery')
    def test_preview_counts_copying_income_without_copying(self):
        s=g.new_campaign('fresh');g.apply_action(s,{'type':'assign-founder','assignment':'commissions'})
        before=deepcopy(s);v=guidance.preview(s)
        self.assertEqual(s,before)
        expected=next(r['change'] for r in v['resources'] if r['name']=='Shared crowns')
        g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['sharedFunds']-before['sharedFunds'],expected)
