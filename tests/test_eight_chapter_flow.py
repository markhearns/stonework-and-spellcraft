"""Earned Chapter 1–8 routes, no cheats, serialized reload after every action."""
from copy import deepcopy
import json
from pathlib import Path
import os
import test_seven_chapter_flow as seven
import field_patrols as p
import game as g

class EightChapterFlowTests(seven.SevenChapterFlowTests):
 def play_seven(self,company):
  super().play_seven(company)
  start={'day':self.s['dayNumber'],'phase':self.s['currentDayPhase'],'funds':self.s['sharedFunds']};count=0
  self.act('trial-start');party=['founder','rhess'];plan='scout' if company=='solo' else 'negotiate'
  for mission in p.MISSIONS:
   if mission!='scout':
    for _ in range(6):
     if not p.night_blockers(self.s):break
     self.advance();count+=1
    if mission=='escort':self.act('trial-plan',choice=plan)
   self.act('watch-depart',participants=party,missionId=mission)
   for _ in range(90):
    r=p.saved(self.s)['active']
    if not r:break
    if r['stage']=='decision':
     rows=[r for r in p.choices(self.s) if not r['blockers']]
     choice=next((r for r in rows if r['kind'] in ('peace','bypass')),None) or max((r for r in rows if r['kind']=='attack'),key=lambda r:2*r['preview']['damage']-r['preview']['injury']-8*sum(n==0 for n in r['preview']['healthAfter'].values()))
     self.act('watch-method',methodId=choice['id'])
    self.advance();count+=1
   self.assertIn(mission,p.chapter(self.s)['completed'])
  for _ in range(7):
   if not p.closing_blockers(self.s):break
   self.advance();count+=1
  self.act('trial-conclude',choice='signals' if company=='solo' else 'supplies')
  self.assertTrue(p.chapter(self.s)['completedOn']);self.assertFalse(self.s['testing']['used']);self.assertLess(self.s['provisions']['unfedDays'],3)
  self.assertGreaterEqual(count,12)
  old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
  report={'route':company,'plan':plan,'start':start,'end':{'day':self.s['dayNumber'],'phase':self.s['currentDayPhase'],'funds':self.s['sharedFunds']},'chapter8Advances':count,'reports':p.saved(self.s)['reports'],'cheats':self.s['testing']['used']}
  if os.environ.get('STONEWORK_EIGHT_AUDIT_DIR'):
   out=Path(os.environ['STONEWORK_EIGHT_AUDIT_DIR']);out.mkdir(parents=True,exist_ok=True);(out/('chapter-eight-'+company+'.json')).write_text(json.dumps(report,indent=2))
