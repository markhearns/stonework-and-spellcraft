"""Mid-campaign castle investigation: restore and use the foundation ritual chamber."""
from copy import deepcopy

ROOM = 'foundation-chamber'
VIEW = 'foundationChamber'
ASSIGNMENT = 'foundation-work'
RITUAL_ASSIGNMENT = 'foundation-ritual'
DURATION = 9
BONUS = 0.2
INVITATION_REPLIES = {
    'mira': 'Yes. Leave the ledger on the table, though. I would like your attention for once without having to compete with a footnote.',
    'tamsin': 'Yes, I would like that. Shall we bring a pitcher of water? Then I can stop inventing reasons to get up again.',
    'iona': 'Yes. I can find the door from here, so you can dispense with the guided tour. Take my hand and come along.',
    'aurelia': 'Yes. I would like some time with you behind a closed door. Let us leave the rest of our plans until afterwards.',
    'neris': 'Yes. Could we turn the lamp toward the violet glass? I like the colour it puts on the ceiling. Come and see from beside me.',
    'sabine': 'A private invitation, a comfortable room, and no speeches? You have made an excellent case. Yes, I would like to join you.',
    'koharu': 'Yes. The latch looks sound, and I am going to leave it alone. If I start discussing its hinges, please remind me why we came down here.',
    'zahra': 'Yes. Leave the lamp low, please. I would like to sit close for a while before we begin.',
    'fenna': 'Yes. I had a clever reply prepared, but now you have asked I would rather take your hand. You may have the clever reply later.',
    'kaede': 'Yes. Put the work list away first. I intend to keep your attention, and I would prefer not to compete with tomorrow’s repairs.',
    'elowen': 'Yes. I would like you to come and sit beside me. The pitcher is full and the door closes; I think we can stop finding things to arrange.',
    'nyssara': 'Yes. I know I have asked a great many questions about the chamber. You need not mistake those for uncertainty about wanting to be here with you.',
    'sylva': 'Yes. There is enough lamplight to see you, and that will do. I can tell you my opinions about the bare stone walls another time.',
}
EMPTY = dict(started=False, completed={}, job=None, invitation=None, ritual=None,
             blessing=None, ritualCount=0, lastRitual=None, concludedOn=None)
STEPS = {
    'connections': dict(name='Trace the connections beneath the hearth', phases=2,
        purpose='Find where the unused service line goes before opening the lower passage.', needs=[],
        result='The line beneath the hearth joins a ring of channels under the inhabited rooms. A separate branch leads down to a closed chamber. You mark the junctions on a plan and uncover its access door. The ordinary hearth supply has its own line.'),
    'instructions': dict(name='Read the chamber’s maintenance ledger', phases=2,
        purpose='Identify the room’s purpose and recover its operating instructions.', needs=['connections'],
        result='The ledger identifies this as a ritual chamber. Consensual sexual intimacy supplies its enchantment; the floor channels carry the resulting blessing into the household network. The recorded effect is 20% faster relationship progress for three days. The instructions also describe an isolation switch and a test signal, so you can check the room before anyone uses it.'),
    'restoration': dict(name='Restore the ritual chamber', phases=3, cost=24,
        materials={'binding-thread': 2, 'porous-clay': 2, 'fireglass': 1},
        purpose='Repair the broken connections, ventilation and door; furnish the room for private use.', needs=['instructions'],
        result='The channels are repaired and the isolation switch works. Fresh linen, a sound door latch and cleared ventilation make the chamber usable. The connections still need testing before you can conduct its ritual.'),
    'isolation': dict(name='Test the independent hearth supply', phases=1,
        purpose='Check that the castle’s essential wards remain stable with the ritual chamber disconnected.', needs=['restoration'],
        result='With the chamber disconnected, the hearth wards keep their normal readings. You check the living rooms, washroom and entrance in turn. All retain their ordinary power. The ritual supplies an additional effect; the castle’s essential services operate without it.'),
    'distribution': dict(name='Test the household connections', phases=1,
        purpose='Send a harmless test signal through the repaired channels and measure where it arrives.', needs=['restoration'],
        result='The same test signal reaches every occupied wing. The junction maintains a connection to each household member, including people travelling beyond the walls. The ledger’s timing marks confirm that the additional effect lasts nine phases. The test checks the circuit without activating a relationship blessing.'),
}
CONCLUSION = ('You record how the chamber works: intimacy supplies the enchantment, the foundation channels distribute it, '
              'and its effect lasts three days. The ordinary wards have a separate supply. You can now use the ritual when '
              'you and an established partner choose to. On the lower side of the junction, a second labelled connection '
              'continues toward the old survey rooms. Its label identifies a reference point for crossings between worlds. '
              'The remaining question is specific: why did the surveyors need that reference point beneath this castle?')


def saved(s):
    return s.get('foundationChamber', EMPTY)


