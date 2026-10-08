// Reviewed candidate connected UI regression.
// Headless template and controller integration checks; not browser/layout QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');
const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'castle-ui-'));
const elements = new Map();
const events = {};
function element(id) {
  if (!elements.has(id)) elements.set(id, {innerHTML:'',textContent:'',classList:{add(){},remove(){}},addEventListener(type, callback){events[type]=callback;},showModal(){this.open=true;}});
  return elements.get(id);
}
let dropCreationResponse = false;
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/validate':result=store.validate_expansion_pack(payload)\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/dialogue/drafts':\n  with store.connect() as db:result={'drafts':[json.loads(r[0]) for r in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC')]}\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  def completion(settings,messages):\n   scene=next(iter(store.read()['householdScenes'].values()))\n   return {'text':json.dumps({'title':'A shared quiet','invitation':'Company?','opening':'She leaves room beside her.','replies':['She respects your choice.']*len(scene['choices'])}),'usage':{'total_tokens':80}}\n  svc=DialogueService(ProviderSettings(sys.argv[1]),completion)\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8'}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});




(async()=>{try {
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings\ns=CampaignLibrary(sys.argv[1]).get('default');state=s.read();state['craftedArtifacts']['scholars-folio']=1\nwith s.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(state),))\nProviderSettings(sys.argv[1]).save({'enabled':True,'model':'mock','apiKey':'test-only','maxOutputTokens':1500})",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'focus'});assert.match(element('#app').innerHTML,/Personal working tools/);
 await click({view:'equipment'});await click({toolAction:'claim',itemId:'scholars-folio'});
 const item=vm.runInContext('Object.keys(state.personalEquipment)[0]',context);assert(item);
 await click({toolAction:'prepare',itemId:item});assert.equal(vm.runInContext('state.preparedEquipment.founder',context),item);
 element('#tool-name-'+item).value='Violet <notes>';await click({toolAction:'rename',itemId:item});assert.match(element('#app').innerHTML,/Violet &lt;notes&gt;/);
 element('#tool-recipient-'+item).value='mira';element('#tool-agreed-'+item).checked=true;
 await click({toolAction:'transfer',itemId:item});assert.equal(vm.runInContext(`state.personalEquipment['${item}'].ownerId`,context),'mira');
 assert.equal(vm.runInContext('state.preparedEquipment.founder',context),undefined);
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));await click({packAction:'bundled'});
 element('#content-pack-reviewed').checked=true;await click({packAction:'activate',packDigest:vm.runInContext('contentPackReport.digest',context)});
 await click({view:'householdContent'});await click({householdContent:'load'});
 const reqs=vm.runInContext('householdContentChoices.residents.mira.scenes[0].requirements',context);
 reqs.forEach((r,i)=>element('#scene-evidence-'+i).value='Reviewed fixture: '+r);element('#scene-prerequisites-reviewed').checked=true;
 await click({householdContent:'propose'});const scene=vm.runInContext('Object.keys(state.householdScenes)[0]',context);
 await click({sceneDraft:'new',sceneId:scene});assert.equal(vm.runInContext(`sceneProposals['${scene}'].status`,context),'ready');
 await click({sceneDraft:'retry',sceneId:scene});await click({sceneDraft:'recover',sceneId:scene});
 element('#scene-model-reviewed-'+scene).checked=true;await click({sceneDraft:'apply',sceneId:scene});
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].title`,context),'A shared quiet');
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'draft');
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));
 const bytes=fs.readFileSync('static/examples/expansion-design-fixture.zip');element('#expansion-file').files=[{size:bytes.length,async arrayBuffer(){return bytes;}}];
 const revision=vm.runInContext('state.revision',context);
 await click({expansionAction:'validate'});assert.equal(vm.runInContext('expansionReport.valid',context),true);
 await click({expansionAction:'load'});const digest=vm.runInContext('expansionReports[0].digest',context);
 await click({expansionAction:'preview',digest});element('#expansion-record').value='ss-material-waxed-linen';
 await click({expansionAction:'record'});assert.match(element('#expansion-record-preview').innerHTML,/Waxed linen cord/);
 assert.equal(vm.runInContext('state.revision',context),revision);
 console.log('PASS: equipment ownership/preparation/transfer, recoverable reviewed scene prose and read-only expansion ZIP review.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
