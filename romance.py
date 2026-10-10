"""Mutual relationship milestones; scores make invitations available, never decisions."""
from copy import deepcopy
import romance_content as content

GREETINGS={
'mira':'“I kept the better chair. You may persuade me to share it.”','tamsin':'“There you are. This cup is for company, not an errand.”','iona':'“I was hoping you would be my next distraction.”','aurelia':'“Off duty. Deliberately pleased to see you.”','neris':'“Your arrival has improved my plans considerably.”','sabine':'“Do come closer. I chose that smile especially for you.”','koharu':'“Nothing is broken. I simply wanted you here.”','zahra':'“I saved a little quiet for us.”','fenna':'“Caught you looking for me. Fortunately, I was looking for you.”','kaede':'“I can spare a moment. For you, I rather wanted to.”','elowen':'“I hoped we might have a little time together.”','nyssara':'“This invitation is exactly what it appears to be.”','sylva':'“There is a place beside me, if you would like it.”'}

def initialize(s):s.setdefault('romance',{'people':{},'memories':{},'dates':{}})
def saved(s):return s.get('romance',{'people':{},'memories':{},'dates':{}})
def person(s,who):return saved(s)['people'].get(who,{'level':0,'mode':'open','deferred':False})
def level(s,who):
 p=person(s,who);return p['level'] if p['mode']=='open' else 0

def history(s,who):
 import outfit_progression
 return outfit_progression.memories(s,who)

def blockers(s,who,index):
 import relationships
 from household_chapters import presence
 from social_life import stamp
 reasons=presence(s,['founder',who]);p=person(s,who)
 if p['mode']!='open':reasons.append('Romantic invitations are paused. Reopen them only if you want to.')
 if index!=p['level']:reasons.append('Share the preceding mutual milestone first.')
 count,trust,affection,respect=content.REQUIREMENTS[index]
 actual=len(history(s,who))
 if actual<count:reasons.append(f'Share {count} distinct remembered moments together ({actual}/{count}).')
 bond=relationships.saved(s)['bonds'].get(relationships.pair_id('founder',who),{})
 for dimension,minimum in [('trust',trust),('affection',affection),('respect',respect)]:
  if bond.get(dimension,0)<minimum:reasons.append(f'Develop {dimension} to {minimum} through shared moments ({bond.get(dimension,0)}/{minimum}).')
 if index:
  previous=saved(s)['memories'].get(f'{who}:{index-1}')
  if previous and stamp(s)<=previous['stamp']:reasons.append('Let one phase pass before the next milestone. No invitation expires.')
 return reasons

def date_blockers(s,who,room):
 from household_chapters import presence,room_reasons
 return presence(s,['founder',who])+room_reasons(s,room)+([] if level(s,who)>=2 else ['Share a mutual first date before arranging this romantic outing.'])

def view(s,who):
 import game as g,intimacy
 if who not in content.SCENES or who not in g.household_members(s):return None
 p=person(s,who);scenes=[]
 for i,(title,opening,response) in enumerate(content.SCENES[who]):
  memory=saved(s)['memories'].get(f'{who}:{i}');reasons=blockers(s,who,i)
  scenes.append({'id':f'{who}:{i}','index':i,'title':title,'opening':memory['opening'] if memory else opening if not reasons else '',
   'memory':deepcopy(memory),'blockers':[] if memory else reasons,'available':not memory and not reasons,'deferred':p['deferred'] and i==p['level']})
 dates=[]
 for room,(title,opening,response) in content.DATES.items():
  memory=saved(s)['dates'].get(who+':'+room);reasons=date_blockers(s,who,room)
  dates.append({'roomId':room,'title':title,'opening':opening if not reasons or memory else '', 'memory':deepcopy(memory),'blockers':[] if memory else reasons,'available':not memory and not reasons})
 return {'who':who,'level':p['level'],'stage':content.STAGES[p['level']],'mode':p['mode'],'scenes':scenes,'dates':dates,'closeness':intimacy.view(s,who)}

def views(s):
 import game as g
 return {who:view(s,who) for who in content.SCENES if who in g.household_members(s)}

def greeting(s,who,fallback=None):
 n=level(s,who)
 if not n:return fallback
 return GREETINGS.get(who,fallback)+(' She offers her hand as you join her.' if n==2 else ' She welcomes you with a familiar kiss.' if n>=3 else '')

