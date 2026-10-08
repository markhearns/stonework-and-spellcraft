"""Individually owned working tools; one prepared tool, no passive production."""
from copy import deepcopy
CATALOG={
 'scholars-folio':{'name':'Scholar’s working folio','principle':'reference-binding','practice':'archive-focus','benefit':'+1 assigned research/archive work. No learning, copying income or personal-story bonus.'},
 'makers-gauge':{'name':'Maker’s alignment gauge','principle':'clear-instruction','practice':'careful-assembly','benefit':'+1 assigned artifact crafting work. No focus inscription, spell testing or training bonus.'}}

UPGRADE_COST=12
UPGRADE_PHASES=2
UPGRADE_NAMES={'scholars-folio':'Cross-reference inscription','makers-gauge':'True-measure inscription'}

def register(namespace):
    for key,d in CATALOG.items():namespace['RECIPES'][key]={'name':d['name'],'requiredPrinciple':d['principle'],'requiredProperties':['vessel','binding'],'requiredWorkPhases':3,'description':d['benefit']+' After crafting, assign ownership and prepare it in Personal equipment.'}

    namespace['EXPEDITION_SITES']['old-waterworks']['approaches']['survey']['reward']+=' Also supplies the field observations for Field calibration research.'
    namespace['PRINCIPLE_NAMES']['field-calibration']='Field calibration'
    namespace['RESEARCH_CATALOG']['field-calibration']={'name':'Field calibration','costCrowns':12,'requiredWorkPhases':4,'requiredPrinciples':['water-guidance','reference-binding'],'principle':'field-calibration','requiredDiscovery':{'siteId':'old-waterworks','approach':'survey'},'description':'Compare the returned waterworks measurements with a stable reference. Learn to keep a small working tool aligned with its purpose.','benefit':'Unlocks personal working-tool inscriptions: +2 matching work instead of +1.'}
    namespace['PRINCIPLE_GUIDE']['field-calibration']={'source':'Return the waterworks survey, then complete Field calibration at the research desk. Other owners study the archived principle personally.','view':'research','use':'Improve an owned folio or alignment gauge.'}

def initialize(s):
    s.setdefault('personalEquipment',{});s.setdefault('preparedEquipment',{})
    s.setdefault('toolUpgradeProjects',{});s.setdefault('toolMoments',{})
    s['researchProjects'].setdefault('field-calibration',{'status':'not-started','completedWorkPhases':0,'contributors':[]})
    for item in s['personalEquipment'].values():item.setdefault('inscription',None)
    for key in CATALOG:s['craftedArtifacts'].setdefault(key,0)

def bonus(s,who,practice):
    key=s.get('preparedEquipment',{}).get(who);item=s.get('personalEquipment',{}).get(key)
    if not item or item['ownerId']!=who:return []
    d=CATALOG[item['kind']];upgraded=bool(item.get('inscription'))
    if 'armoury' in s:
        import armoury as a
        host=next((i for i in a.state(s)['items'].values() if i.get('legacy')=={'kind':'tool','id':key}),None)
        if host:
            if host['location']!='armoury' or a.busy(s,host['id']) or not a.equipped(s,host['id']):return []
            upgraded=a.has(s,who,'legacy-tool')
    return [{'name':item['name'],'amount':2 if upgraded else 1}] if d['practice']==practice else []

def view(s):
    import game as g
    return {'catalogue':deepcopy(CATALOG),'items':deepcopy(s.get('personalEquipment',{})),'prepared':deepcopy(s.get('preparedEquipment',{})),'projects':deepcopy(s.get('toolUpgradeProjects',{})),'upgradeNames':UPGRADE_NAMES,'upgradeCost':UPGRADE_COST,'upgradePhases':UPGRADE_PHASES,'upgradeBlockers':{key:upgrade_blockers(s,item['ownerId'],key) for key,item in s.get('personalEquipment',{}).items()},'moments':deepcopy(s.get('toolMoments',{})),'journey':journey(s),
            'people':{who:{'name':s['people'][who]['name'],'atHome':g.character_at_castle(s,who),'focus':g.focus_view(s,who)} for who in g.household_members(s)}}

