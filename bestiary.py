"""Shared creature definitions, encounter pools and save-scoped field knowledge.

Public views never add discoveries. Sightings occur on arrival, knowledge on
resolution or assigned study, and cheat reveals use the normal cheat transaction.
"""
from copy import deepcopy
import json
from pathlib import Path

CATALOGUE = json.loads(Path(__file__).with_name('bestiary_catalogue.json').read_text())
CREATURES = CATALOGUE['creatures']
ANCESTRIES = CATALOGUE['ancestries']
ENCOUNTERS = CATALOGUE['encounters']
ANCESTRY_LABELS = {d['name'].casefold(): key for key, d in ANCESTRIES.items()}
ANCESTRY_LABELS.update({'angel':'seraph','water elemental':'elemental','fire elemental':'elemental','air elemental':'elemental','earth elemental':'elemental','construct':'golem','catgirl':'catfolk'})
ROUTES = {
    'road': dict(name='Supply road', art='patrol-road', count=1, description='One encounter along the supply road. Animals and raiders; suitable for a rested solo patrol, with retreat available.', pool=['wolf','thief','bandit','boar','lantern-moth','slatehide-lizard'], weights=[25,30,15,10,10,10], rare=0),
    'woods': dict(name='Woodland circuit', art='patrol-wilds', count=2, description='Two woodland encounters. Wolves, boars, badgers, spiders, moths, root mimics and thieves; 5% rare-creature chance per encounter.', pool=['wolf','boar','thief','grave-silk-spider','lantern-moth','root-mimic','storm-antler-stag','griffin','ember-hound','barrow-badger'], weights=[13,17,13,13,13,13,2,2,1,13], rare=5),
    'border': dict(name='Boundary ridge', art='patrol-wilds', count=2, description='Two harder encounters at ridge crossings, cockatrice hollows and old boundary posts. A group is recommended; 10% rare-creature chance per encounter.', pool=['bandit','boar','thief','slatehide-lizard','moss-troll','ruin-gargoyle','restless-sentry','griffin','ember-hound','storm-antler-stag','flint-beak-cockatrice'], weights=[17,8,8,8,17,8,8,4,4,2,16], rare=10),
    'wetland': dict(name='Marsh crossings', art='old-waterworks', count=2, description='Two encounters along reed beds and shallow crossings. Marsh crabs, reed lurkers, lantern moths, siltback tortoises and gloam jellies.', pool=['giant-marsh-crab','reed-lurker','lantern-moth','siltback-tortoise','gloam-jelly'], weights=[25,25,10,20,20], rare=0),
    'ruins': dict(name='Abandoned outbuildings', art='hillfold-bindery', count=2, description='Two encounters in abandoned cellars, kilns and watch posts. Spiders, roots, gargoyles, sentries, rimewing bats and clockwork scarabs; 5% hearth-ash hound chance per encounter.', pool=['grave-silk-spider','root-mimic','ruin-gargoyle','restless-sentry','ember-hound','rimewing-bat','brass-wing-scarab'], weights=[17,10,17,21,5,15,15], rare=5),
}
ROUTES.update({
    'outer-valley': dict(name='Outer valley circuit', challengeTier='Intermediate', count=2, description='Two intermediate encounters through the valley’s woodland, quarry tracks, cliff crossings and marsh banks. Owlbears, rust beetles, blink lynxes, cliff harpies and wisps. A rested equipped party is recommended.', pool=['owlbear','rust-beetle','blink-lynx','cliff-harpy','will-o-wisp'], weights=[20,20,20,20,20], rare=0, art='patrol-wilds', artPath='/assets/bestiary/creatures/blink-lynx.webp'),
    'deep-quarry': dict(name='Deep quarry and buried outwork', challengeTier='Difficult', count=1, description='One difficult basilisk or runebound colossus encounter. Bring treatment supplies and protection; study observed creatures before returning. Opens after Chapter 8.', pool=['basilisk','runebound-colossus'], weights=[50,50], rare=0, art='patrol-wilds', artPath='/assets/bestiary/creatures/runebound-colossus.webp'),
    'high-crags': dict(name='High crags', challengeTier='Difficult', count=1, description='One difficult manticore or wyvern encounter. Prepare cover, venom treatment and a way to exploit landing or recovery openings. Opens after Chapter 8.', pool=['manticore','wyvern'], weights=[50,50], rare=0, art='patrol-wilds', artPath='/assets/bestiary/creatures/wyvern.webp'),
    'flooded-basin': dict(name='Old flood basin', challengeTier='Difficult', count=1, description='One difficult three-headed hydra encounter. A full rested party, binding thread and heat or ice are recommended. Opens after Chapter 8.', pool=['marsh-hydra'], weights=[100], rare=0, art='old-waterworks', artPath='/assets/bestiary/creatures/marsh-hydra.webp'),
})
for route in ROUTES.values():
    folder='locations' if route['art'] in ('old-waterworks','hillfold-bindery') else 'expeditions'
    route.setdefault('artPath','/assets/'+folder+'/'+route['art']+'.webp')
