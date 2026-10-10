"""Optional resident milestones, saved keepsakes and cooperation during real work."""
from copy import deepcopy
import resident_bonds as bonds
from resident_friendship_content import PROJECTS, HABITS

ASSIGNMENT = 'resident-friendship'
VIEW = 'residentFriendships'
EMPTY = {'pairs': {}, 'job': None}
STAGES = (('meeting', 10, 'Make time for one another'),
          ('project', 25, 'Make a shared keepsake'),
          ('visit', 45, 'Try it together'),
          ('tradition', 60, 'Return to a shared tradition'))


def saved(s):
    return s.get('residentFriendshipMilestones', EMPTY)


def initialize(s):
    s.setdefault('residentFriendshipMilestones', deepcopy(EMPTY))


def record(s, key):
    return saved(s)['pairs'].get(key, {'memories': {}, 'deferred': [], 'habit': None, 'keepsake': None})


def score(s, key):
    return bonds.saved(s)['pairs'].get(key, {}).get('score', 0)


def people(s, key):
    import game as g
    if not isinstance(key, str):
        return []
    pair = key.split('|')
    members = set(g.household_members(s)) - {'founder'}
    return pair if len(pair) == 2 and len(set(pair)) == 2 and key == bonds.pair_id(*pair) and set(pair) <= members else []


def next_stage(s, key):
    return next((row for row in STAGES if row[0] not in record(s, key)['memories']), None)


def definition(s, key):
    if key in PROJECTS:
        return PROJECTS[key]
    habit = HABITS.get(record(s, key)['habit'], HABITS['reading'])
    return dict(title=habit['project'], room=habit['room'], keepsake=habit['keepsake'],
                invitation='They would like to make something for the activity they chose together.',
                introduction=habit['lines'], completion=habit['completion'],
                outing='They would like a shared phase to use their keepsake and continue the activity they chose.',
                outingLines=habit['outingLines'], reflection=habit['reflection'])


def lines(s, key, raw):
    import game as g
    a, b = key.split('|')
    names = {'a_name': g.character_profile(s, a)['name'], 'b_name': g.character_profile(s, b)['name']}
    return [{'speaker': a if who == '{a}' else b if who == '{b}' else who,
             'text': text.format(**names)} for who, text in raw]


def blockers(s, key, stage=None, arranging=True):
    import game as g, headquarters as h
    pair = people(s, key)
    if not pair:
        return ['Choose two different current residents.']
    next_row = next_stage(s, key)
    if not next_row:
        return ['All of this pair’s friendship milestones are remembered.']
    current, minimum, _ = next_row
    if stage and stage != current:
        return ['Complete the earlier friendship milestone first.']
    reasons = []
    if score(s, key) < minimum:
        reasons.append('Needs '+str(minimum)+' bonding; this pair has '+str(score(s, key))+'.')
    if arranging and not g.character_at_castle(s, 'founder'):
        reasons.append('Return your scholar home to arrange or join this activity.')
    for who in pair:
        if not g.character_at_castle(s, who):
            reasons.append('Bring '+g.character_profile(s, who)['name']+' home first.')
    if current in ('project', 'visit'):
        room = definition(s, key)['room']
        if not h.ready(s, room):
            reasons.append('Restore '+h.ROOMS[room]['name']+' first.')
        if arranging:
            if saved(s)['job']:
                reasons.append('Finish or cancel the arranged shared activity first.')
            for who in pair:
                if g.character_assignment(s, who) != 'rest':
                    reasons.append('Set '+g.character_profile(s, who)['name']+' to Rest before arranging this activity.')
            if current == 'project' and s['sharedFunds'] < 4:
                reasons.append('Needs 4 shared crowns for the keepsake supplies.')
    return reasons


def job_blockers(s, resume=False):
    import game as g
    job = saved(s)['job']
    if not job:
        return []
    reasons = blockers(s, job['pairId'], job['stage'], False)
    if resume and not g.character_at_castle(s, 'founder'):
        reasons.append('Return your scholar home to resume this activity.')
    for who in job['participants']:
        if who not in g.household_members(s):
            continue
        assignment = g.character_assignment(s, who)
        if (resume and assignment not in ('rest', ASSIGNMENT)) or (not resume and assignment != ASSIGNMENT):
            reasons.append('Set '+g.character_profile(s, who)['name']+' to Rest, then resume the shared activity.' if resume else
                           g.character_profile(s, who)['name']+' is doing another task. The shared activity is paused.')
    return list(dict.fromkeys(reasons))


