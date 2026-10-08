"""Chapter five: ordinary equipment, useful enchantment and a bounded expedition."""
from copy import deepcopy
import armoury as a
import headquarters as h
SITE='north-watch-road'
DEFINITION={'id':SITE,'name':'North watch road','description':'Inspect the wet stair, jammed gate, warning seal and watch sentinel. Every obstacle has an ordinary route.', 'approaches':{'survey':{'name':'Reopen the watch road','description':'One phase out, four persistent encounters and one phase home. Retreat retains progress.','reward':'Once: 18 crowns, 1 moon glass and 2 binding thread, deposited on a completed return.'}}}
STEPS=[
 {'id':'steps','target':6,'name':'The rain-cut steps','description':'Rain has cut across the worn stone. A longer path follows the wall.','tag':'footing','attribute':'dexterity','skill':'fieldcraft','effects':['sure-footing'],'ordinary':2,'ordinaryName':'Lay a safe detour','gearName':'Cross on sure footing'},
 {'id':'gate','target':6,'name':'The jammed watch gate','description':'The gate has sagged onto its retaining pin. A measured lift or careful alignment can release it.','tag':'controlled-force','attribute':'might','skill':'athletics','effects':['measured-force'],'ordinary':2,'ordinaryName':'Brace and dismantle carefully','gearName':'Lift with measured force'},
 {'id':'seal','name':'The unstable warning seal','description':'An old warning repeats without a listener. Trace its boundary before isolating it.','tag':'seal-work','attribute':'intelligence','skill':'artifice','effects':['seal-hand','dungeon-keeper'],'ordinary':2,'ordinaryName':'Record the cycle and isolate it','gearName':'Isolate the seal precisely'},
 {'id':'sentinel','name':'The practice sentinel','description':'A neglected training sentinel blocks the watch post. Its padded arm follows a predictable sweep. A service barrier provides a safe retreat.','tag':'channel-control','attribute':'resolve','skill':'channeling','effects':['measured-force','steady-channel'],'ordinary':3,'ordinaryName':'Withdraw behind the barrier and disconnect power','gearName':'Stop the sweep and release the catch'}]
def saved(s):return s.get('armsOfOurOwn')
def available(s):return bool(s.get('keepingHearth',{}).get('completedOn'))
def initialize(s):s.setdefault('watchRoad',{'completed':[],'pending':None,'outcomes':[],'discoveries':[]})
def active(s):return bool(s.get('expedition') and s['expedition']['siteId']==SITE)
def progress(s):return s['watchRoad']
def step(s):return next((x for x in STEPS if x['id'] not in progress(s)['completed']),None)
def remember(s,title,text,people=()):
 import game as g
 saved(s)['memories'].append({'title':title,'text':text,'participants':['founder',*people],**a.stamp(s)});g.add_journal(s,title+': '+text)
def loadout_ready(s,who):
 import game as g
 l=a.loadout(s,who,'expedition')
 try:a.validate_loadout(s,who,l)
 except g.RuleError:return False
 items=[a.state(s)['items'][key] for key in set(l['slots'].values())]
 return bool(any(set(a.CATALOG[i['definitionId']]['tags'])&{'weapon','focus','tool','shield'} for i in items) and 'shirt' in l['slots'] and 'pants' in l['slots'])
def chapter_status(s):
 r=saved(s)
 if not r:return [False,False,False]
 proofs={p['effect'] for p in a.state(s)['proofs'] if p['effect'] in a.ENCHANTS or p['effect'].startswith('legacy')}
 return [bool(r['drillDone']),len(proofs)>=2 and a.state(s)['commissionDelivered'],'survey' in progress(s)['discoveries']]
