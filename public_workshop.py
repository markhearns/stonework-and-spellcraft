"""Curated public content rules. Fixed adapters; never execute uploaded proposal prose.
Every job owns its reservations and consumes one actual participant assignment.
"""
from copy import deepcopy
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json

IMPLEMENTED_KINDS={'qualification','artifact','furnishing','equipment','inscription','principle','spell','augmentation','perk','support','ritual','starter','service','commission'}

@lru_cache(maxsize=1)
def catalogue():
    data=json.loads((Path(__file__).parent/'content/public-runtime.json').read_text())
    data['supplementalRules']={'equipment-concept':{'id':'public-equipment-fabrication','kind':'equipment','crowns':6,'workPhases':2,'materials':[{'materialId':None,'propertyId':p,'quantity':1,'consumption':'on-completion'} for p in ('binding','vessel')]}}
    return data

def rule_for(r):return catalogue()['rules'].get(r.get('mechanicsProposalId')) or catalogue()['supplementalRules'].get(r['recordType'])

def records(kind):
    return {k:r for k,r in catalogue()['records'].items() if r['recordType']==kind}

def initialize(s):
    s.setdefault('publicWorkshop',{'jobs':{},'items':{},'nextNumber':1,'qualifiedMaterials':{},'materialStock':{k:8 if r['rarityBand']=='ordinary' else 4 if r['rarityBand']=='specialist' else 2 for k,r in records('material').items()},'inventory':{},'reserves':{},'receipts':{},'preparedItems':{},'roomPurposes':{},'roomDecorations':{},'knowledge':{},'testedSpells':{},'preparedSpells':{},'augmentations':{},'learnedPerks':{},'preparedPerks':{},'supports':{},'activities':{},'contracts':{},'rituals':{},'claimedCastOutputs':[],'letters':{}})

def actor(s,who,home=True):
    import game as g
    g.require(isinstance(who,str) and who in g.household_members(s) and who not in ('eris','selene'),'Choose the scholar or an actual household NPC.')
    if home:g.require(g.character_at_castle(s,who) and g.character_at_castle(s,'founder'),'Return home together first.')

def number(s,prefix):
    n=s['publicWorkshop']['nextNumber'];s['publicWorkshop']['nextNumber']+=1
    return prefix+'-'+str(n)

def definition(key,kind=None):
    import game as g
    g.require(isinstance(key,str) and key in catalogue()['records'],'Choose a known public record.')
    r=catalogue()['records'][key]
    if kind:g.require(r['recordType']==kind,'This record has a different purpose.')
    return r

def stock(s,key):
    import game as g
    return s['materialInventory'] if key in g.MATERIALS else s['publicWorkshop']['inventory']

def reserve_target(s,key):
    import game as g
    return s['materialReserveTargets'].get(key,0) if key in g.MATERIALS else s['publicWorkshop']['reserves'].get(key,0)

def available(s,key):return stock(s,key).get(key,0)-reserve_target(s,key)

def properties(s,key):
    import game as g
    if key in g.MATERIALS:return g.MATERIALS[key]['properties']
    return s['publicWorkshop']['qualifiedMaterials'].get(key,[])

def knowledge(s,who):
    import game as g
    return set(g.character_principles(s,who))|set(s['publicWorkshop']['knowledge'].get(who,[]))

def item(s,key,who=None):
    import game as g
    g.require(isinstance(key,str) and key in s['publicWorkshop']['items'],'Choose an existing owned object.')
    r=s['publicWorkshop']['items'][key]
    g.require(not r.get('vaultStored'),'Retrieve this object from the headquarters vault first.')
    if who is not None:g.require(r['ownerId']==who,'This object belongs to someone else.')
    return r

def locked(s,key):
    canonical=s.get('armoury',{}).get('items',{}).get('legacy:public:'+key)
    if canonical and canonical['location'] in ('job','vault'):return True
    return any(key in p.get('lockedItems',[]) for p in s['publicWorkshop']['jobs'].values()) or any(c['itemId']==key and c['status'] in ('working','awaiting-delivery') for c in s['publicWorkshop'].get('contracts',{}).values())

