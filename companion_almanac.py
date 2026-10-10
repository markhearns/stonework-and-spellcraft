"""Progressive disclosures and deterministic everyday companion life."""
from copy import deepcopy
import companion_almanac_content as c
import companion_conversations

TIERS={'familiar':'Getting to know her','trusted':'In her confidence','intimate':'Private affection'}
CHOICES={'curious':('Ask a thoughtful question and listen.','trust'), 'warm':('Respond warmly and make room for her answer.','affection'), 'candid':('Speak honestly, without trying to decide for her.','respect')}

def initialize(s):s.setdefault('companionAlmanac',{'memories':{},'deferred':[]})
def saved(s):return s.get('companionAlmanac',{'memories':{},'deferred':[]})
def members(s):
 import game as g
 return [w for w in c.PERSONAL if w in g.household_members(s) and g.character_profile(s,w).get('adultAgeYears',0)>=18]
def bond(s,who):
 import relationships as r
 return r.saved(s)['bonds'].get(r.pair_id('founder',who),{})
def present(s,people):
 import game as g
 return ['Return home together; this invitation will wait.'] if any(w not in g.household_members(s) or not g.character_at_castle(s,w) for w in people) else []

def definition(s,key):
 import game as g
 parts=key.split(':');kind=parts[0]
 if kind=='pair':
  a,b,index=parts[1],parts[2],int(parts[3]);d=next(p for p in c.PAIRS if p[0]==a and p[1]==b)
  title,opening,result=d[3][index]
  prior=saved(s)['memories'].get(f'pair:{a}:{b}:{index-1}')
  if prior:opening='Last time, you chose: “'+prior['playerLine']+'” '+prior['response']+'\n\n'+opening
  choices=companion_conversations.pair_choices(a,b,index)
  return {'kind':kind,'title':title,'opening':opening,'people':['founder',a,b],
          'responses':{k:v['response'] for k,v in choices.items()},
          'labels':{k:v['label'] for k,v in choices.items()},'index':index,'target':None}
 who=parts[1];p=c.PERSONAL[who];name=g.character_profile(s,who)['name']
 if kind=='initiative':
  title,opening,target=p['initiative']
  responses=dict(zip(('curious','warm','candid'),c.INITIATIVE_REPLIES[who]))
  return {'kind':kind,'title':title,'opening':opening,'people':['founder',who],'responses':responses,'labels':dict(zip(CHOICES,companion_conversations.INITIATIVE_LABELS[who])),'target':{'view':target,'personId':who}}
 title=TIERS[kind]+' · '+name
 conversation=companion_conversations.disclosure(who,kind)
 return {'kind':kind,'title':title,'opening':conversation['opening'],'people':['founder',who],
         'responses':{key:value['response'] for key,value in conversation['choices'].items()},
         'labels':{key:value['label'] for key,value in conversation['choices'].items()},'target':None}

def section_facts(who,tier,state=None):
 p=c.PERSONAL[who];h,w,(b,wa,hi),build,note=c.PHYSICAL[who]
 goal,value,tension=companion_conversations.CHARACTER[who]
 import companion_goals
 if state is not None and companion_goals.complete(state,who):goal="Completed: "+companion_goals.GOALS[who]["proof"]
 if tier=='familiar':return {'A small habit':p['habit'],'A piece of her past':p['history'],'What feels like home':p['comfort'],'What she wants':goal,'What she values':value}
 if tier=='trusted':return {'Bust / waist / hips':f'{b} / {wa} / {hi} cm','Fit and anatomy':note,'Something she finds difficult':p['worry'],'A habit she is working on':tension,'Affection she appreciates':p['affection']}
 return {'Turn-ons':p['attraction'],'Turn-offs':p['turnoff'],'A private admission':p['private'],'What these preferences mean':'An invitation to ask and listen; each moment still needs mutual agreement'}

def keys(s):
 known=members(s)
 return [kind+':'+who for who in known for kind in [*TIERS,'initiative']]+[f'pair:{a}:{b}:{i}' for a,b,_,scenes in c.PAIRS if a in known and b in known for i in range(len(scenes))]

def blockers(s,key,d):
 import romance
 from social_life import stamp
 reasons=present(s,d['people']);kind=d['kind'];mem=saved(s)['memories']
 if kind=='pair':
  a,b=d['people'][1:]
  if not all('familiar:'+w in mem for w in (a,b)):reasons.append('Share each companion’s first personal disclosure. Friendship needs no romance.')
  if d['index']:
   previous=mem.get(f'pair:{a}:{b}:{d["index"]-1}')
   if not previous:reasons.append('Share the preceding conversation between these companions.')
   elif stamp(s)<=previous['stamp']:reasons.append('Let one day phase pass before their next conversation. Nothing expires.')
  return reasons
 who=d['people'][1];b=bond(s,who);level=romance.level(s,who)
 if kind=='familiar' and b.get('trust',0)<2 and level<1:reasons.append('Develop trust to 2 through remembered moments, or share a mutual attraction milestone.')
 if kind in ('trusted','initiative') and 'familiar:'+who not in mem:reasons.append('Share her first personal disclosure.')
 if kind=='trusted' and not (b.get('trust',0)>=4 and b.get('respect',0)>=2) and level<2:reasons.append('Develop trust to 4 and respect to 2, or share a mutual first date.')
 if kind=='intimate':
  if 'trusted:'+who not in mem:reasons.append('Share her trusted disclosure first.')
  if level<3:reasons.append('Establish a mutual partnership with romantic invitations open. Friendship remains complete without this conversation.')
 return reasons

