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
 await click({view:'goals'});
 assert.match(element('#app').innerHTML,/Welcome/);
 await click({pinGoal:'welcome-fenna',pinEnabled:'yes'});
 await click({view:'castle'});
 assert.match(element('#app').innerHTML,/Your goals/);
 assert.match(element('#app').innerHTML,/data-goal-step="welcome-fenna:0"/);
 await click({goalStep:'welcome-fenna:0'});
 assert.equal(vm.runInContext('currentView',context),'research');
 let revision=vm.runInContext('state.revision',context);
 await click({previewAdvance:'yes'});
 assert.equal(element('#context-dialog').open,true);
 assert.match(element('#context-content').innerHTML,/unhurried phase/);
 assert.equal(vm.runInContext('state.revision',context),revision);
 element('#context-dialog').close();
 await click({personContext:'founder'});
 assert.match(element('#context-content').innerHTML,/Open character sheet/);
 assert.equal(vm.runInContext('currentView',context),'research');
 assert.equal(vm.runInContext('state.revision',context),revision);
 element('#context-dialog').close();
 await click({phaseTaskRun:'hearth-study'});
 for(let i=0;i<2;i++)await click({action:'advance'});
 await click({previewAdvance:'yes'});
 assert.match(element('#context-content').innerHTML,/Expected to finish/);
 assert.match(element('#context-content').innerHTML,/Hearth wards/);
 element('#context-dialog').close();
 await click({action:'advance'});
 assert.match(element('#advance-content').innerHTML,/Finished this phase/);
 assert.match(element('#advance-content').innerHTML,/All phase events &amp; routine production|All phase events & routine production/);
 await click({goalStep:'welcome-fenna:1'});
 assert.equal(vm.runInContext('currentView',context),'fullWorkshop');
 await click({readyRecipes:'yes'});
 assert.match(element('#app').innerHTML,/Showing ready recipes/);
 await click({materialContext:'binding-thread'});
 assert.match(element('#context-content').innerHTML,/protected/);
 assert.equal(vm.runInContext('currentView',context),'fullWorkshop');
 element('#context-dialog').close();
 await click({principleContext:'water-guidance'});
 assert.match(element('#context-content').innerHTML,/old waterworks/);
 element('#context-dialog').close();
 await click({phaseTaskRun:'first-lantern'});
 for(let i=0;i<2;i++)await click({action:'advance'});
 assert.match(element('#advance-content').innerHTML,/data-completion-task="install:lantern"/);
 await element('#advance-content').onclick({target:{closest(){return {dataset:{completionTask:'install:lantern'}};}}});
 assert.equal(vm.runInContext('state.lanternDisplayed',context),true);
 await click({artExpand:'library'});
 assert.match(element('#context-content').innerHTML,/expanded-artwork/);
 assert.match(element('#context-content').innerHTML,/library.webp/);
 vm.runInContext('window.scrollY=420',context);await click({view:'stores'});
 assert.equal(vm.runInContext("viewScroll.fullWorkshop",context),420);
 await click({view:'castle'});
 assert.equal(vm.runInContext("state.goalViews.find(g=>g.id==='welcome-fenna').pinned",context),true);
 await click({view:'phaseTasks'});
 let filterRevision=vm.runInContext('state.revision',context);
 await click({phaseFilter:'invitations'});
 assert.match(element('#app').innerHTML,/data-phase-filter="invitations" aria-pressed="true"/);
 assert.match(element('#app').innerHTML,/A light of your own/);
 assert.doesNotMatch(element('#app').innerHTML,/data-phase-task-run="restoration"/);
 assert.equal(vm.runInContext('state.revision',context),filterRevision);
 await click({phaseTaskOpen:'moment:first-light'});
 assert.match(element('#app').innerHTML,/data-solo-moment="first-light"/);
 await click({soloMoment:'first-light',momentChoice:'home'});
 assert.equal(vm.runInContext("state.soloLife.moments['first-light'].choiceId",context),'home');
 assert.match(element('#app').innerHTML,/Shared experiences/);
 await click({view:'phaseTasks'});
 assert.doesNotMatch(element('#app').innerHTML,/data-phase-task-open="moment:first-light"/);
 await click({phaseFilter:'all'});
 await click({action:'start-expedition'});
 await click({action:'advance'});
 await click({view:'phaseTasks'});
 await click({phaseFilter:'invitations'});
 assert.match(element('#app').innerHTML,/Decision needed/);
 console.log('PASS: pinned goals, linked steps, nonmutating preview, completion follow-up, person/material/principle context, recipe filtering, scroll memory and artwork expansion.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