def check_fit(s,r,who):
    import game as g,household_content as h
    ancestry=h.ancestry(s,who) if who!='founder' else None
    g.require(not r['ancestryRestrictions'] or ancestry in r['ancestryRestrictions'],'This concept needs a different established ancestry.')
    g.require(ancestry not in r['excludedAncestries'],'This concept does not fit this established ancestry.')

def price(r):return {'ordinary':3,'specialist':6,'discovery':10}[r['rarityBand']]

def requirements(r,rule):
    return r.get('principleIds',[]) if rule['kind'] in ('artifact','inscription') else []

def begin(s,a,r,rule,mode=None,extra=None):
    import game as g
    w=s['publicWorkshop'];who=a.get('ownerId');actor(s,who)
    g.require(who not in w['jobs'],'Finish or cancel this person’s public workshop project first.')
    g.require(a.get('agreed') is True,'Confirm the actual worker accepts this task and its disclosed costs.')
    check_fit(s,r,who)
    needed=requirements(r,rule)
    g.require(set(needed)<=knowledge(s,who),'The maker must personally learn every required principle: '+', '.join(needed))
    room=a.get('roomId','library');g.require(isinstance(room,str) and g.room_available(s,room),'Choose an available castle room.')
    if (mode or rule['kind']) in ('artifact','equipment','inscription','qualification','study','perk','method'):
        g.require(room=='library','Use the library workbench for this fabrication, study or technical task.')
    g.require(type(rule['crowns']) is int and type(rule['workPhases']) is int and rule['workPhases']>0,'This adapter has no defined work schedule.')
    g.require(s['sharedFunds']>=rule['crowns'],'Not enough shared crowns for the disclosed cost.')
    selections=a.get('materials',[]);g.require(isinstance(selections,list) and all(isinstance(x,str) for x in selections),'Select material IDs for each input.')
    slots=[entry for entry in rule['materials'] for _ in range(entry['quantity'])]
    g.require(len(selections)==len(slots),'Select one material unit for each listed input slot.')
    for key,slot in zip(selections,slots):
        g.require(key==slot['materialId'] if slot['materialId'] else slot['propertyId'] in properties(s,key),'A selected component lacks its tested required material/property.')
    for key,count in Counter(selections).items():g.require(available(s,key)>=count,'Supply every selected component above protected reserves.')
    # Every check precedes the first mutation. The server wraps the whole action in a transaction.
    p={'id':number(s,'work'),'ownerId':who,'recordId':r['id'],'ruleId':rule['id'],'kind':mode or rule['kind'],'name':r['name'],'roomId':room,'crowns':rule['crowns'],'materials':[{'id':key,'consumption':slot['consumption']} for key,slot in zip(selections,slots)],'completedWorkPhases':0,'requiredWorkPhases':rule['workPhases'],'lockedItems':[],**(extra or {})}
    s['sharedFunds']-=p['crowns']
    for key in selections:stock(s,key)[key]-=1
    w['jobs'][who]=p;g.set_character_assignment(s,who,'public-project')
    g.add_journal(s,g.character_profile(s,who)['name']+' began '+r['name']+': '+str(p['crowns'])+' crowns reserved; '+str(p['requiredWorkPhases'])+' assigned phase(s).')

def owned_object(s,p,kind=None):
    key=number(s,'object');r=definition(p['recordId']);s['publicWorkshop']['items'][key]={'id':key,'definitionId':r['id'],'name':r['name'],'kind':kind or p['kind'],'ownerId':p['ownerId'],'ownershipHistory':[p['ownerId']],'madeBy':p['ownerId'],'receiptId':p['id'],'roomId':None,'locationRoomId':p.get('roomId','library'),'active':False,'inscriptions':[],'preparedInscription':None,'uses':[]};return key

def return_materials(s,p,all_inputs=False):
    for row in p['materials']:
        if all_inputs or row['consumption']=='not-consumed':stock(s,row['id'])[row['id']]=stock(s,row['id']).get(row['id'],0)+1

