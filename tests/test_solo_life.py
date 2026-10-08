import copy
import tempfile
import unittest
import uuid
import game as g
import phase_tasks as tasks
import solo_life as life
from server import GameStore

class SoloLifeTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign('fresh')
    def resident(self):
        g.apply_action(self.s,{'type':'cheat-toggle','enabled':True})
        g.apply_action(self.s,{'type':'cheat-character','ancestry':'Human','name':'Aster'})
        return g.household_members(self.s)[1]
    def agree(self,who,role):
        g.apply_action(self.s,{'type':'agree-household-role','characterId':who,'role':role,'enabled':True,'willingnessReviewed':True})
    def test_garden_scholar_resident_withdrawal_and_one_harvest(self):
        s=self.s;who=self.resident();s['restorationStatus']='complete'
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'assign-gardener','characterId':who})
        self.agree(who,'garden')
        g.apply_action(s,{'type':'assign-gardener','characterId':'founder'})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'assign-gardener','characterId':who})
        before=s['materialInventory']['silver-ivy'];g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['materialInventory']['silver-ivy'],before+1)
        g.apply_action(s,{'type':'assign-founder','assignment':'rest'})
        g.apply_action(s,{'type':'assign-gardener','characterId':who})
        self.assertEqual(g.household_resident_room(s,who),'conservatory')
        g.apply_action(s,{'type':'start-expedition','siteId':'old-waterworks'})
        g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['materialInventory']['silver-ivy'],before+2)
        g.apply_action(s,{'type':'return-expedition'});g.apply_action(s,{'type':'advance'})
        g.apply_action(s,{'type':'agree-household-role','characterId':who,'role':'garden','enabled':False})
        self.assertEqual(g.character_assignment(s,who),'rest')
        self.assertFalse(life.offered(s,who,'garden'))
    def test_actual_companion_presence_skill_learning_rewards_and_return(self):
        s=self.s;who=self.resident()
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'start-expedition','companionId':who})
        self.agree(who,'fieldwork');s['characterSkills'][who]['fieldcraft']=1
        g.apply_action(s,{'type':'start-expedition','companionId':who})
        self.assertEqual(g.expedition_party(s),['founder',who]);self.assertFalse(g.character_at_castle(s,who))
        self.assertNotIn(who,g.public_state(s)['presentPeople'])
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'assign-character','characterId':who,'assignment':'rest'})
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'agree-household-role','characterId':who,'role':'fieldwork','enabled':False})
        g.apply_action(s,{'type':'advance'})
        g.apply_action(s,{'type':'choose-expedition-approach','approach':'survey'})
        self.assertEqual(s['expedition']['remainingWorkPhases'],1)
        g.apply_action(s,{'type':'advance'});g.apply_action(s,{'type':'return-expedition'});g.apply_action(s,{'type':'advance'})
        self.assertIn('water-guidance',g.character_principles(s,who));self.assertNotIn('water-guidance',g.character_principles(s,'mira'))
        self.assertIn('old-waterworks:survey',s['characterDevelopment'][who]['advancementAwards'])
        self.assertEqual(s['lastExpeditionReport']['participants'],['founder',who])
        self.assertTrue(g.character_at_castle(s,who));self.assertEqual(g.character_assignment(s,who),'rest')
    def test_invalid_agreements_and_early_return_grant_nothing(self):
        s=self.s;who=self.resident()
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'agree-household-role','characterId':who,'role':'fieldwork','enabled':True})
        self.agree(who,'fieldwork');known=list(g.character_principles(s,who));earned=copy.deepcopy(s['characterDevelopment'][who])
        g.apply_action(s,{'type':'start-expedition','companionId':who});g.apply_action(s,{'type':'return-expedition'});g.apply_action(s,{'type':'advance'})
        self.assertEqual(g.character_principles(s,who),known);self.assertEqual(s['characterDevelopment'][who],earned)
    def test_housewarming_actual_participants_once_without_phase_or_rewards(self):
        s=self.s;who=self.resident()
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'celebrate-solo-household'})
        for p in s['facilityProjects'].values():p['status']='complete'
        s['householdArtifactPlacements']['hearth-kettle']=True;g.check_living_wing_milestone(s)
        before=(s['dayNumber'],s['currentDayPhase'],s['sharedFunds'],s['resonancePoints'])
        g.apply_action(s,{'type':'celebrate-solo-household'})
        self.assertEqual(s['soloLife']['housewarming']['participants'],['founder',who])
        self.assertNotIn('Mira',s['soloLife']['housewarming']['text'])
        self.assertEqual(before,(s['dayNumber'],s['currentDayPhase'],s['sharedFunds'],s['resonancePoints']))
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'celebrate-solo-household'})
    def test_task_board_nonmutating_ready_costs_new_phase_and_dismissal(self):
        s=self.s;before=copy.deepcopy(s);initial=tasks.build(s)
        self.assertEqual(before,s)
        self.assertIn('hearth-study',[r['id'] for r in initial['tasks']]);self.assertNotIn('first-lantern',[r['id'] for r in initial['tasks']])
        g.apply_action(s,{'type':'phase-task-dismiss','taskId':'meet:maren'})
        self.assertTrue(next(r for r in tasks.build(s)['tasks'] if r['id']=='meet:maren')['dismissed'])
        g.apply_action(s,{'type':'phase-task-run','taskId':'hearth-study'})
        self.assertEqual(s['sharedFunds'],20)
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'phase-task-run','taskId':'hearth-study'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        rows={r['id']:r for r in tasks.build(s)['tasks']}
        self.assertIn('first-lantern',rows);self.assertIn('research:archive-foundations',rows)
        self.assertIn('first-lantern',tasks.build(s)['newIds'])
        self.assertIn('first-lantern',tasks.build(g.migrate_state(copy.deepcopy(s)))['newIds'])
        self.assertFalse(rows['meet:maren']['dismissed'])
        g.apply_action(s,{'type':'phase-task-run','taskId':'first-lantern'})
        g.apply_action(s,{'type':'assign-founder','assignment':'rest'})
        self.assertIn('resume:founder:crafting',[r['id'] for r in tasks.build(s)['tasks']])
        g.apply_action(s,{'type':'phase-task-run','taskId':'resume:founder:crafting'})
        for _ in range(2):g.apply_action(s,{'type':'advance'})
        self.assertIn('install:lantern',[r['id'] for r in tasks.build(s)['tasks']])
    def test_task_transaction_stale_rejection_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d,start_type='fresh')
            p={'requestId':uuid.uuid4().hex,'expectedRevision':0,'action':{'type':'phase-task-run','taskId':'hearth-study'}}
            once=store.action(p);self.assertEqual(store.action(p),once)
            invalid={'requestId':uuid.uuid4().hex,'expectedRevision':once['revision'],'action':{'type':'phase-task-run','taskId':'hearth-study'}}
            with self.assertRaises(g.RuleError):store.action(invalid)
            self.assertEqual(store.read(),once)
    def test_waiting_expedition_choices_are_quick_actions_and_not_dismissible(self):
        s=self.s;g.apply_action(s,{'type':'start-expedition'});g.apply_action(s,{'type':'advance'})
        rows=tasks.build(s)['tasks'];self.assertTrue(all(r['group']=='choice' for r in rows))
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':'phase-task-dismiss','taskId':'field-choice:survey'})
        g.apply_action(s,{'type':'phase-task-run','taskId':'field-choice:survey'})
        for _ in range(2):g.apply_action(s,{'type':'advance'})
        self.assertEqual(tasks.build(s)['tasks'][0]['id'],'field-return')
    def test_companion_personal_wealth_and_observatory_return(self):
        s=self.s;who=self.resident();self.agree(who,'fieldwork');s['expeditionWealthPlan']='half-personal'
        g.apply_action(s,{'type':'start-expedition','companionId':who})
        g.apply_action(s,{'type':'advance'});g.apply_action(s,{'type':'choose-expedition-approach','approach':'salvage'})
        g.apply_action(s,{'type':'advance'});g.apply_action(s,{'type':'return-expedition'});g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['personalFunds'][who],2);self.assertEqual(s['personalFunds']['founder'],2);self.assertEqual(s['personalFunds']['mira'],0)
        s['binderyDiscoveries']=['survey']
        g.apply_action(s,{'type':'start-expedition','siteId':'rainward-observatory','companionId':who})
        # Seed a completed field lead to test its distinct multi-stage return resolver.
        s['expedition'].update(chosenApproach='survey',discoveryReady=True)
        g.apply_action(s,{'type':'return-expedition'});g.apply_action(s,{'type':'advance'})
        self.assertIn('gentle-refraction',g.character_principles(s,who))
        self.assertEqual(g.character_assignment(s,who),'rest');self.assertTrue(g.character_at_castle(s,who))
        self.assertEqual(s['lastExpeditionReport']['participants'],['founder',who])

    def test_new_public_completion_is_not_lost_among_old_inventory(self):
        s=self.s
        s['publicWorkshop']['receipts']['recent']={'id':'recent','recordId':'unknown-fixture','name':'A finished work','status':'complete','day':1,'phase':'morning','ownerId':'founder'}
        s['currentDayPhase']='afternoon'
        self.assertIn('public-complete:recent',[r['id'] for r in tasks.build(s)['tasks']])
        s['currentDayPhase']='evening'
        self.assertNotIn('public-complete:recent',[r['id'] for r in tasks.build(s)['tasks']])

    def test_schema38_preserves_state_and_adds_role_records(self):
        s=self.s;s['schemaVersion']=38;s.pop('soloLife');s['sharedFunds']=57
        g.migrate_state(s);self.assertEqual(s['schemaVersion'],66);self.assertEqual(s['sharedFunds'],57)
        self.assertEqual(s['soloLife']['agreements'],{})
