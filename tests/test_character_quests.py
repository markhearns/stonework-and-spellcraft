from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import game as g
import character_quests as q
import character_quest_content as c
import relationships
import test_magic_overhaul as magic
import test_household_chapters as household
from server import GameStore

class CharacterQuestTests(unittest.TestCase):
 def setUp(self):self.s=magic.MagicTests.rich(self)
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def talk(self,key,choice='warm'):self.act('talk-character-quest',questId=key,choice=choice)
 def method(self,key,method='patient'):
  self.act('choose-quest-method',questId=key,methodId=method)
  while q.saved(self.s)['records'][key]['status']=='working':self.advance()
 def finish(self,key,choice='warm'):
  self.talk(key,choice);self.method(key);self.talk(key,choice);self.method(key);self.talk(key,choice)
 def test_all_fourteen_personal_quests_all_tones_complete_with_equal_rewards(self):
  for who in c.PERSONAL:
   for tone in ('flirt','warm','practical'):
    with self.subTest(who=who,tone=tone):
     self.setUp();household.HouseholdChapterTests.member(self,who)
     for p in ('founder',who):self.s['characterBuilds'][p]['attributes']={k:1 for k in g.character_builds.ATTRIBUTES}
     key='personal:'+who;self.finish(key,tone);quest=q.saved(self.s)['records'][key]
     self.assertEqual(quest['status'],'complete');self.assertEqual(len(quest['outcomes']),2);self.assertEqual(len(quest['memories']),3)
     self.assertIn('You remember choosing',quest['memories'][-1]['response'])
     for p in ('founder',who):self.assertEqual(self.s['characterDevelopment'][p]['advancementAwards']['character-quest:'+key]['points'],2)
     self.assertEqual(len(q.view(self.s)['keepsakes']),1)
     self.reject('talk-character-quest',questId=key,choice=tone)
 def test_reading_is_pure_and_hides_future_replies(self):
  old=deepcopy(self.s);view=q.view(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
  row=next(r for r in view['quests'] if r['who']=='mira')
  self.assertNotIn(c.PERSONAL['mira'][7],json.dumps(row));self.assertNotIn(c.PERSONAL['mira'][5],json.dumps(row));self.assertEqual(q.saved(self.s)['records'],{})
 def test_accepting_and_talking_do_not_advance_or_assign_work(self):
  before={k:deepcopy(v) for k,v in self.s.items() if k not in ('characterQuests','journal')}
  self.talk('personal:mira','flirt');self.assertEqual(before,{k:self.s[k] for k in before})
  self.assertIn('No attribute or spell required',q.methods(self.s,q.active(self.s))['patient']['detail'])
 def test_work_requires_both_free_and_does_not_replace_assignments(self):
  self.talk('personal:mira');g.set_character_assignment(self.s,'mira','archive')
  self.reject('choose-quest-method',questId='personal:mira',methodId='patient')
  g.set_character_assignment(self.s,'mira','rest');self.act('choose-quest-method',questId='personal:mira',methodId='patient')
  self.assertEqual(g.character_assignment(self.s,'founder'),q.ASSIGNMENT)
  self.assertEqual(g.character_assignment(self.s,'mira'),q.ASSIGNMENT)
  self.assertTrue(any('quest work +1' in line for line in g.phase_forecast(self.s)))
  g.set_character_assignment(self.s,'mira','rest');self.advance();self.assertEqual(q.active(self.s)['pending']['remaining'],3)
  self.act('resume-character-quest',questId='personal:mira');self.advance();self.assertEqual(q.active(self.s)['pending']['remaining'],2)
 def test_no_rest_healing_or_research_double_work_in_quest_phase(self):
  self.s['fieldMagic']['vitality']['founder']=2;self.s['researchStatus']='in-progress';self.s['researchCompletedPhases']=0
  self.talk('personal:mira');self.act('choose-quest-method',questId='personal:mira',methodId='patient');self.advance()
  self.assertEqual(self.s['fieldMagic']['vitality']['founder'],2);self.assertEqual(self.s['researchCompletedPhases'],0)
 def test_all_seven_magic_routes_actual_owner_principles_and_exact_payment(self):
  for step,d in c.OBSTACLES.items():
   with self.subTest(step=step):
    self.setUp();spell=magic.MagicTests.learned(self,d['spell'],'mira');self.talk('personal:mira');quest=q.active(self.s);quest['steps'][0]=step
    before=deepcopy(self.s['materialInventory']);self.act('choose-quest-method',questId=quest['id'],methodId='spell')
    self.assertEqual(quest['pending']['actor'],'mira');self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1)
    for material,n in g.SPELL_FORMS[d['spell']]['castingInputs'].items():self.assertEqual(self.s['materialInventory'][material],before[material]-n)
    self.advance();self.assertEqual(quest['status'],'interlude');self.assertEqual(quest['outcomes'][0]['spellId'],spell)
 def test_missing_preparation_principles_supplies_and_invalid_inputs_are_atomic(self):
  self.talk('personal:mira');self.reject('choose-quest-method',questId='personal:mira',methodId='spell')
  spell=magic.MagicTests.learned(self,'lucid-sight');self.s['founderKnownPrinciples'].remove('clear-instruction')
  self.reject('choose-quest-method',questId='personal:mira',methodId='spell');g.learn_for_character(self.s,'founder','clear-instruction')
  self.s['materialInventory']['moon-glass']=0;self.reject('choose-quest-method',questId='personal:mira',methodId='spell')
  for fields in ({'questId':[],'methodId':'patient'},{'questId':'personal:mira','methodId':[]},{'questId':'personal:mira','methodId':'invented'}):self.reject('choose-quest-method',**fields)
  self.reject('talk-character-quest',questId='personal:mira',choice=[])
 def test_paid_method_survives_pause_reload_and_resume_without_recharge(self):
  spell=magic.MagicTests.learned(self,'lucid-sight');self.talk('personal:mira');self.act('choose-quest-method',questId='personal:mira',methodId='spell')
  before=deepcopy(self.s['materialInventory']);self.act('pause-character-quest',questId='personal:mira');self.advance();self.s=json.loads(json.dumps(self.s))
  self.assertIsNone(q.active(self.s));self.act('resume-character-quest',questId='personal:mira');self.advance()
  self.assertEqual(self.s['materialInventory']['moon-glass'],before['moon-glass']);self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1)
 def test_skill_routes_and_companion_help_do_not_remove_patient_method(self):
  self.talk('personal:mira')
  for step,d in c.OBSTACLES.items():
   q.active(self.s)['steps'][0]=step
   for who in ('founder','mira'):
    self.s['characterBuilds'][who]['attributes']={k:1 for k in g.character_builds.ATTRIBUTES};self.s['characterSkills'][who]={k:0 for k in g.CHARACTER_SKILLS}
   methods=q.methods(self.s,q.active(self.s));self.assertFalse(methods['patient']['blockers']);self.assertTrue(methods['skilled']['blockers'])
   self.s['characterBuilds']['mira']['attributes'][d['attribute']]=9
   self.assertFalse(q.methods(self.s,q.active(self.s))['skilled']['blockers'])
 def test_board_is_deterministic_saved_nonexpiring_and_bounded(self):
  other=deepcopy(self.s);self.act('generate-character-quests');g.apply_action(other,{'type':'generate-character-quests'})
  self.assertEqual(q.saved(self.s),q.saved(other));self.assertEqual(len(q.saved(self.s)['records']),3)
  self.reject('generate-character-quests');first=deepcopy(q.saved(self.s)['records']);self.s['dayNumber']+=100
  self.reject('generate-character-quests');self.assertEqual(first,q.saved(self.s)['records'])
  self.act('decline-character-quest',questId='request:1');self.act('generate-character-quests')
  self.assertEqual(q.saved(self.s)['serial'],4);self.assertEqual(q.saved(self.s)['records']['request:2'],first['request:2'])
 def test_every_dynamic_template_can_finish_and_rewards_once(self):
  seen=set()
  for day in range(1,25):
   self.setUp();self.s['dayNumber']=day;self.act('generate-character-quests')
   for key,quest in list(q.saved(self.s)['records'].items()):
    if quest['template'] in seen:continue
    self.finish(key,'practical');seen.add(quest['template'])
    before=self.s['materialInventory']['binding-thread'];self.reject('talk-character-quest',questId=key,choice='flirt');self.assertEqual(before,self.s['materialInventory']['binding-thread'])
    self.assertFalse(any(k.startswith('character-quest:request') for k in self.s['characterDevelopment']['founder']['advancementAwards']))
   if len(seen)==len(c.TEMPLATES):break
  self.assertEqual(len(seen),6)
 def test_other_quests_wait_and_absence_pauses_without_progress(self):
  household.HouseholdChapterTests.member(self,'tamsin');self.talk('personal:mira')
  self.reject('talk-character-quest',questId='personal:tamsin',choice='warm');self.act('choose-quest-method',questId='personal:mira',methodId='patient')
  with patch('game.character_at_castle',side_effect=lambda s,p:p!='mira'):
   q.resolve(self.s,[],True);self.assertEqual(q.active(self.s)['pending']['remaining'],3)
  self.act('pause-character-quest',questId='personal:mira');self.talk('personal:tamsin');self.assertEqual(q.active(self.s)['who'],'tamsin')
 def test_context_includes_only_actual_shared_scenes(self):
  self.talk('personal:mira','flirt');context=q.context(self.s,'mira');self.assertEqual(q.context(self.s,'tamsin'),[])
  self.assertNotIn(c.PERSONAL['mira'][6],json.dumps(context));self.assertEqual(len(context[0]['memories']),1)
  context[0]['memories'][0]['response']='changed';self.assertNotEqual(q.active(self.s)['memories'][0]['response'],'changed')
 def test_migration_store_backup_idempotency_and_reload(self):
  self.s.pop('characterQuests');self.s['schemaVersion']=51;before=deepcopy(self.s)
  with tempfile.TemporaryDirectory() as directory:
   st=GameStore(directory)
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   st=GameStore(directory);state=st.read();self.assertEqual(state['schemaVersion'],66)
   self.assertTrue(Path(directory,'campaign-before-schema-51-to-66.sqlite3').exists())
   for k,v in before.items():
    if k not in ('schemaVersion','revision'):self.assertEqual(state[k],v)
   req={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'talk-character-quest','questId':'personal:mira','choice':'flirt'}}
   after=st.action(req);self.assertEqual(st.action(req),after);self.assertEqual(GameStore(directory).read(),after)

 def test_active_rituals_shorten_matching_ordinary_methods_only(self):
  self.talk('personal:mira')
  for step,ritual in c.QUEST_RITUALS.items():
   q.active(self.s)['steps'][0]=step;self.s['lastingRituals']['completed']={}
   self.assertEqual(q.methods(self.s,q.active(self.s))['patient']['phases'],3)
   self.s['lastingRituals']['completed'][ritual]={'active':True}
   method=q.methods(self.s,q.active(self.s))['patient'];self.assertEqual(method['phases'],2);self.assertEqual(method['cost'],{})
   self.assertEqual(q.methods(self.s,q.active(self.s))['spell']['phases'],1)
 def test_ritual_duration_is_saved_and_suspension_does_not_rewrite_paid_work(self):
  self.talk('personal:mira');self.s['lastingRituals']['completed']['archive-circle']={'active':True}
  self.act('choose-quest-method',questId='personal:mira',methodId='patient');self.s['lastingRituals']['completed']['archive-circle']['active']=False
  self.act('pause-character-quest',questId='personal:mira');self.s=json.loads(json.dumps(self.s));self.act('resume-character-quest',questId='personal:mira')
  self.advance(2);self.assertEqual(q.active(self.s)['status'],'interlude');self.assertEqual(q.active(self.s)['outcomes'][0]['ritualId'],'archive-circle')
 def test_repeated_procedural_type_has_material_rewards_but_no_relationship_farming(self):
  self.act('generate-character-quests');data=q.saved(self.s)
  data['records']['request:2']['who']=data['records']['request:1']['who']
  data['records']['request:2']['template']=data['records']['request:1']['template']
  self.finish('request:1');before=deepcopy(relationships.saved(self.s));thread=self.s['materialInventory']['binding-thread']
  self.finish('request:2');self.assertEqual(relationships.saved(self.s),before);self.assertEqual(self.s['materialInventory']['binding-thread'],thread+2)
