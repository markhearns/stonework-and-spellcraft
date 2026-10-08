"""Chapter six: a rescued caravan, dependable suppliers and a roadside refuge."""
from copy import deepcopy
import headquarters as h
SITE='hollow-road'
DEFINITION={'id':SITE,'name':'The Hollow Road','description':'An overdue provision wagon waits beyond a washed-out crossing. Help its travellers return, then rebuild a dependable connection.', 'approaches':{'survey':{'name':'Bring the caravan home','description':'One phase out, five saved decisions and one phase home. Ordinary methods are always available; retreat retains paid work.','reward':'24 provisions, 24 crowns, a supplier introduction and Velis’s correspondence, once on a completed return.'}}}
STEPS=[
 ('tracks','A trail off the road','A broken sign and wheel tracks suggest the wagon turned towards an old shelter.','Follow the wheel marks carefully','Read the trail together','dexterity','fieldcraft','sure-footing'),
 ('crossing','The washed-out crossing','The travellers are safe across a narrow wash. Velis has secured a guide rope.','Lay a stable temporary footbridge','Anchor an enchanted safety line','might','athletics','measured-force'),
 ('stand','Hold the shelter door','Two hungry scavengers prowl the outer yard. The travellers need space to get behind the inner gate.','Wait behind cover and lead the animals away','Hold the lane while the travellers pass','resolve','channeling','warded-cover'),
 ('dispute','The disputed shipment','A porter’s copy and the merchant’s receipt disagree. Velis refuses to make someone pay for a clerical error.','Compare the copies with both people','Read the seal and reconcile the account','intelligence','artifice','clear-measure'),
 ('wagon','Everyone, and then the goods','The axle can carry a modest load. Velis wants the people safe before anything else.','Repair the axle and escort everyone home','Brace the axle for the homeward journey','might','athletics','measured-force')]
def initialize(s):
 s.setdefault('roadsWeKeep',{'started':False,'completedOn':None,'refugeDone':False,'agreement':None,'closing':None,'memories':[]})
 s.setdefault('hollowRoad',{'completed':[],'pending':None,'outcomes':[],'discoveries':[]})
def saved(s):return s['roadsWeKeep']
def available(s):return bool(s.get('armsOfOurOwn',{}).get('completedOn'))
def active(s):return bool(s.get('expedition') and s['expedition']['siteId']==SITE)
def progress(s):return s['hollowRoad']
def step(s):return next((d for d in STEPS if d[0] not in progress(s)['completed']),None)
def remember(s,title,text):
 import game as g
 saved(s)['memories'].append({'title':title,'text':text,'day':s['dayNumber']});g.add_journal(s,title+': '+text)
