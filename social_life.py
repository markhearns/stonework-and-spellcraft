"""Remembered, opt-in dialogue with timed follow-ups and scoped social context."""
from copy import deepcopy
from social_content import CATALOGUE, PAIRS
import attribute_dialogue


def initialize(s):
    s.setdefault('socialLife', {'memories': {}, 'deferred': []})


def saved(s):
    return s.get('socialLife', {'memories': {}, 'deferred': []})


def stamp(s):
    import game as g
    return s['dayNumber'] * len(g.DAY_PHASES) + g.DAY_PHASES.index(s['currentDayPhase'])


def evidence(s, trigger):
    if trigger == 'spell':
        return any(p.get('castCount', 0) > 0 for p in s['spellbook'])
    if trigger == 'ritual':
        return bool(s.get('lastingRituals', {}).get('completed'))
    if trigger == 'journey':
        return (any(v for k, v in s.items() if k.endswith('Discoveries') and isinstance(v, list))
                or bool(s.get('fieldMagic', {}).get('aqueduct', {}).get('discoveries'))
                or bool(s.get('serviceRoad', {}).get('discoveries'))
                or bool(s.get('beaconJourney', {}).get('discoveries'))
                or bool(s.get('lanternAdventure', {}).get('discoveries')))
    return True


def blockers(s, key):
    from household_chapters import presence
    d = CATALOGUE[key]
    reasons = presence(s, d['participants'])
    past = saved(s)['memories'].get(d['previous'])
    if d['previous']:
        if not past:
            reasons.append('Share “' + CATALOGUE[d['previous']]['title'] + '” first.')
        elif stamp(s) <= past['stamp']:
            reasons.append('Let at least one day phase pass before returning to this conversation. No invitation expires.')
    trigger = d.get('trigger')
    if trigger and not evidence(s, trigger):
        reasons.append({'spell': 'Complete an actual household spell casting first.',
                        'journey': 'Bring an expedition discovery home first.',
                        'ritual': 'Complete a lasting ritual circle first.'}[trigger])
    return reasons


def row(s, key):
    d = CATALOGUE[key]
    data = saved(s)
    memory = data['memories'].get(key)
    reasons = blockers(s, key)
    previous = data['memories'].get(d['previous'])
    visible = bool(memory) or not reasons
    opening = d['opening']
    if previous and d.get('branches'):
        opening = d['branches'][previous['choice']] + '\n\n' + opening
    return {'id': key, 'title': d['title'], 'category': d['category'], 'participants': d['participants'][:],
            'stage': d['stage'], 'relationship': d.get('relationship'), 'roomId': 'common-room',
            'opening': memory['opening'] if memory else opening if visible else '',
            'choices': {**{k: {'label': v['label']} for k, v in d['choices'].items()}, **{k:{'label':v['label'], 'blockers':v['blockers'], 'check':v['check']} for k,v in attribute_dialogue.choices(s,key).items()}} if visible and not memory else {},
            'memory': deepcopy(memory), 'callback': deepcopy(previous) if previous else None,
            'blockers': reasons, 'available': not reasons and not memory,
            'deferred': key in data['deferred']}


def view(s):
    import game as g
    members = g.household_members(s)
    rows = [row(s, key) for key, d in CATALOGUE.items() if all(who in members for who in d['participants'])]
    ready = [r for r in rows if r['available'] and not r['deferred']]
    ready.sort(key=lambda r: (0 if r['stage'] else 1 if r['category'] == 'reactions' else 2, r['id']))
    # First choices deliberately exclude future replies. Reading the page cannot unlock a scene.
    return {'scenes': rows, 'invitations': [{'id': r['id'], 'title': r['title'], 'participants': r['participants'],
             'category': r['category'], 'followup': bool(r['stage'])} for r in ready[:3]],
            'readyCount': len(ready), 'rememberedCount': sum(bool(r['memory']) for r in rows),
            'totalCount': len(CATALOGUE), 'deferredCount': sum(r['deferred'] for r in rows),
            'bonds': [{'id': key, 'participants': d['participants'][:], 'label': d['label'],
                      'shared': sum(f'pair:{key}:{i}' in saved(s)['memories'] for i in range(3)),
                      'latest': next((deepcopy(saved(s)['memories'][f'pair:{key}:{i}']) for i in (2,1,0)
                                      if f'pair:{key}:{i}' in saved(s)['memories']), None)}
                     for key, d in PAIRS.items() if all(p in members for p in d['participants'])]}


def context(s, who):
    """Only this person's actual shared conversations, never future scenes or private gossip."""
    records = [m for m in saved(s)['memories'].values() if who in m['participants']]
    return deepcopy(sorted(records, key=lambda m: m['sequence'])[-12:])


def apply(s, a):
    kind = a.get('type')
    if kind not in ('share-social-conversation', 'defer-social-conversation', 'restore-social-conversation'):
        return False
    import game as g
    key = a.get('sceneId')
    g.require(isinstance(key, str) and key in CATALOGUE, 'Choose a known conversation.')
    d = CATALOGUE[key]
    g.require(all(p in g.household_members(s) for p in d['participants']), 'Every participant must be a current resident.')
    g.require(key not in saved(s)['memories'], 'This conversation is already remembered. Reread it without choosing again.')
    if kind == 'restore-social-conversation':
        g.require(key in saved(s)['deferred'], 'This invitation has not been set aside.')
        saved(s)['deferred'].remove(key)
        return True
    reasons = blockers(s, key)
    g.require(not reasons, ' '.join(reasons))
    if kind == 'defer-social-conversation':
        g.require(key not in saved(s)['deferred'], 'This invitation is already set aside.')
        initialize(s)
        saved(s)['deferred'].append(key)
        return True
    choice = a.get('choice')
    alternatives=attribute_dialogue.choices(s,key)
    g.require(isinstance(choice, str) and (choice in d['choices'] or choice in alternatives), 'Choose one of the offered responses.')
    selected=alternatives.get(choice) or d['choices'].get(choice)
    g.require(not selected.get('blockers'), ' '.join(selected.get('blockers',[])))
    current = row(s, key)
    initialize(s)
    data = saved(s)
    canonical = selected.get('follows', choice)
    record = {'id': key, 'title': d['title'], 'opening': current['opening'],
              'participants': d['participants'][:], 'category': d['category'], 'choice': canonical, 'approachId': choice if choice in alternatives else None, 'approachCheck':deepcopy(selected.get('check')),
              'playerLine': selected['label'], 'response': selected['response'],
              'dayNumber': s['dayNumber'], 'phase': s['currentDayPhase'], 'stamp': stamp(s),
              'sequence': len(data['memories']) + 1}
    data['memories'][key] = record
    import relationships
    relationships.remember(s,'social:'+key,{**record,'participants':['founder',*record['participants']]})
    if key in data['deferred']:
        data['deferred'].remove(key)
    g.add_journal(s, 'Shared ' + d['title'] + '. You chose: ' + selected['label'] + '. ' + selected['response'])
    return True
