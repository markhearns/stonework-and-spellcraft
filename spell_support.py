"""Authored, finite work enchantments. Charges are consumed only by matching work."""
from copy import deepcopy

DEFINITIONS=[
 ('research-lens','Lens of comparison',['Reference','Refraction'],['reference-binding','gentle-refraction'],'research',2,2,'person','library',{'moon-glass':1},'Adds 2 work to the recipient’s next two core research/archive work phases. Does not teach unknown principles.'),
 ('craft-hand','Patient hand',['Binding','Clear instruction'],['joined-fibres','clear-instruction'],'craft',2,2,'person','library',{'binding-thread':1},'Adds 2 work to the recipient’s next two core artifact-crafting phases. Does not create an item without a funded recipe.'),
 ('copy-lamp','Scribe’s afterlight',['Light','Preservation'],['luminous-copying','gentle-preservation'],'copy',3,3,'founder','library',{'sun-amber':1},'Adds 3 crowns to each of the scholar’s next three ordinary copying phases. Does not increase spell commissions.'),
 ('focus-guide','Guiding lattice',['Refraction','Binding'],['gentle-refraction','reference-binding'],'focus',1,3,'person','library',{'binding-thread':1},'Adds 1 work to the recipient’s next three signature-focus inscription phases. Does not affect equipment, testing or rituals.'),
 ('bedroom-ward','Settling threshold',['Preservation','Joined fibres'],['gentle-preservation','joined-fibres'],'housing',1,3,'founder','common-room',{'binding-thread':1},'Adds 1 work to the next three funded bedroom-fitting phases. Does not create beds before the room is complete.'),
 ('green-frame','Glasshouse embrace',['Growth','Warmth'],['steady-growth','steady-hearth-wards'],'restoration',1,2,'founder','common-room',{'silver-ivy':1},'Adds 1 work to the next two conservatory-restoration phases. Costs and funding prerequisites still apply.'),
 ('foundation-line','True foundation',['Calibration','Settling'],['field-calibration','settling-flow'],'construction',1,3,'founder','library',{'porous-clay':1},'Adds 1 work to the next three headquarters or living-facility construction phases. Does not accelerate drills, jobs or specialist installations.'),
 ('field-compass','Wayfinder’s impression',['Calibration','Reference'],['field-calibration','reference-binding'],'briefing',0,1,'field','library',{'binding-thread':1},'Prepares one household field briefing: the next ordinary core survey takes one work phase. Shares the existing briefing slot; does not stack with lanterns or field notes or affect Rainward methods.'),
]

def install(forms):
 for key,name,ideas,principles,kind,amount,charges,target,room,inputs,effect in DEFINITIONS:
  forms[key]={'name':name,'ideas':ideas,'requiredPrinciple':principles[0],'requiredPrinciples':principles,'requiredProperties':['vessel','binding'],'roomId':room,'description':effect,'effect':effect+' Casting takes one assigned phase and consumes the listed inputs.','castingInputs':inputs,'materialOutput':{},'crownsOutput':0,'support':{'kind':kind,'amount':amount,'charges':charges,'target':target},'limits':'No passive time advancement. An unused enchantment waits without expiring; identical effects do not stack.'}

def remaining(s,who,kind):return s.get('spellSupports',{}).get(who,{}).get(kind,{}).get('remaining',0)
def bonus(s,who,kind):
 r=s.get('spellSupports',{}).get(who,{}).get(kind,{})
 import lasting_rituals
 base=r.get('amount',0) if r.get('remaining',0)>0 else 0
 haste=s.get('spellSupports',{}).get(who,{}).get('haste',{})
 if who=='founder' and kind in ('housing','restoration','construction') and lasting_rituals.active(s,'foundation-circle'):base+=1
 return base+(haste.get('amount',0) if kind in ('research','craft','focus','housing','restoration','construction') and haste.get('remaining',0)>0 else 0)

def target_for(s,d,owner,requested=None):
 import game as g
 target='founder' if d['support']['target'] in ('founder','field') else requested or owner
 g.require(isinstance(target,str) and target in g.household_members(s),'Choose a current household recipient.')
 g.require(g.character_at_castle(s,target),'The recipient must be home when the enchantment is agreed.')
 return target

