"""Follow Chapters 6–8 guidance from an earned Chapter 6 checkpoint.

Usage: python scripts/audit_late_guidance.py CHECKPOINT_JSON OUTPUT_DIRECTORY
Only a detached test save is changed. Choices in this audit are fixed explicitly.
"""
from pathlib import Path
from copy import deepcopy
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import game as g
import campaign_guidance as guide
import first_hearth
import first_patrol
import field_patrols
import roads_we_keep
import arrivals

s=g.migrate_state(json.loads(Path(sys.argv[1]).read_text()))
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
assert not s['testing']['used']
assert s['armsOfOurOwn']['completedOn'] and not s['roadsWeKeep']['started']
actions=[];steps=[]


def act(kind,**kw):
    global s
    a=dict(type=kind,**kw)
    g.apply_action(s,a)
    s=g.migrate_state(json.loads(json.dumps(s)))
    actions.append(a)


def follow(row):
    assert row['action'] and not row.get('blockers'),row
    a=row['action'];act(a['type'],**{k:v for k,v in a.items() if k!='type'})


def fund(target):
    for _ in range(100):
        if s['sharedFunds']>=target:return
        follow(first_hearth.income(s,target,'the guest bedroom',{'view':'housing'}))
    raise AssertionError('Funding did not finish')


def recruit_rhess():
    contact='introduced-rhess'
    for topic in ('intentions','home','visit'):act('summoning-talk',contactId=contact,topic=topic)
    rooms=arrivals.eligible_rooms(s,s['people']['rhess'])
    if not rooms:
        fund(34);act('hq-bedroom',roomId='guard-dormitory')
        for _ in range(4):act('advance')
        rooms=arrivals.eligible_rooms(s,s['people']['rhess'])
    assert rooms
    act('summoning-invite',contactId=contact,roomId=rooms[0]);act('advance')
    act('summoning-ask-stay',contactId=contact)
    act('summoning-household-decision',contactId=contact,decision='invite-to-stay')
    act('gear-review')


def choose_field():
    e=s.get('expedition')
    if e:
        if e['stage']=='awaiting-choice':act('choose-expedition-approach',approach='survey')
        else:
            choices=(first_patrol if e['siteId'] in first_patrol.SITES else roads_we_keep).encounter_view(s)['choices']
            method=next((key for key in ('keeper','gear') if key in choices and not choices[key]['blockers']),'patient')
            act('choose-encounter-method',methodId=method)
        return
    rows=[r for r in field_patrols.choices(s) if not r['blockers']]
    choice=next((r for r in rows if r['kind'] in ('peace','bypass')),None) or max(
        (r for r in rows if r['kind']=='attack'),
        key=lambda r:2*r['preview']['damage']-r['preview']['injury']-8*sum(n==0 for n in r['preview']['healthAfter'].values()))
    act('watch-method',methodId=choice['id'])


for chapter,record,start,read in [(6,'roadsWeKeep','roads-start',guide.roads),
                                 (7,'firstPatrol','patrol-start',guide.first_patrol),
                                 (8,'firstRealTest','trial-start',guide.trial)]:
    act(start)
    for _ in range(220):
        if s[record]['completedOn']:break
        before=deepcopy(s);row=guide.checked(s,read(s));assert s==before
        assert row and not row.get('blockers'),row
        steps.append(dict(chapter=chapter,id=row['id'],title=row['title'],action=row['action']))
        if row['action']:follow(row)
        elif row['id']=='field-choice':choose_field()
        elif row['id']=='rescue':act('start-expedition',siteId=roads_we_keep.SITE)
        elif row['id']=='agreement' and chapter==6:act('roads-agreement',choice='materials')
        elif row['id']=='trail':act('start-expedition',siteId=first_patrol.TRAIL)
        elif row['id']=='rhess':recruit_rhess()
        elif row['id']=='agreement' and chapter==7:
            act('agree-household-role',characterId='rhess',role='fieldwork',enabled=True,willingnessReviewed=True)
        elif row['id']=='plan':act('patrol-plan',choice='repair') if chapter==7 else act('trial-plan',choice='negotiate')
        elif row['id']=='wardstones':
            act('gear-party-loadout',participants=['founder','rhess'],mode='expedition')
            act('start-expedition',siteId=first_patrol.WARD,companionIds=['rhess'])
        elif row['id']=='mission':
            mission=next(k for k in field_patrols.MISSIONS if k not in field_patrols.chapter(s)['completed'])
            act('watch-depart',participants=['founder','rhess'],missionId=mission)
        elif row['id']=='closing' and chapter==8:act('trial-conclude',choice='signals')
        else:raise AssertionError(row)
    else:raise AssertionError('Guidance did not finish Chapter '+str(chapter))
    print('Chapter',chapter,'complete',flush=True)
assert not s['testing']['used'] and s['provisions']['unfedDays']==0
(out/'save.json').write_text(json.dumps(s))
(out/'report.json').write_text(json.dumps(dict(passed=True,steps=steps,actions=actions,
    completedChapters=[6,7,8],unfedDays=s['provisions']['unfedDays'],cheats=s['testing']['used']),indent=2))
