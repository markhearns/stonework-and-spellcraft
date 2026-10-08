"""Personal, trained field techniques. Optional additive save data; no point pool.

Learning uses the existing training assignment. Prepared actions are bounded and
field outcomes, including costs, resolve only on Advance. Definitions are data.
"""
from copy import deepcopy
PEOPLE={
 'rhess':{'room':'watchtower','branches':[
  ('watchkeeper','Watchkeeper','Hold the line and let someone else take a turn.','warded-cover',
   ('spear-watch','Spear watch',['enemy','physical'],2,1,0,'A measured spear thrust, with cover against retaliation.'),
   ('relief-signal','Relief signal',['enemy'],1,2,0,'Trade striking power for a guarded opening.'),
   ('shared-vigil','Shared vigil','Guarded techniques prevent one additional retaliation damage.','block')),
  ('ember','Ember','Control the flame instead of surrendering to it.','measured-force',
   ('banked-flame','Banked flame',['enemy','fire'],3,0,0,'A precise flare; ember creatures resist the heat.'),
   ('ember-spear','Ember spear',['enemy','physical'],4,0,1,'Drive through a guarded opening; costs 1 vitality on resolution.'),
   ('steady-flame','Steady flame','Ember techniques deal one additional damage to non-ember foes.','damage')),
  ('pathfinder','Pathfinder','Find the route that brings everybody home.','sure-footing',
   ('route-reader','Route reader',['gap','height','flood','trail'],0,0,0,'Secure a crossing or interpret the trail.'),
   ('safe-passage','Safe passage',['submerged','insight','trail'],0,0,0,'Find a service route or reconstruct its instructions.'),
   ('waymarks','Waymarks','Pathfinder obstacle work takes one phase instead of two.','pace'))]},
 'kaede':{'room':'training-yard','branches':[
  ('breaker','Breaker','Put strength exactly where it is needed.','measured-force',
   ('measured-blow','Measured blow',['enemy','physical'],3,0,0,'A committed, controlled strike.'),
   ('gate-breaker','Gate breaker',['enemy','physical'],4,0,1,'A powerful follow-through; costs 1 vitality on resolution.'),
   ('follow-through','Follow-through','Breaker techniques deal one additional damage.','damage')),
  ('stillness','Stillness','Let an opponent make the first mistake.','warded-cover',
   ('settled-stance','Settled stance',['enemy'],2,1,0,'Brace before striking; reduce retaliation.'),
   ('turning-counter','Turning counter',['enemy'],1,2,0,'Deflect the attack; deal 2 extra damage if the foe survives the first hit.'),
   ('unshaken','Unshaken','Stillness techniques prevent one additional retaliation damage.','block')),
  ('instructor','Instructor','Make the person beside you more confident.','clear-measure',
   ('steady-hands','Steady hands',['gap','height','physical'],0,0,0,'Talk the party through sound footing and controlled effort.'),
   ('catch-breath','Catch your breath',['enemy'],1,1,0,'Cover a breathing space; restore 1 vitality to the most injured other companion.'),
   ('clear-example','Clear example','Instructor obstacle work takes one phase; Catch your breath restores 2 vitality.','support'))]},
 'sabine':{'room':'dungeons','branches':[
  ('shadow','Shadow','Use the eye for openings that once made her a thief.','sure-footing',
   ('quiet-step','Quiet step',['gap','height','trail'],0,0,0,'Test the overlooked passage and secure it for the others.'),
   ('slip-the-latch','Slip the latch',['submerged','insight','physical'],0,0,0,'Open a service fastening without destroying it.'),
   ('unseen-route','Unseen route','Shadow obstacle work takes one phase instead of two.','pace')),
  ('restraint','Restraint','Choose when to stop, and help others do the same.','warded-cover',
   ('checked-strike','Checked strike',['enemy'],2,1,0,'An economical strike with a guarded withdrawal.'),
   ('disarming-turn','Disarming turn',['enemy'],1,2,0,'Break the opponent’s rhythm; deal 2 extra damage if it survives the first hit.'),
   ('measured-appetite','Measured appetite','Restraint techniques prevent one additional retaliation damage.','block')),
  ('keeper','Dungeon keeper','Understand locks, wards, and the obligations of keeping watch.','clear-measure',
   ('read-the-lock','Read the lock',['insight','physical'],0,0,0,'Identify a binding or mechanical lock and work through it.'),
   ('ward-key','Ward-key turn',['enemy','insight'],3,0,0,'Interrupt an artificial binding; +1 damage against constructs or undead.'),
   ('keeper-craft','Keeper’s craft','Keeper obstacle work takes one phase; Ward-key turn gains 1 damage against constructs or undead.','keeper'))]}}
