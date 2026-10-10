from copy import deepcopy
import json
import tempfile
import unittest
import uuid
import game as g
import arrivals
import character_pool as pool
import summoning
import personal_stories
from server import GameStore
from dialogue import DialogueService,ProviderSettings

class ArrivalPathTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.store=GameStore(self.temp.name)
        self.service=DialogueService(ProviderSettings(self.temp.name),lambda *_:self.fail('Offline path called provider'))
        s=self.store.read();s['sharedFunds']=500;s['testing']['enabled']=True
        for key in s['materialInventory']:s['materialInventory'][key]=20
        for p in ('clear-instruction','gentle-preservation','courteous-passage'):g.learn_for_character(s,'founder',p)
        s['housingRooms']['west-chamber']['status']='complete';s['housingRooms']['garden-chamber']['status']='complete'
        self.seed(s)
    def seed(self,s):
        with self.store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
    def plan(self,ancestry,**choices):
        draft=self.service.generate(self.store,{'requestId':uuid.uuid4().hex,'expectedRevision':self.store.read()['revision'],'purpose':'candidate-proposal','source':'offline','poolChoices':{'ancestry':ancestry,**choices},'text':'A new adult companion.'})
        self.assertEqual(draft['status'],'ready',draft.get('error'))
        s=self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True})
        return s,'summoned-'+draft['id']
    def advance(self,s,n=1):
        for _ in range(n):g.apply_action(s,{'type':'advance'})
    def reject(self,s,kind,**fields):
        before=deepcopy(s)
        with self.assertRaises(g.RuleError):g.apply_action(s,{'type':kind,**fields})
        self.assertEqual(s,before)
    def test_common_ancestries_have_real_correspondence_not_summoning(self):
        for ancestry in [a for a in pool.COMMON_ANCESTRIES if a!='Bovinefolk']:
            s,who=self.plan(ancestry);money=s['sharedFunds'];phase=s['currentDayPhase']
            self.reject(s,'summoning-prepare',candidateId=who,conductorId='founder',materials=['porous-clay','binding-thread'])
            self.reject(s,'open-correspondence',characterId=who)
            from recruitment_fixture import rescue_and_invite
            rescue_and_invite(s,who)
            self.assertGreaterEqual(s['sharedFunds'],money);self.assertEqual(s['residency'][who]['residencyStatus'],'remote')
            self.reject(s,'open-correspondence',characterId=who)
            cid='introduced-'+who
            for topic in ('intentions','home','visit'):g.apply_action(s,{'type':'summoning-talk','contactId':cid,'topic':topic})
            room=arrivals.eligible_rooms(s,s['people'][who])[0]
            g.apply_action(s,{'type':'summoning-invite','contactId':cid,'roomId':room});self.advance(s)
            self.assertEqual(s['residency'][who]['residencyStatus'],'visiting');self.assertNotIn(who,g.household_members(s))
    def test_kitsune_is_exotic_and_never_ordinary_recruitment(self):
        s,who=self.plan('Kitsune');self.reject(s,'open-correspondence',characterId=who);self.reject(s,'start-golem',characterId=who)
        g.apply_action(s,{'type':'summoning-prepare','candidateId':who,'conductorId':'founder','materials':['porous-clay','binding-thread']});self.advance(s,2)
        self.assertIn(who,s['people']);self.assertEqual(s['people'][who]['ancestryLabel'],'Kitsune')
    def test_golem_waits_for_bed_and_becomes_adult_guest_not_worker(self):
        s,who=self.plan('Golem',bodyMaterial='porcelain');self.reject(s,'summoning-prepare',candidateId=who,conductorId='founder',materials=['porous-clay','binding-thread'])
        g.apply_action(s,{'type':'start-golem','characterId':who});self.advance(s,5)
        self.assertNotIn(who,s['people']);self.advance(s,2);self.assertEqual(s['golemProjects'][who]['completedWorkPhases'],5)
        room=arrivals.eligible_rooms(s,s['reviewedCandidates'][who]['profile'])[0]
        g.apply_action(s,{'type':'choose-golem-room','characterId':who,'roomId':room});self.advance(s)
        self.assertEqual(s['residency'][who]['residencyStatus'],'visiting');self.assertNotIn(who,g.household_members(s));self.assertEqual(s['people'][who]['chronologicalAgeYears'],0);self.assertEqual(s['people'][who]['ageBasis'],'adult-form')
        self.assertEqual(s['personalFunds'][who],0);self.assertEqual(s['additionalResidents'][who]['assignment'],'rest');self.assertEqual(s['bedroomAssignments'][who],room)
        self.reject(s,'cancel-golem',characterId=who);self.reject(s,'start-golem',characterId=who)
        g.public_state(s)
    def test_golem_pause_cancel_refunds_once_and_all_materials_valid(self):
        for material,d in pool.GOLEM_MATERIALS.items():
            self.assertTrue(set(d['materials'])<=set(g.MATERIALS))
            s,who=self.plan('Golem',bodyMaterial=material);funds=s['sharedFunds'];inventory=deepcopy(s['materialInventory'])
            g.apply_action(s,{'type':'start-golem','characterId':who});self.advance(s)
            g.apply_action(s,{'type':'assign-founder','assignment':'rest'});self.advance(s);self.assertEqual(s['golemProjects'][who]['completedWorkPhases'],1)
            g.apply_action(s,{'type':'cancel-golem','characterId':who});self.assertEqual(s['sharedFunds'],funds);self.assertEqual(s['materialInventory'],inventory);self.reject(s,'cancel-golem',characterId=who)
    def test_golem_requirements_and_reserves_are_atomic(self):
        s,who=self.plan('Golem');s['materialReserveTargets']['porous-clay']=20;self.reject(s,'start-golem',characterId=who)
        s['materialReserveTargets']['porous-clay']=0;g.character_principles(s,'founder').remove('clear-instruction');self.reject(s,'start-golem',characterId=who)
        self.reject(s,'assign-founder',assignment='awakening')
    def test_elf_visual_constraints_and_routes(self):
        for ancestry,skin in [('High elf','fair'),('Dark elf','chocolate'),('Drow','grey')]:
            selection=pool.select(g.new_campaign(),'a'*32,{'ancestry':ancestry});p=pool.offline(g.new_campaign(),selection,'a'*32)
            self.assertEqual(selection['arrivalMethod'],'recruitment')
            if ancestry!='Drow':self.assertIn(skin,p['appearanceDescription'])
            else:self.assertIn('subterranean',p['origin'])
        with self.assertRaises(g.RuleError):pool.select(g.new_campaign(),'a'*32,{'ancestry':'Catfolk','arrivalMethod':'summoning'})
    def test_lost_start_response_does_not_charge_twice_and_reload_preserves_work(self):
        s,who=self.plan('Golem');request={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':{'type':'start-golem','characterId':who}}
        first=self.store.action(request);second=self.store.action(request)
        self.assertEqual(first,second);self.assertEqual(first['sharedFunds'],s['sharedFunds']-pool.GOLEM_MATERIALS['clay']['costCrowns'])
        self.assertEqual(GameStore(self.temp.name).read()['golemProjects'],first['golemProjects'])
    def test_new_member_can_finish_personal_story_and_depart_without_losing_identity(self):
        s,who=self.plan('Catfolk')
        # Explicit fixture preference: willing to consider a household, never auto-enrolled.
        c=s['reviewedCandidates'][who];c['stayDecision']='wants-to-stay';c['profile']['stayPreference']='open-to-staying'
        from recruitment_fixture import rescue_and_invite
        rescue_and_invite(s,who);cid='introduced-'+who
        for topic in ('intentions','home','visit'):g.apply_action(s,{'type':'summoning-talk','contactId':cid,'topic':topic})
        room=arrivals.eligible_rooms(s,s['people'][who])[0];g.apply_action(s,{'type':'summoning-invite','contactId':cid,'roomId':room});self.advance(s)
        g.apply_action(s,{'type':'summoning-ask-stay','contactId':cid});self.assertNotIn(who,g.household_members(s))
        g.apply_action(s,{'type':'summoning-household-decision','contactId':cid,'decision':'invite-to-stay'});self.assertIn(who,g.household_members(s))
        self.seed(s)
        draft=self.service.generate(self.store,{'requestId':uuid.uuid4().hex,'purpose':'story-proposal','source':'offline','ownerId':who,'packageId':'personal-folio','expectedRevision':s['revision'],'text':'Her own ambition.'})
        self.assertEqual(draft['status'],'ready',draft.get('error'))
        s=self.service.accept(self.store,{'draftId':draft['id'],'contentReviewed':True,'mechanicsReviewed':True});key='story-'+draft['id']
        g.apply_action(s,{'type':'start-personal-story','storyId':key});self.reject(s,'summoning-depart',contactId=cid);self.advance(s,2)
        self.assertEqual(s['personalStories'][key]['status'],'complete');self.assertEqual(s['characterDevelopment'][who]['advancementAwards']['personal-story:personal-folio']['points'],1)
        g.apply_action(s,{'type':'join-story-scene','storyId':key});g.apply_action(s,{'type':'summoning-depart','contactId':cid});self.advance(s)
        self.assertEqual(s['residency'][who]['residencyStatus'],'away');self.assertEqual(s['personalStories'][key]['sceneStatus'],'remembered')
        self.assertIn(s['personalStories'][key]['proposal']['title'],json.dumps(personal_stories.owner_stories(s,who),ensure_ascii=False))
