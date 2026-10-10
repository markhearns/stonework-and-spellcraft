"""Simple mutual resident bonds, separate from the player's relationship system.

Only committed activities award points. Reads stay pure; each pair owns one
record, so both profiles agree. History and repeat protection are bounded.
"""
from copy import deepcopy
from itertools import combinations

MAX_SCORE = 100
DAILY_CAP = 4
LEVELS = ((0, 'New acquaintances'), (10, 'Familiar'), (25, 'Friendly'),
          (45, 'Close friends'), (70, 'Trusted companions'), (100, 'Deeply bonded'))
EMPTY = {'pairs': {}}


def saved(s):
    return s.get('residentBonds', EMPTY)


def pair_id(a, b):
    return '|'.join(sorted((a, b)))


def empty_pair(a, b):
    return {'participants': sorted((a, b)), 'score': 0, 'history': [],
            'daily': {'day': None, 'earned': 0, 'sources': []}}


def initialize(s):
    """One-time import of recorded history, without rewriting its source."""
    if 'residentBonds' in s:
        return
    s['residentBonds'] = deepcopy(EMPTY)
    pairs = s['residentBonds']['pairs']

    def seed(people, points, title):
        people = sorted(set(p for p in people if p != 'founder'))
        for a, b in combinations(people, 2):
            row = pairs.setdefault(pair_id(a, b), empty_pair(a, b))
            gain = min(MAX_SCORE - row['score'], points)
            if gain <= 0:
                continue
            row['score'] += gain
            row['history'].append({'title': title, 'gain': gain, 'imported': True})
            row['history'] = row['history'][-5:]

    for bond in s.get('relationships', {}).get('bonds', {}).values():
        seed(bond['participants'], 2 * sum(max(0, bond.get(k, 0))
             for k in ('trust', 'affection', 'respect')), 'Earlier shared relationship history')
    from resident_moments import MOMENTS
    for key, record in s.get('residentMoments', {}).items():
        if record.get('status') == 'complete' and key in MOMENTS:
            seed(MOMENTS[key]['participants'], 2, MOMENTS[key]['title'])
    for record in s.get('householdScenes', {}).values():
        if record.get('status') == 'remembered':
            seed(record['participants'], 2, record['title'])


def award(s, participants, source, title, amount=1):
    """Single award gateway, ready for future castle-wide progression effects."""
    import game as g
    residents = set(g.household_members(s)) - {'founder'}
    people = sorted(set(participants) & residents)
    if len(people) < 2 or amount <= 0:
        return []
    initialize(s)
    changes = []
    for a, b in combinations(people, 2):
        key = pair_id(a, b)
        row = saved(s)['pairs'].setdefault(key, empty_pair(a, b))
        if row['score'] >= MAX_SCORE:
            continue
        if row['daily']['day'] != s['dayNumber']:
            row['daily'] = {'day': s['dayNumber'], 'earned': 0, 'sources': []}
        daily = row['daily']
        if source in daily['sources'] or daily['earned'] >= DAILY_CAP:
            continue
        import foundation_chamber
        base = min(int(amount), DAILY_CAP - daily['earned'])
        gain = round(min(base * foundation_chamber.multiplier(s), MAX_SCORE - row['score']), 1)
        if not gain:
            continue
        daily['sources'].append(source)
        daily['earned'] += base
        daily['bonusEarned'] = round(daily.get('bonusEarned', 0) + max(0, gain - base), 1)
        row['score'] = round(row['score'] + gain, 1)
        row['history'].append({'title': title, 'gain': gain,
                               'dayNumber': s['dayNumber'], 'phase': s['currentDayPhase']})
        row['history'] = row['history'][-5:]
        changes.append({'id': key, 'participants': [a, b], 'gain': gain})
    return changes


