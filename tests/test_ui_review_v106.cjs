// v0.106 navigation and presentation regression, using isolated local saves.
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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/portrait-settings':\n  from portrait_generation import PortraitSettings\n  result=PortraitSettings(sys.argv[1]).public()\n elif url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n elif url.path=='/api/equipment/quote':\n  import armoury\n  result=armoury.quote_action(store.read(),payload.get('action'))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 assert.match(value('startScreen()'), /Solo development build · 0\.106/);
 const saved=value('JSON.stringify(state)');
 await click({view:'bestiary'});
 assert.match(value('unifiedBreadcrumb()'),/aria-current="page">Creatures and Peoples/);
 assert.equal((value('directNavigation()').match(/value="bestiary"/g)||[]).length,1,'one functional bestiary destination; individual entries remain in search');
 const listKey=value('uiContextKey()');
 value('window.scrollY=640');
 await click({bestiaryEntry:'grave-silk-spider'});
 assert.notEqual(value('uiContextKey()'),listKey);
 assert.match(value('unifiedBreadcrumb()'),/aria-current="page">Grave-silk spider/);
 assert.equal(value('viewScroll['+JSON.stringify(listKey)+']'),640);
 await click({bestiaryBack:'yes'});assert.equal(value('uiContextKey()'),listKey);
 value('navigateTarget({view:"bestiary",entryId:"drow"})');
 assert.match(value('unifiedBreadcrumb()'),/aria-current="page">Drow/);
 value('setView("bestiary")');assert.equal(value('bestiaryEntry'),null);
 value('uiSearch="moth";navigateTarget({view:"bestiary",entryId:"lantern-moth"})');assert.equal(value('uiSearch'),'');
 assert.equal(value('JSON.stringify(state)'),saved,'UI navigation does not change the save');
 assert.match(value('hqWorkforcePanel()'),/^<details/);
 value('selectedHqRoom="library";roomContext="library";setView("hqRoom")');
 const room=value('pageContent()');
 assert.equal((room.match(/<h[12][^>]*>Library &(?:amp;)? archive<\/h[12]>/g)||[]).length,1);
 assert.ok(room.indexOf('scene-background')<room.indexOf('Room activities'));
 const spells=value('spellsPage()');
 assert.ok(spells.indexOf('Choose a spell to learn')<spells.indexOf('Spell guidance & preparation rules'));
 assert.doesNotMatch(spells,/A finite casting plan/);
 const stores=value('storesPage()');assert.ok(stores.indexOf('Stores & plans')<stores.indexOf('Food and pantry'));
 assert.match(stores,/6 crowns to buy/);assert.doesNotMatch(stores,/to buy crowns/);
 assert.match(value('armouryPage()'),/Receive &amp; equip starting gear/);
 assert.doesNotMatch(value('armouryPage()'),/Review starting equipment/);
 const preview=value('presentUI(advancePreviewPanel())');
 assert.equal((preview.match(/data-person-portrait="founder"/g)||[]).length,1,'one portrait per person in preview');
 const party=value('presentUI(patrolPartyForm())');
 assert.equal((party.match(/data-person-portrait="founder"/g)||[]).length,1,'one portrait per party member');
 value('state.phaseTasks.newIds=[];state.phaseTasks.tasks=state.phaseTasks.tasks.filter(t=>!["choice","ready"].includes(t.group));');
 if(value('state.phaseTasks.tasks.length'))assert.match(value('phaseTaskBoard()'),/class="phase-routine" open/);
 for(const view of ['bestiary','bounties','fieldPatrols']){
  const art=value('activityImage('+JSON.stringify(view)+')');
  const src=art.match(/src="([^"]+)"/)[1];assert.ok(fs.existsSync('static'+src),src);
 }
 console.log('v0.106 checks passed: list/detail scroll keys, correct breadcrumbs, clear navigation search, room hierarchy, actionable spellbook, stores title, accurate gear label, one preview portrait and visible phase opportunities.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