def guidance(s):
 import game as g, first_hearth as f, keeping_hearth as k
 r=saved(s)
 if not r:return None
 import campaign_guidance as guide
 travel=guide.travel_step(s)
 if travel:return travel
 if not r['drillDone']:
  if r['drill']:return f.funded(s,'drill','The field-loadout review',r['drill']['done'],1,drill_working(s),{'type':'arms-resume-drill'},'armsOfOurOwn')
  return f.step('equip','Review and test field loadouts','Review ordinary starting pieces in the Armoury, save the selected party’s expedition loadouts, then perform the one-phase yard review.','armoury')
 if not chapter_status(s)[1] and 'field-calibration' not in g.character_principles(s,'founder'):
  return guide.principle_step(s,'field-calibration')
 if not h.ready(s,'enchanting-room'):return k.hq_step(s,'hq-build','enchanting-room')
 if not chapter_status(s)[1] and a.state(s)['jobs'].get('founder'):
  p=a.state(s)['jobs']['founder']
  return f.funded(s,'equipment',p['name'],p['done'],p['phases'],a.working(s,'founder'),{'type':'gear-resume-job','workerId':'founder'},'armoury')
 if not chapter_status(s)[1]:return f.step('bench','Make and test two useful enchantments','The 32-crown allocation covers two basic inscriptions plus clay and thread. Sure footing on boots helps the wet steps; Measured force on a staff or weapon helps the gate. Other distinct tested effects also count. Deliver the supplied commission after its two work phases.','armoury')
 if not chapter_status(s)[2]:return f.step('road','Inspect the North watch road','Take your field loadouts and bring the completed report home. Ordinary routes remain available.','expeditions',siteId=SITE)
 return f.step('review','Share the closing review','Record the next household equipment priority. This preference is remembered; it does not grant a stat bonus or start work.','armsOfOurOwn')
def view(s):
 import campaign_guidance as guide
 import game as g
 r=saved(s)
 return {'title':'Arms of Our Own','available':available(s),'record':deepcopy(r),'complete':bool(r and r['completedOn']),'undertakings':[{'title':title,'complete':done} for title,done in zip(('Equipment with a purpose','The inscription bench','The watch road'),chapter_status(s))], 'people':[{'id':w,'name':g.character_profile(s,w)['name'],'atHome':g.character_at_castle(s,w),'loadoutReady':loadout_ready(s,w)} for w in g.household_members(s)],'next':guide.checked(s,guidance(s)) if r and not r['completedOn'] else None,'proofs':len({p['effect'] for p in a.state(s)['proofs']}),'commissionDone':a.state(s)['commissionDelivered'],'canConclude':bool(r and all(chapter_status(s)) and g.character_at_castle(s,'founder'))}
def apply(s,act):
 import game as g
 kind=act.get('type')
 if kind=='choose-encounter-method' and active(s):
  e=s['expedition'];g.require(e['stage']=='encounter-choice','Choose a method when an encounter awaits.')
  choices=encounter_view(s)['choices'];key=act.get('methodId');g.require(isinstance(key,str) and key in choices,'Choose an offered watch-road method.');c=choices[key];g.require(not c['blockers'],' '.join(c['blockers']))
  old=progress(s)['pending']
  if old and old['stepId']==step(s)['id'] and old['methodId']==key:old['participants']=c.get('participants') or g.expedition_party(s)
  else:progress(s)['pending']={'stepId':step(s)['id'],'methodId':key,'remaining':c['phases'],'participants':c.get('participants') or g.expedition_party(s)}
  e.update(stage='working',remainingWorkPhases=progress(s)['pending']['remaining']);return True
 if not isinstance(kind,str) or not kind.startswith('arms-'):return False
 a.home(s);g.require(available(s),'Conclude Keeping the Hearth before opening Chapter 5.');r=saved(s)
 if kind=='arms-start':
  g.require(not r,'This chapter has already begun.');s['armsOfOurOwn']={'party':['founder'],'drillDone':False,'drill':None,'allocation':True,'completedOn':None,'priority':None,'memories':[]};s['sharedFunds']+=32
  remember(s,'The practice that nearly worked','The yard exercise holds the line, but an awkward grip catches on a strap. You set down the padded gear and plan a better fitting. A household study allocation supplies 32 crowns for the first inscriptions. There is no new intrusion.');a.review_starters(s)
 else:
  g.require(r is not None,'Open Arms of Our Own first.');g.require(not r['completedOn'],'This chapter is already concluded.')
  if kind=='arms-party':
   party=act.get('participants');g.require(isinstance(party,list) and 1<=len(party)<=3 and party[0]=='founder' and len(party)==len(set(party)),'Choose the founder and up to two distinct willing companions.')
   for who in party:a.home(s,who)
   g.require(act.get('agreed') is True or len(party)==1,'Agree each companion’s participation.');g.require(not r['drill'],'Finish or cancel the yard review first.');r['party']=party
  elif kind=='arms-drill':
   g.require(not r['drillDone'] and not r['drill'],'The yard review is complete or already underway.');g.require(h.ready(s,'training-yard'),'Restore the training yard first.')
   for who in r['party']:
    a.home(s,who);g.require(loadout_ready(s,who),'Save a valid field implement and shirt/pants protection for every participant.');g.require(g.character_assignment(s,who)=='rest','Free every participant from other work first.')
   r['drill']={'participants':r['party'][:],'done':0}
   for who in r['party']:g.set_character_assignment(s,who,'equipment-review')
  elif kind=='arms-resume-drill':
   g.require(r['drill'],'There is no unfinished yard review.')
   for who in r['drill']['participants']:a.home(s,who)
   for who in r['drill']['participants']:g.set_character_assignment(s,who,'equipment-review')
  elif kind=='arms-cancel-drill':
   g.require(r['drill'],'There is no unfinished yard review.')
   for who in r['drill']['participants']:
    if g.character_assignment(s,who)=='equipment-review':g.set_character_assignment(s,who,'rest')
   r['drill']=None
  elif kind=='arms-conclude':
   g.require(all(chapter_status(s)),'Complete all three undertakings before the closing review.');priority=act.get('priority');g.require(priority in ('defense','utility','commissions'),'Choose defense, utility or commissions.');r.update(completedOn=a.stamp(s),priority=priority)
   people=[w for w in r['party'] if w!='founder' and w in g.household_members(s) and g.character_at_castle(s,w)]
   remember(s,'What we carry','The returned watch-road report lies beside familiar equipment. The changes are small enough to name and reliable enough to trust. Next priority: '+{'defense':'dependable defense','utility':'field utility','commissions':'commissioned craft'}[priority]+'. Personal requests remain open at each resident’s pace.',people)
  else:raise g.RuleError('Unknown Chapter 5 action.')
 return True