def complete(s,p):
    w=s['publicWorkshop'];kind=p['kind'];r=w['journeys'][p['journeyId']]['seed'] if kind=='chapter-work' else definition(p['recordId']);result={}
    if kind=='material-order':
        w['inventory'][r['id']]=w['inventory'].get(r['id'],0)+p['quantity'];w['qualifiedMaterials'].pop(r['id'],None)
        result.update(materialId=r['id'],quantity=p['quantity'],needsQualification=True)
    elif kind in ('artifact','equipment','furnishing'):result['itemId']=owned_object(s,p)
    elif kind=='qualification':
        mat=definition(p['materialId'],'material');w['qualifiedMaterials'][mat['id']]=list(mat['propertyIds']);result['materialId']=mat['id']
    elif kind=='inscription':
        host=item(s,p['hostId']);host['inscriptions'].append(r['id']);result['itemId']=host['id']
    else:
        import public_advanced
        result=public_advanced.complete(s,p)
    return_materials(s,p)
    w['receipts'][p['id']]={'id':p['id'],'recordId':p['recordId'],'name':p['name'],'ownerId':p['ownerId'],'status':'complete','day':s['dayNumber'],'phase':s['currentDayPhase'],**result}

def ready(s,p):
    import game as g
    if p['ownerId'] not in g.household_members(s) or not g.character_at_castle(s,p['ownerId']):return False
    if not g.room_available(s,p['roomId']):return False
    if p['kind']=='chapter-work':
        episode=s['publicWorkshop'].get('journeys',{}).get(p['journeyId'])
        if not episode or episode['status']!='active' or episode['chapterIndex']!=p['chapterIndex']:return False
        if not all(person in g.household_members(s) and g.character_at_castle(s,person) for person in episode['participants']):return False
    if p['kind']=='perk':
        import public_progression
        r=definition(p['recordId']);principles,practices=public_progression.prerequisites(r)
        if g.skill_rank(s,p['ownerId'],public_progression.skill(r))<1 or not set(principles)<=knowledge(s,p['ownerId']) or not set(practices)<=set(s['characterDevelopment'][p['ownerId']]['learnedPractices']):return False
    if p['kind']=='cast':
        r=definition(p['recordId'])
        if r['id'] not in s['publicWorkshop']['preparedSpells'].get(p['ownerId'],[]) or not set(r['principleIds'])<=knowledge(s,p['ownerId']):return False
    if p['kind']=='method' and p['recordId'] not in s['characterDevelopment'][p['ownerId']]['preparedPractices']:return False
    for key in p.get('lockedItems',[]):
        if key not in s['publicWorkshop']['items'] or item(s,key)['ownerId']!=p['ownerId']:return False
    return True

def resolve(s,summary):
    import game as g
    w=s['publicWorkshop']
    # Attended effects end with the session; they never run as offline or indefinite automation.
    for obj in w['items'].values():
        obj['active']=False
        if obj['kind']=='experiment':obj['effect']=None
    for who,p in list(w['jobs'].items()):
        if g.character_assignment(s,who)!='public-project' or not ready(s,p):continue
        contribution=1
        if p['kind']=='artifact':
            import public_progression
            support=public_progression.bonus(s,who,'careful-assembly',p['recordId'])
            contribution+=max(int(bool(s['utilityArtifactPlacements'].get('binding-press'))),int(bool(support)))
        import lasting_rituals
        if p['kind']=='artifact' and lasting_rituals.active(s,'maker-circle'):contribution+=1
        import spell_support
        if p['kind'] in ('artifact','equipment','furnishing','inscription','qualification','study','chapter-work','material-order'):
            contribution+=spell_support.haste_extra(s,who,p['completedWorkPhases'],p['requiredWorkPhases'],summary,contribution)
        p['completedWorkPhases']=min(p['requiredWorkPhases'],p['completedWorkPhases']+contribution)
        summary.append(g.character_profile(s,who)['name']+': '+p['name']+' +'+str(contribution)+' work contribution(s) in one assigned phase.')
        if p['completedWorkPhases']>=p['requiredWorkPhases']:
            complete(s,p);del w['jobs'][who];g.set_character_assignment(s,who,'rest');summary.append(p['name']+' completed. See the public workshop receipt.')

