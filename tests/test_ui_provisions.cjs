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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 const value=s=>vm.runInContext(s,context);
 await click({view:'stores'});assert.match(element('#app').innerHTML,/Food and pantry/);
 const old=value('state.provisionsView.stock');await click({foodAction:JSON.stringify({type:'food-buy',bundles:1})});assert.equal(value('state.provisionsView.stock'),old+6);
 await click({foodAction:JSON.stringify({type:'food-assign',characterId:'mira',assignment:'forage'})});assert.equal(value('state.residentAssignment'),'forage');
 element('#food-target').value=7;element('#food-budget').value=2;element('#food-floor').value=10;await click({foodPolicy:'on'});assert.equal(value('state.provisionsView.auto'),true);
 await click({view:'roadsWeKeep'});assert.match(element('#app').innerHTML,/Conclude Arms of Our Own/);
 await click({view:'expeditions'});assert.match(element('#app').innerHTML,/Pantry:/);
 value("state.restorationStatus='complete'");assert.match(value('conservatoryPage()'),/data-production="provisions"/);
 await click({hqRoom:'supply-office'});assert.match(element('#app').innerHTML,/Supply Office/);
 value("state.provisionsView.office=true;supplyBasket={'silver-ivy':30}");const panel=value('supplyOfficePanel()');assert.match(panel,/Delivery quote/);assert.doesNotMatch(panel,/NaN/);
 console.log('PASS: food purchases, primary gathering assignment, auto policy, Chapter 6 gating, expedition pantry and garden control.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
