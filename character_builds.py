"""Individual attributes, affinities and earned perks. All balance is provisional.

No ancestry or descriptive occupation grants a mechanical rank. Training shares
one primary assignment with every other activity and uses existing advancement.
"""
from copy import deepcopy

ATTRIBUTES = {
    'might': {'name': 'Might', 'description': 'Strength, leverage and physical force. Combines with Athletics for lifting, hauling and forceful expedition routes.'},
    'dexterity': {'name': 'Dexterity', 'description': 'Agility and precision. Combines with Fieldcraft for crossings and Artifice for mechanisms. At 8: +1 crafting work.'},
    'vitality': {'name': 'Vitality', 'description': 'Physical endurance and resilience. Combines with Athletics for sustained effort and safe endurance routes; at 8: receiving first aid or resting restores one extra health (maximum 6).'},
    'intelligence': {'name': 'Intelligence', 'description': 'Reasoning, knowledge and understanding. Combines with Scholarship for ciphers and Artifice for engineering. At 8: +1 research/archive work.'},
    'resolve': {'name': 'Resolve', 'description': 'Willpower, concentration and composure. Combines with Channeling for magical control. At 8: +1 personal spell preparation slot.'},
    'charisma': {'name': 'Charisma', 'description': 'Persuasion, expression and social presence. Combines with Diplomacy for additional conversational and negotiation approaches. Never replaces ordinary responses.'},
}
# Individual aptitudes, not ancestry modifiers. All named profiles use the same 30-point budget.
PROFILES = {
 'founder': (5,5,5,5,5,5), 'mira': (3,5,4,7,6,5),
 'tamsin': (5,5,6,4,4,6), 'iona': (4,6,5,5,4,6),
 'aurelia': (6,5,6,4,6,3), 'neris': (3,7,4,7,5,4),
  'sabine': (3,5,4,6,5,7),
 'maren': (5,7,5,6,4,3), 'brakka': (7,4,7,4,5,3),
 'fenna': (3,7,4,5,4,7), 'kaede': (5,7,5,4,6,3),
 'elowen': (3,4,5,6,5,7), 'nyssara': (3,6,4,7,6,4),
 'sylva': (4,4,6,6,6,4),
}

def baseline(who='founder'):
    return dict(zip(ATTRIBUTES, PROFILES.get(who, PROFILES['founder'])))

