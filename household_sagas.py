"""Authored ensemble stories, persistent shared work and actual-party chemistry."""
from copy import deepcopy
from itertools import combinations
import household_saga_content as content

ASSIGNMENT='household-story'
EMPTY={'stories':{},'memories':{},'active':None,'deferred':[],'codas':{},'fieldMemories':{}}
def initialize(s):s.setdefault('householdSagas',deepcopy(EMPTY))
def saved(s):return s.get('householdSagas',EMPTY)
def record(s,key):return saved(s)['stories'].get(key,{'stage':0,'choices':[],'project':None,'withoutProject':False})
def stamp(s):
 from social_life import stamp as now
 return now(s)
def scene_id(key,stage):return key+':'+str(stage)
def members(s):
 import game as g
 return g.household_members(s)
def presence(s,people,founder=True):
 import game as g
 checks=list(dict.fromkeys((['founder'] if founder else [])+list(people)));reasons=[]
 for who in checks:
  if who not in members(s):reasons.append(who.capitalize()+' must be a castle resident.')
  elif not g.character_at_castle(s,who):reasons.append(g.character_profile(s,who)['name']+' must return home.')
 return reasons

def completion(s,key):return record(s,key)['stage']>=3

def scene_blockers(s,key):
 import headquarters as h
 d=content.STORIES[key];r=record(s,key);n=r['stage']
 reasons=presence(s,d['cast'])
 if n>=3:return ['This story is already remembered.']
 if n:
  previous=saved(s)['memories'].get(scene_id(key,n-1))
  if previous and stamp(s)<=previous['stamp']:reasons.append('Let one shared phase pass before the next scene. This invitation never expires.')
 if n==2:
  if not h.ready(s,d['room']):reasons.append('Restore '+h.ROOMS[d['room']]['name']+' for the concluding gathering.')
  if not r['withoutProject'] and not (r['project'] and r['project']['status']=='complete'):reasons.append('Finish the shared project, or choose a gathering without funding it.')
 return reasons

def scene_definition(s,key):
 d=content.STORIES[key];r=record(s,key);n=r['stage']
 if n>=3:return None
 b=deepcopy(d['beats'][n]);callbacks=[]
 if n:
  previous=saved(s)['memories'][scene_id(key,n-1)]
  callbacks.append('Your earlier choice: “'+previous['playerLine']+'”')
  b['opening']=previous['response']+'\n\n'+b['opening']
 if n==2:
  p=r['project'];lead=('Their '+d['projectName'].lower()+' is complete.' if p and p['status']=='complete' else 'They chose to gather without commissioning the shared project. Its practical benefit has not been claimed.')
  b['opening']=lead+'\n\n'+b['opening']
 for other,od in content.STORIES.items():
  overlap=[p for p in d['cast'] if p in od['cast']]
  if other!=key and overlap and completion(s,other):
   import game as g
   old=saved(s)['memories'][scene_id(other,2)]
   callbacks.append(g.character_profile(s,overlap[0])['name']+' recalls “'+od['title']+'”: '+old['playerLine'])
   break
 b['callbacks']=callbacks
 return b

def project_blockers(s,key,workers=None):
 import game as g,headquarters as h
 d=content.STORIES[key];r=record(s,key);p=r['project'];reasons=[]
 if r['stage']<2:reasons.append('Share the first two scenes before agreeing a project.')
 if p and p['status']=='complete':reasons.append('This project is already complete.')
 if saved(s)['active'] not in (None,key):reasons.append('Pause the other shared project first.')
 if not h.ready(s,d['room']):reasons.append('Restore '+h.ROOMS[d['room']]['name']+' first.')
 reasons+=presence(s,[],True)
 if workers is not None:
  if not isinstance(workers,list) or not 2<=len(workers)<=4 or not all(isinstance(w,str) and w in ['founder']+d['cast'] for w in workers) or len(workers)!=len(set(workers)):
   return reasons+['Choose two to four distinct participants from this story or your scholar.']
  reasons+=presence(s,workers)
  for who in workers:
   if who in members(s) and g.character_assignment(s,who) not in ('rest',ASSIGNMENT):reasons.append(g.character_profile(s,who)['name']+' must be resting before joining; their other work is preserved.')
 if not p:
  if s['sharedFunds']<4:reasons.append('Needs 4 shared crowns.')
  if s['materialInventory'].get('binding-thread',0)-s['materialReserveTargets'].get('binding-thread',0)<1:reasons.append('Needs 1 unreserved binding thread.')
 return reasons

