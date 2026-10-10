from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from unittest.mock import patch
import game as g,romance as r,intimacy as i,intimacy_content as c,armoury
from server import GameStore
import test_household_chapters as home_tests
import test_magic_overhaul as magic_tests

class IntimacyTests(unittest.TestCase):
 def setUp(self):self.s=magic_tests.MagicTests.rich(self);self.ready('mira')
 def ready(self,who):
  home_tests.HouseholdChapterTests.member(self,who);home_tests.HouseholdChapterTests.room(self,__import__('signature_equipment').ROOMS[who])
  self.s['housingRooms']['west-chamber']['status']='complete';self.s['bedroomAssignments'][who]='west-chamber'
  armoury.sync(self.s);r.initialize(self.s);r.saved(self.s)['people'][who]={'level':4,'mode':'open','deferred':False}
  for w in ('founder',who):g.set_character_assignment(self.s,w,'rest')
 def act(self,kind,who='mira',**kw):g.apply_action(self.s,dict(type=kind,characterId=who,**kw))
 def begin(self,stage=0,kind='moment',who='mira'):self.act('intimacy-begin',who,stage=stage,sceneKind=kind)
 def close(self,who='mira',choice='close'):self.act('intimacy-resolve',who,choice=choice)
 def later(self,night=False):
  self.s['dayNumber']+=1;self.s['currentDayPhase']='evening' if night else 'afternoon'
 def reject(self,kind,who='mira',**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,who,**kw)
  self.assertEqual(before,self.s)
 def finish(self,stage,who='mira'):
  self.later(stage==3);self.begin(stage,who=who);self.close(who);self.later(stage==3);self.begin(stage,'milestone',who);self.close(who)
 def test_all_128_scenes_are_distinct_and_resolve_for_all_sixteen_adults(self):
  self.assertEqual(set(c.ROWS),set(r.content.SCENES))
  rows=[row for scenes in c.ROWS.values() for row in scenes]
  self.assertEqual(len(rows),64)
  for col in range(6):self.assertEqual(len(set(row[col] for row in rows)),64)
  for who in c.ROWS:
   with self.subTest(who=who):
    self.setUp();self.ready(who)
    for stage in range(4):
     self.finish(stage,who)
     self.assertEqual(i.person(self.s,who)['milestones'][str(stage)]['response'],c.ROWS[who][stage][5])
    self.assertEqual(len(i.person(self.s,who)['milestones']),4)
 def test_replay_retains_first_memory_varies_intro_and_cannot_farm_progress(self):
  self.begin();self.close();first=deepcopy(i.person(self.s,'mira')['moments']['0']['first']);journal=len(self.s['journal'])
  self.reject('intimacy-begin',stage=0,sceneKind='moment')
  for _ in range(8):
   self.later();before={k:deepcopy(v) for k,v in self.s.items() if k!='intimacy'};self.begin();self.close()
   self.assertEqual(before,{k:self.s[k] for k in before})
  p=i.person(self.s,'mira');self.assertEqual(p['moments']['0']['count'],9);self.assertEqual(first,p['moments']['0']['first']);self.assertEqual(journal,len(self.s['journal']));self.assertFalse(p['milestones'])
 def test_no_changes_to_time_work_economy_builds_food_or_bonds(self):
  for stage in range(4):
   self.later(stage==3)
   for kind in ('moment','milestone'):
    before={k:deepcopy(v) for k,v in self.s.items() if k not in ('intimacy','journal')}
    self.begin(stage,kind);self.close();self.assertEqual(before,{k:self.s[k] for k in before});self.later(stage==3)
 def test_gates_prior_caps_relationship_level_phases_days_and_duplicate_endings(self):
  self.reject('intimacy-begin',stage=1,sceneKind='moment');self.reject('intimacy-begin',stage=0,sceneKind='milestone')
  self.begin();self.close();self.reject('intimacy-begin',stage=0,sceneKind='milestone');self.later();self.begin(0,'milestone');self.close()
  self.later();r.saved(self.s)['people']['mira']['level']=1;self.reject('intimacy-begin',stage=1,sceneKind='moment');r.saved(self.s)['people']['mira']['level']=4
  self.begin(1);self.close();self.later();self.s['currentDayPhase']='morning';self.begin(1,'milestone');self.close();self.s['currentDayPhase']='afternoon'
  self.reject('intimacy-begin',stage=1,sceneKind='milestone')
  self.begin(2);self.close();self.s['currentDayPhase']='evening';self.reject('intimacy-begin',stage=2,sceneKind='milestone')
 def test_quiet_company_and_leaving_do_not_spend_phase_or_complete_stage(self):
  old=deepcopy(self.s['relationships']);self.begin();self.close(choice='quiet')
  p=i.person(self.s,'mira');self.assertEqual(p['latest']['choice'],'quiet');self.assertIsNone(p['lastStamp']);self.assertFalse(p['moments']);self.assertFalse(p['milestones'])
  self.begin();self.close(choice='leave');self.assertIsNone(i.person(self.s,'mira')['pending']);self.assertEqual(old,self.s['relationships'])
 def test_pause_clears_pending_preserves_memories_and_reopen_requires_fresh_choice(self):
  self.finish(0);before=deepcopy(i.person(self.s,'mira')['milestones']);self.later();self.begin();self.act('pause-romance')
  self.assertIsNone(i.person(self.s,'mira')['pending']);self.reject('intimacy-begin',stage=0,sceneKind='moment');self.act('reopen-romance')
  self.assertEqual(before,i.person(self.s,'mira')['milestones']);self.reject('intimacy-resolve',choice='close');self.begin();self.close()
 def test_defer_has_no_expiry_or_penalty_and_does_not_accept_anything(self):
  self.begin();self.act('intimacy-defer');self.s['dayNumber']+=1000;self.reject('intimacy-begin',stage=0,sceneKind='moment');self.act('intimacy-restore');self.assertFalse(i.person(self.s,'mira')['moments']);self.begin()
 def test_adulthood_presence_and_invalid_payloads_are_authoritative_and_atomic(self):
  for who in ('founder','mira'):
   old=self.s['people'][who]['adultAgeYears'];self.s['people'][who]['adultAgeYears']=17;self.reject('intimacy-begin',stage=0,sceneKind='moment');self.s['people'][who]['adultAgeYears']=old
  with patch('game.character_at_castle',return_value=False):self.reject('intimacy-begin',stage=0,sceneKind='moment')
  for kw in ({'stage':True,'sceneKind':'moment'},{'stage':4,'sceneKind':'moment'},{'stage':0,'sceneKind':[]},{'who':[],'stage':0,'sceneKind':'moment'},{'who':'fenna','stage':0,'sceneKind':'moment'}):self.reject('intimacy-begin',**kw)
  self.begin();self.reject('intimacy-resolve',choice=[]);self.reject('intimacy-resolve',choice='anything');self.close(choice='leave')
 def test_private_evening_requires_rest_evening_and_real_unshared_accommodation(self):
  for stage in range(3):self.finish(stage)
  self.later();self.reject('intimacy-begin',stage=3,sceneKind='moment');self.s['currentDayPhase']='evening';g.set_character_assignment(self.s,'founder','commissions');self.reject('intimacy-begin',stage=3,sceneKind='moment');g.set_character_assignment(self.s,'founder','rest')
  self.ready('tamsin');self.s['bedroomAssignments']['tamsin']='west-chamber';self.s['bedroomAssignments']['mira']='bedchamber';self.s['bedroomAssignments']['tamsin']='bedchamber';self.reject('intimacy-begin',stage=3,sceneKind='moment')
  self.s['bedroomAssignments']['mira']='west-chamber';self.begin(3);self.assertEqual(i.person(self.s,'mira')['pending']['roomId'],'west-chamber');self.close()
 def test_pending_revalidates_changed_space_and_can_always_be_left(self):
  for stage in range(3):self.finish(stage)
  self.later(True);self.begin(3);self.s['bedroomAssignments']['mira']='bedchamber';self.reject('intimacy-resolve',choice='close');self.close(choice='leave');self.begin(3);self.close()
 def test_unseen_endings_are_hidden_and_views_do_not_mutate(self):
  old=deepcopy(self.s);v=i.view(self.s,'mira');self.assertEqual(old,self.s)
  for row in c.ROWS['mira']:
   for col in (1,2,4,5):self.assertNotIn(row[col],json.dumps(v,ensure_ascii=False))
  self.begin();v=i.view(self.s,'mira');self.assertEqual(v['pending']['opening'],c.ROWS['mira'][0][1]);self.assertNotIn(c.ROWS['mira'][0][2],json.dumps(v,ensure_ascii=False))
 def test_pending_and_replays_survive_sqlite_reload_with_request_idempotency(self):
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory)
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   def api(action):return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'characterId':'mira',**action}})
   api({'type':'intimacy-begin','stage':0,'sceneKind':'moment'});store=GameStore(directory);self.assertIsNotNone(i.person(store.read(),'mira')['pending'])
   request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'intimacy-resolve','characterId':'mira','choice':'close'}}
   first=store.action(request);self.assertEqual(first,store.action(request));self.assertEqual(i.person(GameStore(directory).read(),'mira')['moments']['0']['count'],1)
 def test_actual_romance_milestone_does_not_unlock_closeness_in_same_phase(self):
  from test_romance import RomanceTests
  t=RomanceTests();t.setUp();t.ready();self.s=t.s
  self.act('share-romance',index=0,choice='romantic');self.reject('intimacy-begin',stage=0,sceneKind='moment');self.act('advance');self.begin();self.close()
 def test_optional_state_is_lazy_and_old_save_is_unchanged(self):
  s=g.new_campaign();old=deepcopy(s);i.view(s,'mira');self.assertEqual(old,s);self.assertNotIn('intimacy',s);self.assertEqual(g.migrate_state(json.loads(json.dumps(s))),s)

if __name__=='__main__':unittest.main()
