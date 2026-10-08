"""Persistent personal expression, atomic preparations and earned specializations."""
from copy import deepcopy
import customization_content as c

EMPTY={'people':{},'memories':{}}
def initialize(s):s.setdefault('customization',deepcopy(EMPTY))
def saved(s):return s.get('customization',EMPTY)
def person(s,who):return saved(s)['people'].get(who,{})
def write_person(s,who):
 initialize(s);return s['customization']['people'].setdefault(who,{})
def home(s,who):
 import game as g
 return [] if all(g.character_at_castle(s,p) for p in ('founder',who)) else ['Return home together before making this change.']
def clean(value,limit=120):
 import game as g
 g.require(isinstance(value,str) and len(value)<=limit and not any(ord(x)<32 and x not in '\n\t' for x in value),'Use plain text within the displayed length limit.')
 return value.strip()
def profile(s,who):
 p=c.PROFILES.get(who)
 if p:return dict(zip(('colour','hobby','refreshment','room','keepsake','voice','flirt'),p))
 return {'colour':'charcoal','hobby':'quiet conversation','refreshment':'tea','room':'common-room','keepsake':'a personal note','voice':'“Give me a little time to make this place my own.”','flirt':'“I was hoping you might stay for a while.”'}
def preferences(s,who):
 base=profile(s,who)
 return {**base,**person(s,who).get('preferences',{})}
def style(s,who):
 p=person(s,who);return p.get('styles',{}).get(p.get('selectedStyle'))
def style_blockers(s,who,d):
 import romance
 reasons=home(s,who)
 if who!='founder' and d['occasion']=='private' and romance.level(s,who)<3:reasons.append('Share an established partnership before proposing a private-evening ensemble.')
 return reasons

def snapshot(s,who):
 focus=s['signatureFocuses'][who]
 import personal_paths,armoury
 return {'paths':{k:personal_paths.record(s,who)[k][:] for k in ('techniques','passives')},'gear':{'loadouts':deepcopy(armoury.state(s)['loadouts'].get(who,{})),'mode':armoury.state(s)['mode'].get(who,'household')},'spells':s['preparedSpells'][who][:], 'practices':s['characterDevelopment'][who]['preparedPractices'][:],
  'tool':s.get('preparedEquipment',{}).get(who),'household':focus['householdLoadout'][:],'expedition':focus['expeditionLoadout'][:],
  'publicSpells':s['publicWorkshop']['preparedSpells'].get(who,[])[:], 'publicItem':s['publicWorkshop']['preparedItems'].get(who),'publicInscription':s['publicWorkshop']['items'].get(s['publicWorkshop']['preparedItems'].get(who),{}).get('preparedInscription')}

def restore_preparation(s,who,d):
 import game as g
 g.require(not home(s,who),' '.join(home(s,who)))
 # Temporarily clear shared slots on the private candidate, then revalidate both collections.
 g.apply_action(s,{'type':'public-prepare-spells','ownerId':who,'recordIds':[]})
 g.apply_action(s,{'type':'prepare-spells','characterId':who,'spellIds':d['spells']})
 g.apply_action(s,{'type':'public-prepare-spells','ownerId':who,'recordIds':d['publicSpells']})
 current=s['publicWorkshop']['preparedItems'].get(who)
 if current:g.apply_action(s,{'type':'public-stow','ownerId':who,'itemId':current})
 for key in list(s['characterDevelopment'][who]['preparedPractices']):
  g.apply_action(s,{'type':'prepare-practice','characterId':who,'practiceId':key,'prepared':False})
 for key in d['practices']:g.apply_action(s,{'type':'prepare-practice','characterId':who,'practiceId':key,'prepared':True})
 for context in ('household','expedition'):g.apply_action(s,{'type':'configure-focus','characterId':who,'context':context,'inscriptions':d[context]})
 if d['publicItem']:g.apply_action(s,{'type':'public-prepare-item','ownerId':who,'itemId':d['publicItem'],'inscriptionId':d['publicInscription']})
 if d['tool']:g.apply_action(s,{'type':'prepare-working-tool','ownerId':who,'itemId':d['tool']})
 else:g.apply_action(s,{'type':'stow-working-tool','ownerId':who})
 # Older sets have no paths/gear fields and keep those newer preparations intact.
 import personal_paths,armoury
 if 'paths' in d and who in personal_paths.PEOPLE:
  g.apply_action(s,{'type':'path-clear','characterId':who})
  for kind in ('techniques','passives'):
   for talent in d['paths'][kind]:g.apply_action(s,{'type':'path-prepare','characterId':who,'talentId':talent,'prepared':True})
 if 'gear' in d:
  for mode,loadout in d['gear']['loadouts'].items():g.apply_action(s,{'type':'gear-save-loadout','ownerId':who,'mode':mode,'loadout':loadout})
  g.apply_action(s,{'type':'gear-apply-loadout','ownerId':who,'mode':d['gear']['mode']})


