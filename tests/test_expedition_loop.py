from copy import deepcopy
import unittest
import game as g
import expedition_loop as loop
import field_magic as f
import test_magic_overhaul as magic

class ExpeditionLoopTests(unittest.TestCase):
 def setUp(self):self.s=g.new_campaign()
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def return_home(self):self.act('return-expedition');self.act('advance');return self.s['lastExpeditionReport']['logbook']
 def test_projection_is_readonly(self):
  before=deepcopy(self.s);p=g.public_state(self.s)
  self.assertIn('founder',p['expeditionPreparation']['people']);self.assertEqual(before,self.s)
 def test_normal_survey_records_only_new_knowledge(self):
  self.act('start-expedition');self.act('advance');self.act('choose-expedition-approach',approach='survey');self.act('advance');self.act('advance')
  log=self.return_home();self.assertEqual(log['phases'],4);self.assertTrue(log['completedLead']);self.assertEqual(log['committed'],{})
  self.assertEqual(log['party'][0]['newPrinciples'],['water-guidance']);self.assertEqual(log['party'][0]['assignmentNow'],'rest')
  p=g.public_state(self.s);self.assertTrue(any(r['target'].get('recipeId')=='watering-charm' for r in p['expeditionFollowups']))
 def test_failed_action_does_not_change_receipt(self):
  self.act('start-expedition');self.act('advance');before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act('advance')
  self.assertEqual(self.s,before)
 def test_old_inflight_save_has_honest_partial_receipt(self):
  self.act('start-expedition');self.s['expedition'].pop('logbook');self.act('advance');log=self.return_home()
  self.assertFalse(log['completeCoverage']);self.assertIsNone(log['party'][0]['departureVitality']);self.assertFalse(log['completedLead'])
 def test_unfinished_aqueduct_work_refunds_exact_committed_inputs(self):
  t=magic.MagicTests();t.setUp();t.at('fire');self.s=t.s
  self.act('field-method',method='mundane');pending=deepcopy(f.progress(self.s)['pending']);log=self.return_home()
  self.assertEqual(log['refunded'],pending['inputs']);self.assertEqual(log['crownsRefunded'],pending.get('crowns',0))
  self.assertEqual(log['committed'],pending['inputs']);self.assertEqual(log['outcomes'],[])
 def test_resumed_visit_excludes_previous_outcomes(self):
  t=magic.MagicTests();t.setUp();t.at('fire');self.s=t.s
  self.act('field-method',method='mundane')
  while self.s['expedition']['stage']=='working':self.act('advance')
  first=self.return_home();self.assertEqual(len(first['outcomes']),1)
  self.act('start-expedition',siteId=f.SITE);self.act('advance');second=self.return_home()
  self.assertEqual(second['outcomes'],[]);self.assertEqual(second['committed'],{})
 def test_castle_income_is_not_an_expedition_expense(self):
  self.act('start-expedition');self.act('advance');log=self.return_home()
  self.assertEqual(log['crownsCommitted'],0);self.assertEqual(log['committed'],{})

 def test_duplicate_request_does_not_count_another_phase(self):
  import tempfile,uuid
  from server import GameStore
  with tempfile.TemporaryDirectory() as directory:
   store=GameStore(directory)
   def request(kind):return {'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind}}
   store.action(request('start-expedition'));advance=request('advance');first=store.action(advance);second=store.action(advance)
   self.assertEqual(first,second);self.assertEqual(store.read()['expedition']['logbook']['phases'],1)
 def test_conversations_use_destination_and_preserve_beacon_keys(self):
  import companion_participation as company
  company.returned(self.s,['founder','mira'],[],True,site_id='north-watch-road')
  event=company.saved(self.s)['events']['journey:north-watch-road:mira:complete']
  self.assertEqual(event['siteName'],g.EXPEDITION_SITES['north-watch-road']['name'])
  self.assertNotIn('Stormwatch',str(company.dialogue(self.s,event)))
  company.returned(self.s,['founder','mira'],[],True,site_id='stormwatch-beacon')
  self.assertIn('beacon:mira:complete',company.saved(self.s)['events'])
