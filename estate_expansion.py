"""Bounded solo residential capacity and the optional serviced annex."""
from copy import deepcopy

ROOMS={}
for i in range(1,6):
    ROOMS['gallery-suite-'+str(i)]={'name':'Gallery suite '+str(i),'capacityBeds':1,'costCrowns':18,'requiredWorkPhases':2,'region':'main'}
for i in range(1,5):
    ROOMS['upper-chamber-'+str(i)]={'name':'Upper chamber '+str(i),'capacityBeds':4,'costCrowns':36,'requiredWorkPhases':4,'region':'main'}
for i in range(1,6):
    ROOMS['annex-suite-'+str(i)]={'name':'Annex suite '+str(i),'capacityBeds':1,'costCrowns':16,'requiredWorkPhases':2,'region':'annex'}
    ROOMS['annex-chamber-'+str(i)]={'name':'Annex chamber '+str(i),'capacityBeds':4,'costCrowns':32,'requiredWorkPhases':4,'region':'annex'}
for item in ROOMS.values():
    item['illustrationIsRepresentative']=True
    item['description']=('A private one-bed room with a closing door.' if item['capacityBeds']==1 else 'Four separate beds with privacy screens, personal storage and shared reading space.')+' Basic furnishings and services are included; there is no ongoing upkeep. The illustration is a representative room study, not an exact room-specific rendering.'


def initialize(state):
    import game as g
    state.setdefault('estateAnnex',{'status':'not-started','completedWorkPhases':0,'requiredWorkPhases':5,'committedCrowns':0})
    for key in ROOMS:
        state['housingRooms'].setdefault(key,{'status':'not-started','completedWorkPhases':0,'reservedBeds':0})
        state['roomFurnishings'].setdefault(key,'oak-bench')
        state['roomDecorations'].setdefault(key,{slot:'none' for slot in g.decoration_slots(key)})
        state['savedRoomArrangements'].setdefault(key,{})


def view(state):
    import game as g
    record=state['estateAnnex'];blockers=[]
    if not g.character_at_castle(state,'founder'):blockers.append('Return home to arrange the annex.')
    if not state['livingWingCompletedOn']:blockers.append('Complete A Proper Living Wing first.')
    if 'water-guidance' not in g.character_principles(state,'founder') or 'steady-hearth-wards' not in g.character_principles(state,'founder'):blockers.append('Personally understand Water guidance and Steady hearth wards to extend basic services.')
    if state['sharedFunds']<80:blockers.append('Needs 80 shared crowns for foundations, access and services.')
    if record['status']!='not-started':blockers.append('The annex is already funded or complete.')
    return {**deepcopy(record),'costCrowns':80,'startBlockers':blockers,
        'working':record['status']=='in-progress' and state['founderAssignment']=='estate' and g.character_at_castle(state,'founder'),
        'mainMaximumResidents':25,'annexMaximumResidents':25,'soloFounderPlaces':1}


def apply(state,action):
    kind=action.get('type')
    if kind not in ('fund-annex','resume-annex','cancel-annex'):return False
    import game as g
    g.require(g.character_at_castle(state,'founder'),'Return home before arranging annex work.')
    record=state['estateAnnex']
    if kind=='fund-annex':
        reasons=view(state)['startBlockers'];g.require(not reasons,' '.join(reasons))
        state['sharedFunds']-=80;record.update(status='in-progress',committedCrowns=80,completedWorkPhases=0)
        state['founderAssignment']='estate'
        g.add_journal(state,'Funded the optional annex: 80 crowns, five assigned work phases for access and basic services. No bedroom becomes usable until separately fitted.')
    else:
        g.require(record['status']=='in-progress','There is no unfinished annex construction.')
        if kind=='resume-annex':state['founderAssignment']='estate'
        else:
            state['sharedFunds']+=record['committedCrowns'];record.update(status='not-started',committedCrowns=0,completedWorkPhases=0)
            if state['founderAssignment']=='estate':state['founderAssignment']='rest'
            g.add_journal(state,'Cancelled the unfinished annex. Exact committed crowns returned; existing castle rooms are unchanged.')
    return True


def forecast(state):
    v=view(state)
    return [('Annex access and services: +1 own construction phase.' if v['working'] else 'Annex construction paused; funded progress kept.')] if v['status']=='in-progress' else []


def resolve(state,summary):
    if not view(state)['working']:return
    import spell_support
    record=state['estateAnnex'];record['completedWorkPhases']+=1+spell_support.haste_extra(state,'founder',record['completedWorkPhases'],5,summary)
    summary.append('Annex access and services: '+str(record['completedWorkPhases'])+' / 5 own phases.')
    if record['completedWorkPhases']==5:
        record['status']='complete';state['founderAssignment']='rest'
        summary.append('The optional annex is serviced. Its five private suites and five four-bed chambers can now be fitted individually, up to 25 additional residents. Nothing requires filling it.')


def region_for(room_id):
    return ROOMS.get(room_id,{}).get('region','main')


def placement_blockers(state, who, room_id):
    if who=='founder':return []
    region=region_for(room_id)
    people={person for person,room in state['bedroomAssignments'].items() if person not in ('founder',who) and region_for(room)==region}
    people.update(r['personId'] for r in state.get('arrivalReservations',{}).values() if r['personId'] not in ('founder',who) and region_for(r['roomId'])==region)
    return ['The '+('main castle' if region=='main' else 'annex')+' has all 25 non-founder places occupied or promised.'] if len(people)>=25 else []
