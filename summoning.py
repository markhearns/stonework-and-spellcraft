"""Authored Open Threshold prototype. No provider calls or generated identities."""
from copy import deepcopy

PERSON_ID = 'iona'
PROFILE = {
    'personId':PERSON_ID, 'name':'Iona', 'role':'Demon threshold surveyor · 23',
    'adultAgeYears':23, 'lifeStage':'adult', 'ancestryLabel':'Demon',
    'identityRevision':1, 'identitySource':'authored-summoning-sample',
    'appearanceDescription':'Clearly adult succubus with warm rose-toned skin, long near-black waves, amber eyes, two elegant dark horns, pointed ears and one slender spade-tipped tail. Naturally curvy, with an alluring knowing smile; a fitted burgundy waistcoat over a low-neck charcoal blouse, charcoal trousers, flat boots, map and leather satchel.',
    'startingPractices':['careful-assembly'],
    'ambition':'Make a practical atlas of small crossings and the homes on either side.',
    'accommodationPreference':'separate-bed',
    'origin':'A demon surveyor from the river towns beyond the threshold, with a home and colleagues beyond the castle.',
    'offeredAssignments':['rest','archive','crafting','training','inscribing','spellwork'],
}
TOPICS = {
    'intentions': {'label':'Ask about her work and travels', 'text':'“I map the little crossings people actually use. An elegant door is less interesting than one that opens reliably in the rain. Your library sounds like a good place to compare notes.”'},
    'home': {'label':'Discuss rooms, privacy and household life', 'text':'“A separate bed and somewhere for my field case will do; a shared chamber is fine. My notes stay mine. If I later choose to live here, I can offer archive study and careful making, but please ask before assigning work.”'},
    'visit': {'label':'Ask whether she would like to visit', 'text':'“Yes, I would like to see the place. A visit first, though. An open door is an introduction, not a promise to stay.”'},
}


PERSONAL_TOPICS = {
    'river-home': {'label':'The river towns beyond the threshold', 'text':'“The bridges are built for people with all sorts of inconvenient silhouettes. Horns, wings, extravagant hats. My favourite tea shop has a sign: mind the lintel, not your neighbour’s business.”'},
    'surveying': {'label':'What makes a good map?', 'text':'“A good map admits what it doesn’t know. Here be dragons is rather lazy if the dragon has a name and opening hours.” She taps a pencilled correction. “I prefer to ask.”'},
    'quiet-company': {'label':'Offer some quiet company', 'text':'Iona moves her papers aside. “Stay. I have a letter from the river towns and an argument about a ferry crossing. Which would you like to hear first?”'},
    'flirt': {'label':'Offer a playful compliment', 'text':'Iona meets your gaze, her smile slow and unmistakably amused. “I was wondering whether you admired the tailoring or its occupant.” She lets the question linger. “A little flirting is welcome. Let’s enjoy that without deciding where it has to lead.”'},
}


from summoned_cast import catalogue
CANDIDATES = catalogue(PROFILE, TOPICS, PERSONAL_TOPICS)

def candidate_catalogue(state):
    import containment
    return {**CANDIDATES,**state.get('reviewedCandidates',{}),**state.get('localEncounterCandidates',{}),**containment.introduced_candidates(state)}

def candidate_id(contact):
    return contact.get("candidateId", contact.get("personId") or "iona")

def initialize(state):
    state['summoningContacts'] = {}
    state['residency'] = {}
    state['nextSummoningContactNumber'] = 1
    state['researchProjects'].setdefault('courteous-passage',{'status':'not-started','completedWorkPhases':0,'contributors':[]})


def initialize_person(state, who='iona', summoned=True):
    import game as g
    candidate=candidate_catalogue(state)[who];profile=candidate['profile']
    validate_npc_profile(profile, summoned=summoned)
    if who in state['people']:return
    state['people'][who] = deepcopy(profile)
    g.initialize_character_records(state, who, candidate['principles'], candidate['focusName'])
    if who=='zahra':
        import zahra_identity
        zahra_identity.start_magic(state)
    if who=='iona':
        import resident_projects
        resident_projects.initialize(state)
    import companion_life
    companion_life.initialize(state)
    state['residency'][who] = {'residencyStatus':'remote','candidateStayDecision':'undecided',
        'householdStayDecision':'undecided','agreedRoomId':None,'arrivals':[],'departures':[]}


