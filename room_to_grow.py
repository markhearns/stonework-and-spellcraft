"""Chapter three: a development plan over the authoritative construction systems.

No shadow inventory, construction queue or automatic assignments. Reads are pure;
paid jobs remain in headquarters/housing when priorities or guidance change.
"""
from copy import deepcopy
import headquarters as h
import house_shape as shape
import first_hearth as f

LAYOUTS={
 'private':{'title':'A quiet private suite','rooms':['lower-suite'],'text':'One bed behind a closing door. A small expansion with room for someone who needs privacy.'},
 'shared':{'title':'A shared lower chamber','rooms':['lower-chamber'],'text':'Four separate beds with screens and personal storage. Sharing a room never assigns a relationship.'},
 'mixed':{'title':'Private and shared rooms','rooms':['lower-suite','lower-chamber'],'text':'A private suite alongside a four-bed chamber: five places with different kinds of privacy.'}}
PRIORITIES={
 'accommodation':{'title':'Rooms to call one’s own','order':['services','bedrooms','community','specialist'],'text':'Start with somewhere comfortable to live; let the other rooms support it.'},
 'community':{'title':'A place to spend time together','order':['services','community','bedrooms','specialist'],'text':'Give the new wing a shared centre before fitting its sleeping places.'},
 'specialists':{'title':'Room for useful work','order':['services','specialist','bedrooms','community'],'text':'Prepare a useful facility, then make a home around the work.'}}
COMMUNAL=('none','chapel','sauna')
SPECIALIST=('infirmary','smithy','command-room')
INSPECTIONS={
 'services':('A passage worth opening','The lower passage is dry, the air moves freely, and the warded services reach its sitting space. You can open this part of the castle without leaving its care unfinished.'),
 'bedrooms':('A door, a bed, a choice','You check the fitted sleeping places and their storage. An empty room is a possibility, not an obligation to invite anyone or move a resident.'),
 'community':('Somewhere to linger','You check the seating, lighting and clear path to the door. The new communal room is ready for people to use, with space to sit together or keep a little distance.'),
 'specialist':('Work with a place of its own','You check the specialist facility against the plan. Its ordinary activities are ready when someone chooses to use them; no one has been assigned a profession by its completion.')}


def required_inspections(r):return [k for k in INSPECTIONS if k!='community' or r['communal']!='none']

def saved(s):return s.get('roomToGrow')
def available(s):return shape.chapter_complete(s)
def stamp(s):return shape.stamp(s)
def remember(s,title,text,people=None):
    import game as g
    m={'id':str(len(saved(s)['memories'])),'title':title,'text':text,'participants':list(dict.fromkeys(['founder']+(people or []))),**stamp(s)}
    saved(s)['memories'].append(m);g.add_journal(s,title+': '+text)

def specifications(layout,communal,specialist,priority):
    """Deduplicated dependency order, with categories available for walkthroughs."""
    targets={'services':['underground-quarters'],'bedrooms':LAYOUTS[layout]['rooms'],'community':[] if communal=='none' else [communal],'specialist':[specialist]}
    rows=[];seen=set()
    def add(key,category):
        if key in seen:return
        if key in h.BEDROOMS:
            add(h.BEDROOMS[key]['hq'],'services');d=h.BEDROOMS[key]
            row={'id':key,'kind':'housing','name':d['name'],'cost':d['costCrowns'],'phases':d['requiredWorkPhases'],'needs':[d['hq']],'beds':d['capacityBeds']}
        else:
            d=h.ROOMS[key]
            for dep in d['needs']:add(dep,'services')
            row={'id':key,'kind':'hq','name':d['name'],'cost':d['cost'],'phases':d['phases'],'needs':d['needs'],'principles':d['principles'],'benefit':d['benefit'] or d['use']}
        if key=='conservatory':row.update(kind='restoration',cost=25,phases=3)
        seen.add(key);rows.append({**row,'category':category})
    for category in PRIORITIES[priority]['order']:
        for key in targets[category]:add(key,category)
    return rows

