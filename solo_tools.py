"""Fresh solo beginnings and explicit, save-scoped testing tools."""
import json


def initialize_fresh(s):
    s.update(startType='fresh', campaignName='A beginning in the old stones', currentDayPhase='morning',
             sharedFunds=40, invitationStatus='unavailable', relationshipDescription='No companion met yet')
    s['bedroomAssignments'].pop('mira', None)
    s['roomFurnishings'].update({'common-room':'reading-table','library':'brass-lamp','bedchamber':'none'})
    s['journal']=[{'dayNumber':1,'phase':'morning','text':'You arrive alone with your notes, 40 crowns, two pieces of sun amber and two lengths of binding thread. A sleeping chamber, common room and library are usable. The old hearth wards offer a first practical question.'}]
    s['people']['founder']['identitySource']='solo-opening'
    s['soloLife']['characterSetup']={'profileSaved':False,'finished':False}
    s['soloLife']['arrival']={'choices':{},'completed':False,'skipped':False}
    import first_hearth
    first_hearth.initialize(s)


def apply(s, a):
    import game as g
    import public_workshop as w
    kind=a.get('type')
    if not isinstance(kind,str) or not kind.startswith('cheat-'):return False
    t=s['testing']
    if kind=='cheat-toggle':
        g.require(type(a.get('enabled')) is bool,'Choose whether testing tools are enabled.')
        t['enabled']=a['enabled']
        return True
    g.require(t['enabled'],'Open Cheats and enable cheats for this save first.')
    g.require(g.character_at_castle(s,'founder'),'Return home before using testing tools.')
    def quantity():
        q=a.get('quantity')
        g.require(type(q) is int and 1<=q<=10000,'Choose a whole quantity from 1 to 10,000.')
        return q
    if kind=='cheat-resource':
        key=a.get('resourceId');q=quantity()
        g.require(isinstance(key,str),'Choose a resource.')
        if key=='provisions':
            g.require(s['provisions']['stock']+q<=1000000,'Food stock cannot exceed 1,000,000.')
            s['provisions']['stock']+=q
        elif key in ('crowns','resonance'):
            field='sharedFunds' if key=='crowns' else 'resonancePoints'
            g.require(s[field]+q<=1000000,'The testing balance limit is 1,000,000.')
            s[field]+=q
        else:
            g.require(key in g.MATERIALS or key in w.records('material'),'Choose a known material.')
            inventory=w.stock(s,key)
            g.require(inventory.get(key,0)+q<=1000000,'The testing stock limit is 1,000,000.')
            inventory[key]=inventory.get(key,0)+q
        message=f'Added {q} {key}. Public materials still use their normal qualification rules.'
    elif kind in ('cheat-build','cheat-recruit','cheat-gear','cheat-advancement','cheat-heal','cheat-bestiary'):
        import cheat_tools
        message=cheat_tools.apply(s,a)
    elif kind=='cheat-object':
        key=a.get('recordId');who=a.get('ownerId','founder')
        w.actor(s,who)
        g.require(isinstance(key,str),'Choose an object.')
        if key in g.RECIPES:
            s['craftedArtifacts'][key]=s['craftedArtifacts'].get(key,0)+1
        else:
            r=w.definition(key);rule=w.rule_for(r)
            g.require(rule and rule['kind'] in ('artifact','equipment','furnishing'),'Choose a buildable artifact, furnishing or piece of equipment.')
            w.check_fit(s,r,who)
            g.require(len(s['publicWorkshop']['items'])<500,'The testing object limit is 500.')
            pid=w.number(s,'cheat-object')
            w.owned_object(s,{'recordId':key,'ownerId':who,'kind':rule['kind'],'id':pid},rule['kind'])
        message=f'Created {key} for {g.character_profile(s,who)["name"]}; installation and preparation remain separate.'
    elif kind=='cheat-knowledge':
        who=a.get('ownerId','founder');w.actor(s,who)
        key=a.get('principleId')
        g.require(isinstance(key,str) and key in g.PRINCIPLE_NAMES,'Choose a known principle.')
        known=g.character_principles(s,who)
        g.require(key not in known,'This person already knows that principle.')
        known.append(key)
        if key not in s['archivePrinciples']:s['archivePrinciples'].append(key)
        if who=='founder' and key=='steady-hearth-wards':
            s['researchStatus']='complete';s['researchCompletedPhases']=s['researchRequiredPhases']
            if s['founderAssignment']=='research':s['founderAssignment']='rest'
        message=f'Granted {key} to {g.character_profile(s,who)["name"]}.'
    elif kind=='cheat-character':
        import character_pool as pool
        import candidate_proposals as candidates
        import arrivals
        g.require(len(g.household_members(s))<51,'The household limit is 51 people, including your character.')
        ancestry=a.get('ancestry')
        g.require(isinstance(ancestry,str) and ancestry in pool.ANCESTRIES,'Choose an available ancestry.')
        seed=f'cheat-{t["nextNumber"]}'
        selection=pool.select(s,seed,{'ancestry':ancestry})
        proposal=pool.offline(s,selection,seed)
        proposal.update(accommodationPreference='separate-bed',stayPreference='open-to-staying')
        if a.get('name'):proposal['name']=a['name']
        proposal,_=candidates.validate_candidate(json.dumps(proposal),s)
        who='test-resident-'+str(t['nextNumber'])
        definition=candidates.approved_definition(proposal,who,'offline-testing',seed)
        definition['profile'].update(identitySource='testing-spawn',generationIngredients=selection)
        rooms=arrivals.eligible_rooms(s,definition['profile'])
        room=a.get('roomId') or (rooms[0] if rooms else None)
        g.require(isinstance(room,str) and room in rooms,'A free suitable bed is needed. Instantly restore a guest room first.')
        s['reviewedCandidates'][who]=definition
        arrivals.contact(s,who,'testing-spawn')
        s['additionalResidents'][who]['status']='resident'
        s['residency'][who].update(residencyStatus='resident',candidateStayDecision='wants-to-stay',householdStayDecision='invite-to-stay',agreedRoomId=room)
        s['residency'][who]['arrivals'].append({'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'source':'testing-spawn'})
        s['bedroomAssignments'][who]=room
        message=f'Spawned {proposal["name"]}, adult {ancestry}, in {g.HOUSING_ROOMS[room]["name"]}. Arrival costs and story prerequisites bypassed for testing.'
    else:raise g.RuleError('Unknown testing action.')
    t['used']=True;t['nextNumber']+=1
    t['history'].append({'day':s['dayNumber'],'phase':s['currentDayPhase'],'text':message})
    t['history']=t['history'][-100:]
    g.add_journal(s,'TESTING · '+message)
    return True
