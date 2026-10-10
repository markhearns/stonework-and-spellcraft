"""Progression regressions and earned short routes, including Rhess's guest alliance."""
from copy import deepcopy
import json,os,tempfile,unittest
from pathlib import Path
import game as g,house_shape,headquarters as h,field_patrols as patrols
import foundation_chamber as f,survey_rooms,castle_mystery
import test_eight_chapter_flow as eight

class LeanCampaignTests(eight.EightChapterFlowTests):
 lean=True
 def money(self,n):
  import first_hearth
  for _ in range(100):
   if self.s['sharedFunds']>=n:return
   row=first_hearth.income(self.s,n,'the next campaign project',{'view':'stores'})
   self.assertIsNotNone(row['action']);self.act(**{'kind':row['action']['type'],**{k:v for k,v in row['action'].items() if k!='type'}})
  self.fail('Could not earn the listed project cost.')
 def play_local_patrol(self):
  self.assertFalse(patrols.unlocked(self.s));self.assertTrue(patrols.local_unlocked(self.s))
  for a in ({'type':'trial-start'},{'type':'watch-depart','participants':['founder'],'routeId':'woods'}):
   old=deepcopy(self.s)
   with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
   self.assertEqual(old,self.s)
  self.act('watch-depart',participants=['founder'],routeId='road')
  for _ in range(35):
   run=patrols.saved(self.s)['active']
   if not run:break
   if run['stage']=='decision':
    choices=[c for c in patrols.choices(self.s) if not c['blockers']]
    c=next((c for c in choices if c['kind']=='peace'),None) or max((c for c in choices if c['kind']=='attack'),key=lambda c:2*c['preview']['damage']-c['preview']['injury'])
    self.act('watch-method',methodId=c['id'])
   self.advance()
  self.assertIsNone(patrols.saved(self.s)['active']);self.assertTrue(patrols.saved(self.s)['reports'][-1]['complete'])
  self.act('assign-founder',assignment='rest');self.advance(3)
 def play_foundation(self):
  self.assertFalse(self.s['firstRealTest']['completedOn']);self.assertTrue(f.unlocked(self.s));self.act('foundation-start')
  for key,d in f.STEPS.items():
   costs=sum(max(0,n-self.s['materialInventory'].get(k,0)+self.s['materialReserveTargets'].get(k,0))*g.MATERIALS[k]['price'] for k,n in d.get('materials',{}).items())
   self.money(d.get('cost',0)+costs)
   for k,n in d.get('materials',{}).items():
    while self.s['materialInventory'][k]-self.s['materialReserveTargets'][k]<n:self.act('buy-material',materialId=k)
   m=next(m for m in reversed(f.methods(self.s,key)) if not m['blockers'])
   self.act('foundation-task',stepId=key,methodId=m['id']);self.advance(m['phases'])
  self.act('foundation-conclude');self.assertTrue(f.ready(self.s));self.assertFalse(f.active(self.s))
 def play_seven(self,company):
  super().play_seven(company)
  self.assertTrue(f.saved(self.s)['concludedOn'])
  if company=='solo':self.assertNotIn('rhess',g.household_members(self.s))
  if 'survey' not in self.s['binderyDiscoveries']:
   self.act('start-expedition',siteId='hillfold-bindery');self.advance();self.act('choose-expedition-approach',approach='survey')
   while self.s['expedition']['stage']=='working':self.advance()
   self.act('return-expedition');self.advance()
  if 'gentle-refraction' not in g.character_principles(self.s,'founder'):
   self.act('start-expedition',siteId='rainward-observatory');self.advance();self.act('choose-expedition-approach',approach='survey')
   for method in ('drain-by-hand','clean-lenses','copy-ledger'):
    self.act('choose-encounter-method',methodId=method)
    while self.s['expedition']['stage']=='working':self.advance()
   self.act('return-expedition');self.advance()
  self.assertIn('gentle-refraction',g.character_principles(self.s,'founder'))
  for key in ('window-measure','founding-record'):
   if key in self.s['castleMystery']['discoveries']:continue
   self.act('start-mystery',leadId=key);self.advance(castle_mystery.LEADS[key]['phases'])
  self.assertFalse(survey_rooms.blockers(self.s));self.act('survey-room-start')
  for key,d in survey_rooms.STEPS.items():
   self.act('survey-room-task',stepId=key);self.advance(d['phases'])
  self.act('survey-room-conclude',choice='teach' if company=='solo' else 'questions')
  self.assertTrue(survey_rooms.saved(self.s)['completedOn']);self.assertFalse(self.s['testing']['used']);self.assertEqual(self.s['provisions']['unfedDays'],0)
  self.assertEqual(len(house_shape.completed_paths(self.s)),1)
  old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
  out=os.environ.get('STONEWORK_V114_AUDIT_DIR')
  if out:
   p=Path(out);p.mkdir(parents=True,exist_ok=True);(p/('earned-v114-'+company+'.json')).write_text(json.dumps(self.s))
   (p/('summary-'+company+'.json')).write_text(json.dumps({'day':self.s['dayNumber'],'phase':self.s['currentDayPhase'],'funds':self.s['sharedFunds'],'household':g.household_members(self.s),'rhessResidency':self.s['residency']['rhess']['residencyStatus'],'chaptersComplete':9,'spellCasts':sum(x['castCount'] for x in self.s['spellbook']),'unfedDays':self.s['provisions']['unfedDays'],'cheats':self.s['testing']['used']},indent=2))

