from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game
import summoning
from dialogue import DialogueService, ProviderSettings, dialogue_context
from server import GameStore


def visiting_state():
    state=game.new_campaign()
    summoning.initialize_person(state)
    state['residency']['iona']['residencyStatus']='visiting'
    state['additionalResidents']['iona']['status']='visiting'
    state['bedroomAssignments']['iona']='bedchamber'
    state['summoningContacts']['threshold-1']={'personId':'iona','contactStatus':'open','conversation':[],'discussedTopics':[]}
    return state

class IonaConversationTests(unittest.TestCase):
    def test_authored_topics_and_free_text_change_only_own_history(self):
        state=visiting_state();before=deepcopy(state)
        for topic in summoning.PERSONAL_TOPICS:
            game.apply_action(state,{'type':'summoning-personal-talk','contactId':'threshold-1','topic':topic})
        game.apply_action(state,{'type':'summoning-personal-line','contactId':'threshold-1','text':'An interesting crossing.'})
        self.assertEqual(len(state['additionalResidents']['iona']['conversation']),5)
        for key in before:
            if key!='additionalResidents':self.assertEqual(state[key],before[key],key)
        record=deepcopy(state['additionalResidents']);record['iona']['conversation']=[]
        self.assertEqual(record,before['additionalResidents'])

    def test_absence_and_invalid_topics_are_atomic(self):
        for rs,topic in [('remote','flirt'),('away','flirt'),('visiting','unknown')]:
            state=visiting_state();state['residency']['iona']['residencyStatus']=rs
            before=deepcopy(state)
            with self.assertRaises(game.RuleError):game.apply_action(state,{'type':'summoning-personal-talk','contactId':'threshold-1','topic':topic})
            self.assertEqual(state,before)

    def test_context_uses_her_identity_and_only_her_conversation(self):
        state=visiting_state()
        state['conversation'].append({'speaker':'Mira','text':'MIRA_PRIVATE_SENTINEL'})
        state['additionalResidents']['tamsin']['conversation'].append({'speaker':'Tamsin','text':'TAMSIN_PRIVATE_SENTINEL'})
        state['additionalResidents']['iona']['conversation'].append({'speaker':'Iona','text':'IONA_OWN_SENTINEL'})
        context=json.dumps(dialogue_context(state,'Hello','iona'))
        self.assertIn('IONA_OWN_SENTINEL',context)
        self.assertNotIn('MIRA_PRIVATE_SENTINEL',context)
        self.assertNotIn('TAMSIN_PRIVATE_SENTINEL',context)
        self.assertIn('Demon',context)
        self.assertIn('visiting',context)

    def test_review_retry_acceptance_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory);state=visiting_state()
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))
            settings=ProviderSettings(directory)
            settings.save({'enabled':True,'model':'test/model','apiKey':'fixture','maxOutputTokens':100})
            calls=[]
            def complete(settings,messages):
                calls.append(messages)
                return {'text':'Iona lays her pencil aside. “I have time.”','usage':{}}
            service=DialogueService(settings,complete)
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'characterId':'iona','text':'A moment?'}
            draft=service.generate(store,payload)
            self.assertEqual(store.read(),state)
            self.assertEqual(service.generate(store,payload),draft)
            self.assertEqual(len(calls),1)
            accepted=service.accept(store,{'draftId':draft['id']})
            self.assertEqual(accepted['conversation'],state['conversation'])
            self.assertEqual(len(accepted['additionalResidents']['iona']['conversation']),2)
            self.assertEqual(service.accept(store,{'draftId':draft['id']}),accepted)
            self.assertEqual(GameStore(directory).read(),accepted)
