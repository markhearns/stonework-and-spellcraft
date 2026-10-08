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
const bridge = "import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1]);url=urlsplit(sys.argv[2]);payload=json.load(sys.stdin)\ntry:\n store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n if url.path=='/api/public-workshop/catalogue':\n  import public_workshop\n  import public_integration\n  result=public_integration.catalogue_view()\n elif url.path=='/api/expansion-packs/bundled':result=store.stage_public_bundle()\n elif url.path=='/api/expansion-packs':result=store.expansion_pack_catalogue()\n elif url.path=='/api/expansion-packs/preview':result=store.expansion_pack_preview(payload.get('digest'))\n elif url.path=='/api/household-content':\n  import household_content\n  state=store.read();summary=state.get('activeContentPack')\n  result=household_content.catalogue(state,store.content_pack_preview(summary['digest']) if summary else None)\n elif url.path=='/api/content-packs':result=store.content_pack_catalogue()\n elif url.path=='/api/content-packs/validate':result=store.validate_content_pack(payload)\n elif url.path=='/api/content-packs/preview':result=store.content_pack_preview(payload.get('digest'))\n elif url.path=='/api/provider':result=ProviderSettings(sys.argv[1]).public()\n elif url.path=='/api/campaigns':result={'campaigns':library.list()}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  svc=DialogueService(ProviderSettings(sys.argv[1]))\n  result=svc.review_candidate(store,payload) if url.path.endswith('/review') else svc.generate(store,payload) if url.path.endswith('/draft') else public_state(svc.accept(store,payload))\n else:result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:print(json.dumps({'error':str(error)}))\n";
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  btoa:text=>Buffer.from(text,'binary').toString('base64'), Uint8Array, console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8',maxBuffer:32*1024*1024}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});



