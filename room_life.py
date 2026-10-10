"""Read-only room presence and explanations of individual work."""

ACTIVITIES={'equipment-work':'Fitting or enchanting personal equipment','signature-fitting':'Reviewing a personal fitting','equipment-review':'Practising with the agreed field kit','house-shape':'Fitting an agreed household undertaking','household-story':'Making an agreed shared project','shared-review':'Comparing research notes','rest':'Taking personal time','research':'Studying hearth wards','archive':'Working on shared research','commissions':'Copying for income','crafting':'Making the active artifact','garden':'Tending the conservatory','headquarters':'Working on a headquarters project','facilities':'Restoring living facilities','restoration':'Restoring the conservatory','housing':'Fitting a bedroom','training':'Studying or training','teaching':'Giving an agreed lesson','inscribing':'Inscribing equipment','spellwork':'Practising a spell','personal-request':'Making a personal keepsake','public-project':'Working on an agreed project'}
ACTIVITIES.update({'resident-friendship':'Sharing an agreed friendship activity','foundation-work':'Investigating and restoring the foundation chamber','foundation-ritual':'Sharing an agreed private ritual'})
AMBIENCE={
    'foundation-chamber':('The inspection lamp lights the repaired channels beside the private bed.','The closed door keeps the chamber separate from the household corridors.','A hooded lamp lights the bedside table and the hearth-supply switch.'),
    'library':('Light reaches the reading desk; there is room for a new question.','The long table has space for letters, study and careful work.','The shelves recede into shadow around the reading lamps.'),
    'common-room':('The shared table waits for the day’s first conversations.','A chair by the hearth offers a pause between jobs.','The common room has room for a drink, a game or quiet company.'),
    'conservatory':('Pale light picks out the youngest leaves.','The growing benches make a green shelter from the stone corridors.','The glass holds the last light above the planting benches.'),
    'chapel':('Morning light settles on plain stone and timber.','A quiet bench stands apart from the busy passages.','The room offers quiet without asking for an explanation.'),
    'workshop':('Morning light reaches the workbench and its trays of fittings.','The bench offers space to make, mend and compare materials.','Tools can be put back within reach of tomorrow’s work.'),
    'smithy':('The hearth and bench are ready for practical metalwork.','The working space keeps hot metal apart from stored equipment.','Finished work has a place to cool before it reaches the armoury shelves.'),
    'enchanting-room':('The inscription bench waits for a carefully chosen tool.','A clear work surface leaves room for measured improvements.','Quiet light makes the fine marks easier to follow.'),
    'training-yard':('The yard offers space to practise without crowding the living rooms.','There is room for deliberate drills and a pause between them.','The practice space is clear for the next day.'),
    'warehouse':('Shelves and clear aisles make the day’s supplies easy to find.','There is a place to sort useful stock without filling the living rooms.','The stores wait in their labelled places until needed.'),
}