def present_people(state):
    import game as g
    return list(dict.fromkeys(g.present_household_members(state)+[
        who for who,record in state.get('residency',{}).items()
        if record['residencyStatus'] in ('visiting','resident','departure-agreed') and g.character_at_castle(state,who)]))


def preparation_blockers(state, conductor, candidate="iona"):
    import game as g
    blockers=[]
    if not isinstance(candidate,str) or candidate not in candidate_catalogue(state):return ['Choose an authored exotic contact.']
    from character_pool import arrival_method
    if candidate_catalogue(state)[candidate]['profile'].get('arrivalMethod',arrival_method(candidate_catalogue(state)[candidate]['profile']['ancestryLabel']))!='summoning':return ['Use ordinary correspondence or the golem workbench for this ancestry.']
    try:validate_npc_profile(candidate_catalogue(state)[candidate]['profile'], summoned=True)
    except ValueError as error:blockers.append(str(error))
    if conductor not in g.household_members(state):return ['Choose a household member as conductor.']
    if not g.character_at_castle(state,'founder') or not g.character_at_castle(state,conductor):blockers.append('Founder and conductor must be home to agree this working.')
    if 'courteous-passage' not in g.character_principles(state,conductor):blockers.append('The conductor must learn Courteous passage.')
    if state['sharedFunds']<12:blockers.append('The contact needs 12 shared crowns.')
    if any(c['contactStatus']!='cancelled' and candidate_id(c)==candidate for c in state['summoningContacts'].values()):blockers.append('This person already has an enduring contact. Reopen it rather than creating a duplicate.')
    if any(c['contactStatus']=='preparing' and c['conductorId']==conductor for c in state['summoningContacts'].values()):blockers.append('Finish or cancel this conductor’s existing preparation first.')
    return blockers


def departure_blockers(state,who):
    blockers=[]
    import headquarters
    if headquarters.project_for(state,who):blockers.append('Finish or cancel the funded headquarters job before ending residency.')
    from personal_stories import active_story
    if active_story(state,who):blockers.append('Finish or cancel the funded personal story before departure.')
    if state['additionalResidents'][who]['personalProject']['status']=='in-progress':
        blockers.append('Finish or cancel the committed professional project before departure.')
    import game as g
    if any(p['status']=='in-progress' and g.PERSONAL_REQUESTS[key]['ownerId']==who for key,p in state['personalRequests'].items()):
        blockers.append('Finish or cancel the funded personal request before departure.')
    if state['trainingProjects'][who] or state['focusProjects'][who] or state['spellWork'][who] or state['personalAugmentations'][who]['project']:
        blockers.append('Finish or cancel committed personal learning, equipment, spell or augmentation work before departure.')
    if state['craftingProject'] and state['craftingProject']['crafterId']==who:blockers.append('Finish the committed artifact before departure.')
    if any(p and p.get('teacherId')==who for p in state['trainingProjects'].values()):blockers.append('Finish or cancel agreed teaching before departure.')
    if any(o['crafterId']==who and o.get('delegation',{} ) and o['delegation']['status'] in ('active','paused') for o in state['workOrders']):blockers.append('Revoke or finish the delegated batch before departure.')
    plan=state['castingPlans'].get(who)
    if plan and plan['status'] in ('active','paused'):blockers.append('Cancel or finish the casting plan before departure.')
    return blockers


