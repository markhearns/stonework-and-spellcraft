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
 const setup="import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_resident_friendships import FriendshipTests\nfrom server import GameStore\nt=FriendshipTests();t.setUp();t.points(value=100);t.points('iona|tamsin',25);st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))";
 execFileSync(process.env.PYTHON||'python',['-c',setup,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const action=async(a)=>click({foodAction:JSON.stringify(a)});
 const text=()=>value('plainMarkup(document.querySelector("#app").innerHTML)');
 await click({view:'peopleHub'});assert.match(text(),/Resident friendships/);
 await click({friendshipFilter:'invitations'});assert.equal(value('sectionForView(currentView)'),'peopleHub');
 assert.match(text(),/Make time for one another/);
 assert.doesNotMatch(text(),/The desert remains accessible/);
 assert.ok(Array.isArray(value('state.residentFriendships')),'Older friendship summaries remain compatible');
 await click({friendshipPair:'mira|tamsin'});
 const before=value('JSON.stringify(state)');value('residentFriendshipsPage()');assert.equal(value('JSON.stringify(state)'),before);
 await action({type:'friendship-share',pairId:'mira|tamsin',stage:'meeting'});
 assert.match(text(),/The traveller has reached the desert/);
 assert.match(text(),/4 crowns for supplies/);
 await action({type:'friendship-defer',pairId:'mira|tamsin',stage:'project'});
 assert.match(text(),/Set aside/);await action({type:'friendship-restore',pairId:'mira|tamsin',stage:'project'});
 await action({type:'friendship-arrange',pairId:'mira|tamsin',stage:'project'});
 assert.equal(value('state.sharedFunds'),96);assert.match(text(),/Both|shared phase/);
 await action({type:'assign-character',characterId:'tamsin',assignment:'rest'});assert.match(text(),/Paused/);
 await action({type:'friendship-resume'});await action({type:'advance'});
 assert.match(text(),/Adjustable shared book rest/);assert.match(text(),/Cooperation unlocked/);
 assert.equal(value('state.residentFriendshipsView.pairs.find(r=>r.id==="mira|tamsin").cooperation'),2);
 await action({type:'friendship-arrange',pairId:'mira|tamsin',stage:'visit'});await action({type:'advance'});
 assert.match(text(),/A mark|welcom|oasis/);
 await action({type:'friendship-share',pairId:'mira|tamsin',stage:'tradition'});
 assert.match(text(),/A shared tradition remembered/);
 assert.equal(value('Object.keys(state.residentFriendshipsView.pairs.find(r=>r.id==="mira|tamsin").memories).length'),4);
 await click({uiTarget:JSON.stringify({view:'characterProfile',personId:'mira',characterTab:'relationships'})});
 assert.match(text(),/Shared keepsake &amp; milestones|Shared keepsake & milestones/);
 await click({friendshipPair:'mira|tamsin'});assert.match(text(),/Adjustable shared book rest/);
 value("selectedHqRoom='library';currentView='hqRoom';render()");assert.match(text(),/Made by residents/);
 assert.match(text(),/Adjustable shared book rest/);
 await click({friendshipPair:'iona|tamsin'});assert.match(text(),/Try a short game/);
 await action({type:'friendship-share',pairId:'iona|tamsin',stage:'meeting',choice:'game'});
 assert.match(text(),/understand where I went wrong/);
 assert.doesNotMatch(text(),/The traveller calls the hill/);
 const saved=value('JSON.stringify(state)');await value('readState().then(s=>{state=s;render();})');assert.equal(value('JSON.stringify(state)'),saved);
 value("state.characterCatalog.iona.name='<img src=x onerror=alert(1)>';friendshipFocus='iona|tamsin';currentView='residentFriendships';render()");
 assert.doesNotMatch(element('#app').innerHTML,/<img src=x/);assert.match(element('#app').innerHTML,/&lt;img/);
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"|NaN|\[object Object\]/);
 console.log('PASS: friendship navigation, separate legacy summaries, pair profiles and portraits, hidden future replies, requirements, free meeting, defer/restore, paid project, pause/resume, keepsake room, cooperation, follow-up, tradition, generic choices, escaping and saved-state reload.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
