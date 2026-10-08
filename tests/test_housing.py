from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, resident_room
from server import GameStore

class HousingTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def ready(self):self.state['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
    def restore(self,room='west-chamber'):
        self.ready();self.act('fund-housing',roomId=room);self.advance(2 if room=='west-chamber' else 3)
    def test_funding_prerequisites_cost_once_and_pause(self):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('fund-housing',roomId='west-chamber')
        self.assertEqual(self.state,before)
        self.ready();self.act('fund-housing',roomId='west-chamber');self.advance()
        self.assertEqual(self.state['sharedFunds'],64)
        self.act('fund-housing',roomId='garden-chamber');self.advance()
        self.assertEqual(self.state['sharedFunds'],40)
        self.assertEqual(self.state['housingRooms']['west-chamber']['completedWorkPhases'],1)
        self.act('resume-housing',roomId='west-chamber');self.advance()
        self.assertEqual(self.state['housingRooms']['west-chamber']['status'],'complete')
        self.assertEqual(self.state['bedroomAssignments'],{'founder':'bedchamber','mira':'bedchamber'})
        self.assertEqual(public_state(self.state)['housingSummary']['availableBeds'],1)
        with self.assertRaises(RuleError):self.act('fund-housing',roomId='west-chamber')
        self.act('resume-housing',roomId='garden-chamber');self.advance(2)
        self.assertEqual(public_state(self.state)['housingSummary']['usableBeds'],5)
        self.assertEqual(self.state['sharedFunds'],40)
    def test_reservation_validation_and_moves_preserve_people(self):
        self.restore()
        self.act('reserve-beds',roomId='west-chamber',reservedBeds=1)
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('choose-bedroom',roomId='west-chamber',characterId='mira')
        self.assertEqual(self.state,before)
        for target in (True,-1,2,1.5):
            with self.assertRaises(RuleError):self.act('reserve-beds',roomId='west-chamber',reservedBeds=target)
        self.act('reserve-beds',roomId='west-chamber',reservedBeds=0)
        self.act('choose-bedroom',roomId='west-chamber',characterId='mira')
        self.assertEqual(self.state['bedroomAssignments']['mira'],'west-chamber')
        self.assertEqual(self.state['characterDevelopment'],before['characterDevelopment'])
        self.assertEqual(self.state['resonancePoints'],before['resonancePoints'])
        self.assertEqual(self.state['dayNumber'],before['dayNumber'])
        with self.assertRaises(RuleError):self.act('choose-bedroom',roomId='west-chamber',characterId='founder')
        with self.assertRaises(RuleError):self.act('reserve-beds',roomId='west-chamber',reservedBeds=1)
        again=deepcopy(self.state);self.act('choose-bedroom',roomId='west-chamber',characterId='mira');self.assertEqual(self.state,again)
    def test_evening_location_room_access_and_independent_furnishings(self):
        with self.assertRaises(RuleError):self.act('select-room',roomId='garden-chamber')
        self.restore('garden-chamber')
        self.act('choose-bedroom',roomId='garden-chamber',characterId='mira')
        self.state['currentDayPhase']='evening'
        self.assertEqual(resident_room(self.state),'garden-chamber')
        self.act('select-room',roomId='garden-chamber');self.act('decorate',roomId='garden-chamber',furnishing='none')
        self.assertNotEqual(self.state['roomFurnishings']['garden-chamber'],self.state['roomFurnishings']['bedchamber'])
        self.assertIn('garden-chamber',public_state(self.state)['availableRoomIds'])
        self.state['miraArchiveProject']['status']='complete'
        self.act('start-expedition',companionId='mira')
        self.assertIsNone(resident_room(self.state))
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('choose-bedroom',roomId='bedchamber',characterId='mira')
        self.assertEqual(self.state,before)
    def test_expedition_pauses_housing_and_return_requires_resuming(self):
        self.ready();self.act('fund-housing',roomId='west-chamber');self.advance()
        self.act('start-expedition');self.advance()
        self.assertEqual(self.state['housingRooms']['west-chamber']['completedWorkPhases'],1)
        self.act('return-expedition');self.advance()
        self.assertEqual(self.state['housingRooms']['west-chamber']['completedWorkPhases'],1)
        self.act('resume-housing',roomId='west-chamber');self.advance()
        self.assertEqual(self.state['housingRooms']['west-chamber']['status'],'complete')
    def test_insufficient_funds_is_atomic(self):
        self.ready();self.state['sharedFunds']=15;before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act('fund-housing',roomId='west-chamber')
        self.assertEqual(self.state,before)
    def test_schema_eight_migration_and_retry_reload(self):
        old=deepcopy(self.state);old['schemaVersion']=8
        for key in ('housingRooms','bedroomAssignments','activeHousingRoomId'):old.pop(key)
        for key in ('west-chamber','garden-chamber'):old['roomFurnishings'].pop(key)
        old['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            for key,value in old.items():
                if key not in ('schemaVersion','revision','roomFurnishings'):self.assertEqual(state[key],value,key)
            for key,value in old['roomFurnishings'].items():self.assertEqual(state['roomFurnishings'][key],value)
            self.assertTrue((Path(directory)/'campaign-before-schema-8-to-66.sqlite3').exists())
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'fund-housing','roomId':'west-chamber'}}
            funded=store.action(payload);self.assertEqual(store.action(payload),funded)
            self.assertEqual(funded['sharedFunds'],64)
            self.assertEqual(GameStore(directory).read(),funded)
