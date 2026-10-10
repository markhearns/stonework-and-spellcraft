"""Read-only magic reference, assembled from the executable catalogues."""
from functools import lru_cache

NOTES = {
    'stoneguard':'Protect the person the enemy is about to strike. A strong ward on somebody else will not help them.',
    'gust-strike':'A brief loss of footing gives the next fighter an opening. Tell your companion when to move.',
    'binding-snare':'Anchor the cord before pulling it tight. Stone machinery and drifting lights need another method.',
    'purifying-light':'Check for venom and stiffening joints before treating the wound. Stopping the cause matters as much as healing the injury.',
    'dispel-ward':'Find the anchors feeding the defense. Disconnecting them is more useful than striking the protected shell.',
    'chain-lightning':'Additional arcs need separate targets or conductive parts. Do not spend extra components expecting them to appear.',
    'expedition-warding':'Pack the warded cords where the party can reach them. Their protection is strongest during the first exchanges.',
    'antivenom-preparation':'Label the doses and share their location with the party. Two treatments are useful only if someone knows where to find them.',

    'warm-twist': 'Warm the fibres until they yield. If you smell smoke, you have begun a different experiment.',
    'root-song': 'A tended bed will answer a patient song. An empty pot has very little to say.',
    'luminous-copy': 'The light copies every error as faithfully as every insight. Read the original first.',
    'clarify-glass': 'You are persuading the sediment to settle, not persuading yourself that the vessel was clean.',
    'research-lens': 'Two pages held together can expose a mistake that either page hides alone.',
    'craft-hand': 'The patient hand steadies a maker. It does not excuse a poor joint.',
    'copy-lamp': 'A good scribe asks the lamp for another clear line, not another day without sleep.',
    'focus-guide': 'Mark the guide before you cut. Magic can steady the stroke; it cannot choose your inscription.',
    'bedroom-ward': 'Let the threshold settle around a room already being made ready. A ward is no substitute for a bed.',
    'green-frame': 'A conservatory should hold warmth the way a cupped hand holds a seed: gently.',
    'foundation-line': 'Hang the plumb line before you trust the old wall. Stone remembers a careless measurement.',
    'field-compass': 'The best direction is the one you can explain to the person carrying the other end of the map.',
    'water-jet': 'Aim at the burning timber, not the impressive plume of smoke above it.',
    'wind-step': 'Choose your landing before you borrow the wind. It has no opinion about where you ought to arrive.',
    'borne-flight': 'Balance the packs before lifting the party. Air is a poor place to discover who packed the anvil.',
    'fire-lance': 'A clean line of heat is useful. Feeding a creature already made of embers is merely generous.',
    'ice-bind': 'The brief stillness matters as much as the cold. Use it before your opponent remembers how to move.',
    'arc-bolt': 'Look for metal that continues through the joint. A bright plate is not always a useful conductor.',
    'dawn-lance': 'This light loosens the binding that moves old bones. It has no quarrel with a beating heart.',
    'mending-light': 'First ask where it hurts. Even a careful healing hand must know where to begin.',
    'giant-grasp': 'Strength borrowed for a moment is best spent on the stone, not on proving you can lift it twice.',
    'lucid-sight': 'Clearer sight makes the marks easier to read. It does not make your first interpretation correct.',
    'borrowed-hour': 'Have the tools laid out before casting. A faster hand is of little use while hunting for the chisel.',
    'threshold-fold': 'Keep a sound memory of the destination. A doorway is an arrangement between two places, not a guess.',
    'calm-tide': 'Quiet the panic, then listen. The person beneath it still has a perfectly good right to disagree.',
    'silver-tongue': 'A fair opening can make a bargain easier. It cannot make every answer yes.',
    'mirror-decoy': 'Give the false companion somewhere plausible to stand. Even a lie should understand the room.',
    'wisp-scout': 'Send the little lantern ahead of your boots. It is much easier to retrieve from a flooded stair.',
    'water-walk': 'A still surface can carry you for a crossing. Do not mistake it for a floor you own.',
    'water-breath': 'Agree on the work before you submerge. Being able to breathe does not improve an argument underwater.',
    'archive-circle': 'The circle helps a roomful of scholars work together. Every scholar must still read the page.',
    'maker-circle': 'Leave room for the hands that will use the bench. A flawless circle beneath a heap of tools helps nobody.',
    'garden-circle': 'A lasting garden working rewards a gardener who returns. It does not weed the beds in your absence.',
    'sanctuary-circle': 'Rest is part of the working. Someone determined to keep marching will miss its best kindness.',
    'market-circle': 'A well-kept account is the first component. The second is remembering that a bargain has two sides.',
    'anchor-circle': 'Make home a place you can find again. The anchor saves a component; the journey still needs a destination.',
    'welcome-circle': 'Steady the threshold and leave the choice of crossing it to the visitor.',
    'foundation-circle': 'The house can help you build, but it cannot fund the timber or decide where the next room belongs.',
    'concordant-lesson': 'Leave a little space between the patterns. A crowded memory is not the same thing as a trained one.',
    'lamplit-sight': 'An extra pattern should be carried lightly. Knowing that the blessing can be set aside is part of accepting it.',
    'lamplit-reversal': 'Put down the extra pattern before loosening the blessing. Nothing treasured needs to be torn away.',
}


