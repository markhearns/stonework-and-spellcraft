"""Versioned character ingredients, compatible selections and offline prose.
Only mechanical packages grant capabilities. Selection is stable per request.
"""
from copy import deepcopy
from collections import Counter
import hashlib
import random
import json

VERSION=3
COMMON_ANCESTRIES=('Human','High elf','Dark elf','Drow','Catfolk','Bovinefolk','Orc','Wolfkin','Ogrekin')
GOLEM_MATERIALS={
 'clay':{'name':'Warm clay','appearance':'warm terracotta ceramic with softly burnished surfaces','costCrowns':32,'materials':{'porous-clay':4,'binding-thread':2,'moon-glass':1}},
 'porcelain':{'name':'Glazed porcelain','appearance':'ivory porcelain with fine violet glaze lines and restrained gold repairs','costCrowns':40,'materials':{'porous-clay':3,'fireglass':2,'binding-thread':2,'moon-glass':1}},
 'stone':{'name':'Carved stone','appearance':'smooth charcoal stone with faint mineral veins','costCrowns':36,'materials':{'porous-clay':3,'fireglass':1,'binding-thread':2,'moon-glass':2}},
 'wood':{'name':'Living wood','appearance':'warm wood grain and subtle leaf-veined inlays','costCrowns':34,'materials':{'silver-ivy':4,'binding-thread':3,'moon-glass':1}},
 'metal':{'name':'Enchanted metal','appearance':'dark brushed metal with worn brass joints and softly etched details','costCrowns':44,'materials':{'fireglass':3,'binding-thread':3,'moon-glass':2}},
}

def arrival_method(ancestry):
    return 'construction' if ancestry=='Golem' else 'recruitment' if ancestry in COMMON_ANCESTRIES else 'summoning'
