"""Specialized safe chambers and independent resolution/release decisions.

Containment is not residential housing, employment, romance or recruitment.
Only two authored cases currently exist; ten chambers are an optional ceiling.
"""
from copy import deepcopy
from summoned_cast import profile

CHAMBERS = {f'{ward}-{i}': {'name':f'{"Ember" if ward=="heat" else "Quiet"} chamber {i}', 'ward':ward,
    'costCrowns':14, 'materials':{'porous-clay':2,'binding-thread':1}, 'requiredWorkPhases':2}
    for ward in ('heat','echo') for i in range(1,6)}


def candidate(who,name,age,ancestry,role,ambition,origin,principle,private,personality):
    person=profile(who,name,age,ancestry,role,'careful-assembly',ambition,origin,private)
    person.update(identitySource='authored-containment-sample',personality=personality,stayPreference='open-to-staying')
    return {'profile':person,'categoryId':'outside-encounter','categoryName':'A colleague met beyond the walls',
        'principles':[principle],'focusName':name+'’s personal working tool',
        'greeting':'“We have met under difficult circumstances. I would like our next conversation to be about something I choose.”',
        'stayText':'“I would like to try living here, with my own bed and work we agree together. That is my choice now, not repayment for help.”',
        'departureText':'“I will take my things and leave next phase. Keep our correspondence; I may visit again.”',
        'topics':{
            'intentions':{'label':'Ask about her next plans','text':'“I want to return to useful work, and decide for myself what comes next. Help did not purchase a promise.”'},
            'home':{'label':'Discuss an ordinary bedroom','text':'“An ordinary bedroom, separate from the ward chambers. A private room, please.”' if private else '“My own bed in an ordinary bedroom. Sharing a room is fine; living in a ward chamber is not what I am asking for.”'},
            'visit':{'label':'Offer a separate visit','text':'“A visit sounds good. Let us meet each other outside the circumstances that brought me here.”'}},
        'personalTopics':{'work':{'label':'Ask about her ambitions','text':'“'+ambition+' That is still what I want. A difficult chapter does not have to become my whole biography.”'},
            'company':{'label':'Offer some easy company','text':'“Sit with me a while. We can be ordinary company for an evening.”'}}}



SABINE=candidate('sabine','Sabine',22,'Vampire','archival seal engraver','Catalogue old seals without inheriting their old obligations.',
    'A vampire engraver maintaining an abandoned archive; a misbound defensive oath made her treat arriving travellers as intruders.','gentle-preservation',True,
    'Dryly witty, precise and self-possessed; dislikes inherited obligations and enjoys an honestly negotiated arrangement.')
SABINE['profile']['appearanceDescription']='Pale olive skin, dark auburn bob, hazel eyes, small visible fangs and a fitted midnight archival waistcoat over a wine-coloured blouse; mature features and a composed, mischievous expression.'
CASES={
    
    'sabine':{'candidate':SABINE,'ward':'echo','name':'The oath at the closed archive','lead':'The bindery notes identify an archive engraver whose old protective oath mistakes travellers for intruders. Warders offer safe escort to a Quiet chamber.',
        'situation':'An inherited alarm oath compels a defensive response around the old seals. The Quiet chamber isolates the oath’s trigger without changing Sabine’s preferences.',
        'requiredPrinciple':'gentle-preservation','costCrowns':12,'materials':{'moon-glass':1,'binding-thread':2},'requiredWorkPhases':3,
        'topics':{'account':'“The oath was meant to protect the collection until someone returned. They did not return. I would rather not spend another century treating visitors as a filing error.”',
            'plan':'“Preserve the actual catalogue. Separate the obsolete alarm clause from my working seal. Do not replace it with a new oath to you.”'},
        'resolution':'The obsolete alarm clause is retired while the catalogue remains intact. Sabine’s duty is resolved; neither loyalty nor romantic interest has been rewritten.'},
}


