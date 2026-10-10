"""Low-pressure household provisions, gathering and reviewed supply orders."""
from copy import deepcopy
from math import ceil
PREFERENCES={'founder':'forage','mira':'forage','tamsin':'forage','iona':'forage','aurelia':'forage','neris':'forage','sabine':'hunt','koharu':'forage','zahra':'hunt','fenna':'hunt','kaede':'hunt','elowen':'forage','nyssara':'forage','sylva':'forage','velis':'forage'}
def saved(s):return s['provisions']
def initialize(s):
 import game as g
 s.setdefault('provisions',{'stock':max(14,7*len(g.household_members(s))),'unfedDays':0,'lastMeal':None,'auto':False,'targetDays':7,'budget':6,'floor':20,'ritual':None,'orders':[],'nextOrder':1,'received':0,'gathered':0,'tutorial':False,'patrolWork':{}})
def need(s):
 import game as g,headquarters as h
 n=len(g.household_members(s));return max(1,ceil(n*.8)) if h.ready(s,'kitchen') else max(1,n)
def yield_for(s,who,kind):
 import game as g
 return 6+min(3,g.skill_rank(s,who,'fieldcraft'))+int(PREFERENCES.get(who,'forage')==kind)
def contract(s):
 import resident_specialties as r
 import companion_goals
 return (4 if r.active(s,'velis') else 0)+(2 if s.get('roadsWeKeep',{}).get('agreement')=='food' else 0)+(2 if companion_goals.complete(s,'velis') else 0)
def add(s,n):saved(s)['stock']+=n
def short(s):return saved(s)['unfedDays']>=3
def forecast(s):
 import game as g
 r=saved(s);lines=[]
 for w in g.household_members(s):
  kind=g.character_assignment(s,w)
  if kind in ('hunt','forage') and g.character_at_castle(s,w):lines.append(g.character_profile(s,w)['name']+': +'+str(yield_for(s,w,kind))+' provisions ('+kind+').')
 if s['currentDayPhase']=='evening':lines.append('At morning: '+str(need(s))+' provisions for the whole household, including travellers; '+str(contract(s))+' standing-contract provisions available before breakfast.')
 import resident_friendships
 for kind in ('hunt','forage'):
  cooperation=resident_friendships.cooperation(s,kind)
  if cooperation:lines.append('Resident cooperation: +'+str(cooperation['amount'])+' additional provisions from '+('hunting' if kind=='hunt' else 'foraging')+' together. Included in the phase result once.')
 if r['ritual']:lines.append('Conjure Sustenance: '+('one ritual work phase.' if g.character_assignment(s,'founder')=='food-ritual' and g.character_at_castle(s,'founder') else 'paused.'))
 return lines
def quote(s,requests):
 import game as g,headquarters as h
 g.require(h.ready(s,'supply-office'),'Restore the Supply Office first.')
 g.require(isinstance(requests,dict) and 0<len(requests)<=len(g.MATERIALS),'Choose material quantities to order.')
 rows={}
 for k,n in requests.items():
  g.require(k in g.MATERIALS and type(n) is int and 1<=n<=100,'Choose 1–100 of each known material.');g.require(not g.MATERIALS[k].get('rare'),'Rare creature materials cannot be ordered; recover them through bounties or field encounters.');rows[k]=n
 base=sum(g.MATERIALS[k]['price']*n for k,n in rows.items());specialist='velis' in g.household_members(s) and g.character_at_castle(s,'velis') and g.character_assignment(s,'velis')=='procurement'
 rate=(.7 if specialist else .85)-(.05 if s.get('roadsWeKeep',{}).get('agreement')=='materials' else 0)
 return {'materials':rows,'baseCost':base,'cost':max(1,ceil(base*rate)),'phases':2,'specialist':specialist}
