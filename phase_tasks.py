"""Current, rules-checked tasks. Suggestions do not themselves change the campaign."""
from copy import deepcopy


def phase_key(s):return f"{s['dayNumber']}:{s['currentDayPhase']}"


def build(s):
    import game as g
    import solo_life
    import public_workshop as w
    import local_encounters
    rows=[]
    def add(key,title,detail,view,action=None,group='opportunity',person=None):
        if action:
            # Use the authoritative rules, on a detached state. No provider calls,
            # Advance actions, uploads or generation are proposed by this module.
            try:g.apply_action(deepcopy(s),action)
            except g.RuleError:return
        row={'id':key,'title':title,'detail':detail,'view':view,'group':group,'personId':person}
        if action:row['action']=action
        rows.append(row)
    def resume(who,assignment,title,view):
        if g.character_assignment(s,who)==assignment:return
        current=g.character_assignment(s,who)
        add('resume:'+who+':'+assignment,'Resume '+title,
            g.character_profile(s,who)['name']+' is currently assigned to '+current+'. Switching preserves other project progress; work happens on Advance.',
            view,{'type':'assign-character','characterId':who,'assignment':assignment},'work',who)
    import field_patrols
    patrol=field_patrols.saved(s)['active']
    if patrol:add('field-patrol',patrol['name'],field_patrols.forecast(s)[0],'fieldPatrols',group='choice' if patrol['stage'] in ('decision','site-decision') else 'work')
    e=s['expedition']
    if e:
        if e['stage']=='awaiting-choice':
            for key,d in g.EXPEDITION_SITES[e['siteId']]['approaches'].items():
                add('field-choice:'+key,d['name'],'Choose the next field activity. '+d['reward'],'expeditions',{'type':'choose-expedition-approach','approach':key},'choice')
        elif e['stage']=='encounter-choice':add('field-encounter','Choose the next field method','The party is waiting for your choice before work can continue.','expeditions',group='choice')
        if e['stage']=='ready-to-return':add('field-return','Bring the discoveries home','Begin the return journey; arrival and rewards resolve on the next Advance.','expeditions',{'type':'return-expedition'},'choice')
    trip=s['publicWorkshop'].get('fieldTrip')
    if trip and trip['stage'] in ('awaiting-choice','ready-to-return'):
        add('public-field-choice','Choose a field lead or return','Review the observed context and choose an activity for this party.','publicWorkshop',group='choice')
    if g.character_at_castle(s,'founder'):
        import house_shape
        key=house_shape.saved(s)['active'];r=house_shape.record(s,key) if key else None
        if r and r['project'] and r['project']['status']=='in-progress':
            for who in r['workers']:
                if who in g.household_members(s) and who not in house_shape.eligible(s):add('resume:shape:'+who,'Resume '+house_shape.PATHS[key]['title'],g.character_profile(s,who)['name']+' can resume their agreed work. Other funded work stays paused.','houseShape',{'type':'shape-resume','characterId':who},'work',who)
        import armoury
        for who,job in armoury.state(s)['jobs'].items():
            if not armoury.working(s,who):add('resume:equipment:'+who,'Resume '+job['name'],'Committed costs and progress are retained.','armoury',{'type':'gear-resume-job','workerId':who},'work',who)
        import headquarters
        for who,hp in headquarters.projects(s).items():
            if not headquarters.working(s,who):add('resume:headquarters'+('' if who=='founder' else ':'+who),'Resume '+hp['name']+' · '+g.character_profile(s,who)['name'],'Committed costs and progress are kept.','headquarters',{'type':'hq-resume','workerId':who},'work',who)
        if s['researchStatus']=='not-started':add('hearth-study','Study the hearth wards','20 crowns · 3 assigned work phases. Starts your scholar’s research.','research',{'type':'start-research'})
        if s['researchStatus']=='in-progress':resume('founder','research','hearth research','research')
        if s['craftingProject']:
            p=s['craftingProject'];resume(p['crafterId'],'crafting',g.RECIPES[p['recipeId']]['name'],'workshop')
        elif not s['craftedArtifacts'].get('warming-lantern') and not s['characterDevelopment']['founder']['advancementAwards'].get('artifact:warming-lantern'):
            add('first-lantern','Make a warming lantern','Uses 1 sun amber + 1 binding thread · 2 work phases. Starts your scholar’s crafting.','workshop',{'type':'start-crafting','recipeId':'warming-lantern','materials':['sun-amber','binding-thread'],'crafterId':'founder'})
        if s['restorationStatus']=='in-progress':resume('founder','restoration','conservatory restoration','restoration')
        if s['activeHousingRoomId']:resume('founder','housing','guest-room restoration','housing')
        if s['activeFacilityId']:resume('founder','facilities','living-wing work','ledger')
        if s['localVisit']:add('resume-local','Resume the local introduction','Use your scholar’s next assigned phase to continue this appointment.','localEncounters',{'type':'resume-local-visit'},'work') if s['founderAssignment']!='local-visit' else None
        for who in g.household_members(s):
            if s['trainingProjects'].get(who):resume(who,'training','personal learning','development')
            if s['focusProjects'].get(who):resume(who,'inscribing','focus inscription','focus')
            p=s['publicWorkshop']['jobs'].get(who)
            if p and g.character_assignment(s,who)!='public-project':
                add('resume-public:'+who,'Resume '+p['name'],'Restores this person’s project assignment. Other prerequisites still apply.','publicWorkshop',{'type':'public-resume','ownerId':who},'work',who)
        if s['founderAssignment']=='rest':add('copying','Earn crowns by copying records',str(g.copying_income(s))+' crowns per assigned phase. Assign now; Advance performs the work.','ledger',{'type':'assign-founder','assignment':'commissions'})
        for key,r in local_encounters.view(s)['encounters'].items():
            if r['canStart']:add('meet:'+key,'Meet '+r['name'],r['lead']+' Uses one assigned phase.','localEncounters',{'type':'start-local-visit','encounterId':key},person=key)
        if s['researchStatus']=='complete':
            if s['restorationStatus']=='not-started':add('restore-garden','Restore the conservatory','25 crowns · 3 assigned phases. Opens material or surplus production.','restoration',{'type':'start-restoration'})
            for key,d in g.FACILITIES.items():
                if s['facilityProjects'][key]['status']=='not-started':add('facility:'+key,'Build '+d['name'],str(d['costCrowns'])+' crowns · '+str(d['requiredWorkPhases'])+' assigned phases.','ledger',{'type':'start-facility','facilityId':key})
        if s['researchStatus']=='complete':
            for key,d in g.RESEARCH_CATALOG.items():
                status=s['researchProjects'][key]['status']
                if status!='complete' and not (s['activeResearchId']==key and s['founderAssignment']=='research'):
                    add('research:'+key,('Resume ' if status=='in-progress' else 'Research ')+d['name'],
                        ('Costs already committed. ' if status=='in-progress' else str(d['costCrowns'])+' crowns. ')+str(d['requiredWorkPhases'])+' base work phases; assigns your scholar.',
                        'research',{'type':'focus-research','researchId':key,'leaderId':'founder'},'work' if status=='in-progress' else 'opportunity')
        if not s['lanternDisplayed']:add('install:lantern','Display your warming lantern','Place an available crafted lantern in the common room. No phase cost.','castle',{'type':'display-lantern','displayed':True},'ready')
        if not s['libraryIndexInstalled']:add('install:index','Install a living index charm','Use your crafted charm to support archive work. No phase cost.','research',{'type':'install-index-charm','installed':True},'ready')
        if not s['wateringCharmInstalled']:add('install:watering','Install a self-watering charm','Use your crafted charm in the restored conservatory.','restoration',{'type':'install-watering-charm','installed':True},'ready')
        for key,installed in s['householdArtifactPlacements'].items():
            if not installed:add('install:'+key,'Install '+g.RECIPES[key]['name'],'Places the crafted artifact in its restored facility. No phase cost.','ledger',{'type':'place-household-artifact','artifactId':key,'installed':True},'ready')
        for key,installed in s['utilityArtifactPlacements'].items():
            if not installed:add('install:'+key,'Install '+g.RECIPES[key]['name'],'Uses an available crafted artifact in its appropriate room. No phase cost.','workshop',{'type':'place-utility-artifact','artifactId':key,'installed':True},'ready')
        for key,r in s['housingRooms'].items():
            if r['status']=='not-started' and key in ('west-chamber','garden-chamber'):
                d=g.HOUSING_ROOMS[key]
                add('housing:'+key,'Restore '+d['name'],str(d['costCrowns'])+' crowns · '+str(d['requiredWorkPhases'])+' assigned phases.','housing',{'type':'fund-housing','roomId':key})
        for who in g.household_members(s):
            if s['spellWork'].get(who):resume(who,'spellwork','spell work','spells')
        import personal_stories
        for key,r in personal_stories.view(s)['stories'].items():
            if r['canJoin']:add('story:'+key,r['proposal']['title'],'Completed personal work has opened an optional scene.','stories',group='invitation',person=r['ownerId'])
            elif r['status']=='in-progress' and not r['working']:
                add('resume-story:'+key,'Resume '+r['proposal']['title'],'Continue the owner’s agreed personal project.','stories',{'type':'resume-personal-story','storyId':key},'work',r['ownerId'])
        for key,c in s['summoningContacts'].items():
            who=c.get('personId')
            if c['contactStatus']=='open' and who and s['residency'][who]['residencyStatus']=='remote':
                add('contact:'+who,'A conversation with '+g.character_profile(s,who)['name'],'Review the introduction and discuss whether a visit would suit you both.','summoning',group='ready',person=who)
        # Surface newly completed public-pack work without flooding each phase
        # with every old owned object. Full history remains in the workshop.
        index=g.DAY_PHASES.index(s['currentDayPhase'])
        previous_day=s['dayNumber']-(1 if index==0 else 0)
        previous_phase=g.DAY_PHASES[(index-1)%len(g.DAY_PHASES)]
        for key,r in s['publicWorkshop']['receipts'].items():
            if r.get('status')=='complete' and (r.get('day'),r.get('phase'))==(previous_day,previous_phase):
                add('public-complete:'+key,'Completed: '+r['name'],'Review the result and its available use, installation or follow-up choices.','publicWorkshop',group='ready',person=r.get('ownerId'))
                record=w.catalogue()['records'].get(r.get('recordId'))
                if record:rows[-1].update(recordId=record['id'],recordType=record['recordType'])
        for key in g.NEIGHBOUR_REQUESTS:
            r=g.neighbour_request_view(s,key)
            if r['status']=='accepted':
                request=g.NEIGHBOUR_REQUESTS[key]
                goods=[str(n)+' '+g.RECIPES[k]['name'] for k,n in request['artifacts'].items()]
                goods += [str(n)+' '+g.MATERIALS[k]['name'] for k,n in request['materials'].items()]
                rewards=[str(request['rewardCrowns'])+' crowns']+[str(n)+' '+g.MATERIALS[k]['name'] for k,n in request['rewardMaterials'].items()]
                add('deliver:'+key,'Deliver '+request['name'],'Give '+', '.join(goods)+'. Receive '+', '.join(rewards)+'. No phase cost. Installed items and reserved materials stay protected.','requests',{'type':'deliver-neighbour-request','requestId':key},'ready')
        for who,r in s.get('residency',{}).items():
            if r['residencyStatus']=='visiting':add('visitor:'+who,g.character_profile(s,who)['name']+' is visiting','A visit and household membership are separate choices. Talk together when ready.','summoning',group='ready',person=who)
        for r in g.household_invitations(s):
            if r['canJoin']:add('invite:'+r['id'],r['title'],r['description']+' No deadline or phase cost.','household',group='invitation')
        if 'mira' in g.household_members(s) and s['invitationStatus']=='available' and g.character_at_castle(s,'mira'):
            add('mira-tea','Mira’s tea invitation','An optional conversation, whenever you want it. No expiry.','conversation',group='invitation',person='mira')
        for key,r in s['householdScenes'].items():
            if r['status']=='waiting' and all(g.character_at_castle(s,p) for p in r['participants']):
                add('content-scene:'+key,r['title'],r['invitation'],'householdContent',group='invitation',person=next((p for p in r['participants'] if p!='founder'),None))
        life=solo_life.view(s)
        import living_stories
        for scene in living_stories.rows(s):
            if scene['available']:add('living:'+scene['id'],scene['title'],'An optional invitation from '+scene['name']+'. No phase or resource cost; your choice will be remembered.','livingStories',group='invitation',person=scene['personId'])
        import castle_chapter
        for scene in castle_chapter.view(s)['scenes']:
            if scene['available'] and not scene['memory']:add('chapter:'+scene['id'],scene['title'],'An optional castle reflection. No deadline, phase cost or resource reward.','castleChapter',group='invitation')
        for moment in life['moments']:
            if moment['available']:add('moment:'+moment['id'],moment['title'],'A quiet milestone scene. Choose a reflection; no deadline, phase cost or resource cost.','householdWork',group='invitation')
        if g.room_available(s,'conservatory') and not life['gardeners']:
            add('garden-idle','The conservatory has no gardener','Choose your scholar or an agreed resident. The garden produces one harvest per staffed phase.','householdWork',group='work')
        if life['canCelebrate']:add('housewarming','Celebrate the restored household','Everyone is home. A quiet, one-time scene with no phase or resource cost.','householdWork',{'type':'celebrate-solo-household'},'invitation')
    import household_sagas
    for key,d in household_sagas.content.STORIES.items():
        r=household_sagas.record(s,key)
        if key not in household_sagas.saved(s)['deferred'] and r['stage']<3 and not household_sagas.scene_blockers(s,key):add('saga:'+key,d['beats'][r['stage']]['title'],'An optional ensemble story; no invitation expires.','householdSagas',group='invitation')
    seen=s['soloLife'].get('taskDismissals',{})
    hidden=seen.get('ids',[]) if seen.get('phase')==phase_key(s) else []
    order={'choice':0,'ready':1,'work':2,'invitation':3,'opportunity':4}
    rows.sort(key=lambda r:order[r['group']])
    for r in rows:r['dismissed']=r['id'] in hidden
    notice=s['soloLife'].get('phaseNotice',{})
    new_ids=notice.get('newIds',[]) if notice.get('phase')==phase_key(s) else []
    return {'phase':phase_key(s),'tasks':rows,'newIds':[r['id'] for r in rows if r['id'] in new_ids],'count':sum(not r['dismissed'] for r in rows)}


def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind not in ('phase-task-run','phase-task-dismiss','phase-task-restore'):return False
    if kind=='phase-task-restore':s['soloLife']['taskDismissals']={'phase':phase_key(s),'ids':[]};return True
    key=a.get('taskId')
    g.require(isinstance(key,str),'Choose a task from the current phase.')
    task=next((r for r in build(s)['tasks'] if r['id']==key),None)
    g.require(task is not None,'That task is no longer available. Review the refreshed phase board.')
    if kind=='phase-task-run':
        g.require('action' in task,'Open this task to review its choices.')
        g.apply_action(s,task['action'])
    else:
        g.require(task['group']!='choice','Resolve the waiting field choice before putting it aside.')
        if s['soloLife'].get('taskDismissals',{}).get('phase')!=phase_key(s):s['soloLife']['taskDismissals']={'phase':phase_key(s),'ids':[]}
        hidden=s['soloLife']['taskDismissals']['ids']
        if key not in hidden:hidden.append(key)
    return True
