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
 const act=async action=>{await value('commit('+JSON.stringify(action)+')');};
 await click({view:'castleChapter'});assert.match(element('#app').innerHTML,/Weatherproofing the castle/);assert.match(element('#app').innerHTML,/Quarry shelter/);assert.doesNotMatch(element('#app').innerHTML,/undefined/);
 const revision=value('state.revision');await click({chapterStep:'quarry-shelter'});assert.equal(value('currentView'),'expeditions');assert.equal(value('selectedExpeditionSiteId'),'quarry-shelter');assert.equal(value('state.revision'),revision);
 assert.match(element('#app').innerHTML,/Complete your first hearth-ward study/);assert.match(element('#app').innerHTML,/destination-grid/);
 await act({type:'start-research'});for(let i=0;i<3;i++)await act({type:'advance'});
 await act({type:'set-material-reserve',materialId:'sun-amber',target:value('state.materialInventory["sun-amber"]')});await click({view:'workshop'});assert.match(element('#app').innerHTML,/will use reserved stock/);
 await click({soloCraft:'yes'});for(let i=0;i<2;i++)await act({type:'advance'});
 await act({type:'start-expedition',siteId:'quarry-shelter',carryLantern:true});await act({type:'advance'});await act({type:'choose-expedition-approach',approach:'survey'});await act({type:'advance'});await act({type:'return-expedition'});await act({type:'advance'});
 await click({view:'castleChapter'});assert.match(element('#app').innerHTML,/The practical margin/);
 await click({chapterChoice:'care',chapterScene:'shutter-notes'});assert.match(element('#app').innerHTML,/Remembered on day/);assert.equal(value('state.castleChapter.memories["shutter-notes"].choice'),'care');
 await act({type:'focus-research',researchId:'weather-sealing',leaderId:'founder'});await act({type:'advance'});await act({type:'advance'});
 await click({chapterStep:'weather-screen'});assert.match(element('#app').innerHTML,/assets\/objects\/weather-screen.webp/);assert.equal(value('selectedRecipeId'),'weather-screen');assert.equal(value('currentView'),'fullWorkshop');assert.doesNotMatch(element('#app').innerHTML,/undefined/);
 await click({view:'householdWork'});assert.match(element('#app').innerHTML,/Who can help with what/);assert.match(element('#app').innerHTML,/Scholarship 0/);assert.match(element('#app').innerHTML,/Weather sealing/);
 await click({hqRoom:'library'});assert.match(element('#app').innerHTML,/in this room/);assert.match(element('#app').innerHTML,/Nobody is here at the moment/);
 await click({roomWork:'castleChapter'});assert.equal(value('roomContext'),'library');assert.match(element('#app').innerHTML,/Room activities/);
 await click({view:'expeditions'});assert.match(element('#app').innerHTML,/Arrange the first archive/);assert.match(element('#app').innerHTML,/Ridge cistern/);
 console.log('PASS: notebook navigation, returned discovery and reflection persistence, personal knowledge, reserve warning, room presence and seven responsive destination cards.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