def apply(s,act):
 import game as g,headquarters as h
 kind=act.get('type');r=saved(s)
 if not isinstance(kind,str) or not kind.startswith('food-'):return False
 who=act.get('characterId','founder')
 if kind=='food-assign':
  g.require(g.character_at_castle(s,'founder'),'Return home before changing household assignments.');assignment=act.get('assignment');g.require(who in g.household_members(s) and g.character_at_castle(s,who),'Choose a household member currently at home.')
  g.require(assignment in ('hunt','forage','rest','procurement','road-patrol'),'Choose an offered food or supply assignment.')
  if assignment=='procurement':g.require(who=='velis','Velis negotiates specialist procurement; choose hunting, foraging or other work for this resident.');g.require(h.ready(s,'supply-office'),'Restore the Supply Office first.')
  if assignment=='road-patrol':g.require(s.get('roadsWeKeep',{}).get('refugeDone') and h.ready(s,'guard-barracks'),'Restore the roadside refuge and barracks first.')
  g.set_character_assignment(s,who,assignment);return True
 g.require(g.character_at_castle(s,'founder'),'Return home to change purchasing and household provisioning plans.')
 if kind=='food-buy':
  n=act.get('bundles',1);g.require(type(n) is int and 1<=n<=100,'Buy 1–100 bundles of six provisions.');g.require(s['sharedFunds']>=n,'Each six-provision bundle costs one crown.');s['sharedFunds']-=n;add(s,n*6)
 elif kind=='food-policy':
  for key,lo,hi in [('targetDays',2,30),('budget',0,100),('floor',0,10000)]:g.require(type(act.get(key)) is int and lo<=act[key]<=hi,'Choose valid pantry target, daily spending cap and treasury floor.')
  g.require(type(act.get('enabled')) is bool,'Choose whether automatic purchases are enabled.')
  r.update(auto=act['enabled'],targetDays=act['targetDays'],budget=act['budget'],floor=act['floor'])
 elif kind=='food-tutorial':r['tutorial']=True
 elif kind=='food-ritual':
  g.require(not r['ritual'],'Finish or cancel the current sustenance ritual.')
  g.require('steady-hearth-wards' in g.character_principles(s,'founder'),'Personally learn Steady hearth wards before conjuring sustenance.')
  for k in ('silver-ivy','binding-thread'):g.require(s['materialInventory'][k]-s['materialReserveTargets'][k]>=1,'The ritual needs one unreserved silver ivy and one binding thread.')
  for k in ('silver-ivy','binding-thread'):s['materialInventory'][k]-=1
  r['ritual']={'done':0};g.set_character_assignment(s,'founder','food-ritual')
 elif kind=='food-resume':
  g.require(r['ritual'],'There is no unfinished sustenance ritual.');g.set_character_assignment(s,'founder','food-ritual')
 elif kind=='food-cancel':
  g.require(r['ritual'],'There is no unfinished sustenance ritual.')
  for k in ('silver-ivy','binding-thread'):s['materialInventory'][k]+=1
  r['ritual']=None
  if g.character_assignment(s,'founder')=='food-ritual':g.set_character_assignment(s,'founder','rest')
 elif kind=='food-order':
  q=quote(s,act.get('materials'));g.require(len(r['orders'])<4,'Receive an outstanding order before placing more than four.')
  g.require(s['sharedFunds']>=q['cost'],'The treasury cannot cover this delivery.');g.require(act.get('quotedCost')==q['cost'],'The quote changed. Review the current price first.')
  s['sharedFunds']-=q['cost'];r['orders'].append({**q,'id':r['nextOrder'],'remaining':q['phases']});r['nextOrder']+=1
 elif kind=='food-cancel-order':
  order=next((x for x in r['orders'] if x['id']==act.get('orderId')),None);g.require(order is not None,'Choose an outstanding order.');s['sharedFunds']+=order['cost'];r['orders'].remove(order)
 else:raise g.RuleError('Unknown provisions action.')
 return True