def case_definition(state,who):
    d=deepcopy(CASES[who])
    if who=='sabine' and state.get('containment',{}).get('cases',{}).get(who,{}).get('chapterOrigin')=='keeping-hearth':
        d['lead']='Sabine was intercepted at the service entrance after trying to recover a seal impression tied to her old alarm oath.'
        d['topics']['account']='“I tried to take the impression from your notes. The alarm oath follows its seals, and I wanted it back before another keeper inherited the trouble. I should have asked. The oath is real; so was my poor decision.”'
        d['topics']['plan']='“Keep the catalogue and the impression intact. Retire the obsolete alarm clause, with me checking each change. Then open the door. If we discuss living here afterward, let it be a different conversation.”'
    return d

def work_phases(state,definition):
    import resident_specialties
    return max(1,definition['requiredWorkPhases']-int(resident_specialties.active(state,'sabine')))


def initialize(state):
    state.setdefault('containment',{'chambers':{key:{'status':'sealed'} for key in CHAMBERS},
        'cases':{who:{'status':'unmet','chamberId':None,'discussedTopics':[],'conversation':[],'history':[]} for who in CASES},'project':None})


def introduced_candidates(state):
    return {who:deepcopy(definition['candidate']) for who,definition in CASES.items() if who in state.get('people',{})}


def lead_open(state,who):
    if who=='sabine' and state.get('keepingHearth',{}).get('returnChoice') in ('capture','parley'):return True
    return bool(state['livingWingCompletedOn']) and 'salvage' in state['binderyDiscoveries']


def occupied(state,chamber):
    return any(r['chamberId']==chamber for r in state['containment']['cases'].values())


def cost_blockers(state,definition):
    import game as g
    reasons=[]
    if state['sharedFunds']<definition['costCrowns']:reasons.append('Needs '+str(definition['costCrowns'])+' shared crowns.')
    for key,count in definition['materials'].items():
        if state['materialInventory'][key]-state['materialReserveTargets'][key]<count:reasons.append('Needs '+str(count)+' unreserved '+g.MATERIALS[key]['name']+'.')
    return reasons


def view(state):
    import game as g
    data=state['containment'];home=g.character_at_castle(state,'founder');project=data['project']
    chambers={}
    for key,definition in CHAMBERS.items():
        reasons=cost_blockers(state,definition)
        if not home:reasons.append('Return home to arrange this work.')
        if not state['livingWingCompletedOn']:reasons.append('Complete A Proper Living Wing first.')
        if project:reasons.append('Finish or cancel the current chamber or care project first.')
        if data['chambers'][key]['status']!='sealed':reasons.append('This chamber is already usable.')
        chambers[key]={**deepcopy(definition),'requiredWorkPhases':work_phases(state,definition),**deepcopy(data['chambers'][key]),'occupied':occupied(state,key),'buildBlockers':reasons}
    cases={}
    for who,base in CASES.items():
        definition=case_definition(state,who)
        record=data['cases'][who]
        if record['status']=='unmet' and not lead_open(state,who):continue
        reasons=cost_blockers(state,definition)
        if not home:reasons.append('Return home to agree the care project.')
        if record['status']!='contained':reasons.append('Care work requires the unresolved occupant to be present.')
        if project:reasons.append('Finish or cancel the current chamber or care project first.')
        if len(record['discussedTopics'])<2:reasons.append('Hear her account and agree the practical plan first.')
        if definition['requiredPrinciple'] not in g.character_principles(state,'founder'):reasons.append('Your scholar must learn '+g.PRINCIPLE_NAMES[definition['requiredPrinciple']]+'.')
        cases[who]={**deepcopy(record),'name':definition['candidate']['profile']['name'],'profile':deepcopy(definition['candidate']['profile']),
            'lead':definition['lead'],'situation':definition['situation'],'topics':deepcopy(definition['topics']),
            'costCrowns':definition['costCrowns'],'materials':deepcopy(definition['materials']),'requiredWorkPhases':work_phases(state,definition),
            'resolution':definition['resolution'] if record['status'] in ('safe','release-pending','released') else None,
            'careBlockers':reasons,'compatibleChambers':[key for key,c in chambers.items() if c['ward']==definition['ward'] and c['status']=='ready' and not c['occupied']]}
    return {'chambers':chambers,'cases':cases,'project':deepcopy(project),'working':bool(project and home and state['founderAssignment']=='containment'),
        'usableCapacity':sum(c['status']=='ready' for c in chambers.values()),'occupiedCapacity':sum(c['occupied'] for c in chambers.values()),'maximumCapacity':10}


