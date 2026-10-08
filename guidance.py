"""Save-scoped goals and a read-only preview using the normal Advance resolver."""
from copy import deepcopy


def goals(s):
    import game as g
    import local_encounters as local
    def step(key, label, done, view, **target):
        return {'id':key,'label':label,'complete':bool(done),'target':{'view':view,**target}}
    hearth=step('hearth','Understand the hearth wards',s['researchStatus']=='complete','research')
    made=bool(s['craftedArtifacts'].get('warming-lantern') or s['characterDevelopment']['founder']['advancementAwards'].get('artifact:warming-lantern'))
    lantern=step('lantern','Make a warming lantern',made,'fullWorkshop',recipeId='warming-lantern')
    garden=step('garden','Restore the conservatory · 25 crowns, 3 assigned phases',g.room_available(s,'conservatory'),'restoration')
    rows=[{'id':'first-lantern','title':'Make your first lantern','steps':[hearth,lantern]},
          {'id':'conservatory','title':'Restore the conservatory','steps':[garden]},
          {'id':'living-wing','title':'Complete a proper living wing','steps':[step('wing-'+str(i),r['name']+' — '+r['detail'],r['complete'],r['view']) for i,r in enumerate(g.living_wing_requirements(s))]}]
    for who in ('maren','brakka','fenna'):
        introduced=s['localEncounters'][who]['status']=='introduced'
        resident=who in g.household_members(s)
        steps=[]
        if who=='brakka':steps.append(garden)
        if who=='fenna':
            delivered=s['neighbourRequestProgress']['brook-lamps']['status']=='delivered'
            discovered=bool(g.discoveries_for(s,'fern-nursery'))
            steps=[hearth,step('spare-lantern','Make a spare warming lantern for the brook keepers',delivered or g.spare_artifact_count(s,'warming-lantern')>=1,'fullWorkshop',recipeId='warming-lantern'),
                   step('delivery-thread','Keep two binding threads above your protected reserve',delivered or s['materialInventory']['binding-thread']-s['materialReserveTargets']['binding-thread']>=2,'stores',materialId='binding-thread'),step('footbridge','Deliver A lamp for the footbridge: one spare lantern and two unreserved binding threads',delivered,'requests'),
                   step('nursery','Visit the fern nursery, investigate a lead, and bring the discovery home',discovered,'expeditions',siteId='fern-nursery')]
        steps.extend([step('meet-'+who,'Arrange the introduction · one assigned scholar phase',introduced,'localEncounters'),
            step('welcome-'+who,'Discuss a visit, offer a suitable bed, then agree membership together',resident,'summoning',personId=who)])
        # A resident is already a completed goal, including a testing-created home.
        if resident:
            steps=[{**r,'complete':True} for r in steps]
        rows.append({'id':'welcome-'+who,'title':'Welcome '+local.PEOPLE[who]['name'],'personId':who,'steps':steps,
                     'note':'Visits and membership are separate, voluntary agreements. This goal never makes either decision for you.'})
    pinned=s.get('soloLife',{}).get('pinnedGoals',[])
    for r in rows:
        r['pinned']=r['id'] in pinned
        r['complete']=all(x['complete'] for x in r['steps'])
        r['nextStep']=next((x for x in r['steps'] if not x['complete']),None)
    return rows


def apply(s,a):
    if a.get('type')!='pin-goal':return False
    import game as g
    key=a.get('goalId');enabled=a.get('pinned')
    g.require(isinstance(key,str) and key in {r['id'] for r in goals(s)},'Choose an available goal.')
    g.require(type(enabled) is bool,'Choose whether to pin the goal.')
    pinned=s['soloLife'].setdefault('pinnedGoals',[])
    if enabled and key not in pinned:
        g.require(len(pinned)<3,'Keep at most three pinned goals. Put one aside first.')
        pinned.append(key)
    elif not enabled and key in pinned:pinned.remove(key)
    return True


