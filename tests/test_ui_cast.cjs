// Focused new-cast connected UI regression.
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
const bridge = `import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings,DialogueService\nfrom game import public_state\nfrom urllib.parse import urlsplit,parse_qs\nlibrary=CampaignLibrary(sys.argv[1])\nurl=urlsplit(sys.argv[2])\npayload=json.load(sys.stdin)\ntry:\n if url.path=='/api/provider':\n  settings=ProviderSettings(sys.argv[1])\n  result=settings.save(payload) if payload else settings.public()\n elif url.path=='/api/dialogue/drafts':\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  with store.connect() as db:\n   result={'drafts':[json.loads(row[0]) for row in db.execute('SELECT result FROM dialogue_drafts ORDER BY rowid DESC LIMIT 8')]}\n elif url.path in ('/api/dialogue/draft','/api/dialogue/accept'):\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  service=DialogueService(ProviderSettings(sys.argv[1]),lambda settings,messages:{'text':json.dumps({'formId':'warm-twist','name':'<Cord suggestion>','explanation':'Bind plant fibres into cord.','limitations':['No powers beyond the listed effect.']}) if 'Suggest a bounded spell construction' in messages[0]['content'] else 'A generated <reply> with quiet wit.','usage':{'total_tokens':17}})\n  result=service.generate(store,payload) if url.path.endswith('/draft') else public_state(service.accept(store,payload))\n elif url.path=='/api/campaigns':\n  result=library.create(payload) if payload else {'campaigns':library.list()}\n else:\n  store=library.get(parse_qs(url.query).get('campaign',['default'])[0])\n  result=public_state(store.action(payload) if payload else store.read())\n print(json.dumps(result))\nexcept Exception as error:\n print(json.dumps({'error':str(error)}))`;
const context = vm.createContext({
  FormData:class {constructor(form){this.fields=form.fields;} get(name){return this.fields[name]??null;}},
  console, URLSearchParams, crypto:require('node:crypto').webcrypto,
  setTimeout(){return 0;},clearTimeout(){},
  document:{querySelector(selector){return selector==='.dialogue-history'?null:element(selector);},body:element('body')},
  window:{scrollTo(){}},location:{reload(){}},
  fetch:async(url, options)=>{
    const body = options?.body || '{}';
    const json=JSON.parse(execFileSync(process.env.PYTHON || 'python', ['-c',bridge,directory,url], {input:body, encoding:'utf8',maxBuffer:8*1024*1024}));
    if(url==='/api/campaigns' && options?.method==='POST' && dropCreationResponse) {dropCreationResponse=false;throw new Error('Simulated lost response');}
    return {ok:!json.error,async json(){return json;}};
  }
});