AFFINITIES = {
    'light': {'name': 'Light', 'principles': ['gentle-refraction', 'luminous-copying'], 'forms': ['luminous-copy', 'clarify-glass'], 'description': 'At rank 1, qualifies for Light-related perks. At rank 2, Luminous transcription produces 2 extra crowns and Glass clarification produces 1 extra moon glass per casting.'},
    'growth': {'name': 'Growth', 'principles': ['steady-growth', 'water-guidance'], 'forms': ['root-song'], 'description': 'At rank 1, qualifies for Growth-related perks. At rank 2, Root-song tending produces 1 extra silver ivy per casting.'},
    'hearth': {'name': 'Hearth', 'principles': ['steady-hearth-wards', 'gentle-preservation'], 'forms': ['warm-twist'], 'description': 'At rank 1, qualifies for Hearth-related perks. At rank 2, Warm-twist binding produces 1 extra binding thread per casting; it still consumes its input.'},
}
PERKS = {
    'archive-synthesis': {'name': 'Archive synthesis', 'attribute': 'intelligence', 'skill': 'scholarship', 'affinity': 'light', 'description': 'One extra research/archive work contribution. Does not increase copying income or speed training.'},
    'living-methods': {'name': 'Living methods', 'attribute': 'intelligence', 'skill': 'scholarship', 'affinity': 'growth', 'description': 'One extra silver ivy from each personally cast Root-song tending. Adds to the Growth rank 2 bonus.'},
    'patient-hands': {'name': 'Patient hands', 'attribute': 'dexterity', 'skill': 'artifice', 'affinity': 'hearth', 'description': 'One extra crafting work contribution. Does not speed personal projects, focus work or spell testing.'},
    'glasswright': {'name': 'Glasswright', 'attribute': 'dexterity', 'skill': 'artifice', 'affinity': 'light', 'description': 'One extra fireglass from each personally cast Glass clarification. Adds to the Light rank 2 bonus.'},
    'spell-repertoire': {'name': 'Spell repertoire', 'attribute': 'resolve', 'skill': 'scholarship', 'affinity': 'light', 'description': 'One extra personal spell-preparation slot. Does not grant spells, knowledge or a second action.'},
    'hearth-weaver': {'name': 'Hearth weaver', 'attribute': 'resolve', 'skill': 'artifice', 'affinity': 'hearth', 'description': 'One extra binding thread from each personally cast Warm-twist binding. Adds to the Hearth rank 2 bonus; inputs are still consumed.'},
}
PERKS.update({
 'powerful-frame':{'name':'Practised strength','attribute':'dexterity','skill':'artifice','affinity':'hearth','ancestries':['Bovinefolk','Oni'],'description':'Turn physical strength into controlled workshop technique: +1 crafting work contribution. No faster research, personal stories, training or ritual.'},
 'enduring-focus':{'name':'Enduring focus','attribute':'resolve','skill':'scholarship','affinity':'hearth','ancestries':['Orc'],'description':'Sustain a personal story study: +1 own story work contribution per assigned phase. No extra action or reward; no faster training or construction.'},
 'keen-observation':{'name':'Practised keen observation','attribute':'intelligence','skill':'scholarship','affinity':'light','ancestries':['Wolfkin'],'description':'Train sharp senses into careful comparisons: +1 research/archive work contribution. Does not reveal secrets, grant discoveries or shorten travel.'},
})
KINDS = {'attribute': (ATTRIBUTES, 3, 3), 'affinity': (AFFINITIES, 2, 2), 'perk': (PERKS, 3, 2)}


def empty_build(who='founder'):
    return {'attributeInvestment': 0, 'attributes': baseline(who), 'affinities': {key: 0 for key in AFFINITIES}, 'perks': []}


def initialize(state):
    records = state.setdefault('characterBuilds', {})
    for who in state['characterDevelopment']:
        records.setdefault(who, empty_build(who))


def build(state, who):
    # Safe during upgrades of saves that predate this system. Never mutates reads.
    return state.get('characterBuilds', {}).get(who, empty_build(who))


def invested(state, who):
    record = build(state, who)
    return record.get('attributeInvestment', 0) + 2 * sum(record['affinities'].values()) + 3 * len(record['perks'])


def reserved(project):
    return KINDS[project['kind']][1] if project and project['kind'] in KINDS else 0


def capacity_bonus(state, who):
    record = build(state, who)
    return int(record['attributes']['resolve'] >= 8) + int('spell-repertoire' in record['perks'])


def work_parts(state, who, practice):
    record = build(state, who)
    attribute, perk = ('intelligence', 'archive-synthesis') if practice == 'archive-focus' else ('dexterity', 'patient-hands')
    parts = []
    if record['attributes'][attribute] >= 8:
        parts.append({'name': ATTRIBUTES[attribute]['name'] + ' 8+', 'amount': 1})
    if perk in record['perks']:
        parts.append({'name': PERKS[perk]['name'], 'amount': 1})
    trait='keen-observation' if practice=='archive-focus' else 'powerful-frame'
    if trait in record['perks']:parts.append({'name':PERKS[trait]['name'],'amount':1})
    return parts


