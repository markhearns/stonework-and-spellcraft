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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g,character_builds\nst=GameStore(sys.argv[1]);s=st.read();s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'};s['provisions']['stock']=300;s['testing']['enabled']=True\ncharacter_builds.build(s,'founder')['attributes']={k:10 for k in character_builds.ATTRIBUTES}\ns['characterSkills']['founder']={k:4 for k in g.CHARACTER_SKILLS}\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const before=value('JSON.stringify(state)');
 await click({view:'bestiary'});assert.match(element('#app').innerHTML,/Creatures and Peoples/);assert.match(element('#app').innerHTML,/14/);
 await click({bestiaryEntry:'grave-silk-spider'});let html=element('#app').innerHTML;
 assert.match(html,/Not yet observed/);assert.match(html,/Grave silk/);assert.match(html,/binding thread/i);assert.match(html,/advanced work/);assert.match(html,/bestiary\/creatures\/grave-silk-spider.webp/);
 await click({bestiaryTab:'ancestries'});await click({bestiaryEntry:'seraph'});assert.match(element('#app').innerHTML,/Generic adult ancestry illustration/);
 assert.equal(value('JSON.stringify(state)'),before,'navigation and references never change campaign state');
 await click({bounty:'grave-silk-spider'});html=element('#app').innerHTML;assert.match(html,/Brook apothecary/);assert.match(html,/healing ward/);assert.match(html,/name="bounty" value="grave-silk-spider"/);assert.match(html,/No food reward/);
 assert.equal(value('JSON.stringify(state)'),before);
 await events.submit({preventDefault(){},target:{id:'field-patrol-form',fields:{bounty:'grave-silk-spider','patroller-founder':'on'}}});
 assert.equal(value('state.fieldPatrolView.active.bountyId||state.fieldPatrols.active.bountyId'),'grave-silk-spider');
 await value('commit({type:"advance"})');html=element('#app').innerHTML;assert.match(html,/Grave-silk spider|Grave silk spider/i);assert.match(html,/bestiary-encounter/);
 const method=value('state.fieldPatrolView.active.choices.find(r=>r.kind==="peace"&&!r.blockers.length).id');
 await value('commit({type:"watch-method",methodId:'+JSON.stringify(method)+'})');await value('commit({type:"advance"})');await value('commit({type:"advance"})');
 assert.equal(value('state.bountyView.receipts.length'),1);assert.equal(value('state.materialInventory["grave-silk"]'),1);
 await click({bestiaryEntry:'grave-silk-spider'});assert.match(element('#app').innerHTML,/Entry complete/);assert.match(element('#app').innerHTML,/Encounter values and responses/);
 await click({patrolRepeat:String(value('state.fieldPatrolView.reports.at(-1).id'))});assert.equal(value('currentView'),'bounties');assert.match(element('#app').innerHTML,/name="bounty" value="grave-silk-spider"/);
 await click({view:'stores'});html=element('#app').innerHTML;assert.doesNotMatch(html,/data-buy="grave-silk"/);assert.match(html,/data-sell="grave-silk"/);assert.match(html,/Source and advanced uses/);assert.doesNotMatch(html,/Hunting targets and recent hunts/);
 await click({view:'cheats'});assert.match(element('#app').innerHTML,/Fill out the bestiary/);await value('commit({type:"cheat-bestiary"})');assert.equal(value('state.bestiaryView.complete'),14);
 await click({view:'bestiary'});await click({bestiaryBack:'yes'});assert.match(element('#app').innerHTML,/14 entries complete/);
 console.log('v0.105 connected headless UI checks passed: bestiary, ancestry, bounty departure, real peaceful resolution, materials, stock purchase restrictions and reveal cheat.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
