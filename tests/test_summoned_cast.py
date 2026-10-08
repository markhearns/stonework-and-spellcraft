from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
import game as g
import summoning as s
from dialogue import dialogue_context
from server import GameStore

class SummonedCastTests(unittest.TestCase):
    def setUp(self):
        self.state=g.new_campaign();self.state['sharedFunds']=200
        for m in ('porous-clay','binding-thread'):self.state['materialInventory'][m]=10
        for who in ('founder','mira'):g.learn_for_character(self.state,who,'courteous-passage')
        for room in ('west-chamber','garden-chamber'):self.state['housingRooms'][room]['status']='complete'
    def act(self,kind,**fields):return g.apply_action(self.state,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def prepare(self,who,conductor='founder'):
        self.act('summoning-prepare',candidateId=who,conductorId=conductor,materials=['porous-clay','binding-thread'])
        return 'threshold-'+str(self.state['nextSummoningContactNumber']-1)
    def open(self,who):
        cid=self.prepare(who);self.advance(2)
        for topic in s.CANDIDATES[who]['topics']:self.act('summoning-talk',contactId=cid,topic=topic)
        return cid
    def join(self,who,room):
        cid=self.open(who);self.act('summoning-invite',contactId=cid,roomId=room);self.advance()
        self.act('summoning-ask-stay',contactId=cid)
        self.act('summoning-household-decision',contactId=cid,decision='invite-to-stay')
        return cid
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(before,self.state)

    def test_new_profiles_have_distinct_competence_and_real_assets(self):
        for who in ('aurelia','neris'):
            s.initialize_person(self.state,who)
            s.validate_npc_profile(self.state['people'][who],True)
            self.assertEqual(g.character_principles(self.state,who),s.CANDIDATES[who]['principles'])
            self.assertEqual(self.state['signatureFocuses'][who]['name'],s.CANDIDATES[who]['focusName'])
            self.assertTrue((Path(__file__).parents[1]/'static'/g.ORIGINAL_ASSETS[who].lstrip('/')).is_file())
        self.assertNotEqual(self.state['people']['aurelia']['startingPractices'],self.state['people']['neris']['startingPractices'])

    def test_all_three_can_join_without_duplicating_identity(self):
        for who,room in [('iona','garden-chamber'),('aurelia','west-chamber'),('neris','garden-chamber')]:
            cid=self.join(who,room)
            self.assertIn(who,g.household_members(self.state))
            self.act('summoning-personal-talk',contactId=cid,topic='flirt')
            view=g.public_state(self.state)
            self.assertIn(who,view['characterSheets'])
            self.assertEqual(view['characterSheets'][who]['earnedAdvancement'],0)
            self.reject('summoning-prepare',candidateId=who,conductorId='mira',materials=['porous-clay','binding-thread'])
        self.assertEqual(len(g.household_members(self.state)),5)
        self.assertEqual(self.state['additionalResidents']['aurelia']['personalProject']['status'],'not-started')
        self.assertEqual(self.state['additionalResidents']['neris']['personalProject']['status'],'not-started')

    def test_private_room_preference_and_crowding(self):
        cid=self.open('aurelia')
        self.reject('summoning-invite',contactId=cid,roomId='garden-chamber')
        self.act('summoning-invite',contactId=cid,roomId='west-chamber');self.advance()
        self.assertEqual(self.state['residency']['aurelia']['residencyStatus'],'visiting')
        self.reject('assign-character',characterId='aurelia',assignment='rest')

    def test_one_preparation_per_conductor_but_independent_conductors(self):
        a=self.prepare('aurelia')
        self.reject('summoning-prepare',candidateId='neris',conductorId='founder',materials=['porous-clay','binding-thread'])
        n=self.prepare('neris','mira');self.advance()
        self.assertEqual(self.state['summoningContacts'][a]['completedWorkPhases'],1)
        self.assertEqual(self.state['summoningContacts'][n]['completedWorkPhases'],1)
        self.advance()
        self.assertEqual(self.state['summoningContacts'][a]['personId'],'aurelia')
        self.assertEqual(self.state['summoningContacts'][n]['personId'],'neris')

    def test_cancelled_candidate_refunds_and_can_be_prepared_again(self):
        before=deepcopy(self.state);cid=self.prepare('neris')
        self.act('summoning-cancel',contactId=cid)
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.assertNotIn('neris',self.state['people'])
        self.reject('summoning-cancel',contactId=cid)
        self.prepare('neris')

    def test_departure_return_and_context_are_person_specific(self):
        for who,room in [('aurelia','west-chamber'),('neris','garden-chamber')]:
            cid=self.join(who,room);identity=deepcopy(self.state['people'][who])
            self.act('summoning-personal-talk',contactId=cid,topic='flirt')
            own=deepcopy(self.state['additionalResidents'][who]['conversation'])
            self.state['conversation'].append({'speaker':'Mira','text':'PRIVATE_MIRA'})
            context=json.dumps(dialogue_context(self.state,'Hello',who))
            self.assertNotIn('PRIVATE_MIRA',context)
            self.assertIn(identity['ancestryLabel'],context)
            self.act('summoning-depart',contactId=cid);self.advance()
            self.act('summoning-close',contactId=cid);self.act('summoning-reopen',contactId=cid)
            self.act('summoning-invite',contactId=cid,roomId=room);self.advance()
            self.assertEqual(self.state['people'][who],identity)
            self.assertEqual(self.state['additionalResidents'][who]['conversation'],own)
            self.assertEqual(self.state['residency'][who]['candidateStayDecision'],'undecided')

    def test_legacy_iona_preparation_never_becomes_another_person(self):
        cid=self.prepare('iona');self.state['summoningContacts'][cid].pop('candidateId')
        self.advance(2)
        self.assertEqual(self.state['summoningContacts'][cid]['personId'],'iona')
        self.assertEqual(s.view(self.state)['contacts'][0]['candidateId'],'iona')

    def test_unknown_candidate_is_atomic(self):
        for invalid in ['human','missing',None,[]]:self.reject('summoning-prepare',candidateId=invalid,conductorId='founder',materials=['porous-clay','binding-thread'])

    def test_sqlite_candidate_retry_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.state),))
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.state['revision'],'action':{'type':'summoning-prepare','candidateId':'aurelia','conductorId':'founder','materials':['porous-clay','binding-thread']}}
            result=store.action(payload)
            self.assertEqual(store.action(payload),result)
            self.assertEqual(GameStore(directory).read(),result)
            self.assertEqual(result['summoningContacts']['threshold-1']['candidateId'],'aurelia')
