"""Patrol contracts, prepared-spell conditions and concrete non-combat goals."""
from copy import deepcopy

SITES = {
 'crossing': dict(name='A cracked bridge support', text='The cart cannot cross until the cracked support is braced.',
     manual='Fit a timber brace', finish='Fasten the brace while the ice supports the load',
     spells={'ice-bind':'Freeze a temporary brace around the cracked support'}, condition='The ice supports the load. A party member can now fasten the permanent brace in one phase.'),
 'heat': dict(name='An overheated ward mechanism',text='The metal housing is too hot to touch. Cool it before repairing its latch.',
     manual='Let the mechanism cool, then replace its latch',finish='Replace the cooled latch',
     spells={'water-jet':'Cool the housing with water','ice-bind':'Cool the housing with ice'},condition='The housing is cool enough to handle. A party member can now replace its latch in one phase.'),
 'fumes': dict(name='Fumes in the inspection passage',text='Dust and smoke hide the path markings. Clear the air before checking the route.',
     manual='Open the vents and wait, then check the markings',finish='Read the exposed markings and mark a safe route',
     spells={'wind-step':'Direct a current of air through the passage','water-jet':'Settle the hot dust with water'},condition='The air is clear and the markings are visible. A party member can now mark the route in one phase.'),
}
OBJECTIVES = {
 'escort':dict(name='Deliver a fragile supply crate',site='crossing',enemy='thief',route='road',
     task='Move the crate behind cover',goal=2,crowns=16,food=6,materials={'binding-thread':1},
     text='Brace the bridge, then get the crate past the thieves. Complete two task steps to secure the cargo; driving off or negotiating with the thieves also completes delivery.'),
 'rescue':dict(name='Bring a missing surveyor home',site='fumes',enemy='bandit',route='road',
     task='Lead the surveyor toward the safe route',goal=2,crowns=16,food=6,materials={'moon-glass':1},
     text='Clear the inspection passage, then reach the surveyor. Complete two task steps to bring them to safety; driving off or negotiating with the bandits also opens the way.'),
 'observe':dict(name='Observe a ridge griffin',site='fumes',enemy='griffin',route='border',
     task='Record the griffin’s markings and movements',goal=2,crowns=12,food=4,materials={'moon-glass':2},
     text='Clear the old observation route and record the griffin. Complete two observation steps to finish the study. Fieldcraft rank 1 lets an observer stay hidden; a prepared Wisp scout also prevents retaliation during an observation.'),
 'repair':dict(name='Repair the refuge crossing',site='heat',enemy='bandit',route='road',
     task='Finish the crossing repair under cover',goal=2,crowns=18,food=4,materials={'fireglass':1},
     text='Cool and repair the ward mechanism, then secure the crossing. Complete two task steps to finish the work. With two conscious party members, a protection or control action lets another member complete one task step.'),
}


def spell_options(s,who,forms):
    import game as g
    rows=[]
    for sp in s['spellbook']:
        if sp['ownerId']!=who or sp['formId'] not in forms or sp['status']!='learned' or sp['id'] not in s['preparedSpells'].get(who,[]):continue
        d=g.SPELL_FORMS[sp['formId']]; b=[]
        if any(p not in g.character_principles(s,who) for p in d['requiredPrinciples']):b.append('Learn all principles required by this spell.')
        for k,n in d['castingInputs'].items():
            if s['materialInventory'].get(k,0)-s['materialReserveTargets'].get(k,0)<n:b.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
        rows.append(dict(spellId=sp['id'],formId=sp['formId'],inputs=deepcopy(d['castingInputs']),blockers=b))
    return rows


def attach(s,run,key):
    d=OBJECTIVES[key]
    run.update(objectiveId=key,objectiveProgress=0,siteWork=dict(condition=False,complete=False,pending=None))


def site_choices(s,run):
    import game as g,field_magic as f
    if run['stage']!='site-decision':return []
    d=SITES[OBJECTIVES[run['objectiveId']]['site']];rows=[];condition=run['siteWork']['condition']
    for who in run['party']:
        if f.vitality(s,who)<=0:continue
        rows.append(dict(id=who+':site-work',who=who,name=d['finish'] if condition else d['manual'],
                         phases=1 if condition else 2 if g.skill_rank(s,who,'fieldcraft')>=1 else 3,
                         blockers=[],inputs={},spellId=None))
        if not condition:
            for sp in spell_options(s,who,d['spells']):
                rows.append(dict(id=who+':site-spell:'+sp['spellId'],who=who,name=d['spells'][sp['formId']],phases=1,**sp))
    return rows


def apply(s,a):
    import game as g,field_patrols as p
    if a.get('type')!='watch-site-method':return False
    run=p.saved(s)['active'];g.require(run and run.get('objectiveId') and run['stage']=='site-decision','Wait for a site decision on an objective patrol.')
    row=next((r for r in site_choices(s,run) if r['id']==a.get('methodId')),None)
    g.require(row,'Choose a listed site method.');g.require(not row['blockers'],' '.join(row['blockers']))
    for k,n in row['inputs'].items():s['materialInventory'][k]-=n
    run['pending']=dict(**deepcopy(row),remaining=row['phases']);run['stage']='site-work'
    return True


