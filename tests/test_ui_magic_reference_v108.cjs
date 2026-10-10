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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys\nfrom server import GameStore\nGameStore(sys.argv[1],start_type='fresh')",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const before=value('JSON.stringify(state)');
 assert.ok(value("SYSTEM_GROUPS.magicHub.views.some(r=>r[0]==='magicReference')"));
 value("setView('magicReference')");
 let html=value('systemPageContent()');
 assert.match(html,/Spells &amp; Rituals|Spells & Rituals/);assert.match(html,/50 matching entries/);assert.match(html,/data-magic-reference-entry="water-jet"/);
 value("magicReferenceClick({magicReferenceKind:'ritual'})");html=value('magicReferencePage()');assert.match(html,/14 matching entries/);assert.doesNotMatch(html,/data-magic-reference-entry="water-jet"/);
 value("magicReferenceClick({magicReferenceEntry:'archive-circle'})");html=value('magicReferencePage()');assert.match(html,/Scholar Elian Voss/);assert.match(html,/60 crowns/);assert.match(html,/data-magic-reference-open="archive-circle"/);
 value("magicReferenceClick({magicReferenceBack:'yes'})");assert.match(value('magicReferencePage()'),/14 matching entries/);
 value("magicReferenceKind='all';magicReferenceCollection='all';magicReferenceQuery='underwater'");assert.match(value('magicReferencePage()'),/Undertide breath/);
 value("magicReferenceQuery='zzzz-no-working'");assert.match(value('magicReferencePage()'),/No workings match/);
 value("magicReferenceClick({magicReferenceReset:'yes'})");assert.match(value('magicReferencePage()'),/142 matching entries/);
 value("navigateTarget({view:'magicReference',entryId:'water-jet'})");assert.equal(value('magicReferenceEntry'),'water-jet');assert.match(value('unifiedBreadcrumb()'),/Water jet/);
 value("magicReferenceClick({magicReferenceOpen:'water-jet'})");assert.equal(value('currentView'),'spells');assert.equal(value('spellFormId'),'water-jet');assert.match(value('spellsPage()'),/Browse Spells & Rituals/);
 const ids=value('magicReferenceRows().map(r=>r.id)');
 for(const id of ids){value('magicReferenceEntry='+JSON.stringify(id));const entry=value('magicReferencePage()');assert.match(entry,/Scholar Elian Voss/);assert.match(entry,/<img /);assert.doesNotMatch(entry,/undefined|null/);}
 value("magicReferenceCollection='workshop';magicReferenceEntry=null;magicReferenceQuery=''");assert.match(value('magicReferencePage()'),/92 matching entries/);
 const workshop=value("magicReferenceRows().find(r=>r.collection==='workshop')");
 value('magicReferenceClick({magicReferenceOpen:'+JSON.stringify(workshop.id)+'})');await new Promise(resolve=>setImmediate(resolve));assert.equal(value('publicRecordId'),workshop.recordId);assert.equal(value('currentView'),'publicWorkshop');
 assert.equal(value('JSON.stringify(state)'),before,'Browsing and entry links must not change a campaign, materials or time.');
 console.log('PASS: fresh-game route, 142 illustrated/quoted entries, filters, detail/back, search links, action destinations and unchanged save');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
