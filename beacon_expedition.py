"""A persistent expedition built around voluntary companion participation."""
from copy import deepcopy
import character_approaches as apt
SITE='stormwatch-beacon'
DEFINITION={'id':SITE,'name':'Stormwatch beacon','description':'Restore a coastal warning beacon after a storm. Six connected obstacles with patient solo solutions, specialist techniques, prepared magic and complementary teamwork.', 'approaches':{'survey':{'name':'Relight the warning station','description':'One phase out, six encounters, one phase home. Every obstacle has a free ordinary route. Team methods need two distinct participants. Retreat preserves completed work and unfinished methods.','reward':'Return once with 30 crowns, 2 moon glass, 3 binding thread, and 3 advancement for each returning participant. A companion who returns can invite you to talk about the journey.'}}}

def method(name,phases,text,**kw):return dict(name=name,phases=phases,description=text,**kw)
def specialist(name,attr,skill,text):return method(name,1,text,aptitude=apt.spec(attr,skill))
def team(name,a,b,text):return method(name,1,text,team=[apt.spec(*a,8),apt.spec(*b,8)])
def magic(name,form,text):return method(name,1,text,castForm=form)
STEPS=[
 {'id':'fallen-pine','name':'The pine across the path','description':'A fallen pine blocks the cliff path. Loose branches can be cleared slowly, but its trunk rests under tension.', 'choices':{
 'patient':method('Cut back the branches and clear a walking lane',3,'Three phases. No attributes, supplies or companion required.'),
 'leverage':specialist('Read the load and lever the trunk safely','intelligence','artifice','Use the rocks as fulcrums; one phase, no supplies.'),
 'two-hands':team('Brace the trunk while a partner releases the snag',('might','athletics'),('dexterity','artifice'),'One person holds the load, the other frees the caught branches. One phase; each role needs score 8.'),
 'spell:giant-grasp':magic('Lift the trunk with Giant’s grasp','giant-grasp','A prepared caster lifts the load while the party passes. One phase; listed spell components are paid once.')}},
 {'id':'ravine','name':'The broken keeper’s bridge','description':'The far anchorage survived, but a section of deck hangs below it. The old inspection path remains passable.', 'choices':{
 'patient':method('Follow the lower inspection path',3,'Three phases. Longer, safe, and available alone.'),
 'balance':specialist('Traverse the surviving braces and secure the deck','dexterity','fieldcraft','One phase, no supplies.'),
 'two-hands':team('Anchor the safety line while a partner crosses',('might','athletics'),('dexterity','athletics'),'A strong anchor and a careful climber need score 8 each. One phase.'),
 'spell:borne-flight':magic('Carry the party across with Borne flight','borne-flight','One phase. Only this crossing is resolved; later obstacles remain.')}},
 {'id':'keeper','name':'The keeper who will not hand over the key','description':'The keeper has seen visitors promise repairs and leave. She wants a credible account of what you will do, not a demonstration of power.', 'choices':{
 'patient':method('Listen to her account and agree the repair list',2,'Two phases. A patient conversation works without a social score.'),
 'agreement':specialist('Offer a specific, accountable repair agreement','charisma','diplomacy','One phase. No payment or compelled trust.'),
 'two-hands':team('Explain the fault together and agree who will check it',('intelligence','scholarship'),('charisma','diplomacy'),'Technical understanding and clear delivery, score 8 each. One phase.'),
 'inspection':specialist('Demonstrate the failed warning sequence on her diagram','intelligence','scholarship','One phase. Expertise offers another way to earn access.')}},
 {'id':'flooded-gear','name':'The submerged turning gear','description':'Rain has flooded the drive pit. The gear is intact, but its locking pin must be released before the beacon can turn.', 'choices':{
 'patient':method('Drain the pit through the inspection channel',3,'Three phases; safe and free.'),
 'bypass':specialist('Repair the dry bypass valve','intelligence','artifice','One phase, no diving or supplies.'),
 'two-hands':team('Brace the service arm while a partner withdraws the pin',('vitality','athletics'),('dexterity','artifice'),'Sustained bracing and precise tool handling, score 8 each. Work stays above water; one phase.'),
 'spell:water-breath':magic('Release the pin under Undertide breath','water-breath','One phase. Temporary underwater protection lasts for this encounter.')}},
 {'id':'echo','name':'The last watch still sounding','description':'An old warning echo repeats the night the station failed. Its sound drowns out the timing marks, but it is a memory of a duty, not an enemy to kill.', 'choices':{
 'patient':method('Wait through the cycle and record its quiet intervals',3,'Three phases. Ordinary observation finds a safe working rhythm.'),
 'release':specialist('Reconstruct and speak the completed watch report','intelligence','scholarship','One phase. The remembered duty can finally end.'),
 'two-hands':team('Hold a steady countertone while a partner completes the report',('resolve','channeling'),('charisma','diplomacy'),'Concentration and a clear spoken release, score 8 each. One phase.'),
 'spell:calm-tide':magic('Quiet the warning echo with Calming tide','calm-tide','One phase. The spell quiets this repeating alarm, without altering anyone’s memories.')}},
 {'id':'lens','name':'The turning light','description':'The lens must track freely while its alignment is checked. The keeper waits below for the first complete warning sweep.', 'choices':{
 'patient':method('Mark each stop and align the lens by hand',3,'Three phases. Complete the calibration at an ordinary pace.'),
 'calibrate':specialist('Infer the alignment from the surviving witness marks','intelligence','artifice','One phase, no supplies.'),
 'two-hands':team('Turn the cradle while a partner reads the light',('dexterity','artifice'),('resolve','channeling'),'Precise movement and sustained observation, score 8 each. One phase.'),
 'spell:lucid-sight':magic('Read the alignment under Lucid sight','lucid-sight','Takes one phase and reveals the regulator’s alignment.')}}
]

