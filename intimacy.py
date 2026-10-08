"""Optional, replayable romantic closeness with bounded memories and explicit choices."""
from copy import deepcopy
import intimacy_content as c

EMPTY={'people':{}}
PERSON={'moments':{},'milestones':{},'pending':None,'latest':None,'deferred':False,'lastStamp':None}
def saved(s):return s.get('intimacy',EMPTY)
def person(s,who):return saved(s)['people'].get(who,PERSON)
def write(s,who):return s.setdefault('intimacy',deepcopy(EMPTY))['people'].setdefault(who,deepcopy(PERSON))

def adults(s,who):
 import game as g
 return all(type(g.character_profile(s,w).get('adultAgeYears')) is int and g.character_profile(s,w)['adultAgeYears']>=18 for w in ('founder',who))

def room(s,who,stage):
 import game as g,signature_equipment as equipment
 if stage<3:return equipment.ROOMS[who]
 participants={'founder',who}
 for candidate in dict.fromkeys(s['bedroomAssignments'].get(w) for w in (who,'founder')):
  if not candidate or not g.room_available(s,candidate):continue
  if any(w not in participants and r==candidate for w,r in s['bedroomAssignments'].items()):continue
  if any(r.get('roomId')==candidate for r in s.get('arrivalReservations',{}).values()):continue
  return candidate
 return None

def blockers(s,who,stage,kind):
 import romance,game as g
 from household_chapters import presence,room_reasons
 from social_life import stamp
 p=person(s,who);reasons=presence(s,['founder',who])
 if not adults(s,who):reasons.append('Both characters must be established adults.')
 if romance.person(s,who)['mode']!='open':reasons.append('Romantic invitations are paused. Reopen them only when you want to.')
 if romance.level(s,who)<stage+1:reasons.append('Share the '+('mutual attraction', 'first date', 'partnership', 'private evening')[stage]+' relationship milestone first.')
 shared=romance.saved(s)['memories'].get(f'{who}:{stage}')
 if shared and stamp(s)<=shared['stamp']:reasons.append('Let a day phase pass after the relationship milestone.')
 if stage and str(stage-1) not in p['milestones']:reasons.append('Share the preceding closeness milestone first.')
 if p['lastStamp'] is not None and stamp(s)<=p['lastStamp']:reasons.append('Enjoy another close moment in a later day phase. No invitation expires.')
 space=room(s,who,stage)
 if stage<3:reasons+=room_reasons(s,space)
 else:
  if not space:reasons.append('Arrange a restored bedroom assigned only to either or both of you, with no other resident or arriving guest assigned there.')
  if s['currentDayPhase']!='evening':reasons.append('Choose a private evening during the evening phase.')
  if any(g.character_sheet(s,w)['assignment']!='rest' for w in ('founder',who)):reasons.append('Assign both of you to Rest before a private evening; paid work keeps its progress.')
 if kind=='milestone':
  if str(stage) in p['milestones']:reasons.append('This milestone is already remembered; reread it at any time.')
  first=p['moments'].get(str(stage),{}).get('first')
  if not first:reasons.append('Share this stage’s repeatable moment first.')
  elif stamp(s)<=first['stamp']:reasons.append('Let a day phase pass after your first shared moment at this stage.')
  previous=p['milestones'].get(str(stage-1))
  if previous and s['dayNumber']<=previous['dayNumber']:reasons.append('Let a new day begin after the preceding closeness milestone.')
 return list(dict.fromkeys(reasons))

def definition(who,stage,kind):
 row=c.ROWS[who][stage];offset=0 if kind=='moment' else 3
 return row[offset:offset+3]

