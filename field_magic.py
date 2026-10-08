"""Authored elemental magic and the Cinder aqueduct expedition. No semantic runtime."""
from copy import deepcopy
import character_approaches as approaches
SITE='cinder-aqueduct'
SPELLS=[
 ('water-jet','Water jet',['Water','Pressure'],['water-guidance'],'water',{'porous-clay':1},'Extinguish the aqueduct fire in one phase; strike an ember creature for 4 damage, or another living foe for 2.'),
 ('wind-step','Windstep',['Air','Impulse'],['field-calibration'],'leap',{'binding-thread':1},'Carry the party across the aqueduct’s short broken span in one phase. Does not cross the high tower.'),
 ('borne-flight','Borne flight',['Air','Sustained lift'],['field-calibration','courteous-passage'],'flight',{'sun-amber':1,'binding-thread':1},'Lift the expedition party across a gap or to the high tower landing in one phase. No travel teleportation or unrestricted movement.'),
 ('fire-lance','Fire lance',['Heat','Direction'],['steady-hearth-wards'],'fire',{'sun-amber':1},'Deal 4 damage to a living enemy, 3 to undead or 1 to a construct. Ember creatures are immune. No fire is created in arbitrary rooms.'),
 ('ice-bind','Icebind',['Water','Stillness'],['water-guidance','gentle-preservation'],'ice',{'porous-clay':1,'silver-ivy':1},'Deal 2 damage (4 to ember creatures) and prevent that exchange’s retaliation. Can freeze a safe crossing over the broken span for one phase.'),
 ('arc-bolt','Arc bolt',['Charge','Conduction'],['steady-hearth-wards','field-calibration'],'lightning',{'fireglass':1},'Deal 4 damage, or 6 to a conductive construct, in one exchange. Does not power unknown machines.'),
 ('dawn-lance','Dawn lance',['Light','Unbinding'],['luminous-copying','reference-binding'],'radiant',{'sun-amber':1},'Deal 6 damage to an undead enemy. Cannot target living creatures or constructs.'),
 ('mending-light','Mending light',['Growth','Restoration'],['steady-growth','gentle-preservation'],'heal',{'silver-ivy':1},'Restore 3 vitality to one present party member or household resident, up to 6. One phase; no resurrection or advancement.'),
 ('giant-grasp','Giant’s grasp',['Binding','Force'],['joined-fibres','steady-hearth-wards'],'strength',{'binding-thread':1},'For the caster’s next two physical mission actions: +2 attack damage, or reduce a physical obstacle from two phases to one. Also adds +3 Might to optional approach scores while charged; choosing a boosted approach spends one charge. No permanent attribute increase.'),
 ('lucid-sight','Lucid sight',['Light','Clarity'],['luminous-copying','clear-instruction'],'insight',{'moon-glass':1},'Reduce the caster’s next two deciphering mission obstacles from two phases to one. Also adds +3 Intelligence to optional approach scores while charged; choosing a boosted approach spends one charge. Does not reveal hidden story facts.'),
 ('borrowed-hour','Borrowed hour',['Rhythm','Acceleration'],['clear-instruction','field-calibration'],'haste',{'moon-glass':1},'Adds 1 work on the recipient’s next three eligible funded work phases: core research, artifacts, inscriptions, housing, restoration, facilities, annex construction, personal projects, principle/practice study or public production/study jobs. In missions it shortens three ordinary multi-phase obstacles. Does not advance the day, duplicate income, shorten rituals or care, grant advancement or bypass choices.'),
 ('threshold-fold','Threshold fold',['Passage','Anchor'],['courteous-passage','field-calibration'],'teleport',{'moon-glass':2},'Resolve an outbound journey to a previously reached core site, or a returning core expedition, instantly. Carries the existing party; does not complete fieldwork, reveal a new site or advance castle tasks.'),
]
SPELLS += [
 ('calm-tide','Calming tide',['Water','Emotion'],['water-guidance','clear-instruction'],'calm',{'silver-ivy':1},'Quiet the frightened aqueduct caretaker’s panic for a one-phase conversation that opens passage. Does not rewrite memories, recruit her, establish romance or compel unrelated actions.'),
 ('silver-tongue','Silver suggestion',['Voice','Attention'],['clear-instruction','reference-binding'],'suggestion',{'binding-thread':1},'Make the caretaker’s passage bargain easier: pay 2 crowns instead of the ordinary 8, and finish the negotiation in one phase. Applies only to this authored bargain.'),
 ('mirror-decoy','Mirror decoy',['Light','Echo'],['gentle-refraction','luminous-copying'],'decoy',{'moon-glass':1},'Summon a temporary false companion that absorbs the next two enemy retaliations against the caster. It cannot attack or collect rewards and disappears on returning home.'),
 ('wisp-scout','Wisp scout',['Light','Observation'],['luminous-copying','field-calibration'],'scout',{'sun-amber':1},'Summon a scouting wisp: reveal the next aqueduct obstacle and reduce the next two ordinary multi-phase obstacles by one phase each. One scouting enchantment at a time; no remote private lore.'),
 ('water-walk','Waterwalk',['Water','Surface tension'],['water-guidance','capillary-wicking'],'waterwalk',{'porous-clay':1},'Carry the whole party across the flooded lower gallery in one phase. Does not cross a dry chasm or allow underwater breathing.'),
 ('water-breath','Undertide breath',['Water','Living air'],['water-guidance','steady-growth'],'waterbreath',{'silver-ivy':1},'Let the party breathe underwater while resetting the submerged sluice in one phase instead of draining it over three. Protection lasts for that encounter only.'),
]
STEPS=[
 {'id':'fire','name':'The burning maintenance gate','text':'A fallen lamp has set dry debris burning across the gate. Douse it, freeze it down, or clear a safe route with sand.','tag':'fire','mundane':'Smother the flames with sand','phases':2},
 {'id':'caretaker','name':'The frightened sluice caretaker','text':'A frightened caretaker guards the safe passage. Reassure her patiently, pay her listed access fee, or use a narrowly defined calming or bargaining spell. No threat or romance is involved.','tag':'social','mundane':'Talk through the danger and agree passage','phases':2},
 {'id':'flood','name':'The flooded lower gallery','text':'Shallow floodwater hides unstable footing. A temporary walkway is safe but slow to assemble; water-walking keeps the party above it.','tag':'flood','mundane':'Build a temporary raised walkway','phases':2},
 {'id':'submerged','name':'The submerged sluice wheel','text':'The release wheel is fully underwater. Drain the inspection chamber, or breathe beneath the surface while turning it.','tag':'submerged','mundane':'Drain the inspection chamber','phases':3},
 {'id':'gap','name':'The broken water span','text':'The channel has broken the footbridge. The far ledge is close, but the drop is not forgiving.','tag':'gap','mundane':'Rig a supported rope crossing','phases':2},
 {'id':'ember','name':'The escaped ember hound','text':'An old kiln construct has shed its shell into a hostile living flame. Water or ice can quench it; more fire cannot.','tag':'enemy','enemy':'ember','hp':6,'attack':1,'mundane':'Strike with the insulated survey staff','phases':1},
 {'id':'briar','name':'The briar stalker','text':'A thorn-covered creature nests beside the upper stairs. Its dry outer thorns burn readily. You can fight, wait for it to leave, or distract it.','tag':'enemy','enemy':'living','hp':6,'attack':1,'mundane':'Drive it back with the survey staff','phases':1},
 {'id':'tower','name':'The high inspection landing','text':'The ladder is gone. The sound mooring points permit a careful climb; sustained flight can carry the whole party.','tag':'height','mundane':'Set ropes and climb together','phases':2},
 {'id':'bones','name':'The restless sluice keeper','text':'An undead watchman still bars the service passage. A focused dawn lance can break its animating bond.','tag':'enemy','enemy':'undead','hp':6,'attack':2,'mundane':'Fight defensively with the survey staff','phases':1},
 {'id':'stone','name':'The fallen counterweight','text':'A heavy stone counterweight pins the service door. Levers work; a brief increase in strength makes the lift quicker.','tag':'physical','mundane':'Lever the stone clear','phases':2},
 {'id':'sentinel','name':'The conductive sentinel','text':'A damaged metal sentinel mistakes the repair party for intruders. Its joints conduct a lightning discharge.','tag':'enemy','enemy':'construct','hp':6,'attack':1,'mundane':'Strike the damaged joints','phases':1},
 {'id':'runes','name':'The regulator’s cipher','text':'The final regulator has numbered mechanical stops and an old reference cipher. Read it carefully before opening the sluice.','tag':'insight','mundane':'Decipher the stops and reset the regulator','phases':2},
]
DEFINITION={'id':SITE,'name':'Cinder aqueduct','description':'A twelve-encounter repair expedition with fire, broken crossings, a high landing, hostile creatures and an old regulator. Elemental magic offers specific alternatives. Vitality, enemy damage and completed obstacles persist; retreat is always available.', 'approaches':{'survey':{'name':'Restore the inspection route','description':'Choose a method at each obstacle. Prepared field spells consume their listed components; combat exchanges use one phase. Ordinary methods work without magic, with recovery visits if needed.','reward':'Return once with 24 crowns, 2 moon glass, 2 fireglass and 3 advancement for each returning participant.'}}}