def rows(s,config):
    import game as g
    result=[]
    for spec in specifications(config['layout'],config['communal'],config['specialist'],config['priority']):
        key=spec['id'];who=None;p=None
        if spec['kind']=='restoration':
            done=s['restorationStatus']=='complete';funded=s['restorationStatus']=='in-progress';work=s['restorationCompletedPhases'];who='founder' if funded else None
            working=funded and s['founderAssignment']=='restoration' and g.character_at_castle(s,'founder')
        elif spec['kind']=='housing':
            p=s['housingRooms'][key];done=p['status']=='complete';funded=p['status']=='in-progress';work=p['completedWorkPhases']
            who='founder' if funded else None
            working=funded and s['activeHousingRoomId']==key and s['founderAssignment']=='housing' and g.character_at_castle(s,'founder')
        else:
            done=h.ready(s,key)
            who,p=next(((w,p) for w,p in h.projects(s).items() if p['kind']=='hq-build' and p['id']==key),(None,None))
            funded=bool(p);work=p['done'] if p else spec['phases'] if done else 0
            working=funded and h.working(s,who)
        result.append({**deepcopy(spec),'complete':done,'funded':funded,'done':work,'working':bool(working),'workerId':who,
                       'workerName':g.character_profile(s,who)['name'] if who else None,
                       'held':spec['cost'] if funded else 0,'remainingCost':0 if done or funded else spec['cost'],
                       'target':{'view':{'housing':'housing','restoration':'restoration'}.get(spec['kind'],'headquarters')}})
    return result

def budget(items):
    return {'listedCost':sum(x['cost'] for x in items),'remainingCost':sum(x['remainingCost'] for x in items),
            'heldCost':sum(x['held'] for x in items),'baseWorkRemaining':sum(max(0,x['phases']-x['done']) for x in items if not x['complete']),
            'beds':sum(x.get('beds',0) for x in items),'completeCount':sum(x['complete'] for x in items),'totalCount':len(items)}

def next_step(s,items,worker):
    import game as g
    if not g.character_at_castle(s,'founder'):return f.step('away','Return to the development plan','Work already assigned at home continues. Return before agreeing new construction.','expeditions')
    pending=[x for x in items if not x['complete']]
    if not pending:return None
    # Paid plan work comes first, irrespective of newly selected priorities.
    row=next((x for x in pending if x['funded']),pending[0]);key=row['id']
    if row['funded']:
        resume={'type':'assign-founder','assignment':'restoration'} if row['kind']=='restoration' else {'type':'resume-housing','roomId':key} if row['kind']=='housing' else {'type':'hq-resume','workerId':row['workerId']}
        return f.funded(s,key,row['name'],row['done'],row['phases'],row['working'],resume,row['target']['view'])
    if row['kind']=='hq':
        # Never replace another funded job merely because it is outside this plan.
        p=h.project_for(s,worker)
        if p:return f.funded(s,'other-work',p['name'],p['done'],p['phases'],h.working(s,worker),{'type':'hq-resume','workerId':worker},'headquarters')
        if worker not in g.household_members(s) or not g.character_at_castle(s,worker):return f.step('worker','Choose a builder at home','The selected builder is unavailable. Choose your scholar or another resident on the plan.','roomToGrow')
        missing=[k for k in row.get('principles',[]) if k not in g.character_principles(s,worker)]
        if missing and worker=='founder':
            import campaign_guidance
            return campaign_guidance.principle_step(s,missing[0])
        if missing:return f.step('knowledge','Prepare the chosen builder','This builder must learn '+', '.join(g.PRINCIPLE_NAMES[k] for k in missing)+'. Teach them through normal study, or choose your scholar.','progression')
        if worker!='founder' and worker not in s['headquarters']['workAgreements']:
            return f.step('agreement','Agree construction work','Discuss headquarters work with '+g.character_profile(s,worker)['name']+'. Agreement alone assigns no work.','headquarters',{'type':'hq-agree-work','workerId':worker,'enabled':True},'Agree headquarters work')
    if s['sharedFunds']<row['cost']:return f.income(s,row['cost'],row['name'].lower(),row['target'])
    action={'type':'start-restoration'} if row['kind']=='restoration' else {'type':'fund-housing','roomId':key} if row['kind']=='housing' else {'type':'hq-build','roomId':key,'workerId':worker}
    return f.step(key,'Restore '+row['name'],str(row['cost'])+' crowns once; '+str(row['phases'])+' base work phases. Funding explicitly changes the builder’s assignment; other paid progress is kept.',row['target']['view'],action,'Fund & assign · '+str(row['cost'])+' crowns')

