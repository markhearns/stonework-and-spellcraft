"""Gameplay reachability and real state transitions for the complete public bundle."""
from copy import deepcopy
import json,tempfile,unittest,uuid
from pathlib import Path
import game as g, public_workshop as w, public_integration as i, public_journeys as j, household_content as h, content_packs
from server import GameStore
from test_public_workshop import finish,rich

NOTE='The actual participants chose this comparison and checked the available notes and materials.'
def act(s,kind,**kw):return w.apply(s,{'type':'public-'+kind,'ownerId':'mira','scopeReviewed':True,'agreed':True,'evidence':NOTE,**kw})
def episode(s,r):
 if r['ancestryRestrictions']:s['people']['mira']['ancestryLabel']=content_packs.REGISTRY[r['ancestryRestrictions'][0]]
 people=['mira']
 if r.get('participants') in ('two-npcs','small-group'):
  s['additionalResidents']['tamsin']['status']='resident';s['bedroomAssignments']['tamsin']='bedchamber';people.append('tamsin')
 act(s,'start-journey',recordId=r['id'],participants=people,requirementEvidence=[NOTE]*len(r['establishedFactRequirements']))
 return next(reversed(s['publicWorkshop']['journeys'].values()))
def open_chapter(s,p):
 c=p['chapters'][p['chapterIndex']]
 act(s,'open-chapter',journeyId=p['id'],requirementEvidence=[NOTE]*len(c['requirements']))
 h.apply(s,{'type':'join-content-scene','sceneId':p['current']['sceneId'],'choiceIndex':0})
 return c

