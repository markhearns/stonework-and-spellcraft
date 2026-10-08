"""Measure actual earned-resource routes; optional downtime uses ordinary actions."""
from pathlib import Path
import sys,json,unittest,inspect
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import game as g,test_seven_chapter_flow as flow
original=g.apply_action;routes=[];current=None;chapter=1
with_downtime='--with-downtime' in sys.argv
starts={'shape-start':2,'grow-plan':3,'hearth-start':4,'arms-start':5,'roads-start':6,'patrol-start':7}

def tracked(s,a):
 global chapter
 if a['type'] in starts:chapter=starts[a['type']]
 row=current['chapters'][str(chapter)];row.setdefault('start',{'day':s['dayNumber'],'phase':s['currentDayPhase']});row['actions']+=1
 if a['type']=='advance':
  row['advances']+=1;row['copyingAdvances']+=g.character_assignment(s,'founder')=='commissions';row['restAdvances']+=g.character_assignment(s,'founder')=='rest';row['overnights']+=s['currentDayPhase']=='evening';current['streak']+=1;current['clicks']=0;row['maxConsecutiveAdvances']=max(row['maxConsecutiveAdvances'],current['streak'])
 else:
  current['streak']=0;current['clicks']+=1;row['maxActionsWithoutAdvance']=max(row['maxActionsWithoutAdvance'],current['clicks'])
 result=original(s,a);row['end']={'day':s['dayNumber'],'phase':s['currentDayPhase']};return result

def downtime(s):
 import social_life
 before={'day':s['dayNumber'],'phase':s['currentDayPhase']}
 tracked(s,{'type':'assign-founder','assignment':'rest'})
 choices=[r for r in social_life.view(s)['scenes'] if r['available'] and not r['deferred'] and not r['memory']]
 scene=choices[0]['id'] if choices else None
 if scene:tracked(s,{'type':'share-social-conversation','sceneId':scene,'choice':'warm'})
 while s['currentDayPhase']!='evening':tracked(s,{'type':'advance'})
 people=[w for w in g.household_members(s) if g.character_at_castle(s,w)]
 tracked(s,{'type':'evening-rest','choice':'quiet','participants':people});tracked(s,{'type':'advance'})
 assert all(s['overnightRest'].get(w)==s['dayNumber'] for w in people)
 assert not s['testing']['used']
 current['downtime'].append({'afterChapter':chapter,'start':before,'restedMorning':s['dayNumber'],'participants':people,'conversation':scene})

def wrapped(s,a):
 global current,chapter
 if Path(inspect.currentframe().f_back.f_code.co_filename).parent.name!='tests':return original(s,a)
 if current is None or (s['dayNumber']==1 and a['type']=='food-policy'):
  current={'chapters':{str(i):{'actions':0,'advances':0,'copyingAdvances':0,'restAdvances':0,'overnights':0,'maxConsecutiveAdvances':0,'maxActionsWithoutAdvance':0} for i in range(1,8)},'streak':0,'clicks':0,'downtime':[]};routes.append(current);chapter=1
 if with_downtime and starts.get(a['type'],0)>chapter:downtime(s)
 return tracked(s,a)
g.apply_action=wrapped
suite=unittest.defaultTestLoader.loadTestsFromTestCase(flow.SevenChapterFlowTests);result=unittest.TextTestRunner().run(suite)
for r in routes:r.pop('streak');r.pop('clicks')
output=next((x for x in sys.argv[1:] if not x.startswith('--')),'pacing-report.json')
Path(output).write_text(json.dumps({'passed':result.wasSuccessful(),'routes':routes,'withDowntime':with_downtime,'note':'Deterministic route actions and simulated phases, not measured human playtime. Downtime mode chooses an available conversation and an evening at home between chapters. Reading time is not measured.'},indent=2))
if not result.wasSuccessful():sys.exit(1)
