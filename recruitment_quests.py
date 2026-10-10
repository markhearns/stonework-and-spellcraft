"""Common residents enter through completed rescues or voluntary post-custody agreements."""
from copy import deepcopy
BANDIT_ANCESTRIES=('human','high-elf','dark-elf','drow','catfolk','wolfkin','orc','ogrekin')

def initialize(s):s.setdefault('recruitmentQuests',{})
def saved(s):return s.get('recruitmentQuests',{})
def common(c):
 from character_pool import arrival_method
 return arrival_method(c['profile']['ancestryLabel'])=='recruitment'
def stamp(s):return str(s['dayNumber'])+':'+s['currentDayPhase']
def available_chambers(s):
 import containment
 return [k for k,d in containment.CHAMBERS.items() if d['ward']=='echo' and s['containment']['chambers'][k]['status']=='ready' and not containment.occupied(s,k)]
def occupies(s,chamber):return any(q.get('chamberId')==chamber and q['status'] in ('outbound','custody') for q in saved(s).values())
def lead(s,who,kind,*,world=False):
 import arrivals,game as g
 initialize(s);c=arrivals.candidate(s,who)
 g.require(common(c) or world and c['profile'].get('recruitmentSource')=='world-quest','Exotic recruitment quests must come from a saved rare world report.')
 import encounter_people as ep
 g.require(ep.profile_key(c['profile']) and ep.ancestry(ep.profile_key(c['profile'])) in ep.SUPPORTED,'Golems and spirits do not appear in rescue or bandit encounters. This ancestry has no recruitment encounter.')
 g.require(who not in s['people'],'This person is already known. Continue the existing contact.')
 g.require(kind in ('rescue','capture'),'Choose a rescue or a bandit lead.')
 g.require(who not in saved(s),'This person already has a saved quest. Continue that lead.')
 g.require(kind!='capture' or c['profile'].get('identitySource')!='authored-local-encounter','This named neighbour has a rescue lead, not a bandit identity.')
 if kind=='capture':
  import bestiary
  g.require(bestiary.ancestry_id(c['profile']['ancestryLabel']) in ep.BANDITS,'Dryads, nymphs, golems and spirits do not appear as bandits.')
 name=c['profile']['name']
 saved(s)[who]=dict(kind=kind,status='available',chamberId=None,topics={},conversation=[],lastTalk=None,respect=0,history=[],name=name)
 text=(name+' is trapped beyond a raider roadblock. Clear the road and escort her home before offering an invitation.' if kind=='rescue' else name+' has been identified among a toll-taking band. Locate the group, weaken it, then choose whether to take her into custody. Recruitment is considered only after release.')
 saved(s)[who]['brief']=text;g.add_journal(s,text)

def blockers(s,who):
 import game as g,field_patrols as p
 q=saved(s).get(who);b=[]
 if not q:return ['Choose a quest lead first.']
 if q['status']!='available':b.append('Continue this quest at its current stage.')
 if not p.local_unlocked(s):b.append('Complete Chapter 4, Keeping the Hearth, to open rescue and bandit patrols.')
 if p.saved(s)['active']:b.append('Bring the active patrol home first.')
 if not g.character_at_castle(s,'founder'):b.append('Return home before dispatching the rescue party.')
 if q['kind']=='capture' and not available_chambers(s):b.append('Prepare an unoccupied Quiet chamber in the dungeon before attempting capture.')
 return b

def capture_rows(s,run):
 import bestiary,field_magic as f
 who=run.get('recruitmentId');q=saved(s).get(who)
 if not q or q['kind']!='capture':return []
 b=[]
 if run['hp']>bestiary.ENCOUNTERS[run['enemies'][run['index']]]['hp']//2:b.append('Reduce the bandits to half vitality or lower before securing a surrender.')
 if s['materialInventory']['binding-thread']-s['materialReserveTargets']['binding-thread']<1:b.append('Needs 1 unreserved Binding thread for the escort restraint.')
 return [dict(id=w+':capture-bandit',who=w,name='Secure a surrender and escort '+q['name'],kind='peace',captureRecruit=True,damage=0,block=99,cost=0,inputs={'binding-thread':1},blockers=b[:]) for w in run['party'] if f.vitality(s,w)>0]

