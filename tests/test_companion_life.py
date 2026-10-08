from copy import deepcopy
import json
import tempfile
import unittest
from unittest.mock import patch
import uuid
import game as g
import summoning
import companion_life as life
from server import GameStore
from dialogue import dialogue_context

class CompanionLifeTests(unittest.TestCase):
    def setUp(self):
        self.state=g.new_campaign();self.state['sharedFunds']=200
        for key in self.state['materialInventory']:self.state['materialInventory'][key]=20
        for who,room in [('aurelia','west-chamber'),('neris','garden-chamber'),('iona','garden-chamber')]:
            summoning.initialize_person(self.state,who)
            self.state['residency'][who]['residencyStatus']='resident'
            self.state['additionalResidents'][who]['status']='resident'
            self.state['housingRooms'][room]['status']='complete';self.state['bedroomAssignments'][who]=room
    def act(self,kind,who=None,**fields):return g.apply_action(self.state,{'type':kind,**({'characterId':who} if who else {}),**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,who=None,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(g.RuleError):self.act(kind,who,**fields)
        self.assertEqual(before,self.state)

    def test_projects_pause_and_complete_with_independent_rewards(self):
        self.act('start-companion-project','aurelia');self.act('start-companion-project','neris')
        self.assertEqual(self.state['sharedFunds'],178)
        self.advance();self.act('assign-character','aurelia',assignment='rest');self.advance()
        self.assertEqual(self.state['additionalResidents']['aurelia']['personalProject']['completedWorkPhases'],1)
        self.assertEqual(self.state['additionalResidents']['neris']['personalProject']['completedWorkPhases'],2)
        self.act('resume-companion-project','aurelia');self.advance(2)
        for who,principle in [('aurelia','luminous-copying'),('neris','gentle-refraction')]:
            self.assertEqual(self.state['additionalResidents'][who]['personalProject']['status'],'complete')
            self.assertIn(principle,g.character_principles(self.state,who));self.assertIn(principle,self.state['archivePrinciples'])
            self.assertEqual(g.character_sheet(self.state,who)['earnedAdvancement'],2)
            self.reject('start-companion-project',who);self.reject('cancel-companion-project',who)
        self.assertNotIn('luminous-copying',g.character_principles(self.state,'founder'))
        self.advance(3)
        self.assertEqual(g.character_sheet(self.state,'aurelia')['earnedAdvancement'],2)

    def test_refund_uses_committed_costs_and_only_once(self):
        before=deepcopy(self.state);self.act('start-companion-project','aurelia');self.advance()
        with patch.dict(life.PROJECTS['aurelia'],{'costCrowns':99,'materials':{'fireglass':9}}):self.act('cancel-companion-project','aurelia')
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.assertEqual(g.character_sheet(self.state,'aurelia')['earnedAdvancement'],0)
        self.reject('cancel-companion-project','aurelia')

    def test_protected_stock_and_visitors_cannot_fund(self):
        self.state['materialReserveTargets']['fireglass']=20
        self.reject('start-companion-project','neris')
        self.state['materialReserveTargets']['fireglass']=0
        self.state['additionalResidents']['neris']['status']='visiting'
        self.state['residency']['neris']['residencyStatus']='visiting'
        self.reject('start-companion-project','neris');self.reject('choose-companion-ensemble','neris',ensembleId='evening')

    def test_funded_project_blocks_departure_until_cancelled(self):
        self.act('start-companion-project','neris')
        self.assertTrue(summoning.departure_blockers(self.state,'neris'))
        self.act('cancel-companion-project','neris')
        self.assertFalse(summoning.departure_blockers(self.state,'neris'))

    def test_style_presets_are_personal_free_and_bounded(self):
        before=deepcopy(self.state)
        self.act('choose-companion-ensemble','aurelia',ensembleId='evening')
        self.act('save-companion-style','aurelia',name='Lamplight')
        self.act('choose-companion-ensemble','aurelia',ensembleId='working')
        self.act('load-companion-style','aurelia',name='Lamplight')
        self.assertEqual(self.state['additionalResidents']['aurelia']['wardrobe']['ensembleId'],'evening')
        self.reject('load-companion-style','neris',name='Lamplight')
        for i in range(7):self.act('save-companion-style','aurelia',name='Look '+str(i))
        self.reject('save-companion-style','aurelia',name='Ninth')
        self.act('save-companion-style','aurelia',name='Lamplight')
        self.act('delete-companion-style','aurelia',name='Lamplight')
        for key in before:
            if key!='additionalResidents':self.assertEqual(self.state[key],before[key],key)
        self.reject('choose-companion-ensemble','aurelia',ensembleId='missing')

    def test_illustrated_invitation_keeps_chosen_look_on_replay(self):
        self.reject('join-resident-moment',momentId='aurelia-lamplit')
        self.act('start-companion-project','aurelia');self.advance(3)
        self.act('defer-resident-moment',momentId='aurelia-lamplit');self.advance(3)
        self.reject('join-resident-moment',momentId='aurelia-lamplit')
        self.act('restore-resident-moment',momentId='aurelia-lamplit')
        self.act('choose-companion-ensemble','aurelia',ensembleId='evening')
        before=deepcopy(self.state)
        self.act('join-resident-moment',momentId='aurelia-lamplit')
        self.assertEqual(g.resident_moment_view(self.state,'aurelia-lamplit')['illustrationId'],'aurelia')
        completed=deepcopy(self.state);self.act('join-resident-moment',momentId='aurelia-lamplit');self.assertEqual(completed,self.state)
        self.act('choose-companion-ensemble','aurelia',ensembleId='working')
        self.assertEqual(g.resident_moment_view(self.state,'aurelia-lamplit')['illustrationId'],'aurelia')
        for key in ('dayNumber','currentDayPhase','sharedFunds','resonancePoints','characterDevelopment'):self.assertEqual(self.state[key],before[key])

    def test_friendship_scene_stays_with_participants(self):
        iona=deepcopy(self.state['additionalResidents']['iona']['conversation'])
        self.act('join-resident-moment',momentId='aurelia-neris-evening')
        self.assertEqual(self.state['additionalResidents']['iona']['conversation'],iona)
        self.assertTrue(any(row['participants']==['aurelia','neris'] for row in g.resident_friendships(self.state)))
        self.assertEqual(self.state['additionalResidents']['aurelia']['conversation'][-1]['momentId'],'aurelia-neris-evening')

    def test_context_describes_saved_outfit(self):
        self.act('choose-companion-ensemble','neris',ensembleId='evening')
        context=json.dumps(dialogue_context(self.state,'Hello','neris'))
        self.assertIn('A ripple of violet',context)
        self.assertIn('Violet cowl-neck dress',context)

    def test_schema23_migration_preserves_money_work_and_existing_history(self):
        self.state['schemaVersion']=23
        for who in life.PROJECTS:
            self.state['additionalResidents'][who]['wardrobe'].pop('ensembleId')
            self.state['additionalResidents'][who]['personalProject']['status']='not-offered'
            self.state['people'][who]['offeredAssignments'].remove('personal-project')
        self.state['residentMoments'].pop('aurelia-lamplit')
        before=deepcopy(self.state);g.migrate_state(self.state)
        self.assertEqual(self.state['schemaVersion'],66)
        for who in life.PROJECTS:self.assertEqual(self.state['additionalResidents'][who]['wardrobe']['ensembleId'],'working')
        for key in ('sharedFunds','dayNumber','currentDayPhase','characterDevelopment'):self.assertEqual(self.state[key],before[key])
        migrated=deepcopy(self.state);g.migrate_state(self.state);self.assertEqual(self.state,migrated)

    def test_style_and_project_sqlite_retry_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.state),))
            for action in [{'type':'choose-companion-ensemble','characterId':'neris','ensembleId':'evening'},{'type':'start-companion-project','characterId':'neris'}]:
                payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action}
                result=store.action(payload);self.assertEqual(store.action(payload),result)
            self.assertEqual(GameStore(directory).read(),result)