def resolve_site(s,run,summary):
    import game as g,signature_growth
    if run['stage']=='site-decision':return True
    if run['stage']!='site-work':return False
    row=run['pending'];row['remaining']-=1
    summary.append(row['name']+': '+str(row['phases']-row['remaining'])+'/'+str(row['phases'])+' work phases.')
    if row['remaining']:return True
    if row.get('spellId'):
        sp=g.spell_by_id(s,row['spellId']);sp['castCount']=sp.get('castCount',0)+1
        run['siteWork']['condition']=True;run['stage']='site-decision'
        run.setdefault('workProofs',{}).setdefault(row['who'],[]).append('practical-spell')
        summary.append(SITES[OBJECTIVES[run['objectiveId']]['site']]['condition'])
    else:
        run['siteWork']['complete']=True;run['stage']='decision'
        run.setdefault('workProofs',{}).setdefault(row['who'],[]).append('site-repair')
        summary.append('The route is ready. Choose how to complete the patrol objective.')
    run['pending']=None
    return True


def combat_rows(s,run):
    import game as g,field_magic as f,practical_projects as pp
    if not run.get('objectiveId'):return []
    key=run['objectiveId'];d=OBJECTIVES[key];rows=[]
    for who in run['party']:
        if f.vitality(s,who)<=0:continue
        hidden=key=='observe' and g.skill_rank(s,who,'fieldcraft')>=1
        rows.append(dict(id=who+':objective',who=who,name=d['task']+(' from cover' if hidden else ''),kind='objective',damage=0,block=0,cost=0,actionGuard=1,objectiveStep=1,avoidAttack=hidden,blockers=[]))
        if key=='observe':
            for sp in spell_options(s,who,['wisp-scout']):
                rows.append(dict(id=who+':observe-spell:'+sp['spellId'],who=who,name='Observe through a Wisp scout',kind='spell',spellKind='scout',damage=0,block=0,cost=0,objectiveStep=1,avoidAttack=True,**sp))
    if 'iona' in run['party'] and f.vitality(s,'iona')>0 and pp.active(s,'iona'):
        rows.append(dict(id='iona:atlas-route',who='iona',name='Use Iona’s mapped route to complete the objective',kind='bypass',damage=0,block=99,cost=0,blockers=[]))
    return rows


def enrich(s,run,row):
    import field_magic as f,signature_growth as growth
    if not run.get('objectiveId'):return
    d=OBJECTIVES[run['objectiveId']];step=row.get('objectiveStep',0)
    if run['objectiveId']=='repair' and (row.get('protect') or row.get('control')) and sum(f.vitality(s,w)>0 for w in run['party'])>1:step=1
    if step and growth.personal_effect(s,row['who'])=='task':step+=growth.effect(s,row['who']).get('rank',0)
    row['objectiveStep']=min(step,max(0,d['goal']-run['objectiveProgress']))
    row['objectiveAfter']=min(d['goal'],run['objectiveProgress']+row['objectiveStep'])
    row['objectiveGoal']=d['goal']


def resolved(s,run,row,result):
    """Return true when task work permits safe departure without enemy loot."""
    if not run.get('objectiveId'):return False
    d=OBJECTIVES[run['objectiveId']]
    run['objectiveProgress']=min(d['goal'],run['objectiveProgress']+row.get('objectiveStep',0))
    if row.get('objectiveStep'):
        run.setdefault('workProofs',{}).setdefault(row['who'],[]).append('objective:'+run['objectiveId'])
    return run['objectiveProgress']>=d['goal'] and any(n>0 for n in result['healthAfter'].values())


def returned(s,run,complete,summary):
    import game as g,practical_projects as pp,signature_growth as growth
    if not run.get('objectiveId') or not complete:return None
    key=run['objectiveId'];d=OBJECTIVES[key];loot=run['loot']
    loot['crowns']+=d['crowns'];loot['food']+=d['food']
    for k,n in d['materials'].items():loot['materials'][k]=loot['materials'].get(k,0)+n
    if key in ('observe','repair') and pp.active(s,'sylva'):loot['materials']['silver-ivy']=loot['materials'].get('silver-ivy',0)+2
    s.setdefault('fieldObjectiveHistory',{})[key]=True
    for who in run['party']:g.award_advancement(s,who,'patrol-objective:'+key,1,'First completed '+d['name'].lower())
    for who,proofs in run.get('workProofs',{}).items():
        for proof in set(proofs):growth.record_work(s,who,proof,field=True)
    text=d['name']+' completed. Objective payment: '+str(d['crowns'])+' crowns, '+str(d['food'])+' provisions and '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['materials'].items())+'.'
    summary.append(text);return text


def view(s,run=None):
    result=dict(offers=[dict(id=k,**deepcopy(v)) for k,v in OBJECTIVES.items()])
    if run and run.get('objectiveId'):
        d=OBJECTIVES[run['objectiveId']]
        result.update(id=run['objectiveId'],definition=deepcopy(d),site=deepcopy(SITES[d['site']]),siteWork=deepcopy(run['siteWork']),choices=site_choices(s,run),progress=run['objectiveProgress'])
    return result
