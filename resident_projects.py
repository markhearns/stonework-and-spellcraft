"""Authored professional ambitions, distinct from optional personal keepsakes."""
from copy import deepcopy

IONA_ATLAS = {
    'name':'An atlas of small crossings',
    'description':'Iona wants to compare her field notes with the household’s threshold research, then bind a practical atlas. The useful details are where to put a muddy boot, what a traveller can carry, and how to leave a crossing politely.',
    'costCrowns':10,'materials':{'binding-thread':2,'porous-clay':1},'requiredWorkPhases':3,
    'result':'Iona gains 2 advancement points and learns Courteous passage. Other characters must study the principle separately.',
}


def initialize(state):
    if 'iona' in state['people']:
        profile=state['people']['iona']
        if 'personal-project' not in profile['offeredAssignments']:profile['offeredAssignments'].append('personal-project')
        project=state['additionalResidents']['iona']['personalProject']
        if project['status']=='not-offered':project.update(status='not-started',requiredWorkPhases=3)


def view(state):
    import game as g
    if 'iona' not in state['people']:return None
    project=state['additionalResidents']['iona']['personalProject'];blockers=[]
    if 'iona' not in g.household_members(state):blockers.append('Iona must choose to join the household before offering this work.')
    if not all(g.character_at_castle(state,p) for p in ('founder','iona')):blockers.append('Both people must be home to discuss the atlas.')
    if 'courteous-passage' not in state['archivePrinciples']:blockers.append('Record Courteous passage in the shared archive first.')
    if state['sharedFunds']<IONA_ATLAS['costCrowns']:blockers.append('Needs 10 shared crowns.')
    for material,count in IONA_ATLAS['materials'].items():
        if state['materialInventory'][material]-state['materialReserveTargets'][material]<count:blockers.append('Needs '+str(count)+' unreserved '+g.MATERIALS[material]['name']+'.')
    return {**deepcopy(IONA_ATLAS),**deepcopy(project),'startBlockers':blockers,
        'working':project['status']=='in-progress' and g.character_at_castle(state,'iona') and g.character_assignment(state,'iona')=='personal-project'}


def apply(state,action):
    import game as g
    kind=action.get('type')
    if kind not in ('start-iona-atlas','resume-iona-atlas','cancel-iona-atlas'):return False
    g.require('iona' in g.household_members(state),'Iona must be a household member before agreeing this work.')
    g.require(all(g.character_at_castle(state,p) for p in ('founder','iona')),'Return home together to discuss her atlas.')
    project=state['additionalResidents']['iona']['personalProject']
    if kind=='start-iona-atlas':
        g.require(project['status']=='not-started','This atlas has already been funded or finished.')
        blockers=view(state)['startBlockers'];g.require(not blockers,' '.join(blockers))
        state['sharedFunds']-=IONA_ATLAS['costCrowns']
        for material,count in IONA_ATLAS['materials'].items():state['materialInventory'][material]-=count
        project.update(status='in-progress',completedWorkPhases=0,requiredWorkPhases=3,committedCrowns=IONA_ATLAS['costCrowns'],committedMaterials=deepcopy(IONA_ATLAS['materials']))
        g.set_character_assignment(state,'iona','personal-project')
        g.add_journal(state,'Iona agreed to make her atlas: 10 shared crowns, 2 binding thread and 1 porous clay committed. Three of her assigned work phases; other assignments pause.')
    elif kind=='resume-iona-atlas':
        g.require(project['status']=='in-progress','There is no unfinished atlas to resume.')
        g.set_character_assignment(state,'iona','personal-project')
    else:
        g.require(project['status']=='in-progress','Only an unfinished atlas can be cancelled and refunded.')
        state['sharedFunds']+=project['committedCrowns']
        for material,count in project['committedMaterials'].items():state['materialInventory'][material]+=count
        project.pop('committedCrowns');project.pop('committedMaterials')
        project.update(status='not-started',completedWorkPhases=0)
        if g.character_assignment(state,'iona')=='personal-project':g.set_character_assignment(state,'iona','rest')
        g.add_journal(state,'Iona put the unfinished atlas aside. Exact costs returned once; no advancement or knowledge was granted.')
    return True


def resolve(state,summary):
    import game as g
    if 'iona' not in g.household_members(state):return
    project=state['additionalResidents']['iona']['personalProject']
    if project['status']!='in-progress' or not g.character_at_castle(state,'iona') or g.character_assignment(state,'iona')!='personal-project':return
    import spell_support
    project['completedWorkPhases']+=1+spell_support.haste_extra(state,'iona',project['completedWorkPhases'],3,summary)
    summary.append('Iona’s crossing atlas: '+str(project['completedWorkPhases'])+' / 3 personal work phases.')
    if project['completedWorkPhases']==3:
        project['status']='complete';g.set_character_assignment(state,'iona','rest')
        g.learn_for_character(state,'iona','courteous-passage')
        g.award_advancement(state,'iona','crossing-atlas',2,'Completed her atlas of small crossings')
        summary.append('Iona finished her atlas, learned Courteous passage and earned 2 advancement points.')


def forecast(state):
    item=view(state)
    if not item or item['status']!='in-progress':return []
    return ['Iona’s crossing atlas: '+('+1 personal work phase.' if item['working'] else 'paused; resume her project to continue.')]
