from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign,apply_action,public_state,RuleError,learn_for_character
from server import GameStore

class DelegationTests(unittest.TestCase):
    def setUp(self):
        self.state=new_campaign()
        for who in ('founder','mira'):learn_for_character(self.state,who,'steady-hearth-wards')
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def order(self,maker='mira',count=2):
        self.act('create-work-order',recipeId='warming-lantern',crafterId=maker,materials=['sun-amber','binding-thread'],requestedCount=count)
        return self.state['workOrders'][-1]
    def advance(self,count=1):
        for _ in range(count):self.act('advance')
    def test_reserved_budget_and_stock_protection_exact_cost_refund(self):
        order=self.order();before=self.state['sharedFunds']
        self.state['materialReserveTargets']['sun-amber']=2;self.state['materialReserveTargets']['binding-thread']=2
        self.act('delegate-work-order',orderId=order['id'],budgetCrowns=25)
        self.assertEqual(self.state['sharedFunds'],before-25);self.assertIsNone(self.state['craftingProject'])
        self.advance();self.assertEqual(order['delegation']['spentCrowns'],9)
        self.assertEqual(self.state['materialInventory']['sun-amber'],2);self.assertEqual(self.state['materialInventory']['binding-thread'],2)
        self.advance(3)
        self.assertEqual(order['completedCount'],2);self.assertEqual(order['delegation']['status'],'complete')
        self.assertEqual(order['delegation']['returnedCrowns'],7);self.assertEqual(self.state['sharedFunds'],before-18)
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],2)
        self.advance();self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],2)
        self.assertEqual(sum(self.state['personalFunds'].values()),0)
    def test_zero_budget_uses_only_unreserved_stock_and_then_waits(self):
        order=self.order(count=3);self.act('delegate-work-order',orderId=order['id'],budgetCrowns=0)
        self.advance(4);self.assertEqual(order['completedCount'],2)
        before=deepcopy(self.state);self.advance()
        self.assertIsNone(self.state['craftingProject']);self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        view=public_state(self.state)['workOrderViews'][0]['delegationView']
        self.assertEqual(view['nextPurchaseCostCrowns'],9);self.assertIn('budget',' '.join(view['blockers']))
        self.act('add-delegation-budget',orderId=order['id'],budgetCrowns=9);self.advance(2)
        self.assertEqual(order['completedCount'],3);self.assertEqual(order['delegation']['spentCrowns'],9)
    def test_resident_works_under_agreement_while_scholar_travels(self):
        order=self.order(count=1);self.act('delegate-work-order',orderId=order['id'],budgetCrowns=0)
        self.act('start-expedition');self.advance();self.assertEqual(self.state['craftingProject']['completedWorkPhases'],1)
        self.reject('pause-delegation',orderId=order['id'])
        self.act('choose-expedition-approach',approach='salvage');self.advance()
        self.assertEqual(order['completedCount'],1);self.assertIsNotNone(self.state['expedition'])
    def test_pause_and_assignment_changes_never_take_work_back_automatically(self):
        order=self.order();self.act('delegate-work-order',orderId=order['id'],budgetCrowns=5);self.advance()
        self.act('pause-delegation',orderId=order['id']);self.advance()
        self.assertEqual(self.state['craftingProject']['completedWorkPhases'],1)
        self.act('resume-delegation',orderId=order['id']);self.advance();self.assertEqual(order['completedCount'],1)
        self.act('assign-resident',assignment='rest');self.advance();self.assertIsNone(self.state['craftingProject'])
        self.assertIn('another assignment',' '.join(public_state(self.state)['workOrderViews'][0]['delegationView']['blockers']))
        self.act('resume-delegation',orderId=order['id']);self.advance(2);self.assertEqual(order['completedCount'],2)
    def test_revocation_refunds_once_and_keeps_committed_copy(self):
        order=self.order();self.act('delegate-work-order',orderId=order['id'],budgetCrowns=12);self.advance()
        self.act('revoke-delegation',orderId=order['id']);self.assertEqual(self.state['sharedFunds'],80)
        self.assertIsNotNone(self.state['craftingProject']);self.reject('revoke-delegation',orderId=order['id'])
        self.advance(3);self.assertEqual(order['completedCount'],1)
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
        self.assertIsNone(self.state['craftingProject'])
    def test_one_open_agreement_and_invalid_budgets_are_atomic(self):
        order=self.order();second=self.order('founder')
        for budget in (-1,1001,True,1.5,'10',81):self.reject('delegate-work-order',orderId=order['id'],budgetCrowns=budget)
        self.act('delegate-work-order',orderId=order['id'],budgetCrowns=10)
        self.reject('delegate-work-order',orderId=second['id'],budgetCrowns=0)
        self.reject('remove-work-order',orderId=order['id']);self.reject('start-work-order',orderId=order['id'])
        self.reject('buy-work-order-materials',orderId=order['id'])
        self.act('pause-delegation',orderId=order['id']);self.reject('remove-work-order',orderId=order['id'])
        self.act('revoke-delegation',orderId=order['id']);self.act('remove-work-order',orderId=order['id'])
        self.act('delegate-work-order',orderId=second['id'],budgetCrowns=0)
    def test_fast_maker_cannot_complete_two_copies_in_one_phase(self):
        order=self.order();self.state['characterSkills']['mira']['artifice']=2
        self.act('delegate-work-order',orderId=order['id'],budgetCrowns=0);self.advance()
        self.assertEqual(order['completedCount'],1);self.assertIsNone(self.state['craftingProject'])
        self.advance();self.assertEqual(order['completedCount'],2)
    def test_another_artifact_blocks_and_its_assignment_is_not_hijacked(self):
        order=self.order();self.act('delegate-work-order',orderId=order['id'],budgetCrowns=0)
        self.act('start-crafting',recipeId='warming-lantern',crafterId='mira',materials=['sun-amber','binding-thread'])
        self.act('pause-delegation',orderId=order['id'])
        self.assertEqual(self.state['residentAssignment'],'crafting')
        self.reject('resume-delegation',orderId=order['id']);self.advance(2)
        self.assertEqual(order['completedCount'],0)
        self.act('resume-delegation',orderId=order['id']);self.advance(2);self.assertEqual(order['completedCount'],1)
    def test_nonmember_and_personal_knowledge_constraints(self):
        self.reject('create-work-order',recipeId='warming-lantern',crafterId='tamsin',materials=['sun-amber','binding-thread'],requestedCount=1)
        order=self.order();self.state['residentKnownPrinciples'].remove('steady-hearth-wards')
        self.reject('delegate-work-order',orderId=order['id'],budgetCrowns=0)
    def test_schema_thirteen_migration_and_retry_keep_agreement_money(self):
        order=self.order();old=deepcopy(self.state);old['schemaVersion']=13
        old['workOrders'][0].pop('delegation')
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=?',(json.dumps(old),))
            store=GameStore(directory)
            self.assertTrue((Path(directory)/f"campaign-before-schema-13-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            self.assertIsNone(store.read()['workOrders'][0]['delegation']);self.assertEqual(store.read()['sharedFunds'],80)
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'delegate-work-order','orderId':order['id'],'budgetCrowns':10}}
            result=store.action(payload);self.assertEqual(store.action(payload),result)
            restored=GameStore(directory).read();self.assertEqual(restored['sharedFunds'],70)
            self.assertEqual(restored['workOrders'][0]['delegation']['remainingBudgetCrowns'],10)
