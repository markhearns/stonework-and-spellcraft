from copy import deepcopy
import json,tempfile,unittest,uuid
import game as g
import field_magic as f
import spell_support as support
import lasting_rituals as rituals
from server import GameStore

class MagicTests(unittest.TestCase):
 def setUp(self):self.s=self.rich()
 def rich(self):
  s=g.new_campaign();s['sharedFunds']=10000;s['restorationStatus']='complete'
  for k in s['materialInventory']:s['materialInventory'][k]=200
  for who in ('founder','mira'):
   for p in g.PRINCIPLE_NAMES:g.learn_for_character(s,who,p)
  s['researchStatus']='complete'
  for room in g.headquarters.ROOMS:
   if not g.headquarters.ROOMS[room]['legacy']:s['headquarters']['rooms'][room]='complete'
  return s
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def reject(self,kind,**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(before,self.s)
 def learned(self,form,who='founder',real=False):
  d=g.SPELL_FORMS[form];parts=[next(k for k,m in g.MATERIALS.items() if p in m['properties']) for p in d['requiredProperties']]
  self.act('inscribe-spell',characterId=who,formId=form,materials=parts,name='Injected name',intent='Infinite power')
  spell=self.s['spellbook'][-1]
  if real:self.act('test-spell',spellId=spell['id']);self.advance(2)
  else:spell['status']='learned'
  self.act('prepare-spells',characterId=who,spellIds=[spell['id']]);return spell['id']
 def at(self,step):
  if not self.s['expedition']:
   self.act('start-expedition',siteId=f.SITE);self.advance();self.act('choose-expedition-approach',approach='survey')
  p=f.initialize(self.s)['aqueduct'];p['completed']=[d['id'] for d in f.STEPS[:next(i for i,d in enumerate(f.STEPS) if d['id']==step)]];p['pending']=None;f.resume(self.s)
 def cast(self,spell,target='founder'):
  self.act('field-spell',characterId='founder',spellId=spell,targetId=target);self.advance()
 def test_all_thirty_authored_spells_can_be_studied_and_prepared(self):
  self.assertEqual(len(g.SPELL_FORMS),30)
  for form,d in g.SPELL_FORMS.items():
   with self.subTest(form=form):
    self.s=self.rich();key=self.learned(form,real=True);spell=g.spell_by_id(self.s,key)
    self.assertEqual(spell['name'],d['name']);self.assertEqual(spell['intent'],d['description']);self.assertEqual(spell['status'],'learned');self.assertEqual(len(d['ideas']),2)
 def test_missing_secondary_principle_blocks_study_and_casting(self):
  key=self.learned('arc-bolt');self.s['founderKnownPrinciples'].remove('field-calibration');self.at('sentinel')
  self.reject('field-spell',spellId=key,characterId='founder')
 def test_every_obstacle_has_at_least_two_valid_ordinary_or_spell_methods(self):
  for d in f.STEPS:
   self.s=self.rich();self.at(d['id']);rows=f.view(self.s)['methods'];valid=[r['method'] for r in rows if not r['blockers']]
   self.assertGreaterEqual(len(set(valid)),2,d['id'])
 def test_full_mission_without_magic_and_rewards_only_on_return(self):
  self.act('start-expedition',siteId=f.SITE);self.advance();self.act('choose-expedition-approach',approach='survey')
  before=self.s['sharedFunds']
  while f.step(self.s):
   self.act('field-method',method='evade' if f.step(self.s)['tag']=='enemy' else 'mundane')
   while self.s['expedition']['stage']=='working':self.advance()
  self.assertEqual(self.s['sharedFunds'],before);self.assertEqual(self.s['expedition']['stage'],'ready-to-return')
  self.act('return-expedition');self.advance();self.assertEqual(f.progress(self.s)['discoveries'],['survey'])
  self.assertGreater(self.s['sharedFunds'],before);self.reject('start-expedition',siteId=f.SITE)
 def test_water_fire_wind_flight_ice_and_underwater_have_distinct_targets(self):
  for form,step in [('water-jet','fire'),('wind-step','gap'),('borne-flight','tower'),('ice-bind','gap'),('water-walk','flood'),('water-breath','submerged'),('calm-tide','caretaker')]:
   with self.subTest(form=form):
    self.s=self.rich();key=self.learned(form);self.at(step);self.cast(key);self.assertIn(step,f.progress(self.s)['completed'])
  self.s=self.rich();key=self.learned('wind-step');self.at('tower');self.reject('field-spell',spellId=key,characterId='founder')
 def test_elemental_damage_weakness_immunity_and_anti_undead(self):
  for form,step,expected in [('water-jet','ember',2),('ice-bind','ember',2),('arc-bolt','sentinel',0),('dawn-lance','bones',0),('fire-lance','bones',3)]:
   self.s=self.rich();key=self.learned(form);self.at(step);self.cast(key);self.assertEqual(f.progress(self.s)['enemyHp'][step],expected)
   if form=='ice-bind':self.assertEqual(f.vitality(self.s,'founder'),6)
  self.s=self.rich();key=self.learned('fire-lance');self.at('ember');self.reject('field-spell',spellId=key,characterId='founder')
  self.s=self.rich();key=self.learned('dawn-lance');self.at('sentinel');self.reject('field-spell',spellId=key,characterId='founder')
 def test_healing_first_aid_and_rest_are_bounded(self):
  key=self.learned('mending-light');self.at('bones');f.initialize(self.s)['vitality']['founder']=1
  self.cast(key);self.assertEqual(f.vitality(self.s,'founder'),4)
  self.act('field-method',method='bandage');self.advance();self.assertEqual(f.vitality(self.s,'founder'),6)
  self.reject('field-method',method='bandage');self.act('return-expedition');self.advance()
  f.initialize(self.s)['vitality']['founder']=1;self.act('assign-founder',assignment='rest');expected=4 if self.s['currentDayPhase']=='evening' else 2;self.advance();self.assertEqual(f.vitality(self.s,'founder'),expected)
 def test_suggestion_pays_exact_bargain_and_does_not_change_relationship(self):
  key=self.learned('silver-tongue');self.at('caretaker');before=self.s['sharedFunds'];rel=self.s['relationshipDescription']
  self.cast(key);self.assertEqual(self.s['sharedFunds'],before-2);self.assertEqual(self.s['relationshipDescription'],rel)
 def test_decoy_and_scout_are_temporary_and_consumed_by_valid_uses(self):
  key=self.learned('mirror-decoy');self.at('bones');self.cast(key)
  self.act('field-method',method='mundane');self.advance();self.assertEqual(f.vitality(self.s,'founder'),6);self.assertEqual(f.progress(self.s)['buffs']['founder']['decoy'],1)
  self.act('field-method',method='lure');self.advance();self.assertIn('bones',f.progress(self.s)['completed'])
  self.act('return-expedition');self.advance();self.assertEqual(f.progress(self.s)['buffs'],{})
  self.s=self.rich();key=self.learned('wisp-scout');self.at('fire');self.cast(key);self.assertIn('caretaker',f.progress(self.s)['scoutingReport'])
  self.act('field-method',method='mundane');self.assertEqual(self.s['expedition']['remainingWorkPhases'],1)
 def test_strength_insight_haste_reduce_matching_actions_only(self):
  for form,stage in [('giant-grasp','stone'),('lucid-sight','runes'),('borrowed-hour','submerged')]:
   self.s=self.rich();key=self.learned(form);self.at(stage);self.cast(key);self.act('field-method',method='mundane')
   self.assertEqual(self.s['expedition']['remainingWorkPhases'],2 if stage=='submerged' else 1)
 def test_retreat_refunds_pending_inputs_and_keeps_completed_obstacles(self):
  key=self.learned('silver-tongue');self.at('caretaker');before=self.s['sharedFunds'];stock=deepcopy(self.s['materialInventory'])
  self.act('field-spell',spellId=key,characterId='founder');self.act('return-expedition');self.advance()
  self.assertEqual(self.s['sharedFunds'],before);self.assertEqual(self.s['materialInventory'],stock);self.assertIn('fire',f.progress(self.s)['completed']);self.assertNotIn('caretaker',f.progress(self.s)['completed'])
 def test_teleport_requires_anchor_and_never_advances_household_work(self):
  key=self.learned('threshold-fold');self.act('start-expedition',siteId=f.SITE)
  self.reject('field-spell',spellId=key,characterId='founder');self.advance();self.act('return-expedition')
  before=(self.s['dayNumber'],self.s['currentDayPhase']);self.act('field-spell',spellId=key,characterId='founder')
  self.assertIsNone(self.s['expedition']);self.assertEqual(before,(self.s['dayNumber'],self.s['currentDayPhase']))
  self.act('start-expedition',siteId=f.SITE);self.act('field-spell',spellId=key,characterId='founder');self.assertEqual(self.s['expedition']['stage'],'awaiting-choice')
 def test_work_enchantment_recipient_duplicate_guard_and_finite_consumption(self):
  key=self.learned('copy-lamp','mira');self.act('cast-spell',spellId=key);self.advance()
  self.assertEqual(support.remaining(self.s,'founder','copy'),3);self.reject('cast-spell',spellId=key)
  baseline=g.copying_income(self.s)-3;before=self.s['sharedFunds'];self.act('assign-founder',assignment='commissions');self.advance(3)
  self.assertEqual(self.s['sharedFunds']-before,3*(baseline+3));self.assertEqual(support.remaining(self.s,'founder','copy'),0)
 def test_haste_accelerates_funded_housing_and_preserves_unused_charges(self):
  key=self.learned('borrowed-hour','mira');self.act('cast-spell',spellId=key,targetId='founder');self.advance()
  self.assertEqual(support.remaining(self.s,'founder','haste'),3)
  self.act('assign-founder',assignment='rest');self.advance();self.assertEqual(support.remaining(self.s,'founder','haste'),3)
  room='garden-chamber';self.s['housingRooms'][room]['status']='in-progress';self.s['activeHousingRoomId']=room;self.s['founderAssignment']='housing';self.advance()
  self.assertEqual(self.s['housingRooms'][room]['completedWorkPhases'],2);self.assertEqual(support.remaining(self.s,'founder','haste'),2)
 def test_all_eight_rituals_pause_resume_complete_and_suspend(self):
  for key,d in rituals.CATALOGUE.items():
   with self.subTest(ritual=key):
    self.s=self.rich();self.act('begin-lasting-ritual',ritualId=key,leaderId='founder',partnerId='mira');self.advance()
    self.act('assign-resident',assignment='rest');self.advance();self.assertEqual(rituals.state(self.s)['project']['done'],1)
    self.act('resume-lasting-ritual',ritualId=key);self.advance(d['phases']-1);self.assertTrue(rituals.active(self.s,key))
    self.reject('begin-lasting-ritual',ritualId=key,leaderId='founder',partnerId='mira');self.act('toggle-lasting-ritual',ritualId=key,active=False);self.assertFalse(rituals.active(self.s,key))
 def test_ritual_cancel_refunds_exact_cost_and_no_effect(self):
  before=self.s['sharedFunds'];stock=deepcopy(self.s['materialInventory']);self.act('begin-lasting-ritual',ritualId='archive-circle',leaderId='founder',partnerId='mira');self.advance();self.act('cancel-lasting-ritual',ritualId='archive-circle')
  self.assertEqual(before,self.s['sharedFunds']);self.assertEqual(stock,self.s['materialInventory']);self.assertFalse(rituals.active(self.s,'archive-circle'))
 def test_permanent_benefits_use_real_work_and_do_not_create_trade_loops(self):
  r=rituals.initialize(self.s);r['completed']={key:{'active':True} for key in rituals.CATALOGUE}
  self.s['residentAssignment']='garden';before=self.s['materialInventory']['silver-ivy'];harvest=g.garden_harvest(self.s);self.advance();self.assertEqual(self.s['materialInventory']['silver-ivy']-before,harvest['amount'])
  money=self.s['sharedFunds'];self.act('buy-material',materialId='sun-amber');self.act('sell-material',materialId='sun-amber');self.assertEqual(money,self.s['sharedFunds'])
  f.initialize(self.s)['vitality']['founder']=1;self.advance();self.assertEqual(f.vitality(self.s,'founder'),4)
 def test_save_roundtrip_and_readonly_views_preserve_legacy_and_magic(self):
  key=self.learned('water-jet');self.at('fire');self.cast(key)
  before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s);self.assertEqual(g.migrate_state(json.loads(json.dumps(self.s))),self.s)
 def test_store_retries_commit_one_field_action(self):
  self.at('fire')
  with tempfile.TemporaryDirectory() as root:
   store=GameStore(root)
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.s['revision'],'action':{'type':'field-method','method':'equipment'}}
   first=store.action(payload);self.assertEqual(first,store.action(payload));self.assertEqual(first['materialInventory']['binding-thread'],self.s['materialInventory']['binding-thread']-2)


 def test_old_expeditions_accept_six_paid_spell_methods_and_resume_once(self):
  import service_road as road
  for site,forms in [('rainward-observatory',['water-jet','giant-grasp','lucid-sight']), (road.SITE,['water-walk','wind-step','wisp-scout'])]:
   for form in forms:
    with self.subTest(site=site,form=form):
     self.s=self.rich();key=self.learned(form)
     self.s['binderyDiscoveries']=['survey']
     for loc in ('quarry-shelter','ridge-cistern'):g.discoveries_for(self.s,loc).append('survey')
     self.act('start-expedition',siteId=site);self.advance();self.act('choose-expedition-approach',approach='survey')
     if site==road.SITE:
      p=self.s['serviceRoad'];p['route']='orchard' if form=='wind-step' else 'channel';p['completedSteps']=['fork']+([p['route']] if form=='wisp-scout' else []);road.resume(self.s)
     else:
      p=self.s['observatoryProgress']['survey'];p['completedSteps']=[d['id'] for d in g.OBSERVATORY_STEPS[:forms.index(form)]];self.s['expedition']['stage']='encounter-choice'
     before=deepcopy(self.s['materialInventory']);self.act('choose-encounter-method',methodId='spell:'+form)
     spent=deepcopy(self.s['materialInventory'])
     for material,n in g.SPELL_FORMS[form]['castingInputs'].items():self.assertEqual(spent[material],before[material]-n)
     self.act('return-expedition');self.advance();self.act('start-expedition',siteId=site);self.advance();self.act('choose-expedition-approach',approach='survey')
     self.assertEqual(self.s['expedition']['stage'],'working');self.advance()
     self.assertEqual(self.s['materialInventory'],spent);self.assertEqual(g.spell_by_id(self.s,key)['castCount'],1)
 def test_haste_accelerates_actual_equipment_work_and_keeps_unused_charge(self):
  self.s['headquarters']['rooms']['enchanting-room']='not-started'
  self.s['craftedArtifacts']['scholars-folio']=1
  self.act('claim-working-tool',ownerId='founder',toolId='scholars-folio');item=next(iter(self.s['personalEquipment']))
  self.act('upgrade-working-tool',ownerId='founder',itemId=item,materials=['porous-clay','binding-thread'])
  support.resolve(self.s,g.SPELL_FORMS['borrowed-hour'],'founder',[])
  self.advance();self.assertIsNotNone(self.s['personalEquipment'][item]['inscription'])
  self.assertEqual(support.remaining(self.s,'founder','haste'),2)
  self.advance();self.assertEqual(support.remaining(self.s,'founder','haste'),2)
 def test_new_save_migration_preserves_legacy_named_spells_and_art(self):
  key=self.learned('warm-twist');g.spell_by_id(self.s,key)['name']='Old personal name'
  self.s['assetOverrides']['mira']='/user-assets/my-portrait.png'
  self.s['schemaVersion']=46
  for field in ('spellSupports','fieldMagic','lastingRituals'):self.s.pop(field,None)
  g.migrate_state(self.s)
  self.assertEqual(self.s['schemaVersion'],66);self.assertEqual(g.spell_by_id(self.s,key)['name'],'Old personal name')
  self.assertEqual(self.s['assetOverrides']['mira'],'/user-assets/my-portrait.png')
  before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