RAIDER_ANCESTRIES = ['human','high-elf','dark-elf','drow','catfolk','wolfkin','orc','ogrekin']


def empty():
    return {'entries': {}, 'research': None, 'revealed': False}


def saved(s):
    return s.get('bestiary', empty())


def initialize(s):
    return s.setdefault('bestiary', empty())


def ancestry_id(label):
    return ANCESTRY_LABELS.get(str(label).strip().casefold())


def legacy_knowledge(s):
    """Recover evidence already in old saves without altering or replaying it."""
    result = {}
    for report in s.get('fieldPatrols', {}).get('reports', []):
        for outcome in report.get('outcomes', []):
            d = ENCOUNTERS.get(outcome.get('enemyId'), {})
            cid = d.get('bestiaryId')
            if cid in CREATURES:
                result[cid] = max(result.get(cid, 0), 2 if outcome.get('rewarded') else 1)
    run = s.get('fieldPatrols', {}).get('active')
    if run:
        for outcome in run.get('outcomes', []):
            cid = ENCOUNTERS.get(outcome.get('enemyId'), {}).get('bestiaryId')
            if cid in CREATURES:
                result[cid] = max(result.get(cid, 0), 2 if outcome.get('rewarded') else 1)
        if run['stage'] in ('decision','exchange','site-decision','site-work') and run['index'] < len(run['enemies']):
            cid = ENCOUNTERS.get(run['enemies'][run['index']], {}).get('bestiaryId')
            if cid in CREATURES:
                result[cid] = max(result.get(cid, 0), 1)
    return result


def knowledge(s, cid):
    return max(saved(s)['entries'].get(cid, {}).get('level', 0), legacy_knowledge(s).get(cid, 0))


def learn(s, cid, level, source, *, sighting=False, resolved=False):
    if cid not in CREATURES and cid not in ANCESTRIES:
        return
    record = initialize(s)['entries'].setdefault(cid, {'level': 0, 'sightings': 0, 'resolved': 0, 'firstSeen': None, 'sources': []})
    record['level'] = max(record['level'], level)
    if sighting:
        record['sightings'] += 1
        if record['firstSeen'] is None:
            record['firstSeen'] = {'day': s['dayNumber'], 'phase': s['currentDayPhase'], 'source': source}
    if resolved:
        record['resolved'] += 1
    if source not in record['sources']:
        record['sources'].append(source)


def encounter(s, run):
    if run['index'] >= len(run['enemies']):
        return None
    d = deepcopy(ENCOUNTERS[run['enemies'][run['index']]])
    if d.get('roleId'):
        # Old story and in-flight saves default to the original human opponents.
        ids = run.get('ancestries', [])
        aid = (ids[run['index']] if run['index'] < len(ids) else 'human') or 'human'
        import encounter_people as ep
        a = ANCESTRIES.get(ep.ancestry(aid or 'human'), ANCESTRIES['human'])
        art=ep.art(aid,'capture') or a['art']
        d.update(ancestryId=a['id'], bestiaryId=a['id'], art=art, thumbnail=art, ancestryName=a['name'], banditArt=a['id'] in ep.SUPPORTED, elementalVariant=aid.removeprefix('elemental-') if aid.startswith('elemental-') else None)
    return d


def observe(s, run):
    d = encounter(s, run)
    if not d or run['stage'] == 'outbound':
        return
    seen = run.setdefault('bestiaryObserved', [])
    if run['index'] not in seen:
        learn(s, d['bestiaryId'], 1, 'Creature bounty' if run.get('bountyId') else 'Field patrol', sighting=True)
        seen.append(run['index'])


def resolved(s, run, reward):
    observe(s, run)
    d = encounter(s, run)
    if d and reward:
        learn(s, d['bestiaryId'], 2, 'Resolved encounter', resolved=True)


def study_blockers(s, cid):
    import game as g
    reasons = []
    if not g.character_at_castle(s, 'founder'):
        reasons.append('Return to the castle before studying in the library.')
    if cid not in CREATURES:
        reasons.append('Choose a creature entry.')
    elif knowledge(s, cid) == 0:
        reasons.append('Observe this creature on a patrol or bounty first.')
    elif knowledge(s, cid) >= 2:
        reasons.append('This entry is already complete.')
    if saved(s)['research']:
        reasons.append('Finish or cancel the current bestiary study first.')
    return reasons