def fund(state,kind,target,definition):
    state['sharedFunds']-=definition['costCrowns']
    for key,count in definition['materials'].items():state['materialInventory'][key]-=count
    state['containment']['project']={'kind':kind,'targetId':target,'completedWorkPhases':0,'requiredWorkPhases':work_phases(state,definition),
        'committedCrowns':definition['costCrowns'],'committedMaterials':deepcopy(definition['materials'])}
    state['founderAssignment']='containment'


def cancel(state):
    project=state['containment']['project']
    state['sharedFunds']+=project['committedCrowns']
    for key,count in project['committedMaterials'].items():state['materialInventory'][key]+=count
    state['containment']['project']=None
    if state['founderAssignment']=='containment':state['founderAssignment']='rest'


def apply(state,action):
    kind=action.get('type')
    if kind not in ('build-containment','resume-containment','cancel-containment','admit-containment','talk-containment','care-containment','release-containment','transfer-containment'):return False
    import game as g
    import summoning
    g.require(g.character_at_castle(state,'founder'),'Return home to discuss containment arrangements.')
    data=state['containment'];project=data['project']
    if kind=='build-containment':
        key=action.get('chamberId');g.require(isinstance(key,str) and key in CHAMBERS,'Choose an existing specialized chamber.')
        reasons=view(state)['chambers'][key]['buildBlockers'];g.require(not reasons,' '.join(reasons))
        fund(state,'chamber',key,CHAMBERS[key]);g.add_journal(state,'Funded '+CHAMBERS[key]['name']+'. '+str(data['project']['requiredWorkPhases'])+' assigned work phase(s); specialized capacity does not add residential beds.')
    elif kind in ('resume-containment','cancel-containment'):
        g.require(project is not None,'There is no unfinished chamber or care project.')
        if kind=='resume-containment':state['founderAssignment']='containment'
        else:cancel(state);g.add_journal(state,'Cancelled unfinished chamber/care work. Exact committed materials and crowns returned once; safety and history are unchanged.')
    else:
        who=action.get('characterId');g.require(isinstance(who,str) and who in CASES,'Choose a known case.')
        definition=case_definition(state,who);record=data['cases'][who]
        if kind=='admit-containment':
            g.require(record['status']=='unmet' and lead_open(state,who),'This encounter is not awaiting a first admission.')
            key=action.get('chamberId')
            g.require(isinstance(key,str) and key in view(state)['cases'][who]['compatibleChambers'],'Choose a ready, unoccupied chamber with the appropriate ward.')
            # Identity is established once; normal rooms and employment remain unavailable.
            person=deepcopy(definition['candidate']['profile']);summoning.validate_npc_profile(person)
            g.require(who not in state['people'],'This person already has a persistent identity.')
            state['people'][who]=person;g.initialize_character_records(state,who,definition['candidate']['principles'],definition['candidate']['focusName'])
            state['additionalResidents'][who]['status']='contained'
            state['residency'][who]={'residencyStatus':'contained','candidateStayDecision':'undecided','householdStayDecision':'undecided','agreedRoomId':None,'arrivals':[],'departures':[]}
            state['summoningContacts']['encounter-'+who]={'conductorId':'founder','candidateId':who,'personId':who,'categoryId':'outside-encounter','contactOrigin':'outside-encounter',
                'contactStatus':'closed','completedWorkPhases':0,'requiredWorkPhases':0,'committedCrowns':0,'committedMaterials':{},'discussedTopics':[],'conversation':[]}
            record.update(status='arrival-pending',chamberId=key)
            record['history'].append('Safe escort agreed; no membership or work agreement.')
            g.add_journal(state,person['name']+' has an agreed warder escort next Advance. '+CHAMBERS[key]['name']+' is reserved; no ordinary bed was taken.')
        elif kind=='talk-containment':
            g.require(record['status'] in ('contained','safe'),'Meet her after arrival and before departure.')
            topic=action.get('topic');g.require(isinstance(topic,str) and topic in definition['topics'],'Choose her account or proposed plan.')
            if topic not in record['discussedTopics']:
                record['discussedTopics'].append(topic);record['conversation'].append({'speaker':state['people'][who]['name'],'text':definition['topics'][topic]})
        elif kind=='care-containment':
            reasons=view(state)['cases'][who]['careBlockers'];g.require(not reasons,' '.join(reasons))
            fund(state,'care',who,definition)
            g.add_journal(state,'Agreed a practical resolution with '+state['people'][who]['name']+'. '+str(data['project']['requiredWorkPhases'])+' scholar phase(s), exact listed costs; no loyalty or romance condition.')
        elif kind=='release-containment':
            g.require(record['status']=='safe','Resolve the actual threat before ordinary release; safe transfer to specialists is separately available.')
            record['status']='release-pending';record['history'].append('Unconditional release agreed for next Advance.')
        else:
            g.require(record['status'] in ('arrival-pending','contained','safe'),'Only an expected or present occupant can transfer to the specialist refuge.')
            if project and project['kind']=='care' and project['targetId']==who:cancel(state)
            record['status']='transfer-pending';record['history'].append('Safe specialist transfer agreed; unfinished care refunded, no debt or membership condition.')
    return True


