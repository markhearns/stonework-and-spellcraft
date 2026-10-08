"""A persistent four-encounter journey with two routes and a returned workshop plan."""
from copy import deepcopy
SITE='old-service-road'
DEFINITION={'id':SITE,'name':'The old service road','description':'The quarry and cistern notes meet at a neglected maintenance road. Follow its channels or orchard terraces to a roadkeeper’s shelter, and bring useful working methods home. Four connected encounters; unfinished work survives an early return.',
 'approaches':{'survey':{'name':'Follow the maintenance circuit','description':'One phase out, four encounters of one or two work phases, then one phase home. Choose between two routes; each leads to the same practical plan with different materials. No companion or special tool is required.','reward':'Return a fitted sorting-bench plan, 12 crowns and materials determined by your route and final packing choice. Returning workers earn 2 advancement once. Constructing the improvement is a separate, paid headquarters job.'}}}

def choice(name,phases,description,**kw):return dict(name=name,phases=phases,description=description,**kw)
STEPS={
 'fork':{'id':'fork','name':'The maintenance fork','description':'A shallow channel follows the lower slope; a sequence of worn steps climbs through old fruit trees. The notes describe both, but this survey will follow one. Choose a route; the material reward differs.',
  'choices':{'channel':choice('Trace the lower channel',2,'Follow the stone watercourse patiently. This route will recover two porous clay fittings.',route='channel'), 'orchard':choice('Climb the orchard terraces',2,'Measure the old retaining steps. This route will recover two silver ivy cuttings.',route='orchard'), 'current':choice('Read the flow with Water guidance',1,'Follow the lower channel using learned Water guidance. Same route and clay reward; one fewer phase.',route='channel',principle='water-guidance')}},
 'channel':{'id':'channel','name':'The silted inspection turn','description':'The channel bends beside an old inspection shelf. Loose clay fittings are dry above the waterline. A careful survey can leave the working flow undisturbed.',
  'choices':{'measure':choice('Measure from the dry edge',2,'Record the channel with ordinary tools. No special knowledge required.'),'field':choice('Use practised field measurements',1,'Fieldcraft rank 1 keeps the measurements precise without repeating the walk.',skill='fieldcraft',requiredRank=1)}},
 'orchard':{'id':'orchard','name':'The rooted terrace','description':'Silver ivy has found the joins in a low retaining wall. Follow the original dry steps and take only loose cuttings; there is no need to strip the living wall.',
  'choices':{'steps':choice('Map the surviving steps',2,'Work patiently along the dry terraces. No special knowledge required.'),'field':choice('Read the old footings',1,'Fieldcraft rank 1 distinguishes the old steps from the new root beds.',skill='fieldcraft',requiredRank=1)}},
 'shelter':{'id':'shelter','name':'The roadkeeper’s sorting bench','description':'Inside a plain shelter, a sloped sorting bench keeps wet field samples apart from dry tools. Its removable trays would be useful in your workshop. The surviving joinery, not any grand secret, is the discovery.',
  'choices':{'draw':choice('Draw the joints in daylight',2,'Copy the useful proportions by the doorway. Ordinary patient work is enough.'),'lamp':choice('Dry the measurements by lantern light',1,'A packed warming lantern helps examine the damp inner joints.',lantern=True)}},
 'packing':{'id':'packing','name':'What the field case can hold','description':'Your plan is complete. Choose one of two small bundles to carry alongside the fittings or cuttings already recorded. Neither choice loses the bench plan.',
  'choices':{'cord':choice('Pack sound binding cord',1,'Bring home three binding thread, in addition to the route materials and 12 crowns.'),'glass':choice('Pack the spare fireglass',1,'Bring home two fireglass, in addition to the route materials and 12 crowns.')}},
}

def initialize(s):s.setdefault('serviceRoad',{'completedSteps':[],'pendingWork':None,'route':None,'outcomes':[],'contributors':[],'discoveries':[]})

def available(s):
    import game as g
    return all('survey' in g.discoveries_for(s,k) for k in ('quarry-shelter','ridge-cistern'))

def hint():return 'Survey Quarry shelter and Ridge cistern, then bring both sets of notes home.'

def step(p):
    ids=['fork',p.get('route') or 'channel','shelter','packing']
    return next((STEPS[k] for k in ids if k not in p['completedSteps']),None)

def view(s):
    import game as g
    e=s['expedition']
    if not e or e['siteId']!=SITE or not e['chosenApproach']:return None
    p=s['serviceRoad'];d=step(p)
    return {'progress':deepcopy(p),'totalSteps':4,'step':deepcopy(d),'choices':{k:{**deepcopy(c),'blockers':g.encounter_choice_blockers(s,c)} for k,c in d['choices'].items()} if d else {}}