def drill_working(s):
 import game as g
 r=saved(s);return bool(r and r['drill'] and all(g.character_at_castle(s,w) and g.character_assignment(s,w)=='equipment-review' and loadout_ready(s,w) for w in r['drill']['participants']))
def resolve_drill(s,summary,eligible):
 import game as g
 if not eligible or not drill_working(s):return
 r=saved(s);people=r['drill']['participants'];r['drillDone']=True;r['drill']=None
 for who in people:g.set_character_assignment(s,who,'rest')
 remember(s,'Equipment with a purpose','The party checks grips, straps and signals in a supervised exercise. You choose two applications to improve at the bench.',[w for w in people if w!='founder']);summary.append('Chapter 5 yard review completed.')
def score(s,who,d,tag=None,attribute=None,skill=None):
 import character_approaches as apt
 target=d.get('target',8);r=apt.score(s,who,apt.spec(attribute or d['attribute'],skill or d['skill'],target));bonus,rows=a.approach_bonus(s,who,[tag or d['tag']])
 if d['id']=='sentinel':bonus=max(bonus,max((e['rank'] for e in a.effects(s,who,'expedition') if e['effect'] in d['effects']),default=0))
 if d['id']=='seal' and a.has(s,who,'dungeon-keeper','expedition'):bonus=max(bonus,1)
 bonus=min(2,bonus);r['total']+=bonus;r['qualified']=r['total']>=target;r['detail']+='; equipment +'+str(bonus)+' = '+str(r['total'])+'/'+str(target);r['equipmentBonus']=bonus;return r
