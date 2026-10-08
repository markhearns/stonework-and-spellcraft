from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
import game as g
import party_journeys as j
import party_journey_content as c
import field_magic as f
import romance,character_quests as quests,character_approaches as apt
import test_magic_overhaul as magic
import test_household_chapters as household
from server import GameStore

class PartyJourneyTests(unittest.TestCase):
 def setUp(self):
  self.s=magic.MagicTests.rich(self);self.s['miraArchiveProject']['status']='complete'
  for who in c.CAST:
   if who=='mira':continue
   household.HouseholdChapterTests.member(self,who);self.s['soloLife']['agreements'][who]=['fieldwork']
  self.s['housingRooms']['garden-chamber']['status']='complete'
  for who in c.CAST:self.s['bedroomAssignments'][who]='garden-chamber'
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(self.s,old)
 def start(self,key='flooded-monastery',party=()):
  self.act('start-expedition',siteId=key,companionIds=list(party));self.advance();self.act('choose-expedition-approach',approach='survey')
 def method(self,key):
  self.act('choose-encounter-method',methodId=key)
  while self.s['expedition']['stage']=='working':self.advance()
 def maxed(self):
  for w in g.household_members(self.s):
   self.s['characterBuilds'][w]['attributes']={a:10 for a in g.character_builds.ATTRIBUTES};self.s['characterSkills'][w]={k:2 for k in g.CHARACTER_SKILLS}
 def at(self,key,index,party=()):
  self.start(key,party);j.saved(self.s,key)['completed']=[x['id'] for x in c.SITES[key]['steps'][:index]];j.resume(self.s)
 def finish(self,key):
  while j.step(self.s):
   d=j.step(self.s);self.method('patient' if 'patient' in d['choices'] else next(iter(d['choices'])))
  self.act('return-expedition');self.advance()
 def test_all_sites_solo_minimum_attributes_zero_supplies_complete(self):
  for key,d in c.SITES.items():
   self.setUp();self.s['characterBuilds']['founder']['attributes']={a:1 for a in g.character_builds.ATTRIBUTES};self.s['characterSkills']['founder']={k:0 for k in g.CHARACTER_SKILLS}
   self.s['materialInventory']={k:0 for k in self.s['materialInventory']};self.s['sharedFunds']=0
   self.start(key);self.finish(key)
   p=j.saved(self.s,key);self.assertEqual(p['discoveries'],['survey']);self.assertEqual(len(p['completed']),7);self.assertEqual(self.s['materialInventory']['moon-glass'],2)
   self.assertEqual(self.s['characterDevelopment']['founder']['advancementAwards'][key]['points'],3)
   self.assertNotIn(key,self.s['characterDevelopment']['mira']['advancementAwards']);self.reject('start-expedition',siteId=key,companionIds=[])
 def test_every_authored_method_has_real_costs_and_actor_credit(self):
  count=0
  for key,d in c.SITES.items():
   for idx,step in enumerate(d['steps']):
    for method,choice in step['choices'].items():
     self.setUp();self.maxed();sp=None
     if choice.get('castForm'):sp=magic.MagicTests.learned(self,choice['castForm'],'mira')
     self.at(key,idx,['mira','brakka','sabine']);before=deepcopy(self.s['materialInventory']);self.method(method)
     p=j.saved(self.s,key);out=p['outcomes'][-1];self.assertEqual(set(out['participants']),{'founder','mira','brakka','sabine'})
     costs=g.SPELL_FORMS[choice['castForm']]['castingInputs'] if sp else choice.get('inputs',{})
     for material,n in before.items():self.assertEqual(self.s['materialInventory'][material],n-costs.get(material,0))
     if sp:self.assertEqual(out['casterId'],'mira');self.assertEqual(g.spell_by_id(self.s,sp)['castCount'],1)
     if choice.get('team'):self.assertEqual(len(set(out['actors'])),2)
     if choice.get('lasting'):self.assertEqual(p['inscriptions'][-1]['text'],choice['lasting']);self.assertEqual(p['inscriptions'][-1]['conductorId'],'founder')
     count+=1
  self.assertEqual(count,99)
 def test_all_fourteen_can_travel_and_every_actual_returner_learns(self):
  for who in c.CAST:
   self.setUp();self.start(party=[who]);self.assertFalse(g.character_at_castle(self.s,who));self.finish('flooded-monastery')
   self.assertTrue(g.character_at_castle(self.s,who));self.assertEqual(g.character_assignment(self.s,who),'rest');self.assertIn('water-guidance',g.character_principles(self.s,who));self.assertIn('flooded-monastery',self.s['characterDevelopment'][who]['advancementAwards'])
 def test_generic_old_destinations_accept_four_people_and_release_all(self):
  party=['mira','brakka','sabine'];self.act('start-expedition',siteId='old-waterworks',companionIds=party);self.advance();self.act('choose-expedition-approach',approach='survey')
  while self.s['expedition']['stage']=='working':self.advance()
  self.act('return-expedition');self.advance()
  self.assertEqual(self.s['lastExpeditionReport']['participants'],['founder',*party])
  for who in party:self.assertIn('water-guidance',g.character_principles(self.s,who));self.assertEqual(g.character_assignment(self.s,who),'rest')
 def test_party_input_validation_is_atomic_and_old_single_input_still_works(self):
  for selected in (None,'mira',[[]],['mira']*2,['founder'],['absent'],c.CAST[:4]):self.reject('start-expedition',siteId='old-waterworks',companionIds=selected)
  self.reject('start-expedition',siteId='old-waterworks',companionIds=['mira'],companionId='iona')
  self.s['soloLife']['agreements']['brakka']=[];self.reject('start-expedition',siteId='old-waterworks',companionIds=['mira','brakka'])
  self.act('start-expedition',siteId='old-waterworks',companionId='mira');self.assertEqual(g.expedition_party(self.s),['founder','mira'])
 def test_lantern_accepts_other_companions_without_inventing_trio(self):
  self.start('lantern-pavilion',['brakka','sabine','fenna']);import lantern_adventure as l
  row=next(r for r in l.scene_rows(self.s) if r['id']=='arrival');self.assertNotIn('Mira studies',row['opening']);self.assertEqual(g.expedition_party(self.s),['founder','brakka','sabine','fenna'])
  self.act('return-expedition');self.advance()
  for who in ['brakka','sabine','fenna']:self.assertEqual(g.character_assignment(self.s,who),'rest')
 def test_departure_retains_project_and_stops_actual_workers(self):
  import household_sagas as sagas
  p=sagas.saved(self.s)['stories'].setdefault('workbench',sagas.record(self.s,'workbench'));p['project']={'status':'working','workers':['founder','brakka'],'done':0,'mode':'method','cost':{'crowns':4}}
  g.set_character_assignment(self.s,'founder','household-story');g.set_character_assignment(self.s,'brakka','household-story')
  rows=j.departure(self.s);self.assertTrue(next(r for r in rows if r['id']=='brakka')['commitments'])
  self.start(party=['brakka']);self.method('patient');self.assertEqual(sagas.record(self.s,'workbench')['project']['done'],0)
 def test_partial_work_retreat_json_reload_and_changed_party_actual_contributors(self):
  self.start(party=['mira']);self.act('choose-encounter-method',methodId='patient');self.advance();self.act('return-expedition');self.advance()
  p=j.saved(self.s,'flooded-monastery');self.assertEqual(p['pending']['remaining'],2);self.assertFalse(p['discoveries'])
  self.s=json.loads(json.dumps(self.s));self.start(party=['brakka']);self.advance(2)
  out=j.saved(self.s,'flooded-monastery')['outcomes'][0];self.assertEqual(set(out['participants']),{'founder','mira','brakka'})
 def test_paid_spell_waits_for_original_caster_and_does_not_charge_twice(self):
  sp=magic.MagicTests.learned(self,'water-walk','mira');self.start(party=['mira']);self.act('choose-encounter-method',methodId='spell:water-walk');paid=deepcopy(self.s['materialInventory'])
  self.act('return-expedition');self.advance();self.start();self.assertEqual(self.s['expedition']['stage'],'encounter-choice');self.assertTrue(j.resume_blockers(self.s))
  self.act('return-expedition');self.advance();self.start(party=['mira']);self.assertEqual(self.s['expedition']['stage'],'working');self.advance();self.assertEqual(self.s['materialInventory'],paid);self.assertEqual(g.spell_by_id(self.s,sp)['castCount'],1)
 def test_changed_team_can_replace_saved_method_with_ordinary_route(self):
  self.maxed();self.start(party=['mira']);self.act('choose-encounter-method',methodId='team');self.act('return-expedition');self.advance();self.start(party=['brakka'])
  self.assertEqual(self.s['expedition']['stage'],'encounter-choice');self.method('patient');self.assertEqual(j.saved(self.s,'flooded-monastery')['outcomes'][0]['methodId'],'patient')
 def test_ritual_requires_personal_knowledge_and_unreserved_components(self):
  self.start();self.s['founderKnownPrinciples']=[];self.reject('choose-encounter-method',methodId='ritual')
  self.s['founderKnownPrinciples']=list(g.PRINCIPLE_NAMES);self.s['materialReserveTargets']['moon-glass']=self.s['materialInventory']['moon-glass'];self.reject('choose-encounter-method',methodId='ritual')
  self.s['materialReserveTargets']['moon-glass']=0;self.act('choose-encounter-method',methodId='ritual');self.assertEqual(self.s['expedition']['remainingWorkPhases'],2);self.advance();self.act('return-expedition');self.advance();self.start();self.advance();self.assertEqual(len(j.saved(self.s,'flooded-monastery')['inscriptions']),1)
 def test_support_haste_and_scout_are_costed_phases_and_do_not_stack(self):
  sp=magic.MagicTests.learned(self,'borrowed-hour');self.start();before=deepcopy(self.s['materialInventory']);self.act('journey-support',spellId=sp,targetId='founder');self.assertEqual(self.s['expedition']['remainingWorkPhases'],1)
  self.advance();self.assertEqual(f.progress(self.s)['buffs']['founder']['haste'],3);f.progress(self.s)['buffs']['founder']['scout']=2
  self.act('choose-encounter-method',methodId='patient');self.assertEqual(self.s['expedition']['remainingWorkPhases'],2);self.assertEqual(f.progress(self.s)['buffs']['founder'],{'haste':2,'scout':2})
  self.assertEqual(self.s['materialInventory']['moon-glass'],before['moon-glass']-1);self.advance(2)
  self.act('choose-encounter-method',methodId='ritual');self.assertEqual(self.s['expedition']['remainingWorkPhases'],2);self.assertEqual(f.progress(self.s)['buffs']['founder']['haste'],2)
 def test_home_prepared_haste_shortens_patient_method_once(self):
  self.s['spellSupports']['founder']={'haste':{'spellName':'Borrowed hour','remaining':3,'amount':1}};self.start();self.method('patient');self.assertEqual(self.s['spellSupports']['founder']['haste']['remaining'],2)
 def test_strength_support_changes_real_check_and_consumes_only_used_charge(self):
  sp=magic.MagicTests.learned(self,'giant-grasp');self.at('flooded-monastery',5);self.s['characterBuilds']['founder']['attributes']['might']=6;self.s['characterSkills']['founder']['athletics']=0
  self.reject('choose-encounter-method',methodId='specialist');self.act('journey-support',spellId=sp,targetId='founder');self.advance();self.method('specialist');self.assertEqual(f.progress(self.s)['buffs']['founder']['strength'],1)
 def test_healing_support_checks_target_and_full_health_then_restores(self):
  sp=magic.MagicTests.learned(self,'mending-light');self.start(party=['mira']);self.reject('journey-support',spellId=sp,targetId='brakka');self.reject('journey-support',spellId=sp,targetId='mira')
  self.s['fieldMagic']['vitality']['mira']=2;self.act('journey-support',spellId=sp,targetId='mira');self.advance();self.assertEqual(f.vitality(self.s,'mira'),5)
 def test_scout_report_requires_actual_cast_and_only_shows_next_obstacle(self):
  sp=magic.MagicTests.learned(self,'wisp-scout');self.start();self.assertIsNone(j.views(self.s)['scout']);self.act('journey-support',spellId=sp,targetId='founder');self.advance();self.assertEqual(j.views(self.s)['scout']['name'],c.SITES['flooded-monastery']['steps'][1]['name'])
 def test_support_paid_pending_survives_retreat_requires_original_recipient(self):
  sp=magic.MagicTests.learned(self,'borrowed-hour','mira');self.start(party=['mira','brakka']);self.act('journey-support',spellId=sp,targetId='brakka');cost=deepcopy(self.s['materialInventory']);self.act('return-expedition');self.advance();self.start(party=['mira']);self.assertEqual(self.s['expedition']['stage'],'encounter-choice')
  self.act('return-expedition');self.advance();self.start(party=['mira','brakka']);self.advance();self.assertEqual(f.progress(self.s)['buffs']['brakka']['haste'],3);self.assertEqual(self.s['materialInventory'],cost)
 def test_actual_party_scenes_and_private_memories_never_credit_absentees(self):
  self.start(party=['iona','sabine']);self.act('share-party-journey',siteId='flooded-monastery',sceneId='arrival',choice='listen');self.method('patient');self.method('patient')
  row=next(r for r in j.scenes(self.s,'flooded-monastery') if r['id']=='camp');self.assertIn('Iona offers a grand introduction',row['opening']);self.assertNotIn('Brakka counts',row['opening']);self.assertIn('Earlier you chose',row['opening'])
  before=(self.s['dayNumber'],self.s['currentDayPhase'],deepcopy(self.s['materialInventory']));self.act('share-party-journey',siteId='flooded-monastery',sceneId='camp',choice='playful')
  self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase'],self.s['materialInventory']));self.assertFalse(j.context(self.s,'mira'));self.reject('share-party-journey',siteId='flooded-monastery',sceneId='private:mira',choice='company')
  self.reject('share-party-journey',siteId='flooded-monastery',sceneId='camp',choice='playful')
 def test_all14_private_scenes_and_relationship_gates(self):
  for who in c.CAST:
   self.setUp();self.at('masquerade-manor',2,[who]);self.reject('share-party-journey',siteId='masquerade-manor',sceneId='private:'+who,choice='affection')
   romance.saved(self.s)['people'][who]={'level':2,'mode':'open','deferred':False};self.act('share-party-journey',siteId='masquerade-manor',sceneId='private:'+who,choice='affection');memory=j.saved(self.s,'masquerade-manor')['memories']['private:'+who]
   self.assertEqual(memory['participants'],['founder',who]);self.assertEqual(memory['relationshipLevel'],2);self.assertIn('kiss',memory['response']);self.assertEqual(romance.level(self.s,who),2)
 def test_paused_romance_keeps_friendship_and_future_text_hidden(self):
  self.start(party=['mira']);v=j.views(self.s);private=next(r for r in v['sites']['flooded-monastery']['scenes'] if r['id']=='private:mira');self.assertEqual(private['opening'],'');self.assertEqual(private['choices'],{})
  self.method('patient');self.method('patient');romance.saved(self.s)['people']['mira']={'level':4,'mode':'friendly','deferred':False};self.reject('share-party-journey',siteId='flooded-monastery',sceneId='private:mira',choice='affection');self.act('share-party-journey',siteId='flooded-monastery',sceneId='private:mira',choice='company')
 def test_solo_scenes_do_not_invent_companions(self):
  self.at('frozen-skybridge',2);self.act('share-party-journey',siteId='frozen-skybridge',sceneId='camp',choice='playful');m=j.saved(self.s,'frozen-skybridge')['memories']['camp'];self.assertEqual(m['participants'],['founder']);self.assertNotIn('The others',m['response'])
 def test_installation_benefits_scoped_nonstacking_and_reversible(self):
  key='flooded-monastery';self.start(key,['mira']);self.finish(key);self.assertEqual(j.bonus(self.s,'channeling'),0);self.act('place-journey-legacy',siteId=key,installed=True);self.assertEqual(j.bonus(self.s,'channeling'),1);self.assertIsNone(j.support(self.s,'bargain'))
  self.act('talk-character-quest',questId='personal:mira',choice='warm');q=quests.active(self.s);q['steps'][0]='water';m=quests.methods(self.s,q)['patient'];self.assertEqual(m['phases'],2);self.assertEqual(m['journeyId'],key)
  self.s['lastingRituals']['completed']['garden-circle']={'active':True};self.assertEqual(quests.methods(self.s,q)['patient']['phases'],2)
  self.act('place-journey-legacy',siteId=key,installed=False);self.assertEqual(j.bonus(self.s,'channeling'),0)
 def test_unshared_private_camp_available_at_home_without_absent_third_person(self):
  self.start(party=['mira','brakka']);self.finish('flooded-monastery');self.act('start-expedition',siteId='old-waterworks',companionIds=['brakka']);self.act('return-expedition');self.advance()
  self.s['additionalResidents']['brakka']['status']='departed'
  private=next(r for r in j.scenes(self.s,'flooded-monastery') if r['id']=='private:mira');self.assertTrue(private['available']);self.assertIn('At home',private['opening']);self.act('share-party-journey',siteId='flooded-monastery',sceneId='private:mira',choice='company')
 def test_teleport_moves_whole_party_without_extra_time_and_home_rewards_once(self):
  sp=magic.MagicTests.learned(self,'threshold-fold');self.start(party=['mira','brakka','sabine']);self.act('return-expedition');before=(self.s['dayNumber'],self.s['currentDayPhase']);self.act('field-spell',characterId='founder',spellId=sp,targetId='founder');self.assertIsNone(self.s['expedition']);self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase']))
  self.act('start-expedition',siteId='flooded-monastery',companionIds=['mira','brakka','sabine']);self.act('field-spell',characterId='founder',spellId=sp,targetId='founder');self.assertEqual(self.s['expedition']['stage'],'awaiting-choice')
 def test_migration_backup_old_midjourney_and_idempotent_store_retry(self):
  self.s.pop('partyJourneys');self.s['schemaVersion']=56;self.s.pop('armoury',None);self.s.pop('watchRoad',None);self.s['expedition']={'siteId':'old-waterworks','companionId':'mira','stage':'outbound','chosenApproach':None,'remainingWorkPhases':0,'carriedLantern':False,'restoreLanternDisplay':False,'discoveryReady':False,'wealthPlan':'shared','departureDay':1}
  old=deepcopy(self.s)
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory)
   with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   store=GameStore(directory);current=store.read();self.assertEqual(current['schemaVersion'],66);self.assertEqual(current['expedition'],old['expedition']);self.assertTrue(Path(directory,'campaign-before-schema-56-to-66.sqlite3').exists());self.assertEqual(g.expedition_party(current),['founder','mira'])
   request={'requestId':uuid.uuid4().hex,'expectedRevision':current['revision'],'action':{'type':'return-expedition'}};result=store.action(request);self.assertEqual(result,store.action(request));self.assertEqual(result,GameStore(directory).read())
 def test_views_are_readonly_and_do_not_leak_future_responses(self):
  old=deepcopy(self.s);v=g.public_state(self.s);self.assertEqual(old,self.s);self.assertNotIn(c.CAMPS['mira'][2],json.dumps(v['partyJourneysView']))

 def test_preview_matches_accelerated_duration_without_spending_a_charge(self):
  self.s['spellSupports']['founder']={'haste':{'spellName':'Borrowed hour','remaining':3,'amount':1}};self.start();old=deepcopy(self.s)
  self.assertEqual(j.view(self.s)['choices']['patient']['phases'],2);self.assertEqual(old,self.s)
  self.act('choose-encounter-method',methodId='patient');self.assertEqual(self.s['expedition']['remainingWorkPhases'],2)
  import guidance
  preview=guidance.preview(self.s);row=next(r for r in preview['projects'] if r['id']=='party-journey:flooded-monastery');self.assertEqual(row['progress'],1);self.assertFalse(row['completes']);self.assertEqual(j.saved(self.s,'flooded-monastery')['pending']['remaining'],2)
  self.advance();preview=guidance.preview(self.s);self.assertTrue(next(r for r in preview['projects'] if r['id']=='party-journey:flooded-monastery')['completes'])
 def test_recovered_legacy_applies_to_expedition_checks_not_castle_training(self):
  p=j.saved(self.s,'flooded-monastery');p.update(discoveries=['survey'],installed=True)
  req=apt.spec('resolve','channeling');base=apt.score(self.s,'founder',req,['founder','mira'])['total'];self.start('frozen-skybridge',['mira'])
  self.assertEqual(apt.score(self.s,'founder',req,['founder','mira'])['total'],base+1)