def install(g):
 for key,name,ideas,principles,kind,inputs,effect in SPELLS:
  d={'name':name,'ideas':ideas,'requiredPrinciple':principles[0],'requiredPrinciples':principles,'requiredProperties':['vessel','binding'],'roomId':'library','description':effect,'effect':effect,'castingInputs':inputs,'materialOutput':{},'crownsOutput':0,'field':kind,'limits':'Only explicitly listed mission targets and situations are valid. Learned, prepared magic and listed supplies are required.'}
  if kind=='haste':d['support']={'kind':'haste','amount':1,'charges':3,'target':'person'}
  g.SPELL_FORMS[key]=d
 g.EXPEDITION_SITES[SITE]=DEFINITION

def progress(s):return s.get('fieldMagic',{}).get('aqueduct',{'completed':[],'enemyHp':{},'pending':None,'discoveries':[],'buffs':{}})
def initialize(s):
 m=s.setdefault('fieldMagic',{});m.setdefault('aqueduct',deepcopy(progress(s)));m.setdefault('vitality',{});m.setdefault('visited',[])
 return m

def vitality(s,who):return s.get('fieldMagic',{}).get('vitality',{}).get(who,6)
def heal(s,who,n):initialize(s)['vitality'][who]=min(6,vitality(s,who)+n)
def step(s):return next((d for d in STEPS if d['id'] not in progress(s)['completed']),None)
def resume(s):
 initialize(s);e=s['expedition'];e['stage']='encounter-choice' if step(s) else 'ready-to-return';e['discoveryReady']=step(s) is None

