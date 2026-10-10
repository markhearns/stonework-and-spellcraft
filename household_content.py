"""Reviewed household scenes, descriptive shared history and resident clothing.
Imported prose never resolves work, grants rewards, or changes portraits.
"""
from copy import deepcopy
import hashlib
import json
import content_packs

MAX_ACTIVE_SCENES=200

PACK_ACTIONS={'propose-content-scene','save-content-style','choose-story-pattern'}
ACTIONS=PACK_ACTIONS|{'approve-content-scene','revise-content-scene','defer-content-scene','restore-content-scene','join-content-scene','wear-content-style','restore-content-look','remove-content-style','clear-story-pattern'}


def initialize(state):
    state.setdefault('householdScenes',{})
    state.setdefault('residentStyles',{})
    state.setdefault('residentCurrentStyles',{})
    state.setdefault('residentStoryPatterns',{})


def actors(state):
    import game as g
    return [who for who in g.household_members(state) if who not in ('founder','eris','selene')]


def present(state,who):
    import game as g
    return who in actors(state) and g.character_at_castle(state,who) and g.character_at_castle(state,'founder')


def ancestry(state,who):
    label=state['people'][who]['ancestryLabel']
    return next((key for key,value in content_packs.REGISTRY.items() if value==label),None)


def source_traits(state,who):
    return list(state['people'][who].get('generationIngredients',{}).get('records',{}).values())


def matches(state,who,record):
    return content_packs.compatible(record,ancestry(state,who),source_traits(state,who))


def stamp(state):return {'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']}


def find(pack,kind,key):
    import game as g
    g.require(pack is not None,'Activate a validated content pack first.')
    g.require(isinstance(key,str),'Choose a content record.')
    result=next((r for r in pack['shared'][kind] if r['id']==key),None)
    g.require(result is not None,'That record is not in the active pack.')
    return deepcopy(result)


def context(state,who):
    """Only actual shared scene memories for this participant, never others' private scenes."""
    import equipment, public_journeys, public_life
    return (public_life.context(state,who)+public_journeys.memories(state,who)+equipment.memories(state,who)+[{'title':r['title'],'participants':[state['people'][p]['name'] for p in r['participants']],
             'conversation':r['completedText'],'on':r['completedOn']} for r in state.get('householdScenes',{}).values()
            if r['status']=='remembered' and who in r['participants']])[-8:]


def wardrobe_context(state,who):
    import character_customization as custom
    look=custom.style(state,who)
    if look:return {'name':look['name'],'components':look['garments'][:],'stylingNotes':look['colour']+'; '+look['notes'],'portraitUnchanged':True}
    key=state.get('residentCurrentStyles',{}).get(who)
    style=state.get('residentStyles',{}).get(who,{}).get(key)
    if not style:return None
    return {'name':style['name'],'components':deepcopy(style['components']),'stylingNotes':style['stylingNotes'],'portraitUnchanged':True}


def view(state):
    residents={who:{'name':state['people'][who]['name'],'present':present(state,who),'ancestry':ancestry(state,who),
         'styles':deepcopy(state.get('residentStyles',{}).get(who,{})),
         'currentStyleId':state.get('residentCurrentStyles',{}).get(who),
         'storyPattern':deepcopy(state.get('residentStoryPatterns',{}).get(who))} for who in actors(state)}
    scenes={key:{**deepcopy(r),'canJoin':all(present(state,p) for p in r['participants'])} for key,r in state.get('householdScenes',{}).items()}
    shared=[{'sceneId':key,'title':r['title'],'participants':r['participants'],'description':'Shared a conversation about '+r['title'].lower()+'. No intimacy or relationship status is presumed.'} for key,r in scenes.items() if r['status']=='remembered' and len(r['participants'])>1]
    return {'residents':residents,'scenes':scenes,'sharedHistory':shared}


def verified_requirement(state,requirement):
    """Exact known invariants only; never infer permission or a person's wishes."""
    invariants={
        'The interaction is optional and non-expiring.':'The invitation system has no expiry, obligation or refusal penalty.',
        'Any actual clothing change remains separately chosen.':'Scene responses cannot change clothing; wearing a saved style is a separate agreed action.',
        'A suitable shared reading space is available.':'The established library is available as a shared reading space.',
        'A suitable shared leisure space is established.':'The established common room is available as a shared leisure space.',
        'A suitable shared space is available.':'The established common room is available for shared conversation.'}
    if requirement=='A suitable shared reading space is available.' and 'library' not in state.get('roomFurnishings',{}):return None
    if requirement in ('A suitable shared leisure space is established.','A suitable shared space is available.') and 'common-room' not in state.get('roomFurnishings',{}):return None
    return invariants.get(requirement)


def catalogue(state,pack):
    if not pack:return {'pack':None,'residents':{}}
    return {'pack':deepcopy(state['activeContentPack']),'residents':{who:{
        'scenes':[{**deepcopy(r),'verifiedRequirements':[verified_requirement(state,t) for t in r['requirements']]} for r in pack['shared']['household-interaction'] if matches(state,who,r)],
        'garments':[deepcopy(r) for r in pack['shared']['clothing-component'] if matches(state,who,r)],
        'ensembles':[deepcopy(r) for r in pack['shared']['ensemble'] if matches(state,who,r)],
        'patterns':[deepcopy(r) for r in pack['shared']['story-development-pattern'] if matches(state,who,r)]}
        for who in actors(state)}}


