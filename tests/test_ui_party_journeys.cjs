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
 await click({view:'castle'});assert.match(element('#app').innerHTML,/Journeys with lasting stories/);
 await click({site:'flooded-monastery'});assert.match(element('#app').innerHTML,/Choose your travelling party/);
 element('#carry-lantern').checked=true;await events.change({target:{id:'carry-lantern',checked:true}});
 for(const who of ['mira','brakka','sabine'])await events.change({target:{id:'journey-party-'+who,checked:true}});
 assert.match(element('#app').innerHTML,/3\/3 companions selected/);assert.equal(value('journeyPartySelection.length'),3);assert.match(element('#app').innerHTML,/id="carry-lantern" checked/);
 await events.change({target:{id:'journey-party-iona',checked:true}});assert.equal(value('journeyPartySelection.length'),3);
 assert.match(element('#app').innerHTML,/Prepared spells:<\/strong> Borrowed hour/);
 await click({prepTarget:JSON.stringify({view:'spells',personId:'mira'})});assert.match(element('#app').innerHTML,/Back to preparation/);
 await click({prepReturn:'yes'});assert.equal(value('selectedExpeditionSiteId'),'flooded-monastery');assert.equal(value('journeyPartySelection.length'),3);
 await click({action:'start-expedition'});assert.equal(value('state.expedition.carriedLantern'),true);assert.deepEqual(Array.from(value('state.partyJourneysView.party')),['founder','mira','brakka','sabine']);
 await advance();await click({approach:'survey'});assert.match(element('#app').innerHTML,/A courtyard without a shore/);assert.match(element('#app').innerHTML,/Bind a permanent water-level boundary/);
 await action('share-party-journey',{sceneId:'arrival',choice:'listen'});assert.match(element('#app').innerHTML,/Remembered journey conversations/);
 const sp=value('state.partyJourneysView.supportSpells.find(s=>s.ownerId==="founder").id');
 await action('journey-support',{spellId:sp,targetId:'founder'});assert.match(element('#app').innerHTML,/Borrowed hour<\/strong> · 1 work phase/);await advance();
 await click({encounterMethod:'spell:water-walk'});await advance();assert.equal(value('state.partyJourneys["flooded-monastery"].outcomes[0].casterId'),'mira');
 await click({encounterMethod:'patient'});assert.equal(value('state.expedition.remainingWorkPhases'),2);await advance();
 await click({action:'return-expedition'});await advance();assert.equal(value('state.expedition'),null);assert.match(element('#app').innerHTML,/Supplies &amp; costs|Supplies & costs/);assert.match(element('#app').innerHTML,/Returned early/);assert.ok(value('state.lastExpeditionReport.logbook.outcomes.length')>0);
 await click({action:'start-expedition'});await advance();await click({approach:'survey'});assert.equal(value('state.expedition.remainingWorkPhases'),1);await advance();
 assert.match(element('#app').innerHTML,/A margin for something personal/);await action('share-party-journey',{sceneId:'private:mira',choice:'affection'});assert.match(element('#app').innerHTML,/share a kiss/);
 await action('share-party-journey',{sceneId:'camp',choice:'playful'});assert.match(element('#app').innerHTML,/dry socks/);
 await click({encounterMethod:'ritual'});await advance();await advance();assert.match(element('#app').innerHTML,/Permanent field inscriptions · 1/);
 for(let i=0;i<3;i++){await click({encounterMethod:'specialist'});await advance();}
 await click({encounterMethod:'refuge'});await advance();await click({action:'return-expedition'});await advance();
 assert.equal(value('state.partyJourneys["flooded-monastery"].discoveries.length'),1);assert.match(element('#app').innerHTML,/The rainkeeper’s atlas/);
 await action('place-journey-legacy',{installed:true});await action('share-party-journey',{sceneId:'home',choice:'join'});
 await click({room:'library'});assert.match(element('#app').innerHTML,/The rainkeeper’s atlas/);
 await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.schemaVersion'),65);assert.equal(value('state.partyJourneys["flooded-monastery"].installed'),true);
 assert.doesNotMatch(element('#app').innerHTML,/undefined|src="null"/);
 for(const site of ['frozen-skybridge','masquerade-manor']){await click({site});assert.match(element('#app').innerHTML,/six obstacles and a final commitment/);}
 console.log('PASS: roster of 14, selection cap, departure preparation, four travellers, actual spell caster, support cast phase, accelerated ordinary route, retreat/resume, romance-aware camp, permanent ritual, completed return, legacy installation, room display and reload.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
