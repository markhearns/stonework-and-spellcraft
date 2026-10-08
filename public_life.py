"""Owned household objects and reviewed narrative play from the public archive."""
from copy import deepcopy
import public_workshop as w

MAKABLE={'book-or-document':(6,2),'food-or-drink':(4,1),'garden-specimen':(8,2),'curiosity':(6,2),'gift-or-keepsake':(4,2)}

def apply(s,a):
    import game as g
    data=s['publicWorkshop'];who=a.get('ownerId','founder');kind=a['type']
    if kind=='public-compose-letter':
        r=w.definition(a.get('recordId'),'letter-template');recipient=a.get('clientId');w.actor(s,recipient)
        g.require(recipient!=who and a.get('scopeReviewed') is True,'Review the actual sender, different recipient, chosen wording and disclosure permission.')
        key=w.number(s,'letter');data.setdefault('letters',{})[key]={'id':key,'recordId':r['id'],'senderId':who,'recipientId':recipient,'subject':r['subject'],'body':r['body'],'status':'draft','replyDirections':deepcopy(r['replyDirections'])};return True
    if kind=='public-deliver-letter':
        key=a.get('letterId');g.require(isinstance(key,str) and key in data.get('letters',{}),'Choose a saved fictional letter.')
        letter=data['letters'][key];g.require(letter['senderId']==who and letter['status']=='draft','Only its sender can deliver this unissued letter.')
        w.actor(s,letter['recipientId']);g.require(a.get('scopeReviewed') is True,'Review the chosen message and its intended recipient before delivery.')
        letter['status']='delivered';letter['deliveredOn']={'day':s['dayNumber'],'phase':s['currentDayPhase']};return True
    if kind=='public-gift-object':
        r=w.definition(a.get('recordId'),'gift-or-keepsake');recipient=a.get('clientId');obj=w.item(s,a.get('itemId'),who)
        g.require(a.get('scopeReviewed') is True,'Review this actual owned object, the recipient’s preference and their free acceptance.')
        w.apply(s,{'type':'public-transfer','ownerId':who,'recipientId':recipient,'itemId':obj['id'],'agreed':a.get('agreed')})
        obj.setdefault('giftHistory',[]).append({'recordId':r['id'],'giverId':who,'recipientId':recipient,'day':s['dayNumber'],'phase':s['currentDayPhase']});return True
    if kind=='public-compose-scene':
        import public_content
        r=w.definition(a.get('recordId'),'scene-template');pack_id=r['packId'];digest=w.catalogue()['sourceDigests'][pack_id]
        public_content.compose_scene(s,{**a,'templateReviewed':a.get('agreed'),'prerequisitesReviewed':a.get('agreed')},{'entries':{r['id']:r},'types':{r['id']:'scene-template'}},{'packId':pack_id,'packVersion':'0.1.0','digest':digest});return True
    if kind=='public-make-household-object':
        r=w.definition(a.get('recordId'));g.require(r['recordType'] in MAKABLE,'Choose a household object, meal or specimen.')
        g.require(a.get('scopeReviewed') is True,'Review the actual supplies, existing source permissions and this modest acquisition or preparation.')
        evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the actual source and agreed materials or ingredients.')
        if r['recordType']=='food-or-drink':g.require(s['facilityProjects']['kitchen']['status']=='complete','Restore the kitchen before preparing a meal.')
        if r['recordType']=='garden-specimen':g.require(g.room_available(s,'conservatory'),'Restore the conservatory before establishing a potted specimen.')
        cost,phases=MAKABLE[r['recordType']]
        rule={'id':'household-object-provision','kind':'household-object','crowns':cost,'workPhases':phases,'materials':[]}
        w.begin(s,{**a,'materials':[]},r,rule,extra={'evidence':evidence});return True
    if kind=='public-read-object':
        obj=w.item(s,a.get('itemId'),who);r=w.definition(obj['definitionId']);g.require(r['recordType']=='book-or-document','Choose an owned public book or document.')
        g.require(not w.locked(s,obj['id']),'This copy is reserved.')
        rule={'id':'household-reading','kind':'reading','crowns':0,'workPhases':1,'materials':[]}
        w.begin(s,{**a,'materials':[]},r,rule,extra={'hostId':obj['id'],'lockedItems':[obj['id']]});return True
    if kind=='public-share-meal':
        obj=w.item(s,a.get('itemId'),who);r=w.definition(obj['definitionId']);g.require(r['recordType']=='food-or-drink' and not obj.get('consumed'),'Choose an actual unserved meal.')
        g.require(a.get('agreed') is True,'Review the diner’s current preferences and safe ingredient suitability.')
        g.require(not w.locked(s,obj['id']),'This meal is reserved.')
        obj['consumed']=True;obj['active']=False;g.add_journal(s,g.character_profile(s,who)['name']+' chose the prepared '+r['name']+'. No work or relationship bonus.');return True
    if kind=='public-save-plan':
        r=w.definition(a.get('recordId'));g.require(r['recordType']!='mechanics-proposal','Use dedicated mechanics controls instead.')
        g.require(a.get('scopeReviewed') is True,'Review the template’s established facts and fit; candidates are not accepted history.')
        notes=g.text_value(a.get('evidence'),600);g.require(len(notes)>=12,'Adapt this candidate to the actual people, objects and context.')
        w.check_fit(s,r,who);g.require(len(data['activities'])<100,'Keep at most one hundred public content plans.')
        key=w.number(s,'plan');data['activities'][key]={'id':key,'recordId':r['id'],'ownerId':who,'name':r['name'],'status':'proposed','notes':notes,'seed':deepcopy(r),'events':[]};return True
    if kind in ('public-record-event','public-defer-plan','public-restore-plan'):
        key=a.get('planId');g.require(isinstance(key,str) and key in data['activities'],'Choose an actual saved plan.')
        plan=data['activities'][key];g.require(plan['ownerId']==who,'Choose this participant’s own plan.')
        if kind=='public-defer-plan':plan['status']='deferred';return True
        if kind=='public-restore-plan':plan['status']='proposed';return True
        g.require(plan['status']!='deferred' and a.get('scopeReviewed') is True,'Restore the plan and review the actual chosen event first.')
        note=g.text_value(a.get('evidence'),600);g.require(len(note)>=12,'Record what actually occurred; unresolved possibilities remain candidates.')
        g.require(len(plan['events'])<12,'This plan already holds twelve reviewed events.')
        plan['events'].append({'text':note,'day':s['dayNumber'],'phase':s['currentDayPhase']});plan['status']='in-play'
        # Event notes deliberately do not grant resources, establish private lore, or author external players.
        return True
    if kind=='public-speak-ambient':
        r=w.definition(a.get('recordId'),'ambient-line');g.require(who!='founder','Choose the actual speaking NPC.')
        g.require(a.get('scopeReviewed') is True,'Review her voice and the actually established context.')
        g.require(data.get('lastAmbient',{}).get(who)!=r['id'],'Choose another line or leave room for quiet; do not repeat the same line consecutively.')
        data.setdefault('lastAmbient',{})[who]=r['id'];g.add_journal(s,g.character_profile(s,who)['name']+': “'+r['line']+'”');return True
    return False

