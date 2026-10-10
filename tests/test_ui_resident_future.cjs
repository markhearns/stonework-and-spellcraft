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
 // One established resident is fixture data; all actions below go through GameStore.
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game as g,local_encounters as l,summoning\nst=GameStore(sys.argv[1],start_type='fresh');s=st.read()\ns['localEncounterCandidates']['koharu']=l.definition(s,'koharu');summoning.initialize_person(s,'koharu',summoned=False)\ns['additionalResidents']['koharu']['status']='resident';s['residency']['koharu']['residencyStatus']='resident';s['bedroomAssignments']['koharu']='garden-chamber';s['housingRooms']['garden-chamber']['status']='complete'\ns['headquarters']['rooms']['workshop']='complete';s['sharedFunds']=100\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 const act=async action=>{await value('commit('+JSON.stringify(action)+')');};
 await click({view:'specialists'});assert.match(element('#app').innerHTML,/Resident room improvements/);assert.match(element('#app').innerHTML,/Elowen/);assert.match(element('#app').innerHTML,/Nyssara/);assert.match(element('#app').innerHTML,/Sylva/);assert.match(element('#app').innerHTML,/Aurelia/);assert.match(element('#app').innerHTML,/Neris/);assert.doesNotMatch(element('#app').innerHTML,/>Veyra</);assert.match(element('#app').innerHTML,/Catfolk bookbinder/);assert.doesNotMatch(element('#app').innerHTML,/undefined/);
 await click({view:'livingStories'});assert.match(element('#app').innerHTML,/The repair worth keeping/);
 await click({livingScene:'koharu:0',livingChoice:'quiet'});assert.match(element('#app').innerHTML,/Remembered on day/);assert.equal(value('state.livingStories.memories["koharu:0"].choice'),'quiet');
 await click({view:'specialists'});await click({hqAction:'hq-job',jobId:'specialty-koharu'});assert.equal(value('state.sharedFunds'),76);
 await act({type:'advance'});
 const setKoharuStatus=status=>execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nst=GameStore(sys.argv[1]);s=st.read();s['residency']['koharu']['residencyStatus']=sys.argv[2];s['additionalResidents']['koharu']['status']=sys.argv[2]\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))",directory,status]);
 setKoharuStatus('away');await value('readState().then(s=>{state=s;render();})');
 const cancelButton=element('#app').innerHTML.match(/<button[^>]*data-hq-action="hq-cancel"[^>]*>/)[0];assert.doesNotMatch(cancelButton,/disabled/);
 assert.match(element('#app').innerHTML,/specialist must be a resident and at home/);
 await click({hqAction:'hq-cancel'});assert.equal(value('state.sharedFunds'),100);
 setKoharuStatus('resident');await value('readState().then(s=>{state=s;render();})');
 await click({hqAction:'hq-job',jobId:'specialty-koharu'});
 for(let i=0;i<3;i++)await act({type:'advance'});
 assert.equal(value('state.headquarters.stock["specialty:koharu"]'),1);assert.match(element('#app').innerHTML,/Completed · permanent facility/);
 await act({type:'start-research'});await act({type:'advance'});await act({type:'assign-founder',assignment:'rest'});
 await click({view:'progression'});assert.match(element('#app').innerHTML,/Resume this project/);const funds=value('state.sharedFunds');await click({resumeProject:'hearth'});assert.equal(value('state.sharedFunds'),funds);assert.equal(value('state.founderAssignment'),'research');
 for(let i=0;i<2;i++)await act({type:'advance'});
 await click({view:'localEncounters'});assert.match(element('#app').innerHTML,/Elowen/);assert.match(element('#app').innerHTML,/Drow/);assert.doesNotMatch(element('#app').innerHTML,/src="undefined"/);
 await click({view:'expeditions'});await click({site:'old-service-road'});assert.match(element('#app').innerHTML,/both sets of notes home/);
 // Real returned surveys unlock the longer journey.
 for(const site of ['quarry-shelter','old-waterworks','ridge-cistern']){
  await act({type:'start-expedition',siteId:site});await act({type:'advance'});await act({type:'choose-expedition-approach',approach:'survey'});await act({type:'advance'});await act({type:'advance'});await act({type:'return-expedition'});await act({type:'advance'});
 }
 await act({type:'start-expedition',siteId:'old-service-road'});await act({type:'advance'});await act({type:'choose-expedition-approach',approach:'survey'});
 assert.match(element('#app').innerHTML,/0 \/ 4 ENCOUNTERS/);assert.match(element('#app').innerHTML,/The maintenance fork/);
 await click({encounterMethod:'orchard'});assert.match(element('#app').innerHTML,/2 work phase/);await act({type:'advance'});await act({type:'advance'});
 assert.match(element('#app').innerHTML,/The rooted terrace/);assert.equal(value('state.serviceRoad.route'),'orchard');
 await act({type:'return-expedition'});await act({type:'advance'});await click({view:'livingStories'});assert.match(element('#app').innerHTML,/Remembered on day/);
 console.log('PASS: eleven specialty cards, remembered resident choices, funded installations, direct project resume, elf leads and branched four-stage field controls.');
 }finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
