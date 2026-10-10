"""Creature mechanics, scarce equipment and recruitment use real committed actions."""
from copy import deepcopy
import json
import unittest
import game as g,field_patrols as p,field_magic as f,armoury as a,bestiary as b,creature_challenges as c,rare_accessories as r,recruitment_quests as q,containment
import test_field_patrols as base

class ContentV117Tests(unittest.TestCase):
 act=base.FieldPatrolTests.act
 reject=base.FieldPatrolTests.reject
 member=base.FieldPatrolTests.member
 depart=base.FieldPatrolTests.depart
 enemy=base.FieldPatrolTests.enemy
 equip=base.FieldPatrolTests.equip
 finish=base.FieldPatrolTests.finish
 def setUp(self):
  base.FieldPatrolTests.setUp(self);p.initialize(self.s);self.s['firstRealTest']['completedOn']={'dayNumber':1,'phase':'morning'}
  self.s['sharedFunds']=2000;self.s['founderKnownPrinciples']+=list(g.PRINCIPLE_NAMES)
  for key in self.s['materialInventory']:self.s['materialInventory'][key]=20
 def start_creature(self,cid):
  self.depart();self.enemy(cid);self.act('advance')
 def choice(self,ending):return next(r for r in p.choices(self.s) if r['id'].endswith(ending))
 def step(self,ending):
  row=self.choice(ending);expected=deepcopy(row['preview']);self.act('watch-method',methodId=row['id']);self.act('advance')
  run=p.saved(self.s)['active']
  self.assertEqual({w:f.vitality(self.s,w) for w in run['party']},expected['healthAfter'])
  if run['stage']!='returning':self.assertEqual(run['hp'],expected['enemyAfter'])
  return expected
 def wear(self,key,who='founder'):
  it=a.make(self.s,key,who);a.put_in(self.s,who,it['id'],'expedition');return it
 def candidate(self,ancestry='Human',who='test-traveller'):
  import character_pool as pool,candidate_proposals as cp
  selection=pool.select(self.s,'v117-'+who,{'ancestry':ancestry});proposal=pool.offline(self.s,selection,'v117-'+who)
  self.s['reviewedCandidates'][who]=cp.approved_definition(proposal,who,'offline','v117-'+who)
  return who
 def test_difficult_routes_and_bounties_share_chapter_gate(self):
  self.s['firstRealTest']['completedOn']=None
  for route in ('deep-quarry','high-crags','flooded-basin'):self.reject('watch-depart',routeId=route,participants=['founder'])
  for cid in ('basilisk','manticore','wyvern','marsh-hydra','runebound-colossus'):self.reject('watch-depart',bountyId=cid,participants=['founder'])
  self.assertTrue(all(d['blockers'] for d in p.view(self.s)['routes'].values() if d.get('challengeTier')=='Difficult'))
 def test_every_creature_preview_is_pure_and_matches_resolution(self):
  base=deepcopy(self.s)
  for cid,d in b.CREATURES.items():
   if not b.ENCOUNTERS[d['enemyId']].get('challenge'):continue
   with self.subTest(creature=cid):
    self.s=deepcopy(base);self.equip('founder');self.start_creature(cid)
    old=deepcopy(self.s);rows=p.choices(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
    for row in rows:
     if row['blockers']:continue
     self.s=deepcopy(old);expected=row['preview'];self.act('watch-method',methodId=row['id']);self.act('advance')
     self.assertEqual({w:f.vitality(self.s,w) for w in p.saved(self.s)['active']['party']},expected['healthAfter'],row['id'])
 def test_colossus_shutdown_requires_wards_and_records_discovery_once(self):
  self.start_creature('runebound-colossus')
  self.assertTrue(self.choice(':field-approach')['blockers'])
  for _ in range(3):self.step(':creature:disconnect')
  self.assertEqual(c.state(self.s,p.saved(self.s)['active'])['wards'],0)
  self.assertGreater(self.choice(':strike')['preview']['damage'],1)
 def test_hydra_pin_heat_and_component_reserves_refunds(self):
  self.equip('founder');self.start_creature('marsh-hydra');run=p.saved(self.s)['active']
  self.assertIn('secondary',p.view(self.s)['active']['intent'])
  self.step(':creature:pin');self.step(':creature:pin')
  self.assertNotIn('secondary',p.view(self.s)['active']['intent'])
  self.s['materialReserveTargets']['sun-amber']=20;self.assertTrue(self.choice(':creature:heat')['blockers'])
  self.s['materialReserveTargets']['sun-amber']=0;row=self.choice(':creature:heat');old=self.s['materialInventory']['sun-amber']
  self.act('watch-method',methodId=row['id']);self.assertEqual(self.s['materialInventory']['sun-amber'],old-1)
  self.act('watch-retreat');self.assertEqual(self.s['materialInventory']['sun-amber'],old)
 def test_rare_recipes_exact_cost_reserve_cancel_and_completed_object(self):
  self.s['headquarters']['rooms']['enchanting-room']='complete'
  for key,d in r.RECIPES.items():
   with self.subTest(item=key):
    action=dict(operation='craft',definitionId=key,workerId='founder');quote=a.recipe(self.s,action)
    self.assertFalse(quote['blockers']);self.assertEqual(quote['materials'].count(d['drop']),2)
    self.s['materialReserveTargets'][d['drop']]=19;self.reject('gear-start-job',**action);self.s['materialReserveTargets'][d['drop']]=0
    old=deepcopy(self.s['materialInventory']);money=self.s['sharedFunds'];self.act('gear-start-job',**action);self.act('advance');self.act('gear-cancel-job');self.assertEqual(self.s['materialInventory'],old);self.assertEqual(self.s['sharedFunds'],money)
    self.act('gear-start-job',**action)
    for _ in range(6):self.act('advance')
    self.assertEqual(sum(i['definitionId']==key for i in a.state(self.s)['items'].values()),1)
    self.assertEqual(self.s['materialInventory'][d['drop']],old[d['drop']]-2)
 def test_rare_accessory_effects_ownership_stowing_and_vault(self):
  self.equip('founder');self.start_creature('basilisk');baseline=self.choice(':strike')['preview'];it=self.wear('basilisk-mirror-brooch')
  protected=self.choice(':strike')['preview'];self.assertGreaterEqual(protected['cover'],baseline['cover']+2);self.assertFalse(protected['creatureState']['stiffness'])
  it['ownerId']='mira';self.assertEqual(self.choice(':strike')['preview']['cover'],baseline['cover']);it['ownerId']='founder';it['location']='vault';self.assertEqual(self.choice(':strike')['preview']['cover'],baseline['cover'])
  it['location']='armoury';self.wear('manticore-barb-ring');self.assertEqual(self.choice(':strike')['accessoryDamage'],2)
  self.wear('wyvern-antivenom-locket');run=p.saved(self.s)['active'];run['enemies']=['wyvern'];run['hp']=23;run['round']=2
  self.assertFalse(self.choice(':strike')['preview']['creatureState']['venom'])
  self.wear('hydra-heart-charm');f.initialize(self.s)['vitality']['founder']=3
  self.assertFalse(self.choice(':guard')['preview']['healing']) # The charm cannot revive a knocked-out wearer.
  f.initialize(self.s)['vitality']['founder']=6
  self.assertTrue(any(h['who']=='founder' and h['amount']==1 for h in self.choice(':guard')['preview']['healing']))
 def test_rescue_is_required_and_invitation_is_optional(self):
  who=self.candidate();self.reject('open-correspondence',characterId=who)
  self.act('recruit-lead',characterId=who,questKind='rescue');self.reject('recruit-invite',characterId=who)
  self.equip('founder');self.act('recruit-depart',characterId=who,participants=['founder']);self.finish()
  g.public_state(self.s);self.assertEqual(q.saved(self.s)[who]['status'],'rescued');self.assertNotIn(who,self.s['people'])
  self.act('recruit-invite',characterId=who);self.assertIn(who,self.s['people']);self.assertNotIn(who,g.household_members(self.s));self.reject('recruit-invite',characterId=who)
  self.assertEqual(self.s['summoningContacts']['introduced-'+who]['contactOrigin'],'rescued-traveller')
 def test_capture_reserves_cell_requires_weakened_enemy_and_release(self):
  who=self.candidate('Ogrekin');self.act('recruit-lead',characterId=who,questKind='capture');self.reject('recruit-depart',characterId=who,participants=['founder'])
  chamber=next(k for k,d in containment.CHAMBERS.items() if d['ward']=='echo');self.s['containment']['chambers'][chamber]['status']='ready'
  self.member('rhess');self.equip('founder');self.equip('rhess');self.act('recruit-depart',characterId=who,participants=['founder','rhess']);self.assertTrue(containment.occupied(self.s,chamber));self.act('advance')
  self.reject('watch-method',methodId='founder:capture-bandit')
  for _ in range(5):self.step(':guard')
  self.step(':capture-bandit');self.act('advance');g.public_state(self.s);self.assertEqual(q.saved(self.s)[who]['status'],'custody');self.reject('recruit-invite',characterId=who)
  for topic,choice in [('account','verify'),('restitution','fair'),('future','listen')]:
   self.act('recruit-talk',characterId=who,topic=topic,choice=choice)
   if topic=='account':self.reject('recruit-talk',characterId=who,topic='future',choice='listen')
   self.act('advance')
  self.act('recruit-release',characterId=who);self.assertFalse(containment.occupied(self.s,chamber));self.act('recruit-invite',characterId=who)
  self.assertEqual(self.s['summoningContacts']['introduced-'+who]['contactOrigin'],'released-bandit')
 def test_retreat_frees_reserved_cell_and_grants_no_person(self):
  who=self.candidate();self.act('recruit-lead',characterId=who,questKind='capture');chamber=next(k for k,d in containment.CHAMBERS.items() if d['ward']=='echo');self.s['containment']['chambers'][chamber]['status']='ready'
  self.act('recruit-depart',characterId=who,participants=['founder']);self.act('watch-retreat');self.act('advance');self.assertFalse(containment.occupied(self.s,chamber));self.assertEqual(q.saved(self.s)[who]['status'],'available');self.assertNotIn(who,self.s['people'])
 def test_exotics_and_authored_neighbours_cannot_be_bandit_leads(self):
  who=self.candidate('Kitsune');self.reject('recruit-lead',characterId=who,questKind='rescue')
  import local_encounters
  self.s['localEncounterCandidates']['fenna']=local_encounters.definition(self.s,'fenna');self.reject('recruit-lead',characterId='fenna',questKind='capture')

if __name__=='__main__':unittest.main()