def release(s, job):
    import game as g
    for who in job['participants']:
        if who in g.household_members(s) and g.character_assignment(s, who) == ASSIGNMENT:
            g.set_character_assignment(s, who, 'rest')


def remember(s, key, stage, title, raw, summary=None):
    import game as g
    r = saved(s)['pairs'].setdefault(key, deepcopy(record(s, key)))
    dialogue = lines(s, key, raw)
    changes = bonds.award(s, key.split('|'), 'friendship:'+key+':'+stage, title, 2)
    r['memories'][stage] = dict(title=title, lines=dialogue, dayNumber=s['dayNumber'],
                               phase=s['currentDayPhase'], gain=round(sum(c['gain'] for c in changes), 1))
    if stage in r['deferred']:
        r['deferred'].remove(stage)
    names = ' & '.join(g.character_profile(s, w)['name'] for w in key.split('|'))
    text = names+': '+title+'. '+dialogue[-1]['text']
    if summary is not None:
        summary.append(text)
        bonds.summarize(s, changes, summary)
    else:
        g.add_journal(s, text)


def apply(s, action):
    import game as g
    kind = action.get('type', '')
    if not isinstance(kind, str) or not kind.startswith('friendship-'):
        return False
    initialize(s)
    if kind in ('friendship-resume', 'friendship-cancel'):
        job = saved(s)['job']
        g.require(job, 'There is no arranged shared activity.')
        if kind == 'friendship-cancel':
            s['sharedFunds'] += job['cost']
            release(s, job)
            saved(s)['job'] = None
            g.add_journal(s, 'Cancelled '+job['title']+'. '+str(job['cost'])+' committed crowns refunded. Its invitation remains available.')
        else:
            reasons = job_blockers(s, True)
            g.require(not reasons, ' '.join(reasons))
            for who in job['participants']:
                g.set_character_assignment(s, who, ASSIGNMENT)
        return True
    key, stage = action.get('pairId'), action.get('stage')
    g.require(people(s, key), 'Choose two different current residents.')
    row = next_stage(s, key)
    g.require(row and stage == row[0], 'Choose this pair’s next unshared milestone.')
    r = saved(s)['pairs'].setdefault(key, deepcopy(record(s, key)))
    if kind in ('friendship-defer', 'friendship-restore'):
        g.require(not saved(s)['job'] or saved(s)['job']['pairId'] != key, 'Cancel the arranged activity before putting its invitation aside.')
        g.require(score(s, key) >= row[1], 'Reach this milestone’s bonding requirement first.')
        if kind == 'friendship-defer':
            g.require(stage not in r['deferred'], 'This invitation is already set aside.')
            r['deferred'].append(stage)
        else:
            g.require(stage in r['deferred'], 'This invitation is not set aside.')
            r['deferred'].remove(stage)
        return True
    reasons = blockers(s, key, stage)
    g.require(not reasons, ' '.join(reasons))
    g.require(stage not in r['deferred'], 'Return this invitation before accepting it.')
    d = definition(s, key)
    if kind == 'friendship-share' and stage in ('meeting', 'tradition'):
        if stage == 'meeting':
            choice = action.get('choice', 'named' if key in PROJECTS else None)
            g.require(isinstance(choice,str) and (choice == 'named' if key in PROJECTS else choice in HABITS), 'Choose one of the offered activities.')
            r['habit'] = choice
            raw = d['introduction'] if key in PROJECTS else HABITS[choice]['lines']
            title = 'An idea to share: '+d['keepsake'] if key in PROJECTS else HABITS[choice]['title']
        else:
            raw, title = d['reflection'], 'A shared tradition: '+r['keepsake']['name']
        remember(s, key, stage, title, raw)
    elif kind == 'friendship-arrange' and stage in ('project', 'visit'):
        cost = 4 if stage == 'project' else 0
        title = d['title'] if stage == 'project' else 'Time together: '+d['keepsake']
        s['sharedFunds'] -= cost
        saved(s)['job'] = dict(pairId=key, stage=stage, participants=key.split('|'), room=d['room'],
                               cost=cost, title=title, done=0, phases=1)
        for who in key.split('|'):
            g.set_character_assignment(s, who, ASSIGNMENT)
        g.add_journal(s, 'Arranged '+title+'. Both residents have one shared phase scheduled for the next Advance.')
    else:
        raise g.RuleError('Choose one of the offered friendship actions.')
    return True