def location(s,who):
    import game as g
    import headquarters as h
    if not g.character_at_castle(s,who):return None
    assignment=g.character_assignment(s,who)
    if assignment=='resident-friendship':
        import resident_friendships
        job=resident_friendships.saved(s)['job']
        if job and who in job['participants']:return job['room']
    if assignment=='foundation-ritual':return 'foundation-chamber'
    if assignment=='foundation-work':
        import foundation_chamber as fc
        job=fc.saved(s)['job']
        return 'library' if job and job['stepId']=='instructions' else 'foundation-chamber'
    if assignment=='external-commission':
        import commissions
        job=commissions.saved(s)['job']
        if job and job['workerId']==who:return commissions.CATALOG[job['id']]['room'] or 'library'
    if assignment=='practical-project':
        import practical_projects
        if who in practical_projects.PROJECTS:return practical_projects.PROJECTS[who]['room']
    if assignment=='castle-lamp':return 'library'
    if assignment=='equipment-work':
        job=s.get('armoury',{}).get('jobs',{}).get(who)
        if job:return job['room']
    if assignment=='signature-fitting':
        import signature_equipment as se
        return se.ROOMS.get(who,'workshop')
    if assignment=='equipment-review':return 'training-yard'
    if assignment=='spellwork' and s.get('spellWork',{}).get(who):
        spell=g.spell_by_id(s,s['spellWork'][who]['spellId']);return g.SPELL_FORMS[spell['formId']]['roomId']
    if assignment=='house-shape':
        import house_shape
        key=house_shape.saved(s)['active']
        if key:return house_shape.PATHS[key]['room']
    if assignment=='headquarters':
        project=h.project_for(s,who)
        if project:return project['id'] if project['kind']=='hq-build' else h.JOBS[project['id']]['room']
    if assignment=='containment':return 'dungeons' if h.ready(s,'dungeons') else 'library'
    if assignment=='facilities':return {'service-wards':'living-quarters'}.get(s['activeFacilityId'],s['activeFacilityId']) or 'library'
    if assignment=='public-project':
        job=s.get('publicWorkshop',{}).get('jobs',{}).get(who)
        if job and job.get('roomId') in g.ROOMS:return job['roomId']
    if assignment=='household-story':
        import household_sagas
        key=household_sagas.saved(s)['active']
        if key:return household_sagas.content.STORIES[key]['room']
    if assignment=='housing':return s.get('activeHousingRoomId') or 'living-quarters'
    if assignment in ('garden','restoration'):return 'conservatory'
    preferred={'crafting':'workshop','inscribing':'enchanting-room'}.get(assignment)
    if preferred:return preferred if h.ready(s,preferred) else 'library'
    if assignment!='rest':return 'library'
    import character_customization
    chosen=character_customization.idle_room(s,who)
    if chosen:return chosen
    import living_stories
    routine=living_stories.routine(s,who)
    if routine:return routine
    return {'morning':'library','afternoon':'common-room','evening':s.get('bedroomAssignments',{}).get(who,'living-quarters')}[s['currentDayPhase']]

def work_view(s):
    import game as g
    import guidance
    projects=list(guidance.projects(s).values())
    rows=[]
    for who in g.household_members(s):
        skills=s.get('characterSkills',{}).get(who,{})
        assignment=g.character_assignment(s,who)
        work=[p for p in projects if p['personId']==who or who in p.get('participants',[]) or (p['id']=='research:'+str(s.get('activeResearchId')) and assignment==('research' if who=='founder' else 'archive'))]
        rows.append({'id':who,'name':g.character_profile(s,who)['name'],'atHome':g.character_at_castle(s,who),'assignment':assignment,
            'activity':ACTIVITIES.get(assignment,assignment.replace('-',' ').capitalize()),'roomId':location(s,who),
            'skills':[{'name':name.capitalize(),'rank':skills.get(name,0),'use':use} for name,use in [('scholarship','Each rank adds 1 to assigned shared research; personal lessons keep their own pace.'),('artifice','Each rank adds 1 to assigned artifact work; equipment inscriptions and spells keep their own pace.'),('fieldcraft','Rank 1 shortens ordinary surveys to one work phase; other survey aids do not stack.')]],
            'knownPrinciples':[g.PRINCIPLE_NAMES.get(p,p) for p in g.character_principles(s,who)],'projects':work})
    return rows

def view(s):
    import game as g
    import headquarters as h
    import summoning
    rows={};phase=('morning','afternoon','evening').index(s['currentDayPhase'])
    import living_stories
    people=summoning.present_people(s)
    for key,d in h.ROOMS.items():
        ready=h.ready(s,key)
        occupants=[{'id':who,'name':g.character_profile(s,who)['name'],'activity':ACTIVITIES.get(g.character_assignment(s,who),g.character_assignment(s,who).replace('-',' ').capitalize())} for who in people if location(s,who)==key]
        for person in occupants:
            import romance,companion_almanac
            person['ambient']=companion_almanac.ambient(s,person['id'])
            import household_sagas,party_journeys
            person['greeting']=romance.greeting(s,person['id'],party_journeys.greeting(s,person['id']) or household_sagas.greeting(s,person['id']) or living_stories.GREETINGS.get(person['id'])) if g.character_assignment(s,person['id'])=='rest' else None
        rows[key]={'ready':ready,'description':AMBIENCE.get(key,('The room is ready for the day’s use.','There is space here for useful work and a pause between tasks.','Lamplight softens the worn stone and timber.'))[phase] if ready else 'This space is awaiting restoration. Listed activities remain accessible through the castle’s existing work areas.',
            'occupants':occupants}
    return rows
