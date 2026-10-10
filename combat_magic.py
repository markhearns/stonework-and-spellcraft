"""Explicit patrol spells and consumable expedition preparations; pure shared previews."""
from copy import deepcopy
SPELLS={
 'stoneguard':dict(name='Stoneguard',ideas=['Stone','Shelter'],principles=['settling-flow','gentle-preservation'],inputs={'porous-clay':1,'binding-thread':1},effect='Give one selected party member +3 cover for this exchange and the next two. Cover reduces attacks against that member, including intercepted attacks. Does not prevent a basilisk gaze or poison directly.'),
 'gust-strike':dict(name='Gust strike',ideas=['Air','Impulse'],principles=['field-calibration'],inputs={'binding-thread':1},effect='Deal 2 damage, reduce this retaliation’s force by 2, and give the next damaging action +1 damage. Grounds a wyvern for this exchange and the next two; clears the party’s harpy imbalance.'),
 'binding-snare':dict(name='Binding snare',ideas=['Binding','Restraint'],principles=['joined-fibres','field-calibration'],inputs={'binding-thread':2},effect='Reduce a living enemy’s attack force by 2 for this exchange and the next two. Does not work on constructs, undead or insubstantial wisps. Does not capture or recruit anyone.'),
 'purifying-light':dict(name='Purifying light',ideas=['Light','Preservation'],principles=['luminous-copying','gentle-preservation'],inputs={'silver-ivy':1,'moon-glass':1},effect='Restore 1 vitality to a selected party member and clear venom, stone stiffness, corrosion and imbalance before retaliation. Works on an afflicted member at full vitality. Physical holds remain.'),
 'dispel-ward':dict(name='Dispel ward',ideas=['Reference','Unbinding'],principles=['reference-binding','field-calibration'],inputs={'moon-glass':1},effect='Disconnect up to two colossus ward plates; reveal a wisp or track a blink lynx for the next two exchanges; suppress physical creature armour for this exchange and the next two. Requires one of those defenses to be present.'),
 'chain-lightning':dict(name='Chain lightning',ideas=['Charge','Linked paths'],principles=['steady-hearth-wards','field-calibration','reference-binding'],inputs={'fireglass':2,'binding-thread':1},effect='Deal 5 lightning damage, or 7 to constructs. Extra arcs add 2 damage against raider groups or a hydra, and disconnect up to two colossus ward plates. Active ward plates still cap the current hit at 1. A single ordinary creature gives no extra arc damage.'),
}
RITUALS={
 'expedition-warding':dict(name='Expedition warding',room='library',principles=['settling-flow','reference-binding'],cost=10,phases=2,materials={'porous-clay':2,'binding-thread':1},effect='Prepare one outgoing patrol: every party member gains +1 cover for its first three committed exchanges. All remaining charges end on return or retreat. Does not stack with another preparation of this ritual.',repeatable=True),
 'antivenom-preparation':dict(name='Antivenom preparation',room='common-room',principles=['gentle-preservation','steady-growth'],cost=8,phases=2,materials={'silver-ivy':2,'porous-clay':1},effect='Prepare two shared antidote doses for the next outgoing patrol. Each dose prevents one new manticore or wyvern venom application. Unused doses end on return or retreat. Does not prevent the initial attack or stone stiffness.',repeatable=True),
}

def install(g):
 import lasting_rituals
 for key,d in SPELLS.items():
  g.SPELL_FORMS[key]=dict(name=d['name'],ideas=d['ideas'],requiredPrinciple=d['principles'][0],requiredPrinciples=d['principles'],requiredProperties=['vessel','binding'],roomId='library',description=d['effect'],effect=d['effect'],castingInputs=d['inputs'],materialOutput={},crownsOutput=0,field=key,limits='For field patrols, bounties, recruitment quests and Chapter 8 encounters. Learn, test and prepare personally. Costs use unreserved supplies. Timed effects change only on committed exchanges and end with the encounter.')
 lasting_rituals.CATALOGUE.update(deepcopy(RITUALS))

def state(run):return deepcopy(run.get('combatMagic',{'wards':{},'bound':0,'unwarded':0}))
def preparations(run):return deepcopy(run.get('preparations',{'warding':0,'antivenom':0}))
def depart(s,run):
 prepared=s.setdefault('fieldPreparations',{})
 run['preparations']={}
 for key,charge,n in [('expedition-warding','warding',3),('antivenom-preparation','antivenom',2)]:
  run['preparations'][charge]=n if prepared.pop(key,None) else 0

