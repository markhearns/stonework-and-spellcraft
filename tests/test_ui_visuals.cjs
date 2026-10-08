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
 let prevented=false;
 const click=dataset=>events.click({preventDefault(){prevented=true;},target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'localEncounters'});
 let html=element('#app').innerHTML;
 assert.match(html,/data-person-portrait="fenna"/);
 assert.match(html,/Return with a discovery from the fern nursery/);
 assert.match(html,/data-site="fern-nursery"/);
 const fenna=html.match(/<button[^>]*data-encounter-id="fenna"[^>]*>/)[0];
 assert.match(fenna,/aria-disabled="true"/);
 assert.match(fenna,/data-disabled-reason="Return with a discovery from the fern nursery/);
 const revision=vm.runInContext('state.revision',context);
 await click({localEncounterAction:'start-local-visit',encounterId:'fenna',disabledReason:'Return with a discovery from the fern nursery.'});
 assert.equal(vm.runInContext('state.revision',context),revision);
 assert.equal(element('#unavailable-dialog').open,true);
 assert.equal(prevented,true,'Unavailable submit buttons must cancel the default form submission');
 assert.match(element('#unavailable-content').textContent,/fern nursery/);
 await click({site:'fern-nursery'});
 assert.equal(vm.runInContext('selectedExpeditionSiteId',context),'fern-nursery');
 assert.equal(vm.runInContext('currentView',context),'expeditions');
 // Every unavailable button remains keyboard accessible, but cannot submit.
 const views=['castle','estateHub','studyHub','peopleHub','worldHub','ledger','stores','housing','research','restoration','workshop','fullWorkshop','development','spells','focus','rituals','summoning','contacts','householdWork','localEncounters','journal','cheats','phaseTasks'];
 for(const view of views){
   await click({view});html=element('#app').innerHTML;
   assert(!/<button\b[^>]*\sdisabled(?:=|\s|>)/.test(html),view+' left a non-focusable disabled button');
   for(const tag of html.match(/<button\b[^>]*aria-disabled="true"[^>]*>/g)||[])assert.match(tag,/data-disabled-reason="[^"]+"/);
   assert(!html.includes('src="undefined"'),view+' has a broken image reference');
 }
 const sample=vm.runInContext(`illustrateNames('<p>Fenna spoke to Maren.</p><input value="Fenna"><textarea>Fenna</textarea><select><option>Fenna</option></select><p>Fennarium</p>')`,context);
 assert.equal((sample.match(/data-person-portrait=/g)||[]).length,2);
 assert(sample.includes('<textarea>Fenna</textarea>'));
 assert(sample.includes('<option>Fenna</option>'));
 assert(sample.includes('<input value="Fenna">'));
 vm.runInContext("state.assetOverrides.fenna='/api/art/fenna.png'",context);
 assert.match(vm.runInContext("portraitImage('fenna')",context),/api\/art\/fenna.png\?campaign=default/);
 assert.match(vm.runInContext("portraitImage('founder')",context),/portrait not yet illustrated/);
 assert.match(vm.runInContext(`presentUI('<select><option disabled data-disabled-reason="Return home">Fenna</option></select>')`,context),/Why are some choices unavailable/);
 assert.match(vm.runInContext("activityImage('restoration')",context),/conservatory/);
 console.log('PASS: unavailable action explanations without mutations, Fenna route, portraits, editable fields, image overrides, native select help and all main view rendering.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
