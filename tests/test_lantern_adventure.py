from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
import game as g
import lantern_adventure as l
import lantern_content as c
import character_quests as quests
import romance
import test_magic_overhaul as magic
import test_household_chapters as household
from server import GameStore

class LanternAdventureTests(unittest.TestCase):
 def setUp(self):
  self.s=magic.MagicTests.rich(self);self.s['miraArchiveProject']['status']='complete'
  for who in ('tamsin','iona'):
   household.HouseholdChapterTests.member(self,who);self.s['soloLife']['agreements'][who]=['fieldwork']
  self.s['housingRooms']['garden-chamber']['status']='complete';self.s['bedroomAssignments']['tamsin']='garden-chamber';self.s['bedroomAssignments']['iona']='garden-chamber'
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def start(self,party=()):
  self.act('start-expedition',siteId=l.SITE,companionIds=list(party));self.advance();self.act('choose-expedition-approach',approach='survey')
 def maxed(self):
  for who in ('founder',*c.CAST):
   self.s['characterBuilds'][who]['attributes']={k:10 for k in g.character_builds.ATTRIBUTES};self.s['characterSkills'][who]={k:2 for k in g.CHARACTER_SKILLS}
 def method(self,key):
  self.act('choose-encounter-method',methodId=key)
  while self.s['expedition']['stage']=='working':self.advance()
 def finish(self,legacy='archive'):
  for _ in c.STEPS[:-1]:self.method('patient')
  self.method(legacy);self.act('return-expedition');self.advance()
 def test_minimum_solo_completes_all_three_legacies_without_supplies(self):
  for legacy in c.PURPOSES:
   self.setUp();self.s['characterBuilds']['founder']['attributes']={k:1 for k in g.character_builds.ATTRIBUTES};self.start()
   before=deepcopy(self.s['materialInventory']);self.finish(legacy)
   self.assertEqual(l.saved(self.s)['discoveries'],['survey']);self.assertEqual(l.saved(self.s)['legacy'],legacy)
   self.assertEqual(self.s['materialInventory']['moon-glass'],before['moon-glass']+2);self.assertEqual(l.saved(self.s)['returners'],['founder'])
   self.assertNotIn(l.SITE,self.s['characterDevelopment']['mira']['advancementAwards']);self.reject('start-expedition',siteId=l.SITE)
 def test_three_companions_are_actually_away_and_all_return_with_personal_credit(self):
  self.start(c.CAST)
  self.assertEqual(g.expedition_party(self.s),['founder',*c.CAST])
  for who in c.CAST:self.assertFalse(g.character_at_castle(self.s,who));self.assertEqual(g.character_assignment(self.s,who),'expedition')
  self.finish('music');self.assertEqual(self.s['lastExpeditionReport']['participants'],['founder',*c.CAST])
  for who in ('founder',*c.CAST):
   self.assertTrue(g.character_at_castle(self.s,who));self.assertEqual(g.character_assignment(self.s,who),'rest');self.assertEqual(self.s['characterDevelopment'][who]['advancementAwards'][l.SITE]['points'],3)
 def test_invalid_and_unwilling_parties_are_atomic(self):
  for party in (None,'mira',[[]],['mira','mira'],['eris'],['mira','tamsin','iona','founder']):self.reject('start-expedition',siteId=l.SITE,companionIds=party)
  self.s['soloLife']['agreements']['iona']=[];self.reject('start-expedition',siteId=l.SITE,companionIds=c.CAST)
  self.start(['mira']);self.assertEqual(g.expedition_party(self.s),['founder','mira']);self.assertTrue(g.character_at_castle(self.s,'tamsin'))
 def test_all_23_methods_with_real_participants_and_exact_spell_costs(self):
  count=0
  for index,d in enumerate(c.STEPS):
   for key,choice in d['choices'].items():
    self.setUp();self.maxed();spell=None
    if choice.get('castForm'):spell=magic.MagicTests.learned(self,choice['castForm'],'mira')
    self.start(c.CAST);l.saved(self.s)['completed']=[x['id'] for x in c.STEPS[:index]];l.resume(self.s)
    before=deepcopy(self.s['materialInventory']);self.method(key);outcome=l.saved(self.s)['outcomes'][-1]
    self.assertEqual(set(outcome['participants']),{'founder',*c.CAST})
    if spell:
     for material,n in g.SPELL_FORMS[choice['castForm']]['castingInputs'].items():self.assertEqual(self.s['materialInventory'][material],before[material]-n)
     self.assertEqual(outcome['casterId'],'mira');self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1)
    else:self.assertEqual(self.s['materialInventory']['binding-thread'],before['binding-thread'])
    count+=1
  self.assertEqual(count,23)
 def test_team_roles_require_distinct_capable_present_people(self):
  self.maxed();self.start();self.reject('choose-encounter-method',methodId='team')
  self.act('return-expedition');self.advance();self.start(['mira']);self.assertEqual(len(set(l.pairing(self.s,c.STEPS[0]['choices']['team']))),2);self.method('team')
 def test_paid_spell_and_changed_team_retreat_resume_preserve_progress(self):
  spell=magic.MagicTests.learned(self,'giant-grasp');self.start();self.act('choose-encounter-method',methodId='spell:giant-grasp');before=self.s['materialInventory']['binding-thread']
  self.act('return-expedition');self.advance();self.s=json.loads(json.dumps(self.s));self.start();self.assertEqual(self.s['expedition']['stage'],'working');self.advance()
  self.assertEqual(self.s['materialInventory']['binding-thread'],before);self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1)
  self.maxed();self.act('return-expedition');self.advance();self.start(['mira']);self.act('choose-encounter-method',methodId='team');self.act('return-expedition');self.advance();self.start()
  self.assertEqual(self.s['expedition']['stage'],'encounter-choice');self.method('patient');self.assertEqual(l.saved(self.s)['completed'],['approach','bridge'])
 def test_actual_group_conversations_and_private_context_no_absent_quotes(self):
  self.start(c.CAST);before={k:deepcopy(v) for k,v in self.s.items() if k not in ('lanternAdventure','relationships','journal')}
  self.act('share-lantern-scene',sceneId='arrival',choice='listen');self.assertEqual(before,{k:self.s[k] for k in before})
  self.assertIn('Iona folds the programme',l.saved(self.s)['memories']['arrival']['opening'])
  self.method('patient');self.method('patient');self.assertIn('You previously chose',next(r for r in l.adventure_view(self.s)['scenes'] if r['id']=='camp')['opening'])
  self.act('share-lantern-scene',sceneId='camp:mira',choice='company');self.assertEqual(len(l.context(self.s,'mira')),2);self.assertEqual(len(l.context(self.s,'tamsin')),1)
  self.reject('share-lantern-scene',sceneId='camp:mira',choice='company')
 def test_solo_text_does_not_invent_companions_and_future_responses_hidden(self):
  self.start();view=l.adventure_view(self.s);row=next(r for r in view['scenes'] if r['id']=='arrival')
  for who in ('Mira','Tamsin','Iona'):self.assertNotIn(who,row['opening'])
  self.assertNotIn(c.BEATS['arrival']['choices']['history'][1],json.dumps(view))
  self.assertFalse(next(r for r in view['scenes'] if r['id']=='camp')['available']);self.reject('share-lantern-scene',sceneId='camp:mira',choice='company')
 def test_romantic_camp_uses_established_milestones_and_friendship_remains(self):
  self.start(['mira']);self.method('patient');self.method('patient');self.reject('share-lantern-scene',sceneId='camp:mira',choice='affection')
  romance.saved(self.s)['people']['mira']={'level':3,'mode':'open','deferred':False}
  self.act('share-lantern-scene',sceneId='camp:mira',choice='affection');self.assertIn('Your partner',l.saved(self.s)['memories']['camp:mira']['response'])
 def test_return_rewards_installation_and_home_scene_are_once_and_scoped(self):
  self.reject('place-lantern-corner',installed=True);self.start(c.CAST);self.finish('hospitality');self.assertFalse(l.saved(self.s)['installed'])
  later=next(r for r in l.adventure_view(self.s)['scenes'] if r['id']=='camp:iona');self.assertTrue(later['available']);self.assertIn('Back home',later['opening'])
  self.act('share-lantern-scene',sceneId='camp:iona',choice='company')
  self.reject('share-lantern-scene',sceneId='home',choice='join');self.act('place-lantern-corner',installed=True)
  self.act('share-lantern-scene',sceneId='home',choice='join');self.assertIn('without waiting for you to mediate',l.saved(self.s)['memories']['home']['opening'])
  self.reject('share-lantern-scene',sceneId='home',choice='join');self.reject('place-lantern-corner',installed='true')
  self.act('place-lantern-corner',installed=False);self.assertIsNone(l.support(self.s,'water'));self.assertTrue(l.saved(self.s)['memories']['home'])
 def test_each_legacy_shortens_only_its_quest_types_without_stacking_or_free_rewards(self):
  self.act('talk-character-quest',questId='personal:mira',choice='warm');q=quests.active(self.s)
  for legacy,(_,types) in c.PURPOSES.items():
   l.saved(self.s).update(discoveries=['survey'],legacy=legacy,installed=True)
   for obstacle in __import__('character_quest_content').OBSTACLES:
    q['steps'][0]=obstacle;method=quests.methods(self.s,q)['patient'];self.assertEqual(method['phases'],2 if obstacle in types else 3)
   q['steps'][0]=types[0];ritual=__import__('character_quest_content').QUEST_RITUALS[types[0]];self.s['lastingRituals']['completed'][ritual]={'active':True}
   self.assertEqual(quests.methods(self.s,q)['patient']['phases'],2);self.s['lastingRituals']['completed']={}
 def test_threshold_fold_returns_all_four_without_advancing_castle_work(self):
  spell=magic.MagicTests.learned(self,'threshold-fold');self.start(c.CAST);self.act('return-expedition');dayphase=(self.s['dayNumber'],self.s['currentDayPhase'])
  self.act('field-spell',characterId='founder',spellId=spell,targetId='founder');self.assertIsNone(self.s['expedition']);self.assertEqual((self.s['dayNumber'],self.s['currentDayPhase']),dayphase)
  for who in ('founder',*c.CAST):self.assertTrue(g.character_at_castle(self.s,who))
 def test_readonly_view_and_migration_backup_retry_reload(self):
  old=deepcopy(self.s);l.adventure_view(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
  self.s.pop('lanternAdventure');self.s['schemaVersion']=53;self.s.pop('armoury',None);self.s.pop('watchRoad',None);before=deepcopy(self.s)
  with tempfile.TemporaryDirectory() as directory:
   st=GameStore(directory)
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   st=GameStore(directory);current=st.read();self.assertEqual(current['schemaVersion'],66);self.assertTrue(Path(directory,f"campaign-before-schema-53-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
   for k,v in before.items():
    if k not in ('schemaVersion','revision'):self.assertEqual(current[k],v)
   req={'requestId':uuid.uuid4().hex,'expectedRevision':current['revision'],'action':{'type':'start-expedition','siteId':l.SITE,'companionIds':c.CAST}}
   after=st.action(req);self.assertEqual(st.action(req),after);self.assertEqual(GameStore(directory).read(),after)