from personal_path_content import ADDITIONS
PEOPLE.update(ADDITIONS)
CATALOG={}
for who,person in PEOPLE.items():
 for branch,title,theme,enchant,root,advanced,passive in person['branches']:
  for level,node in enumerate((root,advanced)):
   key,name,tags,damage,block,cost,description=node[:7]
   extra=node[7] if len(node)>7 else {}
   CATALOG[key]=dict(id=key,who=who,branch=branch,branchName=title,theme=theme,enchantment=enchant,name=name,tags=tags,damage=damage,block=block,cost=cost,description=description,kind='technique',requires=root[0] if level else None,advanced=bool(level),**extra)
  key,name,description,effect=passive
  CATALOG[key]=dict(id=key,who=who,branch=branch,branchName=title,theme=theme,enchantment=enchant,name=name,description=description,kind='passive',effect=effect,requires=root[0],advanced=False)

def record(s,who):return s.get('personalPaths',{}).get(who,{'learned':[],'techniques':[],'passives':[]})
def ensure(s,who):return s.setdefault('personalPaths',{}).setdefault(who,deepcopy(record(s,who)))
def home_blockers(s,who):
 import game as g
 return [] if g.character_at_castle(s,'founder') and g.character_at_castle(s,who) else ['Return home together to change this build.']
def learning_blockers(s,who,d):
 import game as g,headquarters as h
 r=record(s,who);b=home_blockers(s,who)
 if not h.ready(s,'training-yard'):b.append('Restore the training yard first.')
 if s['trainingProjects'].get(who):b.append('Finish or cancel the current learning project first.')
 if d['id'] in r['learned']:b.append('Already learned.')
 if d['requires'] and d['requires'] not in r['learned']:b.append('Learn '+CATALOG[d['requires']]['name']+' first.')
 if d['advanced'] and not s.get('armoury',{}).get('signatures',{}).get(who,{}).get('completedOn'):b.append('Complete this resident’s signature equipment request first.')
 if d['kind']=='passive' and g.character_sheet(s,who)['earnedAdvancement']<2:b.append('Earn 2 lifetime advancement from accomplishments; points are not spent. Completing a personal technique at a new field site earns 2 once per site.')
 return b

def view(s):
 import game as g,patrol_tactics
 out={}
 for who in g.household_members(s):
  if who not in PEOPLE:continue
  r=deepcopy(record(s,who));r['homeBlockers']=home_blockers(s,who);r['room']=PEOPLE[who]['room'];r['options']=[]
  for d in CATALOG.values():
   if d['who']!=who:continue
   group='techniques' if d['kind']=='technique' else 'passives';limit=3 if group=='techniques' else 2
   blockers=home_blockers(s,who)
   if d['id'] not in r['learned']:blockers=blockers+['Learn this through assigned training first.']
   if d['id'] not in r[group] and len(r[group])>=limit:blockers=blockers+['Put aside a prepared '+d['kind']+' first.']
   r['options'].append({'patrolNote':patrol_tactics.path_note(d['id']),'preview':preview(s,who,d['id']),**deepcopy(d),'learned':d['id'] in r['learned'],'prepared':d['id'] in r[group],'learningBlockers':learning_blockers(s,who,d),'prepareBlockers':blockers})
  r['drills']=[drill_preview(s,who,key) for key in DRILLS]
  r['lastDrill']=deepcopy(s.get('personalPathDrills',{}).get(who))
  out[who]=r
 return out