def projects(s):
    """Only known projects: no speculative discovery or story prose is exposed."""
    import game as g
    import local_encounters
    out={}
    def add(key,name,who,done,total,view,**target):
        out[key]={'id':key,'name':name,'personId':who,'done':done,'total':total,'target':{'view':view,**target}}
    import bestiary
    study=bestiary.saved(s)['research']
    if study:add('bestiary-study','Bestiary: '+bestiary.CREATURES[study['entryId']]['name'],'founder',study['done'],study['total'],'bestiary',entryId=study['entryId'])
    for who,j in s.get('armoury',{}).get('jobs',{}).items():
        add('equipment:'+who,j['name'],who,j['done'],j['phases'],'armoury')
    import house_shape
    key=house_shape.saved(s)['active']
    r=house_shape.record(s,key) if key else None
    if r and r['project'] and r['project']['status']=='in-progress':
        p=r['project'];add('house-shape',house_shape.PATHS[key]['title'],r['workers'][0] if r['workers'] else 'founder',p['done'],p['total'],'houseShape')
        out['house-shape']['participants']=list(r['workers'])
    import household_sagas
    for key,r in household_sagas.saved(s)['stories'].items():
        project=r['project']
        if project and project['status']!='complete':add('saga:'+key,household_sagas.content.STORIES[key]['projectName'],project['workers'][0],project['done'],2,'householdSagas')
    import lasting_rituals
    ritual=lasting_rituals.state(s)['project']
    if ritual:add('lasting-ritual',lasting_rituals.CATALOGUE[ritual['id']]['name'],ritual['participants'][0],ritual['done'],lasting_rituals.CATALOGUE[ritual['id']]['phases'],'rituals',ritualId=ritual['id'])
    for who,job in s['spellWork'].items():
        if job:
            spell=g.spell_by_id(s,job['spellId']);add('spell-work:'+who,spell['name'],who,spell['completedWorkPhases'] if job['kind']=='test' else 0,2 if job['kind']=='test' else 1,'spells',personId=who)
    if s['researchStatus']=='in-progress':add('hearth','Hearth wards','founder',s['researchCompletedPhases'],s['researchRequiredPhases'],'research')
    if s['restorationStatus']=='in-progress':add('garden','Conservatory restoration','founder',s['restorationCompletedPhases'],s['restorationRequiredPhases'],'restoration')
    p=s['craftingProject']
    if p:add('craft',g.RECIPES[p['recipeId']]['name'],p['crafterId'],p['completedWorkPhases'],g.RECIPES[p['recipeId']]['requiredWorkPhases'],'fullWorkshop',recipeId=p['recipeId'])
    for key,p in s['researchProjects'].items():
        if p['status']=='in-progress':add('research:'+key,g.RESEARCH_CATALOG[key]['name'],p.get('leadId',s.get('researchLeaderId','founder')),p['completedWorkPhases'],g.RESEARCH_CATALOG[key]['requiredWorkPhases'],'research')
    for key,p in s['facilityProjects'].items():
        if p['status']=='in-progress':add('facility:'+key,g.FACILITIES[key]['name'],'founder',p['completedWorkPhases'],g.FACILITIES[key]['requiredWorkPhases'],'ledger')
    for key,p in s['housingRooms'].items():
        if p['status']=='in-progress':add('housing:'+key,g.HOUSING_ROOMS[key]['name'],'founder',p['completedWorkPhases'],g.HOUSING_ROOMS[key]['requiredWorkPhases'],'housing')
    for who,p in s['trainingProjects'].items():
        if p:add('training:'+who,'Personal learning',who,p['completedWorkPhases'],p['requiredWorkPhases'],'development',personId=who)
    for who,p in s['focusProjects'].items():
        if p:add('focus:'+who,'Focus inscription',who,p['completedWorkPhases'],p['requiredWorkPhases'],'focus',personId=who)
    for who,p in s['publicWorkshop']['jobs'].items():
        if p:add('public:'+who,p['name'],who,p['completedWorkPhases'],p['requiredWorkPhases'],'publicWorkshop',personId=who,recordId=p['recordId'])
    for key,p in s['personalStories'].items():
        if p['status']=='in-progress':add('story:'+key,p['proposal']['title'],p['ownerId'],p['completedWorkPhases'],p['rules']['requiredWorkPhases'],'stories',personId=p['ownerId'])
    review=s.get('livingStories',{}).get('review')
    if review:add('shared-review','Shared research-note review','founder',0,1,'livingStories')
    import headquarters
    for who,p in headquarters.projects(s).items():
        add('headquarters' if who=='founder' else 'headquarters:'+who,p['name'],who,p['done'],p['phases'],'headquarters',workerId=who)
    p=s['castleMystery']['project']
    if p:
        import castle_mystery
        add('mystery',castle_mystery.LEADS[p['leadId']]['name'],'founder',p['completedWorkPhases'],p['requiredWorkPhases'],'mystery')
    p=s['localVisit']
    if p:add('local','Introduction to '+local_encounters.PEOPLE[p['encounterId']]['name'],'founder',p['completedWorkPhases'],p['requiredWorkPhases'],'summoning',personId=p['encounterId'])
    import party_journeys
    if party_journeys.active(s) and s['expedition']['stage']=='working':
        site=party_journeys.site(s);job=party_journeys.saved(s,site)['pending']
        if job:
            name=g.SPELL_FORMS[job['support']]['name'] if job.get('support') else party_journeys.step(s)['choices'][job['methodId']]['name']
            total=job.get('required',1)
            add('party-journey:'+site,name,job.get('casterId') or 'founder',total-job['remaining'],total,'expeditions',siteId=site)
    import commissions,practical_projects,castle_reawakening
    job=commissions.saved(s)['job']
    if job:add('commission',job['name'],job['workerId'],job['done'],job['phases'],'commissions')
    for who,job in practical_projects.saved(s).items():
        if not job['completedOn']:
            d=practical_projects.PROJECTS[who];add('practical:'+who,d['name'],who,job['done'],d['phases'],'practicalProjects',personId=who)
    job=castle_reawakening.saved(s)['job']
    if job:add('castle-lamp','Resonance lens study' if job['study'] else 'Library reading-lamp repair','founder',job['done'],job['phases'],'mystery')
    return out


