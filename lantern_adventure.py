"""Multi-companion pavilion expedition with persistent fieldwork and a castle legacy."""
from copy import deepcopy
import character_approaches as apt
from lantern_content import SITE,CAST,DEFINITION,STEPS,PURPOSES,BEATS,CAMP,HOME

def initialize(s):s.setdefault('lanternAdventure',{'completed':[],'pending':None,'outcomes':[],'discoveries':[],'memories':{},'legacy':None,'installed':False,'returners':[]})
def saved(s):return s.get('lanternAdventure',{'completed':[],'pending':None,'outcomes':[],'discoveries':[],'memories':{},'legacy':None,'installed':False,'returners':[]})
def step(s):return next((d for d in STEPS if d['id'] not in saved(s)['completed']),None)
def is_active(s):return bool(s.get('expedition') and s['expedition']['siteId']==SITE)

def pairing(s,c):
 import game as g
 party=g.expedition_party(s)
 if not c.get('team'):return None
 for first in party:
  for second in party:
   if first!=second and apt.score(s,first,c['team'][0])['qualified'] and apt.score(s,second,c['team'][1])['qualified']:
    if 'casterRole' in c:
     caster=[first,second][c['casterRole']]
     if not any(p['ownerId']==caster and p['formId']==c['castForm'] and p['status']=='learned' and p['id'] in s['preparedSpells'][caster] and all(k in g.character_principles(s,caster) for k in g.SPELL_FORMS[c['castForm']]['requiredPrinciples']) for p in s['spellbook']):continue
    return [first,second]
 return None

def blockers(s,c):
 import game as g
 reasons=g.encounter_choice_blockers(s,c)
 if c.get('team') and not pairing(s,c):
  reasons.append('Two different expedition participants must fill these roles: '+'; '.join(g.character_builds.ATTRIBUTES[r['attribute']]['name']+' + twice '+g.CHARACTER_SKILLS[r['skill']]['name']+' at '+str(r['threshold']) for r in c['team'])+'. Ordinary solo routes remain available.')
 if c.get('castForm') and not caster_for(s,c):reasons.append('The prepared caster must fill the specified casting role and have learned its principles; all spell components are required.')
 return reasons

def view(s):
 if not is_active(s):return None
 d=step(s);p=saved(s)
 progress={**deepcopy(p),'completedSteps':p['completed'][:],'pendingWork':{**deepcopy(p['pending']),'remainingWorkPhases':p['pending']['remaining']} if p['pending'] else None}
 return {'progress':progress,'totalSteps':len(STEPS),'step':deepcopy(d),'choices':{k:{**deepcopy(c),'description':description(c),'blockers':blockers(s,c),'participants':pairing(s,c)} for k,c in d['choices'].items()} if d else {}}

def resume(s):
 e=s['expedition'];p=saved(s)
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p['pending']:
  import game as g
  c=step(s)['choices'][p['pending']['methodId']]
  if c.get('team') and not all(w in g.expedition_party(s) and apt.score(s,w,role)['qualified'] for w,role in zip(p['pending']['participants'],c['team'])):e['stage']='encounter-choice'
  else:e.update(stage='working',remainingWorkPhases=p['pending']['remaining'])
 else:e['stage']='encounter-choice'

def apply(s,action):
 if extra_action(s,action):return True
 if action.get('type')!='choose-encounter-method' or not is_active(s):return False
 import game as g, field_magic
 e=s['expedition'];d=step(s);key=action.get('methodId')
 g.require(e['stage']=='encounter-choice' and d is not None,'Choose a method when the party reaches the next obstacle.')
 g.require(isinstance(key,str) and key in d['choices'],'Choose an offered pavilion method.')
 c=d['choices'][key];reasons=blockers(s,c);g.require(not reasons,' '.join(reasons))
 caster=caster_for(s,c)
 if caster:
  for k,n in g.SPELL_FORMS[c['castForm']]['castingInputs'].items():s['materialInventory'][k]-=n
  caster['castCount']+=1
 saved(s)['pending']={'casterId':caster['ownerId'] if caster else None,'stepId':d['id'],'methodId':key,'remaining':c['phases'],'participants':pairing(s,c) or g.expedition_party(s),'magicPaid':c.get('castForm')}
 e.update(stage='working',remainingWorkPhases=c['phases']);g.add_journal(s,d['name']+': '+c['name']+'. '+str(c['phases'])+' phase(s).')
 return True