def damage(kind,d):
 enemy=d.get('enemy')
 if kind=='water':return 4 if enemy=='ember' else 2 if enemy=='living' else 0
 if kind=='fire':return 0 if enemy=='ember' else 1 if enemy=='construct' else 4 if enemy=='living' else 3
 if kind=='ice':return 4 if enemy=='ember' else 2
 if kind=='lightning':return 6 if enemy=='construct' else 4
 if kind=='radiant':return 6 if enemy=='undead' else 0
 return 0

def reasons(s,who,spell_id=None,method=None,target=None):
 import game as g
 e=s['expedition'];r=[]
 if not e:return ['Begin an expedition first.']
 party=g.expedition_party(s)
 if who not in party:return ['The caster must be in this expedition party.']
 if spell_id:
  spell=next((x for x in s['spellbook'] if x['id']==spell_id and x['ownerId']==who),None)
  if not spell:return ['Choose this person’s own spell.']
  form=g.SPELL_FORMS[spell['formId']];kind=form.get('field')
  if spell['status']!='learned' or spell_id not in s['preparedSpells'][who]:r.append('Learn and prepare this spell at home first.')
  if any(p not in g.character_principles(s,who) for p in form['requiredPrinciples']):r.append('The caster must have learned every required principle.')
  import lasting_rituals
  actual_inputs={'moon-glass':1} if kind=='teleport' and lasting_rituals.active(s,'anchor-circle') else form['castingInputs']
  for k,n in actual_inputs.items():
   if s['materialInventory'][k]<n:r.append('Needs '+str(n)+' '+g.MATERIALS[k]['name']+'.')
  if kind=='teleport':
   if e['stage'] not in ('outbound','returning'):r.append('Choose an outbound or returning journey first.')
   if e['stage']=='outbound' and e['siteId'] not in s.get('fieldMagic',{}).get('visited',[]) and not g.discoveries_for(s,e['siteId']):r.append('Reach this destination normally before anchoring a teleport there.')
   return r
 else:kind=method
 if e['siteId']!=SITE or e['stage']!='encounter-choice':r.append('Choose a method at a Cinder aqueduct encounter.');return r
 d=step(s)
 if not d:return r+['All encounters are complete.']
 if vitality(s,who)<=0 and kind not in ('heal','bandage'):r.append('This person needs healing or rest at home before acting.')
 if kind in ('heal','bandage'):
  if target not in party:r.append('Choose a member of this party to heal.')
  elif vitality(s,target)>=6:r.append('That person is already at full vitality.')
  if kind=='bandage' and s['materialInventory']['silver-ivy']<1:r.append('First aid needs 1 silver ivy.')
 elif kind in ('strength','insight','haste','decoy','scout'):
  if progress(s)['buffs'].get(who,{}).get(kind,0):r.append('Use this person’s remaining boost first.')
 elif kind and kind.startswith('aptitude:'):
  option=approaches.field_option(s,who,kind)
  if not option:r.append('This additional approach does not belong to the current obstacle.')
  elif not option['check']['qualified']:r.append(option['check']['detail']+'. Train, bring a capable companion, use a relevant boost, or choose an ordinary method.')
 elif kind=='equipment':
  if d['tag'] not in ('physical','gap','height','flood','fire','insight','submerged'):r.append('Packed tools cannot solve this obstacle.')
  material='moon-glass' if d['tag']=='insight' else 'porous-clay' if d['tag']=='submerged' else 'binding-thread'
  count=1 if d['tag']=='insight' else 2
  if s['materialInventory'][material]<count:r.append('Needs '+str(count)+' '+g.MATERIALS[material]['name']+' for this equipment approach.')
 elif kind=='risk':
  if d['tag'] not in ('physical','gap','height','flood','fire'):r.append('This obstacle has no safe-to-model hurried physical approach.')
  if vitality(s,who)<2:r.append('Needs at least 2 vitality; the hurried method causes 1 injury.')
 elif kind in ('evade','lure'):
  if d['tag']!='enemy':r.append('There is no enemy here to bypass.')
  if kind=='lure' and not progress(s)['buffs'].get(who,{}).get('decoy',0):r.append('Prepare a Mirror decoy before luring the enemy away.')
 elif kind=='bargain':
  if d['tag']!='social':r.append('There is no passage bargain at this obstacle.')
  if s['sharedFunds']<8:r.append('The ordinary passage bargain costs 8 crowns.')
 elif kind=='mundane':pass
 elif not ((kind in ('calm','suggestion') and d['tag']=='social') or (kind=='waterwalk' and d['tag']=='flood') or (kind=='waterbreath' and d['tag']=='submerged') or (kind=='water' and d['tag']=='fire') or (kind=='ice' and d['tag'] in ('fire','gap')) or (kind=='leap' and d['tag']=='gap') or (kind=='flight' and d['tag'] in ('gap','height')) or (d['tag']=='enemy' and damage(kind,d)>0)):
  r.append('This spell has no valid target at this obstacle.')
 if kind=='suggestion' and s['sharedFunds']<2:r.append('The suggested passage bargain still costs 2 crowns.')
 return r

