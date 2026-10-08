"""Earned technical methods and one alternative room-support contribution."""
from copy import deepcopy
import public_workshop as w

ADJACENT={frozenset(('library','common-room')),frozenset(('common-room','bedchamber')),frozenset(('common-room','conservatory'))}
CRAFT_SUPPORT={'dry-parts-beside-covers','material-check-before-assembly','accessible-fitting-beside-repair'}
SCHOLARLY={'metameric-match-check','critical-prerequisite-comparison','support-node-study','datum-transfer-check','survey-uncertainty-bands','route-change-discrimination','misconception-comparison','transfer-of-understanding-trial','wet-page-evidence-recovery','backing-isolation','angle-dependent-finish-record','provenance-preserving-consolidation','shared-tool-conflict-forecast','detachable-damping-fit','beat-pattern-discrimination','curved-surface-marking-jig','inscription-spacing-reconstruction','variable-isolating-demonstration'}


def purpose_eligible(s,key,room):
    import game as g
    slug=key.removeprefix('ss-room-room-purpose-')
    if slug=='cookhouse':return s['facilityProjects']['kitchen']['status']=='complete'
    if slug=='washroom':return s['facilityProjects']['washroom']['status']=='complete' and bool(s['householdArtifactPlacements']['hearth-kettle'])
    if slug=='private-bedchamber':return room in g.HOUSING_ROOMS and g.HOUSING_ROOMS[room]['capacityBeds']==1 and g.room_available(s,room)
    if slug=='conservatory':return room=='conservatory' and g.room_available(s,room)
    if slug=='potting-room':return g.room_available(s,'conservatory')
    if slug in ('quiet-care-suite','secure-sample-room'):return any(c['status']=='ready' for c in s['containment']['chambers'].values())
    return True

def register(g):
    for key,r in w.records('perk-concept').items():g['PRACTICES'][key]={'name':r['name'],'discipline':r['disciplineTheme'],'description':r['proposedBenefit'],'requiredSkill':skill(r),'requiredRank':1}

def skill(r):return 'scholarship' if r['id'].removeprefix('ss-dev-perk-concept-') in SCHOLARLY else 'artifice'

def prerequisites(r):
    import game as g
    refs=[x['id'] for x in r['references'] if x['namespace']=='baseline']
    return [k for k in refs if k in g.PRINCIPLE_NAMES],[k for k in refs if k in g.PRACTICES]

def applicable_perk(s,who,record_id):
    for key in s['characterDevelopment'][who]['preparedPractices']:
        r=w.records('perk-concept').get(key)
        if not r:continue
        proposal=w.catalogue()['records'][r['mechanicsProposalId']]
        if proposal['effects'][0]['unit']!='eligible-artifact-work-contribution':continue
        if any(ref['id']==record_id for ref in r['references']):return r['name']
    return None

def room_support(s,who,practice):
    import game as g
    selection=s['publicWorkshop']['supports'].get(who)
    if not selection:return None
    r=w.definition(selection['recordId']);rooms=selection['rooms'];purposes=s['publicWorkshop']['roomPurposes']
    if frozenset(rooms) not in ADJACENT or not all(g.room_available(s,k) for k in rooms):return None
    if not all(purpose_eligible(s,purposes.get(k,''),k) for k in rooms):return None
    if [purposes.get(k) for k in rooms]!=[r['firstRoomPurposeId'],r['secondRoomPurposeId']]:return None
    if s['publicWorkshop']['receipts'].get(selection['evidenceId'],{}).get('status')!='complete':return None
    needed='careful-assembly' if r['id'].removeprefix('ss-room-adjacency-synergy-') in CRAFT_SUPPORT else 'archive-focus'
    if practice!=needed:return None
    assignment=g.character_assignment(s,who)
    if practice=='archive-focus' and assignment not in ('research','archive'):return None
    if practice=='careful-assembly' and assignment not in ('crafting','public-project'):return None
    return r['name']

def bonus(s,who,practice,record_id=None):
    name=room_support(s,who,practice)
    if record_id:name=applicable_perk(s,who,record_id) or name
    return {'name':name,'amount':1} if name else None

