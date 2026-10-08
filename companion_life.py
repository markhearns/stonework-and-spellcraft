"""Personal work and agreed styling for the new authored companions."""
from copy import deepcopy

PROJECTS = {
    'aurelia':{'name':'A collection of useful light','description':'Aurelia restores and compares shuttered lanterns, recording how to guide a steady light across a working page.',
        'costCrowns':12,'materials':{'fireglass':1,'binding-thread':1},'requiredWorkPhases':3,
        'principle':'luminous-copying','awardId':'aurelia-lantern-study',
        'result':'Aurelia earns 2 advancement, personally learns Luminous copying and records it in the archive. This enables the existing scribe-stone recipe; crafting and installation remain separate.'},
    'neris':{'name':'Glass that welcomes the hand','description':'Neris tests the curves of her glass vessels and records how their shape guides light as well as water.',
        'costCrowns':10,'materials':{'fireglass':1,'porous-clay':2},'requiredWorkPhases':3,
        'principle':'gentle-refraction','awardId':'neris-glass-study',
        'result':'Neris earns 2 advancement, personally learns Gentle refraction and records it in the archive. This enables the existing reading-prism recipe; crafting and installation remain separate.'},
}
ENSEMBLES = {
    'aurelia':{
        'working':{'name':'The lantern keeper','portraitId':'aurelia','components':['Slate-violet bodice and charcoal work skirt','Worn brass clasp','Dark ankle boots']},
        'evening':{'name':'After the lamps are lit','portraitId':'aurelia','components':['Midnight wrap top','Plum draped skirt','Worn brass clasp','Dark ankle boots']}},
    'neris':{
        'working':{'name':'The glassworker','portraitId':'neris','components':['Indigo halter blouse','Plum wrap skirt','Leather belt','Ankle boots']},
        'evening':{'name':'A ripple of violet','portraitId':'neris','components':['Violet cowl-neck dress','Small brass clasp','Ankle boots']}},
}


def initialize(state):
    for who,definition in PROJECTS.items():
        if who not in state.get('people',{}):continue
        record=state['additionalResidents'][who]
        record['wardrobe'].setdefault('ensembleId','working')
        if 'personal-project' not in state['people'][who]['offeredAssignments']:state['people'][who]['offeredAssignments'].append('personal-project')
        if record['personalProject']['status']=='not-offered':record['personalProject'].update(status='not-started',requiredWorkPhases=definition['requiredWorkPhases'])


def project_view(state,who):
    import game as g
    definition=PROJECTS[who];project=state['additionalResidents'][who]['personalProject'];blockers=[]
    if who not in g.household_members(state):blockers.append('Agree household membership before offering this work.')
    if not all(g.character_at_castle(state,p) for p in ('founder',who)):blockers.append('Both people must be home to agree her project.')
    if state['sharedFunds']<definition['costCrowns']:blockers.append('Needs '+str(definition['costCrowns'])+' shared crowns.')
    for material,count in definition['materials'].items():
        if state['materialInventory'][material]-state['materialReserveTargets'][material]<count:blockers.append('Needs '+str(count)+' unreserved '+g.MATERIALS[material]['name']+'.')
    return {**deepcopy(definition),**deepcopy(project),'startBlockers':blockers,
        'working':project['status']=='in-progress' and g.character_at_castle(state,who) and g.character_assignment(state,who)=='personal-project'}


def views(state):
    return {who:{'project':project_view(state,who),'ensembles':deepcopy(ENSEMBLES[who]),
        'ensembleId':state['additionalResidents'][who]['wardrobe'].get('ensembleId','working'),
        'savedStyles':deepcopy(state['additionalResidents'][who]['savedStyles'])} for who in PROJECTS if who in state['people']}


