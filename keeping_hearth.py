"""Chapter four: bounded intrusion, ordinary defenses, and Sabine's existing case.

No timed theft, duplicate identity, forced membership or separate construction engine.
"""
from copy import deepcopy
import headquarters as h
import containment as c
import first_hearth as f

ROOMS=('entry-hall','warehouse','training-yard')
CARE_ROOMS=('underground-quarters','dungeons')
DEFENSES={
 'barriers':{'name':'Shuttered watch post and sound gates','job':'hearth-barriers','text':'Repair the service latch, fit shielded lamps and a watched inner gate. The return encounter stops at a physical barrier.','result':'The new inner gate holds. Shielded light catches the hand at its latch before anyone reaches the stores.'},
 'wards':{'name':'Warning seals and a signal bell','job':'hearth-warning-seals','text':'Fit threshold seals and a bell circuit keyed to the service entrance. These announce an entry; they do not bind a person.','result':'The threshold seal sounds the entry-hall bell. You reach the passage while the intruder is still trying to work out which mark noticed her.'}}
INSPECTIONS={
 'latch':('The service latch','A scrape along the keeper shows how a narrow tool could lift the worn latch. You mark the fitting for repair.'),
 'light':('The dark turn','The service passage disappears from view around one bend. A shuttered lamp can reveal an arrival without lighting the bedrooms.'),
 'alarm':('A warning that reaches someone','The old bell pull ends in a cut cord. An alarm needs a clear destination as well as a loud noise.')}
LESSONS={
 'capacity':('A chamber is not a bedroom','The dungeon ward provides access and secure working space. A fitted Quiet chamber supplies one compatible containment place; it does not add a residential bed. Food, water, bedding and care are included.'),
 'account':('Hear the person and agree the work','The existing case separates her account, a practical plan, learned magic, and funded care. The problem is the obsolete alarm oath; her personality and preferences are not defects to repair. Safe specialist transfer is available without completing that work.'),
 'release':('Resolve the case, then release','Ordinary release follows a resolved case. A safe specialist transfer is also possible, including during unfinished care, with its exact held costs refunded. The chamber becomes free only when departure happens on Advance.'),
 'recruitment':('Recruitment begins outside the chamber','After release, ordinary correspondence can lead to a visit in a private one-bed room, her own decision to stay, and your invitation. A chamber, a work agreement and a bedroom are three separate things. Transfer to specialists does not presume a return.')}

def register():
    for key,d in DEFENSES.items():
        h.JOBS[d['job']]=dict(name=d['name'],room='entry-hall',cost=18,phases=3,output=d['job'],benefit=d['text'])

