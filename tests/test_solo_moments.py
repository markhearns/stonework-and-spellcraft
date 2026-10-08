import copy
import json
import unittest
import game as g
import solo_life
import phase_tasks

class SoloMomentTests(unittest.TestCase):
    def test_locked_away_and_invalid_choices_do_not_mutate(self):
        s=g.new_campaign('fresh')
        for key,choice in [('first-light','home'),('missing','home')]:
            before=copy.deepcopy(s)
            with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'remember-solo-moment','momentId':key,'choiceId':choice})
            self.assertEqual(s,before)
        s['craftedArtifacts']['warming-lantern']=1
        before=copy.deepcopy(s)
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'remember-solo-moment','momentId':'first-light','choiceId':'missing'})
        self.assertEqual(s,before)
        g.apply_action(s,{'type':'start-expedition','siteId':'old-waterworks'})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'remember-solo-moment','momentId':'first-light','choiceId':'home'})

    def test_real_progress_scene_is_optional_and_persists_without_rewards(self):
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'start-research'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        task=next(t for t in phase_tasks.build(s)['tasks'] if t['id']=='first-lantern')
        g.apply_action(s,task['action'])
        for _ in range(2):g.apply_action(s,{'type':'advance'})
        self.assertIn('moment:first-light',[t['id'] for t in phase_tasks.build(s)['tasks']])
        before=copy.deepcopy(s)
        g.apply_action(s,{'type':'remember-solo-moment','momentId':'first-light','choiceId':'home'})
        self.assertEqual(s['dayNumber'],before['dayNumber']);self.assertEqual(s['currentDayPhase'],before['currentDayPhase'])
        for key in ['sharedFunds','materialInventory','characterDevelopment','craftedArtifacts','founderAssignment']:
            self.assertEqual(s[key],before[key])
        s=g.migrate_state(json.loads(json.dumps(s)))
        self.assertEqual(s['soloLife']['moments']['first-light']['choiceId'],'home')
        self.assertNotIn('moment:first-light',[t['id'] for t in phase_tasks.build(s)['tasks']])
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'remember-solo-moment','momentId':'first-light','choiceId':'craft'})

    def test_all_gates_old_save_and_no_expiry(self):
        s=g.new_campaign('fresh')
        self.assertNotIn('moments',s['soloLife'])
        self.assertFalse(any(r['available'] for r in solo_life.moments(s)))
        s['restorationStatus']='complete';s['waterworksDiscoveries']=['survey'];s['neighbourRequestProgress']['brook-lamps']['status']='delivered'
        for key in ['green-room','field-notes','neighbour-reply']:
            row=next(r for r in solo_life.moments(s) if r['id']==key)
            self.assertTrue(row['available'])
            g.apply_action(s,{'type':'remember-solo-moment','momentId':key,'choiceId':row['choices'][0]['id']})
        s['craftedArtifacts']['warming-lantern']=1
        for _ in range(5):g.apply_action(s,{'type':'advance'})
        self.assertTrue(next(r for r in solo_life.moments(s) if r['id']=='first-light')['available'])
        demo=g.new_campaign('demo')
        self.assertFalse(any(r['available'] for r in solo_life.moments(demo)))

    def test_new_moments_follow_real_research_and_time(self):
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'start-research'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        ready={r['id'] for r in solo_life.moments(s) if r['available']}
        self.assertTrue({'hearth-understood','second-morning'}<=ready)
        self.assertNotIn('own-archive',ready);self.assertNotIn('shared-roof',ready)
        g.apply_action(s,{'type':'focus-research','researchId':'archive-foundations','leaderId':'founder'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        for key in ('hearth-understood','second-morning','own-archive'):
            row=next(r for r in solo_life.moments(s) if r['id']==key)
            self.assertTrue(row['available'])
            before=copy.deepcopy(s)
            g.apply_action(s,{'type':'remember-solo-moment','momentId':key,'choiceId':row['choices'][0]['id']})
            for field in s:
                if field not in ('soloLife','journal'):self.assertEqual(s[field],before[field],field)
        s=g.migrate_state(json.loads(json.dumps(s)))
        self.assertEqual(len(s['soloLife']['moments']),3)

    def test_shared_roof_waits_for_membership_not_a_visit(self):
        import summoning
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'start-local-visit','encounterId':'maren'})
        g.apply_action(s,{'type':'advance'})
        contact=next(k for k,c in s['summoningContacts'].items() if c['personId']=='maren')
        for topic in summoning.candidate_catalogue(s)['maren']['topics']:
            g.apply_action(s,{'type':'summoning-talk','contactId':contact,'topic':topic})
        g.apply_action(s,{'type':'summoning-invite','contactId':contact,'roomId':'bedchamber'})
        g.apply_action(s,{'type':'advance'})
        self.assertFalse(next(r for r in solo_life.moments(s) if r['id']=='shared-roof')['available'])
        g.apply_action(s,{'type':'summoning-ask-stay','contactId':contact})
        g.apply_action(s,{'type':'summoning-household-decision','contactId':contact,'decision':'invite-to-stay'})
        self.assertTrue(next(r for r in solo_life.moments(s) if r['id']=='shared-roof')['available'])
        before=copy.deepcopy(s)
        g.apply_action(s,{'type':'remember-solo-moment','momentId':'shared-roof','choiceId':'space'})
        for key in s:
            if key not in ('soloLife','journal'):self.assertEqual(s[key],before[key],key)
        self.assertFalse(s['testing']['used'])
