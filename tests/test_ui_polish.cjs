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
 value('window.scrollTo=({top})=>{window.scrollY=top}');
 await click({view:'castle'});assert.match(element('#app').innerHTML,/BEFORE YOU ADVANCE/);
 await click({uiPerson:'mira'});await click({uiCharacterTab:'style'});value('window.scrollY=870');
 await click({uiCharacterTab:'talk'});assert.equal(value('window.scrollY'),0,'A new tab starts at its heading');
 value('window.scrollY=125');await click({uiCharacterTab:'style'});assert.equal(value('window.scrollY'),870,'Returning restores this tab, not another tab');
 await click({uiPerson:'tamsin'});assert.equal(value('window.scrollY'),0,'A different companion gets a separate position');
 const invitation=value('activityEntries().find(r=>r.id.startsWith("social:"))');assert.ok(invitation);
 value('socialCategory="deferred"');await click({uiTarget:JSON.stringify(invitation.target)});
 assert.equal(value('socialCategory'),'all');assert.equal(value('socialFocus'),invitation.target.sceneId);
 assert.ok(element('#app').innerHTML.includes('id="social-'+invitation.target.sceneId.replaceAll(':','-')+'"'));
 value('rememberUiDraft({id:"spell-target-example",value:"mira",type:"select-one"})');
 assert.equal(value('uiDrafts.get(uiRenderedContext+"::recipient::spell-target-example")'),'mira');
 await click({site:'flooded-monastery'});await click({action:'start-expedition'});
 let html=element('#app').innerHTML;
 assert.ok(html.indexOf('The estate path follows')<html.indexOf('Party condition & field magic'));
 await click({action:'advance'});assert.match(element('#advance-content').innerHTML,/What changed/);
 await click({approach:'survey'});html=element('#app').innerHTML;
 assert.ok(html.indexOf('data-encounter-method="patient"')<html.indexOf('Party condition & field magic'));
 const revision=value('state.revision');await click({view:'castle'});assert.match(element('#app').innerHTML,/A choice is waiting/);assert.equal(value('state.revision'),revision);
 await click({view:'expeditions'});await click({encounterMethod:'patient'});
 assert.ok(value('state.expedition.remainingWorkPhases')>0);await click({action:'advance'});
 assert.match(element('#advance-content').innerHTML,/What changed/);
 console.log('PASS: companion-specific scroll restoration, invitation target/filter recovery, recipient retention, visible phase feedback, decision-first expedition layout and ordinary fieldwork. Headless controller checks.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
