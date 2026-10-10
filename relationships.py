"""Persistent, opt-in bonds. Reads never manufacture history or advance time."""
from copy import deepcopy
from itertools import combinations
from relationship_content import PREFERENCES, STORY, PEOPLE, FOLLOWTHROUGH
from companion_conversations import INVITATION_REPLIES

DIMENSIONS = ('trust', 'affection', 'respect')

def invitation_definition(who):
    p = PREFERENCES[who]
    (question, answer), decline = INVITATION_REPLIES[who]
    return {'title':p[2], 'opening':p[3], 'choices':{
        'join':('Accept and spend time together.',p[4],'affection'),
        'ask':(question,answer,'trust'),
        'decline':('Decline for today.',decline,'respect')}}

def initialize(s):
    s.setdefault('relationships', {'bonds': {}, 'events': {}, 'memories': {}, 'deferred': [], 'promise': None})

def saved(s):
    return s.get('relationships', {'bonds': {}, 'events': {}, 'memories': {}, 'deferred': [], 'promise': None})

def pair_id(a, b):
    return '|'.join(sorted((a, b)))

def remember(s, source, record, dimension=None, amount=1):
    """One contribution per real scene, even for repeatable room activities."""
    if source in saved(s)['events']:
        return
    people = sorted(set(record.get('participants', [])))
    if len(people) < 2:
        return
    choice = record.get('choice')
    dimension = dimension or {'curious':'trust', 'warm':'affection', 'candid':'respect',
        'notice':'respect', 'practice':'trust', 'celebrate':'affection',
        'thanks':'respect', 'learn':'trust', 'company':'affection'}.get(choice, 'trust')
    assert dimension in DIMENSIONS
    initialize(s)
    data = saved(s)
    effects = []
    import foundation_chamber
    gain = round(amount * foundation_chamber.multiplier(s), 1) if amount > 0 else amount
    for a, b in combinations(people, 2):
        key = pair_id(a, b)
        bond = data['bonds'].setdefault(key, {'participants':[a,b], **dict.fromkeys(DIMENSIONS,0)})
        old = bond[dimension]
        bond[dimension] = round(min(12, max(0, old + gain)), 1)
        effects.append({'bondId':key, 'dimension':dimension, 'change':round(bond[dimension]-old, 1)})
    data['events'][source] = {'title':record['title'], 'participants':people,
        'dayNumber':s['dayNumber'], 'phase':s['currentDayPhase'], 'effects':effects}
    if amount > 0:
        import resident_bonds
        resident_bonds.award(s, people, 'scene:' + source, record['title'], 2)

def context(s, who):
    data = saved(s)
    return {'bonds':deepcopy([b for b in data['bonds'].values() if who in b['participants']]),
            'memories':deepcopy([m for m in data['memories'].values() if who in m['participants']]),
            'promise':deepcopy(data['promise']) if who in PEOPLE and data['promise'] else None}

def story_definition(s, index):
    d = deepcopy(STORY[index])
    memories = saved(s)['memories']
    previous = memories.get('story:'+STORY[index-1]['id']) if index else None
    if previous:
        d['opening'] = 'Last time you chose: “'+previous['playerLine']+'”\n\n'+d['opening']
    if d['id'] == 'followthrough':
        agreement = memories.get('story:agreement', {}).get('choice')
        label, _, dim = d['choices']['keep']
        d['choices']['keep'] = (label, FOLLOWTHROUGH.get(agreement,''), dim)
        if agreement == 'no_promise':
            d['choices'] = {'keep':('Hear how their independent trial went.', FOLLOWTHROUGH[agreement], 'respect')}
    if d['id'] in ('review','callback') and saved(s)['promise']:
        promise = saved(s)['promise']
        d['opening'] = 'Your agreement: '+promise['label']+' — '+promise['status']+'.\n\n'+d['opening']
    return d

def row(s, key, definition, people, reasons):
    data = saved(s)
    memory = data['memories'].get(key)
    visible = not reasons and not memory
    return {'id':key, 'title':definition['title'], 'participants':people[:],
        'opening':memory['opening'] if memory else definition['opening'] if visible else '',
        'choices':{k:{'label':v[0], 'effect':('Trust −1 with each companion for withdrawing the promise; their trust in each other is unchanged.' if key=='story:followthrough' and k=='apologise' else v[2].title()+' +1 for each pair present (maximum 12).')} for k,v in definition['choices'].items()} if visible else {},
        'blockers':reasons if not memory else [], 'available':visible,
        'deferred':key in data['deferred'], 'memory':deepcopy(memory)}

