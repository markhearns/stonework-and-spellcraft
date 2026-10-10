"""Progression, budget and migration regressions for the connected 0.4 slice."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid

from game import apply_action, new_campaign, public_state, RuleError, FACILITIES
from server import GameStore


class LivingWingTests(unittest.TestCase):
    def setUp(self):
        self.state = new_campaign()

    def act(self, kind, **fields):
        return apply_action(self.state, {'type': kind, **fields})

    def research(self):
        self.act('start-research')
        for _ in range(3): self.act('advance')

    def visit(self, site, approach, lantern=False):
        self.act('start-expedition', siteId=site, carryLantern=lantern)
        self.act('advance')
        self.act('choose-expedition-approach', approach=approach)
        while self.state['expedition']['stage'] == 'working': self.act('advance')
        self.act('return-expedition'); self.act('advance')

    def build(self, facility_id):
        self.act('start-facility', facilityId=facility_id)
        for _ in range(FACILITIES[facility_id]['requiredWorkPhases']): self.act('advance')

    def test_funding_pause_and_one_scholar_budget(self):
        self.act('start-facility', facilityId='kitchen')
        self.assertEqual(self.state['sharedFunds'], 62)
        self.act('advance')
        with self.assertRaises(RuleError): self.act('start-facility', facilityId='kitchen')
        self.assertEqual(self.state['sharedFunds'], 62)
        self.act('start-facility', facilityId='washroom')
        self.act('advance')
        self.assertEqual(self.state['facilityProjects']['kitchen']['completedWorkPhases'], 1)
        self.assertEqual(self.state['facilityProjects']['washroom']['completedWorkPhases'], 1)
        self.act('start-restoration'); self.act('advance')
        self.assertEqual(self.state['facilityProjects']['washroom']['completedWorkPhases'], 1)
        self.assertEqual(self.state['restorationCompletedPhases'], 1)
        self.act('assign-facility', facilityId='kitchen'); self.act('advance')
        self.assertEqual(self.state['facilityProjects']['kitchen']['status'], 'complete')
        self.assertEqual(self.state['founderAssignment'], 'rest')
        self.assertEqual(self.state['restorationCompletedPhases'], 1)
        with self.assertRaises(RuleError): self.act('assign-facility', facilityId='kitchen')

    def test_prerequisites_and_away_presence(self):
        before = deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('start-facility', facilityId='service-wards')
        self.assertEqual(self.state, before)
        with self.assertRaises(RuleError): self.act('start-expedition', siteId='reedbank-waystation')
        self.act('start-expedition')
        before = deepcopy(self.state)
        for kind, fields in [('start-facility', {'facilityId':'kitchen'}), ('place-household-artifact', {'artifactId':'hearth-kettle','installed':True}), ('celebrate-living-wing', {})]:
            with self.assertRaises(RuleError): self.act(kind, **fields)
            self.assertEqual(self.state, before)

    def test_waystation_rewards_require_return_and_are_unique(self):
        self.visit('old-waterworks', 'survey')
        self.assertTrue(public_state(self.state)['siteAccess']['reedbank-waystation'])
        self.state['craftedArtifacts']['warming-lantern'] = 1
        self.act('start-expedition', siteId='reedbank-waystation', carryLantern=True)
        self.act('advance')
        self.assertEqual(public_state(self.state)['expeditionSite']['id'], 'reedbank-waystation')
        self.act('choose-expedition-approach', approach='survey')
        self.assertEqual(self.state['expedition']['remainingWorkPhases'], 1)
        self.act('advance')
        self.assertNotIn('gentle-preservation', self.state['founderKnownPrinciples'])
        self.act('return-expedition'); self.act('advance')
        self.assertIn('gentle-preservation', self.state['founderKnownPrinciples'])
        self.assertEqual(self.state['lastExpeditionReport']['siteId'], 'reedbank-waystation')
        self.act('start-expedition', siteId='reedbank-waystation'); self.act('advance')
        with self.assertRaises(RuleError): self.act('choose-expedition-approach', approach='survey')
        self.act('choose-expedition-approach', approach='salvage'); self.act('advance')
        before = deepcopy(self.state['materialInventory']); funds = self.state['sharedFunds']
        self.act('return-expedition'); self.act('advance')
        self.assertEqual(self.state['materialInventory']['porous-clay'], before['porous-clay'] + 2)
        self.assertEqual(self.state['materialInventory']['binding-thread'], before['binding-thread'] + 3)
        self.assertEqual(self.state['sharedFunds'], funds + 12)
        with self.assertRaises(RuleError): self.act('start-expedition', siteId='reedbank-waystation')
        # Completion at one site does not close unresolved work at the other.
        self.act('start-expedition', siteId='old-waterworks')

    def test_waystation_early_return_does_not_resolve_lead(self):
        self.visit('old-waterworks', 'survey')
        self.act('start-expedition', siteId='reedbank-waystation'); self.act('advance')
        self.act('choose-expedition-approach', approach='survey'); self.act('advance')
        self.act('return-expedition'); self.act('advance')
        self.assertEqual(self.state['waystationDiscoveries'], [])
        self.assertNotIn('gentle-preservation', self.state['archivePrinciples'])

    def test_pantry_stacks_with_charm_only_for_staffed_sales(self):
        self.visit('old-waterworks', 'survey'); self.visit('reedbank-waystation', 'survey')
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='pantry-seal', materials=['porous-clay','binding-thread'])
        self.act('advance'); self.act('advance')
        with self.assertRaises(RuleError): self.act('place-household-artifact', artifactId='pantry-seal', installed=True)
        self.build('kitchen')
        self.act('start-restoration')
        for _ in range(3): self.act('advance')
        self.act('place-household-artifact', artifactId='pantry-seal', installed=True)
        self.state['craftedArtifacts']['watering-charm'] = 1
        self.act('install-watering-charm', installed=True)
        self.act('garden-production', choice='surplus-sales')
        before = self.state['sharedFunds']; self.act('advance')
        self.assertEqual(self.state['sharedFunds'], before)
        self.act('assign-resident', assignment='garden')
        self.assertEqual(public_state(self.state)['gardenYield'], 8)
        inventory = deepcopy(self.state['materialInventory'])
        self.act('advance')
        self.assertEqual(self.state['sharedFunds'], before + 8)
        self.assertEqual(self.state['materialInventory'], inventory)
        self.act('place-household-artifact', artifactId='pantry-seal', installed=False)
        self.assertEqual(public_state(self.state)['gardenYield'], 6)
        self.act('garden-production', choice='silver-ivy')
        self.act('place-household-artifact', artifactId='pantry-seal', installed=True)
        self.assertEqual(public_state(self.state)['gardenYield'], 2)

    def test_milestone_requires_advance_and_celebration_is_optional_once(self):
        self.research()
        for facility_id in FACILITIES: self.build(facility_id)
        self.assertIsNone(self.state['livingWingCompletedOn'])
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='hearth-kettle', materials=['sun-amber','porous-clay'])
        self.act('advance'); self.act('advance')
        before = (self.state['dayNumber'], self.state['currentDayPhase'])
        self.act('place-household-artifact', artifactId='hearth-kettle', installed=True)
        self.assertEqual((self.state['dayNumber'], self.state['currentDayPhase']), before)
        self.assertIsNone(self.state['livingWingCompletedOn'])
        self.assertTrue(all(row['complete'] for row in public_state(self.state)['livingWingRequirements']))
        self.act('advance')
        self.assertEqual(self.state['livingWingCompletedOn'], {'dayNumber':before[0], 'phase':before[1]})
        self.assertEqual(self.state['livingWingCelebration'], 'available')
        self.assertIn('Milestone: A Proper Living Wing.', ' '.join(self.state['lastPhaseSummary']))
        for _ in range(5): self.act('advance')
        self.assertEqual(self.state['livingWingCelebration'], 'available')
        before = (self.state['dayNumber'], self.state['currentDayPhase'], self.state['sharedFunds'], self.state['resonancePoints'])
        self.act('celebrate-living-wing')
        self.assertEqual((self.state['dayNumber'], self.state['currentDayPhase'], self.state['sharedFunds'], self.state['resonancePoints']), before)
        with self.assertRaises(RuleError): self.act('celebrate-living-wing')
        self.act('place-household-artifact', artifactId='hearth-kettle', installed=False)
        self.act('place-household-artifact', artifactId='hearth-kettle', installed=True)
        self.act('advance')
        self.assertEqual(self.state['livingWingCelebration'], 'completed')
        self.assertEqual(sum('Milestone: A Proper Living Wing.' in row['text'] for row in self.state['journal']), 1)

    def test_copying_commissions_prevent_a_treasury_dead_end(self):
        self.state['sharedFunds'] = 0
        self.act('assign-founder', assignment='commissions')
        self.act('assign-founder', assignment='commissions')
        self.assertEqual(self.state['sharedFunds'], 0)
        self.assertIn('Copying commissions: +4', ' '.join(public_state(self.state)['nextPhaseForecast']))
        for _ in range(7): self.act('advance')
        self.assertEqual(self.state['sharedFunds'], 28)
        self.act('start-restoration')
        self.act('advance')
        self.assertEqual(self.state['sharedFunds'], 3)
        self.assertEqual(self.state['restorationCompletedPhases'], 1)
        self.act('assign-founder', assignment='commissions'); self.act('advance')
        self.assertEqual(self.state['sharedFunds'], 7)
        self.assertEqual(self.state['restorationCompletedPhases'], 1)
        self.act('start-expedition'); self.act('advance')
        self.assertEqual(self.state['sharedFunds'], 7)
        with self.assertRaises(RuleError): self.act('assign-founder', assignment='commissions')

    def test_funding_retry_and_failed_placement_are_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GameStore(directory)
            request = {'requestId':uuid.uuid4().hex, 'expectedRevision':0, 'action':{'type':'start-facility','facilityId':'washroom'}}
            after = store.action(request)
            self.assertEqual(store.action(request), after)
            self.assertEqual(after['sharedFunds'], 62)
            with self.assertRaises(RuleError):
                store.action({'requestId':uuid.uuid4().hex, 'expectedRevision':after['revision'], 'action':{'type':'place-household-artifact','artifactId':'hearth-kettle','installed':True}})
            self.assertEqual(GameStore(directory).read(), after)

    def test_schema_three_migration_keeps_in_flight_work_and_custom_art(self):
        self.act('start-restoration'); self.act('advance')
        self.state['craftedArtifacts']['warming-lantern'] = 1
        self.state['lanternDisplayed'] = True
        self.act('start-expedition', carryLantern=True); self.act('advance')
        self.act('choose-expedition-approach', approach='survey')
        self.state['assetOverrides']['library'] = '/user-assets/custom.webp'
        self.state['wardrobe']['outerLayer'] = 'plum-shawl'
        old = deepcopy(self.state)
        old['schemaVersion'] = 3
        for key in ('characterDevelopment','trainingProjects','residentKnownPrinciples','hearthResearchContributors','miraArchiveProject','libraryIndexInstalled'):
            old.pop(key, None)
        old['expedition'].pop('companionId', None)
        for key in ('waystationDiscoveries','facilityProjects','activeFacilityId','householdArtifactPlacements','livingWingCompletedOn','livingWingCelebration'):
            del old[key]
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)', (json.dumps(old),))
            store = GameStore(directory)
            upgraded = store.read()
            for key, value in old.items():
                if key not in ('schemaVersion', 'revision', 'expedition'): self.assertEqual(upgraded[key], value, key)
            self.assertEqual({key:value for key,value in upgraded['expedition'].items() if key != 'companionId'}, old['expedition'])
            self.assertEqual(upgraded['schemaVersion'],66)
            self.assertEqual(upgraded['revision'], old['revision'] + 1)
            with sqlite3.connect(Path(directory)/f"campaign-before-schema-3-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3") as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign').fetchone()[0]), old)
            self.assertEqual(GameStore(directory).read(), upgraded)
            self.state = upgraded
            self.act('advance'); self.act('return-expedition'); self.act('advance')
            self.assertIn('water-guidance', self.state['founderKnownPrinciples'])
            self.assertTrue(self.state['lanternDisplayed'])
            self.assertEqual(self.state['restorationCompletedPhases'], 1)