def resolve(s, summary):
    job = saved(s)['job']
    if not job or job_blockers(s):
        return
    key, stage = job['pairId'], job['stage']
    d = definition(s, key)
    r = saved(s)['pairs'][key]
    if stage == 'project':
        r['keepsake'] = dict(name=d['keepsake'], room=d.get('displayRoom',d['room']), madeOn=s['dayNumber'])
    remember(s, key, stage, job['title'], d['completion'] if stage == 'project' else d['outingLines'], summary)
    if stage == 'project':
        summary.append('Cooperation unlocked for this pair: +1 shared research work or garden/gathering output when both do the same supported task; +2 at 70 bonding. Only the strongest pair bonus applies to each task.')
    release(s, job)
    saved(s)['job'] = None


def cooperation(s, assignment, eligible=None):
    """One strongest eligible pair per real task; never one bonus per worker."""
    import game as g
    if assignment not in ('archive','archive-project','garden','hunt','forage'):
        return None
    if assignment=='archive' and s['researchStatus']!='in-progress' and not s['activeResearchId']:
        return None
    if assignment=='archive-project' and s['miraArchiveProject']['status']!='in-progress':
        return None
    if assignment=='garden' and not g.room_available(s,'conservatory'):
        return None
    if eligible is None:
        eligible = {w for w in g.household_members(s) if w != 'founder' and
                    g.character_at_castle(s, w) and g.character_assignment(s, w) == assignment}
    else:
        eligible = set(eligible) & (set(g.household_members(s)) - {'founder'})
    candidates = []
    for key, r in saved(s)['pairs'].items():
        pair = key.split('|')
        if 'project' in r['memories'] and set(pair) <= eligible and score(s, key) >= 25:
            candidates.append(dict(pairId=key, participants=pair, amount=2 if score(s, key) >= 70 else 1))
    return max(candidates, key=lambda r: (r['amount'], score(s, r['pairId']), r['pairId']), default=None)


def bonus(s, assignment):
    return (cooperation(s, assignment) or {}).get('amount', 0)


def forecast(s):
    job = saved(s)['job']
    return [job['title']+': '+('paused; review the participants’ tasks to resume.' if job_blockers(s) else 'completes on the next Advance.')] if job else []


def context(s, who):
    """Only completed milestones involving this resident, with no future replies."""
    rows=[]
    for key, r in saved(s)['pairs'].items():
        if who not in key.split('|') or not r['memories']:
            continue
        rows.append(dict(participants=key.split('|'), bonding=score(s,key),
                         keepsake=deepcopy(r['keepsake']), memories=deepcopy(r['memories'])))
    return rows


def view(s):
    import game as g, headquarters as h
    rows = []
    for pair in bonds.view(s)['pairs']:
        key = pair['id']
        if pair['score'] < 10 and key not in saved(s)['pairs']:
            continue
        r, d, next_row = record(s, key), definition(s, key), next_stage(s, key)
        stage = next_row[0] if next_row else None
        reasons = blockers(s, key, stage) if stage else []
        invitation = (d['invitation'] if stage in ('meeting', 'project') and key in PROJECTS else
                      'They would like to choose something to do together.' if stage == 'meeting' else
                      d['invitation'] if stage == 'project' else d['outing'] if stage == 'visit' else
                      'They invite you to hear what they have learned about one another through their shared keepsake.')
        rows.append(dict(id=key, participants=pair['participants'], score=pair['score'], label=pair['label'],
                         stage=stage, title=next_row[2] if next_row else 'A shared tradition remembered',
                         threshold=next_row[1] if next_row else None, invitation=invitation if stage else '',
                         projectName=d['title'] if stage != 'meeting' or key in PROJECTS else None,
                         room=d['room'], roomName=h.ROOMS[d['room']]['name'], keepsake=deepcopy(r['keepsake']),
                         memories=deepcopy(r['memories']), blockers=reasons,
                         deferred=stage in r['deferred'], available=bool(stage and not reasons and stage not in r['deferred']),
                         choices=[{'id': k, 'label': v['label']} for k, v in HABITS.items()] if stage == 'meeting' and key not in PROJECTS else [],
                         phases=1 if stage in ('project', 'visit') else 0, cost=4 if stage == 'project' else 0,
                         cooperation=(2 if pair['score'] >= 70 else 1) if 'project' in r['memories'] else 0))
    job = deepcopy(saved(s)['job'])
    if job:
        job.update(blockers=job_blockers(s), resumeBlockers=job_blockers(s, True))
    return dict(pairs=rows, job=job, readyCount=sum(r['available'] for r in rows),
                activeCooperation=[dict(task=k, **c) for k in ('archive', 'archive-project', 'garden', 'hunt', 'forage')
                                   if (c := cooperation(s, k))])
