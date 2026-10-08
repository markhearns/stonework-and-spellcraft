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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/validate':result=store.validate_expansion_pack(payload)\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/dialogue/drafts':\n  with store.connect() as db:result={'drafts':[json.loads(r[0]) for r in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC')]}\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  def completion(settings,messages):\n   scene=next(iter(store.read()['householdScenes'].values()))\n   return {'text':json.dumps({'title':'A shared quiet','invitation':'Company?','opening':'She leaves room beside her.','replies':['She respects your choice.']*len(scene['choices'])}),'usage':{'total_tokens':80}}\n  svc=DialogueService(ProviderSettings(sys.argv[1]),completion)\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n elif url.path=='/api/equipment/quote':\n  import armoury\n  result=armoury.quote_action(store.read(),payload.get('action'))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json\nfrom server import CampaignLibrary\nimport game as g,headquarters as h\ns=CampaignLibrary(sys.argv[1]).get('default');state=s.read();state['sharedFunds']=200;state['headquarters']['rooms'].update({k:'complete' for k in h.ROOMS});state['materialInventory'].update({k:20 for k in g.MATERIALS})\nfor p in ('field-calibration','water-guidance','clear-instruction'):g.learn_for_character(state,'founder',p)\nwith s.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(state),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'equipment'});assert.match(element('#app').innerHTML,/Armoury &amp; enchanting|Armoury & enchanting/);
 await click({gearAction:JSON.stringify({type:'gear-review'})});
 const key=vm.runInContext("Object.values(state.armouryView.items).find(i=>i.definitionId==='field-boots'&&i.ownerId==='founder').id",context);assert(key);
 await click({gearItem:key});assert.match(element('#app').innerHTML,/Installed and active/);
 element('#gear-name').value='Road <boots>';await click({gearCommand:'rename'});assert.match(element('#app').innerHTML,/Road &lt;boots&gt;/);
 // Keep boots equipped: reviewed work must stow and fund atomically.
 element('#gear-operation').value='enchant';element('#gear-effect').value='sure-footing';
 await click({gearCommand:'review-work'});assert.match(element('#app').innerHTML,/REVIEW BEFORE COMMITTING/);
 assert.equal(vm.runInContext('gearQuote.blockers.length',context),0);assert.match(element('#app').innerHTML,/Stow Road &lt;boots&gt;/);assert.equal(vm.runInContext('gearQuote.action.stowBeforeWork',context),true);
 const action=vm.runInContext('gearQuote.action',context);await click({gearAction:JSON.stringify(action)});
 assert.equal(vm.runInContext('state.armoury.jobs.founder.operation',context),'enchant');assert.match(element('#app').innerHTML,/0\/2 work/);
 await click({gearReview:JSON.stringify({type:'gear-cancel-job'})});assert.match(element('#app').innerHTML,/Refund 8 crowns/);
 await click({gearAction:JSON.stringify({type:'gear-cancel-job'})});assert.equal(vm.runInContext('state.armoury.jobs.founder',context),undefined);
 await click({gearReview:JSON.stringify(action)});await click({gearAction:JSON.stringify(vm.runInContext('gearQuote.action',context))});
 await click({action:'advance'});await click({action:'advance'});assert.match(element('#app').innerHTML,/Recently completed equipment/);
 await click({gearItem:key});await click({gearReview:JSON.stringify({type:'gear-ready',itemId:key,mode:'expedition',enchantmentId:'sure-footing'})});assert.equal(vm.runInContext('gearQuote.blockers.length',context),0);
 await click({gearAction:JSON.stringify(vm.runInContext('gearQuote.action',context))});assert.equal(vm.runInContext('state.armoury.mode.founder',context),'expedition');assert.match(element('#app').innerHTML,/Test active effect/);
 await click({view:'armsOfOurOwn'});assert.match(element('#app').innerHTML,/Conclude Keeping the Hearth|Conclude.*first/);
 vm.runInContext("state.watchRoad.outcomes=[{name:'The steps',method:'Sure footing',timeSaved:1,equipmentUsed:[{ownerName:'Scholar',name:'Road <boots>',effect:'Sure footing'}],scores:{founder:{detail:'Dexterity 5 + equipment 1 = 6 / 6'}}}]",context);
 const notebook=vm.runInContext('watchRoadNotebook()',context);assert.match(notebook,/Road &lt;boots&gt;/);assert.match(notebook,/1 work phase/);assert.match(notebook,/6 \/ 6/);
 console.log('PASS: reviewed combined stow and funding, refund, completion shortcut, field equip/activation and chapter prerequisite UI.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