def apply(s,a):
 if a.get('type') not in ('path-train','path-prepare','path-clear','path-drill'):return False
 import game as g
 who=a.get('characterId');g.require(isinstance(who,str) and who in PEOPLE and who in g.household_members(s),'Choose a household member with personal paths.')
 b=home_blockers(s,who);g.require(not b,' '.join(b))
 if a['type']=='path-drill':
  import headquarters as h
  scenario=a.get('scenario')
  g.require(isinstance(scenario,str) and scenario in DRILLS,'Choose a training-yard exercise.')
  g.require(h.ready(s,'training-yard'),'Restore the training yard first.')
  g.require(not s['trainingProjects'].get(who),'Finish or cancel the current learning project first.')
  trial=drill_preview(s,who,scenario);g.require(not trial['blockers'],' '.join(trial['blockers']))
  s['trainingProjects'][who]={'kind':'personal-drill','targetId':scenario,'completedWorkPhases':0,'requiredWorkPhases':1,'trial':trial}
  g.set_character_assignment(s,who,'training');return True
 if a['type']=='path-clear':
  r=ensure(s,who);r['techniques']=[];r['passives']=[];return True
 key=a.get('talentId');g.require(isinstance(key,str) and key in CATALOG and CATALOG[key]['who']==who,'Choose this resident’s own talent.')
 d=CATALOG[key]
 if a['type']=='path-train':
  b=learning_blockers(s,who,d);g.require(not b,' '.join(b))
  s['trainingProjects'][who]={'kind':'personal-technique','targetId':key,'completedWorkPhases':0,'requiredWorkPhases':2}
  g.set_character_assignment(s,who,'training');g.add_journal(s,g.character_profile(s,who)['name']+' begins '+d['name']+': two assigned training phases, no advancement or crowns spent.')
 else:
  g.require(type(a.get('prepared')) is bool,'Choose whether to prepare this talent.')
  r=ensure(s,who);g.require(key in r['learned'],'Learn this talent first.');group='techniques' if d['kind']=='technique' else 'passives';limit=3 if group=='techniques' else 2
  if a['prepared'] and key not in r[group]:
   replacement=a.get('replaceId')
   if replacement is not None:
    g.require(isinstance(replacement,str) and replacement in r[group],'Choose a currently prepared '+d['kind']+' to replace.')
    r[group][r[group].index(replacement)]=key
   else:g.require(len(r[group])<limit,'Choose a prepared '+d['kind']+' to replace.');r[group].append(key)
  elif not a['prepared'] and key in r[group]:r[group].remove(key)
 return True

def complete(s,who,project,summary):
 r=ensure(s,who);key=project['targetId']
 if key not in r['learned']:r['learned'].append(key)
 summary.append(CATALOG[key]['name']+' learned. Prepare it under Personal paths; no talent is auto-equipped.')

def effect(s,who,key):
 import armoury as a
 d=CATALOG[key];r=record(s,who)
 passive=next((CATALOG[p]['effect'] for p in r['passives'] if CATALOG[p]['branch']==d['branch']),None)
 gear=[x for x in a.effects(s,who,'expedition') if x['effect']==d['enchantment']]
 return {'damage':d['damage']+int(passive=='damage')+int(bool(gear) and d['damage']>0), 'block':d['block']+int(passive=='block'), 'phases':1 if passive in ('pace','support','keeper') or gear else 2,'heal':2 if passive=='support' else 1,'keeper':int(passive=='keeper'),'gear':gear,'cost':d['cost'],'counter':d.get('counter',2 if key in ('turning-counter','disarming-turn') else 0),'healsAlly':(d.get('healsAlly',1 if key=='catch-breath' else 0)+int(passive=='support')) if d.get('healsAlly',key=='catch-breath') else 0,'restoresSelf':d.get('restoresSelf',0)+int(passive=='support' and d.get('restoresSelf',0)>0),'immune':d.get('immune',['ember'] if key=='banked-flame' else [])}

def context(s):
 import field_magic as f,first_patrol as p,roads_we_keep as road
 e=s.get('expedition')
 if not e:return None
 if e['siteId']==f.SITE:
  d=f.step(s)
  return dict(site=e['siteId'],step=d['id'],tag=d['tag'],enemy=d.get('enemy')) if d else None
 module=p if p.active(s) else road if road.active(s) else None
 if not module:return None
 d=module.step(s)
 if not d:return None
 tag={'fieldcraft':'trail','athletics':'physical','artifice':'insight','channeling':'enemy','diplomacy':'social'}[d[5] if module==p else d[6]]
 return dict(site=e['siteId'],step=d[0],tag=tag,enemy=None)