def complete(s,p):
    r=w.definition(p['recordId'])
    if p['kind']=='household-object':
        key=w.owned_object(s,p,'household-object');obj=s['publicWorkshop']['items'][key];obj['sourceEvidence']=p['evidence'];obj['contentKind']=r['recordType'];return {'itemId':key}
    obj=w.item(s,p['hostId']);obj['read']=True;obj['excerpt']=r['excerpt'];return {'itemId':obj['id'],'discussionQuestion':r['discussionQuestion'],'knowledgeGranted':False}


def context(s,who):
    """Only this person's owned reading and actually delivered correspondence."""
    data=s.get('publicWorkshop',{});rows=[]
    for obj in data.get('items',{}).values():
        if obj['ownerId']==who and obj.get('read'):
            r=w.definition(obj['definitionId'])
            rows.append({'title':r['name'],'ownedReading':r['excerpt'],'discussionQuestion':r['discussionQuestion'],'observations':deepcopy(obj.get('observations',[])[-2:]),'knowledgeGranted':False})
    for letter in data.get('letters',{}).values():
        if letter['status']=='delivered' and who in (letter['senderId'],letter['recipientId']):
            rows.append({'title':letter['subject'],'letterBody':letter['body'],'senderId':letter['senderId'],'recipientId':letter['recipientId'],'on':letter['deliveredOn']})
    return rows[-4:]
