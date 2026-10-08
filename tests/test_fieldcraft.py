from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import equipment
import game as g
import household_content as h
import spell_guidance
from server import GameStore

class FieldcraftTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['sharedFunds']=200
  self.s['residentAssignment']='rest'
  for key in self.s['materialInventory']:self.s['materialInventory'][key]=10
 def act(self,kind,**kw):return g.apply_action(self.s,{'type':kind,**kw})
 def advance(self,n=1):
  for _ in range(n):self.act('advance')
 def own(self,who='founder'):
  self.s['craftedArtifacts']['scholars-folio']=1
  self.act('claim-working-tool',ownerId=who,toolId='scholars-folio')
  return next(reversed(self.s['personalEquipment']))
 def start(self,who,key):
  self.act('upgrade-working-tool',ownerId=who,itemId=key,materials=['porous-clay','binding-thread'])
 def test_discovery_research_craft_inscribe_prepare_and_actual_research(self):
  self.act('start-research');self.advance(3)
  g.learn_for_character(self.s,'founder','reference-binding')
  # Even pre-existing knowledge cannot substitute for the returned field record.
  g.learn_for_character(self.s,'founder','water-guidance')
  with self.assertRaises(g.RuleError):self.act('focus-research',researchId='field-calibration',leaderId='founder')
  self.act('start-expedition');self.advance();self.act('choose-expedition-approach',approach='survey');self.advance(2)
  self.assertNotIn('survey',self.s['waterworksDiscoveries'])
  self.act('return-expedition');self.advance()
  self.act('focus-research',researchId='field-calibration',leaderId='founder');self.advance(4)
  self.assertIn('field-calibration',g.character_principles(self.s,'founder'))
  self.assertNotIn('field-calibration',g.character_principles(self.s,'mira'))
  self.act('start-crafting',recipeId='scholars-folio',materials=['porous-clay','binding-thread']);self.advance(3)
  self.act('claim-working-tool',ownerId='founder',toolId='scholars-folio');key=next(iter(self.s['personalEquipment']))
  self.act('rename-working-tool',ownerId='founder',itemId=key,name='Brook notes')
  self.start('founder',key);self.advance(2)
  self.assertEqual(self.s['personalEquipment'][key]['name'],'Brook notes')
  self.act('prepare-working-tool',ownerId='founder',itemId=key)
  self.act('focus-research',researchId='root-rhythms',leaderId='founder');self.advance()
  self.assertEqual(self.s['researchProjects']['root-rhythms']['completedWorkPhases'],3)
  with self.assertRaises(g.RuleError):self.start('founder',key)
 def test_pause_cancel_exact_refund_restart_and_no_double_work(self):
  key=self.own();g.learn_for_character(self.s,'founder','field-calibration');before=deepcopy(self.s)
  self.start('founder',key);self.advance();self.act('assign-founder',assignment='rest');self.advance(2)
  self.assertEqual(self.s['toolUpgradeProjects']['founder']['completedWorkPhases'],1)
  with self.assertRaises(g.RuleError):self.act('start-focus-inscription',characterId='founder',inscriptionId='scholarly-thread',materials=['porous-clay','binding-thread'])
  with self.assertRaises(g.RuleError):self.act('transfer-working-tool',ownerId='founder',itemId=key,recipientId='mira',ownersAgreed=True)
  self.act('cancel-tool-upgrade',ownerId='founder')
  self.assertEqual(self.s['sharedFunds'],before['sharedFunds']);self.assertEqual(self.s['materialInventory'],before['materialInventory'])
  with self.assertRaises(g.RuleError):self.act('cancel-tool-upgrade',ownerId='founder')
  self.start('founder',key);self.advance(2);self.assertIsNotNone(self.s['personalEquipment'][key]['inscription'])
 def test_reserves_knowledge_and_component_counts_are_atomic(self):
  key=self.own();before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.start('founder',key)
  self.assertEqual(self.s,before)
  g.learn_for_character(self.s,'founder','field-calibration')
  self.s['materialReserveTargets']['porous-clay']=self.s['materialInventory']['porous-clay'];before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.start('founder',key)
  self.assertEqual(self.s,before)
  self.s['materialReserveTargets']['porous-clay']=0
  with self.assertRaises(g.RuleError):self.act('upgrade-working-tool',ownerId='founder',itemId=key,materials=['binding-thread','porous-clay'])
 def test_resident_study_invitation_defer_memory_and_no_rewards(self):
  key=self.own('mira');self.s['archivePrinciples'].append('field-calibration')
  self.act('study-principle',characterId='mira',principleId='field-calibration');self.advance(2)
  self.start('mira',key);self.advance(2)
  self.assertEqual(self.s['toolMoments'][key]['status'],'waiting');self.assertEqual(h.context(self.s,'mira'),[])
  self.act('defer-tool-moment',ownerId='mira',itemId=key);self.advance(4)
  self.act('restore-tool-moment',ownerId='mira',itemId=key);before=deepcopy(self.s)
  self.act('join-tool-moment',ownerId='mira',itemId=key,choice='playful')
  for field in ['sharedFunds','materialInventory','resonancePoints','dayNumber','currentDayPhase','characterDevelopment']:self.assertEqual(self.s[field],before[field])
  self.assertEqual(len(h.context(self.s,'mira')),1);self.assertEqual(h.context(self.s,'tamsin'),[])
  with self.assertRaises(g.RuleError):self.act('join-tool-moment',ownerId='mira',itemId=key,choice='work')
 def test_sqlite_cancel_retry_and_old_save_migration(self):
  key=self.own();g.learn_for_character(self.s,'founder','field-calibration');self.start('founder',key)
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d)
   with store.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(self.s),))
   payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.s['revision'],'action':{'type':'cancel-tool-upgrade','ownerId':'founder'}}
   saved=store.action(payload);self.assertEqual(store.action(payload),saved);self.assertEqual(GameStore(d).read(),saved)
  old=g.new_campaign();old['schemaVersion']=34
  old.pop('toolUpgradeProjects');old.pop('toolMoments');old['researchProjects'].pop('field-calibration');g.migrate_state(old)
  self.assertEqual(old['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertEqual(old['toolUpgradeProjects'],{});self.assertEqual(old['dayNumber'],1)
 def test_away_pauses_owner_but_not_resident_and_keeps_identity_after_transfer(self):
  key=self.own();g.learn_for_character(self.s,'founder','field-calibration');self.start('founder',key)
  self.act('start-expedition');self.advance();self.assertEqual(self.s['toolUpgradeProjects']['founder']['completedWorkPhases'],0)
  self.act('return-expedition');self.advance();self.act('resume-tool-upgrade',ownerId='founder');self.advance(2)
  self.act('transfer-working-tool',ownerId='founder',itemId=key,recipientId='mira',ownersAgreed=True)
  self.act('prepare-working-tool',ownerId='mira',itemId=key)
  self.assertEqual(equipment.bonus(self.s,'mira','archive-focus')[0]['amount'],2)
  self.assertEqual(self.s['personalEquipment'][key]['inscription']['madeBy'],'founder')

class SpellGuidanceTests(unittest.TestCase):
 def test_guidance_is_read_only_and_duplicate_components_count(self):
  s=g.new_campaign();s['materialInventory']={k:0 for k in g.MATERIALS};s['materialInventory']['moon-glass']=1;before=deepcopy(s)
  guide=spell_guidance.view(s,'founder');self.assertEqual(s,before)
  self.assertEqual(guide['luminous-copy']['availableCombinations'],[])
  s['materialInventory']['moon-glass']=2;self.assertIn(['moon-glass','moon-glass'],spell_guidance.view(s,'founder')['luminous-copy']['availableCombinations'])
  s['materialReserveTargets']['moon-glass']=1;self.assertEqual(spell_guidance.view(s,'founder')['luminous-copy']['availableCombinations'],[])
 def test_known_principle_does_not_hide_facility_funds_or_existing_work(self):
  s=g.new_campaign();g.learn_for_character(s,'founder','steady-growth');s['sharedFunds']=0
  s['materialInventory']['silver-ivy']=3
  r=spell_guidance.view(s,'founder')['root-song'];self.assertTrue(r['principleKnown'])
  self.assertTrue(any('Restore' in t for t in r['testingBlockers']));self.assertTrue(any('crowns' in t for t in r['testingBlockers']))
  self.assertEqual(r['effect'],g.SPELL_FORMS['root-song']['effect'])
