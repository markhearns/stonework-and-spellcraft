"""Saved procedural requests and authored companion quests. No runtime LLM."""
from copy import deepcopy
from hashlib import sha256
import character_quest_content as content
import character_approaches as apt
from conversation_voice import voice

ASSIGNMENT='character-quest'

def initialize(s):
 s.setdefault('characterQuests',{'records':{},'serial':0,'lastGeneratedDay':None,'seed':'castle-requests-v1','active':None})

def saved(s):return s.get('characterQuests',{'records':{},'serial':0,'lastGeneratedDay':None,'seed':'castle-requests-v1','active':None})

def definition(who):
 p=content.PERSONAL[who]
 return {'id':'personal:'+who,'who':who,'kind':'personal','title':p[0],'purpose':p[1],
         'steps':[p[2],p[3]],'opening':p[4],'middle':p[5],'ending':p[6],'flirt':p[7],
         'status':'offered','step':0,'pending':None,'outcomes':[],'memories':[]}

def records(s):
 import game as g
 import companion_goals
 data=saved(s)
 personal=[data['records'].get('personal:'+who,definition(who)) for who in content.PERSONAL if who in g.household_members(s)
           and (who not in companion_goals.LEGACY_CREDIT or 'ambition:'+who not in data['records'] or 'personal:'+who in data['records'])]
 return companion_goals.definitions(s)+personal+extra_records(s)+[r for r in data['records'].values() if r['kind']=='dynamic']

def extra_records(s):
 import game as g
 import headquarters
 out=[]
 for key,d in content.EXTRA_PERSONAL.items():
  who=d['who'];qid='personal:'+key
  if who not in g.household_members(s):continue
  old=saved(s)['records'].get(qid)
  if old:out.append(old);continue
  if not headquarters.ready(s,d['room']) or who+':0' not in s.get('livingStories',{}).get('memories',{}):continue
  p=d['data'];q=definition(who)
  q.update(id=qid,title=p[0],purpose=p[1],steps=[p[2],p[3]],opening=p[4],middle=p[5],ending=p[6],flirt=p[7])
  out.append(q)
 return out


def people(q):return ['founder',q['who']]

def presence(s,q):
 from household_chapters import presence as check
 import companion_goals
 reasons=check(s,people(q))
 old=saved(s)['records'].get('personal:'+q['who'])
 if q['kind']=='ambition' and q['who'] in companion_goals.LEGACY_CREDIT and old and old['status'] not in ('complete','declined'):
  reasons.append('Finish the earlier quest “'+old['title']+'” first. Its completed work will count toward this goal.')
 return reasons

def staffing(s,q):
 import game as g
 reasons=presence(s,q)
 for who in people(q):
  if g.character_assignment(s,who) not in ('rest',ASSIGNMENT):
   reasons.append(g.character_profile(s,who)['name']+' must be assigned to rest before taking quest work; current work is not replaced automatically.')
 return reasons

def active(s):return saved(s)['records'].get(saved(s)['active'])

def working(s):
 import game as g
 q=active(s)
 return bool(q and q['status']=='working' and not presence(s,q) and all(g.character_assignment(s,p)==ASSIGNMENT for p in people(q)))

def release(s,q):
 import game as g
 for who in people(q):
  if g.character_assignment(s,who)==ASSIGNMENT:g.set_character_assignment(s,who,'rest')

def caster(s,q,form):
 import game as g
 return next((p for p in s['spellbook'] if p['ownerId'] in people(q) and p['formId']==form and p['status']=='learned' and p['id'] in s['preparedSpells'].get(p['ownerId'],[]) and all(k in g.character_principles(s,p['ownerId']) for k in g.SPELL_FORMS[form]['requiredPrinciples'])),None)