def note(key):
    return {'quote': NOTES[key], 'author': 'Scholar Elian Voss', 'work': 'Notes on Household and Field Magic'}


def components(materials, names):
    return ' + '.join(f'{n} {names.get(k, {}).get("name", k)}' for k, n in materials.items()) or 'No casting supplies'


@lru_cache(maxsize=1)
def workshop_entries():
    import game as g
    import public_workshop as w
    catalogue = w.catalogue()
    rows = []
    themes = [('water', 'water-jet'), ('basin', 'water-jet'), ('root', 'root-song'), ('seed', 'root-song'), ('warm', 'warm-twist'), ('knot', 'warm-twist'), ('ink', 'luminous-copy'), ('copy', 'luminous-copy'), ('glass', 'clarify-glass'), ('lens', 'research-lens'), ('light', 'copy-lamp'), ('threshold', 'bedroom-ward'), ('joint', 'craft-hand')]
    for record in catalogue['records'].values():
        kind = record['recordType']
        if kind not in ('spell-construction', 'ritual-concept') or not record.get('mechanicsProposalId'):
            continue  # Four baseline studies are already represented by their live forms.
        rule = catalogue['rules'][record['mechanicsProposalId']]
        ritual = kind == 'ritual-concept'
        topic = (record['name'] + ' ' + record['summary']).lower()
        art = 'archive-circle' if ritual else next((image for word, image in themes if word in topic), 'research-lens')
        knowledge = record.get('principleIds') or [r['id'] for r in record['references'] if r['namespace'] == 'baseline' and r['id'] in g.PRINCIPLE_NAMES]
        supplies = []
        for part in rule.get('materials', []):
            label = g.MATERIALS.get(part.get('materialId'), {}).get('name') or part.get('propertyId', 'suitable component')
            supplies.append(f'{part["quantity"]} {label} ({part.get("consumption", "review consumption")})')
        effect = rule['effectSummary']
        limits = rule.get('limitations', [])
        # Authored in-world annotations quote the specific bounded working, not a new effect.
        observation = record.get('boundedOutcome') if ritual else record.get('desiredEffect', effect)
        quote = f'My margin beside “{record["name"]}” reads: {observation} Record what happened before claiming anything more.'
        rows.append({'id': 'workshop:' + record['id'], 'name': record['name'], 'kind': 'ritual' if ritual else 'spell', 'collection': 'workshop', 'category': 'Shared study ritual' if ritual else 'Workshop spell study', 'art': '/assets/spells/' + art + '.webp', 'description': record['summary'], 'effect': effect, 'requirements': [g.PRINCIPLE_NAMES.get(k, k) for k in knowledge] + ([record['invitationAndAgreement']] if ritual else ['Learn, test and prepare this working personally; use the existing owned target.']), 'cost': f'{rule["crowns"]} crowns' + (' + ' + ' + '.join(supplies) if supplies else '; no material payment'), 'duration': f'{rule["workPhases"]} assigned phase(s)' + (' per role; a person holding several roles completes their work sequentially' if ritual else ' for the reviewed casting; learning and testing are separate'), 'limits': limits, 'roles': record.get('roles', []), 'scholarNote': {'quote': quote, 'author': 'Scholar Elian Voss', 'work': 'Workshop Marginalia'}, 'destination': 'publicWorkshop', 'recordId': record['id'], 'recordType': kind})
    return rows


