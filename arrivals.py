"""Ordinary introductions and constructed companions, separate from summoning."""
from copy import deepcopy
from character_pool import GOLEM_MATERIALS, arrival_method


def initialize(state):
    state.setdefault('golemProjects',{})
    import recruitment_quests
    recruitment_quests.initialize(state)


def candidate(state,who):
    import game as g
    g.require(isinstance(who,str) and who in {**state.get('reviewedCandidates',{}),**state.get('localEncounterCandidates',{})},'Choose a reviewed identity plan.')
    return {**state['reviewedCandidates'],**state.get('localEncounterCandidates',{})}[who]


def contact(state,who,origin):
    """Use the common visit/choice lifecycle only after a valid introduction."""
    import summoning
    key='introduced-'+who
    summoning.initialize_person(state,who,summoned=False)
    c=candidate(state,who)
    state['summoningContacts'][key]={'candidateId':who,'personId':who,'conductorId':None,'categoryId':c['categoryId'],
        'contactOrigin':origin,'contactStatus':'open','completedWorkPhases':0,'requiredWorkPhases':0,'committedCrowns':0,'committedMaterials':{},
        'discussedTopics':[],'conversation':[{'speaker':c['profile']['name'],'text':c['greeting'],'source':'reviewed-candidate'}]}
    return key


def eligible_rooms(state,profile):
    import game as g
    import estate_expansion
    who=profile['personId']
    return [key for key,row in g.housing_summary(state)['rooms'].items() if row['availableBeds']>0 and state['housingRooms'][key]['status']=='complete'
        and (profile.get('accommodationPreference')!='private-room' or g.HOUSING_ROOMS[key]['capacityBeds']==1)
        and not estate_expansion.placement_blockers(state,who,key)]


def blockers(state,who):
    import game as g
    c=candidate(state,who);p=c['profile'];reasons=[]
    if not g.character_at_castle(state,'founder'):reasons.append('Return home before planning this arrival.')
    if who in state['people']:reasons.append('This person already exists. Continue her saved contact; never create her again.')
    if arrival_method(p['ancestryLabel'])=='construction':
        if any(r['status']=='in-progress' for r in state['golemProjects'].values()):reasons.append('Finish or cancel the current construction first.')
        for principle in ('clear-instruction','gentle-preservation'):
            if principle not in g.character_principles(state,'founder'):reasons.append('Your scholar must have learned '+g.PRINCIPLE_NAMES[principle]+'.')
        d=p.get('constructionRules',GOLEM_MATERIALS[p.get('bodyMaterial','clay')])
        if state['sharedFunds']<d['costCrowns']:reasons.append('Needs '+str(d['costCrowns'])+' shared crowns.')
        for key,count in d['materials'].items():
            if state['materialInventory'][key]-state['materialReserveTargets'][key]<count:reasons.append('Needs '+str(count)+' unreserved '+g.MATERIALS[key]['name']+'.')
    return reasons


def view(state):
    import game as g
    rows={}
    for who,c in {**state.get('reviewedCandidates',{}),**state.get('localEncounterCandidates',{})}.items():
        profile=c['profile'];method=profile.get('arrivalMethod',arrival_method(profile['ancestryLabel']))
        if method=='summoning':continue
        project=deepcopy(state['golemProjects'].get(who))
        if project:project['working']=project['status']=='in-progress' and g.character_at_castle(state,'founder') and state['founderAssignment']=='awakening'
        rows[who]={'arrivalMethod':method,'startBlockers':blockers(state,who),'project':project,'eligibleRoomIds':eligible_rooms(state,profile),
            'body':deepcopy(profile.get('constructionRules',GOLEM_MATERIALS[profile.get('bodyMaterial','clay')])) if method=='construction' else None}
    return rows


