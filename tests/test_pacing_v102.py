"""Regression checks for actionable guidance, committed work and real rest gates."""
from copy import deepcopy
import json
import unittest
import game as g
import first_hearth as hearth
import campaign_guidance as guide
import commissions
import guidance
import progression
import phase_tasks
import field_patrols
import first_patrol
import arms_of_our_own as arms
import armoury
import headquarters
import test_household_chapters as household


class PacingTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign('fresh')
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def follow(self,row):
        self.assertTrue(row['action'],row)
        self.assertFalse(row.get('blockers'),row)
        g.apply_action(self.s,row['action'])
        self.s=g.migrate_state(json.loads(json.dumps(self.s)))
    def funding(self,extra=30):
        before=deepcopy(self.s)
        row=hearth.income(self.s,self.s['sharedFunds']+extra,'the next room',{'view':'headquarters'})
        self.assertEqual(before,self.s)
        return row
    def member(self,who):household.HouseholdChapterTests.member(self,who)

    def test_funding_quotes_real_payment_and_keeps_copying_available(self):
        row=self.funding();self.assertEqual(row['action']['type'],'commission-start')
        self.assertEqual(row['incomeOptions'][0]['action']['type'],'plan-income')
        funds=self.s['sharedFunds'];self.follow(row)
        job=commissions.saved(self.s)['job'];self.assertIn(str(job['reward']['crowns']),row['detail'])
        self.assertEqual(funds,self.s['sharedFunds'])
        for _ in range(job['phases']):self.follow(self.funding())
        self.assertEqual(self.s['sharedFunds'],funds+job['reward']['crowns'])
        self.assertIsNone(commissions.saved(self.s)['job'])
        self.assertEqual(self.s['founderAssignment'],'rest')

    def test_paused_commission_resumes_quoted_work_before_another_job(self):
        self.follow(self.funding());self.act('advance');self.act('assign-founder',assignment='rest')
        paid=deepcopy(commissions.saved(self.s)['job']);row=self.funding()
        self.assertEqual(row['action']['type'],'commission-resume');self.follow(row)
        self.assertEqual(paid,commissions.saved(self.s)['job'])
        self.follow(self.funding());self.assertIsNone(commissions.saved(self.s)['job'])

    def test_small_shortfall_prefers_one_phase_copying(self):
        row=self.funding(1);self.assertEqual(row['action']['type'],'plan-income')
        self.assertTrue(row['incomeOptions'])
        self.follow(row);self.act('advance');self.assertEqual(self.s['founderAssignment'],'rest')

    def test_resident_commission_is_not_reassigned_by_founder_funding(self):
        self.s=g.new_campaign()
        self.act('commission-start',commissionId='translate',workerId='mira',payment='crowns',agreed=True)
        job=deepcopy(commissions.saved(self.s)['job']);row=self.funding()
        self.assertEqual(row['action']['type'],'plan-income');self.follow(row)
        self.assertEqual(job,commissions.saved(self.s)['job'])
        self.assertEqual(g.character_assignment(self.s,'mira'),'external-commission')

    def test_equipment_resume_preserves_paid_progress_and_costs(self):
        self.s['headquarters']['rooms']['enchanting-room']='complete'
        for principle in ('water-guidance','field-calibration'):g.learn_for_character(self.s,'founder',principle)
        self.s['materialInventory'].update({'porous-clay':2,'binding-thread':2})
        key=armoury.make(self.s,'field-boots','founder')['id']
        self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId='sure-footing')
        self.act('advance');self.act('assign-founder',assignment='rest')
        paid=deepcopy(armoury.state(self.s)['jobs']['founder']);funds=self.s['sharedFunds']
        self.act('resume-project',projectId='equipment:founder')
        self.assertEqual(paid,armoury.state(self.s)['jobs']['founder']);self.assertEqual(funds,self.s['sharedFunds'])
        self.act('advance');self.assertNotIn('founder',armoury.state(self.s)['jobs'])
        self.assertIn('sure-footing',armoury.state(self.s)['items'][key]['enchantments'])

    def test_calibration_guide_names_and_finishes_research_prerequisite(self):
        self.act('start-research')
        for _ in range(3):self.act('advance')
        g.learn_for_character(self.s,'founder','water-guidance');self.s['waterworksDiscoveries'].append('survey')
        row=guide.principle_step(self.s,'field-calibration')
        self.assertEqual(row['action']['researchId'],'archive-foundations')
        for _ in range(30):
            if 'field-calibration' in g.character_principles(self.s,'founder'):break
            before=deepcopy(self.s);row=guide.checked(self.s,guide.principle_step(self.s,'field-calibration'))
            self.assertEqual(before,self.s);self.follow(row)
        self.assertIn('field-calibration',g.character_principles(self.s,'founder'))

    def test_night_guidance_names_actual_returners_and_does_not_rest_others(self):
        self.s=g.new_campaign();self.act('assign-founder',assignment='commissions')
        self.act('commission-start',commissionId='translate',workerId='mira',payment='crowns',agreed=True)
        self.s['currentDayPhase']='evening'
        row=guide.night_step(self.s,['mira'],1,'firstRealTest')
        self.assertIn('Mira',row['title']);self.follow(row)
        self.assertEqual(self.s['founderAssignment'],'commissions')
        self.follow(guide.night_step(self.s,['mira'],1,'firstRealTest'))
        self.assertIsNone(guide.night_step(self.s,['mira'],1,'firstRealTest'))
        self.assertNotIn('founder',self.s['overnightRest'])

    def test_already_used_winddown_can_recover_changed_assignment(self):
        self.s['currentDayPhase']='evening';self.act('evening-rest',choice='quiet')
        self.act('assign-founder',assignment='commissions')
        row=guide.night_step(self.s,['founder'],1,'firstPatrol')
        self.assertEqual(row['action']['type'],'assign-character');self.follow(row)
        self.follow(guide.night_step(self.s,['founder'],1,'firstPatrol'))
        self.assertIsNone(guide.night_step(self.s,['founder'],1,'firstPatrol'))

    def test_expedition_choice_never_suggests_advance_to_resolve_it(self):
        self.act('start-expedition',siteId='old-waterworks');self.act('advance')
        row=guide.travel_step(self.s);self.assertEqual(row['id'],'field-choice');self.assertIsNone(row['action'])
        self.assertTrue(guidance.preview(self.s)['waitingChoices'])

    def test_patrol_site_and_battle_choices_wait_while_household_works(self):
        self.s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'}
        self.member('rhess');self.act('agree-household-role',characterId='rhess',role='fieldwork',enabled=True,willingnessReviewed=True)
        self.act('assign-founder',assignment='commissions')
        self.act('watch-depart',participants=['rhess'],objectiveId='escort');self.act('advance')
        for stage in ('site-decision','decision'):
            # Both waiting stages deliberately resolve household work only.
            run=field_patrols.saved(self.s)['active'];run['stage']=stage
            before=deepcopy(self.s);preview=guidance.preview(self.s);self.assertEqual(before,self.s)
            self.assertTrue(preview['waitingChoices']);self.assertIsNone(preview['blocked'])
            task=next(x for x in phase_tasks.build(self.s)['tasks'] if x['id']=='field-patrol')
            self.assertEqual(task['group'],'choice');self.assertIsNone(guide.travel_step(self.s)['action'])
            funds=self.s['sharedFunds'];self.act('advance')
            self.assertGreater(self.s['sharedFunds'],funds);self.assertEqual(before['fieldPatrols']['active'],field_patrols.saved(self.s)['active'])

    def test_shared_drill_guidance_uses_the_same_assignment_blockers(self):
        self.s['roadsWeKeep']['completedOn']={'dayNumber':1,'phase':'morning'}
        self.member('rhess');self.s['headquarters']['rooms']['training-yard']='complete'
        self.act('patrol-start');first_patrol.progress(self.s,first_patrol.TRAIL)['discoveries']=['survey']
        first_patrol.saved(self.s)['returnedOn']=1
        self.act('assign-founder',assignment='commissions')
        self.assertTrue(first_patrol.view(self.s)['drillBlockers'])
        for _ in range(6):
            if first_patrol.saved(self.s)['drillDone']:break
            row=first_patrol.view(self.s)['next'];self.follow(row)
        self.assertTrue(first_patrol.saved(self.s)['drillDone'])

    def test_chapter_five_shows_committed_drill_and_equipment_work(self):
        self.s['keepingHearth']={'completedOn':{'dayNumber':1,'phase':'morning'}}
        self.s['headquarters']['rooms']['training-yard']='complete'
        self.act('arms-start');self.act('assign-founder',assignment='rest');self.act('arms-drill')
        before=deepcopy(self.s);row=arms.view(self.s)['next'];self.assertEqual(before,self.s)
        self.assertEqual(row['action']['type'],'advance');self.follow(row)
        self.assertTrue(arms.saved(self.s)['drillDone'])


if __name__=='__main__':unittest.main()
