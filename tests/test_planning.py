"""Research, stock policy and transactional work-order regressions for 0.6."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, learn_for_character, award_advancement
from server import GameStore

class PlanningTests(unittest.TestCase):
    def setUp(self): self.state = new_campaign()
    def act(self, kind, **fields): return apply_action(self.state, {'type':kind, **fields})
    def advance(self, count=1):
        for _ in range(count): self.act('advance')
    def prepare_research(self):
        self.state['researchStatus'] = 'complete'
        self.state['researchCompletedPhases'] = 3
        for who in ('founder','mira'):
            for principle in ('steady-hearth-wards','water-guidance','reference-binding','gentle-preservation'):
                learn_for_character(self.state, who, principle)
    def install(self, artifact):
        self.state['craftedArtifacts'][artifact] = 1
        self.act('place-utility-artifact', artifactId=artifact, installed=True)

    def test_research_prerequisites_focus_pause_and_one_time_funding(self):
        before = deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('focus-research', researchId='root-rhythms', leaderId='founder')
        self.assertEqual(self.state, before)
        self.prepare_research()
        self.act('focus-research', researchId='root-rhythms', leaderId='founder'); self.advance()
        self.assertEqual(self.state['sharedFunds'], 68)
        self.act('focus-research', researchId='luminous-impressions', leaderId='founder'); self.advance()
        self.assertEqual(self.state['researchProjects']['root-rhythms']['completedWorkPhases'], 1)
        self.assertEqual(self.state['researchProjects']['luminous-impressions']['completedWorkPhases'], 1)
        self.assertEqual(self.state['sharedFunds'], 54)
        self.act('focus-research', researchId='root-rhythms', leaderId='founder')
        self.act('assign-resident', assignment='archive'); self.advance(2)
        project = self.state['researchProjects']['root-rhythms']
        self.assertEqual(project['completedWorkPhases'], 5)
        self.assertEqual(project['status'], 'complete')
        self.assertIsNone(self.state['activeResearchId'])
        for who, field in [('founder','founderKnownPrinciples'),('mira','residentKnownPrinciples')]:
            self.assertIn('steady-growth', self.state[field])
            self.assertIn('research:root-rhythms', self.state['characterDevelopment'][who]['advancementAwards'])
        with self.assertRaises(RuleError): self.act('focus-research', researchId='root-rhythms', leaderId='founder')
        self.assertEqual(self.state['sharedFunds'], 54)

    def test_resident_research_while_founder_away_requires_later_personal_study(self):
        self.prepare_research()
        self.act('focus-research', researchId='root-rhythms', leaderId='founder'); self.advance()
        self.act('focus-research', researchId='root-rhythms', leaderId='mira')
        self.act('start-expedition'); self.advance()
        self.act('choose-expedition-approach', approach='salvage'); self.advance(3)
        self.assertEqual(self.state['researchProjects']['root-rhythms']['status'], 'complete')
        self.assertIn('steady-growth', self.state['residentKnownPrinciples'])
        self.assertNotIn('steady-growth', self.state['founderKnownPrinciples'])
        self.assertIn('research:root-rhythms', self.state['characterDevelopment']['founder']['advancementAwards'])
        self.act('return-expedition'); self.advance()
        self.assertNotIn('steady-growth', self.state['founderKnownPrinciples'])
        self.act('study-principle', characterId='founder', principleId='steady-growth'); self.advance(2)
        self.assertIn('steady-growth', self.state['founderKnownPrinciples'])

    def test_prepared_research_and_index_use_the_same_work_budget(self):
        self.prepare_research()
        self.state['libraryIndexInstalled'] = True
        self.act('prepare-practice', characterId='mira', practiceId='archive-focus', prepared=True)
        self.act('focus-research', researchId='shared-lessons', leaderId='mira')
        self.act('assign-founder', assignment='commissions')
        before = self.state['sharedFunds']; self.advance()
        self.assertEqual(self.state['researchProjects']['shared-lessons']['completedWorkPhases'], 3)
        self.assertEqual(self.state['sharedFunds'], before+5)
        self.advance()
        self.assertEqual(self.state['researchProjects']['shared-lessons']['completedWorkPhases'], 4)
        self.assertEqual(self.state['residentAssignment'], 'rest')
        self.assertNotIn('clear-instruction', self.state['founderKnownPrinciples'])

    def test_reserves_prevent_sale_but_allow_explicit_crafting(self):
        self.state['materialInventory']['silver-ivy'] = 2
        self.act('set-material-reserve', materialId='silver-ivy', target=2)
        before = deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('sell-material', materialId='silver-ivy')
        self.assertEqual(self.state, before)
        for target in (-1, 1000, True, 1.5):
            with self.assertRaises(RuleError): self.act('set-material-reserve', materialId='silver-ivy', target=target)
        learn_for_character(self.state, 'founder', 'water-guidance')
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='watering-charm', materials=['porous-clay','silver-ivy'])
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 1)
        self.assertEqual(self.state['materialReserveTargets']['silver-ivy'], 2)
        self.act('set-material-reserve', materialId='silver-ivy', target=0)
        self.act('sell-material', materialId='silver-ivy')
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 0)

    def test_stock_first_and_root_tender_do_not_sell_stock_or_double_harvest(self):
        with self.assertRaises(RuleError): self.install('root-tender')
        self.state['restorationStatus'] = 'complete'
        self.install('root-tender')
        self.state['craftedArtifacts']['watering-charm'] = 1
        self.act('install-watering-charm', installed=True)
        self.state['householdArtifactPlacements']['pantry-seal'] = True
        self.act('set-material-reserve', materialId='silver-ivy', target=2)
        self.act('garden-production', choice='stock-first')
        before = self.state['sharedFunds']; self.advance(2)
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 2)
        self.assertEqual(self.state['sharedFunds'], before)
        forecast = public_state(self.state)['gardenForecast']
        self.assertEqual((forecast['output'],forecast['amount'],forecast['automated']), ('surplus-sales',2,True))
        self.advance()
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 2)
        self.assertEqual(self.state['sharedFunds'], before+2)
        self.act('assign-resident', assignment='garden'); self.advance()
        self.assertEqual(self.state['sharedFunds'], before+10)  # 8 staffed, not 8+2
        self.act('set-material-reserve', materialId='silver-ivy', target=3)
        self.advance()
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 4)  # Whole harvest.
        self.state['miraArchiveProject']['status'] = 'complete'
        self.act('start-expedition', companionId='mira'); self.advance()
        self.assertEqual(self.state['sharedFunds'], before+12)
        self.assertEqual(self.state['materialInventory']['silver-ivy'], 4)

    def test_scribe_and_lesson_tablet_affect_only_their_named_work(self):
        self.install('scribe-stone')
        self.state['libraryIndexInstalled'] = True
        self.state['characterDevelopment']['founder']['learnedPractices'] = ['archive-focus']
        self.act('prepare-practice', characterId='founder', practiceId='archive-focus', prepared=True)
        before = self.state['sharedFunds']; self.advance()
        self.assertEqual(self.state['sharedFunds'], before)
        self.act('assign-founder', assignment='commissions'); self.advance()
        self.assertEqual(self.state['sharedFunds'], before+8)
        self.state['archivePrinciples'].extend(['steady-growth','clear-instruction'])
        self.act('study-principle', characterId='founder', principleId='steady-growth')
        self.install('lesson-tablet')
        self.assertEqual(self.state['trainingProjects']['founder']['requiredWorkPhases'], 2)
        self.advance()
        self.assertNotIn('steady-growth', self.state['founderKnownPrinciples'])
        self.advance()
        self.act('study-principle', characterId='mira', principleId='clear-instruction')
        self.assertEqual(self.state['trainingProjects']['mira']['requiredWorkPhases'], 1)
        self.act('place-utility-artifact', artifactId='lesson-tablet', installed=False)
        self.advance()
        self.assertIn('clear-instruction', self.state['residentKnownPrinciples'])
        self.install('lesson-tablet')
        award_advancement(self.state, 'mira', 'fixture', 2, 'Fixture accomplishment')
        self.act('start-training', characterId='mira', practiceId='careful-assembly')
        self.assertEqual(self.state['trainingProjects']['mira']['requiredWorkPhases'], 2)

    def test_work_order_purchase_start_retry_and_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GameStore(directory)
            def request(kind, **fields):
                return {'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind,**fields}}
            def act(kind, **fields): return store.action(request(kind, **fields))
            payload = request('create-work-order', recipeId='warming-lantern', crafterId='founder', materials=['fireglass','silver-ivy'], requestedCount=2)
            after = store.action(payload); self.assertEqual(store.action(payload), after)
            self.assertEqual(after['sharedFunds'], 80); self.assertEqual(len(after['workOrders']), 1)
            self.assertIsNone(after['craftingProject'])
            with self.assertRaises(RuleError): act('start-work-order', orderId='order-1')
            act('start-research')
            for _ in range(3): act('advance')
            self.assertEqual(public_state(store.read())['workOrderViews'][0]['purchaseCostCrowns'], 13)
            act('buy-work-order-materials', orderId='order-1')
            self.assertEqual(store.read()['sharedFunds'], 47)
            payload = request('start-work-order', orderId='order-1')
            after = store.action(payload); self.assertEqual(store.action(payload), after)
            self.assertEqual(after['materialInventory']['fireglass'], 0)
            with self.assertRaises(RuleError): act('remove-work-order', orderId='order-1')
            for _ in range(2): act('advance')
            self.assertEqual(store.read()['workOrders'][0]['completedCount'], 1)
            self.assertIsNone(store.read()['craftingProject'])
            for _ in range(2): act('advance')
            self.assertEqual(store.read()['workOrders'][0]['completedCount'], 1)
            act('buy-work-order-materials', orderId='order-1'); act('start-work-order', orderId='order-1')
            for _ in range(2): act('advance')
            self.assertEqual(store.read()['workOrders'][0]['completedCount'], 2)
            with self.assertRaises(RuleError): act('start-work-order', orderId='order-1')
            self.assertEqual(public_state(store.read())['characterSheets']['founder']['earnedAdvancement'], 2)
            act('remove-work-order', orderId='order-1')
            self.assertEqual(store.read()['craftedArtifacts']['warming-lantern'], 2)
            self.assertEqual(GameStore(directory).read(), store.read())

    def test_work_order_counts_duplicate_components_and_checks_affordability(self):
        self.state['materialInventory']['moon-glass'] = 1
        self.act('create-work-order', recipeId='hearth-kettle', crafterId='founder', materials=['moon-glass','moon-glass'], requestedCount=1)
        view = public_state(self.state)['workOrderViews'][0]
        self.assertEqual(view['missingMaterials'], {'moon-glass':1})
        self.assertEqual(view['purchaseCostCrowns'], 8)
        self.state['sharedFunds'] = 7; before = deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('buy-work-order-materials', orderId='order-1')
        self.assertEqual(self.state, before)
        with self.assertRaises(RuleError): self.act('create-work-order', recipeId='hearth-kettle', crafterId='founder', materials=['binding-thread','moon-glass'], requestedCount=1)
        with self.assertRaises(RuleError): self.act('create-work-order', recipeId='hearth-kettle', crafterId='founder', materials=['moon-glass','moon-glass'], requestedCount=True)

    def test_schema_five_migration_preserves_active_learning_and_crafting(self):
        self.prepare_research()
        self.act('start-crafting', recipeId='warming-lantern', crafterId='founder', materials=['sun-amber','binding-thread']); self.advance()
        self.state['archivePrinciples'].append('reference-binding')
        self.state['residentKnownPrinciples'].remove('reference-binding')
        self.act('study-principle', characterId='mira', principleId='reference-binding')
        old = deepcopy(self.state)
        for field in ('researchProjects','activeResearchId','utilityArtifactPlacements','materialReserveTargets','workOrders','nextWorkOrderNumber'):
            old.pop(field)
        old['schemaVersion'] = 5
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store = GameStore(directory); upgraded = store.read()
            for key, value in old.items():
                if key not in ('schemaVersion','revision'): self.assertEqual(upgraded[key], value, key)
            self.assertTrue(all(target==0 for target in upgraded['materialReserveTargets'].values()))
            self.assertIsNone(upgraded['activeResearchId'])
            self.assertEqual(GameStore(directory).read(), upgraded)
            with sqlite3.connect(Path(directory)/f"campaign-before-schema-5-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3") as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign').fetchone()[0]), old)
            self.state = upgraded; self.advance(2)
            self.assertEqual(self.state['craftedArtifacts']['warming-lantern'], 1)
            self.assertIn('reference-binding', self.state['residentKnownPrinciples'])
