from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import game as g
import romance as r
import romance_content as c
import relationships as bonds
import outfit_progression as outfits
import character_quests as quests
import test_household_chapters as household
import test_magic_overhaul as magic
from server import GameStore

class RomanceTests(unittest.TestCase):
 def setUp(self):self.s=magic.MagicTests.rich(self)
 def act(self,kind,who='mira',**kw):g.apply_action(self.s,dict(type=kind,characterId=who,**kw))
 def ready(self,who='mira'):
  household.HouseholdChapterTests.member(self,who)
  for i in range(8):self.s['socialLife']['memories'][who+':fixture:'+str(i)]={'participants':[who],'title':'Shared fixture','sequence':i}
  bonds.saved(self.s)['bonds'][bonds.pair_id('founder',who)]={'participants':['founder',who],'trust':6,'affection':6,'respect':4}
 def share(self,index,who='mira'):self.act('share-romance',who,index=index,choice='romantic')
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def advance(self):self.act('advance')
 def test_all_56_scenes_progress_only_by_mutual_choice_and_preserve_resources(self):
  for who in c.SCENES:
   self.setUp();self.ready(who)
   for index in range(4):
    before={k:deepcopy(v) for k,v in self.s.items() if k not in ('romance','relationships','journal')}
    self.share(index,who);self.assertEqual(before,{k:self.s[k] for k in before})
    self.assertEqual(r.level(self.s,who),index+1);self.assertEqual(r.saved(self.s)['memories'][f'{who}:{index}']['response'],c.SCENES[who][index][2])
    self.advance()
   self.assertEqual(len(r.context(self.s,who)['milestones']),4)
   self.reject('share-romance',who=who,index=3,choice='romantic')
 def test_distinct_content_for_all_characters(self):
  rows=[row for scenes in c.SCENES.values() for row in scenes]
  self.assertEqual(len(rows),64)
  for column in range(3):self.assertEqual(len({row[column] for row in rows}),64)
 def test_scores_alone_never_establish_romance_and_views_are_pure(self):
  self.ready();old=deepcopy(self.s);v=r.views(self.s);self.assertEqual(old,self.s);self.assertEqual(r.level(self.s,'mira'),0)
  self.assertTrue(v['mira']['scenes'][0]['available']);self.assertFalse(v['mira']['scenes'][1]['available'])
  self.assertNotIn(c.SCENES['mira'][1][2],json.dumps(v));self.assertEqual(v['mira']['scenes'][1]['opening'],'')
 def test_each_requirement_and_phase_gate_are_authoritative(self):
  self.reject('share-romance',index=0,choice='romantic');self.ready();bond=bonds.saved(self.s)['bonds']['founder|mira']
  for dimension in ('trust','affection'):
   before=bond[dimension];bond[dimension]=0;self.reject('share-romance',index=0,choice='romantic');bond[dimension]=before
  self.share(0);self.reject('share-romance',index=1,choice='romantic');self.advance()
  bond['respect']=0;self.reject('share-romance',index=1,choice='romantic');bond['respect']=1;self.share(1)
 def test_friendly_choice_and_pause_do_not_lose_points_or_fabricate_a_milestone(self):
  self.ready();before=deepcopy(bonds.saved(self.s));self.act('share-romance',index=0,choice='friendly')
  self.assertEqual(before,bonds.saved(self.s));self.assertEqual(r.level(self.s,'mira'),0);self.assertFalse(r.view(self.s,'mira')['scenes'][0]['available'])
  self.act('reopen-romance');self.assertEqual(r.level(self.s,'mira'),0);self.share(0)
  self.act('pause-romance');self.assertEqual(r.level(self.s,'mira'),0);self.assertEqual(r.person(self.s,'mira')['level'],1)
  self.act('reopen-romance');self.assertEqual(r.level(self.s,'mira'),1)
 def test_defer_restore_no_deadline_no_points(self):
  self.ready();old=deepcopy(bonds.saved(self.s));self.act('defer-romance');self.s['dayNumber']+=100
  self.assertTrue(r.view(self.s,'mira')['scenes'][0]['deferred']);self.act('restore-romance');self.assertEqual(old,bonds.saved(self.s));self.share(0)
 def test_absence_invalid_payloads_and_retries_are_atomic(self):
  self.ready()
  with patch('game.character_at_castle',return_value=False):self.reject('share-romance',index=0,choice='romantic')
  for kwargs in ({'index':True,'choice':'romantic'},{'index':4,'choice':'romantic'},{'index':0,'choice':[]},{'who':[],'index':0,'choice':'romantic'},{'who':'eris','index':0,'choice':'romantic'}):self.reject('share-romance',**kwargs)
 def test_all_42_room_dates_require_mutual_dating_and_real_room_then_remember_once(self):
  for who in c.SCENES:
   self.setUp();self.ready(who)
   for room in c.DATES:self.reject('share-romantic-date',who=who,roomId=room,choice='romantic')
   self.share(0,who);self.advance();self.share(1,who)
   for room in c.DATES:
    self.s['headquarters']['rooms'][room]='not-started';self.reject('share-romantic-date',who=who,roomId=room,choice='romantic');self.s['headquarters']['rooms'][room]='complete'
    oldday=self.s['dayNumber'];self.act('share-romantic-date',who,roomId=room,choice='romantic');self.assertEqual(self.s['dayNumber'],oldday)
    self.reject('share-romantic-date',who=who,roomId=room,choice='romantic')
   self.assertEqual(len(r.context(self.s,who)['dates']),3)
 def test_friendly_date_does_not_advance_milestones(self):
  self.ready();self.share(0);self.advance();self.share(1);self.act('share-romantic-date',roomId='pool',choice='friendly')
  self.assertEqual(r.level(self.s,'mira'),2);self.assertIn('quiet conversation',r.saved(self.s)['dates']['mira:pool']['response'])
 def test_wardrobe_uses_quest_relationship_and_participation_history_without_generating_it(self):
  self.assertEqual(outfits.memories(self.s,'mira'),[])
  self.act('talk-character-quest',questId='personal:mira',choice='warm')
  self.assertIn('quest:personal:mira:offered',outfits.memories(self.s,'mira'));self.assertFalse(outfits.blockers(self.s,'mira','2'))
  self.s['relationships']['memories']['actual']={'participants':['founder','mira']}
  self.s['companionParticipation']['memories']['actual']={'participants':['founder','mira']}
  self.assertIn('relationship:actual',outfits.memories(self.s,'mira'));self.assertIn('participation:actual',outfits.memories(self.s,'mira'))
  self.assertNotIn('relationship:actual',outfits.memories(self.s,'tamsin'))
 def test_repeated_generated_template_cannot_farm_wardrobe_evidence(self):
  self.act('generate-character-quests');records=quests.saved(self.s)['records']
  a=records['request:1'];b=records['request:2'];b['who']=a['who'];b['template']=a['template']
  a['memories']=[{'stage':'offered'}];first=outfits.memories(self.s,a['who']);b['memories']=[{'stage':'offered'}]
  self.assertEqual(first,outfits.memories(self.s,a['who']))
 def test_greetings_and_quest_replies_follow_actual_milestones_and_pause(self):
  self.ready();self.assertEqual(r.greeting(self.s,'mira','ordinary'),'ordinary');self.assertEqual(r.quest_reply(self.s,'mira','original'),'original')
  self.share(0);self.assertIn('better chair',r.greeting(self.s,'mira'));self.assertIn('acknowledged',r.quest_reply(self.s,'mira','original'))
  self.advance();self.share(1);self.assertIn('first date',r.quest_reply(self.s,'mira','original'))
  self.act('pause-romance');self.assertEqual(r.greeting(self.s,'mira','ordinary'),'ordinary');self.assertIn('friendly',r.quest_reply(self.s,'mira','original'))
 def test_outfit_choice_is_explicit_and_memory_preserves_what_was_worn(self):
  self.ready();self.act('accept-outfit-invitation',tier='2');self.act('choose-outfit',tier='2');self.share(0)
  self.assertEqual(r.saved(self.s)['memories']['mira:0']['outfitId'],'mira-outfit-2');self.act('choose-outfit',tier=None)
  self.assertEqual(r.saved(self.s)['memories']['mira:0']['outfitId'],'mira-outfit-2')
 def test_dialogue_context_does_not_include_other_people_or_future_scenes(self):
  self.ready();self.share(0);context=r.context(self.s,'mira');self.assertEqual(len(context['milestones']),1);self.assertEqual(r.context(self.s,'tamsin')['milestones'],[])
  self.assertNotIn(c.SCENES['mira'][1][2],json.dumps(context));context['milestones'][0]['response']='changed';self.assertNotEqual(r.saved(self.s)['memories']['mira:0']['response'],'changed')
 def test_migration_preserves_existing_outfits_and_never_invents_romance(self):
  self.ready();self.act('accept-outfit-invitation',tier='2');self.act('choose-outfit',tier='2');self.s.pop('romance');self.s['schemaVersion']=52;old=deepcopy(self.s)
  with tempfile.TemporaryDirectory() as directory:
   st=GameStore(directory)
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   st=GameStore(directory);s=st.read();self.assertEqual(s['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertTrue(Path(directory,f'campaign-before-schema-52-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
   self.assertEqual(r.saved(s)['memories'],{});self.assertEqual(s['outfitProgression'],old['outfitProgression'])
   req={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':{'type':'share-romance','characterId':'mira','index':0,'choice':'romantic'}}
   after=st.action(req);self.assertEqual(st.action(req),after);self.assertEqual(GameStore(directory).read(),after)