def resolve(s):
 import game as g, companion_participation as company
 e=s['expedition'];p=saved(s);party=g.expedition_party(s)
 if e['stage']=='working':
  job=p['pending']
  for who in party:
   if who not in job.setdefault('contributors',[]):job['contributors'].append(who)
  job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
  if job['remaining']:return
  d=step(s);c=d['choices'][job['methodId']]
  if d['id']=='legacy':p['legacy']=job['methodId']
  p['completed'].append(d['id']);p['outcomes'].append({'stepId':d['id'],'name':d['name'],'methodId':job['methodId'],'method':c['name'],'participants':job['contributors'][:],'casterId':job.get('casterId'),'team':bool(c.get('team')),'magic':bool(c.get('castForm'))})
  g.add_journal(s,d['name']+' completed: '+c['name']+'.');s['lastPhaseSummary'].append(d['name']+' completed.');p['pending']=None;resume(s)
 else:
  rewards=['Returned safely. Completed obstacles and any unfinished, paid method are retained.']
  if e['discoveryReady'] and not p['discoveries']:
   p['discoveries'].append('survey');s['materialInventory']['moon-glass']+=2;s['materialInventory']['binding-thread']+=3
   p['returners']=party[:]
   rewards=['2 moon glass and 3 binding thread deposited. Recovered the pavilion lantern, songbook and ledger. Fit the lantern corner in the common room when ready.']
   for who in party:g.award_advancement(s,who,SITE,3,'Recovered the lantern pavilion’s shared legacy')
  # Companion debriefs belong to this adventure, not the beacon invitation catalogue.
  s['lastExpeditionReport']={'siteId':SITE,'approach':e['chosenApproach'],'returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
  if e['restoreLanternDisplay']:s['lanternDisplayed']=True
  s['expedition']=None
  for who in party:g.set_character_assignment(s,who,'rest')
  s['lastPhaseSummary']+=rewards

def caster_for(s,c):
 import field_magic as f,game as g
 if not c.get('castForm'):return None
 candidates=[p for p in s['spellbook'] if p['ownerId'] in g.expedition_party(s) and p['formId']==c['castForm'] and p['status']=='learned' and p['id'] in s['preparedSpells'][p['ownerId']]]
 d=g.SPELL_FORMS[c['castForm']]
 candidates=[p for p in candidates if all(k in g.character_principles(s,p['ownerId']) for k in d['requiredPrinciples']) and all(s['materialInventory'][k]>=n for k,n in d['castingInputs'].items())]
 if 'casterRole' in c:
  pair=pairing(s,c)
  candidates=[p for p in candidates if pair and p['ownerId']==pair[c['casterRole']]]
 return candidates[0] if candidates else None

def description(c):
 import game as g
 text=c['description']
 if c.get('castForm'):
  d=g.SPELL_FORMS[c['castForm']]
  text+=' Requires learned, prepared '+d['name']+'. Components committed once: '+' + '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['castingInputs'].items())+'.'
 return text

