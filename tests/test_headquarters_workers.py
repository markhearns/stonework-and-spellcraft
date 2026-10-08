"""Resident work: concurrency, save continuity, travel, and transaction boundaries."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
import game as g
import headquarters as h
import living_stories
import guidance
import progression
import room_life
import summoning
import local_encounters
from server import GameStore


class HeadquartersWorkerTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign('fresh')
        self.s['sharedFunds']=500
        for who in ('brakka','maren'):
            self.s['localEncounterCandidates'][who]=local_encounters.definition(self.s,who)
            summoning.initialize_person(self.s,who,summoned=False)
            self.s['additionalResidents'][who]['status']='resident'
            self.s['residency'][who]['residencyStatus']='resident'
            self.s['housingRooms']['garden-chamber']['status']='complete'
            self.s['bedroomAssignments'][who]='garden-chamber'
        for room in ('warehouse','workshop','smithy','enchanting-room','command-room','training-yard'):
            self.s['headquarters']['rooms'][room]='complete'

    def act(self,kind,**kwargs):g.apply_action(self.s,dict(type=kind,**kwargs))
    def agree(self,who):self.act('hq-agree-work',workerId=who,enabled=True)
    def reject(self,kind,**kwargs):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kwargs)
        self.assertEqual(self.s,before)
    def advance(self,n=1):
        for _ in range(n):self.act('advance')

    def test_agreement_is_explicit_free_and_not_an_assignment(self):
        self.reject('hq-job',workerId='brakka',jobId='metalware')
        before=deepcopy(self.s);self.agree('brakka')
        for key in ('sharedFunds','dayNumber','currentDayPhase','additionalResidents'):self.assertEqual(self.s[key],before[key])
        self.act('hq-agree-work',workerId='brakka',enabled=False)
        self.reject('hq-job',workerId='brakka',jobId='metalware')
        self.reject('hq-agree-work',workerId='brakka',enabled='true')
        self.reject('hq-agree-work',workerId=[],enabled=True)

    def test_three_facilities_progress_and_complete_independently(self):
        for who in ('brakka','maren'):self.agree(who)
        self.act('hq-job',workerId='brakka',jobId='metalware')
        self.act('hq-build',workerId='maren',roomId='chapel')
        self.act('hq-job',jobId='briefing')
        self.assertEqual(len(h.projects(self.s)),3)
        self.assertEqual(room_life.location(self.s,'brakka'),'smithy')
        self.assertEqual(room_life.location(self.s,'maren'),'chapel')
        before=deepcopy(self.s);preview=guidance.preview(self.s)
        self.assertEqual(self.s,before)
        rows={p['id']:p for p in preview['projects']}
        self.assertGreater(rows['headquarters:brakka']['progress'],0)
        self.assertGreater(rows['headquarters:maren']['progress'],0)
        self.advance(2)
        self.assertTrue(h.ready(self.s,'chapel'))
        self.assertEqual(self.s['headquarters']['stock']['metalware'],1)
        self.assertTrue(self.s['headquarters']['briefing'])
        self.assertEqual(h.projects(self.s),{})
        self.advance(2);self.assertEqual(self.s['headquarters']['stock']['metalware'],1)

    def test_worker_and_facility_cannot_be_double_booked_even_when_paused(self):
        for who in ('brakka','maren'):self.agree(who)
        self.act('hq-job',workerId='brakka',jobId='blade')
        self.act('hq-pause',workerId='brakka')
        self.reject('hq-job',workerId='maren',jobId='metalware')
        self.reject('hq-build',workerId='brakka',roomId='chapel')
        self.reject('hq-agree-work',workerId='brakka',enabled=False)
        self.assertTrue(any('headquarters' in b for b in summoning.departure_blockers(self.s,'brakka')))

    def test_construction_requires_workers_own_knowledge(self):
        self.agree('maren');g.learn_for_character(self.s,'founder','water-guidance')
        self.s['facilityProjects']['washroom']['status']='complete'
        self.s['additionalResidents']['maren']['knownPrinciples']=[]
        self.reject('hq-build',workerId='maren',roomId='pool')
        g.learn_for_character(self.s,'maren','water-guidance')
        self.act('hq-build',workerId='maren',roomId='pool')
        self.assertEqual(h.project_for(self.s,'maren')['cost'],45)

    def test_drills_stay_personal_and_crafting_offer_is_required(self):
        self.agree('brakka');self.reject('hq-job',workerId='brakka',jobId='basic-drill')
        self.s['people']['brakka']['offeredAssignments']=['rest']
        self.reject('hq-job',workerId='brakka',jobId='metalware')
        self.act('hq-job',jobId='basic-drill');self.advance(2)
        self.assertIn('headquarters:basic-drill',self.s['characterDevelopment']['founder']['advancementAwards'])

    def test_workers_continue_during_scholar_travel(self):
        self.agree('brakka');self.act('hq-job',workerId='brakka',jobId='metalware')
        self.act('start-expedition',siteId='old-waterworks',carryLantern=False)
        self.advance()
        self.assertEqual(h.project_for(self.s,'brakka')['done'],1)
        self.reject('hq-cancel',workerId='brakka')
        self.act('choose-expedition-approach',approach='salvage');self.advance()
        self.assertEqual(self.s['headquarters']['stock']['metalware'],1)
        self.assertIsNone(h.project_for(self.s,'brakka'))

    def test_travelling_worker_pauses_and_funded_progress_survives(self):
        self.agree('brakka');self.act('hq-job',workerId='brakka',jobId='blade');self.advance()
        paid=deepcopy(h.project_for(self.s,'brakka'))
        self.act('agree-household-role',characterId='brakka',role='fieldwork',enabled=True,willingnessReviewed=True)
        self.act('start-expedition',siteId='old-waterworks',carryLantern=False,companionId='brakka')
        self.advance();self.assertEqual(h.project_for(self.s,'brakka'),paid)
        self.act('return-expedition');self.advance()
        self.assertEqual(h.project_for(self.s,'brakka'),paid)
        self.assertEqual(g.character_assignment(self.s,'brakka'),'rest')
        self.act('hq-resume',workerId='brakka');self.advance(2)
        self.assertEqual(self.s['headquarters']['stock']['blade'],1)

    def test_pause_resume_arrangement_and_actual_assignments(self):
        self.agree('brakka');self.act('hq-job',workerId='brakka',jobId='blade');self.advance()
        self.act('save-work-arrangement',name='Forge day')
        self.act('assign-character',characterId='brakka',assignment='rest');self.advance()
        self.assertEqual(h.project_for(self.s,'brakka')['done'],1)
        rows=progression.view(self.s)['projects'];row=next(p for p in rows if p['id']=='headquarters:brakka')
        self.assertTrue(row['canResume']);self.assertEqual(row['assignmentImpact'][0]['personId'],'brakka')
        self.act('apply-work-arrangement',name='Forge day');self.advance()
        self.assertEqual(h.project_for(self.s,'brakka')['done'],2)
        self.act('hq-pause',workerId='brakka');self.act('resume-project',projectId='headquarters:brakka');self.advance()
        self.assertEqual(self.s['headquarters']['stock']['blade'],1)

    def test_cancel_refunds_exactly_and_does_not_cancel_other_job(self):
        self.agree('brakka');self.s['headquarters']['stock']['armour']=1
        before=self.s['sharedFunds'];self.act('hq-job',workerId='brakka',jobId='enchant-armour')
        self.act('hq-build',roomId='chapel');self.advance()
        self.act('hq-cancel',workerId='brakka')
        self.assertEqual(self.s['sharedFunds'],before-18)
        self.assertEqual(self.s['headquarters']['stock']['armour'],1)
        self.assertIsNotNone(h.project_for(self.s))
        self.reject('hq-cancel',workerId='brakka')
        self.advance();self.assertTrue(h.ready(self.s,'chapel'))

    def test_cancellation_preserves_a_different_current_assignment(self):
        self.agree('brakka');self.act('hq-job',workerId='brakka',jobId='blade')
        self.act('assign-character',characterId='brakka',assignment='rest')
        self.act('hq-cancel',workerId='brakka');self.assertEqual(g.character_assignment(self.s,'brakka'),'rest')

    def test_specialist_can_install_own_facility_but_other_workers_cannot(self):
        for who in ('brakka','maren'):self.agree(who)
        scene=living_stories.CHAINS['brakka']
        self.act('choose-living-scene',sceneId='brakka:0',choice=next(iter(scene['choices'])))
        self.reject('hq-job',workerId='maren',jobId='specialty-brakka')
        self.act('hq-job',workerId='brakka',jobId='specialty-brakka')
        self.act('start-expedition',siteId='old-waterworks',carryLantern=False);self.advance()
        self.act('choose-expedition-approach',approach='salvage');self.advance()
        self.act('return-expedition');self.advance()
        self.assertEqual(self.s['headquarters']['stock']['specialty:brakka'],1)

    def test_mira_can_agree_and_resume_through_generic_assignment(self):
        self.s=g.new_campaign('demo');self.s['headquarters']['rooms']['smithy']='complete'
        self.agree('mira');self.act('hq-job',workerId='mira',jobId='metalware')
        self.act('assign-character',characterId='mira',assignment='rest')
        self.act('assign-character',characterId='mira',assignment='headquarters');self.advance(2)
        self.assertEqual(self.s['headquarters']['stock']['metalware'],1)

    def test_duplicate_briefings_across_facilities_are_blocked(self):
        self.agree('brakka');self.s['headquarters']['rooms']['guard-barracks']='complete'
        self.s['headquarters']['stock']['specialty:aurelia']=1
        self.act('hq-job',workerId='brakka',jobId='briefing')
        self.reject('hq-job',jobId='watch-briefing')

    def test_invalid_worker_and_funding_failure_do_not_mutate_state(self):
        self.reject('hq-build',workerId=['brakka'],roomId='chapel')
        self.reject('hq-build',workerId='missing',roomId='chapel')
        self.agree('brakka');self.s['sharedFunds']=0
        self.reject('hq-job',workerId='brakka',jobId='metalware')
        self.s['additionalResidents']['brakka']['status']='visiting'
        self.reject('hq-agree-work',workerId='brakka',enabled=True)

    def test_v071_migration_preserves_every_old_field_and_asset(self):
        self.s['headquarters']['stock']['armour']=1
        self.act('hq-job',jobId='enchant-armour');self.advance()
        old=deepcopy(self.s);old['schemaVersion']=58
        old['headquarters'].pop('workerProjects');old['headquarters'].pop('workAgreements')
        old['assetOverrides']={'mira':'/user-assets/accepted.webp'}
        with tempfile.TemporaryDirectory() as folder:
            store=GameStore(folder);asset=Path(folder,'assets','accepted.webp');asset.parent.mkdir(exist_ok=True);asset.write_bytes(b'custom artwork retained')
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
            store=GameStore(folder);new=store.read()
            expected=deepcopy(old);expected['schemaVersion']=66;expected['revision']+=1
            expected['headquarters'].update(workerProjects={},workAgreements=[])
            self.assertEqual(new,expected)
            self.assertTrue(Path(folder,'campaign-before-schema-58-to-66.sqlite3').is_file())
            self.assertEqual(asset.read_bytes(),b'custom artwork retained')
            self.s=new;self.advance(2)
            self.assertEqual(self.s['headquarters']['stock']['warded-armour'],1)

    def test_multiple_jobs_reload_and_retried_funding_cannot_duplicate(self):
        self.agree('brakka')
        with tempfile.TemporaryDirectory() as folder:
            store=GameStore(folder)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
            payload={'action':{'type':'hq-job','jobId':'blade','workerId':'brakka'},'requestId':'v072-job','expectedRevision':self.s['revision']}
            first=store.action(payload);again=store.action(payload)
            self.assertEqual(first,again)
            current=GameStore(folder).read();self.assertEqual(h.project_for(current,'brakka')['cost'],16)
            self.assertEqual(current['sharedFunds'],self.s['sharedFunds']-16)

if __name__=='__main__':unittest.main()
