"""Authored introductions discovered through ordinary work and returned expeditions."""
from copy import deepcopy

PEOPLE={
 'koharu':{'name': 'Koharu', 'age': 23, 'ancestry': 'Kitsune', 'background': 'bookbinder', 'occupation': 'stage-prop restorer', 'temperament': 'playful', 'story': 'repair-method', 'place': 'The neighbouring travelling theatre workshop', 'lead': 'A local kitsune craftswoman brings a broken mechanical bird and an invitation to compare repair methods.', 'unlock': 'Available from the beginning. Koharu already lives nearby; no crossing ritual is needed.', 'greeting': '“Koharu. This bird is supposed to bow, but it has developed an opinion about the audience.” She steadies its loose wooden head. “May I borrow a clear table? You can help decide whether it looks offended or merely tired.”', 'appearance': 'Clearly adult kitsune woman of 23, 158 cm tall, slight slender build with narrow shoulders, warm light-olive skin, hazel-green eyes and long dark chestnut hair worn loose, with thick side locks covering the sides of her head. Exactly two dark brown fox ears on top of her head and one full dark brown fox tail with a cream tip. No human ears. Human face and smooth human skin. Deep-teal wrap blouse, cinnamon divided work skirt, dark leggings, lace-up ankle boots and a small tool belt.', 'origin': 'A kitsune stage-prop restorer from the neighbouring travelling theatre workshop. She repairs small mechanisms, book stands and scenery that must fold neatly into a wagon.', 'ambition': 'Build a small travelling puppet stage with repairs its performers can manage themselves, and write clear instructions for every moving part.'},
 'zahra':{'name': 'Zahra', 'age': 23, 'ancestry': 'Djinn', 'background': 'waterkeeper', 'occupation': 'precision smith', 'temperament': 'poised', 'story': 'water-study', 'place': 'A letter carried through the conservatory wards', 'lead': 'A Djinn smith offers designs for the conservatory’s worn brass water gates. Her letter includes a measured drawing and a tiny ember that fades when the paper cools.', 'unlock': 'Restore the conservatory, then use an exotic contact ritual to exchange an invitation.', 'greeting': '“Zahra. I make small things that must fit properly.” A curl of smoke slips from her hair as she unfolds a hinge drawing. “The ember is mine. The measurements still need checking.”', 'appearance': 'Clearly adult Djinn woman of 23, short at 155 cm, with a soft curvy build, narrow shoulders and no visible muscle definition. Warm brown skin, an oval face, slender nose, softly luminous amber eyes and long black curls that dissolve into grey-violet smoke with tiny ember lights. Indigo wrap blouse, woven sash, loose trousers, short leather apron and ankle boots. A small ember glows above her fingertips.', 'origin': 'A Djinn precision smith from a canal town beyond the threshold. She learned to fit brass sluice gates and direct a small, steady ember before turning to hinges, clasps and musical mechanisms.', 'ambition': 'Make a dependable small clockwork instrument and teach apprentices how to work with heat without wasting delicate pieces.'},
 'fenna':{'name':'Fenna','age':22,'ancestry':'Wolfkin','background':'mapmaker','temperament':'restless','story':'route-notes','place':'The nursery path','lead':'The nursery route may introduce a route keeper interested in comparing observations.','unlock':'Return with a discovery from the fern nursery.','greeting':'“Fenna. You came back with notes instead of a heroic explanation. Promising.” Her ears tilt towards you as she opens a worn notebook. “Let us compare the interesting bits.”','appearance':'Adult wolfkin woman with warm tan human skin, exactly two grey wolf ears on top of her head and a fluffy tail, silver-grey waves covering both sides of her head, no human ears, and amber eyes; sage bodice, navy side-slit skirt and ankle boots.','origin':'A wolfkin route keeper who works between the valley settlements and the fern nursery.','ambition':'Record the small useful routes that grand maps tend to leave out.'},
 'kaede':{'name':'Kaede','age':24,'ancestry':'Ogrekin','background':'glassworker','temperament':'bold','story':'colour-study','place':'The valley glassworks','lead':'The repaired hearth wards draw a local ogrekin glassworker interested in exchanging workshop notes.','unlock':'Complete the first hearth-ward study.','greeting':'“Kaede.” She turns a small glass cup so you can see its thin rim. “I made this one. Getting the thickness even took longer than I care to admit.”','appearance':'Tall adult ogrekin woman with terracotta-red skin, two horns, loose blue-black hair, a full bust, defined waist and rounded hips, with a fit figure and subtle muscle definition; barbarian-style leather cuirass over a violet tunic, full hide trousers, fur shoulder mantle, bracers and fur-trimmed boots.','origin':'A local ogrekin glassworker from the valley glassworks who values controlled strength and a lively exchange of ideas.','ambition':'Study patient colour and the effects of small changes in a glassworking method.'},
}


