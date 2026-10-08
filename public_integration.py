"""Explicit routes for every shipped content type and production/reference tools."""
from collections import Counter,defaultdict
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json
import public_workshop as w

# Reference assets have production/reference routes, not pretend game effects.
ROUTES={
 'material':('workshop','Buy, qualify and reserve actual components'),
 'property-concept':('reference','Find qualifying materials and acceptance tests'),
 'equipment-concept':('workshop','Fabricate, own, inscribe and prepare'),
 'inscription-concept':('workshop','Install and prepare, or follow the baseline focus rule'),
 'artifact-concept':('workshop','Fabricate, install and use'),
 'recipe-concept':('workshop','Fabricate the linked artifact with the same prerequisites'),
 'principle-concept':('study','Personal study with prerequisite guidance'),
 'spell-construction':('spellbook','Build, test, prepare and cast; baseline forms use the existing spellbook'),
 'spell-explanation':('reference','Read alongside the linked spell and its current rules'),
 'ritual-concept':('ritual','Assign actual roles and complete their work'),
 'augmentation-concept':('presentation','Request, try and freely remove'),
 'room-purpose':('room','Set purpose against actual capacity and services'),
 'furnishing-concept':('room','Craft functional fitting or select decorative treatment'),
 'adjacency-synergy':('room','Arrange matching rooms; numerical support only where implemented'),
 'site-template':('fieldwork','Travel, select leads, work and return'),
 'lead-template':('fieldwork','Visit its site and conduct the lead'),
 'discovery-template':('discovery','Archive actual returned observations and follow material or study links'),
 'encounter-template':('fieldwork','Choose an approach on an actual trip'),
 'care-case':('journey','Voluntary care episode with support work and unconditional exit'),
 'community-template':('neighbours','Establish a neighbour through an assigned introduction'),
 'contact-role':('neighbours','Meet a named independent contact after community introduction'),
 'service-concept':('agreement','Fund a bounded service between qualified household members'),
 'personal-arc':('journey','Joined chapter invitations, assigned work and chosen outcomes'),
 'relationship-development':('journey','Shared conversations and individually chosen developments'),
 'scene-template':('scene','Compose, review and join an optional invitation'),
 'ambient-line':('scene','Use a contextual resident aside'),
 'letter-template':('correspondence','Draft, edit and deliver once to a named household recipient'),
 'commission-concept':('agreement','Deliver an actual matching owned output once'),
 'gift-or-keepsake':('objects','Acquire and offer an actual owned gift'),
 'book-or-document':('objects','Acquire, read and discuss an owned copy'),
 'food-or-drink':('objects','Prepare and serve an actual meal once'),
 'garden-specimen':('objects','Establish and observe a conservatory specimen'),
 'curiosity':('objects','Acquire and examine an owned curiosity'),
 'room-art-brief':('production','Prepare a brief tied to an actual room and accepted reference'),
 'object-art-brief':('production','Prepare a brief tied to an owned object'),
 'wardrobe-art-brief':('production','Save compatible garments and prepare a resident-specific art brief'),
 'help-card':('reference','Contextual player help'),
 'feedback-copy':('reference','Troubleshooting guidance with suggested next action'),
 'acceptance-scenario':('qa','Execute and record an evidenced manual check; never mark a preview as passed'),
 'background-mapping':('generation','Apply bounded packages to all mapped occupations at candidate creation'),
 'starting-package-concept':('generation','New scholar or reviewed new candidate only'),
 'perk-concept':('training','Earn, prepare and use the actual method'),
 'training-opportunity':('training','Start a real two-person lesson in a referenced subject'),
 'mechanics-proposal':('rules','Fixed shipped adapter; uploaded prose never executes'),
}

@lru_cache(maxsize=1)
def foundation():
    import public_content
    pack,report,_=public_content.review_bundle(Path(__file__).parent/'content/stonework-and-spellcraft-public-packs.zip')
    return pack,report

def background_mapping(key):
    return deepcopy(next((r for r in w.records('background-mapping').values() if r['sourceOccupationId']==key),None))

def mapped_backgrounds(pack):
    rows=deepcopy(pack['shared']['occupation-background'])
    source={r['id']:r for r in foundation()[0]['shared']['occupation-background']}
    for row in rows:
        mapping=background_mapping(row['id'])
        if mapping and row==source.get(row['id']) and row['suggestedCapabilityPackageId']=='unmapped':
            # The source leaves Small story teller unresolved. Use the bounded teaching starter.
            row['suggestedCapabilityPackageId']=mapping['suggestedStartingPackageId'] or 'ss-dev-starting-package-concept-voluntary-teaching-starter'
    return rows

@lru_cache(maxsize=1)
def coverage():
    by_pack=defaultdict(Counter);unrouted=[]
    for key,r in w.catalogue()['records'].items():
        route=ROUTES.get(r['recordType'])
        if not route:unrouted.append(key)
        else:by_pack[r['packId']][route[0]]+=1
    return {'unroutedRecordIds':unrouted,'recordCount':len(w.catalogue()['records']),'contentCount':sum(r['recordType']!='mechanics-proposal' for r in w.catalogue()['records'].values()),'packs':{k:dict(v) for k,v in by_pack.items()},'routes':{k:{'workflow':v[0],'description':v[1]} for k,v in ROUTES.items()},'meaning':'A route identifies the available use of a record. Reference and production routes do not imply gameplay effects or completed artwork.'}

