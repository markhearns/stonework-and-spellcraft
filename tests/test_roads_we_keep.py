from copy import deepcopy
import unittest
import game as g, roads_we_keep as r, provisions as f
class RoadsTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['armsOfOurOwn']={'party':['founder'],'drillDone':True,'drill':None,'allocation':True,'completedOn':{'dayNumber':1,'phase':'morning'},'priority':'utility','memories':[]}
 def act(self,k,**kw):g.apply_action(self.s,dict(type=k,**kw))
 def start(self):
  if not r.saved(self.s)['started']:self.act('roads-start')
  self.act('start-expedition',siteId=r.SITE);self.act('advance');self.act('choose-expedition-approach',approach='survey')
 def finish(self):
  for _ in range(20):
   e=self.s['expedition']
   if e['stage']=='ready-to-return':break
   if e['stage']=='encounter-choice':self.act('choose-encounter-method',methodId='patient')
   self.act('advance')
  self.act('return-expedition');self.act('advance')
 def test_ordinary_route_contact_rewards_once(self):
  self.start();self.finish();self.assertEqual(len(r.progress(self.s)['completed']),5);self.assertIn('introduced-velis',self.s['summoningContacts']);self.assertNotIn('velis',g.household_members(self.s))
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.start()
  self.assertEqual(self.s,before)
 def test_retreat_retains_partial_work(self):
  self.start();self.act('choose-encounter-method',methodId='patient');self.act('advance');self.assertEqual(r.progress(self.s)['pending']['remaining'],1)
  self.act('return-expedition');self.act('advance');self.start();self.act('advance');self.assertIn('tracks',r.progress(self.s)['completed'])
 def test_malformed_choice_atomic(self):
  self.start();before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('choose-encounter-method',methodId=[])
  self.assertEqual(self.s,before)
 def test_custom_identity_not_overwritten(self):
  self.s['people']['mira']['name']='Velis';before=deepcopy(self.s['people']['mira']);self.start();self.finish();self.assertEqual(before,self.s['people']['mira']);self.assertNotIn('velis',self.s['people'])
 def test_food_assignment_via_saved_work_action(self):
  self.act('assign-character',characterId='mira',assignment='forage');self.assertEqual(g.character_assignment(self.s,'mira'),'forage')
 def test_ritual_pause_refund_and_completion(self):
  g.learn_for_character(self.s,'founder','steady-hearth-wards')
  for k in ('silver-ivy','binding-thread'):self.s['materialInventory'][k]=self.s['materialReserveTargets'][k]+3
  before=deepcopy(self.s['materialInventory']);self.act('food-ritual');self.act('assign-founder',assignment='rest');f.resolve(self.s,[],{'founder':'rest'},'morning');self.assertEqual(f.saved(self.s)['ritual']['done'],0)
  self.act('food-cancel');self.assertEqual(before,self.s['materialInventory'])
  self.act('food-ritual');stock=f.saved(self.s)['stock']
  for _ in range(2):f.resolve(self.s,[],{'founder':'food-ritual'},'morning')
  self.assertEqual(f.saved(self.s)['stock'],stock+18);self.assertIsNone(f.saved(self.s)['ritual'])
 def test_prepared_spell_commits_once_and_resumes_without_rebuy(self):
  import test_magic_overhaul as magic
  chapter=deepcopy(self.s['armsOfOurOwn']);m=magic.MagicTests();m.setUp();m.learned('water-walk');self.s=m.s
  self.s['armsOfOurOwn']=chapter
  self.start();r.progress(self.s)['completed']=['tracks'];r.resume(self.s)
  before=deepcopy(self.s['materialInventory']);self.act('choose-encounter-method',methodId='spell')
  for k,n in g.SPELL_FORMS['water-walk']['castingInputs'].items():self.assertEqual(self.s['materialInventory'][k],before[k]-n)
  paid=deepcopy(self.s['materialInventory']);self.act('return-expedition');self.act('advance');self.start();self.act('advance')
  self.assertIn('crossing',r.progress(self.s)['completed']);self.assertEqual(self.s['materialInventory'],paid)
 def test_saved_gathering_arrangement_restores(self):
  self.act('food-assign',characterId='mira',assignment='forage');self.act('save-work-arrangement',name='Pantry day');self.act('assign-character',characterId='mira',assignment='rest');self.act('apply-work-arrangement',name='Pantry day');self.assertEqual(g.character_assignment(self.s,'mira'),'forage')
if __name__=='__main__':unittest.main()
