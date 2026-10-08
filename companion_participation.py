"""Read-only field advice, honest party comparisons and opt-in remembered practice/return scenes."""
from copy import deepcopy
import character_builds as builds
import character_approaches as apt

VOICES={
 'mira':'“Let me compare this with the notes before we choose.”',
 'tamsin':'“First, check that the person doing this can reach the supplies.”',
 'iona':'“Let us compare the routes. I want to know where each one brings us out.”',
 'aurelia':'“Agree who moves first and who covers the others.”',
 'neris':'“I want to check the surface before choosing how to work on it.”',
 'sabine':'“If we are going to negotiate, decide what we are actually offering.”',
 'maren':'“Show me which part needs to move and which part must stay fixed.”',
 'brakka':'“Before anyone lifts, agree where the load will go.”',
 'fenna':'“Let us check the way back while we can still see it.”',
 'kaede':'“Walk through the steps once before committing to the movement.”',
 'elowen':'“Check whether anyone needs a pause before we start the next part.”',
 'nyssara':'“State the conditions this method needs. Then we can check them.”',
 'sylva':'“Look at what is growing here before we decide what to cut or move.”',
 'velis':'“Compare the supplies each method uses before choosing.”',
 'rhess':'“Agree a signal for stopping as well as starting.”',
}

def voice(who):return VOICES.get(who,'“Check the requirements before choosing this method.”')

def initialize(s):s.setdefault('companionParticipation',{'events':{},'memories':{},'deferred':[]})
def saved(s):return s.get('companionParticipation',{'events':{},'memories':{},'deferred':[]})

def trained(s,who,project):
 if project['kind'] not in ('attribute','skill'):return
 if who=='founder' and not project.get('teacherId'):return
 import game as g
 target=project['targetId'];kind=project['kind'];rank=builds.build(s,who)['attributes'][target] if kind=='attribute' else g.skill_rank(s,who,target)
 title=(builds.ATTRIBUTES if kind=='attribute' else g.CHARACTER_SKILLS)[target]['name']
 learner=who
 if who=='founder':who=project['teacherId']
 key=f'practice:{who}:{learner}:{kind}:{target}:{rank}'
 initialize(s);saved(s)['events'].setdefault(key,{'id':key,'who':who,'title':'A new way to practise '+title,'kind':'practice','learnerId':learner,'subject':title,'rank':rank,'teacherId':project.get('teacherId'),'day':s['dayNumber']})

def returned(s,party,outcomes,complete,site_id=None):
 import game as g
 site_id=site_id or (s.get('expedition') or {}).get('siteId','stormwatch-beacon')
 site_name='the field patrol' if site_id=='field-patrol' else g.EXPEDITION_SITES.get(site_id,{'name':site_id})['name']
 initialize(s)
 for who in party:
  if who=='founder':continue
  mine=[deepcopy(o) for o in outcomes if who in o.get('participants',[])]
  key=('beacon' if site_id=='stormwatch-beacon' else 'journey:'+site_id)+':'+who+(':complete' if complete else ':return')
  saved(s)['events'].setdefault(key,{'id':key,'who':who,'title':('After the beacon' if site_id=='stormwatch-beacon' else 'After '+site_name) if complete else 'The choice to turn home · '+site_name,'siteId':site_id,'siteName':site_name,'kind':'journey','complete':bool(complete),'outcomes':mine,'day':s['dayNumber']})

