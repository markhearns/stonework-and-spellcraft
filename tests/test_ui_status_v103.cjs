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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_household_chapters import HouseholdChapterTests\nfrom server import GameStore\nt=HouseholdChapterTests();t.setUp();t.member('tamsin');t.s['housingRooms']['garden-chamber']['status']='complete';t.s['bedroomAssignments']['tamsin']='garden-chamber';st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=st.read()\nfor i in range(8):s['socialLife']['memories']['mira:fixture:'+str(i)]={'participants':['mira'],'title':'Shared fixture','sequence':i}\ns['relationships']['bonds']['founder|mira']={'participants':['founder','mira'],'trust':6,'affection':6,'respect':4}\nfor room in ('pool','sauna','hot-spring'):s['headquarters']['rooms'][room]='complete'\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const initial=value('JSON.stringify(state)'),day=value('state.dayNumber'),phase=value('state.currentDayPhase');
 const summary=value('relationshipSummary("mira")');
 for(const name of ['Trust','Affection','Respect'])assert.match(summary,new RegExp('aria-label="'+name+'" aria-valuetext="[0-9]+ out of 12"'));
 assert.match(summary,/Romance:<\/strong> Not romantically involved/);
 assert.match(summary,/An invitation is ready/);
 assert.match(summary,/Affection can be platonic/);
 assert.equal((summary.match(/<meter /g)||[]).length,3);
 assert.equal(value('relationshipSummary("founder")'),'');
 assert.equal(value('relationshipSummary("missing-character")'),'');
 assert.equal(value('JSON.stringify(state)'),initial,'status rendering must not mutate state');
 // Scores and the latest change must belong to this exact pair, not another pair in the same event.
 value(`globalThis.originalRelationships=state.relationshipsView;state.relationshipsView={...originalRelationships,bonds:[
 {participants:['founder','mira'],trust:0,affection:12,respect:5},
 {participants:['mira','tamsin'],trust:12,affection:1,respect:1}],events:[
 {title:'Kept the archive promise',dayNumber:4,effects:[{bondId:'founder|mira',dimension:'respect',change:1}]},
 {title:'Mira and Tamsin finished work',dayNumber:5,effects:[{bondId:'mira|tamsin',dimension:'trust',change:1}]}]}`);
 const paired=value('relationshipSummary("mira")');
 assert.match(paired,/aria-label="Trust" aria-valuetext="0 out of 12"/);
 assert.match(paired,/aria-label="Affection" aria-valuetext="12 out of 12"/);
 assert.match(paired,/Kept the archive promise · day 4 · Respect \+1/);
 assert.doesNotMatch(paired,/Mira and Tamsin finished work/);
 assert.match(paired,/Not romantically involved/);
 value('state.relationshipsView=originalRelationships');
 // Overview and Relationships share one summary each, with direct navigation and no time cost.
 await click({character:'mira'});await click({uiCharacterTab:'overview'});
 assert.equal((element('#app').innerHTML.match(/data-ui-key="relationship-summary:mira"/g)||[]).length,1);
 assert.match(element('#app').innerHTML,/data-ui-character-tab="relationships"/);
 assert.match(element('#app').innerHTML,/aria-label="Field health"/);
 await click({uiCharacterTab:'relationships'});
 assert.equal((element('#app').innerHTML.match(/data-ui-key="relationship-summary:mira"/g)||[]).length,1);
 assert.equal(value('state.dayNumber'),day);assert.equal(value('state.currentDayPhase'),phase);
 await click({romanceAction:'defer-romance',romanceWho:'mira'});
 assert.equal((element('#app').innerHTML.match(/data-romance-action="restore-romance"/g)||[]).length,1);
 assert.match(element('#app').innerHTML,/You put this invitation aside/);
 await click({romanceAction:'restore-romance',romanceWho:'mira'});
 await click({view:'castle'});
 const home=element('#app').innerHTML;
 assert.equal((home.match(/data-ui-key="household-resources"/g)||[]).length,1);
 assert.equal((home.match(/data-ui-key="current-work"/g)||[]).length,1);
 assert.match(home,new RegExp(value('state.provisionsView.stock')+' provisions'));
 assert.match(home,new RegExp(value('state.provisionsView.daily')+' used each day'));
 for(const target of ['ledger','stores','resonance','progression','commissions','workArrangements','practicalProjects'])assert.ok(home.includes('data-view="'+target+'"'));
 assert.equal((value('dayPhaseIndicator()').match(/aria-current="step"/g)||[]).length,1);
 assert.equal((value('dayPhaseIndicator()').match(/<li /g)||[]).length,3);
 for(let i=0;i<3;i++)await value('commit({type:"advance"})');
 assert.equal(value('state.dayNumber'),day+1);assert.equal(value('state.currentDayPhase'),phase);
 const working=value('projectProgress({name:"Workshop repair",done:2,total:6,working:true})');
 assert.match(working,/<progress value="2" max="6" aria-label="Workshop repair progress"/);
 assert.match(working,/Working/);
 assert.match(value('projectProgress({name:"Workshop repair",done:2,total:6,working:false})'),/Paused or waiting/);
 for(const id of ['trust','affection','respect','morning','afternoon','evening','resonance']){
  assert.ok(fs.statSync('static/assets/status/'+id+'.webp').size>0);

 }
 assert.equal(value('statusIcon("unknown")'),'');
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"|id="gear-equipment sets"/);
 console.log('PASS: exact-pair scores/history, accessible numeric meters, explicit romance status, read-only summaries, single restore control, direct navigation, consolidated resources/work, full day cycle and seven icon assets.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