def apply(s,a):
    import game as g
    kind=a.get('type')
    if not isinstance(kind,str) or not kind.startswith('public-'):return False
    w=s['publicWorkshop'];who=a.get('ownerId','founder')
    if kind in ('public-field-lead','public-field-encounter','public-return-field-trip'):
        import public_fieldwork
        return public_fieldwork.apply(s,a)
    if kind in ('public-pause-journey','public-end-care'):
        import public_journeys
        return public_journeys.apply(s,a)
    if kind=='public-remove-augmentation':
        import public_advanced
        return public_advanced.apply(s,a)
    if kind=='public-withdraw-ritual':
        import public_rituals
        return public_rituals.cancel(s,who,a.get('ritualId'))
    if kind=='public-cancel':
        import public_rituals
        if public_rituals.cancel(s,who):return True
        g.require(isinstance(who,str) and who in s['people'],'Choose the recorded project owner.');p=w['jobs'].get(who);g.require(p is not None,'No unfinished project to cancel.')
        if p.get('contractId'):
            import public_contracts
            return public_contracts.apply(s,{'type':'public-cancel-agreement','ownerId':who,'contractId':p['contractId']})
        return_materials(s,p,True);s['sharedFunds']+=p['crowns'];w['receipts'][p['id']]={'id':p['id'],'recordId':p['recordId'],'name':p['name'],'ownerId':who,'status':'cancelled','returnedCrowns':p['crowns'],'completedWorkPhases':p['completedWorkPhases']};del w['jobs'][who]
        if g.character_assignment(s,who)=='public-project':g.set_character_assignment(s,who,'rest')
        return True
    if kind=='public-cancel-agreement':
        import public_contracts
        return public_contracts.apply(s,a)
    actor(s,who)
    if kind in ('public-resume','public-pause'):
        g.require(who in w['jobs'],'No unfinished public project.')
        if kind=='public-resume':g.require(ready(s,w['jobs'][who]),'Restore this project’s personal knowledge, earned rank, preparation, ownership and available room before resuming.')
        g.set_character_assignment(s,who,'public-project' if kind=='public-resume' else 'rest');return True
    if kind=='public-buy-material':
        r=definition(a.get('recordId'),'material');quantity=a.get('quantity',1)
        g.require(type(quantity) is int and 1<=quantity<=8,'Order between one and eight units.')
        g.require(w['materialStock'][r['id']]>=quantity,'This supplier has no further stock of that material in this campaign.')
        if r['rarityBand']=='discovery':g.require(bool(w.get('fieldDiscoveries')) or any(s.get(k) for k in ('waterworksDiscoveries','waystationDiscoveries','binderyDiscoveries','nurseryDiscoveries','observatoryDiscoveries')),'Discovery materials need an established field return.')
        import lasting_rituals
        cost=max(1,price(r)-int(lasting_rituals.active(s,'market-circle')))*quantity;g.require(s['sharedFunds']>=cost,'Not enough shared crowns.')
        s['sharedFunds']-=cost;w['materialStock'][r['id']]-=quantity;w['inventory'][r['id']]=w['inventory'].get(r['id'],0)+quantity;w['qualifiedMaterials'].pop(r['id'],None);return True
    if kind=='public-order-material':
        r=definition(a.get('recordId'),'material');quantity=a.get('quantity',1)
        g.require(type(quantity) is int and 1<=quantity<=4,'Choose one to four units for this finite order.')
        g.require(a.get('scopeReviewed') is True,'Confirm the actual supplier offers this listed batch; there is no automatic restock.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the agreed supplier and batch.')
        if r['rarityBand']=='discovery':g.require(bool(w.get('fieldDiscoveries')) or any(s.get(k) for k in ('waterworksDiscoveries','waystationDiscoveries','binderyDiscoveries','nurseryDiscoveries','observatoryDiscoveries')),'Return an actual field discovery before sourcing this material.')
        rule={'id':'bounded-material-order','kind':'material-order','crowns':price(r)*quantity+2,'workPhases':3 if r['rarityBand']=='discovery' else 2,'materials':[]}
        begin(s,{**a,'materials':[]},r,rule,extra={'quantity':quantity,'evidence':evidence});return True
    if kind=='public-set-reserve':
        r=definition(a.get('recordId'),'material');n=a.get('quantity');g.require(type(n) is int and 0<=n<=99,'Choose a reserve from zero to ninety-nine.')
        w['reserves'][r['id']]=n;return True
    if kind=='public-qualify':
        r=definition(a.get('recordId'),'material');g.require(r['id'] not in w['qualifiedMaterials'],'This material’s mapping is already qualified.')
        g.require(a.get('testsReviewed') is True,'Review the stated acceptance tests for this actual material sample.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the actual acceptance-test evidence.')
        rule=deepcopy(catalogue()['rules']['ss-mat-mechanics-reviewed-material-admission']);rule['materials']=[{'materialId':r['id'],'quantity':1,'consumption':'not-consumed','propertyId':None}]
        begin(s,a,r,rule,extra={'materialId':r['id'],'evidence':evidence});return True
    if kind=='public-start':
        r=definition(a.get('recordId'))
        if r['recordType']=='recipe-concept':r=definition(r['artifactId'],'artifact-concept')
        rule=rule_for(r)
        g.require(rule is not None and rule['kind'] in IMPLEMENTED_KINDS,'This record does not have an active workshop adapter.')
        if rule['kind'] not in ('artifact','furnishing','equipment','inscription'):raise g.RuleError('Use this record’s dedicated study, qualification or testing controls.')
        extra={}
        if rule['kind']=='inscription':
            host=item(s,a.get('itemId'),who);g.require(not locked(s,host['id']),'The host is already reserved.')
            g.require(host['definitionId'] in r['validHosts'],'Choose a compatible owned host.')
            g.require(r['id'] not in host['inscriptions'],'This host already has that inscription.')
            extra={'hostId':host['id'],'lockedItems':[host['id']]}
        begin(s,a,r,rule,extra=extra);return True
    if kind in ('public-install','public-stow','public-transfer','public-prepare-item','public-use-item'):
        obj=item(s,a.get('itemId'),who);g.require(not locked(s,obj['id']),'Finish or cancel work on this object first.')
        if kind=='public-install':
            room=a.get('roomId');g.require(isinstance(room,str) and g.room_available(s,room),'Select an available room.')
            g.require(obj['kind'] in ('artifact','furnishing'),'This item is carried rather than installed.')
            g.require(a.get('fitReviewed') is True,'Review fit, circulation, the intended location and occupant permission.')
            g.require(sum(x.get('roomId')==room for x in w['items'].values())<8 or obj['roomId']==room,'This room supports eight public fittings; stow one first.')
            obj['roomId']=room;obj['active']=False
        elif kind=='public-stow':
            obj['roomId']=None;obj['active']=False;obj['preparedInscription']=None
            if w['preparedItems'].get(who)==obj['id']:w['preparedItems'].pop(who)
        elif kind=='public-transfer':
            target=a.get('recipientId');actor(s,target);g.require(target!=who and a.get('agreed') is True,'Both owners must accept this transfer.')
            g.require(obj['roomId'] is None and not obj['active'],'Stow this item before transfer.')
            if w['preparedItems'].get(who)==obj['id']:w['preparedItems'].pop(who)
            obj['preparedInscription']=None;obj['ownerId']=target;obj['ownershipHistory'].append(target)
        elif kind=='public-prepare-item':
            g.require(obj['kind']=='equipment','Choose an owned public equipment item.')
            chosen=a.get('inscriptionId');g.require(isinstance(chosen,str) and chosen in obj['inscriptions'],'Choose an installed inscription.')
            focus=s['signatureFocuses'][who];g.require(not focus['householdLoadout'] and not focus['expeditionLoadout'],'Put aside baseline focus inscriptions before preparing a public focus.')
            if who in w['preparedItems']:item(s,w['preparedItems'][who])['preparedInscription']=None
            obj['preparedInscription']=chosen;w['preparedItems'][who]=obj['id']
        else:
            g.require(a.get('targetReviewed') is True,'Review the owned visible target, permissions and the exact operating limits.')
            target=g.text_value(a.get('target'),180)
            if obj['kind']=='equipment':
                g.require(w['preparedItems'].get(who)==obj['id'] and obj['preparedInscription'],'Prepare this item’s installed inscription first.')
                g.require(not s['signatureFocuses'][who]['householdLoadout'] and not s['signatureFocuses'][who]['expeditionLoadout'],'Put aside the baseline focus before this use.')
                r=definition(obj['preparedInscription']);effect=r['intendedFunction']
            else:
                g.require(obj['roomId'] and g.room_available(s,obj['roomId']),'Install this object in an available room first.')
                r=definition(obj['definitionId']);effect=r.get('proposedFunction') or r.get('functionalProposal')
            obj['active']=True;obj['uses']=(obj['uses']+[{'target':target,'function':effect,'day':s['dayNumber'],'phase':s['currentDayPhase']}])[-8:]
        return True
    import public_advanced
    return public_advanced.apply(s,a)

