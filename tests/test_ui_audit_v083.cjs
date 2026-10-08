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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/portrait-settings':\n  from portrait_generation import PortraitSettings\n  result=PortraitSettings(sys.argv[1]).public()\n elif url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/equipment/quote':\n  import armoury\n  result=armoury.quote_action(store.read(),payload.get('action'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 const value=e=>vm.runInContext(e,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const html=()=>element('#app').innerHTML;
 const initial=value('JSON.stringify(state)');
 const routes=[...new Set(value('navigationChoices().map(r=>r.target.view)').concat(['armoury','armsOfOurOwn','keepingHearth','room','hqRoom','workingTools']))];
 let screens=0;
 for(const view of routes){if(['characterSetup','arrival','settings','campaigns','cheats'].includes(view))continue;
  value('currentView='+JSON.stringify(view)+';roomContext=null;');const page=value('presentUI(pageContent())');
  assert.equal((page.match(/<h1[ >]/g)||[]).length,1,'One primary heading: '+view);
  assert.doesNotMatch(page,/src="(?:undefined|null)"|\bNaN\b/,'Valid composition: '+view);screens++;
 }
 for(const tab of value('Object.keys(UI_CHAR_TABS)')){value('currentView="characterProfile";selectedCharacterId="mira";uiCharacterTab='+JSON.stringify(tab));
  assert.equal((value('pageContent()').match(/<h1[ >]/g)||[]).length,1,'Character heading: '+tab);screens++;
 }
 const roomTarget=value('navigationChoices().find(r=>r.target.roomId==="training-yard").target');
 await click({uiTarget:JSON.stringify(roomTarget)});assert.equal(value('roomContext'),'training-yard');assert.equal(value('selectedHqRoom'),'training-yard');assert.match(value('unifiedBreadcrumb()'),/Training yard|Training Yard/);
 await click({view:'armoury'});assert.equal(value('unifiedSection()'),'studyHub');
 assert.ok(value('navigationChoices().some(r=>r.target.view==="armsOfOurOwn")'));
 assert.ok(value('directNavigation().includes("armsOfOurOwn")'));
 assert.notEqual(value('navigationIcon("magicHub","reference-book")'),value('navigationIcon("studyHub","makers-gauge")'));
 await click({uiTarget:JSON.stringify({view:'armoury',personId:'mira'})});assert.equal(value('gearOwner'),'mira');
 await click({view:'research'});await events.change({target:{id:'research-lead',value:'mira'}});
 assert.ok((html().match(/data-research-lead="mira"/g)||[]).length>0);
 assert.doesNotMatch(html(),/data-research-lead="founder"/);
 await click({uiPerson:'mira'});await click({uiCharacterTab:'development'});
 assert.doesNotMatch(html(),/class="ui-household-drawer"|class="recipe-tabs"|class="panel character-overview"/);
 await click({view:'development'});await events.change({target:{id:'ui-person-switch',value:'founder'}});assert.equal(value('uiCharacterTab'),'development');
 assert.equal(value('JSON.stringify(state)'),initial,'All auditing and navigation is read-only');
 // A real gear action creates pieces; all subsequent UI controls preserve state until review confirmation.
 await click({gearAction:JSON.stringify({type:'gear-review'})});
 await click({personalArmoury:'founder'});
 const item=value('Object.values(state.armouryView.items).find(i=>i.ownerId==="founder"&&i.definitionId==="field-boots").id');
 const staff=value('Object.values(state.armouryView.items).find(i=>i.ownerId==="founder"&&i.definitionId!=="field-boots").id');
 await click({gearItem:item});assert.ok(html().indexOf('id="gear-detail"')<html().indexOf('id="gear-inventory"'));
 assert.doesNotMatch(html(),/id="gear-hand"|id="gear-pattern"/);
 assert.match(html(),/id="gear-effect"/);
 await events.change({target:{id:'gear-operation',value:'refit',type:'select-one'}});
 assert.doesNotMatch(html(),/id="gear-effect"|id="gear-pattern"/);
 value('rememberUiDraft({id:"gear-name",type:"text",value:"A private draft"})');
 await events.change({target:{id:'gear-operation',value:'install-pattern',type:'select-one'}});assert.match(html(),/id="gear-pattern"/);assert.doesNotMatch(html(),/id="gear-effect"/);
 await click({gearItem:staff});assert.notEqual(value('uiDrafts.get(uiFieldKey({id:"gear-name"}))'),'A private draft');
 await click({gearItem:item});assert.equal(value('uiDrafts.get(uiFieldKey({id:"gear-name"}))'),'A private draft');
 const before=value('JSON.stringify(state)');element('#gear-loadout').value='expedition';
 await click({gearCommand:'wear-loadout'});assert.equal(value('gearQuote.action.mode'),'expedition');assert.equal(value('gearQuote.action.type'),'gear-apply-loadout');assert.equal(value('JSON.stringify(state)'),before);
 await click({gearCommand:'dismiss-quote'});
 element('#gear-search').value='zz-no-matching-piece';element('#gear-slot').value='boots';
 await events.submit({preventDefault(){},target:{id:'gear-filter-form'}});assert.match(html(),/No matching equipment/);
 await click({gearCommand:'clear-filters'});assert.equal(value('gearFilter'),'');assert.equal(value('gearSlot'),'');
 await click({toolOwner:'mira'});assert.equal(value('currentView'),'workingTools');assert.equal(value('equipmentOwner'),'mira');assert.match(html(),/Personal working tools/);
 console.log('PASS: '+screens+' routed screen compositions; one primary heading, chapter discovery, distinct icons, correct owner context, research lead selection, operation-specific fields, isolated item drafts, keyboard filtering and non-mutating loadout review. Headless only.');

}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