def methods(s,q):
 import game as g
 step=content.OBSTACLES[q['steps'][q['step']]]
 import lasting_rituals
 ritual=content.QUEST_RITUALS[q['steps'][q['step']]]
 import lantern_adventure
 legacy=lantern_adventure.support(s,q['steps'][q['step']])
 import party_journeys
 journey=party_journeys.support(s,q['steps'][q['step']])
 supported=lasting_rituals.active(s,ritual)
 import household_sagas
 household=household_sagas.comfort(s,q['who'],q['steps'][q['step']])
 common=staffing(s,q)
 if saved(s)['active']!=q['id']:common.append('Resume this quest before choosing a method.')
 checks=[(who,apt.score(s,who,apt.spec(step['attribute'],step['skill']),people(q))) for who in people(q)]
 skilled=next((who for who,c in checks if c['qualified']),None)
 spell=caster(s,q,step['spell']);cost=g.SPELL_FORMS[step['spell']]['castingInputs']
 magic=common+([] if spell else ['A participant must know and prepare '+g.SPELL_FORMS[step['spell']]['name']+' with its principles.'])
 magic += ['Need '+str(n)+' '+k+'.' for k,n in cost.items() if s['materialInventory'].get(k,0)<n]
 result={
 'patient':{'label':step['ordinary'],'phases':2 if supported or legacy or household or journey else 3,'blockers':common,'cost':{},'journeyId':journey,'householdId':household,'legacyId':legacy,'ritualId':ritual if supported else None,'detail':'Free ordinary route. No attribute or spell required.'+(' A displayed expedition legacy saves one phase; it does not stack with other support.' if journey else '')+(' Their shared household project saves one phase; this does not stack with other support.' if household else '')+(' Active '+lasting_rituals.CATALOGUE[ritual]['name']+' saves one phase; this duration is committed when you choose the method.' if supported else '')+(' The installed lantern corner supports this method; its two-phase duration does not stack with a ritual.' if legacy else '')},
 'skilled':{'label':'Use '+g.CHARACTER_SKILLS[step['skill']]['name']+' to solve it efficiently','phases':1,'blockers':common+([] if skilled else ['Need score 9: attribute + twice skill, with eligible companion help.']), 'actor':skilled,'cost':{},'detail':'; '.join(g.character_profile(s,who)['name']+': '+check['detail'] for who,check in checks)},
 'spell':{'label':'Cast '+g.SPELL_FORMS[step['spell']]['name'],'phases':1,'blockers':magic,'actor':spell['ownerId'] if spell else None,'spellId':spell['id'] if spell else None,'formId':step['spell'],'cost':deepcopy(cost),'detail':'Components are committed once. This cast solves this quest obstacle only; it does not also grant the ordinary free-cast effect.'}}
 if q['kind']=='ambition':
  import companion_goals
  return companion_goals.enrich_methods(s,q,result)
 return result

def talk_options(q):
 if q['kind']=='ambition':
  import companion_goals
  return companion_goals.choices(q)
 if q['status']=='offered':return {'flirt':'Accept with a playful compliment.','warm':'Accept because this matters to them.','practical':'Accept and ask where to begin.'}
 if q['status']=='interlude':return {'flirt':'Tease gently, then support their decision.','warm':'Ask what they want to preserve.','practical':'Agree the next practical step.'}
 if q['status']=='ending':return {'flirt':'Return the flirtation and enjoy the moment.','warm':'Celebrate together as friends.','practical':'Admire the result and thank them for the company.'}
 return {}

def opening(q):
 if q['kind']=='ambition':
  import companion_goals
  return companion_goals.opening(q)
 if q['status']=='offered':return q['opening']
 if q['status']=='interlude':return q['middle']
 if q['status']=='ending':return q['ending']
 return ''

def row(s,q):
 reasons=presence(s,q)
 other=active(s)
 if q['status']!='complete' and other and other['id']!=q['id']:reasons.append('Finish or set aside the current quest first.')
 visible=not reasons
 result={k:deepcopy(q[k]) for k in ('id','who','kind','title','purpose','status','step','pending','outcomes','memories')}
 result.update({'opening':opening(q) if visible else '', 'blockers':reasons,
  'choices':talk_options(q) if visible else {},
  'obstacle':content.OBSTACLES[q['steps'][q['step']]]['name'] if q['status'] in ('ready','working') else None,
  'methods':methods(s,q) if q['status']=='ready' and visible else {},
  'resumeBlockers':list(dict.fromkeys(staffing(s,q)+reasons)), 'isWorking':working(s) if other and other['id']==q['id'] else False,
  'reward':'2 advancement each and a named keepsake; once only.' if q['kind']=='personal' else '2 binding thread; no repeatable advancement. Relationship credit once per request type and companion.'})
 result['totalSteps']=len(q['steps'])
 if q['kind']=='ambition':
  import companion_goals
  d=companion_goals.GOALS[q['who']]
  result['reward']='On completion: '+d['keepsake']+'. 2 advancement each, once. Friendship is sufficient.'
  result['proof']=d['proof']
  if q['status'] in ('ready','working'):result['obstacle']=companion_goals.current(q)['title']
 return result

def board_blockers(s):
 import game as g
 data=saved(s);reasons=[]
 if not any(p in g.household_members(s) for p in content.PERSONAL):reasons.append('Recruit a unique companion to unlock their personal requests.')
 if data['lastGeneratedDay']==s['dayNumber']:reasons.append('Today’s request batch has already been generated. Advance into another day for more.')
 if sum(q['kind']=='dynamic' and q['status'] not in ('complete','declined') for q in data['records'].values())>=3:reasons.append('Finish or decline a request to make space on the three-request board. Nothing expires.')
 return reasons

