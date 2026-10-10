"""Accomplishment, preparation, personal mastery and companion regressions."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid

from game import (apply_action, new_campaign, public_state, RuleError, character_sheet,
                  award_advancement, learn_for_character, initialize_development)
from server import GameStore


class DevelopmentTests(unittest.TestCase):
    def setUp(self): self.state = new_campaign()
    def act(self, kind, **fields): return apply_action(self.state, {'type':kind, **fields})
    def advances(self, count):
        for _ in range(count): self.act('advance')
    def research(self):
        self.act('start-research'); self.advances(3)
    def points(self, who='founder'): return character_sheet(self.state, who)['availableAdvancement']
    def learn_practice(self, practice, who='founder'):
        self.act('start-training', characterId=who, practiceId=practice); self.advances(2)
    def open_story(self):
        # The complete milestone is a legitimate prerequisite; unrelated building
        # rules are tested in the full controller playthrough and living-wing suite.
        self.state['livingWingCompletedOn'] = {'dayNumber':1,'phase':'afternoon'}
        self.act('start-archive-project')
    def finish_story(self):
        self.open_story(); self.advances(4)
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='index-charm', crafterId='mira', materials=['porous-clay','binding-thread'])
        self.advances(3)
        self.act('install-index-charm', installed=True)
        self.act('finish-archive-story')

    def test_accomplishments_award_once_not_routine_repetition(self):
        self.research(); self.assertEqual(self.points(), 1)
        for _ in range(2):
            self.act('start-crafting', recipeId='warming-lantern', materials=['sun-amber','binding-thread'])
            self.advances(2)
        self.assertEqual(self.points(), 2)
        self.act('assign-founder', assignment='commissions'); self.advances(5)
        for _ in range(3): self.act('talk', topic='home')
        self.assertEqual(self.points(), 2)

    def test_learning_reserves_points_pauses_and_cancel_releases(self):
        award_advancement(self.state, 'founder', 'test', 2, 'Fixture accomplishment')
        self.act('start-training', characterId='founder', practiceId='careful-assembly')
        self.assertEqual(self.points(), 0)
        self.advances(1)
        self.act('assign-founder', assignment='commissions'); self.advances(2)
        self.assertEqual(self.state['trainingProjects']['founder']['completedWorkPhases'], 1)
        with self.assertRaises(RuleError): self.act('start-training', characterId='founder', practiceId='field-notes')
        self.act('cancel-training', characterId='founder')
        self.assertEqual(self.points(), 2)
        self.assertNotIn('careful-assembly', self.state['characterDevelopment']['founder']['learnedPractices'])
        self.learn_practice('careful-assembly')
        self.assertEqual(self.points(), 0)
        self.assertEqual(self.state['characterDevelopment']['founder']['preparedPractices'], [])

    def test_prepared_assembly_is_real_and_retraining_keeps_knowledge(self):
        self.research()
        award_advancement(self.state, 'founder', 'test', 5, 'Fixture accomplishments')
        for practice in ('careful-assembly','archive-focus','field-notes'): self.learn_practice(practice)
        self.act('prepare-practice', characterId='founder', practiceId='careful-assembly', prepared=True)
        self.act('prepare-practice', characterId='founder', practiceId='archive-focus', prepared=True)
        with self.assertRaises(RuleError): self.act('prepare-practice', characterId='founder', practiceId='field-notes', prepared=True)
        self.act('start-crafting', recipeId='warming-lantern', materials=['sun-amber','binding-thread'])
        self.assertEqual(public_state(self.state)['craftingWorkPerPhase'], 2)
        self.advances(1)
        self.assertIsNone(self.state['craftingProject'])
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'], 1)
        known = deepcopy(self.state['founderKnownPrinciples'])
        earned = character_sheet(self.state,'founder')['earnedAdvancement']
        self.act('start-retraining', characterId='founder'); self.advances(1)
        self.assertEqual(self.points(), earned)
        self.assertEqual(self.state['founderKnownPrinciples'], known)
        self.assertEqual(self.state['characterDevelopment']['founder']['learnedPractices'], [])
        self.assertEqual(self.state['characterDevelopment']['founder']['preparedPractices'], [])

    def test_mira_mastery_and_own_crafting_budget(self):
        self.research()
        with self.assertRaises(RuleError): self.act('start-crafting', recipeId='warming-lantern', crafterId='mira', materials=['sun-amber','binding-thread'])
        self.act('study-principle', characterId='mira', principleId='steady-hearth-wards')
        self.act('assign-founder', assignment='commissions')
        self.advances(2)
        self.assertIn('steady-hearth-wards', self.state['residentKnownPrinciples'])
        before = self.state['sharedFunds']
        self.act('start-crafting', recipeId='warming-lantern', crafterId='mira', materials=['sun-amber','binding-thread'])
        self.assertEqual(self.state['founderAssignment'], 'commissions')
        self.advances(2)
        self.assertEqual(self.state['sharedFunds'], before+8)
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'], 1)
        self.assertEqual(self.points('mira'), 1)
        self.assertEqual(self.points(), 1)
        with self.assertRaises(RuleError): self.act('study-principle', characterId='mira', principleId='water-guidance')

    def test_mira_story_contributors_placement_and_no_duplicate_reward(self):
        with self.assertRaises(RuleError): self.act('start-archive-project')
        self.open_story()
        self.act('prepare-practice', characterId='mira', practiceId='archive-focus', prepared=True)
        self.act('assign-founder', assignment='archive-project')
        self.assertEqual(public_state(self.state)['archiveProjectWorkPerPhase'], 3)
        self.advances(2)
        self.assertEqual(self.state['miraArchiveProject']['completedWorkPhases'], 4)
        self.assertIn('reference-binding', self.state['founderKnownPrinciples'])
        self.assertIn('reference-binding', self.state['residentKnownPrinciples'])
        self.assertEqual(self.state['miraArchiveProject']['status'], 'ready-to-bind')
        with self.assertRaises(RuleError): self.act('finish-archive-story')
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='index-charm', crafterId='mira', materials=['porous-clay','binding-thread'])
        self.advances(3)
        before = (self.state['dayNumber'], self.state['currentDayPhase'], self.state['resonancePoints'])
        self.act('install-index-charm', installed=True)
        self.assertEqual(public_state(self.state)['copyingIncomePerPhase'], 5)
        self.act('finish-archive-story')
        self.assertEqual((self.state['dayNumber'],self.state['currentDayPhase'],self.state['resonancePoints']), before)
        self.assertEqual(self.points('mira'), 4)
        self.assertEqual(self.points(), 1)
        self.assertTrue(public_state(self.state)['siteAccess']['hillfold-bindery'])
        with self.assertRaises(RuleError): self.act('finish-archive-story')
        self.act('install-index-charm', installed=False); self.act('install-index-charm', installed=True)
        self.advances(2); self.assertEqual(self.points('mira'), 4)

    def test_solo_mira_study_does_not_teach_absent_founder(self):
        self.open_story(); self.act('start-expedition'); self.advances(1)
        self.act('choose-expedition-approach', approach='survey'); self.advances(2)
        self.advances(1)
        self.assertIn('reference-binding', self.state['residentKnownPrinciples'])
        self.assertNotIn('reference-binding', self.state['founderKnownPrinciples'])
        self.act('return-expedition'); self.advances(1)
        self.assertNotIn('reference-binding', self.state['founderKnownPrinciples'])
        self.act('study-principle', characterId='founder', principleId='reference-binding'); self.advances(2)
        self.assertIn('reference-binding', self.state['founderKnownPrinciples'])

    def test_companion_presence_preparation_rewards_and_return(self):
        with self.assertRaises(RuleError): self.act('start-expedition', companionId='mira')
        self.finish_story()
        self.learn_practice('field-notes', 'mira')
        self.act('prepare-practice', characterId='mira', practiceId='field-notes', prepared=True)
        self.act('start-restoration'); self.advances(3)
        self.act('assign-resident', assignment='garden')
        self.act('start-expedition', siteId='hillfold-bindery', companionId='mira')
        self.assertIsNone(public_state(self.state)['residentRoomId'])
        self.assertFalse(public_state(self.state)['residentAtCastle'])
        before = deepcopy(self.state['materialInventory'])
        for kind, fields in [('assign-resident',{'assignment':'garden'}),('prepare-practice',{'characterId':'mira','practiceId':'field-notes','prepared':False}),('free-text',{'text':'hello'})]:
            with self.assertRaises(RuleError): self.act(kind, **fields)
        self.advances(1)
        self.assertEqual(self.state['materialInventory'], before)
        self.act('choose-expedition-approach', approach='survey')
        self.assertEqual(self.state['expedition']['remainingWorkPhases'], 1)
        self.advances(1)
        self.assertEqual(self.state['materialInventory']['moon-glass'], 0)
        self.act('return-expedition'); self.advances(1)
        self.assertEqual(self.state['materialInventory']['moon-glass'], 2)
        self.assertEqual(self.state['residentAssignment'], 'rest')
        self.assertTrue(public_state(self.state)['residentAtCastle'])
        for who in ('founder','mira'):
            self.assertIn('hillfold-bindery:survey', self.state['characterDevelopment'][who]['advancementAwards'])
        # A later material choice can use this dual-property glass twice, but needs two items.
        learn_for_character(self.state, 'founder', 'steady-hearth-wards')
        self.act('start-crafting', recipeId='hearth-kettle', materials=['moon-glass','moon-glass'])
        self.assertEqual(self.state['materialInventory']['moon-glass'], 0)

    def test_mira_preferences_and_starting_expertise_survive_retraining(self):
        award_advancement(self.state, 'mira', 'test', 4, 'Fixture accomplishments')
        with self.assertRaises(RuleError): self.act('start-training', characterId='mira', practiceId='field-notes')
        self.learn_practice('careful-assembly', 'mira')
        self.act('prepare-practice', characterId='mira', practiceId='archive-focus', prepared=True)
        self.act('start-retraining', characterId='mira'); self.advances(1)
        self.assertEqual(self.state['characterDevelopment']['mira']['learnedPractices'], ['archive-focus'])
        self.assertEqual(self.state['characterDevelopment']['mira']['preparedPractices'], ['archive-focus'])
        self.assertEqual(self.points('mira'), 4)

    def test_new_action_retries_and_failures_are_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            store = GameStore(directory)
            def request(action): return {'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action}
            payload = request({'type':'prepare-practice','characterId':'mira','practiceId':'archive-focus','prepared':True})
            first = store.action(payload)
            self.assertEqual(store.action(payload), first)
            with self.assertRaises(RuleError): store.action(request({'type':'start-training','characterId':'founder','practiceId':'field-notes'}))
            self.assertEqual(store.read(), first)
            self.assertEqual(GameStore(directory).read(), first)

    def test_schema_four_credit_once_and_preserve_active_artifact(self):
        self.research()
        self.act('start-crafting', recipeId='warming-lantern', materials=['sun-amber','binding-thread']); self.advances(2)
        self.act('buy-material', materialId='porous-clay')
        self.act('start-crafting', recipeId='hearth-kettle', materials=['sun-amber','porous-clay']); self.advances(1)
        old = deepcopy(self.state)
        for key in ('characterDevelopment','trainingProjects','residentKnownPrinciples','hearthResearchContributors','miraArchiveProject','libraryIndexInstalled','binderyDiscoveries'):
            old.pop(key)
        old['materialInventory'].pop('moon-glass')
        old['craftingProject'].pop('crafterId')
        old['schemaVersion'] = 4
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)', (json.dumps(old),))
            store = GameStore(directory); upgraded = store.read()
            self.assertEqual(upgraded['craftingProject']['completedWorkPhases'], 1)
            self.assertEqual(upgraded['craftingProject']['crafterId'], 'founder')
            self.assertEqual(character_sheet(upgraded,'founder')['availableAdvancement'], 2)
            self.assertEqual(upgraded['characterDevelopment']['founder']['preparedPractices'], [])
            self.assertEqual(upgraded['materialInventory']['moon-glass'], 0)
            self.assertEqual(GameStore(directory).read(), upgraded)
            with sqlite3.connect(Path(directory)/f"campaign-before-schema-4-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3") as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign').fetchone()[0]), old)
            self.state = upgraded; self.advances(1)
            self.assertEqual(self.state['craftedArtifacts']['hearth-kettle'], 1)
            self.assertEqual(self.points(), 3)
