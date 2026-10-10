"""Connected delivery, discovery, household scenes and schema-6 persistence."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
from game import (new_campaign, apply_action, public_state, RuleError,
                  learn_for_character, spare_artifact_count, neighbour_request_view)
from server import GameStore

class NeighbourTests(unittest.TestCase):
    def setUp(self): self.state = new_campaign()
    def act(self, kind, **fields): return apply_action(self.state, {'type':kind, **fields})
    def advance(self, count=1):
        for _ in range(count): self.act('advance')
    def open_lamps(self):
        self.act('start-research'); self.advance(3)
    def deliver_lamps(self):
        self.open_lamps()
        self.act('start-crafting', recipeId='warming-lantern', materials=['sun-amber','binding-thread'])
        self.advance(2)
        self.act('buy-material', materialId='binding-thread')
        self.act('accept-neighbour-request', requestId='brook-lamps')
        self.act('deliver-neighbour-request', requestId='brook-lamps')
    def survey_nursery(self, companion=False):
        self.act('start-expedition', siteId='fern-nursery', companionId='mira' if companion else None)
        self.advance(); self.act('choose-expedition-approach', approach='survey')
        self.advance(2); self.act('return-expedition'); self.advance()

    def test_accept_defer_no_commit_no_expiry_and_locked_routes(self):
        before=deepcopy(self.state)
        for kind, fields in [('accept-neighbour-request',{'requestId':'brook-lamps'}), ('start-expedition',{'siteId':'fern-nursery'})]:
            with self.assertRaises(RuleError): self.act(kind, **fields)
            self.assertEqual(self.state,before)
        self.open_lamps(); before=deepcopy(self.state)
        self.act('accept-neighbour-request', requestId='brook-lamps')
        for field in ('sharedFunds','materialInventory','craftedArtifacts','currentDayPhase','dayNumber'):
            self.assertEqual(self.state[field], before[field])
        self.advance(15)
        self.assertEqual(self.state['neighbourRequestProgress']['brook-lamps']['status'],'accepted')
        self.act('defer-neighbour-request', requestId='brook-lamps')
        self.act('accept-neighbour-request', requestId='brook-lamps')
        with self.assertRaises(RuleError): self.act('accept-neighbour-request', requestId='not-real')

    def test_delivery_protects_installations_and_reserves_atomically(self):
        self.open_lamps()
        self.state['craftedArtifacts']['warming-lantern']=1
        self.act('display-lantern', displayed=True)
        self.act('accept-neighbour-request', requestId='brook-lamps')
        before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('deliver-neighbour-request', requestId='brook-lamps')
        self.assertEqual(self.state,before)
        self.state['craftedArtifacts']['warming-lantern']=2
        self.act('set-material-reserve', materialId='binding-thread', target=1)
        before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('deliver-neighbour-request', requestId='brook-lamps')
        self.assertEqual(self.state,before)
        self.act('buy-material', materialId='binding-thread')
        funds=self.state['sharedFunds']; day=(self.state['dayNumber'],self.state['currentDayPhase'])
        self.act('deliver-neighbour-request', requestId='brook-lamps')
        self.assertEqual(self.state['sharedFunds'],funds+24)
        self.assertEqual(self.state['materialInventory']['binding-thread'],1)
        self.assertEqual(self.state['craftedArtifacts']['warming-lantern'],1)
        self.assertTrue(self.state['lanternDisplayed'])
        self.assertEqual((self.state['dayNumber'],self.state['currentDayPhase']),day)
        self.assertTrue(public_state(self.state)['siteAccess']['fern-nursery'])
        before=deepcopy(self.state)
        for kind in ('deliver-neighbour-request','defer-neighbour-request','accept-neighbour-request'):
            with self.assertRaises(RuleError): self.act(kind, requestId='brook-lamps')
            self.assertEqual(self.state,before)

    def test_packed_and_multiple_installed_copies_are_counted(self):
        for artifact, field in [('warming-lantern','lanternDisplayed'),('watering-charm','wateringCharmInstalled'),('index-charm','libraryIndexInstalled')]:
            self.state['craftedArtifacts'][artifact]=2; self.state[field]=True
            self.assertEqual(spare_artifact_count(self.state,artifact),1)
        for artifact, field in [('pantry-seal','householdArtifactPlacements'),('capillary-mat','utilityArtifactPlacements'),('lesson-tablet','utilityArtifactPlacements')]:
            self.state['craftedArtifacts'][artifact]=2; self.state[field][artifact]=True
            self.assertEqual(spare_artifact_count(self.state,artifact),1)
        self.act('start-expedition', carryLantern=True)
        self.assertEqual(spare_artifact_count(self.state,'warming-lantern'),0)
        before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('accept-neighbour-request',requestId='brook-lamps')
        self.assertEqual(before,self.state)

    def test_connected_delivery_survey_craft_install_and_exchange(self):
        self.deliver_lamps()
        self.state['miraArchiveProject']['status']='complete'
        self.survey_nursery(companion=True)
        for field in ('archivePrinciples','founderKnownPrinciples','residentKnownPrinciples'):
            self.assertIn('capillary-wicking',self.state[field])
        self.state['restorationStatus']='complete'
        self.state['materialInventory']['silver-ivy']=4
        self.act('create-work-order',recipeId='capillary-mat',crafterId='mira',materials=['silver-ivy','silver-ivy'],requestedCount=2)
        for _ in range(2):
            self.act('start-work-order',orderId='order-1'); self.advance(3)
        self.assertEqual(self.state['workOrders'][0]['completedCount'],2)
        self.act('place-utility-artifact',artifactId='capillary-mat',installed=True)
        self.act('accept-neighbour-request',requestId='nursery-exchange')
        self.act('deliver-neighbour-request',requestId='nursery-exchange')
        self.assertEqual(self.state['craftedArtifacts']['capillary-mat'],1)
        self.assertTrue(self.state['utilityArtifactPlacements']['capillary-mat'])
        self.assertEqual(self.state['materialInventory']['moon-glass'],2)
        self.act('assign-resident',assignment='garden')
        self.state['wateringCharmInstalled']=True
        self.assertEqual(public_state(self.state)['gardenForecast']['amount'],3)
        self.advance(); self.assertEqual(self.state['materialInventory']['silver-ivy'],3)
        self.act('garden-production',choice='surplus-sales')
        self.assertEqual(public_state(self.state)['gardenForecast']['amount'],6)
        self.act('assign-resident',assignment='rest'); self.state['utilityArtifactPlacements']['root-tender']=True
        self.act('garden-production',choice='silver-ivy')
        self.assertEqual(public_state(self.state)['gardenForecast']['amount'],1)

    def test_early_return_and_salvage_award_only_on_return_once(self):
        self.deliver_lamps(); self.act('start-expedition',siteId='fern-nursery'); self.advance()
        self.act('choose-expedition-approach',approach='survey'); self.advance()
        self.act('return-expedition'); self.advance()
        self.assertNotIn('capillary-wicking',self.state['archivePrinciples'])
        self.assertEqual(self.state['nurseryDiscoveries'],[])
        self.act('start-expedition',siteId='fern-nursery'); self.advance()
        self.act('choose-expedition-approach',approach='salvage')
        before=deepcopy(self.state['materialInventory']); self.advance()
        self.assertEqual(self.state['materialInventory'],before)
        self.act('return-expedition'); self.advance()
        self.assertEqual(self.state['materialInventory']['silver-ivy'],before['silver-ivy']+4)
        self.assertEqual(self.state['nurseryDiscoveries'],['salvage'])
        self.act('start-expedition',siteId='fern-nursery'); self.advance()
        with self.assertRaises(RuleError): self.act('choose-expedition-approach',approach='salvage')

    def test_all_requests_exact_outputs_and_spare_tablets(self):
        self.state['waystationDiscoveries']=['survey']
        self.state['researchProjects']['shared-lessons']['status']='complete'
        self.state['craftedArtifacts'].update({'pantry-seal':2,'lesson-tablet':3})
        self.state['materialInventory']['silver-ivy']=3
        self.state['householdArtifactPlacements']['pantry-seal']=True
        self.state['utilityArtifactPlacements']['lesson-tablet']=True
        self.act('set-material-reserve',materialId='silver-ivy',target=1)
        funds=self.state['sharedFunds']
        for request in ('dry-shelves','school-tablets'):
            self.act('accept-neighbour-request',requestId=request)
            self.assertEqual(neighbour_request_view(self.state,request)['blockers'],[])
            self.act('deliver-neighbour-request',requestId=request)
        self.assertEqual(self.state['sharedFunds'],funds+72)
        self.assertEqual(self.state['craftedArtifacts']['pantry-seal'],1)
        self.assertEqual(self.state['craftedArtifacts']['lesson-tablet'],1)
        self.assertEqual(self.state['materialInventory']['silver-ivy'],1)
        self.assertEqual(self.state['materialInventory']['moon-glass'],1)
        self.assertEqual(self.state['materialInventory']['fireglass'],2)

    def test_scenes_wait_for_presence_are_once_only_and_have_no_resource_reward(self):
        with self.assertRaises(RuleError): self.act('join-household-scene',sceneId='first-letter')
        self.deliver_lamps()
        self.act('start-expedition'); before=deepcopy(self.state)
        with self.assertRaises(RuleError): self.act('join-household-scene',sceneId='first-letter')
        self.assertEqual(self.state,before)
        self.act('return-expedition'); self.advance()
        before=deepcopy(self.state)
        self.act('join-household-scene',sceneId='first-letter')
        for field in ('resonancePoints','sharedFunds','dayNumber','currentDayPhase','characterDevelopment'):
            self.assertEqual(self.state[field],before[field])
        with self.assertRaises(RuleError): self.act('join-household-scene',sceneId='first-letter')
        self.state['nurseryDiscoveries']=['survey']; self.state['restorationStatus']='complete'
        self.act('join-household-scene',sceneId='green-fingers')
        self.assertIn('bench',self.state['conversation'][-1]['text'])
        self.state['completedHouseholdScenes'].remove('green-fingers')
        self.act('accept-invitation')
        self.act('join-household-scene',sceneId='green-fingers')
        self.assertIn('closer',self.state['conversation'][-1]['text'])

    def test_schema_six_backup_retry_and_reload(self):
        self.open_lamps()
        self.act('create-work-order',recipeId='warming-lantern',crafterId='founder',materials=['sun-amber','binding-thread'],requestedCount=2)
        self.act('start-work-order',orderId='order-1'); self.advance()
        old=deepcopy(self.state)
        for field in ('neighbourRequestProgress','nurseryDiscoveries','completedHouseholdScenes'): old.pop(field)
        old['utilityArtifactPlacements'].pop('capillary-mat'); old['schemaVersion']=6
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory); upgraded=store.read()
            for key in old:
                if key not in ('schemaVersion','revision','utilityArtifactPlacements'): self.assertEqual(upgraded[key],old[key],key)
            self.assertEqual(upgraded['utilityArtifactPlacements'],{**old['utilityArtifactPlacements'],'capillary-mat':False})
            with sqlite3.connect(Path(directory)/f"campaign-before-schema-6-to-{__import__('game').CURRENT_SCHEMA_VERSION}.sqlite3") as db:
                self.assertEqual(json.loads(db.execute('SELECT state FROM campaign').fetchone()[0]),old)
            def act(kind,**fields):
                payload={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':kind,**fields}}
                after=store.action(payload); self.assertEqual(store.action(payload),after)
                return after
            act('advance'); act('buy-material',materialId='binding-thread')
            act('accept-neighbour-request',requestId='brook-lamps')
            after=act('deliver-neighbour-request',requestId='brook-lamps')
            self.assertEqual(after['craftedArtifacts']['warming-lantern'],0)
            self.assertEqual(after['workOrders'][0]['completedCount'],1)
            self.assertEqual(after,GameStore(directory).read())
            before=store.read()
            with self.assertRaises(RuleError): act('deliver-neighbour-request',requestId='brook-lamps')
            self.assertEqual(before,store.read())

if __name__=='__main__': unittest.main()
