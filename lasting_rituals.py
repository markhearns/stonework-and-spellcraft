"""Costed, two-person, permanent household rituals with explicit suspension."""
from copy import deepcopy
import character_approaches as aptitudes
CATALOGUE={
 'archive-circle':{'name':'Circle of concordant study','room':'library','principles':['reference-binding','clear-instruction'],'cost':60,'phases':5,'materials':{'moon-glass':2,'binding-thread':2},'effect':'+1 core research/archive contribution per assigned worker; +1 work on personal principle/practice studies. Does not grant knowledge, advancement, retraining or attribute ranks.'},
 'maker-circle':{'name':'The patient workshop','room':'workshop','principles':['joined-fibres','steady-hearth-wards'],'cost':60,'phases':5,'materials':{'fireglass':2,'binding-thread':2},'effect':'+1 core artifact work per maker and +1 work on public artifact jobs. Recipes, ownership and component costs remain required.'},
 'garden-circle':{'name':'The unhurried season','room':'conservatory','principles':['steady-growth','water-guidance'],'cost':50,'phases':4,'materials':{'silver-ivy':3,'porous-clay':2},'effect':'+1 ivy or +2 crowns per staffed garden harvest. No bonus to an unattended root tender or spell production.'},
 'sanctuary-circle':{'name':'Hearth of restoration','room':'common-room','principles':['gentle-preservation','steady-growth'],'cost':40,'phases':4,'materials':{'sun-amber':2,'silver-ivy':2},'effect':'Residents assigned to rest at home recover 3 vitality per phase instead of 1, up to 6. Does not heal travelling residents or resurrect anyone.'},
 'market-circle':{'name':'The fair exchange','room':'common-room','principles':['clear-instruction','reference-binding'],'cost':75,'phases':5,'materials':{'moon-glass':2,'binding-thread':2},'effect':'Finite-stock public material purchases cost 1 crown less per unit, minimum 1; ordinary copying earns +1 crown per phase. Core buy/sell quotes remain unchanged to prevent resale loops. Gifts, recruitment decisions and relationship choices are unchanged.'},
 'anchor-circle':{'name':'The homeward anchor','room':'library','principles':['courteous-passage','field-calibration'],'cost':80,'phases':6,'materials':{'moon-glass':3,'fireglass':2},'effect':'Threshold fold consumes 1 moon glass instead of 2. Still requires a learned prepared spell, an existing journey and a previously reached outbound destination.'},
 'welcome-circle':{'name':'The steady threshold','room':'common-room','principles':['courteous-passage','gentle-preservation'],'cost':60,'phases':5,'materials':{'sun-amber':2,'binding-thread':3},'effect':'+1 work per assigned Open Threshold preparation phase. Invitations, visits, housing, personal decisions and consent remain separate.'},
 'foundation-circle':{'name':'The settled house','room':'workshop','principles':['settling-flow','field-calibration'],'cost':70,'phases':5,'materials':{'porous-clay':3,'fireglass':2},'effect':'+1 work per funded housing, living-facility, conservatory restoration and headquarters room-construction phase. Does not accelerate drills, installations or another ritual.'},
}

def active(s,key):return bool(s.get('lastingRituals',{}).get('completed',{}).get(key,{}).get('active'))
def state(s):return s.get('lastingRituals',{'project':None,'completed':{}})
def initialize(s):return s.setdefault('lastingRituals',{'project':None,'completed':{}})
def blockers(s,key,leader,partner):
 import game as g,headquarters as h
 d=CATALOGUE[key];r=[];members=g.household_members(s)
 if state(s)['project']:r.append('Finish or cancel the current household ritual first.')
 if key in state(s)['completed']:r.append('This lasting ritual is already inscribed; use its activation control.')
 if leader not in members or partner not in members or leader==partner:r.append('Choose two different resident participants.')
 else:
  if not all(g.character_at_castle(s,p) for p in ('founder',leader,partner)):r.append('Return home with both participants.')
  if not all(p in g.character_principles(s,leader) for p in d['principles']):r.append('The conductor must have learned both principles.')
  if not any(p in g.character_principles(s,partner) for p in d['principles']):r.append('The partner must have learned at least one of the ritual principles.')
 if not h.ready(s,d['room']):r.append('Restore '+h.ROOMS[d['room']]['name']+'.')
 if s['sharedFunds']<d['cost']:r.append('Needs '+str(d['cost'])+' shared crowns.')
 for k,n in d['materials'].items():
  if s['materialInventory'][k]-s['materialReserveTargets'][k]<n:r.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
 return r

