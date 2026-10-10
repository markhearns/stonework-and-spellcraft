"""Reachable dialogue branches, durable turns and scoped player knowledge."""
from copy import deepcopy
from itertools import product
from pathlib import Path
from unittest.mock import patch
import json
import sqlite3
import tempfile
import unittest
import uuid

import game as g
import companion_threads as threads
import companion_threads_content as c
import companion_almanac as almanac
import relationships
import resident_bonds
import outfit_progression
import foundation_chamber
from social_life import stamp
from server import GameStore, ConflictError
import test_companion_almanac as fixtures


def encoded(value):
    return json.dumps(value, ensure_ascii=False)


class CompanionThreadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = fixtures.CompanionAlmanacTests()
        fixture.setUp()
        for who in c.PERSONAL:
            fixture.familiar(who)
        cls.base = deepcopy(fixture.s)

    def setUp(self):
        self.s = deepcopy(self.base)

    def answer(self, key, choice='0', state=None):
        state = state if state is not None else self.s
        row = threads.row(state, key)
        self.assertTrue(row['available'], row['blockers'])
        self.assertGreaterEqual(len(row['choices']), 2)
        action = dict(type='thread-answer', sceneId=key, expectedTurn=row['turn'], choice=choice)
        # The branch walk uses the same action handler; separate tests cover the
        # atomic outer dispatcher and actual SQLite request protocol.
        threads.apply(state, action)
        record = threads.saved(state)['records'][key]
        self.assertEqual(record['turns'][-1]['opening'], row['opening'])
        self.assertEqual(record['turns'][-1]['playerLine'], row['choices'][choice]['label'])
        return record

    def finish(self, key, choices=('0','0','0'), state=None):
        for choice in choices:
            record = self.answer(key, choice, state)
        self.assertTrue(record['completed'])
        return record

    def reject(self, action):
        before = deepcopy(self.s)
        with self.assertRaises(g.RuleError):
            g.apply_action(self.s, action)
        self.assertEqual(self.s, before)

    def test_all_personal_paths_have_choices_exact_history_and_one_completion_reward(self):
        for who, choices in product(c.PERSONAL, product(('0','1','2'), ('0','1','2','3'), ('0','1','2'))):
            with self.subTest(who=who, choices=choices):
                state = deepcopy(self.base)
                key = 'personal:' + who
                before = deepcopy(state['relationships'])
                self.answer(key, choices[0], state)
                self.answer(key, choices[1], state)
                self.assertEqual(state['relationships'], before)
                record = self.answer(key, choices[2], state)
                self.assertTrue(record['completed'])
                self.assertEqual(record['stance'], ('support','disagree','independent')[int(choices[2])])
                self.assertEqual(len(record['turns']), 3)
                event = state['relationships']['events']['thread:' + key]
                self.assertEqual(event['effects'][0]['change'], 1)
                for field in ('dayNumber','currentDayPhase','sharedFunds','materialInventory',
                              'romance','founderAssignment','residentAssignment','privateCastleLore'):
                    self.assertEqual(state[field], self.base[field])
                self.assertFalse(threads.row(state, key)['choices'])

    def test_every_preference_and_stance_reaches_a_complete_followup_without_assumed_agreement(self):
        for who, pref, stance in product(c.PERSONAL, range(4), range(3)):
            base = deepcopy(self.base)
            self.finish('personal:' + who, ('0', str(pref), str(stance)), base)
            key = 'followup:' + who
            self.assertFalse(threads.row(base, key)['available'])
            base['dayNumber'] += 1
            row = threads.row(base, key)
            self.assertIn(c.PERSONAL[who]['followups'][pref], row['opening'])
            self.assertEqual(c.PERSONAL[who]['unresolved'] in row['opening'], stance == 1)
            for first, last in product(('0','1','2'), ('0','1')):
                with self.subTest(who=who, preference=pref, stance=stance, first=first, last=last):
                    state = deepcopy(base)
                    record = self.finish(key, (first,last), state)
                    self.assertEqual(record['traditionAgreed'], last == '0')
                    self.assertEqual(bool(threads.profile(state, who)['tradition']), last == '0')
                    self.assertEqual(state['relationships']['events']['thread:' + key]['effects'][0]['change'], 1)

    def test_every_resident_pair_branch_completes_and_returns_with_shared_bonding(self):
        for pair in c.PAIRS:
            key = 'pair:' + pair
            for choices in product(('0','1','2'), ('0','1','2'), ('0','1')):
                state = deepcopy(self.base)
                self.finish(key, choices, state)
                a,b = c.PAIRS[pair]['people']
                bond = resident_bonds.saved(state)['pairs'][resident_bonds.pair_id(a,b)]
                self.assertEqual(bond['score'], 2)
                event = state['relationships']['events']['thread:' + key]
                self.assertEqual(len(event['effects']), 3)
            state['dayNumber'] += 1
            for choices in product(('0','1','2'), ('0','1')):
                later = deepcopy(state)
                self.finish('pair-followup:' + pair, choices, later)
                self.assertEqual(resident_bonds.saved(later)['pairs'][resident_bonds.pair_id(a,b)]['score'], 4)
        self.assertEqual(set(c.PERSONAL), {who for p in c.PAIRS.values() for who in p['people']})

    def test_future_answers_and_unchosen_replies_are_not_sent_to_the_client(self):
        view = encoded(g.public_state(self.s))
        for data in c.PERSONAL.values():
            self.assertNotIn(data['question'], view)
            self.assertNotIn(data['decision'], view)
            for _, reply in data['approaches']:
                self.assertNotIn(reply, view)
        self.answer('personal:mira', '1')
        view = encoded(g.public_state(self.s))
        self.assertIn(c.PERSONAL['mira']['approaches'][1][1], view)
        self.assertNotIn(c.PERSONAL['mira']['approaches'][0][1], view)
        self.assertNotIn(c.PERSONAL['mira']['decision'], view)

    def test_preference_correction_changes_future_invitation_but_not_saved_history(self):
        self.finish('personal:mira', ('0','0','1'))
        record = deepcopy(threads.saved(self.s)['records']['personal:mira'])
        rewards = deepcopy(self.s['relationships'])
        for choice in ('1','2','3','0'):
            g.apply_action(self.s, dict(type='thread-preference', personId='mira', choice=choice))
            self.s['dayNumber'] += 1
            row = threads.row(self.s, 'followup:mira')
            self.assertIn(c.PERSONAL['mira']['followups'][int(choice)], row['opening'])
            self.assertEqual(threads.saved(self.s)['records']['personal:mira'], record)
            self.assertEqual(self.s['relationships'], rewards)
        self.assertEqual(len(threads.profile(self.s, 'mira')['updates']), 4)
        self.reject(dict(type='thread-preference', personId='mira', choice='0'))

    def test_preferences_stay_scoped_to_the_resident_and_unknown_is_not_dislike(self):
        self.finish('personal:mira', ('0','3','1'))
        self.assertEqual(threads.context(self.s,'mira')['currentPlayerPreference']['status'], 'private')
        self.assertIsNone(threads.context(self.s,'tamsin')['currentPlayerPreference'])
        self.assertFalse(threads.context(self.s,'tamsin')['conversations'])
        self.assertEqual(threads.context(self.s,'unknown'), {})
        g.apply_action(self.s, dict(type='thread-preference', personId='mira', choice='2'))
        self.assertEqual(threads.context(self.s,'mira')['currentPlayerPreference']['status'], 'unsure')
        self.finish('pair:mira:nyssara')
        self.assertEqual([r['id'] for r in threads.context(self.s,'nyssara')['conversations']], ['pair:mira:nyssara'])
        self.assertNotIn(c.PERSONAL['mira']['question'], encoded(threads.context(self.s,'nyssara')))

    def test_views_and_context_never_change_the_save(self):
        self.answer('personal:mira')
        before = deepcopy(self.s)
        for who in c.PERSONAL:
            threads.context(self.s, who)
            threads.profile(self.s, who)
        g.public_state(self.s)
        self.assertEqual(self.s, before)

    def test_stale_turn_invalid_choice_and_forged_actions_are_atomic(self):
        key = 'personal:mira'
        for values in ({}, {'expectedTurn':True}, {'expectedTurn':0,'choice':[]},
                       {'expectedTurn':0,'choice':'99'}, {'expectedTurn':1,'choice':'0'}):
            self.reject(dict(type='thread-answer', sceneId=key, **values))
        for key in ([], None, 'personal:unknown', 'pair:founder:mira'):
            self.reject(dict(type='thread-answer', sceneId=key, expectedTurn=0, choice='0'))
        self.reject(dict(type='thread-invent'))
        self.reject(dict(type='thread-preference', personId='mira', choice='0'))
        self.answer('personal:mira')
        self.reject(dict(type='thread-answer', sceneId='personal:mira', expectedTurn=0, choice='0'))

    def test_defer_restore_and_travel_keep_the_exact_place(self):
        key = 'personal:mira'
        self.answer(key)
        record = deepcopy(threads.saved(self.s)['records'][key])
        g.apply_action(self.s, dict(type='thread-defer', sceneId=key))
        self.s['dayNumber'] += 100
        self.assertTrue(threads.row(self.s,key)['deferred'])
        self.reject(dict(type='thread-answer', sceneId=key, expectedTurn=1, choice='0'))
        g.apply_action(self.s, dict(type='thread-restore', sceneId=key))
        g.apply_action(self.s, dict(type='start-expedition', siteId='old-waterworks', companionIds=['mira']))
        self.assertFalse(threads.row(self.s,key)['available'])
        self.reject(dict(type='thread-answer', sceneId=key, expectedTurn=1, choice='0'))
        self.assertEqual(threads.saved(self.s)['records'][key], record)

    def test_familiarity_and_adult_residency_gates_do_not_depend_on_romance(self):
        self.assertEqual(len(threads.views(self.s)['scenes']), 50)
        del self.s['companionAlmanac']['memories']['familiar:mira']
        self.assertFalse(threads.row(self.s,'personal:mira')['available'])
        self.assertFalse(threads.row(self.s,'pair:mira:nyssara')['available'])
        self.reject(dict(type='thread-answer', sceneId='personal:mira', expectedTurn=0, choice='0'))
        self.s['people']['mira']['adultAgeYears'] = 17
        self.assertNotIn('personal:mira', threads.keys(self.s))
        self.reject(dict(type='thread-answer', sceneId='pair:mira:nyssara', expectedTurn=0, choice='0'))

    def test_one_phase_gate_uses_completion_not_start_and_invitations_do_not_expire(self):
        self.answer('personal:mira')
        self.s['dayNumber'] += 4
        self.answer('personal:mira'); self.answer('personal:mira')
        self.assertFalse(threads.row(self.s,'followup:mira')['available'])
        g.apply_action(self.s, {'type':'advance'})
        self.assertTrue(threads.row(self.s,'followup:mira')['available'])
        self.s['dayNumber'] += 100
        self.assertTrue(threads.row(self.s,'followup:mira')['available'])

    def test_bonus_caps_pair_daily_limit_and_no_repeat_farming(self):
        foundation_chamber.saved(self.s)['blessing'] = dict(startsAt=stamp(self.s),expiresAt=stamp(self.s)+9,announcedEnd=False)
        key='pair:mira:nyssara'
        self.assertIn('Trust +1.2', threads.row(self.s,key)['effect'])
        self.assertIn('Bonding +2.4', threads.row(self.s,key)['effect'])
        self.finish(key)
        event = self.s['relationships']['events']['thread:'+key]
        self.assertEqual([e['change'] for e in event['effects']], [1.2]*3)
        self.assertEqual(resident_bonds.saved(self.s)['pairs']['mira|nyssara']['score'], 2.4)
        self.reject(dict(type='thread-answer', sceneId=key, expectedTurn=3, choice='0'))
        self.s['relationships']['bonds']['founder|mira']['trust']=11.8
        self.finish('personal:mira', ('0','3','1'))
        self.assertEqual(self.s['relationships']['bonds']['founder|mira']['trust'], 12)
        resident_bonds.award(self.s,['mira','nyssara'],'another-scene','Another shared activity',2)
        resident_bonds.award(self.s,['mira','nyssara'],'over-cap','Daily cap',2)
        self.assertEqual(resident_bonds.saved(self.s)['pairs']['mira|nyssara']['score'], 4.8)

    def test_completion_counts_as_a_shared_moment_but_individual_answers_do_not(self):
        before = outfit_progression.memories(self.s,'mira')
        self.answer('personal:mira');self.answer('personal:mira')
        self.assertEqual(outfit_progression.memories(self.s,'mira'),before)
        self.answer('personal:mira')
        self.assertEqual(set(outfit_progression.memories(self.s,'mira'))-set(before), {'thread:personal:mira'})

    def test_schema_migration_backs_up_and_preserves_all_previous_fields(self):
        old=deepcopy(self.s);old['schemaVersion']=70;old.pop('companionThreads',None)
        old['companionAlmanac']['memories']['familiar:mira']['response']='Previously saved wording.'
        migrated=deepcopy(old);g.migrate_state(migrated)
        expected=deepcopy(old);expected['schemaVersion']=g.CURRENT_SCHEMA_VERSION
        expected['companionThreads']={'records':{},'preferences':{},'preferenceUpdates':[],'deferred':[]}
        self.assertEqual(migrated,expected)
        g.migrate_state(migrated);self.assertEqual(migrated,expected)
        with tempfile.TemporaryDirectory() as folder:
            store=GameStore(folder)
            with sqlite3.connect(store.database) as db:
                db.execute('UPDATE campaign SET state=? WHERE id=1',(encoded(old),))
            loaded=GameStore(folder).read()
            self.assertEqual(loaded['companionAlmanac'],old['companionAlmanac'])
            backup=Path(folder)/f'campaign-before-schema-70-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3'
            self.assertTrue(backup.exists())
            with sqlite3.connect(backup) as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0]),old)

    def test_store_reload_duplicate_request_and_stale_revision_preserve_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            store=GameStore(folder)
            with sqlite3.connect(store.database) as db:
                db.execute('UPDATE campaign SET state=? WHERE id=1',(encoded(self.s),))
            for turn,choice in enumerate(('2','3','1')):
                before=store.read()
                payload=dict(requestId=uuid.uuid4().hex,expectedRevision=before['revision'],
                             action=dict(type='thread-answer',sceneId='personal:mira',expectedTurn=turn,choice=choice))
                committed=store.action(payload)
                self.assertEqual(store.action(payload),committed)
                store=GameStore(folder)
                self.assertEqual(store.read(),committed)
                stale={**payload,'requestId':uuid.uuid4().hex}
                with self.assertRaises(ConflictError):store.action(stale)
                self.assertEqual(store.read(),committed)
            self.assertEqual(len(committed['companionThreads']['records']['personal:mira']['turns']),3)
            self.assertEqual(len([k for k in committed['relationships']['events'] if k.startswith('thread:')]),1)

    def test_editing_authored_copy_does_not_rewrite_a_completed_transcript(self):
        self.finish('personal:mira',('2','3','1'))
        record=deepcopy(threads.saved(self.s)['records']['personal:mira'])
        changed={**c.PERSONAL['mira'],'opening':'Revised opening','question':'Revised question'}
        with patch.dict(c.PERSONAL,{'mira':changed}):
            self.assertEqual(threads.row(self.s,'personal:mira')['record'],record)
            self.assertEqual(threads.context(self.s,'mira')['conversations'][0],record)

    def test_generated_dialogue_uses_only_its_own_reached_conversations(self):
        import dialogue
        self.answer('personal:mira','2')
        mira=dialogue.dialogue_context(self.s,'What did I say?', 'mira')[0]['content']
        tamsin=dialogue.dialogue_context(self.s,'What did I say?', 'tamsin')[0]['content']
        selected=c.PERSONAL['mira']['approaches'][2][1]
        unchosen=c.PERSONAL['mira']['approaches'][0][1]
        # Provider prompts encode scene facts with JSON's default ASCII escaping.
        self.assertIn(json.dumps(selected)[1:-1],mira)
        self.assertNotIn(json.dumps(selected)[1:-1],tamsin)
        self.assertNotIn(json.dumps(unchosen)[1:-1],mira)


if __name__ == '__main__':
    unittest.main()
