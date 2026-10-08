from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import game as g
import local_encounters as local
import character_pool as pool
import character_builds as builds
import personal_stories as stories
import summoning
from server import GameStore

class LocalExpansionTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,**fields):g.apply_action(self.s,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(self.s,before)
    def unlock(self):
        self.s['hollowRoad']['discoveries']=['survey']
        self.s['patrolJourneys']['watchtower-trail']['discoveries']=['survey']
        self.s['restorationStatus']='complete'
        # Existing room availability uses restoration progress.
        self.s['restorationCompletedPhases']=self.s.get('restorationRequiredPhases',3)
        g.discoveries_for(self.s,'fern-nursery').append('survey')
        g.learn_for_character(self.s,'founder','courteous-passage')
        self.s['researchStatus']='complete'
        g.discoveries_for(self.s,'ridge-cistern').append('survey')
    def introduce(self,key):self.act('start-local-visit',encounterId=key);self.advance()
    def member(self,key):
        self.s['residency'][key]['residencyStatus']='resident';self.s['additionalResidents'][key]['status']='resident'
        self.s['housingRooms']['garden-chamber']['status']='complete';self.s['bedroomAssignments'][key]='garden-chamber'
    def test_new_ancestries_and_appearance_constraints(self):
        for ancestry in ('Bovinefolk','Orc','Wolfkin','Oni'):
            sel=pool.select(self.s,'a'*32,{'ancestry':ancestry});p=pool.offline(self.s,sel,'a'*32)
            self.assertEqual(sel['arrivalMethod'],'summoning' if ancestry=='Oni' else 'recruitment')
            if ancestry=='Orc':self.assertIn('green',p['appearanceDescription'])
            if ancestry=='Bovinefolk':self.assertIn('without body fur',p['appearanceDescription'])
            if ancestry=='Oni':self.assertIn('large bust',p['appearanceDescription'])
    def test_gated_leads_do_not_invent_discoveries(self):
        for key in ('brakka','fenna','kaede'):self.reject('start-local-visit',encounterId=key)
        self.introduce('maren');self.assertIn('maren',self.s['people']);self.assertNotIn('maren',g.household_members(self.s))
        self.assertEqual(self.s['residency']['maren']['residencyStatus'],'remote');self.assertEqual(self.s['sharedFunds'],80)
        self.reject('start-local-visit',encounterId='maren')
    def test_pause_cancel_and_no_assignment_bypass(self):
        self.reject('assign-founder',assignment='local-visit')
        self.act('start-local-visit',encounterId='maren');self.act('assign-founder',assignment='rest');self.advance();self.assertNotIn('maren',self.s['people'])
        self.act('cancel-local-visit');self.reject('cancel-local-visit');self.assertEqual(self.s['localEncounters']['maren']['status'],'available')
        self.act('start-local-visit',encounterId='maren');self.act('resume-local-visit');self.advance();self.assertIn('maren',self.s['people'])
    def test_all_authored_people_portraits_and_oni_requires_ritual(self):
        self.unlock()
        for key in local.PEOPLE:
            self.introduce(key)
            if key in ('elowen','nyssara','sylva'):self.assertEqual(g.ORIGINAL_ASSETS[key],'/assets/portraits/'+key+'.webp')
            else:self.assertTrue((Path('static')/g.ORIGINAL_ASSETS[key].lstrip('/')).is_file())
        self.assertNotIn('kaede',self.s['people']);self.assertIn('kaede',summoning.candidate_catalogue(self.s))
        self.reject('open-correspondence',characterId='kaede')
        for m in self.s['materialInventory']:self.s['materialInventory'][m]=10
        self.act('summoning-prepare',candidateId='kaede',conductorId='founder',materials=['porous-clay','binding-thread']);self.advance(2)
        self.assertIn('kaede',self.s['people']);self.assertEqual(self.s['people']['kaede']['ancestryLabel'],'Oni')
        g.public_state(self.s)
    def test_ancestry_training_is_earned_and_off_ancestry_rejected(self):
        self.introduce('maren');self.member('maren');self.reject('train-character-build',characterId='maren',buildKind='perk',targetId='powerful-frame')
        self.reject('train-character-build',characterId='founder',buildKind='perk',targetId='powerful-frame')
        b=self.s['characterBuilds']['maren'];b['attributes']['dexterity']=6;b['affinities']['hearth']=1;self.s['characterSkills']['maren']['artifice']=1
        g.award_advancement(self.s,'maren','fixture',30,'Fixture training budget')
        before=g.work_contribution(self.s,'maren','careful-assembly')
        self.act('train-character-build',characterId='maren',buildKind='perk',targetId='powerful-frame');self.advance(2)
        self.assertEqual(g.work_contribution(self.s,'maren','careful-assembly'),before+1)
        self.assertEqual(builds.invested(self.s,'maren'),5)
    def test_story_chapters_require_real_shared_history_and_reward_once(self):
        who='mira';self.s['sharedFunds']=200
        for m in self.s['materialInventory']:self.s['materialInventory'][m]=20
        self.assertNotIn('shared-revision',stories.available_packages(self.s,who))
        def create(package,n):
            proposal=stories.outline(self.s,who,package)
            key=stories.approve(self.s,{'id':str(n),'ownerId':who,'proposal':proposal,'model':'offline'})
            self.act('start-personal-story',storyId=key);self.advance(stories.PACKAGES[package]['requiredWorkPhases'])
            return key
        first=create('personal-folio',1)
        self.assertNotIn('shared-revision',stories.available_packages(self.s,who))
        self.act('join-story-scene',storyId=first)
        next_outline=stories.outline(self.s,who,'shared-revision');self.assertIn(self.s['personalStories'][first]['proposal']['title'],next_outline['proposedWork'])
        second=create('shared-revision',2);self.assertIn(first,self.s['personalStories'][second]['continuitySources'])
        self.assertNotIn('collected-method',stories.available_packages(self.s,who));self.act('join-story-scene',storyId=second)
        third=create('collected-method',3);self.assertNotIn('collected-method',stories.available_packages(self.s,who))
        self.assertEqual(self.s['characterDevelopment'][who]['advancementAwards']['personal-story:collected-method']['points'],2)
        self.reject('start-personal-story',storyId=third)
    def test_endurance_only_changes_personal_work_contribution_and_caps(self):
        self.unlock();self.introduce('brakka');self.member('brakka');self.s['sharedFunds']=100
        for m in self.s['materialInventory']:self.s['materialInventory'][m]=10
        self.s['characterBuilds']['brakka']['perks']=['enduring-focus']
        key=stories.approve(self.s,{'id':'orc-story','ownerId':'brakka','proposal':stories.outline(self.s,'brakka','preservation-notebook'),'model':'offline'}) if 'preservation-notebook' in stories.available_packages(self.s,'brakka') else None
        if key is None:
            g.learn_for_character(self.s,'founder','gentle-preservation');key=stories.approve(self.s,{'id':'orc-story','ownerId':'brakka','proposal':stories.outline(self.s,'brakka','preservation-notebook'),'model':'offline'})
        self.act('start-personal-story',storyId=key);self.advance();self.assertEqual(self.s['personalStories'][key]['completedWorkPhases'],2)
        self.assertEqual(stories.view(self.s)['stories'][key]['workPerPhase'],1);self.advance();self.assertEqual(self.s['personalStories'][key]['completedWorkPhases'],3)
    def test_schema30_upgrade_preserves_campaign(self):
        self.s['schemaVersion']=30
        for key in ('localEncounters','localEncounterCandidates','localVisit'):self.s.pop(key)
        before=deepcopy(self.s)
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
            upgraded=GameStore(d).read();self.assertEqual(upgraded['sharedFunds'],before['sharedFunds']);self.assertEqual(upgraded['people'],before['people']);self.assertEqual(upgraded['localEncounterCandidates'],{})
            self.assertTrue(Path(d,'campaign-before-schema-30-to-66.sqlite3').exists())