def casting_output(state, who, form_id):
    import game as g
    definition = g.SPELL_FORMS[form_id]
    materials, crowns = deepcopy(definition['materialOutput']), definition['crownsOutput']
    record = build(state, who)
    bonuses = []
    for key, affinity in AFFINITIES.items():
        if form_id in affinity['forms'] and record['affinities'][key] == 2:
            if crowns:
                crowns += 2
            else:
                for material in materials: materials[material] += 1
            bonuses.append(affinity['name'] + ' affinity rank 2')
    perk = {'root-song': 'living-methods', 'clarify-glass': 'glasswright', 'warm-twist': 'hearth-weaver'}.get(form_id)
    if perk in record['perks']:
        for material in materials: materials[material] += 1
        bonuses.append(PERKS[perk]['name'])
    return {'materialOutput': materials, 'crownsOutput': crowns, 'bonuses': bonuses}


def requirements(state, who, kind, target):
    import game as g
    record = build(state, who)
    definition = KINDS[kind][0][target]
    needs, blockers = [], []
    if definition.get('ancestries'):
        needs.append('Ancestry: '+' or '.join(definition['ancestries']))
        if g.character_profile(state,who)['ancestryLabel'] not in definition['ancestries']:blockers.append('This physical training path belongs to '+' or '.join(definition['ancestries'])+'.')
    if kind == 'attribute':
        if record['attributes'][target] >= 10: blockers.append('Maximum attribute score reached: 10.')
    elif kind == 'affinity':
        names = ' or '.join(g.PRINCIPLE_NAMES[p] for p in definition['principles'])
        needs.append('Personally understand ' + names)
        if not any(p in g.character_principles(state, who) for p in definition['principles']):
            blockers.append('Study ' + names + ' before developing this affinity.')
        if record['affinities'][target] >= 2: blockers.append('Maximum affinity rank reached: 2.')
    else:
        if target in record['perks']: blockers.append('This perk is already learned.')
        attribute, skill, affinity = definition['attribute'], definition['skill'], definition['affinity']
        for label, rank, required in ((ATTRIBUTES[attribute]['name'], record['attributes'][attribute], 6), (g.CHARACTER_SKILLS[skill]['name'], g.skill_rank(state, who, skill), 1), (AFFINITIES[affinity]['name'] + ' affinity', record['affinities'][affinity], 1)):
            needs.append(label + ' rank ' + str(required))
            if rank < required: blockers.append('Requires ' + label + ' rank ' + str(required) + '.')
    return needs, blockers


def view(state, who):
    import game as g
    record = deepcopy(build(state, who))
    record['options'] = []
    sheet = g.character_sheet(state, who)
    for kind, (catalogue, cost, phases) in KINDS.items():
        for target, definition in catalogue.items():
            if definition.get('ancestries') and g.character_profile(state,who)['ancestryLabel'] not in definition['ancestries']:continue
            needs, blockers = requirements(state, who, kind, target)
            if not g.character_at_castle(state, 'founder') or not g.character_at_castle(state, who): blockers.append('Return home together to agree this training.')
            if sheet['trainingProject']: blockers.append('Finish or cancel the current learning project first.')
            if sheet['availableAdvancement'] < cost: blockers.append('Needs ' + str(cost) + ' available advancement.')
            rank = record['attributes'][target] if kind == 'attribute' else record['affinities'][target] if kind == 'affinity' else int(target in record['perks'])
            record['options'].append({'kind': kind, 'id': target, **deepcopy(definition), 'rank': rank, 'cost': cost, 'phases': phases, 'requirements': needs, 'blockers': blockers})
    record['castingOutputs'] = {key: casting_output(state, who, key) for key in g.SPELL_FORMS}
    record['retrainingBlockers'] = retraining_blockers(state, who)
    return record


def retraining_blockers(state, who):
    import game as g
    capacity = (3 if who in g.RITUAL_PARTICIPANTS and state['spellRitual']['status'] == 'complete' else 2) + int(state['personalAugmentations'][who]['active'])
    return ['Put aside personal spells until at most ' + str(capacity) + ' are prepared before retraining.'] if len(state['preparedSpells'][who]) > capacity else []


