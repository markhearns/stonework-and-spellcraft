"""One durable field-party state machine shared by repeatable patrols and Chapter 8.

Choices never advance time; committed exchanges resolve on Advance. No timers,
permanent injuries, item loss, extra food ledger, or free repeat advancement.
"""
from copy import deepcopy
import random
import secrets

import bestiary
import bounty_contracts

ENEMIES=bestiary.ENCOUNTERS
ROUTES=bestiary.ROUTES
MISSIONS={
 'scout':dict(name='Trace the missing delivery',enemies=['thief','wolf'],art='patrol-road'),
 'escort':dict(name='Reopen the supply route',enemies=['bandit','thief'],art='patrol-road'),
 'defend':dict(name='Hold the castle approach',enemies=['bandit','bandit'],art='patrol-road')}
PLANS={'scout':'Mark a sheltered detour: one safe bypass on the escort outing; no reward for the bypassed encounter.', 'negotiate':'Carry a settlement offer: negotiate with the escort bandits without a skill threshold.', 'confront':'Intercept the raiders: +1 damage during the escort outing.'}
IMPROVEMENTS={'signals':'Linked watch signals: +1 party cover on future field patrols.', 'supplies':'Recovery stores: +4 provisions on each fully completed field patrol.', 'contracts':'Road contracts: +2 crowns on each fully completed field patrol.'}

def saved(s):return s.get('fieldPatrols',{'serial':0,'active':None,'reports':[]})
def chapter(s):return s.get('firstRealTest',{'started':False,'completed':[],'lastReturn':None,'lastParty':[],'plan':None,'watchId':None,'completedOn':None,'improvement':None,'memories':[]})
def initialize(s):
 s.setdefault('fieldPatrols',deepcopy(saved(s)));s.setdefault('firstRealTest',deepcopy(chapter(s)))
def unlocked(s):return bool(s.get('firstPatrol',{}).get('completedOn'))
def away(s,who):return bool(saved(s)['active'] and who in saved(s)['active']['party'])
def require(s,condition,message):
 import game as g
 g.require(condition,message)
def member_blockers(s,who):
 import game as g,solo_life,field_magic as f
 b=[]
 if who not in g.household_members(s):return ['Choose a household member.']
 if not g.character_at_castle(s,who):b.append('Return home first.')
 if who!='founder' and not solo_life.offered(s,who,'fieldwork'):b.append('Agree fieldwork first (Mira needs her archive story).')
 if f.vitality(s,who)<3:b.append('Rest to at least 3 vitality before departure.')
 return b

def night_blockers(s):
 c=chapter(s)
 return [] if c['lastReturn'] is None else ['The last story party must sleep at home after returning.'] if any(s.get('overnightRest',{}).get(w,0)<=c['lastReturn'] for w in c['lastParty']) else []
def story_blockers(s,mission):
 import game as g,headquarters as h
 c=chapter(s);b=[]
 if not unlocked(s):b.append('Conclude Chapter 7 first.')
 if not c['started']:b.append('Read the missing-delivery report first.')
 if mission not in MISSIONS:return b+['Choose a story outing.']
 expected=next((k for k in MISSIONS if k not in c['completed']),None)
 if expected!=mission:b.append('Complete the story outings in order; finished outings cannot be farmed.')
 if mission!='scout':
  b+=night_blockers(s)
  if not c['plan']:b.append('Agree a route plan after the scouting outing.')
  if not h.ready(s,'guard-barracks') or not h.ready(s,'training-yard'):b.append('Restore the barracks and training yard.')
 if mission=='defend' and not h.ready(s,'watchtower'):b.append('Restore the watchtower.')
 return b

def equipment(s,who):
 import armoury as a
 tags=set()
 for key in set(a.loadout(s,who,'expedition')['slots'].values()):
  it=a.state(s)['items'].get(key)
  if it and it['ownerId']==who and it['location']=='armoury' and not a.busy(s,key):tags.update(a.CATALOG[it['definitionId']]['tags'])
 return tags