def preparation_blockers(s,who,d):
 import game as g
 try:restore_preparation(deepcopy(s),who,d)
 except g.RuleError as e:return [str(e)]
 return []

def specialization_blockers(s,who,key):
 import game as g,character_builds as b
 d=c.SPECIALIZATIONS[key];reasons=[]
 if b.build(s,who)['attributes'][d['attribute']]<6:reasons.append('Develop '+b.ATTRIBUTES[d['attribute']]['name']+' to 6.')
 if g.skill_rank(s,who,d['skill'])<2:reasons.append('Develop '+g.CHARACTER_SKILLS[d['skill']]['name']+' to rank 2.')
 return reasons

def bonus(s,who,skill):
 key=person(s,who).get('specialization')
 return int(key != 'healer' and key in c.SPECIALIZATIONS and c.SPECIALIZATIONS[key]['skill']==skill and not specialization_blockers(s,who,key))

def scene_blockers(s,who,key):
 import romance,game as g,headquarters as h
 reasons=home(s,who);p=person(s,who)
 if key!='tastes' and not p.get('preferencesKnown'):reasons.append('Ask about personal tastes first.')
 if key in ('leisure','private'):
  room=p.get('leisureRoom',preferences(s,who)['room'])
  if not h.ready(s,room):reasons.append('Restore the chosen leisure room first.')
 if key=='style' and not style(s,who):
  import outfit_progression
  if not outfit_progression.current(s,who):reasons.append('Choose a personal ensemble or an unlocked illustrated outfit first.')
 if key=='space' and not p.get('space',{}).get('installed'):reasons.append('Fit this person’s corner first.')
 if key in ('style','private') and romance.level(s,who)<c.SCENES[key][1]:reasons.append('Share '+('mutual attraction' if key=='style' else 'an established partnership')+' first. Friendship activities remain available.')
 return reasons

def scene_text(s,who,key,choice):
 import game as g,romance
 p=preferences(s,who);name=g.character_profile(s,who)['name'];look=style(s,who)
 import outfit_progression
 look=look or outfit_progression.current(s,who) or {'name':'familiar everyday clothes'}
 opening={
 'tastes':name+' considers the question. '+p['voice'],
 'leisure':name+' has made room for '+p['hobby']+' and '+p['refreshment']+'. “No jobs attached. Stay a while?”',
 'style':name+' turns from the mirror, wearing '+look['name']+'. '+p['flirt'],
 'space':name+' arranges the new corner and leaves a place for '+p['keepsake']+'. '+p['voice'],
 'private':name+' meets you in the quiet of the evening. '+p['flirt'],
 }[key]
 if choice=='warm':response={'tastes':'You listen, remembering the small things as carefully as the large ambitions.','leisure':'The activity wanders into conversation. Neither of you turns the time into another task.','style':'You offer a thoughtful compliment. The smile that follows is pleased and unhurried.','space':'You let your companion decide where the last object belongs, then sit together to enjoy the result.','private':'You settle close and talk softly. The evening remains affectionate without going further.'}[key]
 else:
  response={'tastes':'You promise to remember the preference, especially when planning your next pleasant distraction.','leisure':'A teasing challenge becomes shared laughter; your companion shifts closer, pleased by the attention.','style':'You admit that the outfit has made concentration difficult. Your companion laughs, takes your hand and rewards the honest compliment with a kiss.','space':'Your companion pats the place beside them. The new corner clearly has room for a little flirting.','private':'Your partner draws you into a slow kiss, then rests against you with a satisfied smile. Conversation dwindles into the comfortable privacy of an evening kept for each other.'}[key]
 return opening,response

