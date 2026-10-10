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
    if(json.error)console.error(url,json.error);return {ok:!json.error,async json(){return json;}};
  }
});



(async()=>{try {
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=a=>value('commit('+JSON.stringify(a)+')');
 assert.equal(value('APP_VERSION'),'0.119');assert.equal(value('state.schemaVersion'),76);
 await click({view:'candidateReview'});
 assert.match(element('#app').innerHTML,/Ask about missing travellers/);assert.doesNotMatch(element('#app').innerHTML,/id="candidate-proposal-form"|Create visitor from selected traits|Cheats · custom character authoring/);
 assert.match(element('#app').innerHTML,/dryads and nymphs can be rescued but never appear as bandits/);
 assert.doesNotMatch(value('dayPhaseIndicator()'),/Day \d/);
 assert.match(fs.readFileSync('static/style.css','utf8'),/\.header-day/);
 const destinations=value('regionMap()');assert.equal((destinations.match(/class="destination-art"/g)||[]).length,value('Object.keys(state.expeditionSites).length'));
 for(const m of destinations.matchAll(/src="([^"]+)"/g)){assert.ok(fs.existsSync('static'+m[1].split('?')[0]),m[1]);assert.doesNotMatch(m[1],/castle-emblem/);}
 await click({view:'bestiary'});assert.match(element('#app').innerHTML,/Challenge rank/);
 await events.change({target:{id:'bestiary-rank',value:'Difficult'}});assert.equal(value('bestiaryRank'),'Difficult');
 assert.equal((value('bestiaryPage()').match(/data-bestiary-entry=/g)||[]).length,5);
 await click({bestiaryReset:'yes'});assert.equal(value('bestiaryRank'),'all');
 await click({view:'settings'});await new Promise(resolve=>setImmediate(resolve));
 assert.match(element('#app').innerHTML,/Nine connected chapters/);assert.match(element('#app').innerHTML,/DEVELOPMENT 0.119/);assert.match(element('#app').innerHTML,/Anthropic Messages/);assert.match(element('#app').innerHTML,/OpenAI-compatible image generation/);assert.match(element('#app').innerHTML,/id="portrait-endpoint"/);
 await act({type:'cheat-toggle',enabled:true});await act({type:'cheat-recruit',characterId:'mira'});
 const one=value(`illustrateNames('<p>'+portraitImage('mira')+'<strong>Mira</strong> · reading</p>')`);
 assert.equal((one.match(/data-person-portrait="mira"/g)||[]).length,1);
 await act({type:'cheat-recruit',characterId:'tamsin'});
 const two=value(`illustrateNames('<p>'+portraitImage('mira')+'<strong>Mira</strong> and '+portraitImage('tamsin')+'<strong>Tamsin</strong></p>')`);
 assert.equal((two.match(/data-person-portrait=/g)||[]).length,2);
 await act({type:'cheat-build',buildingId:'chapel'});
 assert.match(value('roomPresencePanel("chapel")'),/Someone at the chapel table/);
 assert.equal((value('chapelSpiritPanel()').match(/chapel-spirit-talk/g)||[]).length,3);
 for(const choice of ['name','limits','trial'])await act({type:'chapel-spirit-talk',choice});
 assert.match(value('chapelSpiritPanel()'),/Introduce yourself and ask what she needs/);
 await act({type:'chapel-spirit-introduce'});await click({summoningCandidate:'merrin'});
 assert.match(element('#app').innerHTML,/Merrin/);assert.match(element('#app').innerHTML,/private/);
 await act({type:'cheat-recruit',characterId:'merrin'});await click({uiPerson:'merrin'});
 for(const tab of ['overview','talk','style','space','development']){
  await click({uiCharacterTab:tab});assert.doesNotMatch(element('#app').innerHTML,/undefined|NaN/);
 }
 for(const stage of [0,1,2,3]){
  if(stage===1)await act({type:'accept-outfit-invitation',characterId:'merrin',tier:'2',responseChoice:'warm'});
  if(stage===3)await act({type:'accept-outfit-invitation',characterId:'merrin',tier:'3',responseChoice:'warm'});
  await act({type:'share-personal-chapter',characterId:'merrin',sceneId:'merrin:'+stage,choice:'gentle'});
 }
 await act({type:'choose-outfit',characterId:'merrin',tier:'3'});await click({uiPerson:'merrin'});
 assert.match(value('companionOverviewPortrait("merrin")'),/overview\/merrin-outfit-3.webp/);
 assert.match(value('wardrobePage()'),/Plum evening dress/);
 assert.match(value('wardrobePage()'),/Plum halter and wrap skirt/);
 await click({view:'candidateReview'});assert.match(element('#app').innerHTML,/Cheats · custom character authoring/);
 await click({helpTopic:'named-recruitment'});assert.match(element('#app').innerHTML,/starts in the demonstration campaign/);
 await click({helpTopic:'optional-providers'});assert.match(element('#app').innerHTML,/Saving the text does not change a portrait/);
 console.log('PASS: v118 recruitment board, rank filter, all expedition art, API controls, portrait deduplication, chapel discovery and Merrin profile, and Help. Connected template checks, not rendered browser QA.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e.stack?.split('\n').slice(-8).join('\n')||e);process.exitCode=1;});
