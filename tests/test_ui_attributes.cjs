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
 const fixture="import sys,json,sqlite3\nimport game as g\nfrom server import GameStore\ns=g.new_campaign();g.award_advancement(s,'founder','fixture',60,'Fixture');s['sharedFunds']=1000;s['researchStatus']='complete'\nst=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))";
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 await click({character:'founder'});
 for(const name of ['Might','Dexterity','Vitality','Intelligence','Resolve','Charisma','Athletics','Diplomacy','Channeling'])assert.match(element('#app').innerHTML,new RegExp(name));
 assert.doesNotMatch(element('#app').innerHTML,/<h3>Insight<\/h3>/);
 await click({socialOpen:'personal:mira:0'});
 assert.match(element('#app').innerHTML,/Charisma 5 \+ Diplomacy 0 = 5 \/ 8/);
 assert.equal(value('state.socialLifeView.scenes.find(r=>r.id==="personal:mira:0").choices["approach:1"].blockers.length'),1);
 assert.equal(value('Object.keys(state.socialLifeView.scenes.find(r=>r.id==="personal:mira:0").choices).length'),5);
 await click({character:'founder'});
 for(const skill of ['diplomacy','athletics'])for(let rank=0;rank<2;rank++){
  await click({skillTrain:skill});await click({action:'advance'});await click({action:'advance'});
 }
 assert.equal(value('state.characterSheets.founder.skills.diplomacy'),2);
 await click({socialOpen:'personal:mira:0'});
 assert.match(element('#app').innerHTML,/Charisma 5 \+ Diplomacy 4 = 9 \/ 8/);
 await click({socialAction:'share-social-conversation',socialScene:'personal:mira:0',socialChoice:'approach:1'});
 assert.match(element('#app').innerHTML,/a rather exact compliment/);
 assert.equal(value('state.socialLife.memories["personal:mira:0"].approachId'),'approach:1');
 await value('commit({type:"start-expedition",siteId:"cinder-aqueduct"})');await click({action:'advance'});
 await value('commit({type:"choose-expedition-approach",approach:"survey"})');await click({view:'expeditions'});
 assert.match(element('#app').innerHTML,/Rake a firebreak/);assert.match(element('#app').innerHTML,/Smother the flames with sand/);
 assert.match(element('#app').innerHTML,/Might 5 \+ Athletics 4 = 9 \/ 9/);
 await click({fieldMethod:'aptitude:firebreak',fieldWho:'founder',fieldTarget:'founder'});await click({action:'advance'});
 assert(value('state.fieldMagic.aqueduct.completed.includes("fire")'));
 await value('readState().then(s=>{state=s;render();})');
 assert.equal(value('state.socialLife.memories["personal:mira:0"].approachId'),'approach:1');
 assert.equal(value('state.characterSheets.founder.skills.athletics'),2);
 assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 console.log('PASS: six attributes, six skills, visible qualification reasons, original choices retained, training, authored alternative memory, specialist expedition route and reload.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
