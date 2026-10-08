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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 assert.match(element('#app').innerHTML,/Character content packs/);
 const buffer=fs.readFileSync('static/examples/content-pack-fixture.zip');
 element('#content-pack-file').files=[{size:buffer.length,arrayBuffer:async()=>buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength)}];
 await click({packAction:'validate'});
 assert.equal(vm.runInContext('contentPackReport.valid',context),true);
 assert.equal(vm.runInContext('state.activeContentPack',context),null);
 const digest=vm.runInContext('contentPackReport.digest',context);
 await click({packAction:'activate',packDigest:digest});
 assert.equal(vm.runInContext('state.activeContentPack',context),null);
 await click({packAction:'preview',packDigest:digest});
 assert.match(element('#app').innerHTML,/Content browser/);
 assert.match(element('#app').innerHTML,/Talvera/);
 element('#pack-browser-group').value='Shared / conversational-voice';
 await click({packAction:'browse-group'});assert.match(element('#app').innerHTML,/Dry warmth/);
 element('#content-pack-reviewed').checked=true;
 await click({packAction:'activate',packDigest:digest});
 assert.equal(vm.runInContext('state.activeContentPack.digest',context),digest);
 await click({view:'candidateReview'});
 element('#pool-contentSource').value='imported';element('#pool-ancestry').value='Wolfkin';
 // Built-in selections are ignored in imported mode, as the form explains.
 element('#pool-background').value='glassworker';
 await click({candidateDraft:'offline'});
 assert.equal(vm.runInContext('candidateProposal.status',context),'ready');
 assert.match(element('#app').innerHTML,/Source ingredients/);
 assert.match(element('#app').innerHTML,/Revise this draft/);
 assert(!element('#app').innerHTML.includes('undefined'));
 const original=vm.runInContext('JSON.parse(JSON.stringify(candidateProposal.proposal))',context);
 for(const [key,value] of Object.entries(original))element('#candidate-edit-'+key).value=value;
 element('#candidate-edit-name').value='<Test visitor>';
 element('#candidate-edit-ambition').value='Create a useful folio of observations.';
 await click({candidateDraft:'edit'});
 assert.equal(vm.runInContext('candidateProposal.editRevision',context),1);
 assert.match(element('#app').innerHTML,/&lt;Test visitor&gt;/);
 assert(!element('#app').innerHTML.includes('<Test visitor>'));
 element('#candidate-content-reviewed').checked=true;element('#candidate-mechanics-reviewed').checked=true;
 await click({candidateDraft:'approve'});
 const who=vm.runInContext('selectedSummoningPerson',context);
 assert.equal(vm.runInContext(`state.reviewedCandidates['${who}'].profile.name`,context),'<Test visitor>');
 assert.match(element('#app').innerHTML,/&lt;Test visitor&gt;/);
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));
 await click({packAction:'deactivate'});
 assert.equal(vm.runInContext('state.activeContentPack',context),null);
 assert.equal(vm.runInContext(`state.reviewedCandidates['${who}'].profile.generationIngredients.pack.digest`,context),digest);
 await click({packAction:'list'});assert.equal(vm.runInContext('contentPackReports.length',context),1);
 console.log('PASS: ZIP upload, validation warnings, content browser, explicit activation, imported offline candidate, field editing, escaped output, approval and source preservation.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
