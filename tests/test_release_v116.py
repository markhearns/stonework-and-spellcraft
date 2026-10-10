from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
import game as g
import ancestry_traits as ancestry
import character_pool as pool
import character_approaches as approaches
import containment
import local_encounters
import scripted_companions as companions
from candidate_proposals import approved_definition
from dialogue import DialogueService,ProviderSettings
from server import GameStore

class Release116Tests(unittest.TestCase):
 def test_every_ancestry_has_exactly_one_check_bonus_no_rank_or_reward(self):
  s=g.new_campaign('fresh');self.assertEqual(set(pool.ANCESTRIES),set(ancestry.TRAITS))
  for label in pool.ANCESTRIES:
   s['people']['founder']['ancestryLabel']=label;before=deepcopy(s);trait=ancestry.for_person(s,'founder')
   for attribute in g.character_builds.ATTRIBUTES:
    check=approaches.score(s,'founder',approaches.spec(attribute,'athletics',6))
    self.assertEqual(check['total'],5+int(attribute==trait['attribute']),(label,attribute,check))
    if attribute==trait['attribute']:self.assertIn('(ancestry) 1',check['detail'])
   self.assertEqual(s,before)
 def test_local_kitsune_keeps_early_route_and_workshop(self):
  s=g.new_campaign('fresh');g.apply_action(s,{'type':'start-local-visit','encounterId':'koharu'});g.apply_action(s,{'type':'advance'})
  self.assertEqual(s['people']['koharu']['ancestryLabel'],'Kitsune');self.assertNotIn('maren',s['people'])
  self.assertEqual(s['summoningContacts']['introduced-koharu']['contactStatus'],'open')
  import resident_specialties,companion_almanac_content as a
  self.assertEqual(resident_specialties.SPECIALTIES['koharu']['room'],'workshop')
  self.assertEqual(sum(g.character_builds.baseline('koharu').values()),30)
  for key,url in g.ORIGINAL_ASSETS.items():
   self.assertNotIn('maren',key);self.assertNotIn('maren',url)
 def test_chamber_consolidation_preserves_case_project_and_refunds_duplicates_once(self):
  s=g.new_campaign('fresh');s['schemaVersion']=72
  s['containment']['chambers']={f'{ward}-{i}':{'status':'ready' if i in (2,3) else 'sealed'} for ward in ('heat','echo') for i in range(1,6)}
  s['containment']['cases']['sabine'].update(status='contained',chamberId='echo-3')
  funds=s['sharedFunds'];clay=s['materialInventory']['porous-clay']
  g.migrate_state(s)
  self.assertEqual(set(s['containment']['chambers']),{'heat-1','echo-1'});self.assertEqual(s['containment']['cases']['sabine']['chamberId'],'echo-1')
  self.assertEqual(s['sharedFunds'],funds+28);self.assertEqual(s['materialInventory']['porous-clay'],clay+4)
  self.assertEqual(containment.view(s)['maximumCapacity'],2);before=deepcopy(s);g.migrate_state(s);self.assertEqual(s,before)
  s['schemaVersion']=72;s['containment']['chambers']={f'{w}-{i}':{'status':'sealed'} for w in ('heat','echo') for i in range(1,6)}
  s['containment']['project']={'kind':'chamber','targetId':'heat-4','completedWorkPhases':1,'requiredWorkPhases':2,'committedCrowns':14,'committedMaterials':{'porous-clay':2,'binding-thread':1}}
  g.migrate_state(s);self.assertEqual(s['containment']['project']['targetId'],'heat-1');self.assertEqual(s['containment']['project']['completedWorkPhases'],1)
 def test_old_identity_rekeys_housing_relationships_and_equipment(self):
  s=g.new_campaign('fresh');g.apply_action(s,{'type':'cheat-toggle','enabled':True});g.apply_action(s,{'type':'cheat-recruit','characterId':'koharu'})
  s=json.loads(json.dumps(s).replace('koharu','maren').replace('Koharu','Maren'));s['people']['maren']['ancestryLabel']='Bovinefolk';s['schemaVersion']=72
  bed=s['bedroomAssignments']['maren'];funds=s['sharedFunds'];s['assetOverrides']['maren']='/user-assets/old.png'
  g.migrate_state(s);self.assertEqual(s['people']['koharu']['ancestryLabel'],'Kitsune');self.assertEqual(s['bedroomAssignments']['koharu'],bed);self.assertEqual(s['sharedFunds'],funds)
  self.assertNotIn('maren',json.dumps(s));self.assertNotIn('koharu',s['assetOverrides']);g.public_state(s)
 def test_offline_recruitment_and_summoning_lifecycle_provider_never_called(self):
  for ancestry_label in ('Human','Demon'):
   with self.subTest(ancestry=ancestry_label),tempfile.TemporaryDirectory() as directory:
    store=GameStore(directory,start_type='fresh');calls=[];service=DialogueService(ProviderSettings(directory),lambda *_:calls.append(1))
    payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'purpose':'candidate-proposal','source':'offline','poolChoices':{'ancestry':ancestry_label,'background':'bookbinder','temperament':'playful'},'text':'Use the selected ingredients.'}
    draft=service.generate(store,payload);self.assertEqual(draft['status'],'ready',draft);self.assertEqual(service.generate(store,payload),draft)
    s=service.accept(store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True});who=draft['approvedCandidateId'] if 'approvedCandidateId' in draft else 'summoned-'+draft['id']
    self.assertNotIn(who,s['people']);s['sharedFunds']=100
    for k in s['materialInventory']:s['materialInventory'][k]=20
    if ancestry_label=='Human':
     from recruitment_fixture import rescue_and_invite
     rescue_and_invite(s,who)
    else:
     g.learn_for_character(s,'founder','courteous-passage');g.apply_action(s,{'type':'summoning-prepare','candidateId':who,'conductorId':'founder','materials':['porous-clay','binding-thread']})
     g.apply_action(s,{'type':'advance'});g.apply_action(s,{'type':'advance'})
    self.assertIn(who,s['people']);self.assertNotIn(who,s['bedroomAssignments']);self.assertTrue(companions.eligible(s,who));self.assertEqual(calls,[])
    cid=next(k for k,c in s['summoningContacts'].items() if c['personId']==who)
    for topic in ('intentions','home','visit'):g.apply_action(s,{'type':'summoning-talk','contactId':cid,'topic':topic})
    s['housingRooms']['west-chamber']['status']='complete'
    g.apply_action(s,{'type':'summoning-invite','contactId':cid,'roomId':'west-chamber'})
    self.assertNotIn(who,s['bedroomAssignments']);g.apply_action(s,{'type':'advance'})
    self.assertEqual(s['residency'][who]['residencyStatus'],'visiting');self.assertNotIn(who,g.household_members(s))
    g.apply_action(s,{'type':'summoning-ask-stay','contactId':cid})
    self.assertNotIn(who,g.household_members(s))
    if s['residency'][who]['candidateStayDecision']=='wants-to-stay':
     g.apply_action(s,{'type':'summoning-household-decision','contactId':cid,'decision':'invite-to-stay'})
     self.assertIn(who,g.household_members(s))
    else:self.assertEqual(s['residency'][who]['candidateStayDecision'],'prefers-to-leave')
    self.assertEqual(s['bedroomAssignments'][who],'west-chamber');self.assertEqual(calls,[])

 def test_companion_choices_remember_actual_response_without_rewards(self):
  s=g.new_campaign('fresh');selection=pool.select(s,'f'*32,{'ancestry':'Human','background':'mapmaker','temperament':'quiet'});proposal=pool.offline(s,selection,'f'*32)
  s['reviewedCandidates']['test-person']=approved_definition(proposal,'test-person','offline','fixture');s['reviewedCandidates']['test-person']['profile']['generationIngredients']=selection
  import arrivals
  arrivals.contact(s,'test-person','ordinary-correspondence');s['residency']['test-person']['residencyStatus']='visiting';s['bedroomAssignments']['test-person']='bedchamber'
  before=(s['dayNumber'],s['currentDayPhase'],s['sharedFunds'],deepcopy(s['materialInventory']),deepcopy(s['residentBonds']))
  g.apply_action(s,{'type':'talk-scripted-companion','characterId':'test-person','topicId':'company','choiceId':'listen'})
  r=companions.view(s)['test-person'];self.assertEqual(r['history'][-1]['lines'][1]['text'],'I would rather watch or listen first');self.assertIn('watching or listening',r['scenes'][2]['opening'])
  self.assertEqual(before,(s['dayNumber'],s['currentDayPhase'],s['sharedFunds'],s['materialInventory'],s['residentBonds']))
  s['residency']['test-person']['residencyStatus']='remote';before=deepcopy(s)
  with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'talk-scripted-companion','characterId':'test-person','topicId':'company','choiceId':'join'})
  self.assertEqual(s,before)
 def test_phase_account_is_scripted_exact_recoverable_and_once_only(self):
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory,start_type='fresh');store.action({'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'advance'}})
   before=store.read();calls=[];service=DialogueService(ProviderSettings(directory),lambda *_:calls.append(1));payload={'requestId':uuid.uuid4().hex,'expectedRevision':before['revision'],'purpose':'journal','source':'offline','text':'Summarize the last phase.'}
   draft=service.generate(store,payload);self.assertEqual(draft['status'],'ready',draft)
   for line in before['lastPhaseSummary']:self.assertIn(line,draft['text'])
   self.assertEqual(service.generate(store,payload),draft);saved=service.accept(store,{'draftId':draft['id']});self.assertEqual(saved,service.accept(store,{'draftId':draft['id']}));self.assertEqual(calls,[])
   self.assertEqual(saved['journal'][-1]['source'],'scripted');self.assertEqual(saved['currentDayPhase'],before['currentDayPhase'])
