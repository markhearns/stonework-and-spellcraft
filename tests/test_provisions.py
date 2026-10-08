"""Food balance, time boundaries, cancellation and save safety."""
from copy import deepcopy
import unittest
import game as g, provisions as f
class ProvisionsTests(unittest.TestCase):
 def setUp(self): self.s=g.new_campaign()
 def act(self,k,**kw):g.apply_action(self.s,dict(type=k,**kw))
 def test_only_morning_consumes_and_views_do_not(self):
  self.s['currentDayPhase']='morning';before=deepcopy(self.s);g.public_state(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
  stock=f.saved(self.s)['stock'];self.act('advance');self.assertEqual(f.saved(self.s)['stock'],stock)
  self.act('advance');self.assertEqual(f.saved(self.s)['stock'],stock)
  self.act('advance');self.assertEqual(f.saved(self.s)['stock'],stock-f.need(self.s))
 def test_gathering_is_primary_and_preference_improves_yield(self):
  self.act('food-assign',characterId='mira',assignment='forage');stock=f.saved(self.s)['stock'];self.act('advance')
  self.assertEqual(f.saved(self.s)['stock']-stock,f.yield_for(self.s,'mira','forage'));self.assertEqual(f.yield_for(self.s,'mira','forage'),f.yield_for(self.s,'mira','hunt')+1)
 def test_purchase_and_policy_do_not_advance(self):
  before=self.s['currentDayPhase'];stock=f.saved(self.s)['stock'];money=self.s['sharedFunds'];self.act('food-buy',bundles=5)
  self.assertEqual(f.saved(self.s)['stock'],stock+30);self.assertEqual(self.s['sharedFunds'],money-5);self.assertEqual(self.s['currentDayPhase'],before)
 def test_auto_respects_budget_and_floor(self):
  f.saved(self.s)['stock']=0;self.s['sharedFunds']=22;self.act('food-policy',enabled=True,targetDays=7,budget=1,floor=20)
  f.resolve(self.s,[],{},'evening');self.assertEqual(self.s['sharedFunds'],21);self.assertEqual(f.saved(self.s)['stock'],6-f.need(self.s))
  f.saved(self.s)['stock']=0;f.resolve(self.s,[],{},'evening');self.assertEqual(self.s['sharedFunds'],20)
  f.saved(self.s)['stock']=0;f.resolve(self.s,[],{},'evening');self.assertEqual(self.s['sharedFunds'],20)
 def test_shortage_requires_three_days_and_clears(self):
  f.saved(self.s)['stock']=0
  for _ in range(2):f.resolve(self.s,[],{},'evening');self.assertFalse(f.short(self.s))
  f.resolve(self.s,[],{},'evening');self.assertTrue(f.short(self.s));self.act('food-buy');f.resolve(self.s,[],{},'evening');self.assertFalse(f.short(self.s))
 def test_free_delivery_capped_at_target(self):
  self.s['roadsWeKeep']['agreement']='food';r=f.saved(self.s);r['stock']=f.need(self.s)*r['targetDays'];funds=self.s['sharedFunds'];f.resolve(self.s,[],{},'evening')
  self.assertEqual(r['stock'],f.need(self.s)*(r['targetDays']-1));self.assertEqual(funds,self.s['sharedFunds'])
 def test_rejections_are_atomic(self):
  for a in [dict(type='food-buy',bundles=True),dict(type='food-policy',enabled=True,targetDays=0,budget=1,floor=0),dict(type='food-ritual'),dict(type='food-order',materials={'silver-ivy':1},quotedCost=0)]:
   before=deepcopy(self.s)
   with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
   self.assertEqual(before,self.s)
 def test_migration_buffer_once(self):
  old=deepcopy(self.s);old['schemaVersion']=60;old.pop('provisions');old.pop('roadsWeKeep');old.pop('hollowRoad');new=g.migrate_state(old)
  self.assertGreaterEqual(f.saved(new)['stock'],7*f.need(new));f.saved(new)['stock']=1;again=g.migrate_state(deepcopy(new));self.assertEqual(again,new)
 def test_orders_pay_once_deliver_once_cancel_exactly(self):
  self.s['headquarters']['rooms']['supply-office']='complete'
  q=f.quote(self.s,{'silver-ivy':2});funds=self.s['sharedFunds'];stock=self.s['materialInventory']['silver-ivy'];self.act('food-order',materials=q['materials'],quotedCost=q['cost']);self.assertEqual(self.s['sharedFunds'],funds-q['cost'])
  f.resolve(self.s,[],{},'morning');self.assertEqual(self.s['materialInventory']['silver-ivy'],stock);f.resolve(self.s,[],{},'afternoon');self.assertEqual(self.s['materialInventory']['silver-ivy'],stock+2);f.resolve(self.s,[],{},'morning');self.assertEqual(self.s['materialInventory']['silver-ivy'],stock+2)
  self.act('food-order',materials=q['materials'],quotedCost=q['cost']);self.act('food-cancel-order',orderId=2);self.assertEqual(self.s['sharedFunds'],funds-q['cost'])
if __name__=='__main__':unittest.main()