def encounter_view(s):
 import game as g,armoury as a,character_approaches as apt
 d=step(s)
 if not d:return None
 party=g.expedition_party(s);scores={w:apt.score(s,w,apt.spec(d[5],d[6],6),party) for w in party}
 good=[w for w in party if scores[w]['qualified'] and a.has(s,w,d[7],'expedition')]
 c={'patient':{'name':d[3],'phases':2,'description':'Safe ordinary work; no components or special equipment.','blockers':[],'participants':party},'gear':{'name':d[4],'phases':1,'description':'A matching active inscription and approach score 6 shorten this work.','blockers':[] if good else ['A traveller needs '+a.enchantment_name(d[7])+' active and the listed approach score 6.'],'participants':good[:1],'scores':scores}}
 if d[0]=='stand':
  covered=[w for w in party if any('shield' in a.CATALOG[a.state(s)['items'][k]['definitionId']]['tags'] for k in set(a.loadout(s,w)['slots'].values()) if k in a.state(s)['items'])]
  pair=next(([w,v] for w in covered for v in party if v!=w),[])
  c['cover']={'name':'One holds cover; one guides the travellers','phases':1,'description':'Two distinct companions, including someone with a worn shield. No injury or ammunition roll.','blockers':[] if pair else ['Bring a worn shield and a second traveller.'],'participants':pair}
 if d[0]=='dispute':
  good=[w for w in party if g.skill_rank(s,w,'diplomacy')>=1]
  c['talk']={'name':'Hear both accounts and negotiate a fair correction','phases':1,'description':'Diplomacy rank 1; nobody pays for the missing clerk’s mistake.','blockers':[] if good else ['A traveller needs Diplomacy rank 1.'],'participants':good[:1]}
 if d[0] in ('crossing','stand'):
  import field_magic
  form='water-walk' if d[0]=='crossing' else 'calm-tide';caster=field_magic.existing_caster(s,form)
  c['spell']={'name':'Cross with Water walk' if d[0]=='crossing' else 'Quiet the animals with Calming tide','phases':1,'description':'A learned prepared spell; components are committed once when chosen.','castForm':form,'participants':[caster['ownerId']] if caster else [],'blockers':[] if caster else ['Bring a qualified caster with this spell prepared and its components.']}
 for key,row in c.items():
  row['timeSaved']=2-row['phases'];row['equipmentUsed']=[{'ownerId':w,'ownerName':g.character_profile(s,w)['name'],'itemId':e['itemId'],'name':e['name'],'effect':a.enchantment_name(e['effect']),'rank':e['rank']} for w in row.get('participants',[]) for e in a.effects(s,w,'expedition') if key=='gear' and e['effect']==d[7]]
 import personal_paths
 c.update(personal_paths.route_choices(s))
 p=progress(s)['pending'];return {'step':{'id':d[0],'name':d[1],'description':d[2]},'choices':c,'totalSteps':5,'progress':{'completedSteps':progress(s)['completed'][:],'pendingWork':{**deepcopy(p),'remainingWorkPhases':p['remaining']} if p else None}}
def resume(s):
 e=s['expedition'];p=progress(s)['pending']
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p:e.update(stage='working',remainingWorkPhases=p['remaining'])
 else:e['stage']='encounter-choice'
