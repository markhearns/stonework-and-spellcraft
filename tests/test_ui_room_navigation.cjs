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
 // Preserve coverage for older fresh saves that have not opted into the chapter.
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import GameStore\ns=GameStore(sys.argv[1],start_type='fresh');state=s.read();state['soloLife'].pop('firstHearth',None)\nwith s.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'castle'});await click({openingReview:'yes'});assert.equal(value('currentView'),'research');assert.equal(value('roomContext'),'library');
 assert.match(element('#app').innerHTML,/Room activities/);assert.match(element('#app').innerHTML,/Begin research/);
 const revision=value('state.revision');await click({roomWork:'requests'});assert.equal(value('currentView'),'requests');assert.equal(value('state.revision'),revision);assert.match(element('#app').innerHTML,/Library &amp; archive/);
 await click({roomWork:'research'});await click({action:'start-research'});
 for(let i=0;i<3;i++)await click({action:'advance'});
 assert.equal(value('state.researchStatus'),'complete');assert.equal(value('roomContext'),'library');
 await click({view:'headquarters'});assert.equal(value('roomContext'),null);
 await click({hqRoom:'workshop'});await click({roomWork:'workshop'});
 assert.match(element('#app').innerHTML,/Begin the lantern/);assert.match(element('#app').innerHTML,/additional facilities and bonuses still require restoration/);
 await click({soloCraft:'yes'});await click({action:'advance'});await click({action:'advance'});
 await click({view:'castle'});assert.equal(value('state.openingGuide.next.id'),'facility:kitchen');
 assert.match(element('#app').innerHTML,/Restore Kitchen/);assert.match(element('#app').innerHTML,/Getting established/);
 await click({openingReview:'yes'});assert.equal(value('roomContext'),'kitchen');assert.equal(value('currentView'),'ledger');
 await click({view:'castle'});await click({openingAction:'yes'});assert.equal(value('state.activeFacilityId'),'kitchen');
 await click({action:'advance'});await click({action:'advance'});assert.equal(value('state.openingGuide.next.id'),'income');
 assert.match(element('#app').innerHTML,/crowns per assigned phase/);await click({openingAction:'yes'});assert.equal(value('state.founderAssignment'),'commissions');
 assert.match(element('#app').innerHTML,/Copying is assigned/);
 const money=value('state.sharedFunds');await click({action:'advance'});assert.equal(value('state.sharedFunds'),money+4);
 await click({view:'headquarters'});await click({hqRoom:'chapel'});await click({roomWork:'journal'});assert.equal(value('roomContext'),'chapel');
 await click({view:'settings'});assert.equal(value('roomContext'),null);
 console.log('PASS: persistent room workspaces, in-room research and crafting, funding guidance, explicit copying and navigation without save mutations.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
