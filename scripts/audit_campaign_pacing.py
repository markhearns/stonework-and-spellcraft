"""Replay earned campaigns, recording actual actions and work without rendering a browser.

Run from the project root: python scripts/audit_campaign_pacing.py OUTPUT_DIRECTORY
Reports contain test campaigns only. No existing save is opened or modified.
"""
from pathlib import Path
import inspect
import json
import sys
import unittest
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import game as g
import test_refinement_campaign_v100 as flow
import field_patrols

output = Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=True)
original = g.apply_action
starts = {'shape-start':2, 'grow-plan':3, 'hearth-start':4, 'arms-start':5,
          'roads-start':6, 'patrol-start':7, 'trial-start':8}
routes = []
current = None
chapter = 1


def point(s):
    assignment=g.character_assignment(s,'founder')
    activity='field-patrol' if field_patrols.away(s,'founder') else assignment
    return dict(day=s['dayNumber'], phase=s['currentDayPhase'], crowns=s['sharedFunds'],
                food=s['provisions']['stock'], unfedDays=s['provisions']['unfedDays'],
                members=g.household_members(s), assignment=assignment, activity=activity)


def tracked(s, action):
    global current, chapter
    # Ignore internal delegation and speculative actions used to validate previews.
    caller = Path(inspect.currentframe().f_back.f_code.co_filename)
    if caller.parent.name != 'tests':
        return original(s, action)
    if current is None or (action['type']=='food-policy' and s['dayNumber']==1):
        current = dict(route=len(routes)+1, actions=[], chapters={}, streak=0)
        routes.append(current)
        chapter = 1
    next_chapter=starts.get(action['type'],chapter)
    if next_chapter != chapter:
        (output / f"route-{current['route']}-before-chapter-{next_chapter}.json").write_text(json.dumps(s))
        chapter = next_chapter
    row=current['chapters'].setdefault(str(chapter), dict(start=point(s), actions=0, advances=0,
        founderAssignments={}, maxConsecutiveAdvances=0))
    before=point(s)
    result=original(s,action)
    row['actions']+=1
    if action['type']=='advance':
        row['advances']+=1
        assignments=row['founderAssignments'];key=before['activity'];assignments[key]=assignments.get(key,0)+1
        current['streak']+=1
        row['maxConsecutiveAdvances']=max(row['maxConsecutiveAdvances'],current['streak'])
    else:current['streak']=0
    row['end']=point(s)
    current['actions'].append(dict(chapter=chapter, action=action, before=before, after=point(s),
                                  summary=s['lastPhaseSummary'] if action['type']=='advance' else []))
    (output / f"route-{current['route']}-latest.json").write_text(json.dumps(s))
    return result


if '--guided-income' in sys.argv:
    import first_hearth
    import test_house_shape, test_keeping_hearth, test_chapter_five_flow
    def guided_money(self, target):
        self.commission_count=getattr(self,'commission_count',0)
        for _ in range(100):
            if self.s['sharedFunds']>=target:break
            action=first_hearth.income(self.s,target,'the next project',{'view':'headquarters'})['action']
            if action['type']=='commission-start':self.commission_count+=1
            self.act(action['type'],**{k:v for k,v in action.items() if k!='type'})
        else:self.fail('The funding guide did not reach its quoted target.')
        self.act('assign-founder',assignment='rest')
    for cls in (test_house_shape.HouseShapeTests,test_keeping_hearth.KeepingHearthTests,
                test_chapter_five_flow.FiveChapterFlowTests,flow.RefinementCampaignTests):
        cls.money=guided_money

g.apply_action=tracked
suite=unittest.defaultTestLoader.loadTestsFromTestCase(flow.RefinementCampaignTests)
result=unittest.TextTestRunner().run(suite)
g.apply_action=original
for route in routes:route.pop('streak')
report=dict(passed=result.wasSuccessful(),guidedIncome='--guided-income' in sys.argv,routes=routes,
            scope='Two continuous fresh campaigns through eight chapters, then a paid objective. Real actions, earned resources, no cheats; serialized reloads in the route helpers. Counts are simulated phases, not human playtime.')
(output/'report.json').write_text(json.dumps(report,indent=2))
for route in routes:
    print('ROUTE',route['route'])
    for chapter,row in route['chapters'].items():
        print(chapter, json.dumps({k:v for k,v in row.items() if k not in ('start','end')}))
if not result.wasSuccessful():sys.exit(1)
