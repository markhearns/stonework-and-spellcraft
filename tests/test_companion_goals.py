"""Exercise finite goals through actual choices, paid work and saved completion."""
from copy import deepcopy
import json, unittest
from unittest.mock import patch
import game as g, companion_goals as cg, character_quests as q
import companion_conversations as cc, headquarters as h, armoury, provisions
import test_household_chapters as household, test_magic_overhaul as magic
import test_content_v117 as creatures
import field_patrols as patrols, creature_challenges, field_magic

class CompanionGoalTests(unittest.TestCase):
 def setUp(self):
  self.s=magic.MagicTests.rich(self)
  for who in cg.GOALS:household.HouseholdChapterTests.member(self,who)
  for key in h.ROOMS:household.HouseholdChapterTests.room(self,key)
  for k in self.s['materialInventory']:self.s['materialInventory'][k]=200;self.s['materialReserveTargets'][k]=0
  self.s['provisions']['stock']=10000
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def finish(self,who,choice='0'):
  key='ambition:'+who
  while True:
   record=next(x for x in q.records(self.s) if x['id']==key)
   if record['status']=='complete':return record
   self.act('talk-character-quest',questId=key,choice=choice)
   if record['status']=='ending':continue
   record=q.saved(self.s)['records'][key]
   if record['status']=='complete':return record
   method=q.methods(self.s,record)['patient'];self.assertFalse(method['blockers'],method['blockers'])
   before=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds']
   self.act('choose-quest-method',questId=key,methodId='patient')
   self.assertEqual(self.s['sharedFunds'],funds-method['crowns'])
   for k,n in method['cost'].items():self.assertEqual(self.s['materialInventory'][k],before[k]-n)
   for _ in range(method['phases']):self.act('advance')
   self.assertIn(q.saved(self.s)['records'][key]['status'],('interlude','ending'))
 def test_all_sixteen_goals_both_choices_finish_through_actual_work(self):
  base=deepcopy(self.s)
  for who,d in cg.GOALS.items():
   for choice in ('0','1'):
    with self.subTest(who=who,choice=choice):
     self.s=deepcopy(base);record=self.finish(who,choice)
     self.assertEqual(len(record['outcomes']),len(d['stages']))
     self.assertEqual(record['decisions'],{str(i):int(choice) for i in range(len(d['stages']))})
     self.assertEqual(len(record['memories']),len(d['stages'])+1)
     self.assertNotEqual(record['memories'][-1]['opening'],record['memories'][-1]['response'])
     self.assertEqual(cg.person(self.s,who)['achievement']['proof'],d['proof'])
     self.assertEqual(cc.CHARACTER[who][0],d['want'])
     for p in ('founder',who):self.assertEqual(self.s['characterDevelopment'][p]['advancementAwards']['character-goal:'+who]['points'],2)
     self.reject('talk-character-quest',questId=record['id'],choice=choice)
     before=deepcopy(self.s['characterDevelopment']);items=deepcopy(armoury.state(self.s));kits=cg.saved(self.s)['kits']
     for followup in ('0','1'):self.act('goal-revisit',characterId=who,choice=followup)
     cg.finish(self.s,record)
     self.assertEqual(before,self.s['characterDevelopment']);self.assertEqual(items,armoury.state(self.s));self.assertEqual(kits,cg.saved(self.s)['kits'])
     self.assertEqual(len(cg.context(self.s,who)['history']),2)
     visible=g.public_state(self.s);self.assertTrue(visible['companionGoalsView']['people'][who]['completed'])
 def test_views_are_pure_hide_unreached_dialogue_and_show_real_stage(self):
  before=deepcopy(self.s);v=g.public_state(self.s);self.assertEqual(before,self.s)
  self.assertEqual(len(v['companionGoalsView']['people']),16)
  self.assertNotIn(cg.GOALS['kaede']['ending'],json.dumps(v))
  self.act('talk-character-quest',questId='ambition:kaede',choice='0')
  v=g.public_state(self.s);self.assertNotIn(cg.GOALS['kaede']['ending'],json.dumps(v))
  row=next(r for r in v['characterQuestsView']['quests'] if r['id']=='ambition:kaede')
  self.assertEqual(row['obstacle'],'Enter and choose a training plan')
  self.assertTrue(row['methods']['spell']['blockers'])
  self.assertEqual(row['methods']['patient']['crowns'],12)
 def test_rooms_reserves_and_rare_samples_block_work_atomically(self):
  self.act('talk-character-quest',questId='ambition:zahra',choice='0');self.s['headquarters']['rooms']['smithy']='not-started'
  self.reject('choose-quest-method',questId='ambition:zahra',methodId='patient')
  self.s['headquarters']['rooms']['smithy']='complete';record=q.active(self.s);record['step']=1
  material=next(iter(cg.current(record)['materials']));self.s['materialReserveTargets'][material]=200
  self.reject('choose-quest-method',questId=record['id'],methodId='patient')
  self.s['materialReserveTargets'][material]=0;self.s['sharedFunds']=0
  self.reject('choose-quest-method',questId=record['id'],methodId='patient')
  self.act('pause-character-quest',questId=record['id']);self.act('talk-character-quest',questId='ambition:elowen',choice='0')
  record=q.active(self.s);record['step']=1;self.s['materialInventory']['manticore-spine']=0
  self.reject('choose-quest-method',questId=record['id'],methodId='patient')
 def test_paid_work_pauses_reloads_and_resumes_without_recharge(self):
  key='ambition:kaede';self.act('talk-character-quest',questId=key,choice='1');self.act('choose-quest-method',questId=key,methodId='patient')
  funds=self.s['sharedFunds'];self.act('pause-character-quest',questId=key);self.act('advance')
  self.assertEqual(q.saved(self.s)['records'][key]['pending']['remaining'],3)
  self.s=g.migrate_state(json.loads(json.dumps(self.s)));self.act('resume-character-quest',questId=key)
  for _ in range(3):self.act('advance')
  self.assertEqual(self.s['sharedFunds'],funds);self.assertEqual(q.active(self.s)['step'],1)
 def test_overlapping_old_quests_count_and_cannot_be_started_twice(self):
  base=deepcopy(self.s)
  for who,credit in cg.LEGACY_CREDIT.items():
   with self.subTest(who=who):
    self.s=deepcopy(base);key='personal:'+who
    self.act('talk-character-quest',questId=key,choice='warm');self.act('pause-character-quest',questId=key)
    self.reject('talk-character-quest',questId='ambition:'+who,choice='0');self.act('resume-character-quest',questId=key)
    for _ in range(2):
     self.act('choose-quest-method',questId=key,methodId='patient')
     for _ in range(3):self.act('advance')
     self.act('talk-character-quest',questId=key,choice='warm')
    definition=next(x for x in cg.definitions(self.s) if x['who']==who);self.assertEqual(definition['step'],credit)
    self.finish(who);self.assertEqual(q.saved(self.s)['records'][key]['status'],'complete')
    self.s=deepcopy(base);self.act('talk-character-quest',questId='ambition:'+who,choice='0')
    self.assertNotIn(key,[x['id'] for x in q.records(self.s)]);self.reject('talk-character-quest',questId=key,choice='warm')
 def test_real_owned_items_and_nonrepeating_rewards(self):
  for who in ('zahra','sabine'):
   self.finish(who);achievement=cg.saved(self.s)['achievements'][who]
   item=armoury.state(self.s)['items'][achievement['itemId']]
   self.assertEqual(item['ownerId'],who)
   if who=='zahra':self.assertEqual(item['enchantments']['measured-force']['rank'],1);self.assertEqual(item['capacity'],2)
 def test_sabine_choices_have_different_prices(self):
  self.act('talk-character-quest',questId='ambition:sabine',choice='0');record=q.active(self.s);record['step']=2
  record['decisions']['2']=0;self.assertEqual(q.methods(self.s,record)['patient']['crowns'],12)
  record['decisions']['2']=1;self.assertEqual(q.methods(self.s,record)['patient']['crowns'],32)
  self.assertIn('direct purchase',cg.result(record))
 def test_menu_and_supply_route_affect_real_morning(self):
  self.finish('tamsin');self.finish('velis');self.assertEqual(provisions.contract(self.s),2)
  stock=self.s['provisions']['stock'];self.act('goal-meal',menu='tamsin');self.assertEqual(self.s['provisions']['stock'],stock)
  self.s['provisions'].update(stock=0,auto=False);self.s['currentDayPhase']='evening';self.act('advance')
  self.assertEqual(self.s['provisions']['lastMeal']['served'],2)
  self.assertIn('pear tart',self.s['provisions']['lastMeal']['menu'])
 def test_restocks_respect_reserves_and_away_is_atomic(self):
  self.finish('elowen');self.assertEqual(cg.saved(self.s)['kits'],1)
  before=deepcopy(self.s['materialInventory']);self.act('goal-craft-kit');self.assertEqual(cg.saved(self.s)['kits'],2)
  self.assertEqual(self.s['materialInventory']['silver-ivy'],before['silver-ivy']-3)
  self.s['materialReserveTargets']['silver-ivy']=self.s['materialInventory']['silver-ivy'];self.reject('goal-craft-kit')
  with patch('game.character_at_castle',return_value=False):self.reject('goal-revisit',characterId='elowen',choice='0')
 def test_completed_merrin_scenes_and_spirit_context_do_not_reopen_goal(self):
  self.finish('merrin');import household_chapters
  rows=household_chapters.personal_rows(self.s,'merrin')
  self.assertEqual(rows[1]['title'],'The complete comedy');self.assertNotIn('looking for another copy',str(rows[1]))
  self.assertIn('massless',cg.context(self.s,'merrin')['spiritInteraction'])
 def test_schema75_migration_preserves_earlier_quests(self):
  self.act('talk-character-quest',questId='personal:mira',choice='warm');self.s.pop('companionGoals',None);self.s['schemaVersion']=75
  old=deepcopy(self.s['characterQuests']);self.s=g.migrate_state(self.s)
  self.assertEqual(self.s['schemaVersion'],76);self.assertEqual(self.s['characterQuests'],old);self.assertEqual(cg.saved(self.s)['achievements'],{})

