from copy import deepcopy
import unittest
import game as g,armoury as a,equipment,signature_equipment as sig,room_life,guidance
import test_armoury
import test_household_chapters

class IntegrationTests(unittest.TestCase):
 def setUp(self):
  f=test_armoury.ArmouryTests();f.setUp();self.s=f.s
 def act(self,k,**kw):g.apply_action(self.s,dict(type=k,**kw))
 def test_all_authored_people_and_founder_complete_signature(self):
  helper=test_household_chapters.HouseholdChapterTests();helper.s=self.s
  for who in sig.CONTENT:
   if who!='founder':helper.member(who)
  self.s['facilityProjects']['kitchen']['status']='complete';self.s['restorationStatus']='complete'
  self.act('gear-review')
  for who in sig.CONTENT:
   with self.subTest(who=who):
    self.act('assign-founder',assignment='rest');g.set_character_assignment(self.s,who,'rest')
    key=next(i['id'] for i in a.state(self.s)['items'].values() if i['ownerId']==who)
    self.act('gear-signature-choose',ownerId=who,itemId=key);self.act('gear-signature-fit',ownerId=who)
    self.assertEqual(room_life.location(self.s,'founder'),sig.ROOMS[who]);self.assertIn('equipment:founder',guidance.projects(self.s))
    self.act('advance');self.act('gear-equip',ownerId=who,itemId=key,replaceConfirmed=True);self.act('gear-signature-proof',ownerId=who)
    self.assertEqual(room_life.location(self.s,who),'training-yard');self.act('advance');self.act('gear-signature-close',ownerId=who,choice='practical')
    self.assertTrue(sig.record(self.s,who)['completedOn']);self.assertEqual(a.state(self.s)['items'][key]['signatureOwner'],who)
    old=deepcopy(self.s)
    with self.assertRaises(g.RuleError):self.act('gear-signature-close',ownerId=who,choice='practical')
    self.assertEqual(old,self.s)
 def test_crafted_tool_keeps_one_physical_identity_and_active_calibration(self):
  self.act('gear-start-job',operation='craft',definitionId='scholars-folio')
  for _ in range(3):self.act('advance')
  it=next(i for i in a.state(self.s)['items'].values() if (i.get('legacy') or {}).get('kind')=='tool');key=it['id'];tid=it['legacy']['id']
  self.act('gear-equip',itemId=key,replaceConfirmed=True);self.act('rename-working-tool',ownerId='founder',itemId=tid,name='Measured pages')
  self.assertEqual(sum(i.get('legacy')=={'kind':'tool','id':tid} for i in a.state(self.s)['items'].values()),1)
  self.act('upgrade-working-tool',ownerId='founder',itemId=tid,materials=['porous-clay','binding-thread']);self.act('advance');self.act('advance')
  self.assertEqual(equipment.bonus(self.s,'founder','archive-focus')[0]['amount'],2)
  self.act('gear-activate',itemId=key,enchantments=[]);self.assertEqual(equipment.bonus(self.s,'founder','archive-focus')[0]['amount'],1)
  self.act('gear-stow',itemId=key);self.act('gear-start-job',operation='expand',itemId=key);self.assertEqual(equipment.bonus(self.s,'founder','archive-focus'),[])
 def test_new_object_job_cannot_reserve_unrelated_host(self):
  key=next(iter(a.state(self.s)['items']));old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('gear-start-job',operation='commission',itemId=key)
  self.assertEqual(old,self.s)
 def test_removing_stowed_inscription_leaves_loadouts_valid(self):
  key=a.make(self.s,'field-boots','founder')['id'];a.state(self.s)['items'][key]['enchantments']['sure-footing']={'id':'sure-footing','rank':1}
  self.act('gear-remove-enchantment',itemId=key,enchantmentId='sure-footing',confirmed=True)
  for mode in a.MODES:a.validate_loadout(self.s,'founder',a.loadout(self.s,'founder',mode))
if __name__=='__main__':unittest.main()