def encounter_view(s):
 import game as g
 if not active(s):return None
 d=step(s);p=progress(s)
 if not d:return None
 party=g.expedition_party(s);scores={who:score(s,who,d) for who in party};qualified=[who for who in party if scores[who]['qualified'] and any(a.has(s,who,e,'expedition') for e in d['effects'])]
 choices={'patient':{'name':d['ordinaryName'],'phases':d['ordinary'],'description':'Safe ordinary work. No equipment effect, score or supplies required. Completed work survives retreat.','blockers':[]},'gear':{'name':d['gearName'],'phases':1,'description':'Active '+', '.join(a.enchantment_name(e) for e in d['effects'])+' and score '+str(d.get('target',8))+'. One field phase; no consumables.','blockers':[] if qualified else ['A participant needs the named active enchantment and score '+str(d.get('target',8))+'.'],'participants':qualified[:1],'scores':scores}}
 if d['id']=='gate':
  sc={w:score(s,w,d,'calibration','intelligence','artifice') for w in party};q=[w for w in party if sc[w]['qualified'] and a.has(s,w,'clear-measure','expedition')]
  choices['measure']={'name':'Realign the retaining pin','phases':1,'description':'Clear measure and Intelligence + twice Artifice at 6.','blockers':[] if q else ['A participant needs active Clear measure and calibration score 6.'],'scores':sc,'participants':q[:1]}
 if d['id']=='sentinel':
  def tags(w):
   keys={k for k in a.loadout(s,w,'expedition')['slots'].values() if a.state(s)['mode'].get(w)=='expedition' and k in a.state(s)['items'] and a.state(s)['items'][k]['ownerId']==w and not a.busy(s,k)};return set().union(*(set(a.CATALOG[a.state(s)['items'][k]['definitionId']]['tags']) for k in keys)) if keys else set()
  pair=next(([w,v] for w in party for v in party if w!=v and ('shield' in tags(w) or a.has(s,w,'warded-cover','expedition')) and 'disarm' in tags(v)),None)
  choices['cover']={'name':'Hold the lane while a partner releases the catch','phases':1,'description':'Two distinct people: one with a shield or active Warded cover, the other with a disarming implement.','blockers':[] if pair else ['Bring two willing participants with cover and a disarming implement.'],'participants':pair}
 for method,c in choices.items():
  c['timeSaved']=d['ordinary']-c['phases']
  effects=set(['clear-measure'] if method=='measure' else ['warded-cover'] if method=='cover' else d['effects'] if method=='gear' else [])
  c['equipmentUsed']=[{'ownerId':w,'ownerName':g.character_profile(s,w)['name'],'itemId':e['itemId'],'name':e['name'],'effect':a.enchantment_name(e['effect']),'rank':e['rank']} for w in (c.get('participants') or []) for e in a.effects(s,w,'expedition') if e['effect'] in effects]
  if method=='cover' and not c['blockers']:
   for who,tag,label in zip(c['participants'],('shield','disarm'),('Cover','Disarm')):
    if tag=='shield' and any(e['ownerId']==who for e in c['equipmentUsed']):continue
    host=next((a.state(s)['items'][k] for k in sorted(set(a.loadout(s,who,'expedition')['slots'].values())) if tag in a.CATALOG[a.state(s)['items'][k]['definitionId']]['tags'] and not a.busy(s,k)),None)
    if host:c['equipmentUsed'].append({'ownerId':who,'ownerName':g.character_profile(s,who)['name'],'itemId':host['id'],'name':host['name'],'effect':label,'rank':0})
 pending=p['pending'];return {'step':deepcopy(d),'choices':choices,'totalSteps':4,'progress':{'completedSteps':p['completed'][:],'pendingWork':{**deepcopy(pending),'remainingWorkPhases':pending['remaining']} if pending else None}}
def resume(s):
 e=s['expedition'];p=progress(s)
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p['pending']:
  c=encounter_view(s)['choices'][p['pending']['methodId']]
  if c['blockers']:e['stage']='encounter-choice'
  else:e.update(stage='working',remainingWorkPhases=p['pending']['remaining'])
 else:e['stage']='encounter-choice'
def resolve_expedition(s):
 import game as g, companion_participation as company
 e=s['expedition'];p=progress(s);party=g.expedition_party(s)
 if e['stage']=='working':
  j=p['pending'];c=encounter_view(s)['choices'][j['methodId']]
  if c['blockers']:e['stage']='encounter-choice';return
  j['remaining']-=1;e['remainingWorkPhases']=j['remaining']
  if j['remaining']:return
  d=step(s);p['completed'].append(d['id']);p['outcomes'].append({'stepId':d['id'],'name':d['name'],'methodId':j['methodId'],'method':c['name'],'participants':j['participants'],'team':j['methodId']=='cover','magic':False,'equipmentUsed':deepcopy(c.get('equipmentUsed',[])),'timeSaved':c.get('timeSaved',0),'scores':{w:deepcopy(c['scores'][w]) for w in j['participants'] if w in c.get('scores',{})}});g.add_journal(s,d['name']+' completed: '+c['name']+'.'+(' '+', '.join(x['ownerName']+'’s '+x['name']+' ('+x['effect']+')' for x in c.get('equipmentUsed',[]))+' helped save '+str(c['timeSaved'])+' work phase(s).' if c.get('equipmentUsed') else ''));p['pending']=None;resume(s)
 else:
  rewards=['Returned safely. Completed watch-road obstacles and unfinished work remain saved.']
  if e['discoveryReady'] and not p['discoveries']:
   p['discoveries'].append('survey');s['materialInventory']['moon-glass']+=1;s['materialInventory']['binding-thread']+=2;rewards=[g.distribute_expedition_wealth(s,18),'1 moon glass and 2 binding thread deposited. The North watch road is open again.']
  company.returned(s,party,p['outcomes'],e['discoveryReady']);s['lastExpeditionReport']={'siteId':SITE,'approach':'survey','returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards,'equipmentOutcomes':deepcopy(p['outcomes'])}
  if e['restoreLanternDisplay']:s['lanternDisplayed']=True
  s['expedition']=None
  for who in party:g.set_character_assignment(s,who,'rest')
  s['lastPhaseSummary']+=rewards