def rows(s):
    import game as g
    from household_chapters import presence
    from social_life import stamp
    members = g.household_members(s)
    data = saved(s)
    result = []
    if all(p in members for p in PEOPLE):
        for i, d in enumerate(STORY):
            reasons = presence(s, PEOPLE)
            if i:
                previous = data['memories'].get('story:'+STORY[i-1]['id'])
                if not previous:
                    reasons.append('Share “'+STORY[i-1]['title']+'” first.')
                elif stamp(s) <= previous['stamp']:
                    reasons.append('Let one shared day phase pass. This invitation never expires.')
            result.append(row(s,'story:'+d['id'],story_definition(s,i),PEOPLE,reasons))
    for who, p in PREFERENCES.items():
        if who not in members:
            continue
        reasons = presence(s, ['founder',who])
        count = sum('founder' in e['participants'] and who in e['participants'] for e in data['events'].values())
        if count < 2:
            reasons.append('Share two distinct remembered moments together after this update; ordinary conversations remain available.')
        definition = invitation_definition(who)
        result.append(row(s,'invitation:'+who,definition,['founder',who],reasons))
    return result

def view(s):
    import game as g
    data = saved(s)
    members = g.household_members(s)
    return {'bonds':deepcopy([b for b in data['bonds'].values() if all(p in members for p in b['participants'])]),
        'events':deepcopy(list(data['events'].values())), 'scenes':rows(s),
        'promise':deepcopy(data['promise']),
        'preferences':{who:{'likes':p[0], 'boundary':p[1]} for who,p in PREFERENCES.items() if who in members}}

def apply(s, action):
    kind = action.get('type')
    if kind not in ('share-relationship','defer-relationship','restore-relationship'):
        return False
    import game as g
    from social_life import stamp
    key = action.get('sceneId')
    g.require(isinstance(key,str), 'Choose a known invitation.')
    current = next((r for r in rows(s) if r['id']==key),None)
    g.require(current is not None, 'These participants must be current residents.')
    g.require(not current['memory'], 'This moment is already remembered.')
    if kind == 'restore-relationship':
        g.require(current['deferred'], 'This invitation is not set aside.')
        saved(s)['deferred'].remove(key)
        return True
    g.require(current['available'], ' '.join(current['blockers']))
    if kind == 'defer-relationship':
        g.require(not current['deferred'], 'This invitation is already set aside.')
        initialize(s)
        saved(s)['deferred'].append(key)
        return True
    choice = action.get('choice')
    g.require(isinstance(choice,str) and choice in current['choices'], 'Choose an offered response.')
    if key.startswith('story:'):
        index = next(i for i,d in enumerate(STORY) if 'story:'+d['id']==key)
        definition = story_definition(s,index)
        label, response, dimension = definition['choices'][choice]
    else:
        who = key.split(':',1)[1]
        label, response, dimension = invitation_definition(who)['choices'][choice]
    initialize(s)
    data = saved(s)
    record = {'id':key, 'title':current['title'], 'opening':current['opening'],
        'participants':current['participants'], 'choice':choice, 'playerLine':label,
        'response':response, 'stamp':stamp(s), 'dayNumber':s['dayNumber'], 'phase':s['currentDayPhase']}
    data['memories'][key] = record
    if key in data['deferred']:
        data['deferred'].remove(key)
    if key == 'story:agreement':
        data['promise'] = {'label':label, 'choice':choice, 'participants':PEOPLE[:],
            'status':'not promised' if choice=='no_promise' else 'open'}
    elif key == 'story:followthrough':
        data['promise']['status'] = ('not promised' if data['promise']['choice']=='no_promise' else
            {'keep':'fulfilled','renegotiate':'renegotiated and fulfilled','apologise':'withdrawn with apology'}[choice])
    # Withdrawing affects trust with the founder, not trust between two NPCs
    # who kept their own word. Other story exchanges build all participating pairs.
    effect_record = record
    if key == 'story:followthrough' and choice == 'apologise':
        for who in ('mira','tamsin'):
            remember(s,key+':'+who,{**record,'participants':['founder',who]},'trust',-1)
    else:
        remember(s,key, effect_record, dimension)
    g.add_journal(s,record['title']+': '+label+' '+response)
    return True