def use_key(c,who,key):return ':'.join((c['site'],c['step'],who,key))
def field_options(s):
 import game as g,field_magic as f,armoury as a
 c=context(s)
 if not c:return []
 rows=[]
 for who in g.expedition_party(s):
  for key in record(s,who)['techniques']:
   d=CATALOG[key]
   if c['tag'] not in d['tags']:continue
   fx=target_effect(s,who,key,c['enemy']);b=[]
   if s['expedition']['stage']!='encounter-choice':b.append('Finish the current field action first.')
   if f.vitality(s,who)<=fx['cost']:b.append('Needs at least '+str(fx['cost']+1)+' vitality.')
   if use_key(c,who,key) in s.get('personalPathUses',[]):b.append('Already used at this obstacle; retreat does not reset it.')
   if d['advanced']:
    signature=s.get('armoury',{}).get('signatures',{}).get(who,{})
    item=a.state(s)['items'].get(signature.get('itemId'),{})
    if not signature.get('completedOn') or item.get('ownerId')!=who or item.get('location')!='armoury' or signature.get('itemId') not in a.loadout(s,who,'expedition')['slots'].values():b.append('Equip the completed signature piece in the expedition loadout.')
   # The aqueduct has explicit combat; story encounters remain safe route work.
   combat=c['site']==f.SITE and c['tag']=='enemy'
   hit=fx['damage']
   if c['enemy'] in fx['immune']:b.append('This enemy is immune to this technique; choose another method.')
   fx['damage']=hit
   text=(str(hit)+' damage; prevent '+str(fx['block'])+' retaliation damage. 1 phase.' if combat else str(fx['phases'])+' phases of route work.')
   if fx['cost']:text+=' Costs '+str(fx['cost'])+' vitality when resolved.'
   text+=' '+d['description']
   if fx['gear']:text+=' Active '+a.enchantment_name(d['enchantment'])+' improves this technique.'
   rows.append(dict(id='personal:'+key,who=who,talentId=key,name=g.character_profile(s,who)['name']+' · '+d['name'],description=text,blockers=b,phases=1 if combat else fx['phases'],effects=fx,context=c))
 return rows

def start_field(s,a):
 import game as g,field_magic as f
 g.require(s.get('expedition') and s['expedition']['siteId']==f.SITE,'Use the offered encounter controls for this expedition.')
 who=a.get('characterId');key=a.get('method')
 row=next((r for r in field_options(s) if r['who']==who and r['id']==key),None)
 g.require(row is not None,'Prepare a personal technique that applies to this obstacle.');g.require(not row['blockers'],' '.join(row['blockers']))
 f.progress(s)['pending']={'kind':key,'who':who,'target':who,'spellId':None,'inputs':{},'crowns':0,'remaining':row['phases'],'personal':deepcopy(row)}
 s['expedition'].update(stage='working',remainingWorkPhases=row['phases'])
 return True

def remember_use(s,row):
 import game as g
 key=use_key(row['context'],row['who'],row['talentId']);uses=s.setdefault('personalPathUses',[])
 if key not in uses:uses.append(key)
 g.award_advancement(s,row['who'],'personal-path:'+row['context']['site'],2,'First personal technique resolved at '+g.EXPEDITION_SITES[row['context']['site']]['name'])

def resolve_field(s,job,d,text):
 import field_magic as f,game as g
 row=job['personal'];who=row['who'];key=row['talentId'];fx=row['effects'];p=f.progress(s)
 remember_use(s,row)
 f.initialize(s)['vitality'][who]=max(0,f.vitality(s,who)-fx['cost'])
 if d['tag']!='enemy':text.append(row['name']+' secures the route.');return True
 hit=fx['damage'];hp=max(0,p['enemyHp'].get(d['id'],d['hp'])-hit)
 counter=fx.get('counter',2 if key in ('turning-counter','disarming-turn') else 0)
 if counter and hp:hp=max(0,hp-counter);hit+=counter
 p['enemyHp'][d['id']]=hp;text.append(row['name']+': '+str(hit)+' damage; '+str(hp)+' enemy vitality remains.')
 if hp:
  injury=max(0,d['attack']-fx['block'])
  if p['buffs'].get(who,{}).get('decoy',0):p['buffs'][who]['decoy']-=1;injury=0
  f.initialize(s)['vitality'][who]=max(0,f.vitality(s,who)-injury);text.append('Retaliation: '+str(injury)+' vitality lost.')
 healing=fx.get('healsAlly',fx['heal'] if key=='catch-breath' else 0)
 if healing:
  others=[w for w in g.expedition_party(s) if w!=who]
  if others:
   target=min(others,key=lambda w:f.vitality(s,w));before=f.vitality(s,target);f.heal(s,target,healing);text.append(g.character_profile(s,target)['name']+' recovers '+str(f.vitality(s,target)-before)+' vitality.')
 if fx.get('restoresSelf'):
  before=f.vitality(s,who);f.heal(s,who,fx['restoresSelf']);text.append('Personal recovery: '+str(f.vitality(s,who)-before)+' vitality.')
 if fx['cost']:text.append('Technique exertion: '+str(fx['cost'])+' vitality.')
 return hp==0

def route_choices(s):
 import game as g,armoury as a
 return {r['id']:{'name':r['name'],'description':r['description'],'blockers':r['blockers'],'phases':r['phases'],'participants':[r['who']],'personal':deepcopy(r),'timeSaved':2-r['phases'],'equipmentUsed':[{'ownerId':r['who'],'ownerName':g.character_profile(s,r['who'])['name'],'itemId':e['itemId'],'name':e['name'],'effect':a.enchantment_name(e['effect']),'rank':e['rank']} for e in r['effects']['gear']]} for r in field_options(s)}

