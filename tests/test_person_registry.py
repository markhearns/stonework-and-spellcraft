from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from game import (new_campaign, migrate_state, apply_action, public_state, CHARACTERS,
                  reserve_arrival, arrival_blockers, known_people, present_household_members, RuleError)
from server import GameStore


class PersonRegistryTests(unittest.TestCase):
    def setUp(self):
        self.state = new_campaign()

    def ready_invitation(self):
        self.state['binderyDiscoveries'] = ['salvage']
        apply_action(self.state, {'type':'meet-candidate'})
        for topic in ('work','home','plans'):
            apply_action(self.state, {'type':'talk-candidate','topic':topic})
        self.state['housingRooms']['west-chamber']['status'] = 'complete'
        apply_action(self.state, {'type':'invite-candidate','roomId':'west-chamber'})

    def test_profiles_are_campaign_owned_and_not_membership(self):
        other = new_campaign()
        self.state['people']['mira']['name'] = 'A local test name'
        self.assertEqual(public_state(self.state)['characterCatalog']['mira']['name'],'A local test name')
        self.assertEqual(other['people']['mira']['name'],'Mira')
        self.assertEqual(CHARACTERS['mira']['name'],'Mira')
        self.assertNotIn('tamsin',known_people(self.state))
        self.assertNotIn('tamsin',public_state(self.state)['characterCatalog'])
        self.assertEqual(present_household_members(self.state),['founder','mira'])
        self.assertTrue(all(p['adultAgeYears']>=18 for p in self.state['people'].values()))

    def test_migration_preserves_gameplay_and_identity_is_stable(self):
        self.ready_invitation()
        old = deepcopy(self.state)
        old['schemaVersion']=19
        old.pop('people'); old.pop('arrivalReservations')
        upgraded=migrate_state(deepcopy(old))
        for key,value in old.items():
            if key!='schemaVersion':self.assertEqual(upgraded[key],value,key)
        self.assertEqual(upgraded['arrivalReservations']['arrival:tamsin']['roomId'],'west-chamber')
        self.assertEqual(migrate_state(deepcopy(upgraded)),upgraded)
        self.assertEqual(json.loads(json.dumps(upgraded))['people'],upgraded['people'])

    def test_sqlite_upgrade_backs_up_and_preserves_pending_arrival(self):
        self.ready_invitation()
        old=deepcopy(self.state);old['schemaVersion']=19
        old.pop('people');old.pop('arrivalReservations')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            upgraded=GameStore(directory).read()
            self.assertTrue((Path(directory)/f"campaign-before-schema-19-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3").exists())
            self.assertEqual(upgraded['people'],GameStore(directory).read()['people'])
            self.assertEqual(upgraded['arrivalReservations']['arrival:tamsin']['reservedBeds'],1)

    def test_arrival_rechecks_capacity_without_displacing_anyone(self):
        self.ready_invitation()
        self.state['bedroomAssignments']['founder']='west-chamber'
        before=deepcopy(self.state['bedroomAssignments'])
        apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['bedroomAssignments'],before)
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'arriving')
        self.assertIn('arrival:tamsin',self.state['arrivalReservations'])
        self.assertTrue(arrival_blockers(self.state,'arrival:tamsin'))
        apply_action(self.state,{'type':'choose-bedroom','characterId':'founder','roomId':'bedchamber'})
        apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'resident')
        self.assertEqual(self.state['arrivalReservations'],{})

    def test_cancel_preserves_contact_and_reinvitation_uses_same_person(self):
        self.ready_invitation()
        before=deepcopy(self.state)
        apply_action(self.state,{'type':'cancel-arrival','characterId':'tamsin'})
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'contacted')
        self.assertEqual(self.state['arrivalReservations'],{})
        for key in ('people','sharedFunds','materialInventory','dayNumber','currentDayPhase'):
            self.assertEqual(self.state[key],before[key])
        self.assertEqual(self.state['additionalResidents']['tamsin']['conversation'],before['additionalResidents']['tamsin']['conversation'])
        apply_action(self.state,{'type':'invite-candidate','roomId':'west-chamber'})
        self.assertEqual(len(self.state['arrivalReservations']),1)
        self.assertEqual(self.state['people'],before['people'])

    def test_invalid_move_is_atomic_and_repeated_reservation_holds_one_bed(self):
        self.ready_invitation()
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):
            apply_action(self.state,{'type':'move-arrival','characterId':'tamsin','roomId':'garden-chamber'})
        self.assertEqual(self.state,before)
        reserve_arrival(self.state,'tamsin','west-chamber','recruitment','tamsin')
        self.assertEqual(public_state(self.state)['housingSummary']['rooms']['west-chamber']['arrivalReservedBeds'],1)

    def test_missing_reservation_waits_and_can_be_repaired(self):
        self.ready_invitation();self.state['arrivalReservations']={}
        apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'arriving')
        apply_action(self.state,{'type':'move-arrival','characterId':'tamsin','roomId':'west-chamber'})
        apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'resident')

    def test_unusable_room_waits_and_remote_cancellation_is_rejected(self):
        self.ready_invitation();self.state['housingRooms']['west-chamber']['status']='in-progress'
        apply_action(self.state,{'type':'advance'})
        self.assertEqual(self.state['additionalResidents']['tamsin']['status'],'arriving')
        self.assertIn('restored',public_state(self.state)['arrivalReservationViews'][0]['blockers'][0])
        apply_action(self.state,{'type':'start-expedition'})
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):apply_action(self.state,{'type':'cancel-arrival','characterId':'tamsin'})
        self.assertEqual(self.state,before)