def eligible(s):
 import game as g
 key=saved(s)['active']
 if not key:return None
 p=record(s,key)['project']
 if not p or p['status']!='working':return None
 import headquarters as h
 if not h.ready(s,content.STORIES[key]['room']):return None
 return key if not presence(s,p['workers'],False) and all(g.character_assignment(s,w)==ASSIGNMENT for w in p['workers']) else None

def release(s,p):
 import game as g
 for who in p['workers']:
  if who in members(s) and g.character_assignment(s,who)==ASSIGNMENT:g.set_character_assignment(s,who,'rest')

def resolve(s,summary,was_eligible):
 import game as g
 if not was_eligible or eligible(s)!=was_eligible:return
 key=was_eligible;p=saved(s)['stories'][key]['project'];p['done']+=1
 summary.append(content.STORIES[key]['projectName']+': '+str(p['done'])+'/2 shared work phases. Both primary assignments are used; more workers do not accelerate it.')
 if p['done']>=2:
  p['status']='complete';p['completedOn']={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']};release(s,p);saved(s)['active']=None
  summary.append('Shared project complete. Its '+('teamwork' if p['mode']=='method' else 'ordinary quest support')+' benefit is now available to the actual workers.')

def teamwork(s,a,b,skill):
 """At most one point, and only two real workers in the current scored party."""
 for key,d in content.STORIES.items():
  p=record(s,key)['project']
  if p and p['status']=='complete' and p['mode']=='method' and d['skill']==skill and a in p['workers'] and b in p['workers']:return key
 return None

def comfort(s,who,obstacle):
 for key,d in content.STORIES.items():
  p=record(s,key)['project']
  if p and p['status']=='complete' and p['mode']=='company' and who in p['workers'] and obstacle in d['obstacles']:return key
 return None

def field_rows(s):
 import game as g
 e=s.get('expedition')
 if not e:return []
 party=g.expedition_party(s);rows=[]
 for key,d in content.STORIES.items():
  speakers=[w for w in d['cast'] if w in party]
  if not speakers or 'founder' not in party or not completion(s,key):continue
  memory_id=key+':'+'|'.join(sorted(speakers));memory=saved(s)['fieldMemories'].get(memory_id)
  first=record(s,key)['choices'][0]
  opening='They recall '+d['title'].lower()+' and the '+('practical approach' if first=='method' else 'time made for company')+' you chose together.\n'+'\n'.join(g.character_profile(s,w)['name']+': '+d['field'][w] for w in speakers)
  rows.append({'id':memory_id,'storyId':key,'title':'A familiar conversation on the road','participants':['founder']+speakers,'opening':opening,'memory':deepcopy(memory)})
 return rows

def coda_rows(s):
 import romance
 rows=[]
 for who,line in content.CODAS.items():
  available=[key for key,d in content.STORIES.items() if who in d['cast'] and completion(s,key)]
  if who not in members(s) or not available:continue
  memory=saved(s)['codas'].get(who);reasons=presence(s,[who]);level=romance.level(s,who)
  if level<1:reasons.append('Share mutual attraction first. The ensemble stories remain available as friendships.')
  rows.append({'id':who,'title':'A little time after the gathering','participants':['founder',who],'opening':line if not reasons or memory else '',
   'blockers':reasons,'memory':deepcopy(memory),'level':level,'storyId':available[-1]})
 return rows

def network(s):
 import relationships
 bonds=[]
 for bond in relationships.saved(s)['bonds'].values():
  people=bond['participants']
  if 'founder' in people or not all(w in members(s) for w in people) or not any(bond[k] for k in relationships.DIMENSIONS):continue
  events=[e for e in relationships.saved(s)['events'].values() if all(w in e['participants'] for w in people)]
  sources=[key for key,d in content.STORIES.items() if all(w in d['cast'] for w in people) and record(s,key)['stage']]
  latest=max(sources,key=lambda k:saved(s)['memories'][scene_id(k,record(s,k)['stage']-1)]['stamp']) if sources else None
  tone='An established connection'
  if latest:
   r=record(s,latest);tone=('Easy company' if r['choices'][-1]=='company' else 'Mutual professional regard') if r['stage']==3 else ('Friendly competitors' if latest in ('sparring','fair','maps') else 'Different perspectives, a shared conversation')
  bonds.append({**deepcopy(bond),'tone':tone,'events':deepcopy(events[-8:]),'stories':sources})
 return bonds

def views(s):
 import game as g,headquarters as h
 rows=[]
 for key,d in content.STORIES.items():
  if not any(w in members(s) for w in d['cast']):continue
  r=record(s,key);reasons=scene_blockers(s,key);definition=scene_definition(s,key) if r['stage']<3 else None
  p=r['project'];workers=p['workers'] if p else d['cast'][:2]
  rows.append({'id':key,'title':d['title'],'cast':d['cast'][:],'roomId':d['room'],'stage':r['stage'],'deferred':key in saved(s)['deferred'],
   'scene':{'title':definition['title'],'opening':definition['opening'] if not reasons else '', 'callbacks':definition['callbacks'] if not reasons else [],'choices':{k:{'label':v['label'],'effect':v['dimension'].title()+' +1 between the companions present.'} for k,v in definition['choices'].items()} if not reasons else {}} if definition else None,
   'blockers':reasons,'memories':deepcopy([saved(s)['memories'][scene_id(key,n)] for n in range(r['stage'])]),
   'project':deepcopy(p),'projectName':d['projectName'],'projectPlanningBlockers':project_blockers(s,key),'projectBlockers':project_blockers(s,key,workers),'defaultWorkers':workers,
   'workerOptions':[{'id':w,'name':g.character_profile(s,w)['name'],'blockers':presence(s,[w])+([] if g.character_assignment(s,w) in ('rest',ASSIGNMENT) else ['Finish or pause the current assignment first.'])} for w in ['founder']+d['cast'] if w in members(s)],
   'mode':r['choices'][0] if r['choices'] else None,'skill':g.CHARACTER_SKILLS[d['skill']]['name'],'obstacles':d['obstacles'][:],'withoutProject':r['withoutProject'],
   'working':eligible(s)==key})
 return {'stories':rows,'bonds':network(s),'codas':coda_rows(s),'field':field_rows(s),'active':saved(s)['active']}

def context(s,who):
 return {'sharedStories':deepcopy([m for m in saved(s)['memories'].values() if who in m['participants']]),
  'privateCoda':deepcopy(saved(s)['codas'].get(who)),
  'fieldMemories':deepcopy([m for m in saved(s)['fieldMemories'].values() if who in m['participants']])}

ACTIONS={'share-household-saga','defer-household-saga','restore-household-saga','fund-household-project','pause-household-project','resume-household-project','gather-without-project','share-saga-coda','share-saga-field'}
def apply(s,a):
 if a.get('type') not in ACTIONS:return False
 candidate=deepcopy(s);_apply(candidate,a);s.clear();s.update(candidate);return True

def _apply(s,a):
 import game as g,relationships,romance
 initialize(s);kind=a['type'];data=saved(s)
 if kind=='share-saga-field':
  row=next((r for r in field_rows(s) if r['id']==a.get('sceneId')),None)
  g.require(row is not None,'These companions must actually be travelling together after their shared story.')
  g.require(not row['memory'],'This travelling conversation is already remembered.')
  m={k:deepcopy(row[k]) for k in ('id','storyId','title','participants','opening')};m.update(response='They agree which suggestion to try. The decision about the actual obstacle remains yours.',dayNumber=s['dayNumber'],phase=s['currentDayPhase'])
  data['fieldMemories'][m['id']]=m;relationships.remember(s,'saga-field:'+m['id'],m,'trust');g.add_journal(s,m['title']);return
 if kind=='share-saga-coda':
  who=a.get('characterId');row=next((r for r in coda_rows(s) if r['id']==who),None)
  g.require(row is not None,'Complete a shared story with this companion first.');g.require(not row['memory'],'This personal invitation is already remembered.')
  g.require(not row['blockers'],' '.join(row['blockers']));choice=a.get('choice');g.require(choice in ('quiet','flirt') if isinstance(choice,str) else False,'Choose quiet company or flirtation.')
  level=romance.level(s,who)
  response='You sit together after the others have left, trading small observations and enjoying the quiet.'
  if choice=='flirt':response={1:'Your compliment draws a pleased smile. Your companion moves closer, letting the attraction remain an invitation rather than a promise.',2:'Your companion accepts the compliment and draws you into a lingering kiss before settling beside you.',3:'Your partner takes your hand and kisses you, openly pleased to have this part of the evening together.',4:'Your partner meets your compliment with a slow kiss and an invitation to leave the bustle behind. The evening becomes private and unhurried.'}[level]
  import outfit_progression,character_customization
  m={'id':who,'title':row['title'],'storyId':row['storyId'],'participants':['founder',who],'opening':row['opening'],'response':response,'choice':choice,'relationshipLevel':level,'outfit':deepcopy(character_customization.style(s,who) or outfit_progression.current(s,who)),'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  data['codas'][who]=m;relationships.remember(s,'saga-coda:'+who,m,'affection' if choice=='flirt' else 'trust');g.add_journal(s,m['title']+': '+response);return
 key=a.get('storyId');g.require(isinstance(key,str) and key in content.STORIES,'Choose a known household story.')
 d=content.STORIES[key];r=record(s,key)
 if kind in ('defer-household-saga','restore-household-saga'):
  g.require(any(w in members(s) for w in d['cast']),'Meet a participant before managing this invitation.')
  if kind.startswith('defer'):
   g.require(key not in data['deferred'],'This invitation is already set aside.');data['deferred'].append(key)
  else:
   g.require(key in data['deferred'],'This invitation is not set aside.');data['deferred'].remove(key)
  return
 if kind=='share-household-saga':
  reasons=scene_blockers(s,key);g.require(not reasons,' '.join(reasons))
  choice=a.get('choice');g.require(isinstance(choice,str) and choice in ('method','company'),'Choose an offered response.')
  b=scene_definition(s,key);v=b['choices'][choice];n=r['stage']
  m={'id':scene_id(key,n),'storyId':key,'title':b['title'],'opening':b['opening'],'callbacks':b['callbacks'],'response':v['response'],'playerLine':v['label'],'choice':choice,'participants':d['cast'][:],'witnesses':['founder'],'stamp':stamp(s),'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  data['memories'][m['id']]=m;r=deepcopy(r);r['stage']+=1;r['choices'].append(choice);data['stories'][key]=r
  relationships.remember(s,'saga:'+m['id'],m,v['dimension']);g.add_journal(s,m['title']+': '+m['response']);return
 g.require(key in data['stories'],'Begin this household story first.');r=data['stories'][key]
 if kind=='gather-without-project':
  g.require(r['stage']==2,'Share the first two scenes before choosing the gathering.')
  g.require(not r['project'],'A funded project keeps its commitment; finish it before this gathering.')
  g.require(not presence(s,d['cast']),' '.join(presence(s,d['cast'])));r['withoutProject']=True;return
 if kind in ('fund-household-project','resume-household-project'):
  workers=a.get('workers') if kind=='fund-household-project' else (r['project'] or {}).get('workers')
  g.require(isinstance(workers,list),'Choose the actual workers for this shared project.')
  reasons=project_blockers(s,key,workers);g.require(not reasons,' '.join(reasons))
  if kind=='fund-household-project':
   g.require(r['project'] is None,'This project is already funded. Resume its saved work.')
   s['sharedFunds']-=4;s['materialInventory']['binding-thread']-=1
   r['project']={'status':'working','done':0,'workers':workers[:],'mode':r['choices'][0],'costCrowns':4,'materials':{'binding-thread':1}}
  else:g.require(r['project'] is not None and r['project']['status']!='complete','There is no unfinished project to resume.');r['project']['status']='working'
  for who in workers:g.set_character_assignment(s,who,ASSIGNMENT)
  data['active']=key;g.add_journal(s,d['projectName']+': '+', '.join(g.character_profile(s,w)['name'] for w in workers)+' agreed two shared work phases.');return
 if kind=='pause-household-project':
  p=r['project'];g.require(p is not None and p['status']=='working','There is no working project to pause.')
  p['status']='paused';release(s,p)
  if data['active']==key:data['active']=None
  return


def greeting(s,who):
 memories=[m for m in saved(s)['memories'].values() if who in m['participants']]
 if not memories:return None
 last=max(memories,key=lambda m:m['stamp']);d=content.STORIES[last['storyId']]
 return 'Remembering “'+d['title']+'”: '+d['field'][who]