def remember(s,who,key,choice):
 import game as g,relationships
 opening,response=scene_text(s,who,key,choice)
 record={'id':who+':'+key,'title':c.SCENES[key][0],'opening':opening,'response':response,'choice':choice,'participants':['founder',who],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'style':deepcopy(style(s,who))}
 s['customization']['memories'][record['id']]=record
 relationships.remember(s,'customization:'+record['id'],record,'affection' if choice=='playful' else 'trust')
 g.add_journal(s,record['title']+': '+response)

def context(s,who):
 return {'appearance':deepcopy(person(s,who).get('appearance',{})),'style':deepcopy(style(s,who)),'personalSpace':deepcopy(person(s,who).get('space',{})),
  'preferences':deepcopy(preferences(s,who)) if person(s,who).get('preferencesKnown') or who=='founder' else {},
  'memories':deepcopy([m for m in saved(s)['memories'].values() if who in m['participants']])}

def idle_room(s,who):
 import headquarters as h
 p=person(s,who);room=p.get('leisureRoom')
 return room if s['currentDayPhase']=='afternoon' and room and h.ready(s,room) else None

def clear_style(s,who):
 if who in saved(s)['people']:saved(s)['people'][who].pop('selectedStyle',None)

def view(s):
 import game as g,headquarters as h,romance,outfit_progression
 rows={};looks=outfit_progression.view(s)
 for who in g.household_members(s):
  p=person(s,who);known=who=='founder' or p.get('preferencesKnown',False)
  rooms=[{'id':key,'name':d['name']} for key,d in h.ROOMS.items() if h.ready(s,key)]
  own=s.get('bedroomAssignments',{}).get(who)
  if own and g.room_available(s,own) and own not in [x['id'] for x in rooms]:rooms.append({'id':own,'name':g.ROOMS.get(own,{}).get('name','Own bedroom')})
  scenes=[]
  if who!='founder':
   for key,(title,_) in c.SCENES.items():
    memory=saved(s)['memories'].get(who+':'+key);reasons=scene_blockers(s,who,key)
    scenes.append({'id':key,'title':title,'blockers':reasons,'memory':deepcopy(memory),'opening':scene_text(s,who,key,'warm')[0] if not reasons or memory else '', 'playfulBlockers':[] if romance.level(s,who)>=(2 if key=='style' else 1) else ['Share '+('a first date' if key=='style' else 'mutual attraction')+' before choosing a romantic response.']})
  specs=[{'id':key,**d,'blockers':home(s,who)+specialization_blockers(s,who,key)} for key,d in c.SPECIALIZATIONS.items()]
  preparations=[]
  for name,d in p.get('preparations',{}).items():
   preparations.append({'name':name,'contents':deepcopy(d),'blockers':preparation_blockers(s,who,d)})
  styles=[{'id':key,**d,'blockers':style_blockers(s,who,d)} for key,d in p.get('styles',{}).items()]
  rows[who]={'id':who,'name':g.character_profile(s,who)['name'],'homeBlockers':home(s,who),'appearance':deepcopy(p.get('appearance',{})),'portraitBrief':portrait_brief(s,who),
   'preferences':preferences(s,who) if known else None,'styles':styles,'selectedStyle':p.get('selectedStyle'),'preparations':preparations,
   'specializations':specs,'specialization':p.get('specialization'),'space':deepcopy(p.get('space',{})), 'cornersOwned':p.get('cornersOwned',[])[:],
   'mementos':mementos(s,who),'rooms':rooms,'leisureRoom':p.get('leisureRoom'),'scenes':scenes,'lessons':g.lesson_offers(s,who),
   'illustratedLooks':deepcopy(looks.get(who,{}).get('looks',[])),
   'refreshmentMemory':deepcopy(saved(s)['memories'].get(who+':refreshment')),'mentorships':mentor_rows(s,who),'history':deepcopy([m for m in saved(s)['memories'].values() if who in m['participants']])}
 return {'people':rows,'garments':c.GARMENTS,'colours':c.COLOURS,'hairStyles':c.HAIR,'occasions':c.OCCASIONS,'spaces':c.SPACES}

