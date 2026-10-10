"""Saved local reports and scripted magical introductions, without NPC authoring."""
from copy import deepcopy
import hashlib
import random
import secrets
import encounter_people as ep

def initialize(s):
    s.setdefault('worldRecruitment',dict(seed=None,serial=0,lastReportDay=None,report=None))

def saved(s):return s.get('worldRecruitment',dict(seed=None,serial=0,lastReportDay=None,report=None))

def rng(s):
    initialize(s);r=saved(s)
    if not r['seed']:r['seed']=secrets.token_hex(16)
    r['serial']+=1
    token=r['seed']+':'+str(r['serial'])
    return random.Random(hashlib.sha256(token.encode()).digest()),token

def pending(s):
    return [q for q in s.get('recruitmentQuests',{}).values() if q['status'] in ('available','outbound','custody','rescued') or q['status']=='released' and q.get('willing')]

def blockers(s,kind='rescue'):
    import game as g,field_patrols as p,recruitment_quests as q
    b=[]
    if not g.character_at_castle(s,'founder'):b.append('Return home to collect local reports.')
    if not p.local_unlocked(s):b.append('Complete Chapter 4, Keeping the Hearth, before arranging recruitment patrols.')
    if saved(s)['report']:b.append('Finish or cancel the current report gathering first.')
    if saved(s)['lastReportDay']==s['dayNumber']:b.append('New reports are available tomorrow. Existing leads remain available.')
    if len(pending(s))>=3:b.append('Resolve an existing lead before taking another; the board holds three unfinished quests.')
    if len(s.get('reviewedCandidates',{}))>=50:b.append('This campaign has reached its limit of fifty generated identities.')
    if kind=='capture' and not q.available_chambers(s):b.append('Restore a free Quiet chamber before asking for bandit leads.')
    return b

def make(s,ancestry,token,source,encounter_key=None,material=None):
    import character_pool as pool,candidate_proposals as cp
    choices={'ancestry':ancestry}
    if material:choices['bodyMaterial']=material
    selection=pool.select(s,token,choices);proposal=pool.offline(s,selection,token)
    who='traveller-'+hashlib.sha256(token.encode()).hexdigest()[:16]
    c=cp.approved_definition(proposal,who,'scripted-world',who)
    c['profile'].update(generationIngredients=selection,recruitmentSource=source)
    if encounter_key:
        ep.apply_element(c['profile'],encounter_key)
        c['profile']['arrivalMethod']='recruitment'
        c['profile']['origin']='A travelling '+ancestry.lower()+' '+proposal['occupation']+' from the valley routes. '+proposal['ambition']
        c['profile']['encounterArtKey']=encounter_key
        c['departureText']='“Thank you for the visit. I will take the valley road from here.”'
    s['reviewedCandidates'][who]=c
    return who

def apply(s,a):
    kind=a.get('type','')
    if not kind.startswith('world-'):return False
    import game as g,character_pool as pool
    initialize(s);r=saved(s)
    g.require(g.character_at_castle(s,'founder'),'Return home before arranging introductions.')
    if kind=='world-reports':
        quest=a.get('questKind','rescue');g.require(quest in ('rescue','capture'),'Choose missing travellers or bandit reports.')
        b=blockers(s,quest);g.require(not b,' '.join(b))
        r['report']={'kind':quest};s['founderAssignment']='local-reports'
        g.add_journal(s,'You arrange to collect '+('missing-traveller' if quest=='rescue' else 'bandit')+' reports. One assigned phase is needed; nobody has been generated or recruited yet.')
    elif kind in ('world-resume','world-cancel'):
        g.require(r['report'] is not None,'There is no unfinished report gathering.')
        if kind=='world-resume':s['founderAssignment']='local-reports'
        else:
            r['report']=None
            if s['founderAssignment']=='local-reports':s['founderAssignment']='rest'
    elif kind=='world-plan':
        ancestry=a.get('ancestry');g.require(isinstance(ancestry,str) and ancestry in pool.ANCESTRIES and pool.arrival_method(ancestry)!='recruitment','Choose an exotic summoning invitation or a golem awakening plan.')
        material=a.get('bodyMaterial','clay') if ancestry=='Golem' else None
        if material:g.require(material in pool.GOLEM_MATERIALS,'Choose a listed golem body material.')
        existing=next((w for w,c in s['reviewedCandidates'].items() if c['profile'].get('recruitmentSource')=='magical-plan' and c['profile']['ancestryLabel']==ancestry and w not in s['people']),None)
        g.require(existing is None,'A plan for this ancestry is already saved. Continue it under Summoning & arrivals.')
        g.require(len(s['reviewedCandidates'])<50,'This campaign has reached its limit of fifty generated identities.')
        _,token=rng(s);who=make(s,ancestry,token,'magical-plan',material=material)
        g.add_journal(s,'Prepared '+('an awakening plan' if ancestry=='Golem' else 'a summoning invitation')+' for '+s['reviewedCandidates'][who]['profile']['name']+'. Complete the usual paid magical work before any meeting. This saved identity will not reroll.')
    else:raise g.RuleError('Choose a listed recruitment-board action.')
    return True

def resolve(s,summary,assignments):
    import game as g,bestiary,recruitment_quests as q
    r=saved(s)
    if not r['report'] or assignments.get('founder')!='local-reports' or not g.character_at_castle(s,'founder'):return
    # Saved serial and seed advance only when the assigned phase completes.
    kind=r['report']['kind']
    randomizer,token=rng(s);key=ep.choose(randomizer,kind);aid=ep.ancestry(key)
    who=make(s,bestiary.ANCESTRIES[aid]['name'],token,'world-quest',key)
    q.lead(s,who,kind,world=True)
    r.update(report=None,lastReportDay=s['dayNumber']);s['founderAssignment']='rest'
    summary.append('Local reports identify '+s['reviewedCandidates'][who]['profile']['name']+'. The '+('rescue' if kind=='rescue' else 'bandit')+' quest is saved on the recruitment board; an introduction requires completing it.')

def view(s):
    import character_pool as pool
    r=saved(s)
    return dict(report=deepcopy(r['report']),working=bool(r['report'] and s['founderAssignment']=='local-reports'),rescueBlockers=blockers(s),captureBlockers=blockers(s,'capture'),ancestries=[a for a in pool.ANCESTRIES if pool.arrival_method(a)=='summoning'],materials=list(pool.GOLEM_MATERIALS),exoticChance=ep.EXOTIC_CHANCE)
