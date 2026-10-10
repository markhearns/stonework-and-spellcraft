"""Chapter nine: answer the foundation junction's survey question with recorded evidence."""
from copy import deepcopy
VIEW='surveyRooms'
ASSIGNMENT='survey-rooms'
EMPTY={'started':False,'completed':{},'job':None,'conclusion':None,'completedOn':None}
STEPS={
 'route':dict(name='Follow the marked service passage',phases=2,needs=[],purpose='Trace the labelled line from the foundation junction to the old survey room.',text='The line ends at a brass reference plate bolted into the bedrock. Separate wires connect it to the ordinary hearth supply and to a measuring lens. The intimate ritual circuit is a third, optional connection. None of these lines opens a crossing by itself.'),
 'ledger':dict(name='Compare the survey register',phases=2,needs=['route'],purpose='Match the plate’s numbered settings with the surviving entries and the castle’s founding record.',text='The register pairs each departure setting with a return setting and a signed closure check. The names match the travelling enchanters in the archive. Their final entries record completed work and separate onward journeys: they closed the survey together before leaving the refuge.'),
 'reference':dict(name='Check why the reference stayed here',phases=2,needs=['ledger'],purpose='Compare the plate with the wall marks while the optional ritual connection is isolated.',text='With the optional connection isolated, the plate and wall marks still agree. The surveyors chose this bedrock because it moved less than the road and river markers, and the ordinary wards kept their instrument at a steady temperature. The household supplied a dependable place to return to. Its relationships could sharpen an auxiliary reading, but no one had to provide intimacy to keep a route safe.'),
 'closure':dict(name='Verify the closed survey settings',phases=1,needs=['reference'],purpose='Inspect the disconnected crossing controls without opening a passage.',text='The return settings are intact, but their activation links were deliberately removed and labelled after the final survey. There is no open crossing under the castle. You record the missing links and the closure checks so a future investigator can tell a dormant instrument from a working passage. Reopening one would require a separate investigation and an explicit decision.'),
}
CLOSINGS={
 'preserve':('Keep the original evidence together','You place the traced connections, measured settings and closure checks beside the original register. Later repairs can now be compared with this record instead of relying on a remembered story.'),
 'teach':('Write an explanation a new keeper can use','You write three clear instructions: maintain the ordinary supply, leave the activation links disconnected, and check the return setting before considering any new survey. You put the evidence behind each instruction in the same folder.'),
 'questions':('Record the answer and the remaining limits','You separate what the tests established from what they did not. The castle was a stable survey reference and a place to return to. The old settings record destinations; they do not prove those destinations remain safe today.'),
}
def saved(s):return s.get('surveyRooms',EMPTY)
def initialize(s):s.setdefault('surveyRooms',deepcopy(EMPTY))
def unlocked(s):return bool(s.get('firstRealTest',{}).get('completedOn'))
def blockers(s,key=None):
 import game as g,foundation_chamber as f
 b=[];r=saved(s)
 if not unlocked(s):b.append('Complete Chapter 8: The First Real Test.')
 if not f.saved(s)['concludedOn']:b.append('Restore the foundation chamber and record its findings. The private ritual is optional.')
 if 'founding-record' not in s['castleMystery']['discoveries']:b.append('Complete “Put the evidence together” in Castle history. Existing findings count.')
 if not g.character_at_castle(s,'founder'):b.append('Return your scholar home.')
 if key:
  if not r['started']:b.append('Open the survey investigation first.')
  if r['job']:b.append('Finish or cancel the current survey task.')
  if key in r['completed']:b.append('This task is already complete.')
  b.extend('Complete '+STEPS[k]['name']+' first.' for k in STEPS[key]['needs'] if k not in r['completed'])
 return b

def apply(s,a):
 import game as g
 kind=a.get('type','')
 if not kind.startswith('survey-room-'):return False
 initialize(s);r=saved(s)
 g.require(g.character_at_castle(s,'founder'),'Return home before changing the survey investigation.')
 if kind in ('survey-room-resume','survey-room-cancel'):
  g.require(r['job'],'There is no unfinished survey task.')
  if kind=='survey-room-resume':g.set_character_assignment(s,'founder',ASSIGNMENT)
  else:
   r['job']=None
   if g.character_assignment(s,'founder')==ASSIGNMENT:g.set_character_assignment(s,'founder','rest')
  return True
 b=blockers(s);g.require(not b,' '.join(b))
 if kind=='survey-room-start':
  g.require(not r['started'],'The survey investigation is already open.');r['started']=True
  g.add_journal(s,'The Survey Rooms: the foundation label points to a specific question. Why did the surveyors need a stable reference beneath this castle? You bring the recorded founding evidence to the lower passage.')
 elif kind=='survey-room-task':
  key=a.get('stepId');g.require(isinstance(key,str) and key in STEPS,'Choose a listed survey task.')
  b=blockers(s,key);g.require(not b,' '.join(b));r['job']={'stepId':key,'done':0,'phases':STEPS[key]['phases']};g.set_character_assignment(s,'founder',ASSIGNMENT)
 elif kind=='survey-room-conclude':
  choice=a.get('choice');g.require(isinstance(choice,str) and choice in CLOSINGS,'Choose how to record the findings.')
  g.require(r['started'] and len(r['completed'])==len(STEPS) and not r['completedOn'],'Finish the four survey tasks before concluding once.')
  r['conclusion']={'choice':choice,'title':CLOSINGS[choice][0],'text':CLOSINGS[choice][1]};r['completedOn']={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  g.award_advancement(s,'founder','survey-rooms',2,'Established the purpose and current state of the old survey room')
  g.add_journal(s,'The Survey Rooms: '+CLOSINGS[choice][1]+' Your scholar gains 2 advancement points.')
 else:raise g.RuleError('Choose a listed survey-room action.')
 return True

def working(s):
 import game as g
 return bool(saved(s)['job'] and g.character_at_castle(s,'founder') and g.character_assignment(s,'founder')==ASSIGNMENT)
def resolve(s,summary):
 import game as g
 if not working(s):return
 r=saved(s);p=r['job'];p['done']+=1;d=STEPS[p['stepId']]
 summary.append(d['name']+': '+str(p['done'])+'/'+str(p['phases'])+' phases.')
 if p['done']==p['phases']:
  r['completed'][p['stepId']]={'title':d['name'],'text':d['text'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
  r['job']=None;g.set_character_assignment(s,'founder','rest');summary.append(d['text'])
def forecast(s):
 p=saved(s)['job']
 return [STEPS[p['stepId']]['name']+(': +1 investigation phase.' if working(s) else ': paused; progress kept.')] if p else []
def view(s):
 r=saved(s)
 return {**deepcopy(r),'unlocked':unlocked(s),'blockers':blockers(s),'working':working(s),'steps':[{'id':k,'name':d['name'],'purpose':d['purpose'],'phases':d['phases'],'blockers':blockers(s,k),'memory':deepcopy(r['completed'].get(k))} for k,d in STEPS.items()],'choices':[{'id':k,'label':v[0]} for k,v in CLOSINGS.items()]}
