"""Persistent authored conversations; reads expose only the reached exchange.

Every answer is validated against the current turn. game.apply_action stages
these writes atomically; GameStore supplies durable revision/idempotency checks.
No answer advances time, assigns work, spends resources or establishes romance.
"""
from copy import deepcopy

import companion_almanac as almanac
import companion_threads_content as content
from social_life import stamp


def initialize(state):
    state.setdefault('companionThreads', {
        'records': {}, 'preferences': {}, 'preferenceUpdates': [], 'deferred': []})


def saved(state):
    return state.get('companionThreads', {
        'records': {}, 'preferences': {}, 'preferenceUpdates': [], 'deferred': []})


def keys(state):
    members = set(almanac.members(state))
    personal = [kind + ':' + who for who in content.PERSONAL if who in members
                for kind in ('personal', 'followup')]
    peers = [kind + ':' + pair for pair, data in content.PAIRS.items()
             if set(data['people']) <= members for kind in ('pair', 'pair-followup')]
    return personal + peers


def definition(key):
    kind, subject = key.split(':', 1)
    is_pair = kind in ('pair', 'pair-followup')
    data = content.PAIRS[subject] if is_pair else content.PERSONAL[subject]
    later = kind in ('followup', 'pair-followup')
    title = (data['laterTitle'] if is_pair else 'Another visit · ' + data['title']) if later else data['title']
    return {'kind': kind, 'subject': subject, 'title': title,
            'participants': ['founder'] + (data['people'] if is_pair else [subject]),
            'totalTurns': 2 if later else 3,
            'previousId': (('pair:' if is_pair else 'personal:') + subject) if later else None}


def preference_options(who):
    data = content.PERSONAL[who]
    return [*data['options'],
            ('I am not sure; ask me at the time', data['uncertainty']),
            ('I would rather not discuss my preference', data['privacy'])]


def current_node(state, key, turn):
    d = definition(key)
    who = d['subject']
    if d['kind'] in ('pair', 'pair-followup'):
        data = content.PAIRS[who]
        return (data['laterNodes'] if d['previousId'] else data['nodes'])[turn]
    data = content.PERSONAL[who]
    if d['kind'] == 'personal':
        return [(data['opening'], data['approaches']),
                (data['question'], preference_options(who)),
                (data['decision'], data['endings'])][turn]
    choices, question, yes, once = content.FOLLOWUP[who]
    if turn:
        return question, [yes, once]
    pref = saved(state)['preferences'].get(who)
    # Old/corrected preferences never become knowledge for another resident.
    index = pref['choice'] if pref else 2
    opening = data['followups'][index]
    previous = saved(state)['records'].get(d['previousId'])
    if previous and previous.get('stance') == 'disagree':
        opening += '\n\n' + data['unresolved']
    return opening, choices


def blockers(state, key, d):
    reasons = almanac.present(state, d['participants'])
    memories = almanac.saved(state)['memories']
    import game
    for who in d['participants'][1:]:
        if 'familiar:' + who not in memories:
            reasons.append('Share ' + game.character_profile(state, who)['name'] + '’s first personal disclosure.')
    if d['previousId']:
        previous = saved(state)['records'].get(d['previousId'])
        if not previous or not previous['completed']:
            reasons.append('Finish “' + definition(d['previousId'])['title'] + '” first.')
        elif stamp(state) <= previous['stamp']:
            reasons.append('Let one day phase pass before this follow-up. The invitation does not expire.')
    return reasons


def row(state, key):
    d = definition(key)
    record = saved(state)['records'].get(key)
    completed = bool(record and record['completed'])
    turn = len(record['turns']) if record else 0
    reasons = [] if completed else blockers(state, key, d)
    deferred = key in saved(state)['deferred']
    available = not completed and not reasons and not deferred
    opening, options = current_node(state, key, turn) if available else ('', [])
    import foundation_chamber
    multiplier = foundation_chamber.multiplier(state)
    effect = ('No time or supplies. On completion: up to Trust +' + format(multiplier, 'g') +
              ' for each present pair, once (maximum 12). Respectful disagreement earns the same trust.')
    if len(d['participants']) > 2:
        effect += (' The two residents also gain up to Bonding +' + format(2 * multiplier, 'g') +
                   ', within their daily allowance (maximum 100).')
    if multiplier > 1:
        effect += ' The active foundation blessing’s +20% is included.'
    # Do not include authored answers, future nodes or unchosen branches.
    return {**d, 'id': key, 'turn': turn, 'available': available,
            'completed': completed, 'deferred': deferred, 'blockers': reasons,
            'opening': opening, 'choices': {str(i): {'label': label} for i, (label, _) in enumerate(options)},
            'record': deepcopy(record),
            'effect': effect}


def profile(state, who):
    if who not in almanac.members(state):
        return None
    data = saved(state)
    preference = deepcopy(data['preferences'].get(who))
    record = data['records'].get('followup:' + who)
    return {'preference': preference,
            'preferenceChoices': {str(i): {'label': label} for i, (label, _) in enumerate(preference_options(who))} if preference else {},
            'canChangePreference': bool(preference) and not almanac.present(state, ['founder', who]),
            'tradition': content.PERSONAL[who]['tradition'] if record and record.get('traditionAgreed') else None,
            'updates': deepcopy([u for u in data['preferenceUpdates'] if u['personId'] == who])}


