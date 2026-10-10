from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
import game as g
import character_builds as b
from server import GameStore


class CharacterBuildTests(unittest.TestCase):
    def setUp(self):
        self.s = g.new_campaign()
        g.award_advancement(self.s, 'founder', 'test', 100, 'Test accomplishment')
    def act(self, kind, **fields):
        return g.apply_action(self.s, {'type': kind, **fields})
    def train(self, kind, target, who='founder'):
        self.act('train-character-build', characterId=who, buildKind=kind, targetId=target)
        for _ in range(b.KINDS[kind][2]): self.act('advance')
    def reject(self, kind, **fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError): self.act(kind, **fields)
        self.assertEqual(self.s, before)
    def qualify(self, perk, who='founder'):
        definition=b.PERKS[perk]
        record=self.s['characterBuilds'][who]
        record['attributes'][definition['attribute']]=6
        record['affinities'][definition['affinity']]=1
        self.s['characterSkills'][who][definition['skill']]=1
    def test_new_and_newly_introduced_characters_have_independent_baselines(self):
        self.assertEqual(b.build(self.s,'founder'), b.empty_build())
        self.s['people']['visitor']={**deepcopy(self.s['people']['mira']), 'personId':'visitor'}
        g.initialize_character_records(self.s,'visitor',[],'A small focus')
        self.s['characterBuilds']['visitor']['attributes']['intelligence']=8
        self.assertEqual(b.build(self.s,'mira')['attributes']['intelligence'],7)
        g.initialize_character_records(self.s,'visitor',[],'Another focus')
        self.assertEqual(b.build(self.s,'visitor')['attributes']['intelligence'],8)
    def test_training_reserves_then_invests_once_own_three_phases(self):
        before=g.character_sheet(self.s,'founder')['availableAdvancement']
        self.act('train-character-build',characterId='founder',buildKind='attribute',targetId='intelligence')
        self.assertEqual(g.character_sheet(self.s,'founder')['reservedAdvancement'],3)
        self.assertEqual(g.character_sheet(self.s,'founder')['availableAdvancement'],before-3)
        self.act('advance'); self.act('advance')
        self.assertEqual(b.build(self.s,'founder')['attributes']['intelligence'],5)
        self.act('advance')
        sheet=g.character_sheet(self.s,'founder')
        self.assertEqual(sheet['investedAdvancement'],3)
        self.assertEqual(sheet['reservedAdvancement'],0)
        self.assertEqual(sheet['availableAdvancement'],before-3)
        self.assertEqual(b.build(self.s,'founder')['attributes']['intelligence'],6)
        self.assertEqual(g.character_assignment(self.s,'founder'),'rest')
        self.act('advance');self.assertEqual(b.build(self.s,'founder')['attributes']['intelligence'],6)
    def test_pause_cancel_releases_reservation_without_free_progress(self):
        self.act('train-character-build',characterId='founder',buildKind='attribute',targetId='resolve')
        self.act('advance');self.act('assign-founder',assignment='rest');self.act('advance')
        self.assertEqual(self.s['trainingProjects']['founder']['completedWorkPhases'],1)
        self.act('cancel-training',characterId='founder')
        self.assertEqual(g.character_sheet(self.s,'founder')['availableAdvancement'],100)
        self.reject('cancel-training',characterId='founder')
    def test_validation_limits_home_and_single_project_are_atomic(self):
        for kind,target in [('unknown','x'),('attribute','x'),([], 'intelligence'),('attribute', {})]:
            self.reject('train-character-build',characterId='founder',buildKind=kind,targetId=target)
        self.reject('train-character-build',characterId='tamsin',buildKind='attribute',targetId='intelligence')
        for _ in range(5):self.train('attribute','intelligence')
        self.reject('train-character-build',characterId='founder',buildKind='attribute',targetId='intelligence')
        self.act('start-training',characterId='founder',practiceId='archive-focus')
        self.reject('train-character-build',characterId='founder',buildKind='attribute',targetId='resolve')
        self.act('cancel-training',characterId='founder');self.act('start-expedition')
        self.reject('train-character-build',characterId='founder',buildKind='attribute',targetId='resolve')
    def test_affinity_requires_personal_knowledge_not_shared_archive_or_ancestry(self):
        self.s['archivePrinciples'].append('gentle-refraction')
        self.reject('train-character-build',characterId='founder',buildKind='affinity',targetId='light')
        g.learn_for_character(self.s,'founder','gentle-refraction')
        self.train('affinity','light');self.train('affinity','light')
        self.reject('train-character-build',characterId='founder',buildKind='affinity',targetId='light')
        self.assertEqual(b.build(self.s,'mira')['affinities']['light'],0)
    def test_perks_require_all_paths_and_do_not_grant_extra_training_speed(self):
        self.reject('train-character-build',characterId='founder',buildKind='perk',targetId='archive-synthesis')
        self.qualify('archive-synthesis')
        self.train('perk','archive-synthesis')
        self.reject('train-character-build',characterId='founder',buildKind='perk',targetId='archive-synthesis')
        self.act('train-character-build',characterId='founder',buildKind='attribute',targetId='intelligence')
        self.act('advance');self.assertEqual(self.s['trainingProjects']['founder']['completedWorkPhases'],1)
    def test_work_parts_are_personal_scoped_and_no_income_multiplier(self):
        research=g.work_contribution(self.s,'founder','archive-focus')
        craft=g.work_contribution(self.s,'founder','careful-assembly')
        income=g.copying_income(self.s)
        record=self.s['characterBuilds']['founder'];record['attributes']['intelligence']=8;record['perks']=['archive-synthesis']
        self.assertEqual(g.work_contribution(self.s,'founder','archive-focus'),research+2)
        self.assertEqual(g.work_contribution(self.s,'founder','careful-assembly'),craft)
        self.assertEqual(g.copying_income(self.s),income)
        record['attributes']['dexterity']=8;record['perks'].append('patient-hands')
        self.assertEqual(g.work_contribution(self.s,'founder','careful-assembly'),craft+2)
        self.assertEqual(sum(p['amount'] for p in g.public_state(self.s)['workContributionViews']['founder']['archive-focus']),research+2)
    def test_casting_bonus_actual_output_matches_preview_no_free_inputs_or_repeat(self):
        who='founder';self.s['sharedFunds']=200
        for key in self.s['materialInventory']:self.s['materialInventory'][key]=10
        g.learn_for_character(self.s,who,'gentle-refraction')
        self.s['characterBuilds'][who]['affinities']['light']=2
        self.s['characterBuilds'][who]['perks']=['glasswright']
        self.act('draft-spell',characterId=who,formId='clarify-glass',name='Four clear lenses',intent='Clarify glass',materials=['moon-glass','moon-glass'])
        spell=self.s['spellbook'][-1]['id'];self.act('test-spell',spellId=spell);self.act('advance');self.act('advance')
        self.act('prepare-spells',characterId=who,spellIds=[spell])
        before=self.s['materialInventory']['moon-glass'];inputs=self.s['materialInventory']['fireglass']
        self.act('cast-spell',spellId=spell)
        self.assertEqual(self.s['materialInventory']['fireglass'],inputs-1)
        self.assertEqual(self.s['materialInventory']['moon-glass'],before)
        self.assertIn('4 Moon glass',g.public_state(self.s)['spellViews'][-1]['personalEffect'])
        self.act('advance');self.assertEqual(self.s['materialInventory']['moon-glass'],before+4)
        self.act('advance');self.assertEqual(self.s['materialInventory']['moon-glass'],before+4)
        self.assertEqual(b.casting_output(self.s,'mira','clarify-glass')['materialOutput']['moon-glass'],2)
    def test_all_affinity_and_perk_outputs_are_bounded(self):
        record=self.s['characterBuilds']['founder'];record['affinities']={key:2 for key in b.AFFINITIES};record['perks']=list(b.PERKS)
        self.assertEqual(b.casting_output(self.s,'founder','root-song')['materialOutput'],{'silver-ivy':4})
        self.assertEqual(b.casting_output(self.s,'founder','warm-twist')['materialOutput'],{'binding-thread':4})
        self.assertEqual(b.casting_output(self.s,'founder','luminous-copy')['crownsOutput'],8)
        self.assertEqual(g.spell_preparation_capacity(self.s),3)
    def test_retraining_refunds_build_but_preserves_personal_knowledge_and_history(self):
        for _ in range(3):self.train('attribute','resolve')
        self.assertEqual(g.spell_preparation_capacity(self.s),3)
        g.learn_for_character(self.s,'founder','gentle-refraction')
        awards=deepcopy(self.s['characterDevelopment']['founder']['advancementAwards'])
        self.s['preparedSpells']['founder']=['one','two','three']
        self.reject('start-retraining',characterId='founder')
        self.s['preparedSpells']['founder']=[]
        self.act('start-retraining',characterId='founder')
        # A changed loadout after agreement also cannot sneak through completion.
        self.s['preparedSpells']['founder']=['one','two','three'];self.act('advance')
        self.assertEqual(self.s['trainingProjects']['founder']['completedWorkPhases'],0)
        self.s['preparedSpells']['founder']=[];self.act('advance')
        self.assertEqual(b.build(self.s,'founder'),b.empty_build())
        self.assertEqual(g.character_sheet(self.s,'founder')['availableAdvancement'],100)
        self.assertIn('gentle-refraction',g.character_principles(self.s,'founder'))
        self.assertEqual(self.s['characterDevelopment']['founder']['advancementAwards'],awards)
    def test_resident_uses_same_costs_own_budget_and_no_personality_changes(self):
        g.award_advancement(self.s,'mira','test',10,'Her accomplishment')
        profile=deepcopy(self.s['people']['mira']);founder=deepcopy(b.build(self.s,'founder'))
        self.train('attribute','intelligence','mira')
        self.assertEqual(g.character_sheet(self.s,'mira')['investedAdvancement'],3)
        self.assertEqual(b.build(self.s,'founder'),founder)
        self.assertEqual(self.s['people']['mira'],profile)
    def test_schema25_upgrade_preserves_old_save_and_retry_reload(self):
        old=deepcopy(self.s);old.pop('characterBuilds');old['schemaVersion']=25
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);upgraded=store.read()
            for key,value in old.items():
                if key not in ('schemaVersion','revision'):self.assertEqual(upgraded[key],value,key)
            self.assertTrue((Path(directory)/f"campaign-before-schema-25-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            request={'requestId':uuid.uuid4().hex,'expectedRevision':upgraded['revision'],'action':{'type':'train-character-build','characterId':'founder','buildKind':'attribute','targetId':'intelligence'}}
            after=store.action(request)
            self.assertEqual(store.action(request),after)
            self.assertEqual(GameStore(directory).read(),after)
