"""A read-only preparation view and factual, per-visit field receipts.

Receipts are attached only after successful actions. No reward, time, equipment,
or relationship decision is made by this module. Old saves need no migration.
"""
from copy import deepcopy

FIELD_ACTIONS={'choose-encounter-method','field-spell','field-method','journey-support'}

def history(s,site,approach=None):
    paths={'hollow-road':'hollowRoad','north-watch-road':'watchRoad','stormwatch-beacon':'beaconJourney','lantern-pavilion':'lanternAdventure','old-service-road':'serviceRoad'}
    if site in ('watchtower-trail','broken-wardstones'):return s.get('patrolJourneys',{}).get(site,{}).get('outcomes',[])
    if site in paths:return s.get(paths[site],{}).get('outcomes',[])
    if site=='cinder-aqueduct':return s.get('fieldMagic',{}).get('aqueduct',{}).get('outcomes',[])
    return s.get('partyJourneys',{}).get(site,{}).get('outcomes',[])

def snapshot(s,action):
    import game as g,field_magic
    e=s.get('expedition')
    if not e and action.get('type')!='start-expedition':return None
    party=g.expedition_party(s) if e else []
    result={'expedition':deepcopy(e),'materials':dict(s['materialInventory']),'crowns':s['sharedFunds'],
            'health':{w:field_magic.vitality(s,w) for w in party},'assignments':{w:g.character_assignment(s,w) for w in g.household_members(s)},
            'known':{w:list(g.character_principles(s,w)) for w in g.household_members(s)}}
    if e:
        result['historyCount']=len(history(s,e['siteId'],e.get('chosenApproach')))
        result['party']=party
        result['discoveries']=list(g.discoveries_for(s,e['siteId']))
        if e['siteId']=='cinder-aqueduct':result['refundable']=deepcopy(field_magic.progress(s).get('pending'))
        if e['siteId']=='rainward-observatory' and e['stage']=='working':result['encounter']=g.encounter_view(s)
    return result

def new_log(s,party,before,complete=True):
    import game as g,field_magic
    return {'version':1,'completeCoverage':complete,'departureDay':s['dayNumber'],'departurePhase':s['currentDayPhase'],
            'phases':0,'committed':{},'crownsCommitted':0,'refunded':{},'crownsRefunded':0,'outcomes':[],
            'party':[{'id':w,'name':g.character_profile(s,w)['name'],'assignment':before['assignments'].get(w,'rest'),
                      'departureVitality':field_magic.vitality(s,w) if complete else None,
                      'principles':before['known'].get(w,[])} for w in party]}

def record_success(s,action,before):
    if before is None:return
    import game as g,field_magic,companion_participation as company
    kind=action.get('type');e=s.get('expedition');old=before['expedition']
    if not old:
        if e:e['logbook']=new_log(s,g.expedition_party(s),before)
        return
    log=deepcopy(old.get('logbook')) or new_log(s,before['party'],before,False)
    if kind=='advance':log['phases']+=1
    if kind in FIELD_ACTIONS:
        for key,n in before['materials'].items():
            used=n-s['materialInventory'].get(key,0)
            if used>0:log['committed'][key]=log['committed'].get(key,0)+used
        log['crownsCommitted']+=max(0,before['crowns']-s['sharedFunds'])
    new=history(s,old['siteId'],old.get('chosenApproach'))[before['historyCount']:]
    for row in new:
        r=deepcopy(row)
        if old['siteId']=='old-service-road':
            import service_road
            step=service_road.STEPS.get(r.get('stepId'),{})
            r['name']=step.get('name','Fieldwork');r['method']=step.get('choices',{}).get(r.get('methodId'),{}).get('name',r.get('text','Fieldwork'))
            r.pop('text',None)
        elif old['siteId']=='cinder-aqueduct':
            step=next((d for d in field_magic.STEPS if d['id']==r.get('stepId')),{})
            r['name']=step.get('name','Fieldwork')
        r.setdefault('name',r.get('stepId','Fieldwork').replace('-',' ').capitalize())
        r.setdefault('method',r.get('text',r.get('methodId','Patient work')))
        r.setdefault('participants',[r['actor']] if r.get('actor') else before['party'])
        log['outcomes'].append(r)
    encounter=before.get('encounter')
    if kind=='advance' and encounter and (encounter.get('progress',{}).get('pendingWork') or {}).get('remainingWorkPhases')==1:
        job=encounter['progress']['pendingWork'];c=encounter['choices'].get(job['methodId'],{})
        log['outcomes'].append({'name':encounter['step']['name'],'method':c.get('name',job['methodId']),'participants':before['party'],'stepId':encounter['step']['id']})
    if e:
        e['logbook']=log;return
    report=s.get('lastExpeditionReport')
    if not report or report.get('siteId')!=old['siteId']:return
    # The aqueduct alone explicitly refunds unfinished work on returning.
    refund=before.get('refundable')
    if refund:
        log['refunded']=deepcopy(refund.get('inputs',{}));log['crownsRefunded']=refund.get('crowns',0)
    log['completedLead']=bool(old.get('discoveryReady'))
    log['returnedPhase']=s['currentDayPhase']
    for row in log['party']:
        who=row['id'];row['returnVitality']=field_magic.vitality(s,who)
        known=row.pop('principles',[])
        row['newPrinciples']=[p for p in g.character_principles(s,who) if p not in known]
        row['assignmentNow']=g.character_assignment(s,who)
    report['logbook']=log
    food_rewards={'old-waterworks':6,'reedbank-waystation':8,'fern-nursery':12,'quarry-shelter':6,'flooded-monastery':12,'lantern-pavilion':8}
    if old['siteId'] in food_rewards and set(g.discoveries_for(s,old['siteId']))-set(before.get('discoveries',[])):
        import provisions
        amount=food_rewards[old['siteId']];provisions.add(s,amount)
        line=str(amount)+' provisions secured with this newly completed lead.'
        report['rewards'].append(line);s['lastPhaseSummary'].append(line)
    # Beacon/watch-road callbacks are already created by their resolver. Other
    # sites share the same opt-in conversation system, with per-site identities.
    if old['siteId'] not in ('stormwatch-beacon','north-watch-road'):
        company.returned(s,before['party'],log['outcomes'],log['completedLead'],site_id=old['siteId'])

