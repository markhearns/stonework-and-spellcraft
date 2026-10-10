"""Read-only next steps for the later chapters; ordinary actions own every change."""
from copy import deepcopy
import first_hearth as f


def checked(s, row):
    """Keep the normal action's exact blockers beside a suggested button."""
    import game as g
    if row and row.get('action'):
        try:g.apply_action(deepcopy(s), row['action'])
        except g.RuleError as error:row['blockers']=[str(error)]
    return row


def travel_step(s):
    import field_patrols as patrols
    run=patrols.saved(s)['active']
    if run:
        if run['stage'] in ('decision','site-decision'):
            return f.step('field-choice','Choose the party’s next action',
                'Review the available methods, their costs and their results. The party waits until you choose; advancing time does not choose for you.','fieldPatrols')
        return f.step('field-work',run['name'],patrols.forecast(s)[0],
            'fieldPatrols',{'type':'advance'},'Advance · continue the patrol')
    e=s.get('expedition')
    if e:
        if e['stage'] in ('awaiting-choice','encounter-choice'):
            return f.step('field-choice','Choose an expedition method',
                'Review the available methods and their work phases. Choose a method or begin the return journey before advancing.','expeditions',siteId=e['siteId'])
        if e['stage']=='ready-to-return':
            return f.step('return','Bring the completed report home',
                'Begin the return journey, then Advance to arrive. Rewards are received at home.',
                'expeditions',{'type':'return-expedition'},'Begin the return journey',siteId=e['siteId'])
        return f.step('travel','Continue the expedition',
            'Advance resolves one phase of the selected travel or fieldwork and the household’s other assignments.',
            'expeditions',{'type':'advance'},'Advance · continue the expedition',siteId=e['siteId'])
    if s.get('publicWorkshop',{}).get('fieldTrip'):
        return f.step('public-trip','Finish or return from the workshop expedition',
            'Review the current field choice and bring the party home before starting chapter work.','publicWorkshop')
    return None


def rest_assignment(s, people, view, reason):
    import game as g
    for who in people:
        name=g.character_profile(s,who)['name']
        if not g.character_at_castle(s,who):
            return f.step('return', 'Bring '+name+' home',reason+' Rest must take place at home.',view)
        if g.character_assignment(s,who)!='rest':
            return f.step('rest','Set '+name+' to Rest',
                reason+' This pauses '+name+'’s current assignment and keeps paid work progress. Only Advance moves time.',
                view,{'type':'assign-character','characterId':who,'assignment':'rest'},'Set '+name+' to Rest')
    return None


def night_step(s, people, returned_day, view):
    import game as g
    need=[w for w in people if s.get('overnightRest',{}).get(w,0)<=returned_day]
    if not need:return None
    names=', '.join(g.character_profile(s,w)['name'] for w in need)
    reason=names+' need a night at home after this return.'
    assignment=rest_assignment(s,need,view,reason)
    if assignment:return assignment
    evening=s['currentDayPhase']=='evening'
    return f.step('sleep','Sleep at home before continuing',reason+' '+
        ('They are assigned to Rest. Advance ends the evening and records their overnight rest.' if evening else
         'They are assigned to Rest. Daytime rest restores vitality; overnight rest is recorded when you advance the evening. Keep them resting then.'),
        view,{'type':'advance'},'Advance · sleep and begin morning' if evening else 'Advance · rest through this phase')


def evening_step(s, view):
    if s['currentDayPhase']=='evening':return None
    return f.step('evening','Share the closing supper this evening',
        'The required night’s rest is recorded. You can work or visit people today. Advance your chosen assignments until evening, then return here for supper.',
        view,{'type':'advance'},'Advance · resolve current assignments')