def resume(s):
    import game as g
    e=s['expedition'];p=s['serviceRoad'];d=step(p)
    if d is None:e.update(stage='ready-to-return',discoveryReady=True)
    elif p['pendingWork'] and not g.encounter_choice_blockers(s,d['choices'][p['pendingWork']['methodId']]):e.update(stage='working',remainingWorkPhases=p['pendingWork']['remainingWorkPhases'])
    else:e['stage']='encounter-choice'
    g.add_journal(s,'Resumed the old service road. Completed encounters and unfinished work are retained.')

def apply(s,a):
    e=s['expedition']
    if a.get('type')!='choose-encounter-method' or not e or e['siteId']!=SITE:return False
    import game as g
    g.require(e['stage']=='encounter-choice','Complete or pause the current field work first.')
    p=s['serviceRoad'];d=step(p);method=a.get('methodId')
    g.require(d is not None and isinstance(method,str) and method in d['choices'],'Choose a method for this encounter.')
    c=d['choices'][method];blockers=g.encounter_choice_blockers(s,c);g.require(not blockers,' '.join(blockers))
    import field_magic
    field_magic.commit_existing(s,c)
    p['pendingWork']={'stepId':d['id'],'methodId':method,'remainingWorkPhases':c['phases'],'magicPaid':c.get('castForm')}
    e.update(stage='working',remainingWorkPhases=c['phases'])
    g.add_journal(s,d['name']+': '+c['name']+'. '+str(c['phases'])+' work phase(s).')
    return True

def resolve(s):
    import game as g
    e=s['expedition'];p=s['serviceRoad'];party=g.expedition_party(s)
    if e['stage']=='working':
        job=p['pendingWork'];d=step(p);c=d['choices'][job['methodId']]
        for who in party:
            if who not in p['contributors']:p['contributors'].append(who)
        job['remainingWorkPhases']-=1;e['remainingWorkPhases']=job['remainingWorkPhases']
        text=d['name']+': '+str(job['remainingWorkPhases'])+' phase(s) remain.'
        if not job['remainingWorkPhases']:
            if c.get('route'):p['route']=c['route']
            p['completedSteps'].append(d['id']);p['outcomes'].append({'stepId':d['id'],'methodId':job['methodId'],'text':d['name']+' — '+c['name']})
            p['pendingWork']=None
            complete=step(p) is None;e.update(stage='ready-to-return' if complete else 'encounter-choice',discoveryReady=complete)
            text=d['name']+' completed. '+('The plan is ready to bring home.' if complete else 'Choose the next method when ready.')
    else:
        rewards=[]
        if e['discoveryReady'] and 'survey' not in p['discoveries']:
            p['discoveries'].append('survey')
            materials={'porous-clay':2} if p['route']=='channel' else {'silver-ivy':2}
            packing=next(r['methodId'] for r in p['outcomes'] if r['stepId']=='packing')
            materials.update({'binding-thread':3} if packing=='cord' else {'fireglass':2})
            for key,n in materials.items():s['materialInventory'][key]+=n
            rewards=[g.distribute_expedition_wealth(s,12),', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in materials.items())+' deposited in shared stores.','The sorting-bench plan is in the archive. Restore the workshop, then fit it as a separate headquarters job: 18 crowns, two phases, +1 core artifact work per assigned maker at home.']
            import resident_specialties
            resident_specialties.field_reward(s,rewards)
            for who in party:
                if who in p['contributors']:g.award_advancement(s,who,SITE+':survey',2,'Worked on and returned the old service road survey')
        else:rewards=['Returned safely. Completed encounters and unfinished field work are saved; no field rewards were deposited.']
        if e['restoreLanternDisplay']:s['lanternDisplayed']=True
        s['lastExpeditionReport']={'siteId':SITE,'approach':e['chosenApproach'],'returnedDay':s['dayNumber'],'participants':party[:],'rewards':rewards}
        for who in party:g.set_character_assignment(s,who,'rest')
        s['expedition']=None
        if 'steady-hearth-wards' in s['archivePrinciples'] and 'steady-hearth-wards' not in s['founderKnownPrinciples']:
            g.learn_principle(s,'steady-hearth-wards');g.award_advancement(s,'founder','hearth-understood',1,'Understood steady hearth wards')
        text='Your scholar returned safely. '+' '.join(rewards)
    s['lastPhaseSummary']=[line for line in s['lastPhaseSummary'] if not line.startswith('A restful phase.')]
    s['lastPhaseSummary'].append(text);g.add_journal(s,text)

def register(g):
    g['EXPEDITION_SITES'][SITE]=DEFINITION
    import headquarters as h
    h.JOBS['sorting-bench']={'name':'Fit the roadkeeper’s sorting bench','room':'workshop','cost':18,'phases':2,'output':'sorting-bench','benefit':'A plan for removable sample trays. Install it once to add +1 work per phase to core artifact crafting by each assigned maker at home.'}
