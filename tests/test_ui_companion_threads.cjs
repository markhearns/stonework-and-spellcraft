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
  if (!elements.has(id)) elements.set(id, {innerHTML:'',textContent:'',focus(){this.focused=true;},scrollIntoView(){},classList:{add(){},remove(){}},addEventListener(type, callback){events[type]=callback;},showModal(){this.open=true;},close(){this.open=false;}});
  return elements.get(id);
}
let dropCreationResponse = false;
let dropThreadResponse = false;
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/portrait-settings':\n  from portrait_generation import PortraitSettings\n  result=PortraitSettings(sys.argv[1]).public()\n elif url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, structuredCloneForTest:value=>JSON.parse(JSON.stringify(value)), console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{getElementById(id){return element('#'+id);},querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{search:'?campaign=default',reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8',maxBuffer:32*1024*1024}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    if(dropThreadResponse && JSON.parse(body).action?.type==='thread-answer'){dropThreadResponse=false;throw new Error('Simulated lost conversation response');}
    return {ok:!json.error,async json(){return json;}};
  }
});




(async()=>{try {
 const fixture="import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_companion_almanac import CompanionAlmanacTests\nimport companion_threads_content as c\nfrom server import GameStore\nt=CompanionAlmanacTests();t.setUp()\nfor who in c.PERSONAL:t.familiar(who)\nst=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const row=id=>value('state.companionThreadsView.scenes.find(r=>r.id==='+JSON.stringify(id)+')');
 const open=async id=>click({uiTarget:JSON.stringify(value('threadTarget(state.companionThreadsView.scenes.find(r=>r.id==='+JSON.stringify(id)+'))'))});
 const actions=()=>[...element('#app').innerHTML.matchAll(/data-thread-action="([^"]+)"/g)].map(m=>JSON.parse(m[1].replaceAll('&quot;','"').replaceAll('&#39;',"'").replaceAll('&amp;','&')));
 const act=async(type,id,choice)=>{const a=actions().find(a=>a.type===type&&a.sceneId===id&&(choice===undefined||a.choice===choice));assert.ok(a,'Rendered action '+type+' '+id+' '+choice);await click({threadAction:JSON.stringify(a)});};
 const answer=async(id,choice='0')=>act('thread-answer',id,choice);
 const before=value('JSON.stringify([state.dayNumber,state.currentDayPhase,state.sharedFunds,state.materialInventory,state.founderAssignment,state.residentAssignment,state.romance])');
 assert.equal(value('state.schemaVersion'),76);assert.equal(value('APP_VERSION'),'0.119');
 assert.equal(value('state.companionThreadsView.scenes.length'),50);
 assert.ok(value('activityEntries().some(r=>r.id==="thread:personal:mira")'));
 await open('personal:mira');
 assert.match(element('#app').innerHTML,/Conversations to return to|EXCHANGE 1 OF 3/);
 assert.doesNotMatch(element('#app').innerHTML,/The husband comes back for the dog/);
 assert.equal(element('#thread-personal-mira').focused,true);
 dropThreadResponse=true;
 await answer('personal:mira','2');
 assert.ok(value('pendingRequest'));assert.equal(row('personal:mira').turn,0);
 await click({action:'retry'});
 assert.equal(row('personal:mira').turn,1);assert.equal(value('pendingRequest'),null);
 assert.match(element('#app').innerHTML,/literary fraud/);
 await act('thread-defer','personal:mira');
 assert.equal(row('personal:mira').deferred,true);
 await value('readState().then(s=>{state=s;render()})');
 assert.equal(row('personal:mira').turn,1);
 assert.ok(!value('activityEntries().some(r=>r.id==="thread:personal:mira")'));
 await act('thread-restore','personal:mira');await answer('personal:mira','3');
 assert.match(element('#app').innerHTML,/Your latest answer|rather not discuss/);
 await answer('personal:mira','1');
 assert.equal(row('personal:mira').completed,true);assert.equal(row('followup:mira').available,false);
 assert.ok(value('journalRecords().some(r=>r.id==="thread:personal:mira"&&r.memory.turns.length===3)'));
 const original=JSON.stringify(row('personal:mira').record);
 await click({uiCharacterTab:'about'});
 const pref=actions().find(a=>a.type==='thread-preference'&&a.personId==='mira'&&a.choice==='1');assert.ok(pref);await click({threadAction:JSON.stringify(pref)});
 assert.equal(JSON.stringify(row('personal:mira').record),original);
 assert.match(element('#app').innerHTML,/convincing ending/);
 assert.ok(value('journalRecords().some(r=>r.id==="preference:mira:0")'));
 for(const [index,who] of value('Object.keys(state.companionThreadsView.people)').entries()){
  if(who==='mira')continue;
  const id='personal:'+who;await open(id);
  await answer(id,String(index%3));await answer(id,String(index%4));await answer(id,String(index%3));
  assert.equal(row(id).completed,true);
  assert.doesNotMatch(element('#app').innerHTML,/undefined|src="null"/);
 }
 assert.equal(value('JSON.stringify([state.dayNumber,state.currentDayPhase,state.sharedFunds,state.materialInventory,state.founderAssignment,state.residentAssignment,state.romance])'),before);
 const peers=value('state.companionThreadsView.scenes.filter(r=>r.kind==="pair").map(r=>r.id)');
 for(const id of peers){await open(id);await answer(id,'2');await answer(id,'1');await answer(id,'1');assert.equal(row(id).completed,true);}
 await click({action:'advance'});
 await open('followup:mira');assert.match(element('#app').innerHTML,/divide the household goods/);assert.match(element('#app').innerHTML,/not quietly recorded a conversion/);
 for(const who of value('Object.keys(state.companionThreadsView.people)')){
  const id='followup:'+who;await open(id);await answer(id,'0');await answer(id,who==='mira'?'0':'1');
 }
 assert.match(value('threadPreferencePanel("mira")'),/A tradition you agreed to/);
 assert.doesNotMatch(value('threadPreferencePanel("tamsin")'),/A tradition you agreed to/);
 for(const id of peers){const next=id.replace('pair:','pair-followup:');await open(next);await answer(next,'2');await answer(next,'1');}
 await click({view:'storyJournal'});await click({uiJournalKind:'memories'});
 assert.equal(value('journalRecords().filter(r=>r.id.startsWith("thread:")&&r.memory).length'),50);
 assert.ok(!value('activityEntries().some(r=>r.id.startsWith("thread:"))'));
 await value('readState().then(s=>{state=s;render()})');
 assert.equal(value('state.companionThreadsView.scenes.filter(r=>r.completed).length'),50);
 await open('personal:mira');
 assert.match(element('#app').innerHTML,/Read all 3 saved exchanges/);
 assert.equal(actions().filter(a=>a.type==='thread-answer').length,0);
 const escaped=value('(()=>{let r=structuredCloneForTest(state.companionThreadsView.scenes[0]);r.record.turns[0].response="<script>bad()</script>";return threadScene(r,true)})()');
 assert.ok(escaped.includes('&lt;script&gt;bad()&lt;/script&gt;'));assert.ok(!escaped.includes('<script>bad()'));
 await click({view:'help'});value('helpTopic="continuing-conversations";helpQuery="";render()');
 assert.match(element('#app').innerHTML,/Every selected response is saved/);
 console.log('PASS: all 50 conversations through rendered controls, 125 saved exchanges, 16 profiles, preference correction, disagreement callback, deferred/reloaded turns, lost-response retry, journal, scope, exact effects, escaping and direct navigation. Headless integration; not pixel QA.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