def changes(before, s):
    after=projects(s)
    return [{**p,'after':after[k]['done'] if k in after else p['total'],
             'completes':k not in after,'progress':(after[k]['done'] if k in after else p['total'])-p['done']} for k,p in before.items()]


def waiting_choices(s):
    import field_patrols
    rows=[]
    e=s.get('expedition')
    if e and e['stage'] in ('awaiting-choice','encounter-choice','ready-to-return'):
        rows.append({'title':'Begin the return journey' if e['stage']=='ready-to-return' else 'Choose an expedition method',
                     'detail':'Open the expedition to choose the next step.', 'target':{'view':'expeditions','siteId':e['siteId']}})
    run=field_patrols.saved(s)['active']
    if run and run['stage'] in ('decision','site-decision'):
        rows.append({'title':'Choose a patrol site method' if run['stage']=='site-decision' else 'Choose the party’s next action',
                     'detail':'The party waits for your choice. Advance still moves time and resolves household work, but does not choose a field action.',
                     'target':{'view':'fieldPatrols'}})
    return rows


def preview(s):
    import game as g
    before=projects(s)
    waiting=waiting_choices(s)
    future=deepcopy(s)
    try:g.apply_action(future,{'type':'advance'})
    except g.RuleError as error:return {'blocked':str(error),'waitingChoices':waiting,'projects':[], 'completions':[], 'resources':[]}
    rows=changes(before,future)
    resources=[]
    def resource(key,name,before,after):
        if before!=after:resources.append({'id':key,'name':name,'before':before,'after':after,'change':after-before})
    resource('crowns','Shared crowns',s['sharedFunds'],future['sharedFunds'])
    resource('resonance','Resonance',s['resonancePoints'],future['resonancePoints'])
    import provisions
    resource('provisions','Provisions',provisions.view(s)['stock'],provisions.view(future)['stock'])
    for key,m in g.MATERIALS.items():
        diff=future['materialInventory'].get(key,0)-s['materialInventory'].get(key,0)
        if diff:resource(key,m['name'],s['materialInventory'].get(key,0),future['materialInventory'].get(key,0))
    return {'blocked':None,'waitingChoices':waiting,'routineChanges':[x for x in future['lastPhaseSummary'] if x.startswith('Routine:')],'projects':rows,'completions':[r for r in rows if r['completes']],
            'resources':[r for r in resources if r['change']], 'dayNumber':future['dayNumber'],'phase':future['currentDayPhase']}