def apply(s, action):
    import game as g
    kind = action.get('type')
    if kind not in ('bestiary-study', 'bestiary-resume', 'bestiary-cancel'):
        return False
    r = initialize(s)
    g.require(g.character_at_castle(s, 'founder'), 'Return home before changing library study.')
    if kind == 'bestiary-study':
        cid = action.get('entryId')
        g.require(isinstance(cid, str), 'Choose a creature entry.')
        blockers = study_blockers(s, cid)
        g.require(not blockers, ' '.join(blockers))
        r['research'] = {'entryId': cid, 'done': 0, 'total': 1}
        g.set_character_assignment(s, 'founder', 'bestiary-study')
    elif kind == 'bestiary-resume':
        g.require(r['research'] is not None, 'There is no unfinished bestiary study.')
        g.set_character_assignment(s, 'founder', 'bestiary-study')
    else:
        g.require(r['research'] is not None, 'There is no unfinished bestiary study.')
        r['research'] = None
        if g.character_assignment(s, 'founder') == 'bestiary-study':
            g.set_character_assignment(s, 'founder', 'rest')
    return True


def working(s):
    import game as g
    return bool(saved(s)['research'] and g.character_at_castle(s, 'founder') and g.character_assignment(s, 'founder') == 'bestiary-study')


def resolve(s, summary, assignments):
    import game as g
    job = saved(s)['research']
    if not job or assignments.get('founder') != 'bestiary-study' or not working(s):
        return
    learn(s, job['entryId'], 2, 'Library study')
    summary.append('Bestiary study complete: ' + CREATURES[job['entryId']]['name'] + '. Behaviour, advice and encounter values are recorded.')
    initialize(s)['research'] = None
    g.set_character_assignment(s, 'founder', 'rest')


def reveal_all(s):
    for cid in (*CREATURES, *ANCESTRIES):
        learn(s, cid, 2, 'Cheat reveal')
    initialize(s)['revealed'] = True
    return f'Revealed all {len(CREATURES)} creature entries and {len(ANCESTRIES)} ancestry entries. No sightings, victories, rewards, recruits or story progress were added.'


def creature_view(s, cid):
    import field_magic
    d = deepcopy(CREATURES[cid])
    level = knowledge(s, cid)
    import bounty_contracts
    sample=bounty_contracts.SAMPLES[cid];d['sample']={'id':sample[0],'name':sample[1],'icon':'/assets/materials/'+sample[0]+'.webp','properties':sample[2],'collection':sample[4],'uses':bounty_contracts.uses(sample[0]),'held':s['materialInventory'].get(sample[0],0),'ordinaryMaterials':deepcopy(ENCOUNTERS[d['enemyId']]['materials'])}
    d.update(level=level, status=('Not yet observed', 'Observed', 'Entry complete')[min(2,level)], record=deepcopy(saved(s)['entries'].get(cid, {})), studyBlockers=study_blockers(s, cid))
    if level < 1:
        d['signs'] = None
    if level < 2:
        for k in ('behaviour', 'advice', 'materialsNote', 'preparation'):
            d[k] = None
        d['combat'] = None
        d['mechanics'] = []
    else:
        e = ENCOUNTERS[d['enemyId']]
        d['combat'] = {'hp': e['hp'], 'attack': e['attack'], 'armour': e.get('armour',0), 'patterns': deepcopy(e['patterns']), 'approach': deepcopy(e['approach']), 'spellDamage': {kind: field_magic.damage(kind,e) for kind in ('water','fire','ice','lightning','radiant')}, 'reward': {'crowns': e['crowns'], 'food': e['food'], 'materials': deepcopy(e['materials'])}}
    return d


def view(s):
    import game as g
    creatures = sorted((creature_view(s, cid) for cid in CREATURES),key=lambda d:(('Standard','Intermediate','Difficult').index(d['challengeTier']),d['name'].casefold()))
    people = []
    for aid, data in ANCESTRIES.items():
        row = deepcopy(data)
        import ancestry_traits
        row['ancestryTrait']=ancestry_traits.definition(data['name'])
        row['knownPeople'] = [{'id':who,'name':g.character_profile(s,who)['name']} for who in g.household_members(s) if ancestry_id(g.character_profile(s,who).get('ancestryLabel')) == aid]
        row['record'] = deepcopy(saved(s)['entries'].get(aid, {}))
        import character_builds as cb
        row['training'] = [{'id':pid,'name':perk['name'],'description':perk['description'],'requirements':'Requires '+cb.ATTRIBUTES[perk['attribute']]['name']+' 6, '+g.CHARACTER_SKILLS[perk['skill']]['name']+' 1 and '+cb.AFFINITIES[perk['affinity']]['name']+' affinity 1. Costs 3 advancement points and 2 assigned training phases.'} for pid,perk in cb.PERKS.items() if data['name'] in perk.get('ancestries',[])]
        people.append(row)
    research = deepcopy(saved(s)['research'])
    if research:
        research.update(name=CREATURES[research['entryId']]['name'], working=working(s))
    return {'creatures':creatures, 'ancestries':people, 'research':research, 'observed':sum(c['level']>0 for c in creatures), 'complete':sum(c['level']>=2 for c in creatures), 'total':len(creatures), 'revealed':saved(s)['revealed'], 'atHome':g.character_at_castle(s,'founder')}
