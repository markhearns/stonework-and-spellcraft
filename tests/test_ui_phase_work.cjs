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
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'phaseTasks'});
 assert.match(element('#app').innerHTML,/Study the hearth wards/);
 await click({phaseTaskDismiss:'meet:maren'});assert.match(element('#app').innerHTML,/Show tasks put aside/);
 await click({phaseTaskRun:'hearth-study'});
 for(let i=0;i<3;i++)await click({action:'advance'});
 assert.match(element('#advance-content').innerHTML,/new tasks? available/);
 assert.match(element('#advance-content').innerHTML,/Make a warming lantern/);
 element('#open-phase-tasks').onclick();
 assert.equal(vm.runInContext('currentView',context),'phaseTasks');
 assert.match(element('#app').innerHTML,/NEW THIS PHASE/);
 await click({phaseTaskRun:'first-lantern'});
 for(let i=0;i<2;i++)await click({action:'advance'});
 assert.match(element('#advance-content').innerHTML,/Display your warming lantern/);
 await click({phaseTaskRun:'install:lantern'});
 assert.equal(vm.runInContext('state.lanternDisplayed',context),true);
 await vm.runInContext("commit({type:'cheat-toggle',enabled:true})",context);
 await vm.runInContext("commit({type:'cheat-character',ancestry:'Human',name:'Aster'})",context);
 await vm.runInContext("commit({type:'cheat-build',buildingId:'conservatory'})",context);
 const who=vm.runInContext("Object.keys(state.characterCatalog).find(k=>k!=='founder')",context);
 await click({view:'householdWork'});assert.match(element('#app').innerHTML,/Work agreements/);
 element('#role-'+who+'-garden').checked=true;
 await click({householdRole:'garden',person:who,enable:'yes'});
 await click({gardener:who});await click({action:'advance'});
 assert.equal(vm.runInContext("state.materialInventory['silver-ivy']",context),1);
 element('#role-'+who+'-fieldwork').checked=true;
 await click({householdRole:'fieldwork',person:who,enable:'yes'});
 await click({view:'expeditions'});assert.match(element('#app').innerHTML,/Choose your travelling party/);
 await events.change({target:{id:'journey-party-'+who,checked:true}});element('#carry-lantern').checked=false;
 await click({action:'start-expedition'});
 assert.match(element('#app').innerHTML.replace(/<[^>]*>/g,''),/PARTY · .*Aster/);
 assert.equal(vm.runInContext(`state.characterSheets['${who}'].atCastle`,context),false);
 await click({action:'advance'});await click({view:'phaseTasks'});
 assert.match(element('#app').innerHTML,/CHOICE WAITING/);
 await click({phaseTaskRun:'field-choice:survey'});
 for(let i=0;i<2;i++)await click({action:'advance'});
 await click({phaseTaskRun:'field-return'});await click({action:'advance'});
 assert.equal(vm.runInContext(`state.characterSheets['${who}'].atCastle`,context),true);
 assert.equal(vm.runInContext(`state.characterSheets['${who}'].knownPrinciples.includes('water-guidance')`,context),true);
 console.log('PASS: phase board quick actions, phase notifications, dismissal, work agreements, resident gardening and actual expedition companion return.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