def initialize(s):s.setdefault('beaconJourney',{'completed':[],'pending':None,'outcomes':[],'discoveries':[]})
def saved(s):return s.get('beaconJourney',{'completed':[],'pending':None,'outcomes':[],'discoveries':[]})
def step(s):return next((d for d in STEPS if d['id'] not in saved(s)['completed']),None)
def is_active(s):return bool(s.get('expedition') and s['expedition']['siteId']==SITE)

def pairing(s,c):
 import game as g
 party=g.expedition_party(s)
 if not c.get('team'):return None
 for first in party:
  for second in party:
   if first!=second and apt.score(s,first,c['team'][0])['qualified'] and apt.score(s,second,c['team'][1])['qualified']:
    if 'casterRole' in c:
     caster=[first,second][c['casterRole']]
     if not any(p['ownerId']==caster and p['formId']==c['castForm'] and p['status']=='learned' and p['id'] in s['preparedSpells'][caster] and all(k in g.character_principles(s,caster) for k in g.SPELL_FORMS[c['castForm']]['requiredPrinciples']) for p in s['spellbook']):continue
    return [first,second]
 return None

def blockers(s,c):
 import game as g
 reasons=g.encounter_choice_blockers(s,c)
 if c.get('team') and not pairing(s,c):
  reasons.append('Two different expedition participants must fill these roles: '+'; '.join(g.character_builds.ATTRIBUTES[r['attribute']]['name']+' + twice '+g.CHARACTER_SKILLS[r['skill']]['name']+' at '+str(r['threshold']) for r in c['team'])+'. Ordinary solo routes remain available.')
 if c.get('castForm') and not caster_for(s,c):reasons.append('The prepared caster must fill the specified casting role and have learned its principles; all spell components are required.')
 return reasons

def view(s):
 if not is_active(s):return None
 d=step(s);p=saved(s)
 progress={**deepcopy(p),'completedSteps':p['completed'][:],'pendingWork':{**deepcopy(p['pending']),'remainingWorkPhases':p['pending']['remaining']} if p['pending'] else None}
 return {'progress':progress,'totalSteps':len(STEPS),'step':deepcopy(d),'choices':{k:{**deepcopy(c),'description':description(c),'blockers':blockers(s,c),'participants':pairing(s,c)} for k,c in d['choices'].items()} if d else {}}

def resume(s):
 e=s['expedition'];p=saved(s)
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p['pending']:
  import game as g
  c=step(s)['choices'][p['pending']['methodId']]
  if c.get('team') and not all(w in g.expedition_party(s) and apt.score(s,w,role)['qualified'] for w,role in zip(p['pending']['participants'],c['team'])):e['stage']='encounter-choice'
  else:e.update(stage='working',remainingWorkPhases=p['pending']['remaining'])
 else:e['stage']='encounter-choice'