def resolved(s,run,row):
 if run.get('recruitmentId'):run['recruitmentCaptured']=bool(row.get('captureRecruit'))

def returned(s,run,complete,summary):
 who=run.get('recruitmentId')
 if not who:return
 q=saved(s)[who]
 if complete and (q['kind']=='rescue' or run.get('recruitmentCaptured')):
  q['status']='rescued' if q['kind']=='rescue' else 'custody'
  text=q['name']+(' returns safely. You may offer a household introduction or wish her well.' if q['status']=='rescued' else ' reaches the reserved Quiet chamber. Hear her account, discuss restitution and her plans, then decide on release. No household membership is granted in custody.')
 else:
  q['status']='available';q['chamberId']=None
  text='The party returns without '+q['name']+'. The lead remains available; no recruitment progress was granted.'
 q['history'].append(text);summary.append(text)

def topics(s,who):
 import arrivals
 p=arrivals.candidate(s,who)['profile'];ambition=p.get('ambition','Find dependable paid work and a place of her own.')
 return {
 'account':dict(name='Hear her account',text='“I took guard wages, then stayed when the group began collecting tolls it had no right to demand. I chose to stay. I will name the crossings we used so the missing cargo can be traced.”',choices=[('verify','Check her account against the recovered route notes.',1,'You compare the crossings with the patrol report. Her account matches; the names and dates go into the recovery record.'),('excuse','Say the theft no longer matters.',0,'“It matters to the people whose supplies went missing. I need to put that right.”'),('end','Decline to rely on her account.',0,'You decide to check the crossings independently. Her account is recorded without your endorsement; release remains available.')]),
 'restitution':dict(name='Agree how to put things right',text='“The recovered supplies belong to their owners. If I take work here after release, I want ordinary wages and a clear agreement about what I still owe.”',choices=[('fair','Return the goods and discuss paid restitution after release.',1,'“That gives me something I can actually do. Put the hours and wages in writing.”'),('conditional','Make freedom depend on joining the household.',0,'“Then it is not an offer I can choose. Release and work need to be separate decisions.”'),('leave','Agree to release her without a work arrangement.',0,'“Then I will leave when the release is settled. Thank you for being clear.”')]),
 'future':dict(name='Ask what she wants next',text='“I still have plans beyond this mistake.” '+ambition,choices=[('listen','Ask what honest work would help her pursue that goal.',1,'She describes the tools and practice she needs. You discuss a trial visit with ordinary wages and the freedom to leave.'),('dismiss','Tell her to put her own plans aside.',0,'“I need work I can live with, not another group telling me what I should want.”'),('road','Offer directions for continuing elsewhere.',0,'You mark a safe route and explain where returning travellers can find work.')])}