def view(state):
    import game as g
    contacts=[]
    for key,c in state['summoningContacts'].items():
        row=deepcopy(c);row['id']=key
        candidate=candidate_catalogue(state)[candidate_id(c)]
        row.update(candidateId=candidate_id(c),topics=deepcopy(candidate['topics']),personalTopics=deepcopy(candidate['personalTopics']),startingPrinciples=list(candidate['principles']))
        row['working']=c['contactStatus']=='preparing' and g.character_at_castle(state,c['conductorId']) and g.character_assignment(state,c['conductorId'])=='summoning'
        if c['personId']:
            who=c['personId'];row['profile']=deepcopy(state['people'][who]);row['residency']=deepcopy(state['residency'][who])
            row['eligibleRoomIds']=[room for room,data in g.housing_summary(state)['rooms'].items() if data['availableBeds']>0 and (state['people'][who]['accommodationPreference']!='private-room' or g.HOUSING_ROOMS[room]['capacityBeds']==1)]
            row['departureBlockers']=departure_blockers(state,who)
            row['outsideCareStatus']=state.get('containment',{}).get('cases',{}).get(who,{}).get('status')
        contacts.append(row)
    candidates={key:{'profile':deepcopy(c['profile']),'categoryName':c['categoryName'],'startingPrinciples':list(c['principles']),'preparationBlockers':{who:preparation_blockers(state,who,key) for who in g.household_members(state)}} for key,c in candidate_catalogue(state).items()}
    return {'candidates':candidates,'contacts':contacts,'topics':deepcopy(TOPICS),'personalTopics':deepcopy(PERSONAL_TOPICS),'preparationBlockers':{who:preparation_blockers(state,who) for who in g.household_members(state)}}


