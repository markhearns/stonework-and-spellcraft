/* Optional rendered review. Requires Node, Python and Playwright Chromium.
   Run from the project: node scripts/browser_review.cjs [output-directory]
   Uses temporary fresh saves and localhost only. Never uses your data directory.
   Passing these checks does not substitute for inspecting the screenshots. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
const output=path.resolve(process.argv[2]||path.join(root,'browser-review'));
fs.mkdirSync(output,{recursive:true});
const reports=[];
async function server(directory,scenario){
 const code="import sys\nfrom server import GameStore,create_server\nGameStore(sys.argv[1],start_type='fresh')\nif sys.argv[2]=='established':\n import json,sqlite3\n sys.path.insert(0,'tests')\n from test_party_journeys import PartyJourneyTests\n import test_magic_overhaul as magic\n t=PartyJourneyTests();t.setUp();t.maxed();magic.MagicTests.learned(t,'borrowed-hour');magic.MagicTests.learned(t,'water-walk','mira')\n with sqlite3.connect(GameStore(sys.argv[1]).database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(t.s),))\ns=create_server('127.0.0.1',0,sys.argv[1])\nprint(s.server_port,flush=True)\ns.serve_forever()";
 const child=spawn(process.env.PYTHON||'python',['-u','-c',code,directory,scenario],{cwd:root});
 let errors='';child.stderr.on('data',x=>errors+=x);
 try{
  const port=await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(Error('Test server startup timed out: '+errors)),15000);
   child.once('error',e=>{clearTimeout(timer);reject(e);});
   child.once('exit',()=>{clearTimeout(timer);reject(Error('Test server exited: '+errors));});
   child.stdout.once('data',x=>{clearTimeout(timer);resolve(Number(String(x).trim()));});
  });
  if(!port)throw Error('Invalid test server port');
  return {child,url:'http://127.0.0.1:'+port+'/?campaign=default'};
 }catch(e){child.kill();throw e;}
}
async function main(){
 const browser=await chromium.launch({headless:true});
 try{for(const viewport of [{width:1440,height:1000},{width:390,height:844},{width:320,height:740}]){for(const scenario of ['fresh','established']){
  const directory=fs.mkdtempSync(path.join(os.tmpdir(),'stonework-render-'));
  let srv,context;
  const report={viewport,scenario,screens:[],errors:[],keyboard:[]};reports.push(report);
  try{
   srv=await server(directory,scenario);
   context=await browser.newContext({viewport,isMobile:viewport.width<600,hasTouch:viewport.width<600});
   const page=await context.newPage();
   page.on('pageerror',e=>report.errors.push(e.message));
   page.on('response',r=>{if(r.status()>=400)report.errors.push(r.status()+' '+r.url());});
   page.setDefaultTimeout(15000);
   const click=async selector=>{
    await page.locator(selector).first().click();
    await page.waitForFunction(()=>typeof busy==='undefined'||!busy);
    // Phase result dialogs are deliberately explicit; Escape is a real keyboard dismissal.
    while(await page.locator('dialog[open]').count())await page.keyboard.press('Escape');
   };
   const capture=async name=>{
    await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].filter(i=>i.loading!=='lazy').map(i=>i.decode().catch(()=>{})));});
    const metrics=await page.evaluate(()=>({
     overflow:document.documentElement.scrollWidth>innerWidth+1,
     brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),
     smallTargets:[...document.querySelectorAll('button,a,input,select,summary')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&(r.height<24||r.width<24);}).map(e=>(e.textContent||e.getAttribute('aria-label')||e.tagName).trim().slice(0,80))
    }));
    const file=viewport.width+'-'+scenario+'-'+name+'.png';await page.screenshot({path:path.join(output,file),fullPage:true});
    report.screens.push({name,file,...metrics});
    if(metrics.overflow)report.errors.push(name+': horizontal page overflow');
    if(metrics.brokenImages.length)report.errors.push(name+': broken images');
   };
   const navigate=async view=>{
    const toggle=page.locator('[data-navigation-toggle]');
    if(await toggle.isVisible()&&await toggle.getAttribute('aria-expanded')==='false')await click('[data-navigation-toggle]');
    const primary=page.locator('#main-navigation > button[data-view="'+view+'"]');
    if(await primary.count()){await primary.click();return;}
    const screens=page.locator('details[data-ui-key="all-screens"]');
    if(await screens.getAttribute('open')===null)await screens.locator('summary').click();
    await page.locator('#direct-navigation').selectOption(view);
   };
   await page.goto(srv.url);
   if(scenario==='fresh'){await page.locator('#founder-profile-form').waitFor();await capture('character');
   await page.locator('#founder-name').fill('Rowan the Patient');await page.locator('#founder-age').fill('36');
   await click('#founder-profile-form button[type="submit"], #founder-profile-form button.primary');
   await click('[data-setup-continue]');await capture('arrival');
   await click('[data-arrival-choice]');await click('[data-arrival-choice]');await capture('orientation');
   await click('[data-arrival-enter="begin"]');await capture('home');
   await click('[data-opening-review]');await click('[data-action="start-research"]');
   for(let i=0;i<3;i++)await click('[data-action="advance"]');
   await navigate('workshop');await capture('first-craft');await click('[data-solo-craft]');
   for(let i=0;i<2;i++)await click('[data-action="advance"]');
   await navigate('castle');await capture('first-lantern-home');
   for(const view of ['headquarters','expeditions','castleChapter','householdWork','livingStories','specialists','progression','phaseTasks','stores']){await navigate(view);await capture(view);}
   await navigate('headquarters');await click('[data-hq-room="library"]');await capture('library');
   await click('[data-room-work="castleChapter"]');await capture('library-notebook');
   }else{
    await page.locator('[data-ui-key="activity"]').waitFor();await capture('home');
    await navigate('peopleHub');await click('[data-ui-person="mira"]');await capture('companion');
    await click('[data-ui-character-tab="style"]');
    await click('details[data-ui-key="appearance"] > summary');
    const hair=page.locator('#personal-appearance-form input[name="hairColour"]');
    await hair.fill('A draft kept while browsing');
    await click('[data-ui-character-tab="talk"]');await capture('conversation');
    await click('[data-ui-character-tab="style"]');
    if(await hair.inputValue()!=='A draft kept while browsing')report.errors.push('Appearance draft lost on tab change');
    await capture('appearance-draft');
    await navigate('storyJournal');await page.locator('#ui-journal-search').fill('Mira');
    if(!await page.locator('#ui-journal-search').evaluate(e=>e===document.activeElement))report.errors.push('Journal typing lost focus');
    await capture('journal-search');
    await navigate('magicHub');await navigate('spells');await page.locator('#ui-magic-state').selectOption('prepared');await capture('prepared-spells');
    await navigate('expeditions');await click('[data-site="flooded-monastery"]');await capture('departure');
    await click('[data-action="start-expedition"]');await click('[data-action="advance"]');await click('[data-approach="survey"]');await capture('field-decision');
    await click('[data-encounter-method="patient"]');await click('[data-action="advance"]');await capture('ordinary-fieldwork');
    await click('[data-action="return-expedition"]');await click('[data-action="advance"]');await capture('returned-home');
   }
   await page.keyboard.press('Tab');report.keyboard.push(await page.evaluate(()=>({tag:document.activeElement.tagName,text:document.activeElement.textContent?.trim().slice(0,120)})));
   const before=await page.evaluate(()=>({revision:state.revision,day:state.dayNumber,lantern:state.craftedArtifacts['warming-lantern']}));
   await page.reload();await page.waitForFunction(()=>typeof state!=='undefined'&&state?.revision>=0);
   const after=await page.evaluate(()=>({revision:state.revision,day:state.dayNumber,lantern:state.craftedArtifacts['warming-lantern']}));
   if(JSON.stringify(before)!==JSON.stringify(after))report.errors.push('Reload changed saved progression');
   await capture('reload');
  }catch(e){report.errors.push(e.stack||String(e));}
  finally{if(context)await context.close();if(srv){srv.child.kill();await new Promise(resolve=>srv.child.exitCode!==null?resolve():srv.child.once('exit',resolve));}fs.rmSync(directory,{recursive:true,force:true});}
 }}}finally{await browser.close();fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({rendered:true,manualScreenshotReviewRequired:true,reports},null,2));}
 if(reports.some(r=>r.errors.length))throw Error('Rendered review found issues; inspect report.json and screenshots.');
 console.log('Rendered checks complete. Inspect screenshots, small-target reports, focus visibility and touch behavior before visual sign-off.');
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
