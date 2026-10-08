"""Actual role bindings and independent assigned phases; no implied helper."""
from copy import deepcopy
from collections import Counter
import public_workshop as w

def start(s,a):
    import game as g
    r=w.definition(a.get('recordId'),'ritual-concept');rule=deepcopy(w.catalogue()['rules'][r['mechanicsProposalId']])
    bindings=a.get('roleBindings');g.require(isinstance(bindings,list) and len(bindings)==len(r['roles']) and all(isinstance(k,str) for k in bindings),'Bind every role to an actual willing person.')
    who=a.get('ownerId');g.require(who in bindings,'The coordinator must fill an actual role.')
    g.require(a.get('participantsAgreed') is True,'Every actual participant must accept their own role and remain free to withdraw.')
    evidence=g.text_value(a.get('evidence'),600);g.require(len(evidence)>=12,'Record the physical setup, existing facts and comparison question.')
    principles=[ref['id'] for ref in r['references'] if ref['namespace']=='baseline' and ref['id'] in g.PRINCIPLE_NAMES]
    for person in set(bindings):
        w.actor(s,person);g.require(person not in s['publicWorkshop']['jobs'],'A participant already has a public project.')
    for i,person in enumerate(bindings):
        if principles:g.require(principles[min(i,len(principles)-1)] in w.knowledge(s,person),'The person in each role must have learned its required principle.')
    # Dry-run every participant reservation before committing any assignments or costs.
    clone=deepcopy(s);data=clone['publicWorkshop'];ritual_id=w.number(clone,'ritual');data.setdefault('rituals',{})[ritual_id]={'id':ritual_id,'recordId':r['id'],'name':r['name'],'roleBindings':bindings[:],'progress':{},'status':'in-progress','evidence':evidence,'crowns':rule['crowns'],'ownerId':who}
    for person,count in Counter(bindings).items():
        personal_rule=deepcopy(rule);personal_rule['workPhases']*=count
        if person!=who:personal_rule['crowns']=0
        w.begin(clone,{**a,'ownerId':person,'materials':[]},r,personal_rule,mode='ritual-part',extra={'ritualId':ritual_id,'roles':[r['roles'][i] for i,p in enumerate(bindings) if p==person]})
    s.clear();s.update(clone)

def finish(s,p):
    data=s['publicWorkshop'];ritual=data['rituals'][p['ritualId']];ritual['progress'][p['ownerId']]=p['requiredWorkPhases']
    if set(ritual['progress'])==set(ritual['roleBindings']):
        r=w.definition(ritual['recordId']);ritual['status']='complete';ritual['outcome']={'boundedPurpose':r['boundedOutcome'],'observations':ritual['evidence'],'conclusion':'No unobserved outcome, personal agreement, knowledge grant, construction or arrival is inferred.'}
    return {'ritualId':ritual['id'],'completedRoles':p['roles']}

def cancel(s,who,ritual_id=None):
    import game as g
    data=s['publicWorkshop'];p=data['jobs'].get(who)
    if ritual_id is None:
        if not p or p['kind']!='ritual-part':return False
        ritual_id=p['ritualId']
    g.require(isinstance(ritual_id,str) and ritual_id in data.get('rituals',{}),'Choose a recorded ritual.')
    ritual=data['rituals'][ritual_id]
    g.require(who in ritual['roleBindings'] and ritual['status']=='in-progress','Only a participant can withdraw from unfinished ritual work.')
    for person,job in list(data['jobs'].items()):
        if job.get('ritualId')==ritual['id']:
            w.return_materials(s,job,True);del data['jobs'][person]
            if g.character_assignment(s,person)=='public-project':g.set_character_assignment(s,person,'rest')
    s['sharedFunds']+=ritual['crowns'];ritual['status']='cancelled';ritual['returnedCrowns']=ritual['crowns'];return True
