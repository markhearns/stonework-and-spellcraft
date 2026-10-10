"""Branch routing, history integrity and knowledge scope for the dialogue review."""
from copy import deepcopy
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import game as g
import companion_almanac as a
import companion_almanac_content as content
import companion_conversations as conversations
import social_life
import relationships
import party_journeys
import test_companion_almanac as fixtures
from server import GameStore

def prose(value):
    return json.dumps(value, ensure_ascii=False)

class CompanionDialogueReviewTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.CompanionAlmanacTests()
        self.f.setUp()
        self.s = self.f.s
        for who in content.PERSONAL:
            self.f.trust(who)

    def test_all_personal_branches_save_selected_words_without_spending_time(self):
        for who in content.PERSONAL:
            for tier in a.TIERS:
                for choice in a.CHOICES:
                    with self.subTest(who=who,tier=tier,choice=choice):
                        s = deepcopy(self.s)
                        for prior in ('familiar','trusted'):
                            if prior == tier: break
                            a.apply(s,{'type':'share-almanac','sceneId':prior+':'+who,'choice':'curious'})
                        if tier == 'intimate':
                            s['romance']['people'][who]={'level':3,'mode':'open','deferred':False}
                        key=tier+':'+who
                        before=(s['sharedFunds'],s['dayNumber'],s['currentDayPhase'])
                        row=a.row(s,key)
                        self.assertTrue(row['available'],row['blockers'])
                        self.assertEqual(len({v['label'] for v in row['choices'].values()}),3)
                        expected=a.definition(s,key)
                        self.assertEqual(len(set(expected['responses'].values())),3)
                        self.assertNotIn(expected['responses'][choice],prose(row))
                        a.apply(s,{'type':'share-almanac','sceneId':key,'choice':choice})
                        memory=a.row(s,key)['memory']
                        self.assertEqual(memory['playerLine'],row['choices'][choice]['label'])
                        self.assertEqual(memory['response'],expected['responses'][choice])
                        self.assertEqual(before,(s['sharedFunds'],s['dayNumber'],s['currentDayPhase']))
                        self.assertEqual(a.row(s,key)['choices'],{})
                        with self.assertRaises(g.RuleError):
                            a.apply(s,{'type':'share-almanac','sceneId':key,'choice':choice})

    def test_pair_branches_callback_to_actual_choice_and_never_spend_resources(self):
        for left,right,_,scenes in content.PAIRS:
            base=deepcopy(self.s)
            for who in (left,right):a.apply(base,{'type':'share-almanac','sceneId':'familiar:'+who,'choice':'curious'})
            for index in range(len(scenes)):
                key=f'pair:{left}:{right}:{index}'
                for choice in a.CHOICES:
                    with self.subTest(pair=(left,right),index=index,choice=choice):
                        s=deepcopy(base);row=a.row(s,key);before=(s['sharedFunds'],s['dayNumber'],s['currentDayPhase'])
                        self.assertTrue(row['available'],row['blockers'])
                        a.apply(s,{'type':'share-almanac','sceneId':key,'choice':choice})
                        memory=a.saved(s)['memories'][key]
                        self.assertEqual(memory['playerLine'],row['choices'][choice]['label'])
                        self.assertEqual(memory['response'],a.definition(base,key)['responses'][choice])
                        self.assertEqual(before,(s['sharedFunds'],s['dayNumber'],s['currentDayPhase']))
                        if index<2:
                            following=a.definition(s,f'pair:{left}:{right}:{index+1}')['opening']
                            self.assertIn(memory['playerLine'],following)
                            self.assertIn(memory['response'],following)
                a.apply(base,{'type':'share-almanac','sceneId':key,'choice':'curious'})
                base['dayNumber']+=1

    def test_editorial_changes_do_not_rewrite_saved_history_or_reload(self):
        key='familiar:mira'
        a.apply(self.s,{'type':'share-almanac','sceneId':key,'choice':'warm'})
        record=a.saved(self.s)['memories'][key]
        record.update(opening='A previously saved opening.',playerLine='A previously chosen reply.',response='A previously saved answer.')
        expected=deepcopy(record)
        with patch.dict(conversations.FAMILIAR,{'mira':conversations.scene('A later revision.',('One','New one'),('Two','New two'),('Three','New three'))}):
            self.assertEqual(a.row(self.s,key)['memory'],expected)
            self.assertEqual(a.row(self.s,key)['opening'],expected['opening'])
            self.assertEqual(a.context(self.s,'mira')['rememberedMoments'][0],expected)
            with tempfile.TemporaryDirectory() as folder:
                store=GameStore(folder)
                with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(prose(self.s),))
                reloaded=GameStore(folder).read()
                self.assertEqual(a.saved(reloaded)['memories'][key],expected)
                g.migrate_state(reloaded)
                self.assertEqual(a.saved(reloaded)['memories'][key],expected)

    def test_goals_require_disclosure_and_private_facts_stay_gated(self):
        for who in content.PERSONAL:
            s=deepcopy(self.s);goal,value,tension=conversations.CHARACTER[who]
            self.assertNotIn(goal,prose(a.profile(s,who)))
            self.assertNotIn(goal,prose(a.context(s,who)))
            a.apply(s,{'type':'share-almanac','sceneId':'familiar:'+who,'choice':'warm'})
            self.assertIn(goal,prose(a.context(s,who)))
            self.assertIn(value,prose(a.profile(s,who)))
            self.assertNotIn(tension,prose(a.profile(s,who)))
            self.assertFalse(a.row(s,'intimate:'+who)['available'])
            self.assertNotIn(content.PERSONAL[who]['private'],prose(a.context(s,who)))

    def test_neris_followup_does_not_invent_unchosen_duck_song(self):
        for choice in ('curious','warm','candid'):
            s=deepcopy(self.s)
            social_life.apply(s,{'type':'share-social-conversation','sceneId':'personal:neris:0','choice':'curious'})
            s['dayNumber']+=1
            social_life.apply(s,{'type':'share-social-conversation','sceneId':'personal:neris:1','choice':choice})
            s['dayNumber']+=1
            row=social_life.row(s,'personal:neris:2')
            self.assertTrue(row['available'])
            if choice!='warm':self.assertNotIn('duck',row['opening'].lower())
            else:self.assertIn('duck',row['opening'].lower())

    def test_initiatives_and_invitations_record_the_displayed_choice(self):
        for who in content.PERSONAL:
            s=deepcopy(self.s)
            a.apply(s,{'type':'share-almanac','sceneId':'familiar:'+who,'choice':'warm'})
            key='initiative:'+who;row=a.row(s,key)
            self.assertEqual(len(set(x['label'] for x in row['choices'].values())),3)
            a.apply(s,{'type':'share-almanac','sceneId':key,'choice':'candid'})
            self.assertEqual(a.saved(s)['memories'][key]['playerLine'],row['choices']['candid']['label'])
        for who in relationships.PREFERENCES:
            choices=relationships.invitation_definition(who)['choices']
            self.assertEqual(len({v[1] for v in choices.values()}),3)
            self.assertEqual({k:v[2] for k,v in choices.items()},{'join':'affection','ask':'trust','decline':'respect'})

    def test_camp_question_is_platonic_and_saves_its_own_reply(self):
        for who in ('mira','neris','velis','rhess'):
            f=fixtures.fixtures.PartyJourneyTests();f.setUp();f.at('flooded-monastery',2,[who])
            s=f.s
            s['romance']['people'][who]={'level':0,'mode':'friendly','deferred':False}
            key='private:'+who
            row=next(r for r in party_journeys.scenes(s,'flooded-monastery') if r['id']==key)
            self.assertTrue(row['available'])
            self.assertIn('company',row['choices']);self.assertIn('curious',row['choices'])
            self.assertTrue(row['choices']['affection']['blockers'])
            before=(s['sharedFunds'],s['dayNumber'],s['currentDayPhase'])
            f.act('share-party-journey',siteId='flooded-monastery',sceneId=key,choice='curious')
            memory=party_journeys.saved(s,'flooded-monastery')['memories'][key]
            self.assertEqual(memory['response'],conversations.CAMP_QUESTIONS[who][1])
            self.assertEqual(before,(s['sharedFunds'],s['dayNumber'],s['currentDayPhase']))
            self.assertEqual(s['romance']['people'][who]['level'],0)

if __name__=='__main__':unittest.main()