def initialize(s):
    s.setdefault('foundationChamber', deepcopy(EMPTY))


def stamp(s):
    import game as g
    return s['dayNumber'] * 3 + g.DAY_PHASES.index(s['currentDayPhase'])


def unlocked(s):
    return bool(s.get('armsOfOurOwn', {}).get('completedOn') or s.get('firstRealTest', {}).get('completedOn') or saved(s)['started'])


def ready(s):
    return all(key in saved(s)['completed'] for key in STEPS)


def active(s):
    blessing = saved(s)['blessing']
    return bool(blessing and blessing['startsAt'] <= stamp(s) < blessing['expiresAt'])


def multiplier(s):
    return 1 + BONUS if active(s) else 1


def bonus_view(s):
    import game as g
    b = saved(s)['blessing']
    enabled = active(s)
    return dict(active=enabled, percent=20, remainingPhases=b['expiresAt']-stamp(s) if enabled else 0,
                endsOn={'dayNumber': b['expiresAt']//3, 'phase': g.DAY_PHASES[b['expiresAt']%3]} if enabled else None,
                description='Positive relationship gains and resident bonding are increased by 20%.')


def methods(s, key):
    import game as g
    rows = [dict(id='careful', name='Measure the channels by hand' if key=='connections' else 'Clean and read the original pages' if key=='instructions' else STEPS[key]['name'], phases=STEPS[key]['phases'], blockers=[])]
    if key == 'connections':
        rows.append(dict(id='wards', name='Trace the line with Steady hearth wards', phases=1,
                         blockers=[] if 'steady-hearth-wards' in g.character_principles(s, 'founder') else ['Personally learn Steady hearth wards first.']))
    if key == 'instructions':
        rows.append(dict(id='archive', name='Compare your recorded founding evidence', phases=1,
                         blockers=[] if 'founding-record' in s['castleMystery']['discoveries'] else ['Complete “Put the evidence together” in Castle history first, or read the original pages.']))
    return rows


def blockers(s, key):
    import game as g
    r = saved(s); d = STEPS[key]; reasons = []
    if not unlocked(s): reasons.append('Complete Chapter 5: Arms of Our Own first.')
    if not r['started']: reasons.append('Begin the investigation below.')
    if not g.character_at_castle(s, 'founder'): reasons.append('Return your scholar to the castle.')
    if key in r['completed']: reasons.append('This step is already complete.')
    reasons.extend('Complete “'+STEPS[need]['name']+'” first.' for need in d['needs'] if need not in r['completed'])
    if r['job']: reasons.append('Finish or cancel the current chapter task first.')
    if s['sharedFunds'] < d.get('cost', 0): reasons.append('Needs '+str(d['cost'])+' shared crowns.')
    for material, n in d.get('materials', {}).items():
        if s['materialInventory'].get(material, 0)-s['materialReserveTargets'].get(material, 0) < n:
            reasons.append('Needs '+str(n)+' unreserved '+g.MATERIALS[material]['name']+'.')
    return reasons


def working(s):
    import game as g
    return bool(saved(s)['job'] and g.character_at_castle(s, 'founder') and g.character_assignment(s, 'founder')==ASSIGNMENT)


def partner_blockers(s, who, assignments=True):
    import game as g, romance
    reasons = []
    if not ready(s): reasons.append('Restore the chamber and complete both circuit tests first.')
    if who == 'founder' or who not in g.household_members(s): return reasons+['Choose a current resident partner.']
    for person in ('founder', who):
        profile = g.character_profile(s, person)
        if type(profile.get('adultAgeYears')) is not int or profile['adultAgeYears'] < 18:
            reasons.append('Both participants must be adults.')
        if not g.character_at_castle(s, person): reasons.append('Bring '+profile['name']+' home first.')
        if assignments and g.character_assignment(s, person) != 'rest': reasons.append('Set '+profile['name']+' to Rest before arranging the ritual.')
    if romance.person(s, who)['mode'] != 'open': reasons.append('Romantic invitations with this partner are paused.')
    if romance.level(s, who) < 4: reasons.append('Share the Private evening relationship milestone with this partner first.')
    return reasons


def ritual_work_blockers(s):
    import game as g
    job = saved(s)['ritual']
    if not job: return []
    reasons = partner_blockers(s, job['partnerId'], False)
    for who in ('founder', job['partnerId']):
        if who in g.household_members(s) and g.character_assignment(s, who) != RITUAL_ASSIGNMENT:
            reasons.append('Resume the ritual to assign both participants to their private phase.')
    return list(dict.fromkeys(reasons))


def release_ritual(s, who):
    import game as g
    for person in ('founder', who):
        if person in g.household_members(s) and g.character_assignment(s, person)==RITUAL_ASSIGNMENT:
            g.set_character_assignment(s, person, 'rest')


def apply(s, a):
    import game as g
    kind = a.get('type')
    if not isinstance(kind, str) or not kind.startswith('foundation-'): return False
    initialize(s); r = saved(s)
    if kind == 'foundation-start':
        g.require(unlocked(s), 'Complete Chapter 5: Arms of Our Own first.')
        g.require(g.character_at_castle(s, 'founder'), 'Return home to begin the investigation.')
        g.require(not r['started'], 'The investigation has already begun.')
        r['started'] = True
        g.add_journal(s, 'Beneath the Hearth: repairs to the lower wing reveal a disconnected line beneath the hearth. Trace it to find what it served.')
    elif kind == 'foundation-task':
        key, method = a.get('stepId'), a.get('methodId', 'careful')
        g.require(isinstance(key, str) and key in STEPS, 'Choose a listed chapter task.')
        reasons = blockers(s, key); g.require(not reasons, ' '.join(reasons))
        selected = next((m for m in methods(s, key) if m['id']==method), None)
        g.require(selected is not None, 'Choose a listed investigation method.')
        g.require(not selected['blockers'], ' '.join(selected['blockers']))
        d = STEPS[key]; cost=d.get('cost', 0); materials=d.get('materials', {})
        s['sharedFunds'] -= cost
        for material, n in materials.items(): s['materialInventory'][material] -= n
        r['job'] = dict(stepId=key, method=selected['name'], done=0, phases=selected['phases'], cost=cost, materials=deepcopy(materials))
        g.set_character_assignment(s, 'founder', ASSIGNMENT)
        g.add_journal(s, 'Started '+d['name'].lower()+': '+str(selected['phases'])+' assigned phase(s).')
    elif kind in ('foundation-resume', 'foundation-cancel'):
        g.require(r['job'], 'There is no unfinished chapter task.')
        g.require(g.character_at_castle(s, 'founder'), 'Return home to manage this task.')
        if kind == 'foundation-resume': g.set_character_assignment(s, 'founder', ASSIGNMENT)
        else:
            s['sharedFunds'] += r['job']['cost']
            for material, n in r['job']['materials'].items(): s['materialInventory'][material] += n
            r['job'] = None
            if g.character_assignment(s, 'founder')==ASSIGNMENT: g.set_character_assignment(s, 'founder', 'rest')
            g.add_journal(s, 'Cancelled the unfinished foundation task. Its committed costs were refunded; completed discoveries remain recorded.')
    elif kind == 'foundation-conclude':
        g.require(ready(s), 'Complete the investigation, restoration and both circuit tests first.')
        g.require(not r['concludedOn'], 'The chamber investigation is already complete.')
        g.require(g.character_at_castle(s, 'founder'), 'Return home to record your findings.')
        r['concludedOn'] = dict(dayNumber=s['dayNumber'], phase=s['currentDayPhase'])
        g.award_advancement(s, 'founder', 'beneath-the-hearth', 2, 'Restored and tested the foundation ritual chamber')
        g.add_journal(s, 'Chamber investigation complete. '+CONCLUSION+' Your scholar gains 2 advancement points.')
    elif kind == 'foundation-invite':
        who=a.get('characterId')
        g.require(isinstance(who,str), 'Choose a resident partner.')
        reasons=partner_blockers(s, who); g.require(not reasons, ' '.join(reasons))
        g.require(not r['ritual'] and not r['invitation'], 'Finish or cancel the current ritual invitation first.')
        r['invitation'] = {'partnerId': who}
    elif kind == 'foundation-decline':
        g.require(r['invitation'], 'There is no open invitation.')
        r['invitation'] = None
    elif kind == 'foundation-ritual-start':
        invitation=r['invitation']; g.require(invitation, 'Ask a partner and review the invitation first.')
        who=invitation['partnerId']; reasons=partner_blockers(s, who)
        g.require(not reasons, ' '.join(reasons))
        g.require(not r['ritual'], 'The ritual is already arranged.')
        r['ritual'] = {'partnerId': who}; r['invitation'] = None
        for person in ('founder', who): g.set_character_assignment(s, person, RITUAL_ASSIGNMENT)
        g.add_journal(s, 'You and '+g.character_profile(s, who)['name']+' agree to a private ritual in the foundation chamber. One shared phase is scheduled for the next Advance.')
    elif kind in ('foundation-ritual-resume', 'foundation-ritual-cancel'):
        g.require(r['ritual'], 'There is no arranged ritual.')
        who = r['ritual']['partnerId']
        if kind == 'foundation-ritual-cancel':
            release_ritual(s, who); r['ritual'] = None
        else:
            reasons = partner_blockers(s, who, False); g.require(not reasons, ' '.join(reasons))
            for person in ('founder', who): g.set_character_assignment(s, person, RITUAL_ASSIGNMENT)
    else: raise g.RuleError('Choose a listed foundation chamber action.')
    return True


def resolve(s, summary):
    import game as g, relationships
    r=saved(s)
    if working(s):
        p=r['job']; p['done']+=1; d=STEPS[p['stepId']]
        summary.append(d['name']+': '+str(p['done'])+' / '+str(p['phases'])+' phases.')
        if p['done']>=p['phases']:
            key=p['stepId']; r['completed'][key]=dict(title=d['name'], text=d['result'], method=p['method'], dayNumber=s['dayNumber'], phase=s['currentDayPhase'])
            if key=='restoration': s['headquarters']['rooms'][ROOM]='complete'
            r['job']=None; g.set_character_assignment(s, 'founder', 'rest')
            summary.append(d['result'])
    if r['ritual'] and not ritual_work_blockers(s):
        who=r['ritual']['partnerId']; name=g.character_profile(s, who)['name']; r['ritualCount']+=1
        text=('You and '+name+' confirm that you both want to continue and close the chamber door. The scene fades to black. '
              'Afterwards, you check the indicator beside the door. The household blessing is active for the next three days.')
        record=dict(title='A private ritual in the foundation chamber', response=text, participants=['founder',who], dayNumber=s['dayNumber'], phase=s['currentDayPhase'])
        relationships.remember(s, 'foundation-ritual:'+str(r['ritualCount']), record, 'affection')
        r['lastRitual']=deepcopy(record)
        r['blessing']=dict(startsAt=stamp(s)+1, expiresAt=stamp(s)+1+DURATION, announcedEnd=False)
        release_ritual(s, who); r['ritual']=None
        summary.extend([text, 'Household blessing: +20% positive relationship gains and resident bonding for 9 phases. Existing blessings are refreshed, not added together.'])


def after_advance(s):
    import game as g
    b=saved(s)['blessing']
    if b and stamp(s)>=b['expiresAt'] and not b['announcedEnd']:
        b['announcedEnd']=True
        text='The foundation chamber’s three-day blessing has ended. Relationship gains return to their normal rate.'
        s['lastPhaseSummary'].append(text); g.add_journal(s, text)


def forecast(s):
    r=saved(s); rows=[]
    if r['job']: rows.append(STEPS[r['job']['stepId']]['name']+(': +1 work phase.' if working(s) else ': paused; resume the task to continue.'))
    if r['ritual']: rows.append('Foundation chamber ritual: '+('paused. '+' '.join(ritual_work_blockers(s)) if ritual_work_blockers(s) else 'one private phase; activates +20% relationship gains for the following 9 phases.'))
    return rows


def view(s):
    import game as g, romance_content
    r=saved(s); rows=[]
    for key,d in STEPS.items():
        rows.append(dict(id=key, name=d['name'], purpose=d['purpose'], cost=d.get('cost',0), materials=deepcopy(d.get('materials',{})),
                         memory=deepcopy(r['completed'].get(key)), blockers=blockers(s,key), methods=methods(s,key)))
    job=deepcopy(r['job'])
    if job: job.update(name=STEPS[job['stepId']]['name'], working=working(s))
    candidates=[dict(id=who, name=g.character_profile(s,who)['name'], blockers=partner_blockers(s,who))
                for who in g.household_members(s) if who!='founder' and who in romance_content.SCENES]
    invite=deepcopy(r['invitation'])
    if invite:
        who=invite['partnerId']; invite['name']=g.character_profile(s,who)['name']
        invite['blockers']=partner_blockers(s,who)
        invite['reply']=('We need to leave this for another time.' if invite['blockers'] else
                         INVITATION_REPLIES.get(who, 'Yes. I would like to spend this time with you.'))
    return dict(unlocked=unlocked(s), started=r['started'], complete=bool(r['concludedOn']), ready=ready(s),
                roomReady='restoration' in r['completed'], steps=rows, job=job, invitation=invite,
                ritual=deepcopy(r['ritual']), ritualBlockers=ritual_work_blockers(s), partners=candidates,
                ritualResumeBlockers=partner_blockers(s,r['ritual']['partnerId'],False) if r['ritual'] else [],
                blessing=bonus_view(s), lastRitual=deepcopy(r['lastRitual']), ritualCount=r['ritualCount'],
                conclusion=CONCLUSION if r['concludedOn'] else '', forecast=forecast(s))


def register(namespace):
    import headquarters as h
    h.ROOMS[ROOM]=h.room('Foundation ritual chamber', 'Learning',
        'A private underground chamber connected to the household wards. Discovered in the lower wing; restoration is available after Chapter 5.',
        (VIEW,), cost=24, phases=3, benefit='An optional private ritual grants +20% relationship gains and resident bonding for three days.')
    namespace['ORIGINAL_ASSETS'][ROOM]='/assets/rooms/foundation-chamber.webp'