def review_requirements(requirements,action,state=None):
    import game as g
    evidence=action.get('requirementEvidence',[])
    g.require(isinstance(evidence,list) and len(evidence)==len(requirements),'Record a basis for each narrative prerequisite. No prerequisites are inferred from a seed.')
    g.require(not requirements or action.get('prerequisitesReviewed') is True,'Review the prerequisites against established play first.')
    return [{'requirement':r,'reviewedBasis':verified_requirement(state,r) or g.text_value(e,300),'verifiedByRules':bool(verified_requirement(state,r))} for r,e in zip(requirements,evidence)] if state is not None else [{'requirement':r,'reviewedBasis':g.text_value(e,300)} for r,e in zip(requirements,evidence)]


def apply(state,action,pack=None):
    import game as g
    kind=action.get('type')
    if kind not in ACTIONS:return False
    initialize(state)
    if kind.endswith('content-scene') and kind!='propose-content-scene':
        key=action.get('sceneId');g.require(isinstance(key,str) and key in state['householdScenes'],'Choose a saved household invitation.')
        r=state['householdScenes'][key]
        if kind=='defer-content-scene':
            g.require(r['status']=='waiting','Only a waiting invitation can be put aside.');r['status']='deferred'
        elif kind=='restore-content-scene':
            g.require(r['status']=='deferred','That invitation is not deferred.');r['status']='waiting'
        else:
            g.require(all(present(state,p) for p in r['participants']),'Return home with every participant. The invitation will wait.')
            if kind=='revise-content-scene':
                g.require(r['status']=='draft','Only an unapproved scene can be revised.')
                title=g.text_value(action.get('title'),80)
                invitation=g.text_value(action.get('invitation'),600)
                opening=g.text_value(action.get('opening'),600)
                replies=action.get('replies')
                g.require(isinstance(replies,list) and len(replies)==len(r['choices']),'Provide one response for each saved discussion direction.')
                replies=[g.text_value(text,600) for text in replies]
                r.update(title=title,invitation=invitation,opening=opening)
                for choice,text in zip(r['choices'],replies):choice['reply']=text
            elif kind=='approve-content-scene':
                g.require(r['status']=='draft','This invitation has already been reviewed.')
                g.require(action.get('contentReviewed') is True,'Review the complete scene, responses and each participant’s independent wishes first.')
                r.update(status='waiting',approvedOn=stamp(state))
            elif kind=='join-content-scene':
                g.require(r['status']=='waiting','This invitation is not waiting; remembered scenes cannot be replayed as new events.')
                choice=action.get('choiceIndex')
                g.require(type(choice) is int and 0<=choice<len(r['choices']),'Choose one of the reviewed discussion directions.')
                if r['choices'][choice].get('kind')=='decline':
                    r.update(status='deferred',lastResponse=r['choices'][choice]['reply'])
                    return True
                r.update(status='remembered',choiceIndex=choice,completedOn=stamp(state),completedText=[r['opening'],'Discussion chosen: '+r['choices'][choice]['label'],r['choices'][choice]['reply']],
                         portraitPaths={p:state.get('assetOverrides',{}).get(p) for p in r['participants']},clothing={p:wardrobe_context(state,p) for p in r['participants']})
                import resident_bonds
                resident_bonds.award(state,r['participants'],'content-scene:'+key,r['title'],2)
                g.add_journal(state,'Shared conversation: '+r['title']+'. Resident participants build their mutual bond; no time, goods or advancement were spent.')
        return True
    who=action.get('ownerId')
    g.require(isinstance(who,str) and present(state,who),'Choose a household resident and return home together.')
    if kind in PACK_ACTIONS:
        g.require(pack is not None,'Activate a content pack for new scene, clothing or story suggestions.')
        g.require(action.get('packDigest')==(state.get('activeContentPack') or {}).get('digest'),'The active pack changed. Reload the household content choices first.')
    if kind=='propose-content-scene':
        seed=find(pack,'household-interaction',action.get('seedId'))
        people=action.get('participants')
        g.require(isinstance(people,list) and all(isinstance(p,str) for p in people) and len(set(people))==len(people) and who in people,'Choose distinct participants including the inviting resident.')
        expected={'npc-player':(1,1),'two-npcs':(2,2),'small-group':(2,3)}[seed['participants']]
        g.require(expected[0]<=len(people)<=expected[1],'Choose the number of residents required by this scene.')
        g.require(all(present(state,p) for p in people),'Every participant must be a household member at home.')
        g.require(all(matches(state,p,seed) for p in people),'This seed conflicts with a participant.')
        evidence=review_requirements(seed['requirements'],action,state)
        g.require(sum(r['status'] not in ('remembered','withdrawn') for r in state['householdScenes'].values())<MAX_ACTIVE_SCENES,'This campaign supports two hundred unresolved invitations; completed memories remain archived.')
        source=deepcopy(state['activeContentPack'])
        key=hashlib.sha256(json.dumps([source['digest'],seed['id'],sorted(people)]).encode()).hexdigest()[:24]
        g.require(key not in state['householdScenes'],'This group already has this invitation or its remembered conversation.')
        names=', '.join(state['people'][p]['name'] for p in people)
        state['householdScenes'][key]={'title':seed['label'],'invitation':seed['openingInvitation'],'opening':seed['openingInvitation'],
            'participants':people,'ownerId':who,'status':'draft','source':source,'seed':seed,'prerequisiteEvidence':evidence,'createdOn':stamp(state),
            'choices':[{'label':line,'kind':'decline' if line.lower().startswith('decline') else 'discussion','reply':(state['people'][who]['name']+' accepts the refusal without asking for a reason. “Of course. The invitation can wait.”') if line.lower().startswith('decline') else (state['people'][who]['name']+' smiles. '+['“There is room for your version of the idea, too.”','“I like a suggestion that leaves room to change our minds.”','“We need not settle everything tonight.”','“Shall we leave the next step open?”'][i%4]),'possibleNextStep':seed['possibleDevelopments'][i%len(seed['possibleDevelopments'])]} for i,line in enumerate(seed['possibleResponses'])]}
    elif kind=='save-content-style':
        styles=state['residentStyles'].get(who,{})
        g.require(len(styles)<20,'Keep at most twenty saved styles per resident.')
        g.require(action.get('anatomyReviewed') is True and action.get('residentAgreed') is True,'Review coverage, anatomy and her willingness before saving this look.')
        ids=action.get('componentIds')
        ensemble=None
        if action.get('ensembleId'):
            ensemble=find(pack,'ensemble',action['ensembleId']);g.require(matches(state,who,ensemble),'That ensemble is incompatible with this resident.')
            ids=ensemble['componentIds']
        g.require(isinstance(ids,list) and 1<=len(ids)<=12 and all(isinstance(k,str) for k in ids) and len(set(ids))==len(ids),'Choose one to twelve distinct garments.')
        parts=[find(pack,'clothing-component',key) for key in ids]
        g.require(all(matches(state,who,p) for p in parts),'A garment conflicts with this resident’s ancestry or saved traits.')
        slots=[p['slot'] for p in parts]
        g.require('dress' in slots or ('top' in slots and 'bottom' in slots),'A look needs a dress or both a top and bottom for coverage.')
        g.require(not ('dress' in slots and ('top' in slots or 'bottom' in slots)),'Choose a dress or separates, not both.')
        g.require(all(slots.count(slot)<=1 for slot in slots if slot!='accessory'),'Choose only one garment in each non-accessory slot.')
        for part in parts:
            others=[p for p in parts if p['id']!=part['id']]
            g.require(content_packs.compatible(part,ancestry(state,who),others+([ensemble] if ensemble else [])) and not any(p['slot'] in part['incompatibleSlots'] for p in others),'These garments have incompatible layers or conflicts.')
        name=g.text_value(action.get('name'),60)
        g.require(name.casefold() not in {s['name'].casefold() for s in styles.values()},'Give this resident’s style a distinct name.')
        key=hashlib.sha256(json.dumps([who,name,ids,state['activeContentPack']['digest']]).encode()).hexdigest()[:24]
        state['residentStyles'].setdefault(who,styles)
        styles[key]={'name':name,'source':deepcopy(state['activeContentPack']),'components':parts,'ensemble':ensemble,
                     'stylingNotes':g.text_value(action.get('stylingNotes') or (ensemble or {}).get('stylingNotes') or 'Worn comfortably, with appropriate coverage and room for her natural features.',600),'savedOn':stamp(state)}
    elif kind=='wear-content-style':
        key=action.get('styleId');g.require(isinstance(key,str) and key in state['residentStyles'].get(who,{}),'Choose one of her saved styles.')
        g.require(action.get('residentAgreed') is True,'Confirm this is a change she welcomes.')
        state['residentCurrentStyles'][who]=key
        import character_customization as custom, outfit_progression
        custom.clear_style(state,who)
        outfit_progression.clear_selection(state,who)
    elif kind=='restore-content-look':state['residentCurrentStyles'].pop(who,None)
    elif kind=='remove-content-style':
        key=action.get('styleId');g.require(isinstance(key,str) and key in state['residentStyles'].get(who,{}),'Choose a saved style.')
        g.require(state['residentCurrentStyles'].get(who)!=key,'Restore her established look or choose another style before removing this one.')
        del state['residentStyles'][who][key]
    elif kind=='choose-story-pattern':
        pattern=find(pack,'story-development-pattern',action.get('patternId'))
        g.require(matches(state,who,pattern),'This pattern conflicts with her traits.')
        evidence=review_requirements(pattern['requiredEstablishedFacts'],action)
        state['residentStoryPatterns'][who]={'source':deepcopy(state['activeContentPack']),'pattern':pattern,'prerequisiteEvidence':evidence}
    elif kind=='clear-story-pattern':state['residentStoryPatterns'].pop(who,None)
    return True