ACTIONS={'offer-personal-refreshment','share-mentor-reflection','save-personal-appearance','save-personal-style','wear-personal-style','delete-personal-style','clear-personal-style','save-complete-preparation','load-complete-preparation','delete-complete-preparation','choose-specialization','share-personal-scene','save-personal-preferences','choose-leisure-room','fit-personal-corner','put-away-personal-corner'}
def apply(s,a):
 if a.get('type') not in ACTIONS:return False
 # All validation, including preparation side effects, completes on a private candidate.
 candidate=deepcopy(s);_apply(candidate,a);s.clear();s.update(candidate);return True

def _apply(s,a):
 import game as g,headquarters as h,romance
 who=a.get('characterId');kind=a['type']
 g.require(isinstance(who,str) and who in g.household_members(s),'Choose a current household member.')
 g.require(not home(s,who),' '.join(home(s,who)))
 p=write_person(s,who)
 if kind=='offer-personal-refreshment':
  g.require(who!='founder' and p.get('preferencesKnown'),'Discover this companion’s tastes first.')
  key=who+':refreshment';g.require(key not in saved(s)['memories'],'This thoughtful gift is already remembered.')
  g.require(s['sharedFunds']>=2,'Needs 2 crowns for the chosen refreshment.')
  pref=preferences(s,who);s['sharedFunds']-=2
  record={'id':key,'title':'You remembered the little things','opening':'You bring '+pref['refreshment']+' and ask whether this is a good moment for company.','response':g.character_profile(s,who)['name']+' makes room for you. “You remembered.” '+pref['voice'],'participants':['founder',who],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  saved(s)['memories'][key]=record
  import relationships
  relationships.remember(s,'customization:'+key,record,'trust')
 elif kind=='share-mentor-reflection':
  key=a.get('lessonId');row=next((r for r in mentor_rows(s,who) if r['id']==key),None)
  g.require(row is not None,'Complete a real lesson before reflecting on it.')
  g.require(not row['memory'],'This lesson reflection is already remembered.')
  g.require(not row['blockers'],' '.join(row['blockers']))
  import relationships
  record={k:deepcopy(row[k]) for k in ('id','title','opening','response','participants')}
  record.update(dayNumber=s['dayNumber'],phase=s['currentDayPhase'])
  saved(s)['memories'][key]=record
  relationships.remember(s,'customization:'+key,record,'respect')
 elif kind=='save-personal-appearance':
  fields=a.get('appearance');g.require(isinstance(fields,dict) and not set(fields)-{'hairStyle','hairColour','eyes','complexion','build','markings','accessories'},'Choose supported appearance fields.')
  fields={k:clean(v,160) for k,v in fields.items()}
  g.require(fields.get('hairStyle','Keep established hair') in c.HAIR,'Choose an offered hair style.')
  p['appearance']=fields
 elif kind=='save-personal-style':
  name=clean(a.get('name'),40);g.require(name,'Give the ensemble a name.')
  occasion=a.get('occasion');colour=a.get('colour');ids=a.get('garments')
  g.require(isinstance(occasion,str) and occasion in c.OCCASIONS and isinstance(colour,str) and colour in c.COLOURS,'Choose an occasion and colour.')
  g.require(isinstance(ids,list) and 1<=len(ids)<=8 and all(isinstance(k,str) and k in c.GARMENTS for k in ids) and len(ids)==len(set(ids)),'Choose one to eight distinct offered garments.')
  slots=[c.GARMENTS[k][0] for k in ids]
  g.require(slots.count('base')==1 and all(slots.count(k)<=1 for k in ('lower','feet','outer')),'Choose one base garment and at most one lower garment, footwear and outer layer.')
  g.require(not ('evening-dress' in ids or 'silk-slip' in ids) or 'lower' not in slots,'A full dress or slip replaces the lower garment.')
  g.require('evening-dress' in ids or 'silk-slip' in ids or 'lower' in slots,'Add a lower garment to the shirt or blouse.')
  g.require(not any(c.GARMENTS[k][2]=='private' for k in ids) or occasion=='private','Use the private-evening occasion for private garments.')
  styles=p.setdefault('styles',{});g.require(name in styles or len(styles)<12,'Keep at most twelve personal ensembles.')
  styles[name]={'name':name,'occasion':occasion,'colour':colour,'garments':ids[:],'notes':clean(a.get('notes',''),240),'portraitUnchanged':True}
 elif kind in ('wear-personal-style','delete-personal-style'):
  key=a.get('styleId');g.require(isinstance(key,str) and key in p.get('styles',{}),'Choose a saved ensemble.')
  if kind=='wear-personal-style':
   reasons=style_blockers(s,who,p['styles'][key]);g.require(not reasons,' '.join(reasons));p['selectedStyle']=key
   import outfit_progression
   outfit_progression.clear_selection(s,who)
   s.get('residentCurrentStyles',{}).pop(who,None)
  else:
   g.require(key!=p.get('selectedStyle'),'Restore the illustrated look before deleting this ensemble.');del p['styles'][key]
 elif kind=='clear-personal-style':p.pop('selectedStyle',None)
 elif kind.endswith('complete-preparation'):
  name=clean(a.get('name'),40);g.require(name,'Name this preparation.');sets=p.setdefault('preparations',{})
  if kind.startswith('save'):
   g.require(name in sets or len(sets)<8,'Keep at most eight complete preparations.');sets[name]=deepcopy(snapshot(s,who))
  else:
   g.require(name in sets,'Choose a saved preparation.')
   if kind.startswith('load'):restore_preparation(s,who,sets[name])
   else:del sets[name]
 elif kind=='choose-specialization':
  key=a.get('specialization');g.require(key is None or isinstance(key,str) and key in c.SPECIALIZATIONS,'Choose an offered specialization.')
  reasons=specialization_blockers(s,who,key) if key else [];g.require(not reasons,' '.join(reasons));p['specialization']=key
 elif kind=='share-personal-scene':
  key=a.get('sceneId');choice=a.get('choice');g.require(who!='founder' and isinstance(key,str) and key in c.SCENES,'Choose a companion invitation.')
  g.require(who+':'+key not in saved(s)['memories'],'This invitation is already remembered.')
  g.require(choice in ('warm','playful') if isinstance(choice,str) else False,'Choose a warm or playful response.')
  reasons=scene_blockers(s,who,key);g.require(not reasons,' '.join(reasons))
  if choice=='playful':g.require(romance.level(s,who)>=(2 if key=='style' else 1),'Share the required mutual romantic milestone first.')
  if key=='tastes':p['preferencesKnown']=True
  remember(s,who,key,choice)
 elif kind=='save-personal-preferences':
  g.require(who=='founder','Companions reveal their own tastes through conversation.')
  fields=a.get('preferences');g.require(isinstance(fields,dict) and set(fields)<= {'colour','hobby','refreshment','keepsake'},'Choose supported preferences.')
  p['preferences']={k:clean(v,80) for k,v in fields.items()}
 elif kind=='choose-leisure-room':
  room=a.get('roomId');g.require(room is None or isinstance(room,str) and room in h.ROOMS and h.ready(s,room),'Choose a restored communal room.')
  g.require(who=='founder' or p.get('preferencesKnown'),'Discuss personal tastes first.')
  p['leisureRoom']=room
 elif kind=='fit-personal-corner':
  key=a.get('cornerId');room=a.get('roomId');g.require(isinstance(key,str) and key in c.SPACES,'Choose a personal corner.')
  d=c.SPACES[key];own=s.get('bedroomAssignments',{}).get(who)
  g.require(isinstance(room,str) and (room==own and g.room_available(s,room) or room==d['room'] and h.ready(s,room)),'Use the matching restored communal room or this person’s assigned bedroom.')
  title=clean(a.get('name',d['name']),60);g.require(title,'Name the corner.')
  token=a.get('mementoId')
  memento=next((m for m in mementos(s,who) if m['id']==token),None) if token else None
  g.require(not token or memento is not None,'Choose a keepsake from this person’s actual completed history.')
  owned=p.setdefault('cornersOwned',[])
  if key not in owned:
   g.require(s['sharedFunds']>=d['cost'],'Needs 4 shared crowns.')
   material=d['material'];g.require(s['materialInventory'].get(material,0)-s['materialReserveTargets'].get(material,0)>=1,'Needs 1 unreserved '+g.MATERIALS[material]['name']+'.')
   s['sharedFunds']-=d['cost'];s['materialInventory'][material]-=1;owned.append(key)
  p['space']={'kind':key,'name':title,'roomId':room,'installed':True,'detail':d['detail'],'memento':deepcopy(memento)}
 elif kind=='put-away-personal-corner':
  g.require(p.get('space',{}).get('installed'),'There is no installed corner to put away.');p['space']['installed']=False
 g.add_journal(s,g.character_profile(s,who)['name']+': '+kind.replace('-',' ')+'.')


def portrait_brief(s,who):
 import game as g
 p=g.character_profile(s,who)
 parts=['Portrait of '+p['name']+'. Preserve the established adult identity and ancestry: '+p.get('ancestryLabel','')+'.']
 parts += [k+': '+v for k,v in person(s,who).get('appearance',{}).items() if v]
 d=style(s,who)
 if d:parts.append('Ensemble: '+d['name']+'; '+d['colour']+'; '+', '.join(c.GARMENTS[k][1] for k in d['garments'])+'. '+d['notes'])
 parts.append('Footwear must be flat: no high heels, wedges or platforms. Preserve distinct adult proportions and ancestry features.')
 if who!='founder':parts.append('Youthful clearly adult facial appearance, with fresh skin and soft natural facial contours; never childlike.')
 parts.append('Antique engraving-inspired fantasy illustration, etched linework, muted natural colours, dim but readable. No text or interface. Keep clothing opaque and anatomy natural.')
 return ' '.join(parts)


def mentor_rows(s,who):
 import game as g
 rows={}
 for lesson in s.get('lessonHistory',[]):
  if lesson['learnerId']!=who:continue
  teacher=lesson['teacherId'];key='mentor:'+teacher+':'+who+':'+lesson['kind']+':'+lesson['targetId']
  if teacher not in g.household_members(s):continue
  subject=g.PRINCIPLE_NAMES.get(lesson['targetId'],g.CHARACTER_SKILLS.get(lesson['targetId'],{}).get('name',lesson['targetId']))
  opening=g.character_profile(s,teacher)['name']+' revisits the lesson in '+subject+'. '+profile(s,teacher)['voice']
  response=g.character_profile(s,who)['name']+' describes the part that finally made sense. The two compare methods and keep both perspectives in their notes.'
  rows[key]={'id':key,'title':'What the lesson left us','participants':[teacher,who],'opening':opening,'response':response,'blockers':home(s,teacher)+home(s,who),'memory':deepcopy(saved(s)['memories'].get(key))}
 return list(rows.values())


def mementos(s,who):
 result=[]
 for q in s.get('characterQuests',{}).get('records',{}).values():
  if q.get('who')==who and q.get('status')=='complete':result.append({'id':'quest:'+q['id'],'name':q['title'],'source':'Completed quest'})
 for site,r in s.get('partyJourneys',{}).items():
  if r['discoveries'] and who in r['returners']:
   import party_journeys
   result.append({'id':'journey:'+site,'name':party_journeys.SITES[site]['legacy'],'source':'Actually returned from '+party_journeys.SITES[site]['name']})
 lantern=s.get('lanternAdventure',{})
 if lantern.get('discoveries') and who in lantern.get('returners',[]):result.append({'id':'lantern','name':'A note from the forgotten lantern pavilion','source':'Actually returned from the pavilion'})
 for key,m in saved(s)['memories'].items():
  if who in m['participants']:result.append({'id':'memory:'+key,'name':m['title'],'source':'A shared memory, day '+str(m['dayNumber'])})
 for key,m in s.get('householdSagas',{}).get('memories',{}).items():
  if who in m['participants']:result.append({'id':'saga:'+key,'name':m['title'],'source':'Shared ensemble story, day '+str(m['dayNumber'])})
 return result[-30:]
