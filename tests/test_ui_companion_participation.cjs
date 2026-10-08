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
 const fixture="import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nimport test_magic_overhaul as unused";
 const setup="import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_magic_overhaul import MagicTests\nfrom server import GameStore\nimport game as g\ns=MagicTests().rich();s['miraArchiveProject']['status']='complete'\nfor who in ('founder','mira'):s['characterBuilds'][who]['attributes']={k:10 for k in g.character_builds.ATTRIBUTES}\ng.award_advancement(s,'mira','fixture',30,'Fixture')\nst=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))";
 execFileSync(process.env.PYTHON||'python',['-c',setup,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'expeditions'});assert.match(element('#app').innerHTML,/Compare the party/);assert.match(element('#app').innerHTML,/Stormwatch beacon/);
 await click({character:'mira'});await click({skillTrain:'diplomacy'});await click({action:'advance'});await click({action:'advance'});
 await click({character:'mira'});await click({uiCharacterTab:'talk'});assert.match(element('#app').innerHTML,/A new way to practise Diplomacy/);
 const event=value('state.companionParticipationView.events[0].id');
 await click({participationAction:'defer-participation',participationEvent:event});assert.match(element('#app').innerHTML,/Restore invitation/);
 await click({participationAction:'restore-participation',participationEvent:event});
 await click({participationAction:'share-participation',participationEvent:event,participationChoice:'notice'});
 assert.match(element('#app').innerHTML,/Remembered on day/);
 await value('commit({type:"start-expedition",siteId:"stormwatch-beacon",companionId:"mira"})');await click({action:'advance'});
 await value('commit({type:"choose-expedition-approach",approach:"survey"})');await click({view:'expeditions'});
 assert.match(element('#app').innerHTML,/A companion has an idea/);assert.match(element('#app').innerHTML,/<dt>Participants<\/dt>/);assert.deepEqual(Array.from(value('state.encounterView.choices["two-hands"].actingPeople')),['founder','mira']);
 assert.match(element('#app').innerHTML,/Cut back the branches/);
 await click({companionSuggestion:'0'});assert.equal(value('state.expedition.stage'),'working');await click({action:'advance'});
 for(let i=1;i<6;i++){await click({encounterMethod:'two-hands'});await click({action:'advance'});}
 assert.equal(value('state.expedition.stage'),'ready-to-return');
 await value('commit({type:"return-expedition"})');await click({action:'advance'});await click({character:'mira'});await click({uiCharacterTab:'talk'});
 assert.match(element('#app').innerHTML,/After the beacon/);
 await click({participationAction:'share-participation',participationEvent:'beacon:mira:complete',participationChoice:'thanks'});
 assert.ok(element('#app').innerHTML.includes(value('escapeHtml(state.companionParticipation.memories["beacon:mira:complete"].response)')));
 await value('readState().then(s=>{state=s;render();})');
 assert.equal(value('state.companionParticipation.memories["beacon:mira:complete"].choice'),'thanks');
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 console.log('PASS: party comparison, real training invitation, Later/restore, remembered dialogue, proactive suggestions, complementary roles, full beacon return, debrief and persistence.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
