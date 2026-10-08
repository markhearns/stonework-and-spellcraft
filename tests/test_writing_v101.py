"""Check that editorial content covers real events and states its existing effects."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

import game as g
import companion_almanac as almanac
import companion_almanac_content as almanac_content
import companion_participation as participation
import conversation_voice
import household_chapter_content
import household_chapters
import personal_stories
import relationships
import shared_history
import test_party_journeys as journey_fixtures


class WritingReviewTests(unittest.TestCase):
    def setUp(self):
        fixture = journey_fixtures.PartyJourneyTests()
        fixture.setUp()
        self.s = fixture.s

    def test_every_authored_companion_and_pair_has_complete_content(self):
        cast = set(almanac_content.PERSONAL)
        self.assertEqual(cast, set(conversation_voice.ROWS))
        self.assertEqual(cast, set(almanac_content.INITIATIVE_REPLIES))
        self.assertEqual(cast, set(participation.VOICES))
        for who in cast:
            with self.subTest(who=who):
                self.assertEqual(set(conversation_voice.voice(who)), set(conversation_voice.FIELDS))
                d = almanac.definition(self.s, 'initiative:' + who)
                self.assertEqual(set(d['responses']), set(almanac.CHOICES))
                self.assertEqual(len(set(d['responses'].values())), 3)
        pairs = {(row[0], row[1]) for row in household_chapter_content.PAIRS}
        self.assertEqual(pairs, set(household_chapter_content.PAIR_FOLLOWUPS))
        before = deepcopy(self.s)
        for row in household_chapters.pair_rows(self.s):
            if row['id'].endswith(':1'):
                self.assertEqual(set(row['choices']), {'method', 'meaning'})
        self.assertEqual(before, self.s)

    def test_choice_effects_match_the_actual_award_and_do_not_advance_or_pay(self):
        events = [dict(kind='practice', subject='Diplomacy', rank=2, learnerId='mira'),
                  dict(kind='journey', complete=True, siteName='Test journey', outcomes=[]),
                  *[dict(kind='patrol-moment', occasion=occasion, reported=True)
                    for occasion in ('care', 'cover', 'rare')]]
        for event in events:
            event.update(id='editorial-check', who='mira', title='Recorded event', day=1)
            for start in (0, 12):
                state = deepcopy(self.s)
                participation.initialize(state)
                participation.saved(state)['events'][event['id']] = event
                key = relationships.pair_id('founder', 'mira')
                state['relationships']['bonds'][key] = dict(participants=['founder', 'mira'], **dict.fromkeys(relationships.DIMENSIONS, start))
                row = participation.event_row(state, event['id'])
                for choice, shown in row['choices'].items():
                    with self.subTest(kind=event['kind'], choice=choice, start=start):
                        candidate = deepcopy(state)
                        dimension = shown['effect'].split()[0].lower()
                        before = {k:deepcopy(v) for k,v in candidate.items() if k not in ('companionParticipation','journal','relationships')}
                        g.apply_action(candidate, dict(type='share-participation', eventId=event['id'], choice=choice))
                        bond = candidate['relationships']['bonds'][key]
                        for axis in relationships.DIMENSIONS:
                            self.assertEqual(bond[axis], min(12, start + int(axis == dimension)))
                        self.assertEqual(before, {k:candidate[k] for k in before})
                        with self.assertRaises(g.RuleError):
                            g.apply_action(candidate, dict(type='share-participation', eventId=event['id'], choice=choice))

    def test_lesson_content_covers_real_training_subjects_and_names_the_learner(self):
        subjects = {d['name'] for d in g.character_builds.ATTRIBUTES.values()} | {d['name'] for d in g.CHARACTER_SKILLS.values()}
        self.assertEqual(subjects, set(participation.PRACTICE))
        for subject in subjects:
            e = dict(kind='practice', who='mira', learnerId='founder', subject=subject, rank=2)
            opening, choices = participation.dialogue(self.s, e)
            self.assertIn('teaching you '+subject+' 2', opening)
            self.assertEqual(set(choices), {'notice','practice','celebrate'})
            self.assertIn(subject, choices['notice']['label'])

    def test_reported_return_does_not_invent_shared_participation_or_failure(self):
        e = dict(kind='journey', who='mira', reported=True, complete=True, siteName='The ridge', outcomes=[])
        opening, choices = participation.dialogue(self.s, e)
        self.assertIn('You stayed at the castle', opening)
        self.assertIn('completed the journey', opening)
        self.assertNotIn('returned before completing', opening)
        self.assertIn('without adding an individual accomplishment', choices['thanks']['response'])

    def test_planned_party_display_matches_saved_party_and_never_departs(self):
        people = ['brakka','iona','fenna','mira','rhess']
        shared_history.record(self.s,'objective:rescue',people,'Completed rescue','The surveyor returned.','fieldwork')
        row = shared_history.view(self.s,'brakka')[0]
        plan = next(c for c in row['choices'] if c['id']=='plan')
        before = {k:deepcopy(v) for k,v in self.s.items() if k not in ('sharedHistory','journal')}
        g.apply_action(self.s,dict(type='history-share',eventId=row['id'],choiceId='plan'))
        self.assertEqual(shared_history.saved(self.s)['suggestedParty'], ['founder','brakka','iona','fenna'])
        for who in shared_history.saved(self.s)['suggestedParty']:
            self.assertIn(g.character_profile(self.s,who)['name'], plan['effect'])
        self.assertNotIn('Rhess',plan['effect'])
        self.assertEqual(before,{k:self.s[k] for k in before})

    def test_completed_memories_survive_new_definitions_and_json_reload(self):
        shared_history.record(self.s,'objective:rescue',['mira'],'Rescue','The surveyor returned.','fieldwork')
        row = shared_history.view(self.s)[0]
        g.apply_action(self.s,dict(type='history-share',eventId=row['id'],choiceId='company'))
        remembered = deepcopy(shared_history.saved(self.s)['memories'])
        self.s = g.migrate_state(json.loads(json.dumps(self.s)))
        before = deepcopy(self.s)
        with patch.dict(conversation_voice.ROWS, mira=('Revised prose',)*6):
            self.assertEqual(shared_history.view(self.s)[0]['memory'],remembered[row['id']])
            g.public_state(self.s)
        self.assertEqual(before,self.s)

    def test_all_six_offline_packages_remain_valid_and_keep_existing_rules(self):
        self.s['archivePrinciples'] = list(g.PRINCIPLE_NAMES)
        for package in personal_stories.PACKAGES:
            if not personal_stories.chapter_available(self.s,'mira',personal_stories.PACKAGES[package]):
                self.fail('Earlier completed package should unlock '+package)
            proposal = personal_stories.outline(self.s,'mira',package)
            checked,rules = personal_stories.validate(json.dumps(proposal),self.s,'mira')
            self.assertEqual(checked,proposal)
            for key,value in personal_stories.PACKAGES[package].items():self.assertEqual(rules[key],value)
            personal_stories.approve(self.s,dict(ownerId='mira',proposal=proposal,id=package,model='offline',source='offline'))
            record=self.s['personalStories']['story-'+package]
            record.update(status='complete',sceneStatus='remembered')
