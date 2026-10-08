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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'castle'});assert.match(element('#app').innerHTML,/Browse quests, stories & memories/);
 await click({character:'mira'});await click({uiCharacterTab:'quests'});assert.match(element('#app').innerHTML,/Stories, quests & a little mischief/);
 assert.match(element('#app').innerHTML,/The scandal in the margins/);assert.doesNotMatch(element('#app').innerHTML,/an ink ribbon tied at her wrist/);
 const quest=async(type,extra={})=>click({questAction:type,questId:'personal:mira',...extra});
 const day=value('state.dayNumber');
 await quest('talk-character-quest',{questChoice:'flirt'});assert.equal(value('state.dayNumber'),day);
 let html=element('#app').innerHTML;assert.match(html,/charm the archivist/);assert.match(html,/Free ordinary route/);assert.match(html,/lucid-sight\.webp/);
 assert.match(html,/A participant must know and prepare/);
 await quest('choose-quest-method',{questMethod:'patient'});
 assert.equal(value('state.founderAssignment'),'character-quest');assert.equal(value('state.residentAssignment'),'character-quest');
 await value('commit({type:"advance"})');assert.equal(value('state.characterQuests.records["personal:mira"].pending.remaining'),2);
 await quest('pause-character-quest');assert.equal(value('state.founderAssignment'),'rest');
 await value('readState().then(s=>{state=s;render();})');assert.match(element('#app').innerHTML,/Resume this quest/);
 await quest('resume-character-quest');await value('commit({type:"advance"})');await value('commit({type:"advance"})');
 assert.match(element('#app').innerHTML,/credited only as a copyist/);
 await quest('talk-character-quest',{questChoice:'practical'});
 await quest('choose-quest-method',{questMethod:'patient'});
 for(let i=0;i<3;i++)await value('commit({type:"advance"})');
 assert.match(element('#app').innerHTML,/an ink ribbon tied at her wrist/);
 assert.doesNotMatch(element('#app').innerHTML,/make me blush without skipping/);
 await quest('talk-character-quest',{questChoice:'flirt'});
 assert.match(element('#app').innerHTML,/make me blush without skipping/);
 assert.equal(value('state.characterQuests.records["personal:mira"].status'),'complete');
 assert.equal(value('state.characterDevelopment.founder.advancementAwards["character-quest:personal:mira"].points'),2);
 await click({questAction:'generate-character-quests'});assert.equal(value('state.characterQuests.serial'),3);
 assert.match(element('#app').innerHTML,/Today’s request batch has already been generated/);
 const requests=value('JSON.stringify(state.characterQuests.records)');await value('readState().then(s=>{state=s;render();})');assert.equal(value('JSON.stringify(state.characterQuests.records)'),requests);
 assert.match(element('#app').innerHTML,/Household request board/);assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 console.log('PASS: quest discovery, authored story, spell icons and blockers, phase work, pause/resume, reload, hidden endings, flirt choice, exact reward, saved procedural board and daily limit.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
