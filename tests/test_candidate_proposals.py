from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game as g
import summoning
from candidate_proposals import validate_candidate,candidate_context,approved_definition,PACKAGES
from dialogue import DialogueService,ProviderSettings,dialogue_context
from server import GameStore


def candidate_fixture(**changes):
    return {'name':'Vesper','adultAgeYears':24,'ancestryLabel':'Vampire','occupation':'candlemaker',
        'personality':'Warm, teasing and proud of a carefully finished piece.',
        'appearanceDescription':'Clearly adult woman with copper-brown skin, black curls and a fitted violet dress.',
        'origin':'An artisan from the river market, with a home and friends of her own.',
        'ambition':'Make lights that are useful and lovely to share.',
        'accommodationPreference':'separate-bed','capabilityPackageId':'light-maker','stayPreference':'open-to-staying',
        'introduction':'“Vesper. Your library sounds like a place worth visiting.”',
        'personalTopic':'“I like a room people want to linger in. A lamp can help.”',**changes}

class CandidateProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=GameStore(self.temp.name);self.settings=ProviderSettings(self.temp.name)
        self.settings.save({'enabled':True,'model':'test/model','apiKey':'fixture-secret','maxOutputTokens':1000})
        self.output=candidate_fixture();self.calls=[]
        def completion(settings,messages):
            self.calls.append(messages);return {'text':json.dumps(self.output),'usage':{'total_tokens':250}}
        self.service=DialogueService(self.settings,completion)
    def draft(self):
        self.payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision'],'purpose':'candidate-proposal','text':'A confident adult vampire artisan.'}
        return self.service.generate(self.store,self.payload)
    def accept(self,draft):return self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
    def seed(self,state):
        with self.store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))

    def test_structural_age_ancestry_budget_validation(self):
        state=self.store.read()
        for changes in [{'adultAgeYears':17},{'adultAgeYears':26},{'adultAgeYears':True},{'adultAgeYears':'24'},{'ancestryLabel':'Unknown ancestry'},{'capabilityPackageId':'archmage'},{'extraPowers':['free crowns']},{'stayPreference':'obedient'},{'name':'Eris'},{'name':'iona'},{'accommodationPreference':'anywhere'}]:
            with self.subTest(changes=changes),self.assertRaises(g.RuleError):validate_candidate(json.dumps(candidate_fixture(**changes)),state)
        with self.assertRaises(g.RuleError):validate_candidate('{"name":"One","name":"Two"}',state)
        with self.assertRaises(g.RuleError):validate_candidate('not json',state)
        with self.assertRaises(g.RuleError):validate_candidate('[]',state)
        p,r=validate_candidate(json.dumps(self.output),state)
        self.assertEqual(r['earnedAdvancement'],0);self.assertEqual(r['startingSkillRanks'],0);self.assertEqual(r['focusCapacity'],1)

    def test_generation_is_nonmutating_and_retries_once(self):
        before=self.store.read();draft=self.draft()
        self.assertEqual(draft['status'],'ready');self.assertEqual(self.store.read(),before)
        self.assertEqual(self.service.generate(self.store,self.payload),draft);self.assertEqual(len(self.calls),1)
        with self.assertRaises(g.RuleError):self.service.generate(self.store,{**self.payload,'text':'Another identity'})

    def test_explicit_review_required_and_only_plan_is_created(self):
        draft=self.draft();before=self.store.read()
        for payload in [{'draftId':draft['id']},{'draftId':draft['id'],'contentReviewed':'true','mechanicsReviewed':True}]:
            with self.assertRaises(g.RuleError):self.service.accept(self.store,payload)
            self.assertEqual(self.store.read(),before)
        state=self.accept(draft);who='summoned-'+draft['id']
        self.assertIn(who,state['reviewedCandidates']);self.assertNotIn(who,state['people'])
        for key in before:
            if key not in ('reviewedCandidates','revision'):self.assertEqual(before[key],state[key],key)
        self.assertEqual(self.accept(draft),state);self.assertEqual(GameStore(self.temp.name).read(),state)

    def test_invalid_provider_output_stays_failed_without_person(self):
        self.output=candidate_fixture(adultAgeYears=16);before=self.store.read();draft=self.draft()
        self.assertEqual(draft['status'],'failed');self.assertNotIn('proposal',draft);self.assertEqual(self.store.read(),before)

    def test_recheck_same_identity_after_campaign_change_without_provider_call(self):
        draft=self.draft();state=self.store.read();g.apply_action(state,{'type':'advance'});state['revision']+=1;self.seed(state)
        with self.assertRaises(g.RuleError):self.accept(draft)
        revised=self.service.review_candidate(self.store,{'draftId':draft['id'],'expectedRevision':state['revision']})
        self.assertEqual(revised['proposal'],draft['proposal']);self.assertEqual(len(self.calls),1)
        self.assertEqual(revised['generationRevision'],draft['baseRevision'])
        self.assertEqual(self.service.generate(self.store,self.payload),revised)
        self.assertIn('summoned-'+draft['id'],self.accept(revised)['reviewedCandidates'])

    def test_recheck_rejects_name_conflict(self):
        first=self.draft();second=self.draft();self.accept(first)
        with self.assertRaises(g.RuleError):self.service.review_candidate(self.store,{'draftId':second['id'],'expectedRevision':self.store.read()['revision']})

    def test_context_excludes_private_histories_and_secrets(self):
        state=self.store.read();state['conversation']=[{'speaker':'Mira','text':'PRIVATE_CONVERSATION'}];state['hiddenTruth']='SECRET_CASTLE'
        context=json.dumps(candidate_context(state,'A visitor'))
        self.assertNotIn('PRIVATE_CONVERSATION',context);self.assertNotIn('SECRET_CASTLE',context);self.assertNotIn('fixture-secret',context)

    def lifecycle(self,visit_only=False):
        self.output=candidate_fixture(stayPreference='visit-only' if visit_only else 'open-to-staying')
        draft=self.draft();state=self.accept(draft);who='summoned-'+draft['id']
        state['sharedFunds']=100;state['materialInventory']['porous-clay']=3;state['materialInventory']['binding-thread']=3
        state['housingRooms']['garden-chamber']['status']='complete';g.learn_for_character(state,'founder','courteous-passage')
        g.apply_action(state,{'type':'summoning-prepare','candidateId':who,'conductorId':'founder','materials':['porous-clay','binding-thread']})
        for _ in range(2):g.apply_action(state,{'type':'advance'})
        cid='threshold-1'
        for topic in ('intentions','home','visit'):g.apply_action(state,{'type':'summoning-talk','contactId':cid,'topic':topic})
        g.apply_action(state,{'type':'summoning-invite','contactId':cid,'roomId':'garden-chamber'});g.apply_action(state,{'type':'advance'})
        return state,who,cid

    def test_reviewed_person_uses_full_lifecycle_and_independent_budget(self):
        state,who,cid=self.lifecycle()
        self.assertEqual(state['sharedFunds'],88);self.assertNotIn(who,g.household_members(state))
        g.apply_action(state,{'type':'summoning-ask-stay','contactId':cid});g.apply_action(state,{'type':'summoning-household-decision','contactId':cid,'decision':'invite-to-stay'})
        self.assertIn(who,g.household_members(state));self.assertEqual(g.character_sheet(state,who)['earnedAdvancement'],0)
        self.assertEqual(g.character_principles(state,who),PACKAGES['light-maker']['principles'])
        self.assertTrue(all(rank==0 for rank in state['characterSkills'][who].values()))
        identity=deepcopy(state['people'][who]);g.apply_action(state,{'type':'summoning-depart','contactId':cid});g.apply_action(state,{'type':'advance'})
        g.apply_action(state,{'type':'summoning-invite','contactId':cid,'roomId':'garden-chamber'});g.apply_action(state,{'type':'advance'})
        self.assertEqual(state['people'][who],identity)
        self.assertEqual(g.public_state(state)['originalAssets'][who],'/assets/placeholders/visitor-placeholder.svg')
        self.assertIn('Vesper',json.dumps(dialogue_context(state,'Hello',who)))

    def test_visit_only_preference_cannot_be_overridden_by_household(self):
        state,who,cid=self.lifecycle(True)
        for _ in range(3):
            g.apply_action(state,{'type':'summoning-household-decision','contactId':cid,'decision':'invite-to-stay'})
            g.apply_action(state,{'type':'summoning-ask-stay','contactId':cid})
        self.assertEqual(state['residency'][who]['candidateStayDecision'],'prefers-to-leave')
        self.assertEqual(state['residency'][who]['residencyStatus'],'visiting');self.assertNotIn(who,g.household_members(state))

    def test_plan_portrait_override_and_rollback_remain_cosmetic(self):
        draft=self.draft();state=self.accept(draft);who='summoned-'+draft['id'];before=deepcopy(state)
        g.apply_action(state,{'type':'accept-artwork','assetId':who,'assetPath':'/user-assets/reviewed.png'})
        self.assertEqual(state['people'],before['people']);self.assertEqual(state['reviewedCandidates'],before['reviewedCandidates'])
        g.apply_action(state,{'type':'rollback-artwork','assetId':who})
        self.assertEqual(state['assetOverrides'][who],'/assets/placeholders/visitor-placeholder.svg')

    def test_legacy_schema24_migration_does_not_create_people_or_spend(self):
        state=self.store.read();state['schemaVersion']=24;state.pop('reviewedCandidates');before=deepcopy(state)
        g.migrate_state(state);self.assertEqual(state['reviewedCandidates'],{})
        for key in before:
            if key!='schemaVersion':self.assertEqual(state[key],before[key])

    def test_plan_limit_and_duplicate_name_are_enforced(self):
        state=self.store.read()
        for n in range(50):state['reviewedCandidates']['summoned-'+str(n)]=approved_definition(candidate_fixture(name='Visitor '+str(n)),'summoned-'+str(n),'test','draft')
        self.seed(state)
        with self.assertRaises(g.RuleError):self.draft()
        self.assertEqual(len(self.calls),0)