def apply(s,a):
 if a.get('type') not in ('field-spell','field-method'):return False
 import game as g
 if a.get('type')=='field-method' and isinstance(a.get('method'),str) and a['method'].startswith('personal:'):
  import personal_paths
  return personal_paths.start_field(s,a)
 who=a.get('characterId','founder');spell_id=a.get('spellId') if a['type']=='field-spell' else None;method=a.get('method') if not spell_id else None;target=a.get('targetId',who)
 g.require(isinstance(who,str) and (isinstance(spell_id,str) if a['type']=='field-spell' else isinstance(method,str) and (method in ('mundane','bandage','bargain','equipment','risk','evade','lure') or method.startswith('aptitude:'))),'Choose a field method or saved spell.')
 blocked=reasons(s,who,spell_id,method,target);g.require(not blocked,' '.join(blocked))
 form=g.SPELL_FORMS[g.spell_by_id(s,spell_id)['formId']] if spell_id else None;kind=form['field'] if form else method
 inputs=deepcopy(form['castingInputs']) if form else {'silver-ivy':1} if method=='bandage' else {'binding-thread':2} if method=='equipment' else {}
 import lasting_rituals
 if kind=='teleport' and lasting_rituals.active(s,'anchor-circle'):inputs={'moon-glass':1}
 if kind=='equipment':
  tag=step(s)['tag'];inputs={'moon-glass':1} if tag=='insight' else {'porous-clay':2} if tag=='submerged' else {'binding-thread':2}
 cost=2 if kind=='suggestion' else 8 if kind=='bargain' else 0
 for k,n in inputs.items():s['materialInventory'][k]-=n
 s['sharedFunds']-=cost
 initialize(s)
 if kind=='teleport':
  g.spell_by_id(s,spell_id)['castCount']+=1
  g.resolve_expedition(s);g.add_journal(s,'Threshold fold resolved the journey instantly. No castle work or day phase advanced.');return True
 p=progress(s);d=step(s);phases=3 if kind=='evade' else 2 if kind=='equipment' and d['tag']=='submerged' else 1
 if kind=='mundane':
  phases=d['phases'];buffs=p['buffs'].get(who,{})
  boost='insight' if d['tag']=='insight' else 'strength'
  if d['tag']!='enemy' and phases>1 and buffs.get(boost,0):phases=1;buffs[boost]-=1
  if phases>1 and buffs.get('haste',0):phases-=1;buffs['haste']-=1
  if phases>1 and buffs.get('scout',0):phases-=1;buffs['scout']-=1
 aptitude=approaches.field_option(s,who,kind) if kind.startswith('aptitude:') else None
 if aptitude and aptitude['check']['buff']:p['buffs'][who][aptitude['check']['buff']]-=1
 p['pending']={'aptitude':deepcopy(aptitude),'kind':kind,'who':who,'target':target,'spellId':spell_id,'inputs':inputs,'crowns':cost,'remaining':phases}
 s['expedition'].update(stage='working',remainingWorkPhases=phases)
 g.add_journal(s,(form['name'] if form else d['mundane'] if kind=='mundane' else aptitude['name'] if aptitude else kind.title())+' agreed: '+str(phases)+' phase(s). Supplies committed.')
 return True