PRACTICE={
 'Might':('“Before lifting, set your feet and bring the load close. Reaching for it with straight arms makes the same weight much harder to control.”','“Try to describe where your feet, hands and load should be before anything leaves the ground.”'),
 'Dexterity':('“I slowed the movement until I could place my fingers correctly every time. Speed was hiding the point where I lost control.”','“Describe one movement in order: where the hand starts, what it touches and when the grip changes.”'),
 'Vitality':('“I stopped treating the first sign of fatigue as something to conceal. Keeping a pace I could sustain made the later attempts steadier.”','“Describe how you would pace the work and when you would call for a pause.”'),
 'Intelligence':('“I wrote the assumptions beside the answer. That showed me which conclusion depended on something I had never checked.”','“Choose a claim in the notes. Say what supports it and what observation would make you revise it.”'),
 'Resolve':('“When I lost my place, I returned to the last step I could account for. Starting the whole task again was making each interruption worse.”','“Name the last completed step before you describe the next one. That gives you a place to return after an interruption.”'),
 'Charisma':('“I stated the request before explaining why I deserved an answer. The other person could finally tell what I was asking them to decide.”','“Make a request in one sentence. Then say why the other person might accept or refuse it.”'),
 'Athletics':('“I placed my weight over the next foothold before reaching farther. Pulling harder did not fix a poor stance.”','“Describe where your weight goes before you move a hand or foot.”'),
 'Diplomacy':('“I asked what the other person needed before repeating my offer. We had been arguing about the price when their difficulty was the delivery date.”','“Start with the disputed term. Ask one question that would tell you why it matters to the other person.”'),
 'Channeling':('“I practised stopping the flow cleanly. Holding it longer was no improvement if I could not end it when I chose.”','“Explain how you begin the flow, keep it steady and stop it. The last part belongs in the lesson too.”'),
 'Scholarship':('“I checked whether two references were independent. They looked like agreement until I noticed both were copying the same earlier error.”','“Put the original observation before the later commentary. Say which part you would still need to verify.”'),
 'Artifice':('“I changed one fitting at a time. Replacing three parts together gave me a working device without telling me which part had failed.”','“Point to the part you would test first, and explain what each possible result would tell you.”'),
 'Fieldcraft':('“I practised recording a landmark from both directions. A path that looks obvious on the way out can be hard to recognise coming back.”','“Describe the return route from the far side of the landmark. Do not rely on ‘left’ without saying which way you are facing.”'),
}

def dialogue(s,e):
 import game as g
 from conversation_voice import voice as character_voice
 who=e['who'];name=g.character_profile(s,who)['name'];v=character_voice(who)
 if e['kind']=='patrol-moment':
  import patrol_homecoming
  return patrol_homecoming.dialogue(s,e)
 if e['kind']=='practice':
  subject=e['subject'];lesson,exercise=PRACTICE.get(subject,('“Let us put the completed exercise beside the instructions and check each step.”','“Explain the first step, the result you expect and what you would check if it differs.”'))
  opening=name+' has completed '+subject+' '+str(e['rank'])+'. '+v['review']
  if e.get('learnerId')=='founder':opening=name+' has finished teaching you '+subject+' '+str(e['rank'])+'. '+v['review']
  elif e.get('teacherId'):opening+=' The lesson was with '+g.character_profile(s,e['teacherId'])['name']+'.'
  return opening,{
   'notice':{'label':'Ask which part of '+subject+' needed attention.','response':lesson+' '+v['credit']},
   'practice':{'label':'Talk through one '+subject+' exercise.','response':exercise+' You compare the explanation with the completed lesson notes.'},
   'celebrate':{'label':'Thank her for the work and share a drink.','response':v['company']}}
 destination=e.get('siteName','Stormwatch');outcomes=e.get('outcomes',[])
 detail=(' The recorded choice at '+outcomes[-1]['name'].lower()+' was '+outcomes[-1]['method']+'.') if outcomes else (' The party completed the journey; this record lists no individual method for '+name+'.' if e.get('complete') else ' The party returned before completing the journey.')
 opening=name+(' brings you the return report from '+destination+'. You stayed at the castle during the outing.' if e.get('reported') else ' opens the account of your return from '+destination+'.')+detail+' '+v['review']
 teams=[o for o in outcomes if o.get('team')];magic=[o for o in outcomes if o.get('magic')]
 contribution=('At '+teams[0]['name'].lower()+', the team used '+teams[0]['method']+'. Holding the other part of the work was a separate task, and you keep both participants in the record.' if teams else 'You keep the recorded method and its participants together.' if outcomes else 'You record the return without adding an individual accomplishment that the report does not contain.')
 preparation=('You mark '+magic[0]['method']+' for a component check before another departure. ' if magic else '')
 return opening,{
  'thanks':{'label':'Thank her and record her part in the journey.','response':contribution+' '+v['credit']},
  'learn':{'label':'Ask what she would check before the next outing.','response':preparation+v['proposal']},
  'company':{'label':'Close the report and share a drink.','response':v['company']}}

def event_row(s,key):
 import game as g
 e=saved(s)['events'][key];who=e['who'];memory=saved(s)['memories'].get(key)
 present=who in g.household_members(s) and all(g.character_at_castle(s,p) for p in ('founder',who))
 opening,choices=dialogue(s,e)
 return {**deepcopy(e),'opening':opening if present or memory else '', 'choices':{k:{'label':v['label'],'effect':{'notice':'Respect','practice':'Trust','celebrate':'Affection','thanks':'Respect','learn':'Trust','company':'Affection'}.get(k,'Trust')+' +1 between you and '+g.character_profile(s,who)['name']+' (maximum 12), once for this conversation.'} for k,v in choices.items()} if present and not memory else {},'memory':deepcopy(memory),'blockers':[] if present else ['Return home together to share this invitation.'],'deferred':key in saved(s)['deferred']}

