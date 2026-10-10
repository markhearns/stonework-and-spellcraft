from copy import deepcopy
from pathlib import Path
import json,tempfile,unittest,uuid
import game as g
import keeping_hearth as k
import containment as c
import resident_specialties as specialties
import character_quests as quests
import living_stories
import test_room_to_grow as chapter_three
from server import GameStore

class KeepingHearthTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  chapter_three.RoomToGrowTests.setUpClass();t=chapter_three.RoomToGrowTests();t.setUp();t.plan();t.play();cls.beginning=deepcopy(t.s)
 def setUp(self):self.s=deepcopy(self.beginning)
 def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def money(self,n):
  if self.s['sharedFunds']>=n:return
  self.act('assign-founder',assignment='commissions')
  while self.s['sharedFunds']<n:self.advance()
  self.act('assign-founder',assignment='rest')
 def reject(self,a):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
  self.assertEqual(before,self.s)
 def play(self,defense='barriers',choice='capture',stop=None,transfer=False):
  if not k.saved(self.s):self.act('hearth-start')
  for _ in range(220):
   before=deepcopy(self.s);v=k.view(self.s);self.assertEqual(before,self.s);stage=v['stage']
   if stage=='complete' or stage==stop:return
   if self.s['expedition']:
    e=self.s['expedition']
    self.act('choose-expedition-approach',approach='survey') if e['stage']=='awaiting-choice' else self.act('return-expedition') if e['stage']=='ready-to-return' else self.advance()
   elif stage in ('intrusion','review'):self.act('hearth-scare',choice='confront' if stage=='intrusion' else 'review')
   elif stage=='inspection':self.act('hearth-inspect',area=next(x['id'] for x in v['inspections'] if not x['complete']))
   elif stage=='design':self.act('hearth-design',choice=defense)
   elif stage=='return':self.act('hearth-return',choice=choice if v['newEncounter'] else 'review')
   elif stage=='tutorial':self.act('hearth-lesson',lessonId=next(x['id'] for x in v['lessons'] if not x['complete'] and x['ready']))
   elif stage=='closing':self.act('hearth-finish')
   elif transfer and v['canTransfer']:self.act('transfer-containment',characterId='sabine')
   else:
    n=v['next'];self.assertIsNotNone(n,v);self.assertFalse(n.get('blockers'),n)
    if n['id']=='preservation':self.act('start-expedition',siteId='reedbank-waystation',carryLantern=bool(self.s['craftedArtifacts'].get('warming-lantern')))
    else:self.assertIsNotNone(n['action'],n);g.apply_action(self.s,n['action'])
   self.s=g.migrate_state(json.loads(json.dumps(self.s)))
  self.fail(repr(k.view(self.s)))
 def recruit(self):
  contact='encounter-sabine'
  for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=contact,topic=topic)
  self.act('summoning-invite',contactId=contact,roomId='lower-suite');self.advance()
  self.act('summoning-ask-stay',contactId=contact);self.act('summoning-household-decision',contactId=contact,decision='invite-to-stay')
 def complete_quest(self,key):
  self.act('assign-founder',assignment='rest');self.act('assign-character',characterId='sabine',assignment='rest')
  for _ in range(20):
   q=next(q for q in quests.records(self.s) if q['id']==key)
   if q['status']=='complete':return
   if q['status']=='ready':self.act('choose-quest-method',questId=key,methodId='patient')
   elif q['status']=='working':self.advance()
   else:self.act('talk-character-quest',questId=key,choice='warm')
  self.fail(q)
 def test_capture_release_and_both_defenses_use_normal_work_and_reload(self):
  for defense in k.DEFENSES:
   with self.subTest(defense=defense):
    self.s=deepcopy(self.beginning);beds=deepcopy(self.s['bedroomAssignments']);lore=deepcopy(self.s['privateCastleLore']);self.play(defense)
    self.assertEqual(k.stage(self.s),'complete');self.assertEqual(k.case(self.s)['status'],'released')
    self.assertEqual(self.s['bedroomAssignments'],beds);self.assertNotIn('sabine',g.household_members(self.s))
    self.assertFalse(self.s['testing']['used']);self.assertEqual(lore,self.s['privateCastleLore'])
    self.assertTrue(all(h['complete'] for h in k.view(self.s)['requirements']));self.assertEqual(len(k.saved(self.s)['lessons']),4)
    self.assertEqual(self.s['people']['sabine'],c.SABINE['profile']);self.assertEqual(k.case(self.s)['chapterOrigin'],'keeping-hearth')
    self.assertIn('tried to take',c.case_definition(self.s,'sabine')['topics']['account'])
    self.reject({'type':'hearth-return','choice':'capture'});self.reject({'type':'hearth-finish'})
 def test_parley_and_transfer_do_not_force_recruitment_or_rewrite_identity(self):
  self.play(choice='parley',transfer=True);self.assertEqual(k.case(self.s)['status'],'transferred');self.assertEqual(c.view(self.s)['occupiedCapacity'],0)
  self.assertNotIn('sabine',g.household_members(self.s));self.assertEqual(self.s['summoningContacts']['encounter-sabine']['contactStatus'],'closed')
 def test_drive_away_keeps_original_future_encounter_possible(self):
  self.play(choice='drive-away');self.assertEqual(k.case(self.s)['status'],'unmet');self.assertNotIn('sabine',self.s['people'])
  self.assertFalse(k.quiet_ready(self.s));self.assertEqual(c.view(self.s)['occupiedCapacity'],0)
 def test_resident_specialty_quests_and_household_scenes_are_real(self):
  self.play();self.recruit();self.assertIn('sabine',g.household_members(self.s));profile=deepcopy(self.s['people']['sabine'])
  self.act('choose-living-scene',sceneId='sabine:0',choice='release')
  self.assertTrue(any(q['id']=='personal:sabine-keys' for q in quests.records(self.s)))
  self.money(28);self.act('hq-job',jobId='specialty-sabine');self.advance(3);self.assertTrue(specialties.active(self.s,'sabine'))
  self.money(14)
  # Components may need normal purchases after the chapter.
  for key,n in c.CHAMBERS['echo-2']['materials'].items():
   while self.s['materialInventory'][key]-self.s['materialReserveTargets'][key]<n:self.money(g.MATERIALS[key]['price']);self.act('buy-material',materialId=key)
  self.money(14);self.act('build-containment',chamberId='echo-2');self.assertEqual(self.s['containment']['project']['requiredWorkPhases'],1);self.advance()
  self.assertEqual(self.s['containment']['chambers']['echo-2']['status'],'ready')
  for key in ('personal:sabine','personal:sabine-keys'):self.complete_quest(key)
  self.assertEqual(len([x for x in quests.view(self.s)['keepsakes'] if x['who']=='sabine']),2)
  self.assertEqual(profile,self.s['people']['sabine'])
  for stage in (0,1):self.act('share-specialist-chapter',characterId='sabine',sceneId='sabine:'+str(stage),choice='craft')
  self.act('share-room-activity',characterId='sabine',sceneId='sabine:dungeons',choice='quiet')
  self.act('share-specialist-chapter',characterId='sabine',sceneId='sabine:2',choice='company')
  self.assertIn('dungeons',living_stories.ROUTINES['sabine']['morning'])
 def test_old_resident_is_never_recast_as_a_thief(self):
  self.play();self.recruit();self.s.pop('keepingHearth');before=deepcopy(self.s['people']['sabine']);bed=self.s['bedroomAssignments']['sabine'];case=deepcopy(k.case(self.s))
  self.play();self.assertEqual(k.saved(self.s)['mode'],'established');self.assertEqual(k.saved(self.s)['returnChoice'],'review')
  self.assertEqual(before,self.s['people']['sabine']);self.assertEqual(case,k.case(self.s));self.assertEqual(bed,self.s['bedroomAssignments']['sabine'])
 def test_atomic_guards_and_read_only_views(self):
  before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s);self.assertNotIn('keepingHearth',self.s)
  self.act('hearth-start')
  for a in ({'type':'hearth-return','choice':'capture'},{'type':'hearth-design','choice':'wards'},
            {'type':'hearth-scare','choice':'companion','characterId':'sabine'},{'type':'hearth-scare','choice':[]},
            {'type':'hearth-lesson','lessonId':'release'},{'type':'hearth-finish'},{'type':'hearth-visibility','enabled':'false'}):self.reject(a)
  items=deepcopy(self.s['materialInventory']);self.advance(4);self.assertEqual(items,self.s['materialInventory']);self.assertEqual(k.stage(self.s),'intrusion')
 def test_existing_paid_care_keeps_duration_when_specialty_is_installed(self):
  self.s['sharedFunds']=100
  for key in self.s['materialInventory']:self.s['materialInventory'][key]=20
  self.act('build-containment',chamberId='echo-1');old=deepcopy(self.s['containment']['project'])
  self.s['headquarters']['stock']['specialty:sabine']=1
  self.assertEqual(self.s['containment']['project'],old);self.assertEqual(c.view(self.s)['chambers']['echo-2']['requiredWorkPhases'],1)
  self.advance();self.assertEqual(self.s['containment']['project']['completedWorkPhases'],1);self.advance();self.assertIsNone(self.s['containment']['project'])
  self.assertEqual(c.work_phases(self.s,c.CASES['sabine']),2)
 def test_retry_persists_one_capture_identity(self):
  self.play(stop='return');self.act('hearth-return',choice='capture');self.play(stop='return')
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d,start_type='fresh')
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'hearth-return','choice':'capture'}}
   first=store.action(request);self.assertEqual(first,store.action(request));self.assertEqual(first,GameStore(d).read())
   self.assertEqual(first['containment']['cases']['sabine']['status'],'arrival-pending');self.assertEqual(list(first['people']).count('sabine'),1)
 def test_every_authored_expedition_has_a_real_optimized_image(self):
  from PIL import Image
  for site in g.EXPEDITION_SITES:
   path=Path('static'+g.ORIGINAL_ASSETS[site]);self.assertTrue(path.is_file(),site)
   with Image.open(path) as im:self.assertGreater(im.width,400)
  for row in json.loads(Path('docs/ART_V078.json').read_text())['assets']:
   self.assertLess(row['bytes'],520000);self.assertLess(row['bytes'],row['sourceBytes']//4)

if __name__=='__main__':unittest.main()
