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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=a=>value('commit('+JSON.stringify(a)+')');
 await click({view:'castleMap'});
 assert.equal(value('castleMapRooms().length'),53);
 assert.equal(value('new Set(castleMapRooms().map(r=>r.id)).size'),53);
 const expected=value('[...Object.keys(state.headquartersView.catalogue),...Object.keys(state.housingCatalog),...Object.keys(state.containmentView.chambers),"survey-rooms"].sort().join("|")');
 assert.equal(value('castleMapRooms().map(r=>r.id).sort().join("|")'),expected);
 const revision=value('state.revision'),stamp=value('state.dayNumber+":"+state.currentDayPhase');
 const seen=new Set();
 for(const [level] of value('CASTLE_MAP_LEVELS')){
  await click({castleMapLevel:level});
  const html=element('#app').innerHTML;
  assert.match(html,/Stairs and passages/);
  assert.doesNotMatch(html,/undefined|NaN/);
  for(const m of html.matchAll(/data-castle-map-room="([^"]+)"/g))seen.add(m[1]);
  for(const m of html.matchAll(/<button class="castle-map-room[^>]*>([\s\S]*?)<\/button>/g)){
   for(const img of m[1].matchAll(/src="([^"]+)"/g))assert.ok(fs.existsSync('static'+img[1].split('?')[0]),img[1]);
  }
 }
 assert.equal(seen.size,53);assert.equal(value('state.revision'),revision);assert.equal(value('state.dayNumber+":"+state.currentDayPhase'),stamp);
 await click({castleMapLevel:'lower'});
 const unknown=element('#app').innerHTML.match(/<button[^>]*data-castle-map-room="foundation-chamber"[^>]*>([\s\S]*?)<\/button>/)[1];
 assert.match(unknown,/\?\?\?/);assert.doesNotMatch(unknown,/Foundation|ritual|<img/);
 await click({castleMapRoom:'foundation-chamber'});assert.match(element('#unavailable-content').textContent,/not been identified/);assert.equal(value('state.revision'),revision);
 element('#unavailable-dialog').close();await click({castleMapLevel:'ground'});
 await act({type:'hq-build',roomId:'entry-hall'});await act({type:'advance'});await act({type:'assign-founder',assignment:'rest'});
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="entry-hall"))'),/Repair paused.*1\/2/);
 await act({type:'cheat-toggle',enabled:true});await act({type:'cheat-build',buildingId:'entry-hall'});
 await value('readState().then(s=>{state=s;render()})');
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="entry-hall"))'),/is-ready/);
 await click({castleMapRoom:'entry-hall'});assert.equal(value('currentView'),'hqRoom');assert.equal(value('selectedHqRoom'),'entry-hall');
 await click({view:'castleMap'});await click({castleMapRoom:'annex-suite-1'});assert.equal(value('currentView'),'housing');assert.equal(value('housingRegionFilter'),'annex');
 await click({view:'castleMap'});await click({castleMapRoom:'heat-1'});assert.equal(value('currentView'),'containment');
 const beforeHelp=value('state.revision');await click({helpTopic:'foundation-ritual'});
 assert.match(element('#app').innerHTML,/nine phases/);assert.match(element('#app').innerHTML,/Private evening/);assert.match(element('#app').innerHTML,/20%/);
 await click({helpTopic:'rooms'});assert.match(element('#app').innerHTML,/Stair buttons/);assert.match(element('#app').innerHTML,/question marks/);
 await click({helpTopic:'cheats'});assert.match(element('#app').innerHTML,/both circuit tests/);assert.equal(value('state.revision'),beforeHelp);
 const setup="import sys,json\nsys.path.insert(0,'tests')\nfrom test_foundation_chamber import FoundationChamberTests\nfrom server import GameStore\nt=FoundationChamberTests();t.setUp();t.act('foundation-start');t.step('connections');t.step('instructions');t.act('cheat-toggle',enabled=True)\nst=GameStore(sys.argv[1])\nwith st.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python3',['-c',setup,directory]);await value('readState().then(s=>{state=s;render()})');
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="foundation-chamber"))'),/Foundation ritual chamber/);
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="foundation-chamber"))'),/is-ruined/);
 await act({type:'cheat-build',buildingId:'foundation-chamber'});
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="foundation-chamber"))'),/is-ready/);
 assert.equal(value('state.foundationChamberView.ready'),false);assert.equal(value('state.foundationChamberView.blessing.active'),false);
 console.log('PASS: 53 map locations across five levels; stairs/passages without time or save changes; hidden special-room names and art; construction, pause, completion and reload; room destinations; Help; discovered foundation cheat preserves tests and ritual gates.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
