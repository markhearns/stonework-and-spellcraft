"""Campaign-owned castle history. Only discovered evidence enters public contexts."""
from copy import deepcopy

LEADS = {
    'hearth-margin': {'name': 'A mark beneath the hearth lintel', 'phases': 2, 'description': 'Compare the restored living-wing wards with a small maker’s mark.'},
    'archive-leaf': {'name': 'A leaf without a catalogue number', 'phases': 2, 'description': 'Compare a loose archival leaf with the mark already recorded.'},
    'window-measure': {'name': 'The measure of the old windows', 'phases': 3, 'description': 'Use learned refraction to read an old optical inscription.'},
    'founding-record': {'name': 'Put the evidence together', 'phases': 2, 'description': 'Compare the three independent records and establish what they support.'},
}


def initial_packet():
    return {
        'version': 2, 'contentKind': 'authored-castle-history',
        'foundation': 'The castle was a refuge and workshop founded by itinerant enchanters. Its living wards resonated with freely shared desire and intimacy as a supplementary source of enchantment, never as payment for shelter. The founders later dispersed by agreement after their long survey ended; they left the refuge dormant, not cursed or betrayed.',
        'evidence': {
            'hearth-margin': 'Under the repaired lintel is a maker’s mark: several hands around an open door. A service line runs around, rather than through, the small violet chamber in the stone. The ordinary hearth wards were designed to function without that chamber.',
            'archive-leaf': 'The recovered leaf lists visiting craftspeople rather than subjects or servants. Beside the sleeping rooms, a keeper wrote: “A bed is a promise, never a bargain.” A separate margin describes the house answering willingly shared warmth, flirtation and desire.',
            'window-measure': 'Read through a steady refracting lens, the inscription records the completion of a long survey. Its signatories chose different roads and left instructions to keep the house safe and dormant until another household took responsibility for it.',
            'founding-record': 'Together, the records describe a refuge made by travelling enchanters, maintained by ordinary practical magic and enriched by freely shared intimacy. Its keepers dispersed after finishing their survey. The house waited in dormancy; its decline was neglect over time, not punishment for refusing its desires.',
        },
    }


def initialize(state):
    state.setdefault('privateCastleLore', initial_packet())
    state.setdefault('castleMystery', {'discoveries': {}, 'project': None, 'sharedWith': {}})


def blockers(state, key):
    import game as g
    discoveries = state['castleMystery']['discoveries']; result = []
    if not g.character_at_castle(state, 'founder'): result.append('Return your scholar to the castle.')
    if key in discoveries: result.append('This evidence is already recorded.')
    if key == 'hearth-margin' and not state['livingWingCompletedOn']: result.append('Complete A Proper Living Wing first.')
    if key == 'archive-leaf':
        if 'hearth-margin' not in discoveries: result.append('Record the hearth mark first.')
        if state['miraArchiveProject']['status'] not in ('ready-to-bind', 'complete') and state['researchProjects'].get('archive-foundations',{}).get('status')!='complete':
            result.append('Complete Arrange the first archive, or the living-index study. A companion’s personal story is not required.')
    if key == 'window-measure':
        if 'hearth-margin' not in discoveries: result.append('Record the hearth mark first.')
        if 'gentle-refraction' not in g.character_principles(state, 'founder'): result.append('Your scholar must learn Gentle refraction.')
    if key == 'founding-record' and not all(key in discoveries for key in ('hearth-margin','archive-leaf','window-measure')): result.append('Record all three sources before drawing the conclusion.')
    import castle_reawakening
    if key in castle_reawakening.LEADS:result.extend(castle_reawakening.lead_blockers(state,key))
    return result


def view(state):
    import game as g
    record = state['castleMystery']; project = record['project']
    return {'contentLabel': 'The castle’s recorded history. Discoveries already made in this campaign are kept unchanged.',
        'discoveries': deepcopy(record['discoveries']), 'project': deepcopy(project),
        'working': bool(project and state['founderAssignment']=='mystery' and g.character_at_castle(state,'founder')),
        'leads': {key: {**deepcopy(definition), 'blockers': blockers(state,key) + (['Finish or cancel the current investigation first.'] if project else [])} for key,definition in LEADS.items()},
        'sharedWith': deepcopy(record['sharedWith']),
        'shareTargets': {who:g.character_profile(state,who)['name'] for who in g.household_members(state) if who!='founder' and g.character_at_castle(state,who)}}


