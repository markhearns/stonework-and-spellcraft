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
 const fixture="import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=g.new_campaign('fresh');s['sharedFunds']=0\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(r=>setImmediate(r));
 const value=e=>vm.runInContext(e,context),act=a=>value(`commit(${JSON.stringify(a)})`);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 let html=value('firstHearthPanel()');
 assert.match(html,/Accept commission/);assert.match(html,/Copy records instead/);
 assert.match(html,/Materials used: none/);assert.doesNotMatch(html,/undefined|src="null"/);
 const primary=JSON.parse(value('JSON.stringify(state.firstHearthView.next.action)'));
 const crowns=value('state.sharedFunds'),phase=value('state.currentDayPhase');
 await click({firstHearthAction:JSON.stringify(primary)});
 assert.equal(value('state.founderAssignment'),'external-commission');assert.equal(value('state.sharedFunds'),crowns);assert.equal(value('state.currentDayPhase'),phase);
 await act({type:'advance'});await act({type:'assign-founder',assignment:'rest'});
 html=value('firstHearthPanel()');assert.match(html,/Resume funded work/);assert.match(html,/1 \/ 2 work complete/);
 await click({firstHearthAction:value('JSON.stringify(state.firstHearthView.next.action)')});
 await act({type:'advance'});assert.ok(value('state.sharedFunds')>crowns);
 await act({type:'advance'}); // Tomorrow's finite order and copying are both available.
 const alternative=value('state.firstHearthView.next.incomeOptions.find(x=>x.action.type==="plan-income")');
 assert.ok(alternative);await click({foodAction:JSON.stringify(alternative.action)});
 assert.equal(value('state.founderAssignment'),'commissions');
 for(let i=0;i<12&&value('state.dailyPlanView.status')!=='complete';i++)await act({type:'advance'});
 assert.equal(value('state.dailyPlanView.status'),'complete');assert.equal(value('state.founderAssignment'),'rest');
 // A separate saved fixture exposes the real site-decision controller.
 const late="import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=g.new_campaign('fresh');s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'};g.apply_action(s,{'type':'trial-start'});g.apply_action(s,{'type':'watch-depart','participants':['founder'],'objectiveId':'escort'});g.apply_action(s,{'type':'advance'})\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))";
 execFileSync(process.env.PYTHON||'python',['-c',late,directory]);await value('readState().then(s=>{state=s;render();})');
 html=value('nextPhaseStrip()');assert.match(html,/Choose a patrol site method/);assert.match(html,/Advance still moves time/);assert.doesNotMatch(html,/Your scholar is resting/);
 assert.equal(value("activityEntries().filter(r=>r.target.view==='fieldPatrols').length"),1);
 assert.match(value('trialPage()'),/Choose the party’s next action/);
 assert.doesNotMatch(value('trialPage()'),/undefined|src="null"/);
 console.log('PASS: commission and copying buttons, quoted payment, pause/resume, bounded income, one waiting-site card and truthful Advance feedback through persisted API state.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
