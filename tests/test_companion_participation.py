from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
import game as g
import beacon_expedition as b
import companion_participation as c
import test_magic_overhaul as magic
import test_household_chapters as household
from server import GameStore

class CompanionParticipationTests(unittest.TestCase):
 def setUp(self):
  self.s=magic.MagicTests.rich(self);self.s['miraArchiveProject']['status']='complete'
 def act(self,kind,**kw):return g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def start(self,companion=None):
  self.act('start-expedition',siteId=b.SITE,companionId=companion);self.advance();self.act('choose-expedition-approach',approach='survey')
 def maxed(self,who):
  self.s['characterBuilds'][who]['attributes']={k:10 for k in g.character_builds.ATTRIBUTES}
  self.s['characterSkills'][who]={k:2 for k in g.CHARACTER_SKILLS}
 def method(self,key):
  self.act('choose-encounter-method',methodId=key)
  while self.s['expedition']['stage']=='working':self.advance()
 def test_full_solo_journey_at_minimum_attributes_and_reward_once_on_return(self):
  self.s['characterBuilds']['founder']['attributes']={k:1 for k in g.character_builds.ATTRIBUTES}
  self.start();before=self.s['sharedFunds']
  for d in b.STEPS:
   self.assertEqual(b.blockers(self.s,d['choices']['patient']),[])
   self.method('patient')
  self.assertEqual(self.s['sharedFunds'],before);self.assertEqual(self.s['expedition']['stage'],'ready-to-return')
  self.act('return-expedition');self.advance();self.assertEqual(b.saved(self.s)['discoveries'],['survey'])
  self.assertGreater(self.s['sharedFunds'],before);self.assertEqual(c.saved(self.s)['events'],{})
  import social_life
  self.assertTrue(social_life.evidence(self.s,'journey'))
  self.reject('start-expedition',siteId=b.SITE)
 def test_all_ordinary_specialist_and_team_routes_resolve_with_real_participants(self):
  count=0
  for i,d in enumerate(b.STEPS):
   for key,choice in d['choices'].items():
    if choice.get('castForm'):continue
    self.setUp();self.maxed('founder');self.maxed('mira');self.start('mira')
    b.saved(self.s)['completed']=[x['id'] for x in b.STEPS[:i]];b.resume(self.s)
    before=deepcopy(self.s['materialInventory']);self.method(key)
    self.assertEqual(b.saved(self.s)['outcomes'][-1]['methodId'],key)
    self.assertEqual(self.s['materialInventory'],before)
    if choice.get('team'):self.assertEqual(len(set(b.saved(self.s)['outcomes'][-1]['participants'])),2)
    count+=1
  self.assertEqual(count,19)
 def test_team_requires_two_distinct_present_people_and_not_one_omnipotent_person(self):
  self.maxed('founder');self.maxed('mira');self.start()
  self.reject('choose-encounter-method',methodId='two-hands')
  self.assertFalse(c.suggestions(self.s));self.assertTrue(b.blockers(self.s,b.STEPS[0]['choices']['two-hands']))
  self.method('patient')
 def test_complementary_roles_work_when_neither_character_can_fill_both(self):
  self.s['characterBuilds']['founder']['attributes']['might']=8
  self.s['characterBuilds']['mira']['attributes']['dexterity']=8
  self.start('mira');self.assertEqual(b.pairing(self.s,b.STEPS[0]['choices']['two-hands']),['founder','mira'])
  self.method('two-hands');self.assertTrue(b.saved(self.s)['outcomes'][0]['team'])
 def test_paid_magic_retreat_resume_and_retry_never_recharge(self):
  key=magic.MagicTests.learned(self,'giant-grasp');self.start();before=self.s['materialInventory']['binding-thread']
  self.act('choose-encounter-method',methodId='spell:giant-grasp')
  self.assertEqual(self.s['materialInventory']['binding-thread'],before-1)
  self.act('return-expedition');self.advance();self.assertEqual(b.saved(self.s)['pending']['remaining'],1)
  self.start();self.assertEqual(self.s['expedition']['stage'],'working');self.advance()
  self.assertEqual(self.s['materialInventory']['binding-thread'],before-1)
  self.assertEqual(g.spell_by_id(self.s,key)['castCount'],1)
 def test_all_seven_spell_and_spell_team_methods_pay_exact_components(self):
  count=0
  for i,d in enumerate(b.STEPS):
   for key,choice in d['choices'].items():
    if not choice.get('castForm'):continue
    self.setUp();self.maxed('founder');self.maxed('mira')
    owner='mira' if choice.get('casterRole')==1 else 'founder'
    spell=magic.MagicTests.learned(self,choice['castForm'],owner)
    self.start('mira');b.saved(self.s)['completed']=[x['id'] for x in b.STEPS[:i]];b.resume(self.s)
    before=deepcopy(self.s['materialInventory']);self.method(key)
    for material,n in g.SPELL_FORMS[choice['castForm']]['castingInputs'].items():self.assertEqual(self.s['materialInventory'][material],before[material]-n)
    self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1);count+=1
  self.assertEqual(count,7)
 def test_unprepared_spell_and_fake_method_rejected_atomically(self):
  self.start('mira');self.reject('choose-encounter-method',methodId='spell:giant-grasp');self.reject('choose-encounter-method',methodId='imaginary')
 def test_suggestions_are_optional_valid_readonly_and_name_actual_companion(self):
  self.maxed('mira');self.maxed('founder');self.start('mira');before=deepcopy(self.s)
  v=c.view(self.s);self.assertEqual(before,self.s);self.assertTrue(v['suggestions'])
  for suggestion in v['suggestions']:self.assertEqual(suggestion['who'],'mira')
  self.act(**{'kind':v['suggestions'][0]['action']['type'],**{k:v for k,v in v['suggestions'][0]['action'].items() if k!='type'}})
  self.assertEqual(self.s['expedition']['stage'],'working');self.assertEqual(c.suggestions(self.s),[])
 def test_aqueduct_suggestions_use_companions_real_scores_and_health(self):
  self.maxed('mira');self.act('start-expedition',siteId='cinder-aqueduct',companionId='mira');self.advance();self.act('choose-expedition-approach',approach='survey')
  self.assertTrue(c.suggestions(self.s));self.s['fieldMagic']['vitality']['mira']=0;self.assertFalse(c.suggestions(self.s))
 def test_actual_training_creates_invitation_once_and_can_be_deferred_and_remembered(self):
  g.award_advancement(self.s,'mira','fixture',30,'Fixture')
  self.act('train-skill',characterId='mira',skillId='diplomacy');self.advance()
  self.assertEqual(c.saved(self.s)['events'],{});self.advance()
  event=next(iter(c.saved(self.s)['events']));old=deepcopy(self.s)
  c.view(self.s);self.assertEqual(old,self.s)
  self.act('defer-participation',eventId=event);self.assertIn(event,c.saved(self.s)['deferred'])
  self.act('restore-participation',eventId=event);before={k:deepcopy(v) for k,v in self.s.items() if k not in ('companionParticipation','journal','relationships')}
  self.act('share-participation',eventId=event,choice='notice');self.assertEqual(before,{k:self.s[k] for k in before})
  self.assertEqual(len(c.context(self.s,'mira')),1);self.assertEqual(c.context(self.s,'tamsin'),[])
  self.reject('share-participation',eventId=event,choice='notice')
 def test_teacher_invitation_remembers_a_real_founder_lesson(self):
  self.s['characterSkills']['mira']['diplomacy']=2;g.award_advancement(self.s,'founder','fixture',10,'Fixture')
  self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='skill',targetId='diplomacy');self.advance()
  event=next(iter(c.saved(self.s)['events']));self.assertIn('finished teaching you Diplomacy 1',c.event_row(self.s,event)['opening'])
 def test_completed_return_invitation_recalls_actual_team_method_and_preserves_original_social_content(self):
  self.maxed('founder');self.maxed('mira');self.start('mira')
  for _ in b.STEPS:self.method('two-hands')
  self.assertEqual(c.saved(self.s)['events'],{});self.act('return-expedition');self.advance()
  event='beacon:mira:complete';self.assertEqual(len(c.saved(self.s)['events'][event]['outcomes']),6)
  self.act('share-participation',eventId=event,choice='thanks');self.assertIn('Brace the trunk while a partner releases the snag',c.context(self.s,'mira')[0]['response'])
  self.assertEqual(len(g.public_state(self.s)['socialLifeView']['scenes']),5)
 def test_changed_party_cannot_resume_missing_teammates_pending_role(self):
  self.maxed('founder');self.maxed('mira');self.start('mira');self.act('choose-encounter-method',methodId='two-hands')
  self.act('return-expedition');self.advance();self.start()
  self.assertEqual(self.s['expedition']['stage'],'encounter-choice')
  self.reject('choose-encounter-method',methodId='two-hands');self.method('patient')
 def test_all_character_training_and_return_dialogues_offer_three_distinct_replies(self):
  for who in c.VOICES:
   household.HouseholdChapterTests.member(self,who)
   c.trained(self.s,who,{'kind':'skill','targetId':'diplomacy'})
   c.returned(self.s,['founder',who],[],False)
  for event in c.saved(self.s)['events'].values():
   opening,choices=c.dialogue(self.s,event);self.assertTrue(opening);self.assertEqual(len(choices),3);self.assertEqual(len({r['response'] for r in choices.values()}),3)
 def test_schema49_migration_backup_and_store_retries(self):
  self.s['schemaVersion']=49;self.s.pop('beaconJourney');self.s.pop('companionParticipation');old=deepcopy(self.s)
  with tempfile.TemporaryDirectory() as directory:
   with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
    db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
   store=GameStore(directory);current=store.read()
   self.assertTrue((Path(directory)/f"campaign-before-schema-49-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
   for k,v in old.items():
    if k not in ('schemaVersion','revision'):self.assertEqual(current[k],v,k)
   req={'requestId':uuid.uuid4().hex,'expectedRevision':current['revision'],'action':{'type':'start-expedition','siteId':b.SITE,'companionId':'mira'}}
   after=store.action(req);self.assertEqual(store.action(req),after);self.assertEqual(GameStore(directory).read(),after)

 def test_saved_team_work_rechecks_retrained_roles_and_records_actual_workers(self):
  self.maxed('founder');self.maxed('mira');self.start('mira');self.act('choose-encounter-method',methodId='two-hands')
  self.act('return-expedition');self.advance()
  self.s['characterBuilds']['mira']['attributes']={k:1 for k in g.character_builds.ATTRIBUTES}
  self.s['characterSkills']['mira']={k:0 for k in g.CHARACTER_SKILLS}
  self.start('mira');self.assertEqual(self.s['expedition']['stage'],'encounter-choice')
  self.method('patient');self.assertEqual(set(b.saved(self.s)['outcomes'][0]['participants']),{'founder','mira'})
