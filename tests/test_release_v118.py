from copy import deepcopy
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
import uuid
from unittest.mock import patch
import game as g
import bestiary
import encounter_people as ep
import world_recruitment as world
import chapel_spirit as spirit
import recruitment_quests as quests
import field_magic
from dialogue import ProviderSettings,DialogueService,provider_completion
from portrait_generation import PortraitSettings,provider_image
from server import GameStore

class Release118Tests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'};self.s['provisions']['stock']=300
 def act(self,kind,**fields):g.apply_action(self.s,dict(type=kind,**fields))
 def reject(self,kind,**fields):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**fields)
  self.assertEqual(before,self.s)
 def test_all_ranks_sorted_without_revealing_knowledge(self):
  old=deepcopy(self.s);view=bestiary.view(self.s);self.assertEqual(self.s,old)
  rows=view['creatures'];self.assertEqual(len(rows),30)
  self.assertEqual({r['challengeTier'] for r in rows},{'Standard','Intermediate','Difficult'})
  self.assertEqual(rows,sorted(rows,key=lambda r:(('Standard','Intermediate','Difficult').index(r['challengeTier']),r['name'].casefold())))
  self.assertTrue(all(r['combat'] is None for r in rows))
 def test_bandit_pool_excludes_dryads_and_nymphs_but_rescues_keep_them(self):
  self.assertTrue({'dryad','nymph'}<=set(ep.SUPPORTED))
  self.assertFalse({'dryad','nymph','golem','spirit'}&set(ep.BANDITS))
  keys={ep.ancestry(ep.choose(random.Random(n),'capture')) for n in range(10000)}
  self.assertTrue(keys<=set(ep.BANDITS))
  for aid in ('dryad','nymph'):
   self.assertIsNone(ep.art(aid,'capture'));self.assertIn('/rescues/',ep.art(aid,'rescue'))
   s=deepcopy(self.s);who=world.make(s,aid.title(),'excluded-bandit-'+aid,'world-quest',aid)
   with self.assertRaises(g.RuleError):quests.lead(s,who,'capture',world=True)
   quests.lead(s,who,'rescue',world=True)

 def test_report_needs_work_phase_is_saved_and_cannot_reroll_today(self):
  self.s['currentDayPhase']='morning'
  self.act('world-reports');self.assertFalse(quests.saved(self.s));before=deepcopy(self.s)
  g.public_state(self.s);g.public_state(self.s);self.assertEqual(self.s,before)
  self.act('assign-founder',assignment='rest');self.act('advance');self.assertFalse(quests.saved(self.s))
  self.act('world-resume');self.act('advance');self.assertEqual(len(quests.saved(self.s)),1)
  old=deepcopy(quests.saved(self.s));self.reject('world-reports')
  loaded=g.migrate_state(json.loads(json.dumps(self.s)));self.assertEqual(quests.saved(loaded),old)
  self.assertNotIn('seed',g.public_state(self.s)['worldRecruitment'])
  self.assertTrue(quests.view(self.s)['quests'][0]['art'].startswith('/assets/bestiary/rescues/'))
 def test_one_percent_boundary_and_exclusions(self):
  class R:
   def __init__(self,n):self.n=n;self.pools=[]
   def random(self):return self.n
   def choice(self,pool):self.pools.append(pool);return pool[0]
  low=R(.00999);high=R(.01)
  self.assertIn(ep.choose(low),ep.EXOTIC);self.assertIn(ep.choose(high),ep.COMMON)
  self.assertFalse({'golem','spirit'}&set(ep.SUPPORTED))
  keys={ep.choose(random.Random(n)) for n in range(10000)}
  self.assertTrue(all(ep.ancestry(k) in ep.SUPPORTED for k in keys))
 def test_rare_elementals_have_exact_variant_art_for_both_quests(self):
  for element in ep.ELEMENTS:
   for kind in ('rescue','capture'):
    with self.subTest(element=element,kind=kind):
     s=deepcopy(self.s);who=world.make(s,'Elemental','test-'+element+kind,'world-quest','elemental-'+element)
     quests.lead(s,who,kind,world=True);q=quests.view(s)['quests'][0]
     self.assertIn('elemental-'+element+'.webp',q['art']);self.assertEqual(s['reviewedCandidates'][who]['profile']['elementalVariant'],element)
     with self.assertRaises(g.RuleError):quests.lead(s,who,kind,world=True)
  for ancestry in ('Spirit','Golem'):
   s=deepcopy(self.s);who=world.make(s,ancestry,'excluded-'+ancestry,'world-quest')
   with self.assertRaises(g.RuleError):quests.lead(s,who,'rescue',world=True)
   with self.assertRaises(g.RuleError):quests.lead(s,who,'capture',world=True)
 def test_magical_plan_preserves_identity_and_does_not_create_person(self):
  self.act('world-plan',ancestry='Djinn');who=next(w for w in self.s['reviewedCandidates'] if w.startswith('traveller-'))
  self.assertNotIn(who,self.s['people']);self.reject('world-plan',ancestry='Djinn')
  self.act('world-plan',ancestry='Golem',bodyMaterial='clay')
  golem=next(c for c in self.s['reviewedCandidates'].values() if c['profile']['ancestryLabel']=='Golem')
  self.assertEqual(golem['profile']['chronologicalAgeYears'],0)
 def introduce_spirit(self):
  self.s['headquarters']['rooms']['chapel']='complete'
  for c in ('name','limits','trial'):self.act('chapel-spirit-talk',choice=c)
  self.act('chapel-spirit-introduce')
 def test_spirit_discovery_is_gated_branching_and_not_instant_membership(self):
  self.assertIsNone(spirit.view(self.s));self.reject('chapel-spirit-talk',choice='name')
  self.s['headquarters']['rooms']['chapel']='complete';self.reject('chapel-spirit-introduce')
  self.introduce_spirit();self.assertNotIn('merrin',g.household_members(self.s));self.assertEqual(len(spirit.saved(self.s)['history']),3)
  self.reject('chapel-spirit-introduce');self.assertEqual(self.s['people']['merrin']['ancestryLabel'],'Spirit')
  self.assertEqual(spirit.saved(g.migrate_state(json.loads(json.dumps(self.s)))),spirit.saved(self.s))
 def recruit_spirit(self):
  self.introduce_spirit();cid='introduced-merrin';self.s['housingRooms']['west-chamber']['status']='complete'
  for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=cid,topic=topic)
  self.act('summoning-invite',contactId=cid,roomId='west-chamber');self.act('advance')
  self.assertNotIn('merrin',g.household_members(self.s))
  self.act('summoning-ask-stay',contactId=cid);self.act('summoning-household-decision',contactId=cid,decision='invite-to-stay')
 def test_spirit_household_project_dialogue_and_specialty(self):
  self.recruit_spirit();self.assertIn('merrin',g.household_members(self.s))
  self.act('talk-scripted-companion',characterId='merrin',topicId='company',choiceId='join')
  self.assertIn('magistrate',json.dumps(self.s['additionalResidents']['merrin']['conversation']))
  self.s['sharedFunds']=100;self.s['materialInventory']['binding-thread']=4;self.s['materialInventory']['sun-amber']=2
  self.act('start-companion-project',characterId='merrin')
  for _ in range(3):self.act('advance')
  self.assertEqual(self.s['additionalResidents']['merrin']['personalProject']['status'],'complete')
  self.assertIn('gentle-preservation',g.character_principles(self.s,'merrin'))
  self.act('choose-living-scene',sceneId='merrin:0',choice='private')
  self.act('hq-job',jobId='specialty-merrin')
  for _ in range(3):self.act('advance')
  self.assertEqual(self.s['headquarters']['stock']['specialty:merrin'],1)
  self.s['currentDayPhase']='morning';self.s['founderAssignment']='rest';field_magic.initialize(self.s)['vitality']['founder']=1
  self.act('advance');self.assertGreaterEqual(field_magic.vitality(self.s,'founder'),3)
  g.public_state(self.s)
 def test_custom_authoring_requires_cheats_but_old_saved_plans_are_kept(self):
  with tempfile.TemporaryDirectory() as td:
   store=GameStore(td);svc=DialogueService(ProviderSettings(td));payload=dict(requestId=uuid.uuid4().hex,expectedRevision=store.read()['revision'],purpose='candidate-proposal',source='offline',text='An adult visitor from the character pool.')
   with self.assertRaises(g.RuleError):svc.generate(store,payload)
   state=store.read();state['testing']['enabled']=True
   with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))
   draft=svc.generate(store,payload);self.assertEqual(draft['status'],'ready')
   accepted=svc.accept(store,dict(draftId=draft['id'],contentReviewed=True,mechanicsReviewed=True));self.assertTrue(accepted['testing']['used'])