def forecast(state):
    rows=[];data=state['containment'];project=data['project']
    if project:
        import game as g
        working=g.character_at_castle(state,'founder') and state['founderAssignment']=='containment'
        rows.append('Specialized chambers · '+('+1 own work phase.' if working else 'work paused; progress kept.'))
    for who,r in data['cases'].items():
        if r['status'].endswith('-pending'):rows.append(CASES[who]['candidate']['profile']['name']+' · '+r['status'].replace('-',' ')+' next Advance; chamber remains reserved until then.')
    return rows


def resolve(state,summary):
    import game as g
    data=state['containment'];project=data['project']
    if project and g.character_at_castle(state,'founder') and state['founderAssignment']=='containment':
        project['completedWorkPhases']+=1
        summary.append('Specialized '+project['kind']+' work: '+str(project['completedWorkPhases'])+' / '+str(project['requiredWorkPhases'])+' own phases.')
        if project['completedWorkPhases']>=project['requiredWorkPhases']:
            target=project['targetId']
            if project['kind']=='chamber':
                data['chambers'][target]['status']='ready';summary.append(CHAMBERS[target]['name']+' is ready. One compatible occupant, separate from residential capacity.')
            else:
                data['cases'][target]['status']='safe';data['cases'][target]['history'].append(CASES[target]['resolution'])
                g.award_advancement(state,'founder','containment:'+target,2,'Resolved '+CASES[target]['name'].lower())
                summary.append(CASES[target]['resolution']+' Unconditional release is now available; recruitment is a separate future conversation.')
            data['project']=None;state['founderAssignment']='rest'
    for who,r in data['cases'].items():
        name=CASES[who]['candidate']['profile']['name']
        if r['status']=='arrival-pending':
            r['status']='contained';r['history'].append('Arrived safely in the compatible chamber.')
            summary.append(name+' arrived by warder escort. Food, bedding and care are provided without work or intimacy requirements.')
        elif r['status'] in ('release-pending','transfer-pending'):
            released=r['status']=='release-pending'
            r.update(status='released' if released else 'transferred',chamberId=None)
            state['residency'][who]['residencyStatus']='away';state['additionalResidents'][who]['status']='away'
            state['residency'][who]['departures'].append({'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
            state['summoningContacts']['encounter-'+who]['contactStatus']='open' if released else 'closed'
            r['history'].append('Left freely with belongings.' if released else 'Transferred safely to external specialists; no return or recruitment presumed.')
            summary.append(name+(' left freely. An ordinary correspondence and visit can be offered separately.' if released else ' transferred safely to the specialist refuge. The chamber is free; her identity and record remain.'))
