from copy import deepcopy
import json
import tempfile
import threading
import unittest
import urllib.request
import uuid
from dialogue import DialogueService, ProviderSettings
from game import RuleError
from server import GameStore, create_server
from spell_proposals import proposal_context, validate_proposal

class SpellProposalTests(unittest.TestCase):
    def test_provider_spell_design_is_rejected_before_call_or_mutation(self):
        with tempfile.TemporaryDirectory() as root:
            store=GameStore(root);settings=ProviderSettings(root);calls=[]
            settings.save({'enabled':True,'model':'example/model','apiKey':'test-secret','maxOutputTokens':500})
            service=DialogueService(settings,lambda *args:calls.append(args))
            before=store.read()
            with self.assertRaisesRegex(RuleError,'Choose a spell in the Spellbook'):
                service.generate(store,{'requestId':uuid.uuid4().hex,'expectedRevision':before['revision'],'purpose':'spell-proposal','ownerId':'founder','text':'Invent a spell'})
            self.assertEqual(calls,[]);self.assertEqual(before,store.read())
    def test_legacy_validator_remains_bounded(self):
        from game import new_campaign
        s=new_campaign();proposal={'formId':'warm-twist','name':'Old custom title','explanation':'An old description','limitations':[]}
        old,review=validate_proposal(json.dumps(proposal),s,'founder')
        self.assertEqual(old['name'],'Old custom title');self.assertIn('Consume 1 silver ivy',review['exactEffect'])
        for change in ({'formId':'free-infinite-gold'},{'cost':0},{'formId':[]},{'limitations':'none'}):
            with self.assertRaises(RuleError):validate_proposal(json.dumps({**proposal,**change}),s,'founder')