class PublicIntegrationTests(unittest.TestCase):
 def test_every_shipped_record_has_an_explicit_route(self):
  coverage=i.coverage();self.assertEqual(coverage['unroutedRecordIds'],[])
  self.assertEqual(coverage['contentCount'],1599);self.assertEqual(coverage['recordCount'],1918);self.assertEqual(len(coverage['packs']),16)
 def test_all_arcs_relationships_and_care_episodes_complete_through_actual_steps(self):
  for typ in j.NARRATIVE_TYPES:
   for r in w.records(typ).values():
    with self.subTest(record=r['id']):
     s=g.new_campaign();p=episode(s,r);funds=s['sharedFunds'];knowledge=deepcopy(s['residentKnownPrinciples'])
     while p['status']=='active':
      c=open_chapter(s,p)
      if c['phases']:
       with self.assertRaises(g.RuleError):act(s,'resolve-chapter',journeyId=p['id'],resolution='continue')
       act(s,'work-chapter',journeyId=p['id']);finish(s,'mira')
      act(s,'resolve-chapter',journeyId=p['id'],resolution='continue')
     self.assertEqual(p['status'],'complete');self.assertEqual(len(p['steps']),len(p['chapters']))
     self.assertEqual(s['sharedFunds'],funds);self.assertEqual(s['residentKnownPrinciples'],knowledge)
     with self.assertRaises(g.RuleError):act(s,'resolve-chapter',journeyId=p['id'],resolution='continue')
 def test_invitation_preview_decline_pause_and_privacy_do_not_complete_chapters(self):
  s=g.new_campaign();p=episode(s,next(iter(w.records('personal-arc').values())));c=p['chapters'][0]
  act(s,'open-chapter',journeyId=p['id'],requirementEvidence=[NOTE]*len(c['requirements']))
  with self.assertRaises(g.RuleError):act(s,'work-chapter',journeyId=p['id'])
  scene=p['current']['sceneId'];h.apply(s,{'type':'join-content-scene','sceneId':scene,'choiceIndex':1})
  with self.assertRaises(g.RuleError):act(s,'resolve-chapter',journeyId=p['id'],resolution='continue')
  h.apply(s,{'type':'restore-content-scene','sceneId':scene});h.apply(s,{'type':'join-content-scene','sceneId':scene,'choiceIndex':0})
  act(s,'work-chapter',journeyId=p['id']);act(s,'pause-journey',journeyId=p['id']);g.resolve_work(s)
  self.assertEqual(s['publicWorkshop']['jobs']['mira']['completedWorkPhases'],0)
  act(s,'resume-journey',journeyId=p['id']);act(s,'resume');finish(s,'mira')
  act(s,'resolve-chapter',journeyId=p['id'],resolution='revise-goal',evidence='PRIVATE-CHAPTER: she chose to preserve the incomplete notebook.')
  self.assertIn('PRIVATE-CHAPTER',json.dumps(h.context(s,'mira')));self.assertNotIn('PRIVATE-CHAPTER',json.dumps(h.context(s,'tamsin')))
 def test_care_can_end_away_without_work_or_fee_and_blocks_resume(self):
  s=g.new_campaign();p=episode(s,next(iter(w.records('care-case').values())))
  open_chapter(s,p);act(s,'resolve-chapter',journeyId=p['id'],resolution='continue');open_chapter(s,p);act(s,'work-chapter',journeyId=p['id'])
  s['expedition']={'companionId':'mira'};funds=s['sharedFunds'];act(s,'end-care',journeyId=p['id'])
  self.assertEqual(p['status'],'closed');self.assertNotIn('mira',s['publicWorkshop']['jobs']);self.assertEqual(s['sharedFunds'],funds)
  s=g.new_campaign();p=episode(s,next(iter(w.records('care-case').values())));c=p['chapters'][0]
  act(s,'open-chapter',journeyId=p['id'],requirementEvidence=[NOTE]*len(c['requirements']));scene=p['current']['sceneId']
  act(s,'end-care',journeyId=p['id']);self.assertEqual(s['householdScenes'][scene]['status'],'withdrawn')
  with self.assertRaises(g.RuleError):h.apply(s,{'type':'restore-content-scene','sceneId':scene})
 def test_fresh_campaign_field_return_discovery_and_tool_without_cheats(self):
  s=g.new_campaign();before=deepcopy(s);site=next(iter(w.records('site-template').values()));lead=next(r for r in w.records('lead-template').values() if r['siteId']==site['id']);discovery=next(r for r in w.records('discovery-template').values() if r['leadId']==lead['id'])
  def action(kind,**kw):g.apply_action(s,{'type':kind,**kw})
  with self.assertRaises(g.RuleError):act(s,'share-discovery',ownerId='founder',recordId=discovery['id'],evidenceId='missing')
  act(s,'start-field-trip',ownerId='founder',recordId=site['id'],participants=['founder'])
  action('advance');act(s,'field-lead',ownerId='founder',recordId=lead['id']);action('advance');action('advance');act(s,'return-field-trip',ownerId='founder');action('advance')
  receipt=next(x for x in s['publicWorkshop']['receipts'].values() if x.get('observation'))
  act(s,'share-discovery',ownerId='founder',recordId=discovery['id'],evidenceId=receipt['id'])
  with self.assertRaises(g.RuleError):act(s,'share-discovery',ownerId='founder',recordId=discovery['id'],evidenceId=receipt['id'])
  self.assertEqual(s['founderKnownPrinciples'],before['founderKnownPrinciples'])
  action('buy-material',materialId='porous-clay')
  tool=next(iter(w.records('equipment-concept')))
  act(s,'start',ownerId='founder',recordId=tool,materials=['binding-thread','porous-clay']);action('advance');action('advance')
  self.assertEqual(len(s['publicWorkshop']['items']),1);self.assertGreaterEqual(s['sharedFunds'],0)
 def test_all_discoveries_need_their_exact_returned_lead(self):
  for r in w.records('discovery-template').values():
   s=g.new_campaign();s['publicWorkshop']['receipts']['proof']={'id':'proof','status':'complete','observation':{'leadId':r['leadId']}}
   act(s,'share-discovery',ownerId='founder',recordId=r['id'],evidenceId='proof')
   self.assertEqual(s['publicWorkshop']['discoveries'][r['id']]['receiptId'],'proof')
 def test_all_communities_and_contacts_have_persistent_introductions(self):
  s=g.new_campaign()
  for n,r in enumerate(w.records('contact-role').values()):
   if r['communityId'] not in s['publicWorkshop']['communities']:
    with self.assertRaises(g.RuleError):act(s,'meet-contact',ownerId='founder',recordId=r['id'],contactName='Test contact '+str(n))
    act(s,'establish-community',ownerId='founder',recordId=r['communityId']);finish(s)
   act(s,'meet-contact',ownerId='founder',recordId=r['id'],contactName='Test contact '+str(n));finish(s)
  self.assertEqual(len(s['publicWorkshop']['communities']),8);self.assertEqual(len(s['publicWorkshop']['contacts']),32)
  self.assertEqual(g.household_members(s),['founder','mira'])
 def test_all_occupation_mappings_are_available_without_rewriting_source(self):
  pack,_=i.foundation();before=deepcopy(pack);mapped=i.mapped_backgrounds(pack)
  self.assertEqual(sum(r['suggestedCapabilityPackageId']=='unmapped' for r in mapped),0);self.assertEqual(pack,before)
  self.assertEqual(len(w.records('background-mapping')),30)
  s=g.new_campaign();s['activeContentPack']=i.foundation()[1]['summary']
  import character_pool
  for ancestry in content_packs.REGISTRY.values():
   selection=content_packs.select(s,ancestry,{'contentSource':'imported','ancestry':ancestry},pack)
   proposal=content_packs.offline(selection);character_pool.validate_selection(proposal,selection)
   if selection['records'].get('backgroundMapping'):self.assertEqual(selection['records']['sourceBackground']['suggestedCapabilityPackageId'],'unmapped')
 def test_training_uses_real_teacher_knowledge_and_both_assignments(self):
  r=next(iter(w.records('training-opportunity').values()));s=g.new_campaign();target=next(x['id'] for x in r['references'] if x['id'] in g.PRINCIPLE_NAMES)
  with self.assertRaises(g.RuleError):act(s,'start-training',recordId=r['id'],clientId='founder',targetId=target,partiesAgreed=True)
  s['founderKnownPrinciples'].append(target)
  act(s,'start-training',recordId=r['id'],clientId='founder',targetId=target,partiesAgreed=True)
  self.assertEqual(s['founderAssignment'],'teaching');self.assertEqual(s['residentAssignment'],'training')
  g.apply_action(s,{'type':'advance'});self.assertIn(target,s['residentKnownPrinciples'])
 def test_all_wardrobe_briefs_save_compatible_components_without_wearing(self):
  for r in w.records('wardrobe-art-brief').values():
   s=g.new_campaign();s['people']['mira']['ancestryLabel']=content_packs.REGISTRY[r['ancestryId']]
   act(s,'save-brief-style',recordId=r['id'])
   self.assertEqual(len(s['residentStyles']['mira']),1);self.assertNotIn('mira',s['residentCurrentStyles']);self.assertIsNone(s['activeContentPack'])
 def test_art_and_qa_records_are_explicit_not_generated_or_auto_passed(self):
  s=g.new_campaign();r=next(iter(w.records('wardrobe-art-brief').values()));act(s,'save-brief',recordId=r['id'])
  brief=next(iter(s['publicWorkshop']['productionBriefs'].values()));self.assertFalse(brief['artworkGenerated']);self.assertEqual(brief['subject']['personId'],'mira')
  r=next(iter(w.records('acceptance-scenario').values()))
  with self.assertRaises(g.RuleError):act(s,'record-qa',recordId=r['id'],result='passed',scopeReviewed=False)
  act(s,'record-qa',recordId=r['id'],result='blocked');self.assertEqual(next(iter(s['publicWorkshop']['qaRuns'].values()))['kind'],'user-recorded-manual-check')
  definition=next(iter(w.records('equipment-concept')))
  obj=w.owned_object(s,{'recordId':definition,'ownerId':'mira','kind':'equipment','id':'fixture-owned'});slot='public-'+obj
  before=deepcopy(s['publicWorkshop']['items']);funds=s['sharedFunds']
  self.assertIn(slot,g.public_state(s)['originalAssets'])
  g.apply_action(s,{'type':'accept-artwork','assetId':slot,'assetPath':'/user-assets/fixture.png'})
  g.apply_action(s,{'type':'rollback-artwork','assetId':slot})
  self.assertEqual(s['assetOverrides'][slot],w.asset_slots(s)[slot]);self.assertEqual(s['publicWorkshop']['items'],before);self.assertEqual(s['sharedFunds'],funds)
 def test_migration_persistence_retry_and_failed_action_rollback(self):
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory);old=store.read();old['schemaVersion']=36
   for k in ('journeys','discoveries','communities','contacts','productionBriefs','qaRuns'):old['publicWorkshop'].pop(k)
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
   store=GameStore(directory);self.assertEqual(store.read()['schemaVersion'],66);self.assertTrue(Path(directory,'campaign-before-schema-36-to-66.sqlite3').exists())
   r=next(iter(w.records('community-template')));payload={'requestId':str(uuid.uuid4()),'expectedRevision':store.read()['revision'],'action':{'type':'public-establish-community','ownerId':'founder','recordId':r,'scopeReviewed':True,'agreed':True,'evidence':NOTE}}
   first=store.action(payload);self.assertEqual(first,store.action(payload));self.assertEqual(first,GameStore(directory).read())
   before=deepcopy(store.read());payload.update(requestId=str(uuid.uuid4()),expectedRevision=before['revision']);payload['action']['recordId']='bad'
   with self.assertRaises(g.RuleError):store.action(payload)
   self.assertEqual(store.read(),before)

 def test_all_golem_looks_have_exact_material_mappings(self):
  pack,_=i.foundation();seen=[]
  for material in ('clay','porcelain','stone','wood','metal'):
   rows=i.golem_appearances(pack,material);self.assertEqual(len(rows),5);seen.extend(r['id'] for r in rows)
  self.assertEqual(len(set(seen)),25)
  altered=deepcopy(pack);altered['ancestries']['golem']['appearanceDescriptions'][0]['skin']='unreviewed metal replacement'
  self.assertEqual(len(i.golem_appearances(altered,'clay')),4)
 def test_changed_occupation_does_not_inherit_an_unreviewed_mapping(self):
  pack,_=i.foundation();pack=deepcopy(pack);row=next(r for r in pack['shared']['occupation-background'] if r['suggestedCapabilityPackageId']=='unmapped');row['occupation']='Changed role'
  self.assertEqual(next(r for r in i.mapped_backgrounds(pack) if r['id']==row['id'])['suggestedCapabilityPackageId'],'unmapped')
 def test_source_seed_chapters_and_conditional_golem_story(self):
  s=g.new_campaign();r=i.source_stories()['human-story-001']
  act(s,'adopt-character-story',recordId=r['id'],requirementEvidence=[])
  p=next(iter(s['publicWorkshop']['journeys'].values()));open_chapter(s,p);act(s,'work-chapter',journeyId=p['id']);finish(s,'mira');act(s,'resolve-chapter',journeyId=p['id'],resolution='conclude')
  self.assertEqual(p['status'],'complete')
  s=g.new_campaign();s['people']['mira']['ancestryLabel']='Golem'
  with self.assertRaises(g.RuleError):act(s,'adopt-character-story',recordId='golem-story-020',requirementEvidence=[NOTE])
  s['people']['mira']['bodyMaterial']='wood'
  act(s,'adopt-character-story',recordId='golem-story-020',requirementEvidence=[NOTE])
  self.assertEqual(len(s['publicWorkshop']['journeys']),1)
 def test_owned_reading_and_delivered_letters_stay_participant_scoped(self):
  import public_life
  s=g.new_campaign();letter=next(iter(w.records('letter-template')))
  act(s,'compose-letter',ownerId='founder',clientId='mira',recordId=letter)
  key=next(iter(s['publicWorkshop']['letters']))
  act(s,'edit-letter',ownerId='founder',letterId=key,subject='Private comparison',body='READING-PRIVATE: the corrected sample notes are ready.')
  self.assertEqual(public_life.context(s,'mira'),[])
  act(s,'deliver-letter',ownerId='founder',letterId=key)
  self.assertIn('READING-PRIVATE',json.dumps(public_life.context(s,'mira')));self.assertNotIn('READING-PRIVATE',json.dumps(public_life.context(s,'tamsin')))
 def test_fresh_scholar_can_research_build_test_prepare_cast_and_install(self):
  s=g.new_campaign()
  def action(kind,**kw):g.apply_action(s,{'type':kind,**kw})
  def advance(n):
   for _ in range(n):action('advance')
  action('start-research');advance(3);self.assertIn('steady-hearth-wards',s['founderKnownPrinciples'])
  for _ in range(2):action('buy-material',materialId='binding-thread')
  action('buy-material',materialId='porous-clay')
  form='ss-mag-spell-construction-loosen-a-practice-knot'
  act(s,'build-experiment',ownerId='founder',recordId=form,materials=['binding-thread','porous-clay'],targetReviewed=True);advance(2)
  setup=next(iter(s['publicWorkshop']['items']))
  act(s,'test-spell',ownerId='founder',recordId=form,itemId=setup,materials=['binding-thread','sun-amber'],targetReviewed=True);advance(2)
  act(s,'prepare-spells',ownerId='founder',recordIds=[form])
  act(s,'cast',ownerId='founder',recordId=form,itemId=setup,materials=['binding-thread','sun-amber'],targetReviewed=True);advance(1)
  self.assertTrue(s['publicWorkshop']['items'][setup]['active'])
  artifact='ss-art-artifact-concept-margin-dry-book-rest'
  act(s,'start',ownerId='founder',recordId=artifact,materials=['sun-amber','binding-thread']);advance(2)
  obj=next(x for x in s['publicWorkshop']['items'].values() if x['definitionId']==artifact)
  act(s,'install',ownerId='founder',itemId=obj['id'],roomId='library',fitReviewed=True)
  act(s,'use-item',ownerId='founder',itemId=obj['id'],targetReviewed=True,target='An owned blank practice page on the library table.')
  self.assertTrue(obj['active']);self.assertGreaterEqual(s['sharedFunds'],0)

 def test_every_art_brief_binds_an_actual_matching_subject(self):
  for r in w.records('object-art-brief').values():
   s=g.new_campaign();subject=r['subjectReference']['id'];obj=w.owned_object(s,{'recordId':subject,'ownerId':'founder','kind':'equipment','id':'fixture-existing-object'})
   act(s,'save-brief',ownerId='founder',recordId=r['id'],itemId=obj)
   brief=next(iter(s['publicWorkshop']['productionBriefs'].values()));self.assertEqual(brief['subject']['object']['definitionId'],subject)
  for r in w.records('room-art-brief').values():
   s=g.new_campaign();s['publicWorkshop']['roomPurposes']['library']=r['subjectReference']['id']
   act(s,'save-brief',ownerId='founder',recordId=r['id'],roomId='library')
   self.assertEqual(next(iter(s['publicWorkshop']['productionBriefs'].values()))['subject']['roomId'],'library')
 def test_completed_scene_archive_does_not_block_new_chapters(self):
  s=g.new_campaign();s['householdScenes']={str(n):{'status':'remembered'} for n in range(300)}
  p=episode(s,next(iter(w.records('personal-arc').values())));open_chapter(s,p)
  self.assertEqual(len(s['householdScenes']),301)

 def test_every_foundation_story_can_be_adopted_by_an_eligible_resident(self):
  stories=i.source_stories();self.assertEqual(len(stories),525)
  for r in stories.values():
   s=g.new_campaign();s['people']['mira']['ancestryLabel']=content_packs.REGISTRY[r['ancestryId']]
   if r['ancestryId']=='golem':s['people']['mira']['bodyMaterial']='wood'
   act(s,'adopt-character-story',recordId=r['id'],requirementEvidence=[NOTE]*len(r['requirements']))
   self.assertEqual(next(iter(s['publicWorkshop']['journeys'].values()))['recordId'],r['id'])
