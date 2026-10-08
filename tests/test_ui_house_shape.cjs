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
 // The fixture is earned through the first chapter's ordinary actions, not cheats.
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import GameStore\nsys.path.insert(0,'tests')\nimport test_house_shape as t\nt.HouseShapeTests.setUpClass();x=t.HouseShapeTests();x.setUp();x.recruit();s=GameStore(sys.argv[1],start_type='fresh')\nx.s['soloLife']['characterSetup']={'profileSaved':True,'finished':True};x.s['soloLife']['arrival']['completed']=True\nwith s.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(x.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const act=a=>click({shapeAction:JSON.stringify(a)});
 await click({view:'castle'});assert.match(element('#app').innerHTML,/The House Takes Shape/);
 await click({view:'houseShape'});assert.match(element('#app').innerHTML,/A working archive/);assert.match(element('#app').innerHTML,/A dependable kitchen garden/);assert.match(element('#app').innerHTML,/A working commission bench/);
 assert.match(element('#app').innerHTML,/data-person-portrait="maren"/);
 await act({type:'shape-start',pathId:'cultivation'});
 await act({type:'shape-visibility',enabled:false});assert.equal(value('state.houseShapeView.enabled'),false);
 await act({type:'shape-visibility',enabled:true});
 let steps=0,sawPaused=false;
 for(;steps<180;steps++){
  const v=value('state.houseShapeView'),r=v.record,d=v.paths.find(p=>p.id===v.active);
  if(v.stage==='complete')break;
  const e=value('state.expedition');
  if(e){await act(e.stage==='awaiting-choice'?{type:'choose-expedition-approach',approach:'survey'}:e.stage==='ready-to-return'?{type:'return-expedition'}:{type:'advance'});continue;}
  if(v.stage==='proposal')await act({type:'shape-purpose',choice:'welcome'});
  else if(v.stage==='design'){
   assert.match(element('#app').innerHTML,/No bonus to sales/);
   await act({type:'shape-design',choice:'nursery'});
  }else if(v.stage==='planning'){
   if(!r.workers.includes('maren')){await act({type:'shape-include',characterId:'maren'});continue;}
   const missing=Object.entries(d.inputs).find(([key,n])=>value('state.materialInventory['+JSON.stringify(key)+']-state.materialReserveTargets['+JSON.stringify(key)+']')<n);
   const cost=missing?value('state.materialCatalog['+JSON.stringify(missing[0])+'].price'):d.cost;
   if(value('state.sharedFunds')<cost){await act(value('state.founderAssignment')==='commissions'?{type:'advance'}:{type:'assign-founder',assignment:'commissions'});continue;}
   if(missing){await act({type:'buy-material',materialId:missing[0]});continue;}
   if(value('state.founderAssignment')!=='rest'){await act({type:'assign-founder',assignment:'rest'});continue;}
   assert.equal(v.blockers.length,0,JSON.stringify(v.blockers));await act({type:'shape-fund'});
  }else if(v.stage==='construction'){
   if(!sawPaused){await act({type:'shape-pause'});assert.match(element('#app').innerHTML,/Work is paused/);await act({type:'shape-resume',characterId:'founder'});await act({type:'shape-resume',characterId:'maren'});sawPaused=true;}
   await act({type:'advance'});
  }else if(v.stage==='gathering')await act({type:'shape-gather',choice:'credit'});
  else if(v.stage==='ending')await act({type:'shape-finish'});
  else{
   const n=v.next;assert.ok(n);assert.equal((n.blockers||[]).length,0,JSON.stringify(n));
   if(n.id==='field')await act({type:'start-expedition',siteId:n.target.siteId,carryLantern:true});
   else {assert.ok(n.action);await act(n.action);}
  }
 }
 assert.ok(steps<180);assert.ok(sawPaused);assert.equal(value('state.testing.used'),false);
 assert.equal(value('state.houseShapeView.record.project.contributions.maren'),3);
 assert.match(element('#app').innerHTML,/What grows next/);
 await vm.runInContext('readState().then(result=>{state=result;render();})',context);
 assert.equal(value('state.houseShapeView.record.finished'),true);
 await click({view:'headquarters'});await click({hqRoom:'conservatory'});
 assert.match(element('#app').innerHTML,/Botanical propagation beds/);
 await click({view:'storyJournal'});assert.ok(value('journalRecords().some(r=>r.id.startsWith("house-shape:"))'));
 console.log('PASS: Chapter two connected UI, three plans, shared contributors, real funding, pause/resume, expedition, harvest, historical evidence, room outcome, notebook and reload.');
} finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
