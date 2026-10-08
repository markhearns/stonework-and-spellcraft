"""Selected public field sites: actual travel, bounded work and returned observations."""
from copy import deepcopy
import public_workshop as w

def away(s,who):
    trip=s.get('publicWorkshop',{}).get('fieldTrip')
    return bool(trip and who in trip['participants'])

def apply(s,a):
    import game as g
    kind=a['type'];data=s['publicWorkshop'];trip=data.get('fieldTrip')
    if kind=='public-start-field-trip':
        g.require(g.character_at_castle(s,'founder'),'Return home before starting another field trip.')
        g.require(a.get('ownerId')=='founder','The scholar leads public field trips.')
        g.require(not trip and s['expedition'] is None,'Return from the current expedition before beginning another.')
        r=w.definition(a.get('recordId'),'site-template');people=a.get('participants',['founder'])
        g.require(isinstance(people,list) and all(isinstance(p,str) for p in people) and people and people[0]=='founder' and len(people)<=2 and len(set(people))==len(people),'Choose the scholar and at most one actual companion.')
        for who in people:w.actor(s,who)
        g.require(a.get('scopeReviewed') is True,'Review this selected public location, safe return route, participants and existing access.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Establish the actual destination and permitted route.')
        data['fieldTrip']={'siteId':r['id'],'name':r['name'],'participants':people[:],'stage':'outbound','site':deepcopy(r),'routeEvidence':evidence,'leadId':None,'remainingWorkPhases':0,'observations':[],'encounters':[]}
        for who in people:g.set_character_assignment(s,who,'public-expedition')
        return True
    if kind in ('public-field-lead','public-field-encounter','public-return-field-trip'):
        g.require(trip is not None,'There is no public field trip underway.')
        if kind=='public-return-field-trip':
            g.require(trip['stage']!='returning','The party is already returning.');trip['stage']='returning';return True
        g.require(trip['stage'] in ('awaiting-choice','ready-to-return'),'Reach the site or finish the current activity first.')
        g.require(a.get('scopeReviewed') is True,'Review the actually observed context before selecting this activity.')
        r=w.definition(a.get('recordId'),'lead-template' if kind=='public-field-lead' else 'encounter-template')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the observed context without accepting a speculative explanation.')
        if kind=='public-field-lead':
            g.require(r['siteId']==trip['siteId'],'Choose a lead at this actual site.')
            existing=data.get('fieldDiscoveries',{}).get(trip['siteId'],[])
            g.require(r['id'] not in existing and all(o.get('leadId')!=r['id'] for o in trip['observations']),'This lead is already recorded or awaiting return.')
            trip['leadId']=r['id'];trip['choice']=None;trip['remainingWorkPhases']=1 if s.get('headquarters',{}).get('armourEquipped') and s['headquarters']['stock'].get('warded-armour',0)>0 else 2
        else:
            choice=a.get('choiceIndex');g.require(type(choice) is int and 0<=choice<len(r['approachOptions']),'Choose one of this encounter’s actual approaches.')
            g.require(r['id'] not in trip['encounters'],'This encounter was already used on this trip.')
            trip['encounters'].append(r['id']);trip['leadId']=None;trip['choice']=r['approachOptions'][choice];trip['remainingWorkPhases']=1
        trip['workRecord']=deepcopy(r);trip['workEvidence']=evidence;trip['stage']='working';return True
    return False

def resolve(s,summary):
    import game as g
    data=s['publicWorkshop'];trip=data.get('fieldTrip')
    if not trip:return
    if trip['stage']=='outbound':trip['stage']='awaiting-choice';summary.append('Arrived at '+trip['name']+'. Choose a lead, a reviewed encounter or the safe return route.')
    elif trip['stage']=='working':
        trip['remainingWorkPhases']-=1;summary.append(trip['name']+': one actual field phase completed.')
        if trip['remainingWorkPhases']==0:
            trip['observations'].append({'leadId':trip['leadId'],'recordId':trip['workRecord']['id'],'name':trip['workRecord']['name'],'evidence':trip['workEvidence'],'approach':trip.get('choice'),'candidateOutcomes':trip['workRecord'].get('possibleOutcomes',[]),'discoveryCandidates':[deepcopy(d) for d in w.records('discovery-template').values() if d.get('leadId')==trip['leadId']] if trip['leadId'] else []})
            trip['stage']='ready-to-return'
    elif trip['stage']=='returning':
        for row in trip['observations']:
            if row['leadId']:data.setdefault('fieldDiscoveries',{}).setdefault(trip['siteId'],[]).append(row['leadId'])
            key=w.number(s,'field-record');data['receipts'][key]={'id':key,'recordId':row['recordId'],'ownerId':'founder','name':row['name'],'status':'complete','observation':deepcopy(row),'day':s['dayNumber'],'phase':s['currentDayPhase']}
        data['lastFieldReport']=deepcopy(trip)
        for who in trip['participants']:
            if g.character_assignment(s,who)=='public-expedition':g.set_character_assignment(s,who,'rest')
        data['fieldTrip']=None;summary.append('Returned from '+trip['name']+'. Observations are archived; proposed interpretations grant no knowledge, loot or hidden facts.')

def view(s):
    trip=deepcopy(s['publicWorkshop'].get('fieldTrip'))
    if trip:trip['leads']=[{'id':k,'name':r['name']} for k,r in w.records('lead-template').items() if r['siteId']==trip['siteId']]
    return trip

def forecast(s):
    trip=s['publicWorkshop'].get('fieldTrip')
    if not trip:return []
    stage=trip['stage']
    text='arrive at the selected site' if stage=='outbound' else 'return home with recorded observations' if stage=='returning' else 'complete one field-work phase' if stage=='working' else 'wait for a field choice or the safe return route'
    return [trip['name']+': '+text+'.']
