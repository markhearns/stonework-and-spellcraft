from copy import deepcopy
from pathlib import Path
import unittest,tempfile,json,sqlite3,uuid
import game as g
import character_customization as c
import customization_content as content
import character_approaches as apt
import character_pool
import test_magic_overhaul as magic
import test_household_chapters as household
from server import GameStore

class CustomizationTests(unittest.TestCase):
 def setUp(self):self.s=magic.MagicTests.rich(self)
 def act(self,kind,who='founder',**kw):g.apply_action(self.s,{'type':kind,'characterId':who,**kw})
 def reject(self,kind,who='founder',**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,who,**kw)
  self.assertEqual(old,self.s)
 def style(self,who='founder',**kw):
  data=dict(name='Quiet evening',occasion='leisure',colour='teal',garments=['soft-blouse','long-skirt','slippers'],notes='A ribbon at the wrist.');data.update(kw)
  self.act('save-personal-style',who,**data)
 def test_read_purity_and_empty_migration(self):
  before=deepcopy(self.s);c.view(self.s);self.assertEqual(before,self.s)
  self.s['schemaVersion']=54;self.s.pop('customization');before=deepcopy(self.s);g.migrate_state(self.s)
  self.assertEqual(self.s['customization'],{'people':{},'memories':{}});self.assertEqual(self.s['sharedFunds'],before['sharedFunds']);self.assertEqual(self.s['schemaVersion'],66)
 def test_appearance_is_descriptive_and_prompt_aware(self):
  before=deepcopy(self.s['characterBuilds']);art=deepcopy(self.s['assetOverrides'])
  self.act('save-personal-appearance',appearance={'hairStyle':'Braided','hairColour':'copper','markings':'a small old scar'})
  self.assertEqual(before,self.s['characterBuilds']);self.assertEqual(art,self.s['assetOverrides'])
  self.assertIn('copper',c.portrait_brief(self.s,'founder'))
  from founder_setup import portrait_prompt
  self.assertIn('copper',portrait_prompt(self.s))
  self.reject('save-personal-appearance',appearance={'powers':'flight'})
  self.reject('save-personal-appearance',appearance={'eyes':'x'*161})
 def test_garment_compatibility_and_selection(self):
  self.style();self.act('wear-personal-style',styleId='Quiet evening');self.assertEqual(c.style(self.s,'founder')['name'],'Quiet evening')
  self.reject('save-personal-style',name='bad',occasion='everyday',colour='teal',garments=['linen-shirt'])
  self.reject('save-personal-style',name='bad',occasion='formal',colour='teal',garments=['evening-dress','trousers'])
  self.reject('delete-personal-style',styleId='Quiet evening');self.act('clear-personal-style');self.act('delete-personal-style',styleId='Quiet evening')
 def test_private_styles_require_real_partnership_and_respect_pause(self):
  self.style('mira',name='Private velvet',occasion='private',garments=['silk-slip','robe'])
  self.reject('wear-personal-style','mira',styleId='Private velvet')
  self.s['romance']['people']['mira']={'level':3,'mode':'open','deferred':False}
  self.act('wear-personal-style','mira',styleId='Private velvet');self.assertIsNotNone(c.style(self.s,'mira'))
  self.act('pause-romance','mira');self.act('clear-personal-style','mira');self.reject('wear-personal-style','mira',styleId='Private velvet')
 def test_preparations_restore_real_tool_practices_and_spells(self):
  self.s['craftedArtifacts']['scholars-folio']=1
  g.apply_action(self.s,{'type':'claim-working-tool','ownerId':'founder','toolId':'scholars-folio'})
  tool=next(iter(self.s['personalEquipment']))
  g.apply_action(self.s,{'type':'prepare-working-tool','ownerId':'founder','itemId':tool})
  self.act('save-complete-preparation',name='Explorer');before=c.snapshot(self.s,'founder')
  g.apply_action(self.s,{'type':'stow-working-tool','ownerId':'founder'})
  self.act('load-complete-preparation',name='Explorer');self.assertEqual(before,c.snapshot(self.s,'founder'))
  self.s['personalEquipment'][tool]['ownerId']='mira';self.reject('load-complete-preparation',name='Explorer')
  self.assertTrue(c.view(self.s)['people']['founder']['preparations'][0]['blockers'])
 def test_preparation_invalid_spell_cannot_partially_change_other_slots(self):
  self.act('save-complete-preparation',name='Explorer')
  c.person(self.s,'founder')['preparations']['Explorer']['spells']=['does-not-exist']
  self.reject('load-complete-preparation',name='Explorer')
 def test_specializations_earned_single_active_and_retraining_suspends(self):
  self.reject('choose-specialization',specialization='envoy')
  self.s['characterBuilds']['founder']['attributes']['charisma']=6;self.s['characterSkills']['founder']['diplomacy']=2
  self.act('choose-specialization',specialization='envoy')
  r=apt.score(self.s,'founder',apt.spec('charisma','diplomacy'));self.assertEqual(r['total'],11);self.assertIn('specialization 1',r['detail'])
  self.s['characterSkills']['founder']['diplomacy']=0;self.assertEqual(c.bonus(self.s,'founder','diplomacy'),0)
 def test_healer_has_bounded_separate_effect(self):
  self.s['characterBuilds']['founder']['attributes']['intelligence']=6;self.s['characterSkills']['founder']['channeling']=2
  self.act('choose-specialization',specialization='healer');self.assertEqual(apt.healing_bonus(self.s,'founder'),2);self.assertEqual(c.bonus(self.s,'founder','channeling'),0)
 def test_preferences_reveal_and_idle_location_preserve_work(self):
  self.assertIsNone(c.view(self.s)['people']['mira']['preferences'])
  self.reject('choose-leisure-room','mira',roomId='common-room')
  self.act('share-personal-scene','mira',sceneId='tastes',choice='warm');self.assertEqual(c.preferences(self.s,'mira')['hobby'],'bad poetry')
  self.act('choose-leisure-room','mira',roomId='common-room')
  import room_life
  self.s['currentDayPhase']='afternoon';g.set_character_assignment(self.s,'mira','rest');self.assertEqual(room_life.location(self.s,'mira'),'common-room')
  g.set_character_assignment(self.s,'mira','archive');self.assertEqual(room_life.location(self.s,'mira'),'library')
  self.reject('save-personal-preferences','mira',preferences={'hobby':'anything'})
 def test_authored_preferences_distinct_all_fourteen_and_no_farming(self):
  self.assertEqual(len(content.PROFILES),15);self.assertEqual(len({p[5] for p in content.PROFILES.values()}),15)
  for who in content.PROFILES:
   if who not in g.household_members(self.s):household.HouseholdChapterTests.member(self,who)
   before=(self.s['dayNumber'],self.s['currentDayPhase'],self.s['sharedFunds'])
   self.act('share-personal-scene',who,sceneId='tastes',choice='warm');self.reject('share-personal-scene',who,sceneId='tastes',choice='warm')
   self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase'],self.s['sharedFunds']))
 def test_private_and_style_scenes_require_correct_milestones(self):
  self.act('share-personal-scene','mira',sceneId='tastes',choice='warm');self.style('mira');self.act('wear-personal-style','mira',styleId='Quiet evening')
  self.reject('share-personal-scene','mira',sceneId='style',choice='warm')
  self.s['romance']['people']['mira']={'level':1,'mode':'open','deferred':False}
  self.reject('share-personal-scene','mira',sceneId='style',choice='playful')
  self.act('share-personal-scene','mira',sceneId='style',choice='warm')
  self.reject('share-personal-scene','mira',sceneId='private',choice='warm')
  self.s['romance']['people']['mira']['level']=3;self.act('choose-leisure-room','mira',roomId='common-room')
  self.act('share-personal-scene','mira',sceneId='private',choice='playful')
  self.assertIn('slow kiss',c.saved(self.s)['memories']['mira:private']['response'])
 def test_corner_cost_once_reserves_and_room_ownership(self):
  before=self.s['sharedFunds'];thread=self.s['materialInventory']['binding-thread']
  self.act('fit-personal-corner',cornerId='reading',roomId='library',name='My shelf');self.assertEqual(self.s['sharedFunds'],before-4);self.assertEqual(self.s['materialInventory']['binding-thread'],thread-1)
  self.act('put-away-personal-corner');self.act('fit-personal-corner',cornerId='reading',roomId='library',name='Still my shelf');self.assertEqual(self.s['sharedFunds'],before-4)
  self.reject('fit-personal-corner',cornerId='reading',roomId='workshop',name='Wrong room')
  self.s['materialReserveTargets']['binding-thread']=self.s['materialInventory']['binding-thread'];self.reject('fit-personal-corner',cornerId='music',roomId='common-room',name='Reserved')
 def test_context_only_actual_participants_no_future_replies(self):
  self.assertEqual(c.context(self.s,'mira')['memories'],[])
  self.act('share-personal-scene','mira',sceneId='tastes',choice='warm')
  self.assertEqual(len(c.context(self.s,'mira')['memories']),1);self.assertEqual(c.context(self.s,'tamsin')['memories'],[])
  self.assertNotIn('slow kiss',json.dumps(c.context(self.s,'mira')))
 def test_actual_mentorship_reflection_once(self):
  self.s['characterSkills']['mira']['scholarship']=2
  g.award_advancement(self.s,'founder','lesson-test',10,'Learning')
  g.apply_action(self.s,{'type':'start-lesson','learnerId':'founder','teacherId':'mira','subjectKind':'skill','targetId':'scholarship'})
  self.assertEqual(c.mentor_rows(self.s,'founder'),[])
  self.act('advance');row=c.mentor_rows(self.s,'founder')[0]
  self.act('share-mentor-reflection',lessonId=row['id']);self.reject('share-mentor-reflection',lessonId=row['id'])
  self.assertEqual(c.saved(self.s)['memories'][row['id']]['participants'],['mira','founder'])
 def test_recruit_appearance_choices_remain_compatible(self):
  selection=character_pool.select(self.s,'appearance-selection',{'ancestry':'Human','hair':character_pool.HAIR[2],'build':character_pool.BUILDS[3]})
  self.assertEqual(selection['appearance']['hair'],character_pool.HAIR[2]);self.assertEqual(selection['appearance']['build'],character_pool.BUILDS[3])
  with self.assertRaises(g.RuleError):character_pool.select(self.s,'bad-selection',{'hair':'invalid'})
 def test_away_edits_rejected_and_store_reload_backup(self):
  self.s['founderAssignment']='expedition';self.s['expedition']={'siteId':'old-waterworks','stage':'outbound'}
  self.reject('save-personal-appearance',appearance={})
  with tempfile.TemporaryDirectory() as directory:
   st=GameStore(directory);s=st.read();s['schemaVersion']=54;s.pop('customization')
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
   st=GameStore(directory);s=st.read();self.assertEqual(s['schemaVersion'],66);self.assertTrue(Path(directory,'campaign-before-schema-54-to-66.sqlite3').exists())
   a={'action':{'type':'save-personal-appearance','characterId':'founder','appearance':{'hairStyle':'Braided'}},'requestId':str(uuid.uuid4()),'expectedRevision':s['revision']}
   first=st.action(a);again=st.action(a);self.assertEqual(first,again);self.assertEqual(GameStore(directory).read()['customization']['people']['founder']['appearance']['hairStyle'],'Braided')
 def test_saved_spells_share_capacity_and_pending_cast_is_atomic(self):
  t=magic.MagicTests();t.s=self.s
  spell=t.learned('mending-light')
  self.act('save-complete-preparation',name='Healing');self.act('prepare-spells',spellIds=[])
  self.act('load-complete-preparation',name='Healing');self.assertEqual(self.s['preparedSpells']['founder'],[spell])
  self.s['spellWork']['founder']={'kind':'cast','spellId':spell,'committedInputs':{}}
  self.reject('load-complete-preparation',name='Healing')
 def test_imported_spells_restore_and_over_capacity_is_atomic(self):
  import public_workshop as w
  ids=[r['id'] for r in w.records('spell-construction').values() if r['mechanicsProposalId']][:3]
  self.s['publicWorkshop']['testedSpells']['founder']=ids
  g.apply_action(self.s,{'type':'public-prepare-spells','ownerId':'founder','recordIds':ids[:1]})
  self.act('save-complete-preparation',name='Public explorer')
  g.apply_action(self.s,{'type':'public-prepare-spells','ownerId':'founder','recordIds':[]})
  self.act('load-complete-preparation',name='Public explorer');self.assertEqual(self.s['publicWorkshop']['preparedSpells']['founder'],ids[:1])
  c.person(self.s,'founder')['preparations']['Public explorer']['publicSpells']=ids
  self.reject('load-complete-preparation',name='Public explorer')
 def test_mementos_must_be_real_personal_history(self):
  self.assertEqual(c.mementos(self.s,'mira'),[])
  self.reject('fit-personal-corner','mira',cornerId='reading',roomId='library',name='History',mementoId='invented')
  self.act('share-personal-scene','mira',sceneId='tastes',choice='warm')
  self.act('fit-personal-corner','mira',cornerId='reading',roomId='library',name='History',mementoId='memory:mira:tastes')
  self.assertEqual(c.person(self.s,'mira')['space']['memento']['source'],'A shared memory, day 1')
 def test_ui_views_do_not_reveal_private_scene_before_unlock(self):
  row=next(x for x in c.view(self.s)['people']['mira']['scenes'] if x['id']=='private')
  self.assertEqual(row['opening'],'');self.assertIsNone(row['memory']);self.assertTrue(row['blockers'])
 def test_favourite_refreshment_costs_once_and_does_not_set_romance(self):
  self.reject('offer-personal-refreshment','mira')
  self.act('share-personal-scene','mira',sceneId='tastes',choice='warm');before=self.s['sharedFunds'];romance=deepcopy(self.s['romance'])
  self.act('offer-personal-refreshment','mira');self.assertEqual(self.s['sharedFunds'],before-2);self.assertEqual(romance,self.s['romance'])
  self.assertIn('spiced tea',c.saved(self.s)['memories']['mira:refreshment']['opening']);self.reject('offer-personal-refreshment','mira')
 def test_illustrated_and_descriptive_wardrobe_have_one_active_selection(self):
  self.style('mira');self.act('wear-personal-style','mira',styleId='Quiet evening')
  import household_content
  self.assertEqual(household_content.wardrobe_context(self.s,'mira')['name'],'Quiet evening')
  self.s['outfitProgression']['mira']={'selected':None,'invitations':{'2':{}}}
  self.act('choose-outfit','mira',tier='2');self.assertIsNone(c.style(self.s,'mira'))
  self.act('wear-personal-style','mira',styleId='Quiet evening');self.assertIsNone(self.s['outfitProgression']['mira']['selected'])
  self.act('wardrobe',outerLayer='plum-shawl');self.assertIsNone(c.style(self.s,'mira'))
