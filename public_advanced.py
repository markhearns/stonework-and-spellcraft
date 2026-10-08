"""Typed study, test, cast and reversible personal presentation adapters."""
from copy import deepcopy
import public_workshop as w

def rule_for(r):return deepcopy(w.catalogue()['rules'][r['mechanicsProposalId']])

def personal_requirements(s,r,who):
    import game as g
    required=r.get('principleIds',r.get('neighbouringPrincipleIds',[]))
    g.require(set(required)<=w.knowledge(s,who),'Personally learn the required principles first: '+', '.join(required))

def specimen(s,a,r,who):
    import game as g
    obj=w.item(s,a.get('itemId'),who)
    g.require(obj['kind']=='experiment' and obj['definitionId']==r['id'],'Choose this person’s prepared experimental setup for this exact form.')
    g.require(not w.locked(s,obj['id']),'The experimental setup is already reserved.')
    g.require(a.get('targetReviewed') is True,'Inspect the actual inert targets, component fit, permissions and scope limits.')
    return obj

def apply(s,a):
    import game as g
    kind=a['type'];who=a.get('ownerId','founder');data=s['publicWorkshop']
    if kind=='public-remove-augmentation':
        # Ending a personal trial is unconditional: no location, fee, phase, helper or explanation.
        g.require(isinstance(who,str) and who in s['people'],'Choose the person who owns this presentation trial.')
        data['augmentations'].pop(who,None)
        p=data['jobs'].get(who)
        if p and p['kind']=='augmentation':
            w.return_materials(s,p,True);s['sharedFunds']+=p['crowns'];del data['jobs'][who]
            if g.character_assignment(s,who)=='public-project':g.set_character_assignment(s,who,'rest')
        return True
    if kind=='public-start-ritual':
        import public_rituals
        public_rituals.start(s,a);return True
    if kind=='public-prepare-spells':
        ids=a.get('recordIds');g.require(isinstance(ids,list) and all(isinstance(k,str) for k in ids) and len(ids)==len(set(ids)),'Select distinct tested forms.')
        g.require(set(ids)<=set(data['testedSpells'].get(who,[])),'Test each form personally first.')
        g.require(len(ids)+len(s['preparedSpells'][who])<=g.spell_preparation_capacity(s,who),'Public and baseline forms share the existing personal preparation slots.')
        g.require(who not in data['jobs'] or data['jobs'][who]['kind']!='cast','Complete or cancel casting before changing preparation.')
        data['preparedSpells'][who]=ids[:];return True
    if kind in ('public-study','public-build-experiment','public-test-spell','public-cast','public-augment'):
        r=w.definition(a.get('recordId'))
        if kind=='public-study':
            g.require(r['recordType']=='principle-concept','Choose a principle study.')
            g.require(r['id'] not in w.knowledge(s,who),'This person already knows this principle.')
            personal_requirements(s,r,who);rule=rule_for(r)
            evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the selected experiment and its comparison question.')
            w.begin(s,a,r,rule,mode='study',extra={'evidence':evidence});return True
        if kind=='public-augment':
            g.require(r['recordType']=='augmentation-concept','Choose a reversible presentation trial.')
            g.require(who not in data['augmentations'],'End the existing trial before starting another.')
            g.require(a.get('anatomyReviewed') is True and a.get('participantRequested') is True,'The adult participant must request this exact change to their established anatomy.')
            original=g.text_value(a.get('originalAppearance'),600)
            w.begin(s,a,r,rule_for(r),extra={'originalAppearance':original});return True
        g.require(r['recordType']=='spell-construction' and r['mechanicsProposalId'],'Use the existing spellbook for the four baseline study forms.')
        personal_requirements(s,r,who);rule=rule_for(r)
        if kind=='public-build-experiment':
            rule.update(crowns=4,workPhases=2,materials=[{'materialId':None,'propertyId':p,'quantity':1,'consumption':'on-completion'} for p in ('binding','vessel')])
            g.require(a.get('targetReviewed') is True,'Review the finite inert samples and physical setup required by this exact form.')
            evidence=g.text_value(a.get('evidence'),600)
            g.require(len(evidence)>=12,'Describe the actual owned inert samples, reference and accessible stop.')
            w.begin(s,a,r,rule,mode='experiment',extra={'evidence':evidence});return True
        obj=specimen(s,a,r,who)
        extra={'lockedItems':[obj['id']],'hostId':obj['id']}
        if kind=='public-test-spell':
            g.require(r['id'] not in data['testedSpells'].get(who,[]),'This person has already tested this form.')
            rule.update(crowns=4,workPhases=2)
            w.begin(s,a,r,rule,mode='spell-test',extra=extra);return True
        g.require(r['id'] in data['testedSpells'].get(who,[]) and r['id'] in data['preparedSpells'].get(who,[]),'Personally test and prepare this exact form first.')
        if r['ordinaryOrExceptional']=='exceptional':
            g.require(a.get('exceptionalReviewed') is True,'Review this exceptional form’s specific endpoints, ownership, reference and recovery limits.')
        import public_spell_effects
        target_fields=public_spell_effects.validate(s,a,r,who,obj)
        extra.update(target_fields)
        extra['lockedItems']=list(set(extra['lockedItems']+[target_fields[k] for k in ('targetItemId','destinationItemId') if k in target_fields]+target_fields.get('targetItemIds',[])))
        w.begin(s,a,r,rule,mode='cast',extra=extra);return True
    if kind=='public-clear-trial':
        obj=w.item(s,a.get('itemId'),who);g.require(not w.locked(s,obj['id']),'Finish or cancel the reserved operation before changing its target.')
        obj['trialFinish']=None
        obj.setdefault('experimentalState',{}).pop('trialFinish',None)
        if obj['experimentalState'].get('temporaryLabel')=='attached':obj['experimentalState']['temporaryLabel']='released'
        return True
    if kind=='public-stop-experiment':
        obj=w.item(s,a.get('itemId'),who);g.require(obj['kind']=='experiment','Choose an experimental setup.')
        obj['active']=False;obj['effect']=None;return True
    import public_journeys, public_integration
    if public_journeys.apply(s,a):return True
    if public_integration.apply(s,a):return True
    import public_fieldwork
    if public_fieldwork.apply(s,a):return True
    import public_life
    if public_life.apply(s,a):return True
    import public_contracts
    if public_contracts.apply(s,a):return True
    import public_progression
    if public_progression.apply(s,a):return True
    raise g.RuleError('This public action is not implemented.')

