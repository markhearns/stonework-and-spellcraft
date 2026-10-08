"""Persistent party journeys, real participants and deterministic authored methods."""
from copy import deepcopy
from itertools import combinations
import party_journey_content as content
import character_approaches as apt

SITES=content.SITES

def empty():return {'completed':[],'pending':None,'outcomes':[],'discoveries':[],'memories':{},'returners':[],'ending':None,'installed':False,'inscriptions':[]}
def initialize(s):s.setdefault('partyJourneys',{key:empty() for key in SITES})
def saved(s,site):return s.get('partyJourneys',{}).get(site,empty())
def active(s):return bool(s.get('expedition') and s['expedition'].get('siteId') in SITES)
def site(s):return s['expedition']['siteId']
def step(s):return next((d for d in SITES[site(s)]['steps'] if d['id'] not in saved(s,site(s))['completed']),None)

def party_selection(s,a):
 import game as g,solo_life
 selected=a.get('companionIds',([a['companionId']] if a.get('companionId') is not None else []))
 g.require(isinstance(selected,list) and len(selected)<=3 and all(isinstance(w,str) for w in selected),'Choose up to three willing resident companions.')
 g.require(len(set(selected))==len(selected),'Choose each companion only once.')
 if 'companionIds' in a and a.get('companionId') is not None:g.require(a['companionId'] in selected,'The individual companion must also be in the selected party.')
 reasons=[reason for who in selected for reason in solo_life.companion_blockers(s,who)]
 g.require(not reasons,' '.join(reasons))
 return selected[:]

def qualified(s,who,req):
 import game as g
 return apt.score(s,who,req,g.expedition_party(s),True)

def pairing(s,c):
 import game as g
 if not c.get('team'):return None
 return next(([a,b] for a in g.expedition_party(s) for b in g.expedition_party(s) if a!=b and qualified(s,a,c['team'][0])['qualified'] and qualified(s,b,c['team'][1])['qualified']),None)

def conductor(s,c):
 import game as g
 return next((w for w in g.expedition_party(s) if all(p in g.character_principles(s,w) for p in c.get('ritualPrinciples',[]))),None)

def blockers(s,c):
 import game as g,field_magic
 r=[]
 if c.get('team') and not pairing(s,c):r.append('Two distinct present people must meet the two role scores of 8. The free ordinary route remains available.')
 if c.get('aptitude') and not any(qualified(s,w,c['aptitude'])['qualified'] for w in g.expedition_party(s)):r.append('A present person needs score 9 in '+c['aptitude']['attribute']+' + twice '+c['aptitude']['skill']+'.')
 if c.get('castForm') and not field_magic.existing_caster(s,c['castForm']):r.append('Learn and prepare '+g.SPELL_FORMS[c['castForm']]['name']+' on a present caster and carry its listed components.')
 if c.get('ritualPrinciples') and not conductor(s,c):r.append('One present conductor must have learned '+', '.join(g.PRINCIPLE_NAMES[p] for p in c['ritualPrinciples'])+'.')
 for k,n in c.get('inputs',{}).items():
  if s['materialInventory'][k]-s['materialReserveTargets'][k]<n:r.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
 return r

def description(c):
 import game as g
 text=c['description']
 if c.get('castForm'):
  d=g.SPELL_FORMS[c['castForm']];text+=' Components: '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['castingInputs'].items())+'.'
 if c.get('ritualPrinciples'):text+=' Principles: '+', '.join(g.PRINCIPLE_NAMES[p] for p in c['ritualPrinciples'])+'.'
 return text

def resume_blockers(s):
 import game as g
 job=saved(s,site(s))['pending']
 if not job:return []
 party=g.expedition_party(s)
 if job.get('support'):
  return [] if job['casterId'] in party and job['targetId'] in party else ['The original caster and recipient must return to finish this paid casting. Choose an ordinary method to replace it without a refund.']
 c=step(s)['choices'][job['methodId']]
 if c.get('team') and not all(w in party and qualified(s,w,role)['qualified'] for w,role in zip(job['actors'],c['team'])):return ['The original two qualified workers must return to resume this method. You can choose another route; committed costs are not refunded.']
 if job.get('casterId') and job['casterId'] not in party:return ['The original caster must return to finish this paid method. You can choose another route; committed costs are not refunded.']
 if c.get('ritualPrinciples') and not all(p in g.character_principles(s,job['casterId']) for p in c['ritualPrinciples']):return ['The original ritual conductor must still know both principles.']
 if c.get('aptitude') and not all(w in party for w in job['actors']):return ['The original specialist must return, or choose another method.']
 return []

