"""Chapter seven: share the watch, restore the tower, relieve its keeper."""
from copy import deepcopy
import headquarters as h
TRAIL='watchtower-trail'
WARD='broken-wardstones'
SITES={TRAIL:('The Watchtower Trail','Follow abandoned camps to the keeper of the old tower.'),WARD:('The Broken Wardstones','Return with Rhess to contain the awakened boundary guardian.')}
STEPS={TRAIL:[
 ('camp','A supper left behind','The camp was abandoned in order, not panic. Someone drew a warning in the ashes.','Compare tracks and abandoned belongings','dexterity','fieldcraft','sure-footing'),
 ('signal','An answer from the tower','A shutter flashes twice. The keeper wants you to stop outside the damaged boundary.','Answer the signal and approach openly','charisma','diplomacy','clear-measure'),
 ('keeper','The woman holding the door','Rhess lowers her spear. She has been diverting travellers while containing a damaged stone guardian alone.','Help brace the door and listen to her account','might','athletics','measured-force')],WARD:[
 ('trail','Someone has been here before','Rhess finds the gouges where the stone guardian crossed the path. It follows the old boundary, even through new roads.','Mark a safe approach and an escape route','dexterity','fieldcraft','sure-footing'),
 ('ward','Read the broken command','The ward orders the guardian to defend a settlement that no longer exists. Its cracked return mark repeats the order.','Copy the fragments and compare their instructions','intelligence','artifice','clear-measure'),
 ('guardian','Hold the guardian at the crossing','Stone limbs scrape across the ford. Someone must draw its attention while the others reach the return mark.','Use cover and carefully rotate the distraction','resolve','channeling','warded-cover'),
 ('seal','A boundary people can cross','With the guardian contained, the old command can be repaired or safely retired.','Brace the housing and complete the chosen repair','might','athletics','measured-force')]}
def initialize(s):
 s.setdefault('firstPatrol',{'started':False,'completedOn':None,'drill':None,'drillDone':False,'returnedOn':None,'resolution':None,'memories':[],'breathUsed':False})
 s.setdefault('patrolJourneys',{k:{'completed':[],'pending':None,'outcomes':[],'discoveries':[]} for k in SITES})
 import household_rest
 household_rest.initialize(s)
 s['localEncounters'].setdefault('rhess',{'status':'available','completedOn':None})
def saved(s):return s['firstPatrol']
def active(s):return bool(s.get('expedition') and s['expedition']['siteId'] in SITES)
def progress(s,site=None):return s['patrolJourneys'][site or s['expedition']['siteId']]
def step(s):return next((d for d in STEPS[s['expedition']['siteId']] if d[0] not in progress(s)['completed']),None)
def available(s):return bool(s.get('roadsWeKeep',{}).get('completedOn'))
def remember(s,title,text):
 import game as g
 saved(s)['memories'].append({'title':title,'text':text,'day':s['dayNumber']});g.add_journal(s,title+': '+text)
def departure_blockers(s,site):
 import game as g
 r=saved(s);b=[]
 if not available(s) or not r['started']:b.append('Conclude Chapter 6 and open The First Patrol.')
 if site==WARD:
  if not progress(s,TRAIL)['discoveries']:b.append('Return from the watchtower trail first.')
  if 'rhess' not in g.household_members(s):b.append('Invite Rhess to visit and agree household membership through Contacts.')
  if not r['drillDone']:b.append('Complete the two-phase shared relief drill.')
  if not h.ready(s,'watchtower'):b.append('Restore the watchtower.')
  if not r['resolution']:b.append('Agree whether to repair or retire the old guardian command.')
  if not r['returnedOn'] or any(s.get('overnightRest',{}).get(w,0)<=r['returnedOn'] for w in ('founder','rhess')):b.append('After returning and recruiting Rhess, spend an evening with both of you resting at home; Advance includes overnight sleep.')
 return b

