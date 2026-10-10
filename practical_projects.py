"""Three resident-led improvements whose effects use existing patrol rewards and defenses."""
from copy import deepcopy

PROJECTS = {
    'iona': dict(name='Mark safe routes in Iona’s atlas', room='command-room', cost=10,
        inputs={'binding-thread': 1}, phases=3,
        opening='Iona spreads her finished atlas across the map table. “The main road is obvious. I want to mark the tracks a laden cart can actually use. Give me three work phases and I can add reliable detours.”',
        effect='On an objective patrol with Iona, bypass one enemy after clearing the site obstacle. Earn the objective payment on completion; the bypass grants no enemy loot or enemy-type advancement.'),
    'zahra': dict(name='Make Zahra’s field-fitting gauges', room='smithy', cost=10,
        inputs={'binding-thread': 1, 'porous-clay': 1}, phases=3,
        opening='Zahra lays a twisted strap on her bench. “It held, but it pulled the coat sideways. I can make gauges that let me fit everyone’s straps before we leave. Three work phases.”',
        effect='When Zahra joins a field patrol, every conscious party member gains 1 personal cover against the first enemy attack in each encounter.'),
    'sylva': dict(name='Plant Sylva’s field-specimen beds', room='conservatory', cost=10,
        inputs={'silver-ivy': 1, 'porous-clay': 1}, phases=3,
        opening='Sylva sets three cuttings in separate clay pots. “These roots need different soil. Build me a divided bed and I can grow useful ivy from the specimens we bring home.”',
        effect='Each completed creature-observation or crossing-repair patrol brings home 2 additional silver ivy. Sylva must still live here and the conservatory must be available.'),
}


def saved(s): return s.get('practicalProjects', {})


def active(s, who):
    import game as g, headquarters as h
    return bool(saved(s).get(who, {}).get('completedOn') and who in g.household_members(s) and h.ready(s, PROJECTS[who]['room']))


def blockers(s, who):
    import game as g, headquarters as h
    if who not in PROJECTS: return ['Choose a listed companion project.']
    d = PROJECTS[who]; b = []
    if who not in g.household_members(s): b.append('Invite this companion to join the household first.')
    elif not all(g.character_at_castle(s,w) for w in ('founder',who)): b.append('Return home together to discuss the project.')
    if not h.ready(s,d['room']): b.append('Restore the '+(h.ROOMS.get(d['room']) or g.ROOMS[d['room']])['name']+'.')
    if who == 'iona' and s.get('additionalResidents',{}).get('iona',{}).get('personalProject',{}).get('status') != 'complete': b.append('Complete Iona’s crossing atlas first.')
    if who == 'zahra' and not ('journey:field-patrol:zahra:complete' in s.get('companionParticipation',{}).get('events',{}) or any('zahra' in r['party'] and r['complete'] for r in s.get('fieldPatrols',{}).get('reports',[]))):
        b.append('Return from a completed field patrol with Zahra before discussing the fitting problem.')
    if who == 'sylva' and not (g.discoveries_for(s,'fern-nursery') or s.get('fieldObjectiveHistory',{}).get('observe')):
        b.append('Bring home a fern-nursery discovery or complete a creature-observation patrol.')
    if who in saved(s): b.append('This project is already funded or complete.')
    if s['sharedFunds'] < d['cost']: b.append('Needs '+str(d['cost'])+' shared crowns.')
    for k,n in d['inputs'].items():
        if s['materialInventory'].get(k,0)-s['materialReserveTargets'].get(k,0) < n: b.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
    return b


def apply(s,a):
    import game as g
    kind = a.get('type')
    if kind not in ('practical-start','practical-resume','practical-cancel'): return False
    who=a.get('characterId'); g.require(isinstance(who,str) and who in PROJECTS,'Choose a listed companion project.')
    d=PROJECTS[who]
    g.require(who in g.household_members(s) and all(g.character_at_castle(s,w) for w in ('founder',who)), 'Return home together to agree the work.')
    if kind=='practical-start':
        b=blockers(s,who); g.require(not b,' '.join(b))
        s['sharedFunds']-=d['cost']
        for k,n in d['inputs'].items(): s['materialInventory'][k]-=n
        s.setdefault('practicalProjects',{})[who]=dict(done=0,completedOn=None,cost=d['cost'],inputs=deepcopy(d['inputs']))
        g.set_character_assignment(s,who,'practical-project')
        g.add_journal(s,d['opening']+' Agreed cost: '+str(d['cost'])+' crowns and the listed materials.')
    else:
        r=saved(s).get(who);g.require(r and not r['completedOn'],'Choose an unfinished practical project.')
        if kind=='practical-resume': g.set_character_assignment(s,who,'practical-project')
        else:
            s['sharedFunds']+=r['cost']
            for k,n in r['inputs'].items(): s['materialInventory'][k]+=n
            del s['practicalProjects'][who]
            if g.character_assignment(s,who)=='practical-project': g.set_character_assignment(s,who,'rest')
    return True


def resolve(s,summary,assignments):
    import game as g, signature_growth, shared_history
    for who,r in saved(s).items():
        if r['completedOn'] or assignments.get(who)!='practical-project': continue
        d=PROJECTS[who];r['done']+=1
        summary.append(d['name']+': '+str(r['done'])+'/'+str(d['phases'])+' work phases.')
        if r['done']<d['phases']: continue
        r['completedOn']=dict(day=s['dayNumber'],phase=s['currentDayPhase'])
        signature_growth.record_work(s,who,'household-improvement')
        shared_history.record(s,'project:'+who,[who],d['name'],d['effect'],'work')
        g.set_character_assignment(s,who,'rest');summary.append('Completed: '+d['effect'])


def view(s):
    import game as g
    return [dict(id=w,**deepcopy(d),progress=deepcopy(saved(s).get(w)),active=active(s,w),
        working=g.character_at_castle(s,w) and g.character_assignment(s,w)=='practical-project' if w in g.household_members(s) else False,
        blockers=blockers(s,w)) for w,d in PROJECTS.items()]