class IdentityAndSaveTests(unittest.TestCase):
 def test_authored_djinn_has_new_identity_and_bounded_magic(self):
  import local_encounters,summoning,character_builds,armoury,art_catalogue,resident_specialties
  s=g.new_campaign('fresh');s['localEncounterCandidates']['zahra']=local_encounters.definition(s,'zahra');summoning.initialize_person(s,'zahra')
  self.assertEqual(s['people']['zahra']['ancestryLabel'],'Djinn');self.assertEqual(s['people']['zahra']['name'],'Zahra')
  self.assertEqual(sum(character_builds.build(s,'zahra')['attributes'].values()),30)
  self.assertEqual(character_builds.build(s,'zahra')['attributes']['might'],3)
  sp=next(x for x in s['spellbook'] if x['ownerId']=='zahra');self.assertEqual(sp['formId'],'warm-twist');self.assertEqual(sp['castCount'],0)
  self.assertEqual(armoury.STARTERS['zahra'],'repair-hammer')
  self.assertIn('zahra',art_catalogue.ART_ASSETS)
  self.assertNotIn('brakka',json.dumps(s).lower());self.assertNotIn('brakka',local_encounters.PEOPLE)
  old=deepcopy(s);self.assertEqual(g.migrate_state(json.loads(json.dumps(s))),old)
 def test_finished_opening_not_reopened_and_optional_chamber_survives_upgrade(self):
  s=g.new_campaign('fresh');s['soloLife']['firstHearth']['memories']['conclusion']={'choiceId':'history'};s['foundationChamber']['started']=True;s['schemaVersion']=71
  import early_lessons
  g.migrate_state(s);self.assertIsNone(early_lessons.next_step(s));self.assertTrue(f.unlocked(s));self.assertFalse(survey_rooms.saved(s)['completedOn'])
 def test_survey_actions_rollback_and_do_not_leak_unearned_evidence(self):
  s=g.new_campaign('fresh');old=deepcopy(s)
  with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'survey-room-task','stepId':'reference'})
  self.assertEqual(old,s);self.assertNotIn('bedrock because',json.dumps(survey_rooms.view(s)))

 def test_survey_endings_preserve_evidence_and_reward_only_once(self):
  import test_foundation_chamber as fixture
  for choice in survey_rooms.CLOSINGS:
   t=fixture.FoundationChamberTests();t.setUp();t.chapter();s=t.s
   s['castleMystery']['discoveries']['founding-record']={'text':s['privateCastleLore']['evidence']['founding-record']}
   g.apply_action(s,{'type':'survey-room-start'})
   for key,d in survey_rooms.STEPS.items():
    g.apply_action(s,{'type':'survey-room-task','stepId':key})
    for _ in range(d['phases']):g.apply_action(s,{'type':'advance'})
   evidence=deepcopy(s['castleMystery']);g.apply_action(s,{'type':'survey-room-conclude','choice':choice})
   self.assertEqual(s['castleMystery'],evidence)
   self.assertEqual(s['characterDevelopment']['founder']['advancementAwards']['survey-rooms']['points'],2)
   old=deepcopy(s)
   with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'survey-room-conclude','choice':choice})
   self.assertEqual(s,old)
 def test_tradition_is_available_at_sixty_bonding(self):
  import test_resident_friendships as fixtures,resident_friendships as friendship
  t=fixtures.FriendshipTests();t.setUp();t.project();t.points(value=45)
  t.act('friendship-arrange',pairId='mira|tamsin',stage='visit');t.act('advance')
  t.points(value=59);t.reject('friendship-share',pairId='mira|tamsin',stage='tradition')
  t.points(value=60);t.act('friendship-share',pairId='mira|tamsin',stage='tradition')
  self.assertIn('tradition',friendship.record(t.s,'mira|tamsin')['memories'])
