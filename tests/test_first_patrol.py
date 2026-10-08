from copy import deepcopy
import unittest,json
import game as g,first_patrol as p,headquarters as h,field_magic as f
class PatrolTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['roadsWeKeep']['completedOn']={'dayNumber':1,'phase':'morning'}
 def act(self,k,**kw):g.apply_action(self.s,dict(type=k,**kw));self.s=g.migrate_state(json.loads(json.dumps(self.s)))
 def start(self):
  self.act('patrol-start');self.act('start-expedition',siteId=p.TRAIL);self.act('advance');self.act('choose-expedition-approach',approach='survey')
 def finish(self):
  for _ in range(20):
   if self.s['expedition']['stage']=='ready-to-return':break
   if self.s['expedition']['stage']=='encounter-choice':self.act('choose-encounter-method',methodId='patient')
   self.act('advance')
  self.act('return-expedition');self.act('advance')
 def test_introduction_reward_receipt_and_single_return(self):
  self.start();self.finish();self.assertIn('introduced-rhess',self.s['summoningContacts']);self.assertEqual(len(self.s['lastExpeditionReport']['logbook']['outcomes']),3)
  with self.assertRaises(g.RuleError):self.act('start-expedition',siteId=p.TRAIL)
 def test_retreat_resume_saved_work(self):
  self.start();self.act('choose-encounter-method',methodId='patient');self.act('advance');self.act('return-expedition');self.act('advance');self.act('start-expedition',siteId=p.TRAIL);self.act('advance');self.act('choose-expedition-approach',approach='survey');self.act('advance');self.assertIn('camp',p.progress(self.s)['completed'])
 def test_malformed_choice_atomic(self):
  self.start();old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('choose-encounter-method',methodId=[])
  self.assertEqual(old,self.s)
 def test_overnight_requires_rest_at_home(self):
  self.s['currentDayPhase']='evening';self.act('assign-founder',assignment='commissions');self.act('advance');self.assertNotIn('founder',self.s['overnightRest'])
  self.act('assign-founder',assignment='rest');self.act('advance');self.assertNotIn('founder',self.s['overnightRest']);self.act('advance');self.act('advance');self.assertEqual(self.s['overnightRest']['founder'],self.s['dayNumber'])
 def test_gates_no_early_tower_or_final_departure(self):
  self.assertTrue(h.blockers(self.s,'watchtower'))
  with self.assertRaises(g.RuleError):self.act('start-expedition',siteId=p.WARD,companionIds=[])
 def test_custom_name_kept(self):
  self.s['people']['mira']['name']='Rhess';self.start();self.finish();self.assertNotIn('rhess',self.s['people'])
 def member(self):
  import test_household_chapters as household
  household.HouseholdChapterTests.member(self,'rhess')
 def test_breath_cost_survives_retreat_and_is_not_recharged(self):
  self.member();self.s['firstPatrol'].update(started=True,drillDone=True,returnedOn=1,resolution='repair');self.s['overnightRest'].update(founder=2,rhess=2);self.s['patrolJourneys'][p.TRAIL]['discoveries']=['survey'];self.s['headquarters']['rooms']['watchtower']='complete'
  self.act('agree-household-role',characterId='rhess',role='fieldwork',enabled=True,willingnessReviewed=True)
  self.act('start-expedition',siteId=p.WARD,companionIds=['rhess']);self.act('advance');self.act('choose-expedition-approach',approach='survey');self.s['patrolJourneys'][p.WARD]['completed']=['trail'];p.resume(self.s)
  self.act('choose-encounter-method',methodId='breath');self.assertEqual(f.vitality(self.s,'rhess'),5);self.act('return-expedition');self.act('advance')
  self.act('start-expedition',siteId=p.WARD,companionIds=['rhess']);self.act('advance');self.act('choose-expedition-approach',approach='survey');self.act('advance');self.assertTrue(p.encounter_view(self.s)['choices']['breath']['blockers']);self.assertEqual(f.vitality(self.s,'rhess'),5)
 def test_drill_pauses_when_someone_works(self):
  self.member();self.s['headquarters']['rooms']['training-yard']='complete'
  for w in ('founder','rhess'):self.act('assign-character',characterId=w,assignment='rest')
  self.act('patrol-drill');self.act('assign-founder',assignment='commissions');self.act('advance');self.assertEqual(p.saved(self.s)['drill']['done'],0)
  self.act('assign-founder',assignment='rest');self.act('advance');self.act('advance');self.assertTrue(p.saved(self.s)['drillDone'])
 def test_keeper_bonus_requires_assignment_and_improvement(self):
  import provisions
  self.member();self.s['roadsWeKeep']['refugeDone']=True;self.s['headquarters']['rooms']['watchtower']='complete';self.s['headquarters']['stock']['specialty:rhess']=1
  before=(self.s['provisions']['stock'],self.s['sharedFunds']);provisions.resolve(self.s,[],{'rhess':'rest'},'morning');self.assertEqual(before,(self.s['provisions']['stock'],self.s['sharedFunds']))
  for _ in range(2):provisions.resolve(self.s,[],{'rhess':'road-patrol'},'morning')
  self.assertEqual((before[0]+6,before[1]+3),(self.s['provisions']['stock'],self.s['sharedFunds']))
 def test_evening_winddown_pauses_paid_work_without_advancing(self):
  self.s['currentDayPhase']='evening';self.s['sharedFunds']=100;self.act('start-research');project=deepcopy(self.s['researchProjects']);f.initialize(self.s)['vitality']['founder']=1
  self.act('evening-rest',choice='tea');self.assertEqual(self.s['researchProjects'],project);self.assertEqual(self.s['currentDayPhase'],'evening')
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('evening-rest',choice='quiet')
  self.assertEqual(self.s,old);self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),4);self.assertEqual(self.s['currentDayPhase'],'morning');self.assertEqual(self.s['researchProjects'],project)
