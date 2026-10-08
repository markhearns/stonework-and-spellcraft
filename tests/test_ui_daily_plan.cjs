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
 const fixture="import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=g.new_campaign();s['currentDayPhase']='evening';g.apply_action(s,{'type':'start-research'})\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(r=>setImmediate(r));
 const value=e=>vm.runInContext(e,context),act=a=>value(`commit(${JSON.stringify(a)})`);
 let html=value('unifiedHome()');assert.match(html,/Rest tonight/);assert.equal((html.match(/data-ui-key="evening-rest"/g)||[]).length,1);
 const original=value('JSON.stringify(state)');value('state.companionAlmanacView.people.mira.ambient=null');
 html=value("companionPresencePanel('mira')");assert.match(html,/Location/);assert.match(html,/Activity/);assert.doesNotMatch(html,/Away from the castle/);
 value('state.characterSheets.mira.atCastle=false');assert.match(value("companionPresencePanel('mira')"),/Away from the castle/);value('state='+original);
 const target=value('state.sharedFunds')+6;const paid=value('JSON.stringify(state.researchProjects)');
 await act({type:'plan-income',targetCrowns:target,purpose:'the next room'});assert.match(value('dailyPlanPanel()'),/Earning for the next room/);assert.match(value('dailyPlanPanel()'),/Pause earning/);
 await act({type:'evening-rest',choice:'tea',participants:['founder','mira']});assert.equal(value('state.currentDayPhase'),'evening');
 await act({type:'advance'});assert.equal(value('state.currentDayPhase'),'morning');
 assert.equal(value('JSON.stringify(state.researchProjects)'),paid);assert.match(value('dailyPlanPanel()'),/A rested morning/);assert.match(value('dailyPlanPanel()'),/data-resume-project="hearth"/);assert.match(value('dailyPlanPanel()'),/Resume earning/);
 const phaseBefore=value('state.researchCompletedPhases'),fundsBefore=value('state.sharedFunds');
 await act({type:'resume-project',projectId:'hearth'});assert.equal(value('state.sharedFunds'),fundsBefore);
 await act({type:'advance'});assert.ok(value('state.researchCompletedPhases')>phaseBefore);
 await act({type:'plan-income',targetCrowns:target,purpose:'the next room'});
 for(let i=0;i<4&&value('state.dailyPlanView.status')!=='complete';i++)await act({type:'advance'});
 assert.equal(value('state.dailyPlanView.status'),'complete');assert.equal(value('state.founderAssignment'),'rest');
 await act({type:'clear-income-plan'});assert.equal(value('state.dailyPlanView'),null);
 const mixed=value("balancedActivityRows([{kind:'decisions',id:'d'},...Array.from({length:6},(_,i)=>({kind:'work',id:'w'+i})),{kind:'invitations',id:'i'}]).map(r=>r.id)");
 assert.deepEqual(Array.from(mixed.slice(0,4)),['d','w0','i','w1']);assert.equal(new Set(mixed).size,8);
 const beforeNotice=value('JSON.stringify(state)');value("state.lastExpeditionReport={siteId:'old-waterworks',returnedDay:state.dayNumber}");
 assert.match(value('returnHomeNotice()'),/Open return report/);value('state.dayNumber+=2');assert.equal(value('returnHomeNotice()'),'');value('state='+beforeNotice);
 assert.equal(value('state.testing.used'),false);
 console.log('PASS: Home evening rest, exact party selection, morning funded-project resume, bounded earning, actual companion presence, balanced activity overview; normal actions and no cheats.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