ANCESTRIES={
 'Bovinefolk':{'detail':'bovine horns, bovine ears and a slender tufted tail, a human face and smooth human skin without body fur','backgrounds':['bookbinder','glassworker','gardener','waterkeeper','conservator']},
 'Orc':{'detail':'small tusks, strong features and an enduring sturdy physique','backgrounds':['bookbinder','lampwright','glassworker','courier','waterkeeper','mapmaker']},
 'Wolfkin':{'detail':'exactly two expressive wolf ears on top of the head and a fluffy wolf tail, a human face and smooth human skin; no human side ears, hair covers the sides of the head','backgrounds':['bookbinder','courier','gardener','mapmaker','conservator']},
 'Ogrekin':{'detail':'two strong horns and a powerful imposing frame with mature generous curves and a large bust','backgrounds':['lampwright','glassworker','bookbinder','waterkeeper','conservator']},
 'Human':{'detail':'individual, wholly human features','backgrounds':['bookbinder','lampwright','glassworker','courier','gardener','waterkeeper','mapmaker','conservator']},
 'High elf':{'detail':'long pointed ears and woodland-inspired personal adornments','backgrounds':['bookbinder','gardener','waterkeeper','mapmaker','conservator']},
 'Dark elf':{'detail':'elegant pointed ears and fine expressive features','backgrounds':['bookbinder','lampwright','glassworker','courier','mapmaker','conservator']},
 'Drow':{'detail':'pointed ears, luminous eyes adapted to subterranean light, and silvery hair accents','backgrounds':['bookbinder','lampwright','glassworker','waterkeeper','mapmaker','conservator']},
 'Catfolk':{'detail':'exactly two expressive feline ears on top of the head and a softly furred tail; no human side ears, hair covers the sides of the head','backgrounds':['bookbinder','lampwright','courier','gardener','mapmaker','conservator']},
 'Kitsune':{'detail':'exactly two fox ears on top of the head and one luxuriant fox tail; no human side ears, hair covers the sides of the head; tail count conveys no free magical power','backgrounds':['bookbinder','lampwright','glassworker','courier','gardener','mapmaker']},
 'Golem':{'detail':'a carefully crafted adult feminine form with fine visible maker’s joins','backgrounds':['bookbinder','lampwright','glassworker','gardener','waterkeeper','conservator']},
 'Demon':{'detail':'small swept horns and a slender expressive tail','backgrounds':['bookbinder','lampwright','glassworker','courier','gardener','mapmaker']},
 'Seraph':{'detail':'soft feathered wings with subtly luminous edges','backgrounds':['bookbinder','lampwright','courier','gardener','mapmaker','conservator']},
 'Elemental':{'detail':'mineral-flecked skin and a faint inner shimmer','backgrounds':['lampwright','glassworker','gardener','waterkeeper','mapmaker']},
 'Vampire':{'detail':'delicate fangs and attentive luminous eyes','backgrounds':['bookbinder','lampwright','glassworker','courier','mapmaker','conservator']},
 'Fae':{'detail':'leaflike ears and small iridescent markings','backgrounds':['bookbinder','gardener','waterkeeper','courier','mapmaker']},
 'Djinn':{'detail':'a gentle smoke-like shimmer around her hair','backgrounds':['lampwright','glassworker','courier','waterkeeper','mapmaker']},
 'Dragonkin':{'detail':'small curved horns and fine scales at her temples','backgrounds':['bookbinder','lampwright','glassworker','conservator','waterkeeper']},
 'Dryad':{'detail':'leaf-veined markings and small living twigs woven through her hair','backgrounds':['bookbinder','gardener','waterkeeper','mapmaker','conservator']},
 'Nymph':{'detail':'dew-bright markings and a soft natural shimmer','backgrounds':['lampwright','gardener','waterkeeper','courier','mapmaker']},
 'Spirit':{'detail':'a pearly translucent glow at the edges of her silhouette','backgrounds':['bookbinder','lampwright','gardener','waterkeeper','conservator']},
}
BACKGROUNDS={
 'bookbinder':{'name':'Travelling bookbinder','packageId':'archive-reader','origin':'She repaired well-used books in a travelling workshop, learning to value the notes people leave between the printed lines.','stories':['field-guide','teaching-notes','repair-method']},
 'lampwright':{'name':'Lamplight apprentice','packageId':'light-maker','origin':'She apprenticed in a small lamp workshop, making patient adjustments for readers who worked late.','stories':['useful-light','teaching-notes','repair-method']},
 'glassworker':{'name':'Glass workshop assistant','packageId':'light-maker','origin':'She sorted and finished glass in a modest cooperative workshop, keeping a notebook of promising imperfect pieces.','stories':['useful-light','colour-study','repair-method']},
 'courier':{'name':'Night-route courier','packageId':'light-maker','origin':'She carried letters between isolated workshops and learned how a dependable light makes a long road less lonely.','stories':['route-notes','useful-light','teaching-notes']},
 'gardener':{'name':'Terrace gardener','packageId':'water-worker','origin':'She tended a crowded terrace garden, comparing watering methods and trading practical notes with her neighbours.','stories':['garden-notes','water-study','field-guide']},
 'waterkeeper':{'name':'Canal measuring apprentice','packageId':'water-worker','origin':'She helped measure small irrigation channels, learning to check a hopeful estimate against what the water actually did.','stories':['water-study','route-notes','teaching-notes']},
 'mapmaker':{'name':'Survey notebook keeper','packageId':'archive-reader','origin':'She kept field notebooks for a survey workshop, preserving small observations that larger maps tended to omit.','stories':['route-notes','field-guide','teaching-notes']},
 'conservator':{'name':'Small archive conservator','packageId':'archive-reader','origin':'She worked in a neighbourhood archive, protecting ordinary records whose value came from the lives behind them.','stories':['repair-method','field-guide','colour-study']},
}
TEMPERAMENTS={
 'playful':{'name':'Playful and observant','text':'Quick to notice small details and quick with a teasing smile; she becomes quietly methodical when something matters.','charm':'a mischievous smile and relaxed, confident posture'},
 'poised':{'name':'Poised and curious','text':'Composed in company and warmly curious in private conversation; her polished manner gives way to delighted questions around a new craft.','charm':'a knowing half-smile and elegant ease'},
 'bold':{'name':'Bold and considerate','text':'Direct about what she wants and generous with encouragement; she checks that her enthusiasm leaves room for other people.','charm':'an assured gaze and an easy, inviting grin'},
 'coy':{'name':'Coy and determined','text':'Enjoys a little playful ambiguity in conversation, but states her boundaries plainly and sees practical promises through.','charm':'an amused sideways glance and a soft smile'},
 'quiet':{'name':'Quiet and wry','text':'Listens before speaking, notices absurdities, and saves her dry humour for people willing to listen in return.','charm':'a restrained smile that brightens when she is interested'},
 'sunny':{'name':'Warm and exacting','text':'Welcoming and openly affectionate with friends; cheerfulness never stops her pointing out a crooked measurement.','charm':'a bright adult smile and animated expressive hands'},
 'restless':{'name':'Restless and reflective','text':'Loves trying an unfamiliar method, then sitting down to understand why it worked; wants companionship without surrendering her independence.','charm':'lively eyes and a slightly conspiratorial smile'},
 'romantic':{'name':'Romantic and practical','text':'Finds beauty in ordinary work and likes a little ceremony; remains sensible about costs, effort and personal choice.','charm':'a warm lingering gaze and graceful, unhurried gestures'},
}
STORIES={
 'field-guide':{'name':'A guide to overlooked details','ambition':'Make a small illustrated guide to useful details that other observers tend to overlook.','hook':'Begin with a carefully checked personal folio of observations.'},
 'teaching-notes':{'name':'Notes someone else can use','ambition':'Turn her working notes into clear examples that a willing beginner could understand.','hook':'Prepare and compare examples before arranging her own teaching folio.'},
 'repair-method':{'name':'A kinder repair method','ambition':'Document a careful repair method that preserves the character of well-used things.','hook':'Compare small samples and record what survives each treatment.'},
 'useful-light':{'name':'Light for a working desk','ambition':'Study a comfortable light for long evenings of reading and delicate handwork.','hook':'Record useful comparisons rather than promising a new magical artifact.'},
 'colour-study':{'name':'A notebook of patient colour','ambition':'Collect practical observations about colour, ageing and the way light changes a surface.','hook':'Compare existing samples in a personal notebook.'},
 'route-notes':{'name':'The small routes between places','ambition':'Build a readable record of local routes and the useful observations larger maps leave out.','hook':'Organize known observations; new places require actual expeditions.'},
 'garden-notes':{'name':'A garden worth understanding','ambition':'Keep a clear record of how familiar plants respond to careful changes in watering.','hook':'Begin with notes and comparisons, not an unearned harvest.'},
 'water-study':{'name':'Where the water really goes','ambition':'Make water-guidance observations understandable enough to check and repeat.','hook':'Assemble measured examples into a personal study.'},
}
SKIN=('deep warm brown','warm tan','olive brown','fair with freckles','rich umber','golden brown','cool light brown','copper brown')
HAIR=('long black curls','an auburn bob','dark brown waves','short silver curls','a thick chestnut braid','cropped black coils','long ash-blonde waves','a loose dark-red braid')
BUILDS=('compact and softly curved','tall and gently curved','athletic with soft curves','full-figured and poised','slender with mature proportions','broad-shouldered and graceful')
NAMES=('Amara','Vesper','Liora','Zahara','Calista','Saffira','Nyra','Elara','Thalia','Ravena','Isolde','Soraya','Maelle','Leona','Cerys','Naima')
SURNAMES=('Vale','Morrow','Ash','Reed','Wren','Hale','Vell','Fen')


