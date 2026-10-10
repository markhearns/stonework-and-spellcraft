"""Field-earned refinements on the existing signature item and equipment work queue."""
from copy import deepcopy
CHOICES={'edge':('Precision','Add 1 damage per rank to damaging patrol actions.'),'guard':('Shelter','Add 1 personal cover per rank, including when intercepting for someone else.'),'care':('Care','Restore 1 additional vitality per rank with an existing healing action. Does not grant a healing ability.')}
PERSONAL={
 'founder':('Measured casting','spell','Damaging patrol spells deal 1 additional damage per rank.'),
 'mira':('Read the opening','opening','Control actions leave an opening worth 1 additional damage per rank.'),
 'iona':('Covering signal','intercept','Interception adds 1 personal cover per rank.'),
 'koharu':('Steady working hand','task','Objective task actions complete 1 additional task step per rank.'),
 'zahra':('Balanced guard','guarded','Guarded strikes deal 1 additional damage per rank.'),
 'fenna':('Distracting feint','control','Control actions reduce incoming force by 1 additional point per rank.'),
 'kaede':('Controlled impact','technique','Damaging personal techniques deal 1 additional damage per rank.'),
 'tamsin':('Safe footing','task-guard','Objective task actions add 1 personal cover per rank.'),
 'elowen':('Careful treatment','healing','Existing healing actions restore 2 additional vitality per rank, capped at full health.'),
 'nyssara':('Calibrated casting','spell','Damaging patrol spells deal 1 additional damage per rank.'),
 'neris':('Directed current','water','Water and ice patrol spells deal 2 additional damage per rank.'),
 'aurelia':('Hold the shield','intercept','Interception adds 1 personal cover per rank.'),
 'sylva':('Gripping roots','control','Control actions reduce incoming force by 1 additional point per rank.'),
 'sabine':('Cut the opening','opening','Control actions leave an opening worth 1 additional damage per rank.'),
 'velis':('Organised fieldwork','task','Objective task actions complete 1 additional task step per rank.'),
 'rhess':('Watchkeeper’s counter','guarded','Guarded strikes deal 1 additional damage per rank.'),
}

def choices_for(who):
 result=dict(CHOICES)
 if who in PERSONAL:result['personal']=(PERSONAL[who][0],PERSONAL[who][2])
 return result

def personal_effect(s,who):
 return PERSONAL.get(who,('',None,''))[1] if effect(s,who).get('choice')=='personal' else None

def proof_count(h):return len(h.get('enemyTypes',[]))+len(h.get('workTypes',[]))

def record_work(s,who,key,field=False):
 import armoury as a,game as g
 it=item(s,who)
 mode='expedition' if field else 'household'
 if not it or it['location']!='armoury' or a.busy(s,it['id']) or it['id'] not in a.loadout(s,who,mode)['slots'].values():return
 h=deepcopy(history(it,who));old=proof_count(h);types=h.setdefault('workTypes',[])
 if key not in types:types.append(key)
 it['fieldHistory']=h
 if not field:
  for count,rank in ((2,1),(4,2)):
   if old<count<=proof_count(h):g.add_journal(s,it['name']+' has recorded '+str(count)+' different accomplishments. Rank '+str(rank)+' refinement is now available to fund in the Armoury.')

def item(s,who,equipped=False):
 import armoury as a
 sig=a.state(s)['signatures'].get(who,{})
 it=a.state(s)['items'].get(sig.get('itemId'))
 if not sig.get('completedOn') or not it or it['ownerId']!=who or it.get('signatureOwner')!=who:return None
 if equipped and (it['location']!='armoury' or a.busy(s,it['id']) or it['id'] not in a.loadout(s,who,'expedition')['slots'].values()):return None
 return it

def history(it,who):
 h=(it or {}).get('fieldHistory',{})
 return h if h.get('ownerId')==who else dict(ownerId=who,enemyTypes=[],returns=[])
def effect(s,who):
 it=item(s,who,True);r=(it or {}).get('fieldRefinement',{})
 return r if r.get('ownerId')==who else {}

def encounter(s,run):
 # Proofs stay pending on the trip until the character and physical item return.
 import field_magic as f
 key=run['enemies'][run['index']]
 for who in run['party']:
  it=item(s,who,True)
  if not it or f.vitality(s,who)<=0:continue
  rows=run.setdefault('signatureProofs',{}).setdefault(who,dict(itemId=it['id'],enemyTypes=[]))
  if key not in rows['enemyTypes']:rows['enemyTypes'].append(key)

def returned(s,run,complete):
 import armoury as a
 unlocked=[]
 for who in dict.fromkeys(list(run.get('signatureProofs',{}))+list(run.get('signatureCountsBeforeReturn',{}))):
  proof=run.get('signatureProofs',{}).get(who)
  it=item(s,who)
  if not it or (proof and it['id']!=proof['itemId']):continue
  h=deepcopy(history(it,who));old=run.get('signatureCountsBeforeReturn',{}).get(who,proof_count(h))
  if not proof and old==proof_count(h):continue
  h['enemyTypes']=list(dict.fromkeys(h['enemyTypes']+(proof['enemyTypes'] if proof else [])))
  if complete and run['id'] not in h['returns']:h['returns']=(h['returns']+[run['id']])[-3:]
  it['fieldHistory']=h
  if old<2<=proof_count(h):unlocked.append(dict(who=who,itemId=it['id'],name=it['name'],rank=1))
  if old<4<=proof_count(h):unlocked.append(dict(who=who,itemId=it['id'],name=it['name'],rank=2))
 return unlocked