def resume(s):
 e=s['expedition'];p=saved(s,site(s))
 if not step(s):e.update(stage='ready-to-return',discoveryReady=True)
 elif p['pending'] and not resume_blockers(s):e.update(stage='working',remainingWorkPhases=p['pending']['remaining'])
 else:e.update(stage='encounter-choice',remainingWorkPhases=0)

def patient_support(s):
 import game as g,field_magic,spell_support
 for who in g.expedition_party(s):
  buffs=field_magic.progress(s)['buffs'].get(who,{})
  for kind in ('haste','scout'):
   if buffs.get(kind,0)>0:return {'who':who,'kind':kind}
  if spell_support.bonus(s,who,'haste')>0:return {'who':who,'kind':'prepared haste'}
 return None

def view(s):
 if not active(s):return None
 import game as g
 p=saved(s,site(s));d=step(s)
 progress={**deepcopy(p),'completedSteps':p['completed'][:],'pendingWork':{**deepcopy(p['pending']),'remainingWorkPhases':p['pending']['remaining']} if p['pending'] else None}
 choices={}
 if d:
  for k,c in d['choices'].items():
   acceleration=patient_support(s) if k=='patient' else None
   choices[k]={**deepcopy(c),'phases':c['phases']-int(bool(acceleration)),'description':description(c)+(' An available '+acceleration['kind']+' charge reduces this choice to two phases; the charge is spent when you choose.' if acceleration else ''),'blockers':blockers(s,c),'participants':pairing(s,c),'scores':{w:qualified(s,w,c['aptitude']) for w in g.expedition_party(s)} if c.get('aptitude') else {}}
 return {'progress':progress,'step':deepcopy(d),'choices':choices,'totalSteps':len(SITES[site(s)]['steps']),'resumeBlockers':resume_blockers(s)}

def apply(s,a):
 kind=a.get('type')
 if kind not in ('share-party-journey','place-journey-legacy','journey-support') and not (kind=='choose-encounter-method' and active(s)):return False
 candidate=deepcopy(s);_apply(candidate,a);s.clear();s.update(candidate);return True

