from copy import deepcopy
import json,unittest,tempfile,sqlite3
import game as g, personal_paths as p, field_magic as f, armoury as a
import test_household_chapters as household

class PersonalPathTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['researchStatus']='complete'
  for who in ('rhess','kaede','sabine'):household.HouseholdChapterTests.member(self,who)
  self.s['headquarters']['rooms']['training-yard']='complete';a.sync(self.s)
 def act(self,kind,**kw):
  g.apply_action(self.s,dict(type=kind,**kw));self.s=g.migrate_state(json.loads(json.dumps(self.s)))
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def prepare(self,who,*keys):
  p.ensure(self.s,who)['learned']=list(keys)
  for key in keys:self.act('path-prepare',characterId=who,talentId=key,prepared=True)
 def at(self,step,who='kaede'):
  self.s['expedition']={'siteId':f.SITE,'partyIds':['founder',who],'companionId':who,'stage':'encounter-choice','discoveryReady':False,'chosenApproach':'survey','restoreLanternDisplay':False}
  f.initialize(self.s);f.progress(self.s)['completed']=[d['id'] for d in f.STEPS[:next(i for i,d in enumerate(f.STEPS) if d['id']==step)]]
 def test_training_pauses_persists_and_spends_no_household_advancement(self):
  before=g.character_sheet(self.s,'kaede')['availableAdvancement'];funds=self.s['sharedFunds']
  self.act('path-train',characterId='kaede',talentId='measured-blow');self.act('advance')
  self.assertEqual(self.s['trainingProjects']['kaede']['completedWorkPhases'],1)
  self.act('assign-character',characterId='kaede',assignment='rest');self.act('advance');self.assertEqual(self.s['trainingProjects']['kaede']['completedWorkPhases'],1)
  self.act('assign-character',characterId='kaede',assignment='training');self.act('advance');self.assertIn('measured-blow',p.record(self.s,'kaede')['learned']);self.assertFalse(p.record(self.s,'kaede')['techniques']);self.assertEqual(before,g.character_sheet(self.s,'kaede')['availableAdvancement']);self.assertEqual(funds,self.s['sharedFunds'])
 def test_talent_and_character_validation_atomic(self):
  for kw in [dict(characterId=[],talentId='measured-blow'),dict(characterId='kaede',talentId=[]),dict(characterId='kaede',talentId='spear-watch')]:self.reject('path-train',**kw)
  self.reject('path-prepare',characterId='kaede',talentId='measured-blow',prepared=True)
  self.s['headquarters']['rooms']['training-yard']='not-started';self.reject('path-train',characterId='kaede',talentId='measured-blow')
 def test_slots_are_separate_and_clear_keeps_knowledge(self):
  keys=[k for k,d in p.CATALOG.items() if d['who']=='kaede'];p.ensure(self.s,'kaede')['learned']=keys
  for key in ('measured-blow','settled-stance','steady-hands'):self.act('path-prepare',characterId='kaede',talentId=key,prepared=True)
  self.reject('path-prepare',characterId='kaede',talentId='gate-breaker',prepared=True)
  for key in ('follow-through','unshaken'):self.act('path-prepare',characterId='kaede',talentId=key,prepared=True)
  self.reject('path-prepare',characterId='kaede',talentId='clear-example',prepared=True)
  self.act('path-clear',characterId='kaede');self.assertEqual(p.record(self.s,'kaede')['learned'],keys);self.assertFalse(p.record(self.s,'kaede')['techniques'])
 def test_signature_gate_and_passive_lifetime_requirement(self):
  self.prepare('kaede','measured-blow');self.reject('path-train',characterId='kaede',talentId='gate-breaker');self.reject('path-train',characterId='kaede',talentId='follow-through')
  g.award_advancement(self.s,'kaede','test',2,'Evidence');self.s['characterSkills']['kaede']['athletics']=1
  self.assertEqual(g.character_sheet(self.s,'kaede')['availableAdvancement'],0)
  self.act('path-train',characterId='kaede',talentId='follow-through');self.act('advance');self.act('advance');self.assertIn('follow-through',p.record(self.s,'kaede')['learned'])
 def test_combat_damage_guard_award_and_duplicate_rejection(self):
  self.prepare('kaede','settled-stance','unshaken');self.at('bones');before=f.vitality(self.s,'kaede')
  self.act('field-method',characterId='kaede',method='personal:settled-stance');self.assertNotIn('bones',f.progress(self.s)['enemyHp']);self.act('advance')
  self.assertEqual(f.progress(self.s)['enemyHp']['bones'],4);self.assertEqual(f.vitality(self.s,'kaede'),before)
  self.assertEqual(g.character_sheet(self.s,'kaede')['earnedAdvancement'],2)
  self.reject('field-method',characterId='kaede',method='personal:settled-stance')
 def test_active_enchantment_only_and_single_count_for_two_hands(self):
  self.prepare('kaede','measured-blow','follow-through');it=a.make(self.s,'steel-kanabo','kaede');it['enchantments']={'measured-force':{'id':'measured-force','rank':2}}
  a.put_in(self.s,'kaede',it['id'],'expedition');a.loadout(self.s,'kaede','expedition')['active'][it['id']]=['measured-force']
  self.assertEqual(p.effect(self.s,'kaede','measured-blow')['damage'],4)
  a.state(self.s)['mode']['kaede']='expedition';self.assertEqual(p.effect(self.s,'kaede','measured-blow')['damage'],5)
  self.assertEqual(len(p.effect(self.s,'kaede','measured-blow')['gear']),1)
 def test_advanced_requires_owned_equipped_signature(self):
  self.prepare('kaede','gate-breaker');self.at('bones');self.reject('field-method',characterId='kaede',method='personal:gate-breaker')
  it=a.make(self.s,'steel-kanabo','kaede');a.put_in(self.s,'kaede',it['id'],'expedition');a.state(self.s)['signatures']['kaede']={'itemId':it['id'],'completedOn':{'day':1}}
  self.act('field-method',characterId='kaede',method='personal:gate-breaker');self.act('advance');self.assertEqual(f.progress(self.s)['enemyHp']['bones'],2);self.assertEqual(f.vitality(self.s,'kaede'),3)
 def test_wounded_cannot_spend_last_vitality(self):
  self.prepare('kaede','measured-blow');self.at('bones');f.initialize(self.s)['vitality']['kaede']=0;self.reject('field-method',characterId='kaede',method='personal:measured-blow')
 def test_retreat_no_reward_pending_and_used_survives(self):
  self.prepare('kaede','steady-hands');self.at('stone');self.act('field-method',characterId='kaede',method='personal:steady-hands');self.act('advance');self.act('return-expedition');self.act('advance');self.assertNotIn('personalPathUses',self.s);self.assertEqual(g.character_sheet(self.s,'kaede')['earnedAdvancement'],0)
  self.at('stone');self.act('field-method',characterId='kaede',method='personal:steady-hands');self.act('advance');self.act('advance');self.assertEqual(len(self.s['personalPathUses']),1)
  self.act('return-expedition');self.act('advance');self.at('stone');self.reject('field-method',characterId='kaede',method='personal:steady-hands')
 def test_route_methods_chapter_six_and_seven(self):
  import roads_we_keep as road,first_patrol as patrol
  self.prepare('rhess','route-reader','waymarks')
  for site in (road.SITE,patrol.WARD):
   self.s['expedition']={'siteId':site,'partyIds':['founder','rhess'],'stage':'encounter-choice','discoveryReady':False,'chosenApproach':'survey','restoreLanternDisplay':False}
   self.act('choose-encounter-method',methodId='personal:route-reader');self.act('advance')
   progress=road.progress(self.s) if site==road.SITE else patrol.progress(self.s)
   self.assertEqual(len(progress['completed']),1);self.assertIn('Route reader',progress['outcomes'][0]['method']);self.assertEqual(progress['outcomes'][0]['timeSaved'],1)
 def test_wrong_site_or_wrong_actor_cannot_use_personal_field_endpoint(self):
  import roads_we_keep as road
  self.prepare('kaede','steady-hands');self.s['expedition']={'siteId':road.SITE,'partyIds':['founder','kaede'],'stage':'encounter-choice'}
  self.reject('field-method',characterId='kaede',method='personal:steady-hands')
  self.at('stone');self.reject('field-method',characterId='founder',method='personal:steady-hands');self.reject('path-clear',characterId='kaede')
 def test_every_node_learns_and_view_remains_pure(self):
  for who in ('rhess','kaede','sabine'):
   g.award_advancement(self.s,who,'test',2,'Evidence');a.state(self.s)['signatures'][who]={'completedOn':{'day':1},'itemId':'test'}
   for key,d in p.CATALOG.items():
    if d['who']!=who:continue
    self.act('path-train',characterId=who,talentId=key);self.act('advance');self.act('advance');self.assertIn(key,p.record(self.s,who)['learned'])
  old=deepcopy(self.s);view=p.view(self.s);self.assertEqual(self.s,old);self.assertEqual(sum(len(view[w]['options']) for w in ('rhess','kaede','sabine')),27)
 def test_flame_immunity_and_counter(self):
  self.prepare('rhess','banked-flame');self.at('ember','rhess');self.reject('field-method',characterId='rhess',method='personal:banked-flame')
  self.s['expedition']=None;self.prepare('kaede','turning-counter');it=a.make(self.s,'steel-kanabo','kaede');a.put_in(self.s,'kaede',it['id'],'expedition');a.state(self.s)['signatures']['kaede']={'itemId':it['id'],'completedOn':{'day':1}}
  self.at('bones');self.act('field-method',characterId='kaede',method='personal:turning-counter');self.act('advance');self.assertEqual(f.progress(self.s)['enemyHp']['bones'],3);self.assertEqual(f.vitality(self.s,'kaede'),6)
 def test_support_heals_companion_and_cannot_repeat(self):
  self.prepare('kaede','catch-breath','clear-example');it=a.make(self.s,'steel-kanabo','kaede');a.put_in(self.s,'kaede',it['id'],'expedition');a.state(self.s)['signatures']['kaede']={'itemId':it['id'],'completedOn':{'day':1}}
  self.at('bones');f.initialize(self.s)['vitality']['founder']=1
  self.act('field-method',characterId='kaede',method='personal:catch-breath');self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),3);self.reject('field-method',characterId='kaede',method='personal:catch-breath')
 def test_drill_snapshot_persists_and_no_rewards_or_injury(self):
  self.prepare('kaede','measured-blow','follow-through');before=(g.character_sheet(self.s,'kaede')['earnedAdvancement'],f.vitality(self.s,'kaede'),deepcopy(self.s['materialInventory']))
  self.act('path-drill',characterId='kaede',scenario='sparring');self.act('path-clear',characterId='kaede');self.act('advance')
  report=self.s['personalPathDrills']['kaede'];self.assertIn('4 damage',report['rows'][0]['detail']);self.assertEqual(report['name'],'Guarded sparring')
  self.assertEqual(before,(g.character_sheet(self.s,'kaede')['earnedAdvancement'],f.vitality(self.s,'kaede'),self.s['materialInventory']))
  self.reject('path-drill',characterId='kaede',scenario='sparring')
 def test_retraining_keeps_personal_knowledge(self):
  self.prepare('kaede','measured-blow');g.award_advancement(self.s,'kaede','earned',2,'Evidence');self.s['characterSkills']['kaede']['athletics']=1
  self.act('start-retraining',characterId='kaede');self.act('advance');self.assertEqual(p.record(self.s,'kaede')['learned'],['measured-blow']);self.assertEqual(p.record(self.s,'kaede')['techniques'],['measured-blow'])
 def test_additive_upgrade_and_reload(self):
  old=deepcopy(self.s);p.view(self.s);self.assertEqual(self.s,old)
  self.act('path-train',characterId='sabine',talentId='read-the-lock');self.act('advance');snapshot=deepcopy(self.s);self.s=g.migrate_state(json.loads(json.dumps(self.s)));self.assertEqual(snapshot,self.s);self.act('advance');self.assertIn('read-the-lock',p.record(self.s,'sabine')['learned'])

if __name__=='__main__':unittest.main()