def apply(state,action):
    import game as g
    kind=action.get('type')
    if not isinstance(kind,str) or not kind.startswith('summoning-'):return False
    g.require(g.character_at_castle(state,'founder'),'Return home before discussing a contact or visit.')
    if kind=='summoning-prepare':
        who=action.get('conductorId');g.require(isinstance(who,str),'Choose a conductor.')
        candidate=action.get('candidateId','iona')
        blockers=preparation_blockers(state,who,candidate);g.require(not blockers,' '.join(blockers))
        materials=action.get('materials')
        g.require(isinstance(materials,list) and len(materials)==2 and all(isinstance(m,str) and m in g.MATERIALS for m in materials),'Choose a vessel and a binding component.')
        for material,prop in zip(materials,('vessel','binding')):g.require(prop in g.MATERIALS[material]['properties'],'Choose components with the listed properties.')
        committed={m:materials.count(m) for m in set(materials)}
        for m,count in committed.items():g.require(state['materialInventory'][m]-state['materialReserveTargets'][m]>=count,'Not enough unreserved '+g.MATERIALS[m]['name']+'.')
        state['sharedFunds']-=12
        for m,count in committed.items():state['materialInventory'][m]-=count
        contact_id='threshold-'+str(state['nextSummoningContactNumber']);state['nextSummoningContactNumber']+=1
        state['summoningContacts'][contact_id]={'conductorId':who,'candidateId':candidate,'categoryId':candidate_catalogue(state)[candidate]['categoryId'],'personId':None,
            'contactStatus':'preparing','completedWorkPhases':0,'requiredWorkPhases':2,'committedCrowns':12,
            'committedMaterials':committed,'discussedTopics':[],'conversation':[]}
        g.set_character_assignment(state,who,'summoning')
        g.add_journal(state,'Prepared the Open Threshold: 12 crowns and the chosen components committed. Two conductor phases; no person has arrived.')
        return True
    contact_id=action.get('contactId')
    g.require(isinstance(contact_id,str) and contact_id in state['summoningContacts'],'Choose an existing contact.')
    c=state['summoningContacts'][contact_id];who=c['personId'];status=c['contactStatus']
    if c.get('contactOrigin')=='outside-encounter':
        g.require(state['containment']['cases'][who]['status']=='released','Ordinary contact, visits and recruitment become available only after unconditional release. Specialist transfer does not imply recruitment.')
    if kind in ('summoning-resume','summoning-cancel'):
        g.require(status=='preparing','Only unfinished preparation can be resumed or refunded.')
        if kind=='summoning-resume':
            g.require(g.character_at_castle(state,c['conductorId']),'The conductor must be home.')
            g.set_character_assignment(state,c['conductorId'],'summoning')
        else:
            state['sharedFunds']+=c['committedCrowns']
            for m,count in c['committedMaterials'].items():state['materialInventory'][m]+=count
            c['contactStatus']='cancelled'
            if g.character_assignment(state,c['conductorId'])=='summoning':g.set_character_assignment(state,c['conductorId'],'rest')
            g.add_journal(state,'Cancelled unfinished threshold preparation. Exact committed crowns and components returned once.')
        return True
    g.require(who is not None,'Finish the contact preparation first.')
    candidate=candidate_catalogue(state)[who];topics=candidate['topics'];personal_topics=candidate['personalTopics'];name=state['people'][who]['name']
    residence=state['residency'][who];rs=residence['residencyStatus']
    if kind=='summoning-close':
        g.require(status=='open' and rs in ('remote','away'),'Only a remote contact without an agreed visit can be closed.')
        c['contactStatus']='closed'
    elif kind=='summoning-reopen':
        g.require(status=='closed','This contact is already open.')
        c['contactStatus']='open'
    else:
        g.require(status=='open','Reopen the existing contact first.')
        if kind in ('summoning-personal-talk','summoning-personal-line'):
            g.require(rs in ('visiting','resident','departure-agreed'),'Meet in person during a visit or household stay.')
            g.require(g.character_at_castle(state,who),name+' must be at home for this conversation.')
            lines=state['additionalResidents'][who]['conversation']
            if kind=='summoning-personal-talk':
                topic=action.get('topic')
                g.require(isinstance(topic,str) and topic in personal_topics,'Choose an offered personal conversation.')
                lines.append({'speaker':state['people'][who]['name'],'text':personal_topics[topic]['text'],'source':candidate.get('textSource','authored'),'topicId':topic})
            else:
                lines.append({'speaker':'You','text':g.text_value(action.get('text'))})
            del lines[:-60]
        elif kind=='summoning-talk':
            topic=action.get('topic');g.require(isinstance(topic,str) and topic in topics,'Choose a conversation topic.')
            if topic not in c['discussedTopics']:
                c['discussedTopics'].append(topic);c['conversation'].append({'speaker':name,'text':topics[topic]['text'],'source':candidate.get('textSource','authored')})
        elif kind in ('summoning-invite','summoning-move-arrival'):
            g.require(rs in (('remote','away') if kind=='summoning-invite' else ('arrival-agreed',)),'Choose a remote contact or pending arrival.')
            g.require(all(topic in c['discussedTopics'] for topic in topics),'Discuss intentions, household life and the visit first.')
            room=action.get('roomId');g.reserve_arrival(state,who,room,'summoning',contact_id)
            residence.update(residencyStatus='arrival-agreed',agreedRoomId=room,candidateStayDecision='undecided',householdStayDecision='undecided')
            c['conversation'].append({'speaker':name,'text':'“Yes, that bed suits me. I will cross next phase, as a visitor.”','source':candidate.get('textSource','authored')})
        elif kind=='summoning-cancel-arrival':
            g.require(rs=='arrival-agreed','No pending visit to withdraw.')
            state['arrivalReservations'].pop('arrival:'+who,None)
            residence.update(residencyStatus='remote',agreedRoomId=None)
        elif kind=='summoning-ask-stay':
            g.require(rs=='visiting','Discuss staying during a visit.')
            if residence['candidateStayDecision']=='undecided':
                residence['candidateStayDecision']=candidate.get('stayDecision','wants-to-stay')
                c['conversation'].append({'speaker':name,'text':candidate['stayText'],'source':candidate.get('textSource','authored')})
            maybe_join(state,who)
        elif kind=='summoning-household-decision':
            g.require(rs=='visiting','Make the household decision during a visit.')
            decision=action.get('decision');g.require(decision in ('invite-to-stay','do-not-invite','undecided'),'Choose a household decision.')
            residence['householdStayDecision']=decision;maybe_join(state,who)
        elif kind=='summoning-depart':
            g.require(rs in ('visiting','resident'),'Only a present visitor or resident can agree departure.')
            blockers=departure_blockers(state,who);g.require(not blockers,' '.join(blockers))
            residence['residencyStatus']='departure-agreed'
            state['additionalResidents'][who]['status']='departure-agreed'
            g.set_character_assignment(state,who,'rest')
            c['conversation'].append({'speaker':name,'text':candidate['departureText'],'source':candidate.get('textSource','authored')})
        else:raise g.RuleError('Unknown summoning action.')
    return True


def maybe_join(state,who):
    import game as g
    r=state['residency'][who]
    if r['candidateStayDecision']=='wants-to-stay' and r['householdStayDecision']=='invite-to-stay':
        r['residencyStatus']='resident';state['additionalResidents'][who]['status']='resident'
        g.set_character_assignment(state,who,'rest')
        g.add_journal(state,state['people'][who]['name']+' and the household both agreed that she would stay. Her existing identity and belongings are kept; no work, allowance or romance was assigned.')


