"""Two continuous six-chapter routes using earned resources and normal actions."""
import unittest,json
from copy import deepcopy
import game as g, armoury as a, arms_of_our_own as five, headquarters as h
import test_first_hearth as first, test_house_shape as shape, test_room_to_grow as grow, test_keeping_hearth as security

class FiveChapterFlowTests(unittest.TestCase):
 def act(self,kind,**kw):
  g.apply_action(self.s,{'type':kind,**kw});self.s=g.migrate_state(json.loads(json.dumps(self.s)))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def money(self,n):
  if self.s['sharedFunds']>=n:return
  self.act('assign-founder',assignment='commissions')
  while self.s['sharedFunds']<n:self.advance()
  self.act('assign-founder',assignment='rest')
 def learn(self,key):
  if key in g.character_principles(self.s,'founder'):return
  if key=='gentle-preservation' and key not in self.s['archivePrinciples']:
   self.act('start-expedition',siteId='reedbank-waystation',carryLantern=bool(self.s['craftedArtifacts'].get('warming-lantern')))
   for _ in range(12):
    e=self.s['expedition']
    if not e:break
    if e['stage']=='awaiting-choice':self.act('choose-expedition-approach',approach='survey')
    elif e['stage']=='ready-to-return':self.act('return-expedition')
    else:self.advance()
   self.assertIn(key,self.s['archivePrinciples'])
   if key in g.character_principles(self.s,'founder'):return
  if key not in self.s['archivePrinciples']:
   research_id=next((rid for rid,d in g.RESEARCH_CATALOG.items() if d.get('principle')==key),key)
   d=g.RESEARCH_CATALOG[research_id]
   for dep in d['requiredPrinciples']:self.learn(dep)
   self.money(d['costCrowns']);self.act('focus-research',researchId=research_id,leaderId='founder')
   for _ in range(20):
    if self.s['researchProjects'][research_id]['status']=='complete':break
    self.advance()
  if key not in g.character_principles(self.s,'founder'):
   self.act('study-principle',characterId='founder',principleId=key)
   for _ in range(10):
    if key in g.character_principles(self.s,'founder'):break
    self.advance()
  self.assertIn(key,g.character_principles(self.s,'founder'))
 def test_solo_and_company_complete_all_six_chapters(self):
  for company,defense,resolution in [('solo','barriers','capture'),('meet','wards','drive-away')]:
   with self.subTest(company=company):
    one=first.FirstHearthTests();one.setUp();one.act('food-policy',enabled=True,targetDays=7,budget=2,floor=0);one.play(company=company,approach='salvage',reload_each=True)
    two=shape.HouseShapeTests();two.s=one.s;two.beginning=deepcopy(one.s)
    for path,design in [('scholarship','table'),('cultivation','nursery'),('craftsmanship','production')]:two.run_chapter(path,design)
    two.act('shape-conclude');three=grow.RoomToGrowTests();three.s=two.s;three.plan(layout='private' if company=='solo' else 'shared',specialist='smithy');three.play()
    four=security.KeepingHearthTests();four.s=three.s;four.play(defense=defense,choice=resolution);self.s=four.s
    self.act('arms-start');people=['founder']
    if company=='meet':
     cid='introduced-maren'
     for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=cid,topic=topic)
     import arrivals
     room=arrivals.eligible_rooms(self.s,self.s['people']['maren'])[0];self.act('summoning-invite',contactId=cid,roomId=room);self.advance()
     self.act('summoning-ask-stay',contactId=cid);self.act('summoning-household-decision',contactId=cid,decision='invite-to-stay')
     self.assertIn('maren',g.household_members(self.s));self.act('gear-review');people.append('maren');self.act('agree-household-role',characterId='maren',role='fieldwork',enabled=True,willingnessReviewed=True)
     self.act('arms-party',participants=people,agreed=True)
    for w in people:self.act('assign-character',characterId=w,assignment='rest')
    self.act('arms-drill');self.advance();self.assertTrue(five.saved(self.s)['drillDone'])
    self.learn('field-calibration')
    if not h.ready(self.s,'enchanting-room'):
     self.money(65);self.act('hq-build',roomId='enchanting-room')
     for _ in range(10):
      if h.ready(self.s,'enchanting-room'):break
      self.advance()
    for definition,effect in [('field-boots','sure-footing'),('field-staff','measured-force')]:
     self.learn(a.ENCHANTS[effect]['requiredPersonalPrinciple'])
     key=next(i['id'] for i in a.state(self.s)['items'].values() if i['ownerId']=='founder' and i['definitionId']==definition)
     self.act('gear-stow',itemId=key)
     for material in ('porous-clay','binding-thread'):
      if self.s['materialInventory'][material]-self.s['materialReserveTargets'][material]<1:self.money(g.MATERIALS[material]['price']);self.act('buy-material',materialId=material)
     self.money(8);self.act('gear-start-job',operation='enchant',itemId=key,enchantmentId=effect);self.advance(2)
     self.act('gear-equip',itemId=key,mode='expedition',replaceConfirmed=True);self.act('gear-activate',itemId=key,mode='expedition',enchantments=[effect]);self.act('gear-test',itemId=key,mode='expedition',enchantmentId=effect)
    self.act('gear-start-job',operation='commission');self.advance(2);self.act('gear-deliver-commission')
    self.act('gear-party-loadout',participants=people,mode='expedition')
    self.act('start-expedition',siteId=five.SITE,companionIds=people[1:]);self.advance();self.act('choose-expedition-approach',approach='survey')
    for _ in range(20):
     if self.s['expedition']['stage']=='ready-to-return':break
     if self.s['expedition']['stage']=='encounter-choice':
      choices=five.encounter_view(self.s)['choices'];method=next((k for k,c in choices.items() if k!='patient' and not c['blockers']),'patient');self.act('choose-encounter-method',methodId=method)
     self.advance()
    self.act('return-expedition');self.advance();self.act('arms-conclude',priority='utility' if company=='solo' else 'defense')
    self.assertTrue(five.saved(self.s)['completedOn']);self.assertGreaterEqual(sum(x.get('timeSaved',0) for x in self.s['watchRoad']['outcomes']),2);self.assertFalse(self.s['testing']['used']);self.assertGreaterEqual(self.s['sharedFunds'],0);self.assertNotIn('sabine',g.household_members(self.s))
    receipt=self.s['lastExpeditionReport']['logbook']
    self.assertTrue(receipt['completeCoverage']);self.assertTrue(receipt['completedLead'])
    self.assertEqual(len(receipt['outcomes']),len(self.s['watchRoad']['outcomes']))
    self.assertGreaterEqual(sum(o.get('timeSaved',0) for o in receipt['outcomes']),2)
    import roads_we_keep as roads
    self.money(60);self.act('food-buy',bundles=10);self.act('roads-start')
    self.act('start-expedition',siteId=roads.SITE,companionIds=people[1:]);self.advance();self.act('choose-expedition-approach',approach='survey')
    for _ in range(20):
     if self.s['expedition']['stage']=='ready-to-return':break
     if self.s['expedition']['stage']=='encounter-choice':
      choices=roads.encounter_view(self.s)['choices'];method=next((k for k,c in choices.items() if k!='patient' and not c['blockers']),'patient');self.act('choose-encounter-method',methodId=method)
     self.advance()
    self.act('return-expedition');self.advance();self.assertEqual(len(self.s['hollowRoad']['outcomes']),5)
    self.act('roads-agreement',choice='food' if company=='solo' else 'materials')
    self.money(28);self.act('hq-build',roomId='supply-office');self.advance(3)
    self.money(18);self.act('hq-job',jobId='roadside-refuge');self.advance(3);self.act('roads-conclude')
    self.assertTrue(roads.saved(self.s)['completedOn']);self.assertFalse(self.s['testing']['used'])
    self.assertEqual(self.s['provisions']['unfedDays'],0)
    cid='introduced-velis'
    for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=cid,topic=topic)
    import arrivals
    room=arrivals.eligible_rooms(self.s,self.s['people']['velis'])[0];self.act('summoning-invite',contactId=cid,roomId=room);self.advance()
    self.act('summoning-ask-stay',contactId=cid);self.act('summoning-household-decision',contactId=cid,decision='invite-to-stay')
    self.assertIn('velis',g.household_members(self.s));self.act('food-assign',characterId='velis',assignment='forage');self.advance()
    # Reopening and the public UI projection preserve the fully earned campaign.
    before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
    if hasattr(self,'play_seven'):self.play_seven(company)

if __name__=='__main__':unittest.main()
