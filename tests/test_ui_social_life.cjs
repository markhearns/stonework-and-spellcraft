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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_household_chapters import HouseholdChapterTests\nfrom server import GameStore\nt=HouseholdChapterTests();t.setUp();t.member('tamsin');t.s['housingRooms']['garden-chamber']['status']='complete';t.s['bedroomAssignments']['tamsin']='garden-chamber';st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'castle'});assert.match(element('#app').innerHTML,/What’s happening/);
 await click({socialOpen:'personal:mira:0'});
 let html=element('#app').innerHTML;
 assert.match(html,/The correction in red/);assert.match(html,/Ask what bothered her/);
 assert.doesNotMatch(html,/Mira brings a small index headed/);
 const day=value('state.dayNumber'),funds=value('state.sharedFunds'),assignment=value('state.founderAssignment');
 await click({socialAction:'share-social-conversation',socialScene:'personal:mira:0',socialChoice:'candid'});
 html=element('#app').innerHTML;assert.match(html,/Your response/);assert.match(html,/Accuracy did not give me ownership/);
 assert.equal(value('state.dayNumber'),day);assert.equal(value('state.sharedFunds'),funds);assert.equal(value('state.founderAssignment'),assignment);
 assert.equal(value('state.socialLifeView.scenes.find(r=>r.id==="personal:mira:1").available'),false);
 await value('commit({type:"advance"})');
 await click({socialOpen:'personal:mira:1'});assert.match(element('#app').innerHTML,/What you said last time/);
 await click({socialAction:'share-social-conversation',socialScene:'personal:mira:1',socialChoice:'warm'});
 await value('commit({type:"advance"})');await click({socialOpen:'personal:mira:2'});
 assert.match(element('#app').innerHTML,/requires two unconvincing actors/);
 await click({socialOpen:'everyday:mira'});await click({socialAction:'defer-social-conversation',socialScene:'everyday:mira'});
 await click({socialCategory:'deferred'});assert.match(element('#app').innerHTML,/Return this invitation/);
 await click({socialAction:'restore-social-conversation',socialScene:'everyday:mira'});
 await click({socialOpen:'pair:mira-tamsin:0'});assert.match(element('#app').innerHTML,/The recipe in the margin/);
 await click({socialAction:'share-social-conversation',socialScene:'pair:mira-tamsin:0',socialChoice:'curious'});
 await value('readState().then(s=>{state=s;render();})');
 assert.equal(value('state.socialLife.memories["pair:mira-tamsin:0"].choice'),'curious');
 assert.match(element('#app').innerHTML,/Your response/);
 await click({socialCategory:'remembered'});html=element('#app').innerHTML;
 assert.match(html,/The correction in red/);assert.match(html,/The recipe in the margin/);assert.doesNotMatch(html,/src="undefined"/);
 console.log('PASS: home invitations, authored responses remain visible, phase-gated callbacks, branches, later/restore, peer conversations, rereading, reload and no resource or assignment changes.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
