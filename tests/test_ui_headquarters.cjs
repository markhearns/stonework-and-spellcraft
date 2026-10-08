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
  if (!elements.has(id)) elements.set(id, {innerHTML:'',textContent:'',classList:{add(){},remove(){}},addEventListener(type, callback){events[type]=callback;},showModal(){this.open=true;},close(){this.open=false;}});
  return elements.get(id);
}
let dropCreationResponse = false;
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/portrait-settings':\n  from portrait_generation import PortraitSettings\n  result=PortraitSettings(sys.argv[1]).public()\n elif url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{search:'?campaign=default',reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8',maxBuffer:32*1024*1024}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});



(async()=>{try {
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'headquarters'});
 assert.match(element('#app').innerHTML,/Rooms with a purpose/);
 for(const name of ['Library &amp; archive','Warehouse &amp; stores','Smithy &amp; armoury','Chapel &amp; sanctuary','Underground living quarters','Dungeon ward','Training yard','Hot spring baths'])assert.ok(element('#app').innerHTML.includes(name),name);
 for(const id of value('Object.keys(state.headquartersView.catalogue)'))assert.ok(element('#app').innerHTML.includes(value('state.originalAssets['+JSON.stringify(id)+']')),id+' artwork');
 const revision=value('state.revision');await click({hqRoom:'chapel'});assert.equal(value('state.revision'),revision);
 assert.match(element('#app').innerHTML,/no magical knowledge required/);
 assert.match(element('#app').innerHTML,/\/assets\/rooms\/chapel.webp/);
 await click({hqAction:'hq-build',roomId:'chapel'});
 assert.equal(value('state.founderAssignment'),'headquarters');assert.equal(value('state.sharedFunds'),22);
 assert.match(element('#app').innerHTML,/0 \/ 2 phases/);
 await click({action:'advance'});await click({founder:'rest'});await click({action:'advance'});
 assert.equal(value('state.headquarters.project.done'),1);
 assert.match(element('#app').innerHTML,/Paused; progress kept/);
 await click({hqAction:'hq-resume'});await click({action:'advance'});
 assert.equal(value('state.headquarters.rooms.chapel'),'complete');
 await click({hqAction:'hq-scene',roomId:'chapel',choice:'reflect'});
 assert.match(element('#app').innerHTML,/consider what you want this home to stand for/);
 await click({hqRoom:'vault'});assert.match(element('#app').innerHTML,/two different core expedition sites/);assert.match(element('#app').innerHTML,/data-disabled-reason=/);
 await click({hqRoom:'library'});assert.match(element('#app').innerHTML,/correspondence, private study, shared reading and bookbinding/);
 await click({hqArt:'chapel'});assert.equal(value('reviewAssetId'),'chapel');assert.equal(value('currentView'),'review');
 await click({view:'containment'});assert.match(element('#app').innerHTML,/ember-chamber-family.webp/);assert.match(element('#app').innerHTML,/quiet-chamber-family.webp/);
 await click({hqArt:'echo-1'});assert.equal(value('reviewAssetId'),'echo-1');assert.match(element('#app').innerHTML,/Quiet chamber 1/);
 await click({view:'housing'});assert.match(element('#app').innerHTML,/Lower private suite/);assert.match(element('#app').innerHTML,/Guard dormitory/);assert.match(element('#app').innerHTML,/Complete Underground living quarters/);
 console.log('PASS: headquarters navigation, construction, pause/resume, optional chapel scene, prerequisites, art target and gated bedrooms.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
