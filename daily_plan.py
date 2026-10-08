"""Optional, bounded copying goals. Ordinary work and costs remain authoritative."""
from copy import deepcopy

def saved(s):return s.get('dailyPlan',{}).get('income')

def apply(s,a):
 if a.get('type') not in ('plan-income','clear-income-plan'):return False
 import game as g
 g.require(g.character_at_castle(s,'founder'),'Return home before changing your earning plan.')
 if a['type']=='clear-income-plan':
  s.setdefault('dailyPlan',{})['income']=None
  return True
 target=a.get('targetCrowns');g.require(type(target) is int and 1<=target<=10000,'Choose a treasury target between 1 and 10,000 crowns.')
 purpose=g.text_value(a.get('purpose'),100)
 g.require(s['sharedFunds']<target,'You already have enough crowns for this target.')
 g.apply_action(s,{'type':'assign-founder','assignment':'commissions'})
 s.setdefault('dailyPlan',{})['income']={'target':target,'purpose':purpose,'startedDay':s['dayNumber'],'completedOn':None}
 g.add_journal(s,f'Earning plan: copy until the shared treasury holds {target} crowns for {purpose}. Work stops at the target; nothing is purchased automatically.')
 return True

def resolve(s):
 import game as g
 p=saved(s)
 if not p or p['completedOn'] or s['sharedFunds']<p['target']:return
 p['completedOn']={'day':s['dayNumber'],'phase':s['currentDayPhase']}
 if g.character_at_castle(s,'founder') and g.character_assignment(s,'founder')=='commissions':g.set_character_assignment(s,'founder','rest')
 line=f"Funding ready: {p['purpose']}. The treasury holds {s['sharedFunds']} crowns; target {p['target']}. Review and fund the project when ready."
 s['lastPhaseSummary'].append(line);g.add_journal(s,line)

def view(s):
 import game as g
 p=saved(s)
 if not p:return None
 missing=max(0,p['target']-s['sharedFunds']);rate=g.copying_income(s)
 return {**deepcopy(p),'funds':s['sharedFunds'],'shortfall':missing,'income':rate,
         'status':'complete' if p['completedOn'] else 'working' if g.character_at_castle(s,'founder') and g.character_assignment(s,'founder')=='commissions' else 'paused',
         'copyingPhases':(missing+rate-1)//rate,'atHome':g.character_at_castle(s,'founder')}