def apply(state,action):
    kind=action.get('type')
    if kind not in ('open-correspondence','start-golem','resume-golem','cancel-golem','choose-golem-room'):return False
    import game as g
    who=action.get('characterId');c=candidate(state,who);profile=c['profile'];method=profile.get('arrivalMethod',arrival_method(profile['ancestryLabel']))
    g.require(g.character_at_castle(state,'founder'),'Return home before planning this arrival.')
    if kind=='open-correspondence':
        g.require(method=='recruitment','Ordinary introductions are for common ancestries; use the appropriate magical path for others.')
        g.require(who not in state['people'],'Continue this person’s existing correspondence.')
        import recruitment_quests
        g.require(not recruitment_quests.common(c),'Complete a rescue or a bandit recruitment quest before offering an invitation. Open the recruitment quest board.')
        contact(state,who,'ordinary-correspondence')
        return True
    g.require(method=='construction','Only a reviewed golem can use the construction ritual.')
    if kind=='start-golem':
        reasons=blockers(state,who);g.require(not reasons,' '.join(reasons))
        d=profile.get('constructionRules',GOLEM_MATERIALS[profile.get('bodyMaterial','clay')])
        state['sharedFunds']-=d['costCrowns']
        for key,count in d['materials'].items():state['materialInventory'][key]-=count
        state['golemProjects'][who]={'status':'in-progress','completedWorkPhases':0,'requiredWorkPhases':6,'bodyWorkPhases':4,
            'committedCrowns':d['costCrowns'],'committedMaterials':deepcopy(d['materials']),'roomId':None,'completedOn':None}
        state['founderAssignment']='awakening'
        g.add_journal(state,'Funded '+profile['name']+'’s adult golem body and animating focus. Four construction phases, then two awakening phases; no living person exists yet.')
    else:
        project=state['golemProjects'].get(who)
        g.require(project is not None and project['status']=='in-progress','Choose unfinished golem construction. Awakened people cannot be cancelled or rebuilt.')
        if kind=='resume-golem':state['founderAssignment']='awakening'
        elif kind=='choose-golem-room':
            room=action.get('roomId');g.require(isinstance(room,str) and room in eligible_rooms(state,profile),'Choose a suitable currently free room. Awakening checks its capacity again; this is not a reservation.')
            project['roomId']=room
        else:
            state['sharedFunds']+=project['committedCrowns']
            for key,count in project['committedMaterials'].items():state['materialInventory'][key]+=count
            project['status']='cancelled'
            if state['founderAssignment']=='awakening':state['founderAssignment']='rest'
            g.add_journal(state,'Cancelled an unawakened construction plan. Exact committed costs returned; no person was destroyed.')
    return True


def forecast(state):
    import game as g
    lines=[]
    for who,r in state['golemProjects'].items():
        if r['status']!='in-progress':continue
        working=g.character_at_castle(state,'founder') and state['founderAssignment']=='awakening'
        waiting=r['completedWorkPhases']==5 and r['roomId'] not in eligible_rooms(state,candidate(state,who)['profile'])
        lines.append(candidate(state,who)['profile']['name']+' · '+('waiting for suitable free accommodation.' if waiting else '+1 own construction / awakening phase.' if working else 'construction paused; progress kept.'))
    return lines


def resolve(state,summary):
    import game as g
    if not g.character_at_castle(state,'founder') or state['founderAssignment']!='awakening':return
    for who,r in state['golemProjects'].items():
        if r['status']!='in-progress':continue
        c=candidate(state,who);name=c['profile']['name']
        if r['completedWorkPhases']==5 and r['roomId'] not in eligible_rooms(state,c['profile']):
            summary.append(name+'’s awakening waits safely for an agreed suitable free bed. No extra costs or work were consumed.');return
        r['completedWorkPhases']+=1
        summary.append(name+': '+str(r['completedWorkPhases'])+' / 6 construction and awakening phases.')
        if r['completedWorkPhases']<6:return
        contact(state,who,'constructed-companion')
        when={'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']}
        r.update(status='complete',completedOn=deepcopy(when))
        state['people'][who]['awakenedOn']=deepcopy(when)
        state['bedroomAssignments'][who]=r['roomId']
        state['residency'][who].update(residencyStatus='visiting',agreedRoomId=r['roomId'],arrivals=[deepcopy(when)])
        state['additionalResidents'][who]['status']='visiting';state['founderAssignment']='rest'
        g.add_journal(state,name+' awakened as a fully adult person with her own preferences. Accommodation is provided; membership, work and romance remain separate choices.')
        summary.append(name+' is awake and accommodated as a guest. Discuss the household with her in People & arrivals.')
        return
