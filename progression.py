"""Concrete, validated project resumption and affordable next improvements."""
from copy import deepcopy

def resume_action(s,key):
    import guidance
    p=guidance.projects(s).get(key)
    if not p:return None
    who=p['personId']
    if key=='resident-friendship':return {'type':'friendship-resume'}
    if key=='foundation-task':return {'type':'foundation-resume'}
    if key=='foundation-ritual':return {'type':'foundation-ritual-resume'}
    if key.startswith('equipment:'):return {'type':'gear-resume-job','workerId':who}
    if key=='commission':return {'type':'commission-resume'}
    if key.startswith('practical:'):return {'type':'practical-resume','characterId':who}
    if key=='bestiary-study':return {'type':'bestiary-resume'}
    if key=='castle-lamp':return {'type':'castle-lamp-resume'}
    if key=='house-shape':return {'type':'shape-resume','characterId':who}
    if key=='mystery':return {'type':'resume-mystery'}
    if key=='hearth':return {'type':'assign-founder','assignment':'research'}
    if key=='garden':return {'type':'assign-founder','assignment':'restoration'}
    if key=='craft':return {'type':'assign-character','characterId':who,'assignment':'crafting'}
    if key.startswith('research:'):return {'type':'focus-research','researchId':key.split(':',1)[1],'leaderId':who}
    if key.startswith('facility:'):return {'type':'assign-facility','facilityId':key.split(':',1)[1]}
    if key=='lasting-ritual':return {'type':'resume-lasting-ritual','ritualId':s['lastingRituals']['project']['id']}
    if key.startswith('spell-work:'):return {'type':'assign-character','characterId':who,'assignment':'spellwork'}
    if key=='headquarters' or key.startswith('headquarters:'):return {'type':'hq-resume','workerId':who}
    if key.startswith('housing:'):return {'type':'resume-housing','roomId':key.split(':',1)[1]}
    if key.startswith('training:'):
        if s['trainingProjects'][who].get('teacherId'):return {'type':'resume-lesson','learnerId':who}
        return {'type':'assign-character','characterId':who,'assignment':'training'}
    if key.startswith('focus:'):return {'type':'assign-character','characterId':who,'assignment':'inscribing'}
    if key.startswith('public:'):return {'type':'public-resume','ownerId':who}
    if key.startswith('story:'):return {'type':'resume-personal-story','storyId':key.split(':',1)[1]}
    if key=='shared-review':return {'type':'resume-shared-review'}
    if key=='local':return {'type':'resume-local-visit'}
    return None

def view(s,advance_preview=None):
    import game as g
    import guidance
    import headquarters as h
    preview=guidance.preview(s) if advance_preview is None else advance_preview
    forecast={p['id']:p for p in preview['projects']};projects=[]
    for key,p in guidance.projects(s).items():
        action=resume_action(s,key);blockers=[];impact=[]
        if action:
            try:
                staged=deepcopy(s);g.apply_action(staged,action)
                impact=[{'personId':who,'name':g.character_profile(s,who)['name'],'before':g.character_assignment(s,who),'after':g.character_assignment(staged,who)} for who in g.household_members(s) if g.character_assignment(s,who)!=g.character_assignment(staged,who)]
            except g.RuleError as error:blockers.append(str(error))
        projects.append({**p,'working':forecast.get(key,{}).get('progress',0)>0,'canResume':action is not None and not blockers,'blockers':blockers,'assignmentImpact':impact})
    upgrades=[]
    for key,d in h.ROOMS.items():
        if d['legacy'] or h.ready(s,key):continue
        affordable=s['sharedFunds']>=d['cost']
        test=deepcopy(s);test['sharedFunds']=max(test['sharedFunds'],d['cost'])
        if h.blockers(test,key):continue
        shortfall=max(0,d['cost']-s['sharedFunds']);income=g.copying_income(s)
        upgrades.append({'id':key,'name':d['name'],'cost':d['cost'],'phases':d['phases'],'benefit':d['benefit'],'affordable':affordable,'shortfall':shortfall,'copyingPhases':(shortfall+income-1)//income,'unlocks':[r['name'] for r in h.ROOMS.values() if key in r['needs']]})
    upgrades.sort(key=lambda r:(not r['affordable'],r['cost'],r['name']))
    return {'projects':projects,'upgrades':upgrades,'copyingIncome':g.copying_income(s)}

def apply(s,a):
    if a.get('type')!='resume-project':return False
    import game as g
    key=a.get('projectId');g.require(isinstance(key,str),'Choose a funded project.')
    action=resume_action(s,key);g.require(action is not None,'Open this project’s own controls to review its assignment.')
    g.apply_action(s,action)
    return True