def preparation(s):
    import game as g,armoury as a,field_magic
    people={}
    for who in g.household_members(s):
        mode=a.state(s)['mode'].get(who,'household');load=a.loadout(s,who)
        ids=list(dict.fromkeys(load['slots'].values()));items=a.state(s)['items']
        blockers=[]
        try:a.validate_loadout(s,who,a.loadout(s,who,'expedition'))
        except g.RuleError as error:blockers.append(str(error))
        people[who]={'vitality':field_magic.vitality(s,who),'mode':mode,'savedFieldBlockers':blockers,
            'items':[{'id':key,'name':items[key]['name'],'slots':[slot for slot,k in load['slots'].items() if k==key]} for key in ids if key in items],
            'fieldEffects':[{**deepcopy(e),'label':a.enchantment_name(e['effect'])} for e in a.effects(s,who,'expedition')],
            'hasSavedFieldItems':bool(a.loadout(s,who,'expedition')['slots'])}
    return {'people':people}

def followups(s,public):
    """Link existing earned opportunities; never reveal future scenes or award them."""
    import game as g
    report=s.get('lastExpeditionReport')
    if not report:return []
    party=report.get('participants',['founder']);rows=[]
    for e in public.get('companionParticipationView',{}).get('events',[]):
        site=e.get('siteId','stormwatch-beacon')
        if e['who'] in party and e.get('kind')=='journey' and site==report['siteId'] and not e['memory'] and not e['deferred']:
            rows.append({'label':e['title'],'detail':'Optional conversation · no time cost.','target':{'view':'characterProfile','personId':e['who'],'characterTab':'talk'},'blockers':e['blockers']})
    for row in public.get('armouryView',{}).get('signatures',[]):
        if row['who'] in party and row['stage']!='complete':rows.append({'label':row['title'],'detail':'Personal equipment request · '+row['stage']+'.','target':{'view':'armoury','personId':row['who']},'blockers':row['blockers']})
    journey=public.get('partyJourneysView',{}).get('sites',{}).get(report['siteId'])
    if journey and journey['completed'] and not journey['installed']:
        rows.append({'label':'Display '+journey['legacy'],'detail':journey['legacyText'],'target':{'view':'expeditions','siteId':report['siteId']},'blockers':[] if journey['canPlace'] else ['Restore its associated room first.']})
    log=report.get('logbook',{})
    for p in log.get('party',[]):
        for principle in p.get('newPrinciples',[]):
            recipes=[(key,d) for key,d in g.RECIPES.items() if d.get('requiredPrinciple')==principle]
            for key,d in recipes:
                if not any(r['target'].get('recipeId')==key for r in rows):rows.append({'label':d['name'],'detail':'Newly understood by '+p['name']+'. Review components and workshop requirements.','target':{'view':'workshop','recipeId':key,'personId':p['id']},'blockers':[]})
    return rows

def encounter_details(s,view):
    """Only annotate methods already exposed at the current obstacle."""
    if not view or not view.get('step'):return
    import game as g,field_magic,beacon_expedition,party_journeys
    party=g.expedition_party(s)
    for c in view['choices'].values():
        people=list(c.get('participants') or [])
        if c.get('castForm'):
            spell=beacon_expedition.caster_for(s,c) if beacon_expedition.is_active(s) else field_magic.existing_caster(s,c['castForm'])
            if spell and spell['ownerId'] not in people:people.append(spell['ownerId'])
        if c.get('ritualPrinciples') and party_journeys.active(s):
            who=party_journeys.conductor(s,c)
            if who and who not in people:people.append(who)
        if not people and c.get('scores'):
            people=[w for w,row in c['scores'].items() if row.get('qualified')][:1]
        if not people and not any(c.get(k) for k in ('castForm','ritualPrinciples','aptitude','scores')):people=party[:]
        c['actingPeople']=people
        costs=dict(c.get('inputs',{}))
        if c.get('castForm'):
            for key,n in g.SPELL_FORMS[c['castForm']]['castingInputs'].items():costs[key]=costs.get(key,0)+n
        c['reviewInputs']=costs
