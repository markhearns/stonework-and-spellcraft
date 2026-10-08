"""Extend discovered history without replacing a campaign's saved explanation."""
from copy import deepcopy

LEADS={
 'ward-junction':dict(name='Trace the library’s disconnected ward',phases=2,description='Follow the old service line from the library lamp to its disconnected junction.'),
 'survey-cylinder':dict(name='Read the survey cylinder',phases=2,description='Inspect the brass cylinder found beside the junction and compare its route marks with the archive.'),
 'lamp-plan':dict(name='Recover the reading-lamp repair plan',phases=2,description='Compare the cylinder’s measurements with the library fittings and write a repair plan.'),
}
EVIDENCE={
 'ward-junction':'The library lamp has two separate connections. One carries ordinary hearth power. The other leads to the small violet chamber. A broken switch, rather than a missing power source, stopped the lamp from working.',
 'survey-cylinder':'The cylinder contains a record of shallow crossings between this world and another. Its makers used the castle as a stable reference point. They recorded each crossing, closed it after the survey, and left the routes marked for later study.',
 'lamp-plan':'The measurements explain the lamp’s purpose. Its steady light makes tiny changes in ward inscriptions visible. A second lens can show how the violet chamber responds to an established affectionate household. Repairing the ordinary lamp needs no Resonance.',
}


def install():
    import castle_mystery
    castle_mystery.LEADS.update(LEADS)


def lead_blockers(s,key):
    import game as g,headquarters as h
    known=s['castleMystery']['discoveries'];b=[]
    prior={'ward-junction':'founding-record','survey-cylinder':'ward-junction','lamp-plan':'survey-cylinder'}[key]
    if prior not in known:b.append('Record '+__import__('castle_mystery').LEADS[prior]['name']+' first.')
    if key=='ward-junction' and not h.ready(s,'workshop'):b.append('Restore the workshop to inspect the disconnected parts.')
    if key=='survey-cylinder' and 'courteous-passage' not in g.character_principles(s,'founder'):b.append('Learn Courteous passage to read the survey markings.')
    return b


def ensure_packet(s,key):
    if key in EVIDENCE:
        s['privateCastleLore']['evidence'].setdefault(key,EVIDENCE[key])


def saved(s):return s.get('castleReawakening',{'restored':False,'studyComplete':False,'job':None,'shownTo':[]})


def blockers(s,study=False):
    import game as g
    r=saved(s);b=[]
    if not g.character_at_castle(s,'founder'):b.append('Return your scholar home.')
    if r['job']:b.append('Finish or cancel the current lamp work.')
    if 'lamp-plan' not in s['castleMystery']['discoveries']:b.append('Recover the reading-lamp repair plan first.')
    if study:
        if not r['restored']:b.append('Repair the library reading lamp first.')
        if r['studyComplete']:b.append('The Resonance study is already complete.')
        if s['resonancePoints']<12:b.append('The household needs 12 accumulated Resonance. Existing mutual affection generates it on Advance; repeating conversations is unnecessary.')
    elif r['restored']:b.append('The library reading lamp is already repaired.')
    cost=8 if study else 6;material='moon-glass' if study else 'binding-thread'
    if s['sharedFunds']<cost:b.append('Needs '+str(cost)+' shared crowns.')
    if s['materialInventory'].get(material,0)-s['materialReserveTargets'].get(material,0)<1:b.append('Needs 1 unreserved '+g.MATERIALS[material]['name']+'.')
    return b


def apply(s,a):
    import game as g,shared_history
    kind=a.get('type')
    if kind not in ('castle-lamp-start','castle-lamp-study','castle-lamp-resume','castle-lamp-cancel','castle-lamp-colour','castle-lamp-share'):return False
    g.require(g.character_at_castle(s,'founder'),'Return home to use the library lamp.')
    r=s.setdefault('castleReawakening',deepcopy(saved(s)))
    if kind in ('castle-lamp-start','castle-lamp-study'):
        study=kind=='castle-lamp-study';b=blockers(s,study);g.require(not b,' '.join(b))
        cost=8 if study else 6;material='moon-glass' if study else 'binding-thread'
        s['sharedFunds']-=cost;s['materialInventory'][material]-=1
        r['job']=dict(study=study,done=0,phases=2,cost=cost,material=material)
        g.set_character_assignment(s,'founder','castle-lamp')
    elif kind in ('castle-lamp-resume','castle-lamp-cancel'):
        g.require(r['job'],'There is no unfinished lamp work.')
        if kind=='castle-lamp-resume':g.set_character_assignment(s,'founder','castle-lamp')
        else:
            s['sharedFunds']+=r['job']['cost'];s['materialInventory'][r['job']['material']]+=1;r['job']=None
            if g.character_assignment(s,'founder')=='castle-lamp':g.set_character_assignment(s,'founder','rest')
    elif kind=='castle-lamp-colour':
        g.require(r['studyComplete'],'Complete the Resonance lens study before adjusting its colour.')
        colour=a.get('colour');g.require(colour in ('amber','violet'),'Choose amber or violet light.')
        s['roomFurnishings']['library']='brass-lamp' if colour=='amber' else 'violet-lamp'
        g.add_journal(s,'Set the library reading lamp to '+colour+'. This changes its appearance only.')
    else:
        who=a.get('characterId')
        g.require(r['restored'],'Repair the reading lamp first.')
        g.require(isinstance(who,str) and who!='founder' and who in g.household_members(s) and g.character_at_castle(s,who),'Choose a companion currently at home.')
        g.require(who not in r['shownTo'],'This companion has already seen the repaired lamp.')
        r['shownTo'].append(who)
        # Sharing the lamp includes only already discovered evidence.
        known=s['castleMystery']['sharedWith'].setdefault(who,[])
        for key in LEADS:
            if key in s['castleMystery']['discoveries'] and key not in known:known.append(key)
        shared_history.record(s,'library-lamp',['founder',who],'Reading the old survey together',
            'The repaired lamp made the fine route marks legible. You compared the discovered survey with '+g.character_profile(s,who)['name']+'.','discovery')
    return True


def resolve(s,summary,assignments):
    import game as g,signature_growth
    r=saved(s);job=r['job']
    if not job or assignments.get('founder')!='castle-lamp':return
    job['done']+=1
    summary.append(('Resonance lens study' if job['study'] else 'Reading-lamp repair')+': '+str(job['done'])+'/2 work phases.')
    if job['done']<2:return
    if job['study']:
        r['studyComplete']=True
        g.learn_for_character(s,'founder','field-calibration')
        g.award_advancement(s,'founder','resonance-lens',1,'Completed the Resonance lens study')
        summary.append('Resonance lens study complete: learned Field calibration, gained 1 advancement point and unlocked amber/violet library lighting. Resonance was not spent.')
    else:
        r['restored']=True;s['roomFurnishings']['library']='brass-lamp'
        summary.append('The reading lamp works again. You can show the discovered survey markings to a companion and begin the optional Resonance lens study at 12 Resonance.')
    signature_growth.record_work(s,'founder','castle-study')
    r['job']=None;g.set_character_assignment(s,'founder','rest')


def view(s):
    import game as g
    r=saved(s)
    return dict(**deepcopy(r),repairBlockers=blockers(s),studyBlockers=blockers(s,True),
                people=[dict(id=w,name=g.character_profile(s,w)['name'],available=g.character_at_castle(s,w) and w not in r['shownTo']) for w in g.household_members(s) if w!='founder'],
                resonance=s['resonancePoints'],gain=g.resonance_forecast(s))