def apply(s,a):
    import game as g
    kind=a['type'];who=a.get('ownerId','founder');data=s['publicWorkshop']
    if kind in ('public-set-purpose','public-decorate-room'):
        r=w.definition(a.get('recordId'),'room-purpose' if kind=='public-set-purpose' else 'furnishing-concept');room=a.get('roomId')
        g.require(isinstance(room,str) and g.room_available(s,room),'Choose an available room.')
        g.require(a.get('fitReviewed') is True,'Review actual room fit, privacy, services, safe circulation and permission.')
        if kind=='public-set-purpose':
            g.require(purpose_eligible(s,r['id'],room),'Establish the actual restored services, one-person bedroom, garden or care capacity required by this purpose first.')
            data['roomPurposes'][room]=r['id']
        else:
            g.require(r['mechanicsProposalId'] is None,'Craft this functional fitting first.')
            data['roomDecorations'][room]=r['id']
        return True
    if kind=='public-select-support':
        if not a.get('recordId'):data['supports'].pop(who,None);return True
        r=w.definition(a['recordId'],'adjacency-synergy');g.require(r['mechanicsProposalId'] is not None,'This adjacency is descriptive and has no numerical contribution.')
        rooms=a.get('rooms');g.require(isinstance(rooms,list) and len(rooms)==2 and all(isinstance(k,str) for k in rooms) and frozenset(rooms) in ADJACENT,'Choose two connected main-wing rooms.')
        g.require(all(g.room_available(s,k) for k in rooms),'Both rooms must be available.')
        g.require([data['roomPurposes'].get(k) for k in rooms]==[r['firstRoomPurposeId'],r['secondRoomPurposeId']],'Set the matching purpose in each room first.')
        evidence=a.get('evidenceId');g.require(isinstance(evidence,str) and data['receipts'].get(evidence,{}).get('status')=='complete','Choose a completed supporting-work receipt.')
        g.require(a.get('evidenceReviewed') is True,'Review why this actual completed evidence supports this comparison.')
        data['supports'][who]={'recordId':r['id'],'rooms':rooms,'evidenceId':evidence};return True
    if kind=='public-learn-perk':
        r=w.definition(a.get('recordId'),'perk-concept');principles,practices=prerequisites(r)
        development=s['characterDevelopment'][who]
        g.require(r['id'] not in development['learnedPractices'],'This method is already learned.')
        g.require(g.skill_rank(s,who,skill(r))>=1,'Earn rank 1 in '+skill(r)+' first.')
        g.require(set(principles)<=w.knowledge(s,who) and set(practices)<=set(development['learnedPractices']),'Personally learn the prerequisite principles and practices first.')
        g.require(g.character_sheet(s,who)['availableAdvancement']>=2,'This investment needs two unspent advancement points.')
        g.require(a.get('evidenceReviewed') is True,'Review the method’s actual samples, observations and personal prerequisites.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the learning evidence.')
        w.begin(s,a,r,deepcopy(w.catalogue()['rules'][r['mechanicsProposalId']]),mode='perk',extra={'evidence':evidence});return True
    if kind=='public-use-method':
        r=w.definition(a.get('recordId'),'perk-concept');g.require(r['id'] in s['characterDevelopment'][who]['preparedPractices'],'Prepare this personally learned method in an existing practice slot.')
        obj=w.item(s,a.get('itemId'),who);g.require(not w.locked(s,obj['id']),'This object is reserved for another project.')
        g.require(a.get('evidenceReviewed') is True,'Review the actual controlled samples, permissions and limits.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the observations this method will compare.')
        rule=deepcopy(w.catalogue()['rules'][r['mechanicsProposalId']]);rule.update(workPhases=1,crowns=0,materials=[])
        w.begin(s,a,r,rule,mode='method',extra={'evidence':evidence,'hostId':obj['id'],'lockedItems':[obj['id']]});return True
    return False

def complete(s,p):
    who=p['ownerId'];r=w.definition(p['recordId'])
    if p['kind']=='perk':s['characterDevelopment'][who]['learnedPractices'].append(r['id']);return {'learnedMethod':r['id'],'evidence':p['evidence']}
    obj=w.item(s,p['hostId']);obj.setdefault('methodRecords',[]).append({'methodId':r['id'],'evidence':p['evidence'],'receiptId':p['id']})
    return {'targetId':obj['id'],'methodId':r['id'],'evidence':p['evidence']}