def catalogue():
    return {'version':VERSION,'ancestries':deepcopy(ANCESTRIES),'backgrounds':deepcopy(BACKGROUNDS),'temperaments':deepcopy(TEMPERAMENTS),'stories':deepcopy(STORIES),'commonAncestries':list(COMMON_ANCESTRIES),'golemMaterials':deepcopy(GOLEM_MATERIALS),'hairChoices':list(HAIR),'buildChoices':list(BUILDS),'arrivalMethods':{k:arrival_method(k) for k in ANCESTRIES}}


def select(state,request_id,choices=None,pack=None):
    from game import RuleError
    choices={} if choices is None else deepcopy(choices)
    if isinstance(choices,dict) and choices.get('contentSource')=='imported':
        import content_packs
        if not pack:raise RuleError('Activate a validated content pack in this campaign first.')
        return content_packs.select(state,request_id,choices,pack)
    if isinstance(choices,dict) and choices.get('ancestry')=='Angel':choices['ancestry']='Seraph'
    if not isinstance(choices,dict) or set(choices)-{'ancestry','background','temperament','story','arrivalMethod','bodyMaterial','hair','build'}:raise RuleError('Choose recognized character pool ingredients.')
    for key,values in [('ancestry',ANCESTRIES),('background',BACKGROUNDS),('temperament',TEMPERAMENTS),('story',STORIES),('arrivalMethod',('summoning','recruitment','construction')),('bodyMaterial',GOLEM_MATERIALS),('hair',HAIR),('build',BUILDS)]:
        if key in choices and (not isinstance(choices[key],str) or choices[key] not in values):raise RuleError('Unknown pool '+key+'.')
    route=choices.get('arrivalMethod',arrival_method(choices['ancestry']) if choices.get('ancestry') else 'summoning')
    if choices.get('bodyMaterial') and route!='construction':raise RuleError('Body materials apply only to constructed golems.')
    profiles=[c['profile'] for c in state.get('reviewedCandidates',{}).values()]
    profiles += [p for p in state['people'].values() if p.get('identitySource')!='reviewed-candidate-proposal' and p.get('personId')!='founder']
    rng=random.Random(hashlib.sha256(request_id.encode()).digest())
    def choose(options,counts):
        return rng.choices(options,weights=[1/(1+counts[x])**2 for x in options],k=1)[0]
    combinations=[(a,b,s) for a,d in ANCESTRIES.items() if arrival_method(a)==route for b in d['backgrounds'] for s in BACKGROUNDS[b]['stories'] if all(choices.get(k,v)==v for k,v in [('ancestry',a),('background',b),('story',s)])]
    if not combinations:raise RuleError('That ancestry, background and story do not form a supported combination. Choose compatible ingredients or leave one automatic.')
    counts=Counter((p.get('generationIngredients',{}).get('ancestry',p.get('ancestryLabel')),p.get('generationIngredients',{}).get('background'),p.get('generationIngredients',{}).get('story')) for p in profiles)
    ancestry_counts=Counter(p.get('ancestryLabel') for p in profiles)
    combination=rng.choices(combinations,weights=[1/((1+counts[x])**2*(1+ancestry_counts[x[0]])) for x in combinations],k=1)[0]
    a,b,s=combination
    t=choices.get('temperament') or choose(list(TEMPERAMENTS),Counter(p.get('generationIngredients',{}).get('temperament') for p in profiles))
    appearance={key:choose(list(values),Counter(p.get('generationIngredients',{}).get('appearance',{}).get(key) for p in profiles)) for key,values in [('skin',SKIN),('hair',HAIR),('build',BUILDS)]}
    if a in ('Bovinefolk','Ogrekin'):appearance['build']='strong, broad-shouldered and generously curvy'
    if a=='Orc':appearance.update(skin=rng.choice(['moss green','deep jade green','olive green']),build='sturdy, powerful and softly curved')
    if a=='Ogrekin':appearance['skin']=rng.choice(['muted terracotta red','warm copper brown','dusky blue'])
    if a=='High elf':appearance['skin']='fair with warm or cool undertones'
    if a=='Dark elf':appearance['skin']='rich chocolate brown'
    if a=='Drow':appearance['skin']=rng.choice(['slate grey','deep charcoal','soft violet-grey'])
    if a=='Golem':appearance['skin']=GOLEM_MATERIALS[choices.get('bodyMaterial','clay')]['appearance']
    for key in ('hair','build'):
        if key in choices:appearance[key]=choices[key]
    return {'arrivalMethod':route,**({'bodyMaterial':choices.get('bodyMaterial','clay')} if a=='Golem' else {}),'version':VERSION,'ancestry':a,'background':b,'temperament':t,'story':s,'appearance':appearance,'adultAgeYears':rng.randint(18,25)}


