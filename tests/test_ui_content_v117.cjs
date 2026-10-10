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
 execFileSync(process.env.PYTHON||'python',['-c',"import json,sys\nfrom server import GameStore\nimport game as g,field_patrols as p,armoury as a,character_pool as pool,candidate_proposals as cp,character_builds as cb\ns=g.new_campaign('fresh');s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'};p.initialize(s);s['firstRealTest']['completedOn']={'dayNumber':1,'phase':'morning'};s['firstRealTest']['improvement']='signals'\ns['sharedFunds']=2000;s['provisions']['stock']=500;s['founderKnownPrinciples']+=list(g.PRINCIPLE_NAMES)\nfor key in s['materialInventory']:s['materialInventory'][key]=20\ncb.build(s,'founder')['attributes']['might']=6;s['characterSkills']['founder']['athletics']=2\ns['containment']['chambers']['echo-1']['status']='ready'\ns['fieldPreparations']={'expedition-warding':{'dayNumber':1,'phase':'morning'}}\nfor kind in ('stoneguard','dispel-ward'):\n g.apply_action(s,{'type':'inscribe-spell','characterId':'founder','formId':kind,'materials':['porous-clay','binding-thread']});s['spellbook'][-1]['status']='learned'\ng.apply_action(s,{'type':'prepare-spells','characterId':'founder','spellIds':[x['id'] for x in s['spellbook'][-2:]]})\nfor key in ('steel-sword','leather-coat'):\n it=a.make(s,key,'founder');a.put_in(s,'founder',it['id'],'expedition')\nselection=pool.select(s,'v117ui',{'ancestry':'Ogrekin'});candidate=cp.approved_definition(pool.offline(s,selection,'v117ui'),'road-recruit','offline','v117ui');s['reviewedCandidates']['road-recruit']=candidate\nstore=GameStore(sys.argv[1],start_type='fresh')\nwith store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))\n",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=a=>value('commit('+JSON.stringify(a)+')');

 assert.equal(value('APP_VERSION'),'0.117');
 assert.match(value('lastingRitualsPanel()'),/Ready for the next field patrol/);
 assert.match(value('magicReferencePage()'),/36 castle spells/);
 await act({type:'watch-depart',bountyId:'runebound-colossus',participants:['founder']});await act({type:'advance'});
 await click({view:'fieldPatrols'});let html=element('#app').innerHTML;
 assert.match(html,/active ward plates/);assert.match(html,/Disconnect/);assert.match(html,/Creature rules and available counters/);assert.doesNotMatch(html,/undefined|NaN/);
 assert.match(value('bountyPage()'),/Difficult challenge/);
 assert.match(html,/Stoneguard/);assert.match(html,/Dispel ward/);assert.match(html,/Expedition warding/);
 const protection=value('state.fieldPatrolView.active.choices.find(r=>r.spellKind==="stoneguard")');
 await act({type:'watch-method',methodId:protection.id});await act({type:'advance'});
 assert.match(element('#app').innerHTML,/Stoneguard \+3 cover for 2 further exchanges/);
 assert.equal(value('state.fieldPreparations["expedition-warding"]'),undefined);
 assert.match(value('armouryPage()'),/Basilisk mirror brooch/);assert.match(value('armouryPage()'),/Regeneration|Restores 1 vitality/);
 await act({type:'watch-retreat'});await act({type:'advance'});
 await act({type:'recruit-lead',characterId:'road-recruit',questKind:'capture'});
 await click({view:'fieldPatrols'});assert.match(element('#app').innerHTML,/recruit-party-road-recruit/);assert.match(element('#app').innerHTML,/bandits\/ogrekin.webp/);
 await events.submit({preventDefault(){},target:{id:'recruit-party-road-recruit',fields:{characterId:'road-recruit','recruiter-founder':'on'}}});
 assert.equal(value('state.fieldPatrolView.active.recruitmentId'),'road-recruit');await act({type:'advance'});
 assert.match(element('#app').innerHTML,/Reduce the bandits to half vitality/);
 for(let n=0;n<3;n++){await act({type:'watch-method',methodId:'founder:guard'});await act({type:'advance'});}
 await act({type:'watch-method',methodId:'founder:capture-bandit'});await act({type:'advance'});await act({type:'advance'});
 await click({view:'containment'});assert.match(element('#app').innerHTML,/Captured bandits/);assert.match(element('#app').innerHTML,/Hear her account/);assert.match(element('#app').innerHTML,/Release her from custody/);
 for(const [topic,choice] of [['account','verify'],['restitution','fair'],['future','listen']]){await act({type:'recruit-talk',characterId:'road-recruit',topic,choice});await act({type:'advance'});}
 await act({type:'recruit-release',characterId:'road-recruit'});assert.match(element('#app').innerHTML,/Offer a household introduction/);
 await act({type:'recruit-invite',characterId:'road-recruit'});assert.equal(value('state.residency["road-recruit"].residencyStatus'),'remote');
 assert.equal(value('state.containmentView.occupiedCapacity'),0);
 await click({summoningCandidate:'road-recruit'});assert.match(element('#app').innerHTML,/Established contact/);assert.doesNotMatch(element('#app').innerHTML,/undefined|NaN/);
 console.log('PASS: real creature conditions and counters, rare equipment descriptions, bandit art, party form submission, capture, dungeon choices, release and optional invitation. Headless connected UI.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(error=>{console.error(error);process.exitCode=1;});