def encounter_view(s):
 import game as g,armoury as a,character_approaches as apt,field_magic
 d=step(s)
 if not d:return None
 party=g.expedition_party(s);scores={w:apt.score(s,w,apt.spec(d[4],d[5],6),party) for w in party};good=[w for w in party if scores[w]['qualified'] and a.has(s,w,d[6],'expedition')]
 choices={'patient':{'name':d[3],'phases':2,'description':'Two phases of safe coordinated work. No injury or component cost.','blockers':[],'participants':party},'gear':{'name':'Use a proven enchanted fitting','phases':1,'description':'Active matching inscription and approach score 6.','blockers':[] if good else ['A traveller needs '+a.enchantment_name(d[6])+' active and approach score 6.'],'participants':good[:1],'scores':scores}}
 if 'rhess' in party and d[0] in ('trail','guardian'):
  choices['keeper']={'name':'Let Rhess choose the defensive ground','phases':1,'description':'Her knowledge opens a sheltered route.','blockers':[],'participants':['rhess']}
 if 'rhess' in party and d[0] in ('ward','guardian'):
  choices['breath']={'name':'Rhess uses a controlled breath of heat','phases':1,'description':'Clear the damaged binding or draw the guardian. Once across this expedition lead; costs Rhess 1 vitality and remains spent after retreat.','blockers':(['Her breath has already been committed to this lead.'] if saved(s)['breathUsed'] else [])+(['Rhess needs at least 3 vitality.'] if field_magic.vitality(s,'rhess')<3 else []),'participants':['rhess']}
 for key,row in choices.items():
  row['timeSaved']=2-row['phases'];row['equipmentUsed']=[{'ownerId':w,'ownerName':g.character_profile(s,w)['name'],'itemId':e['itemId'],'name':e['name'],'effect':a.enchantment_name(e['effect']),'rank':e['rank']} for w in row['participants'] for e in a.effects(s,w,'expedition') if key=='gear' and e['effect']==d[6]]
 import personal_paths
 choices.update(personal_paths.route_choices(s))
 p=progress(s)['pending'];return {'step':{'id':d[0],'name':d[1],'description':d[2]},'choices':choices,'totalSteps':len(STEPS[s['expedition']['siteId']]),'progress':{'completedSteps':progress(s)['completed'][:],'pendingWork':{**deepcopy(p),'remainingWorkPhases':p['remaining']} if p else None}}
def resume(s):
 e=s['expedition'];p=progress(s)['pending']
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p:e.update(stage='working',remainingWorkPhases=p['remaining'])
 else:e['stage']='encounter-choice'
