"""Executable public rules: ownership, escrow, work, preparation and reversibility."""
from copy import deepcopy
from pathlib import Path
import json,tempfile,unittest,uuid
import game as g, public_workshop as w,public_advanced,public_progression,public_starters
from server import GameStore,CampaignLibrary

def rich():
 s=g.new_campaign();s['sharedFunds']=100000;s['founderKnownPrinciples']=list(g.PRINCIPLE_NAMES);s['residentKnownPrinciples']=list(g.PRINCIPLE_NAMES)
 s['personalFunds']['founder']=1000;s['personalFunds']['mira']=1000
 s['restorationStatus']='complete'
 for k in g.MATERIALS:s['materialInventory'][k]=1000
 for k,r in w.records('material').items():s['publicWorkshop']['inventory'][k]=1000;s['publicWorkshop']['qualifiedMaterials'][k]=r['propertyIds'][:]
 for who in ['founder','mira']:s['publicWorkshop']['knowledge'][who]=list(w.records('principle-concept'))
 return s

def components(s,rule):
 out=[]
 for slot in rule['materials']:
  key=slot.get('materialId') or next(k for k in [*g.MATERIALS,*w.records('material')] if slot['propertyId'] in w.properties(s,k))
  out += [key]*slot['quantity']
 return out

def start(s,r,**kw):
 rule=w.rule_for(r)
 return w.apply(s,{'type':'public-start','ownerId':'founder','recordId':r['id'],'roomId':'library','agreed':True,'materials':components(s,rule),**kw})

def finish(s,who='founder'):
 for _ in range(30):
  if who not in s['publicWorkshop']['jobs']:return
  g.resolve_work(s)
 raise AssertionError('Project did not complete')

