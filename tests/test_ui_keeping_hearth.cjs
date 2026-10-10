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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import GameStore\nsys.path.insert(0,'tests')\nimport test_keeping_hearth as t\nt.KeepingHearthTests.setUpClass();x=t.KeepingHearthTests();x.setUp();s=GameStore(sys.argv[1],start_type='fresh')\nx.s['soloLife']['characterSetup']={'profileSaved':True,'finished':True};x.s['soloLife']['arrival']['completed']=True\nwith s.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(x.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const act=a=>click({hearthAction:JSON.stringify(a)});
 await click({view:'castle'});assert.match(element('#app').innerHTML,/Keeping the Hearth/);
 for(const id of ['cinder-aqueduct','stormwatch-beacon','lantern-pavilion','flooded-monastery','frozen-skybridge','masquerade-manor']){
  await click({view:'expeditions'});await click({site:id});assert.ok(element('#app').innerHTML.includes('/assets/locations/'+id+'.webp'),id);
 }
 await click({view:'keepingHearth'});await act({type:'hearth-start'});
 assert.match(element('#app').innerHTML,/data-person-portrait="sabine"/);
 await act({type:'hearth-visibility',enabled:false});assert.equal(value('state.keepingHearthView.record.enabled'),false);
 await act({type:'hearth-visibility',enabled:true});
 let steps=0,sawCapture=false,sawJourneyArt=false;
 for(;steps<240;steps++){
  const v=value('state.keepingHearthView');if(v.stage==='complete')break;
  const e=value('state.expedition');
  if(e){
   await click({view:'expeditions'});assert.ok(element('#app').innerHTML.includes(value('state.originalAssets[state.expedition.siteId]')));sawJourneyArt=true;
   await act(e.stage==='awaiting-choice'?{type:'choose-expedition-approach',approach:'survey'}:e.stage==='ready-to-return'?{type:'return-expedition'}:{type:'advance'});
   await click({view:'keepingHearth'});continue;
  }
  if(v.stage==='intrusion')await act({type:'hearth-scare',choice:'confront'});
  else if(v.stage==='inspection')await act({type:'hearth-inspect',area:v.inspections.find(x=>!x.complete).id});
  else if(v.stage==='design')await act({type:'hearth-design',choice:'wards'});
  else if(v.stage==='return'){await act({type:'hearth-return',choice:'capture'});if(v.quietReady){sawCapture=true;assert.equal(value('state.containment.cases.sabine.status'),'arrival-pending');}else{assert.equal(value('state.containment.cases.sabine.status'),'unmet');assert.equal(value('state.keepingHearthView.carePlanned'),true);}}
  else if(v.stage==='tutorial')await act({type:'hearth-lesson',lessonId:v.lessons.find(x=>!x.complete&&x.ready).id});
  else if(v.stage==='closing')await act({type:'hearth-finish'});
  else {
   const n=v.next;assert.ok(n,JSON.stringify(v));assert.equal((n.blockers||[]).length,0,JSON.stringify(n));
   await act(n.id==='preservation'?{type:'start-expedition',siteId:'reedbank-waystation',carryLantern:!!value('state.craftedArtifacts["warming-lantern"]')}:n.action);
  }
 }
 assert.ok(steps<240);assert.ok(sawCapture);assert.ok(sawJourneyArt);assert.equal(value('state.testing.used'),false);
 await click({view:'castle'});
 assert.ok(element('#app').innerHTML.includes('data-ui-key="chapter-history"'));
 for(const view of ['houseShape','roomToGrow','keepingHearth'])assert.ok(element('#app').innerHTML.includes('data-view="'+view+'"'));
 assert.ok(!element('#app').innerHTML.includes('chapter-complete:'));
 await click({view:'keepingHearth'});
 assert.equal(value('state.containment.cases.sabine.status'),'released');assert.equal(value('state.characterCatalog.sabine'),undefined);
 await click({view:'containment'});assert.match(element('#app').innerHTML,/dungeon and recruitment tutorial/);
 for(const topic of ['intentions','home','visit'])await act({type:'summoning-talk',contactId:'encounter-sabine',topic});
 await act({type:'summoning-invite',contactId:'encounter-sabine',roomId:'lower-suite'});await act({type:'advance'});
 await act({type:'summoning-ask-stay',contactId:'encounter-sabine'});await act({type:'summoning-household-decision',contactId:'encounter-sabine',decision:'invite-to-stay'});
 await click({view:'keepingHearth'});assert.equal(value('state.keepingHearthView.resident'),true);assert.match(element('#app').innerHTML,/Dungeon specialty/);
 await act({type:'choose-living-scene',sceneId:'sabine:0',choice:'release'});
 while(value('state.sharedFunds')<28){await act(value('state.founderAssignment')==='commissions'?{type:'advance'}:{type:'assign-founder',assignment:'commissions'});}
 await act({type:'hq-job',jobId:'specialty-sabine'});for(let i=0;i<3;i++)await act({type:'advance'});
 await click({view:'specialists'});assert.match(element('#app').innerHTML,/release-key register/);
 assert.ok(value('state.characterQuestsView.quests.some(q=>q.id==="personal:sabine-keys")'));
 await vm.runInContext('readState().then(result=>{state=result;render();})',context);
 assert.equal(value('state.keepingHearthView.stage'),'complete');assert.equal(value('state.headquarters.stock["specialty:sabine"]'),1);
 await click({view:'storyJournal'});assert.ok(value('journalRecords().some(r=>r.id.startsWith("keeping-hearth:"))'));
 console.log('PASS: Chapter 4 capture, real construction and drill, expedition imagery before/during travel, care, release, tutorial, private-room recruitment, Sabine specialty, new quest, portraits and saved continuity.');
} finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