def apply(s,act):
 import game as g,field_magic
 k=act.get('type');r=saved(s)
 if k=='choose-encounter-method' and active(s):
  g.require(s['expedition']['stage']=='encounter-choice','Wait for a field decision.');key=act.get('methodId');choices=encounter_view(s)['choices'];g.require(isinstance(key,str) and key in choices,'Choose an offered method.');c=choices[key];g.require(not c['blockers'],' '.join(c['blockers']))
  if key=='breath':
   r['breathUsed']=True;field_magic.initialize(s)['vitality']['rhess']=field_magic.vitality(s,'rhess')-1
  progress(s)['pending']={'methodId':key,'remaining':c['phases'],'participants':c['participants'][:],'outcome':deepcopy(c)};resume(s);return True
 if not isinstance(k,str) or not k.startswith('patrol-'):return False
 g.require(g.character_at_castle(s,'founder'),'Return home first.');g.require(available(s),'Conclude Chapter 6 first.')
 if k=='patrol-start':
  g.require(not r['started'],'The patrol has already begun.');r['started']=True;remember(s,'An unanswered signal','Velis brings reports of deserted camps. A tower lamp still answers the road, though nobody remembers assigning a keeper.')
 elif k=='patrol-plan':
  g.require(progress(s,TRAIL)['discoveries'],'Meet the keeper and bring her account home first.');g.require(not progress(s,WARD)['completed'] and not r['completedOn'],'The field resolution is already underway.');g.require(act.get('choice') in ('repair','retire'),'Choose repair or safe retirement.');r['resolution']=act['choice']
 elif k=='patrol-drill':
  b=drill_blockers(s);g.require(not b,' '.join(b));r['drill']={'done':0};remember(s,'Practice handing over','Rhess teaches a quiet signal for taking over cover. The second exercise will be hers: stepping back when you answer it.')
 elif k=='patrol-conclude':
  b=closing_blockers(s);g.require(not b,' '.join(b));r['completedOn']={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']};remember(s,'The first shared watch','The tower lantern is visible from supper. Rhess starts to rise at a sound outside, then sits again when another guard answers. She puts a small carved token beside her plate. “I thought this one could stay here.”')
 else:raise g.RuleError('Unknown Chapter 7 action.')
 return True

def drill_blockers(s):
 import game as g
 r=saved(s);b=[]
 if r['drillDone'] or r['drill']:b.append('The relief drill is already complete or underway.')
 if any(w not in g.household_members(s) or not g.character_at_castle(s,w) for w in ('founder','rhess')):b.append('Bring yourself and household member Rhess home.')
 elif any(g.character_assignment(s,w)!='rest' for w in ('founder','rhess')):b.append('Set both yourself and Rhess to Rest before beginning the shared drill.')
 if not h.ready(s,'training-yard'):b.append('Restore the training yard.')
 return b

def resolve_home(s,summary,assignments,phase):
 import game as g
 r=saved(s)
 if r['drill'] and all(assignments.get(w)=='rest' for w in ('founder','rhess')):
  r['drill']['done']+=1;summary.append('Shared relief drill: '+str(r['drill']['done'])+'/2 phases. Rhess practices giving up the front position.')
  if r['drill']['done']==2:r['drillDone']=True;r['drill']=None

def resolve_expedition(s):
 import game as g,arrivals,local_encounters,provisions
 e=s['expedition'];site=e['siteId'];p=progress(s);party=g.expedition_party(s)
 if e['stage']=='working':
  job=p['pending'];g.require(job is not None,'Choose a field method first.')
  if not all(w in party for w in job['participants']):
   e['stage']='encounter-choice';s['lastPhaseSummary'].append('The previous method needs travellers who are no longer present. Choose a new method; no work was completed.');return
  job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
  if job['remaining']:return
  d=step(s);c=job['outcome']
  import personal_paths
  personal_paths.resolve_route(s,c,s['lastPhaseSummary'])
  p['outcomes'].append({'stepId':d[0],'name':d[1],'method':c['name'],'participants':job['participants'],'equipmentUsed':c['equipmentUsed'],'timeSaved':c['timeSaved']});p['completed'].append(d[0]);p['pending']=None;resume(s);return
 rewards=['Returned safely; completed decisions and paid work are retained.']
 if e['discoveryReady'] and not p['discoveries']:
  p['discoveries'].append('survey');s['sharedFunds']+=20;provisions.add(s,12);rewards=['The household receives 20 crowns and 12 provisions for securing this route.']
  if site==TRAIL:
   saved(s)['returnedOn']=s['dayNumber'];rewards.append('Rhess offers correspondence. Invite her through Contacts, restore the tower, practice relief, and sleep at home before the next journey.')
   if 'rhess' not in s['people'] and not any(x['name'].casefold()=='rhess' for x in list(s['people'].values())+[c['profile'] for c in s['reviewedCandidates'].values()]):
    s['localEncounterCandidates']['rhess']=local_encounters.definition(s,'rhess');s['localEncounters']['rhess'].update(status='introduced',completedOn={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']});arrivals.contact(s,'rhess','ordinary-encounter')
  else:
   saved(s)['finalReturnDay']=s['dayNumber'];rewards.append('The guardian command was '+('repaired with a safe crossing' if saved(s)['resolution']=='repair' else 'retired and its boundary marked for ordinary patrols')+'. Rhess asks to share the closing supper after a night home.')
 s['lastExpeditionReport']={'siteId':site,'approach':'survey','returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
 if e['restoreLanternDisplay']:s['lanternDisplayed']=True
 s['expedition']=None
 for w in party:g.set_character_assignment(s,w,'rest')
 s['lastPhaseSummary']+=rewards;remember(s,'Home from '+SITES[site][0],rewards[-1])
def closing_blockers(s):
 import game as g
 r=saved(s);b=[]
 if 'rhess' not in g.household_members(s) or not g.character_at_castle(s,'rhess'):b.append('Bring Rhess home for the shared supper.')
 if r['completedOn']:b.append('Chapter complete.')
 if not progress(s,WARD)['discoveries']:b.append('Return with the wardstone resolution first.')
 if s['currentDayPhase']!='evening':b.append('Share the closing supper in the evening.')
 if any(s.get('overnightRest',{}).get(w,0)<=r.get('finalReturnDay',10**9) for w in ('founder','rhess')):b.append('Both you and Rhess need a night resting at home after the final expedition before the closing supper.')
 return b
def view(s):
 import campaign_guidance as guide
 import game as g
 r=saved(s)
 return {**deepcopy(r),'next':guide.checked(s,guide.first_patrol(s)),'drillBlockers':drill_blockers(s),'available':available(s),'met':bool(progress(s,TRAIL)['discoveries']),'resident':'rhess' in g.household_members(s),'tower':h.ready(s,'watchtower'),'trailBlockers':departure_blockers(s,TRAIL),'wardBlockers':departure_blockers(s,WARD),'closingBlockers':closing_blockers(s),'nightRestDay':s['overnightRest'].get('founder')}
def register(g):
 h.ROOMS['watchtower']=h.room('Watchtower & signal room','Defence','A castle-linked outpost with a signal lamp, route table and a chair for the guard coming off duty.',('firstPatrol','expeditions'),32,4,('guard-barracks','supply-office'),benefit='A restored route outpost. Shares castle supplies; no separate inventory or hunger meter.')
 for key,(name,description) in SITES.items():
  g['EXPEDITION_SITES'][key]={'id':key,'name':name,'description':description,'approaches':{'survey':{'name':'Follow the patrol route','description':'Saved decisions with safe retreat. Prepared approaches shorten work; every decision remains yours.','reward':'20 shared crowns and 12 provisions on the first completed return.'}}};g['ORIGINAL_ASSETS'][key]='/assets/expeditions/'+key+'.webp'
 g['ORIGINAL_ASSETS']['watchtower']='/assets/rooms/watchtower.webp'
