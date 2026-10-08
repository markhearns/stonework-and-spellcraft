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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=g.new_campaign()\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const share=stage=>click({socialAction:'share-personal-chapter',socialPerson:'mira',socialScene:'mira:'+stage,socialChoice:'gentle'});
 await click({view:'householdChapters'});let html=element('#app').innerHTML;
 assert.match(html,/Life together/);assert.match(html,/The stolen ship/);assert.match(html,/Share her relaxed wardrobe invitation/);
 assert.doesNotMatch(html,/src="undefined"/);
 const funds=value('state.sharedFunds'),day=value('state.dayNumber'),assignment=value('state.founderAssignment');
 await share(0);assert.equal(value('state.householdChaptersView.people[0].completed'),1);
 await click({view:'wardrobe'});element('#outfit-response-mira-2').value='playful';
 await click({outfitAction:'accept-outfit-invitation',outfitOwner:'mira',outfitTier:'2'});
 assert.equal(value('state.outfitProgression.mira.invitations["2"].choice'),'playful');
 assert.match(element('#app').innerHTML,/footnote into a chapter/);
 await click({chapterPerson:'mira'});await share(1);await share(2);
 await click({view:'wardrobe'});await click({outfitAction:'accept-outfit-invitation',outfitOwner:'mira',outfitTier:'3'});
 await click({chapterPerson:'mira'});await share(3);assert.match(element('#app').innerHTML,/4\/4 personal chapters/);
 await click({chapterPerson:'mira',chapterSection:'activities',chapterRoom:'common-room'});
 html=element('#app').innerHTML;assert.match(html,/Showing activities/);assert.match(html,/data-social-scene="mira:common-room"/);assert.doesNotMatch(html,/data-social-scene="mira:library"/);
 await click({socialAction:'share-room-activity',socialPerson:'mira',socialScene:'mira:common-room',socialChoice:'quiet'});
 const memories=value('state.outfitProgressionView.mira.memories');
 await click({socialAction:'share-room-activity',socialPerson:'mira',socialScene:'mira:common-room',socialChoice:'playful'});
 assert.equal(value('state.outfitProgressionView.mira.memories'),memories);assert.match(element('#app').innerHTML,/Last shared on day/);
 await events.change({target:{id:'chapter-person',value:'mira'}});assert.equal(value('chapterRoomFilter'),null);
 assert.equal(value('state.sharedFunds'),funds);assert.equal(value('state.dayNumber'),day);assert.equal(value('state.founderAssignment'),assignment);
 await click({view:'workArrangements'});
 await events.submit({preventDefault(){},target:{id:'work-arrangement-form',fields:{name:'Quiet <afternoon>'}}});
 assert.match(element('#app').innerHTML,/Quiet &lt;afternoon&gt;/);
 await value('commit({type:"assign-founder",assignment:"commissions"})');
 assert.match(element('#app').innerHTML,/commissions →/);
 await click({workArrangement:'apply-work-arrangement',workName:'Quiet <afternoon>'});assert.equal(value('state.founderAssignment'),assignment);
 await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.householdChaptersView.people[0].completed'),4);
 await click({workArrangement:'delete-work-arrangement',workName:'Quiet <afternoon>'});assert.equal(value('state.workArrangementsView.plans.length'),0);
 await value('commit({type:"start-research"})');await value('commit({type:"assign-founder",assignment:"commissions"})');await click({view:'progression'});
 assert.match(element('#app').innerHTML,/Resuming changes:/);assert.match(element('#app').innerHTML,/commissions → research/);
 console.log('PASS: connected four-chapter route, remembered wardrobe response, room filtering/revisits, no time/resource costs, saved work previews and restoration, escaping, reload, project assignment impacts.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
