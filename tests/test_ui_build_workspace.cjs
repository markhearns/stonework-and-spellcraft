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
 execFileSync(process.env.PYTHON||'python',['-c',"import sys,json,sqlite3\nfrom server import GameStore\nimport game,personal_paths,armoury\nsys.path.insert(0,'tests')\nfrom test_household_chapters import HouseholdChapterTests\nt=HouseholdChapterTests();t.s=game.new_campaign()\nfor who in personal_paths.PEOPLE:\n if who not in ('founder','mira'):t.member(who)\n t.s['bedroomAssignments'][who]='bedchamber'\n personal_paths.ensure(t.s,who)['learned']=[k for k,d in personal_paths.CATALOG.items() if d['who']==who]\narmoury.sync(t.s)\nt.s['headquarters']['rooms']['training-yard']='complete'\nst=GameStore(sys.argv[1])\nwith sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))",directory]);
 vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 const value=expr=>vm.runInContext(expr,context);
 const click=dataset=>events.click({preventDefault(){},target:{closest(){return {dataset,disabled:false};}}});
 const act=action=>click({pathAction:JSON.stringify(action)});
 const markup=[];
 for(const who of value('Object.keys(state.personalPathsView)')){
  value(`selectedCharacterId='${who}';uiCharacterTab='development';currentView='characterProfile';buildUi('${who}').page='loadout';render()`);
  const all=value('developmentPage(true)');assert.doesNotMatch(all,/undefined|src="null"/);assert.match(all,/aria-controls="build-pane-loadout"/);assert.equal((all.match(/class="build-talent-detail"/g)||[]).length,1);assert.equal((all.match(/data-build-talent=/g)||[]).length,3);assert.doesNotMatch(all,/romance-overview/);
  markup.push({who,html:all});
  const branches=value(`state.personalPathsView.${who}.options.filter(d=>!d.requires).map(d=>d.branch)`);
  for(const branch of branches){await click({buildPage:'paths'});await click({buildBranch:branch});assert.equal(value(`buildUi('${who}').branch`),branch);assert.equal((value(`personalPathsPanel('${who}')`).match(/data-build-talent=/g)||[]).length,3);}
  await click({buildPage:'training'});assert.equal(value(`buildUi('${who}').page`),'training');assert.match(value('developmentPage(true)'),/How attributes & expertise work/);
 }
 // Source-level DOM structure checks use a parser, not screenshots or a browser renderer.
 const parse="import sys,json\nfrom lxml import html\nrows=json.load(sys.stdin)\nfor r in rows:\n doc=html.fromstring('<main>'+r['html']+'</main>')\n panes=doc.xpath('./section[starts-with(@id,\"build-pane-\")]')\n assert len(panes)==3,(r['who'],len(panes))\n assert not panes[0].get('hidden') is not None,r['who']\n assert all(p.get('hidden') is not None for p in panes[1:]),r['who']\n ids=doc.xpath('//@id');assert len(ids)==len(set(ids)),(r['who'],'duplicate DOM ids')\nprint('DOM OK for '+str(len(rows))+' characters')";
 assert.match(execFileSync(process.env.PYTHON||'python',['-c',parse],{input:JSON.stringify(markup),encoding:'utf8',maxBuffer:32*1024*1024}),/DOM OK for 16/);
 value("selectedCharacterId='kaede';uiCharacterTab='development';buildUi('kaede').page='paths';buildUi('kaede').branch='breaker';render()");
 for(const talentId of ['measured-blow','settled-stance','steady-hands'])await act({type:'path-prepare',characterId:'kaede',talentId,prepared:true});
 await click({buildTalent:'gate-breaker'});await click({buildReplace:'gate-breaker'});assert.match(value("personalPathsPanel('kaede')"),/Replace which technique/);
 await act({type:'path-prepare',characterId:'kaede',talentId:'gate-breaker',prepared:true,replaceId:'measured-blow'});assert.deepEqual(Array.from(value('state.personalPathsView.kaede.techniques')),['gate-breaker','settled-stance','steady-hands']);
 await value("commit({type:'save-complete-preparation',characterId:'kaede',name:'Guard and guide'})");await act({type:'path-clear',characterId:'kaede'});await value("commit({type:'load-complete-preparation',characterId:'kaede',name:'Guard and guide'})");assert.equal(value('state.personalPathsView.kaede.techniques.length'),3);
 await click({buildPage:'training'});await click({buildDrill:'crossing'});await act({type:'path-drill',characterId:'kaede',scenario:'crossing'});const active=value('developmentPage(true)');assert.ok(active.indexOf('Current training')<active.indexOf('Build sections'));assert.match(active,/Rope crossing/);
 await value("commit({type:'advance'})");await value('readState().then(s=>{state=s;render();})');assert.equal(value('state.personalPathsView.kaede.lastDrill.name'),'Rope crossing');
 await click({uiCharacterTab:'preparation'});assert.equal(value('uiCharacterTab'),'development');assert.equal(value("buildUi('kaede').page"),'loadout');
 assert.equal(value('Object.keys(UI_CHAR_TABS).includes("preparation")'),false);
 await click({view:'archiveProject'});assert.equal(value('uiCharacterTab'),'quests');assert.equal(value('selectedCharacterId'),'mira');assert.match(element('#app').innerHTML,/An archive worth getting lost in/);
 await click({character:'iona',characterSection:'quests'});assert.equal(value('uiCharacterTab'),'quests');assert.equal(value('selectedCharacterId'),'iona');
 console.log('PASS: all 16 build workspaces and 48 branches; valid pane hierarchy, one selected talent, no duplicate ids; direct slot replacement, complete build save/load, persistent training strip and compatibility navigation.');
}finally{fs.rmSync(directory,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1;});