(async()=>{try {
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'publicWorkshop'});await vm.runInContext('loadPublicCatalogue()',context);
 assert.match(element('#app').innerHTML,/Public workshop/);
 assert.equal(vm.runInContext('state.publicWorkshopView.implementedMechanics',context),319);
 element('#public-type').value='equipment-concept';await click({publicAction:'filter'});
 element('#public-owner').value='founder';element('#public-room').value='library';element('#public-reviewed').checked=true;
 element('#public-material-0').value='binding-thread';element('#public-material-1').value='porous-clay';
 await click({buy:'porous-clay'});
 const funds=vm.runInContext('state.sharedFunds',context);
 await click({publicAction:'start'});
 assert.equal(vm.runInContext('state.sharedFunds',context),funds-6);
 assert.equal(vm.runInContext('state.founderAssignment',context),'public-project');
 await click({publicAction:'pause',ownerId:'founder'});await click({action:'advance'});
 assert.equal(vm.runInContext('state.publicWorkshopView.jobs.founder.completedWorkPhases',context),0);
 await click({publicAction:'resume',ownerId:'founder'});
 await click({action:'advance'});await click({action:'advance'});
 assert.equal(vm.runInContext('Object.keys(state.publicWorkshopView.items).length',context),1);
 assert.equal(vm.runInContext('Object.keys(state.publicWorkshopView.jobs).length',context),0);
 element('#public-type').value='book-or-document';await click({publicAction:'filter'});
 element('#public-evidence').value='The author permits this newly acquired printed copy and its reading.';
 await click({publicAction:'make-household-object'});await click({action:'advance'});await click({action:'advance'});
 const book=vm.runInContext("Object.values(state.publicWorkshopView.items).find(x=>x.contentKind==='book-or-document').id",context);
 element('#public-item').value=book;await click({publicAction:'read-object'});await click({action:'advance'});
 assert.equal(vm.runInContext(`state.publicWorkshopView.items['${book}'].read`,context),true);
 element('#public-type').value='site-template';await click({publicAction:'filter'});
 element('#public-evidence').value='The public destination and open walking route are established for this chosen trip.';
 await click({publicAction:'start-field-trip'});
 assert.equal(vm.runInContext('state.founderAtCastle',context),false);
 await click({action:'advance'});
 assert.equal(vm.runInContext('state.publicWorkshopView.fieldTrip.stage',context),'awaiting-choice');
 const lead=vm.runInContext('state.publicWorkshopView.fieldTrip.leads[0].id',context);
 await click({publicAction:'field-lead',recordId:lead});await click({action:'advance'});await click({action:'advance'});
 await click({publicAction:'return-field-trip'});await click({action:'advance'});
 assert.equal(vm.runInContext('state.founderAtCastle',context),true);
 assert.equal(vm.runInContext('state.publicWorkshopView.lastFieldReport.observations.length',context),1);
 // Continue through returned discovery, personal chapters, neighbours and production.
 const discovery=vm.runInContext('state.publicWorkshopView.returnedDiscoveries[0]',context);
 await click({publicAction:'open-record',recordId:discovery.recordId});
 element('#public-discovery-receipt').value=discovery.receiptId;
 await click({publicAction:'share-discovery'});
 assert.equal(vm.runInContext('Object.keys(state.publicWorkshopView.discoveries).length',context),1);
 await click({publicAction:'open-type',recordType:'personal-arc'});
 element('#public-owner').value='mira';element('#public-evidence').value='Mira chose to examine this incomplete family recipe, which she brought to the household.';
 vm.runInContext('publicCatalogue.records[publicRecordId].establishedFactRequirements',context).forEach((q,n)=>element('#public-journey-evidence-'+n).value='Established for this test: '+q.fact);
 await click({publicAction:'start-journey'});
 const journey=vm.runInContext('state.publicWorkshopView.journeys[0]',context);
 assert(journey);assert.match(element('#app').innerHTML,/Stories & chosen developments/);
 element('#journey-note-'+journey.id).value='Mira chose to compare what her recipe says and which steps need clarification.';
 element('#journey-review-'+journey.id).checked=true;
 journey.chapters[0].requirements.forEach((q,n)=>element('#chapter-'+journey.id+'-'+n).value='Reviewed actual context: '+q);
 await click({publicAction:'open-chapter',journeyId:journey.id,ownerId:'mira'});
 const scene=vm.runInContext('state.publicWorkshopView.journeys[0].current.sceneId',context);
 await click({view:'householdContent'});
 await click({householdContent:'join',sceneId:scene,choiceIndex:'0'});
 assert.equal(vm.runInContext(`state.householdScenes['${scene}'].status`,context),'remembered');
 await click({view:'publicWorkshop'});
 await click({publicAction:'work-chapter',journeyId:journey.id,ownerId:'mira'});await click({action:'advance'});
 element('#journey-choice-'+journey.id).value='continue';
 await click({publicAction:'resolve-chapter',journeyId:journey.id,ownerId:'mira'});
 assert.equal(vm.runInContext('state.publicWorkshopView.journeys[0].chapterIndex',context),1);
 await click({publicAction:'open-type',recordType:'community-template'});element('#public-owner').value='founder';
 element('#public-evidence').value='The neighbouring court agreed to an introductory visit over its publicly open route.';
 await click({publicAction:'establish-community'});await click({action:'advance'});await click({action:'advance'});
 assert.equal(vm.runInContext('Object.keys(state.publicWorkshopView.communities).length',context),1);
 await click({publicAction:'open-type',recordType:'contact-role'});element('#public-contact-name').value='Vela';
 await click({publicAction:'meet-contact'});await click({action:'advance'});
 assert.equal(vm.runInContext('Object.values(state.publicWorkshopView.contacts)[0].name',context),'Vela');
 await click({publicAction:'open-type',recordType:'wardrobe-art-brief'});element('#public-owner').value='mira';
 await click({publicAction:'save-brief-style'});await click({publicAction:'save-brief'});
 assert.equal(vm.runInContext('Object.keys(state.residentStyles.mira).length',context),1);
 assert.equal(vm.runInContext('Object.keys(state.publicWorkshopView.productionBriefs).length',context),1);
 assert.match(element('#app').innerHTML,/Download this production brief/);
 // Withdrawing care also withdraws its unopened invitation.
 await click({publicAction:'open-type',recordType:'care-case'});element('#public-owner').value='mira';
 vm.runInContext('publicCatalogue.records[publicRecordId].establishedFactRequirements',context).forEach((q,n)=>element('#public-journey-evidence-'+n).value='Confirmed care request: '+q.fact);
 await click({publicAction:'start-journey'});
 const care=vm.runInContext('state.publicWorkshopView.journeys.find(x=>x.kind==="care-case")',context);
 element('#journey-note-'+care.id).value='Mira asks for this practical support and chooses a quiet available place.';element('#journey-review-'+care.id).checked=true;
 care.chapters[0].requirements.forEach((q,n)=>element('#chapter-'+care.id+'-'+n).value='Reviewed in this available room: '+q);
 await click({publicAction:'open-chapter',journeyId:care.id,ownerId:'mira'});
 await click({publicAction:'end-care',journeyId:care.id,ownerId:'mira'});
 await click({publicAction:'open-chapter-scene',journeyId:care.id,ownerId:'mira'});
 assert.match(element('#app').innerHTML,/Support ended by choice/);
 await click({view:'publicWorkshop'});
 // Every public type renders an inspectable, navigable workflow without undefined values.
 const types=vm.runInContext('[...new Set(Object.values(publicCatalogue.records).map(r=>r.recordType))].filter(x=>x!=="mechanics-proposal")',context);
 for(const type of types){await click({publicAction:'open-type',recordType:type});assert.doesNotMatch(element('#app').innerHTML,/undefined|NaN/,type);}
 console.log('Public integration UI: all record types, actual costs, field return, discovery, joined chapter, assigned work, resolution, community, named contact and wardrobe/art production passed.');

} finally {fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
