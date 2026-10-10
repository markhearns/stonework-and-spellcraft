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
const bridge = `import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nsys.path.insert(0,'tests')\nfrom test_candidate_proposals import candidate_fixture\nimport character_pool as pool\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1])\nurl=urlsplit(sys.argv[2])\npayload=json.load(sys.stdin)\ntry:\n if url.path=='/api/provider':\n  settings=ProviderSettings(sys.argv[1])\n  result=settings.save(payload) if payload else settings.public()\n elif url.path=='/api/dialogue/drafts':\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  with store.connect() as db:\n   result={'drafts':[json.loads(row[0]) for row in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC LIMIT 8')]}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review','/api/story/review'):\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  service=DialogueService(ProviderSettings(sys.argv[1]),lambda settings,messages:{'text':json.dumps(candidate_fixture(name='<svg/onload=alert(1)>',**{k:v for k,v in pool.offline(store.read(),pool.select(store.read(),payload['requestId'],payload.get('poolChoices',{})),payload['requestId']).items() if k in ('occupation','ancestryLabel','adultAgeYears','capabilityPackageId')})) if 'Propose one fictional adult woman' in messages[0]['content'] else json.dumps({'formId':'warm-twist','name':'<Cord suggestion>','explanation':'Bind plant fibres into cord.','limitations':['No powers beyond the listed effect.']}) if 'Suggest a bounded spell construction' in messages[0]['content'] else 'A generated <reply> with quiet wit.','usage':{'total_tokens':17}})\n  result=service.review_story(store,payload) if url.path=='/api/story/review' else service.review_candidate(store,payload) if url.path.endswith('/review') else service.generate(store,payload) if url.path.endswith('/draft') else public_state(service.accept(store,payload))\n elif url.path=='/api/campaigns':\n  result=library.create(payload) if payload else {'campaigns':library.list()}\n else:\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:\n print(json.dumps({'error':str(error)}))`;
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  console, URLSearchParams, crypto:require('node:crypto').webcrypto,
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



const fixture=`import json,sys\nfrom server import CampaignLibrary\nimport game as g\ns=g.new_campaign();s['sharedFunds']=300\nfor k in s['materialInventory']:s['materialInventory'][k]=20\ns['housingRooms']['garden-chamber']['status']='complete'\nstore=CampaignLibrary(sys.argv[1]).get('default')\nwith store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))`;
(async()=>{try{
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'localEncounters'});assert.match(element('#app').innerHTML,/koharu.webp/);assert.match(element('#app').innerHTML,/wolfkin/i);
 await click({localEncounterAction:'start-local-visit',encounterId:'koharu'});await click({founder:'rest'});await click({action:'advance'});
 assert.equal(vm.runInContext('state.localEncounters.koharu.status',context),'available');
 await click({localEncounterAction:'resume-local-visit'});await click({action:'advance'});
 assert.equal(vm.runInContext('state.residency.koharu.residencyStatus',context),'remote');
 await click({summoningCandidate:'koharu'});assert.match(element('#app').innerHTML,/koharu.webp/);
 const cid='introduced-koharu';
 for(const topic of ['intentions','home','visit'])await click({summoningAction:'summoning-talk',contactId:cid,topic});
 await click({summoningAction:'summoning-invite',contactId:cid,visitRoom:'garden-chamber'});await click({action:'advance'});
 await click({summoningAction:'summoning-ask-stay',contactId:cid});await click({summoningAction:'summoning-household-decision',contactId:cid,stayDecision:'invite-to-stay'});
 await click({character:'koharu'});assert.match(element('#app').innerHTML,/Practised strength/);
 await click({storyOwner:'koharu'});element('#story-package').value='personal-folio';
 await click({storyDraft:'offline'});element('#story-content-reviewed').checked=true;element('#story-mechanics-reviewed').checked=true;await click({storyDraft:'approve'});
 const first=vm.runInContext('Object.keys(state.personalStories)[0]',context);
 await click({storyAction:'start-personal-story',storyId:first});await click({action:'advance'});await click({action:'advance'});
 assert.equal(vm.runInContext(`state.personalStoryView.owners.koharu.packages['shared-revision']`,context),undefined);
 await click({storyAction:'join-story-scene',storyId:first});
 assert(vm.runInContext(`state.personalStoryView.owners.koharu.packages['shared-revision']`,context));
 element('#story-package').value='shared-revision';await click({storyDraft:'offline'});
 assert.match(element('#app').innerHTML,/Build on the completed work/);
 await click({storyDraft:'approve'});
 const second=vm.runInContext('Object.keys(state.personalStories)[1]',context);
 assert(vm.runInContext(`state.personalStories['${second}'].continuitySources.includes('${first}')`,context));
 await vm.runInContext('readState().then(s=>{state=s;render();})',context);
 assert(!element('#app').innerHTML.includes('undefined'));
 console.log('PASS: illustrated local meeting, pause/resume, ordinary contact, two-sided membership, ancestry training display, shared-history chapter unlock and durable continuity. Headless only.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
