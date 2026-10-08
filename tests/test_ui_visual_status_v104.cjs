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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_household_chapters import HouseholdChapterTests\nfrom server import GameStore\nt=HouseholdChapterTests();t.setUp();t.member('tamsin');t.s['housingRooms']['garden-chamber']['status']='complete';t.s['bedroomAssignments']['tamsin']='garden-chamber';st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=st.read()\nfor i in range(8):s['socialLife']['memories']['mira:fixture:'+str(i)]={'participants':['mira'],'title':'Shared fixture','sequence':i}\ns['relationships']['bonds']['founder|mira']={'participants':['founder','mira'],'trust':6,'affection':6,'respect':4}\nfor room in ('pool','sauna','hot-spring'):s['headquarters']['rooms'][room]='complete'\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g,armoury,spell_support\nst=GameStore(sys.argv[1]);s=st.read();g.apply_action(s,{'type':'gear-review'});armoury.make(s,'work-dress','founder');shield=armoury.make(s,'field-shield','founder');shield['enchantments']['warded-cover']={'id':'warded-cover','rank':1};spell_support.resolve(s,g.SPELL_FORMS['copy-lamp'],'founder',[]);spell_support.resolve(s,g.SPELL_FORMS['research-lens'],'mira',[]);s['craftedArtifacts']['warming-lantern']=1;s['provisions']['stock']=90;s['currentDayPhase']='evening';s['romance']['people']['mira']={'level':1,'mode':'open','deferred':False};s['roomFurnishings']['common-room']='velvet-settee';g.apply_action(s,{'type':'assign-founder','assignment':'commissions'})\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const before=value('JSON.stringify(state)'),day=value('state.dayNumber');
 let effects=value('temporaryEffectCards("founder")');
 assert.match(effects,/copy-lamp\.webp/);assert.match(effects,/3 matching work phases remaining/);
 assert.match(effects,/Adds 3 crowns per ordinary copying phase/);assert.doesNotMatch(effects,/Lens of comparison/);
 assert.match(value('temporaryEffectCards("mira")'),/research-lens\.webp/);
 await click({previewAdvance:'yes'});
 const preview=element('#context-content').innerHTML;
 assert.match(preview,/resource-forecast/);assert.match(preview,/provisions\.webp/);assert.match(preview,/resonance\.webp/);
 assert.equal(value('JSON.stringify(state)'),before,'opening forecasts and effect summaries is read-only');
 const rows=JSON.parse(value('JSON.stringify(state.advancePreview.resources)'));
 await value('commit({type:"advance"})');
 for(const r of rows){const actual=r.id==='crowns'?value('state.sharedFunds'):r.id==='provisions'?value('state.provisionsView.stock'):r.id==='resonance'?value('state.resonancePoints'):value('state.materialInventory['+JSON.stringify(r.id)+']');assert.equal(actual,r.after,r.id);}
 assert.equal(value('state.dayNumber'),day+1);
 assert.match(value('temporaryEffectCards("founder")'),/2 matching work phases remaining/);
 await value('commit({type:"assign-founder",assignment:"rest"})');await value('commit({type:"advance"})');
 assert.match(value('temporaryEffectCards("founder")'),/2 matching work phases remaining/,'rest must not spend a copying charge');
 // Pure rendering of a field effect uses field actions as its unit, and hides expired uses.
 value('globalThis.savedField={e:state.expedition,f:state.fieldMagic,p:state.partyJourneysView};state.expedition={siteId:"old-waterworks"};state.partyJourneysView={party:["founder"]};state.fieldMagic={aqueduct:{buffs:{founder:{haste:2,decoy:0}}}}');
 effects=value('temporaryEffectCards("founder")');assert.match(effects,/borrowed-hour\.webp/);assert.match(effects,/2 field uses remaining/);assert.doesNotMatch(effects,/Mirror decoy/);
 value('state.expedition=savedField.e;state.fieldMagic=savedField.f;state.partyJourneysView=savedField.p');
 await click({view:'armoury'});assert.match(element('#app').innerHTML,/empty-gear-slot/);
 const dress=value('Object.values(state.armouryView.items).find(i=>i.definitionId==="work-dress").id');
 const stateBeforeQuote=value('JSON.stringify(state)');
 await value('reviewGear({type:"gear-equip",itemId:'+JSON.stringify(dress)+'})');
 let html=element('#app').innerHTML;
 assert.match(html,/gear-change-columns/);assert.match(html,/Stowed/);assert.match(html,/Equipped/);assert.match(html,/equipment-work-dress\.webp/);
 assert.equal(value('JSON.stringify(state)'),stateBeforeQuote);
 const q=JSON.parse(value('JSON.stringify(gearQuote)'));
 await click({gearAction:JSON.stringify(q.action)});
 assert.equal(value('state.armouryView.loadouts.founder[state.armouryView.mode.founder].slots.shirt'),dress);
 assert.equal(value('state.armouryView.loadouts.founder[state.armouryView.mode.founder].slots.pants'),dress);
 await value('commit({type:"gear-apply-loadout",mode:"expedition"})');
 const shield=value('Object.values(state.armouryView.items).find(i=>i.definitionId==="field-shield").id');
 await value('reviewGear({type:"gear-equip",itemId:'+JSON.stringify(shield)+',hand:"hand2"})');
 assert.match(element('#app').innerHTML,/Patrol equipment bonuses/);
 assert.match(element('#app').innerHTML,/<td>\+0 → \+1<\/td>/);
 await click({gearAction:value('JSON.stringify(gearQuote.action)')});
 await value('reviewGear({type:"gear-activate",itemId:'+JSON.stringify(shield)+',enchantments:["warded-cover"]})');
 assert.match(element('#app').innerHTML,/Changes to active enchantments/);
 assert.match(element('#app').innerHTML,/Warded cover/);
 assert.match(element('#app').innerHTML,/<td>Inactive<\/td><td>Active · rank 1<\/td>/);
 assert.match(element('#app').innerHTML,/<td>\+1 → \+2<\/td>/);
 await click({gearAction:value('JSON.stringify(gearQuote.action)')});
 const forecast=value('forecastProject({name:"Archive repair",done:2,after:3,total:3,progress:1,completes:true})');
 assert.match(forecast,/Finishes on Advance/);assert.match(forecast,/value="2"/);assert.match(forecast,/value="3"/);
 for(const [kind,label] of [['ready','Ready'],['paused','Paused'],['choice','Decision needed'],['invitation','Invitation'],['working','Working']]){
  const badge=value('uiStatusBadge('+JSON.stringify(kind)+','+JSON.stringify(label)+')');assert.ok(badge.includes(label));assert.match(badge,/alt="" aria-hidden="true"/);
 }
 // A blocked or already-shared room conversation must not inflate the available count.
 value('globalThis.savedRoom={h:state.householdChaptersView,j:state.headquartersView.projects};state.householdChaptersView={people:[{activities:[{roomId:"library",available:true,memory:null},{roomId:"library",available:false,memory:null},{roomId:"library",available:true,memory:{}}]}]};state.headquartersView.projects=[{roomId:"library",kind:"hq-build",working:false,done:1,phases:3}]');
 const room=value('roomStatusMarkers("library")');assert.match(room,/Work paused · 1\/3/);assert.match(room,/1 conversation available/);assert.match(room,/invitation\.webp/);
 value('state.householdChaptersView=savedRoom.h;state.headquartersView.projects=savedRoom.j');
 await click({view:'headquarters'});assert.match(element('#app').innerHTML,/room-status-markers/);
 await click({view:'storyJournal'});html=element('#app').innerHTML;
 assert.match(html,/journal-thumbnail/);assert.match(html,/Crafted artifacts/);
 const artifacts=value('journalRecords().filter(r=>r.kind==="artifacts")');assert.ok(artifacts.some(r=>r.target.recipeId==='warming-lantern'));
 assert.equal(value('journalArtwork({target:{siteId:"unseen-place"}})'),'', 'no made-up art for unknown discoveries');
 const snapshot=value('JSON.stringify(state)');await value('readState().then(s=>{state=s;render();})');assert.equal(value('JSON.stringify(state)'),snapshot);
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 for(const id of ['ready','paused','choice','invitation'])assert.ok(fs.statSync('static/assets/status/'+id+'.webp').size>0);
 console.log('PASS: exact illustrated forecasts, matching-work charges, field-use counts, pictured equipment displacement and commit, status labels, truthful room markers, journal thumbnails, real artifact records and read-only/reload checks.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