def quote(s,who,choice,rank):
 import game as g,armoury as a,headquarters as hq
 it=item(s,who);b=[];current=(it or {}).get('fieldRefinement',{})
 if current.get('ownerId')!=who:current={}
 current_rank=current.get('rank',0);upgrade=rank>current_rank
 cost=6 if upgrade and rank==1 else 10 if upgrade else 4
 materials={'binding-thread':1} if upgrade and rank==1 else {'moon-glass':1,'binding-thread':1} if upgrade else {}
 if upgrade and rank==2 and choice in ('edge','guard','care','personal'):
  import bounty_contracts
  materials[bounty_contracts.choose(s,bounty_contracts.SIGNATURE_PROPERTIES[choice])]=1
 phases=2 if upgrade else 1
 if not it:b.append('Complete a signature equipment request first.')
 if who not in g.household_members(s) or not all(g.character_at_castle(s,w) for w in ('founder',who)):b.append('Return home together.')
 if not hq.ready(s,'enchanting-room'):b.append('Restore the enchanting room.')
 if who!='founder' and who not in a.state(s)['workAgreements']:b.append('Agree equipment work with this companion in the Armoury first.')
 if who in a.state(s)['jobs']:b.append('Finish or cancel this character’s equipment work.')
 if choice not in choices_for(who) or rank not in (1,2):b.append('Choose an offered refinement and rank.')
 if rank>current_rank+1 or rank<max(1,current_rank):b.append('Install rank one before strengthening it; changing focus keeps the current rank.')
 if proof_count(history(it,who))<(2 if rank==1 else 4):b.append('Record '+str(2 if rank==1 else 4)+' different accomplishments with this completed piece equipped: patrol enemy types, commission types, practical household work or completed field tasks.')
 if current.get('choice')==choice and current_rank==rank:b.append('Already installed.')
 if it and (it['location']!='armoury' or a.busy(s,it['id'])):b.append('Retrieve the signature piece and finish reserved work.')
 if s['sharedFunds']<cost:b.append('Needs '+str(cost)+' shared crowns.')
 for k,n in materials.items():
  if s['materialInventory'].get(k,0)-s['materialReserveTargets'].get(k,0)<n:b.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
 return dict(choice=choice,rank=rank,cost=cost,materials=materials,phases=phases,workPerPhase=2 if rank==2 and s['headquarters']['stock'].get('deep-heat-bench') else 1,blockers=b,itemId=it['id'] if it else None)

def view(s,who):
 it=item(s,who)
 if not it:return None
 current=it.get('fieldRefinement',{})
 if current.get('ownerId')!=who:current={}
 rank=current.get('rank',0);quotes=[]
 for level in ([1] if not rank else [1,2] if rank==1 else [2]):
  for choice,(name,text) in choices_for(who).items():quotes.append({**quote(s,who,choice,level),'name':name,'description':text})
 return dict(itemId=it['id'],itemName=it['name'],history=deepcopy(history(it,who)),proofCount=proof_count(history(it,who)),current=deepcopy(current),currentName=choices_for(who).get(current.get('choice'),('None',))[0],options=quotes)

def apply(s,act):
 import game as g,armoury as a
 if act.get('type')!='gear-signature-refine':return False
 who=act.get('ownerId');a.home(s,who);choice=act.get('choice');rank=act.get('rank')
 g.require(isinstance(choice,str) and choice in choices_for(who) and type(rank) is int and rank in (1,2),'Choose a listed refinement and rank.')
 q=quote(s,who,choice,rank);g.require(not q['blockers'],' '.join(q['blockers']));it=item(s,who)
 s['sharedFunds']-=q['cost']
 for k,n in q['materials'].items():s['materialInventory'][k]-=n
 # Refinement pauses household work and removes the piece from all loadouts.
 for mode in a.MODES:
  load=a.loadout(s,who,mode);load['slots']={k:v for k,v in load['slots'].items() if v!=it['id']};load['active'].pop(it['id'],None)
 it['location']='job';a.state(s)['jobs'][who]=dict(operation='signature-refinement',workerId=who,itemId=it['id'],effect=None,name=it['name']+' · '+choices_for(who)[choice][0],cost=q['cost'],phases=q['phases'],done=0,materials=[k for k,n in q['materials'].items() for _ in range(n)],room='enchanting-room',refinementChoice=choice,refinementRank=rank)
 g.set_character_assignment(s,who,'equipment-work');return True

def finish(s,job):
 import armoury as a,signature_equipment as sig
 it=a.state(s)['items'][job['itemId']];who=job['workerId']
 it['fieldRefinement']=dict(ownerId=who,choice=job['refinementChoice'],rank=job['refinementRank'])
 name,description=choices_for(who)[job['refinementChoice']]
 sig.remember(s,who,'A familiar piece, refined',it['name']+' now carries '+name+' rank '+str(job['refinementRank'])+'. '+description+' Equip it again to use the effect.')
