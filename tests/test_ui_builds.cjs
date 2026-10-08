// Character build connected UI regression.
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
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8'}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});

const fixture=`import json,sys
from server import CampaignLibrary
import game as g
s=g.new_campaign();g.award_advancement(s,'founder','fixture',60,'Fixture accomplishment');g.learn_for_character(s,'founder','gentle-refraction')
store=CampaignLibrary(sys.argv[1]).get('default')
with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))`;
(async()=>{try {
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 const read=expression=>vm.runInContext(expression,context);
 await click({character:'founder'});
 assert.match(element('#app').innerHTML,/Magical affinities/);
 assert.match(element('#app').innerHTML,/Archive synthesis/);
 await click({buildKind:'attribute',buildTrain:'intelligence'});
 assert.equal(read('state.characterSheets.founder.reservedAdvancement'),3);
 assert.match(element('#app').innerHTML,/<h3>Intelligence<\/h3>/);
 await click({action:'advance'});
 await click({worker:'founder',workerAssignment:'rest'});await click({action:'advance'});
 assert.equal(read('state.trainingProjects.founder.completedWorkPhases'),1);
 await click({worker:'founder',workerAssignment:'training'});await click({action:'advance'});await click({action:'advance'});
 assert.equal(read('state.characterBuildViews.founder.attributes.intelligence'),6);
 await click({buildKind:'affinity',buildTrain:'light'});await click({action:'advance'});await click({action:'advance'});
 assert.equal(read('state.characterBuildViews.founder.affinities.light'),1);
 await click({skillTrain:'scholarship'});await click({action:'advance'});await click({action:'advance'});
 await click({buildKind:'perk',buildTrain:'archive-synthesis'});await click({action:'advance'});await click({action:'advance'});
 assert(read('state.characterBuildViews.founder.perks.includes("archive-synthesis")'));
 assert(read('state.workContributionViews.founder["archive-focus"].some(row=>row.name==="Archive synthesis")'));
 assert(!element('#app').innerHTML.includes('undefined'));
 await click({action:'start-training-reset'});await click({action:'advance'});
 assert.equal(read('state.characterSheets.founder.availableAdvancement'),60);
 assert.equal(read('state.characterBuildViews.founder.perks.length'),0);
 await read('readState().then(result=>{state=result;render();})');
 assert.equal(read('state.characterBuildViews.founder.attributes.intelligence'),5);
 console.log('PASS: character development UI training, pause/resume, affinity prerequisites, perk effects, retraining and reload.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