def apply(s,a):
 kind=a.get('type','')
 if not kind.startswith('recruit-'):return False
 import game as g,arrivals,field_patrols as p,bestiary
 initialize(s);who=a.get('characterId');c=arrivals.candidate(s,who)
 g.require(g.character_at_castle(s,'founder'),'Bring your scholar home for this decision.')
 if kind=='recruit-lead':lead(s,who,a.get('questKind','rescue'));return True
 q=saved(s).get(who);g.require(q is not None,'Choose a saved recruitment quest.')
 if kind=='recruit-depart':
  b=blockers(s,who);g.require(not b,' '.join(b))
  party=a.get('participants');g.require(isinstance(party,list) and 'founder' in party,'Bring your scholar on this recruitment quest.')
  chamber=available_chambers(s)[0] if q['kind']=='capture' else None
  p.apply(s,dict(type='watch-depart',routeId='road',participants=party))
  enemy='thief' if q['kind']=='rescue' else 'bandit'
  run=p.saved(s)['active'];run.update(name=('Rescue ' if q['kind']=='rescue' else 'Find the toll-taking band: ')+q['name'],enemies=[enemy],ancestries=[__import__('encounter_people').profile_key(c['profile']) if q['kind']=='capture' else 'human'],hp=p.ENEMIES[enemy]['hp'],recruitmentId=who)
  q.update(status='outbound',chamberId=chamber);return True
 g.require(q['status']!='outbound','Bring the quest party home before resolving this lead.')
 if kind=='recruit-talk':
  g.require(q['status']=='custody','Conversations about the capture take place in the dungeon before release.')
  topic=a.get('topic');choice=a.get('choice');g.require(isinstance(topic,str) and isinstance(choice,str),'Choose a listed topic and response.');d=topics(s,who).get(topic)
  g.require(d is not None and topic not in q['topics'],'Choose an undiscussed conversation topic.')
  g.require(q['lastTalk']!=stamp(s),'Give her time to consider this conversation. Advance before another discussion.')
  selected=next((x for x in d['choices'] if x[0]==choice),None);g.require(selected is not None,'Choose a listed response.')
  q['topics'][topic]=choice;q['respect']+=selected[2];q['lastTalk']=stamp(s)
  q['conversation'] += [dict(speaker=q['name'],text=d['text']),dict(speaker='You',text=selected[1]),dict(speaker=q['name'],text=selected[3])]
 elif kind=='recruit-release':
  g.require(q['status']=='custody','This person is not in custody.')
  q['chamberId']=None;q['status']='released'
  if len(q['topics'])==3 and q['respect']>=2:q['willing']=True
  else:q['willing']=False
  g.add_journal(s,q['name']+' was released. '+('She is willing to discuss a trial visit.' if q['willing'] else 'She chooses to continue elsewhere.'))
 elif kind=='recruit-invite':
  g.require(q['status']=='rescued' or q['status']=='released' and q.get('willing'),'Complete the rescue, or reach an agreement and release her before offering an invitation.')
  g.require(who not in s['people'],'Continue this person’s saved contact.')
  origin='rescued-traveller' if q['kind']=='rescue' else 'released-bandit'
  contact=arrivals.contact(s,who,origin);q['status']='invited'
  name=q['name'];opening=('“Thank you for getting me past the roadblock. I would like to hear about the household before deciding whether to visit.”' if q['kind']=='rescue' else '“I am here because I chose to come back. Let us discuss the work, the room and what each of us expects.”')
  s['summoningContacts'][contact]['conversation']=[dict(speaker=name,text=opening,source='recruitment-quest')]
  g.add_journal(s,name+' accepted an introduction. A suitable bed, a visit and household membership still need their usual separate agreements.')
 elif kind=='recruit-decline':
  g.require(q['status'] in ('rescued','released'),'Release a captured person before closing this lead.')
  q['status']='departed';g.add_journal(s,q['name']+' leaves with directions for a safe onward journey. No invitation was made.')
 else:raise g.RuleError('Choose a listed recruitment decision.')
 return True

def view(s):
 import game as g,bestiary,arrivals
 rows=[]
 for who,q in saved(s).items():
  c=arrivals.candidate(s,who);aid=bestiary.ancestry_id(c['profile']['ancestryLabel'])
  rows.append(dict(deepcopy(q),id=who,art=__import__('encounter_people').art(__import__('encounter_people').profile_key(c['profile']),q['kind']) or bestiary.ANCESTRIES[aid]['art'],blockers=blockers(s,who),canTalk=g.character_at_castle(s,'founder') and q['lastTalk']!=stamp(s),topics={k:{**d,'choices':[dict(id=x[0],label=x[1]) for x in d['choices']]} for k,d in topics(s,who).items() if k not in q['topics']}))
 return dict(quests=rows,members=[dict(id=w,name=g.character_profile(s,w)['name'],blockers=__import__('field_patrols').member_blockers(s,w)) for w in g.household_members(s)])