def apply_action(state, action):
    if action.get('type') != 'train-character-build': return False
    import game as g
    who, kind, target = action.get('characterId'), action.get('buildKind'), action.get('targetId')
    g.require(isinstance(who, str) and who in g.household_members(state), 'Choose a current household member.')
    g.require(isinstance(kind, str) and kind in KINDS, 'Choose an attribute, affinity or perk.')
    g.require(isinstance(target, str) and target in KINDS[kind][0], 'Choose a supported development.')
    option = next((row for row in view(state, who)['options'] if row['kind'] == kind and row['id'] == target),None)
    g.require(option is not None,'This ancestry has not offered that training path.')
    g.require(not option['blockers'], ' '.join(option['blockers']))
    state['trainingProjects'][who] = {'kind': kind, 'targetId': target, 'completedWorkPhases': 0, 'requiredWorkPhases': option['phases']}
    g.set_character_assignment(state, who, 'training')
    g.add_journal(state, g.character_profile(state, who)['name'] + ' agreed to develop ' + option['name'] + ': ' + str(option['cost']) + ' advancement reserved, ' + str(option['phases']) + ' own learning phases.')
    return True


def complete(state, who, project, summary):
    import game as g
    kind, target = project['kind'], project['targetId']
    record = state['characterBuilds'][who]
    if kind == 'perk': record['perks'].append(target)
    else:
        record['attributes' if kind == 'attribute' else 'affinities'][target] += 1
        if kind == 'attribute':
            record['attributes'][target] = max(record['attributes'][target], project.get('legacyCompletionScore', 0))
            record['attributeInvestment'] = record.get('attributeInvestment', 0) + 3
    summary.append(g.character_profile(state, who)['name'] + ' developed ' + KINDS[kind][0][target]['name'] + '. Its listed benefits are now active; no extra action was granted.')


def output_description(state, who, form_id):
    import game as g
    if g.SPELL_FORMS[form_id].get('support') or g.SPELL_FORMS[form_id].get('field'):
        return g.SPELL_FORMS[form_id]['effect']+' Trained casting: Resolve + twice Channeling at 9 adds one enchantment charge; Dexterity + twice Channeling at 9 adds one valid offensive damage; Intelligence + twice Channeling at 9 adds one healing. Health remains capped at 6.'
    output = casting_output(state, who, form_id)
    parts = [str(count) + ' ' + g.MATERIALS[key]['name'] for key, count in output['materialOutput'].items()]
    if output['crownsOutput']: parts.append(str(output['crownsOutput']) + ' shared crowns')
    inputs = [str(count) + ' ' + g.MATERIALS[key]['name'] for key, count in g.SPELL_FORMS[form_id]['castingInputs'].items()]
    return 'Personal casting result: ' + ', '.join(parts) + ' per assigned phase. ' + ('Inputs: ' + ', '.join(inputs) + '. ' if inputs else 'No casting inputs. ') + ('Bonuses: ' + ', '.join(output['bonuses']) + '.' if output['bonuses'] else 'No build bonuses.')


def migrate(state):
    """Preserve old expenditure, completed benefits, and in-flight learning."""
    for who, record in state.get('characterBuilds', {}).items():
        if 'attributeInvestment' in record: continue
        old = record['attributes']
        scores = baseline(who)
        for key, rank in old.items():
            target = 'intelligence' if key == 'insight' else key
            if target in scores and rank > 1:
                scores[target] = max(scores[target] + rank - 1, 6 if rank == 2 else 8)
        record['attributeInvestment'] = 3 * sum(max(0, rank - 1) for rank in old.values())
        record['attributes'] = scores
        project=state.get('trainingProjects',{}).get(who)
        if project and project.get('kind')=='attribute':
            old_target=project.get('targetId')
            if old.get(old_target)==2:project['legacyCompletionScore']=8
    for project in state.get('trainingProjects', {}).values():
        if project and project.get('kind') == 'attribute' and project.get('targetId') == 'insight':
            project['targetId'] = 'intelligence'
    for skills in state.get('characterSkills', {}).values():
        for key in ('athletics', 'diplomacy', 'channeling'): skills.setdefault(key, 0)
