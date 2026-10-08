from copy import deepcopy
import unittest
import game as g,armoury as a,arms_of_our_own as c
import test_armoury
class EquipmentPlayabilityTests(unittest.TestCase):
 def setUp(self):
  f=test_armoury.ArmouryTests();f.setUp();self.s=f.s
 def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
 def boots(self):return next(i['id'] for i in a.state(self.s)['items'].values() if i['ownerId']=='founder' and i['definitionId']=='field-boots')
 def work(self):return dict(type='gear-start-job',operation='enchant',itemId=self.boots(),enchantmentId='sure-footing',stowBeforeWork=True)
 def test_combined_stow_quote_is_readonly_and_failed_commit_is_atomic(self):
  old=deepcopy(self.s);q=a.quote_action(self.s,self.work());self.assertEqual(old,self.s);self.assertFalse(q['blockers']);self.assertTrue(any('Stow' in x for x in q['changes']));self.assertTrue(q['assignments'])
  self.s['sharedFunds']=0;old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):g.apply_action(self.s,self.work())
  self.assertEqual(old,self.s)
 def test_completion_preparation_and_proof_keep_identity(self):
  key=self.boots();g.apply_action(self.s,self.work());self.assertFalse(a.equipped(self.s,key));self.act('advance');self.act('advance')
  self.assertEqual(a.view(self.s)['recentCompleted'][-1]['itemId'],key)
  q=a.quote_action(self.s,{'type':'gear-ready','itemId':key,'mode':'expedition','enchantmentId':'sure-footing'});self.assertFalse(q['blockers']);g.apply_action(self.s,q['action'])
  self.assertTrue(a.has(self.s,'founder','sure-footing','expedition'));self.act('gear-test',itemId=key,mode='expedition',enchantmentId='sure-footing')
  self.assertEqual(a.state(self.s)['proofs'][-1]['itemId'],key)
 def test_shortfall_quote_honours_reserves_and_exact_market_cost(self):
  self.s['materialInventory']={k:0 for k in g.MATERIALS};self.s['materialReserveTargets']={k:0 for k in g.MATERIALS};self.s['materialReserveTargets']['binding-thread']=2
  before=deepcopy(self.s);q=a.quote_action(self.s,self.work());self.assertEqual(before,self.s)
  self.assertEqual(q['quote']['supplyShortfalls'],{'porous-clay':1,'binding-thread':3});self.assertEqual(q['quote']['supplyCost'],14)
 def test_existing_bench_does_not_hide_personal_calibration_study(self):
  self.s['armsOfOurOwn']={'drillDone':True,'completedOn':None};self.s['founderKnownPrinciples'].remove('field-calibration');self.assertIn('field-calibration',self.s['archivePrinciples'])
  self.assertEqual(c.guidance(self.s)['id'],'study')
 def test_early_field_upgrade_reports_named_gear_and_saves_time(self):
  key=self.boots();g.apply_action(self.s,self.work());self.act('advance');self.act('advance');self.act('gear-rename',itemId=key,name='My road boots')
  self.act('gear-ready',itemId=key,mode='expedition',enchantmentId='sure-footing',replaceConfirmed=True)
  self.s['keepingHearth']={'completedOn':{'day':1}};self.act('arms-start');self.s['armsOfOurOwn']['drillDone']=True;a.state(self.s)['proofs']=[{'effect':'sure-footing'},{'effect':'measured-force'}];a.state(self.s)['commissionDelivered']=True;self.act('start-expedition',siteId=c.SITE);self.act('advance');self.act('choose-expedition-approach',approach='survey')
  choice=c.encounter_view(self.s)['choices']['gear'];self.assertFalse(choice['blockers']);self.assertEqual(choice['timeSaved'],1);self.assertEqual(choice['equipmentUsed'][0]['name'],'My road boots')
  self.act('choose-encounter-method',methodId='gear');self.act('advance');row=self.s['watchRoad']['outcomes'][0]
  self.assertEqual(row['equipmentUsed'][0]['itemId'],key);self.assertEqual(row['scores']['founder']['equipmentBonus'],1);self.assertIn('My road boots',str(self.s['journal']))
 def test_budget_and_repeat_commission_remain_bounded(self):
  total=0
  for definition,effect in [('field-boots','sure-footing'),('field-staff','measured-force')]:
   key=next(i['id'] for i in a.state(self.s)['items'].values() if i['ownerId']=='founder' and i['definitionId']==definition)
   q=a.quote_action(self.s,{'type':'gear-start-job','itemId':key,'operation':'enchant','enchantmentId':effect,'stowBeforeWork':True})['quote'];total+=q['cost']+sum(g.MATERIALS[m]['price'] for m in q['materials'])
  self.assertEqual(total,32)
  for pay in (12,8):
   before=self.s['sharedFunds'];self.act('gear-start-job',operation='commission');self.act('advance');self.act('advance');self.act('gear-deliver-commission');self.assertEqual(self.s['sharedFunds']-before,pay)
if __name__=='__main__':unittest.main()
