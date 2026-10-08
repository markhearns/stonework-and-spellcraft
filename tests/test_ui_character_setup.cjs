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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/portrait-settings':\n  from portrait_generation import PortraitSettings\n  result=PortraitSettings(sys.argv[1]).public()\n elif url.path=='/api/portrait-draft':\n  from portrait_generation import PortraitSettings,PortraitService\n  settings=PortraitSettings(sys.argv[1]);settings.save({'enabled':True,'model':'fixture/image','apiKey':'fixture'})\n  result=PortraitService(settings,lambda c,p:'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=').generate(store,payload)\n elif url.path=='/api/portrait-drafts':\n  from portrait_generation import PortraitSettings,PortraitService\n  result=PortraitService(PortraitSettings(sys.argv[1])).list(store)\n elif url.path=='/api/upload':result={'assetPath':store.upload(payload)}\n elif url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result=library.create(payload) if payload else {'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
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
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const value=expr=>vm.runInContext(expr,context);
 assert.equal(value('currentView'),'characterSetup');
 assert.match(element('#app').innerHTML,/Name/);assert.match(element('#app').innerHTML,/Age/);
 assert.match(element('#app').innerHTML,/Using the placeholder/);
 assert.match(element('#app').innerHTML,/Generate a portrait with an image model/);
 const fields={name:'Aster <b>',age:'28',pronouns:'they/them',background:'traveller',appearanceDescription:'Curly hair',backgroundNotes:'A quiet traveller'};
 await events.submit({preventDefault(){},target:{id:'founder-profile-form',fields}});
 assert.equal(value('state.people.founder.name'),'Aster <b>');
 assert.match(element('#app').innerHTML,/Aster &lt;b&gt;/);
 assert.equal(value('state.people.founder.adultAgeYears'),28);
 const before=value('state.revision');
 await click({portraitGenerate:'new'});
 assert.equal(value('portraitDraft.status'),'ready');
 assert.equal(value('state.revision'),before);
 assert.match(element('#app').innerHTML,/class="portrait-generation" open/);
 assert.match(element('#app').innerHTML,/Accept this portrait/);
 assert.equal(value('state.assetOverrides.founder'),undefined);
 await click({portraitAccept:'yes'});
 const accepted=value('state.assetOverrides.founder');assert.match(accepted,/user-assets/);
 await click({portraitPlaceholder:'yes'});
 assert.equal(value('state.assetOverrides.founder'),undefined);
 await click({action:'rollback-art'});
 assert.equal(value('state.assetOverrides.founder'),accepted);
 // Imported preview also follows the existing upload/accept transaction.
 vm.runInContext("proposedArtwork={url:'data:image/webp;base64,UklGRjAwMDBXRUJQZml4dHVyZQ=='};render()",context);
 assert.match(element('#app').innerHTML,/Accept imported portrait/);
 await click({action:'accept-art'});
 assert.match(value('state.assetOverrides.founder'),/webp$/);
 assert.ok(value('state.assetHistory.founder.includes('+JSON.stringify(accepted)+')'));
 await click({setupContinue:'yes'});
 assert.equal(value('currentView'),'arrival');
 await click({arrivalEnter:'skip'});
 assert.equal(value('currentView'),'castle');
 await click({view:'characterSetup'});
 assert.equal(value('state.people.founder.name'),'Aster <b>');
 await click({portraitRecover:'yes'});
 assert.equal(value('portraitDraft.status'),'accepted');
 assert.equal(value('state.sharedFunds'),40);assert.equal(value('state.dayNumber'),1);
 console.log('PASS: player identity, escaping, generated preview/acceptance, import acceptance, placeholder/rollback, portrait recovery and arrival continuation.');
 } finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
