from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import game as g
import castle_chapter as chapter
import room_life
import phase_tasks
from server import GameStore

class CastleChapterTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign('fresh')
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def fund(self,n):
        if self.s['sharedFunds']<n:
            self.act('assign-founder',assignment='commissions')
            while self.s['sharedFunds']<n:self.advance()
    def reject(self,kind,**kw):
        old=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(old,self.s)
    def hearth(self):self.act('start-research');self.advance(3)
    def travel(self,site,approach='survey',**kw):
        self.act('start-expedition',siteId=site,**kw);self.advance()
        self.act('choose-expedition-approach',approach=approach)
        while self.s['expedition']['stage']=='working':self.advance()
        self.act('return-expedition');self.advance()
    def research(self,key):
        self.fund(g.RESEARCH_CATALOG[key]['costCrowns'])
        self.act('focus-research',researchId=key,leaderId='founder')
        while self.s['researchProjects'][key]['status']!='complete':self.advance()
    def craft(self,key,materials):
        for material in set(materials):
            while self.s['materialInventory'][material]<materials.count(material):
                self.fund(g.MATERIALS[material]['price']);self.act('buy-material',materialId=material)
        self.act('start-crafting',recipeId=key,materials=materials)
        while self.s['craftingProject']:self.advance()
    def test_real_solo_route_uses_earned_money_returned_surveys_and_installations(self):
        self.reject('start-expedition',siteId='quarry-shelter');self.reject('start-expedition',siteId='ridge-cistern')
        self.hearth();self.craft('warming-lantern',['sun-amber','binding-thread'])
        self.travel('quarry-shelter',carryLantern=True)
        self.assertNotIn('weather-sealing',g.character_principles(self.s,'founder'))
        self.research('weather-sealing');self.craft('weather-screen',['porous-clay','binding-thread'])
        income=g.copying_income(self.s);self.act('place-utility-artifact',artifactId='weather-screen',installed=True)
        self.assertEqual(g.copying_income(self.s),income+1)
        self.travel('old-waterworks',carryLantern=True);self.travel('ridge-cistern',carryLantern=True)
        self.research('settling-flow');self.craft('cistern-filter',['porous-clay','silver-ivy'])
        self.reject('place-utility-artifact',artifactId='cistern-filter',installed=True)
        self.fund(25);self.act('start-restoration');self.advance(3)
        self.act('place-utility-artifact',artifactId='cistern-filter',installed=True)
        self.assertTrue(chapter.view(self.s)['complete']);self.assertFalse(self.s['testing']['used'])
        self.assertEqual(g.household_members(self.s),['founder']);self.assertGreaterEqual(self.s['sharedFunds'],0)
        self.assertEqual(self.s,json.loads(json.dumps(self.s)))
    def test_early_return_and_unreturned_findings_do_not_unlock_research(self):
        self.hearth();self.act('start-expedition',siteId='quarry-shelter');self.advance();self.act('choose-expedition-approach',approach='survey');self.advance(2)
        self.assertFalse(g.discoveries_for(self.s,'quarry-shelter'))
        self.assertTrue(any('bring' in x for x in g.research_blockers(self.s,'weather-sealing','founder')))
        self.act('return-expedition');self.advance();self.assertEqual(g.discoveries_for(self.s,'quarry-shelter'),['survey'])
        self.act('start-expedition',siteId='quarry-shelter');self.act('return-expedition');self.advance()
        self.assertEqual(g.discoveries_for(self.s,'quarry-shelter'),['survey'])
    def test_salvage_and_advancement_cannot_be_farmed(self):
        self.hearth();before=deepcopy(self.s['materialInventory']);money=self.s['sharedFunds'];self.travel('quarry-shelter','salvage')
        self.assertEqual(self.s['materialInventory']['binding-thread'],before['binding-thread']+3)
        self.assertEqual(self.s['materialInventory']['porous-clay'],before['porous-clay']+2)
        self.assertEqual(self.s['sharedFunds'],money+8)
        self.act('start-expedition',siteId='quarry-shelter');self.advance();self.reject('choose-expedition-approach',approach='salvage')
        self.act('return-expedition');self.advance();self.assertEqual(self.s['sharedFunds'],money+8)
    def test_reflections_are_optional_atomic_once_only_and_without_rewards(self):
        self.reject('chapter-reflection',sceneId='first-rain',choice='listen')
        self.hearth();self.travel('quarry-shelter')
        self.reject('chapter-reflection',sceneId=[],choice='care');self.reject('chapter-reflection',sceneId='shutter-notes',choice='bad')
        self.reject('chapter-reflection',sceneId='shutter-notes',choice='care',personId='mira')
        before=deepcopy(self.s);self.act('chapter-reflection',sceneId='shutter-notes',choice='care')
        after=deepcopy(self.s)
        for field in ['castleChapter','journal']:before.pop(field);after.pop(field)
        self.assertEqual(before,after)
        self.reject('chapter-reflection',sceneId='shutter-notes',choice='curiosity')
        self.s['utilityArtifactPlacements']['weather-screen']=True
        self.act('start-expedition',siteId='old-waterworks');self.reject('chapter-reflection',sceneId='first-rain',choice='listen')
    def test_shared_reflections_require_a_real_present_resident_and_keep_agreements(self):
        self.s['headquarters']['rooms']['chapel']='complete'
        self.reject('chapter-reflection',sceneId='chapel-pause',choice='silence',personId='mira')
        self.act('cheat-toggle',enabled=True);self.act('cheat-character',ancestry='Human',name='Aster')
        who=g.household_members(self.s)[1];before=deepcopy(self.s['soloLife'])
        self.act('chapter-reflection',sceneId='chapel-pause',choice='silence',personId=who)
        self.assertEqual(self.s['soloLife'],before)
        memory=self.s['castleChapter']['memories']['chapel-pause'];self.assertEqual(memory['personId'],who);self.assertIn('Aster',memory['text'])
    def test_filter_only_benefits_staffed_ivy_and_never_stacks_copies(self):
        self.s['restorationStatus']='complete';self.s['utilityArtifactPlacements']['cistern-filter']=True
        self.s['craftedArtifacts']['cistern-filter']=4
        self.assertEqual(g.garden_harvest(self.s)['amount'],0)
        self.act('assign-gardener',characterId='founder');self.assertEqual(g.garden_harvest(self.s)['amount'],2)
        self.s['gardenProductionChoice']='surplus-sales';self.assertEqual(g.garden_harvest(self.s)['amount'],4)
        self.act('assign-founder',assignment='rest');self.s['utilityArtifactPlacements']['root-tender']=True
        self.s['gardenProductionChoice']='silver-ivy';self.assertEqual(g.garden_harvest(self.s)['amount'],1)
    def test_room_presence_tracks_actual_assignment_pause_and_travel_read_only(self):
        self.hearth();self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        self.assertEqual(room_life.location(self.s,'founder'),'library')
        self.s['headquarters']['rooms']['workshop']='complete';self.assertEqual(room_life.location(self.s,'founder'),'workshop')
        old=deepcopy(self.s);v=g.public_state(self.s);self.assertEqual(old,self.s)
        self.assertEqual(v['roomLifeView']['workshop']['occupants'][0]['activity'],'Making the active artifact')
        self.act('assign-founder',assignment='rest');self.assertEqual(room_life.location(self.s,'founder'),'library')
        self.act('start-expedition',siteId='old-waterworks');self.assertIsNone(room_life.location(self.s,'founder'))
        self.assertFalse(any(r['occupants'] for r in room_life.view(self.s).values()))
    def test_research_guidance_tracks_selected_resident_lead(self):
        self.hearth();self.travel('quarry-shelter')
        self.act('cheat-toggle',enabled=True);self.act('cheat-character',ancestry='Human',name='Aster')
        who=g.household_members(self.s)[1];g.learn_for_character(self.s,who,'steady-hearth-wards')
        self.act('focus-research',researchId='weather-sealing',leaderId=who)
        self.assertEqual(self.s['researchProjects']['weather-sealing']['leadId'],who)
        row=next(p for p in room_life.work_view(self.s) if p['id']==who)
        self.assertTrue(any(p['name']=='Weather sealing' for p in row['projects']))
        founder=next(p for p in room_life.work_view(self.s) if p['id']=='founder')
        self.assertFalse(any(p['name']=='Weather sealing' for p in founder['projects']))

    def test_migration_backs_up_preserves_art_and_work_and_is_idempotent(self):
        self.hearth();self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        old=deepcopy(self.s);old['schemaVersion']=40;old.pop('castleChapter')
        for key in chapter.RESEARCH:old['researchProjects'].pop(key)
        for key in chapter.ARTIFACTS:old['utilityArtifactPlacements'].pop(key);old['craftedArtifacts'].pop(key)
        old['assetOverrides']={'founder':'/user-assets/accepted.png'}
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
            new=GameStore(directory).read();self.assertEqual(new['schemaVersion'],66)
            for field in ('craftingProject','founderAssignment','assetOverrides','materialInventory','sharedFunds'):self.assertEqual(old[field],new[field])
            self.assertTrue(Path(directory,'campaign-before-schema-40-to-66.sqlite3').exists())
            self.assertEqual(new,g.migrate_state(deepcopy(new)))
    def test_available_reflections_appear_in_phase_invitations_and_disappear_after_choice(self):
        self.hearth();self.travel('quarry-shelter')
        self.assertIn('chapter:shutter-notes',[r['id'] for r in phase_tasks.build(self.s)['tasks']])
        self.act('chapter-reflection',sceneId='shutter-notes',choice='care')
        self.assertNotIn('chapter:shutter-notes',[r['id'] for r in phase_tasks.build(self.s)['tasks']])

if __name__=='__main__':unittest.main()
