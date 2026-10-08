"""Finite, funded household service and delivery agreements with named parties."""
from copy import deepcopy
import public_workshop as w

SERVICE='ss-comm-mechanics-explicit-service-agreement'
COMMISSION='ss-post-mechanics-bounded-commission-settlement'

def apply(s,a):
    import game as g
    data=s['publicWorkshop'];contracts=data.setdefault('contracts',{});kind=a['type'];who=a.get('ownerId','founder')
    if kind in ('public-order-service','public-offer-delivery'):
        client=a.get('clientId');w.actor(s,client);g.require(client!=who and a.get('partiesAgreed') is True,'Name two different actual parties who both accept these fixed terms.')
        r=w.definition(a.get('recordId'),'service-concept' if kind=='public-order-service' else 'commission-concept')
        obj=w.item(s,a.get('itemId'));g.require(not w.locked(s,obj['id']) and not any(c['status'] in ('working','awaiting-delivery') and c['itemId']==obj['id'] for c in contracts.values()),'This exact object already has reserved work or delivery.')
        g.require(obj['ownerId']==(client if kind=='public-order-service' else who),'The recorded owner must authorize this exact object.')
        g.require(obj['roomId'] is None and not obj['active'],'Stow the object before service or delivery.')
        g.require(a.get('scopeReviewed') is True,'Review this actual item against the requested scope, limits, provider ability and acceptance criteria.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the agreed scope and current condition.')
        if kind=='public-offer-delivery':
            references=[ref['id'] for ref in r['supportedWorkReferences']]
            if not references:references=[ref['id'] for ref in r['references'] if ref['id'] in w.records('artifact-concept')]
            g.require(obj['definitionId'] in references,'The owned output must match the commission’s supported work definition.')
        else:g.require(max(g.skill_rank(s,who,'artifice'),g.skill_rank(s,who,'scholarship'))>=1,'The provider needs an earned practical or scholarly rank before accepting a technical service.')
        fee=0 if obj.get('baselineForm')=='luminous-copy' else 8
        g.require(s['personalFunds'].get(client,0)>=fee,'The client needs '+str(fee)+' personal crowns; no other wallet will be charged.')
        clone=deepcopy(s);cd=clone['publicWorkshop'];key=w.number(clone,'agreement');c={'id':key,'recordId':r['id'],'name':r['name'],'ownerId':who,'clientId':client,'itemId':obj['id'],'fee':fee,'status':'awaiting-delivery','kind':'service' if kind=='public-order-service' else 'commission','evidence':evidence}
        clone['personalFunds'][client]-=fee;cd.setdefault('contracts',{})[key]=c
        if kind=='public-order-service':
            rule=deepcopy(w.catalogue()['rules'][SERVICE]);rule['crowns']=0
            w.begin(clone,a,r,rule,mode='service',extra={'contractId':key,'hostId':obj['id']})
            c['status']='working'
        s.clear();s.update(clone);return True
    if kind in ('public-deliver','public-cancel-agreement'):
        key=a.get('contractId');g.require(isinstance(key,str) and key in contracts,'Choose an accepted agreement.')
        c=contracts[key];g.require(who in (c['ownerId'],c['clientId']),'Only an actual party can settle or cancel this agreement.')
        g.require(c['status'] in ('working','awaiting-delivery'),'This agreement is already settled or cancelled.')
        if kind=='public-cancel-agreement':
            p=data['jobs'].get(c['ownerId'])
            if p and p.get('contractId')==key:
                w.return_materials(s,p,True);del data['jobs'][c['ownerId']]
                if g.character_assignment(s,c['ownerId'])=='public-project':g.set_character_assignment(s,c['ownerId'],'rest')
            s['personalFunds'][c['clientId']]+=c['fee'];c['status']='cancelled';return True
        g.require(c['status']=='awaiting-delivery' and a.get('deliveryAccepted') is True,'Complete the actual work and record the client’s acceptance first.')
        w.actor(s,c['ownerId']);w.actor(s,c['clientId']);obj=w.item(s,c['itemId'])
        g.require(obj['ownerId']==(c['clientId'] if c['kind']=='service' else c['ownerId']),'The output ownership changed; cancel and review again.')
        if c['kind']=='commission':obj['ownerId']=c['clientId'];obj['ownershipHistory'].append(c['clientId'])
        s['personalFunds'][c['ownerId']]+=c['fee'];c['status']='delivered';c['deliveredOn']={'day':s['dayNumber'],'phase':s['currentDayPhase']}
        return True
    if kind=='public-claim-baseline':
        key=a.get('recordId');g.require(isinstance(key,str) and key in g.RECIPES,'Choose a crafted baseline artifact.')
        g.require(g.spare_artifact_count(s,key)>0 and a.get('agreed') is True,'The household must agree to assign an unreserved crafted object to this owner.')
        s['craftedArtifacts'][key]-=1;object_id=w.number(s,'object')
        data['items'][object_id]={'id':object_id,'definitionId':key,'name':g.RECIPES[key]['name'],'kind':'baseline-artifact','ownerId':who,'ownershipHistory':[who],'madeBy':None,'receiptId':'household-allocation','roomId':None,'active':False,'inscriptions':[],'preparedInscription':None,'uses':[]};return True
    if kind=='public-claim-cast-output':
        spell=g.spell_by_id(s,a.get('spellId'));g.require(spell['ownerId']==who and spell['castCount']>0,'Choose this caster’s actual completed baseline casting.')
        proof=spell['id']+':'+str(spell['castCount']);used=data.setdefault('claimedCastOutputs',[]);g.require(proof not in used,'This cast’s output has already been allocated.')
        form=g.SPELL_FORMS[spell['formId']];g.require(a.get('agreed') is True,'The household must authorize transfer of the actual above-reserve output.')
        for key,n in form['materialOutput'].items():g.require(w.available(s,key)>=n,'The actual output batch is unavailable above protected reserves.')
        for key,n in form['materialOutput'].items():s['materialInventory'][key]-=n
        key=w.number(s,'object');data['items'][key]={'id':key,'definitionId':spell['formId'],'name':form['name']+' — completed batch','kind':'delivered-batch','baselineForm':spell['formId'],'ownerId':who,'ownershipHistory':[who],'madeBy':who,'receiptId':proof,'contents':deepcopy(form['materialOutput']),'roomId':None,'active':False,'inscriptions':[],'preparedInscription':None,'uses':[]};used.append(proof);return True
    return False

def complete(s,p):
    c=s['publicWorkshop']['contracts'][p['contractId']];c['status']='awaiting-delivery';obj=w.item(s,c['itemId']);obj.setdefault('serviceRecords',[]).append({'recordId':c['recordId'],'scope':c['evidence'],'receiptId':p['id']})
    return {'contractId':c['id'],'targetId':obj['id'],'acceptancePending':True}
