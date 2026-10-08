from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import game as g
import estate_expansion as e
from server import GameStore

class EstateExpansionTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign();self.s['sharedFunds']=2000
        self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        for key in ('water-guidance','steady-hearth-wards'):g.learn_for_character(self.s,'founder',key)
    def act(self,kind,**fields):return g.apply_action(self.s,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(self.s,before)
    def room(self,key):
        self.act('fund-housing',roomId=key);self.advance(g.HOUSING_ROOMS[key]['requiredWorkPhases'])
    def test_exact_bounded_capacities_and_no_free_rooms(self):
        self.assertEqual(sum(r['capacityBeds'] for k,r in g.HOUSING_ROOMS.items() if e.region_for(k)=='main'),35)
        self.assertEqual(sum(r['capacityBeds'] for k,r in g.HOUSING_ROOMS.items() if e.region_for(k)=='annex'),25)
        self.assertEqual(g.housing_summary(self.s)['usableBeds'],2)
        for key in e.ROOMS:
            self.assertFalse(g.room_available(self.s,key))
            self.reject('select-room',roomId=key)
            self.reject('reserve-beds',roomId=key,reservedBeds=1)
    def test_main_suite_opens_with_independent_furnishing_and_arrangement(self):
        self.room('gallery-suite-1')
        self.act('choose-bedroom',roomId='gallery-suite-1',characterId='mira')
        self.act('select-room',roomId='gallery-suite-1')
        self.act('decorate',roomId='gallery-suite-1',furnishing='velvet-bench')
        self.act('save-room-arrangement',roomId='gallery-suite-1',name='Mira’s quiet room')
        self.assertEqual(self.s['bedroomAssignments']['mira'],'gallery-suite-1')
        self.assertEqual(self.s['roomFurnishings']['gallery-suite-2'],'oak-bench')
        self.assertTrue(g.public_state(self.s)['rooms']['gallery-suite-1']['illustrationIsRepresentative'])
    def test_annex_needs_services_then_individual_room_funding(self):
        self.reject('fund-housing',roomId='annex-suite-1')
        g.character_principles(self.s,'founder').remove('water-guidance');self.reject('fund-annex')
        g.learn_for_character(self.s,'founder','water-guidance')
        self.act('fund-annex');self.advance(4)
        self.assertEqual(g.housing_summary(self.s)['usableBeds'],2)
        self.reject('fund-housing',roomId='annex-suite-1');self.advance()
        self.assertEqual(self.s['estateAnnex']['status'],'complete')
        self.assertEqual(g.housing_summary(self.s)['usableBeds'],2)
        self.room('annex-suite-1');self.assertEqual(g.housing_summary(self.s)['usableBeds'],3)
        self.reject('fund-annex');self.reject('cancel-annex')
    def test_annex_pause_and_exact_cancel_do_not_change_castle_rooms(self):
        self.room('gallery-suite-1');rooms=deepcopy(self.s['housingRooms']);funds=self.s['sharedFunds']
        self.act('fund-annex');self.advance();self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(self.s['estateAnnex']['completedWorkPhases'],1)
        self.act('cancel-annex');self.assertEqual(self.s['sharedFunds'],funds);self.assertEqual(self.s['housingRooms'],rooms)
        self.reject('cancel-annex');self.reject('assign-founder',assignment='estate')
    def test_private_preference_is_generic_for_all_people(self):
        self.s['people']['mira']['accommodationPreference']='private-room'
        self.room('upper-chamber-1');self.reject('choose-bedroom',roomId='upper-chamber-1',characterId='mira')
        self.room('gallery-suite-1');self.act('choose-bedroom',roomId='gallery-suite-1',characterId='mira')
        self.assertEqual(self.s['bedroomAssignments']['mira'],'gallery-suite-1')
    def test_region_limit_reserves_founder_place_even_if_founder_moves(self):
        self.s['bedroomAssignments']={'founder':'annex-suite-1',**{'person-'+str(i):'upper-chamber-1' for i in range(25)}}
        self.assertTrue(e.placement_blockers(self.s,'new-person','gallery-suite-1'))
        self.assertFalse(e.placement_blockers(self.s,'person-1','gallery-suite-1'))
        self.assertFalse(e.placement_blockers(self.s,'founder','gallery-suite-1'))
        self.assertFalse(e.placement_blockers(self.s,'new-person','annex-suite-2'))
        self.s['bedroomAssignments'].pop('person-24')
        self.s['arrivalReservations']['arrival:waiting']={'personId':'waiting','roomId':'upper-chamber-2','reservedBeds':1}
        self.assertTrue(e.placement_blockers(self.s,'new-person','gallery-suite-1'))
    def test_named_arrival_region_check_cannot_be_bypassed(self):
        self.s['housingRooms']['gallery-suite-1']['status']='complete'
        self.s['additionalResidents']['tamsin']['status']='contacted'
        self.s['bedroomAssignments']={'founder':'annex-suite-1',**{'person-'+str(i):'upper-chamber-1' for i in range(25)}}
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):g.reserve_arrival(self.s,'tamsin','gallery-suite-1','recruitment','tamsin')
        self.assertEqual(self.s,before)
    def test_schema28_upgrade_keeps_funded_original_rooms_and_choices(self):
        self.s['housingRooms']['west-chamber'].update(status='in-progress',completedWorkPhases=1)
        old=deepcopy(self.s);old.pop('estateAnnex');old['schemaVersion']=28
        for key in e.ROOMS:
            for field in ('housingRooms','roomFurnishings','roomDecorations','savedRoomArrangements'):old[field].pop(key)
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)');db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);upgraded=store.read()
            self.assertTrue((Path(directory)/'campaign-before-schema-28-to-66.sqlite3').exists())
            self.assertEqual(upgraded['housingRooms']['west-chamber'],old['housingRooms']['west-chamber'])
            self.assertEqual(upgraded['bedroomAssignments'],old['bedroomAssignments'])
            self.assertEqual(upgraded['sharedFunds'],old['sharedFunds'])
            self.assertEqual(upgraded,GameStore(directory).read())

    def test_full_fifty_resident_arrival_membership_and_extra_bed_rejection(self):
        import summoning
        from candidate_proposals import approved_definition
        from test_candidate_proposals import candidate_fixture
        self.s['estateAnnex']['status']='complete'
        for key,record in self.s['housingRooms'].items():
            if not g.HOUSING_ROOMS[key].get('hq'):record['status']='complete'
        for index in range(50):
            who='scale-'+str(index)
            self.s['reviewedCandidates'][who]=approved_definition(candidate_fixture(name='Resident '+str(index)),who,'fixture','fixture-'+str(index))
            summoning.initialize_person(self.s,who)
            self.s['summoningContacts'][who]={'conductorId':'founder','candidateId':who,'personId':who,'categoryId':'reviewed-visitor','contactStatus':'open',
                'completedWorkPhases':2,'requiredWorkPhases':2,'committedCrowns':12,'committedMaterials':{},'discussedTopics':['intentions','home','visit'],'conversation':[]}
            if index<49:
                room=next(key for key,row in g.housing_summary(self.s)['rooms'].items() if row['availableBeds']>0)
                self.act('summoning-invite',contactId=who,roomId=room)
        self.assertEqual(g.housing_summary(self.s)['availableBeds'],0)
        self.reject('summoning-invite',contactId='scale-49',roomId='gallery-suite-1')
        self.advance()
        for index in range(49):
            who='scale-'+str(index)
            self.act('summoning-ask-stay',contactId=who)
            self.act('summoning-household-decision',contactId=who,decision='invite-to-stay')
        summary=g.housing_summary(self.s)
        self.assertEqual(summary['residentCount'],50)
        self.assertEqual(summary['occupiedBeds'],51)
        self.assertEqual(len(g.household_members(self.s)),51)
        for region in ('main','annex'):
            self.assertEqual(sum(who!='founder' and e.region_for(room)==region for who,room in self.s['bedroomAssignments'].items()),25)
        public=g.public_state(self.s)
        self.assertEqual(len(public['characterSheets']),51)
        self.assertEqual(public['containmentView']['occupiedCapacity'],0)
        self.assertNotIn('privateCastleLore',public)
        self.act('summoning-depart',contactId='scale-0');self.advance()
        self.assertEqual(g.housing_summary(self.s)['availableBeds'],1)