def check(s,d,target):
 import game as g
 kind=d['support']['kind']
 g.require(not (s['headquarters']['briefing'] if kind=='briefing' else remaining(s,target,kind)),'This enchantment is already prepared. Use its remaining charges first.')
 for job in s['spellWork'].values():
  if not job or job['kind']!='cast':continue
  other=g.SPELL_FORMS[g.spell_by_id(s,job['spellId'])['formId']].get('support')
  g.require(not(other and other['kind']==kind and job.get('targetId')==target),'Another caster is already preparing this enchantment for that recipient.')

def resolve(s,d,target,summary,caster=None):
 spec=d['support'];kind=spec['kind']
 import character_approaches as a
 extra=int(caster is not None and a.score(s,caster,a.spec('resolve','channeling'))['qualified'])
 if kind=='briefing':s['headquarters']['briefing']=True
 else:s.setdefault('spellSupports',{}).setdefault(target,{})[kind]={'spellName':d['name'],'remaining':spec['charges']+extra,'amount':spec['amount']}
 summary.append(d['name']+' prepared. '+d['description']+(' Practised channeling adds one charge.' if extra and kind!='briefing' else ''))

def consume(s,who,kind,summary,include_haste=True):
 if include_haste and kind in ('research','craft','focus','housing','restoration','construction'):consume(s,who,'haste',summary)
 r=s.get('spellSupports',{}).get(who,{}).get(kind)
 if r and r['remaining']>0:
  r['remaining']-=1;summary.append(r['spellName']+': one charge used; '+str(r['remaining'])+' remaining.')

def snapshot(s):
 import game as g
 out=[]
 for who in g.household_members(s):
  if not g.character_at_castle(s,who):continue
  assignment=g.character_assignment(s,who)
  kind=None
  if assignment in ('research','archive') and (s['researchStatus']=='in-progress' or s['activeResearchId']):kind='research'
  elif assignment=='archive-project' and s['miraArchiveProject']['status']=='in-progress':kind='research'
  elif assignment=='crafting' and s['craftingProject'] and s['craftingProject']['crafterId']==who:kind='craft'
  elif assignment=='commissions' and who=='founder':kind='copy'
  if kind and bonus(s,who,kind):out.append((who,kind))
 return out

def view(s):
 import game as g
 return [{'personId':who,'name':g.character_profile(s,who)['name'],'kind':kind,**deepcopy(r)} for who,records in s.get('spellSupports',{}).items() if who in g.household_members(s) for kind,r in records.items() if r['remaining']>0]


def haste_extra(s,who,done,total,summary,base=1):
 extra=min(bonus(s,who,'haste'),max(0,total-done-base))
 if extra:consume(s,who,'haste',summary)
 return extra


def opportunities(s):
 """Read-only suggestions tied to actual funded work; never auto-cast or reassign."""
 import game as g
 tasks=[]
 for who in g.household_members(s):
  if not g.character_at_castle(s,who):continue
  if s['researchStatus']=='in-progress' or s['activeResearchId']:tasks.append(('research-lens',who,'Funded research is waiting.'))
  if s['craftingProject'] and s['craftingProject']['crafterId']==who:tasks.append(('craft-hand',who,'This resident is the funded artifact maker.'))
  if s['focusProjects'][who]:tasks.append(('focus-guide',who,'A personal focus inscription is funded.'))
  if who=='founder':
   if s['founderAssignment']=='commissions':tasks.append(('copy-lamp',who,'Copying is currently assigned.'))
   if s['activeHousingRoomId']:tasks.append(('bedroom-ward',who,'Bedroom fitting is funded.'))
   if s['restorationStatus']=='in-progress':tasks.append(('green-frame',who,'Conservatory restoration is funded.'))
   if s['headquarters']['project'] and s['headquarters']['project']['kind']=='hq-build':tasks.append(('foundation-line',who,'A headquarters room is under construction.'))
 rows=[]
 for form,target,reason in tasks:
  if bonus(s,target,g.SPELL_FORMS[form]['support']['kind']):continue
  for spell in s['spellbook']:
   who=spell['ownerId']
   if spell['formId']!=form or spell['status']!='learned' or who not in g.household_members(s) or not g.character_at_castle(s,who):continue
   rows.append({'spellId':spell['id'],'formId':form,'name':g.SPELL_FORMS[form]['name'],'casterId':who,'targetId':target,'reason':reason,'prepared':spell['id'] in s['preparedSpells'][who],'assignment':g.character_assignment(s,who)})
 return rows