def guidance(selection):
    if selection.get('contentSource')=='imported':return deepcopy(selection)
    return {'selection':selection,'ancestry':ANCESTRIES[selection['ancestry']], 'background':BACKGROUNDS[selection['background']], 'temperament':TEMPERAMENTS[selection['temperament']], 'story':STORIES[selection['story']]}


def validate_selection(proposal,selection):
    from game import RuleError
    if selection.get('contentSource')=='imported':
        b=selection['records']['background']
        if proposal['ancestryLabel']!=selection['ancestry'] or proposal['adultAgeYears']!=selection['adultAgeYears'] or proposal['occupation']!=b['occupation'] or proposal['capabilityPackageId']!=b['suggestedCapabilityPackageId']:
            raise RuleError('The proposal changed its selected ancestry, age, occupation or capability package.')
        return
    if proposal['ancestryLabel']!=('Seraph' if selection['ancestry']=='Angel' else selection['ancestry']) or proposal['capabilityPackageId']!=BACKGROUNDS[selection['background']]['packageId'] or proposal['adultAgeYears']!=selection['adultAgeYears'] or proposal['occupation']!=BACKGROUNDS[selection['background']]['name']:
        raise RuleError('The proposal changed its selected ancestry, age, occupation or capability package. No identity was created.')