def equipment_bonuses(s,who):
 """Equipment-only patrol values shared by action and equipment previews."""
 import armoury as a
 tags=equipment(s,who)
 force=min(2,max((e['rank'] for e in a.effects(s,who,'expedition') if e['effect']=='measured-force'),default=0))
 return {'damage':int('weapon' in tags)+force,
         'cover':int(bool(tags & {'shield','protection'}))+int(a.has(s,who,'warded-cover','expedition'))}

def cover(s,party):
 import armoury as a,headquarters as h,resident_specialties as rs
 active=saved(s)['active'];bonus=int(len(party)>1)+int(chapter(s)['improvement']=='signals')
 sources=[]
 if s['headquarters']['stock'].get('warded-watch-network'):bonus+=1;sources.append('Warded watch network +1')
 if len(party)>1:sources.append('Companion cover +1')
 if chapter(s)['improvement']=='signals':sources.append('Linked signals +1')
 if 'rhess' in party and rs.active(s,'rhess'):bonus+=1;sources.append('Rhess’s watchtower improvement +1')
 if active and active['mission']=='defend':
  for room,label in [('guard-barracks','Barracks'),('watchtower','Watchtower')]:
   if h.ready(s,room):bonus+=1;sources.append(label+' +1')
  watch=chapter(s)['watchId']
  if watch and watch not in party:
   import game as g
   if g.character_at_castle(s,watch) and g.character_assignment(s,watch)=='road-patrol':bonus+=1;sources.append('Home watch +1')
 return min(3,bonus),sources

def choices(s):
 import game as g,field_magic as f,character_approaches as apt,personal_paths as paths,armoury as a,patrol_tactics as tactics
 run=saved(s)['active']
 if not run or run['stage']!='decision':return []
 d=bestiary.encounter(s,run);party=[w for w in run['party'] if f.vitality(s,w)>0];shared,_=cover(s,party);rows=[]
 for who in party:
  tags=equipment(s,who);gear=equipment_bonuses(s,who);protect=gear['cover']
  skill=int(apt.score(s,who,apt.spec('might','athletics'),party)['qualified'])
  base=1+gear['damage']+skill+int(run['mission']=='escort' and chapter(s)['plan']=='confront')
  defence=protect+shared
  for key,label,hit,block in [('strike','Strike',base,defence),('guard','Guarded strike',max(1,base-1),defence+1)]:
   rows.append(dict(id=who+':'+key,who=who,name=label,damage=hit,block=block,cost=0,blockers=[],kind='attack'))
  req=apt.spec('charisma','diplomacy',9) if d['kind']=='human' else apt.spec('dexterity','fieldcraft',9)
  qualifies=apt.score(s,who,req,party)['qualified'] or (d['kind']=='human' and run['mission']=='escort' and chapter(s)['plan']=='negotiate')
  if d.get('roleId') or d.get('bestiaryId') in ('wolf','briarback-boar'):rows.append(dict(id=who+':peace',who=who,name='Negotiate a withdrawal' if d['kind']=='human' else 'Drive away without a fight',damage=0,block=99,cost=0,kind='peace',blockers=[] if qualifies else ['Needs approach score 9: '+req['attribute']+' + twice '+req['skill']+'.']))
  approach=d.get('approach')
  if approach and d.get('bestiaryId') not in ('wolf','briarback-boar'):
   req=apt.spec(approach['attribute'],approach['skill'],approach['threshold']);qualifies=apt.score(s,who,req,party)['qualified']
   rows.append(dict(id=who+':field-approach',who=who,name=approach['name'],damage=0,block=99,cost=0,kind='peace',blockers=[] if qualifies else ['Needs approach score '+str(approach['threshold'])+': '+req['attribute']+' + twice '+req['skill']+'.']))
  incoming=tactics.intent(s,run)
  if incoming and incoming['target']!=who and ('shield' in tags or set(paths.record(s,who)['techniques']) & tactics.PROTECT):
   rows.append(dict(id=who+':protect',who=who,name='Cover '+g.character_profile(s,incoming['target'])['name'],damage=1,block=defence+2,cost=0,kind='protect',blockers=[]))
  for key in paths.record(s,who)['techniques']:
   t=paths.CATALOG[key]
   if 'enemy' not in t['tags']:continue
   fx=paths.target_effect(s,who,key,d['enemy']);b=[]
   if who+':'+key in run['used']:b.append('Already used in this encounter.')
   if f.vitality(s,who)<=fx['cost']:b.append('Not enough vitality for the exertion cost.')
   if d['enemy'] in fx['immune']:b.append('This enemy is immune.')
   if t['advanced']:
    sig=a.state(s)['signatures'].get(who,{});it=a.state(s)['items'].get(sig.get('itemId'),{})
    if not sig.get('completedOn') or it.get('ownerId')!=who or it.get('location')!='armoury' or sig.get('itemId') not in a.loadout(s,who,'expedition')['slots'].values():b.append('Equip this character’s completed signature item.')
   rows.append(dict(id=who+':'+key,who=who,name=t['name'],damage=fx['damage']+fx.get('counter',0),block=fx['block']+defence,cost=fx['cost'],kind='technique',effects=fx,blockers=b))
  for spell in s['spellbook']:
   form=g.SPELL_FORMS[spell['formId']];kind=form.get('field')
   if spell['ownerId']!=who or spell['status']!='learned' or spell['id'] not in s['preparedSpells'].get(who,[]) or kind not in ('water','fire','ice','lightning','radiant','heal'):continue
   inputs=form['castingInputs'];b=[]
   if any(p not in g.character_principles(s,who) for p in form['requiredPrinciples']):b.append('Learn all required principles.')
   if any(s['materialInventory'].get(k,0)-s['materialReserveTargets'].get(k,0)<n for k,n in inputs.items()):b.append('Needs unreserved casting components: '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in inputs.items())+'.')
   rows.append(dict(id=who+':spell:'+spell['id'],who=who,name=form['name'],damage=0 if kind=='heal' else f.damage(kind,d),block=99 if kind=='ice' else defence,cost=0,kind='spell',spellId=spell['id'],spellKind=kind,inputs=deepcopy(inputs),blockers=b))
 if run['mission']=='escort' and chapter(s)['plan']=='scout' and not run['bypassUsed']:rows.append(dict(id='detour',who=party[0] if party else run['party'][0],name='Use the surveyed detour (no encounter reward)',kind='bypass',damage=0,block=99,cost=0,blockers=[]))
 import field_objectives
 rows.extend(field_objectives.combat_rows(s,run))
 return tactics.enrich(s,run,rows)

