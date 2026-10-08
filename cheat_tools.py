"""Current-system cheat actions. Called only inside the campaign transaction."""
from copy import deepcopy


def unique_ids():
    from household_chapter_content import PROFILES
    return tuple(PROFILES)


def view(s):
    import game as g, headquarters as h, armoury
    import local_encounters as local, summoning, containment
    names={**g.CHARACTERS,**{k:v['profile'] for k,v in summoning.CANDIDATES.items()},
           **{k:local.definition(s,k)['profile'] for k in local.PEOPLE},
           **{k:v['candidate']['profile'] for k,v in containment.CASES.items()}}
    return {'companions':[{'id':k,'name':names[k]['name'],'recruited':k in g.household_members(s)} for k in unique_ids()],
            'rooms':{**{k:d['name'] for k,d in g.HOUSING_ROOMS.items()},**{k:d['name'] for k,d in g.FACILITIES.items()},
                     **{k:d['name'] for k,d in h.ROOMS.items() if not d.get('legacy')},'conservatory':'Conservatory'},
            'gear':{k:d['name'] for k,d in armoury.CATALOG.items()}}


def build(s,key):
    import game as g, headquarters as h
    g.require(isinstance(key,str) and key in view(s)['rooms'],'Choose a listed room or facility.')
    if key=='conservatory':
        g.require(s['restorationStatus']!='complete','The conservatory is already restored.')
        s['restorationStatus']='complete';s['restorationCompletedPhases']=s['restorationRequiredPhases']
        if s['founderAssignment']=='restoration':s['founderAssignment']='rest'
    elif key in g.HOUSING_ROOMS:
        r=s['housingRooms'][key];g.require(r['status']!='complete','This bedroom is already restored.')
        r.update(status='complete',completedWorkPhases=g.HOUSING_ROOMS[key]['requiredWorkPhases'])
        if g.HOUSING_ROOMS[key].get('region')=='annex':s['estateAnnex'].update(status='complete',completedWorkPhases=s['estateAnnex']['requiredWorkPhases'])
        if s['activeHousingRoomId']==key:
            s['activeHousingRoomId']=None
            if s['founderAssignment']=='housing':s['founderAssignment']='rest'
    elif key in g.FACILITIES:
        r=s['facilityProjects'][key];g.require(r['status']!='complete','This facility is already complete.')
        r.update(status='complete',completedWorkPhases=g.FACILITIES[key]['requiredWorkPhases'])
        if s['activeFacilityId']==key:
            s['activeFacilityId']=None
            if s['founderAssignment']=='facilities':s['founderAssignment']='rest'
    else:
        g.require(not h.ready(s,key),'This room is already restored.')
        s['headquarters']['rooms'][key]='complete'
        for who,p in list(h.projects(s).items()):
            if p['kind']=='hq-build' and p['id']==key:
                h.put_project(s,who,None)
                if g.character_assignment(s,who)=='headquarters':g.set_character_assignment(s,who,'rest')
    return 'Completed '+view(s)['rooms'][key]+'. No time or new cost; any earlier construction payments remain spent.'


