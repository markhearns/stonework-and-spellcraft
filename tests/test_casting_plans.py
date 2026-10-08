from copy import deepcopy
import tempfile
import unittest
import uuid
from game import new_campaign,apply_action,learn_for_character,RuleError,SPELL_FORMS,public_state
from server import GameStore

class CastingPlanTests(unittest.TestCase):
    def setUp(self):
        self.state=new_campaign();self.state['sharedFunds']=200
        for key in self.state['materialInventory']:self.state['materialInventory'][key]=20
        self.state['restorationStatus']='complete'
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def spell(self,who='founder',form='warm-twist'):
        learn_for_character(self.state,who,SPELL_FORMS[form]['requiredPrinciple'])
        materials={'warm-twist':['sun-amber','binding-thread'],'root-song':['silver-ivy','binding-thread'],'luminous-copy':['moon-glass','sun-amber']}[form]
        self.act('draft-spell',characterId=who,formId=form,name='Useful working',intent='The listed effect.',materials=materials)
        key=self.state['spellbook'][-1]['id'];self.act('test-spell',spellId=key);self.advance(2)
        self.act('prepare-spells',characterId=who,spellIds=[key]);return key
    def plan(self,who,key,count=3):self.act('plan-castings',characterId=who,spellId=key,requestedCount=count)
    def test_finite_plan_exact_outputs_no_early_commit_and_no_extra_cast(self):
        key=self.spell();before=deepcopy(self.state);self.plan('founder',key)
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.advance(3)
        self.assertEqual(self.state['castingPlans']['founder']['completedCount'],3)
        self.assertEqual(self.state['castingPlans']['founder']['status'],'complete')
        self.assertEqual(self.state['materialInventory']['silver-ivy'],before['materialInventory']['silver-ivy']-3)
        self.assertEqual(self.state['materialInventory']['binding-thread'],before['materialInventory']['binding-thread']+6)
        self.assertEqual(self.state['characterDevelopment'],before['characterDevelopment'])
        after=deepcopy(self.state['materialInventory']);self.advance();self.assertEqual(self.state['materialInventory'],after)
    def test_protected_stock_waits_without_spending_shared_or_personal_funds(self):
        key=self.spell();self.state['materialReserveTargets']['silver-ivy']=20
        self.plan('founder',key);before=self.state['sharedFunds'];self.advance()
        self.assertEqual(self.state['castingPlans']['founder']['completedCount'],0)
        self.assertEqual(self.state['sharedFunds'],before);self.assertIn('unreserved',' '.join(public_state(self.state)['castingPlanViews']['founder']['blockers']))
        self.act('set-material-reserve',materialId='silver-ivy',target=19);self.advance(2)
        self.assertEqual(self.state['castingPlans']['founder']['completedCount'],1)
        self.assertEqual(self.state['personalFunds']['founder'],0)
    def test_assignment_pause_prepare_changes_and_cancellation_are_explicit(self):
        key=self.spell();self.plan('founder',key);self.advance()
        self.act('assign-founder',assignment='rest');self.advance();self.assertEqual(self.state['castingPlans']['founder']['completedCount'],1)
        self.act('resume-casting-plan',characterId='founder');self.act('prepare-spells',characterId='founder',spellIds=[])
        self.assertEqual(self.state['castingPlans']['founder']['status'],'paused')
        self.reject('resume-casting-plan',characterId='founder')
        self.act('prepare-spells',characterId='founder',spellIds=[key]);self.advance();self.assertEqual(self.state['castingPlans']['founder']['completedCount'],1)
        self.act('resume-casting-plan',characterId='founder');self.act('cancel-casting-plan',characterId='founder');self.advance()
        self.assertEqual(self.state['castingPlans']['founder']['completedCount'],1)
        self.act('cast-spell',spellId=key);self.advance();self.assertEqual(self.state['spellbook'][0]['castCount'],2)
    def test_count_ownership_preparation_and_manual_job_conflicts(self):
        key=self.spell();other=self.spell('mira')
        for count in (0,13,True,1.5,'3'):self.reject('plan-castings',characterId='founder',spellId=key,requestedCount=count)
        self.reject('plan-castings',characterId='founder',spellId=other,requestedCount=1)
        self.act('cast-spell',spellId=key);self.reject('plan-castings',characterId='founder',spellId=key,requestedCount=1)
        self.act('cancel-spell-casting',characterId='founder');self.plan('founder',key)
        self.reject('cast-spell',spellId=key);self.reject('plan-castings',characterId='founder',spellId=key,requestedCount=1)
    def test_resident_plan_runs_during_scholar_travel_without_remote_replanning(self):
        key=self.spell('mira','luminous-copy');self.plan('mira',key,2);before=self.state['sharedFunds']
        self.act('start-expedition');self.advance();self.reject('pause-casting-plan',characterId='mira')
        self.act('choose-expedition-approach',approach='survey');self.advance()
        self.assertEqual(self.state['castingPlans']['mira']['status'],'complete');self.assertEqual(self.state['sharedFunds'],before+12)
    def test_same_phase_output_does_not_feed_another_casting_plan(self):
        root=self.spell('founder','root-song');binding=self.spell('mira','warm-twist')
        self.state['materialInventory']['silver-ivy']=0
        self.plan('founder',root,2);self.plan('mira',binding,2);self.advance()
        self.assertEqual(self.state['castingPlans']['mira']['completedCount'],0)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],2)
        self.advance();self.assertEqual(self.state['castingPlans']['mira']['completedCount'],1)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],3)
    def test_two_casting_plans_compete_for_stock_without_negative_inventory(self):
        first=self.spell('founder');second=self.spell('mira');self.state['materialInventory']['silver-ivy']=1
        self.plan('founder',first,1);self.plan('mira',second,1);self.advance()
        self.assertEqual(self.state['materialInventory']['silver-ivy'],0)
        self.assertEqual(self.state['castingPlans']['founder']['completedCount'],1)
        self.assertEqual(self.state['castingPlans']['mira']['completedCount'],0)
    def test_plan_retry_and_reload_keep_exact_count(self):
        import json,sqlite3
        key=self.spell()
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=?',(json.dumps(self.state),))
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'plan-castings','characterId':'founder','spellId':key,'requestedCount':2}}
            once=store.action(payload);self.assertEqual(store.action(payload),once)
            advance={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'advance'}}
            once=store.action(advance);self.assertEqual(store.action(advance),once)
            self.assertEqual(GameStore(directory).read()['castingPlans']['founder']['completedCount'],1)
