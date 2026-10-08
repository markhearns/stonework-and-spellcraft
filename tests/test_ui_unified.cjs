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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_party_journeys import PartyJourneyTests\nimport test_magic_overhaul as magic\nfrom server import GameStore\nt=PartyJourneyTests();t.setUp();t.maxed();t.s['craftedArtifacts']['warming-lantern']=1;magic.MagicTests.learned(t,'borrowed-hour');magic.MagicTests.learned(t,'water-walk','mira');t.s['romance']['people']['mira']={'level':2,'mode':'open','deferred':False};st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const action=(type,data={})=>click({journeyAction:JSON.stringify({type,siteId:'flooded-monastery',...data})});
 const advance=()=>click({action:'advance'});
 const before=value('JSON.stringify(state)');
 await click({view:'castle'});assert.match(element('#app').innerHTML,/What’s happening/);
 assert.equal(value('UI_PRIMARY.length'),6);
 assert.equal(value('activityEntries().some(r=>r.id.startsWith("quest:"))'),true);
 for(const who of value('Object.keys(state.characterCatalog)')){
  await click({uiPerson:who});
  for(const tab of value('Object.keys(UI_CHAR_TABS)')){
   await click({uiCharacterTab:tab});
   assert.doesNotMatch(element('#app').innerHTML,/undefined|src="null"/,who+':'+tab);
   assert.match(element('#app').innerHTML,/ui-character-tabs/);
  }
 }
 await click({view:'storyJournal'});
 for(const kind of ['active','personal','shared','expeditions','memories','log','all']){await click({uiJournalKind:kind});assert.doesNotMatch(element('#app').innerHTML,/undefined/);}
 await events.input({target:{id:'ui-journal-search',value:'zz-no-result'}});assert.match(element('#app').innerHTML,/No records match/);
 await click({uiJournalReset:'yes'});
 await events.input({target:{id:'ui-nav-search',value:'Mira'}});assert.match(element('#app').innerHTML,/Character ·/);
 await click({uiTarget:JSON.stringify({view:'characterProfile',personId:'mira',characterTab:'quests'})});assert.equal(value('selectedCharacterId'),'mira');assert.equal(value('uiCharacterTab'),'quests');
 await click({view:'spells'});
 for(const situation of value('Object.keys(UI_MAGIC_SITUATIONS)')){
  await events.change({target:{id:'ui-magic-situation',value:situation}});
  for(const status of ['all','known','prepared','usable','missing']){await events.change({target:{id:'ui-magic-state',value:status}});assert.doesNotMatch(element('#app').innerHTML,/undefined|NaN/);}
 }
 await click({uiMagicReset:'yes'});
 assert.match(value('magicFacts({id:"test",formId:"threshold-fold",ownerId:"founder",status:"learned"})'),/Instant travel when eligible/);
 await click({view:'castle'});await click({uiFeed:'invitations'});await click({uiPage:'feed',uiOffset:'1'});
 assert.equal(value('JSON.stringify(state)'),before,'Browsing must never mutate campaign state');
 // Each remembered date must remain distinct in the combined journal.
 value('state.romanceView.mira.dates.forEach((r,i)=>r.memory={title:"Date "+i,participants:["founder","mira"],dayNumber:1,response:"Remembered"})');
 assert.equal(value('journalRecords().filter(r=>r.id.startsWith("romance:mira:date:")).length'),value('state.romanceView.mira.dates.length'));
 // Confirm the submission controller actually clears only the committed form's draft.
 await click({view:'stores'});
 value('uiDrafts.set(uiRenderedContext+"::reserve-silver-ivy::target","0");uiDrafts.set(uiRenderedContext+"::other-form::notes","keep me")');
 await events.submit({preventDefault(){},target:{id:'reserve-silver-ivy',fields:{target:'0'}}});
 assert.equal(value('uiDrafts.has(uiRenderedContext+"::reserve-silver-ivy::target")'),false);
 assert.equal(value('uiDrafts.get(uiRenderedContext+"::other-form::notes")'),'keep me');
 console.log('PASS: six destinations, all resident tabs, combined journal, date identities, search, magic filters, instant travel timing, activity pagination and read-only browsing. Headless integration only.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
