"""Run from the project root to replay all six Chapter 2 orders, without cheats."""
import sys,json,itertools
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,'.');sys.path.insert(0,'tests')
import test_house_shape as test
import room_to_grow as grow
import house_shape as shape
import game as g

test.HouseShapeTests.setUpClass();reports=[]
for i,order in enumerate(itertools.permutations(shape.PATHS)):
 t=test.HouseShapeTests();t.setUp();start=t.s['dayNumber'];counts=[]
 for key in order:
  design=list(shape.PATHS[key]['designs'])[i%2]
  t.run_chapter(key,design)
  counts.append(shape.view(t.s)['completedCount'])
  assert not grow.available(t.s)
 t.act('shape-conclude');assert grow.available(t.s)
 reports.append({'order':order,'completedCounts':counts,'chapter3Available':grow.available(t.s),'endDay':t.s['dayNumber'],'funds':t.s['sharedFunds'],'cheatsUsed':t.s['testing']['used']})
 print(order,'passed',flush=True)
Path('docs/CHAPTER_FLOW_V077.json').write_text(json.dumps(reports,indent=2))
