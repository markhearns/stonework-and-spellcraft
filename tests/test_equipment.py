from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game as g
import equipment
from server import GameStore

class EquipmentTests(unittest.TestCase):
 def setUp(self):self.s=g.new_campaign()
 def act(self,kind,**kw):return g.apply_action(self.s,{'type':kind,'ownerId':'founder',**kw})
 def claim(self,kind='scholars-folio'):
  self.s['craftedArtifacts'][kind]+=1;self.act('claim-working-tool',toolId=kind);return next(reversed(self.s['personalEquipment']))
 def test_real_crafting_cost_work_claim_and_prepare(self):
  g.learn_for_character(self.s,'founder','reference-binding')
  self.s['materialInventory'].update({'porous-clay':2,'binding-thread':2})
  self.act('start-crafting',recipeId='scholars-folio',materials=['porous-clay','binding-thread'])
  self.assertEqual(self.s['materialInventory']['porous-clay'],1)
  for _ in range(3):self.act('advance')
  self.assertEqual(self.s['craftedArtifacts']['scholars-folio'],1)
  before=deepcopy(self.s);self.act('claim-working-tool',toolId='scholars-folio')
  self.assertEqual(self.s['craftedArtifacts']['scholars-folio'],0)
  key=next(iter(self.s['personalEquipment']))
  base=g.work_contribution(self.s,'founder','archive-focus')
  self.act('prepare-working-tool',itemId=key)
  self.assertEqual(g.work_contribution(self.s,'founder','archive-focus'),base+1)
  for k in ['dayNumber','currentDayPhase','sharedFunds','materialInventory']:self.assertEqual(before[k],self.s[k])
  with self.assertRaises(g.RuleError):self.act('claim-working-tool',toolId='scholars-folio')
 def test_one_slot_scope_ownership_transfer_and_away(self):
  folio=self.claim();gauge=self.claim('makers-gauge');self.act('prepare-working-tool',itemId=folio)
  self.assertEqual(equipment.bonus(self.s,'founder','careful-assembly'),[])
  self.act('prepare-working-tool',itemId=gauge);self.assertEqual(equipment.bonus(self.s,'founder','archive-focus'),[])
  self.act('rename-working-tool',itemId=gauge,name='My faithful gauge')
  with self.assertRaises(g.RuleError):self.act('transfer-working-tool',itemId=gauge,recipientId='mira')
  self.act('transfer-working-tool',itemId=gauge,recipientId='mira',ownersAgreed=True)
  self.assertNotIn('founder',self.s['preparedEquipment'])
  with self.assertRaises(g.RuleError):self.act('prepare-working-tool',itemId=gauge)
  self.act('prepare-working-tool',ownerId='mira',itemId=gauge)
  self.assertEqual(self.s['personalEquipment'][gauge]['ownershipHistory'],['founder','mira'])
  self.act('start-expedition')
  with self.assertRaises(g.RuleError):self.act('stow-working-tool',ownerId='mira')
  self.assertEqual(g.work_contribution(self.s,'founder','archive-focus'),0)
 def test_sqlite_retries_and_migration_preserve_ownership(self):
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);s=store.read();s['craftedArtifacts']['scholars-folio']=1
   with store.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(s),))
   p={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':{'type':'claim-working-tool','ownerId':'mira','toolId':'scholars-folio'}}
   saved=store.action(p);self.assertEqual(store.action(p),saved);self.assertEqual(GameStore(d).read(),saved)
   old=deepcopy(saved);old['schemaVersion']=33;g.migrate_state(old)
   self.assertEqual(old['personalEquipment'],saved['personalEquipment'])
   self.assertEqual(old['schemaVersion'],g.CURRENT_SCHEMA_VERSION)