def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind not in ('claim-working-tool','prepare-working-tool','stow-working-tool','rename-working-tool','transfer-working-tool','upgrade-working-tool','resume-tool-upgrade','cancel-tool-upgrade','join-tool-moment','defer-tool-moment','restore-tool-moment'):return False
    who=a.get('ownerId')
    g.require(isinstance(who,str) and who in g.household_members(s),'Choose a household member.')
    g.require(g.character_at_castle(s,'founder') and g.character_at_castle(s,who),'Return home together before changing equipment.')
    if kind in ('join-tool-moment','defer-tool-moment','restore-tool-moment'):
        moment_action(s,a,who);return True
    if kind in ('upgrade-working-tool','resume-tool-upgrade','cancel-tool-upgrade'):
        upgrade_action(s,a,who);return True
    if kind=='claim-working-tool':
        tool=a.get('toolId');g.require(isinstance(tool,str) and tool in CATALOG,'Choose a supported working tool.')
        g.require(g.spare_artifact_count(s,tool)>0,'Craft an unreserved copy first.')
        g.require(sum(r['ownerId']==who for r in s['personalEquipment'].values())<8,'Keep at most eight working tools per person.')
        item_id='tool-'+str(s.get('nextEquipmentNumber',1));s['nextEquipmentNumber']=s.get('nextEquipmentNumber',1)+1
        s['craftedArtifacts'][tool]-=1
        s['personalEquipment'][item_id]={'kind':tool,'ownerId':who,'name':CATALOG[tool]['name'],'ownershipHistory':[who],'inscription':None}
    elif kind=='stow-working-tool':s['preparedEquipment'].pop(who,None)
    else:
        key=a.get('itemId');g.require(isinstance(key,str) and key in s['personalEquipment'] and s['personalEquipment'][key]['ownerId']==who,'Choose this person’s own item.')
        item=s['personalEquipment'][key]
        if kind=='prepare-working-tool':s['preparedEquipment'][who]=key
        elif kind=='rename-working-tool':item['name']=g.text_value(a.get('name'),60)
        else:
            g.require(not any(p['itemId']==key for p in s.get('toolUpgradeProjects',{}).values()),'Finish or cancel this tool’s inscription before transferring it.')
            target=a.get('recipientId')
            g.require(isinstance(target,str) and target!=who and target in g.household_members(s) and g.character_at_castle(s,target),'Choose another household member at home.')
            g.require(a.get('ownersAgreed') is True,'Both people must agree the ownership transfer.')
            g.require(sum(r['ownerId']==target for r in s['personalEquipment'].values())<8,'The recipient already has eight working tools.')
            if s['preparedEquipment'].get(who)==key:s['preparedEquipment'].pop(who)
            item['ownerId']=target;item['ownershipHistory'].append(target)
    return True


def upgrade_blockers(s,who,key):
    import game as g
    item=s['personalEquipment'][key];rows=[]
    if who not in g.household_members(s):rows.append('The owner must be a current household member.')
    if not g.character_at_castle(s,'founder') or not g.character_at_castle(s,who):rows.append('Return home together to agree the work.')
    if item.get('inscription'):rows.append('This tool already has its permanent inscription.')
    if s.get('toolUpgradeProjects',{}).get(who):rows.append('Finish or cancel this owner’s current tool inscription.')
    if s['focusProjects'].get(who):rows.append('Finish this owner’s signature-focus work first.')
    if who not in ('founder','mira') and 'inscribing' not in g.character_profile(s,who).get('offeredAssignments',g.TAMSIN_ASSIGNMENTS):rows.append('This resident has not offered inscription work.')
    if 'field-calibration' not in g.character_principles(s,who):rows.append('The owner must personally learn Field calibration.')
    if s['sharedFunds']<UPGRADE_COST:rows.append('Requires 12 shared crowns.')
    return rows


def upgrade_action(s,a,who):
    import game as g
    kind=a['type'];project=s['toolUpgradeProjects'].get(who)
    if kind=='upgrade-working-tool':
        key=a.get('itemId')
        g.require(isinstance(key,str) and key in s['personalEquipment'] and s['personalEquipment'][key]['ownerId']==who,'Choose an owned working tool.')
        blockers=upgrade_blockers(s,who,key);g.require(not blockers,' '.join(blockers))
        materials=a.get('materials');g.validate_spell_materials(materials,['vessel','binding'])
        for material in set(materials):g.require(s['materialInventory'][material]-s['materialReserveTargets'][material]>=materials.count(material),'Supply the selected components above protected reserves.')
        s['sharedFunds']-=UPGRADE_COST
        for material in materials:s['materialInventory'][material]-=1
        s['toolUpgradeProjects'][who]={'itemId':key,'materials':materials[:],'costCrowns':UPGRADE_COST,'completedWorkPhases':0,'requiredWorkPhases':UPGRADE_PHASES}
        g.set_character_assignment(s,who,'inscribing')
        g.add_journal(s,g.character_profile(s,who)['name']+' began a personal tool inscription: 12 crowns, one vessel and one binding component committed.')
    else:
        g.require(project is not None,'There is no unfinished tool inscription for this owner.')
        if kind=='resume-tool-upgrade':g.set_character_assignment(s,who,'inscribing')
        else:
            s['sharedFunds']+=project['costCrowns']
            for material in project['materials']:s['materialInventory'][material]+=1
            del s['toolUpgradeProjects'][who]
            if g.character_assignment(s,who)=='inscribing':g.set_character_assignment(s,who,'rest')
            g.add_journal(s,'Cancelled unfinished tool inscription; committed crowns and components returned. Elapsed phases are not restored.')