def offline(state,selection,request_id):
    if selection.get('contentSource')=='imported':
        import content_packs
        return content_packs.offline(selection)
    rng=random.Random(request_id)
    existing={p['name'].casefold() for p in state['people'].values()}|{c['profile']['name'].casefold() for c in state.get('reviewedCandidates',{}).values()}|{'eris','selene','mira','tamsin','iona','aurelia','neris','sabine','zahra'}
    names=[n+' '+s for n in NAMES for s in SURNAMES if (n+' '+s).casefold() not in existing]
    from game import RuleError
    if not names:raise RuleError('The offline name pool is exhausted.')
    name=rng.choice(names);a=selection['appearance'];b=BACKGROUNDS[selection['background']];t=TEMPERAMENTS[selection['temperament']];s=STORIES[selection['story']]
    result={'name':name,'adultAgeYears':selection['adultAgeYears'],'ancestryLabel':selection['ancestry'],'occupation':b['name'],'personality':t['text'],
        'appearanceDescription':'An unmistakably adult woman, '+a['build']+', with '+a['skin']+' skin, '+a['hair']+', and '+ANCESTRIES[selection['ancestry']]['detail']+'. She wears a fitted midnight-violet bodice over an opaque soft-necked blouse and a practical skirt, with '+t['charm']+'.',
        'origin':b['origin'],'ambition':s['ambition'],'accommodationPreference':rng.choice(['separate-bed','private-room']),'capabilityPackageId':b['packageId'],'stayPreference':rng.choice(['open-to-staying','open-to-staying','visit-only']),
        'introduction':'“'+name+'. I heard this was a house where useful work and a little curiosity could share a desk. I would like to see it for myself.”',
        'personalTopic':'“'+s['ambition']+' That is a project I would like to make my own. A good conversation along the way would be welcome.”'}
    import scripted_companions
    hobby,value,difficulty,anecdote,question=scripted_companions.life(selection)
    result['personality']=(t['text']+' '+value+' Enjoys '+hobby+'. '+difficulty)[:400]
    result['introduction']='“'+name+'. '+{'recruitment':'Your letter reached the workshop.','summoning':'Your invitation reached me between jobs.','construction':'I would like to introduce myself.'}[selection['arrivalMethod']]+' '+s['hook']+' Would your household have room for that sort of work?”'
    result['personalTopic']='“'+anecdote+' '+question+'”'
    if selection['ancestry']=='Golem':
        result['origin']='A proposed companion to be constructed and awakened here, fully adult in form and cognition, with no invented years of lived history. Her interests and starting knowledge are bounded by the reviewed plan.'
        result['appearanceDescription']='A clearly adult feminine golem, '+a['build']+', made from '+GOLEM_MATERIALS[selection.get('bodyMaterial','clay')]['appearance']+', with '+a['hair']+' and '+t['charm']+'. An opaque fitted violet bodice and practical skirt complement fine handmade joins. No childlike presentation.'
        result['introduction']='“'+name+'. This is a beginning, then. I would like to look around, ask questions, and decide what to make of it for myself.”'
    elif selection['ancestry']=='Drow':result['origin']='From a subterranean settlement. '+result['origin']
    elif selection['ancestry']=='High elf':result['origin']='From a forest community. '+result['origin']
    return result


def migrate_ancestry_names(state):
    """Terminology-only update; preserve identity, art and player-written history."""
    profiles=list(state.get('people',{}).values())+[c['profile'] for c in state.get('reviewedCandidates',{}).values()]
    for p in profiles:
        if p.get('ancestryLabel')=='Angel':
            p['ancestryLabel']='Seraph'
            if p.get('role','').startswith('Angel '):p['role']='Seraph '+p['role'][6:]
        ingredients=p.get('generationIngredients',{})
        if ingredients.get('ancestry')=='Angel':ingredients['ancestry']='Seraph'
        if p.get('personId')=='aurelia' and p.get('origin')=='An angel conservator from a dusk-lit hospice of travelling scholars.':p['origin']='A seraph conservator from a dusk-lit hospice of travelling scholars.'
