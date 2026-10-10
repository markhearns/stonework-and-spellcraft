from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign,apply_action,RuleError,learn_for_character,award_advancement,character_sheet,public_state
from server import GameStore

class LessonTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign();learn_for_character(self.state,'mira','gentle-preservation')
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def lesson(self):self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='principle',targetId='gentle-preservation')
    def test_principle_lesson_commits_two_people_and_teaches_only_learner(self):
        before=deepcopy(self.state);self.lesson()
        self.assertEqual(self.state['residentAssignment'],'teaching');self.assertEqual(self.state['founderAssignment'],'training')
        self.assertNotIn('gentle-preservation',self.state['founderKnownPrinciples'])
        self.act('advance');self.assertIn('gentle-preservation',self.state['founderKnownPrinciples'])
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds']);self.assertEqual(self.state['characterDevelopment'],before['characterDevelopment'])
        self.assertEqual(self.state['residentAssignment'],'rest');self.assertEqual(len(self.state['lessonHistory']),1)
        self.reject('start-lesson',learnerId='founder',teacherId='mira',subjectKind='principle',targetId='gentle-preservation')
    def test_either_assignment_pauses_and_resume_reassigns_both(self):
        self.lesson();self.act('assign-resident',assignment='rest');self.act('advance')
        self.assertEqual(self.state['trainingProjects']['founder']['completedWorkPhases'],0)
        self.assertIn('paused',' '.join(public_state(self.state)['lessonReadiness']['founder']))
        self.act('resume-lesson',learnerId='founder');self.act('assign-founder',assignment='commissions');before=self.state['sharedFunds'];self.act('advance')
        self.assertEqual(self.state['sharedFunds'],before+4);self.assertNotIn('gentle-preservation',self.state['founderKnownPrinciples'])
        self.act('resume-lesson',learnerId='founder');self.act('advance');self.assertEqual(self.state['sharedFunds'],before+4)
    def test_skill_cost_reserved_and_cancelled_without_teacher_reward(self):
        self.state['characterSkills']['mira']['scholarship']=1
        self.reject('start-lesson',learnerId='founder',teacherId='mira',subjectKind='skill',targetId='scholarship')
        award_advancement(self.state,'founder','fixture',4,'Fixture')
        self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='skill',targetId='scholarship')
        self.assertEqual(character_sheet(self.state,'founder')['reservedAdvancement'],2)
        self.act('cancel-training',characterId='founder');self.assertEqual(character_sheet(self.state,'founder')['availableAdvancement'],4)
        self.assertEqual(self.state['residentAssignment'],'rest')
        self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='skill',targetId='scholarship');self.act('advance')
        self.assertEqual(self.state['characterSkills']['founder']['scholarship'],1)
        self.assertEqual(character_sheet(self.state,'founder')['availableAdvancement'],2)
        self.assertEqual(self.state['characterDevelopment']['mira']['advancementAwards'],{})
    def test_unjoined_same_person_unknown_subject_rejected_and_fieldcraft_lesson_available(self):
        for fields in ({'teacherId':'tamsin','targetId':'gentle-preservation'},{'teacherId':'founder','targetId':'gentle-preservation'},{'teacherId':'mira','targetId':'not-real'}):
            self.reject('start-lesson',learnerId='founder',subjectKind='principle',**fields)
        self.state['characterSkills']['founder']['fieldcraft']=2;award_advancement(self.state,'mira','fixture',4,'Fixture')
        self.act('start-lesson',learnerId='mira',teacherId='founder',subjectKind='skill',targetId='fieldcraft')
        self.act('advance');self.assertEqual(self.state['characterSkills']['mira']['fieldcraft'],1)
    def test_existing_lessons_and_learning_prevent_overbooking(self):
        self.state['additionalResidents']['tamsin']['status']='resident'
        self.state['bedroomAssignments']['tamsin']='bedchamber'
        self.lesson()
        self.reject('start-lesson',learnerId='tamsin',teacherId='mira',subjectKind='principle',targetId='gentle-preservation')
        self.reject('start-lesson',learnerId='mira',teacherId='tamsin',subjectKind='principle',targetId='gentle-preservation')
        self.act('cancel-training',characterId='founder')
        self.act('study-principle',characterId='founder',principleId='gentle-preservation')
        self.reject('start-lesson',learnerId='founder',teacherId='mira',subjectKind='principle',targetId='gentle-preservation')
    def test_absence_keeps_lesson_and_cancellation_does_not_erase_other_assignment(self):
        self.lesson();self.act('start-expedition');self.act('advance')
        self.assertNotIn('gentle-preservation',self.state['founderKnownPrinciples'])
        self.reject('resume-lesson',learnerId='founder');self.act('return-expedition');self.act('advance')
        self.act('assign-resident',assignment='rest');self.act('cancel-training',characterId='founder')
        self.assertEqual(self.state['residentAssignment'],'rest');self.assertEqual(self.state['lessonHistory'],[])
    def test_resident_pair_can_finish_while_founder_travels(self):
        self.state['additionalResidents']['tamsin']['status']='resident';self.state['bedroomAssignments']['tamsin']='bedchamber'
        learn_for_character(self.state,'mira','water-guidance')
        self.act('start-lesson',learnerId='tamsin',teacherId='mira',subjectKind='principle',targetId='water-guidance')
        self.act('start-expedition');self.act('advance')
        self.assertIn('water-guidance',self.state['additionalResidents']['tamsin']['knownPrinciples'])
        self.assertNotIn('water-guidance',self.state['founderKnownPrinciples'])
    def test_teacher_retraining_requires_requalification_or_cancellation(self):
        award_advancement(self.state,'mira','fixture',4,'Fixture');award_advancement(self.state,'founder','fixture',4,'Fixture')
        self.act('train-skill',characterId='mira',skillId='scholarship');self.act('advance');self.act('advance')
        self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='skill',targetId='scholarship')
        self.act('start-retraining',characterId='mira');self.act('advance')
        self.assertEqual(self.state['characterSkills']['founder']['scholarship'],0)
        self.reject('resume-lesson',learnerId='founder');self.act('cancel-training',characterId='founder')
        self.assertEqual(character_sheet(self.state,'founder')['reservedAdvancement'],0)
    def test_schema_migration_and_safe_lesson_retry(self):
        old=deepcopy(self.state);old['schemaVersion']=14;old.pop('lessonHistory')
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=?',(json.dumps(old),))
            store=GameStore(directory)
            self.assertTrue((Path(directory)/f"campaign-before-schema-14-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'start-lesson','learnerId':'founder','teacherId':'mira','subjectKind':'principle','targetId':'gentle-preservation'}}
            once=store.action(payload);self.assertEqual(store.action(payload),once)
            self.assertEqual(GameStore(directory).read()['trainingProjects']['founder']['teacherId'],'mira')