def principle_step(s, principle):
    import game as g
    name=g.PRINCIPLE_NAMES[principle]
    if principle in g.character_principles(s,'founder'):return None
    p=s['trainingProjects']['founder']
    if p:
        taught=bool(p.get('teacherId'))
        return f.funded(s,'study','The scholar’s agreed learning',p['completedWorkPhases'],p['requiredWorkPhases'],
            not g.lesson_blockers(s,'founder') if taught else s['founderAssignment']=='training',
            {'type':'resume-lesson','learnerId':'founder'} if taught else {'type':'assign-founder','assignment':'training'},'development')
    if principle in s['archivePrinciples']:
        return f.step('study','Study '+name,
            'The archive contains this method. Personal study uses the scholar’s primary assignment; other paid work keeps its progress.',
            'development',{'type':'study-principle','characterId':'founder','principleId':principle},'Begin personal study')
    research=next(((key,d) for key,d in g.RESEARCH_CATALOG.items() if d['principle']==principle),None)
    if research:
        key,d=research
        for required in d['requiredPrinciples']:
            if required not in g.character_principles(s,'founder'):return principle_step(s,required)
        discovery=d.get('requiredDiscovery')
        if discovery and discovery['approach'] not in g.discoveries_for(s,discovery['siteId']):
            return f.step('survey','Survey '+g.EXPEDITION_SITES[discovery['siteId']]['name'],
                'Return with the survey before researching '+name+'.','expeditions',siteId=discovery['siteId'])
        p=s['researchProjects'][key];action={'type':'focus-research','researchId':key,'leaderId':'founder'}
        if p['status']=='in-progress':
            return f.funded(s,'research',d['name'],p['completedWorkPhases'],d['requiredWorkPhases'],
                s['activeResearchId']==key and s['founderAssignment']=='research',action,'research')
        if s['sharedFunds']<d['costCrowns']:return f.income(s,d['costCrowns'],d['name'].lower(),{'view':'research'})
        return f.step('research',d['name'],str(d['costCrowns'])+' crowns; '+str(d['requiredWorkPhases'])+
            ' work contributions. The scholar learns '+name+' on completion. Other paid work keeps its progress.',
            'research',action,'Fund & begin research')
    source=g.PRINCIPLE_GUIDE.get(principle,{})
    site={'water-guidance':'old-waterworks','gentle-preservation':'reedbank-waystation'}.get(principle)
    return f.step('learn','Learn '+name,source.get('source','Review this principle’s source in character development.'),
        source.get('view','development'),**({'siteId':site} if site else {}))


def roads(s):
    import roads_we_keep as r, headquarters as h, keeping_hearth as k
    c=r.saved(s)
    if not r.available(s) or not c['started'] or c['completedOn']:return None
    travel=travel_step(s)
    if travel:return travel
    if not r.progress(s)['discoveries']:
        return f.step('rescue','Prepare the caravan rescue','Choose a party and depart for the Hollow Road. Review each field method when you arrive.','expeditions',siteId=r.SITE)
    if not c['agreement']:
        return f.step('agreement','Choose the supplier agreement','Provisions adds 2 free food each morning. Materials gives an additional 5% saving on consolidated deliveries. Choose below.','roadsWeKeep')
    if not h.ready(s,'supply-office'):return k.hq_step(s,'hq-build','supply-office')
    if not c['refugeDone']:return k.hq_step(s,'hq-job','roadside-refuge')
    return f.step('closing','Review the completed road work','The caravan, agreement, Supply Office and refuge are ready. Velis does not need to join the household to conclude this chapter.',
        'roadsWeKeep',{'type':'roads-conclude'},'Share the closing review')