def complete(s,p):
    data=s['publicWorkshop'];who=p['ownerId'];kind=p['kind'];r=data['journeys'][p['journeyId']]['seed'] if kind=='chapter-work' else w.definition(p['recordId'])
    if kind in ('chapter-work','community-visit','contact-meeting'):
        import public_journeys
        return public_journeys.complete(s,p)
    if kind=='ritual-part':
        import public_rituals
        return public_rituals.finish(s,p)
    if kind=='service':
        import public_contracts
        return public_contracts.complete(s,p)
    if kind in ('household-object','reading'):
        import public_life
        return public_life.complete(s,p)
    if kind=='study':
        data['knowledge'].setdefault(who,[]).append(r['id']);return {'learnedPrinciple':r['id'],'observation':p['evidence']}
    if kind=='experiment':
        key=w.owned_object(s,p,'experiment');data['items'][key].update(roomId=p['roomId'],setupEvidence=p['evidence'],effect=None)
        return {'itemId':key}
    if kind=='spell-test':
        data['testedSpells'].setdefault(who,[]).append(r['id']);return {'testedSpell':r['id'],'targetId':p['hostId']}
    if kind=='cast':
        obj=w.item(s,p['hostId']);obj['active']=True;obj['effect']={'formId':r['id'],'description':r['desiredEffect'],'limits':r['scopeLimits'],'receiptId':p['id']}
        import public_spell_effects
        transition=public_spell_effects.apply(s,p,r,obj)
        return {**transition,'effect':r['desiredEffect']}
    if kind=='augmentation':
        data['augmentations'][who]={'recordId':r['id'],'name':r['name'],'appearanceEffect':r['appearanceEffect'],'originalAppearance':p['originalAppearance'],'receiptId':p['id']}
        return {'appearanceTrial':r['id']}
    if kind in ('perk','method'):
        import public_progression
        return public_progression.complete(s,p)
    import game as g
    raise g.RuleError('This public job has no completion adapter.')