def resolve(s):
 import game as g
 e=s['expedition'];p=progress(s);party=g.expedition_party(s)
 if e['stage']=='returning':
  initialize(s);p=progress(s)
  if p['pending']:
   for k,n in p['pending']['inputs'].items():s['materialInventory'][k]+=n
   s['sharedFunds']+=p['pending'].get('crowns',0)
   p['pending']=None
  p['buffs']={}
  rewards=['Returned safely. Completed obstacles and enemy damage are retained; unfinished spell inputs are returned.']
  if e['discoveryReady'] and not p['discoveries']:
   p['discoveries'].append('survey');s['materialInventory']['moon-glass']+=2;s['materialInventory']['fireglass']+=2
   rewards=[g.distribute_expedition_wealth(s,24),'2 moon glass and 2 fireglass deposited; the aqueduct route is restored.']
   for who in party:g.award_advancement(s,who,SITE,3,'Restored the Cinder aqueduct')
  if e['restoreLanternDisplay']:s['lanternDisplayed']=True
  s['lastExpeditionReport']={'siteId':SITE,'approach':e['chosenApproach'],'returnedDay':s['dayNumber'],'participants':party,'rewards':rewards}
  s['expedition']=None
  for who in party:g.set_character_assignment(s,who,'rest')
  s['lastPhaseSummary']+=rewards;return
 job=p['pending'];job['remaining']-=1;e['remainingWorkPhases']=job['remaining']
 if job['remaining']>0:return
 d=step(s);who=job['who'];kind=job['kind'];text=[];complete=False
 if job['spellId']:g.spell_by_id(s,job['spellId'])['castCount']+=1
 if kind.startswith('personal:'):
  import personal_paths
  complete=personal_paths.resolve_field(s,job,d,text)
 elif kind in ('heal','bandage'):heal(s,job['target'],(3+approaches.healing_bonus(s,who) if kind=='heal' else 2+int(approaches.builds.build(s,job['target'])['attributes']['vitality']>=8)));text.append('Health restored to '+str(vitality(s,job['target']))+'/6.')
 elif kind in ('strength','insight','haste','decoy','scout'):
  p['buffs'].setdefault(who,{})[kind]=(3 if kind=='haste' else 2)+int(approaches.score(s,who,approaches.spec('resolve','channeling'))['qualified'])
  text.append('Temporary '+kind+' boost prepared; no permanent attributes changed.')
  if kind=='scout':
   upcoming=next((x for x in STEPS if x['id'] not in p['completed'] and x['id']!=d['id']),None)
   p['scoutingReport']=('Next obstacle: '+upcoming['name']+'. '+upcoming['text']) if upcoming else 'This is the final obstacle.'
   text.append(p['scoutingReport'])
 elif kind.startswith('aptitude:'):
  complete=True;text.append(job['aptitude']['result']);text.append(job['aptitude']['check']['detail'])
 elif kind in ('evade','lure'):
  complete=True
  if kind=='lure':p['buffs'][who]['decoy']-=1
  text.append('The enemy is bypassed alive; no retaliation or kill reward.')
 elif kind=='risk':
  initialize(s)['vitality'][who]=vitality(s,who)-1;complete=True;text.append('The hurried crossing succeeds at the cost of 1 vitality.')
 elif d['tag']=='enemy':
  hit=2+int(approaches.score(s,who,approaches.spec('might','athletics'))['qualified']) if kind=='mundane' else damage(kind,d)+approaches.precision_bonus(s,who)
  if kind=='mundane' and p['buffs'].get(who,{}).get('strength',0):hit+=2;p['buffs'][who]['strength']-=1
  hp=max(0,p['enemyHp'].get(d['id'],d['hp'])-hit);p['enemyHp'][d['id']]=hp;complete=hp==0
  text.append(str(hit)+' damage; '+str(hp)+' enemy vitality remains.')
  if hp and kind!='ice':
   if p['buffs'].get(who,{}).get('decoy',0):p['buffs'][who]['decoy']-=1;text.append('The summoned decoy draws the retaliation; no vitality lost.')
   else:initialize(s)['vitality'][who]=max(0,vitality(s,who)-d['attack']);text.append('Retaliation: '+str(d['attack'])+' damage; '+str(vitality(s,who))+'/6 vitality.')
 else:complete=True
 if complete:
  p['completed'].append(d['id']);p.setdefault('outcomes',[]).append({'stepId':d['id'],'method':kind,'actor':who,'text':' '.join(text)})
  text.append(d['name']+' cleared.')
 p['pending']=None;resume(s);s['lastPhaseSummary']+=text;g.add_journal(s,' '.join(text))

