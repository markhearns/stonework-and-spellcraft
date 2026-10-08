"""A persistent shared undertaking using ordinary rooms, resources and one task per person."""
from copy import deepcopy
from house_shape_content import PATHS, PURPOSES, CLOSINGS
ASSIGNMENT='house-shape'
EMPTY={'active':None,'projects':{},'enabled':True}

def saved(s):return s.get('houseShape',EMPTY)
def record(s,key):return saved(s)['projects'].get(key)
def initialize(s):s.setdefault('houseShape',deepcopy(EMPTY))
def stamp(s):return {'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
def available(s):
    opening=s.get('soloLife',{}).get('firstHearth')
    return bool(s['livingWingCompletedOn']) and 'hearth-margin' in s['castleMystery']['discoveries'] and (not opening or 'conclusion' in opening['memories'])

def undertakings_complete(s):return all(record(s,k) and record(s,k)['finished'] for k in PATHS)
def chapter_complete(s):return undertakings_complete(s) and bool(saved(s).get('conclusion'))
def bonus(s,effect):
    return sum(PATHS[k]['designs'][r['design']]['amount'] for k,r in saved(s)['projects'].items()
               if r.get('project') and r['project']['status']=='complete' and PATHS[k]['designs'][r['design']]['effect']==effect)

def remember(s,key,title,text,people=None):
    import game as g
    r=record(s,key)
    m={'id':str(len(r['memories'])),'title':title,'text':text,'participants':list(dict.fromkeys(['founder']+(people or []))),**stamp(s)}
    r['memories'].append(m);g.add_journal(s,title+': '+text)

def adviser(s,key):
    import game as g
    known=g.known_people(s)
    return next((who for who in PATHS[key]['advisers'] if who in known),None)

def studies_remaining(s):
    return [k for k,p in s['researchProjects'].items() if p['status']!='complete' and (k!='archive-foundations' or s.get('startType')=='fresh')]

def use_ready(r):return bool(r['used'] or r.get('masteryAcknowledged'))

def archive_ready(s):
    return s['researchProjects']['archive-foundations']['status']=='complete' or s['miraArchiveProject']['status'] in ('ready-to-bind','complete')

def preparation(s,key):
    import game as g,headquarters as h
    d=PATHS[key];rows=[]
    rows.append({'label':'Return '+g.EXPEDITION_SITES[d['site']]['name']+' · '+d['approach'],
                 'complete':d['approach'] in g.discoveries_for(s,d['site']),
                 'target':{'view':'expeditions','siteId':d['site']},'detail':d['field']})
    rows.append({'label':'Restore '+h.ROOMS[d['room']]['name'],'complete':h.ready(s,d['room']),
                 'target':{'view':'restoration' if d['room']=='conservatory' else 'headquarters'},'detail':h.ROOMS[d['room']]['benefit'] or 'Use the room’s ordinary restoration rules.'})
    if d['research']:
        rows.append({'label':g.RESEARCH_CATALOG[d['research']]['name'] if s.get('startType')=='fresh' else 'Complete the living-index study','complete':archive_ready(s),
                     'target':{'view':'research' if s.get('startType')=='fresh' else 'development'},'detail':'The existing research project provides the practical archive knowledge.'})
    return rows

def eligible(s):
    import game as g
    key=saved(s)['active'];r=record(s,key) if key else None
    if not r or not r['project'] or r['project']['status']!='in-progress':return []
    return [who for who in r['workers'] if who in g.household_members(s) and g.character_at_castle(s,who) and g.character_assignment(s,who)==ASSIGNMENT]

def release(s,r):
    import game as g
    for who in r['workers']:
        if who in g.household_members(s) and g.character_assignment(s,who)==ASSIGNMENT:g.set_character_assignment(s,who,'rest')

def blockers(s,key,funding=False):
    import game as g
    r=record(s,key);d=PATHS[key];out=[]
    if not g.character_at_castle(s,'founder'):out.append('Return home to agree or fund the plan.')
    if not r:return out+['Choose this undertaking first.']
    if not r['purpose']:out.append('Discuss what you want this space to do.')
    out.extend('Complete: '+x['label']+'.' for x in preparation(s,key) if not x['complete'])
    if not r['design']:out.append('Choose the room’s design after reviewing the field findings.')
    if not r['workers']:out.append('Agree at least one contributor; your scholar may work alone.')
    if funding:
        if r['project']:out.append('This project is already funded or completed.')
        if s['sharedFunds']<d['cost']:out.append(f'Needs {d["cost"]} crowns; {s["sharedFunds"]} available.')
        for k,n in d['inputs'].items():
            free=s['materialInventory'][k]-s['materialReserveTargets'][k]
            if free<n:out.append(f'Needs {n} unreserved {g.MATERIALS[k]["name"]}; {max(0,free)} available.')
        for who in r['workers']:
            if who not in g.household_members(s):out.append(who+' is no longer resident; remove or replace this contributor.')
            elif not g.character_at_castle(s,who):out.append(g.character_profile(s,who)['name']+' must return home for funding.')
            elif g.character_assignment(s,who)!='rest':out.append(g.character_profile(s,who)['name']+' must finish or explicitly pause their current task before funding.')
    return out

def resolve(s,summary,workers):
    import game as g
    key=saved(s)['active'];r=record(s,key) if key else None
    if not r or not r['project'] or r['project']['status']!='in-progress':return
    p=r['project']
    for who in workers:
        if who not in eligible(s) or p['done']>=p['total']:continue
        p['done']+=1
        p['contributions'][who]=p['contributions'].get(who,0)+1
        p['names'][who]=g.character_profile(s,who)['name']
        summary.append(p['names'][who]+': +1 work on '+PATHS[key]['title'].lower()+'.')
    if p['done']>=p['total']:
        p.update(status='complete',completedOn=stamp(s));release(s,r)
        summary.append(PATHS[key]['designs'][r['design']]['name']+' completed. '+PATHS[key]['designs'][r['design']]['benefit'])

def usage_snapshot(s):
    import game as g
    return {'assignments':{who:g.character_assignment(s,who) for who in g.household_members(s) if g.character_at_castle(s,who)},
            'research':s['researchCompletedPhases']+sum(p['completedWorkPhases'] for p in s['researchProjects'].values())+s['miraArchiveProject']['completedWorkPhases'],
            'craft':deepcopy(s['craftingProject']),'garden':g.garden_harvest(s),
            'complete':[key for key,r in saved(s)['projects'].items() if r['project'] and r['project']['status']=='complete']}

def record_usage(s,before):
    import game as g
    after_research=s['researchCompletedPhases']+sum(p['completedWorkPhases'] for p in s['researchProjects'].values())+s['miraArchiveProject']['completedWorkPhases']
    for key in before['complete']:
        r=record(s,key)
        if r['used']:continue
        effect=PATHS[key]['designs'][r['design']]['effect'];people=[];description=''
        if effect=='copy' and before['assignments'].get('founder')=='commissions':
            people=['founder'];description='An ordinary copying phase used the fitted desk’s income bonus.'
        elif effect=='research' and after_research>before['research']:
            people=[who for who,a in before['assignments'].items() if a in ('research','archive','archive-project')]
            description='An ordinary shared research phase used the fitted archive.'
        elif effect=='craft' and before['craft']:
            p=before['craft'];after=s['craftingProject']
            if before['assignments'].get(p['crafterId'])=='crafting' and (not after or after['completedWorkPhases']>p['completedWorkPhases']):
                people=[p['crafterId']];description='An ordinary artifact-crafting phase used the fitted assembly bench.'
        elif effect in ('ivy','garden-sales'):
            h=before['garden'];wanted='silver-ivy' if effect=='ivy' else 'surplus-sales'
            if h['staffed'] and h['amount'] and h['output']==wanted:
                people=[who for who,a in before['assignments'].items() if a=='garden'];description='An ordinary staffed harvest used the fitted growing beds.'
        if people:
            r['used']={'participants':people,'text':description,**stamp(s)}
            g.add_journal(s,PATHS[key]['title']+': '+description)

def ordinary_next(s,key):
    """Guidance links/actions reuse authoritative ordinary rules; they never auto-run."""
    import game as g,headquarters as h,first_hearth as f
    r=record(s,key);d=PATHS[key]
    if not g.character_at_castle(s,'founder'):
        return f.step('away','Continue your expedition','Agreed contributors at home can keep working. Return before changing the plan.','publicWorkshop' if s['publicWorkshop'].get('fieldTrip') else 'expeditions')
    if d['approach'] not in g.discoveries_for(s,d['site']):
        return f.step('field','Bring the project’s findings home',d['field'],'expeditions',siteId=d['site'])
    if not h.ready(s,d['room']):
        if d['room']=='conservatory':
            if s['restorationStatus']=='in-progress':return f.funded(s,'garden','Conservatory restoration',s['restorationCompletedPhases'],s['restorationRequiredPhases'],s['founderAssignment']=='restoration',{'type':'assign-founder','assignment':'restoration'},'restoration')
            if s['sharedFunds']<25:return f.income(s,25,'the conservatory',{'view':'restoration'})
            return f.step('restore','Restore the conservatory','25 crowns; three assigned phases. Other scholar work pauses.','restoration',{'type':'start-restoration'},'Fund restoration · 25 crowns')
        p=h.project_for(s)
        if p:return f.funded(s,'headquarters',p['name'],p['done'],p['phases'],h.working(s),{'type':'hq-resume'},'headquarters')
        room='warehouse' if not h.ready(s,'warehouse') else d['room'];rd=h.ROOMS[room]
        if s['sharedFunds']<rd['cost']:return f.income(s,rd['cost'],rd['name'],{'view':'headquarters'})
        return f.step('restore','Restore '+rd['name'],f'{rd["cost"]} crowns; {rd["phases"]} work phases. You may choose an agreed resident in Headquarters instead.','headquarters',{'type':'hq-build','roomId':room},'Fund & assign · '+str(rd['cost'])+' crowns')
    research=d['research'] if d['research'] and not archive_ready(s) else None
    if r['project'] and r['project']['status']=='complete' and not use_ready(r):
        effect=d['designs'][r['design']]['effect']
        if effect=='copy':return f.step('use','Put the desk to work','Assign ordinary copying and Advance once. The desk adds income only to actual work.','phaseTasks',{'type':'advance'} if s['founderAssignment']=='commissions' else {'type':'assign-founder','assignment':'commissions'},'Advance · copy' if s['founderAssignment']=='commissions' else 'Assign copying')
        if effect in ('ivy','garden-sales'):
            wanted='silver-ivy' if effect=='ivy' else 'surplus-sales'
            if s['gardenProductionChoice']!=wanted:return f.step('use','Choose what the garden produces','Choose the output supported by this design. This sets a priority; it does not harvest or advance time.','restoration',{'type':'garden-production','choice':wanted},'Choose '+wanted)
            staffed=any(g.character_assignment(s,w)=='garden' and g.character_at_castle(s,w) for w in g.household_members(s))
            return f.step('use','Tend the fitted beds','One ordinary staffed harvest demonstrates the garden’s chosen benefit.','restoration',{'type':'advance'} if staffed else {'type':'assign-gardener','characterId':'founder'},'Advance · harvest' if staffed else 'Assign your scholar to the garden')
        if effect=='craft':return f.recipe_step(s,'warming-lantern')
        candidates=[k for k in ('weather-sealing','archive-foundations') if k in studies_remaining(s)]
        research=candidates[0] if candidates else next((k for k,p in s['researchProjects'].items() if p['status']!='complete' and not g.research_blockers(s,k,'founder')),None)
        if not studies_remaining(s):return f.step('mastery','All current shared studies are complete','This established campaign has no remaining shared research to demonstrate. You may record that fact without inventing a work phase or awarding anything. The fitted archive remains ready for future studies.','research',{'type':'shape-acknowledge-mastery'},'Record existing mastery · no reward')
        if not research:return f.step('use','Use the archive in ordinary research','Choose a remaining shared research project and assign a researcher. The chapter waits without a deadline.','research')
    if key=='craftsmanship' and r['gathered'] and use_ready(r) and s['neighbourRequestProgress']['brook-lamps']['status']!='delivered':
        if s['neighbourRequestProgress']['brook-lamps']['status']=='offered':
            return f.step('neighbour','Useful work for the brook keepers','Their established request needs one spare warming lantern and two unreserved binding threads. It rewards 24 crowns, a clay vessel and the fern-nursery connection. Acceptance spends nothing.','requests',{'type':'accept-neighbour-request','requestId':'brook-lamps'},'Accept the neighbour request')
        if g.spare_artifact_count(s,'warming-lantern')<1:return f.recipe_step(s,'warming-lantern')
        free=s['materialInventory']['binding-thread']-s['materialReserveTargets']['binding-thread']
        if free<2:
            cost=g.MATERIALS['binding-thread']['price']
            if s['sharedFunds']<cost:return f.income(s,cost,'the delivery cord',{'view':'stores'})
            return f.step('neighbour','Keep enough delivery cord above reserves','Buy one binding thread, or explicitly review your reserve. Delivery never takes protected supplies.','stores',{'type':'buy-material','materialId':'binding-thread'},'Buy one binding thread · '+str(cost)+' crowns')
        return f.step('neighbour','Deliver a lamp for the footbridge','Deliver one spare warming lantern and two unreserved binding threads. Receive 24 crowns, one porous clay and the fern-nursery connection, once.','requests',{'type':'deliver-neighbour-request','requestId':'brook-lamps'},'Deliver the listed goods')
    if r['gathered'] and use_ready(r) and 'archive-leaf' not in s['castleMystery']['discoveries']:
        research='archive-foundations' if not archive_ready(s) else None
        if not research:
            p=s['castleMystery']['project']
            if p:return f.funded(s,'mystery','Archive investigation',p['completedWorkPhases'],p['requiredWorkPhases'],s['founderAssignment']=='mystery',{'type':'resume-mystery'},'mystery')
            return f.step('clue','Read the next piece of evidence','Investigate the uncatalogued leaf: two assigned phases, no crowns. The existing campaign history remains authoritative.','mystery',{'type':'start-mystery','leadId':'archive-leaf'},'Begin investigation · 2 phases')
    if research:
        if research=='archive-foundations' and s.get('startType')!='fresh':
            return f.step('research','Continue the living-index study','The demonstration household uses its existing archive project. Complete its study; the personal story ending is not required.','development')
        p=s['researchProjects'][research];rd=g.RESEARCH_CATALOG[research]
        if p['status']=='not-started' and s['sharedFunds']<rd['costCrowns']:return f.income(s,rd['costCrowns'],rd['name'],{'view':'research'})
        if p['status']=='in-progress':return f.funded(s,'research',rd['name'],p['completedWorkPhases'],rd['requiredWorkPhases'],s['founderAssignment']=='research' and s['activeResearchId']==research,{'type':'focus-research','researchId':research,'leaderId':'founder'},'research')
        return f.step('research',rd['name'],f'{rd["costCrowns"]} crowns; {rd["requiredWorkPhases"]} work phases. Other scholar work pauses.','research',{'type':'focus-research','researchId':research,'leaderId':'founder'},'Fund & assign research')
    return None


def forecast(s):
    import game as g
    key=saved(s)['active'];r=record(s,key) if key else None
    if not r or not r['project'] or r['project']['status']!='in-progress':return []
    workers=eligible(s)
    return [PATHS[key]['title']+': '+(', '.join(g.character_profile(s,w)['name'] for w in workers)+' contribute up to '+str(min(len(workers),r['project']['total']-r['project']['done']))+' work.' if workers else 'paused; held costs and progress kept.')]

def room_improvements(s,room):
    return [{'pathId':key,'title':d['title'],'design':deepcopy(d['designs'][r['design']]),
             'contributors':deepcopy(r['project']['contributions']),'names':deepcopy(r['project']['names'])}
            for key,d in PATHS.items() if d['room']==room and (r:=record(s,key)) and r['project'] and r['project']['status']=='complete']


def context(s,who):
    return [deepcopy(m) for r in saved(s)['projects'].values() for m in r['memories'] if who in m['participants']]


def view(s):
    import game as g
    key=saved(s)['active'];r=record(s,key) if key else None
    rows=[]
    for k,d in PATHS.items():
        old=record(s,k);a=old['adviserId'] if old else adviser(s,k)
        public={field:deepcopy(d[field]) for field in ('title','room','site','approach','research','cost','inputs','work','proposal','voice','field')}
        public['designs']={dk:{field:val for field,val in dd.items() if field!='response'} for dk,dd in d['designs'].items()}
        rows.append({'id':k,**public,'adviserId':a,'adviserName':g.character_profile(s,a)['name'] if a else None,'status':'complete' if old and old['finished'] else 'started' if old else 'available'})
    result={'title':'The House Takes Shape','available':available(s),'enabled':saved(s)['enabled'],'paths':rows,'active':key,'record':deepcopy(r),'people':[], 'next':None,'blockers':[]}
    result.update(completedCount=sum(bool(record(s,k) and record(s,k)['finished']) for k in PATHS),allUndertakingsComplete=undertakings_complete(s),chapterComplete=chapter_complete(s),conclusion=deepcopy(saved(s).get('conclusion')))
    result['improvements']={room:room_improvements(s,room) for room in ('library','conservatory','workshop')}
    result['memories']=[deepcopy(m) for row in saved(s)['projects'].values() for m in row['memories']]
    if not r:return result
    # Future story text is not included before its stage; catalogue mechanics remain reviewable.
    d=PATHS[key];prep=preparation(s,key);prepared=all(x['complete'] for x in prep)
    stage='proposal' if not r['purpose'] else 'preparation' if not prepared else 'design' if not r['design'] else 'planning' if not r['project'] else 'construction' if r['project']['status']!='complete' else 'gathering' if not r['gathered'] else 'use' if not use_ready(r) else 'neighbour' if key=='craftsmanship' and s['neighbourRequestProgress']['brook-lamps']['status']!='delivered' else 'evidence' if 'archive-leaf' not in s['castleMystery']['discoveries'] else 'ending' if not r['finished'] else 'complete'
    result.update(stage=stage,preparation=prep,working=eligible(s),purposes={k:v[0] for k,v in PURPOSES.items()},closings={k:v[0] for k,v in CLOSINGS.items()},blockers=blockers(s,key,True))
    result['scene']={'proposal':d['proposal'],'design':d['complication'],'gathering':d['gathering'],'evidence':d['clue'],'ending':d['ending']}.get(stage)
    result['people']=[{'id':who,'name':g.character_profile(s,who)['name'],'atHome':g.character_at_castle(s,who),'assignment':g.character_assignment(s,who),'included':who in r['workers']} for who in g.household_members(s)]
    if stage in ('preparation','use','neighbour','evidence'):result['next']=ordinary_next(s,key)
    n=result['next']
    if n and n.get('action'):
        try:g.apply_action(deepcopy(s),n['action'])
        except g.RuleError as e:n['blockers']=[str(e)]
    result['evidence']=deepcopy(s['castleMystery']['discoveries'].get('archive-leaf')) if stage in ('ending','complete') else None
    return result


def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind in ('assign-founder','assign-character','assign-resident') and a.get('assignment')==ASSIGNMENT:
        who='founder' if kind=='assign-founder' else 'mira' if kind=='assign-resident' else a.get('characterId')
        a={**a,'type':'shape-resume','characterId':who};kind=a['type']
    if not isinstance(kind,str) or not kind.startswith('shape-'):return False
    g.require(available(s),'Finish The First Hearth, including its closing choice. Older campaigns without that chapter may qualify through the living wing and hearth evidence.')
    if kind=='shape-visibility':
        g.require(type(a.get('enabled')) is bool,'Choose whether to show chapter guidance.')
        initialize(s);saved(s)['enabled']=a['enabled'];return True
    g.require(g.character_at_castle(s,'founder'),'Return home before changing the shared plan.')
    if kind=='shape-conclude':
        g.require(undertakings_complete(s) and not saved(s).get('conclusion'),'Finish all three undertakings before closing Chapter 2 once.')
        contributions={}
        for path in PATHS:
            p=record(s,path)['project']
            for who,n in p['contributions'].items():
                entry=contributions.setdefault(who,{'name':p['names'][who],'work':0});entry['work']+=n
        designs=[PATHS[k]['designs'][record(s,k)['design']]['name'] for k in PATHS]
        text='The first hearth gave you somewhere to return to. '+', '.join(designs)+' have made that home useful in three different ways. The archive evidence remains one discovery, read alongside the work rather than earned again. Recorded contributions: '+', '.join(d['name']+' · '+str(d['work'])+' work' for d in contributions.values())+'. The next page asks where a larger household could live, meet and work.'
        people=[who for who in contributions if who!='founder' and who in g.household_members(s) and g.character_at_castle(s,who)]
        remember(s,saved(s)['active'],'Three rooms, one home',text,people)
        saved(s)['conclusion']={'text':text,'contributions':contributions,'participants':['founder']+people,**stamp(s)}
        return True
    key=a.get('pathId',saved(s)['active'])
    g.require(isinstance(key,str) and key in PATHS,'Choose one of the three undertakings.')
    d=PATHS[key];r=record(s,key)
    if kind=='shape-start':
        active=saved(s)['active'];old=record(s,active) if active else None
        g.require(not old or old['finished'] or active==key,'Finish the current chapter undertaking before choosing another; ordinary projects remain available.')
        g.require(not r,'This undertaking is already saved.')
        initialize(s);saved(s)['active']=key
        saved(s)['projects'][key]={'purpose':None,'design':None,'workers':['founder'],'adviserId':adviser(s,key),'project':None,'memories':[],'gathered':False,'used':None,'finished':False}
        remember(s,key,'An undertaking chosen',d['proposal'],[adviser(s,key)] if adviser(s,key) else [])
        return True
    g.require(r is not None and saved(s)['active']==key,'Open the active undertaking first.')
    if kind=='shape-purpose':
        c=a.get('choice');g.require(not r['purpose'] and isinstance(c,str) and c in PURPOSES,'Choose the undertaking’s purpose once.')
        r['purpose']=c;remember(s,key,'What this room is for',PURPOSES[c][1],[r['adviserId']] if r['adviserId'] else [])
    elif kind=='shape-design':
        c=a.get('choice');g.require(r['purpose'] and all(x['complete'] for x in preparation(s,key)),'Return the findings, restore the room and complete its study first.')
        g.require(not r['project'] and isinstance(c,str) and c in d['designs'],'Choose a design before funding. Cancel unfinished work to revise it.')
        r['design']=c;remember(s,key,'The space you chose',d['designs'][c]['response'],[r['adviserId']] if r['adviserId'] else [])
    elif kind in ('shape-include','shape-remove'):
        who=a.get('characterId')
        g.require(isinstance(who,str) and who in (g.household_members(s) if kind=='shape-include' else r['workers']),'Choose a current contributor.')
        g.require(not r['project'] or r['project']['status']!='complete','The completed project keeps its actual contributors.')
        if kind=='shape-include':
            g.require(who not in r['workers'] and len(r['workers'])<3,'Choose up to three distinct contributors.')
            g.require(g.character_at_castle(s,who),'Discuss participation together at home.')
            r['workers'].append(who);remember(s,key,'An agreed contributor',g.character_profile(s,who)['name']+' agreed to this undertaking. No work or payment was assigned.',[who])
        else:
            if who in g.household_members(s) and g.character_assignment(s,who)==ASSIGNMENT:g.set_character_assignment(s,who,'rest')
            r['workers'].remove(who)
    elif kind=='shape-fund':
        reasons=blockers(s,key,True);g.require(not reasons,' '.join(reasons))
        s['sharedFunds']-=d['cost']
        for k,n in d['inputs'].items():s['materialInventory'][k]-=n
        r['project']={'status':'in-progress','done':0,'total':d['work'],'crowns':d['cost'],'inputs':deepcopy(d['inputs']),'contributions':{},'names':{}}
        for who in r['workers']:g.set_character_assignment(s,who,ASSIGNMENT)
        g.add_journal(s,'Funded '+d['title']+'. Costs held once; agreed contributors assigned.')
    elif kind in ('shape-resume','shape-pause','shape-cancel'):
        p=r['project'];g.require(p and p['status']=='in-progress','Choose a funded unfinished undertaking.')
        if kind=='shape-resume':
            who=a.get('characterId','founder')
            g.require(isinstance(who,str) and who in r['workers'] and who in g.household_members(s),'Agree this contributor first.')
            g.require(g.character_at_castle(s,who),'The contributor must be home.')
            g.set_character_assignment(s,who,ASSIGNMENT)
        else:
            release(s,r)
            if kind=='shape-cancel':
                s['sharedFunds']+=p['crowns']
                for k,n in p['inputs'].items():s['materialInventory'][k]+=n
                r['project']=None;g.add_journal(s,'Cancelled unfinished '+d['title']+'. Exact held costs returned; unfinished work discarded. The design and conversation memories remain.')
    elif kind=='shape-gather':
        c=a.get('choice');g.require(r['project'] and r['project']['status']=='complete' and not r['gathered'],'Complete the installation before gathering once.')
        g.require(isinstance(c,str) and c in CLOSINGS,'Choose a way to mark the completed room.')
        people=[w for w in r['project']['contributions'] if w!='founder' and w in g.household_members(s) and g.character_at_castle(s,w)]
        text=d['gathering']+' '+d['designs'][r['design']]['name']+'. '+CLOSINGS[c][1]
        remember(s,key,'A room put together',text,people);r['gathered']=True
        if key=='craftsmanship':
            remember(s,key,'Useful work beyond the walls','The brook keepers’ existing request is a practical way to put the workshop in touch with its neighbours. A lamp and cord must actually be delivered; this conversation supplies neither.')
    elif kind=='shape-acknowledge-mastery':
        g.require(r['project'] and r['project']['status']=='complete' and d['designs'][r['design']]['effect']=='research' and not studies_remaining(s) and not use_ready(r),'Only a completed archive with no remaining shared studies can record existing mastery.')
        r['masteryAcknowledged']={'text':'All current shared research was already complete. No new demonstration, phase or reward is claimed.',**stamp(s)}
    elif kind=='shape-finish':
        g.require(key!='craftsmanship' or s['neighbourRequestProgress']['brook-lamps']['status']=='delivered','Deliver the brook keepers’ request before concluding the workshop undertaking.')
        g.require(r['gathered'] and use_ready(r) and 'archive-leaf' in s['castleMystery']['discoveries'] and not r['finished'],'Gather in the finished room, use its benefit in ordinary work, and record the archive leaf first.')
        remember(s,key,'An undertaking complete',d['ending']+' Your chosen purpose: '+PURPOSES[r['purpose']][0]+'.')
        r['finished']=True;r['completedOn']=stamp(s)
    else:raise g.RuleError('Unknown household undertaking action.')
    return True
