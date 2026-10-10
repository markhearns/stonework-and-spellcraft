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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{search:'',reload(){}},
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
 await click({view:'fullWorkshop'});
 let html=element('#app').innerHTML;
 assert.match(html,/data-painted-item="warming-lantern"/);
 assert.match(html,/materials-atlas.webp/);
 assert.match(html,/workshop-atlas.webp/);
 assert.match(html,/painted-detail/);
 assert(!/[♜✧♧⌑⌂✎◇⌁≡▤⚙]/.test(html),'Decorative font symbols remain');
 const source=fs.readFileSync('static/app.js','utf8');
 assert(!/[♜✧♧⌑⌂✎◇⌁≡▤⚙]/.test(source),'Decorative font symbols remain in templates');
 for(const id of vm.runInContext('Object.keys(state.recipeCatalog)',context))assert.match(vm.runInContext('paintedIcon('+JSON.stringify(id)+')',context),['weather-screen','cistern-filter'].includes(id)?/objects/:/workshop-atlas.webp/);
 for(const id of vm.runInContext('Object.keys(state.materialCatalog)',context))assert.match(vm.runInContext('paintedIcon('+JSON.stringify(id)+')',context),/materials-atlas.webp/);
 const words=vm.runInContext(`illustrateNames('<p>Fenna greets Fenna. Koharu smiles at Fenna.</p><p>Fenna returns.</p><button>Fenna</button><textarea>Fenna</textarea>')`,context);
 assert.equal((words.match(/data-person-portrait="fenna"/g)||[]).length,3,'One portrait per character per independent block');
 assert.equal((words.match(/data-person-portrait="koharu"/g)||[]).length,1);
 assert(words.includes('<textarea>Fenna</textarea>'));
 for(const file of ['workshop-atlas.webp','materials-atlas.webp','midnight-paper.webp','botanical-frame.webp','castle-emblem.webp']){
  const bytes=fs.readFileSync('static/assets/ui/'+file);assert.equal(bytes.subarray(8,12).toString(),'WEBP');
 }
 for(const view of ['castle','estateHub','studyHub','peopleHub','worldHub','stores','phaseTasks','goals','research','localEncounters','development','expeditions','resonance','settings']){await click({view});html=element('#app').innerHTML;assert(!html.includes('src="undefined"'),view);assert.match(html,/castle-emblem.webp/);}
 await click({view:'publicWorkshop'});await new Promise(resolve=>setImmediate(resolve));
 assert.match(element('#app').innerHTML,/(Category|Object) illustration/);
 assert.match(element('#app').innerHTML,/data-public-action="inspect"/);
 console.log('PASS: generated raster artwork wired to all core items/materials, navigation and public categories; repeated portrait reduction; core views and labels retained.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