def apply(s,a):
 kind=a.get('type')
 if kind not in ('begin-lasting-ritual','resume-lasting-ritual','cancel-lasting-ritual','toggle-lasting-ritual'):return False
 import game as g
 g.require(g.character_at_castle(s,'founder'),'Return home to arrange a household ritual.')
 key=a.get('ritualId');g.require(isinstance(key,str) and key in CATALOGUE,'Choose an authored ritual.')
 d=CATALOGUE[key];r=state(s)
 if kind=='toggle-lasting-ritual':
  g.require(key in r['completed'] and type(a.get('active')) is bool,'Choose an inscribed ritual and its active state.')
  r['completed'][key]['active']=a['active'];return True
 if kind=='begin-lasting-ritual':
  leader=a.get('leaderId');partner=a.get('partnerId');g.require(isinstance(leader,str) and isinstance(partner,str),'Choose the participants.')
  reasons=blockers(s,key,leader,partner);g.require(not reasons,' '.join(reasons))
  participants=[leader,partner];previous={p:g.character_assignment(s,p) for p in participants}
  s['sharedFunds']-=d['cost']
  for k,n in d['materials'].items():s['materialInventory'][k]-=n
  r=initialize(s);r['project']={'id':key,'participants':participants,'previous':previous,'done':0,'requiredPhases':ritual_phases(s,key,participants),'cost':d['cost'],'materials':deepcopy(d['materials'])}
 else:
  p=r['project'];g.require(p is not None and p['id']==key,'Choose the current ritual.')
  if kind=='cancel-lasting-ritual':
   s['sharedFunds']+=p['cost']
   for k,n in p['materials'].items():s['materialInventory'][k]+=n
   for who in p['participants']:
    if who in g.household_members(s) and g.character_assignment(s,who)=='ritual-circle':g.set_character_assignment(s,who,'rest')
   r['project']=None;g.add_journal(s,'Cancelled '+d['name']+'. Committed costs returned; no lasting effect granted.');return True
  g.require(all(w in g.household_members(s) and g.character_at_castle(s,w) for w in p['participants']),'Both original participants must be resident and home to resume.')
 for who in r['project']['participants']:g.set_character_assignment(s,who,'ritual-circle')
 g.add_journal(s,d['name']+' arranged. Both participants must work together for '+str(r['project'].get('requiredPhases',d['phases']))+' phases; other funded work is retained.')
 return True

def ready(s,p):
 import game as g,headquarters as h
 d=CATALOGUE[p['id']];leader,partner=p['participants']
 return h.ready(s,d['room']) and all(w in g.household_members(s) and g.character_at_castle(s,w) and g.character_assignment(s,w)=='ritual-circle' for w in p['participants']) and all(x in g.character_principles(s,leader) for x in d['principles']) and any(x in g.character_principles(s,partner) for x in d['principles'])
def resolve(s,summary):
 import game as g
 p=state(s)['project']
 if not p or not ready(s,p):return
 p['done']+=1;d=CATALOGUE[p['id']];required=p.get('requiredPhases',d['phases']);summary.append(d['name']+': '+str(p['done'])+'/'+str(required)+' shared phases.')
 if p['done']<required:return
 state(s)['completed'][p['id']]={'active':True,'participants':p['participants'][:],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
 for who in p['participants']:g.set_character_assignment(s,who,'rest')
 state(s)['project']=None;summary.append(d['name']+' is now a lasting household enchantment. '+d['effect'])
def view(s):
 import game as g
 members=g.household_members(s);p=state(s)['project']
 return {'project':deepcopy(p),'working':bool(p and ready(s,p)),'completed':deepcopy(state(s)['completed']),'catalogue':deepcopy(CATALOGUE),'options':{key:[{'leaderId':a,'partnerId':b,'phases':ritual_phases(s,key,[a,b]),'blockers':blockers(s,key,a,b)} for a in members for b in members if a!=b] for key in CATALOGUE}}


def ritual_phases(s,key,participants):
 return CATALOGUE[key]['phases']-int(all(aptitudes.score(s,p,aptitudes.spec('resolve','channeling'))['qualified'] for p in participants))