const fixture=`import json,sys\nfrom server import CampaignLibrary\nfrom dialogue import ProviderSettings\nimport game as g\ns=g.new_campaign();s['sharedFunds']=300\nfor m in ('porous-clay','binding-thread'):s['materialInventory'][m]=20\ng.learn_for_character(s,'founder','courteous-passage')\nfor room in ('west-chamber','garden-chamber'):s['housingRooms'][room]['status']='complete'\nfor who,room in [('iona','garden-chamber'),('aurelia','west-chamber'),('neris','garden-chamber')]:\n g.apply_action(s,{'type':'summoning-prepare','candidateId':who,'conductorId':'founder','materials':['porous-clay','binding-thread']})\n for _ in range(2):g.apply_action(s,{'type':'advance'})\n cid='threshold-'+str(s['nextSummoningContactNumber']-1)\n for topic in ('intentions','home','visit'):g.apply_action(s,{'type':'summoning-talk','contactId':cid,'topic':topic})\n g.apply_action(s,{'type':'summoning-invite','contactId':cid,'roomId':room});g.apply_action(s,{'type':'advance'})\n g.apply_action(s,{'type':'summoning-ask-stay','contactId':cid});g.apply_action(s,{'type':'summoning-household-decision','contactId':cid,'decision':'invite-to-stay'})\nstore=CampaignLibrary(sys.argv[1]).get('default')\nwith store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))\nProviderSettings(sys.argv[1]).save({'enabled':True,'model':'test/model','apiKey':'fixture','maxOutputTokens':200})`;
(async()=>{try{
  execFileSync(process.env.PYTHON||'python',['-c',fixture,directory]);
  vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);
  await new Promise(resolve=>setImmediate(resolve));
  const click=dataset=>events.click({target:{closest(){return {dataset,disabled:false};}}});
  for(const who of ['iona','aurelia','neris']) {
    await click({summoningCandidate:who});
    assert.equal(vm.runInContext('dialogueCharacter()',context),who);
    assert(!element('#app').innerHTML.includes('undefined'));
    assert.equal((element('#app').innerHTML.match(/id="dialogue-message"/g)||[]).length,1);
    const cid=vm.runInContext(`Object.entries(state.summoningContacts).find(([,c])=>c.personId==='${who}')[0]`,context);
    await click({summoningAction:'summoning-personal-talk',contactId:cid,topic:'flirt'});
    element('#dialogue-message').value='Stay a little?';
    await vm.runInContext('requestDialogue()',context);
    assert.equal(vm.runInContext('dialogueDraft.characterId',context),who);
    await vm.runInContext('acceptDialogue()',context);
    assert.equal(vm.runInContext(`state.additionalResidents.${who}.conversation.at(-1).source`,context),'generated');

    if(who!=='iona') {
      await click({view:'stores'});await click({buy:'fireglass'});
      await click({companionOpen:who,companionSection:'project'});
      assert.match(element('#app').innerHTML,/Agree & fund her study/);
      await click({companionAction:'start-companion-project',companionOwner:who});
      for(let i=0;i<3;i++)await click({action:'advance'});
      assert.equal(vm.runInContext(`state.companionLifeViews.${who}.project.status`,context),'complete');
      await click({companionOpen:who,companionSection:'wardrobe'});
      await click({companionAction:'choose-companion-ensemble',companionOwner:who,ensembleId:'evening'});
      assert.match(element('#app').innerHTML,new RegExp(who+'.webp'));
      await events.submit({preventDefault(){},target:{id:'companion-style-form',fields:{characterId:who,name:'Evening '+who}}});
      assert.match(element('#app').innerHTML,/Wear saved style/);
      await click({companionAction:'choose-companion-ensemble',companionOwner:who,ensembleId:'working'});
      await click({companionAction:'load-companion-style',companionOwner:who,styleName:'Evening '+who});
      await click({companionOpen:who,companionSection:'moments'});
      const moment=who==='aurelia'?'aurelia-lamplit':'neris-glasslight';
      await click({residentMoment:moment,momentAction:'join-resident-moment'});
      assert.match(element('#app').innerHTML,/moment-illustration/);
      assert.match(element('#app').innerHTML,new RegExp(who+'.webp'));
      await vm.runInContext('readState().then(result=>{state=result;render();})',context);
      assert.equal(vm.runInContext(`state.companionLifeViews.${who}.ensembleId`,context),'evening');
      const room=vm.runInContext(`Object.entries(state.roomOccupants).find(([,ids])=>ids.includes('${who}'))[0]`,context);
      await click({room});
      assert.match(element('#app').innerHTML,new RegExp('data-companion-open="'+who+'"'));
    }
    for(const page of ['development','focus','spells','household','ledger','housing','workroom','review']) {
      vm.runInContext(`selectedCharacterId='${who}';setView('${page}')`,context);
      assert(!element('#app').innerHTML.includes('undefined'),who+' '+page);
    }
    await click({summoningPerson:who,view:'summoning'});
    assert.equal(vm.runInContext('selectedSummoningPerson',context),who);
    await click({summoningAction:'summoning-depart',contactId:cid});
    await click({action:'advance'});
    assert.match(element('#app').innerHTML,/Remembered conversations/);
    assert(!element('#app').innerHTML.includes('id="summoned-message-form"'));
  }
  console.log('PASS: three-candidate routing, unique conversation forms, scoped generated replies, five-person household views, funded projects, saved styles, illustrated moments, room shortcuts, departure and remembered history.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
