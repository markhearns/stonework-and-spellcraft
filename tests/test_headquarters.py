from copy import deepcopy
import json
import tempfile
import unittest
import game as g
import headquarters as h
from server import GameStore

class HeadquartersTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign('fresh')
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(self.s,before)
    def rich(self):self.s['sharedFunds']=2000
    def open(self,*keys):
        for key in keys:self.s['headquarters']['rooms'][key]='complete'
    def job(self,key):self.act('hq-job',jobId=key);self.advance(h.JOBS[key]['phases'])
    def test_fresh_amenity_and_knowledge_gates(self):
        self.act('hq-build',roomId='chapel');self.assertEqual(self.s['sharedFunds'],22)
        self.assertFalse(h.ready(self.s,'chapel'));self.advance(2);self.assertTrue(h.ready(self.s,'chapel'))
        self.assertFalse(self.s['founderKnownPrinciples'])
        self.rich();self.reject('hq-build',roomId='enchanting-room');self.reject('hq-build',roomId='sauna')
        self.reject('hq-build',roomId='library')
    def test_pause_resume_cancel_and_exact_refund(self):
        self.act('hq-build',roomId='warehouse');self.advance();self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(self.s['headquarters']['project']['done'],1)
        self.assertTrue(any(x['id']=='resume:headquarters' for x in g.public_state(self.s)['phaseTasks']['tasks']))
        self.act('hq-resume');self.act('hq-cancel');self.assertEqual(self.s['sharedFunds'],40)
        self.reject('hq-cancel');self.reject('assign-founder',assignment='headquarters')
    def test_single_project_away_and_invalid_actions_are_atomic(self):
        self.act('hq-build',roomId='warehouse');self.reject('hq-build',roomId='chapel');self.reject('hq-job',jobId='bad')
        self.act('start-expedition',siteId='old-waterworks',carryLantern=False)
        self.reject('hq-resume');self.reject('hq-cancel');self.reject('hq-scene',roomId='common-room',choice='drink')
        self.advance();self.assertEqual(self.s['headquarters']['project']['done'],0)
    def test_upgrade_preserves_existing_saves_art_and_assignments(self):
        old=deepcopy(self.s);old.pop('headquarters');old['schemaVersion']=39
        for key in h.BEDROOMS:
            for field in ('housingRooms','roomFurnishings','roomDecorations','savedRoomArrangements'):old[field].pop(key)
        old['assetOverrides']={'mira':'/user-assets/accepted.png','library':'/user-assets/room.png'}
        before=deepcopy(old);g.migrate_state(old)
        for field in ('assetOverrides','bedroomAssignments','sharedFunds','founderAssignment','founderKnownPrinciples'):self.assertEqual(old[field],before[field])
        self.assertFalse(old['headquarters']['rooms']);self.assertEqual(old,g.migrate_state(json.loads(json.dumps(old))))
        import sqlite3
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(before),))
            upgraded=GameStore(directory).read()
            self.assertEqual(upgraded['schemaVersion'],66)
            self.assertEqual(upgraded['assetOverrides'],before['assetOverrides'])
            self.assertTrue(Path(directory,'campaign-before-schema-39-to-66.sqlite3').exists())
            self.assertEqual(upgraded,GameStore(directory).read())
    def test_workshop_bonus_does_not_gate_old_crafting(self):
        before=g.work_contribution(self.s,'founder','careful-assembly');self.open('workshop')
        self.assertEqual(g.work_contribution(self.s,'founder','careful-assembly'),before+1)
        self.assertEqual(g.work_contribution_parts(self.s,'founder','careful-assembly')[-1]['name'],'Fitted headquarters workshop')
    def test_forging_cancel_upgrade_and_once_only_drills(self):
        self.rich();self.open('smithy','training-yard','enchanting-room')
        self.job('metalware');funds=self.s['sharedFunds'];self.act('hq-sell-metalware');self.assertEqual(self.s['sharedFunds'],funds+12);self.reject('hq-sell-metalware')
        self.reject('hq-job',jobId='equipped-drill');self.job('blade');self.job('armour')
        self.job('basic-drill');self.reject('hq-job',jobId='basic-drill');self.job('equipped-drill')
        awards=self.s['characterDevelopment']['founder']['advancementAwards'];self.assertEqual(awards['headquarters:equipped-drill']['points'],2)
        funds=self.s['sharedFunds'];self.act('hq-job',jobId='enchant-armour');self.assertEqual(self.s['headquarters']['stock']['armour'],0)
        self.advance();self.act('hq-cancel');self.assertEqual(self.s['headquarters']['stock']['armour'],1);self.assertEqual(self.s['sharedFunds'],funds)
        self.job('enchant-armour');self.act('hq-equip-armour',equipped=True);self.assertTrue(self.s['headquarters']['armourEquipped'])
        self.reject('hq-equip-armour',equipped='true')
    def test_briefing_only_consumed_by_core_survey(self):
        self.open('command-room');self.job('briefing');self.reject('hq-job',jobId='briefing')
        self.act('start-expedition',siteId='old-waterworks',carryLantern=False);self.advance()
        self.act('choose-expedition-approach',approach='survey');self.assertEqual(self.s['expedition']['remainingWorkPhases'],1);self.assertFalse(self.s['headquarters']['briefing'])
    def test_vault_reserves_installed_goods_and_conservation(self):
        self.open('vault');self.s['materialInventory']['fireglass']=4;self.s['materialReserveTargets']['fireglass']=2
        self.reject('hq-deposit',itemId='fireglass',quantity=3);self.act('hq-deposit',itemId='fireglass',quantity=2)
        self.assertEqual(self.s['materialInventory']['fireglass'],2)
        self.reject('hq-withdraw',itemId='fireglass',quantity=3);self.act('hq-withdraw',itemId='fireglass',quantity=2)
        self.assertEqual(self.s['materialInventory']['fireglass'],4);self.reject('hq-deposit',itemId='fireglass',quantity=True)
        self.s['craftedArtifacts']['warming-lantern']=1;self.s['lanternDisplayed']=True
        self.reject('hq-deposit',itemId='warming-lantern',quantity=1)
        self.s['lanternDisplayed']=False;self.act('hq-deposit',itemId='warming-lantern',quantity=1);self.assertEqual(g.spare_artifact_count(self.s,'warming-lantern'),0)
        self.act('hq-withdraw',itemId='warming-lantern',quantity=1);self.assertEqual(g.spare_artifact_count(self.s,'warming-lantern'),1)
    def test_vault_late_game_discovery_gate(self):
        self.rich();self.open('warehouse','enchanting-room');self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        for p in ('field-calibration','reference-binding'):g.learn_for_character(self.s,'founder',p)
        self.reject('hq-build',roomId='vault')
        g.discoveries_for(self.s,'old-waterworks').append('survey');g.discoveries_for(self.s,'fern-nursery').append('survey')
        self.act('hq-build',roomId='vault');self.advance(6);self.assertTrue(h.ready(self.s,'vault'))
    def test_housing_gated_and_beds_separately_fitted(self):
        self.rich();self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.reject('fund-housing',roomId='lower-suite');self.open('underground-quarters');self.assertEqual(g.housing_summary(self.s)['usableBeds'],2)
        self.act('fund-housing',roomId='lower-suite');self.advance(2);self.assertEqual(g.housing_summary(self.s)['usableBeds'],3)
        self.act('choose-bedroom',roomId='lower-suite',characterId='founder');self.assertEqual(self.s['bedroomAssignments']['founder'],'lower-suite')
        self.reject('fund-housing',roomId='guard-dormitory')
    def test_optional_scenes_do_not_advance_or_reward(self):
        before=(self.s['sharedFunds'],self.s['dayNumber'],self.s['currentDayPhase'])
        self.act('hq-scene',roomId='common-room',choice='games');self.assertEqual(before,(self.s['sharedFunds'],self.s['dayNumber'],self.s['currentDayPhase']))
        self.reject('hq-scene',roomId='common-room',choice='games');self.reject('hq-scene',roomId='chapel',choice='reflect')
        self.open('chapel');self.act('hq-scene',roomId='chapel',choice='reflect')
    def test_view_read_only_and_new_art_slot_independent(self):
        before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(self.s,before)
        self.act('accept-artwork',assetId='chapel',assetPath='/user-assets/chapel.png');self.assertNotIn('mira',self.s['assetOverrides'])
        self.act('rollback-artwork',assetId='chapel');self.assertEqual(self.s['assetOverrides']['chapel'],g.ORIGINAL_ASSETS['chapel'])
    def test_public_object_vault_preserves_identity_blocks_use_and_reservations(self):
        import public_workshop as w
        self.open('vault')
        self.s['publicWorkshop']['items']['treasure']={'id':'treasure','name':'Rare keepsake','ownerId':'founder','kind':'artifact','roomId':None,'active':False,'inscriptions':[]}
        self.s['assetOverrides']['public-object:treasure']='/user-assets/keepsake.png'
        self.act('hq-store-object',itemId='treasure')
        self.reject('public-install',ownerId='founder',itemId='treasure',roomId='library',fitReviewed=True)
        self.act('hq-retrieve-object',itemId='treasure');self.assertEqual(w.item(self.s,'treasure')['ownerId'],'founder')
        self.assertEqual(self.s['assetOverrides']['public-object:treasure'],'/user-assets/keepsake.png')
        self.s['publicWorkshop']['items']['treasure']['roomId']='library';self.reject('hq-store-object',itemId='treasure')
        self.s['publicWorkshop']['items']['treasure'].update(roomId=None,ownerId='mira');self.reject('hq-store-object',itemId='treasure')
    def test_enchanting_room_accelerates_owned_tool_inscription(self):
        self.open('enchanting-room')
        self.s['personalEquipment']['tool-test']={'kind':'makers-gauge','ownerId':'founder','name':'Test gauge','inscription':None}
        self.s['toolUpgradeProjects']['founder']={'itemId':'tool-test','materials':[],'costCrowns':12,'completedWorkPhases':0,'requiredWorkPhases':2}
        self.s['founderAssignment']='inscribing';self.advance()
        self.assertIsNotNone(self.s['personalEquipment']['tool-test']['inscription'])
    def test_warded_armour_changes_only_public_lead_work(self):
        import public_workshop as w
        site=next(iter(w.records('site-template')))
        lead=next(r for r in w.records('lead-template').values() if r['siteId']==site)
        self.s['headquarters']['stock']['warded-armour']=1;self.act('hq-equip-armour',equipped=True)
        self.act('public-start-field-trip',ownerId='founder',recordId=site,participants=['founder'],scopeReviewed=True,evidence='A reviewed accessible local route.')
        self.advance();self.act('public-field-lead',ownerId='founder',recordId=lead['id'],scopeReviewed=True,evidence='Observed the actual lead on location.')
        self.assertEqual(self.s['publicWorkshop']['fieldTrip']['remainingWorkPhases'],1)
        self.advance();self.assertEqual(self.s['publicWorkshop']['fieldTrip']['stage'],'ready-to-return')
    def test_saved_project_and_inventory_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory,start_type='fresh');state=store.read()
            payload={'action':{'type':'hq-build','roomId':'warehouse'},'expectedRevision':state['revision'],'requestId':'hq-test-build'}
            result=store.action(payload)
            self.assertEqual(GameStore(directory).read()['headquarters'],result['headquarters'])
            self.assertEqual(result,store.action(payload))

if __name__=='__main__':unittest.main()