def shared_evidence(state, who):
    record = state.get('castleMystery', {})
    return [deepcopy(record['discoveries'][key]) for key in record.get('sharedWith',{}).get(who,[]) if key in record.get('discoveries',{})]


def apply(state, action):
    kind=action.get('type')
    if kind not in ('start-mystery','resume-mystery','cancel-mystery','share-mystery'): return False
    import game as g
    g.require(g.character_at_castle(state,'founder'),'Return your scholar to the castle before investigating or sharing evidence.')
    record=state['castleMystery'];project=record['project']
    if kind=='share-mystery':
        who, key=action.get('characterId'), action.get('leadId')
        g.require(isinstance(who,str) and who in g.household_members(state) and who!='founder','Choose a household colleague.')
        g.require(g.character_at_castle(state,who),'Wait until your colleague is home to share this evidence.')
        g.require(isinstance(key,str) and key in record['discoveries'],'Only recorded discoveries can be shared.')
        known=record['sharedWith'].setdefault(who,[])
        if key not in known:
            known.append(key)
            g.add_journal(state,'Shared recorded evidence with '+g.character_profile(state,who)['name']+': '+LEADS[key]['name']+'. You recorded the discussion; it does not add evidence or change relationships.')
    elif kind=='start-mystery':
        key=action.get('leadId')
        g.require(isinstance(key,str) and key in LEADS,'Choose an available investigation.')
        g.require(project is None,'Finish or cancel the current investigation first.')
        reasons=blockers(state,key);g.require(not reasons,' '.join(reasons))
        import castle_reawakening
        castle_reawakening.ensure_packet(state,key)
        record['project']={'leadId':key,'completedWorkPhases':0,'requiredWorkPhases':LEADS[key]['phases']}
        state['founderAssignment']='mystery'
        g.add_journal(state,'Began investigating '+LEADS[key]['name'].lower()+'. No crowns or Resonance required; own assigned phases only.')
    elif kind=='resume-mystery':
        g.require(project is not None,'There is no unfinished investigation.')
        state['founderAssignment']='mystery'
    else:
        g.require(project is not None,'There is no unfinished investigation to cancel.')
        record['project']=None
        if state['founderAssignment']=='mystery': state['founderAssignment']='rest'
        g.add_journal(state,'Put the unfinished investigation aside. Recorded evidence is kept; unfinished progress is discarded.')
    return True


def forecast(state):
    import game as g
    project=state['castleMystery']['project']
    if not project:return []
    working=state['founderAssignment']=='mystery' and g.character_at_castle(state,'founder')
    return [LEADS[project['leadId']]['name']+(': +1 investigation phase.' if working else ': paused; evidence and progress kept.')]


def resolve(state, summary):
    import game as g
    record=state['castleMystery'];project=record['project']
    if not project or state['founderAssignment']!='mystery' or not g.character_at_castle(state,'founder'):return
    project['completedWorkPhases']+=1
    key=project['leadId']
    summary.append(LEADS[key]['name']+': '+str(project['completedWorkPhases'])+' / '+str(project['requiredWorkPhases'])+' investigation phases.')
    if project['completedWorkPhases']<project['requiredWorkPhases']:return
    # Copy the campaign's own immutable packet, not a newly generated explanation.
    if key not in record['discoveries']:
        record['discoveries'][key]={'title':LEADS[key]['name'],'text':state['privateCastleLore']['evidence'][key],
            'sourceVersion':state['privateCastleLore']['version'],'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']}
        g.award_advancement(state,'founder','mystery:'+key,1,'Recorded '+LEADS[key]['name'].lower())
    record['project']=None;state['founderAssignment']='rest'
    summary.append('Recorded evidence in the castle mystery ledger: '+LEADS[key]['name']+'. One advancement; no automatic sharing or relationship change.')
