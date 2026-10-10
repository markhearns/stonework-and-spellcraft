from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import game as g
import headquarters as h
import living_stories as life
import local_encounters as local
import resident_specialties as specialties
import service_road as road
import room_life
import progression
import summoning
from server import GameStore

class ResidentFutureTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign('fresh')
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**kw):
        old=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(old,self.s)
    def member(self,who):
        if who=='sabine':
            import containment
            self.s['reviewedCandidates'][who]=deepcopy(containment.SABINE)
        if who in local.PEOPLE:
            self.s['localEncounterCandidates'][who]=local.definition(self.s,who)
            summoning.initialize_person(self.s,who,summoned=False)
        elif who!='tamsin':summoning.initialize_person(self.s,who)
        self.s['additionalResidents'][who]['status']='resident'
        if who in self.s['residency']:self.s['residency'][who]['residencyStatus']='resident'
        self.s['housingRooms']['garden-chamber']['status']='complete';self.s['bedroomAssignments'][who]='garden-chamber'
    def room(self,key):
        if key=='conservatory':self.s['restorationStatus']='complete'
        elif key in ('kitchen','washroom'):self.s['facilityProjects'][key]['status']='complete'
        elif key not in ('library','common-room'):self.s['headquarters']['rooms'][key]='complete'
    def first_scene(self,who):
        self.room(life.CHAINS[who]['roomId'])
        self.act('choose-living-scene',sceneId=who+':0',choice=next(iter(life.CHAINS[who]['choices'])))
    def open_road(self):
        for key in ('quarry-shelter','ridge-cistern'):g.discoveries_for(self.s,key).append('survey')
    def set_out(self):
        self.act('start-expedition',siteId=road.SITE);self.advance();self.act('choose-expedition-approach',approach='survey')
    def method(self,key):
        self.act('choose-encounter-method',methodId=key)
        while self.s['expedition']['stage']=='working':self.advance()
    def test_elf_introductions_are_gated_ordinary_contacts_with_stable_profiles(self):
        for who in ('elowen','nyssara'):self.reject('start-local-visit',encounterId=who)
        self.act('start-research');self.advance(3)
        self.act('start-local-visit',encounterId='elowen');self.advance()
        self.assertEqual(self.s['people']['elowen']['ancestryLabel'],'High elf')
        self.assertEqual(self.s['residency']['elowen']['residencyStatus'],'remote')
        self.assertNotIn('elowen',g.household_members(self.s))
        g.discoveries_for(self.s,'ridge-cistern').append('survey')
        self.act('start-local-visit',encounterId='nyssara');self.advance()
        self.assertEqual(self.s['people']['nyssara']['ancestryLabel'],'Drow')
        self.assertEqual(g.ORIGINAL_ASSETS['nyssara'],'/assets/portraits/nyssara.webp')
    def test_twelve_specialties_reject_missing_resident_and_duplicate_building(self):
        self.assertEqual(len(specialties.SPECIALTIES),14)
        for who,d in specialties.SPECIALTIES.items():
            with self.subTest(who=who):
                self.s=g.new_campaign('fresh');self.s['sharedFunds']=500;self.room(d['room'])
                self.reject('hq-job',jobId='specialty-'+who)
                self.member(who);self.reject('hq-job',jobId='specialty-'+who)
                self.first_scene(who);before=self.s['sharedFunds']
                self.act('hq-job',jobId='specialty-'+who);self.assertEqual(self.s['sharedFunds'],before-d['cost'])
                self.advance(d['phases']);self.assertTrue(specialties.active(self.s,who))
                self.reject('hq-job',jobId='specialty-'+who)
    def test_specialist_absence_pauses_build_and_cancel_refunds(self):
        self.member('koharu');self.room('workshop');self.first_scene('koharu');self.s['sharedFunds']=100
        self.act('hq-job',jobId='specialty-koharu');self.advance()
        self.s['residency']['koharu']['residencyStatus']='away';self.s['additionalResidents']['koharu']['status']='away'
        self.advance();self.assertEqual(self.s['headquarters']['project']['done'],1)
        self.reject('hq-resume')
        self.act('hq-cancel');self.assertEqual(self.s['sharedFunds'],100)
    def test_scene_choice_changes_followup_and_grants_no_resources_or_time(self):
        self.member('koharu');self.room('workshop')
        before=deepcopy(self.s);self.act('choose-living-scene',sceneId='koharu:0',choice='quiet')
        for field in ('dayNumber','currentDayPhase','sharedFunds','materialInventory','characterDevelopment','founderAssignment'):self.assertEqual(before[field],self.s[field])
        self.reject('choose-living-scene',sceneId='koharu:0',choice='visible')
        self.reject('choose-living-scene',sceneId='koharu:1',choice='method')
        self.s['researchStatus']='complete';g.learn_for_character(self.s,'founder','steady-hearth-wards');self.s['sharedFunds']=50
        self.act('focus-research',researchId='archive-foundations',leaderId='founder')
        self.act('assign-character',characterId='koharu',assignment='archive');self.advance()
        row=next(r for r in life.rows(self.s) if r['id']=='koharu:1')
        self.assertTrue(row['available']);self.assertIn('felt right in the hand',row['opening'])
        self.act('choose-living-scene',sceneId='koharu:1',choice='method')
        self.assertEqual(self.s,json.loads(json.dumps(self.s)))
    def test_merely_assigned_resident_does_not_count_as_shared_contributor(self):
        self.member('koharu');self.s['researchStatus']='complete';g.learn_for_character(self.s,'founder','steady-hearth-wards')
        self.act('focus-research',researchId='archive-foundations',leaderId='founder');self.s['researchProjects']['archive-foundations']['completedWorkPhases']=2
        self.act('assign-character',characterId='koharu',assignment='archive');self.advance()
        self.assertFalse(self.s['livingStories']['sharedWork'].get('koharu'))
    def test_review_can_be_cancelled_after_resident_leaves(self):
        self.member('koharu');self.first_scene('koharu')
        for who in ('founder','koharu'):g.learn_for_character(self.s,who,'steady-hearth-wards')
        self.act('start-shared-review',characterId='koharu')
        self.s['residency']['koharu']['residencyStatus']='remote';self.s['additionalResidents']['koharu']['status']='away'
        self.advance();self.assertIsNotNone(self.s['livingStories']['review'])
        self.act('cancel-shared-review');self.assertIsNone(self.s['livingStories']['review']);self.assertEqual(self.s['founderAssignment'],'rest')

    def test_shared_review_opens_followup_without_new_research_or_double_work(self):
        self.member('koharu');self.first_scene('koharu')
        self.reject('start-shared-review',characterId='koharu')
        for who in ('founder','koharu'):g.learn_for_character(self.s,who,'steady-hearth-wards')
        self.act('assign-founder',assignment='commissions');money=self.s['sharedFunds']
        self.act('start-shared-review',characterId='koharu')
        self.advance();self.assertEqual(self.s['sharedFunds'],money)
        self.assertEqual(self.s['founderAssignment'],'commissions')
        self.assertTrue(next(r for r in life.rows(self.s) if r['id']=='koharu:1')['available'])
        self.advance();self.assertEqual(self.s['sharedFunds'],money+g.copying_income(self.s))
        self.reject('start-shared-review',characterId='koharu')

    def test_routines_use_ready_rooms_and_assignments_take_priority(self):
        self.member('zahra');self.s['currentDayPhase']='afternoon';self.s['dayNumber']=1
        self.assertEqual(room_life.location(self.s,'zahra'),'common-room')
        self.room('pool');self.assertEqual(room_life.location(self.s,'zahra'),'pool')
        self.s['additionalResidents']['zahra']['assignment']='archive';self.assertEqual(room_life.location(self.s,'zahra'),'library')
        before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
    def test_specialist_benefits_are_exact_and_persist_after_departure(self):
        income=g.copying_income(self.s);research=g.work_contribution(self.s,'founder','archive-focus');craft=g.work_contribution(self.s,'founder','careful-assembly');slots=g.spell_preparation_capacity(self.s)
        for who in specialties.SPECIALTIES:self.s['headquarters']['stock']['specialty:'+who]=1
        self.assertEqual(g.copying_income(self.s),income+2)
        self.assertEqual(g.work_contribution(self.s,'founder','archive-focus'),research)
        self.assertEqual(g.work_contribution(self.s,'founder','careful-assembly'),craft+1)
        self.assertEqual(g.spell_preparation_capacity(self.s),slots+1)
        self.s['restorationStatus']='complete';self.s['gardenProductionChoice']='surplus-sales'
        self.assertEqual(g.garden_harvest(self.s)['amount'],0)
        self.act('assign-gardener',characterId='founder');self.assertEqual(g.garden_harvest(self.s)['amount'],6)
    def test_specialist_production_jobs_require_facility_and_conserve_cancel_costs(self):
        self.s['sharedFunds']=100;self.room('workshop');self.room('enchanting-room')
        for job,who,material,n in [('prepare-fireglass','nyssara','fireglass',2),('assess-deep-samples','nyssara','moon-glass',1)]:
            self.s['headquarters']['stock'].pop('specialty:'+who,None)
            self.reject('hq-job',jobId=job);self.s['headquarters']['stock']['specialty:'+who]=1
            before=self.s['materialInventory'][material];money=self.s['sharedFunds'];self.act('hq-job',jobId=job);self.advance();self.act('hq-cancel')
            self.assertEqual(self.s['sharedFunds'],money);self.assertEqual(self.s['materialInventory'][material],before)
            self.act('hq-job',jobId=job);self.advance(2);self.assertEqual(self.s['materialInventory'][material],before+n)
    def test_long_journey_branches_persists_partial_work_and_rewards_only_on_return(self):
        for route,stage,reward in [('channel','channel','porous-clay'),('orchard','orchard','silver-ivy')]:
            with self.subTest(route=route):
                self.s=g.new_campaign('fresh');self.reject('start-expedition',siteId=road.SITE);self.open_road();self.set_out()
                self.reject('advance');self.reject('choose-encounter-method',methodId='bad')
                self.act('choose-encounter-method',methodId=route);self.advance()
                self.act('return-expedition');self.advance();self.assertFalse(g.discoveries_for(self.s,road.SITE))
                self.s=json.loads(json.dumps(self.s));self.set_out();self.assertEqual(self.s['expedition']['remainingWorkPhases'],1);self.advance()
                self.assertEqual(g.encounter_view(self.s)['step']['id'],stage)
                self.method('measure' if route=='channel' else 'steps');self.method('draw')
                before=deepcopy(self.s['materialInventory']);money=self.s['sharedFunds'];self.method('cord')
                self.assertEqual(self.s['materialInventory'],before);self.assertFalse(g.discoveries_for(self.s,road.SITE))
                self.act('return-expedition');self.advance();self.assertEqual(g.discoveries_for(self.s,road.SITE),['survey'])
                self.assertEqual(self.s['materialInventory'][reward],before[reward]+2);self.assertEqual(self.s['sharedFunds'],money+12)
                self.assertEqual(self.s['materialInventory']['binding-thread'],before['binding-thread']+3)
                self.reject('start-expedition',siteId=road.SITE)
    def test_sorting_bench_requires_returned_plan_and_is_once_only(self):
        self.s['sharedFunds']=100;self.room('workshop');self.reject('hq-job',jobId='sorting-bench')
        self.s['serviceRoad']['discoveries']=['survey'];before=g.work_contribution(self.s,'founder','careful-assembly')
        self.act('hq-job',jobId='sorting-bench');self.advance(2)
        self.assertEqual(g.work_contribution(self.s,'founder','careful-assembly'),before+1);self.reject('hq-job',jobId='sorting-bench')
    def test_fenna_bonus_only_for_a_new_returned_lead(self):
        self.s['headquarters']['stock']['specialty:fenna']=1;before=self.s['materialInventory']['binding-thread']
        self.act('start-expedition',siteId='old-waterworks');self.advance();self.act('choose-expedition-approach',approach='survey');self.advance(2)
        self.assertEqual(self.s['materialInventory']['binding-thread'],before)
        self.act('return-expedition');self.advance();self.assertEqual(self.s['materialInventory']['binding-thread'],before+1)
        self.act('start-expedition',siteId='old-waterworks');self.act('return-expedition');self.advance();self.assertEqual(self.s['materialInventory']['binding-thread'],before+1)
    def test_one_click_resume_preserves_paid_work_and_money(self):
        self.act('start-research');self.advance();self.act('assign-founder',assignment='rest')
        before=self.s['sharedFunds'];self.act('resume-project',projectId='hearth')
        self.assertEqual(self.s['founderAssignment'],'research');self.assertEqual(self.s['sharedFunds'],before)
        self.assertEqual(self.s['researchCompletedPhases'],1)
        self.reject('resume-project',projectId='bad')
    def test_affordable_guidance_and_upgrade_migration_preserve_artwork(self):
        before=deepcopy(self.s);v=progression.view(self.s);self.assertEqual(before,self.s)
        self.assertTrue(any(r['affordable'] for r in v['upgrades']))
        old=deepcopy(self.s);old['schemaVersion']=41;old.pop('livingStories');old.pop('serviceRoad')
        for who in ('elowen','nyssara'):old['localEncounters'].pop(who)
        old['people']['tamsin']['ancestryLabel']='Human';old['assetOverrides']={'tamsin':'/user-assets/accepted.png'};old['assetHistory']={'tamsin':['/user-assets/previous.png']}
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
            upgraded=GameStore(directory).read();self.assertEqual(upgraded['schemaVersion'],66)
            self.assertEqual(upgraded['people']['tamsin']['ancestryLabel'],'Catfolk')
            for key in ('assetOverrides','assetHistory','additionalResidents','sharedFunds','materialInventory'):self.assertEqual(upgraded[key],old[key])
            self.assertTrue(Path(directory,f"campaign-before-schema-41-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            self.assertEqual(upgraded,g.migrate_state(deepcopy(upgraded)))

    def test_requested_roster_has_unique_names_and_exact_room_associations(self):
        expected={'rhess':'watchtower','velis':'supply-office','sabine':'dungeons','koharu':'workshop','zahra':'smithy','fenna':'common-room','iona':'command-room','kaede':'training-yard','tamsin':'kitchen','elowen':'infirmary','nyssara':'enchanting-room','neris':'hot-spring','aurelia':'guard-barracks','sylva':'conservatory'}
        self.assertEqual({who:d['room'] for who,d in specialties.SPECIALTIES.items()},expected)
        self.assertEqual({who:life.CHAINS[who]['roomId'] for who in expected},expected)
        import containment
        names=[d['name'] for d in local.PEOPLE.values()]+[d['profile']['name'] for d in summoning.CANDIDATES.values()]+[d['candidate']['profile']['name'] for d in containment.CASES.values()]+['Tamsin','Mira']
        self.assertEqual(len(names),len(set(names)))
        self.assertNotEqual(g.ORIGINAL_ASSETS['nyssara'],g.ORIGINAL_ASSETS['sabine'])
        self.assertNotIn('veyra',containment.CASES)
    def test_dryad_discovery_requires_ritual_before_visit_and_keeps_identity(self):
        self.reject('start-local-visit',encounterId='sylva')
        self.s['restorationStatus']='complete';g.discoveries_for(self.s,'fern-nursery').append('survey')
        self.act('start-local-visit',encounterId='sylva');self.advance()
        self.assertNotIn('sylva',self.s['people'])
        self.assertEqual(summoning.candidate_catalogue(self.s)['sylva']['profile']['ancestryLabel'],'Dryad')
        self.reject('summoning-prepare',candidateId='sylva',conductorId='founder',materials=['porous-clay','binding-thread'])
        g.learn_for_character(self.s,'founder','courteous-passage')
        for key in self.s['materialInventory']:self.s['materialInventory'][key]=10
        self.act('summoning-prepare',candidateId='sylva',conductorId='founder',materials=['porous-clay','binding-thread']);self.advance(2)
        self.assertEqual(self.s['people']['sylva']['name'],'Sylva')
        self.assertNotIn('sylva',g.household_members(self.s))
    def test_forge_speed_is_visible_and_only_changes_new_jobs(self):
        self.room('smithy');self.s['sharedFunds']=100
        self.act('hq-job',jobId='metalware');self.assertEqual(self.s['headquarters']['project']['phases'],2)
        self.s['headquarters']['stock']['specialty:zahra']=1
        self.assertEqual(h.view(self.s)['jobs']['metalware']['phases'],1)
        self.advance();self.assertIsNotNone(self.s['headquarters']['project'])
        self.advance();self.assertEqual(self.s['headquarters']['stock']['metalware'],1)
        self.act('hq-job',jobId='metalware');self.advance();self.assertEqual(self.s['headquarters']['stock']['metalware'],2)
    def test_specialist_drills_award_once_and_watch_briefings_do_not_stack(self):
        for who,job,award in [('kaede','advanced-control-drill',2),('neris','thermal-balance-study',1),('aurelia','watch-drill',2)]:
            self.room(specialties.SPECIALTIES[who]['room']);self.reject('hq-job',jobId=job)
            self.s['headquarters']['stock']['specialty:'+who]=1
            if who=='kaede':
                self.reject('hq-job',jobId=job)
                self.s['headquarters']['stock'].update(blade=1,armour=1)
            before=sum(a['points'] for a in self.s['characterDevelopment']['founder']['advancementAwards'].values())
            self.act('hq-job',jobId=job);self.advance(h.JOBS[job]['phases'])
            self.assertEqual(sum(a['points'] for a in self.s['characterDevelopment']['founder']['advancementAwards'].values()),before+award)
            self.reject('hq-job',jobId=job)
        self.act('hq-job',jobId='watch-briefing');self.advance();self.assertTrue(self.s['headquarters']['briefing'])
        self.reject('hq-job',jobId='watch-briefing');self.room('command-room');self.reject('hq-job',jobId='briefing')
    def test_dryad_beds_improve_only_staffed_ivy_and_kitchen_only_staffed_sales(self):
        self.s['restorationStatus']='complete';self.s['headquarters']['stock'].update({'specialty:sylva':1,'specialty:tamsin':1})
        self.s['utilityArtifactPlacements']['root-tender']=True
        self.assertEqual(g.garden_harvest(self.s)['amount'],1)
        self.act('assign-gardener',characterId='founder');self.assertEqual(g.garden_harvest(self.s)['amount'],2)
        self.s['gardenProductionChoice']='surplus-sales';self.assertEqual(g.garden_harvest(self.s)['amount'],6)
        self.act('assign-founder',assignment='rest');self.assertEqual(g.garden_harvest(self.s)['amount'],2)
    def test_previous_paid_specialties_preserve_bonuses_and_accepted_art(self):
        self.s['schemaVersion']=42;self.s['headquarters'].pop('legacySpecialties')
        self.s['headquarters']['stock'].update({'specialty:zahra':1,'specialty:tamsin':1,'specialty:kaede':1})
        self.s['assetOverrides']['neris']='/api/assets/accepted-neris.png'
        research=g.work_contribution(self.s,'founder','archive-focus')
        g.migrate_state(self.s)
        self.assertEqual(self.s['schemaVersion'],66)
        self.assertEqual(g.work_contribution(self.s,'founder','archive-focus'),research+1)
        self.assertEqual(self.s['assetOverrides']['neris'],'/api/assets/accepted-neris.png')
        self.s['restorationStatus']='complete';self.s['gardenProductionChoice']='surplus-sales';self.act('assign-gardener',characterId='founder')
        self.assertEqual(g.garden_harvest(self.s)['amount'],6)
        self.room('workshop');self.s['sharedFunds']=100
        self.act('hq-job',jobId='prepare-fireglass');self.advance(2)
        self.assertEqual(self.s['materialInventory']['fireglass'],2)

if __name__=='__main__':unittest.main()
