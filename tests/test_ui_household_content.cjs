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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));
 await click({packAction:'bundled'});
 assert.equal(vm.runInContext('contentPackReport.recordCount',context),3595);
 element('#content-pack-reviewed').checked=true;
 await click({packAction:'activate',packDigest:vm.runInContext('contentPackReport.digest',context)});
 await click({view:'household'});assert.match(element('#app').innerHTML,/Open household life/);
 await click({view:'householdContent'});await click({householdContent:'load'});
 assert.match(element('#app').innerHTML,/Separate books, shared quiet/);
 const requirements=vm.runInContext('householdContentChoices.residents.mira.scenes[0].requirements',context);
 requirements.forEach((r,i)=>element('#scene-evidence-'+i).value='Reviewed: '+r);
 element('#scene-prerequisites-reviewed').checked=true;
 await click({householdContent:'propose'});
 const scene=vm.runInContext('Object.keys(state.householdScenes)[0]',context);
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'draft');
 await click({householdContent:'approve',sceneId:scene});
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'draft');
 element('#scene-reviewed-'+scene).checked=true;
 await click({householdContent:'approve',sceneId:scene});
 await click({householdContent:'defer',sceneId:scene});
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'deferred');
 await click({householdContent:'restore',sceneId:scene});
 await click({householdContent:'join',sceneId:scene,choiceIndex:'0'});
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'remembered');
 element('#household-ensemble').value='ensemble-001';
 await click({householdContent:'ensemble'});assert.match(element('#household-ensemble-preview').innerHTML,/Cream linen work shirt/);
 element('#household-style-name').value='Quiet <reading>';
 element('#household-anatomy-reviewed').checked=true;element('#household-style-agreed').checked=true;
 await click({householdContent:'save-style'});
 const style=vm.runInContext('Object.keys(state.residentStyles.mira)[0]',context);
 assert(style);assert.match(element('#app').innerHTML,/Quiet &lt;reading&gt;/);
 element('#household-wear-agreed').checked=true;
 await click({householdContent:'wear-style',styleId:style});
 assert.equal(vm.runInContext('state.residentCurrentStyles.mira',context),style);
 const pattern=vm.runInContext('householdContentChoices.residents.mira.patterns[0]',context);
 pattern.requiredEstablishedFacts.forEach((r,i)=>element('#pattern-evidence-'+i).value='Established in the fixture: '+r);
 element('#pattern-prerequisites-reviewed').checked=true;
 await click({householdContent:'choose-pattern'});
 assert.equal(vm.runInContext('state.residentStoryPatterns.mira.pattern.id',context),pattern.id);
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));await click({packAction:'deactivate'});
 await click({view:'householdContent'});
 assert.match(element('#app').innerHTML,/Quiet &lt;reading&gt;/);
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'remembered');
 await click({householdContent:'restore-look'});
 assert.equal(vm.runInContext('state.residentCurrentStyles.mira',context),undefined);
 console.log('PASS: full bundled pack, reviewed scene prerequisites, invitation/defer/join, garment review, saved styling, story pattern and persistence after deactivation.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
