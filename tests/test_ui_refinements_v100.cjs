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
 const fixture="import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom server import GameStore\nfrom test_refinements_v100 import RefinementTests\nt=RefinementTests();t.setUp();t.field_ready();t.member('zahra');t.spell('founder','water-jet');t.s['currentDayPhase']='evening'\nst=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(r=>setImmediate(r));
 const value=e=>vm.runInContext(e,context),act=a=>value(`provisionsClick({foodAction:${JSON.stringify(JSON.stringify(a))}})`);
 let html=value('commissionsPage()');assert.match(html,/Translate a damaged travel journal/);assert.match(html,/one advancement point|1 advancement point/);assert.match(html,/Restore the Workshop/i);
 await act({type:'commission-start',commissionId:'translate',workerId:'founder',payment:'crowns'});
 assert.match(value('commissionsPage()'),/0\/2 phases/);
 value("currentView='workArrangements';render()");
 await events.submit({preventDefault(){},target:{id:'routine-form',fields:{mode:'project',projectId:'commission',restEvenings:'on',assignment:'forage',target:'600'}}});
 assert.equal(value('state.routineView.rows[0].status'),'active');assert.match(value('advancePreviewPanel()'),/rests tonight/);
 await act({type:'advance'});assert.equal(value('state.commissionView.job.done'),0);
 await act({type:'advance'});await act({type:'advance'});
 assert.equal(value('state.commissionView.job'),null);assert.equal(value('state.routineView.rows[0].status'),'complete');
 value("currentView='fieldPatrols';render()");assert.match(value('fieldPatrolPage()'),/Observe a ridge griffin/);
 await events.submit({preventDefault(){},target:{id:'field-patrol-form',fields:{route:'road',objective:'rescue','patroller-founder':'on','patroller-zahra':'on'}}});
 assert.equal(value('state.fieldPatrolView.active.objectiveId'),'rescue');await act({type:'advance'});
 assert.equal(value('state.fieldPatrolView.active.stage'),'site-decision');
 html=value('patrolActivePanel()');assert.match(html,/Fumes in the inspection passage/);assert.match(html,/Settle the hot dust with water/);
 const spell=value('state.fieldPatrolView.objectives.choices.find(r=>r.spellId).id');
 await act({type:'watch-site-method',methodId:spell});await act({type:'advance'});
 assert.equal(value('state.fieldPatrolView.objectives.siteWork.condition'),true);
 html=value('patrolActivePanel()');assert.match(html,/one phase/);
 await act({type:'watch-site-method',methodId:'zahra:site-work'});await act({type:'advance'});
 assert.equal(value('state.fieldPatrolView.active.stage'),'decision');assert.match(value('patrolActivePanel()'),/Objective work: 1\/2/);
 await act({type:'watch-method',methodId:'founder:objective'});await act({type:'advance'});
 await act({type:'watch-method',methodId:'founder:objective'});await act({type:'advance'});await act({type:'advance'});
 assert.equal(value('state.fieldPatrolView.active'),null);assert.match(value('sharedHistoryPage()'),/Bring a missing surveyor home/);
 const id=value('state.sharedHistoryView[0].id');await act({type:'history-share',eventId:id,choiceId:'plan'});
 assert.match(value('sharedHistoryPage()'),/on the proposed party list/);assert.match(value('patrolPartyForm()'),/Review the party/);
 await value("provisionsClick({historyParty:'yes'})");assert.deepEqual(Array.from(value('patrolDraft.party')),['founder','zahra']);assert.equal(value('state.fieldPatrolView.active'),null);
 for(const [view,fn,pattern] of [['practicalProjects','practicalProjectsPage()',/fitting gauges/],['mystery','mysteryPage()',/6 crowns, 1 binding thread/],['resonance','resonancePage()',/12 points/]]){value(`currentView=${JSON.stringify(view)};render()`);html=value(fn);assert.match(html,pattern);assert.doesNotMatch(html,/undefined|NaN/);}
 assert.match(value('practicalProjectsPage()'),/three work phases|3 assigned work phases/);
 assert.equal(value("HELP_TOPICS.some(t=>t.id==='refinements')"),true);
 assert.equal(value('state.testing.used'),false);
 console.log('PASS: new pages, exact explanations, commission and routine controllers, evening rest, objective departure form, spell condition, second-worker completion, preview, reward, remembered-party review and persisted API state. No rendered-browser claim.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