def apply(s,act):
 import game as g
 kind=act.get('type');r=saved(s)
 if kind=='choose-encounter-method' and active(s):
  g.require(s['expedition']['stage']=='encounter-choice','Choose a route when an obstacle awaits.');key=act.get('methodId');choices=encounter_view(s)['choices'];g.require(isinstance(key,str) and key in choices,'Choose an offered method.');c=choices[key];g.require(not c['blockers'],' '.join(c['blockers']))
  if c.get('castForm'):
   import field_magic
   field_magic.commit_existing(s,c)
  progress(s)['pending']={'methodId':key,'remaining':c['phases'],'participants':c['participants'][:],'outcome':deepcopy(c)};resume(s);return True
 if not isinstance(kind,str) or not kind.startswith('roads-'):return False
 g.require(g.character_at_castle(s,'founder'),'Return home for the chapter review.');g.require(available(s),'Conclude Chapter 5 first.')
 if kind=='roads-start':
  g.require(not r['started'],'The chapter has already begun.');r['started']=True;remember(s,'An overdue wagon','A promised supply wagon has missed its arrival. The watch road is open; now the household can help the people who use it.')
 elif kind=='roads-agreement':
  g.require(bool(progress(s)['discoveries']),'Bring the caravan home first.');g.require(not r['agreement'],'The supplier agreement is already recorded.');choice=act.get('choice');g.require(choice in ('food','materials'),'Choose provisions or workshop supplies as your first standing relationship.');r['agreement']=choice;remember(s,'Names behind the goods','You agree dependable terms with the caravan cooperative. Velis keeps both copies identical. Your first priority is '+choice+'.')
 elif kind=='roads-conclude':
  g.require(r['started'] and not r['completedOn'] and bool(progress(s)['discoveries']) and r['agreement'] and h.ready(s,'supply-office') and r['refugeDone'],'Rescue the caravan, agree supplies, restore the Supply Office and complete the roadside refuge.');r['completedOn']={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']};remember(s,'The roads we keep','The refuge has a dry roof, the castle has a receiving desk, and the returning wagon has familiar faces. Velis’s decision about where to live remains her own.')
 else:raise g.RuleError('Unknown Chapter 6 action.')
 return True
def resolve_expedition(s):
 import game as g,provisions,local_encounters,arrivals
 e=s['expedition'];p=progress(s);party=g.expedition_party(s)
 if e['stage']=='working':
  job=p['pending'];c=job['outcome'] if job['outcome'].get('personal') else encounter_view(s)['choices'][job['methodId']]
  if c['blockers'] and not job['outcome'].get('castForm'):e['stage']='encounter-choice';return
  if not all(w in party for w in job['participants']):e['stage']='encounter-choice';return
  job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
  if job['remaining']:return
  d=step(s);record=job['outcome']
  import personal_paths
  personal_paths.resolve_route(s,record,s['lastPhaseSummary'])
  p['outcomes'].append({'stepId':d[0],'name':d[1],'method':record['name'],'participants':job['participants'],'equipmentUsed':record['equipmentUsed'],'timeSaved':record['timeSaved']});p['completed'].append(d[0]);p['pending']=None;resume(s);return
 rewards=['Returned safely. Completed obstacles and paid work remain saved.']
 if e['discoveryReady'] and not p['discoveries']:
  p['discoveries'].append('survey');provisions.add(s,24);wealth=g.distribute_expedition_wealth(s,24);rewards=['The caravan is safe: 24 provisions and 24 crowns returned. Velis offers correspondence; visiting and joining remain separate choices.',wealth]
  if 'velis' not in s['people'] and 'velis' not in s['localEncounterCandidates'] and not any(x['name'].casefold()=='velis' for x in list(s['people'].values())+[c['profile'] for c in s['reviewedCandidates'].values()]):
   s['localEncounterCandidates']['velis']=local_encounters.definition(s,'velis');s['localEncounters']['velis'].update(status='introduced',completedOn={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']});arrivals.contact(s,'velis','ordinary-encounter')
 s['lastExpeditionReport']={'siteId':SITE,'approach':'survey','returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
 if e['restoreLanternDisplay']:s['lanternDisplayed']=True
 s['expedition']=None
 for who in party:g.set_character_assignment(s,who,'rest')
 s['lastPhaseSummary']+=rewards
 remember(s,'The caravan’s return' if p['discoveries'] else 'A safe retreat',rewards[0])
def view(s):
 import campaign_guidance as guide
 import game as g
 r=saved(s);rescued=bool(progress(s)['discoveries'])
 return {**deepcopy(r),'next':guide.checked(s,guide.roads(s)),'available':available(s),'rescued':rescued,'office':h.ready(s,'supply-office'),'resident':'velis' in g.household_members(s),'canConclude':bool(r['started'] and not r['completedOn'] and rescued and r['agreement'] and r['refugeDone'] and h.ready(s,'supply-office'))}
def register(g):
 h.ROOMS['supply-office']=h.room('Supply Office & receiving store','Work','Sample drawers, scales and a receiving counter connect household plans to dependable supplies.',('stores',),28,3,('kitchen',),benefit='Consolidate material orders for delivery in two phases. Ordinary purchases remain available.')
 h.JOBS['roadside-refuge']={'name':'Restore the roadside refuge','room':'supply-office','cost':18,'phases':3,'output':'roadside-refuge','benefit':'A dry shelter and signed route agreement enable optional two-phase patrols: 4 provisions and 2 crowns.'}
 g['EXPEDITION_SITES'][SITE]=DEFINITION
 g['ORIGINAL_ASSETS'].update({SITE:'/assets/expeditions/hollow-road.webp','supply-office':'/assets/rooms/supply-office.webp'})
