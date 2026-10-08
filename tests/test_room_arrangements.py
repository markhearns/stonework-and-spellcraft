from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import new_campaign, apply_action, public_state, RuleError, room_furnishing_view
from server import GameStore

class RoomArrangementTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,room='common-room',**fields):return apply_action(self.state,{'type':kind,'roomId':room,**fields})
    def test_slots_are_independent_free_and_cannot_install_work_artifacts(self):
        before=deepcopy(self.state)
        self.act('decorate-room-slot',slotId='floor',decorationId='violet-runner')
        self.act('decorate-room-slot',slotId='wall',decorationId='fern-study')
        for key in before:
            if key not in ('roomDecorations','revision'):self.assertEqual(before[key],self.state[key],key)
        for fields in ({'slotId':'floor','decorationId':'scribe-stone'},{'slotId':'wall','decorationId':'ink-rug'},{'slotId':[],'decorationId':'none'}):
            before=deepcopy(self.state)
            with self.assertRaises(RuleError):self.act('decorate-room-slot',**fields)
            self.assertEqual(before,self.state)
    def test_unrestored_rooms_and_wrong_room_choices_rejected(self):
        for room in ('conservatory','west-chamber','garden-chamber','invented'):
            with self.assertRaises(RuleError):self.act('decorate-room-slot',room,slotId='floor',decorationId='reed-mat')
        self.state['restorationStatus']='complete'
        with self.assertRaises(RuleError):self.act('decorate-room-slot','conservatory',slotId='floor',decorationId='ink-rug')
        self.act('decorate-room-slot','conservatory',slotId='floor',decorationId='reed-mat')
    def test_saved_arrangement_restores_choices_not_installations_or_resident_property(self):
        self.act('decorate',furnishing='velvet-settee')
        self.act('decorate-room-slot',slotId='floor',decorationId='ink-rug')
        self.act('save-room-arrangement',name='Quiet evening')
        self.act('decorate',furnishing='reading-table')
        self.act('decorate-room-slot',slotId='floor',decorationId='none')
        self.state['lanternDisplayed']=True
        before=deepcopy(self.state)
        self.act('load-room-arrangement',name='Quiet evening')
        self.assertEqual(self.state['roomFurnishings']['common-room'],'velvet-settee')
        self.assertEqual(self.state['roomDecorations']['common-room']['floor'],'ink-rug')
        for key in before:
            if key not in ('revision','roomDecorations','roomFurnishings'):self.assertEqual(before[key],self.state[key],key)
        self.act('delete-room-arrangement',name='Quiet evening')
        self.assertEqual(self.state['roomFurnishings']['common-room'],'velvet-settee')
    def test_saves_are_room_scoped_bounded_and_replacement_is_a_snapshot(self):
        for i in range(6):self.act('save-room-arrangement',name=str(i))
        with self.assertRaises(RuleError):self.act('save-room-arrangement',name='seventh')
        self.act('decorate-room-slot',slotId='wall',decorationId='star-chart')
        self.act('save-room-arrangement',name='0')
        self.act('decorate-room-slot',slotId='wall',decorationId='none')
        self.assertEqual(self.state['savedRoomArrangements']['common-room']['0']['decorations']['wall'],'star-chart')
        with self.assertRaises(RuleError):self.act('load-room-arrangement','library',name='0')
        self.act('save-room-arrangement','library',name='0')
    def test_summary_reports_conditional_bonuses_and_all_installed_artifacts(self):
        self.act('decorate',furnishing='velvet-settee')
        self.assertIn('Current contribution: +0',room_furnishing_view(self.state,'common-room')[0]['effect'])
        self.act('accept-invitation')
        self.assertIn('Current contribution: +1',room_furnishing_view(self.state,'common-room')[0]['effect'])
        self.state['wateringCharmInstalled']=True
        self.state['utilityArtifactPlacements']['root-tender']=True
        rows=room_furnishing_view(self.state,'conservatory')
        self.assertEqual([row['name'] for row in rows],['Self-watering charm','Root tender'])
        self.assertIn('staffed',rows[0]['effect']);self.assertIn('Without a gardener',rows[1]['effect'])
        for key in self.state['utilityArtifactPlacements']:self.state['utilityArtifactPlacements'][key]=True
        self.assertTrue(public_state(self.state)['roomFurnishingViews']['library'])
    def test_schema16_migration_preserves_choices_and_artifacts_then_persists_arrangement(self):
        old=deepcopy(self.state);old['schemaVersion']=16
        old.pop('roomDecorations');old.pop('savedRoomArrangements')
        old['roomFurnishings']['common-room']='velvet-settee';old['lanternDisplayed']=True
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            self.assertTrue((Path(directory)/'campaign-before-schema-16-to-66.sqlite3').exists())
            self.assertEqual(state['roomFurnishings'],old['roomFurnishings']);self.assertTrue(state['lanternDisplayed'])
            self.assertEqual(state['dayNumber'],old['dayNumber']);self.assertEqual(state['sharedFunds'],old['sharedFunds'])
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'save-room-arrangement','roomId':'common-room','name':'Saved on upgrade'}}
            after=store.action(payload);self.assertEqual(store.action(payload),after)
            self.assertEqual(GameStore(directory).read(),after)