def _apply(s,a):
 import game as g,field_magic,relationships,spell_support,romance,headquarters
 kind=a['type']
 if kind=='place-journey-legacy':
  key=a.get('siteId');g.require(isinstance(key,str) and key in SITES,'Choose a recovered journey legacy.')
  p=saved(s,key);d=SITES[key]
  g.require(p['discoveries'] and g.character_at_castle(s,'founder'),'Bring the completed expedition home first.')
  g.require(type(a.get('installed')) is bool,'Choose whether to display the legacy.')
  g.require(not a['installed'] or headquarters.ready(s,d['room']),'Restore the legacy’s room before displaying it.')
  p['installed']=a['installed'];g.add_journal(s,('Displayed ' if a['installed'] else 'Stored ')+d['legacy']+'.');return
 if kind=='share-party-journey':
  key=a.get('siteId');g.require(isinstance(key,str) and key in SITES,'Choose a known journey.')
  row=next((r for r in scenes(s,key) if r['id']==a.get('sceneId')),None)
  g.require(row is not None and row['available'],'Share this scene with its actual participants at the appropriate point. Remembered scenes can be reread.')
  choice=a.get('choice');g.require(isinstance(choice,str) and choice in row['choices'],'Choose an offered response.')
  c=row['choices'][choice];g.require(not c.get('blockers'),' '.join(c.get('blockers',[])))
  record={'id':row['id'],'title':row['title'],'opening':row['opening'],'participants':row['participants'][:],'choice':choice,'playerLine':c['label'],'response':c['response'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  if row['id'].startswith('private:'):record['relationshipLevel']=romance.level(s,row['participants'][-1])
  saved(s,key)['memories'][row['id']]=record
  relationships.remember(s,'journey:'+key+':'+row['id'],record,'affection' if choice=='affection' else 'respect' if choice=='credit' else 'trust')
  g.add_journal(s,row['title']+': '+record['response']);return
 g.require(active(s) and s['expedition']['stage']=='encounter-choice' and step(s) is not None,'Choose a method when the party reaches an obstacle.')
 p=saved(s,site(s));e=s['expedition'];party=g.expedition_party(s)
 if kind=='journey-support':
  spell=next((x for x in s['spellbook'] if x['id']==a.get('spellId')),None);target=a.get('targetId')
  g.require(spell is not None and spell['formId'] in SUPPORT_FORMS and spell['ownerId'] in party,'Choose a present caster’s support spell.')
  g.require(target in party,'Choose a present recipient.')
  form=g.SPELL_FORMS[spell['formId']]
  g.require(spell['status']=='learned' and spell['id'] in s['preparedSpells'][spell['ownerId']] and all(q in g.character_principles(s,spell['ownerId']) for q in form['requiredPrinciples']),'Learn and prepare the caster’s own spell and principles first.')
  g.require(not p['pending'],'Resume or replace the unfinished method before starting a support casting.')
  for k,n in form['castingInputs'].items():g.require(s['materialInventory'][k]>=n,'Carry the listed casting components.')
  if spell['formId']=='mending-light':g.require(field_magic.vitality(s,target)<6,'This recipient already has full vitality.')
  for k,n in form['castingInputs'].items():s['materialInventory'][k]-=n
  spell['castCount']+=1;p['pending']={'support':spell['formId'],'casterId':spell['ownerId'],'targetId':target,'remaining':1,'contributors':[]}
  e.update(stage='working',remainingWorkPhases=1);return
 d=step(s);key=a.get('methodId');g.require(isinstance(key,str) and key in d['choices'],'Choose an offered journey method.')
 c=d['choices'][key];reasons=blockers(s,c);g.require(not reasons,' '.join(reasons))
 caster=field_magic.existing_caster(s,c['castForm']) if c.get('castForm') else None
 actors=pairing(s,c) or ([next(w for w in party if qualified(s,w,c['aptitude'])['qualified'])] if c.get('aptitude') else party[:])
 checks=list(zip(actors,c.get('team',[]))) if c.get('team') else [(actors[0],c['aptitude'])] if c.get('aptitude') else []
 for w,req in checks:
  check=qualified(s,w,req)
  if check['buff']:field_magic.progress(s)['buffs'][w][check['buff']]-=1
 if caster:
  for k,n in g.SPELL_FORMS[c['castForm']]['castingInputs'].items():s['materialInventory'][k]-=n
  caster['castCount']+=1
 for k,n in c.get('inputs',{}).items():s['materialInventory'][k]-=n
 support=patient_support(s) if key=='patient' else None
 phases=c['phases']-int(bool(support))
 if support:
  who=support['who'];kind=support['kind']
  if kind=='prepared haste':spell_support.consume(s,who,'haste',[],include_haste=False)
  else:field_magic.progress(s)['buffs'][who][kind]-=1
 p['pending']={'stepId':d['id'],'methodId':key,'remaining':phases,'required':phases,'actors':actors,'casterId':caster['ownerId'] if caster else conductor(s,c) if c.get('ritualPrinciples') else None,'contributors':[],'supportUsed':support}
 e.update(stage='working',remainingWorkPhases=phases);g.add_journal(s,d['name']+': '+c['name']+' · '+str(phases)+' phase(s).')

SUPPORT_FORMS={'mending-light':'Restore 3 vitality, or 4 with an active healer specialization (up to 6).','borrowed-hour':'Shorten the next three ordinary journey obstacles by one phase each.','giant-grasp':'Add 3 Might to the next two qualifying specialist/team roles.','lucid-sight':'Add 3 Intelligence to the next two qualifying specialist/team roles.','wisp-scout':'Preview the next obstacle and shorten two ordinary obstacles by one phase each.'}

def resolve(s):
 import game as g,field_magic
 key=site(s);d=SITES[key];p=saved(s,key);e=s['expedition'];party=g.expedition_party(s)
 if e['stage']=='working':
  job=p['pending']
  for w in party:
   if w not in job['contributors']:job['contributors'].append(w)
  job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
  if job['remaining']:return
  if job.get('support'):
   form=job['support'];target=job['targetId'];who=job['casterId']
   if form=='mending-light':
    import character_customization
    field_magic.heal(s,target,3+character_customization.bonus(s,who,'healing'))
   else:
    b=field_magic.initialize(s)['aqueduct']['buffs'].setdefault(target,{})
    buff,n={'borrowed-hour':('haste',3),'giant-grasp':('strength',2),'lucid-sight':('insight',2),'wisp-scout':('scout',2)}[form];b[buff]=n
   p['pending']=None;resume(s);s['lastPhaseSummary'].append(g.SPELL_FORMS[form]['name']+' completed for '+g.character_profile(s,target)['name']+'.');return
  current=step(s);c=current['choices'][job['methodId']]
  record={'stepId':current['id'],'name':current['name'],'methodId':job['methodId'],'method':c['name'],'participants':job['contributors'][:],'actors':job['actors'][:],'casterId':job['casterId'],'supportUsed':job['supportUsed']}
  p['outcomes'].append(record);p['completed'].append(current['id'])
  if c.get('lasting'):p['inscriptions'].append({'stepId':current['id'],'text':c['lasting'],'conductorId':job['casterId']})
  if current['id']=='future':p['ending']=job['methodId']
  p['pending']=None;resume(s);s['lastPhaseSummary'].append(current['name']+' completed: '+c['name']+'.');g.add_journal(s,current['name']+' completed.');return
 rewards=['Returned safely. Completed work, paid unfinished methods and permanent inscriptions are retained.']
 if e['discoveryReady'] and not p['discoveries']:
  p['discoveries'].append('survey');p['returners']=party[:];s['materialInventory']['moon-glass']+=2;s['materialInventory']['binding-thread']+=3
  for w in party:g.award_advancement(s,w,key,3,'Completed '+d['name']);g.learn_for_character(s,w,d['principle'])
  rewards=['2 moon glass and 3 binding thread deposited. Recovered '+d['legacy']+'.',g.PRINCIPLE_NAMES[d['principle']]+' learned by the returning party.',d['endings'][p['ending']][1],'Display the recovered legacy in the '+g.headquarters.ROOMS[d['room']]['name']+' to use its benefit.']
 s['lastExpeditionReport']={'siteId':key,'approach':e['chosenApproach'],'returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
 if e['restoreLanternDisplay']:s['lanternDisplayed']=True
 s['expedition']=None
 for w in party:
  g.set_character_assignment(s,w,'rest');field_magic.progress(s)['buffs'].pop(w,None)
 s['lastPhaseSummary']+=rewards;g.add_journal(s,'Returned from '+d['name']+'. '+' '.join(rewards))

def callbacks(s,party):
 import household_sagas,relationships
 lines=[]
 for a,b in combinations(party,2):
  memories=[m for m in household_sagas.saved(s)['memories'].values() if a in m['participants'] and b in m['participants']]
  if memories:lines.append('A shared memory returns: '+memories[-1]['title']+'. You recall choosing “'+memories[-1]['playerLine']+'”.')
  bond=relationships.saved(s)['bonds'].get(relationships.pair_id(a,b))
  if bond and max(bond[k] for k in relationships.DIMENSIONS)>=3:
   import game as g
   lines.append(g.character_profile(s,a)['name']+' and '+g.character_profile(s,b)['name']+' have enough shared trust, affection or respect to make room for a comfortable pause.')
 return list(dict.fromkeys(lines))[:3]

def scenes(s,key):
 import game as g,romance
 p=saved(s,key);d=SITES[key];field=active(s) and site(s)==key
 home=bool(p['discoveries'] and p['returners'] and all(w in g.household_members(s) and g.character_at_castle(s,w) for w in p['returners']))
 party=g.expedition_party(s) if field else p['returners'][:]
 ready=bool(field and s['expedition']['stage'] not in ('outbound','returning') or home)
 rows=[];index=list(SITES).index(key)
 def add(identity,title,opening,members,available,choices):
  memory=p['memories'].get(identity)
  rows.append({'id':identity,'title':title,'participants':memory['participants'][:] if memory else members[:],'opening':memory['opening'] if memory else opening if available else '', 'available':bool(available and not memory),'memory':deepcopy(memory),'choices':choices if available and not memory else {}})
 voices='\n\n'.join(g.character_profile(s,w)['name']+': “'+content.VOICES[w][index]+'”' for w in party if w in content.VOICES)
 previous=p['memories'].get('arrival');recalled='\n\nEarlier you chose: “'+previous['playerLine']+'”.' if previous else ''
 for identity,title,after,opening in [
  ('arrival','What we came to recover',0,'Before beginning, you consider what this place might mean to the people who used it.'),
  ('camp','An evening that belongs to the party',2,d['campPlace']),
  ('credit','Who will the report remember?',5,'The finds are almost ready to bring home. You consider whose work might otherwise disappear behind a neat account of your success.')]:
  if home:opening='Back at the castle, you talk about a question left for later in the journey. '+('The report can still include how the party rested and what the shelter meant.' if identity=='camp' else opening)
  text=opening+'\n\n'+voices+(recalled if identity!='arrival' else '')
  if identity=='camp':text+='\n\n'+'\n\n'.join(line for a,b,line in content.PAIRS if a in party and b in party)
  text+='\n\n'+'\n\n'.join(callbacks(s,party))
  choices={'listen':{'label':'Make room for everyone’s perspective','response':'You listen without turning the conversation into a vote. The report can preserve more than one reason for caring.'},'credit':{'label':'Name the work that might otherwise go unseen','response':'You agree to record the practical work as carefully as the striking discoveries.'}}
  if identity=='camp':choices={'company':{'label':'Put the report aside and enjoy the company','response':'For a little while, nobody has to produce a useful result. The rest becomes part of the journey.'},'playful':{'label':'Offer a deliberately overdramatic expedition toast','response':'You solemnly salute dry socks, sound hinges and the courage to sit down. '+('The others add increasingly ridiculous honours until the formal speech collapses into laughter.' if len(party)>1 else 'The empty cup receives its honour with admirable dignity.')}}
  add(identity,title,text,party,ready and len(p['completed'])>=after,choices)
 for who in content.CAST:
  title,opening,response=content.CAMPS[who]
  # A returning participant can share their own private scene without summoning the whole party.
  private_home=bool(p['discoveries'] and who in p['returners'] and all(w in g.household_members(s) and g.character_at_castle(s,w) for w in ('founder',who)))
  available=len(p['completed'])>=2 and (ready and field and who in party or private_home)
  setting=d['campPlace'] if field else 'At home, you find a quiet place to talk about the journey.'
  choices={'company':{'label':'Enjoy the quiet company','response':response},'affection':{'label':'Share a moment of established mutual affection','response':romance.quest_reply(s,who,response),'blockers':[] if romance.level(s,who)>=1 else ['First establish mutual attraction together. Quiet company is always available.']}}
  if field and key=='masquerade-manor':opening+=' She holds a half-mask beside her face, then lowers it. “Entirely optional. I rather like knowing who I am talking to.”'
  add('private:'+who,title,setting+'\n\n'+opening,['founder',who],available,choices)
 ending=d['endings'].get(p['ending'],('',''))[1]
 add('home','Something the household can use',d['home']+'\n\n'+ending+'\n\n'+voices,p['returners'],home and p['installed'],{'join':{'label':'Try the recovered object together','response':'The relic becomes a useful part of an ordinary evening. You remember the people who brought it home and the people who cared for it before you.'}})
 return rows

def installed(s,key):
 import headquarters
 return bool(saved(s,key)['discoveries'] and saved(s,key)['installed'] and headquarters.ready(s,SITES[key]['room']))
def bonus(s,skill):return int(any(d['skill']==skill and installed(s,key) for key,d in SITES.items()))
def support(s,obstacle):return next((key for key,d in SITES.items() if obstacle in d['helps'] and installed(s,key)),None)
def context(s,who):return deepcopy([m for key in SITES for m in saved(s,key)['memories'].values() if who in m['participants']])

def views(s):
 import game as g,headquarters,field_magic
 result={}
 for key,d in SITES.items():
  p=saved(s,key);rows=scenes(s,key)
  for r in rows:r['choices']={k:{'label':v['label'],'blockers':v.get('blockers',[])} for k,v in r['choices'].items()}
  result[key]={'name':d['name'],'active':active(s) and site(s)==key,'completed':bool(p['discoveries']),'completedSteps':len(p['completed']),'pendingPhases':p['pending']['remaining'] if p['pending'] else 0,'totalSteps':len(d['steps']),'legacy':d['legacy'],'legacyText':d['legacyText'],'installed':p['installed'],'effective':installed(s,key),'roomId':d['room'],'canPlace':bool(p['discoveries'] and g.character_at_castle(s,'founder') and headquarters.ready(s,d['room'])),'scenes':rows,'outcomes':deepcopy(p['outcomes']),'inscriptions':deepcopy(p['inscriptions']),'ending':d['endings'].get(p['ending'],('',''))[1]}
 party=g.expedition_party(s);spells=[];scout=None
 if active(s):
  for sp in s['spellbook']:
   if sp['ownerId'] not in party or sp['formId'] not in SUPPORT_FORMS or sp['id'] not in s['preparedSpells'][sp['ownerId']] or sp['status']!='learned':continue
   form=g.SPELL_FORMS[sp['formId']]
   reasons=[]
   if s['expedition']['stage']!='encounter-choice' or saved(s,site(s))['pending']:reasons.append('Start support casting at an obstacle with no unfinished method.')
   if not all(p in g.character_principles(s,sp['ownerId']) for p in form['requiredPrinciples']):reasons.append('The caster must know every required principle.')
   if not all(s['materialInventory'][k]>=n for k,n in form['castingInputs'].items()):reasons.append('Carry the listed spell components.')
   spells.append({'id':sp['id'],'ownerId':sp['ownerId'],'name':form['name'],'effect':SUPPORT_FORMS[sp['formId']],'inputs':deepcopy(form['castingInputs']),'blockers':reasons,'targets':[{'id':w,'blockers':['Already at full vitality.'] if sp['formId']=='mending-light' and field_magic.vitality(s,w)>=6 else []} for w in party]})
  if any(field_magic.progress(s)['buffs'].get(w,{}).get('scout',0)>0 for w in party):
   steps=SITES[site(s)]['steps'];current=step(s);idx=steps.index(current) if current else len(steps)
   if idx+1<len(steps):scout={'name':steps[idx+1]['name'],'description':steps[idx+1]['description']}
 return {'sites':result,'party':party if s.get('expedition') else [],'supportSpells':spells,'scout':scout}

def departure(s):
 import game as g,companion_participation,guidance,household_sagas,character_quests
 rows=companion_participation.view(s)['comparison'];jobs=list(guidance.projects(s).values())
 for r in rows:
  who=r['id'];r['assignment']=g.character_assignment(s,who)
  r['commitments']=[{'name':j['name'],'progress':str(j['done'])+'/'+str(j['total'])} for j in jobs if j['personId']==who or who in j.get('participants',[])]
  for key,story in household_sagas.saved(s)['stories'].items():
   p=story['project']
   if p and p['status']!='complete' and who in p['workers'] and not any(x['name']==household_sagas.content.STORIES[key]['projectName'] for x in r['commitments']):r['commitments'].append({'name':household_sagas.content.STORIES[key]['projectName'],'progress':str(p['done'])+'/2'})
  ritual=s.get('lastingRituals',{}).get('project')
  if ritual and who in ritual['participants']:
   import lasting_rituals
   name=lasting_rituals.CATALOGUE[ritual['id']]['name']
   if not any(x['name']==name for x in r['commitments']):r['commitments'].append({'name':name,'progress':str(ritual['done'])+'/'+str(ritual.get('requiredPhases',lasting_rituals.CATALOGUE[ritual['id']]['phases']))})
  quest=character_quests.active(s)
  if quest and who in ('founder',quest.get('who')):r['commitments'].append({'name':'Active character quest','progress':'Retained while away'})
 return rows


def greeting(s,who):
 records=[(key,m) for key in SITES for m in saved(s,key)['memories'].values() if who in m['participants'] and saved(s,key)['discoveries']]
 if not records or who not in content.VOICES:return None
 key,m=records[-1]
 return 'Remembering '+SITES[key]['name']+': “'+content.VOICES[who][list(SITES).index(key)]+'”'

def install(g):
 for form in g.SPELL_FORMS:
  uses=[{'siteId':key,'siteName':d['name'],'obstacle':step['name'],'method':choice['name']} for key,d in SITES.items() for step in d['steps'] for choice in step['choices'].values() if choice.get('castForm')==form]
  if uses:
   g.SPELL_FORMS[form]['journeyUses']=uses
   g.SPELL_FORMS[form]['effect']+=' Additional authored routes: '+'; '.join(u['obstacle']+' ('+u['siteName']+')' for u in uses)+'. Each listed route takes one phase and consumes the spell’s listed components once.'
  if form in SUPPORT_FORMS:g.SPELL_FORMS[form]['effect']+=' On the monastery, skybridge and manor journeys, one explicit support-casting phase can '+SUPPORT_FORMS[form][0].lower()+SUPPORT_FORMS[form][1:]
