import unittest,json
from copy import deepcopy
import game as g
import armoury as a
import arms_of_our_own as chapter
import headquarters as h

class ArmouryTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();s=self.s
  s['sharedFunds']=400;s['headquarters']['rooms'].update({k:'complete' for k in h.ROOMS})
  s['materialInventory'].update({k:30 for k in g.MATERIALS})
  for p in ('water-guidance','field-calibration','clear-instruction','reference-binding','steady-hearth-wards'):g.learn_for_character(s,'founder',p)
  self.act('gear-review')
 def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
 def item(self,definition,owner='founder'):
  it=a.make(self.s,definition,owner);return it['id']
 def equip(self,key,**kw):self.act('gear-equip',itemId=key,replaceConfirmed=True,**kw)
 def enchant(self,key,e):
  self.act('gear-stow',itemId=key);self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId=e)
  for _ in range(2):self.act('advance')
 def test_starters_once_and_usable(self):
  before=deepcopy(a.state(self.s));self.act('gear-review');self.assertEqual(before['items'],a.state(self.s)['items']);self.assertTrue(chapter.loadout_ready(self.s,'founder'))
 def test_dress_atomic_displacement_and_rejection(self):
  dress=self.item('work-dress');old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('gear-equip',itemId=dress)
  self.assertEqual(old,self.s);self.equip(dress);l=a.loadout(self.s,'founder');self.assertEqual(l['slots']['shirt'],dress);self.assertEqual(l['slots']['pants'],dress)
  trousers=self.item('work-trousers');self.equip(trousers);l=a.loadout(self.s,'founder');self.assertNotIn('shirt',l['slots']);self.assertEqual(l['slots']['pants'],trousers)
 def test_two_hands_one_effect_and_channel_limit(self):
  weapon=self.item('steel-kanabo');self.enchant(weapon,'measured-force');self.equip(weapon);self.act('gear-activate',itemId=weapon,enchantments=['measured-force']);self.assertEqual(len(a.effects(self.s,'founder')),1)
  self.assertEqual(a.loadout(self.s,'founder')['slots']['hand2'],weapon)
  for n in range(4):
   key=self.item(['plain-ring','plain-pendant','cloth-cap','field-boots'][n]);it=a.state(self.s)['items'][key];it['enchantments']['weather-seal']={'id':'weather-seal','rank':1};self.equip(key)
   if n<3:self.act('gear-activate',itemId=key,enchantments=['weather-seal'])
   else:
    old=deepcopy(self.s)
    with self.assertRaises(g.RuleError):self.act('gear-activate',itemId=key,enchantments=['weather-seal'])
    self.assertEqual(old,self.s)
 def test_invalid_hand_slot_and_partial_multislot_rejected(self):
  key=self.item('steel-sword')
  with self.assertRaises(g.RuleError):self.act('gear-save-loadout',loadout={'slots':{'head':key},'active':{}})
  key=self.item('work-dress')
  with self.assertRaises(g.RuleError):self.act('gear-save-loadout',loadout={'slots':{'shirt':key},'active':{}})
 def test_exact_cancel_refund_and_no_double_refund(self):
  key=self.item('steel-sword');before=(self.s['sharedFunds'],deepcopy(self.s['materialInventory']))
  self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId='measured-force');self.act('advance');self.act('gear-cancel-job')
  self.assertEqual(before,(self.s['sharedFunds'],self.s['materialInventory']))
  with self.assertRaises(g.RuleError):self.act('gear-cancel-job')
 def test_reserves_personal_knowledge_and_paused_jobs(self):
  key=self.item('field-boots');self.s['materialReserveTargets'].update(self.s['materialInventory']);old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId='sure-footing')
  self.assertEqual(old,self.s);self.s['materialReserveTargets']={k:0 for k in g.MATERIALS};self.s['founderKnownPrinciples'].remove('water-guidance')
  with self.assertRaises(g.RuleError):self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId='sure-footing')
  g.learn_for_character(self.s,'founder','water-guidance');self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId='sure-footing');self.act('assign-founder',assignment='rest');self.act('advance');self.assertEqual(a.state(self.s)['jobs']['founder']['done'],0)
  self.act('gear-resume-job');self.act('advance');self.assertEqual(a.state(self.s)['jobs']['founder']['done'],1)
 def test_pattern_consumed_once_and_returned_on_cancel(self):
  key=self.item('steel-sword');target=self.item('steel-kanabo');self.enchant(key,'measured-force');self.act('gear-start-job',operation='extract',itemId=key,enchantmentId='measured-force');self.act('advance')
  pattern=next(iter(a.state(self.s)['patterns']));self.act('gear-start-job',operation='install-pattern',itemId=target,patternId=pattern)
  self.assertNotIn(pattern,a.state(self.s)['patterns']);self.act('gear-cancel-job');self.assertIn(pattern,a.state(self.s)['patterns'])
  self.act('gear-start-job',operation='install-pattern',itemId=target,patternId=pattern);self.act('advance');self.assertFalse(a.state(self.s)['patterns']);self.assertIn('measured-force',a.state(self.s)['items'][target]['enchantments']);self.assertNotIn('measured-force',a.state(self.s)['items'][key]['enchantments'])
 def test_commission_no_free_boots_and_one_payment(self):
  count=len(a.state(self.s)['items']);funds=self.s['sharedFunds'];self.act('gear-start-job',operation='commission');self.act('advance');self.act('advance');self.assertEqual(len(a.state(self.s)['items']),count);self.assertEqual(self.s['sharedFunds'],funds)
  self.act('gear-deliver-commission');self.assertEqual(self.s['sharedFunds'],funds+12)
  with self.assertRaises(g.RuleError):self.act('gear-deliver-commission')
 def test_transfer_equipped_rejected_and_loadout_missing_reported(self):
  key=self.item('steel-sword');self.equip(key);self.act('gear-save-loadout',mode='expedition')
  with self.assertRaises(g.RuleError):self.act('gear-transfer',itemId=key,recipientId='mira',agreed=True)
  self.act('gear-stow',itemId=key);self.act('gear-transfer',itemId=key,recipientId='mira',agreed=True);self.assertEqual(a.state(self.s)['items'][key]['ownerId'],'mira')
  self.assertNotIn(key,a.loadout(self.s,'founder','expedition')['slots'].values())
 def test_preview_is_read_only(self):
  key=self.item('work-dress');before=deepcopy(self.s);q=a.quote_action(self.s,{'type':'gear-equip','itemId':key});self.assertTrue(q['changes']);self.assertEqual(before,self.s)
 def test_migration_idempotent_keeps_legacy_tool_focus_ward(self):
  s=g.new_campaign();s.pop('armoury');s.pop('watchRoad');s['schemaVersion']=59
  s['personalEquipment']['old']={'kind':'scholars-folio','ownerId':'founder','name':'My notes','ownershipHistory':['founder'],'inscription':'Cross-reference inscription'};s['preparedEquipment']['founder']='old'
  s['signatureFocuses']['founder'].update(capacity=2,inscriptions=['scholarly-thread','copying-line'],householdLoadout=['scholarly-thread','copying-line'])
  s['headquarters']['stock'].update({'blade':2,'armour':1,'warded-armour':1});s['headquarters']['armourEquipped']=True
  s['assetOverrides']['mira']='kept.webp';g.migrate_state(s);old=deepcopy(s);g.migrate_state(s);self.assertEqual(old,s);self.assertEqual(s['assetOverrides']['mira'],'kept.webp')
  self.assertEqual(a.state(s)['items']['legacy:tool:old']['name'],'My notes');self.assertEqual(sum(a.stock_kind(i)=='blade' for i in a.state(s)['items'].values()),2)
  self.assertTrue(g.focus_effect_active(s,'founder','copying-line'));self.assertTrue(s['headquarters']['armourEquipped'])
 def test_legacy_hq_conversion_preserves_one_object(self):
  self.s['headquarters']['stock']['armour']+=1;a.sync(self.s);key=next(i['id'] for i in a.state(self.s)['items'].values() if a.stock_kind(i)=='armour');before=len(a.state(self.s)['items'])
  self.act('hq-job',jobId='enchant-armour')
  for _ in range(3):self.act('advance')
  self.assertEqual(len(a.state(self.s)['items']),before);self.assertIn('legacy-ward',a.state(self.s)['items'][key]['enchantments'])
 def test_stowed_new_effect_not_applied_from_saved_field_loadout(self):
  key=self.item('field-boots');self.enchant(key,'sure-footing');self.equip(key,mode='expedition');self.act('gear-activate',itemId=key,mode='expedition',enchantments=['sure-footing']);self.assertTrue(a.has(self.s,'founder','sure-footing','expedition'))
  self.act('gear-apply-loadout',mode='household');self.assertFalse(a.has(self.s,'founder','sure-footing','expedition'))
 def test_chapter_complete_retreat_and_reward_once(self):
  self.s['keepingHearth']={'completedOn':{'day':1}};before=self.s['sharedFunds'];self.act('arms-start');self.assertEqual(self.s['sharedFunds'],before+32)
  with self.assertRaises(g.RuleError):self.act('arms-start')
  self.act('assign-founder',assignment='rest');self.act('arms-drill');self.act('advance');self.assertTrue(chapter.saved(self.s)['drillDone'])
  for definition,effect in [('field-boots','sure-footing'),('work-shirt','weather-seal')]:
   key=self.item(definition);self.enchant(key,effect);self.equip(key,mode='expedition');self.act('gear-activate',itemId=key,mode='expedition',enchantments=[effect]);self.act('gear-test',itemId=key,mode='expedition',enchantmentId=effect)
  self.act('gear-start-job',operation='commission');self.act('advance');self.act('advance');self.act('gear-deliver-commission');self.assertTrue(g.site_available(self.s,chapter.SITE))
  self.act('start-expedition',siteId=chapter.SITE);self.act('advance');self.act('choose-expedition-approach',approach='survey');self.act('choose-encounter-method',methodId='patient');self.act('advance');self.act('return-expedition');self.act('advance');self.assertEqual(chapter.progress(self.s)['pending']['remaining'],1)
  self.act('start-expedition',siteId=chapter.SITE);self.act('advance');self.act('choose-expedition-approach',approach='survey')
  for _ in range(20):
   if self.s['expedition']['stage']=='ready-to-return':break
   if self.s['expedition']['stage']=='encounter-choice':self.act('choose-encounter-method',methodId='patient')
   self.act('advance')
  funds=self.s['sharedFunds'];self.act('return-expedition');self.act('advance');self.assertEqual(self.s['sharedFunds'],funds+18);self.act('arms-conclude',priority='utility');self.assertTrue(chapter.saved(self.s)['completedOn'])
  with self.assertRaises(g.RuleError):self.act('start-expedition',siteId=chapter.SITE)
 def test_resident_signature_real_fitting_proof_conversation(self):
  key=next(i['id'] for i in a.state(self.s)['items'].values() if i['ownerId']=='mira');self.act('assign-founder',assignment='rest');self.act('assign-resident',assignment='rest')
  self.act('gear-signature-choose',ownerId='mira',itemId=key);self.act('gear-signature-fit',ownerId='mira');self.act('advance');self.assertTrue(a.state(self.s)['signatures']['mira']['fitted'])
  self.equip(key,ownerId='mira');self.act('gear-signature-proof',ownerId='mira');self.act('advance');self.act('gear-signature-close',ownerId='mira',choice='personal');self.assertTrue(a.state(self.s)['signatures']['mira']['completedOn']);self.assertEqual(a.state(self.s)['items'][key]['capacity'],2)
  self.assertTrue(a.state(self.s)['memories']);self.assertTrue(g.public_state(self.s)['armouryView']['signatures'])
if __name__=='__main__':unittest.main()