def phase_groups(s):
    """Snapshot real work and shared leisure before work releases assignments."""
    import game as g
    import headquarters as h
    import room_life
    import house_shape
    import household_sagas
    import arms_of_our_own
    import lasting_rituals
    home = [p for p in g.household_members(s) if p != 'founder' and g.character_at_castle(s, p)]
    assignments = {p: g.character_assignment(s, p) for p in home}
    groups = []

    def add(key, title, people):
        if len(set(people) - {'founder'}) >= 2:
            groups.append((key, title, list(people)))

    if s['researchStatus'] == 'in-progress' or s['activeResearchId']:
        add('research', 'Working on shared research', [p for p in home if assignments[p] == 'archive'])
    if s['miraArchiveProject']['status'] == 'in-progress':
        add('living-index', 'Studying the living index together', [p for p in home if assignments[p] == 'archive-project'])
    for kind, title in [('garden', 'Tending the conservatory together'),
                        ('hunt', 'Hunting for household provisions'),
                        ('forage', 'Foraging for household provisions'),
                        ('road-patrol', 'Keeping the road watch together')]:
        if kind == 'garden' and not g.room_available(s, 'conservatory'):
            continue
        if kind == 'road-patrol' and not s.get('roadsWeKeep', {}).get('refugeDone'):
            continue
        add(kind, title, [p for p in home if assignments[p] == kind])
    for who, project in s['trainingProjects'].items():
        if (project and project.get('teacherId') and who in home
                and assignments[who] == 'training' and not g.lesson_blockers(s, who)):
            add('lesson:' + who, 'An agreed lesson together', [who, project['teacherId']])
    ritual = lasting_rituals.state(s)['project']
    if ritual and lasting_rituals.ready(s, ritual):
        add('ritual', 'Working together: ' + lasting_rituals.CATALOGUE[ritual['id']]['name'], ritual['participants'])
    add('house-shape', 'Restoring a shared household undertaking', house_shape.eligible(s))
    saga = household_sagas.eligible(s)
    if saga:
        add('household-project', 'Working on an agreed household project', household_sagas.record(s, saga)['project']['workers'])
    if arms_of_our_own.drill_working(s):
        add('drill', 'Practising the agreed field kit together', arms_of_our_own.saved(s)['drill']['participants'])
    rooms = {}
    for who in home:
        if assignments[who] != 'rest':
            continue
        room = room_life.location(s, who)
        if room in ('library', 'common-room', 'conservatory', 'hot-spring', 'sauna', 'pool') and h.ready(s, room):
            rooms.setdefault(room, []).append(who)
    for room, people in rooms.items():
        add('leisure:' + room, 'Shared leisure in the ' + h.ROOMS[room]['name'].lower(), people)
    return groups, home


def resolve_phase(s, snapshot, summary):
    import headquarters as h
    groups, home = snapshot
    meal = s.get('provisions', {}).get('lastMeal')
    if (s['currentDayPhase'] == 'evening' and meal and meal['day'] == s['dayNumber']
            and meal['served'] == meal['needed'] and h.ready(s, 'kitchen')):
        groups.append(('meal', 'Sharing a household meal', home))
    changes = []
    for key, title, people in groups:
        changes.extend(award(s, people, 'phase:' + s['currentDayPhase'] + ':' + key, title))
    summarize(s, changes, summary)


def summarize(s, changes, summary):
    if not changes:
        return
    import game as g
    totals = {}
    for change in changes:
        totals[change['id']] = round(totals.get(change['id'], 0) + change['gain'], 1)
    if len(totals) <= 3:
        detail = '; '.join(' & '.join(g.character_profile(s, p)['name'] for p in key.split('|'))
                           + ' +' + str(gain) for key, gain in totals.items())
        summary.append('Resident bonding: ' + detail + '. See their profiles for the shared activity.')
    else:
        summary.append('Resident bonding grew across ' + str(len(totals)) + ' pairs through shared activities. See their profiles for details.')


def view(s):
    import game as g
    residents = [p for p in g.household_members(s) if p != 'founder']
    rows = []
    for a, b in combinations(residents, 2):
        key = pair_id(a, b)
        row = saved(s)['pairs'].get(key, empty_pair(a, b))
        level = max(i for i, (minimum, _) in enumerate(LEVELS) if row['score'] >= minimum)
        earned = row['daily']['earned'] if row['daily']['day'] == s['dayNumber'] else 0
        rows.append({'id': key, 'participants': sorted((a, b)), 'score': row['score'],
                     'level': level, 'label': LEVELS[level][1],
                     'nextAt': LEVELS[level + 1][0] if level + 1 < len(LEVELS) else None,
                     'today': earned, 'todayBonus': row['daily'].get('bonusEarned',0) if earned else 0,
                     'history': deepcopy(row['history'])})
    return {'pairs': rows, 'maximum': MAX_SCORE, 'dailyCap': DAILY_CAP,
            'levels': [{'level': i, 'score': n, 'label': label} for i, (n, label) in enumerate(LEVELS)]}