def first_patrol(s):
    import first_patrol as p, headquarters as h, keeping_hearth as k, game as g, solo_life
    c=p.saved(s);view='firstPatrol'
    if not p.available(s) or not c['started'] or c['completedOn']:return None
    travel=travel_step(s)
    if travel:return travel
    if not p.progress(s,p.TRAIL)['discoveries']:
        return f.step('trail','Follow the Watchtower Trail','Choose your party and prepare the first journey.','expeditions',siteId=p.TRAIL)
    if not p.willing_ally(s):
        if not p.guest_blockers(s):return f.step('rhess','Agree a guest alliance','Rhess will help with the wardstones as a guest. Permanent membership remains a separate choice.',view,{'type':'patrol-guest-ally'},'Agree the guest alliance')
        return f.step('rhess','Invite Rhess through Contacts','Discuss her account and offer a visit in an available private bedroom. Once she arrives, agree a guest alliance here or discuss permanent membership in Contacts.','contacts')
    if not c['drillDone']:
        free=rest_assignment(s,['founder','rhess'],view,'The relief drill needs both participants resting at home.')
        if free:return free
        if c['drill']:return f.step('drill','Continue the shared relief drill',str(c['drill']['done'])+'/2 phases complete. Keep both participants assigned to Rest; changing either assignment pauses the drill.',view,{'type':'advance'},'Advance · practice relief')
        return f.step('drill','Practice handing over the watch','Two phases while you and Rhess are both resting at home. Starting the drill does not advance time.',view,{'type':'patrol-drill'},'Begin the shared relief drill')
    if not h.ready(s,'watchtower'):return k.hq_step(s,'hq-build','watchtower')
    if not c['resolution']:
        return f.step('plan','Choose the guardian’s future','Repair the old command or retire it safely. Both choices make the road safe; the resolution is remembered. Choose below.',view)
    finished=bool(p.progress(s,p.WARD)['discoveries'])
    night=night_step(s,['founder','rhess'],c.get('finalReturnDay',c['returnedOn']) if finished else c['returnedOn'],view)
    if night:return night
    if not finished:
        if not p.guest_ally(s) and not solo_life.offered(s,'rhess','fieldwork'):
            return f.step('agreement','Agree fieldwork with Rhess','Review and agree her fieldwork role before selecting her for the wardstone expedition.','characterProfile',personId='rhess',characterTab='development')
        if p.guest_ally(s):return f.step('wardstones','Return with your guest ally','You and Rhess will travel together to resolve the wardstones. Her guest agreement covers this journey; no household membership is added.',view,{'type':'start-expedition','siteId':p.WARD,'companionIds':['rhess']},'Depart with Rhess')
        return f.step('wardstones','Return to the Broken Wardstones with Rhess','Select Rhess in the expedition party. Her knowledge offers specific field methods when you reach the damaged boundary.','expeditions',siteId=p.WARD)
    return evening_step(s,view) or f.step('closing','Share the closing supper','Both of you have slept at home since the final return. Review the watch together.',view,{'type':'patrol-conclude'},'Share the closing supper')


def trial(s):
    import field_patrols as p
    c=p.chapter(s);view='firstRealTest'
    if not p.unlocked(s) or not c['started'] or c['completedOn']:return None
    travel=travel_step(s)
    if travel:return travel
    if c['lastReturn'] is not None:
        night=night_step(s,c['lastParty'],c['lastReturn'],view)
        if night:return night
    if 'scout' in c['completed'] and not c['plan']:
        return f.step('plan','Choose how to reopen the supply route','Review the three route plans below: one safe bypass, easier negotiation, or extra damage. Choose the approach you want to use.',view)
    mission=next((key for key in p.MISSIONS if key not in c['completed']),None)
    if mission:
        row=f.step('mission',p.MISSIONS[mission]['name'],'Review the party, vitality, equipment and fieldwork agreements below. For a solo outing, recover to 6 vitality and equip protective armour or a shield. Guarded strikes trade damage for cover. One night restores up to 3 vitality; rest longer if needed.',view)
        row['blockers']=p.story_blockers(s,mission)
        return row
    return evening_step(s,view) or f.step('closing','Choose a permanent patrol improvement','Share supper and choose linked signals, recovery stores or road contracts below. The choice also awards 20 crowns and 2 advancement points to each member of the final story party.',view)
