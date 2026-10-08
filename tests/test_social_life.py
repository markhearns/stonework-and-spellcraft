from copy import deepcopy
import json, tempfile, unittest, uuid
from unittest.mock import patch
import game as g
import social_life as social
import social_content as content
import test_household_chapters as household_tests
from server import GameStore

class SocialLifeTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def member(self,who):household_tests.HouseholdChapterTests.member(self,who)
    def share(self,key,choice='curious'):self.act('share-social-conversation',sceneId=key,choice=choice)
    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(before,self.s)
    def all_members(self):
        for who in content.PERSONAL:self.member(who)
    def unlock_context(self):
        self.s['spellbook'].append({'id':'evidence-only','ownerId':'founder','formId':'warm-twist','castCount':1})
        self.s['binderyDiscoveries']=['survey']
        self.s['lastingRituals']['completed']['archive-circle']={'active':True}
    def test_complete_all_106_scenes_with_each_response_path_without_cost_or_assignment_changes(self):
        for choice in ('curious','warm','candid'):
            self.s=g.new_campaign();self.all_members();self.unlock_context()
            for key,d in content.CATALOGUE.items():
                with self.subTest(choice=choice,key=key):
                    self.s['dayNumber']+=1
                    protected={k:deepcopy(v) for k,v in self.s.items() if k not in ('socialLife','journal','relationships')}
                    self.share(key,choice)
                    self.assertEqual(protected,{k:self.s[k] for k in protected})
                    m=social.saved(self.s)['memories'][key]
                    self.assertEqual(m['response'],d['choices'][choice]['response'])
                    if d.get('branches'):self.assertTrue(m['opening'].startswith(d['branches'][choice]))
            self.assertEqual(len(social.saved(self.s)['memories']),100)
            self.assertTrue(all(b['shared']==3 for b in social.view(self.s)['bonds']))
    def test_all_characters_have_personal_and_peer_content_and_distinct_replies(self):
        self.assertEqual(len(content.PERSONAL),13);self.assertEqual(len(content.PAIRS),10)
        self.assertEqual(len(content.REACTIONS),13);self.assertEqual(len(content.GATHERINGS),5)
        self.assertEqual(set(content.PERSONAL),{p for a in content.PAIRS.values() for p in a['participants']})
        self.assertEqual(len({d['title'] for d in content.CATALOGUE.values()}),100)
        self.assertEqual(len({d['opening'] for d in content.CATALOGUE.values()}),100)
        for d in content.CATALOGUE.values():
            self.assertEqual(len(d['choices']),3)
            self.assertEqual(len({c['response'] for c in d['choices'].values()}),3)
    def test_followup_requires_elapsed_phase_and_never_rewrites_a_choice(self):
        self.reject('share-social-conversation',sceneId='personal:mira:1',choice='warm')
        self.share('personal:mira:0','candid')
        self.reject('share-social-conversation',sceneId='personal:mira:1',choice='warm')
        self.reject('share-social-conversation',sceneId='personal:mira:0',choice='warm')
        self.act('advance');self.share('personal:mira:1','warm');self.act('advance')
        r=social.row(self.s,'personal:mira:2');self.assertIn('requires two unconvincing actors',r['opening'])
        self.assertEqual(r['callback']['choice'],'warm');self.share('personal:mira:2','candid')
        self.assertEqual(social.saved(self.s)['memories']['personal:mira:0']['choice'],'candid')
    def test_actual_context_gates_and_unavailable_outcomes_are_not_exposed(self):
        self.member('nyssara');self.member('iona')
        for key in ('reaction:mira','reaction:nyssara','reaction:iona'):
            self.reject('share-social-conversation',sceneId=key,choice='curious')
            r=social.row(self.s,key);self.assertEqual(r['opening'],'');self.assertEqual(r['choices'],{})
        self.unlock_context()
        for key in ('reaction:mira','reaction:nyssara','reaction:iona'):
            self.assertTrue(social.row(self.s,key)['available']);self.share(key)
    def test_away_people_and_invalid_payloads_are_atomic(self):
        for fields in ({'sceneId':[],'choice':'warm'},{'sceneId':'bad','choice':'warm'}, {'sceneId':'personal:mira:0','choice':[]}, {'sceneId':'personal:mira:0','choice':'invented'}, {'sceneId':'personal:brakka:0','choice':'warm'}):
            self.reject('share-social-conversation',**fields)
        with patch('game.character_at_castle',return_value=False):self.reject('share-social-conversation',sceneId='personal:mira:0',choice='curious')
        self.member('tamsin')
        with patch('game.character_at_castle',side_effect=lambda s,p:p!='tamsin'):
            self.reject('share-social-conversation',sceneId='pair:mira-tamsin:0',choice='curious')
    def test_later_never_expires_or_consumes_progress_and_restore_is_guarded(self):
        key='personal:mira:0';self.act('defer-social-conversation',sceneId=key)
        self.assertNotIn(key,{r['id'] for r in social.view(self.s)['invitations']})
        self.reject('defer-social-conversation',sceneId=key)
        self.s['dayNumber']+=100
        self.assertTrue(social.row(self.s,key)['available'])
        self.act('restore-social-conversation',sceneId=key)
        self.assertIn(key,{r['id'] for r in social.view(self.s)['invitations']})
        self.reject('restore-social-conversation',sceneId=key)
        self.act('defer-social-conversation',sceneId=key);self.share(key)
        self.assertNotIn(key,social.saved(self.s)['deferred'])
    def test_peer_branch_records_what_was_agreed_and_stays_stable_on_reload(self):
        self.member('tamsin');self.share('pair:mira-tamsin:0','warm');self.act('advance')
        self.share('pair:mira-tamsin:1','candid');self.act('advance')
        self.share('pair:mira-tamsin:2','curious')
        m=social.saved(self.s)['memories']['pair:mira-tamsin:2']
        self.assertIn('Two complete recipes',m['opening'])
        self.assertEqual(g.migrate_state(json.loads(json.dumps(self.s))),self.s)
    def test_context_scopes_real_memories_and_does_not_leak_other_private_conversations(self):
        from dialogue import dialogue_context
        self.member('tamsin');self.share('personal:mira:0','candid');self.share('personal:tamsin:0','warm');self.share('pair:mira-tamsin:0')
        facts=json.loads(dialogue_context(self.s,'What have we discussed?','mira')[0]['content'].split('Scene facts: ',1)[1])
        records=facts['rememberedSocialConversations']
        self.assertEqual({r['id'] for r in records},{'personal:mira:0','pair:mira-tamsin:0'})
        self.assertEqual(records[0]['playerLine'],content.PERSONAL['mira'][0]['choices']['candid']['label'])
        self.assertNotIn('personal:mira:1',{r['id'] for r in records})
    def test_readonly_views_and_solo_have_no_phantom_invitations(self):
        before=deepcopy(self.s);social.view(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
        v=social.view(g.new_campaign('fresh'));self.assertEqual(v['scenes'],[]);self.assertEqual(v['invitations'],[]);self.assertEqual(v['bonds'],[])
    def test_old_save_initializes_social_state_without_rewriting_prior_history(self):
        self.s.pop('socialLife');self.s['schemaVersion']=47;before=deepcopy(self.s)
        g.migrate_state(self.s);self.assertEqual(self.s['schemaVersion'],66)
        for k in before:
            if k!='schemaVersion':self.assertEqual(before[k],self.s[k])
        self.assertEqual(self.s['socialLife'],{'memories':{},'deferred':[]})
    def test_store_retry_records_one_exchange_and_reload_retains_it(self):
        with tempfile.TemporaryDirectory() as root:
            store=GameStore(root);s=store.read()
            action={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':{'type':'share-social-conversation','sceneId':'personal:mira:0','choice':'warm'}}
            once=store.action(action);self.assertEqual(once,store.action(action))
            loaded=GameStore(root).read();self.assertEqual(len(loaded['socialLife']['memories']),1)
            self.assertEqual(loaded['socialLife'],once['socialLife'])

    def test_new_shared_memories_count_once_for_existing_optional_invitations(self):
        import outfit_progression as outfits
        self.assertTrue(outfits.blockers(self.s,'mira','2'))
        self.act('defer-social-conversation',sceneId='everyday:mira')
        self.assertTrue(outfits.blockers(self.s,'mira','2'))
        self.share('personal:mira:0')
        self.assertEqual(outfits.blockers(self.s,'mira','2'),[])
        self.act('accept-outfit-invitation',characterId='mira',tier='2')
        self.share('everyday:mira');self.act('advance');self.share('personal:mira:1')
        self.assertEqual(outfits.blockers(self.s,'mira','3'),[])
        before=outfits.memories(self.s,'mira');social.view(self.s);g.public_state(self.s)
        self.assertEqual(before,outfits.memories(self.s,'mira'));self.assertEqual(len(before),3)
        self.assertIsNone(outfits.current(self.s,'mira'))
