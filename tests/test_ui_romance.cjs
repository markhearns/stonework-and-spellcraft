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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g\nst=GameStore(sys.argv[1]);s=st.read()\nfor i in range(8):s['socialLife']['memories']['mira:fixture:'+str(i)]={'participants':['mira'],'title':'Shared fixture','sequence':i}\ns['relationships']['bonds']['founder|mira']={'participants':['founder','mira'],'trust':6,'affection':6,'respect':4}\nfor room in ('pool','sauna','hot-spring'):s['headquarters']['rooms'][room]='complete'\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({view:'castle'});assert.match(element('#app').innerHTML,/What’s happening/);
 await click({character:'mira'});await click({uiCharacterTab:'relationships'});assert.match(element('#app').innerHTML,/Between you/);
 assert.match(element('#app').innerHTML,/A remarkably personal footnote/);assert.doesNotMatch(element('#app').innerHTML,/A promising first draft/);
 const romance=async(type,index,choice='romantic',room)=>click({romanceAction:type,romanceWho:'mira',...(index===undefined?{}:{romanceIndex:String(index)}),romanceChoice:choice,...(room?{romanceRoom:room}:{})});
 const day=value('state.dayNumber'),funds=value('state.sharedFunds');
 await romance('share-romance',0,'friendly');assert.match(element('#app').innerHTML,/Romantic invitations:<\/strong> Paused/);assert.equal(value('state.romance.people.mira.level'),0);
 await romance('reopen-romance');await romance('defer-romance');assert.match(element('#app').innerHTML,/Return this invitation/);await romance('restore-romance');
 await romance('share-romance',0);assert.equal(value('state.romance.people.mira.level'),1);assert.equal(value('state.dayNumber'),day);assert.equal(value('state.sharedFunds'),funds);
 assert.match(element('#app').innerHTML,/three excellent excuses/);assert.match(element('#app').innerHTML,/Let one phase pass/);
 await value('commit({type:"advance"})');await romance('share-romance',1);assert.match(element('#app').innerHTML,/A promising first draft/);
 await click({outfitAction:'accept-outfit-invitation',outfitOwner:'mira',outfitTier:'2'});
 assert.match(element('#app').innerHTML,/Choose an illustrated outfit for a date/);
 await click({outfitAction:'choose-outfit',outfitOwner:'mira',outfitTier:'2'});assert.equal(value('state.outfitProgression.mira.selected'),'2');
 await romance('share-romantic-date',undefined,'romantic','pool');assert.match(element('#app').innerHTML,/light kiss before returning/);
 await value('commit({type:"advance"})');await romance('share-romance',2);assert.match(element('#app').innerHTML,/Partners/);
 await value('commit({type:"advance"})');await romance('share-romance',3);assert.match(element('#app').innerHTML,/Partners · private evening shared/);assert.match(element('#app').innerHTML,/Hearthside reading/);
 const record=value('JSON.stringify(state.romance)');await value('readState().then(s=>{state=s;render();})');assert.equal(value('JSON.stringify(state.romance)'),record);
 await romance('pause-romance');assert.equal(value('state.romance.people.mira.level'),4);assert.match(element('#app').innerHTML,/Romantic invitations:<\/strong> Paused/);
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 console.log('PASS: mutual progression, friendly pause/reopen, later/restore, hidden scenes, phase gate, all milestones, real outfit selection, illustrated date, resource preservation and reload.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