def resolve_route(s,row,summary):
 import field_magic as f
 if not row.get('personal'):return
 r=row['personal'];remember_use(s,r);cost=r['effects']['cost'];who=r['who']
 if cost:f.initialize(s)['vitality'][who]=max(0,f.vitality(s,who)-cost)
 summary.append(r['name']+' completed'+(' · '+str(cost)+' vitality exertion.' if cost else '.'))


DRILLS={
 'sparring':('Guarded sparring','enemy','living'),
 'sentinel':('Armoured training dummy','enemy','construct'),
 'crossing':('Rope crossing','gap',None),
 'mechanism':('Practice ward lock','insight',None),
 'lifting':('Braced lifting exercise','physical',None),
}
def drill_preview(s,who,key):
 import armoury as a,game as g,headquarters as h
 name,tag,enemy=DRILLS[key];trial={**s,'armoury':{**a.state(s),'mode':{**a.state(s)['mode'],who:'expedition'}}};rows=[]
 for talent in record(s,who)['techniques']:
  d=CATALOG[talent]
  if tag not in d['tags']:continue
  fx=target_effect(trial,who,talent,enemy);b=[]
  if d['advanced']:
   sig=a.state(s)['signatures'].get(who,{});it=a.state(s)['items'].get(sig.get('itemId'),{})
   if not sig.get('completedOn') or it.get('ownerId')!=who or it.get('location')!='armoury' or sig.get('itemId') not in a.loadout(s,who,'expedition')['slots'].values():b.append('Equip the completed signature piece in the expedition loadout.')
  hit=fx['damage']
  if tag=='enemy':
   counter=fx['counter'] if hit<6 else 0
   detail=str(hit+counter)+' damage against a 6-vitality target; '+str(max(0,2-fx['block']) if hit+counter<6 else 0)+' retaliation from a 2-damage attack; '+str(fx['cost'])+' exertion.'
   if fx['healsAlly']:detail+=' An injured companion would recover '+str(fx['healsAlly'])+' vitality.'
   if fx['restoresSelf']:detail+=' Personal recovery: '+str(fx['restoresSelf'])+' vitality.'
  else:detail=str(fx['phases'])+' phases of field work; '+str(fx['cost'])+' exertion.'
  rows.append({'id':talent,'name':d['name'],'detail':detail,'blockers':b})
 blockers=home_blockers(s,who)
 if not h.ready(s,'training-yard'):blockers.append('Restore the training yard first.')
 if s['trainingProjects'].get(who):blockers.append('Finish or cancel the current learning project first.')
 if not any(not r['blockers'] for r in rows):blockers.append('Prepare an eligible technique and equip any required signature piece.')
 return {'id':key,'name':name,'rows':rows,'blockers':blockers}

def finish_drill(s,who,project,summary):
 s.setdefault('personalPathDrills',{})[who]={**deepcopy(project['trial']),'day':s['dayNumber'],'phase':s['currentDayPhase']}
 summary.append(project['trial']['name']+' complete: results recorded under Build → Training. No vitality, supplies, or advancement changed.')


def preview(s,who,key):
 """The same effect calculation as the field, projected into saved field gear."""
 import armoury as a
 trial={**s,'armoury':{**a.state(s),'mode':{**a.state(s)['mode'],who:'expedition'}}}
 d=CATALOG[key]
 if d['kind']=='passive':return None
 fx=effect(trial,who,key)
 parts=[d['name']+': '+str(d['damage'])+' base damage, '+str(d['block'])+' base guard.']
 parts += [CATALOG[x]['name']+': '+CATALOG[x]['description'] for x in record(s,who)['passives'] if CATALOG[x]['branch']==d['branch']]
 parts += [a.enchantment_name(x['effect'])+' on '+x['name']+': matching inscription active in the saved expedition loadout.' for x in fx['gear']]
 return {k:v for k,v in fx.items() if k!='gear'}|{'breakdown':parts,'equipment':[{**x,'icon':'/assets/equipment/'+a.CATALOG[a.state(s)['items'][x['itemId']]['definitionId']]['iconId']+'.webp'} for x in fx['gear']]}


def target_effect(s,who,key,enemy=None):
 fx=effect(s,who,key);d=CATALOG[key]
 targets=d.get('bonusAgainst',['construct','undead'] if key=='ward-key' else [])
 if enemy in targets:
  fx['damage']+=d.get('bonusDamage',1)+(fx['keeper'] if enemy in ('construct','undead') else 0)
 if enemy in fx['immune']:fx['damage']=0
 return fx