def remember(s,title,text):
 import game as g
 chapter(s)['memories'].append(dict(title=title,text=text,day=s['dayNumber']));g.add_journal(s,title+': '+text)

def apply(s,act):
 import game as g,armoury as a,field_magic as f
 kind=act.get('type','');initialize(s);r=saved(s);c=chapter(s)
 import patrol_homecoming
 if patrol_homecoming.apply(s,act):return
 require(s,unlocked(s),'Conclude Chapter 7 to unlock field patrols and Chapter 8.')
 import field_objectives as objectives
 if objectives.apply(s,act):
  if r['active']:bestiary.observe(s,r['active'])
  return
 if kind=='watch-depart':
  require(s,r['active'] is None,'Bring the active patrol home first.')
  require(s,g.character_at_castle(s,'founder'),'Return home before dispatching a patrol.')
  party=act.get('participants');route=act.get('routeId');mission=act.get('missionId')
  objective=act.get('objectiveId');bounty=act.get('bountyId')
  require(s,bounty is None or (isinstance(bounty,str) and bounty in bounty_contracts.CONTRACTS and objective is None and mission is None),'Choose one bounty, objective or story outing.')
  require(s,objective is None or (isinstance(objective,str) and objective in objectives.OBJECTIVES and mission is None),'Choose a listed objective without a Chapter 8 mission.')
  require(s,isinstance(party,list) and 1<=len(party)<=4 and all(isinstance(w,str) for w in party) and len(set(party))==len(party),'Choose one to four distinct household members.')
  b=[x for w in party for x in member_blockers(s,w)];require(s,not b,' '.join(b))
  if bounty is not None:
   b=bounty_contracts.blockers(s,bounty);require(s,not b,' '.join(b));d=bounty_contracts.CONTRACTS[bounty];enemies=[d['enemyId']];name=d['name'];route=d['route']
  elif objective is not None:
   d=objectives.OBJECTIVES[objective];enemies=[d['enemy']];name=d['name'];route=d['route']
  elif mission is not None:
   require(s,isinstance(mission,str) and mission in MISSIONS,'Choose an offered story outing.');b=story_blockers(s,mission);require(s,not b,' '.join(b));require(s,'founder' in party,'Bring your scholar on Chapter 8 story outings.');enemies=MISSIONS[mission]['enemies'][:];name=MISSIONS[mission]['name'];route='road'
  else:
   require(s,isinstance(route,str) and route in ROUTES,'Choose an offered patrol route.');d=ROUTES[route]
   r.setdefault('seed',secrets.token_hex(16));rng=random.Random(r['seed']+':'+str(r['serial']+1));enemies=rng.choices(d['pool'],weights=d['weights'],k=d['count']);name=d['name']
  ancestries=[rng.choice(bestiary.RAIDER_ANCESTRIES) if ENEMIES[key].get('roleId') else None for key in enemies] if bounty is None and objective is None and mission is None else ['human' if ENEMIES[key].get('roleId') else None for key in enemies]
  previous_modes={w:a.state(s)['mode'].get(w,'household') for w in party}
  for w in party:
   a.validate_loadout(s,w,a.loadout(s,w,'expedition'));a.state(s)['mode'][w]='expedition';g.set_character_assignment(s,w,'rest')
  r['serial']+=1;r['active']=dict(id=r['serial'],name=name,party=party[:],previousModes=previous_modes,route=route,mission=mission,enemies=enemies,ancestries=ancestries,index=0,hp=encounter_hp(s,enemies[0],mission),stage='outbound',pending=None,used=[],bypassUsed=False,outcomes=[],loot={'crowns':0,'food':0,'materials':{}},log=[],startedDay=s['dayNumber'],retreated=False,round=0,opening=False,contributions={})
  if bounty:bounty_contracts.attach(r['active'],bounty)
  if objective:objectives.attach(s,r['active'],objective)
  g.add_journal(s,'Departed: '+name+'. '+', '.join(g.character_profile(s,w)['name'] for w in party)+'. Household work pauses; expedition equipment is active.');return
 if kind=='watch-method':
  run=r['active'];require(s,run is not None and run['stage']=='decision','Wait for a patrol decision.');key=act.get('methodId');row=next((x for x in choices(s) if x['id']==key),None);require(s,row is not None,'Choose an offered patrol method.');require(s,not row['blockers'],' '.join(row['blockers']))
  for k,n in row.get('inputs',{}).items():s['materialInventory'][k]-=n
  run['pending']=deepcopy(row);run['stage']='exchange';return
 if kind=='watch-retreat':
  run=r['active'];require(s,run is not None and run['stage'] in ('outbound','decision','exchange','site-decision','site-work'),'This patrol is already returning or absent.')
  for k,n in (run['pending'] or {}).get('inputs',{}).items():s['materialInventory'][k]+=n
  run.update(stage='returning',retreated=True,pending=None);run['log'].append('Withdrew safely. Completed encounter rewards are retained; unfinished rewards are not granted.');return
 require(s,g.character_at_castle(s,'founder') and not r['active'],'Bring the patrol and your scholar home first.')
 if kind=='trial-start':
  require(s,not c['started'],'Chapter 8 has already begun.');c['started']=True
  remember(s,'The missing delivery','Rhess puts two signal records beside Velis’s delivery ledger. “The same wagon stopped twice,” she says. Velis taps its seal number. “The driver reached the refuge. Someone has the cargo. We can investigate when we are ready.”')
 elif kind=='trial-plan':
  require(s,'scout' in c['completed'] and 'escort' not in c['completed'],'Scout the missing delivery before agreeing the escort plan.');choice=act.get('choice');require(s,isinstance(choice,str) and choice in PLANS,'Choose a route plan.');c['plan']=choice
  remember(s,'The route plan',PLANS[choice]+(' Sabine identifies a false toll mark from the recovered harness. “They want us to mistake theft for authority. Ask who issued their order.”' if 'sabine' in g.household_members(s) else 'Velis compares the recovered seal with her contract. The toll collectors have no claim on the cargo.'))
 elif kind=='trial-watch':
  require(s,c['started'] and not c['completedOn'],'Begin Chapter 8 before choosing its home watch.');old=c['watchId']
  who=act.get('characterId');require(s,who is None or (isinstance(who,str) and who!='founder' and who in g.household_members(s) and g.character_at_castle(s,who)),'Choose a companion currently at home, or the ordinary barracks watch.');c['watchId']=who
  if old and old!=who and g.character_at_castle(s,old) and g.character_assignment(s,old)=='road-patrol':g.set_character_assignment(s,old,'rest')
  if who:g.set_character_assignment(s,who,'road-patrol')
 elif kind=='trial-conclude':
  b=closing_blockers(s);require(s,not b,' '.join(b));choice=act.get('choice');require(s,isinstance(choice,str) and choice in IMPROVEMENTS,'Choose a permanent road improvement.');c['improvement']=choice;c['completedOn']={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']};s['sharedFunds']+=20
  for w in c['lastParty']:g.award_advancement(s,w,'chapter-eight',2,'Held the castle approach and reviewed the watch together.')
  remember(s,'The first real test','The next delivery arrives with its seals intact. Velis counts the crates, then closes the ledger. Rhess hands the evening watch to the barracks guard and sits down for supper. You agree what to improve: '+IMPROVEMENTS[choice]+' The recovered contract pays 20 crowns. Nobody needs to stand watch alone tonight.')
 else:raise g.RuleError('Unknown patrol or Chapter 8 action.')

def encounter_hp(s,key,mission):
 import keeping_hearth
 return max(1,ENEMIES[key]['hp']-(2 if mission=='defend' and keeping_hearth.defense_ready(s) else 0))

def finish_encounter(s,run,row,reward=True):
 import game as g
 key=run['enemies'][run['index']];d=bestiary.encounter(s,run)
 bestiary.resolved(s,run,reward)
 run['outcomes'].append(dict(name=d['name'],method=row['name'],participants=[row['who']],enemyId=key,bestiaryId=d['bestiaryId'],ancestryId=d.get('ancestryId'),rewarded=reward))
 if reward:
  import signature_growth
  signature_growth.encounter(s,run)
  if not run.get('bountyId'):
   run['loot']['crowns']+=d['crowns'];run['loot']['food']+=d['food']
  for k,n in d['materials'].items():run['loot']['materials'][k]=run['loot']['materials'].get(k,0)+n
  bounty_contracts.collect(s,run,d['bestiaryId'])
 run['index']+=1;run['used']=[];run['round']=0;run['opening']=False;run['retaliationSeen']=False
 if run['index']==len(run['enemies']):run['stage']='returning'
 else:
  run.update(stage='decision',hp=encounter_hp(s,run['enemies'][run['index']],run['mission']))
  bestiary.observe(s,run)

def resolve(s,summary):
 import game as g,field_magic as f,provisions,companion_participation as cp,armoury as a
 run=saved(s)['active']
 if not run:return
 import field_objectives as objectives
 if objectives.resolve_site(s,run,summary):return
 if run['stage']=='decision':return
 if run['stage']=='outbound':run['stage']='site-decision' if run.get('objectiveId') else 'decision';bestiary.observe(s,run);summary.append(run['name']+': the party is waiting for your first encounter decision.');return
 if run['stage']=='returning':
  complete=not run['retreated'] and run['index']==len(run['enemies']);loot=run['loot'];c=chapter(s)
  import signature_growth
  run['signatureCountsBeforeReturn']={w:signature_growth.proof_count(signature_growth.history(it,w)) for w in run['party'] if (it:=signature_growth.item(s,w,True))}
  objective_text=objectives.returned(s,run,complete,summary)
  for who,stats in run.get('contributions',{}).items():
   for stat,proof in [('protected','protection'),('healed','healing'),('controlled','control')]:
    if complete and stats.get(stat,0):signature_growth.record_work(s,who,proof,field=True)
  bounty_text=bounty_contracts.returned(s,run,complete)
  if bounty_text:summary.append(bounty_text);run['log'].append(bounty_text)
  if complete and not run['mission'] and not run.get('bountyId'):
   if c['improvement']=='supplies':loot['food']+=4
   if c['improvement']=='contracts':loot['crowns']+=2
  s['sharedFunds']+=loot['crowns'];provisions.add(s,loot['food'])
  for k,n in loot['materials'].items():s['materialInventory'][k]+=n
  for w in run['party']:
   g.set_character_assignment(s,w,'rest');a.state(s)['mode'][w]=run.get('previousModes',{}).get(w,'household')
   for outcome in run['outcomes']:
    if outcome['rewarded']:g.award_advancement(s,w,'field-patrol:'+outcome['enemyId'],1,'First resolved field patrol encounter: '+outcome['name'])
  if complete and run['mission']:
   c['completed'].append(run['mission']);c['lastReturn']=s['dayNumber'];c['lastParty']=run['party'][:]
   text={'scout':'The harness cuts and recovered seal show an organized theft. Velis can now identify the affected contracts. Choose a route plan, then give the returning party a night at home.', 'escort':'The cargo reaches the refuge. A lookout reports that the remaining raiders are testing the castle approach. Rest the returning party, review the home watch and choose when to meet them.', 'defend':'The raiders withdraw from the defended approach. The tower warning and barracks relief held. Rest the party overnight before the closing supper.'}[run['mission']]
   remember(s,run['name'],text);summary.append(text)
  cp.returned(s,run['party'],run['outcomes'],complete,'field-patrol')
  if 'founder' not in run['party']:
   for w in run['party']:
    key='journey:field-patrol:'+w+(':complete' if complete else ':return');cp.saved(s)['events'][key]['reported']=True
  import signature_growth,patrol_homecoming
  unlocks=signature_growth.returned(s,run,complete)
  report=dict(route=run['route'],signatureUnlocks=unlocks,contributions=deepcopy(run.get('contributions',{})),id=run['id'],name=run['name'],party=run['party'],complete=complete,mission=run['mission'],returnedDay=s['dayNumber'],loot=deepcopy(loot),outcomes=deepcopy(run['outcomes']),log=run['log'][-30:])
  if run.get('bountyId'):report.update(bountyId=run['bountyId'],bountyText=bounty_text)
  if run.get('objectiveId'):report.update(objectiveId=run['objectiveId'],objectiveText=objective_text)
  import shared_history
  shared_history.returned(s,run,report)
  patrol_homecoming.returned(s,run,report)
  saved(s)['reports']=(saved(s)['reports']+[report])[-10:];saved(s)['active']=None
  summary.append(run['name']+': home. '+str(loot['crowns'])+' crowns, '+str(loot['food'])+' provisions, '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in loot['materials'].items())+'. Party assigned to Rest. This travel phase does not count as sleeping at home.');return
 row=run['pending'];who=row['who'];lines=[]
 import patrol_tactics as tactics
 result=tactics.preview(s,run,row)
 run['retaliationSeen']=run.get('retaliationSeen',run.get('round',0)>0) or not result['cancelled']
 for w,n in result['healthAfter'].items():f.initialize(s)['vitality'][w]=n
 if row['kind']=='technique':run['used'].append(row['id'])
 if row['kind']=='spell':
  spell=g.spell_by_id(s,row['spellId']);spell['castCount']=spell.get('castCount',0)+1
 stats=run.setdefault('contributions',{}).setdefault(who,dict(damage=0,healed=0,protected=0,controlled=0,actions=0))
 stats['damage']+=result['damage'];stats['healed']+=sum(x['amount'] for x in result['healing']);stats['protected']+=result['protectedDamage'];stats['controlled']+=int(result['controlReduction']>0);stats['actions']+=1
 run['hp']=result['enemyAfter'];run['round']=run.get('round',0)+1;run['opening']=result['opening']
 lines.append(g.character_profile(s,who)['name']+' · '+row['name']+': '+str(result['damage'])+' damage; enemy '+str(run['hp'])+' vitality remains.')
 if result['intercepted']:lines.append(g.character_profile(s,who)['name']+' covers '+g.character_profile(s,result['originalTarget'])['name']+'.')
 if result['injury']:lines.append(g.character_profile(s,result['target'])['name']+' loses '+str(result['injury'])+' vitality.')
 elif not result['cancelled']:lines.append('The attack is contained; nobody loses vitality.')
 for heal in result['healing']:lines.append(g.character_profile(s,heal['who'])['name']+' recovers '+str(heal['amount'])+' vitality.')
 if row.get('control'):lines.append('The next damaging action gains '+str(result['opening'] or 0)+' damage.')
 task_complete=objectives.resolved(s,run,row,result)
 if row.get('objectiveStep'):lines.append('Objective work: '+str(run['objectiveProgress'])+'/'+str(objectives.OBJECTIVES[run['objectiveId']]['goal'])+' steps complete.')
 if task_complete and run['hp']:
  finish_encounter(s,run,row,False)
  lines.append('The objective is secure. The party leaves safely; objective payment is due on return. No enemy loot is awarded.')
 elif not run['hp']:
  if row['kind']=='bypass':run['bypassUsed']=True
  finish_encounter(s,run,row,row['kind']!='bypass')
 elif not any(f.vitality(s,w)>0 for w in run['party']):run.update(stage='returning',retreated=True);lines.append('The party falls back. Rest at home before another outing; no permanent injuries or equipment loss.')
 else:run['stage']='decision'
 run['pending']=None;run['log']=(run['log']+lines)[-30:];summary.extend(lines)