def row(s,key):
 d=definition(s,key);m=saved(s)['memories'].get(key);r=blockers(s,key,d);deferred=key in saved(s)['deferred'];available=not m and not r and not deferred
 return {'id':key,'kind':d['kind'],'title':d['title'],'participants':d['people'],'opening':m['opening'] if m else d['opening'] if available else '', 'choices':{k:{'label':d.get('labels',{}).get(k,v[0]),'effect':v[1].title()+' +1 for each present pair, once (maximum 12).'} for k,v in CHOICES.items()} if available else {},'memory':deepcopy(m),'blockers':r if not m else [],'available':available,'deferred':deferred,'target':d['target']}

def profile(s,who):
 import game as g
 if who not in members(s):return None
 d=g.character_profile(s,who);p=c.PERSONAL[who];h,w,_,build,note=c.PHYSICAL[who];mem=saved(s)['memories']
 return {'id':who,'name':d['name'],'basic':{'Age':str(d['adultAgeYears'])+' years','Ancestry':d['ancestryLabel'],'Height':str(h)+' cm','Approximate weight':str(w)+' kg' if w is not None else 'No fixed physical mass · spirit form','Build':build,'Dominant hand':p['hand'],'Measurement note':note},'sections':[{'id':tier,'title':title,'known':tier+':'+who in mem,'facts':section_facts(who,tier,s) if tier+':'+who in mem else {}} for tier,title in TIERS.items()]}

def ambient(s,who):
 import game as g
 if who not in members(s) or not g.character_at_castle(s,who):return None
 p=c.PERSONAL[who];assignment=g.character_assignment(s,who)
 if assignment!='rest':
  from room_life import ACTIVITIES
  return {'kind':'work','text':ACTIVITIES.get(assignment,assignment.replace('-',' ').capitalize())+'. Her current assignment is still her plan; an invitation can wait.'}
 phase=('morning','afternoon','evening').index(s['currentDayPhase']);options=[{'kind':'routine','text':p['idle'][phase]}]
 report=s.get('lastExpeditionReport')
 if report and who in report.get('participants',[]):options.append({'kind':'journey','text':'She recalls returning from '+g.EXPEDITION_SITES[report['siteId']]['name']+'. “'+p['comfort']+' That sounds rather good after fieldwork.”'})
 spells=[sp for sp in s.get('spellbook',[]) if sp['ownerId']==who and sp.get('castCount',0)>0]
 if spells:options.append({'kind':'magic','text':'She mentions her experience casting '+g.SPELL_FORMS[spells[-1]['formId']]['name']+'. “There is satisfaction in knowing what a working will actually do.”'})
 mine=[m for m in saved(s)['memories'].values() if who in m['participants'] and m['kind'] in ('pair','initiative')]
 if mine:options.append({'kind':'memory','text':'She recalls “'+mine[-1]['title']+'”. “I am glad we took time for that conversation.”'})
 return options[(s['dayNumber']*3+phase+list(c.PERSONAL).index(who))%len(options)]

def views(s):
 import room_life
 rows=[row(s,key) for key in keys(s)]
 return {'people':{who:{**profile(s,who),'roomId':room_life.location(s,who),'ambient':ambient(s,who)} for who in members(s)},'scenes':rows,'readyCount':sum(r['available'] for r in rows)}

def context(s,who):
 p=profile(s,who)
 if not p:return {}
 return {'knownProfile':{'basic':p['basic'],'disclosures':[r for r in p['sections'] if r['known']]},'rememberedMoments':[deepcopy(m) for m in saved(s)['memories'].values() if who in m['participants']][-12:]}

def apply(s,a):
 kind=a.get('type')
 if kind not in ('share-almanac','defer-almanac','restore-almanac'):return False
 import game as g
 key=a.get('sceneId');g.require(isinstance(key,str) and key in keys(s),'Choose an available invitation from a current resident.')
 r=row(s,key);g.require(not r['memory'],'This conversation is already remembered.')
 if kind=='restore-almanac':
  g.require(r['deferred'],'This invitation is not set aside.');initialize(s);saved(s)['deferred'].remove(key);return True
 g.require(r['available'],' '.join(r['blockers']) or 'Restore this invitation before sharing it.')
 if kind=='defer-almanac':initialize(s);saved(s)['deferred'].append(key);return True
 choice=a.get('choice');g.require(isinstance(choice,str) and choice in CHOICES,'Choose an offered response.')
 from social_life import stamp
 d=definition(s,key);record={'id':key,'kind':d['kind'],'title':d['title'],'participants':d['people'],'opening':d['opening'],'choice':choice,'playerLine':r['choices'][choice]['label'],'response':d['responses'][choice],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'stamp':stamp(s)}
 initialize(s);saved(s)['memories'][key]=record
 import relationships
 relationships.remember(s,'almanac:'+key,record,dimension=CHOICES[choice][1])
 g.add_journal(s,d['title']+': '+record['playerLine']+' '+record['response'])
 return True
