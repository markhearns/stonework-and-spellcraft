// Containment lifecycle connected UI regression.
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
const bridge = `import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nsys.path.insert(0,'tests')\nfrom test_candidate_proposals import candidate_fixture\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1])\nurl=urlsplit(sys.argv[2])\npayload=json.load(sys.stdin)\ntry:\n if url.path=='/api/provider':\n  settings=ProviderSettings(sys.argv[1])\n  result=settings.save(payload) if payload else settings.public()\n elif url.path=='/api/dialogue/drafts':\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  with store.connect() as db:\n   result={'drafts':[json.loads(row[0]) for row in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC LIMIT 8')]}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  service=DialogueService(ProviderSettings(sys.argv[1]),lambda settings,messages:{'text':json.dumps(candidate_fixture(name='<svg/onload=alert(1)>',occupation='<b>glassworker</b>')) if 'Propose one fictional adult woman' in messages[0]['content'] else json.dumps({'formId':'warm-twist','name':'<Cord suggestion>','explanation':'Bind plant fibres into cord.','limitations':['No powers beyond the listed effect.']}) if 'Suggest a bounded spell construction' in messages[0]['content'] else 'A generated <reply> with quiet wit.','usage':{'total_tokens':17}})\n  result=service.review_candidate(store,payload) if url.path.endswith('/review') else service.generate(store,payload) if url.path.endswith('/draft') else public_state(service.accept(store,payload))\n elif url.path=='/api/campaigns':\n  result=library.create(payload) if payload else {'campaigns':library.list()}\n else:\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:\n print(json.dumps({'error':str(error)}))`;
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8',maxBuffer:32*1024*1024}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    if(json.error)console.error(url,json.error);
    return {ok:!json.error,async json(){return json;}};
  }
});

const fixture=`import json,sys
from server import CampaignLibrary
import game as g
s=g.new_campaign();s['sharedFunds']=250;s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'};s['binderyDiscoveries']=['salvage']
for key in s['materialInventory']:s['materialInventory'][key]=20
for key in ('water-guidance','gentle-preservation'):g.learn_for_character(s,'founder',key)
s['housingRooms']['garden-chamber']['status']='complete';s['housingRooms']['west-chamber']['status']='complete'
store=CampaignLibrary(sys.argv[1]).get('default')
with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))`;
(async()=>{try {
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 const read=expression=>vm.runInContext(expression,context);
 const care=(action,who='',extra={})=>click({containmentAction:action,carePerson:who,...extra});
 const advance=async n=>{for(let i=0;i<n;i++)await click({action:'advance'});};
 await click({view:'containment'});assert.match(element('#app').innerHTML,/optional maximum 2/);
 await care('build-containment','',{chamberId:'echo-1'});await advance(1);
 await click({founder:'rest'});await advance(1);
 assert.equal(read('state.containment.project.completedWorkPhases'),1);
 await care('resume-containment');await advance(1);
 await care('admit-containment','sabine',{chamberId:'echo-1'});await advance(1);
 assert.match(element('#app').innerHTML,/assets\/portraits\/sabine.webp/);
 assert.match(element('#app').innerHTML,/Hear her account/);
 assert(!read('state.householdMembers?.includes("sabine")||Boolean(state.characterCatalog.sabine)'));
 await click({summoningCandidate:'sabine'});
 assert.match(element('#app').innerHTML,/Normal visits and recruitment are not available/);
 assert(!element('#app').innerHTML.includes('>Reopen the same contact<'));
 await click({view:'containment'});
 for(const topic of ['account','plan'])await care('talk-containment','sabine',{careTopic:topic});
 await care('care-containment','sabine');await advance(3);
 assert.match(element('#app').innerHTML,/Agree unconditional release/);
 await care('release-containment','sabine');await advance(1);
 assert.equal(read('state.containmentView.occupiedCapacity'),0);
 await click({summoningCandidate:'sabine'});
 for(const topic of ['intentions','home','visit'])await click({summoningAction:'summoning-talk',contactId:'encounter-sabine',topic});
 await click({summoningAction:'summoning-invite',contactId:'encounter-sabine',visitRoom:'west-chamber'});await advance(1);
 await click({summoningAction:'summoning-ask-stay',contactId:'encounter-sabine'});
 assert(!read('Boolean(state.characterCatalog.sabine)'));
 await click({summoningAction:'summoning-household-decision',contactId:'encounter-sabine',stayDecision:'invite-to-stay'});
 assert(read('Boolean(state.characterCatalog.sabine)'));
 for(const page of ['development','focus','spells','household','housing','ledger','workroom','review','summoning','containment']) {
   read(`selectedCharacterId='sabine';setView('${page}')`);
   assert(!element('#app').innerHTML.includes('undefined'),page+' missing data');
 }
 await click({view:'containment'});
 await read('readState().then(result=>{state=result;render();})');
 assert.equal(read('state.containment.cases.sabine.status'),'released');
 assert.equal(read('state.containmentView.occupiedCapacity'),0);
 console.log('PASS: specialized chamber UI construction, pause/resume, care, release, separate visit/membership, artwork, reload.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
