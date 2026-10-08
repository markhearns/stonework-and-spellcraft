"""Two earned-resource routes through all seven chapters, reloading after actions."""
from copy import deepcopy
import json,os
from pathlib import Path
import test_chapter_five_flow as six
import game as g,first_patrol as p,headquarters as h,arrivals,field_magic
class SevenChapterFlowTests(six.FiveChapterFlowTests):
 def journey(self,site,party,fast):
  self.act('start-expedition',siteId=site,companionIds=party);self.advance();self.act('choose-expedition-approach',approach='survey')
  for _ in range(25):
   if self.s['expedition']['stage']=='ready-to-return':break
   if self.s['expedition']['stage']=='encounter-choice':
    choices=p.encounter_view(self.s)['choices'];method=next((k for k in ('breath','keeper','gear') if k in choices and not choices[k]['blockers']),'patient') if fast else 'patient';self.act('choose-encounter-method',methodId=method)
   self.advance()
  self.act('return-expedition');self.advance()
 def play_seven(self,company):
  start=deepcopy(self.s);self.act('patrol-start');self.journey(p.TRAIL,[],company=='meet');self.assertIn('introduced-rhess',self.s['summoningContacts'])
  cid='introduced-rhess'
  for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId=cid,topic=topic)
  rooms=arrivals.eligible_rooms(self.s,self.s['people']['rhess'])
  if not rooms:
   # Existing spare room construction, funded through commissions.
   self.money(34);self.act('hq-bedroom',roomId='guard-dormitory');self.advance(4);rooms=arrivals.eligible_rooms(self.s,self.s['people']['rhess'])
  self.act('summoning-invite',contactId=cid,roomId=rooms[0]);self.advance();self.act('summoning-ask-stay',contactId=cid);self.act('summoning-household-decision',contactId=cid,decision='invite-to-stay')
  self.act('agree-household-role',characterId='rhess',role='fieldwork',enabled=True,willingnessReviewed=True);self.act('gear-review')
  self.money(32);self.act('hq-build',roomId='watchtower');self.advance(4);self.assertTrue(h.ready(self.s,'watchtower'))
  for w in ('founder','rhess'):self.act('assign-character',characterId=w,assignment='rest')
  self.act('patrol-drill');self.advance(2);self.act('patrol-plan',choice='repair' if company=='solo' else 'retire')
  for _ in range(3):
   if not p.departure_blockers(self.s,p.WARD):break
   self.advance()
  self.assertEqual(p.departure_blockers(self.s,p.WARD),[])
  self.act('gear-party-loadout',participants=['founder','rhess'],mode='expedition');self.journey(p.WARD,['rhess'],company=='meet')
  for _ in range(6):
   if not p.closing_blockers(self.s):break
   self.advance()
  self.act('patrol-conclude');self.assertTrue(p.saved(self.s)['completedOn']);self.assertFalse(self.s['testing']['used'])
  before=deepcopy(self.s);v=g.public_state(self.s);self.assertEqual(before,self.s);self.assertIn('rhess',v['characterCatalog']);self.assertIn('overview-rhess',v['originalAssets'])
  if not os.environ.get('STONEWORK_AUDIT_DIR'):return
  out=Path(os.environ['STONEWORK_AUDIT_DIR']);out.mkdir(parents=True,exist_ok=True);(out/('earned-seven-'+company+'.json')).write_text(json.dumps(self.s));(out/('chapter-seven-'+company+'.json')).write_text(json.dumps({'startDay':start['dayNumber'],'startPhase':start['currentDayPhase'],'endDay':self.s['dayNumber'],'endPhase':self.s['currentDayPhase'],'breathUsed':p.saved(self.s)['breathUsed'],'outcomes':self.s['patrolJourneys']},indent=2))