def view(s,who):
 import romance,game as g
 if who not in c.ROWS or who not in g.household_members(s) or not adults(s,who):return None
 p=person(s,who);rows=[]
 for stage,label in enumerate(c.STAGES):
  variants={}
  for kind in ('moment','milestone'):
   title,opening,_=definition(who,stage,kind);reasons=blockers(s,who,stage,kind)
   memory=p['milestones'].get(str(stage)) if kind=='milestone' else p['moments'].get(str(stage),{}).get('first')
   variants[kind]={'title':title,'blockers':reasons,'available':not reasons,'memory':deepcopy(memory),'count':p['moments'].get(str(stage),{}).get('count',0) if kind=='moment' else int(bool(memory))}
  rows.append({'stage':stage,'label':label,**variants})
 pending=None
 if p['pending']:
  pending=deepcopy(p['pending']);stage=pending['stage'];kind=pending['kind'];title,opening,_=definition(who,stage,kind)
  reasons=blockers(s,who,stage,kind)
  if pending['roomId']!=room(s,who,stage):reasons.append('Your available space changed. Put this invitation aside and open it again in the new space.')
  pending.update(title=title,opening=opening,blockers=reasons)
 return {'stages':rows,'pending':pending,'latest':deepcopy(p['latest']),'deferred':p['deferred'],'mode':romance.person(s,who)['mode'],'completed':len(p['milestones']),'roomId':room(s,who,0)}

def context(s,who):
 p=person(s,who)
 return {'milestones':deepcopy(list(p['milestones'].values())),'latest':deepcopy(p['latest'])}

def apply(s,a):
 kind=a.get('type')
 if kind not in ('intimacy-begin','intimacy-resolve','intimacy-defer','intimacy-restore'):return False
 import game as g,romance
 from social_life import stamp
 who=a.get('characterId');g.require(isinstance(who,str) and who in c.ROWS,'Choose an authored companion.')
 if kind in ('intimacy-defer','intimacy-restore'):
  g.require(who in g.household_members(s),'Choose a current resident companion.')
  p=write(s,who);p['pending']=None;p['deferred']=kind=='intimacy-defer';return True
 if kind=='intimacy-begin':
  g.require(who in g.household_members(s),'Choose a current resident companion.')
  stage=a.get('stage');scene=a.get('sceneKind')
  g.require(type(stage) is int and 0<=stage<4 and isinstance(scene,str) and scene in ('moment','milestone'),'Choose an offered closeness scene.')
  reasons=blockers(s,who,stage,scene);g.require(not reasons,' '.join(reasons))
  p=write(s,who);g.require(not p['deferred'],'Return the invitation when you want it.')
  g.require(not p['pending'],'Finish or put aside the open invitation first.')
  p['pending']={'stage':stage,'kind':scene,'roomId':room(s,who,stage)};return True
 p=person(s,who);pending=p['pending'];g.require(pending is not None,'Open an invitation first.')
 choice=a.get('choice');g.require(isinstance(choice,str) and choice in ('close','quiet','leave'),'Choose closeness, quiet company, or leave the invitation for later.')
 if choice=='leave':
  p=write(s,who);p['pending']=None;return True
 reasons=blockers(s,who,pending['stage'],pending['kind']);g.require(not reasons,' '.join(reasons))
 g.require(pending['roomId']==room(s,who,pending['stage']),'Your available space changed. Reopen the invitation in the new space.')
 stage=pending['stage'];scene=pending['kind'];title,opening,response=definition(who,stage,scene)
 p=write(s,who)
 if choice=='quiet':response=g.character_profile(s,who)['name']+' agrees to sit with you. You leave the romantic invitation for another evening.'
 count=p['moments'].get(str(stage),{}).get('count',0)
 if choice=='close' and scene=='moment' and count:
  response=('You accept the invitation again. ' if count%2 else 'You choose to spend this time together again. ')+response
 memory={'id':f'intimacy:{who}:{scene}:{stage}','title':title,'opening':opening,'response':response,'choice':choice,'participants':['founder',who],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'stamp':stamp(s),'roomId':pending['roomId'],'stage':stage,'kind':scene}
 p['latest']=memory;p['pending']=None
 if choice=='quiet':return True
 p['lastStamp']=stamp(s)
 if scene=='moment':
  r=p['moments'].setdefault(str(stage),{'first':deepcopy(memory),'count':0});r['count']+=1;r['latest']=deepcopy(memory)
  if r['count']==1:g.add_journal(s,title+': '+response)
 else:
  p['milestones'][str(stage)]=deepcopy(memory);g.add_journal(s,title+': '+response)
 return True