def view(s):
 import game as g
 e=s['expedition'];people=g.expedition_party(s) if e else g.household_members(s)
 out={'active':bool(e and e['siteId']==SITE),'vitality':[{'id':who,'name':g.character_profile(s,who)['name'],'value':vitality(s,who)} for who in people],'spells':[],'step':None}
 if not e:return out
 if out['active']:
  d=step(s);out.update(step=deepcopy(d),progress=deepcopy(progress(s)),totalSteps=len(STEPS),methods=[])
  if d:
   if d.get('hp'):out['step']['hp']=progress(s)['enemyHp'].get(d['id'],d['hp'])
   for who in people:
    for option in approaches.field_options(s,who):
     out['methods'].append({'who':who,'target':who,'method':option['id'],'name':option['name']+' · 1 phase · '+option['check']['detail'],'blockers':reasons(s,who,method=option['id'])})
    for method in ('mundane','bandage','bargain','equipment','risk','evade','lure'):
     for target in (people if method=='bandage' else [who]):out['methods'].append({'who':who,'target':target,'method':method,'name':d['mundane'] if method=='mundane' else 'Pay 8 crowns for passage' if method=='bargain' else {'equipment':('Use a reading prism · 1 moon glass · 1 phase' if d['tag']=='insight' else 'Rig clay siphons · 2 porous clay · 2 phases' if d['tag']=='submerged' else 'Rig packed equipment · 2 binding thread · 1 phase'),'risk':'Hurry through · 1 vitality · 1 phase','evade':'Wait and slip past · 3 phases','lure':'Lure away with a prepared decoy · 1 phase'}.get(method,'First aid: '+g.character_profile(s,target)['name']),'blockers':reasons(s,who,method=method,target=target)})
 for spell in s['spellbook']:
  if spell['ownerId'] not in people:continue
  d=g.SPELL_FORMS[spell['formId']]
  if not d.get('field'):continue
  inputs=deepcopy(d['castingInputs'])
  import lasting_rituals
  if d['field']=='teleport' and lasting_rituals.active(s,'anchor-circle'):inputs['moon-glass']=1
  for target in (people if d['field']=='heal' else [spell['ownerId']]):out['spells'].append({'id':spell['id'],'who':spell['ownerId'],'target':target,'name':d['name'],'effect':d['effect']+(' Your precision adds 1 damage to a valid offensive hit.' if damage(d.get('field'),step(s) or {}) and approaches.precision_bonus(s,spell['ownerId']) else '')+(' Your restorative technique adds '+str(approaches.healing_bonus(s,spell['ownerId']))+' healing.' if d.get('field')=='heal' and approaches.healing_bonus(s,spell['ownerId']) else '')+(' Resolve + twice Channeling of 9 grants one extra charge.' if d.get('field') in ('strength','insight','haste','decoy','scout') else ''),'inputs':inputs,'blockers':reasons(s,spell['ownerId'],spell['id'],target=target)})
 import personal_paths
 if out['active']:
  out.setdefault('methods',[]).extend({'who':r['who'],'target':r['who'],'method':r['id'],'name':r['name']+' · '+r['description'],'blockers':r['blockers']} for r in personal_paths.field_options(s))
 return out


