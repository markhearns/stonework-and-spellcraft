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
    if(json.error)console.error(url,json.error);return {ok:!json.error,async json(){return json;}};
  }
});



(async()=>{try {
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=a=>value('commit('+JSON.stringify(a)+')');
 assert.equal(value('APP_VERSION'),'0.118');
 await act({type:'cheat-toggle',enabled:true});await act({type:'cheat-recruit',characterId:'koharu'});
 await act({type:'cheat-build',buildingId:'garden-chamber'});
 await act({type:'choose-bedroom',characterId:'koharu',roomId:'garden-chamber'});
 await click({uiPerson:'koharu'});
 assert.match(element('#app').innerHTML,/Accommodation/);assert.match(element('#app').innerHTML,/Garden chamber/);
 assert.match(element('#app').innerHTML,/Living quarters/);assert.match(element('#app').innerHTML,/Foxlike agility/);assert.doesNotMatch(element('#app').innerHTML,/Maren|Bovinefolk|undefined|NaN/);
 const map=value('castleMapRoom(castleMapRooms().find(r=>r.id==="garden-chamber"))');
 assert.match(map,/Assigned beds: Koharu/);
 assert.match(value('castleMapRoom(castleMapRooms().find(r=>r.id==="living-quarters"))'),/Koharu/);
 await click({castleMapRoom:'garden-chamber'});assert.equal(value('currentView'),'room');assert.equal(value('state.selectedRoomId'),'garden-chamber');
 await act({type:'choose-bedroom',characterId:'koharu',roomId:'bedchamber'});
 assert.doesNotMatch(value('castleMapRoom(castleMapRooms().find(r=>r.id==="garden-chamber"))'),/Assigned beds: Koharu/);
 await value('readState().then(s=>{state=s;render()})');assert.match(value('characterHousingPanel("koharu")'),/Guest chamber/);
 // Build a real offline contact in the same store; no enabled provider.
 const setup=`import sys,json,uuid
from server import GameStore
from dialogue import DialogueService,ProviderSettings
import game as g
store=GameStore(sys.argv[1]);svc=DialogueService(ProviderSettings(sys.argv[1]))
d=svc.generate(store,dict(requestId=uuid.uuid4().hex,expectedRevision=store.read()['revision'],purpose='candidate-proposal',source='offline',poolChoices=dict(ancestry='Human',background='mapmaker',temperament='quiet'),text='A visitor from the selected traits.'))
assert d['status']=='ready',d
s=svc.accept(store,dict(draftId=d['id'],contentReviewed=True,mechanicsReviewed=True));who='summoned-'+d['id']
import sys;sys.path.insert(0,'tests')
from recruitment_fixture import rescue_and_invite
rescue_and_invite(s,who);cid='introduced-'+who
for topic in ('intentions','home','visit'):g.apply_action(s,dict(type='summoning-talk',contactId=cid,topic=topic))
s['housingRooms']['west-chamber']['status']='complete'
g.apply_action(s,dict(type='summoning-invite',contactId=cid,roomId='west-chamber'));g.apply_action(s,dict(type='advance'))
with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
print(who)`;
 const who=execFileSync(process.env.PYTHON||'python3',['-c',setup,directory],{encoding:'utf8'}).trim();
 await value('readState().then(s=>{state=s;render()})');await click({summoningCandidate:who});
 assert.match(element('#app').innerHTML,/Her own plans &amp; interests|Her own plans & interests/);
 assert.match(element('#app').innerHTML,/A map that admits uncertainty/);
 const phase=value('state.dayNumber+":"+state.currentDayPhase'),funds=value('state.sharedFunds');
 await click({scriptedCompanion:who,topicId:'craft',choiceId:'0'});
 assert.match(element('#app').innerHTML,/solid line for a walked route/);assert.equal(value('state.sharedFunds'),funds);assert.equal(value('state.dayNumber+":"+state.currentDayPhase'),phase);
 await value('readState().then(s=>{state=s;render()})');assert.match(element('#app').innerHTML,/solid line for a walked route/);
 await click({helpTopic:'scripted-solo'});assert.match(element('#app').innerHTML,/No\. Chapters/);
 await click({view:'journal'});element('#journal-draft-brief').value='Summarize the last phase.';await value('requestDialogue()');
 assert.equal(value('dialogueDraft.status'),'ready');assert.equal(value('dialogueDraft.source'),'offline');
 await value('acceptDialogue()');assert.equal(value('state.journal.at(-1).source'),'scripted');
 console.log('PASS: live bedroom moves and reload, profile/quarters/map occupancy, ancestry UI, provider-free created visitor, three-way dialogue response and persistence, Help and scripted journal account.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
