"""Bounded assignment plans. They only run inside an explicit Advance."""
from copy import deepcopy


def saved(s): return s.get('householdRoutines', {})


def resume(s, who, project):
    import game as g, guidance, progression
    p=guidance.projects(s).get(project)
    g.require(p and p['personId']==who and len(p.get('participants',[who]))==1,
              'Choose this worker’s existing individual project. Group work needs its own review.')
    action=progression.resume_action(s,project)
    g.require(action,'Resume this project from its own screen; it does not support a routine.')
    before={w:g.character_assignment(s,w) for w in g.household_members(s) if w!=who}
    g.apply_action(s,action)
    g.require(all(g.character_assignment(s,w)==v for w,v in before.items()),'This project changes another person’s assignment. Resume it from its own screen.')


def apply(s,a):
    import game as g, guidance
    kind=a.get('type')
    if kind not in ('routine-start','routine-pause','routine-resume','routine-remove'): return False
    who=a.get('workerId')
    g.require(isinstance(who,str) and who in g.household_members(s),'Choose a household worker.')
    g.require(all(g.character_at_castle(s,w) for w in ('founder',who)),'Return home together to change this routine.')
    rows=s.setdefault('householdRoutines',{})
    if kind=='routine-start':
        mode=a.get('mode');night=a.get('restEvenings',True)
        g.require(mode in ('project','provisions') and type(night) is bool,'Choose a project or provision target and whether evenings are for rest.')
        fallback=a.get('afterProject') or None
        if fallback:
            g.require(isinstance(fallback,str),'Choose an existing project after gathering.')
            staged=deepcopy(s);resume(staged,who,fallback)
        r=dict(mode=mode,restEvenings=night,afterProject=fallback,status='active',reason='',sleeping=False)
        if mode=='project':
            project=a.get('projectId');g.require(isinstance(project,str),'Choose an existing funded project.')
            resume(s,who,project);r['projectId']=project;r['projectName']=guidance.projects(s)[project]['name']
            g.require(fallback!=project,'Choose a different follow-up project, or Rest.')
        else:
            target=a.get('target');assignment=a.get('assignment','forage')
            g.require(type(target) is int and s['provisions']['stock']<target<=1000,'Choose a provision target above current stock and at most 1,000.')
            g.require(assignment in ('hunt','forage'),'Choose hunting or foraging.')
            g.apply_action(s,dict(type='food-assign',characterId=who,assignment=assignment))
            r.update(target=target,assignment=assignment)
        r['expectedAssignment']=g.character_assignment(s,who);s.setdefault('householdRoutines',{})[who]=r
        g.add_journal(s,g.character_profile(s,who)['name']+' agreed a bounded routine. Evening rest: '+('yes' if night else 'no')+'. Only Advance carries it out.')
    else:
        g.require(who in rows,'Choose an existing routine.');r=rows[who]
        if kind=='routine-remove': del rows[who]
        elif kind=='routine-pause':
            r.update(status='paused',reason='Paused by you.',sleeping=False)
            g.set_character_assignment(s,who,'rest')
        else:
            g.require(r['status']!='complete','This routine is complete. Agree a new one.')
            if r['mode']=='project': resume(s,who,r['projectId'])
            else:
                g.require(s['provisions']['stock']<r['target'],'The provision target is already met. Remove this routine or agree a new one.')
                g.apply_action(s,dict(type='food-assign',characterId=who,assignment=r['assignment']))
            r=s['householdRoutines'][who]
            r.update(status='active',reason='',sleeping=False,expectedAssignment=g.character_assignment(s,who))
    return True


def before_advance(s):
    import game as g, guidance
    notes=[]
    for who in list(saved(s)):
        r=saved(s)[who]
        if r['status']!='active': continue
        if who not in g.household_members(s) or not g.character_at_castle(s,who):
            r.update(status='paused',reason='Away from home. Resume this routine after returning.',sleeping=False);continue
        if g.character_assignment(s,who)!=r['expectedAssignment']:
            r.update(status='paused',reason='The assignment changed. Your new assignment is kept.',sleeping=False);continue
        if r['mode']=='project':
            project=guidance.projects(s).get(r['projectId'])
            if project and project['name']!=r.get('projectName',project['name']):
                r.update(status='paused',reason='The project changed. Your new assignment is kept.',sleeping=False);continue
        if r['mode']=='provisions' and s['provisions']['stock']>=r['target']:
            g.set_character_assignment(s,who,'rest');r.update(stopping=True,sleeping=False,expectedAssignment='rest')
            notes.append('Routine: '+g.character_profile(s,who)['name']+' already has the agreed provision stock and rests this phase.')
            continue
        if r['restEvenings'] and s['currentDayPhase']=='evening':
            g.set_character_assignment(s,who,'rest');r.update(sleeping=True,expectedAssignment='rest')
            notes.append('Routine: '+g.character_profile(s,who)['name']+' rests tonight; unfinished work is kept.')
    return notes


def after_advance(s):
    import game as g, guidance
    notes=[]
    for who in list(saved(s)):
        r=saved(s)[who]
        if r['status']!='active': continue
        if not g.character_at_castle(s,who):
            r.update(status='paused',reason='Away from home. Resume after returning.');continue
        complete=(r['projectId'] not in guidance.projects(s)) if r['mode']=='project' else r.get('stopping',False) or s['provisions']['stock']>=r['target']
        name=g.character_profile(s,who)['name']
        if complete:
            g.set_character_assignment(s,who,'rest');r.update(status='complete',sleeping=False)
            note='Routine: '+name+' reached the agreed stopping point and is assigned to Rest.'
            if r['afterProject']:
                try:
                    staged=deepcopy(s);resume(staged,who,r['afterProject']);s.clear();s.update(staged)
                    r=s['householdRoutines'][who]
                    note='Routine: '+name+' reached the stopping point. The agreed follow-up project is assigned for the next Advance.'
                except g.RuleError as e:
                    r['reason']='Follow-up remains paused: '+str(e);note+=' '+r['reason']
            notes.append(note)
        elif r['sleeping']:
            try:
                staged=deepcopy(s)
                if r['mode']=='project':resume(staged,who,r['projectId'])
                else:g.apply_action(staged,dict(type='food-assign',characterId=who,assignment=r['assignment']))
                s.clear();s.update(staged)
                r=s['householdRoutines'][who]
                r.update(sleeping=False,expectedAssignment=g.character_assignment(s,who))
                notes.append('Routine: '+name+' has slept and resumes the agreed work next phase.')
            except g.RuleError as e:r.update(status='paused',reason=str(e),sleeping=False)
    s['lastPhaseSummary'].extend(notes)
    for line in notes:g.add_journal(s,line)


def view(s):
    import game as g, guidance, progression
    projects=guidance.projects(s)
    return dict(rows=[dict(workerId=w,name=g.character_profile(s,w)['name'],**deepcopy(r)) for w,r in saved(s).items() if w in g.household_members(s)],
        workers=[dict(id=w,name=g.character_profile(s,w)['name'],atHome=g.character_at_castle(s,w),
            projects=[dict(id=k,name=p['name']) for k,p in projects.items() if p['personId']==w and len(p.get('participants',[w]))==1 and progression.resume_action(s,k)]) for w in g.household_members(s)])