def view(s):
 return {'quests':[row(s,q) for q in records(s)],'boardBlockers':board_blockers(s),'activeId':saved(s)['active'],
         'keepsakes':[{'title':q['title'],'who':q['who'],'name':q['title']+' — a shared keepsake'} for q in saved(s)['records'].values() if q['kind']=='personal' and q['status']=='complete']}

def context(s,who):
 return deepcopy([{'title':q['title'],'status':q['status'],'outcomes':q['outcomes'],'memories':q['memories']} for q in saved(s)['records'].values() if q['who']==who and q['memories']])

def generate(s):
 import game as g
 data=saved(s);patrons=[p for p in content.PERSONAL if p in g.household_members(s)]
 slots=3-sum(q['kind']=='dynamic' and q['status'] not in ('complete','declined') for q in data['records'].values())
 for _ in range(slots):
  data['serial']+=1;number=data['serial'];digest=sha256((data['seed']+':'+str(number)+':'+str(s['dayNumber'])).encode()).digest()
  who=patrons[int.from_bytes(digest[:2],'big')%len(patrons)];template=digest[2]%len(content.TEMPLATES)
  title,first,second,premise=content.TEMPLATES[template];place=content.PLACES[digest[3]%len(content.PLACES)];mood=content.MOODS[digest[4]%len(content.MOODS)]
  name=g.character_profile(s,who)['name'];q=definition(who)
  q.update({'id':'request:'+str(number),'kind':'dynamic','template':template,'title':name+' and '+title,'purpose':premise,'steps':[first,second],
    'opening':name+' asks for help at '+place+'. '+premise+' The invitation comes with '+mood+'.',
    'middle':'The first problem is solved at '+place+'. '+name+' checks the result with you before taking on the second part. “Let us finish this properly. Then we can enjoy ourselves.”',
    'ending':'Both parts of the request are complete at '+place+'. '+name+' puts the work aside. '+content.PERSONAL[who][6],
    'place':place,'mood':mood})
  # Dynamic endings must not claim the separate personal quest was completed.
  q['ending']='Both parts of the request are complete at '+place+'. '+name+' puts the work aside and offers you a place beside them for a small celebration. The promised reward is ready, whatever tone you choose.'
  q['flirt']=content.REQUEST_FLIRT[who]
  if digest[4]%len(content.MOODS)==2:q['ending']+=' Keeping the playful promise, '+name+' changes into a festive outfit for the celebration.'
  data['records'][q['id']]=q
 data['lastGeneratedDay']=s['dayNumber']