def initialize(state):
    state.setdefault('localEncounters',{key:{'status':'available','completedOn':None} for key in PEOPLE})
    state.setdefault('localEncounterCandidates',{})
    state.setdefault('localVisit',None)


def unlocked(state,key):
    import game as g
    if key=='rhess':return bool(state.get('patrolJourneys',{}).get('watchtower-trail',{}).get('discoveries'))
    if key=='velis':return bool(state.get('hollowRoad',{}).get('discoveries'))
    if key=='sylva':return g.room_available(state,'conservatory') and bool(g.discoveries_for(state,'fern-nursery'))
    if key in ('elowen','kaede'):return state['researchStatus']=='complete'
    if key=='nyssara':return 'survey' in g.discoveries_for(state,'ridge-cistern')
    if key=='koharu':return True
    if key=='zahra':return g.room_available(state,'conservatory')
    if key=='fenna':return bool(g.discoveries_for(state,'fern-nursery'))
    return 'courteous-passage' in state['archivePrinciples']


def definition(state,key):
    import character_pool as pool
    from candidate_proposals import approved_definition
    d=PEOPLE[key];selection=pool.select(state,'authored-local-'+key,{'ancestry':d['ancestry'],'background':d['background'],'temperament':d['temperament'],'story':d['story']})
    selection['adultAgeYears']=d['age']
    p=pool.offline(state,selection,'authored-local-'+key)
    p.update(name=d['name'],adultAgeYears=d['age'],appearanceDescription=d['appearance'],origin=d['origin'],ambition=d['ambition'],introduction=d['greeting'],accommodationPreference='separate-bed',stayPreference='open-to-staying')
    if d.get('occupation'):p['occupation']=d['occupation']
    c=approved_definition(p,key,'authored-local-v1','local-'+key)
    
    if key=='zahra':
        c['principles']=['water-guidance','steady-hearth-wards']
        c['focusName']='Ember-marked brass gauge'
        c['topics']['intentions']['text']='“I fit sluice gates, hinges and little musical movements. My ember keeps a small piece evenly warm; it does not measure or shape the piece for me.”'
        c['personalTopics']['interests']['text']='“I am making a musical box with a tune I chose myself. The third note keeps catching. I can control the heat; persuading a spring to behave is another matter.”'
    if key=='koharu':
        c['profile'].update(arrivalMethod='recruitment',personality='Quick-witted, candid and absorbed by small mechanisms. Enjoys playful surprises, painted scenery and spiced plum tea. Values the audience’s enjoyment and repair instructions anyone can follow; dislikes humiliating jokes and starts redesigning before asking.')
        c['topics']['intentions']['text']='“Stage birds, folding scenery, book stands: things that have to survive a wagon ride. I want performers to repair them without sending for me. A good trick can keep its secret; a broken hinge needs instructions.”'
        c['personalTopics']['interests']['text']='“I am painting a ridiculous little dragon for my puppet stage. Its eyebrows must move before its mouth does, or the joke arrives in the wrong order. Would you rather see the mechanism or try its voice?”'
    selection.pop('appearance',None) # Authored appearance is fixed by the portrait and explicit description above.
    c['profile'].update(identitySource='authored-local-encounter',generationIngredients=selection)
    c['textSource']='authored-local-encounter'
    return c


def start_blockers(state, key):
    import game as g
    reasons = []
    if not unlocked(state, key):
        reasons.append(PEOPLE[key]['unlock'])
    if state['localEncounters'][key]['status'] != 'available':
        reasons.append('This introduction has already been made. Continue her correspondence instead.')
    if state['localVisit'] is not None:
        reasons.append('Finish or put aside the current local appointment first.')
    if not g.character_at_castle(state, 'founder'):
        reasons.append('Return home before arranging a local appointment.')
    name = PEOPLE[key]['name'].casefold()
    if any(p['name'].casefold() == name for p in list(state['people'].values()) + [c['profile'] for c in state['reviewedCandidates'].values()]):
        reasons.append('That name already belongs to an established character; their saved identity is preserved.')
    return reasons


