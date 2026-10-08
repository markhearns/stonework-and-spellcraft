"""Return recovery, bounded resident moments and explicit repeat preparation."""
from copy import deepcopy
from conversation_voice import voice

OCCASIONS={
 'care':('Ask how to prepare for the next injury.', '“Keep the healing supplies where the person using them can reach them. Before we leave, I want that person to point to the pocket or pouch they will use.”'),
 'cover':('Ask how the party can make covering easier.', '“Someone stepping between an attacker and a companion needs room to move. Next time, let us choose who covers whom before the path narrows.”'),
 'rare':('Ask what to record about the creature.', '“Record its movement and the response we chose. A name in a bestiary is useful; an account of what actually happened is what the next party can compare with their own encounter.”'),
}

def returned(s,run,report):
 import companion_participation as cp
 cp.initialize(s)
 for who in run['party']:
  if who=='founder':continue
  stats=run.get('contributions',{}).get(who,{})
  occasion='rare' if any(o.get('rewarded') and o['enemyId'] in ('griffin','ember-hound') for o in run['outcomes']) else 'care' if stats.get('healed',0)>0 else 'cover' if stats.get('protected',0)>0 else None
  if not occasion:continue
  key='patrol-moment:'+who+':'+occasion
  cp.saved(s)['events'].setdefault(key,dict(id=key,who=who,title={'rare':'After an unfamiliar creature','care':'The care that made a difference','cover':'Taking the exposed position'}[occasion],kind='patrol-moment',day=s['dayNumber'],reported='founder' not in run['party'],occasion=occasion,patrolName=run['name'],enemyNames=[o['name'] for o in run['outcomes'] if o.get('rewarded') and o['enemyId'] in ('griffin','ember-hound')],healed=stats.get('healed',0),protected=stats.get('protected',0)))

def dialogue(s,e):
 import game as g
 name=g.character_profile(s,e['who'])['name'];v=voice(e['who']);occasion=e.get('occasion','rare')
 label,observation=OCCASIONS[occasion]
 fact=(name+' restored '+str(e['healed'])+' vitality during the patrol.' if occasion=='care' and e.get('healed') else name+' intercepted attacks that would have caused '+str(e['protected'])+' vitality loss to companions.' if occasion=='cover' and e.get('protected') else 'The report records the encounter with '+', '.join(e['enemyNames'])+'.' if e.get('enemyNames') else {'care':'The patrol record includes healing given to the party.','cover':'The patrol record includes protection given to companions.','rare':'The patrol record includes an encounter with an unusual creature.'}[occasion])
 opening=name+(' brings you the patrol report; you were at the castle during the outing. ' if e['reported'] else ' opens the return report with you. ')+fact+' '+v['review']
 return opening,{
  'notice':{'label':label,'response':observation+' '+v['credit']},
  'prepare':{'label':'Ask what she would check before another patrol.','response':v['proposal']+' You leave the suggestion beside the report to review before departure.'},
  'rest':{'label':'Close the report and share a drink.','response':v['company']}}

def view(s):
 import field_patrols as p,field_magic as f,game as g,provisions
 reports=p.saved(s)['reports']
 if not reports:return None
 r=reports[-1];rows=[]
 for who in r['party']:
  if who not in g.household_members(s):continue
  health=f.vitality(s,who);home=g.character_at_castle(s,who);assignment=g.character_assignment(s,who)
  rows.append(dict(id=who,name=g.character_profile(s,who)['name'],vitality=health,atHome=home,resting=home and assignment=='rest',needsSleep=s.get('overnightRest',{}).get(who,0)<=r['returnedDay'],dayHealing=1 if provisions.short(s) else 1+int(bool(s['headquarters']['stock'].get('recovery-ward'))),nightHealing=1 if provisions.short(s) else 3+int(bool(s['headquarters']['stock'].get('recovery-ward'))),roles=deepcopy(r.get('contributions',{}).get(who,{}))))
 b=[]
 if not g.character_at_castle(s,'founder'):b.append('Return home to organize recovery.')
 if any(not x['atHome'] for x in rows):b.append('Bring the whole returning party home first.')
 if len(rows)!=len(r['party']):b.append('A former party member no longer lives here.')
 return dict(reportId=r['id'],name=r['name'],route=r.get('route','road'),mission=r.get('mission'),rows=rows,blockers=b,visible=not p.saved(s).get('dismissedReturn')==r['id'] and not p.saved(s)['active'] and s['dayNumber']<=r['returnedDay']+2,unlocks=deepcopy(r.get('signatureUnlocks',[])),complete=r['complete'],loot=deepcopy(r['loot']))

def apply(s,act):
 import game as g,field_patrols as p
 kind=act.get('type')
 if kind not in ('watch-rest-party','watch-dismiss-return'):return False
 v=view(s);g.require(v is not None and type(act.get('reportId')) is int and act['reportId']==v['reportId'],'Review the latest return report first.')
 if kind=='watch-dismiss-return':p.saved(s)['dismissedReturn']=v['reportId'];return True
 g.require(not v['blockers'],' '.join(v['blockers']))
 for who in [r['id'] for r in v['rows']]:g.set_character_assignment(s,who,'rest')
 g.add_journal(s,'Patrol recovery: '+', '.join(r['name'] for r in v['rows'])+' assigned to Rest. Advance performs recovery; existing project progress is kept.')
 return True
