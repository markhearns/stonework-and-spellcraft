"""Attribute migration, additive routes, real work and remembered social alternatives."""
from copy import deepcopy
import json, sqlite3, tempfile, unittest, uuid
from pathlib import Path
import game as g
import character_builds as b
import character_approaches as a
import attribute_dialogue as dialogue
import social_life as social
import social_content
import field_magic as field
import spell_support
import lasting_rituals as rituals
from server import GameStore
import test_magic_overhaul as magic_tests
import test_household_chapters as household_tests

class AttributeIntegrationTests(unittest.TestCase):
    def setUp(self): self.s=g.new_campaign()
    def act(self,kind,**kw):return g.apply_action(self.s,{'type':kind,**kw})
    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(before,self.s)
    def member(self,who):household_tests.HouseholdChapterTests.member(self,who)
    def rich(self):return magic_tests.MagicTests.rich(self)
    def at(self,key):magic_tests.MagicTests.at(self,key)
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def boost(self,who='founder'):
        self.s['characterBuilds'][who]['attributes']={k:10 for k in b.ATTRIBUTES}
        self.s['characterSkills'][who]={k:2 for k in g.CHARACTER_SKILLS}
    def test_profiles_are_distinct_balanced_and_free_with_all_skills_trainable(self):
        self.assertEqual(len(b.ATTRIBUTES),6)
        self.assertEqual(len(set(b.PROFILES.values())),len(b.PROFILES))
        for who,values in b.PROFILES.items():
            self.assertEqual(sum(values),30,who)
            self.assertTrue(all(1<=v<=10 for v in values))
        for who in social_content.PERSONAL:
            self.member(who)
            self.assertEqual(b.build(self.s,who)['attributes'],b.baseline(who))
            self.assertEqual(g.character_sheet(self.s,who)['offeredSkills'],list(g.CHARACTER_SKILLS))
            self.assertEqual(b.invested(self.s,who),0)
    def test_legacy_migration_preserves_spend_thresholds_pending_completion_and_idempotence(self):
        self.s['schemaVersion']=48
        self.s['characterBuilds']['founder']={'attributes':{'insight':2,'dexterity':3,'resolve':3},'affinities':{'light':1,'growth':0,'hearth':0},'perks':['archive-synthesis']}
        self.s['characterSkills']['founder']={'scholarship':1,'artifice':0,'fieldcraft':0}
        self.s['trainingProjects']['founder']={'kind':'attribute','targetId':'insight','completedWorkPhases':2,'requiredWorkPhases':3}
        g.set_character_assignment(self.s,'founder','training')
        before={k:deepcopy(self.s[k]) for k in ('sharedFunds','journal','socialLife','spellbook')}
        g.migrate_state(self.s)
        self.assertEqual(self.s['schemaVersion'],g.CURRENT_SCHEMA_VERSION)
        self.assertEqual(b.invested(self.s,'founder'),20)
        self.assertEqual(b.capacity_bonus(self.s,'founder'),1)
        self.assertEqual(self.s['trainingProjects']['founder']['targetId'],'intelligence')
        saved=deepcopy(self.s);g.migrate_state(self.s);self.assertEqual(saved,self.s)
        for key,value in before.items():self.assertEqual(value,self.s[key])
        self.advance();self.assertEqual(b.build(self.s,'founder')['attributes']['intelligence'],8)
        self.assertEqual(b.invested(self.s,'founder'),23)
    def test_schema48_sqlite_backup_retries_and_new_skill_lesson_reload(self):
        self.s['schemaVersion']=48
        self.s['characterBuilds']['founder']={'attributes':{'insight':1,'dexterity':1,'resolve':1},'affinities':{'light':0,'growth':0,'hearth':0},'perks':[]}
        g.award_advancement(self.s,'founder','fixture',30,'Fixture')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(self.s),))
            store=GameStore(directory);s=store.read()
            self.assertTrue((Path(directory)/f"campaign-before-schema-48-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            req={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':{'type':'train-skill','characterId':'founder','skillId':'diplomacy'}}
            trained=store.action(req);self.assertEqual(store.action(req),trained)
            self.assertEqual(GameStore(directory).read(),trained)
    def test_every_field_route_resolves_one_phase_without_supplies_injury_or_early_reward(self):
        count=0
        for obstacle,routes in a.FIELD.items():
            for route in routes:
                with self.subTest(obstacle=obstacle,route=route[0]):
                    self.s=self.rich();self.boost();self.at(obstacle)
                    before=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds'];health=field.vitality(self.s,'founder')
                    self.act('field-method',method='aptitude:'+route[0]);self.assertEqual(self.s['expedition']['remainingWorkPhases'],1)
                    self.advance();self.assertIn(obstacle,field.progress(self.s)['completed'])
                    self.assertEqual(self.s['materialInventory'],before);self.assertEqual(self.s['sharedFunds'],funds)
                    self.assertEqual(field.vitality(self.s,'founder'),health)
                    self.assertIn(route[4],field.progress(self.s)['outcomes'][-1]['text'])
                    count+=1
        self.assertEqual(count,25)
    def test_low_attributes_never_block_existing_methods_and_forged_routes_are_atomic(self):
        self.s=self.rich()
        self.s['characterBuilds']['founder']['attributes']={k:1 for k in b.ATTRIBUTES}
        for obstacle in a.FIELD:
            self.at(obstacle)
            self.assertEqual(field.reasons(self.s,'founder',method='mundane'),[])
            for row in a.field_options(self.s,'founder'):
                self.reject('field-method',method=row['id'])
            self.reject('field-method',method='aptitude:made-up')
        self.reject('field-method',method='aptitude:lift',characterId='koharu')
    def test_present_capable_help_and_spell_charge_are_real_contributions(self):
        self.s=self.rich();self.at('stone')
        self.s['characterBuilds']['founder']['attributes']['might']=6
        self.s['characterSkills']['founder']['athletics']=1
        self.assertEqual(a.field_option(self.s,'founder','aptitude:lift')['check']['total'],8)
        self.s['characterBuilds']['mira']['attributes']['might']=6
        # A strong resident left at home must not qualify the route.
        self.assertFalse(a.field_option(self.s,'founder','aptitude:lift')['check']['qualified'])
        self.s['expedition']['companionId']='mira'
        self.assertEqual(a.field_option(self.s,'founder','aptitude:lift')['check']['total'],10)
        self.s['fieldMagic']['vitality']['mira']=0
        self.assertFalse(a.field_option(self.s,'founder','aptitude:lift')['check']['qualified'])
        self.s['expedition']['companionId']=None
        field.progress(self.s)['buffs']={'founder':{'strength':2}}
        before=deepcopy(self.s);field.view(self.s);self.assertEqual(before,self.s)
        self.act('field-method',method='aptitude:lift')
        self.assertEqual(field.progress(self.s)['buffs']['founder']['strength'],1)
        self.advance();self.assertEqual(field.progress(self.s)['buffs']['founder']['strength'],1)
    def test_all_social_alternatives_keep_original_choices_and_scoped_memories(self):
        count=0
        for key,d in social_content.CATALOGUE.items():
            for choice,definition in dialogue.definitions(key).items():
                self.s=g.new_campaign();self.boost()
                for who in d['participants']:self.member(who)
                if d['previous']:
                    self.act('share-social-conversation',sceneId=d['previous'],choice='warm');self.advance()
                row=social.row(self.s,key)
                self.assertTrue(set(d['choices']).issubset(row['choices']))
                before={k:deepcopy(v) for k,v in self.s.items() if k not in ('socialLife','journal','relationships','residentBonds')}
                self.act('share-social-conversation',sceneId=key,choice=choice)
                self.assertEqual(before,{k:self.s[k] for k in before})
                memory=social.saved(self.s)['memories'][key]
                self.assertEqual(memory['response'],definition['response']);self.assertEqual(memory['approachId'],choice)
                self.assertEqual(memory['choice'],definition['follows'])
                for p in d['participants']:self.assertIn(memory,social.context(self.s,p))
                self.reject('share-social-conversation',sceneId=key,choice=choice)
                count+=1
        self.assertEqual(count,36)
    def test_unqualified_social_approach_explains_requirement_without_hiding_originals(self):
        key='personal:mira:0';row=social.row(self.s,key)
        self.assertEqual(len(row['choices']),5)
        self.assertTrue(row['choices']['approach:0']['blockers'])
        self.reject('share-social-conversation',sceneId=key,choice='approach:0')
        self.act('share-social-conversation',sceneId=key,choice='candid')
        self.assertEqual(social.saved(self.s)['memories'][key]['choice'],'candid')
    def test_alternate_social_memory_continues_authored_followups_without_branch_key_errors(self):
        self.boost();self.act('share-social-conversation',sceneId='personal:mira:0',choice='approach:0')
        self.advance();row=social.row(self.s,'personal:mira:1')
        self.assertEqual(row['callback']['approachId'],'approach:0')
        self.act('share-social-conversation',sceneId='personal:mira:1',choice='curious');self.advance()
        self.assertTrue(social.row(self.s,'personal:mira:2')['available'])
    def test_older_sites_keep_all_ordinary_choices_and_add_real_one_phase_routes(self):
        import service_road as road
        steps=g.OBSERVATORY_STEPS+[g.OBSERVATORY_RECOVERY]+list(road.STEPS.values())
        self.s=self.rich();self.s['binderyDiscoveries']=['survey']
        self.act('start-expedition',siteId='rainward-observatory');self.advance();self.act('choose-expedition-approach',approach='survey')
        routes=[c for d in steps for k,c in d['choices'].items() if k.startswith('aptitude:')]
        self.assertEqual(len(routes),7)
        for c in routes:self.assertTrue(g.encounter_choice_blockers(self.s,c))
        self.boost()
        for c in routes:self.assertFalse(g.encounter_choice_blockers(self.s,c))
        self.act('choose-encounter-method',methodId='aptitude:read-gradient');self.advance()
        self.assertIn(g.OBSERVATORY_STEPS[0]['id'],self.s['observatoryProgress']['survey']['completedSteps'])
    def test_building_bonus_forecast_resolution_and_no_wasted_enchantment_charge(self):
        self.s['sharedFunds']=200;self.s['characterSkills']['founder']['athletics']=2
        self.act('hq-build',roomId='warehouse')
        self.s['spellSupports']['founder']={'construction':{'spellName':'True foundation','amount':1,'remaining':3}}
        forecast=g.headquarters.forecast(self.s);self.assertIn('+2 work',forecast[0])
        self.advance();self.assertTrue(g.headquarters.ready(self.s,'warehouse'))
        self.assertEqual(self.s['spellSupports']['founder']['construction']['remaining'],3)
    def test_channeling_improves_casting_and_ritual_pair_without_changing_existing_project(self):
        self.s=self.rich()
        for who in ('founder','mira'):self.s['characterSkills'][who]['channeling']=2
        d=g.SPELL_FORMS['research-lens'];summary=[]
        spell_support.resolve(self.s,d,'mira',summary,'founder')
        self.assertEqual(self.s['spellSupports']['mira'][d['support']['kind']]['remaining'],d['support']['charges']+1)
        self.assertEqual(rituals.ritual_phases(self.s,'archive-circle',['founder','mira']),4)
        self.act('begin-lasting-ritual',ritualId='archive-circle',leaderId='founder',partnerId='mira')
        self.assertEqual(rituals.state(self.s)['project']['requiredPhases'],4)
        self.advance(3);self.assertNotIn('archive-circle',rituals.state(self.s)['completed'])
        self.advance();self.assertIn('archive-circle',rituals.state(self.s)['completed'])
    def test_precision_bonus_does_not_turn_immune_spells_into_valid_attacks(self):
        self.s=self.rich();self.boost()
        key=magic_tests.MagicTests.learned(self,'fire-lance');self.at('ember')
        self.reject('field-spell',spellId=key,characterId='founder')
        self.at('briar');self.act('field-spell',spellId=key,characterId='founder');self.advance()
        self.assertEqual(field.progress(self.s)['enemyHp']['briar'],1)
    def test_retraining_restores_individual_baseline_and_refunds_only_paid_training(self):
        self.member('zahra');before=b.baseline('zahra')
        g.award_advancement(self.s,'zahra','fixture',10,'Fixture')
        self.act('train-character-build',characterId='zahra',buildKind='attribute',targetId='might');self.advance(3)
        self.assertEqual(b.build(self.s,'zahra')['attributes']['might'],before['might']+1)
        self.assertEqual(b.invested(self.s,'zahra'),3)
        self.act('start-retraining',characterId='zahra');self.advance()
        self.assertEqual(b.build(self.s,'zahra')['attributes'],before)
        self.assertEqual(b.invested(self.s,'zahra'),0)
    def test_readonly_views_do_not_spend_charges_reveal_future_replies_or_modify_builds(self):
        self.boost();before=deepcopy(self.s)
        for _ in range(2):
            g.public_state(self.s);social.view(self.s);b.view(self.s,'founder')
        self.assertEqual(before,self.s)
        row=social.row(self.s,'personal:mira:0')
        self.assertNotIn('response',row['choices']['approach:0'])
        self.assertEqual(social.row(self.s,'personal:mira:1')['opening'],'')

    def test_vitality_improves_recipient_recovery_and_never_exceeds_health_cap(self):
        self.s=self.rich();self.s['characterBuilds']['founder']['attributes']['vitality']=8
        field.initialize(self.s)['vitality']['founder']=1
        self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(field.vitality(self.s,'founder'),3)
        self.at('fire');self.act('field-method',method='bandage',targetId='founder');self.advance()
        self.assertEqual(field.vitality(self.s,'founder'),6)
        self.reject('field-method',method='bandage',targetId='founder')
