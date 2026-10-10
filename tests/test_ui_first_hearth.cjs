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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const act=action=>click({firstHearthAction:JSON.stringify(action)});
 await events.submit({preventDefault(){},target:{id:'founder-profile-form',fields:{name:'Rowan',age:'32',pronouns:'they/them',background:'traveller',appearanceDescription:'A worn coat',backgroundNotes:''}}});
 await click({setupContinue:'yes'});await click({arrivalEnter:'skip'});
 assert.match(element('#app').innerHTML,/The First Hearth/);
 const rev=value('state.revision');
 await click({uiTarget:JSON.stringify(value('state.firstHearthView.next.target'))});
 assert.equal(value('currentView'),'research');assert.equal(value('state.revision'),rev);
 await click({view:'castle'});
 await act({type:'first-hearth-guidance',enabled:false});
 assert.match(element('#app').innerHTML,/Chapter guidance is put aside/);
 await act({type:'first-hearth-guidance',enabled:true});
 let sawPortrait=false,sawMemory=false,sawPaused=false,steps=0;
 for(;steps<140;steps++){
  const v=value('state.firstHearthView');
  if(v.complete)break;
  if(v.scene){
   const sc=v.scene;
   if(sc.id==='repair-notes'){assert.match(element('#app').innerHTML,/data-person-portrait="koharu"/);sawPortrait=true;}
   const choice=sc.id==='company'?'meet':sc.id==='conclusion'?'craft':sc.choices[0].id;
   const day=value('state.dayNumber'),phase=value('state.currentDayPhase');
   await act({type:'first-hearth-choice',sceneId:sc.id,choiceId:choice});
   assert.equal(value('state.dayNumber'),day);assert.equal(value('state.currentDayPhase'),phase);
   assert.ok(value('state.firstHearthView.memories').some(m=>m.id===sc.id));sawMemory=true;
  }else if(value('state.expedition')){
   const stage=value('state.expedition.stage');
   await act(stage==='awaiting-choice'?{type:'choose-expedition-approach',approach:'salvage'}:stage==='ready-to-return'?{type:'return-expedition'}:{type:'advance'});
  }else if(v.next.id==='fieldwork'){
   await click({uiTarget:JSON.stringify(v.next.target)});assert.equal(value('selectedExpeditionSiteId'),'quarry-shelter');
   await act({type:'start-expedition',siteId:'quarry-shelter',carryLantern:true});await click({view:'castle'});
  }else{
   assert.equal(v.nextBlockers.length,0,JSON.stringify(v.nextBlockers));
   if(v.next.id==='hearth'&&v.next.action.type==='advance'&&!sawPaused){
    await act({type:'assign-founder',assignment:'rest'});
    assert.match(element('#app').innerHTML,/Resume funded work/);
    const funds=value('state.sharedFunds');await act(value('state.firstHearthView.next.action'));
    assert.equal(value('state.sharedFunds'),funds);sawPaused=true;
   }else await act(v.next.action);
  }
 }
 assert.ok(steps<140);assert.ok(sawPortrait&&sawMemory&&sawPaused);
 assert.match(element('#app').innerHTML,/CHAPTER REMEMBERED/);
 assert.equal(value('state.testing.used'),false);
 await vm.runInContext('readState().then(result=>{state=result;render();})',context);
 assert.equal(value('state.firstHearthView.complete'),true);
 await click({view:'storyJournal'});
 assert.ok(value('journalRecords().some(r=>r.id==="first-hearth:repair-notes")'));
 await click({view:'castle'});await click({uiTarget:JSON.stringify(value('state.firstHearthView.next.target'))});
 assert.equal(value('currentView'),'castleChapter');
 console.log('PASS: First Hearth complete connected UI playthrough, portrait, explicit choices, real costs and phases, pause/resume, journal, guidance dismissal, reload and chosen next direction.');
} finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
