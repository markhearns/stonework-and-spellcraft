"""Readable enemy intentions and one shared preview/resolution calculation.

Existing equipment and prepared personal paths determine roles; there is no
second talent tree or combat currency. All functions here are read-only.
"""
from copy import deepcopy
PROTECT={'spear-watch','relief-signal','scholar-ward','iona-signal','aurelia-turn','aurelia-catch','brakka-hold','brakka-answer','nyssara-buffer'}
CONTROL={'disarming-turn','tamsin-snare','maren-wedge','sylva-anchor','sylva-draw','scholar-unbinding','iona-sever','mira-afterimage','fenna-close','velis-cover','elowen-balance','neris-reflect'}
import bestiary
PATTERNS={key:d['patterns'] for key,d in bestiary.ENCOUNTERS.items()}

def intent(s,run):
 import field_magic as f,field_patrols as p
 if run['index']>=len(run['enemies']):return None
 party=[w for w in run['party'] if f.vitality(s,w)>0]
 if not party:return None
 turn=run.get('round',0);key=run['enemies'][run['index']];name,extra,pierce,target=PATTERNS[key][turn%3]
 who=party[0] if target=='front' else min(party,key=lambda w:f.vitality(s,w)) if target=='weak' else party[turn%len(party)]
 return dict(name=name,target=who,attack=p.ENEMIES[key]['attack']+extra,pierce=pierce,round=turn+1)

def defence(s,who,party):
 import field_patrols as p,armoury as a,signature_growth as growth
 tags=p.equipment(s,who);sources=[]
 if tags & {'shield','protection'}:sources.append(('Armour or shield',1))
 if a.has(s,who,'warded-cover','expedition'):sources.append(('Warded cover',1))
 shared,why=p.cover(s,party)
 if shared:sources.append(('Party cover (cap 3)',shared))
 refine=growth.effect(s,who)
 if refine.get('choice')=='guard':sources.append(('Signature shelter',refine['rank']))
 import practical_projects,field_patrols
 run=field_patrols.saved(s)['active']
 if run and not run.get('retaliationSeen',run.get('round',0)>0) and 'brakka' in party and practical_projects.active(s,'brakka'):sources.append(('Brakka’s fitted straps: first attack',1))
 return sum(n for _,n in sources),[name+' +'+str(n) for name,n in sources]

def enrich(s,run,rows):
 import personal_paths as paths,signature_growth as growth
 for row in rows:
  key=row['id'].split(':',1)[-1];fx=row.get('effects',{});refine=growth.effect(s,row['who'])
  row['actionGuard']=row.get('actionGuard',2 if row['kind']=='protect' else fx.get('block',0) if row['kind']=='technique' else 1 if key=='guard' else 0)
  row['counter']=fx.get('counter',0)
  if row['kind']=='technique':row['damage']=max(0,row['damage']-row['counter'])
  row['protect']=key in PROTECT or row['kind']=='protect'
  row['control']=key in CONTROL
  row['role']='Objective work' if row.get('objectiveStep') else 'Protection' if row['protect'] else 'Control' if row['control'] else 'Healing' if fx.get('healsAlly') or row.get('spellKind')=='heal' else 'Negotiation' if row['kind']=='peace' else 'Route' if row['kind']=='bypass' else 'Damage'
  if refine.get('choice')=='edge' and row['damage']>0:row['damage']+=refine['rank'];row['signatureDamage']=refine['rank']
  row['healingBonus']=refine['rank'] if refine.get('choice')=='care' else 0
  special=growth.personal_effect(s,row['who']);rank=refine.get('rank',0)
  extra=rank if ((special=='spell' and row['kind']=='spell' and row['damage']>0) or (special=='technique' and row['kind']=='technique' and row['damage']>0) or (special=='guarded' and key=='guard')) else 2*rank if special=='water' and row.get('spellKind') in ('water','ice') else 0
  row['damage']+=extra
  if extra:row['personalDamage']=extra
  if special=='intercept' and row['protect']:row['actionGuard']+=rank
  if special=='task-guard' and row.get('objectiveStep'):row['actionGuard']+=rank
  if special=='healing':row['healingBonus']+=2*rank
  row['controlBonus']=rank if special=='control' else 0
  row['openingBonus']=rank if special=='opening' else 0
  import field_objectives
  field_objectives.enrich(s,run,row)
  row['preview']=preview(s,run,row)
 return rows

