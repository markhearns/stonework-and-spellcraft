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
 const fixture="import sys,json,sqlite3\nfrom server import GameStore\nimport game,romance,armoury,headquarters\nsys.path.insert(0,'tests')\nfrom test_household_chapters import HouseholdChapterTests\nfrom test_magic_overhaul import MagicTests\nt=HouseholdChapterTests();t.s=MagicTests.rich(t)\nfor who in romance.content.SCENES:\n t.member(who);t.room(__import__('signature_equipment').ROOMS[who]);t.s['bedroomAssignments'][who]='bedchamber'\n romance.saved(t.s)['people'][who]={'level':4,'mode':'open','deferred':False}\nt.s['housingRooms']['west-chamber']['status']='complete';t.s['bedroomAssignments']['mira']='west-chamber'\ngame.set_character_assignment(t.s,'founder','rest');game.set_character_assignment(t.s,'mira','rest');armoury.sync(t.s)\nst=GameStore(sys.argv[1])\nwith st.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const action=a=>click({intimacyAction:JSON.stringify({characterId:'mira',...a})});
 for(const who of value('Object.keys(state.romanceView)')){
  await click({character:who,characterSection:'relationships'});
  const html=value(`intimacyPanel('${who}')`);assert.equal((html.match(/data-intimacy-stage=/g)||[]).length,4);assert.equal((html.match(/class="closeness-choice"/g)||[]).length,1);assert.doesNotMatch(html,/undefined|src="null"/);assert.match(html,/0\/4 milestones/);
  await click({intimacyStage:'2'});assert.equal(value(`intimacyStage.${who}`),2);assert.match(value(`intimacyPanel('${who}')`),/preceding closeness milestone/);
 }
 assert.equal(value('activityEntries().filter(r=>r.id.startsWith("closeness:")).length'),15);
 await click({character:'mira',characterSection:'relationships'});await click({intimacyStage:'0'});
 await action({type:'intimacy-begin',stage:0,sceneKind:'moment'});assert.match(element('#app').innerHTML,/Open closeness invitation/);assert.match(element('#app').innerHTML,/Choose quiet company instead/);
 await value('readState().then(s=>{state=s;render();})');assert.ok(value('state.romanceView.mira.closeness.pending'));
 await action({type:'intimacy-resolve',choice:'quiet'});assert.equal(value('state.romanceView.mira.closeness.stages[0].moment.count'),0);assert.match(element('#app').innerHTML,/Quiet company; milestone still available/);
 await action({type:'intimacy-begin',stage:0,sceneKind:'moment'});await action({type:'intimacy-resolve',choice:'leave'});assert.equal(value('state.romanceView.mira.closeness.pending'),null);
 for(let stage=0;stage<4;stage++){
  await click({intimacyStage:String(stage)});
  for(const kind of ['moment','milestone']){
   for(let n=0;n<8&&!value(`state.romanceView.mira.closeness.stages[${stage}].${kind}.available`);n++)await value("commit({type:'advance'})");
   assert.equal(value(`state.romanceView.mira.closeness.stages[${stage}].${kind}.available`),true,`${stage} ${kind}`);
   const phase=value('state.dayNumber+":"+state.currentDayPhase'),funds=value('state.sharedFunds');
   await action({type:'intimacy-begin',stage,sceneKind:kind});assert.match(element('#app').innerHTML,/class="closeness-room"/);
   await action({type:'intimacy-resolve',choice:'close'});assert.equal(value('state.dayNumber+":"+state.currentDayPhase'),phase);assert.equal(value('state.sharedFunds'),funds);
  }
 }
 assert.equal(value('activityEntries().filter(r=>r.id==="closeness:mira").length'),0);
 assert.equal(value('state.romanceView.mira.closeness.completed'),4);assert.equal(value('journalRecords().filter(r=>r.id.startsWith("close:mira:")).length'),8);
 await value("commit({type:'advance'})");await action({type:'intimacy-begin',stage:0,sceneKind:'moment'});await action({type:'intimacy-resolve',choice:'close'});
 assert.equal(value('state.romanceView.mira.closeness.stages[0].moment.count'),2);assert.equal(value('journalRecords().filter(r=>r.id.startsWith("close:mira:")).length'),8);
 await action({type:'intimacy-defer'});assert.match(element('#app').innerHTML,/Return these invitations/);await action({type:'intimacy-restore'});
 await value("commit({type:'pause-romance',characterId:'mira'})");assert.match(value("intimacyPanel('mira')"),/invitations are paused/);await value("commit({type:'reopen-romance',characterId:'mira'})");
 await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.romanceView.mira.closeness.completed'),4);
 console.log('PASS: all 15 compact scene panels, four-stage navigation, quiet/leave choices, pending reload, all eight Mira scenes through real Advance gates, private room art, repeat counts, unique journal memories, defer/restore and romantic pause/reopen.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