def forecast(state):
    import game as g
    rows=[]
    for c in state.get('summoningContacts',{}).values():
        if c['contactStatus']=='preparing':
            working=g.character_at_castle(state,c['conductorId']) and g.character_assignment(state,c['conductorId'])=='summoning'
            rows.append('Open Threshold · '+candidate_catalogue(state)[candidate_id(c)]['profile']['name']+': '+('+1 conductor phase.' if working else 'paused; resume the conductor’s assignment.'))
    for who,r in state.get('residency',{}).items():
        if r['residencyStatus']=='arrival-agreed':
            blockers=g.arrival_blockers(state,'arrival:'+who)
            rows.append(state['people'][who]['name']+'’s visit: '+(' '.join(blockers) if blockers else 'arrives next Advance; no work starts.'))
        if r['residencyStatus']=='departure-agreed':rows.append(state['people'][who]['name']+' departs next Advance; her identity and possessions are kept.')
    return rows


def resolve_work(state,summary):
    import game as g
    for c in state['summoningContacts'].values():
        if c['contactStatus']!='preparing' or not g.character_at_castle(state,c['conductorId']) or g.character_assignment(state,c['conductorId'])!='summoning':continue
        import lasting_rituals
        c['completedWorkPhases']=min(2,c['completedWorkPhases']+1+int(lasting_rituals.active(state,'welcome-circle')))
        summary.append('Open Threshold · '+candidate_catalogue(state)[candidate_id(c)]['profile']['name']+' preparation: '+str(c['completedWorkPhases'])+' / 2 conductor phases.')
        if c['completedWorkPhases']==2:
            who=candidate_id(c);candidate=candidate_catalogue(state)[who];name=candidate['profile']['name']
            initialize_person(state,who);c['personId']=who;c['contactStatus']='open'
            c['conversation'].append({'speaker':name,'text':candidate['greeting'],'source':candidate.get('textSource','authored')})
            g.set_character_assignment(state,c['conductorId'],'rest')
            summary.append('The Open Threshold reaches '+name+'. A conversation is available under Summoning; no visit has been agreed.')


def resolve_visits(state):
    import game as g
    for who,r in state['residency'].items():
        if r['residencyStatus']=='arrival-agreed':
            blockers=g.arrival_blockers(state,'arrival:'+who)
            if blockers:
                state['lastPhaseSummary'].append(state['people'][who]['name']+'’s arrival waits: '+' '.join(blockers));continue
            reservation=state['arrivalReservations'].pop('arrival:'+who)
            state['bedroomAssignments'][who]=reservation['roomId']
            r['agreedRoomId']=reservation['roomId'];r['residencyStatus']='visiting'
            r['arrivals'].append({'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
            state['additionalResidents'][who]['status']='visiting'
            text=state['people'][who]['name']+' arrived as a visitor. Her bed is occupied, but she has no household assignment or automatic allowance.'
        elif r['residencyStatus']=='departure-agreed':
            state['bedroomAssignments'].pop(who,None);r['agreedRoomId']=None;r['residencyStatus']='away'
            r['departures'].append({'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
            state['additionalResidents'][who]['status']='away';state['householdAllowancePlan']['dailyCrowns'][who]=0
            text=state['people'][who]['name']+' departed with her belongings. The bed is free; her identity, learning and correspondence remain saved.'
        else:continue
        state['lastPhaseSummary'].append(text);g.add_journal(state,text)


EXOTIC_ANCESTRIES = frozenset({'demon','seraph','elemental','vampire','fae','djinn','dragonkin','spirit','dryad','nymph','kitsune'})

def validate_npc_profile(profile, summoned=False):
    """Authored identity gate; the player character is outside this NPC policy."""
    age=profile.get('adultAgeYears')
    if type(age) is not int or not 18 <= age <= 25:
        raise ValueError('NPCs must be clearly adult and aged 18–25.')
    if profile.get('lifeStage') != 'adult':
        raise ValueError('NPC life stage must be adult.')
    if summoned and str(profile.get('ancestryLabel','')).lower() not in EXOTIC_ANCESTRIES:
        raise ValueError('Summoned NPCs must have an approved exotic ancestry.')
