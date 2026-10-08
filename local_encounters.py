"""Authored introductions discovered through ordinary work and returned expeditions."""
from copy import deepcopy

PEOPLE={
 'maren':{'name':'Maren','age':24,'ancestry':'Bovinefolk','background':'bookbinder','temperament':'playful','story':'repair-method','place':'The neighbouring joinery','lead':'A nearby craftswoman offers an afternoon comparing repair methods.','unlock':'Available from the beginning.','greeting':'“Maren. I can lift the case myself, thank you. You may impress me by finding somewhere sensible to put it.” Her smile takes the sting out of the challenge.','appearance':'Strong, curvy adult woman with smooth warm brown human skin, bovine horns and ears, a tufted tail, chestnut waves and hazel eyes; fitted plum work bodice, charcoal skirt and worn apron.','origin':'A bovinefolk craftswoman who repairs cases and book furniture at the neighbouring joinery.','ambition':'Develop careful repair notes for useful objects too often discarded.'},
 'brakka':{'name':'Brakka','age':23,'ancestry':'Orc','background':'waterkeeper','temperament':'poised','story':'water-study','place':'A conservatory work visit','lead':'A green-skinned irrigation worker has heard that the old conservatory is usable again.','unlock':'Restore the conservatory.','greeting':'“Brakka. I have patience for awkward channels and very little for confident guesses.” She lifts a measuring cord and gives you an amused look. “Which sort of afternoon shall we have?”','appearance':'Sturdy, athletic and curvy adult orc woman with olive-green skin, a broad nose, strong jaw, small upward lower canine tusks rooted in her mouth, black braided hair and amber eyes. Youthful feminine features retain her clearly orc identity; plum work tunic, charcoal trousers, leather apron, bracers and boots.','origin':'An orc irrigation worker from the valley gardens, accustomed to steady demanding work and careful measurements.','ambition':'Make a reliable notebook of small irrigation channels and how to check them.'},
 'fenna':{'name':'Fenna','age':22,'ancestry':'Wolfkin','background':'mapmaker','temperament':'restless','story':'route-notes','place':'The nursery path','lead':'The nursery route may introduce a route keeper interested in comparing observations.','unlock':'Return with a discovery from the fern nursery.','greeting':'“Fenna. You came back with notes instead of a heroic explanation. Promising.” Her ears tilt towards you as she opens a worn notebook. “Let us compare the interesting bits.”','appearance':'Adult wolfkin woman with warm tan human skin, grey wolf ears and fluffy tail, silver-grey waves and amber eyes; sage bodice, navy side-slit skirt and ankle boots.','origin':'A wolfkin route keeper who works between the valley settlements and the fern nursery.','ambition':'Record the small useful routes that grand maps tend to leave out.'},
 'kaede':{'name':'Kaede','age':24,'ancestry':'Oni','background':'glassworker','temperament':'bold','story':'colour-study','place':'A letter from beyond the threshold','lead':'Passage studies can uncover an oni glassworker interested in exchanging workshop notes.','unlock':'Record Courteous passage in the archive.','greeting':'“Kaede.” She turns a small glass cup so you can see its thin rim. “I made this one. Getting the thickness even took longer than I care to admit.”','appearance':'Tall adult oni woman with terracotta-red skin, two horns, loose blue-black hair, a full bust, defined waist and rounded hips, with a fit figure and subtle muscle definition; barbarian-style leather cuirass over a violet tunic, full hide trousers, fur shoulder mantle, bracers and fur-trimmed boots.','origin':'An oni glassworker beyond the threshold who values controlled strength and a lively exchange of ideas.','ambition':'Study patient colour and the effects of small changes in a glassworking method.'},
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
    if key=='elowen':return state['researchStatus']=='complete'
    if key=='nyssara':return 'survey' in g.discoveries_for(state,'ridge-cistern')
    if key=='maren':return True
    if key=='brakka':return g.room_available(state,'conservatory')
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
    if key not in ('kaede','sylva'):arrivals.contact(state,key,'ordinary-encounter')
    text=('A letter establishes '+d['name']+'’s identity and interests. Use the normal exotic contact ritual before meeting her.' if key in ('kaede','sylva') else d['name']+' is now an ordinary contact. An agreed visit and household membership remain separate choices.')
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
