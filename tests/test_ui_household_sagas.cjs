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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_household_sagas import HouseholdSagaTests\nfrom server import GameStore\nt=HouseholdSagaTests();t.setUp();t.s['romance']['people']['mira']={'level':2,'mode':'open','deferred':False};st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const action=(type,data={})=>click({sagaAction:JSON.stringify({type,storyId:'margins',...data})});
 const submit=(id,fields)=>events.submit({preventDefault(){},target:{id,fields}});
 await click({view:'castle'});assert.match(element('#app').innerHTML,/Household stories & connections/);
 await click({view:'householdSagas'});assert.equal(value('state.householdSagasView.stories.length'),12);
 assert.match(element('#app').innerHTML,/Three versions of the truth/);assert.doesNotMatch(element('#app').innerHTML,/undefined|src="null"/);
 await action('share-household-saga',{choice:'method'});assert.match(element('#app').innerHTML,/Let one shared phase pass/);
 await value('commit({type:"advance"})');assert.match(element('#app').innerHTML,/Your earlier choice/);
 await action('share-household-saga',{choice:'company'});
 await submit('saga-project-form',{'worker-founder':'yes','worker-mira':'yes'});
 assert.equal(value('state.householdSagas.stories.margins.project.workers.length'),2);assert.equal(value('state.residentAssignment'),'household-story');
 await value('commit({type:"advance"})');assert.match(element('#app').innerHTML,/1\/2 phases/);
 await action('pause-household-project');await value('commit({type:"advance"})');assert.equal(value('state.householdSagas.stories.margins.project.done'),1);
 await action('resume-household-project');await value('commit({type:"advance"})');await action('share-household-saga',{choice:'company'});
 assert.equal(value('state.householdSagas.stories.margins.stage'),3);assert.match(element('#app').innerHTML,/All three scenes are remembered/);
 await click({sagaTab:'bonds'});assert.match(element('#app').innerHTML,/What brought them here/);assert.match(element('#app').innerHTML,/Neris/);assert.match(element('#app').innerHTML,/Respect/);
 await click({sagaTab:'codas'});assert.match(element('#app').innerHTML,/A little time after the gathering/);await action('share-saga-coda',{characterId:'mira',choice:'flirt'});assert.match(element('#app').innerHTML,/lingering kiss/);
 await value('commit({type:"start-expedition",siteId:"old-waterworks",companionId:"mira"})');await click({view:'expeditions'});
 assert.match(element('#app').innerHTML,/Company with a shared history/);const scene=value('state.householdSagasView.field[0].id');await action('share-saga-field',{sceneId:scene});assert.match(element('#app').innerHTML,/decision about the actual obstacle remains yours/);
 assert.equal(value('state.expedition.stage'),'outbound');
 await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.householdSagas.stories.margins.stage'),3);assert.equal(value('state.householdSagas.codas.mira.relationshipLevel'),2);
 console.log('PASS: all 12 stories listed, portraits, phase gating, recalled choice, real worker selection, paid project pause/resume, completion, NPC bonds, relationship-aware coda, actual-party field conversation and reload.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
