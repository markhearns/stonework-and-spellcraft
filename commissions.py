"""External clients pay for finite work; rewards are quoted when accepted."""
from copy import deepcopy

CATALOG = {
    'translate': dict(name='Translate a damaged travel journal', client='Hillfold bindery',
        description='Compare the damaged place names with the client’s clean maps. Return a readable translation.',
        skill='scholarship', room=None, inputs={}, phases=2),
    'restore': dict(name='Repair a wagon lantern', client='Reedbank carriers',
        description='Replace the loose binding and test the lamp before it goes back on the road.',
        skill='artifice', room='workshop', inputs={'binding-thread': 1}, phases=2),
    'remedies': dict(name='Prepare a travelling medicine kit', client='Brook keepers',
        description='Prepare labelled dressings and a measured batch of wound wash from the client’s supplies.',
        skill='scholarship', room='infirmary', inputs={'silver-ivy': 1}, phases=2),
    'ward': dict(name='Diagnose a failed boundary ward', client='Roadside refuge',
        description='Test the supplied wardstone and return a repair plan. The client performs the installation.',
        skill='scholarship', room='library', inputs={'porous-clay': 1}, phases=2),
}


def saved(s):
    return s.get('externalCommissions', {'job': None, 'completed': {}, 'receipts': []})


def blockers(s, key, who, reward='crowns'):
    import game as g, headquarters as h
    if key not in CATALOG or who not in g.household_members(s):
        return ['Choose a listed commission and a household member.']
    d = CATALOG[key]; b = []
    if not all(g.character_at_castle(s, w) for w in ('founder', who)):
        b.append('Bring your scholar and the worker home.')
    if saved(s)['job']:
        b.append('Finish or cancel the current external commission.')
    if saved(s)['completed'].get(key) == s['dayNumber']:
        b.append('This client has already received today’s order. Another order is available tomorrow.')
    if d['room'] and not h.ready(s, d['room']):
        b.append('Restore the '+(h.ROOMS.get(d['room']) or g.ROOMS[d['room']])['name']+' first.')
    # Translation is available from the opening; other trades require training.
    if key != 'translate' and g.skill_rank(s, who, d['skill']) < 1:
        b.append('The worker needs rank 1 in '+d['skill']+'.')
    for k, n in d['inputs'].items():
        if s['materialInventory'].get(k, 0)-s['materialReserveTargets'].get(k, 0) < n:
            b.append('Needs '+str(n)+' unreserved '+g.MATERIALS[k]['name']+'.')
    if reward not in ('crowns', 'materials', 'knowledge'):
        b.append('Choose crowns, materials or a lesson as payment.')
    if reward == 'knowledge' and 'commission:'+key in s['characterDevelopment'][who]['advancementAwards']:
        b.append('This worker has already learned this client’s lesson. Choose another payment.')
    return b


def rewards(s, key):
    import game as g
    crowns = 2*g.copying_income(s)+4
    return {
        'crowns': dict(crowns=crowns, materials={}, advancement=0,
                      text=str(crowns)+' shared crowns.'),
        'materials': dict(crowns=4, materials={'binding-thread': 3, 'moon-glass': 1}, advancement=0,
                         text='4 shared crowns, 3 binding thread and 1 moon glass.'),
        'knowledge': dict(crowns=g.copying_income(s), materials={}, advancement=1,
                         text=str(g.copying_income(s))+' shared crowns and 1 advancement point for the worker, once per client.'),
    }


def apply(s, a):
    import game as g
    kind = a.get('type')
    if kind not in ('commission-start', 'commission-resume', 'commission-cancel'):
        return False
    r = s.setdefault('externalCommissions', deepcopy(saved(s)))
    if kind == 'commission-start':
        key, who, payment = a.get('commissionId'), a.get('workerId'), a.get('payment')
        g.require(all(isinstance(x, str) for x in (key, who, payment)), 'Choose a commission, worker and payment.')
        b = blockers(s, key, who, payment); g.require(not b, ' '.join(b))
        g.require(who=='founder' or a.get('agreed') is True,'Agree this specific commission with the companion before assigning it.')
        d = CATALOG[key]
        for k, n in d['inputs'].items(): s['materialInventory'][k] -= n
        r['job'] = dict(id=key, name=d['name'], workerId=who, payment=payment,
                        reward=deepcopy(rewards(s, key)[payment]), inputs=deepcopy(d['inputs']),
                        done=0, phases=d['phases'])
        g.set_character_assignment(s, who, 'external-commission')
        g.add_journal(s, d['client']+' accepted '+d['name'].lower()+'. '+str(d['phases'])+' assigned work phases; payment: '+r['job']['reward']['text'])
    else:
        job = r['job']; g.require(job, 'There is no unfinished external commission.')
        who = job['workerId']
        g.require(all(g.character_at_castle(s, w) for w in ('founder', who)), 'Return home together to change this commission.')
        if kind == 'commission-resume':
            g.set_character_assignment(s, who, 'external-commission')
        else:
            for k, n in job['inputs'].items(): s['materialInventory'][k] += n
            r['job'] = None
            if g.character_assignment(s, who) == 'external-commission': g.set_character_assignment(s, who, 'rest')
            g.add_journal(s, 'Cancelled the external commission. All committed materials returned; no payment or lesson awarded.')
    return True


def resolve(s, summary, assignments):
    import game as g, signature_growth, shared_history
    r = saved(s); job = r['job']
    if not job or assignments.get(job['workerId']) != 'external-commission': return
    who = job['workerId']; job['done'] += 1
    summary.append(job['name']+': '+str(job['done'])+'/'+str(job['phases'])+' work phases.')
    if job['done'] < job['phases']: return
    reward = job['reward']; s['sharedFunds'] += reward['crowns']
    for k, n in reward['materials'].items(): s['materialInventory'][k] += n
    if reward['advancement']: g.award_advancement(s, who, 'commission:'+job['id'], 1, 'Learned from '+CATALOG[job['id']]['client'])
    signature_growth.record_work(s, who, 'commission:'+job['id'])
    shared_history.record(s, 'commission:'+job['id']+':'+who, [who], 'Completed '+job['name'].lower(),
                          CATALOG[job['id']]['client']+' accepted the finished work.', 'work')
    r['completed'][job['id']] = s['dayNumber']
    r['receipts'] = (r['receipts']+[dict(name=job['name'], workerId=who, day=s['dayNumber'], payment=reward['text'])])[-8:]
    r['job'] = None; g.set_character_assignment(s, who, 'rest')
    summary.append('Commission delivered. '+reward['text']+' Worker assigned to Rest.')


def view(s):
    import game as g
    r = saved(s); job = deepcopy(r['job'])
    if job: job['working'] = g.character_at_castle(s, job['workerId']) and g.character_assignment(s, job['workerId']) == 'external-commission'
    return dict(job=job, receipts=deepcopy(r['receipts']), offers=[dict(id=key, **deepcopy(d), rewards=rewards(s, key),
        workers=[dict(id=w, name=g.character_profile(s,w)['name'], blockers={p:blockers(s,key,w,p) for p in ('crowns','materials','knowledge')}) for w in g.household_members(s)]) for key,d in CATALOG.items()])