def view(state):
    import game as g
    return {'project':deepcopy(state['localVisit']),'working':state['localVisit'] is not None and g.character_at_castle(state,'founder') and state['founderAssignment']=='local-visit',
        'encounters':{key:{**deepcopy(d),**deepcopy(state['localEncounters'][key]),'unlocked':unlocked(state,key),
        'startBlockers':start_blockers(state,key), 'canStart':not start_blockers(state,key)} for key,d in PEOPLE.items()}}


def apply(state,action):
    kind=action.get('type')
    if kind not in ('start-local-visit','resume-local-visit','cancel-local-visit'):return False
    import game as g
    g.require(g.character_at_castle(state,'founder'),'Return home before arranging a local appointment.')
    if kind=='start-local-visit':
        key=action.get('encounterId');g.require(isinstance(key,str) and key in PEOPLE,'Choose an existing introduction.')
        g.require(not start_blockers(state,key),' '.join(start_blockers(state,key)))
        # Do not rename a pre-existing custom character or confuse two saved identities.
        name=PEOPLE[key]['name'].casefold()
        g.require(not any(p['name'].casefold()==name for p in list(state['people'].values())+[c['profile'] for c in state['reviewedCandidates'].values()]),'That name already belongs to an established custom identity. This authored introduction remains unavailable; your saved person is preserved.')
        state['localVisit']={'encounterId':key,'requiredWorkPhases':1,'completedWorkPhases':0};state['founderAssignment']='local-visit'
    else:
        g.require(state['localVisit'] is not None,'There is no unfinished local appointment.')
        if kind=='resume-local-visit':state['founderAssignment']='local-visit'
        else:
            state['localVisit']=None
            if state['founderAssignment']=='local-visit':state['founderAssignment']='rest'
    return True


def forecast(state):
    if not state['localVisit']:return []
    v=view(state);d=PEOPLE[state['localVisit']['encounterId']]
    return [d['name']+' · '+('complete a one-phase introduction.' if v['working'] else 'appointment paused.')]