def existing_caster(s,form_id):
 import game as g
 d=g.SPELL_FORMS[form_id]
 return next((spell for spell in s['spellbook'] if spell['formId']==form_id and spell['ownerId'] in g.expedition_party(s) and spell['status']=='learned' and spell['id'] in s['preparedSpells'][spell['ownerId']] and all(p in g.character_principles(s,spell['ownerId']) for p in d['requiredPrinciples']) and all(s['materialInventory'][k]>=n for k,n in d['castingInputs'].items())),None)

def existing_blockers(s,choice):
 import game as g
 form=choice.get('castForm')
 if not form:return []
 e=s['expedition']
 if e['siteId'] in ('stormwatch-beacon','lantern-pavilion'):
  return [] if existing_caster(s,form) else ['A party member must know and prepare '+g.SPELL_FORMS[form]['name']+' and carry its casting components.']
 p=s['serviceRoad'] if e['siteId']=='old-service-road' else s['observatoryProgress'][e['chosenApproach']]
 if p.get('pendingWork',{} ) and p['pendingWork'].get('magicPaid')==form:return []
 return [] if existing_caster(s,form) else ['A party member must know and prepare '+g.SPELL_FORMS[form]['name']+' and carry its casting components.']

def commit_existing(s,choice):
 import game as g
 form=choice.get('castForm')
 if not form:return
 spell=existing_caster(s,form);g.require(spell is not None,'Restore the prepared spell and its components first.')
 for key,n in g.SPELL_FORMS[form]['castingInputs'].items():s['materialInventory'][key]-=n
 spell['castCount']+=1

def expand_existing(g):
 import service_road as road
 mappings=[(g.OBSERVATORY_STEPS[0],'water-jet','Drive the trapped water out'),(g.OBSERVATORY_STEPS[1],'giant-grasp','Brace and free the stiff alignment wheel'),(g.OBSERVATORY_STEPS[2],'lucid-sight','Read the weather diagrams with sharpened insight'),(road.STEPS['channel'],'water-walk','Inspect from the water surface'),(road.STEPS['orchard'],'wind-step','Step between the surviving terraces'),(road.STEPS['shelter'],'wisp-scout','Scout the hidden joints before drawing them')]
 for step,form,name in mappings:
  d=g.SPELL_FORMS[form];cost=' + '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['castingInputs'].items())
  step['choices']['spell:'+form]={'name':name,'phases':1,'castForm':form,'description':'One phase. Requires learned, prepared '+d['name']+' in the party. Consume '+cost+' when chosen; an interrupted paid method remains saved.'}