class Provider118Tests(unittest.TestCase):
 def test_custom_endpoints_keys_and_no_auth_local(self):
  with tempfile.TemporaryDirectory() as td:
   settings=ProviderSettings(td);base=dict(enabled=True,model='example/model',maxOutputTokens=500,apiKey='secret')
   settings.save(base);self.assertNotIn('secret',json.dumps(settings.public()))
   before=settings.read()
   with self.assertRaises(g.RuleError):settings.save({**base,'apiKey':'','endpoint':'https://example.org/v1/chat/completions'})
   self.assertEqual(settings.read(),before)
   settings.save({**base,'apiKey':'','authMode':'none','endpoint':'http://localhost:1234/v1/chat/completions'})
   self.assertEqual(settings.read()['apiKey'],'')
   for url in ('http://example.org/v1/chat/completions','file:///tmp/a','https://user:secret@example.org/api','https://example.org/api?key=secret'):
    with self.assertRaises(g.RuleError):settings.save({**base,'endpoint':url})
 def test_three_text_formats_parse_usage_and_send_correct_auth(self):
  cases=[('openai',{'choices':[{'message':{'content':'Hello'}}],'usage':{'total_tokens':8}},'Authorization'),('anthropic',{'content':[{'type':'text','text':'Hello'}],'usage':{'input_tokens':3,'output_tokens':5}},'X-api-key'),('gemini',{'candidates':[{'content':{'parts':[{'text':'Hello'}]}}],'usageMetadata':{'totalTokenCount':8}},'X-goog-api-key')]
  for fmt,reply,header in cases:
   c=dict(enabled=True,format=fmt,endpoint='https://example.org/v1/{model}',model='text-model',apiKey='secret',maxOutputTokens=500)
   with patch('provider_protocols.open_request',return_value=io.BytesIO(json.dumps(reply).encode())) as call:r=provider_completion(c,[dict(role='system',content='Be concise'),dict(role='user',content='Hello')])
   self.assertEqual(r,{'text':'Hello','usage':{'total_tokens':8}} if fmt!='anthropic' else {'text':'Hello','usage':{'prompt_tokens':3,'completion_tokens':5,'total_tokens':8}})
   req=call.call_args.args[0];self.assertEqual(req.full_url,'https://example.org/v1/text-model');self.assertIn(header,dict(req.header_items()))
   body=json.loads(req.data);self.assertNotIn('tools',body)
   if fmt=='anthropic':self.assertEqual(body['system'],'Be concise');self.assertEqual(len(body['messages']),1)
 def test_image_formats_accept_only_embedded_data_and_error_redacts(self):
  data='data:image/png;base64,YQ=='
  cases=[('openai-images',{'data':[{'b64_json':'YQ=='}]}),('openrouter-images',{'choices':[{'message':{'images':[{'image_url':{'url':data}}]}}]}),('gemini-images',{'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/png','data':'YQ=='}}]}}]})]
  for fmt,reply in cases:
   c=dict(format=fmt,endpoint='https://example.org/images',model='image-model',apiKey='secret')
   with patch('provider_protocols.open_request',return_value=io.BytesIO(json.dumps(reply).encode())):self.assertEqual(provider_image(c,'A portrait'),data)
  with patch('provider_protocols.open_request',side_effect=RuntimeError('secret')):
   with self.assertRaises(g.RuleError) as err:provider_image(c,'A portrait')
   self.assertNotIn('secret',str(err.exception))
