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
const bridge = `import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nsys.path.insert(0,'tests')\nfrom test_candidate_proposals import candidate_fixture\nimport character_pool as pool\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1])\nurl=urlsplit(sys.argv[2])\npayload=json.load(sys.stdin)\ntry:\n if url.path=='/api/provider':\n  settings=ProviderSettings(sys.argv[1])\n  result=settings.save(payload) if payload else settings.public()\n elif url.path=='/api/dialogue/drafts':\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  with store.connect() as db:\n   result={'drafts':[json.loads(row[0]) for row in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC LIMIT 8')]}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept','/api/candidate/review'):\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  service=DialogueService(ProviderSettings(sys.argv[1]),lambda settings,messages:{'text':json.dumps(candidate_fixture(name='<svg/onload=alert(1)>',**{k:v for k,v in pool.offline(store.read(),pool.select(store.read(),payload['requestId'],payload.get('poolChoices',{})),payload['requestId']).items() if k in ('occupation','ancestryLabel','adultAgeYears','capabilityPackageId')})) if 'Propose one fictional adult woman' in messages[0]['content'] else json.dumps({'formId':'warm-twist','name':'<Cord suggestion>','explanation':'Bind plant fibres into cord.','limitations':['No powers beyond the listed effect.']}) if 'Suggest a bounded spell construction' in messages[0]['content'] else 'A generated <reply> with quiet wit.','usage':{'total_tokens':17}})\n  result=service.review_candidate(store,payload) if url.path.endswith('/review') else service.generate(store,payload) if url.path.endswith('/draft') else public_state(service.accept(store,payload))\n elif url.path=='/api/campaigns':\n  result=library.create(payload) if payload else {'campaigns':library.list()}\n else:\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:\n print(json.dumps({'error':str(error)}))`;
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

const fixture=`import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings\nimport game as g\ns=g.new_campaign();s['testing']['enabled']=True;s['sharedFunds']=100\nfor m in ('porous-clay','binding-thread'):s['materialInventory'][m]=5\ng.learn_for_character(s,'founder','courteous-passage')\ns['housingRooms']['garden-chamber']['status']='complete'\nstore=CampaignLibrary(sys.argv[1]).get('default')\nwith store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))\nProviderSettings(sys.argv[1]).save({'enabled':True,'model':'test/model','apiKey':'fixture','maxOutputTokens':1000})`;
(async()=>{try {
 execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
 await click({view:'candidateReview'});
 element('#candidate-brief').value='An adult vampire artisan.';
 await click({candidateDraft:'new'});
 assert.equal(vm.runInContext('candidateProposal.status',context),'ready');
 assert.match(element('#app').innerHTML,/&lt;svg\/onload=alert\(1\)&gt;/);
 assert(!element('#app').innerHTML.includes('<svg/onload'));
 await click({candidateDraft:'approve'});
 assert.equal(vm.runInContext('Object.keys(state.reviewedCandidates).length',context),0);
 await click({action:'advance'});
 await click({candidateDraft:'recheck'});
 assert.equal(vm.runInContext('candidateProposal.baseRevision===state.revision',context),true);
 element('#candidate-content-reviewed').checked=true;element('#candidate-mechanics-reviewed').checked=true;
 await click({candidateDraft:'approve'});
 const who=vm.runInContext('selectedSummoningPerson',context);
 assert.match(who,/^summoned-/);
 assert.equal(vm.runInContext('Object.keys(state.people).length',context),3);
 assert.match(element('#app').innerHTML,/visitor-placeholder.svg/);
 await events.submit({preventDefault(){},target:{id:'summoning-form',fields:{candidateId:who,conductorId:'founder',component0:'porous-clay',component1:'binding-thread'}}});
 await click({action:'advance'});await click({action:'advance'});
 const cid=vm.runInContext(`Object.entries(state.summoningContacts).find(([,c])=>c.personId==='${who}')[0]`,context);
 for(const topic of ['intentions','home','visit'])await click({summoningAction:'summoning-talk',contactId:cid,topic});
 await click({summoningAction:'summoning-invite',contactId:cid,visitRoom:'garden-chamber'});await click({action:'advance'});
 await click({summoningAction:'summoning-ask-stay',contactId:cid});await click({summoningAction:'summoning-household-decision',contactId:cid,stayDecision:'invite-to-stay'});
 for(const page of ['development','focus','spells','household','housing','ledger','workroom','review','summoning']) {
   vm.runInContext(`selectedCharacterId='${who}';setView('${page}')`,context);
   const html=element('#app').innerHTML;
   assert(!html.includes('undefined'),page+' missing data');
   assert(!html.includes('<svg/onload'),page+' unescaped name');
   assert(!html.includes('<b>glassworker</b>'),page+' unescaped occupation');
 }
 element('#dialogue-message').value='Hello there.';await vm.runInContext('requestDialogue()',context);
 assert.equal(vm.runInContext('dialogueDraft.characterId',context),who);
 await vm.runInContext('acceptDialogue()',context);
 await click({candidatePortrait:who});assert.equal(vm.runInContext('reviewAssetId',context),who);
 await click({summoningCandidate:who});await click({summoningAction:'summoning-depart',contactId:cid});await click({action:'advance'});
 assert.match(element('#app').innerHTML,/Remembered conversations/);
 await vm.runInContext('readState().then(result=>{state=result;render();})',context);
 assert.equal(vm.runInContext(`state.residency['${who}'].residencyStatus`,context),'away');
 console.log('PASS: candidate proposal review/recheck, explicit approval, funded contact, generated identity escaping, membership, scoped dialogue, portrait review and departure/reload.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
