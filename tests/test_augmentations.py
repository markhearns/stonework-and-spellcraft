from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
from game import new_campaign,apply_action,RuleError,learn_for_character,spell_preparation_capacity,augmentation_view
from server import GameStore

class AugmentationTests(unittest.TestCase):
    def setUp(self):
        self.state=new_campaign();learn_for_character(self.state,'founder','gentle-refraction')
        self.state['materialInventory']['moon-glass']=3;self.state['materialInventory']['binding-thread']=3
    def act(self,kind,who='founder'):return apply_action(self.state,{'type':kind,'characterId':who})
    def advance(self,n=1):
        for _ in range(n):apply_action(self.state,{'type':'advance'})
    def test_explicit_cost_two_phases_and_personal_capacity_without_other_rewards(self):
        before=deepcopy(self.state);self.act('begin-augmentation')
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds']-10)
        self.assertEqual(self.state['materialInventory']['moon-glass'],2)
        self.advance();self.assertEqual(spell_preparation_capacity(self.state,'founder'),2)
        self.advance();self.assertEqual(spell_preparation_capacity(self.state,'founder'),3)
        self.assertEqual(spell_preparation_capacity(self.state,'mira'),2)
        for key in ('resonancePoints','relationshipDescription','characterDevelopment','preparedSpells'):self.assertEqual(before[key],self.state[key])
        with self.assertRaises(RuleError):self.act('begin-augmentation')
    def test_protected_materials_and_personal_knowledge_required_atomically(self):
        self.state['materialReserveTargets']['moon-glass']=3;before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('begin-augmentation')
        self.assertEqual(before,self.state)
        self.state['materialReserveTargets']['moon-glass']=0
        self.state['founderKnownPrinciples'].remove('gentle-refraction');before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('begin-augmentation')
        self.assertEqual(before,self.state)
    def test_pause_cancel_refunds_exactly_once_and_resume_uses_primary_assignment(self):
        before=deepcopy(self.state);self.act('begin-augmentation');self.advance()
        apply_action(self.state,{'type':'assign-founder','assignment':'rest'});self.advance()
        self.assertEqual(self.state['personalAugmentations']['founder']['project']['completedWorkPhases'],1)
        self.act('cancel-augmentation')
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds']);self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        with self.assertRaises(RuleError):self.act('cancel-augmentation')
        self.act('begin-augmentation');self.act('resume-augmentation');self.advance(2)
        self.assertTrue(self.state['personalAugmentations']['founder']['active'])
    def test_reversal_waits_for_excess_preparation_never_silently_discards_spells(self):
        self.act('begin-augmentation');self.advance(2)
        self.state['preparedSpells']['founder']=['one','two','three']
        self.act('reverse-augmentation');self.advance()
        self.assertTrue(self.state['personalAugmentations']['founder']['active'])
        self.assertEqual(self.state['personalAugmentations']['founder']['project']['completedWorkPhases'],0)
        self.assertEqual(self.state['preparedSpells']['founder'],['one','two','three'])
        self.assertIn('Put aside',augmentation_view(self.state,'founder')['workBlockers'][0])
        self.state['preparedSpells']['founder'].pop();self.advance()
        self.assertFalse(self.state['personalAugmentations']['founder']['active'])
        self.assertEqual(self.state['preparedSpells']['founder'],['one','two'])
        self.assertEqual(spell_preparation_capacity(self.state,'founder'),2)
    def test_reversal_cancellation_keeps_blessing_and_existing_ritual_bonus_stacks(self):
        self.state['spellRitual']['status']='complete'
        self.act('begin-augmentation');self.advance(2);self.assertEqual(spell_preparation_capacity(self.state,'founder'),4)
        money=self.state['sharedFunds'];self.act('reverse-augmentation');self.act('cancel-augmentation')
        self.assertTrue(self.state['personalAugmentations']['founder']['active']);self.assertEqual(self.state['sharedFunds'],money)
    def test_resident_offer_presence_and_independent_work_while_scholar_away(self):
        learn_for_character(self.state,'mira','gentle-refraction')
        with self.assertRaises(RuleError):self.act('begin-augmentation','mira')
        self.state['miraArchiveProject']['status']='complete';self.act('begin-augmentation','mira')
        apply_action(self.state,{'type':'start-expedition'});self.advance()
        apply_action(self.state,{'type':'choose-expedition-approach','approach':'survey'});self.advance()
        self.assertTrue(self.state['personalAugmentations']['mira']['active'])
        with self.assertRaises(RuleError):self.act('reverse-augmentation','mira')
    def test_persisted_funding_retry_and_reload_never_double_charge(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.state),))
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.state['revision'],'action':{'type':'begin-augmentation','characterId':'founder'}}
            after=store.action(payload);self.assertEqual(after,store.action(payload));self.assertEqual(after,GameStore(directory).read())