def apply(s,a):
    import game as g, household_content as h
    kind=a['type'];who=a.get('ownerId','founder');d=s['publicWorkshop']
    if kind=='public-edit-letter':
        letter=d['letters'].get(a.get('letterId'));g.require(letter is not None and letter['senderId']==who and letter['status']=='draft','Only the sender can edit an undelivered draft.')
        subject=g.text_value(a.get('subject'),120);body=g.text_value(a.get('body'),4000)
        letter.update(subject=subject,body=body);return True
    if kind=='public-examine-object':
        obj=w.item(s,a.get('itemId'),who);r=w.definition(obj['definitionId'])
        g.require(r['recordType'] in ('garden-specimen','curiosity','book-or-document'),'Choose a specimen, curiosity or document.')
        if r['recordType']=='book-or-document':g.require(obj.get('read'),'Read this copy before discussing it.')
        g.require(a.get('scopeReviewed') is True,'Review the actual observation without confirming an uncertain origin or magical claim.')
        note=g.text_value(a.get('evidence'),600);g.require(len(note)>=12,'Record the observation or discussion.')
        g.require(not w.locked(s,obj['id']),'Finish the work reserving this object first.')
        obj.setdefault('observations',[]).append({'text':note,'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']});return True
    if kind=='public-save-brief':
        r=w.definition(a.get('recordId'));g.require(r['recordType'] in ('room-art-brief','object-art-brief','wardrobe-art-brief'),'Choose a visual production brief.')
        g.require(a.get('scopeReviewed') is True,'Review the actual subject and its accepted reference before saving a production brief.')
        if r['recordType']=='room-art-brief':
            room=a.get('roomId');g.require(g.room_available(s,room),'Choose an available room.')
            expected=r['subjectReference']['id'];g.require(d['roomPurposes'].get(room)==expected,'Set this brief’s matching purpose in the actual room first.')
            subject={'roomId':room,'assetId':room,'name':g.ROOMS.get(room,{}).get('name',room),'acceptedReference':s['assetOverrides'].get(room,g.ORIGINAL_ASSETS.get(room)),'purposeId':expected,'installedObjects':[deepcopy(o) for o in d['items'].values() if o.get('roomId')==room]}
        elif r['recordType']=='object-art-brief':
            obj=w.item(s,a.get('itemId'),who);g.require(obj['definitionId']==r['subjectReference']['id'],'Choose an owned instance of the brief’s actual subject.')
            subject={'object':deepcopy(obj),'assetId':'public-'+obj['id'],'acceptedReference':s['assetOverrides'].get('public-'+obj['id'])}
        else:
            g.require(h.present(s,who),'Choose a present resident.');w.check_fit(s,r,who)
            subject={'personId':who,'assetId':who,'name':s['people'][who]['name'],'acceptedAppearance':s['people'][who].get('appearanceDescription',s['people'][who].get('appearance','')),'acceptedReference':s['assetOverrides'].get(who,g.ORIGINAL_ASSETS.get(who)),'currentStyle':h.wardrobe_context(s,who)}
        key=w.number(s,'art-brief');d['productionBriefs'][key]={'id':key,'recordId':r['id'],'ownerId':who,'name':r['name'],'status':'ready-for-production','subject':subject,'brief':deepcopy(r),'sourceDigest':w.catalogue()['sourceDigests'][r['packId']],'prompt':json.dumps({'actualSubject':subject,'instructions':r},ensure_ascii=False,indent=2),'artworkGenerated':False};return True
    if kind=='public-save-brief-style':
        r=w.definition(a.get('recordId'),'wardrobe-art-brief');w.check_fit(s,r,who)
        pack,report=foundation();clone=deepcopy(s);previous=clone.get('activeContentPack')
        clone['activeContentPack']=report['summary']
        h.apply(clone,{'type':'save-content-style','ownerId':who,'componentIds':r['garmentReferenceIds'],'name':r['name'],'packDigest':report['digest'],'anatomyReviewed':a.get('scopeReviewed'),'residentAgreed':a.get('agreed'),'stylingNotes':r['coverageRequirements']},pack)
        clone['activeContentPack']=previous;s.clear();s.update(clone);return True
    if kind=='public-record-qa':
        r=w.definition(a.get('recordId'),'acceptance-scenario');result=a.get('result')
        g.require(result in ('passed','failed','blocked'),'Record passed, failed or blocked after the actual check.')
        g.require(a.get('scopeReviewed') is True,'Confirm you performed this scenario or observed the stated blocker; reading it is not execution.')
        note=g.text_value(a.get('evidence'),600);g.require(len(note)>=12,'Record what was tested, observed and which environment was used.')
        key=w.number(s,'manual-qa');d['qaRuns'][key]={'id':key,'recordId':r['id'],'result':result,'evidence':note,'kind':'user-recorded-manual-check','revision':s['revision'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']};return True
    return False


def golem_appearances(pack,material):
    """Exact shipped-record mappings, never an inference from uploaded prose."""
    source={r['id']:r for r in foundation()[0]['ancestries']['golem']['appearanceDescriptions']}
    first={'clay':1,'porcelain':6,'stone':11,'wood':16,'metal':21}[material]
    ids={'golem-appearance-'+str(n).zfill(3) for n in range(first,first+5)}
    return [r for r in pack['ancestries']['golem']['appearanceDescriptions'] if r['id'] in ids and r==source.get(r['id'])]

@lru_cache(maxsize=1)
def source_stories():
    pack,_=foundation()
    return {r['id']:{**deepcopy(r),'name':r['title'],'summary':r['premise'],'recordType':'foundation-story','packId':'stonework-spellcraft-character-foundations','ancestryId':key,'ancestryRestrictions':[key],'excludedAncestries':[],'references':[],'establishedFactRequirements':[{'fact':x} for x in r['requirements']]} for key,ancestry in pack['ancestries'].items() for r in ancestry['storySeeds']}

def catalogue_view():return {**w.catalogue(),'integration':coverage(),'foundationStories':source_stories()}