def view(s):
    import game as g
    w=s['publicWorkshop']
    import public_fieldwork, public_journeys
    counts=Counter(r['kind'] for r in catalogue()['rules'].values())
    return {**public_journeys.view(s),'implementedMechanics':sum(n for k,n in counts.items() if k in IMPLEMENTED_KINDS),'proposedMechanics':319,'fieldTrip':public_fieldwork.view(s),'lastFieldReport':deepcopy(w.get('lastFieldReport')),'actors':{who:{'name':g.character_profile(s,who)['name'],'atHome':g.character_at_castle(s,who),'assignment':g.character_assignment(s,who),'knownPrinciples':sorted(knowledge(s,who))} for who in g.household_members(s) if who not in ('eris','selene')},'jobs':deepcopy(w['jobs']),'items':deepcopy(w['items']),'inventory':deepcopy(w['inventory']),'stock':deepcopy(w['materialStock']),'qualifiedMaterials':deepcopy(w['qualifiedMaterials']),'reserves':deepcopy(w['reserves']),'receipts':list(w['receipts'].values()),'starterOptions':{k:r['name'] for k,r in records('starting-package-concept').items()},'implementedKinds':sorted(IMPLEMENTED_KINDS),'knowledge':deepcopy(w['knowledge']),'testedSpells':deepcopy(w['testedSpells']),'preparedSpells':deepcopy(w['preparedSpells']),'augmentations':deepcopy(w['augmentations']),'roomPurposeNames':{room:definition(k)['name'] for room,k in w['roomPurposes'].items()},'roomDecorationNames':{room:definition(k)['name'] for room,k in w['roomDecorations'].items()},'roomPurposes':deepcopy(w['roomPurposes']),'roomDecorations':deepcopy(w['roomDecorations']),'supports':deepcopy(w['supports']),'rituals':deepcopy(w.get('rituals',{})),'letters':deepcopy(w.get('letters',{})),'contracts':deepcopy(w.get('contracts',{})),'activities':[{k:v for k,v in a.items() if k!='seed'} for a in w['activities'].values()]}

def forecast(s):
    import game as g
    return [g.character_profile(s,who)['name']+': '+p['name']+(' +1 assigned phase.' if g.character_assignment(s,who)=='public-project' and ready(s,p) else ' paused; resume the project at home.') for who,p in s['publicWorkshop']['jobs'].items()]


def asset_slots(s):
    """Stable illustration slots follow actual object identities, not catalogue types."""
    from art_catalogue import OBJECT_ART
    return {'public-'+key:OBJECT_ART.get(obj.get('definitionId'),'/assets/placeholders/object-placeholder.svg') for key,obj in s.get('publicWorkshop',{}).get('items',{}).items()}