def closing_blockers(s):
 import game as g
 c=chapter(s);b=[]
 if c['completedOn']:b.append('Chapter complete.')
 if 'defend' not in c['completed']:b.append('Return after holding the castle approach.')
 b+=night_blockers(s)
 if s['currentDayPhase']!='evening':b.append('Share the closing supper in the evening.')
 if any(not g.character_at_castle(s,w) for w in c['lastParty']):b.append('Bring the returning story party home.')
 return b

def view(s):
 import campaign_guidance as guide
 import game as g,field_magic as f,patrol_tactics as tactics,patrol_homecoming
 run=saved(s)['active'];public=deepcopy(run)
 if public:
  public.pop('enemies');public['total']=len(run['enemies']);public['enemy']=bestiary.encounter(s,run) if run['index']<len(run['enemies']) and run['stage']!='outbound' else None
  public['entranceDefense']=bool(run['mission']=='defend' and encounter_hp(s,'bandit','defend')<ENEMIES['bandit']['hp'])
  public['intent']=tactics.intent(s,run) if run['stage'] in ('decision','exchange') else None
  public['choices']=choices(s);public['cover'],public['coverSources']=cover(s,[w for w in run['party'] if f.vitality(s,w)>0]);public['partyRows']=[dict(id=w,name=g.character_profile(s,w)['name'],vitality=f.vitality(s,w),roles=tactics.roles(s,w)) for w in run['party']]
 import field_objectives
 return dict(objectives=field_objectives.view(s,run),homecoming=patrol_homecoming.view(s),unlocked=unlocked(s),active=public,routes=deepcopy(ROUTES),reports=deepcopy(saved(s)['reports']),members=[dict(id=w,name=g.character_profile(s,w)['name'],vitality=f.vitality(s,w),roles=tactics.roles(s,w),blockers=member_blockers(s,w)) for w in g.household_members(s)],chapter={**deepcopy(chapter(s)), 'next':guide.checked(s,guide.trial(s)), 'missions':{k:{**deepcopy(d),'blockers':story_blockers(s,k)} for k,d in MISSIONS.items()},'plans':PLANS,'improvements':IMPROVEMENTS,'closingBlockers':closing_blockers(s),'nightBlockers':night_blockers(s)})

def forecast(s):
 r=saved(s)['active']
 if not r:return []
 return [r['name']+': '+{'outbound':'arrive and wait for a decision.','decision':'waiting for your decision; no automatic combat.','exchange':'resolve the selected battle action.','site-decision':'waiting for your site choice; no automatic work.','site-work':'complete one phase of the selected site work.','returning':'return home, receive earned rewards and begin resting next phase.'}[r['stage']]]
