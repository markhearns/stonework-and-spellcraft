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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nsys.path.insert(0,'tests')\nfrom test_customization import CustomizationTests\nfrom server import GameStore\nt=CustomizationTests();t.setUp();st=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const submit=(id,fields)=>events.submit({preventDefault(){},target:{id,fields}});
 const act=(type,data={},who='founder')=>click({personalAction:JSON.stringify({type,characterId:who,...data})});
 await click({personalPerson:'founder'});assert.match(element('#app').innerHTML,/Personal corner/);
 for(const tab of ['overview','appearance','wardrobe','preparation','growth','life','space']){
  await click({personalTab:tab});assert.doesNotMatch(element('#app').innerHTML,/undefined|src="null"/);
 }
 await click({personalTab:'appearance'});await submit('personal-appearance-form',{hairStyle:'Braided',hairColour:'copper'});assert.equal(value('state.customization.people.founder.appearance.hairColour'),'copper');assert.match(element('#app').innerHTML,/Portrait brief/);
 await click({personalTab:'wardrobe'});await submit('personal-style-form',{name:'Reading velvet',occasion:'leisure',colour:'teal',base:'soft-blouse',lower:'long-skirt',feet:'slippers'});
 await act('wear-personal-style',{styleId:'Reading velvet'});assert.match(element('#app').innerHTML,/Reading velvet · selected/);assert.match(element('#app').innerHTML,/established portrait retained/);
 await click({personalTab:'preparation'});await submit('personal-preparation-form',{name:'Ruin explorer'});await act('load-complete-preparation',{name:'Ruin explorer'});assert.match(element('#app').innerHTML,/Ruin explorer/);
 await click({personalTab:'space'});await submit('personal-space-form',{name:'My reading corner',cornerId:'reading',roomId:'library'});assert.equal(value('state.customization.people.founder.space.installed'),true);
 await click({room:'library'});assert.match(element('#app').innerHTML,/My reading corner/);
 await click({personalPerson:'mira'});await click({personalTab:'life'});await act('share-personal-scene',{sceneId:'tastes',choice:'warm'},'mira');assert.match(element('#app').innerHTML,/bad poetry/);
 await submit('personal-leisure-form',{roomId:'common-room'});assert.equal(value('state.customization.people.mira.leisureRoom'),'common-room');
 await click({personalTab:'wardrobe'});assert.match(element('#app').innerHTML,/mira-outfit-2/);assert.match(element('#app').innerHTML,/Share wardrobe invitation/);
 await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.customization.people.founder.selectedStyle'),'Reading velvet');assert.equal(value('state.schemaVersion'),65);
 console.log('PASS: seven character tabs, appearance brief, saved garment ensemble, atomic preparation, paid personal corner in actual room, companion tastes, leisure routine, illustrated wardrobe, reload.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