def rows(s,run):
 import game as g,field_magic as f,bestiary,creature_challenges as c
 d=bestiary.encounter(s,run);able=[w for w in run['party'] if f.vitality(s,w)>0];result=[];magic=state(run);st=c.state(s,run)
 for spell in s['spellbook']:
  kind=spell['formId'];who=spell['ownerId']
  if kind not in SPELLS or who not in able or spell['status']!='learned' or spell['id'] not in s['preparedSpells'].get(who,[]):continue
  form=g.SPELL_FORMS[kind];b=[]
  if any(pr not in g.character_principles(s,who) for pr in form['requiredPrinciples']):b.append('Learn all required principles.')
  for k,n in form['castingInputs'].items():
   if s['materialInventory'][k]-s['materialReserveTargets'][k]<n:b.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
  damage=2 if kind=='gust-strike' else (7 if d['enemy']=='construct' else 5)+(2 if d.get('roleId') or c.key(run)=='marsh-hydra' else 0) if kind=='chain-lightning' else 0
  if kind=='binding-snare' and (d['enemy']!='living' or c.key(run)=='will-o-wisp'):b.append('Needs a solid living target; this enemy cannot be held by the snare.')
  if kind=='binding-snare' and magic['bound']:b.append('The existing snare still has '+str(magic['bound'])+' exchanges remaining.')
  if kind=='dispel-ward' and not (d.get('armour') or c.key(run) in ('runebound-colossus','will-o-wisp','blink-lynx')):b.append('This enemy has no applicable ward, concealment or physical armour to suppress.')
  if kind=='dispel-ward' and c.key(run)=='runebound-colossus' and not st.get('wards'):b.append('All ward plates are already disconnected.')
  if kind=='dispel-ward' and magic['unwarded'] and c.key(run)!='runebound-colossus':b.append('The defense is already suppressed for '+str(magic['unwarded'])+' more exchanges.')
  targets=run['party'] if kind in ('stoneguard','purifying-light') else [None]
  for target in targets:
   blocked=b[:];extra={};label=form['name']
   if target:
    label+=' · '+g.character_profile(s,target)['name']
    if kind=='stoneguard':
     extra['magicGuardTarget']=target
     if f.vitality(s,target)<=0:blocked.append('Choose a conscious party member to protect.')
     if magic['wards'].get(target):blocked.append('Stoneguard is already active on this member.')
    else:
     extra.update(purifyTarget=target,treatmentAmount=1)
     afflicted=any(st.get(k,{}).get(target) for k in ('venom','stiffness','corrosion','imbalance'))
     if f.vitality(s,target)>=6 and not afflicted:blocked.append('This member has full vitality and no removable condition.')
   result.append(dict(id=who+':spell:'+spell['id']+((':'+target) if target else ''),who=who,name=label,damage=damage,block=0,actionGuard=0,cost=0,kind='spell',spellId=spell['id'],spellKind=kind,inputs=deepcopy(form['castingInputs']),blockers=blocked,challengeControl=kind=='gust-strike',**extra))
 return result

def cover(s,run,who):
 if not run:return 0,[]
 amount=0;notes=[]
 if state(run)['wards'].get(who):amount+=3;notes.append('Stoneguard +3')
 if preparations(run).get('warding'):amount+=1;notes.append('Expedition warding +1')
 return amount,notes

def prepare(s,run,original):
 row=deepcopy(original);old=state(run);st=deepcopy(old);prep=preparations(run)
 st['wards']={w:n-1 for w,n in old['wards'].items() if n>1};st['bound']=max(0,old['bound']-1);st['unwarded']=max(0,old['unwarded']-1)
 kind=row.get('spellKind')
 if kind=='stoneguard':st['wards'][row['magicGuardTarget']]=2;row['extraCover']={row['magicGuardTarget']:3}
 if kind=='binding-snare':st['bound']=2
 row['magicAttackReduction']=2 if old['bound'] or kind=='binding-snare' else 0
 if kind=='dispel-ward':st['unwarded']=2
 if old['unwarded'] or kind=='dispel-ward':row['ignoreCreatureArmour']=True
 prep['warding']=max(0,prep.get('warding',0)-1)
 return row,st,prep

def finish(s,run,row,result):
 notes=result.setdefault('challengeNotes',[]);kind=row.get('spellKind')
 if kind=='stoneguard':notes.append('Stoneguard protects the selected member now and for the next two exchanges.')
 if kind=='binding-snare':notes.append('The snare reduces attack force by 2 now and for the next two exchanges.')
 if kind=='dispel-ward':notes.append('Physical creature armour is suppressed now and for the next two exchanges.')
 if row.get('magicAttackReduction'):result['breakdown'].append('Binding snare reduces attack force by 2.')
 return result

def view(s,run):
 import game as g
 st=state(run);prep=preparations(run);notes=[]
 for who,n in st['wards'].items():
  if n:notes.append(g.character_profile(s,who)['name']+': Stoneguard +3 cover for '+str(n)+' further exchanges.')
 if st['bound']:notes.append('Binding snare: enemy force -2 for '+str(st['bound'])+' further exchanges.')
 if st['unwarded']:notes.append('Creature armour suppressed for '+str(st['unwarded'])+' further exchanges.')
 if prep.get('warding'):notes.append('Expedition warding: everyone has +1 cover for '+str(prep['warding'])+' further exchanges.')
 if prep.get('antivenom'):notes.append('Antivenom preparation: '+str(prep['antivenom'])+' shared doses remain.')
 return notes
