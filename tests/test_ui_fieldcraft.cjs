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
  if (!elements.has(id)) elements.set(id, {innerHTML:'',textContent:'',classList:{add(){},remove(){}},addEventListener(type, callback){events[type]=callback;},showModal(){this.open=true;}});
  return elements.get(id);
}
let dropCreationResponse = false;
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/validate':result=store.validate_expansion_pack(payload)\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/dialogue/drafts':\n  with store.connect() as db:result={'drafts':[json.loads(r[0]) for r in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC')]}\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  def completion(settings,messages):\n   scene=next(iter(store.read()['householdScenes'].values()))\n   return {'text':json.dumps({'title':'A shared quiet','invitation':'Company?','opening':'She leaves room beside her.','replies':['She respects your choice.']*len(scene['choices'])}),'usage':{'total_tokens':80}}\n  svc=DialogueService(ProviderSettings(sys.argv[1]),completion)\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8'}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});





(async()=>{try {
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import CampaignLibrary\nimport game as g\nstore=CampaignLibrary(sys.argv[1]).get('default');s=store.read();s['craftedArtifacts']['scholars-folio']=1;s['sharedFunds']=200\nfor key in s['materialInventory']:s['materialInventory'][key]=10\ng.learn_for_character(s,'mira','field-calibration')\nwith store.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'equipment'});await click({toolOwner:'founder'});assert.match(element('#app').innerHTML,/Discover, understand, make, use/);
 element('#equipment-owner').value='mira';await click({toolAction:'owner'});
 await click({toolAction:'claim',itemId:'scholars-folio'});
 const item=vm.runInContext('Object.keys(state.personalEquipment)[0]',context);
 element('#tool-vessel-'+item).value='porous-clay';element('#tool-binding-'+item).value='binding-thread';
 await click({toolAction:'upgrade',itemId:item,ownerId:'mira'});assert.equal(vm.runInContext('state.residentAssignment',context),'inscribing');
 await click({view:'workroom'});assert.match(element('#app').innerHTML,/Personal tool inscription/);
 await vm.runInContext("commit({type:'advance'},'')",context);
 await click({toolOwner:'mira'});await click({worker:'mira',workerAssignment:'rest'});
 await vm.runInContext("commit({type:'advance'},'')",context);assert.equal(vm.runInContext('state.toolUpgradeProjects.mira.completedWorkPhases',context),1);
 await click({toolAction:'resume',ownerId:'mira'});await vm.runInContext("commit({type:'advance'},'')",context);
 assert.equal(vm.runInContext('state.toolUpgradeProjects.mira',context),undefined);
 assert.match(element('#app').innerHTML,/Cross-reference inscription/);
 await click({toolAction:'prepare',itemId:item});assert.match(element('#app').innerHTML,/\+2 matching work/);
 await click({view:'household'});assert.match(element('#app').innerHTML,/Something made her own/);
 await click({toolAction:'defer',itemId:item,ownerId:'mira'});await click({toolAction:'restore',itemId:item,ownerId:'mira'});
 await click({toolAction:'playful',itemId:item,ownerId:'mira'});
 assert.equal(vm.runInContext(`state.toolMoments['${item}'].status`,context),'remembered');assert.match(element('#app').innerHTML,/all your attention/);
 await click({view:'spells'});assert.match(element('#app').innerHTML,/fixed combinations of ideas/);
 const parts=vm.runInContext("state.spellGuidance[selectedCharacterId]['warm-twist'].availableCombinations[0]",context);
 const revision=vm.runInContext('state.revision',context);
 await click({guideForm:'warm-twist',combo:'0'});
 assert.equal(vm.runInContext("spellDrafts[selectedCharacterId+':warm-twist'].firstComponent",context),parts[0]);
 assert.equal(vm.runInContext('state.revision',context),revision);
 await click({site:'old-waterworks'});assert.match(element('#app').innerHTML,/field observations for Field calibration/);
 console.log('PASS: tool inscription start/pause/resume/completion, earned resident invitation, workroom visibility, offline spell form guidance and discovery links.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