class FieldKitTests(unittest.TestCase):
 setUp=creatures.ContentV117Tests.setUp
 act=creatures.ContentV117Tests.act
 reject=creatures.ContentV117Tests.reject
 depart=creatures.ContentV117Tests.depart
 enemy=creatures.ContentV117Tests.enemy
 start_creature=creatures.ContentV117Tests.start_creature
 def test_goal_kit_real_preview_payment_and_refund(self):
  cg.initialize(self.s);cg.saved(self.s)['achievements']['elowen']={'test':True};cg.saved(self.s)['kits']=2
  self.start_creature('manticore');run=patrols.saved(self.s)['active'];run['round']=1
  field_magic.initialize(self.s)['vitality']['founder']=2
  st=creature_challenges.state(self.s,run);st['venom']['founder']=2;st['stiffness']['founder']=3;run['creatureState']=st
  row=next(r for r in patrols.choices(self.s) if r.get('goalKit'))
  self.assertFalse(row['blockers']);self.assertEqual(row['preview']['healing'][0]['amount'],4)
  self.assertNotIn('founder',row['preview']['creatureState']['venom']);self.assertNotIn('founder',row['preview']['creatureState']['stiffness'])
  self.act('watch-method',methodId=row['id']);self.assertEqual(cg.saved(self.s)['kits'],1)
  self.act('advance');self.assertEqual(field_magic.vitality(self.s,'founder'),row['preview']['healthAfter']['founder'])
  self.assertEqual(cg.saved(self.s)['kits'],1);self.act('watch-retreat');self.assertEqual(cg.saved(self.s)['kits'],1)
 def test_pending_goal_kit_returns_once_on_retreat(self):
  cg.initialize(self.s);cg.saved(self.s)['achievements']['elowen']={'test':True};cg.saved(self.s)['kits']=1
  self.start_creature('basilisk');field_magic.initialize(self.s)['vitality']['founder']=4
  row=next(r for r in patrols.choices(self.s) if r.get('goalKit'));self.act('watch-method',methodId=row['id'])
  self.assertEqual(cg.saved(self.s)['kits'],0);self.act('watch-retreat');self.assertEqual(cg.saved(self.s)['kits'],1)
  self.reject('watch-retreat');self.assertEqual(cg.saved(self.s)['kits'],1)

if __name__=='__main__':unittest.main()