def snapshot(s):
    r=saved(s)
    return rows(s,r) if r and not r.get('completedOn') else []

def record_work(s,before):
    """Credit only observed work deltas, not assumed historical contributors."""
    import game as g
    r=saved(s)
    if not before or not r:return
    after={x['id']:x for x in rows(s,r)}
    for old in before:
        if not old['funded'] or not old['working']:continue
        new=after[old['id']];delta=max(0,(old['phases'] if new['complete'] else new['done'])-old['done'])
        if not delta:continue
        entry=r['contributions'].setdefault(old['id'],{})
        who=old['workerId'];credit=entry.setdefault(who,{'name':g.character_profile(s,who)['name'],'work':0});credit['work']+=delta

def context(s,who):return [deepcopy(m) for m in (saved(s) or {}).get('memories',[]) if who in m['participants']]

def suggestions(s):
    import game as g
    result=[]
    for who in g.household_members(s):
        if who=='founder':continue
        p=g.character_profile(s,who)
        if p.get('accommodationPreference')=='private-room':
            result.append({'personId':who,'name':p['name'],'text':p['name']+' has agreed to a private one-bed room. A lower private suite can respect that preference; any move remains a separate choice.'})
    return result

def view(s):
    import game as g
    r=saved(s)
    v={'title':'Room to Grow','available':available(s),'record':deepcopy(r),'layouts':deepcopy(LAYOUTS),'priorities':deepcopy(PRIORITIES),
       'communal':{k:({'title':'Use the existing common room','text':'No additional communal construction. You can add a chapel or sauna later.'} if k=='none' else {'title':h.ROOMS[k]['name'],'text':h.ROOMS[k]['benefit']}) for k in COMMUNAL},
       'specialists':{k:{'title':h.ROOMS[k]['name'],'text':h.ROOMS[k]['benefit']} for k in SPECIALIST},
       'suggestions':suggestions(s),'next':None,'rows':[],'memories':deepcopy(r['memories']) if r else [],'stage':'locked' if not available(s) else 'planning'}
    if not available(s):return v
    if not r:
        # Read-only comparison includes existing and paid work; no draft is installed by reading.
        v['previews']={layout+':'+communal+':'+specialist:budget(rows(s,{'layout':layout,'communal':communal,'specialist':specialist,'priority':'accommodation'})) for layout in LAYOUTS for communal in COMMUNAL for specialist in SPECIALIST}
        return v
    items=rows(s,r);v.update(rows=items,budget=budget(items),workers=[{'id':who,'name':g.character_profile(s,who)['name'],'assignment':g.character_assignment(s,who),'atHome':g.character_at_castle(s,who)} for who in g.household_members(s)])
    complete=all(x['complete'] for x in items)
    v['stage']='complete' if r.get('completedOn') else 'closing' if complete and all(k in r['inspections'] for k in required_inspections(r)) else 'walkthrough' if complete else 'construction'
    v['inspections']=[{'id':key,'title':title,'complete':key in r['inspections'],'text':text if key in r['inspections'] or complete else None} for key,(title,text) in INSPECTIONS.items() if key in required_inspections(r)]
    if v['stage']=='construction':v['next']=next_step(s,items,r['workerId'])
    n=v['next']
    if n and n.get('action'):
        try:g.apply_action(deepcopy(s),n['action'])
        except g.RuleError as e:n['blockers']=[str(e)]
    return v

