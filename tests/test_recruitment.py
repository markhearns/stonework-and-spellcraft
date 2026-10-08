from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, learn_for_character, character_assignment, character_sheet, research_work, spell_preparation_capacity, household_resident_room
from server import GameStore

class RecruitmentTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def introduce(self):
        self.state['binderyDiscoveries']=['salvage'];self.state['miraArchiveProject']['status']='complete'
        self.act('meet-candidate')
        for topic in ('work','home','plans'):self.act('talk-candidate',topic=topic)
    def prepare_room(self):
        self.state['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.act('fund-housing',roomId='west-chamber');self.advance(2)
    def recruit(self):
        self.introduce();self.prepare_room();self.act('invite-candidate',roomId='west-chamber');self.advance()
    def test_introduction_is_gated_and_conversations_are_free_idempotent(self):
        self.assertNotIn('tamsin',public_state(self.state)['characterCatalog'])
        self.reject('meet-candidate');self.state['binderyDiscoveries']=['salvage'];self.act('meet-candidate')
        self.reject('invite-candidate',roomId='west-chamber')
        before=deepcopy(self.state)
        self.act('talk-candidate',topic='home');self.act('talk-candidate',topic='home')
        self.assertEqual(len(self.state['additionalResidents']['tamsin']['conversation']),2)
        for key in ('dayNumber','currentDayPhase','sharedFunds','resonancePoints','relationshipDescription','materialInventory'):self.assertEqual(self.state[key],before[key])
    def test_named_arrival_reservation_protects_the_bed_and_only_advance_arrives(self):
        self.introduce();self.prepare_room();self.act('reserve-beds',roomId='west-chamber',reservedBeds=1)
        self.reject('invite-candidate',roomId='west-chamber');self.act('reserve-beds',roomId='west-chamber',reservedBeds=0)
        before=deepcopy(self.state);self.act('invite-candidate',roomId='west-chamber')
        self.assertNotIn('tamsin',public_state(self.state)['characterCatalog']);summary=public_state(self.state)['housingSummary']
        self.assertEqual(summary['rooms']['west-chamber']['arrivalReservedBeds'],1)
        self.assertEqual(summary['rooms']['west-chamber']['plannedReservedBeds'],0)
        self.reject('choose-bedroom',roomId='west-chamber',characterId='founder')
        self.reject('reserve-beds',roomId='west-chamber',reservedBeds=1)
        self.act('reserve-beds',roomId='west-chamber',reservedBeds=0)
        self.assertEqual(public_state(self.state)['housingSummary']['rooms']['west-chamber']['availableBeds'],0)
        self.assertEqual(self.state['currentDayPhase'],before['currentDayPhase'])
        self.advance();self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'resident')
        self.assertEqual(self.state['bedroomAssignments']['tamsin'],'west-chamber')
        self.assertEqual(public_state(self.state)['housingSummary']['residentCount'],2)
        self.assertEqual(public_state(self.state)['housingSummary']['occupiedBeds'],3)
        self.assertEqual(character_assignment(self.state,'tamsin'),'rest')
        self.assertEqual(self.state['relationshipDescription'],before['relationshipDescription'])
    def test_private_room_preference_and_offered_assignments_are_enforced(self):
        self.recruit();self.reject('choose-bedroom',roomId='bedchamber',characterId='tamsin')
        for assignment in ('garden','expedition','ritual','commissions'):self.reject('assign-character',characterId='tamsin',assignment=assignment)
        self.reject('start-expedition',companionId='tamsin')
        self.state['currentDayPhase']='evening';self.assertEqual(household_resident_room(self.state,'tamsin'),'west-chamber')
        self.assertEqual(public_state(self.state)['roomOccupants']['west-chamber'],['tamsin'])
    def test_third_resident_contributes_research_and_learns_independently(self):
        self.recruit();self.act('start-research');self.act('assign-founder',assignment='rest')
        self.act('assign-character',characterId='tamsin',assignment='archive');self.assertEqual(research_work(self.state),1)
        self.advance(3);self.assertIn('steady-hearth-wards',self.state['additionalResidents']['tamsin']['knownPrinciples'])
        self.assertNotIn('steady-hearth-wards',self.state['residentKnownPrinciples'])
        self.assertEqual(character_assignment(self.state,'tamsin'),'rest')
    def test_notebook_has_personal_time_knowledge_and_advancement(self):
        self.recruit();self.reject('start-resident-project',characterId='tamsin')
        self.state['libraryIndexInstalled']=True;self.state['materialInventory']['binding-thread']=2
        funds=self.state['sharedFunds'];self.act('start-resident-project',characterId='tamsin')
        self.assertEqual(self.state['sharedFunds'],funds-8);self.assertEqual(self.state['materialInventory']['binding-thread'],0)
        self.advance();self.act('assign-character',characterId='tamsin',assignment='rest');self.advance()
        self.assertEqual(self.state['additionalResidents']['tamsin']['personalProject']['completedWorkPhases'],1)
        self.act('assign-character',characterId='tamsin',assignment='personal-project');self.advance(2)
        self.assertIn('joined-fibres',self.state['additionalResidents']['tamsin']['knownPrinciples'])
        self.assertIn('joined-fibres',self.state['archivePrinciples']);self.assertNotIn('joined-fibres',self.state['founderKnownPrinciples'])
        self.assertEqual(character_sheet(self.state,'tamsin')['availableAdvancement'],2)
        self.reject('start-resident-project',characterId='tamsin')
    def test_shared_crafting_maker_remains_tamsin_and_press_bonus_applies(self):
        self.recruit();learn_for_character(self.state,'tamsin','joined-fibres')
        self.state['materialInventory']['porous-clay']=2;self.state['materialInventory']['binding-thread']=2
        self.act('prepare-practice',characterId='tamsin',practiceId='careful-assembly',prepared=True)
        self.act('start-crafting',recipeId='binding-press',materials=['porous-clay','binding-thread'],crafterId='tamsin')
        self.assertEqual(self.state['craftingProject']['crafterId'],'tamsin');self.assertEqual(self.state['residentAssignment'],'rest')
        self.assertEqual(public_state(self.state)['craftingWorkPerPhase'],2);self.advance(2)
        self.assertIn('artifact:binding-press',self.state['characterDevelopment']['tamsin']['advancementAwards'])
        self.act('place-utility-artifact',artifactId='binding-press',installed=True)
        self.act('start-crafting',recipeId='binding-press',materials=['porous-clay','binding-thread'],crafterId='tamsin')
        self.assertEqual(public_state(self.state)['craftingWorkPerPhase'],3)
    def test_two_person_ritual_does_not_assign_or_reward_third_resident(self):
        self.recruit();self.state['libraryIndexInstalled']=True
        for who in ('founder','mira'):
            for principle in ('reference-binding','clear-instruction'):learn_for_character(self.state,who,principle)
        self.state['materialInventory']['porous-clay']=2;self.state['materialInventory']['binding-thread']=2
        self.act('start-spell-ritual',materials=['porous-clay','binding-thread','porous-clay','binding-thread']);self.advance(2)
        self.assertEqual(self.state['spellRitual']['contributions'],{'founder':2,'mira':2})
        self.assertEqual(spell_preparation_capacity(self.state,'tamsin'),2)
        self.assertEqual(spell_preparation_capacity(self.state,'mira'),3)
        self.assertEqual(character_assignment(self.state,'tamsin'),'rest')
    def test_arrival_during_preagreed_travel_is_safe_but_remote_reassignment_is_not(self):
        self.introduce();self.prepare_room();self.act('invite-candidate',roomId='west-chamber')
        self.act('start-expedition');self.advance()
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'resident')
        self.reject('assign-character',characterId='tamsin',assignment='rest')
        self.assertIn('tamsin',public_state(self.state)['characterCatalog'])
    def test_schema_eleven_migration_and_invitation_retry_persist(self):
        self.introduce();self.prepare_room();old=deepcopy(self.state);old['schemaVersion']=11
        old.pop('additionalResidents');old.pop('pendingResidentArrival');old['utilityArtifactPlacements'].pop('binding-press')
        for field in ('characterDevelopment','characterSkills','trainingProjects','signatureFocuses','focusProjects','preparedSpells','spellWork'):old[field].pop('tamsin')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            self.assertTrue((Path(directory)/'campaign-before-schema-11-to-66.sqlite3').exists())
            self.assertEqual(state['bedroomAssignments'],old['bedroomAssignments']);self.assertEqual(state['sharedFunds'],old['sharedFunds'])
            def call(kind,**fields):return store.action({'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind,**fields}})
            call('meet-candidate')
            for topic in ('work','home','plans'):call('talk-candidate',topic=topic)
            request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'invite-candidate','roomId':'west-chamber'}}
            once=store.action(request);self.assertEqual(store.action(request),once)
            self.assertEqual(GameStore(directory).read()['pendingResidentArrival']['roomId'],'west-chamber')
            call('advance');self.assertEqual(GameStore(directory).read()['additionalResidents']['tamsin']['status'],'resident')



    def test_personal_styles_are_independent_free_and_persistent(self):
        self.reject('style-resident',outerLayer='plum-shawl')
        self.recruit();before=deepcopy(self.state)
        self.act('style-resident',outerLayer='plum-shawl');self.act('save-resident-style',name='By the lamp')
        self.act('style-resident',outerLayer='none');self.act('load-resident-style',name='By the lamp')
        record=self.state['additionalResidents']['tamsin']
        self.assertEqual(record['wardrobe']['outerLayer'],'plum-shawl')
        self.assertEqual(self.state['wardrobe'],before['wardrobe'])
        for key in ('dayNumber','currentDayPhase','resonancePoints','sharedFunds','characterDevelopment'):
            self.assertEqual(self.state[key],before[key])
        self.act('save-resident-style',name='By the lamp');self.assertEqual(len(record['savedStyles']),1)
        self.reject('style-resident',outerLayer='unsupported');self.reject('load-resident-style',name='missing')
        self.assertEqual(public_state(json.loads(json.dumps(self.state)))['additionalResidents']['tamsin']['savedStyles'],record['savedStyles'])

    def test_optional_scenes_are_separate_and_rewards_cannot_repeat(self):
        from game import resonance_forecast
        from dialogue import dialogue_context
        self.recruit();self.reject('join-resident-scene',sceneId='tea-and-margins')
        record=self.state['additionalResidents']['tamsin'];record['personalProject']['status']='complete'
        self.reject('join-resident-scene',sceneId='a-playful-margin')
        before=deepcopy(self.state)
        self.act('join-resident-scene',sceneId='tea-and-margins');self.act('join-resident-scene',sceneId='tea-and-margins')
        self.assertEqual(self.state['resonancePoints'],before['resonancePoints'])
        self.act('join-resident-scene',sceneId='a-playful-margin');self.act('join-resident-scene',sceneId='a-playful-margin')
        self.assertEqual(self.state['resonancePoints'],before['resonancePoints']+2)
        self.assertEqual(len(record['completedScenes']),2)
        for key in ('relationshipDescription','conversation','characterDevelopment','sharedFunds','dayNumber','currentDayPhase'):
            self.assertEqual(self.state[key],before[key])
        self.assertEqual(resonance_forecast(self.state),0)
        self.state['roomFurnishings']['common-room']='velvet-settee'
        self.assertEqual(resonance_forecast(self.state),1)
        self.state['completedDevelopments'].append('shared-flirtation')
        self.assertEqual(resonance_forecast(self.state),2)
        self.assertIn('mutually welcomed flirtation',dialogue_context(self.state,'Tea?','tamsin')[0]['content'])
        self.act('start-expedition')
        self.reject('style-resident',outerLayer='none')
        self.reject('join-resident-scene',sceneId='tea-and-margins')