def apply(s,action):
 if action.get('type')!='choose-encounter-method' or not is_active(s):return False
 import game as g, field_magic
 e=s['expedition'];d=step(s);key=action.get('methodId')
 g.require(e['stage']=='encounter-choice' and d is not None,'Choose a method when the party reaches the next obstacle.')
 g.require(isinstance(key,str) and key in d['choices'],'Choose an offered beacon method.')
 c=d['choices'][key];reasons=blockers(s,c);g.require(not reasons,' '.join(reasons))
 caster=caster_for(s,c)
 if caster:
  for k,n in g.SPELL_FORMS[c['castForm']]['castingInputs'].items():s['materialInventory'][k]-=n
  caster['castCount']+=1
 saved(s)['pending']={'stepId':d['id'],'methodId':key,'remaining':c['phases'],'participants':pairing(s,c) or g.expedition_party(s),'magicPaid':c.get('castForm')}
 e.update(stage='working',remainingWorkPhases=c['phases']);g.add_journal(s,d['name']+': '+c['name']+'. '+str(c['phases'])+' phase(s).')
 return True

def resolve(s):
 import game as g, companion_participation as company
 e=s['expedition'];p=saved(s);party=g.expedition_party(s)
 if e['stage']=='working':
  job=p['pending']
  for who in party:
   if who not in job.setdefault('contributors',[]):job['contributors'].append(who)
  job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
  if job['remaining']:return
  d=step(s);c=d['choices'][job['methodId']]
  p['completed'].append(d['id']);p['outcomes'].append({'stepId':d['id'],'name':d['name'],'methodId':job['methodId'],'method':c['name'],'participants':job['contributors'][:],'team':bool(c.get('team')),'magic':bool(c.get('castForm'))})
  g.add_journal(s,d['name']+' completed: '+c['name']+'.');s['lastPhaseSummary'].append(d['name']+' completed.');p['pending']=None;resume(s)
 else:
  rewards=['Returned safely. Completed obstacles and any unfinished, paid method are retained.']
  if e['discoveryReady'] and not p['discoveries']:
   p['discoveries'].append('survey');s['materialInventory']['moon-glass']+=2;s['materialInventory']['binding-thread']+=3
   rewards=[g.distribute_expedition_wealth(s,30),'2 moon glass and 3 binding thread deposited. The beacon is warning passing ships again.']
   for who in party:g.award_advancement(s,who,SITE,3,'Returned the restored beacon survey')
  company.returned(s,party,p['outcomes'],e['discoveryReady'])
  s['lastExpeditionReport']={'siteId':SITE,'approach':e['chosenApproach'],'returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
  if e['restoreLanternDisplay']:s['lanternDisplayed']=True
  s['expedition']=None
  for who in party:g.set_character_assignment(s,who,'rest')
  s['lastPhaseSummary']+=rewards

STEPS[1]['choices']['team:wind-step']={**team('Anchor a line while a partner Windsteps to the far brace',('might','athletics'),('dexterity','channeling'),'One phase. A braced anchor and a precise caster cross using a short air impulse instead of sustained flight.'),'castForm':'wind-step','casterRole':1}
STEPS[3]['choices']['team:water-jet']={**team('Drive water off the pin while a partner withdraws it',('resolve','channeling'),('dexterity','artifice'),'One phase. A caster keeps the service pin clear while a partner works the dry tool head.'),'castForm':'water-jet','casterRole':0}

def caster_for(s,c):
 import field_magic as f,game as g
 if not c.get('castForm'):return None
 candidates=[p for p in s['spellbook'] if p['ownerId'] in g.expedition_party(s) and p['formId']==c['castForm'] and p['status']=='learned' and p['id'] in s['preparedSpells'][p['ownerId']]]
 d=g.SPELL_FORMS[c['castForm']]
 candidates=[p for p in candidates if all(k in g.character_principles(s,p['ownerId']) for k in d['requiredPrinciples']) and all(s['materialInventory'][k]>=n for k,n in d['castingInputs'].items())]
 if 'casterRole' in c:
  pair=pairing(s,c)
  candidates=[p for p in candidates if pair and p['ownerId']==pair[c['casterRole']]]
 return candidates[0] if candidates else None

def description(c):
 import game as g
 text=c['description']
 if c.get('castForm'):
  d=g.SPELL_FORMS[c['castForm']]
  text+=' Requires learned, prepared '+d['name']+'. Components committed once: '+' + '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['castingInputs'].items())+'.'
 return text


# Explicit consumers: equipment never raises every check sharing a skill.
STEPS[1]['choices']['balance']['aptitude']['equipmentTags']=['footing']
STEPS[5]['choices']['calibrate']['aptitude']['equipmentTags']=['calibration']
STEPS[4]['choices']['two-hands']['team'][0]['equipmentTags']=['channel-control']