def view(state):
    import game as g
    import headquarters as h
    import lasting_rituals
    rows = []
    for key, form in g.SPELL_FORMS.items():
        category = 'Field spell' if form.get('field') else 'Work enchantment' if form.get('support') else 'Household spell'
        owners = [g.character_profile(state, spell['ownerId'])['name'] for spell in state['spellbook'] if spell['formId'] == key and spell['status'] == 'learned']
        rows.append({'id': key, 'name': form['name'], 'kind': 'spell', 'collection': 'castle', 'category': category, 'art': '/assets/spells/' + key + '.webp', 'description': form['description'], 'effect': form['effect'], 'requirements': [g.PRINCIPLE_NAMES[p] for p in form['requiredPrinciples']] + ['Testing room: ' + g.ROOMS[form['roomId']]['name'], 'Personal learning, testing and a prepared spell slot.'], 'cost': components(form['castingInputs'], g.MATERIALS), 'duration': 'Instant eligible core travel' if form.get('field') == 'teleport' else 'One assigned casting phase or one listed field action', 'limits': [form.get('limits', 'The listed effect applies only to its authored work.')] , 'learning': 'Testing costs 4 crowns, two suitable components and two assigned phases. Required component properties: ' + ', '.join(form['requiredProperties']) + '.', 'knownBy': sorted(set(owners)), 'scholarNote': note(key), 'destination': 'spells'})
    completed = state.get('lastingRituals', {}).get('completed', {})
    for key, ritual in lasting_rituals.CATALOGUE.items():
        rows.append({'id': key, 'name': ritual['name'], 'kind': 'ritual', 'collection': 'castle', 'category': 'Lasting household ritual', 'art': '/assets/spells/' + key + '.webp', 'description': ritual['effect'], 'effect': ritual['effect'], 'requirements': ['Conductor: ' + ' + '.join(g.PRINCIPLE_NAMES[p] for p in ritual['principles']), 'Partner: at least one of those principles.', 'Two different resident participants at home.', 'Room: ' + h.ROOMS[ritual['room']]['name']], 'cost': str(ritual['cost']) + ' crowns + ' + components(ritual['materials'], g.MATERIALS), 'duration': str(ritual['phases']) + ' shared phases; one fewer when both participants meet the Channeling aptitude requirement', 'limits': ['Both participants must keep their ritual assignments; interruptions preserve paid progress.', 'An inscribed circle can be suspended and reactivated without erasing it.'], 'status': 'Active' if completed.get(key, {}).get('active') else 'Suspended' if key in completed else 'Not yet inscribed', 'scholarNote': note(key), 'destination': 'rituals'})
    for row in rows:
        if row['kind']=='ritual' and lasting_rituals.CATALOGUE.get(row['id'],{}).get('repeatable'):
            row.update(category='Expedition preparation ritual',status='Ready for next patrol' if row['id'] in state.get('fieldPreparations',{}) else 'Not prepared',duration='Two shared preparation phases; one when both participants qualify. One outgoing patrol only.',limits=['Both participants work together at home. Interruptions preserve progress; cancelling unfinished preparation refunds costs.', 'A ready preparation waits until a patrol departs. Remaining protection ends on return or retreat. Prepare again for another patrol.'])
    specials = [
        {'id':'concordant-lesson','name':'The concordant lesson','artKey':'archive-circle','description':'A shared memory exercise using the living index.','effect':'The scholar and Mira each gain three base preparation slots instead of two. Existing prepared spells remain chosen.','requirements':['The scholar and Mira must be home and personally know Reference binding.','At least one participant knows Clear instruction.','The living index charm is installed.'],'cost':'18 crowns + one vessel and one binding component per participant (four components total)','duration':'Two shared phases, with both participants assigned','limits':['One-time ritual; no change to personality or relationships.'],'destination':'rituals'},
        {'id':'lamplit-sight','name':'Lamplit sight','artKey':'lucid-sight','description':'A voluntary personal blessing with a faint violet glint in the eyes.','effect':'Adds one personal spell-preparation slot while active.','requirements':['Personally know Gentle refraction.','A usable library; the scholar and recipient must be home.','Available to the scholar, and to Mira or Tamsin after her professional project.'],'cost':'10 crowns + ' + components(g.AUGMENTATION_MATERIALS,g.MATERIALS),'duration':'Two personal ritual phases','limits':['Does not stack. An unfinished receiving ritual can be cancelled for a refund.'],'destination':'development'},
        {'id':'lamplit-reversal','name':'Reversal of Lamplit sight','artKey':'lucid-sight','description':'Freely set aside the personal blessing.','effect':'Restores ordinary appearance and the previous spell capacity.','requirements':['An active Lamplit sight blessing and no unfinished personal ritual.','Both people at home; put aside enough prepared spells to fit the restored capacity.'],'cost':'No crowns or supplies','duration':'One personal ritual phase','limits':['No penalty to personality, relationships or learned spells.'],'destination':'development'},
    ]
    for row in specials:
        row.update({'kind':'ritual','collection':'castle','category':'Personal and shared ritual','art':'/assets/spells/'+row.pop('artKey')+'.webp','scholarNote':note(row['id'])})
        rows.append(row)
    import foundation_chamber as fc
    rows.append({'id':'foundation-intimacy','name':'Foundation chamber ritual','kind':'ritual','collection':'castle',
        'category':'Household relationship blessing','art':'/assets/spells/foundation-intimacy.webp',
        'description':'An optional intimacy ritual, presented through a fade to black.',
        'effect':'+20% to positive trust, affection, respect and resident bonding gains throughout the household for 9 phases (three days). A gain of 1 becomes 1.2; 2 becomes 2.4.',
        'requirements':['Restore the foundation chamber after Chapter 5 and complete both circuit tests.',
            'You and an adult resident partner must have shared the Private evening relationship milestone, with romantic invitations enabled.',
            'Both participants must be home and assigned to Rest before agreeing to the ritual.'],
        'cost':'No crowns or materials per ritual; one shared phase. Restoring the chamber costs 24 crowns, 2 binding thread, 2 porous clay and 1 fireglass.',
        'duration':'One shared phase to perform; the blessing lasts the following 9 phases.',
        'limits':['Renewing refreshes the duration; the percentage never stacks.',
            'Only positive gains are increased. Score ceilings and relationship choices remain in place.',
            'Bonding bonus points do not use the ordinary four-point daily bonding allowance.'],
        'status':'Active: '+str(fc.bonus_view(state)['remainingPhases'])+' phases remaining' if fc.active(state) else 'Ready' if fc.ready(state) else 'Restore and test the chamber after Chapter 5',
        'scholarNote':{'quote':'We measured the same increase in every occupied wing. The chamber shares its effect through the foundation channels.',
            'author':'Scholar Elian Voss','work':'Notes on Household and Field Magic'},'destination':fc.VIEW})
    return {'entries': rows + workshop_entries(), 'castleSpellCount':len(g.SPELL_FORMS), 'castleRitualCount':len(lasting_rituals.CATALOGUE)+len(specials)+1, 'workshopCount':len(workshop_entries())}
