"""Public bundle integration: real saves, immutable review and explicit invitations."""
from copy import deepcopy
from pathlib import Path
import io,json,sqlite3,tempfile,unittest,uuid,zipfile
from unittest.mock import patch
import expansion_packs,game,household_content as h,public_content
from server import GameStore,ConflictError
from test_content_packs import change,zip_payload

FOUNDATION,FOUNDATION_REPORT,REVIEWED=public_content.review_bundle(Path('content/stonework-and-spellcraft-public-packs.zip'))
PACK,REPORT=next((p,r) for p,r in REVIEWED if 'scenes' in r['packId'])
SEED=next(v for k,v in PACK['entries'].items() if PACK['types'][k]=='scene-template' and v['participants']=='npc-player' and not v['ancestryRestrictions'])
def proposal(seed=SEED,people=None):
 return {'type':'propose-expansion-scene','ownerId':'mira','packDigest':REPORT['digest'],'recordId':seed['id'],'participants':people or ['mira'],'templateReviewed':True,'prerequisitesReviewed':True,'requirementEvidence':['Human review establishes the context in this fixture.']*(len(seed['establishedFactRequirements'])+1)}

class PublicContentTests(unittest.TestCase):
 def test_full_bundle_counts_idempotence_reload_and_backup(self):
  self.assertEqual(FOUNDATION_REPORT['digest'],'95a4ac6af6c67709215604bb26923aeb1f1c42fdeb48c7e5c86797b655ec4831')
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);before=store.read();r=store.stage_public_bundle()
   self.assertEqual((len(r['packs']),r['contentCount'],r['mechanicsCount']),(16,1599,319))
   self.assertEqual(store.stage_public_bundle(),r);self.assertEqual(store.read(),before)
   self.assertEqual(len(GameStore(d).expansion_pack_catalogue()['packs']),16)
   with zipfile.ZipFile(io.BytesIO(store.backup_archive())) as z:z.extract('campaign.sqlite3',d+'/backup')
   with sqlite3.connect(d+'/backup/campaign.sqlite3') as db:self.assertEqual(db.execute('SELECT count(*) FROM expansion_packs').fetchone()[0],16)
 def test_conflicting_bundle_rolls_back_without_partial_staging(self):
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);p,r=REVIEWED[0];changed=deepcopy(p['sourceFiles']);changed['README.md']+=' Different review.'
   self.assertTrue(store.validate_expansion_pack(zip_payload(changed))['valid'])
   with self.assertRaises(game.RuleError):store.stage_public_bundle()
   self.assertEqual(len(store.expansion_pack_catalogue()['packs']),1)
   self.assertEqual(store.content_pack_catalogue()['packs'],[])
 def test_scene_transaction_retry_stale_guard_and_join(self):
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);store.stage_public_bundle();before=store.read()
   request={'requestId':str(uuid.uuid4()),'expectedRevision':before['revision'],'action':proposal()}
   state=store.action(request);self.assertEqual(store.action(request),state)
   with self.assertRaises(ConflictError):store.action({**request,'requestId':str(uuid.uuid4())})
   key=next(iter(state['householdScenes']));self.assertEqual(state['householdScenes'][key]['status'],'draft')
   self.assertEqual(GameStore(d).read()['householdScenes'],state['householdScenes'])
   def act(kind,**fields):return store.action({'requestId':str(uuid.uuid4()),'expectedRevision':store.read()['revision'],'action':{'type':kind,'sceneId':key,**fields}})
   with self.assertRaises(game.RuleError):act('join-content-scene',choiceIndex=0)
   act('approve-content-scene',contentReviewed=True)
   act('join-content-scene',choiceIndex=2);self.assertEqual(h.context(store.read(),'mira'),[])
   act('restore-content-scene');state=act('join-content-scene',choiceIndex=0)
   self.assertEqual(state['householdScenes'][key]['status'],'remembered')
   self.assertEqual(len(h.context(state,'mira')),1);self.assertEqual(h.context(state,'tamsin'),[])
   for field in ('dayNumber','currentDayPhase','sharedFunds','materialInventory','resonancePoints','activeContentPack'):
    if field in before:self.assertEqual(state[field],before[field])
   self.assertEqual(state['householdScenes'][key]['seed'],SEED)
 def test_scene_prerequisites_presence_participants_and_ancestry(self):
  for fields in ({'templateReviewed':False},{'requirementEvidence':[]},{'participants':['eris']},{'participants':['selene']},{'participants':['mira','mira']}):
   state=game.new_campaign();before=deepcopy(state)
   with self.assertRaises(game.RuleError):public_content.compose_scene(state,{**proposal(),**fields},PACK,REPORT)
   self.assertEqual(state,before)
  state=game.new_campaign();state['expedition']={'companionId':'mira'}
  with self.assertRaises(game.RuleError):public_content.compose_scene(state,proposal(),PACK,REPORT)
  altered=deepcopy(PACK);altered['entries'][SEED['id']]['ancestryRestrictions']=['seraph']
  with self.assertRaises(game.RuleError):public_content.compose_scene(game.new_campaign(),proposal(),altered,REPORT)
 def test_nested_invalid_objects_and_private_templates_fail_cleanly(self):
  deps=[public_content.foundation_dependency(FOUNDATION)]+[p for p,r in REVIEWED if p is not PACK]
  filename=next(f['path'] for f in PACK['manifest']['files'] if f['recordType']=='scene-template')
  for field,value in [('choices',[None]),('choices',[{'id':[]}]),('visibility','private-template'),('establishedFactRequirements',[{}])]:
   files=deepcopy(PACK['sourceFiles']);change(files,filename,lambda x:x['entries'][0].update({field:value}))
   self.assertFalse(expansion_packs.validate(files,deps)[1]['valid'])
  files=deepcopy(PACK['sourceFiles']);change(files,'vocabulary.json',lambda x:x.update(tags=[{'id':'incomplete'}]))
  self.assertFalse(expansion_packs.validate(files,deps)[1]['valid'])
 def test_all_eighty_templates_compose_with_their_required_group_size(self):
  for key,seed in PACK['entries'].items():
   if PACK['types'][key]!='scene-template':continue
   state=game.new_campaign();state['additionalResidents']['tamsin']['status']='resident';state['bedroomAssignments']['tamsin']='bedchamber'
   people=['mira'] if seed['participants']=='npc-player' else ['mira','tamsin']
   public_content.compose_scene(state,proposal(seed,people),PACK,REPORT)
   scene=next(iter(state['householdScenes'].values()))
   self.assertEqual(scene['status'],'draft');self.assertTrue(any(c['kind']=='decline' for c in scene['choices']))

 def test_real_http_bundle_route_and_scene_action(self):
  import threading,urllib.request
  from server import create_server
  with tempfile.TemporaryDirectory() as d:
   server=create_server('127.0.0.1',0,d);worker=threading.Thread(target=lambda:server.serve_forever(poll_interval=.05),daemon=True);worker.start()
   def request(path,payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request('http://127.0.0.1:'+str(server.server_address[1])+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as response:return json.load(response)
   try:
    report=request('/api/expansion-packs/bundled',{});self.assertEqual(len(report['packs']),16)
    state=request('/api/state')
    state=request('/api/action',{'requestId':str(uuid.uuid4()),'expectedRevision':state['revision'],'action':proposal()})
    self.assertEqual(len(state['householdScenes']),1)
   finally:server.shutdown();worker.join();server.server_close()