def resolve(state,summary):
    if not view(state)['working']:return
    import game as g
    import arrivals
    key=state['localVisit']['encounterId'];d=PEOPLE[key]
    state['localEncounterCandidates'][key]=definition(state,key)
    state['localEncounters'][key].update(status='introduced',completedOn={'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
    state['localVisit']=None;state['founderAssignment']='rest'
    import recruitment_quests
    is_common=recruitment_quests.common(state['localEncounterCandidates'][key])
    if is_common:recruitment_quests.lead(state,key,'rescue')
    elif key not in ('sylva','zahra'):arrivals.contact(state,key,'ordinary-encounter')
    text=('A letter establishes '+d['name']+'’s identity and interests. Use the normal exotic contact ritual before meeting her.' if key in ('sylva','zahra') else d['name']+' is now an ordinary contact. An agreed visit and household membership remain separate choices.')
    if is_common:text=d['name']+'’s route notes identify a stranded traveller beyond a raider roadblock. Her rescue lead is on the recruitment quest board; no person has joined the household.'
    summary.append(text);g.add_journal(state,text)

# Two authored common-ancestry specialists use ordinary introductions and visits.
PEOPLE.update({
 'elowen':{'name':'Elowen','age':24,'ancestry':'High elf','background':'conservator','temperament':'poised','story':'repair-method','place':'The ward conservator’s correspondence','lead':'A high elf ward conservator asks to compare the castle’s repaired hearth inscriptions.','unlock':'Complete the first hearth-ward study.','greeting':'“Elowen. I repair household wards: heat, water, preservation. My first question is always what stopped working. The dramatic explanation can wait until I have seen it.”','appearance':'Clearly adult high elf woman, long pointed ears, warm ivory skin, grey-green eyes, honey-blonde hair in a loose practical braid; muted sage blouse, charcoal fitted waistcoat, long violet skirt and worn boots. Small plain brass clasps; no crown, glowing eyes or ceremonial luxury.','origin':'A travelling high elf conservator of domestic wards, interested in dependable preparation rather than spectacle.','ambition':'Build a preparation circle that helps different practitioners keep their own workings distinct.'},
 'nyssara':{'name':'Nyssara','age':25,'ancestry':'Drow','background':'glassworker','temperament':'restless','story':'colour-study','occupation':'enchanter','place':'An enchanter above the ridge cistern','lead':'The returned cistern survey attracts a drow enchanter interested in the old workings and the minerals that hold them.','unlock':'Survey Ridge cistern and bring the findings home.','greeting':'“Nyssara. I enchant equipment that has to survive being used.” She turns a small inscribed focus in her hand. “A convincing shimmer is not a test result.”','appearance':'Clearly adult drow woman, long pointed ears, muted slate-violet skin, silver-white shoulder-length wavy hair, warm copper-brown eyes; faded petrol-blue work shirt, charcoal trousers, violet sash, scuffed boots and a small mineral pouch. Humanlike expressive face; no glowing eyes, spider motifs or villain costume.','origin':'An independent drow enchanter from a subterranean craft settlement beneath the valley, with a dry wit and a talent for dependable equipment inscriptions and carefully prepared magical materials.','ambition':'Build an enchanting bench for reliable gear upgrades, with tested inscriptions and honest notes about their limits.'},
})

PEOPLE['sylva']={'name':'Sylva','age':21,'ancestry':'Dryad','background':'gardener','temperament':'playful','story':'garden-notes','place':'A letter among the nursery cuttings','lead':'A dryad cultivator offers to help the restored conservatory become a dependable source of living plants.','unlock':'Restore the conservatory and return a discovery from the fern nursery. Then use the normal exotic contact ritual.','greeting':'“Sylva. I grow herbs and take cuttings for damaged gardens. I also keep a few flowers simply because I like them.”','appearance':'A beautiful adult dryad of 21 with a soft heart-shaped face, amber-gold eyes, distinctly celadon-green living-sapwood skin, deeper green lips and one pair of broad veined leaf ears in place of human ears. Long forest-green waves grow among ivy, ivory blossoms and a small crown of budding twigs. Subtle longitudinal woodgrain is part of her green skin, without tattoo-like vines or painted leaf markings. Her hands and natural bare feet are green too. An opaque overlapping-leaf bodice and calf-length leaf-and-birch skirt are tied with a braided vine belt. Warm, playful expression; no shoes.','origin':'A dryad cultivator who tends a woodland nursery beyond the valley threshold, patient with seedlings and mischievous with their keepers.','ambition':'Create living propagation beds that produce healthy cuttings without exhausting the parent plants.'}


def revise_nyssara(state):
    """User-requested vocation correction; retain earned knowledge, possessions and history."""
    profiles=[]
    if 'nyssara' in state.get('people',{}):profiles.append(state['people']['nyssara'])
    candidate=state.get('localEncounterCandidates',{}).get('nyssara')
    if candidate:profiles.append(candidate['profile'])
    for profile in profiles:
        if profile.get('identitySource')!='authored-local-encounter':continue
        if profile.get('role')=='Drow enchanter · 25' and profile.get('ancestryLabel')=='Drow':continue
        profile.setdefault('identityHistory',[]).append({k:deepcopy(profile.get(k)) for k in ('role','ancestryLabel','appearanceDescription','origin','ambition','identityRevision')})
        profile.update(role='Drow enchanter · 25',ancestryLabel='Drow',appearanceDescription=PEOPLE['nyssara']['appearance'],origin=PEOPLE['nyssara']['origin'],ambition=PEOPLE['nyssara']['ambition'],identityRevision=profile.get('identityRevision',1)+1)


def revise_sylva(state):
    """Preserve identity and accepted art while aligning botanical appearance text."""
    profiles=[]
    if 'sylva' in state.get('people',{}):profiles.append(state['people']['sylva'])
    candidate=state.get('localEncounterCandidates',{}).get('sylva')
    if candidate:profiles.append(candidate['profile'])
    for profile in profiles:
        if profile.get('identitySource')!='authored-local-encounter':continue
        if profile.get('appearanceDescription')==PEOPLE['sylva']['appearance']:continue
        profile.setdefault('identityHistory',[]).append({k:deepcopy(profile.get(k)) for k in ('appearanceDescription','identityRevision')})
        profile.update(appearanceDescription=PEOPLE['sylva']['appearance'],identityRevision=profile.get('identityRevision',1)+1)

# Named common neighbours have concrete rescue leads before an optional invitation.
for _who,_lead in {
 'fenna':'Fenna’s route notebook reaches the castle with a returning courier. A toll-taking band has blocked her way back from the nursery path.',
 'kaede':'The valley glassworks reports that Kaede and a wagon of repair supplies are stranded beyond an illegal roadblock.',
 'elowen':'Elowen’s hearth-ward report arrives without its author. A traveller saw her waiting with other travellers behind a raider barricade.',
 'nyssara':'Nyssara sent the cistern survey ahead, but her mineral cart has been stopped by raiders on the return road.'
}.items():
 PEOPLE[_who]['lead']=_lead