def saved(s):return s.get('keepingHearth')
def available(s):return bool(s.get('roomToGrow',{}).get('completedOn'))
def stamp(s):return {'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
def remember(s,title,text,people=()):
    import game as g
    r=saved(s);m={'id':str(len(r['memories'])),'title':title,'text':text,'participants':list(dict.fromkeys(['founder']+list(people))),**stamp(s)}
    r['memories'].append(m);g.add_journal(s,title+': '+text)
def context(s,who):return [deepcopy(m) for m in (saved(s) or {}).get('memories',[]) if who in m['participants']]
def case(s):return s['containment']['cases']['sabine']
def fresh_encounter(s):return saved(s)['mode']=='intrusion' and case(s)['status']=='unmet' and 'sabine' not in s['people']
def defense_ready(s):
    r=saved(s);return bool(r and r['defense'] and s['headquarters']['stock'].get(DEFENSES[r['defense']]['job']))
def quiet_ready(s):return any(x['status']=='ready' for k,x in s['containment']['chambers'].items() if c.CHAMBERS[k]['ward']=='echo')
def care_planned(s):return saved(s).get('responsePlan') in ('capture','parley')
def required_rooms(s):return ROOMS+CARE_ROOMS if care_planned(s) else ROOMS
def prepared(s):return all(h.ready(s,k) for k in required_rooms(s)) and 'basic-drill' in s['headquarters']['completedDrills'] and defense_ready(s) and (not care_planned(s) or quiet_ready(s))
def required_lessons(s):return list(LESSONS) if saved(s)['returnChoice'] in ('capture','parley') or case(s)['status']!='unmet' else []

def supplies(s,definition,title):
    """Buy one missing component at a time above reserves; normal prices and income."""
    import game as g
    for key,n in definition['materials'].items():
        if s['materialInventory'][key]-s['materialReserveTargets'][key]<n:
            price=g.MATERIALS[key]['price']
            if s['sharedFunds']<price:return f.income(s,price,title,{'view':'stores'})
            return f.step('supplies','Prepare '+title,f'Buy one {g.MATERIALS[key]["name"]} for {price} crowns. Protected reserves are kept.','stores',{'type':'buy-material','materialId':key},'Buy one component',materialId=key)
    if s['sharedFunds']<definition['costCrowns']:return f.income(s,definition['costCrowns'],title,{'view':'containment'})
    return None

def hq_step(s,kind,key):
    import game as g
    owner,p=next(((w,p) for w,p in h.projects(s).items() if p['kind']==kind and p['id']==key),(None,None))
    if p:return f.funded(s,key,p['name'],p['done'],p['phases'],h.working(s,owner),{'type':'hq-resume','workerId':owner},'headquarters')
    p=h.project_for(s)
    if p:return f.funded(s,'paid-work',p['name'],p['done'],p['phases'],h.working(s),{'type':'hq-resume'},'headquarters')
    d=(h.ROOMS if kind=='hq-build' else h.JOBS)[key]
    if kind=='hq-build':
        for dep in d['needs']:
            if not h.ready(s,dep):return hq_step(s,'hq-build',dep)
    if s['sharedFunds']<d['cost']:return f.income(s,d['cost'],d['name'].lower(),{'view':'headquarters'})
    return f.step(key,d['name'],f'{d["cost"]} crowns; {d["phases"]} base assigned phases. Existing paid work keeps its progress. Agreed resident builders can use the ordinary room controls.','headquarters',{'type':kind,('roomId' if kind=='hq-build' else 'jobId'):key},'Fund & assign' if d['cost'] else 'Assign the drill')

def containment_step(s):
    p=s['containment']['project']
    if p:return f.funded(s,'containment','Specialized '+p['kind']+' work',p['completedWorkPhases'],p['requiredWorkPhases'],s['founderAssignment']=='containment',{'type':'resume-containment'},'containment')
    return None

def preservation_step(s):
    """Respect personal learning already agreed before proposing another trip."""
    import game as g
    p=s['trainingProjects']['founder']
    if p:
        if p.get('teacherId'):
            working=not g.lesson_blockers(s,'founder')
            resume={'type':'resume-lesson','learnerId':'founder'}
        else:
            working=s['founderAssignment']=='training'
            resume={'type':'assign-founder','assignment':'training'}
        return f.funded(s,'learning','The scholar’s agreed learning',p['completedWorkPhases'],p['requiredWorkPhases'],working,resume,'development')
    if 'gentle-preservation' in s['archivePrinciples']:
        return f.step('study-preservation','Study the archived preservation method',
            'The archive already contains Gentle preservation. Study it personally before agreeing Sabine’s care; no repeat expedition is needed. This uses the scholar’s primary assignment.',
            'development',{'type':'study-principle','characterId':'founder','principleId':'gentle-preservation'},'Begin personal study')
    return f.step('preservation','Learn Gentle preservation','Survey Reedbank waystation and return with its preservation method. A knowledgeable resident can also offer a personal lesson through development. Sabine can transfer to specialists now if you prefer.','expeditions',siteId='reedbank-waystation')

def construction_next(s):
    for key in required_rooms(s):
        if not h.ready(s,key):return hq_step(s,'hq-build',key)
    if 'basic-drill' not in s['headquarters']['completedDrills']:return hq_step(s,'hq-job','basic-drill')
    if not defense_ready(s):return hq_step(s,'hq-job',DEFENSES[saved(s)['defense']]['job'])
    if care_planned(s) and not quiet_ready(s):
        pending=containment_step(s)
        if pending:return pending
        key=next(k for k,d in c.CHAMBERS.items() if d['ward']=='echo' and s['containment']['chambers'][k]['status']=='sealed')
        missing=supplies(s,c.CHAMBERS[key],'a Quiet chamber')
        return missing or f.step('chamber','Fit a Quiet chamber','14 crowns plus two unreserved porous clay and one binding thread. This creates specialized capacity, not a residential bed.','containment',{'type':'build-containment','chamberId':key},'Fund the listed chamber')

def care_next(s):
    import game as g
    r=case(s);status=r['status']
    if status.endswith('-pending'):return f.step('departure','Resolve the agreed arrival or departure','Only Advance moves the escort or frees a reserved chamber. Everyone else keeps their current assignments.','containment',{'type':'advance'},'Advance · resolve escort')
    if status=='contained':
        for topic in c.CASES['sabine']['topics']:
            if topic not in r['discussedTopics']:return f.step('account','Hear Sabine’s '+topic,'Discuss the existing case in the Quiet chamber. This does not recruit her or assign work.','containment',{'type':'talk-containment','characterId':'sabine','topic':topic},'Discuss '+topic)
        pending=containment_step(s)
        if pending:return pending
        if 'gentle-preservation' not in g.character_principles(s,'founder'):
            return preservation_step(s)
        missing=supplies(s,c.CASES['sabine'],'Sabine’s agreed care')
        return missing or f.step('care','Separate the obsolete oath','12 crowns, one unreserved moon glass and two binding thread; the existing care project resolves the old alarm clause. Release does not depend on recruitment.','containment',{'type':'care-containment','characterId':'sabine'},'Fund the agreed resolution')
    if status=='safe':return f.step('release','Open the door','Sabine’s case is resolved. Release is free, with no bed, work, gratitude or relationship requirement.','containment',{'type':'release-containment','characterId':'sabine'},'Agree unconditional release')
    return None

def lesson_ready(s,key):
    status=case(s)['status'];r=saved(s)
    if key=='capacity':return quiet_ready(s)
    if r['returnChoice']=='review' and status=='unmet':return True
    if key=='account':return len(case(s)['discussedTopics'])>=2 or status in ('released','transferred') or r['returnChoice']=='drive-away'
    if key in ('release','recruitment'):return status in ('released','transferred') or r['returnChoice']=='drive-away'
    return False

def stage(s):
    r=saved(s)
    if not r:return 'opening' if available(s) else 'locked'
    if r['completedOn']:return 'complete'
    if not r['introChoice']:return 'intrusion' if r['mode']=='intrusion' else 'review'
    if len(r['inspections'])<len(INSPECTIONS):return 'inspection'
    if not r['defense']:return 'design'
    if not prepared(s):return 'construction'
    if not r['returnChoice']:return 'return'
    if care_next(s):return 'care'
    if any(k not in r['lessons'] for k in required_lessons(s)):return 'tutorial'
    return 'closing'

def view(s):
    import game as g
    r=saved(s);v={'title':'Keeping the Hearth','available':available(s),'record':deepcopy(r),'stage':stage(s),'next':None,'defenses':deepcopy(DEFENSES),'memories':deepcopy(r['memories']) if r else []}
    if not available(s) or not r:return v
    v['newEncounter']=fresh_encounter(s)
    v['companions']=[{'id':who,'name':g.character_profile(s,who)['name']} for who in g.household_members(s) if who!='founder' and g.character_at_castle(s,who)]
    v['canUseLantern']=bool(g.spare_artifact_count(s,'warming-lantern'))
    v['inspections']=[{'id':key,'title':d[0],'text':d[1] if key in r['inspections'] or v['stage']=='inspection' else None,'complete':key in r['inspections']} for key,d in INSPECTIONS.items()]
    v['requirements']=[{'id':key,'title':h.ROOMS[key]['name'],'complete':h.ready(s,key),'cost':h.ROOMS[key]['cost'],'target':{'view':'hqRoom','roomId':key}} for key in required_rooms(s)]
    v['requirements'] += [{'id':'basic-drill','title':'Introductory defensive training','complete':'basic-drill' in s['headquarters']['completedDrills'],'cost':0,'target':{'view':'hqRoom','roomId':'training-yard'}},{'id':'defense','title':'Entrance protections','complete':defense_ready(s),'cost':18,'target':{'view':'hqRoom','roomId':'entry-hall'}}]+([{'id':'quiet-chamber','title':'One fitted Quiet chamber','complete':quiet_ready(s),'cost':14,'target':{'view':'containment'}}] if care_planned(s) else [])
    v['lessons']=[{'id':key,'title':d[0],'text':d[1],'complete':key in r['lessons'],'ready':lesson_ready(s,key)} for key,d in LESSONS.items() if key in required_lessons(s)] if r['returnChoice'] else []
    v['quietReady']=quiet_ready(s);v['carePlanned']=care_planned(s)
    v['caseStatus']=case(s)['status'];v['resident']='sabine' in g.household_members(s)
    v['canTransfer']=case(s)['status'] in ('arrival-pending','contained','safe')
    if not g.character_at_castle(s,'founder'):
        v['next']=f.step('away','Return home','Construction already assigned at the castle can continue. Return before making security decisions.','expeditions')
    elif v['stage']=='construction':v['next']=construction_next(s)
    elif v['stage']=='care':v['next']=care_next(s)
    n=v['next']
    if n and n.get('action'):
        try:g.apply_action(deepcopy(s),n['action'])
        except g.RuleError as e:n['blockers']=[str(e)]
    return v

def apply(s,a):
    import game as g
    kind=a.get('type')
    if not isinstance(kind,str) or not kind.startswith('hearth-'):return False
    g.require(available(s),'Finish Room to Grow before beginning this chapter.')
    g.require(g.character_at_castle(s,'founder'),'Return home before changing castle security arrangements.')
    r=saved(s)
    if kind=='hearth-start':
        g.require(not r,'This chapter already has a saved record.')
        mode='intrusion' if case(s)['status']=='unmet' and 'sabine' not in s['people'] else 'established'
        s['keepingHearth']={'mode':mode,'introChoice':None,'inspections':{},'defense':None,'returnChoice':None,'lessons':{},'enabled':True,'memories':[],'completedOn':None}
        remember(s,'A noise at the service door' if mode=='intrusion' else 'A security review worth making',
          'A pale, auburn-haired woman is lifting the service latch with an engraver’s tool. She reaches toward a seal impression among the repair notes, then looks up at your light. “Sabine. If introductions are unavoidable.” Nothing has left the stores. The encounter waits for your response.' if mode=='intrusion' else 'Sabine is already known to the household. This chapter begins with an inspection of the service entrance instead of a new theft.')
        return True
    g.require(r is not None,'Open the chapter first.')
    if kind=='hearth-visibility':
        g.require(type(a.get('enabled')) is bool,'Choose whether to show guidance.');r['enabled']=a['enabled'];return True
    g.require(not r['completedOn'],'This chapter is already remembered.')
    if kind=='hearth-scare':
        choice=a.get('choice');g.require(not r['introChoice'],'The opening is already resolved.')
        allowed=('confront','lantern','companion') if r['mode']=='intrusion' else ('review',)
        g.require(isinstance(choice,str) and choice in allowed,'Choose an offered response.')
        people=[]
        if choice=='lantern':g.require(g.spare_artifact_count(s,'warming-lantern')>0,'Have a spare warming lantern to expose the service passage.')
        if choice=='companion':
            who=a.get('characterId');g.require(isinstance(who,str) and who!='founder' and who in g.household_members(s) and g.character_at_castle(s,who),'Choose a resident currently at home.');people=[who]
        text={'confront':'You challenge her from the lit doorway. Sabine withdraws through the service passage, leaving the seal impression where it lay.',
              'lantern':'You lift the warming lantern. Its clear light exposes the latch tool; Sabine retreats rather than remain in view. The lantern stays yours.',
              'companion':'You call your companion to the doorway. Faced with company and a clear exit, Sabine slips back into the grounds. Nothing was stolen.',
              'review':'You mark out a security review around the existing service entrance. Prior encounters and relationships remain exactly as they were.'}[choice]
        r['introChoice']=choice;remember(s,'The first response',text,people)
    elif kind=='hearth-inspect':
        key=a.get('area');g.require(r['introChoice'] and isinstance(key,str) and key in INSPECTIONS and key not in r['inspections'],'Choose an unrecorded inspection after the opening.')
        r['inspections'][key]=stamp(s);remember(s,*INSPECTIONS[key])
    elif kind=='hearth-design':
        key=a.get('choice');g.require(len(r['inspections'])==len(INSPECTIONS) and not r['defense'] and isinstance(key,str) and key in DEFENSES,'Inspect the route and choose one defensive plan once.')
        r['defense']=key;remember(s,'A plan for the service entrance',DEFENSES[key]['text'])
    elif kind=='hearth-care-plan':
        g.require(not r['returnChoice'] and care_planned(s),'There is no unfinished escort plan to put aside.')
        r['responsePlan']=None
        remember(s,'Rely on the entrance protections','You put the escort plan aside. Paid construction keeps its progress and remains available in the construction controls.')
    elif kind=='hearth-return':
        g.require(prepared(s) and not r['returnChoice'],'Complete the listed entrance protections and basic training first.')
        choice=a.get('choice');fresh=fresh_encounter(s)
        g.require(isinstance(choice,str) and choice in (('capture','parley','drive-away') if fresh else ('review',)),'Choose a response appropriate to the current encounter.')
        if fresh and choice in ('capture','parley') and not quiet_ready(s):
            r['responsePlan']=choice
            remember(s,'Prepare specialized care','You plan a Quiet chamber before attempting an escort. Sabine has not returned yet. The incident waits while you prepare; you can change this plan and rely on the entrance protections instead.')
            return True
        # Admission validates against a staged state so failure cannot leave a half-resolved encounter.
        staged=deepcopy(s);saved(staged)['returnChoice']=choice
        if fresh and choice in ('capture','parley'):
            chambers=[key for key,d in c.CHAMBERS.items() if d['ward']=='echo' and s['containment']['chambers'][key]['status']=='ready' and not c.occupied(s,key)]
            g.require(chambers,'Prepare an unoccupied Quiet chamber before arranging the escort.')
            g.apply_action(staged,{'type':'admit-containment','characterId':'sabine','chamberId':chambers[0]})
            case(staged)['chapterOrigin']='keeping-hearth'
            text=DEFENSES[r['defense']]['result']+(' Your yard training keeps the interception controlled. Sabine is captured with the latch tool and agrees to put it down.' if choice=='capture' else ' You keep a clear distance and ask what the seal is for. Sabine puts the tool down and accepts a safe escort.')+' “The old alarm oath follows its seals. I tried to take the impression before it found another keeper. A poor introduction; I am aware.” The Quiet chamber can isolate that existing oath. Her escort arrives on the next Advance.'
        elif fresh:text=DEFENSES[r['defense']]['result']+' You order Sabine to leave. She withdraws; there is no prisoner, stolen stock or recruitment reward. Her original archive encounter can still be pursued; specialized care can be prepared then if you choose.'
        else:text='You rehearse the service-door approach against the completed protections. The new route is secure. Sabine’s existing case and residency are respected; the chapter does not stage another capture.'
        remember(staged,'The service door, a second time',text,['sabine'] if fresh and choice in ('capture','parley') else [])
        s.clear();s.update(staged)
    elif kind=='hearth-lesson':
        key=a.get('lessonId');g.require(r['returnChoice'] and isinstance(key,str) and key in LESSONS and key not in r['lessons'] and lesson_ready(s,key),'Complete the relevant real case step before recording this lesson.')
        r['lessons'][key]=stamp(s);remember(s,*LESSONS[key])
    elif kind=='hearth-finish':
        g.require(prepared(s) and r['returnChoice'] and not care_next(s) and all(k in r['lessons'] for k in required_lessons(s)),'Resolve the incident and any care you chose to undertake first.')
        r['completedOn']=stamp(s)
        remember(s,'Keeping the Hearth','The repaired entrance gives a clear warning, and the basic drill gives you a practiced response. The incident is resolved. '+('Sabine is now a resident by a separate agreement.' if 'sabine' in g.household_members(s) else 'Any invitation to Sabine remains a separate choice.'))
    else:raise g.RuleError('Unknown castle security action.')
    return True