def recruit(s,selected):
    import game as g, summoning, local_encounters as local, containment, arrivals, armoury
    g.require(isinstance(selected,str) and selected in (*unique_ids(),'all'),'Choose a unique companion or all remaining companions.')
    targets=[k for k in unique_ids() if k not in g.household_members(s)] if selected=='all' else [selected]
    g.require(targets and all(k not in g.household_members(s) for k in targets),'These companions have already joined.')
    g.require(len(g.household_members(s))+len(targets)<=51,'The household limit is 51 people, including your character.')
    added=[];built=[]
    for who in targets:
        if who in summoning.CANDIDATES:s['reviewedCandidates'].setdefault(who,deepcopy(summoning.CANDIDATES[who]))
        if who in containment.CASES:
            s['reviewedCandidates'].setdefault(who,deepcopy(containment.CASES[who]['candidate']))
            p=s['containment']['project']
            if p and p['kind']=='care' and p['targetId']==who:containment.cancel(s)
            r=s['containment']['cases'][who]
            r.update(status='released',chamberId=None)
            r['history'].append('Cheat: case bypassed and companion recruited; no case reward granted.')
        if who in local.PEOPLE:
            s['localEncounterCandidates'].setdefault(who,local.definition(s,who))
            s['localEncounters'][who].update(status='introduced',completedOn={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']})
            if s.get('localVisit',{} ) and s['localVisit'].get('encounterId')==who:
                s['localVisit']=None
                if s['founderAssignment']=='local-visit':s['founderAssignment']='rest'
        if who not in ('mira','tamsin'):summoning.initialize_person(s,who,summoned=who in summoning.CANDIDATES)
        if who=='mira':
            # Mira's original character records exist even in a fresh solo save.
            # Membership must not convert that campaign into the demonstration.
            s['additionalResidents'].setdefault(who,{'status':'contacted','assignment':'rest','discussedTopics':[],'conversation':[],'wardrobe':{'outerLayer':'none'},'savedStyles':[],'completedScenes':[],'sharedFlirtation':False,'relationshipDescription':'Household colleagues; no romance established'})
            s['additionalResidents'][who].update(knownPrinciples=s['residentKnownPrinciples'][:],personalProject={'status':'not-offered','completedWorkPhases':0,'requiredWorkPhases':0})
        if who=='mira':
            if s['invitationStatus']=='unavailable':s['invitationStatus']='available'
            if s['relationshipDescription']=='No companion met yet':s['relationshipDescription']='Household companions; no romance established'
        profile=g.character_profile(s,who)
        for key,r in list(s['arrivalReservations'].items()):
            if r['personId']==who:del s['arrivalReservations'][key]
        if s.get('pendingResidentArrival',{}).get('characterId')==who:s['pendingResidentArrival']={}
        contacts=[r for r in s['summoningContacts'].values() if summoning.candidate_id(r)==who]
        for r in contacts:
            if r['contactStatus']=='preparing':
                s['sharedFunds']+=r.get('committedCrowns',0)
                for k,n in r.get('committedMaterials',{}).items():s['materialInventory'][k]+=n
                conductor=r.get('conductorId')
                if conductor and g.character_assignment(s,conductor)=='summoning':g.set_character_assignment(s,conductor,'rest')
                r.update(committedCrowns=0,committedMaterials={})
            r['contactStatus']='open';r['personId']=who
        if who not in ('mira','tamsin') and not contacts:arrivals.contact(s,who,'cheat-recruitment')
        existing=s['bedroomAssignments'].get(who)
        rooms=arrivals.eligible_rooms(s,profile)
        room=existing if existing and g.room_available(s,existing) else (rooms[0] if rooms else None)
        if room is None:
            # Restore only as much accommodation as this shortcut needs.
            for key,d in g.HOUSING_ROOMS.items():
                if s['housingRooms'][key]['status']=='complete' or d.get('region')=='annex':continue
                if profile.get('accommodationPreference')=='private-room' and d['capacityBeds']!=1:continue
                import estate_expansion
                if estate_expansion.placement_blockers(s,who,key):continue
                if s['housingRooms'][key]['reservedBeds']>=d['capacityBeds']:continue
                build(s,key);built.append(d['name']);rooms=arrivals.eligible_rooms(s,profile)
                if rooms:room=rooms[0];break
        g.require(room is not None,'No suitable bed can be added without displacing someone. Free a bed or restore an annex bedroom first.')
        s['additionalResidents'][who]['status']='resident'
        r=s['residency'].setdefault(who,{'arrivals':[],'departures':[]})
        r.update(residencyStatus='resident',candidateStayDecision='wants-to-stay',householdStayDecision='invite-to-stay',agreedRoomId=room)
        r['arrivals'].append({'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'source':'cheat-recruitment'})
        s['bedroomAssignments'][who]=room
        added.append(profile['name'])
    armoury.sync(s);armoury.review_starters(s)
    # Recruitment should not leave a full roster with an immediately empty pantry.
    import provisions
    s['provisions']['stock']=max(s['provisions']['stock'],7*provisions.need(s))
    return 'Recruited '+', '.join(added)+'. Starter equipment and at least seven days of food are ready. Quests, chapter progress and relationships are unchanged.'+(' Restored bedrooms: '+', '.join(built)+'.' if built else '')


def apply(s,a):
    import game as g,armoury
    kind=a['type']
    if kind=='cheat-bestiary':
        import bestiary
        return bestiary.reveal_all(s)
    if kind=='cheat-recruit':return recruit(s,a.get('characterId'))
    if kind=='cheat-build':return build(s,a.get('buildingId'))
    who=a.get('ownerId','founder')
    g.require(isinstance(who,str) and who in g.household_members(s),'Choose a current household member.')
    if kind=='cheat-gear':
        key=a.get('recordId');g.require(isinstance(key,str) and key in armoury.CATALOG,'Choose a listed equipment item.')
        g.require(len(s['armoury']['items'])<1000,'The equipment limit for cheats is 1,000 items.')
        item=armoury.make(s,key,who)
        return 'Added '+item['name']+' for '+g.character_profile(s,who)['name']+'. Equip and enchant it from Build → Loadout.'
    if kind=='cheat-advancement':
        n=a.get('quantity');g.require(type(n) is int and 1<=n<=10000,'Choose 1–10,000 advancement points.')
        g.award_advancement(s,who,'cheat:'+str(s['testing']['nextNumber']),n,'Cheat: advancement points')
        return 'Added '+str(n)+' advancement points for '+g.character_profile(s,who)['name']+'. Training still takes its listed phases.'
    if kind=='cheat-heal':
        import field_magic
        field_magic.initialize(s)
        s['fieldMagic']['vitality'][who]=6
        return 'Restored '+g.character_profile(s,who)['name']+' to 6 health.'
    raise g.RuleError('Unknown cheat action.')
