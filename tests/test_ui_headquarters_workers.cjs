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
 const fixture="import json,sqlite3,sys\nfrom server import GameStore\nsys.path.insert(0,'tests')\nfrom test_headquarters_workers import HeadquartersWorkerTests\nt=HeadquartersWorkerTests();t.setUp()\ns=GameStore(sys.argv[1])\nwith sqlite3.connect(s.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory],{encoding:'utf8'});
 await value('readState().then(s=>{state=s;render();})');
 await click({view:'headquarters'});
 assert.match(element('#app').innerHTML,/Arrange headquarters work/);
 const revision=value('state.revision');
 await events.change({target:{id:'hq-worker',value:'brakka'}});
 assert.equal(value('state.revision'),revision);
 assert.match(element('#app').innerHTML,/Agree headquarters work/);
 await click({hqAction:'hq-agree-work',workerId:'brakka',enabled:'true'});
 await click({hqRoom:'smithy'});
 assert.match(element('#app').innerHTML,/Worker: <strong>/);
 assert.match(element('#app').innerHTML,/worker-id="brakka"/);
 await click({hqAction:'hq-job',workerId:'brakka',jobId:'blade'});
 assert.equal(value('state.additionalResidents.brakka.assignment'),'headquarters');
 await events.change({target:{id:'hq-worker',value:'founder'}});
 await click({hqRoom:'chapel'});await click({hqAction:'hq-build',workerId:'founder',roomId:'chapel'});
 assert.equal(value('state.headquartersView.projects.length'),2);
 assert.match(element('#app').innerHTML,/Brakka/);
 assert.match(element('#app').innerHTML,/Committed: 16 crowns/);
 await click({action:'advance'});
 assert.equal(value('state.headquarters.workerProjects.brakka.done'),1);
 await click({hqAction:'hq-pause',workerId:'brakka'});
 await click({view:'progression'});assert.match(element('#app').innerHTML,/headquarters:brakka/);
 await click({hqAction:'hq-resume',workerId:'brakka'});
 await click({action:'advance'});
 assert.equal(value('state.headquarters.rooms.chapel'),'complete');
 await value('readState().then(s=>{state=s;render();})');
 assert.equal(value('state.headquarters.workerProjects.brakka.done'),2);
 await click({action:'advance'});assert.equal(value('state.headquarters.stock.blade'),1);
 assert.equal(value('state.headquartersView.projects.length'),0);
 await click({hqRoom:'smithy'});await events.change({target:{id:'hq-worker',value:'brakka'}});
 await click({hqAction:'hq-job',workerId:'brakka',jobId:'metalware'});
 const paid=value('state.sharedFunds');await click({hqAction:'hq-cancel',workerId:'brakka'});
 assert.equal(value('state.sharedFunds'),paid+8);
 assert.match(value('startScreen()'),/stonework-and-spellcraft-logo-v074.webp/);
 console.log('PASS: worker agreement, selected-worker funding, concurrent projects, pause/resume, completion, reload, refunds and title logo.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
