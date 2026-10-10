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



execFileSync(process.env.PYTHON || 'python',['-c',`import sys,json,sqlite3
sys.path.insert(0,'tests')
from test_companion_goals import CompanionGoalTests
from server import GameStore
import companion_goals as cg,character_quests as q
fixture=CompanionGoalTests();fixture.setUp();s=fixture.s
for record in cg.definitions(s):
 if record['who']=='tamsin':continue
 record.update(status='complete',step=len(record['steps']),outcomes=[{'method':x['work'],'result':x['result']} for x in cg.GOALS[record['who']]['stages']])
 q.saved(s)['records'][record['id']]=record;cg.finish(s,record)
store=GameStore(sys.argv[1])
with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
`,directory],{encoding:'utf8'});
(async()=>{try {
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=a=>value('commit('+JSON.stringify(a)+')');
 assert.equal(value('APP_VERSION'),'0.119');assert.equal(value('state.schemaVersion'),76);
 for(const who of Object.keys(value('state.companionGoalsView.people'))){
  await click({uiPerson:who});
  for(const tab of ['overview','talk','quests']){
   await click({uiCharacterTab:tab});const html=element('#app').innerHTML;
   assert.match(html,new RegExp('data-companion-goal="'+who+'"'));assert.doesNotMatch(html,/undefined|NaN/);
   assert.ok(value('companionGoalPanel('+JSON.stringify(who)+')').includes(value('escapeHtml(state.companionGoalsView.people['+JSON.stringify(who)+'].goal)')));
  }
 }
 assert.match(value('goalRoomWorks("hot-spring")'),/elemental grotto/);
 assert.match(value('goalRoomWorks("smithy")'),/Emberline/);
 assert.match(value('goalKitPanel()'),/1 ready/);
 await click({foodAction:JSON.stringify({type:'goal-craft-kit'})});assert.equal(value('state.companionGoalsView.kits'),2);
 await click({uiPerson:'tamsin'});await click({uiCharacterTab:'quests'});
 const quest=async(type,extra={})=>click({questAction:type,questId:'ambition:tamsin',...extra});
 for(let step=0;step<4;step++){
  assert.equal(Object.keys(value('state.characterQuestsView.quests.find(q=>q.id==="ambition:tamsin").choices')).length,2);
  await quest('talk-character-quest',{questChoice:String(step%2)});
  const cost=value('state.characterQuestsView.quests.find(q=>q.id==="ambition:tamsin").methods.patient.crowns');
  assert.ok(element('#app').innerHTML.includes(cost+' crown'));
  await quest('choose-quest-method',{questMethod:'patient'});
  if(step===0){
   await quest('pause-character-quest');await value('readState().then(s=>{state=s;render();})');
   assert.match(element('#app').innerHTML,/Resume this quest/);await quest('resume-character-quest');
  }
  const n=value('state.characterQuests.records["ambition:tamsin"].pending.remaining');
  for(let i=0;i<n;i++)await act({type:'advance'});
 }
 await quest('talk-character-quest',{questChoice:'0'});
 assert.match(element('#app').innerHTML,/PERSONAL GOAL ACHIEVED/);assert.match(element('#app').innerHTML,/four-dish feast is served/);
 await click({foodAction:JSON.stringify({type:'goal-revisit',characterId:'tamsin',choice:'0'})});
 assert.match(element('#app').innerHTML,/served through a funnel/);
 await click({foodAction:JSON.stringify({type:'goal-meal',menu:'tamsin'})});
 assert.equal(value('state.companionGoalsView.meal'),'tamsin');assert.match(value('provisionsPanel()'),/Tamsin’s four-dish menu/);
 await click({helpTopic:'personal-goals'});assert.match(element('#app').innerHTML,/65 work stages/);assert.match(element('#app').innerHTML,/Merrin/);
 console.log('PASS: v119 all 16 profiles and quests, completed room works, field-kit restock, Tamsin full branching quest, pause/reload, success dialogue, menu controls and Help. Connected templates/controllers, not rendered layout QA.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e.stack?.split('\n').slice(-8).join('\n')||e);process.exitCode=1;});
