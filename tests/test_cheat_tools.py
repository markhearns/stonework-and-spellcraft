from copy import deepcopy
import json,tempfile,unittest,uuid
import game as g,cheat_tools as c,armoury,local_encounters as local,summoning,containment,provisions,headquarters as h
from server import GameStore

class CheatToolsTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign('fresh');self.act('cheat-toggle',enabled=True)
 def act(self,kind,**fields):return g.apply_action(self.s,dict(type=kind,**fields))
 def reject(self,kind,**fields):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**fields)
  self.assertEqual(before,self.s)
 def recruit(self,who):self.act('cheat-recruit',characterId=who)
 def test_every_unique_companion_individually_on_fresh_save(self):
  for who in c.unique_ids():
   with self.subTest(who=who):
    self.setUp();self.recruit(who)
    self.assertEqual(set(g.household_members(self.s)),{'founder',who})
    self.assertTrue(g.character_at_castle(self.s,who));self.assertIn(who,self.s['characterDevelopment'])
    self.assertTrue(self.s['armoury']['loadouts'][who]['expedition']['slots'])
    self.assertIn(who,g.public_state(self.s)['characterCatalog'])
    self.act('advance');self.assertEqual(g.household_members(self.s).count(who),1)
    self.reject('cheat-recruit',characterId=who)
 def test_all_preserves_chapters_relationships_and_current_residents(self):
  self.recruit('mira');self.s['personalFunds']['mira']=13
  before={k:deepcopy(self.s.get(k)) for k in ('soloLife','houseShape','roomToGrow','romance','dayNumber','currentDayPhase')}
  self.recruit('all');self.assertEqual(set(g.household_members(self.s)),{'founder',*c.unique_ids()})
  self.assertEqual(self.s['personalFunds']['mira'],13)
  self.assertEqual(before,{k:self.s.get(k) for k in before})
  self.assertEqual(self.s['startType'],'fresh')
  self.assertGreaterEqual(self.s['provisions']['stock'],7*provisions.need(self.s))
  self.assertTrue(all(r['availableBeds']>=0 for r in g.housing_summary(self.s)['rooms'].values()))
  for _ in range(4):self.act('advance')
  self.assertEqual(len(g.household_members(self.s)),17)
  self.assertEqual(len(g.public_state(self.s)['characterCatalog']),17)
 def test_demo_does_not_duplicate_mira(self):
  self.s=g.new_campaign();self.act('cheat-toggle',enabled=True);before=deepcopy(self.s['characterDevelopment']['mira'])
  self.recruit('all');self.assertEqual(g.household_members(self.s).count('mira'),1);self.assertEqual(before,self.s['characterDevelopment']['mira'])
 def test_pending_local_visit_is_cleared(self):
  self.act('start-local-visit',encounterId='koharu');self.recruit('koharu')
  self.assertIsNone(self.s['localVisit']);self.assertEqual(self.s['founderAssignment'],'rest')
  self.act('advance');self.assertEqual(len([r for r in self.s['summoningContacts'].values() if r['personId']=='koharu']),1)
 def test_paid_summoning_is_refunded_once_and_contact_is_usable(self):
  self.s['founderKnownPrinciples'].append('courteous-passage');self.s['materialInventory']['porous-clay']=2
  funds=self.s['sharedFunds'];thread=self.s['materialInventory']['binding-thread']
  self.act('summoning-prepare',conductorId='founder',candidateId='iona',materials=['porous-clay','binding-thread'])
  self.recruit('iona');self.assertEqual(self.s['sharedFunds'],funds);self.assertEqual(self.s['materialInventory']['binding-thread'],thread)
  contact=next(iter(self.s['summoningContacts']));self.assertEqual(self.s['summoningContacts'][contact]['personId'],'iona')
  self.act('summoning-talk',contactId=contact,topic='intentions');g.public_state(self.s)
  self.reject('summoning-cancel',contactId=contact)
 def test_pending_arrival_released_and_not_repeated(self):
  self.recruit('koharu');self.s['additionalResidents']['koharu']['status']='visiting';self.s['residency']['koharu']['residencyStatus']='arrival-agreed'
  room=self.s['bedroomAssignments'].pop('koharu');self.s['arrivalReservations']['test']={'personId':'koharu','roomId':room,'sourceType':'summoning','sourceId':next(iter(self.s['summoningContacts'])),'reservedBeds':1}
  self.recruit('koharu');self.assertNotIn('test',self.s['arrivalReservations']);self.act('advance');self.assertEqual(g.household_members(self.s).count('koharu'),1)
 def test_pending_tamsin_arrival_is_removed(self):
  self.s['pendingResidentArrival']={'characterId':'tamsin','roomId':'west-chamber'}
  self.s['arrivalReservations']['arrival:tamsin']={'personId':'tamsin','roomId':'west-chamber','sourceType':'recruitment','sourceId':'tamsin','reservedBeds':1}
  self.recruit('tamsin');self.assertEqual(self.s['pendingResidentArrival'],{});self.act('advance');g.public_state(self.s)
 def test_dungeon_case_and_paid_care_are_resolved_without_rewards(self):
  who='sabine';self.s['reviewedCandidates'][who]=deepcopy(containment.CASES[who]['candidate']);summoning.initialize_person(self.s,who,summoned=False)
  r=self.s['containment']['cases'][who];r.update(status='contained',chamberId='quiet-chamber-1')
  # A held project is refunded using the existing cancellation rule.
  self.s['containment']['project']={'kind':'care','targetId':who,'committedCrowns':12,'committedMaterials':{'binding-thread':2},'completedWorkPhases':1,'requiredWorkPhases':3}
  funds=self.s['sharedFunds'];self.recruit(who)
  self.assertEqual(self.s['sharedFunds'],funds+12);self.assertIsNone(self.s['containment']['project']);self.assertIsNone(self.s['containment']['cases'][who]['chamberId'])
  self.assertEqual(self.s['containment']['cases'][who]['status'],'released')
  self.assertNotIn('containment:sabine',self.s['characterDevelopment']['founder']['advancementAwards'])
  self.act('advance');self.assertIn(who,g.household_members(self.s));g.public_state(self.s)
 def test_no_room_failure_is_atomic(self):
  for r in self.s['housingRooms'].values():r['status']='complete';r['reservedBeds']=0
  for k,r in self.s['housingRooms'].items():r['reservedBeds']=g.HOUSING_ROOMS[k]['capacityBeds']-int(self.s['bedroomAssignments'].get('founder')==k)
  self.reject('cheat-recruit',characterId='all')
 def test_invalid_locked_and_away_cheats_are_atomic(self):
  for who in (None,[],True,'not-a-person','founder'):self.reject('cheat-recruit',characterId=who)
  self.act('cheat-toggle',enabled=False);self.reject('cheat-recruit',characterId='all');self.act('cheat-toggle',enabled=True)
  self.s['expedition']={'siteId':'old-waterworks','stage':'outward','partyIds':['founder'],'companionIds':[]}
  self.reject('cheat-recruit',characterId='all')
 def test_all_current_room_types(self):
  for k in c.view(self.s)['rooms']:
   if k in g.HOUSING_ROOMS and self.s['housingRooms'][k]['status']=='complete':continue
   if k in h.ROOMS and h.ready(self.s,k):continue
   self.act('cheat-build',buildingId=k)
  self.assertEqual(self.s['headquarters']['rooms']['watchtower'],'complete')
  self.assertEqual(self.s['housingRooms']['annex-suite-5']['status'],'complete');g.public_state(self.s)
  self.assertTrue(all(r['status']=='ready' for r in self.s['containment']['chambers'].values()))
 def test_foundation_restoration_keeps_discovery_tests_and_ritual_requirements(self):
  import foundation_chamber as f
  from test_foundation_chamber import FoundationChamberTests
  t=FoundationChamberTests();t.setUp();self.s=t.s;self.act('cheat-toggle',enabled=True)
  self.assertNotIn(f.ROOM,c.view(self.s)['rooms']);self.reject('cheat-build',buildingId=f.ROOM)
  t.act('foundation-start');t.step('connections');t.step('instructions')
  self.assertIn(f.ROOM,c.view(self.s)['rooms'])
  t.act('foundation-task',stepId='restoration',methodId='careful')
  paid=(self.s['sharedFunds'],deepcopy(self.s['materialInventory']),self.s['dayNumber'],self.s['currentDayPhase'])
  self.act('cheat-build',buildingId=f.ROOM)
  self.assertEqual(paid,(self.s['sharedFunds'],self.s['materialInventory'],self.s['dayNumber'],self.s['currentDayPhase']))
  self.assertIn('restoration',f.saved(self.s)['completed']);self.assertTrue(h.ready(self.s,f.ROOM))
  self.assertIsNone(f.saved(self.s)['job']);self.assertEqual(self.s['founderAssignment'],'rest')
  self.assertFalse(f.ready(self.s));self.assertIsNone(f.saved(self.s)['blessing'])
  self.reject('cheat-build',buildingId=f.ROOM)
  g.public_state(self.s)
 def test_funded_hq_room_finished_without_repeated_work(self):
  self.s['sharedFunds']=100;self.act('hq-build',roomId='entry-hall')
  funds=self.s['sharedFunds'];self.act('cheat-build',buildingId='entry-hall');self.assertIsNone(h.project_for(self.s));self.assertEqual(self.s['sharedFunds'],funds)
  self.act('advance');self.assertEqual(self.s['headquarters']['rooms']['entry-hall'],'complete')
 def test_food_gear_advancement_and_health(self):
  start=self.s['provisions']['stock'];self.act('cheat-resource',resourceId='provisions',quantity=20);self.assertEqual(self.s['provisions']['stock'],start+20)
  self.act('cheat-gear',recordId='steel-sword',ownerId='founder');self.assertTrue(any(x['definitionId']=='steel-sword' and x['ownerId']=='founder' for x in self.s['armoury']['items'].values()))
  self.act('cheat-advancement',ownerId='founder',quantity=7);self.assertEqual(g.character_sheet(self.s,'founder')['availableAdvancement'],7)
  self.s['fieldMagic']['vitality']['founder']=1;self.act('cheat-heal',ownerId='founder');self.assertEqual(self.s['fieldMagic']['vitality']['founder'],6)
  for q in (True,-1,10001,'5'):self.reject('cheat-advancement',quantity=q)
  self.assertTrue(self.s['testing']['used'])
 def test_save_retry_and_reload(self):
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d,start_type='fresh')
   def payload(a):return {'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':a}
   store.action(payload({'type':'cheat-toggle','enabled':True}));p=payload({'type':'cheat-recruit','characterId':'all'})
   first=store.action(p);self.assertEqual(store.action(p),first);self.assertEqual(GameStore(d).read(),first)
   self.assertEqual(len(g.household_members(first)),17)
 def test_later_chapter_introductions_keep_cheated_residents(self):
  import test_first_patrol as patrol, test_roads_we_keep as roads
  t=patrol.PatrolTests();t.setUp();g.apply_action(t.s,{'type':'cheat-toggle','enabled':True});g.apply_action(t.s,{'type':'cheat-recruit','characterId':'rhess'})
  profile=deepcopy(t.s['people']['rhess']);bed=t.s['bedroomAssignments']['rhess'];t.start();t.finish()
  self.assertEqual(profile,t.s['people']['rhess']);self.assertEqual(bed,t.s['bedroomAssignments']['rhess']);self.assertIn('rhess',g.household_members(t.s))
  self.assertEqual(len([r for r in t.s['summoningContacts'].values() if r['personId']=='rhess']),1)
 def test_mira_conversation_invitation_and_personal_scene_work(self):
  self.recruit('mira');self.act('talk',topic='research');self.assertEqual(self.s['invitationStatus'],'available')
  self.act('share-personal-chapter',characterId='mira',sceneId='mira:0',choice='gentle')
  self.assertTrue(g.character_at_castle(self.s,'mira'));self.assertEqual(self.s['startType'],'fresh')
 def test_cheat_catalogue_is_pure_and_hidden_until_enabled(self):
  before=deepcopy(self.s);self.assertEqual(len(c.view(self.s)['companions']),16);self.assertEqual(self.s,before)
  self.act('cheat-toggle',enabled=False);self.assertIsNone(g.public_state(self.s)['cheatsView'])
 def test_generated_residents_use_the_current_fifty_one_person_limit(self):
  for key in g.HOUSING_ROOMS:
   if self.s['housingRooms'][key]['status']!='complete':self.act('cheat-build',buildingId=key)
  for index in range(50):self.act('cheat-character',ancestry='Human',name='Test Resident '+str(index+1))
  self.assertEqual(len(g.household_members(self.s)),51)
  self.reject('cheat-character',ancestry='Human',name='One too many')
