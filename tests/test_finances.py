from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, distribute_expedition_wealth
from server import GameStore

class FinanceTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def plan(self,founder=2,mira=1,floor=20):
        self.act('set-allowance-plan',dailyCrowns={'founder':founder,'mira':mira},minimumTreasuryCrowns=floor)
    def test_migration_preserves_money_time_and_departed_party(self):
        self.act('start-expedition');old=deepcopy(self.state);old['schemaVersion']=12
        for key in ('personalFunds','personalPossessions','householdAllowancePlan','expeditionWealthPlan','moneyJournal'):old.pop(key)
        old['expedition'].pop('wealthPlan')
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=?',(json.dumps(old),))
            migrated=GameStore(directory).read()
            self.assertTrue((Path(directory)/f"campaign-before-schema-12-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            self.assertEqual(migrated['schemaVersion'],66)
            for key in ('sharedFunds','dayNumber','currentDayPhase','materialInventory'):self.assertEqual(migrated[key],old[key])
            self.assertEqual(migrated['expedition']['wealthPlan'],'shared')
            self.assertTrue(all(value==0 for value in migrated['personalFunds'].values()))
    def test_daily_payments_only_at_morning_and_conserve_total_money(self):
        before=self.state['sharedFunds'];self.plan();self.assertEqual(self.state['sharedFunds'],before)
        self.act('advance');self.assertEqual(self.state['personalFunds']['founder'],0)
        self.act('advance');self.assertEqual(self.state['personalFunds']['founder'],2)
        self.assertEqual(self.state['personalFunds']['mira'],1)
        self.assertEqual(self.state['sharedFunds']+sum(self.state['personalFunds'].values()),before)
        for _ in range(2):self.act('advance')
        self.assertEqual(self.state['personalFunds']['founder'],2)
        self.act('advance');self.assertEqual(self.state['personalFunds']['founder'],4)
    def test_insufficient_allowance_skips_everyone_without_arrears(self):
        self.plan();self.state['sharedFunds']=22;self.state['currentDayPhase']='evening'
        self.act('advance');self.assertEqual(self.state['sharedFunds'],22)
        self.assertEqual(sum(self.state['personalFunds'].values()),0)
        self.assertIn('skipped for everyone',' '.join(self.state['lastPhaseSummary']))
        self.state['sharedFunds']=30;self.state['currentDayPhase']='evening';self.act('advance')
        self.assertEqual(self.state['sharedFunds'],27)
        self.assertEqual(sum(self.state['personalFunds'].values()),3)
    def test_resolved_work_income_can_cover_same_morning_payment(self):
        self.plan();self.state['sharedFunds']=20;self.state['currentDayPhase']='evening'
        self.act('assign-founder',assignment='commissions');self.act('advance')
        self.assertEqual(sum(self.state['personalFunds'].values()),3)
        self.assertGreaterEqual(self.state['sharedFunds'],20)
    def test_plan_validation_is_atomic_and_rejects_nonmembers(self):
        for bad in (-1,11,True,1.5,'2'):
            self.reject('set-allowance-plan',dailyCrowns={'founder':bad,'mira':0},minimumTreasuryCrowns=20)
        self.reject('set-allowance-plan',dailyCrowns={'founder':1},minimumTreasuryCrowns=20)
        self.reject('set-allowance-plan',dailyCrowns={'founder':1,'mira':1,'tamsin':1},minimumTreasuryCrowns=20)
        self.reject('set-expedition-wealth-plan',planId={})
        self.reject('allocate-personal-funds',characterId='tamsin',crowns=1)
    def test_one_time_allocation_and_personal_purchase_never_touch_other_wallet(self):
        before=deepcopy(self.state)
        self.act('allocate-personal-funds',characterId='mira',crowns=4)
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds']-4)
        self.act('buy-personal-item',characterId='mira',itemId='poetry-book')
        self.assertEqual(self.state['personalFunds']['mira'],0)
        self.assertEqual(self.state['personalPossessions']['mira'],['poetry-book'])
        for key in ('wardrobe','characterDevelopment','relationshipDescription','resonancePoints','dayNumber','currentDayPhase','materialInventory'):
            self.assertEqual(self.state[key],before[key])
        self.reject('buy-personal-item',characterId='mira',itemId='poetry-book')
        self.reject('buy-personal-item',characterId='founder',itemId='poetry-book')
        self.reject('buy-personal-item',characterId='founder',itemId='scholar-journal')
        self.reject('allocate-personal-funds',characterId='founder',crowns=60)
    def test_personal_share_waits_for_completed_return_and_cannot_repeat(self):
        self.act('set-expedition-wealth-plan',planId='half-personal')
        self.act('start-expedition');self.act('advance')
        self.act('choose-expedition-approach',approach='salvage');self.act('advance')
        self.assertEqual(self.state['personalFunds']['founder'],0)
        self.act('return-expedition');self.act('advance')
        self.assertEqual(self.state['personalFunds']['founder'],4)
        self.assertEqual(self.state['sharedFunds'],84)
        self.act('start-expedition');self.act('advance');self.act('return-expedition');self.act('advance')
        self.assertEqual(self.state['personalFunds']['founder'],4)
    def test_party_share_is_equal_with_whole_crown_remainder_shared(self):
        self.state['miraArchiveProject']['status']='complete'
        self.act('set-expedition-wealth-plan',planId='quarter-personal')
        self.act('start-expedition',companionId='mira')
        before=self.state['sharedFunds'];line=distribute_expedition_wealth(self.state,14)
        self.assertEqual(self.state['personalFunds']['founder'],1);self.assertEqual(self.state['personalFunds']['mira'],1)
        self.assertEqual(self.state['sharedFunds'],before+12);self.assertIn('12 shared',line)
        self.reject('set-expedition-wealth-plan',planId='shared')
    def test_arrivals_get_zero_allowance_and_existing_wallets_remain_their_own(self):
        self.plan();self.state['additionalResidents']['tamsin']['status']='resident'
        self.state['bedroomAssignments']['tamsin']='bedchamber';self.state['currentDayPhase']='evening'
        self.act('advance');self.assertEqual(self.state['personalFunds']['tamsin'],0)
        self.assertEqual(self.state['personalFunds']['mira'],1)
        self.act('set-allowance-plan',dailyCrowns={'founder':2,'mira':1,'tamsin':1},minimumTreasuryCrowns=20)
        self.state['currentDayPhase']='evening';self.act('advance')
        self.assertEqual(self.state['personalFunds']['tamsin'],1)
    def test_retry_and_reload_cannot_double_allocate(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'allocate-personal-funds','characterId':'founder','crowns':4}}
            once=store.action(payload);self.assertEqual(store.action(payload),once)
            again=GameStore(directory).read()
            self.assertEqual(again['personalFunds']['founder'],4);self.assertEqual(again['sharedFunds'],76)
            self.assertEqual(len(again['moneyJournal']),1)