def apply(state,action):
    import game as g
    kind=action.get('type')
    actions=('start-companion-project','resume-companion-project','cancel-companion-project','choose-companion-ensemble','save-companion-style','load-companion-style','delete-companion-style')
    if kind not in actions:return False
    who=action.get('characterId')
    g.require(isinstance(who,str) and who in PROJECTS and who in g.household_members(state),'Choose a resident who has offered these choices.')
    g.require(all(g.character_at_castle(state,p) for p in ('founder',who)),'Return home together to agree this change.')
    definition=PROJECTS[who];record=state['additionalResidents'][who];project=record['personalProject']
    if kind=='start-companion-project':
        g.require(project['status']=='not-started','This project is already funded or complete.')
        blockers=project_view(state,who)['startBlockers'];g.require(not blockers,' '.join(blockers))
        state['sharedFunds']-=definition['costCrowns']
        for material,count in definition['materials'].items():state['materialInventory'][material]-=count
        project.update(status='in-progress',completedWorkPhases=0,requiredWorkPhases=definition['requiredWorkPhases'],committedCrowns=definition['costCrowns'],committedMaterials=deepcopy(definition['materials']))
        g.set_character_assignment(state,who,'personal-project')
        g.add_journal(state,state['people'][who]['name']+' agreed '+definition['name'].lower()+'. Exact listed costs committed; three personal work phases.')
    elif kind=='resume-companion-project':
        g.require(project['status']=='in-progress','There is no unfinished project to resume.')
        g.set_character_assignment(state,who,'personal-project')
    elif kind=='cancel-companion-project':
        g.require(project['status']=='in-progress','Only unfinished work can be cancelled and refunded.')
        state['sharedFunds']+=project.pop('committedCrowns')
        for material,count in project.pop('committedMaterials').items():state['materialInventory'][material]+=count
        project.update(status='not-started',completedWorkPhases=0)
        if g.character_assignment(state,who)=='personal-project':g.set_character_assignment(state,who,'rest')
        g.add_journal(state,state['people'][who]['name']+' put her unfinished project aside. Exact committed costs returned once; no advancement earned.')
    elif kind=='choose-companion-ensemble':
        ensemble=action.get('ensembleId')
        g.require(isinstance(ensemble,str) and ensemble in ENSEMBLES[who],'Choose one of her illustrated ensembles.')
        record['wardrobe']['ensembleId']=ensemble
        import outfit_progression
        outfit_progression.clear_selection(state,who)
        import character_customization
        character_customization.clear_style(state,who)
        state.get('residentCurrentStyles',{}).pop(who,None)
    else:
        name=g.text_value(action.get('name'),40)
        styles=record['savedStyles'];existing=next((item for item in styles if item['name']==name),None)
        if kind=='save-companion-style':
            g.require(existing is not None or len(styles)<8,'Keep up to eight named styles; forget one before adding another.')
            if existing:existing['ensembleId']=record['wardrobe']['ensembleId']
            else:styles.append({'name':name,'ensembleId':record['wardrobe']['ensembleId']})
        else:
            g.require(existing is not None,'Choose a saved style belonging to this resident.')
            if kind=='load-companion-style':
                record['wardrobe']['ensembleId']=existing['ensembleId']
                import outfit_progression
                outfit_progression.clear_selection(state,who)
                import character_customization
                character_customization.clear_style(state,who)
                state.get('residentCurrentStyles',{}).pop(who,None)
            else:styles.remove(existing)
    return True


def resolve(state,summary):
    import game as g
    for who,definition in PROJECTS.items():
        if who not in g.household_members(state):continue
        project=state['additionalResidents'][who]['personalProject']
        if project['status']!='in-progress' or not g.character_at_castle(state,who) or g.character_assignment(state,who)!='personal-project':continue
        project['completedWorkPhases']+=1
        summary.append(state['people'][who]['name']+' · '+definition['name']+': '+str(project['completedWorkPhases'])+' / '+str(project['requiredWorkPhases'])+' personal phases.')
        if project['completedWorkPhases']>=project['requiredWorkPhases']:
            project['status']='complete';g.set_character_assignment(state,who,'rest')
            g.learn_for_character(state,who,definition['principle'])
            g.award_advancement(state,who,definition['awardId'],2,'Completed '+definition['name'].lower())
            summary.append(definition['result'])


def forecast(state):
    import game as g
    return [state['people'][who]['name']+' · '+item['project']['name']+': '+('+1 personal work phase.' if item['project']['working'] else 'paused; resume her project to continue.')
        for who,item in views(state).items() if item['project']['status']=='in-progress']
