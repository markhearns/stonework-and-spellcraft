"""Patrol transactions, real household absence, combat and all Chapter 8 plans."""
from copy import deepcopy
import json
import unittest
import game as g, field_patrols as p, field_magic as f, armoury as a
import test_household_chapters as household

class FieldPatrolTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'}
  self.s['provisions']['stock']=300
 def act(self,k,**kw):
  g.apply_action(self.s,dict(type=k,**kw));self.s=g.migrate_state(json.loads(json.dumps(self.s)))
 def reject(self,k,**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(k,**kw)
  self.assertEqual(before,self.s)
 def member(self,w):
  household.HouseholdChapterTests.member(self,w);self.act('agree-household-role',characterId=w,role='fieldwork',enabled=True,willingnessReviewed=True);a.sync(self.s)
 def depart(self,party=None,route='road',mission=None):self.act('watch-depart',participants=party or ['founder'],routeId=route,missionId=mission)
 def enemy(self,key):
  run=p.saved(self.s)['active'];run['enemies']=[key];run.update(index=0,hp=p.ENEMIES[key]['hp'])
 def equip(self,w):
  for definition in ('steel-sword','leather-coat'):
   it=a.make(self.s,definition,w);self.act('gear-equip',ownerId=w,itemId=it['id'],mode='expedition')
 def finish(self):
  for _ in range(70):
   run=p.saved(self.s)['active']
   if not run:return
   if run['stage']=='decision':
    rows=[r for r in p.choices(self.s) if not r['blockers']];peace=next((r for r in rows if r['kind'] in ('peace','bypass')),None)
    row=peace or max((r for r in rows if r['kind']=='attack'),key=lambda r:2*r['preview']['damage']-r['preview']['injury']-8*sum(n==0 for n in r['preview']['healthAfter'].values()))
    self.act('watch-method',methodId=row['id'])
   self.act('advance')
  self.fail('Patrol did not finish')
 def rested(self):
  for _ in range(6):
   if not p.night_blockers(self.s):return
   self.act('advance')
  self.fail('Sleep gate did not clear')
 def test_locked_atomic(self):
  self.s['firstPatrol']['completedOn']=None;self.reject('watch-depart',participants=['founder'],routeId='road');self.reject('trial-start')
 def test_bad_party_and_route_atomic(self):
  for party in ([],['founder','founder'],[{}],['missing'],['founder']*5):self.reject('watch-depart',participants=party,routeId='road')
  self.reject('watch-depart',participants=['founder'],routeId=[])
 def test_unwilling_and_wounded(self):
  household.HouseholdChapterTests.member(self,'rhess');self.reject('watch-depart',participants=['rhess'],routeId='road')
  f.initialize(self.s)['vitality']['founder']=2;self.reject('watch-depart',participants=['founder'],routeId='road')
 def test_solo_companion_founder_works(self):
  self.member('rhess');self.equip('rhess');self.act('assign-founder',assignment='commissions');before=self.s['sharedFunds'];self.depart(['rhess']);self.assertTrue(g.character_at_castle(self.s,'founder'));self.assertFalse(g.character_at_castle(self.s,'rhess'));self.act('advance');self.assertGreater(self.s['sharedFunds'],before);self.assertEqual(f.vitality(self.s,'rhess'),6)
  self.reject('assign-character',characterId='rhess',assignment='rest');self.reject('watch-depart',participants=['founder'],routeId='road')
 def test_founder_legacy_actions_blocked_while_away(self):
  self.depart()
  for k,kw in [('assign-founder',{'assignment':'commissions'}),('start-expedition',{'siteId':'old-waterworks'}),('start-research',{})]:self.reject(k,**kw)
 def test_pending_decision_waits_no_injury(self):
  self.depart();self.act('advance');run=deepcopy(p.saved(self.s)['active']);health=f.vitality(self.s,'founder')
  for _ in range(4):self.act('advance')
  self.assertEqual(run,p.saved(self.s)['active']);self.assertEqual(health,f.vitality(self.s,'founder'));self.assertFalse(self.s['overnightRest'].get('founder'))
 def test_reload_stable_encounters(self):
  self.depart(route='border');before=deepcopy(p.saved(self.s)['active']);self.s=g.migrate_state(json.loads(json.dumps(self.s)));self.assertEqual(before,p.saved(self.s)['active']);self.assertNotIn('enemies',p.view(self.s)['active'])
 def test_damage_and_actual_armour_enchantment(self):
  self.equip('founder');self.depart();self.enemy('bandit');self.act('advance');row=next(r for r in p.choices(self.s) if r['id']=='founder:guard');self.assertGreaterEqual(row['damage'],1);self.assertEqual(row['block'],2)
  self.act('watch-method',methodId=row['id']);self.assertEqual(p.saved(self.s)['active']['hp'],10);self.act('advance');self.assertEqual(p.saved(self.s)['active']['hp'],10-row['damage']);self.assertEqual(f.vitality(self.s,'founder'),5)
 def test_companion_cover_and_no_double_booking(self):
  self.member('rhess');self.depart(['founder','rhess']);self.act('advance');self.assertEqual(p.view(self.s)['active']['cover'],1);self.reject('start-expedition',siteId='old-waterworks',companionIds=['rhess'])
 def test_rewards_once_and_repeat_advancement_bounded(self):
  self.equip('founder')
  for _ in range(2):
   self.depart();self.enemy('wolf');self.finish();report=p.saved(self.s)['reports'][-1];self.assertTrue(report['complete']);self.assertEqual(report['loot']['crowns'],3)
  awards=self.s['characterDevelopment']['founder']['advancementAwards'];self.assertEqual(len([k for k in awards if k.startswith('field-patrol:')]),1)
  self.reject('watch-retreat');self.reject('watch-method',methodId='founder:strike')
 def test_retreat_rest_not_arrival_sleep(self):
  self.depart();self.act('watch-retreat');self.s['currentDayPhase']='evening';f.initialize(self.s)['vitality']['founder']=1;self.act('advance');self.assertTrue(g.character_at_castle(self.s,'founder'));self.assertEqual(f.vitality(self.s,'founder'),1);self.assertFalse(self.s['overnightRest'].get('founder'));self.assertEqual(g.character_assignment(self.s,'founder'),'rest');self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),2)
 def test_defeat_safe_and_no_unearned_loot(self):
  self.depart();self.enemy('griffin');self.act('advance');f.initialize(self.s)['vitality']['founder']=1;self.act('watch-method',methodId='founder:strike');self.act('advance');self.assertEqual(p.saved(self.s)['active']['stage'],'returning');self.act('advance');self.assertFalse(p.saved(self.s)['reports'][-1]['complete']);self.assertEqual(p.saved(self.s)['reports'][-1]['loot']['crowns'],0)
 def test_view_is_read_only(self):
  old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s);self.depart();self.act('advance');old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
 def test_malformed_method_atomic(self):
  self.depart();self.act('advance');self.reject('watch-method',methodId=[])
 def test_all_enemy_rewards_have_real_materials(self):
  for d in p.ENEMIES.values():self.assertTrue(set(d['materials'])<=set(g.MATERIALS))
 def test_rare_weights_and_persistence(self):
  for route,expected in [('woods',5),('border',10)]:
   d=p.ROUTES[route];self.assertEqual(sum(weight for key,weight in zip(d['pool'],d['weights']) if p.ENEMIES[key]['kind']=='mythical'),expected);self.assertEqual(sum(d['weights']),100)
 def test_personal_technique_once_and_advanced_gate(self):
  import personal_paths as paths
  self.s.setdefault('personalPaths',{})['founder']={'learned':[],'techniques':[],'passives':[]}
  keys=[k for k,d in paths.CATALOG.items() if d['who']=='founder' and d['kind']=='technique' and 'enemy' in d['tags']]
  self.s['personalPaths']['founder']['techniques']=keys
  self.depart();self.enemy('griffin');self.act('advance');rows=[r for r in p.choices(self.s) if r['kind']=='technique'];self.assertTrue(rows)
  for row in rows:
   if paths.CATALOG[row['id'].split(':',1)[1]]['advanced']:self.assertTrue(row['blockers'])
  basic=next(r for r in rows if not r['blockers']);self.act('watch-method',methodId=basic['id']);self.act('advance')
  if p.saved(self.s)['active']['stage']=='decision':self.assertTrue(next(r for r in p.choices(self.s) if r['id']==basic['id'])['blockers'])
 def spell(self):
  form=next(k for k,d in g.SPELL_FORMS.items() if d.get('field')=='water');d=g.SPELL_FORMS[form]
  self.s['spellbook'].append(dict(id='patrol-water',formId=form,name=d['name'],ownerId='founder',status='learned',castCount=0,materials=[]))
  self.s['preparedSpells']['founder'].append('patrol-water')
  self.s['founderKnownPrinciples']=list(set(self.s['founderKnownPrinciples']+d['requiredPrinciples']))
  for k,n in d['castingInputs'].items():self.s['materialInventory'][k]+=n+10
  return d
 def test_spell_inputs_refund_and_resolve(self):
  d=self.spell();self.depart();self.enemy('ember-hound');self.act('advance');before=deepcopy(self.s['materialInventory']);self.act('watch-method',methodId='founder:spell:patrol-water')
  for k,n in d['castingInputs'].items():self.assertEqual(before[k]-n,self.s['materialInventory'][k])
  self.act('watch-retreat');self.assertEqual(before,self.s['materialInventory']);self.act('advance');self.depart();self.enemy('ember-hound');self.act('advance');self.act('watch-method',methodId='founder:spell:patrol-water');self.act('advance');self.assertEqual(p.saved(self.s)['active']['hp'],8);self.assertEqual(g.spell_by_id(self.s,'patrol-water')['castCount'],1)
 def test_story_all_plans_and_sleep_gates(self):
  initial=deepcopy(self.s)
  for plan in p.PLANS:
   with self.subTest(plan=plan):
    self.s=deepcopy(initial);self.member('rhess');self.equip('founder');self.equip('rhess')
    for room in ('guard-barracks','watchtower','training-yard'):self.s['headquarters']['rooms'][room]='complete'
    self.act('trial-start');self.depart(['founder','rhess'],mission='scout');self.finish();self.assertIn('scout',p.chapter(self.s)['completed']);self.assertTrue(p.night_blockers(self.s));self.act('trial-plan',choice=plan);self.reject('watch-depart',participants=['founder','rhess'],missionId='escort');self.rested();self.depart(['founder','rhess'],mission='escort');self.finish();self.assertIn('escort',p.chapter(self.s)['completed']);self.rested();self.depart(['founder','rhess'],mission='defend');self.finish();self.assertIn('defend',p.chapter(self.s)['completed']);self.rested()
    while self.s['currentDayPhase']!='evening':self.act('advance')
    self.act('trial-conclude',choice='signals');self.assertTrue(p.chapter(self.s)['completedOn']);self.reject('trial-conclude',choice='supplies');self.reject('watch-depart',participants=['founder'],missionId='scout')

 def test_equipment_mode_restored_on_return(self):
  a.state(self.s)['mode']['founder']='social';self.depart();self.assertEqual(a.state(self.s)['mode']['founder'],'expedition');self.act('watch-retreat');self.act('advance');self.assertEqual(a.state(self.s)['mode']['founder'],'social')
 def test_mythical_reward_and_component_deposit(self):
  self.member('rhess');self.equip('rhess');self.equip('founder');before=self.s['materialInventory']['fireglass'];self.depart(['founder','rhess']);self.enemy('ember-hound');self.finish();self.assertTrue(p.saved(self.s)['reports'][-1]['complete']);self.assertEqual(self.s['materialInventory']['fireglass'],before+2)
 def test_solo_return_conversation_is_report(self):
  import companion_participation as cp
  self.member('rhess');self.depart(['rhess']);self.act('watch-retreat');self.act('advance');e=next(e for e in cp.saved(self.s)['events'].values() if e.get('siteId')=='field-patrol');opening,options=cp.dialogue(self.s,e);self.assertIn('You stayed at the castle',opening)
 def test_real_entrance_improvement_affects_defense(self):
  import keeping_hearth as hearth
  self.s['keepingHearth']={'defense':'barriers'};self.s['headquarters']['stock']['hearth-barriers']=1
  self.assertTrue(hearth.defense_ready(self.s));self.assertEqual(p.encounter_hp(self.s,'bandit','defend'),8);self.assertEqual(p.encounter_hp(self.s,'bandit',None),10)
 def test_patrol_does_not_consume_food_twice(self):
  self.depart();self.s['currentDayPhase']='evening';before=self.s['provisions']['stock'];import provisions
  need=provisions.need(self.s);self.act('advance');self.assertEqual(self.s['provisions']['stock'],before-need)
 def test_named_watch_stops_when_replaced(self):
  self.member('rhess');self.act('trial-start');self.act('trial-watch',characterId='rhess');self.assertEqual(g.character_assignment(self.s,'rhess'),'road-patrol');self.act('trial-watch',characterId=None);self.assertEqual(g.character_assignment(self.s,'rhess'),'rest')
