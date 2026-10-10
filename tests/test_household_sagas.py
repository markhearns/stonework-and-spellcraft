from copy import deepcopy
from collections import Counter
from pathlib import Path
import json,sqlite3,tempfile,unittest,uuid
import game as g,household_sagas as saga,household_saga_content as c
import character_approaches as apt,character_quests as quests,relationships
import test_magic_overhaul as magic,test_household_chapters as household
from server import GameStore

class HouseholdSagaTests(unittest.TestCase):
 def setUp(self):
  self.s=magic.MagicTests.rich(self)
  for who in c.CODAS:
   if who not in g.household_members(self.s):household.HouseholdChapterTests.member(self,who)
  self.s['miraArchiveProject']['status']='complete'
  self.s['housingRooms']['garden-chamber']['status']='complete'
  for who in c.CODAS:
   self.s['soloLife']['agreements'][who]=['fieldwork'];self.s['bedroomAssignments'][who]='garden-chamber';g.set_character_assignment(self.s,who,'rest')
 def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
 def reject(self,kind,**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(before,self.s)
 def share(self,key,choice='method'):self.act('share-household-saga',storyId=key,choice=choice)
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def middle(self,key,mode='method'):
  self.share(key,mode);self.advance();self.share(key,mode)
 def finish(self,key,mode='method',project=True,workers=None):
  self.middle(key,mode)
  if project:self.act('fund-household-project',storyId=key,workers=workers or c.STORIES[key]['cast'][:2]);self.advance(2)
  else:self.act('gather-without-project',storyId=key);self.advance()
  self.share(key,mode)
 def test_all_fourteen_have_two_central_roles_and_all_72_choices_complete(self):
  counts=Counter(w for d in c.STORIES.values() for w in d['cast']);self.assertEqual(set(counts),set(c.CODAS));self.assertTrue(all(n>=2 for n in counts.values()));self.assertEqual(len(c.STORIES),12)
  initial=deepcopy(self.s)
  for key in c.STORIES:
   for mode in ('method','company'):
    self.s=deepcopy(initial);self.finish(key,mode)
    self.assertTrue(saga.completion(self.s,key));self.assertEqual(len(saga.saved(self.s)['memories']),3)
    self.assertEqual(saga.record(self.s,key)['project']['done'],2)
    self.reject('share-household-saga',storyId=key,choice=mode)
 def test_all_stories_have_a_zero_resource_friendship_completion(self):
  initial=deepcopy(self.s)
  for key in c.STORIES:
   self.s=deepcopy(initial);self.s['sharedFunds']=0;self.s['materialInventory']={k:0 for k in self.s['materialInventory']}
   self.finish(key,'company',False);self.assertTrue(saga.completion(self.s,key));self.assertIsNone(saga.record(self.s,key)['project']);self.assertEqual(self.s['sharedFunds'],0)
 def test_actual_cast_presence_phase_gates_and_no_time_from_conversation(self):
  before=(self.s['dayNumber'],self.s['currentDayPhase']);self.share('margins');self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase']))
  self.reject('share-household-saga',storyId='margins',choice='method');self.advance()
  self.s['additionalResidents']['neris']['status']='contacted';self.reject('share-household-saga',storyId='margins',choice='method')
 def test_choices_callbacks_only_actual_shared_crossovers(self):
  self.finish('margins','company',False);self.share('maps','method');self.advance()
  row=next(r for r in saga.views(self.s)['stories'] if r['id']=='maps')
  self.assertIn('Your earlier choice',row['scene']['callbacks'][0]);self.assertTrue(any('margins' in x for x in row['scene']['callbacks']))
  self.assertFalse(any('borrowed ribbon' in x for x in row['scene']['callbacks']))
  self.assertEqual(len(saga.context(self.s,'mira')['sharedStories']),4);self.assertEqual(saga.context(self.s,'zahra')['sharedStories'],[])
 def test_projects_use_only_actual_workers_and_exact_cost_once(self):
  self.middle('margins');funds=self.s['sharedFunds'];thread=self.s['materialInventory']['binding-thread']
  self.act('fund-household-project',storyId='margins',workers=['founder','mira']);self.assertEqual(self.s['sharedFunds'],funds-4);self.assertEqual(self.s['materialInventory']['binding-thread'],thread-1)
  self.assertEqual(g.character_assignment(self.s,'neris'),'rest');self.advance();self.act('pause-household-project',storyId='margins')
  self.advance(2);self.assertEqual(saga.record(self.s,'margins')['project']['done'],1)
  self.act('resume-household-project',storyId='margins');self.advance();self.assertEqual(self.s['sharedFunds'],funds-4)
  self.assertEqual(saga.teamwork(self.s,'founder','mira','scholarship'),'margins');self.assertIsNone(saga.teamwork(self.s,'founder','neris','scholarship'))
 def test_invalid_workers_reserves_and_busy_people_are_atomic(self):
  self.middle('margins')
  for workers in (None,[],['mira'],['mira','mira'],['mira','fenna'],['mira',{}]):self.reject('fund-household-project',storyId='margins',workers=workers)
  g.set_character_assignment(self.s,'mira','archive');self.reject('fund-household-project',storyId='margins',workers=['mira','neris']);g.set_character_assignment(self.s,'mira','rest')
  self.s['materialReserveTargets']['binding-thread']=self.s['materialInventory']['binding-thread'];self.reject('fund-household-project',storyId='margins',workers=['mira','neris'])
 def test_more_workers_no_extra_work_and_no_double_assignment(self):
  self.middle('fair');self.act('fund-household-project',storyId='fair',workers=['elowen','fenna','mira','iona']);self.advance();self.assertEqual(saga.record(self.s,'fair')['project']['done'],1)
  g.set_character_assignment(self.s,'iona','rest');self.advance();self.assertEqual(saga.record(self.s,'fair')['project']['done'],1)
  self.act('resume-household-project',storyId='fair');self.advance();self.assertEqual(saga.record(self.s,'fair')['project']['status'],'complete')
 def test_project_can_continue_while_founder_is_away(self):
  self.middle('margins');self.act('fund-household-project',storyId='margins',workers=['mira','neris'])
  self.act('start-expedition',siteId='old-waterworks');self.advance();self.act('choose-expedition-approach',approach='survey');self.advance();self.assertEqual(saga.record(self.s,'margins')['project']['status'],'complete')
  self.assertFalse(g.character_at_castle(self.s,'founder'))
 def test_one_active_project_and_later_funding_after_free_gathering(self):
  self.finish('margins',project=False);self.middle('maps');self.act('fund-household-project',storyId='maps',workers=['fenna','kaede'])
  self.reject('fund-household-project',storyId='margins',workers=['mira','neris']);self.act('pause-household-project',storyId='maps')
  self.act('fund-household-project',storyId='margins',workers=['mira','neris']);self.advance(2);self.assertTrue(saga.completion(self.s,'margins'))
 def test_advance_preview_is_read_only_and_reports_real_shared_work(self):
  import guidance
  self.middle('margins');self.act('fund-household-project',storyId='margins',workers=['mira','neris']);old=deepcopy(self.s)
  preview=guidance.preview(self.s);self.assertEqual(old,self.s);self.assertTrue(any(r['id']=='saga:margins' for r in preview['projects']))
 def test_party_bonus_is_bounded_and_requires_present_workers(self):
  self.finish('margins',workers=['founder','mira']);req=apt.spec('intelligence','scholarship')
  score=apt.score(self.s,'founder',req,['founder','mira']);self.assertIn('practised teamwork 1',score['detail'])
  self.assertNotIn('practised teamwork',apt.score(self.s,'founder',req,['founder','neris'])['detail'])
  self.assertNotIn('practised teamwork',apt.score(self.s,'founder',req)['detail'])
 def test_comfort_only_matching_companion_and_never_stacks(self):
  self.finish('margins','company',workers=['mira','neris']);q=quests.definition('mira');q['steps']=['cipher','search'];self.assertEqual(quests.methods(self.s,q)['patient']['phases'],2)
  self.assertEqual(quests.methods(self.s,q)['patient']['householdId'],'margins')
  q['who']='tamsin';self.assertEqual(quests.methods(self.s,q)['patient']['phases'],3)
  q['who']='mira';self.s['lanternAdventure'].update(discoveries=['survey'],legacy='archive',installed=True)
  self.assertEqual(quests.methods(self.s,q)['patient']['phases'],2)
 def test_companion_bonds_have_actual_events_without_player_romance(self):
  self.share('margins');net=saga.network(self.s);self.assertEqual(len(net),3)
  self.assertTrue(all('founder' not in b['participants'] for b in net));self.assertEqual(self.s['romance']['people'],{})
  for b in net:self.assertEqual(b['respect'],1);self.assertEqual(len(b['events']),1)
 def test_optional_codas_respect_real_romance_stage_pause_and_once_only(self):
  self.finish('margins',project=False);self.reject('share-saga-coda',characterId='mira',choice='flirt')
  for level in (1,2,3,4):
   s=deepcopy(self.s);self.s['romance']['people']['mira']={'level':level,'mode':'open','deferred':False}
   self.act('share-saga-coda',characterId='mira',choice='flirt');m=saga.saved(self.s)['codas']['mira'];self.assertEqual(m['relationshipLevel'],level)
   self.assertEqual(self.s['romance']['people']['mira']['level'],level);self.reject('share-saga-coda',characterId='mira',choice='flirt')
   if level==1:self.assertNotIn('kiss',m['response'])
   self.s=s
  self.s['romance']['people']['mira']={'level':4,'mode':'friendly','deferred':False};self.reject('share-saga-coda',characterId='mira',choice='quiet')
 def test_field_conversation_requires_real_party_and_does_not_solve_obstacle(self):
  self.finish('fair',project=False);self.act('start-expedition',siteId='lantern-pavilion',companionIds=['mira','tamsin','iona'])
  row=next(r for r in saga.field_rows(self.s) if r['storyId']=='fair');self.assertEqual(row['participants'],['founder','mira','iona'])
  self.assertNotIn('Elowen:',row['opening']);before=deepcopy(self.s['expedition'])
  self.act('share-saga-field',sceneId=row['id']);self.assertEqual(self.s['expedition'],before);self.reject('share-saga-field',sceneId=row['id'])
  self.assertEqual(saga.context(self.s,'elowen')['fieldMemories'],[])
 def test_all_fourteen_can_recall_their_story_on_a_real_two_person_expedition(self):
  initial=deepcopy(self.s)
  for who in c.CODAS:
   self.s=deepcopy(initial);key=next(k for k,d in c.STORIES.items() if who in d['cast'])
   self.finish(key,project=False);self.act('start-expedition',siteId='old-waterworks',companionId=who)
   row=next(r for r in saga.field_rows(self.s) if r['storyId']==key);self.assertEqual(row['participants'],['founder',who])
   self.act('share-saga-field',sceneId=row['id']);self.assertEqual(self.s['expedition']['stage'],'outbound')
 def test_finite_deferral_read_purity_and_migration(self):
  self.act('defer-household-saga',storyId='margins');self.advance(6);self.assertIn('margins',saga.saved(self.s)['deferred']);self.act('restore-household-saga',storyId='margins')
  old=deepcopy(self.s);saga.views(self.s);self.assertEqual(old,self.s)
  self.s['schemaVersion']=55;self.s.pop('householdSagas');funds=self.s['sharedFunds'];g.migrate_state(self.s);self.assertEqual(self.s['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertEqual(self.s['sharedFunds'],funds);self.assertEqual(saga.saved(self.s)['memories'],{})
 def test_save_backup_request_id_and_reload(self):
  with tempfile.TemporaryDirectory() as folder:
   st=GameStore(folder);old=deepcopy(self.s);old['schemaVersion']=55;old.pop('householdSagas')
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
   st=GameStore(folder);self.assertTrue(Path(folder,f'campaign-before-schema-55-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
   payload={'requestId':str(uuid.uuid4()),'expectedRevision':st.read()['revision'],'action':{'type':'share-household-saga','storyId':'margins','choice':'method'}}
   first=st.action(payload);self.assertEqual(st.action(payload),first);self.assertEqual(GameStore(folder).read()['householdSagas']['stories']['margins']['stage'],1)