class PublicWorkshopTests(unittest.TestCase):
 def test_all_fabrication_definitions_have_real_owned_outputs(self):
  for typ in ('artifact-concept','equipment-concept','furnishing-concept'):
   for r in w.records(typ).values():
    if not w.rule_for(r):continue
    s=rich();before=s['sharedFunds'];start(s,r);self.assertEqual(s['publicWorkshop']['items'],{})
    finish(s);obj=next(iter(s['publicWorkshop']['items'].values()))
    self.assertEqual(obj['definitionId'],r['id']);self.assertFalse(obj['active']);self.assertIsNone(obj['roomId']);self.assertEqual(obj['ownerId'],'founder')
    count=len(s['publicWorkshop']['items']);g.resolve_work(s);self.assertEqual(len(s['publicWorkshop']['items']),count)
 def test_all_materials_qualify_only_after_review_and_assigned_work(self):
  for r in w.records('material').values():
   s=rich();s['publicWorkshop']['qualifiedMaterials'].pop(r['id']);before=deepcopy(s)
   a={'type':'public-qualify','recordId':r['id'],'ownerId':'founder','materials':[r['id']],'agreed':True,'evidence':'Compared the actual sample with the acceptance test and its control.'}
   with self.assertRaises(g.RuleError):w.apply(s,a)
   self.assertEqual(s,before);w.apply(s,{**a,'testsReviewed':True});finish(s)
   self.assertEqual(s['publicWorkshop']['qualifiedMaterials'][r['id']],r['propertyIds']);self.assertEqual(s['publicWorkshop']['inventory'][r['id']],before['publicWorkshop']['inventory'][r['id']])
 def test_reserves_pause_cancel_and_sqlite_retry(self):
  r=next(iter(w.records('artifact-concept').values()));s=rich();rule=w.rule_for(r);keys=components(s,rule)
  for k in keys:
   if k in g.MATERIALS:s['materialReserveTargets'][k]=s['materialInventory'][k]
  before=deepcopy(s)
  with self.assertRaises(g.RuleError):start(s,r)
  self.assertEqual(s,before)
  s=rich();before=deepcopy(s);start(s,r);w.apply(s,{'type':'public-pause','ownerId':'founder'});g.resolve_work(s);self.assertEqual(s['publicWorkshop']['jobs']['founder']['completedWorkPhases'],0)
  w.apply(s,{'type':'public-cancel','ownerId':'founder'})
  self.assertEqual(s['materialInventory'],before['materialInventory']);self.assertEqual(s['sharedFunds'],before['sharedFunds'])
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-cancel','ownerId':'founder'})
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d)
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(rich()),))
   payload={'requestId':str(uuid.uuid4()),'expectedRevision':0,'action':{'type':'public-start','ownerId':'founder','recordId':r['id'],'agreed':True,'materials':keys}}
   first=store.action(payload);self.assertEqual(store.action(payload),first);self.assertEqual(GameStore(d).read(),first)
 def test_all_inscriptions_enforce_their_exact_host(self):
  for r in w.records('inscription-concept').values():
   if not r['mechanicsProposalId']:continue
   s=rich();host=w.definition(r['validHosts'][0]);start(s,host);finish(s);key=next(iter(s['publicWorkshop']['items']))
   start(s,r,itemId=key);finish(s);self.assertIn(r['id'],s['publicWorkshop']['items'][key]['inscriptions'])
   w.apply(s,{'type':'public-prepare-item','ownerId':'founder','itemId':key,'inscriptionId':r['id']})
   w.apply(s,{'type':'public-use-item','ownerId':'founder','itemId':key,'targetReviewed':True,'target':'The inspected owned inert practice sample.'})
   self.assertTrue(s['publicWorkshop']['items'][key]['active'])
 def test_all_public_forms_build_test_prepare_cast_without_resources_generated(self):
  for r in w.records('spell-construction').values():
   if not r['mechanicsProposalId']:continue
   s=rich();a={'ownerId':'founder','recordId':r['id'],'agreed':True,'targetReviewed':True,'exceptionalReviewed':True,'evidence':'A finite owner-approved inert setup, source reference and accessible stop are available.'}
   w.apply(s,{**a,'type':'public-build-experiment','materials':['binding-thread','porous-clay']});finish(s);key=next(iter(s['publicWorkshop']['items']));a['itemId']=key;a['materials']=components(s,w.catalogue()['rules'][r['mechanicsProposalId']])
   with self.assertRaises(g.RuleError):w.apply(s,{**a,'type':'public-cast'})
   w.apply(s,{**a,'type':'public-test-spell'});finish(s)
   w.apply(s,{'type':'public-prepare-spells','ownerId':'founder','recordIds':[r['id']]})
   import public_spell_effects
   slug=public_spell_effects.slug(r)
   if slug in ('paired-circle-freight-fold','permissioned-object-recovery','isolated-residual-unweaving','remove-a-trial-finish','release-a-temporary-label','shared-reversible-sample-finish'):
    focus=next(iter(w.records('equipment-concept')));target=w.owned_object(s,{'recordId':focus,'ownerId':'founder','kind':'equipment','id':'fixture-owned-object'})
    s['publicWorkshop']['items'][target]['experimentalState']={'temporaryLabel':'attached'};s['publicWorkshop']['items'][target]['trialFinish']=None if slug=='shared-reversible-sample-finish' else {'receiptId':'earlier-finish'}
    a['targetItemId']=target
    if slug=='shared-reversible-sample-finish':a['additionalTargetItemIds']=[w.owned_object(s,{'recordId':focus,'ownerId':'founder','kind':'equipment','id':'second-sample'})]
    if slug=='paired-circle-freight-fold':
     dest=w.owned_object(s,{'recordId':r['id'],'ownerId':'founder','kind':'experiment','id':'fixture-second-circle','roomId':'common-room'})
     s['publicWorkshop']['items'][dest]['roomId']='common-room';a['destinationItemId']=dest
   before=deepcopy(s['materialInventory']);w.apply(s,{**a,'type':'public-cast'});finish(s)
   self.assertEqual(s['materialInventory'],before);self.assertEqual(s['publicWorkshop']['items'][key]['effect']['formId'],r['id'])
 def test_principle_study_does_not_teach_another_person(self):
  s=rich();s['publicWorkshop']['knowledge']['founder']=[];s['publicWorkshop']['knowledge']['mira']=[]
  r=next(iter(w.records('principle-concept').values()))
  w.apply(s,{'type':'public-study','ownerId':'founder','recordId':r['id'],'agreed':True,'evidence':'Compare a temporary join with the unjoined control.'});finish(s)
  self.assertIn(r['id'],w.knowledge(s,'founder'));self.assertNotIn(r['id'],w.knowledge(s,'mira'))
 def test_all_reversible_augmentations_restore_without_a_phase_or_fee(self):
  for r in w.records('augmentation-concept').values():
   s=rich();s['people']['mira']['ancestryLabel']='Seraph'
   if r['ancestryRestrictions']:
    import content_packs
    s['people']['mira']['ancestryLabel']=content_packs.REGISTRY[r['ancestryRestrictions'][0]]
   original=deepcopy(s['people']['mira'])
   w.apply(s,{'type':'public-augment','ownerId':'mira','recordId':r['id'],'agreed':True,'anatomyReviewed':True,'participantRequested':True,'originalAppearance':'The original accepted appearance remains intact.'});finish(s,'mira')
   s['expedition']={'companionId':'mira'};funds=s['sharedFunds'];day=s['dayNumber']
   w.apply(s,{'type':'public-remove-augmentation','ownerId':'mira'})
   self.assertEqual(s['people']['mira'],original);self.assertEqual(s['sharedFunds'],funds);self.assertEqual(s['dayNumber'],day);self.assertNotIn('mira',s['publicWorkshop']['augmentations'])
 def test_ritual_roles_take_independent_phases_and_cancel_once(self):
  for r in w.records('ritual-concept').values():
   s=rich();bindings=['founder']*len(r['roles'])
   w.apply(s,{'type':'public-start-ritual','ownerId':'founder','recordId':r['id'],'roleBindings':bindings,'participantsAgreed':True,'agreed':True,'evidence':'The inert control and actual observations are explicitly distinguished.'})
   self.assertEqual(s['publicWorkshop']['jobs']['founder']['requiredWorkPhases'],w.catalogue()['rules'][r['mechanicsProposalId']]['workPhases']*len(bindings));finish(s)
   self.assertEqual(next(iter(s['publicWorkshop']['rituals'].values()))['status'],'complete')
 def test_all_creation_packages_are_small_unique_and_retry_safe(self):
  for key in w.records('starting-package-concept'):
   s=g.new_campaign();public_starters.initialize_new_scholar(s,key)
   self.assertEqual(len(s['founderKnownPrinciples']),1);self.assertEqual(len(s['characterDevelopment']['founder']['learnedPractices']),1);self.assertTrue(all(v==0 for v in s['characterSkills']['founder'].values()))
   with self.assertRaises(g.RuleError):public_starters.initialize_new_scholar(s,key)
  with tempfile.TemporaryDirectory() as d:
   lib=CampaignLibrary(d);a={'campaignId':'c-'+uuid.uuid4().hex,'name':'Test creation','mode':'solo','publicStarter':next(iter(w.records('starting-package-concept')))}
   self.assertEqual(lib.create(a),lib.create(a))
   with self.assertRaises(g.RuleError):lib.create({**a,'publicStarter':None})
 def test_perk_investment_and_preparation_share_existing_limits(self):
  s=rich();r=next(iter(w.records('perk-concept').values()));principles,practices=public_progression.prerequisites(r)
  s['characterSkills']['founder']['artifice']=1;s['characterDevelopment']['founder']['learnedPractices']+=practices;s['characterDevelopment']['founder']['advancementAwards']['fixture']={'points':100,'reason':'Earned fixture'}
  a={'type':'public-learn-perk','recordId':r['id'],'ownerId':'founder','agreed':True,'evidenceReviewed':True,'evidence':'Two measured sections demonstrate actual independent understanding.'}
  w.apply(s,a);self.assertEqual(g.character_sheet(s,'founder')['reservedAdvancement'],2);finish(s)
  self.assertIn(r['id'],s['characterDevelopment']['founder']['learnedPractices']);self.assertEqual(g.character_sheet(s,'founder')['reservedAdvancement'],0)
  with self.assertRaises(g.RuleError):w.apply(s,a)
 def test_ownership_delivery_and_service_money_are_conserved(self):
  s=rich();r=next(iter(w.records('artifact-concept').values()));start(s,r);finish(s);key=next(iter(s['publicWorkshop']['items']))
  commission=next(r for r in w.records('commission-concept').values() if any(ref['id']==s['publicWorkshop']['items'][key]['definitionId'] for ref in r['references']))
  before=sum(s['personalFunds'].values())
  a={'type':'public-offer-delivery','recordId':commission['id'],'ownerId':'founder','clientId':'mira','itemId':key,'partiesAgreed':True,'scopeReviewed':True,'evidence':'The actual completed object satisfies the accepted scope.'}
  w.apply(s,a);c=next(iter(s['publicWorkshop']['contracts']))
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-transfer','ownerId':'founder','recipientId':'mira','itemId':key,'agreed':True})
  w.apply(s,{'type':'public-deliver','ownerId':'founder','contractId':c,'deliveryAccepted':True})
  self.assertEqual(s['publicWorkshop']['items'][key]['ownerId'],'mira');self.assertEqual(sum(s['personalFunds'].values()),before)
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-deliver','ownerId':'founder','contractId':c,'deliveryAccepted':True})
  service=next(iter(w.records('service-concept').values()));s['characterSkills']['founder']['artifice']=1
  w.apply(s,{'type':'public-order-service','recordId':service['id'],'ownerId':'founder','clientId':'mira','itemId':key,'agreed':True,'partiesAgreed':True,'scopeReviewed':True,'evidence':'Assess the owned workpiece and record a proposed repair sample.'});finish(s)
  c=list(s['publicWorkshop']['contracts'])[-1];self.assertEqual(s['publicWorkshop']['contracts'][c]['status'],'awaiting-delivery')
  w.apply(s,{'type':'public-cancel-agreement','ownerId':'founder','contractId':c});self.assertEqual(sum(s['personalFunds'].values()),before)

 def test_prepared_public_spells_cannot_exceed_baseline_slots(self):
  s=rich();forms=list(w.records('spell-construction'))[4:7];s['publicWorkshop']['testedSpells']['founder']=forms
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-prepare-spells','ownerId':'founder','recordIds':forms})
  self.assertNotIn('founder',s['publicWorkshop']['preparedSpells'])
 def test_room_support_and_perk_replace_binding_press_not_stack(self):
  s=rich();r=w.definition('ss-room-adjacency-synergy-dry-parts-beside-covers');s['publicWorkshop']['roomPurposes']={'library':r['firstRoomPurposeId'],'common-room':r['secondRoomPurposeId']}
  s['publicWorkshop']['receipts']['evidence']={'status':'complete'}
  w.apply(s,{'type':'public-select-support','ownerId':'founder','recordId':r['id'],'rooms':['library','common-room'],'evidenceId':'evidence','evidenceReviewed':True})
  s['utilityArtifactPlacements']['binding-press']=True;s['founderAssignment']='crafting'
  parts=g.work_contribution_parts(s,'founder','careful-assembly')
  self.assertEqual(sum(x['amount'] for x in parts if x['name'] in ('Binding press',r['name'])),1)
  s['publicWorkshop']['roomPurposes']['common-room']='changed'
  self.assertIsNone(public_progression.room_support(s,'founder','careful-assembly'))
 def test_withdrawal_after_one_ritual_participant_finishes(self):
  import public_rituals
  s=rich();r=next(iter(w.records('ritual-concept').values()));before=s['sharedFunds']
  w.apply(s,{'type':'public-start-ritual','ownerId':'founder','recordId':r['id'],'roleBindings':['founder','mira'],'participantsAgreed':True,'agreed':True,'evidence':'The two actual participants compare their independently recorded controls.'})
  w.apply(s,{'type':'public-pause','ownerId':'mira'});finish(s)
  ritual=next(iter(s['publicWorkshop']['rituals']))
  w.apply(s,{'type':'public-withdraw-ritual','ownerId':'founder','ritualId':ritual})
  self.assertEqual(s['sharedFunds'],before);self.assertEqual(s['publicWorkshop']['jobs'],{})
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-withdraw-ritual','ownerId':'founder','ritualId':ritual})
 def test_all_public_sites_have_bounded_actual_travel_and_no_duplicate_leads(self):
  import public_fieldwork
  for r in w.records('site-template').values():
   s=rich();money=s['sharedFunds'];known=deepcopy(s['founderKnownPrinciples'])
   w.apply(s,{'type':'public-start-field-trip','ownerId':'founder','recordId':r['id'],'scopeReviewed':True,'evidence':'The public location and safe route have been explicitly established.'})
   self.assertFalse(g.character_at_castle(s,'founder'))
   with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'assign-founder','assignment':'commissions'})
   g.resolve_work(s);lead=public_fieldwork.view(s)['leads'][0]['id']
   a={'type':'public-field-lead','ownerId':'founder','recordId':lead,'scopeReviewed':True,'evidence':'These are the actually visible observations; interpretations remain uncertain.'}
   w.apply(s,a);g.resolve_work(s);g.resolve_work(s)
   with self.assertRaises(g.RuleError):w.apply(s,a)
   w.apply(s,{'type':'public-return-field-trip','ownerId':'founder'});g.resolve_work(s)
   self.assertTrue(g.character_at_castle(s,'founder'));self.assertEqual(s['sharedFunds'],money);self.assertEqual(s['founderKnownPrinciples'],known)
 def test_household_objects_are_owned_reading_does_not_grant_mastery_and_meals_are_finite(self):
  for typ in ('book-or-document','food-or-drink','garden-specimen','curiosity','gift-or-keepsake'):
   s=rich();s['facilityProjects']['kitchen']['status']='complete';r=next(iter(w.records(typ).values()));known=deepcopy(s['founderKnownPrinciples'])
   w.apply(s,{'type':'public-make-household-object','ownerId':'founder','recordId':r['id'],'agreed':True,'scopeReviewed':True,'evidence':'Actual ordinary supplies and the owner’s permission are established.'});finish(s);key=next(iter(s['publicWorkshop']['items']))
   if typ=='book-or-document':w.apply(s,{'type':'public-read-object','ownerId':'founder','itemId':key,'agreed':True});finish(s);self.assertTrue(s['publicWorkshop']['items'][key]['read'])
   if typ=='food-or-drink':
    w.apply(s,{'type':'public-share-meal','ownerId':'founder','itemId':key,'agreed':True})
    with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-share-meal','ownerId':'founder','itemId':key,'agreed':True})
   self.assertEqual(s['founderKnownPrinciples'],known)
 def test_schema35_migration_preserves_state_and_backup(self):
  old=g.new_campaign();old.pop('publicWorkshop');old['schemaVersion']=35;before=deepcopy(old)
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d)
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
   s=GameStore(d).read();self.assertEqual(s['schemaVersion'],66)
   for key,value in before.items():
    if key not in ('schemaVersion','revision'):self.assertEqual(s[key],value,key)
   self.assertEqual(s['revision'],before['revision']+1)
   self.assertTrue((Path(d)/f"campaign-before-schema-35-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
 def test_every_earned_method_can_be_acquired_and_prepared_without_free_rank(self):
  for r in w.records('perk-concept').values():
   s=rich();principles,practices=public_progression.prerequisites(r);who='founder'
   s['characterSkills'][who][public_progression.skill(r)]=1;s['characterDevelopment'][who]['learnedPractices']+=practices
   s['characterDevelopment'][who]['advancementAwards']['fixture']={'points':100,'reason':'Prior earned work'}
   ranks=deepcopy(s['characterSkills'][who]);a={'type':'public-learn-perk','ownerId':who,'recordId':r['id'],'agreed':True,'evidenceReviewed':True,'evidence':'Actual prerequisite studies and a controlled comparison establish the learning evidence.'}
   w.apply(s,a);finish(s);g.apply_action(s,{'type':'prepare-practice','characterId':who,'practiceId':r['id'],'prepared':True})
   self.assertIn(r['id'],s['characterDevelopment'][who]['preparedPractices']);self.assertEqual(s['characterSkills'][who],ranks)
 def test_every_room_support_can_be_selected_with_actual_adjacent_purposes(self):
  for r in w.records('adjacency-synergy').values():
   if r['mechanicsProposalId'] is None:continue
   s=rich();s['publicWorkshop']['roomPurposes']={'library':r['firstRoomPurposeId'],'common-room':r['secondRoomPurposeId']};s['publicWorkshop']['receipts']['completed-evidence']={'status':'complete'}
   a={'type':'public-select-support','recordId':r['id'],'ownerId':'founder','rooms':['library','common-room'],'evidenceId':'completed-evidence','evidenceReviewed':True}
   w.apply(s,a);self.assertEqual(s['publicWorkshop']['supports']['founder']['recordId'],r['id'])
   with self.assertRaises(g.RuleError):w.apply(s,{**a,'rooms':['library','bedchamber']})
 def test_golem_public_starters_remain_prospective(self):
  from candidate_proposals import approved_definition,validate_candidate
  from test_candidate_proposals import candidate_fixture
  p=candidate_fixture();p['ancestryLabel']='Golem';p['capabilityPackageId']=next(iter(w.records('starting-package-concept')))
  proposal,review=validate_candidate(json.dumps(p),g.new_campaign())
  candidate=approved_definition(proposal,'new-golem','fixture','draft')
  self.assertEqual(candidate['principles'],[]);self.assertEqual(candidate['profile']['startingPractices'],[])
  self.assertEqual(review['principles'],[])
 def test_letters_gifts_and_narrative_plans_preserve_mechanics(self):
  s=rich();r=next(iter(w.records('letter-template').values()));funds=s['sharedFunds'];principles=deepcopy(s['founderKnownPrinciples'])
  w.apply(s,{'type':'public-compose-letter','ownerId':'mira','clientId':'founder','recordId':r['id'],'scopeReviewed':True})
  letter=next(iter(s['publicWorkshop']['letters']))
  w.apply(s,{'type':'public-deliver-letter','ownerId':'mira','letterId':letter,'scopeReviewed':True})
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-deliver-letter','ownerId':'mira','letterId':letter,'scopeReviewed':True})
  r=next(iter(w.records('gift-or-keepsake').values()))
  w.apply(s,{'type':'public-make-household-object','ownerId':'founder','recordId':r['id'],'agreed':True,'scopeReviewed':True,'evidence':'The modest keepsake uses actual newly purchased ordinary supplies.'});finish(s);key=next(iter(s['publicWorkshop']['items']))
  w.apply(s,{'type':'public-gift-object','ownerId':'founder','clientId':'mira','recordId':r['id'],'itemId':key,'agreed':True,'scopeReviewed':True})
  self.assertEqual(s['publicWorkshop']['items'][key]['ownerId'],'mira');self.assertEqual(len(s['publicWorkshop']['items']),1)
  r=next(iter(w.records('encounter-template').values()));before=deepcopy(s)
  w.apply(s,{'type':'public-save-plan','ownerId':'founder','recordId':r['id'],'scopeReviewed':True,'evidence':'A candidate for later fieldwork, with no accepted event or invented observation.'})
  plan=next(iter(s['publicWorkshop']['activities']))
  w.apply(s,{'type':'public-record-event','ownerId':'founder','planId':plan,'scopeReviewed':True,'evidence':'The player recorded a chosen discussion; the interpretation remains unresolved.'})
  self.assertEqual(s['sharedFunds'],before['sharedFunds']);self.assertEqual(s['founderKnownPrinciples'],principles);self.assertEqual(s['dayNumber'],before['dayNumber'])
 def test_freight_moves_same_item_and_removal_needs_a_registered_effect(self):
  import public_spell_effects
  s=rich();r=w.definition('ss-mag-spell-construction-paired-circle-freight-fold');focus=next(iter(w.records('equipment-concept')))
  src=w.owned_object(s,{'recordId':r['id'],'ownerId':'founder','id':'source','roomId':'library'},'experiment');s['publicWorkshop']['items'][src]['roomId']='library'
  dest=w.owned_object(s,{'recordId':r['id'],'ownerId':'founder','id':'destination','roomId':'common-room'},'experiment');s['publicWorkshop']['items'][dest]['roomId']='common-room'
  target=w.owned_object(s,{'recordId':focus,'ownerId':'founder','id':'owned-parcel','roomId':'library'},'equipment');n=len(s['publicWorkshop']['items']);obj=s['publicWorkshop']['items'][src]
  data=public_spell_effects.validate(s,{'targetItemId':target,'destinationItemId':dest},r,'founder',obj)
  public_spell_effects.apply(s,{'id':'cast-receipt',**data},r,obj)
  self.assertEqual(len(s['publicWorkshop']['items']),n);self.assertEqual(s['publicWorkshop']['items'][target]['ownerId'],'founder');self.assertEqual(s['publicWorkshop']['items'][target]['locationRoomId'],'common-room')
  removal=w.definition('ss-mag-spell-construction-remove-a-trial-finish')
  with self.assertRaises(g.RuleError):public_spell_effects.validate(s,{'targetItemId':target},removal,'founder',obj)
 def test_shipped_rule_coverage_has_explicit_finite_costs_and_exact_spell_transitions(self):
  import public_spell_effects
  self.assertEqual(len(w.catalogue()['rules']),319)
  for rule in w.catalogue()['rules'].values():
   self.assertIn(rule['kind'],w.IMPLEMENTED_KINDS);self.assertIs(type(rule['crowns']),int);self.assertGreaterEqual(rule['crowns'],0);self.assertIs(type(rule['workPhases']),int)
  forms={public_spell_effects.slug(r) for r in w.records('spell-construction').values() if r['mechanicsProposalId']}
  self.assertEqual(forms,set(public_spell_effects.STATES))
 def test_stale_perk_eligibility_pauses_without_grant_or_lost_inputs(self):
  s=rich();r=next(iter(w.records('perk-concept').values()));_,practices=public_progression.prerequisites(r)
  s['characterSkills']['founder']['artifice']=1;s['characterDevelopment']['founder']['learnedPractices']+=practices;s['characterDevelopment']['founder']['advancementAwards']['fixture']={'points':100,'reason':'Earned fixture'}
  w.apply(s,{'type':'public-learn-perk','ownerId':'founder','recordId':r['id'],'agreed':True,'evidenceReviewed':True,'evidence':'The actual prerequisite comparisons are available and reviewed.'})
  s['characterSkills']['founder']['artifice']=0;g.resolve_work(s)
  self.assertEqual(s['publicWorkshop']['jobs']['founder']['completedWorkPhases'],0)
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-resume','ownerId':'founder'})
  self.assertNotIn(r['id'],s['characterDevelopment']['founder']['learnedPractices'])
 def test_recipe_alias_cannot_bypass_personal_knowledge_and_purposes_cannot_create_capacity(self):
  s=g.new_campaign();r=next(iter(w.records('recipe-concept').values()));before=deepcopy(s)
  with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-start','ownerId':'founder','recordId':r['id'],'agreed':True,'materials':['sun-amber','binding-thread']})
  self.assertEqual(s,before)
  for purpose in ('private-bedchamber','washroom','cookhouse','quiet-care-suite'):
   with self.assertRaises(g.RuleError):w.apply(s,{'type':'public-set-purpose','ownerId':'founder','recordId':'ss-room-room-purpose-'+purpose,'roomId':'library','fitReviewed':True})
  self.assertEqual(s,before)
 def test_finite_material_orders_deliver_once_and_require_qualification(self):
  s=rich();r=next(r for r in w.records('material').values() if r['rarityBand']=='ordinary');s['publicWorkshop']['materialStock'][r['id']]=0;before=s['publicWorkshop']['inventory'][r['id']]
  a={'type':'public-order-material','ownerId':'founder','recordId':r['id'],'quantity':2,'agreed':True,'scopeReviewed':True,'evidence':'The named supplier accepts this finite two-unit batch with actual delivery.'}
  w.apply(s,a);self.assertEqual(s['publicWorkshop']['inventory'][r['id']],before);finish(s)
  self.assertEqual(s['publicWorkshop']['inventory'][r['id']],before+2);self.assertNotIn(r['id'],s['publicWorkshop']['qualifiedMaterials']);g.resolve_work(s);self.assertEqual(s['publicWorkshop']['inventory'][r['id']],before+2)
