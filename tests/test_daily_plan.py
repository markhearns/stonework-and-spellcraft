from copy import deepcopy
import json,unittest,tempfile,uuid
import game as g,daily_plan,guidance,household_rest
from server import GameStore

class DailyPlanTests(unittest.TestCase):
 def setUp(self):self.s=g.new_campaign('fresh')
 def act(self,kind,**kw):return g.apply_action(self.s,{'type':kind,**kw})
 def reject(self,kind,**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(self.s,before)
 def target(self,extra=5):return self.s['sharedFunds']+extra
 def test_goal_uses_ordinary_income_stops_and_does_not_spend(self):
  target=self.target();funds=self.s['sharedFunds'];rate=g.copying_income(self.s)
  self.act('plan-income',targetCrowns=target,purpose='a workshop')
  self.assertEqual(self.s['sharedFunds'],funds)
  for _ in range(3):
   before=deepcopy(self.s);preview=guidance.preview(self.s);self.assertEqual(self.s,before)
   self.act('advance')
   self.assertEqual(self.s['sharedFunds']-before['sharedFunds'],next(r['change'] for r in preview['resources'] if r['name']=='Shared crowns'))
   if daily_plan.view(self.s)['status']=='complete':break
  self.assertEqual(self.s['founderAssignment'],'rest');self.assertGreaterEqual(self.s['sharedFunds'],target)
  self.assertLess(self.s['sharedFunds'],target+rate);once=deepcopy(daily_plan.saved(self.s));funds=self.s['sharedFunds']
  self.act('advance');self.assertEqual(daily_plan.saved(self.s),once);self.assertEqual(self.s['sharedFunds'],funds)
 def test_pause_resume_reload_and_clear_never_spend(self):
  target=self.target(30);self.act('plan-income',targetCrowns=target,purpose='the garden')
  self.act('assign-founder',assignment='rest');self.s=g.migrate_state(json.loads(json.dumps(self.s)))
  self.assertEqual(daily_plan.view(self.s)['status'],'paused');funds=self.s['sharedFunds']
  self.act('plan-income',targetCrowns=target,purpose='the garden');self.assertEqual(self.s['sharedFunds'],funds)
  self.act('clear-income-plan');self.assertIsNone(daily_plan.view(self.s));self.assertEqual(self.s['founderAssignment'],'commissions')
 def test_invalid_goal_is_atomic(self):
  for value in (True,0,-1,1.5,10001,'30',None):self.reject('plan-income',targetCrowns=value,purpose='a room')
  self.reject('plan-income',targetCrowns=self.target(),purpose='')
  self.reject('plan-income',targetCrowns=self.s['sharedFunds'],purpose='already funded')
 def test_other_income_completion_does_not_replace_different_assignment(self):
  target=self.target();self.act('plan-income',targetCrowns=target,purpose='a room');self.act('assign-founder',assignment='rest')
  self.s['sharedFunds']=target;self.act('advance');self.assertEqual(self.s['founderAssignment'],'rest')
  self.assertEqual(daily_plan.view(self.s)['status'],'complete')
 def test_day_end_costs_are_included_before_target_is_checked(self):
  self.s['currentDayPhase']='evening';self.s['provisions']['stock']=0
  self.act('food-policy',enabled=True,targetDays=7,budget=2,floor=0)
  target=self.target(g.copying_income(self.s));self.act('plan-income',targetCrowns=target,purpose='the next room');self.act('advance')
  self.assertLess(self.s['sharedFunds'],target);self.assertIsNone(daily_plan.saved(self.s)['completedOn'])
 def test_group_winddown_only_changes_named_people_and_keeps_paid_work(self):
  self.s=g.new_campaign();self.s['currentDayPhase']='evening';self.act('start-research')
  paid=deepcopy(self.s['researchProjects']);day=self.s['dayNumber']
  self.act('evening-rest',choice='tea',participants=['founder','mira'])
  self.assertEqual(self.s['founderAssignment'],'rest');self.assertEqual(self.s['residentAssignment'],'rest')
  self.assertEqual(self.s['researchProjects'],paid);self.assertEqual(self.s['currentDayPhase'],'evening')
  self.act('advance');self.assertEqual(self.s['overnightRest']['founder'],day+1);self.assertEqual(self.s['overnightRest']['mira'],day+1)
  self.assertEqual(self.s['currentDayPhase'],'morning')
 def test_group_winddown_invalid_or_away_person_changes_nobody(self):
  self.s=g.new_campaign();self.s['currentDayPhase']='evening'
  for people in ([],['mira'],['founder','unknown'],['founder','founder'],['founder',{}]):self.reject('evening-rest',choice='quiet',participants=people)
  self.act('start-expedition',siteId='old-waterworks');self.reject('evening-rest',choice='quiet',participants=['founder','mira'])
 def test_save_retry_is_idempotent(self):
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory,start_type='fresh');s=store.read()
   payload={'requestId':str(uuid.uuid4()),'expectedRevision':s['revision'],'action':{'type':'plan-income','targetCrowns':s['sharedFunds']+10,'purpose':'the garden'}}
   first=store.action(payload);self.assertEqual(first,store.action(payload))
   self.assertEqual(GameStore(directory).read()['dailyPlan'],first['dailyPlan'])

 def test_solo_winddown_does_not_change_other_residents(self):
  self.s=g.new_campaign();self.s['currentDayPhase']='evening'
  assignment=self.s['residentAssignment']
  self.act('evening-rest',choice='reading')
  self.assertEqual(self.s['residentAssignment'],assignment)
  self.assertEqual(self.s['founderAssignment'],'rest')

 def test_public_view_reuses_one_read_only_advance_forecast(self):
  from unittest.mock import patch
  self.act('start-research');before=deepcopy(self.s)
  with patch('guidance.preview',wraps=guidance.preview) as spy:
   view=g.public_state(self.s)
   self.assertEqual(spy.call_count,1)
  self.assertEqual(self.s,before)
  self.assertEqual(view['advancePreview'],guidance.preview(self.s))
  self.assertTrue(next(p for p in view['progressionView']['projects'] if p['id']=='hearth')['working'])