def apply(s,a):
    import game as g
    kind=a.get('type')
    if not isinstance(kind,str) or not kind.startswith('grow-'):return False
    g.require(available(s),'Complete one Chapter 2 undertaking and its closing scene first.')
    g.require(g.character_at_castle(s,'founder'),'Return home before changing or reviewing the development plan.')
    r=saved(s)
    if kind=='grow-plan':
        g.require(not r,'This chapter already has a saved plan; reorder its priorities without replacing paid work.')
        layout=a.get('layout');communal=a.get('communal');specialist=a.get('specialist');priority=a.get('priority')
        g.require(isinstance(layout,str) and layout in LAYOUTS and isinstance(communal,str) and communal in COMMUNAL and isinstance(specialist,str) and specialist in SPECIALIST and isinstance(priority,str) and priority in PRIORITIES,'Choose a layout, communal room, specialist facility and priority.')
        s['roomToGrow']={'layout':layout,'communal':communal,'specialist':specialist,'priority':priority,'workerId':'founder','enabled':True,'inspections':{},'contributions':{},'memories':[],'completedOn':None}
        designs=[shape.PATHS[k]['designs'][shape.record(s,k)['design']]['name'] for k in shape.completed_paths(s)]
        remember(s,'A larger home, on paper','The first hearth made the castle habitable. '+', '.join(designs)+' gave it useful working rooms. Now you plan '+LAYOUTS[layout]['title'].lower()+', '+('use of the existing common room' if communal=='none' else h.ROOMS[communal]['name'].lower())+' and '+h.ROOMS[specialist]['name'].lower()+'. '+PRIORITIES[priority]['text']+' The plan commits no crowns or assignments.')
        return True
    g.require(r is not None,'Draw up the development plan first.')
    if kind=='grow-visibility':
        g.require(type(a.get('enabled')) is bool,'Choose whether to show chapter guidance.');r['enabled']=a['enabled'];return True
    g.require(not r['completedOn'],'This chapter is already remembered. Ordinary castle development remains available.')
    if kind=='grow-priority':
        choice=a.get('priority');g.require(isinstance(choice,str) and choice in PRIORITIES,'Choose a known priority.')
        r['priority']=choice
    elif kind=='grow-worker':
        who=a.get('workerId');g.require(isinstance(who,str) and who in g.household_members(s),'Choose a current household member.')
        r['workerId']=who
    elif kind=='grow-inspect':
        key=a.get('area');g.require(isinstance(key,str) and key in required_inspections(r) and key not in r['inspections'],'Choose an unrecorded walkthrough stop.')
        g.require(all(x['complete'] for x in rows(s,r)),'Finish the planned rooms and services before the walkthrough.')
        title,text=INSPECTIONS[key];r['inspections'][key]=stamp(s);remember(s,title,text)
    elif kind=='grow-finish':
        choice=a.get('choice');g.require(choice in ('quiet','gather'),'Choose a quiet conclusion or a gathering.')
        g.require(all(k in r['inspections'] for k in required_inspections(r)) and all(x['complete'] for x in rows(s,r)),'Complete the wing and its walkthrough first.')
        people=[who for who in g.household_members(s) if who!='founder' and g.character_at_castle(s,who)] if choice=='gather' else []
        work={}
        for credits in r['contributions'].values():
            for who,d in credits.items():work[who]={'name':d['name'],'work':work.get(who,{}).get('work',0)+d['work']}
        credit=' Recorded work: '+', '.join(d['name']+' · '+str(d['work'])+' work' for d in work.values())+'.' if work else ' The plan used rooms already restored; no new construction credit is invented.'
        text=('You gather in the common room after inspecting the lower wing. '+('Present: '+', '.join(g.character_profile(s,w)['name'] for w in people)+'. ' if people else 'For now, you mark the occasion on your own. ') if choice=='gather' else 'You walk back through the wing in the quiet and leave a lamp by the stair. ')
        text+='The castle now has '+str(budget(rows(s,r))['beds'])+' fitted sleeping place(s) in this plan and a useful facility. From a first hearth, to working rooms, to room for a household: each chapter has left something usable behind. Empty beds may stay empty; further development is yours to choose.'+credit
        text+=' Behind the lower passage’s blocked side door, you find paired foundation channels and a surveyor’s mark. You record their position; equipment calibration will give you the tools to trace them safely.'
        remember(s,'Room to Grow',text,people);r['completedOn']=stamp(s);r['closingChoice']=choice
    else:raise g.RuleError('Unknown castle development action.')
    return True