def resolve(s,summary,assignments,phase):
 import game as g,headquarters as h
 r=saved(s)
 for who,kind in assignments.items():
  if who not in g.household_members(s) or not g.character_at_castle(s,who):continue
  if kind in ('hunt','forage'):
   amount=yield_for(s,who,kind);add(s,amount);r['gathered']+=amount;summary.append(g.character_profile(s,who)['name']+' brought home '+str(amount)+' provisions from '+('hunting' if kind=='hunt' else 'foraging')+'.')
  if kind=='road-patrol' and s.get('roadsWeKeep',{}).get('refugeDone'):
   r['patrolWork'][who]=r['patrolWork'].get(who,0)+1
   if r['patrolWork'][who]>=2:
    import resident_specialties
    bonus=who=='rhess' and resident_specialties.active(s,'rhess') and h.ready(s,'watchtower')
    food,crowns=(6,3) if bonus else (4,2)
    r['patrolWork'][who]=0;add(s,food);s['sharedFunds']+=crowns;summary.append(g.character_profile(s,who)['name']+' completed a road patrol: '+str(food)+' provisions and '+str(crowns)+' crowns from the refuge agreement.')
 import resident_friendships
 for kind in ('hunt','forage'):
  workers=[w for w,k in assignments.items() if k==kind and w in g.household_members(s) and g.character_at_castle(s,w)]
  cooperation=resident_friendships.cooperation(s,kind,workers)
  if cooperation:
   amount=cooperation['amount'];add(s,amount);r['gathered']+=amount
   summary.append('Resident cooperation: '+' & '.join(g.character_profile(s,w)['name'] for w in cooperation['participants'])+' brought back '+str(amount)+' additional provisions from '+('hunting' if kind=='hunt' else 'foraging')+' together.')
 if r['ritual'] and assignments.get('founder')=='food-ritual' and g.character_at_castle(s,'founder'):
  r['ritual']['done']+=1
  if r['ritual']['done']>=2:r['ritual']=None;add(s,18);g.set_character_assignment(s,'founder','rest');summary.append('Conjure Sustenance completed: 18 provisions. Familiar nourishing food, with no expiry timer.')
 for order in r['orders'][:]:
  order['remaining']-=1
  if order['remaining']<=0:
   for k,n in order['materials'].items():s['materialInventory'][k]+=n
   r['orders'].remove(order);r['received']+=1;summary.append('Supply order '+str(order['id'])+' delivered its paid materials.')
 if phase!='evening':return
 daily=need(s);target=r['targetDays']*daily
 gift=min(contract(s),max(0,target-r['stock']))
 if gift:add(s,gift);summary.append('Standing supply agreements delivered '+str(gift)+' provisions without spending crowns.')
 if r['auto']:
  bundles=min(max(0,ceil((target-r['stock'])/6)),r['budget'],max(0,s['sharedFunds']-r['floor']))
  if bundles:s['sharedFunds']-=bundles;add(s,bundles*6);summary.append('Automatic pantry purchase: '+str(bundles*6)+' provisions for '+str(bundles)+' crowns; treasury floor respected.')
 served=min(daily,r['stock']);r['stock']-=served;r['unfedDays']=0 if served==daily else r['unfedDays']+1
 r['lastMeal']={'needed':daily,'served':served,'day':s['dayNumber']}
 import companion_goals
 if companion_goals.complete(s,'tamsin') and companion_goals.saved(s)['meal']=='tamsin':
  r['lastMeal']['menu']='Tamsin’s herb broth, mushroom pie, oat rolls and pear tart'
  summary.append('Household menu: '+r['lastMeal']['menu']+'. The normal provision cost applies.')
 summary.append('Household meals: '+str(served)+' / '+str(daily)+' provisions; '+str(r['stock'])+' remain.')
 if r['unfedDays']>=3:summary.append('Three or more unfed days: resting restores at most one vitality per phase. Feed the household to clear this capped effect; nobody dies or loses relationships.')
def view(s):
 import game as g,headquarters as h
 r=saved(s);daily=need(s)
 return {**deepcopy(r),'daily':daily,'days':round(r['stock']/daily,1),'people':[{'id':w,'name':g.character_profile(s,w)['name'],'assignment':g.character_assignment(s,w),'atHome':g.character_at_castle(s,w),'preferred':PREFERENCES.get(w,'forage'),'hunt':yield_for(s,w,'hunt'),'forage':yield_for(s,w,'forage')} for w in g.household_members(s)],'contract':contract(s),'office':h.ready(s,'supply-office'),'materialAgreement':s.get('roadsWeKeep',{}).get('agreement')=='materials','ritualKnown':'steady-hearth-wards' in g.character_principles(s,'founder'),'ritualWorking':bool(r['ritual'] and g.character_assignment(s,'founder')=='food-ritual' and g.character_at_castle(s,'founder')),'shortage':short(s),'forecast':forecast(s)}