def apply(s,a):
 kind=a.get('type')
 if kind not in ('generate-character-quests','talk-character-quest','choose-quest-method','pause-character-quest','resume-character-quest','decline-character-quest'):return False
 import game as g
 import relationships
 if kind=='generate-character-quests':
  reasons=board_blockers(s);g.require(not reasons,' '.join(reasons));initialize(s);generate(s);return True
 key=a.get('questId');g.require(isinstance(key,str),'Choose a known quest.')
 q=next((q for q in records(s) if q['id']==key),None);g.require(q is not None,'Choose a current companion’s quest.')
 g.require(q['status'] not in ('complete','declined'),'This quest is already concluded.')
 if kind=='pause-character-quest':
  g.require(saved(s)['active']==key,'This quest is not active.')
  release(s,q);saved(s)['active']=None;q['paused']=True;return True
 if kind=='decline-character-quest':
  g.require(q['kind']=='dynamic' and q['status']=='offered','Only an unaccepted procedural request can be declined; accepted quests can be set aside.')
  q['status']='declined';return True
 reasons=presence(s,q);g.require(not reasons,' '.join(reasons))
 if kind=='resume-character-quest':
  g.require((q.get('paused') or (q['status']=='working' and not working(s))) and saved(s)['active'] in (None,key),'Set aside your other quest first, or choose an accepted paused quest.')
  reasons=staffing(s,q) if q['status']=='working' else []
  g.require(not reasons,' '.join(reasons));saved(s)['active']=key;q['paused']=False
  if q['status']=='working':
   for who in people(q):g.set_character_assignment(s,who,ASSIGNMENT)
  return True
 if kind=='choose-quest-method':
  g.require(saved(s)['active']==key and q['status']=='ready','Resume this quest and reach an unresolved obstacle first.')
  method=a.get('methodId');g.require(isinstance(method,str) and method in ('patient','skilled','spell'),'Choose an offered method.')
  selected=methods(s,q)[method];g.require(not selected['blockers'],' '.join(selected['blockers']))
  s['sharedFunds']-=selected.get('crowns',0)
  for material,n in selected['cost'].items():s['materialInventory'][material]-=n
  if selected.get('spellId'):g.spell_by_id(s,selected['spellId'])['castCount']+=1
  q['pending']={'method':method,'label':selected['label'],'remaining':selected['phases'],'actor':selected.get('actor'),'spellId':selected.get('spellId'),'cost':deepcopy(selected['cost']),'crowns':selected.get('crowns',0),'ritualId':selected.get('ritualId'),'legacyId':selected.get('legacyId'),'householdId':selected.get('householdId'),'journeyId':selected.get('journeyId')}
  q['status']='working'
  for who in people(q):g.set_character_assignment(s,who,ASSIGNMENT)
  g.add_journal(s,q['title']+': '+selected['label']+'. Advance resolves '+str(selected['phases'])+' assigned quest phase(s).');return True
 options=talk_options(q);choice=a.get('choice')
 g.require(isinstance(choice,str) and choice in options,'Choose an offered response.')
 g.require(saved(s)['active'] in (None,key) and (q['status']=='offered' or saved(s)['active']==key),'Resume this quest, or set aside the current quest first.')
 old_status=q['status'];text=opening(q)
 if q['kind']=='ambition':
  import companion_goals
  reply=companion_goals.reply(q,choice)
 elif old_status=='ending':
  reply=q['flirt'] if choice=='flirt' else (voice(q['who'])['company'] if choice=='warm' else voice(q['who'])['review']+' You check the finished work together. '+q['outcomes'][-1]['result'])
 else:
  obstacle=content.OBSTACLES[q['steps'][q['step']]]
  next_step='The next task is to '+obstacle['name'][0].lower()+obstacle['name'][1:]+'. One way to do it: '+obstacle['ordinary']+'.'
  reply=({'flirt':content.QUEST_TEASING[q['who']]+' You agree to help with the request. '+next_step,
          'warm':'You agree to keep the original aim: '+q['purpose']+'. '+voice(q['who'])['review']+' '+next_step,
          'practical':next_step+' You can compare the available methods before assigning anyone to the work.'})[choice]
 initialize(s);saved(s)['records'][key]=q;saved(s)['active']=key
 memory={'title':q['title'],'participants':people(q),'stage':old_status,'opening':text,'choice':choice,'playerLine':options[choice],'response':reply,'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
 if old_status=='ending' and choice=='flirt':
  import romance
  memory['response']=romance.quest_reply(s,q['who'],memory['response'])
 if old_status=='ending' and q['kind']!='ambition':memory['response']+=' You remember choosing “'+q['memories'][0]['playerLine']+'” when this began, and solving it through '+', then '.join(o['method'] for o in q['outcomes'])+'.'
 q['memories'].append(memory)
 if old_status=='ending':
  q['status']='complete';saved(s)['active']=None;release(s,q)
  if q['kind']=='ambition':
   companion_goals.finish(s,q)
  elif q['kind']=='personal':
   for who in people(q):g.award_advancement(s,who,'character-quest:'+key,2,q['title'])
  else:s['materialInventory']['binding-thread']=s['materialInventory'].get('binding-thread',0)+2
  source='quest:'+key if q['kind'] in ('personal','ambition') else 'quest-request:'+q['who']+':'+str(q['template'])
  relationships.remember(s,source,memory,'trust' if q['kind']=='ambition' else {'flirt':'affection','warm':'trust','practical':'respect'}[choice])
 else:q['status']='ready'
 g.add_journal(s,q['title']+': '+memory['playerLine']+' '+memory['response']);return True

def resolve(s,summary,eligible):
 q=active(s)
 if not eligible or not working(s):return
 q['pending']['remaining']-=1
 summary.append(q['title']+': one shared quest phase completed.')
 if q['pending']['remaining']>0:return
 import companion_goals
 result=companion_goals.result(q) if q['kind']=='ambition' else content.OBSTACLES[q['steps'][q['step']]]['result']
 q['outcomes'].append({'obstacle':q['steps'][q['step']],'method':q['pending']['label'],'actor':q['pending']['actor'],'spellId':q['pending']['spellId'],'ritualId':q['pending'].get('ritualId'),'legacyId':q['pending'].get('legacyId'),'householdId':q['pending'].get('householdId'),'journeyId':q['pending'].get('journeyId'),'result':result})
 q['pending']=None;release(s,q);q['step']+=1;q['status']='ending' if q['step']==len(q['steps']) else 'interlude'
 summary.append(q['outcomes'][-1]['result']+' An optional conversation is ready; no time passes until you choose Advance again.')