def resolve(s,summary):
    import game as g
    for who,project in list(s.get('toolUpgradeProjects',{}).items()):
        if who not in g.household_members(s) or not g.character_at_castle(s,who) or g.character_assignment(s,who)!='inscribing':continue
        import headquarters
        work=1+int(headquarters.ready(s,'enchanting-room'))
        import spell_support
        work+=spell_support.haste_extra(s,who,project['completedWorkPhases'],project['requiredWorkPhases'],summary,work)
        project['completedWorkPhases']+=work
        item=s['personalEquipment'][project['itemId']]
        summary.append(g.character_profile(s,who)['name']+': '+item['name']+' inscription +'+str(work)+' work.')
        if project['completedWorkPhases']>=project['requiredWorkPhases']:
            item['inscription']={'name':UPGRADE_NAMES[item['kind']],'madeBy':who,'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
            del s['toolUpgradeProjects'][who];g.set_character_assignment(s,who,'rest')
            summary.append(item['name']+' completed: +2 matching assigned work when prepared, replacing its original +1.')
            if who!='founder':s['toolMoments'][project['itemId']]={'ownerId':who,'itemName':item['name'],'inscriptionName':item['inscription']['name'],'status':'waiting'}


def journey(s):
    import game as g
    discovered='survey' in g.discoveries_for(s,'old-waterworks')
    research=s['researchProjects']['field-calibration']
    return {'discovered':discovered,'research':deepcopy(research),'researchBlockers':g.research_blockers(s,'field-calibration','founder'),'ownedCount':len(s['personalEquipment']),'upgradedCount':sum(bool(i.get('inscription')) for i in s['personalEquipment'].values()),'preparedCount':len(s['preparedEquipment'])}


def moment_action(s,a,who):
    import game as g
    key=a.get('itemId');g.require(isinstance(key,str) and key in s['toolMoments'],'Choose a saved tool invitation.')
    r=s['toolMoments'][key];g.require(r['ownerId']==who,'This invitation belongs to its original maker.')
    kind=a['type']
    if kind=='defer-tool-moment':g.require(r['status']=='waiting','This invitation is not waiting.');r['status']='deferred';return
    if kind=='restore-tool-moment':g.require(r['status']=='deferred','This invitation is not deferred.');r['status']='waiting';return
    g.require(r['status']=='waiting','This conversation is already remembered or deferred.')
    choice=a.get('choice');g.require(choice in ('work','playful'),'Choose one of the offered conversation tones.')
    name=s['people'][who]['name'];tool=r['itemName']
    opening=name+' sets '+tool+' on the desk, then leaves the chair beside her free. “Finished. I thought you might want the first look.”'
    if choice=='work':reply='“The trick was finding a reference I could trust,” she says, turning the tool so its new inscription catches the lamp. “Now the correction stays where I put it.”'
    elif who=='mira':reply='Mira looks up through her lashes. “You may admire the binding. Though I would hate to think the book was getting all your attention.” Her smile makes the distinction quite deliberate.'
    else:reply='She catches the appreciative look and answers with a slow, amused smile. “The workmanship is down here. But I am willing to share the credit.” She taps the new inscription with one finger.'
    r.update(status='remembered',choice=choice,conversation=[opening,reply],completedOn={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']})
    g.add_journal(s,'Shared a conversation with '+name+' about her completed '+tool+'.')


def memories(s,who):
    return [{'title':'A tool made her own','participants':[s['people'][who]['name']],'conversation':r['conversation'],'on':r['completedOn']} for r in s.get('toolMoments',{}).values() if r['ownerId']==who and r['status']=='remembered'][-4:]