def context(s,who):return [deepcopy(m) for m in saved(s)['memories'].values() if m['who']==who][-12:]

def suggestions_for(s,who):
 import game as g, field_magic as f, beacon_expedition as beacon
 e=s.get('expedition')
 if not who or not e or e['stage']!='encounter-choice':return []
 rows=[]
 if e['siteId']==f.SITE:
  for option in apt.field_options(s,who):
   if not f.reasons(s,who,method=option['id']):rows.append({'who':who,'line':voice(who),'name':option['name'],'detail':option['check']['detail']+' · one phase','action':{'type':'field-method','characterId':who,'method':option['id']}})
 elif beacon.is_active(s):
  for key,c in beacon.step(s)['choices'].items():
   if key=='patient' or beacon.blockers(s,c):continue
   if c.get('aptitude') and not apt.score(s,who,c['aptitude'],g.expedition_party(s))['qualified']:continue
   if c.get('castForm'):
    caster=beacon.caster_for(s,c)
    if not caster or caster['ownerId']!=who:continue
   rows.append({'who':who,'line':voice(who),'name':c['name'],'detail':beacon.description(c),'action':{'type':'choose-encounter-method','methodId':key}})
 return rows[:2]

def suggestions(s):
 import game as g
 return [row for who in g.expedition_party(s)[1:] for row in suggestions_for(s,who)]

def view(s):
 import game as g, solo_life
 members=g.household_members(s)
 comparison=[]
 for who in members:
  b=builds.build(s,who);spells=[p for p in s['spellbook'] if p['ownerId']==who and p['id'] in s['preparedSpells'][who] and p['status']=='learned']
  comparison.append({'id':who,'name':g.character_profile(s,who)['name'],'attributes':deepcopy(b['attributes']),'skills':{k:g.skill_rank(s,who,k) for k in g.CHARACTER_SKILLS},'spells':[g.SPELL_FORMS[p['formId']]['name'] for p in spells],'roles':[label for label,attribute,skill in [('brace a load','might','athletics'),('cross on a safety line','dexterity','athletics'),('work a mechanism','dexterity','artifice'),('maintain a steady spell','resolve','channeling'),('explain the technical fault','intelligence','scholarship'),('negotiate the repair','charisma','diplomacy'),('hold the service arm','vitality','athletics')] if apt.score(s,who,apt.spec(attribute,skill,8))['qualified']],'blockers':solo_life.companion_blockers(s,who) if who!='founder' else []})
 return {'comparison':comparison,'suggestions':suggestions(s),'events':[event_row(s,k) for k,e in saved(s)['events'].items() if e['who'] in members]}

def apply(s,action):
 if action.get('type') not in ('share-participation','defer-participation','restore-participation'):return False
 import game as g
 key=action.get('eventId');g.require(isinstance(key,str) and key in saved(s)['events'],'Choose an actual training or journey invitation.')
 e=saved(s)['events'][key];g.require(e['who'] in g.household_members(s),'This person must be a current resident.')
 g.require(key not in saved(s)['memories'],'This exchange is already remembered.')
 row=event_row(s,key);g.require(not row['blockers'],' '.join(row['blockers']))
 if action['type']=='defer-participation':
  g.require(key not in saved(s)['deferred'],'This invitation is already set aside.');saved(s)['deferred'].append(key);return True
 if action['type']=='restore-participation':
  g.require(key in saved(s)['deferred'],'This invitation is not set aside.');saved(s)['deferred'].remove(key);return True
 opening,choices=dialogue(s,e);choice=action.get('choice');g.require(isinstance(choice,str) and choice in choices,'Choose an offered reply.')
 record={'id':key,'who':e['who'],'participants':['founder',e['who']],'title':e['title'],'opening':opening,'choice':choice,'playerLine':choices[choice]['label'],'response':choices[choice]['response'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
 saved(s)['memories'][key]=record
 import relationships
 relationships.remember(s,'participation:'+key,record)
 if key in saved(s)['deferred']:saved(s)['deferred'].remove(key)
 g.add_journal(s,e['title']+': '+record['playerLine']+' '+record['response']);return True
