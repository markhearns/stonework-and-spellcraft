from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game as g
import household_content as h
import scene_drafts
from dialogue import DialogueService,ProviderSettings
from server import GameStore
from test_household_content import PACK,REPORT

class SceneDraftTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.store=GameStore(self.temp.name);s=self.store.read();s['activeContentPack']=REPORT['summary']
  seed=next(r for r in PACK['shared']['household-interaction'] if r['participants']=='npc-player')
  h.apply(s,{'type':'propose-content-scene','ownerId':'mira','packDigest':REPORT['digest'],'seedId':seed['id'],'participants':['mira'],'prerequisitesReviewed':True,'requirementEvidence':['Fixture reviewed agreement.']*len(seed['requirements'])},PACK)
  self.key=next(iter(s['householdScenes']));self.original=s
  with self.store.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(s),))
  settings=ProviderSettings(self.temp.name);settings.save({'enabled':True,'model':'test-model','maxOutputTokens':1500,'apiKey':'test-only-key'})
  self.proposal={'title':'Between the shelves','invitation':'Will you sit with me?','opening':'She leaves an inviting space beside her.','replies':['She respects the choice.']*len(s['householdScenes'][self.key]['choices'])}
  self.calls=[]
  def completion(settings,messages):self.calls.append(messages);return {'text':json.dumps(self.proposal),'usage':{'total_tokens':35}}
  self.service=DialogueService(settings,completion)
  self.payload={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'purpose':'scene-proposal','sceneId':self.key,'text':'Warm, playful company.'}
 def test_provider_retry_review_apply_and_separate_approval(self):
  d=self.service.generate(self.store,self.payload);self.assertEqual(d['status'],'ready',d)
  self.assertEqual(self.service.generate(self.store,self.payload),d);self.assertEqual(len(self.calls),1)
  self.assertEqual(self.store.read(),self.original)
  with self.assertRaises(g.RuleError):self.service.accept(self.store,{'draftId':d['id']})
  saved=self.service.accept(self.store,{'draftId':d['id'],'contentReviewed':True})
  self.assertEqual(saved['householdScenes'][self.key]['status'],'draft')
  self.assertEqual(saved['householdScenes'][self.key]['title'],self.proposal['title'])
  self.assertEqual(self.service.accept(self.store,{'draftId':d['id'],'contentReviewed':True}),saved)
  self.assertEqual(saved['dayNumber'],self.original['dayNumber']);self.assertEqual(saved['sharedFunds'],self.original['sharedFunds'])
 def test_stale_campaign_and_invalid_provider_shape(self):
  d=self.service.generate(self.store,self.payload)
  self.store.action({'requestId':uuid.uuid4().hex,'expectedRevision':self.original['revision'],'action':{'type':'advance'}})
  with self.assertRaises(g.RuleError):self.service.accept(self.store,{'draftId':d['id'],'contentReviewed':True})
  for value in [{**self.proposal,'reward':100},{**self.proposal,'replies':[]},{**self.proposal,'title':True}]:
   with self.assertRaises(g.RuleError):scene_drafts.validate(json.dumps(value),self.original,self.key)
 def test_private_history_excluded_and_no_permission_inference(self):
  s=deepcopy(self.original);s['privateCastleLore']={'secret':'PRIVATE_SENTINEL'};s['dialogueHistory']=[{'text':'PRIVATE_SENTINEL'}]
  self.assertNotIn('PRIVATE_SENTINEL',json.dumps(scene_drafts.context(s,self.key,'Hello')))
  self.assertTrue(h.verified_requirement(s,'A suitable shared reading space is available.'))
  self.assertIsNone(h.verified_requirement(s,'Both residents choose to participate.'))
  evidence=h.review_requirements(['A suitable shared reading space is available.'],{'requirementEvidence':[''],'prerequisitesReviewed':True},s)
  self.assertTrue(evidence[0]['verifiedByRules'])
  with self.assertRaises(g.RuleError):h.review_requirements(['Both residents choose to participate.'],{'requirementEvidence':[''],'prerequisitesReviewed':True},s)
  s['householdScenes'][self.key]['status']='waiting'
  with self.assertRaises(g.RuleError):scene_drafts.context(s,self.key,'Hello')
