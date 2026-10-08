"""Source-backed chapters, returned discoveries and established neighbours.
A preview is never history. Chapters require an actual joined invitation and,
where appropriate, a completed assignment before a chosen resolution is saved.
"""
from copy import deepcopy
import public_workshop as w

NARRATIVE_TYPES={'personal-arc','relationship-development','care-case'}

def initialize(s):
    d=s['publicWorkshop']
    for key in ('journeys','discoveries','communities','contacts','productionBriefs','qaRuns'):
        d.setdefault(key,{})

def stamp(s):return {'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}

def chapters(r):
    if r['recordType']=='personal-arc':
        return [{'title':c['title'],'invitation':c['optionalInvitation'],'activity':c['proposedActivity'],'requirements':c['requiredEstablishedFacts'],'possibility':c['possibleResolution'],'phases':1} for c in r['chapters']]
    if r['recordType']=='relationship-development':
        return [{'title':r['name'],'invitation':r['startingContext'],'activity':point,'requirements':[r['startingContext']],'possibility':r['possibleSharedMemory'],'phases':0} for point in r['mutualChoicePoints'][:2]]
    return [{'title':title,'invitation':r['temporaryProblem'],'activity':activity,'requirements':r['accommodationNeeds'],'possibility':r['practicalResolution'],'phases':phases} for title,activity,phases in [('Agree practical support',r['containmentJustification'],0),('Carry out the chosen comparison',r['practicalResolution'],1),('Choose what happens next',r['unconditionalRelease'],0)]]

def journey(s,a):
    import game as g
    key=a.get('journeyId');g.require(isinstance(key,str) and key in s['publicWorkshop']['journeys'],'Choose an existing story or care episode.')
    p=s['publicWorkshop']['journeys'][key]
    g.require(a.get('ownerId')==p['ownerId'],'Choose the participant who owns this episode.')
    return p

def evidence(a):
    import game as g
    g.require(a.get('scopeReviewed') is True,'Confirm these actual participants chose this activity and its established context.')
    note=g.text_value(a.get('evidence'),600)
    g.require(len(note)>=12,'Describe the actual context or chosen outcome; a possible resolution is not evidence.')
    return note

def present(s,p):
    import game as g
    for who in p['participants']:w.actor(s,who)
    g.require(p['status']=='active','Resume this episode before progressing.')

def apply(s,a):
    import game as g, household_content as h
    kind=a['type'];who=a.get('ownerId','founder');d=s['publicWorkshop']
    if kind in ('public-start-journey','public-adopt-character-story'):
        if kind=='public-adopt-character-story':
            import public_integration as integration
            source=integration.source_stories().get(a.get('recordId'));g.require(source is not None,'Choose a supplied character story seed.')
            if source['id']=='golem-story-020':
                profile=s['people'].get(who,{})
                g.require(profile.get('bodyMaterial',profile.get('generationIngredients',{}).get('bodyMaterial'))=='wood','This concern needs an actually awakened living-wood golem.')
            r={**deepcopy(source),'recordType':'personal-arc','chapters':[{'title':'Choose the question','optionalInvitation':source['openingHook'],'proposedActivity':source['premise'],'requiredEstablishedFacts':['The resident has chosen this concern; any premise or prior history actually applies.']+source['requirements'],'possibleResolution':'Choose a question to explore without assuming its outcome.'}]+[{'title':'Explore possibility '+str(n+1),'optionalInvitation':source['openingHook'],'proposedActivity':text,'requiredEstablishedFacts':['The previous discussion occurred and the resident still chooses this activity.'],'possibleResolution':'Record only the observed result, or revise the goal.'} for n,text in enumerate(source['possibleDevelopments'])] }
        else:r=w.definition(a.get('recordId'))
        g.require(r['recordType'] in NARRATIVE_TYPES,'Choose a personal arc, relationship or care episode.')
        g.require(who!='founder','Choose the resident whose concern this is.')
        w.check_fit(s,r,who);note=evidence(a)
        participants=a.get('participants',[who]);g.require(isinstance(participants,list) and all(isinstance(p,str) for p in participants) and who in participants and len(set(participants))==len(participants),'Choose distinct actual participants including the owner.')
        limit=(2,2) if r.get('participants')=='two-npcs' else (2,3) if r.get('participants')=='small-group' else (1,1)
        g.require(limit[0]<=len(participants)<=limit[1],'Choose the required number of household residents.')
        for person in participants:
            g.require(h.present(s,person),'Choose present household residents.');w.check_fit(s,r,person)
        g.require(not any(p['recordId']==r['id'] and p['ownerId']==who for p in d['journeys'].values()),'This resident already has this persistent episode.')
        requirements=[x['fact'] for x in r['establishedFactRequirements']]
        bases=h.review_requirements(requirements,{**a,'prerequisitesReviewed':a.get('scopeReviewed')})
        key=w.number(s,'journey');d['journeys'][key]={'id':key,'recordId':r['id'],'ownerId':who,'participants':participants[:],'name':r['name'],'kind':r['recordType'],'seed':deepcopy(r),'sourceDigest':w.catalogue()['sourceDigests'].get(r['packId']) or __import__('public_integration').foundation()[1]['digest'],'context':note,'prerequisiteEvidence':bases,'status':'active','chapterIndex':0,'chapters':chapters(r),'steps':[],'current':None,'createdOn':stamp(s)};return True
    if kind in ('public-pause-journey','public-resume-journey','public-end-care'):
        p=journey(s,a)
        g.require(p['status'] not in ('complete','closed'),'This episode is already concluded.')
        if kind=='public-end-care':
            g.require(p['kind']=='care-case','Choose an actual care episode.')
            job=d['jobs'].get(who)
            if job and job.get('journeyId')==p['id']:w.apply(s,{'type':'public-cancel','ownerId':who})
            current=p.get('current')
            if current:
                scene=s['householdScenes'].get(current['sceneId'])
                if scene and scene['status']!='remembered':scene['status']='withdrawn';scene['lastResponse']='Support ended by choice. No follow-up is owed.'
            p['status']='closed';p['closedOn']=stamp(s);p['closure']='Participant ended support freely; no cure, transfer or recruitment is inferred.'
        elif kind=='public-pause-journey':
            p['status']='paused'
            job=d['jobs'].get(who)
            if job and job.get('journeyId')==p['id'] and g.character_assignment(s,who)=='public-project':g.set_character_assignment(s,who,'rest')
        else:p['status']='active'
        return True
    if kind in ('public-open-chapter','public-work-chapter','public-resolve-chapter'):
        p=journey(s,a);present(s,p);chapter=p['chapters'][p['chapterIndex']]
        if kind=='public-open-chapter':
            g.require(p['current'] is None,'Join or resolve the current chapter before opening another.')
            note=evidence(a)
            bases=h.review_requirements(chapter['requirements'],{**a,'prerequisitesReviewed':a.get('scopeReviewed')})
            g.require(sum(r['status'] not in ('remembered','withdrawn') for r in s['householdScenes'].values())<h.MAX_ACTIVE_SCENES,'Complete an existing invitation before adding another; archived memories are retained.')
            key=w.number(s,'chapter-scene')
            s['householdScenes'][key]={'title':p['name']+' — '+chapter['title'],'invitation':chapter['invitation'],'opening':chapter['activity'],'participants':p['participants'][:],'ownerId':who,'journeyId':p['id'],'status':'waiting','source':{'packId':p['seed']['packId'],'packVersion':'1.0.0' if p['seed']['packId']=='stonework-spellcraft-character-foundations' else '0.1.0','digest':p['sourceDigest']},'seed':{'id':p['recordId']},'prerequisiteEvidence':bases,'createdOn':stamp(s),'approvedOn':stamp(s),'choices':[{'label':'Explore this question together','kind':'discussion','reply':'We choose to explore this question. Its result will depend on the work and choices that follow.'},{'label':'Leave this invitation for later','kind':'decline','reply':'Of course. We can leave the question open.'}]}
            p['current']={'sceneId':key,'context':note,'workReceiptId':None};return True
        cur=p['current'];g.require(cur is not None and s['householdScenes'][cur['sceneId']]['status']=='remembered','Join the chapter’s invitation before undertaking or resolving it.')
        if kind=='public-work-chapter':
            g.require(chapter['phases']>0 and cur['workReceiptId'] is None,'This chapter does not need further assigned work.')
            note=evidence(a)
            w.begin(s,{**a,'materials':[]},p['seed'],{'id':'public-chapter-work','kind':'chapter-work','crowns':0,'workPhases':chapter['phases'],'materials':[]},extra={'journeyId':p['id'],'chapterIndex':p['chapterIndex'],'evidence':note});return True
        if chapter['phases']:
            receipt=d['receipts'].get(cur['workReceiptId'],{})
            g.require(receipt.get('status')=='complete' and receipt.get('journeyId')==p['id'] and receipt.get('chapterIndex')==p['chapterIndex'],'Complete this chapter’s assigned work first.')
        note=evidence(a);choice=a.get('resolution');g.require(choice in ('continue','revise-goal','conclude'),'Choose continue, revise the goal, or conclude here.')
        p['steps'].append({'chapterIndex':p['chapterIndex'],'title':chapter['title'],**cur,'resolution':choice,'outcome':note,'on':stamp(s)})
        p['current']=None;p['chapterIndex']+=1
        if choice=='revise-goal':p['revisedGoal']=note
        if choice=='conclude' or p['chapterIndex']==len(p['chapters']):p['status']='complete';p['completedOn']=stamp(s)
        g.add_journal(s,'Chapter shared: '+p['name']+' — '+chapter['title']+'. Recorded only the chosen outcome.');return True
    if kind=='public-share-discovery':
        r=w.definition(a.get('recordId'),'discovery-template');note=evidence(a)
        receipt=d['receipts'].get(a.get('evidenceId'),{})
        g.require(receipt.get('status')=='complete' and receipt.get('observation',{}).get('leadId')==r['leadId'],'Bring this exact lead’s observations home before sharing its discovery.')
        g.require(r['id'] not in d['discoveries'],'This discovery is already archived; its original evidence is retained.')
        d['discoveries'][r['id']]={'recordId':r['id'],'receiptId':receipt['id'],'observation':note,'candidateObservation':r['observation'],'uncertainInterpretations':deepcopy(r['possibleInterpretations']),'sharedBy':who,'on':stamp(s)};return True
    if kind=='public-establish-community':
        r=w.definition(a.get('recordId'),'community-template');note=evidence(a)
        g.require(r['id'] not in d['communities'],'This neighbouring community is already established.')
        g.require(not any(j['recordId']==r['id'] for j in d['jobs'].values()),'Contact with this community is already underway.')
        w.begin(s,{**a,'materials':[]},r,{'id':'community-introduction','kind':'community-visit','crowns':0,'workPhases':2,'materials':[]},extra={'evidence':note});return True
    if kind=='public-meet-contact':
        r=w.definition(a.get('recordId'),'contact-role');note=evidence(a)
        g.require(r['communityId'] in d['communities'],'Establish contact with this community first.')
        g.require(r['id'] not in d['contacts'],'This contact already has a persistent identity.')
        g.require(not any(j['recordId']==r['id'] for j in d['jobs'].values()),'This introduction is already underway.')
        name=g.text_value(a.get('contactName'),40)
        g.require(name.casefold() not in {p['name'].casefold() for p in [*s['people'].values(),*d['contacts'].values()]},'Choose a distinct name for this independent adult contact.')
        w.begin(s,{**a,'materials':[]},r,{'id':'contact-introduction','kind':'contact-meeting','crowns':0,'workPhases':1,'materials':[]},extra={'evidence':note,'contactName':name});return True
    if kind=='public-talk-contact':
        r=w.definition(a.get('recordId'),'contact-role');contact=d['contacts'].get(r['id'])
        g.require(contact is not None,'Meet this named contact before opening a conversation.')
        note=evidence(a);choice=a.get('choiceIndex')
        topics=[r['ownAgenda'],*r['helpfulKnowledge']]
        g.require(type(choice) is int and 0<=choice<len(topics),'Choose one of this contact’s actual topics.')
        memory={'topic':topics[choice],'chosenContext':note,'on':stamp(s),'participantId':who}
        g.require(not contact.get('conversations') or contact['conversations'][-1]['topic']!=topics[choice],'Leave room between repeated questions; the previous answer remains available.')
        contact.setdefault('conversations',[]).append(memory)
        g.add_journal(s,'Spoke with '+contact['name']+' about '+topics[choice]+'. No personal mastery or recruitment granted.');return True
    if kind=='public-start-training':
        r=w.definition(a.get('recordId'),'training-opportunity');note=evidence(a)
        refs={x['id'] for x in r['references']};target=a.get('targetId');g.require(target in refs,'Choose a subject referenced by this exercise.')
        g.require(a.get('partiesAgreed') is True,'Both the learner and the actual teacher must choose this lesson.')
        g.apply_lesson_action(s,{'type':'start-lesson','learnerId':who,'teacherId':a.get('clientId'),'subjectKind':'principle','targetId':target})
        s['trainingProjects'][who].update(sourceOpportunityId=r['id'],exerciseEvidence=note);return True
    return False

def complete(s,p):
    d=s['publicWorkshop']
    if p['kind']=='chapter-work':
        episode=d['journeys'][p['journeyId']];episode['current']['workReceiptId']=p['id']
        return {'journeyId':episode['id'],'chapterIndex':p['chapterIndex'],'observations':p['evidence'],'resolutionPending':True}
    r=w.definition(p['recordId'])
    if p['kind']=='community-visit':
        d['communities'][r['id']]={'recordId':r['id'],'name':r['name'],'context':p['evidence'],'receiptId':p['id'],'establishedOn':stamp(s)}
        return {'communityId':r['id'],'contactsAvailable':[c['id'] for c in w.records('contact-role').values() if c['communityId']==r['id']]}
    d['contacts'][r['id']]={'recordId':r['id'],'communityId':r['communityId'],'name':p['contactName'],'occupation':r['occupation'],'ownAgenda':r['ownAgenda'],'context':p['evidence'],'receiptId':p['id'],'recruitmentStatus':'not-a-recruit','metOn':stamp(s)}
    return {'contactId':r['id'],'name':p['contactName']}

def memories(s,who):
    return [{'title':p['name'],'participants':p['participants'],'chapters':[{'title':x['title'],'outcome':x['outcome'],'on':x['on']} for x in p['steps']],'status':p['status']} for p in s['publicWorkshop'].get('journeys',{}).values() if who in p['participants'] and p['steps']][-6:]

def view(s):
    d=s['publicWorkshop'];result={key:deepcopy(d.get(key,{})) for key in ('discoveries','communities','contacts','productionBriefs','qaRuns')}
    result['journeys']=[{k:deepcopy(v) for k,v in p.items() if k!='seed'} for p in d.get('journeys',{}).values()]
    result['returnedDiscoveries']=[{'recordId':r['id'],'name':r['name'],'receiptId':receipt['id'],'shared':r['id'] in d.get('discoveries',{})} for receipt in d['receipts'].values() if receipt.get('status')=='complete' and receipt.get('observation',{}).get('leadId') for r in w.records('discovery-template').values() if r['leadId']==receipt['observation']['leadId']]
    return result