def quest_reply(s,who,original):
 n=level(s,who)
 if person(s,who)['mode']!='open':return 'They accept the compliment warmly and keep the celebration friendly, as you asked.'
 if n==0:return original
 return original+(['',' You both recognise the attraction you have already acknowledged; this invitation no longer needs to hide inside a joke.', ' You share a kiss, remembering the first date you chose together.', ' Your partner takes your hand. The celebration has the easy affection of a relationship you have both named.', ' Your partner draws close for a kiss, and the celebration becomes an unhurried private evening together.'][n])

def context(s,who):
 import intimacy
 return {'closeness':intimacy.context(s,who),'relationship':deepcopy(person(s,who)),'milestones':deepcopy([m for m in saved(s)['memories'].values() if who in m['participants']]),'dates':deepcopy([m for m in saved(s)['dates'].values() if who in m['participants']])}

def apply(s,a):
 kind=a.get('type')
 if kind not in ('share-romance','defer-romance','restore-romance','pause-romance','reopen-romance','share-romantic-date'):return False
 import game as g,relationships
 from household_chapters import presence
 from social_life import stamp
 who=a.get('characterId');g.require(isinstance(who,str) and who in content.SCENES and who in g.household_members(s),'Choose an established resident companion.')
 if kind in ('pause-romance','reopen-romance','defer-romance','restore-romance'):
  p=person(s,who)
  if kind=='defer-romance':g.require(p['level']<4 and not p['deferred'],'There is no new invitation to set aside.')
  if kind=='restore-romance':g.require(p['deferred'],'This invitation is not set aside.')
  initialize(s);p=saved(s)['people'].setdefault(who,deepcopy(p))
  if kind in ('pause-romance','reopen-romance'):p['mode']='friendly' if kind=='pause-romance' else 'open'
  if kind=='pause-romance' and who in s.get('intimacy',{}).get('people',{}):s['intimacy']['people'][who]['pending']=None
  if kind in ('defer-romance','restore-romance'):p['deferred']=kind=='defer-romance'
  return True
 reasons=presence(s,['founder',who]);g.require(not reasons,' '.join(reasons))
 choice=a.get('choice');g.require(choice in ('romantic','friendly') if isinstance(choice,str) else False,'Choose an offered response.')
 if kind=='share-romantic-date':
  room=a.get('roomId');g.require(isinstance(room,str) and room in content.DATES,'Choose an authored date location.')
  key=who+':'+room;g.require(key not in saved(s)['dates'],'This date is already remembered.')
  reasons=date_blockers(s,who,room);g.require(not reasons,' '.join(reasons))
  title,opening,response=content.DATES[room]
  if choice=='friendly':response='You enjoy a quiet conversation together without taking the invitation further. Your companion is happy to share the time at this pace.'
  group='dates'
 else:
  index=a.get('index');g.require(type(index) is int and 0<=index<4,'Choose a known relationship milestone.')
  key=f'{who}:{index}';g.require(key not in saved(s)['memories'],'This milestone is already remembered.')
  reasons=blockers(s,who,index);g.require(not reasons,' '.join(reasons))
  if choice=='friendly':
   initialize(s);p=saved(s)['people'].setdefault(who,deepcopy(person(s,who)));p['mode']='friendly';p['deferred']=False
   if who in s.get('intimacy',{}).get('people',{}):s['intimacy']['people'][who]['pending']=None
   g.add_journal(s,g.character_profile(s,who)['name']+' understood your request to keep your time together non-romantic for now. No relationship points were lost.');return True
  title,opening,response=content.SCENES[who][index];group='memories'
 initialize(s);p=saved(s)['people'].setdefault(who,deepcopy(person(s,who)))
 import outfit_progression
 outfit=outfit_progression.current(s,who)
 record={'outfitId':outfit['id'] if outfit else None,'outfitName':outfit['name'] if outfit else None,'id':key,'title':title,'opening':opening,'response':response,'choice':choice,'participants':['founder',who],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'stamp':stamp(s)}
 saved(s)[group][key]=record
 if group=='memories':p['level']+=1;p['deferred']=False
 relationships.remember(s,'romance:'+group+':'+key,record,'affection' if choice=='romantic' else 'trust')
 g.add_journal(s,title+': '+response);return True