def extra_action(s,a):
 import game as g,solo_life,relationships,romance
 kind=a.get('type')
 if kind=='place-lantern-corner':
  g.require(saved(s)['discoveries'] and saved(s)['legacy'] in PURPOSES,'Recover the pavilion lantern and bring it home first.')
  g.require(g.character_at_castle(s,'founder'),'Return home to arrange the common room.')
  g.require(type(a.get('installed')) is bool,'Choose whether the lantern corner is installed.')
  saved(s)['installed']=a['installed'];g.add_journal(s,('Installed ' if a['installed'] else 'Put away ')+PURPOSES[saved(s)['legacy']][0]+'.');return True
 if kind!='share-lantern-scene':return False
 key=a.get('sceneId');g.require(isinstance(key,str),'Choose a known adventure scene.')
 row=next((r for r in scene_rows(s) if r['id']==key),None)
 g.require(row is not None and row['available'],'Share this scene with its actual participants at the appropriate point in the journey.')
 choice=a.get('choice');g.require(isinstance(choice,str) and choice in row['choices'],'Choose an offered response.')
 selected=row['choices'][choice];g.require(not selected.get('blockers'),' '.join(selected.get('blockers',[])))
 record={'id':key,'title':row['title'],'opening':row['opening'],'participants':row['participants'][:],'choice':choice,'playerLine':selected['label'],'response':selected['response'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
 saved(s)['memories'][key]=record
 relationships.remember(s,'lantern:'+key,record,'affection' if choice=='affection' else 'respect' if choice in ('names','humble','history') else 'trust')
 g.add_journal(s,row['title']+': '+record['playerLine']+' '+record['response']);return True

def scene_rows(s):
 import game as g,romance
 from household_chapters import presence
 p=saved(s);field=is_active(s)
 home_party=[who for who in p['returners'] if who in g.household_members(s)]
 home_ready=bool(p['discoveries'] and 'founder' in home_party and not presence(s,home_party))
 party=g.expedition_party(s) if field else home_party
 candidates=[]
 for key,d in BEATS.items():
  members=party if party else ['founder']
  ready=((field and s['expedition']['stage'] not in ('outbound','returning')) or home_ready) and len(p['completed'])>=d['after']
  opening=d['opening']+'\n\n'+'\n'.join(d['voices'][who] for who in CAST if who in members)
  if all(who in members for who in CAST):opening+='\n\n'+d['pair']
  if not field and home_ready:opening='Back at the castle, you open the expedition notes together and discuss the question you left for later. '+opening.replace('Before the work begins, there is time to decide what deserves attention.','There is still time to discuss what deserved attention.').replace('On a dry rest ledge beyond the crossing, the packed food is divided and the programme is spread where everyone can reach it.','You remember the dry rest ledge beyond the crossing and spread the programme on the table at home.')
  previous=p['memories'].get('arrival')
  if key!='arrival' and previous:opening+='\n\nYou previously chose: “'+previous['playerLine']+'”.'
  candidates.append((key,d['title'],members,ready,opening,{k:{'label':v[0],'response':v[1]} for k,v in d['choices'].items()}))
 for who in CAST:
  title,opening,response=CAMP[who]
  ready=who in party and len(p['completed'])>=2 and ((field and s['expedition']['stage'] not in ('outbound','returning')) or home_ready)
  if not field and home_ready:opening='Back home, you find a quiet place to talk about the journey. '+opening
  choices={'company':{'label':'Enjoy the quiet company','response':response},'affection':{'label':'Share an affectionate moment in your established relationship','response':romance.quest_reply(s,who,response),'blockers':[] if romance.level(s,who)>=1 else ['First share mutual attraction at home. The friendship scene is always available.']}}
  candidates.append(('camp:'+who,title,['founder',who],ready,opening,choices))
 if p['discoveries']:
  members=[who for who in p['returners'] if who in g.household_members(s)]
  ready=p['installed'] and 'founder' in members and not presence(s,members)
  opening='The recovered lantern now lights the '+PURPOSES[p['legacy']][0].lower()+'. All three finds have a place here, whichever purpose you chose.\n\n'+'\n'.join(HOME[who] for who in CAST if who in members)
  if all(who in members for who in CAST):opening+='\n\nMira asks Iona to check a notation. Tamsin sits down before offering an opinion. Iona laughs and moves the spare chair closer. They have begun using the corner without waiting for you to mediate.'
  candidates.append(('home','The first evening under the recovered light',members,ready,opening,{'join':{'label':'Join them and let the evening find its own shape','response':'The archive, tune and table can coexist. You join a conversation that belongs to the household, rather than a committee waiting for your verdict.'},'notice':{'label':'Recognise what each person helped preserve','response':'You name the care, practical work and delight that brought the corner home. Nobody’s contribution is reduced to a supporting footnote.'}}))
 rows=[]
 for key,title,members,ready,opening,choices in candidates:
  memory=p['memories'].get(key)
  rows.append({'id':key,'title':title,'participants':memory['participants'][:] if memory else members[:],'opening':memory['opening'] if memory else opening if ready else '',
   'available':bool(ready and not memory),'memory':deepcopy(memory),'choices':choices if ready and not memory else {}})
 return rows

def adventure_view(s):
 import game as g,solo_life
 rows=scene_rows(s)
 for row in rows:
  row['choices']={k:{'label':v['label'],'blockers':v.get('blockers',[])} for k,v in row['choices'].items()}
 p=saved(s)
 return {'active':is_active(s),'scenes':rows,'cast':[{'id':who,'name':g.character_profile(s,who)['name'],'blockers':solo_life.companion_blockers(s,who)} for who in CAST if who in g.household_members(s)],
  'completed':bool(p['discoveries']),'installed':p['installed'],'legacy':p['legacy'],'legacyName':PURPOSES[p['legacy']][0] if p['legacy'] else None,
  'helps':list(PURPOSES[p['legacy']][1]) if p['legacy'] else [],'canPlace':bool(p['discoveries'] and g.character_at_castle(s,'founder')),
  'party':g.expedition_party(s) if is_active(s) else [],'outcomes':deepcopy(p['outcomes'])}

def support(s,obstacle):
 p=saved(s)
 return p['legacy'] if p['installed'] and p['discoveries'] and p['legacy'] in PURPOSES and obstacle in PURPOSES[p['legacy']][1] else None

def context(s,who):return deepcopy([m for m in saved(s)['memories'].values() if who in m['participants']])