def views(state):
    scenes = [row(state, key) for key in keys(state)]
    return {'scenes': scenes,
            'people': {who: profile(state, who) for who in almanac.members(state)},
            'readyCount': sum(r['available'] for r in scenes)}


def context(state, who):
    if who not in almanac.members(state):
        return {}
    data = saved(state)
    return {'conversations': deepcopy([r for r in data['records'].values()
                                       if who in r['participants']]),
            'currentPlayerPreference': deepcopy(data['preferences'].get(who)),
            'preferenceCorrections': deepcopy([u for u in data['preferenceUpdates'] if u['personId'] == who]),
            'agreedTradition': profile(state, who)['tradition'],
            'guidance': 'Only these reached exchanges happened. A preference was shared with this resident alone. Use the latest correction. Uncertainty is not dislike; privacy means do not press for a reason or keep asking. A disagreement may remain open. Plans for a future visit are not completed activities.'}


def preference_record(state, who, choice):
    label, _ = preference_options(who)[choice]
    return {'personId': who, 'question': content.PERSONAL[who]['question'],
            'choice': choice, 'status': 'known' if choice < 2 else 'unsure' if choice == 2 else 'private',
            'playerLine': label, 'dayNumber': state['dayNumber'],
            'phase': state['currentDayPhase'], 'stamp': stamp(state)}


def apply(state, action):
    import game
    kind = action.get('type')
    if kind not in ('thread-answer', 'thread-defer', 'thread-restore', 'thread-preference'):
        return False
    choice = action.get('choice')
    if kind == 'thread-preference':
        who = action.get('personId')
        game.require(isinstance(who, str) and who in almanac.members(state), 'Choose a current companion.')
        game.require(who in saved(state)['preferences'], 'Share this preference in her conversation first.')
        game.require(not almanac.present(state, ['founder', who]), 'Return home together to discuss a change.')
        game.require(isinstance(choice, str) and choice in ('0', '1', '2', '3'), 'Choose one of the offered answers.')
        previous = saved(state)['preferences'][who]
        game.require(str(previous['choice']) != choice, 'She already remembers that answer.')
        initialize(state)
        new = preference_record(state, who, int(choice))
        saved(state)['preferences'][who] = new
        update = {**new, 'title': 'An updated preference',
                  'response': preference_options(who)[int(choice)][1]}
        saved(state)['preferenceUpdates'].append(update)
        game.add_journal(state, game.character_profile(state, who)['name'] + ': ' + new['playerLine'] + ' ' + update['response'])
        return True
    key = action.get('sceneId')
    game.require(isinstance(key, str) and key in keys(state), 'Choose a conversation with current adult residents.')
    r = row(state, key)
    game.require(not r['completed'], 'This conversation is already remembered. You can reread it without repeating its reward.')
    if kind == 'thread-restore':
        game.require(r['deferred'], 'This invitation has not been set aside.')
        initialize(state)
        saved(state)['deferred'].remove(key)
        return True
    if kind == 'thread-defer':
        game.require(not r['deferred'], 'This invitation is already set aside.')
        initialize(state)
        saved(state)['deferred'].append(key)
        return True
    game.require(r['available'], ' '.join(r['blockers']) or 'Restore this invitation before continuing.')
    expected = action.get('expectedTurn')
    game.require(type(expected) is int and expected == r['turn'], 'This conversation has moved on. Use the responses currently shown.')
    game.require(isinstance(choice, str) and choice in r['choices'], 'Choose one of the offered responses.')
    opening, options = current_node(state, key, r['turn'])
    label, response = options[int(choice)]
    initialize(state)
    d = definition(key)
    record = saved(state)['records'].setdefault(key, {
        'id': key, 'kind': d['kind'], 'title': d['title'], 'participants': d['participants'],
        'opening': opening, 'turns': [], 'completed': False})
    record['turns'].append({'opening': opening, 'choice': choice,
                            'playerLine': label, 'response': response,
                            'dayNumber': state['dayNumber'], 'phase': state['currentDayPhase']})
    record.update(dayNumber=state['dayNumber'], phase=state['currentDayPhase'], stamp=stamp(state))
    if d['kind'] == 'personal' and r['turn'] == 1:
        saved(state)['preferences'][d['subject']] = preference_record(state, d['subject'], int(choice))
    if len(record['turns']) == d['totalTurns']:
        record['completed'] = True
        if d['kind'] == 'personal':
            record['stance'] = ('support', 'disagree', 'independent')[int(choice)]
        elif d['kind'] == 'followup':
            record['traditionAgreed'] = choice == '0'
        # Standard journal/relationship consumers get an exact readable transcript.
        record['playerLine'] = record['turns'][0]['playerLine']
        record['response'] = '\n\n'.join(
            ([record['turns'][0]['response']] + [t['opening'] + '\nYou: ' + t['playerLine'] + '\n' + t['response'] for t in record['turns'][1:]]))
        import relationships
        relationships.remember(state, 'thread:' + key, record, dimension='trust')
        game.add_journal(state, 'Conversation remembered: ' + d['title'] + '. The full exchange is in your journal.')
    return True