def preview(s,run,row):
 import field_magic as f,field_patrols as p
 health={w:f.vitality(s,w) for w in run['party']};before=health.copy();who=row['who'];hit=row['damage'];fx=row.get('effects',{});incoming=intent(s,run)
 peaceful=row['kind'] in ('peace','bypass');healing=[];parts=[]
 health[who]=max(0,health[who]-row['cost'])
 enemy_armour=p.ENEMIES[run['enemies'][run['index']]].get('armour',0) if row['kind']!='spell' else 0
 if hit>0 and enemy_armour:
  reduced=min(enemy_armour,max(0,hit-1));hit-=reduced;parts.append('Creature plates reduce physical damage by '+str(reduced)+'. Physical attacks still deal at least 1 damage.')
 opening=(int(run.get('opening') or 0) if hit>0 else 0)
 hit+=opening
 hp=max(0,run['hp']-hit)
 counter=min(hp,row.get('counter',0)) if hp>0 else 0;hp-=counter;hit=min(run['hp'],hit+counter)
 if peaceful:hp=0;hit=0
 heal=3 if row.get('spellKind')=='heal' else fx.get('healsAlly',0)
 targets=run['party'] if row.get('spellKind')=='heal' else [w for w in run['party'] if w!=who]
 if heal and targets:
  target=min(targets,key=lambda w:health[w]);amount=min(6-health[target],heal+row.get('healingBonus',0));health[target]+=amount
  if amount:healing.append(dict(who=target,amount=amount))
 target=incoming['target'] if incoming else who;original=target
 if row.get('protect') and health[who]>0:target=who
 party=[w for w in run['party'] if health[w]>0]
 block,defence_parts=defence(s,target,party);parts+=defence_parts
 # The base row includes the actor's old passive defence. Only its action guard
 # belongs to that actor; another targeted member uses their own equipment.
 actor_base,_=defence(s,who,party)
 action_guard=row.get('actionGuard',max(0,row['block']-actor_base))
 if target==who:block+=action_guard;parts.append('Selected action +'+str(action_guard))
 # Ice suppresses the whole retaliation, including attacks at another member.
 cancelled=peaceful or not hp or row.get('spellKind')=='ice' or row.get('avoidAttack',False)
 reduction=2+row.get('controlBonus',0) if row.get('control') else 0
 attack=max(0,(incoming['attack'] if incoming else 0)-reduction)
 pierce=incoming['pierce'] if incoming else 0
 effective=max(0,block-pierce)
 injury=0 if cancelled else min(health[target],max(0,attack-effective))
 prevented=0
 if row.get('protect') and original!=target and not cancelled:
  old_block,_=defence(s,original,party);prevented=max(0,attack-max(0,old_block-pierce))
 health[target]=max(0,health[target]-injury)
 restore=fx.get('restoresSelf',0)
 if restore:
  amount=min(6-health[who],restore+row.get('healingBonus',0));health[who]+=amount
  if amount:healing.append(dict(who=who,amount=amount))
 if row.get('control'):parts.append('Control reduces incoming force by '+str(reduction)+' and opens the next damaging action (+'+str(1+row.get('openingBonus',0))+').')
 if opening:parts.append('Previous opening +'+str(opening)+' damage.')
 if row.get('personalDamage'):parts.append('Personal signature refinement +'+str(row['personalDamage'])+' damage.')
 if row.get('signatureDamage'):parts.append('Signature precision +'+str(row['signatureDamage'])+' damage.')
 if row.get('healingBonus'):parts.append('Signature care +'+str(row['healingBonus'])+' healing when needed.')
 return dict(enemyAfter=hp,damage=hit,healthAfter=health,healthBefore=before,target=target,originalTarget=original,injury=injury,healing=healing,intercepted=bool(row.get('protect') and original!=target),protectedDamage=prevented,controlReduction=reduction if not cancelled else 0,opening=(1+row.get('openingBonus',0)) if row.get('control') and hp else False,attack=attack,pierce=pierce,cover=block,effectiveCover=effective,cancelled=cancelled,exertion=row['cost'],breakdown=parts)

def roles(s,who):
 import personal_paths as paths,field_patrols as p,game as g
 techniques=paths.record(s,who)['techniques'];result=[]
 if set(techniques)&PROTECT or 'shield' in p.equipment(s,who):result.append('Protection')
 if set(techniques)&CONTROL:result.append('Control')
 if any(paths.effect(s,who,k).get('healsAlly') for k in techniques) or any(x['ownerId']==who and x['status']=='learned' and x['id'] in s['preparedSpells'].get(who,[]) and g.SPELL_FORMS[x['formId']].get('field')=='heal' for x in s['spellbook']):result.append('Healing')
 if 'weapon' in p.equipment(s,who) or any(paths.CATALOG[k].get('damage',0)>=3 for k in techniques):result.append('Damage')
 return result or ['Generalist']


def path_note(key):
 if key in PROTECT:return 'Patrol role: Protection. Intercepts the visible enemy attack for the threatened companion; the actor uses their own gear and this technique’s guard.'
 if key in CONTROL:return 'Patrol role: Control. Reduces this attack’s force by 2 and opens the next damaging action for +1 damage.'
 return ''
