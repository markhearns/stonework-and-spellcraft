from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid
import game as g
import summoning
from server import GameStore


class SummoningTests(unittest.TestCase):
    def setUp(self):
        self.state=g.new_campaign()
        self.state['sharedFunds']=200
        self.state['materialInventory']['porous-clay']=10
        self.state['materialInventory']['binding-thread']=10

    def act(self,kind,**fields):return g.apply_action(self.state,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def prepare(self):
        g.learn_for_character(self.state,'founder','courteous-passage')
        self.act('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread'])
        return next(reversed(self.state['summoningContacts']))
    def contact(self):
        self.cid=self.prepare();self.advance(2)
        for topic in summoning.TOPICS:self.act('summoning-talk',contactId=self.cid,topic=topic)
        return self.cid
    def visit(self):
        self.contact();self.state['housingRooms']['garden-chamber']['status']='complete'
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber');self.advance()
    def recruit(self):
        self.visit();self.act('summoning-ask-stay',contactId=self.cid)
        self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')

    def test_research_unlock_has_ritual_gate_and_ordinary_mastery(self):
        self.state['researchStatus']='complete'
        for p in ('clear-instruction','gentle-refraction'):g.learn_for_character(self.state,'founder',p)
        self.reject('focus-research',researchId='courteous-passage',leaderId='founder')
        self.state['spellRitual']['status']='complete'
        funds=self.state['sharedFunds'];self.act('focus-research',researchId='courteous-passage',leaderId='founder')
        self.assertEqual(self.state['sharedFunds'],funds-12);self.advance(3)
        self.assertIn('courteous-passage',g.character_principles(self.state,'founder'))
        self.assertNotIn('courteous-passage',g.character_principles(self.state,'mira'))

    def test_costs_atomic_and_reserves_protected(self):
        self.reject('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread'])
        g.learn_for_character(self.state,'founder','courteous-passage')
        self.reject('summoning-prepare',conductorId='founder',materials=['binding-thread','porous-clay'])
        self.state['materialReserveTargets']['binding-thread']=10
        self.reject('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread'])
        self.state['materialReserveTargets']['binding-thread']=0
        self.state['sharedFunds']=11
        self.reject('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread'])

    def test_pause_and_exact_refund_once(self):
        before=deepcopy(self.state);cid=self.prepare();self.advance()
        self.act('assign-founder',assignment='rest');self.advance()
        self.assertEqual(self.state['summoningContacts'][cid]['completedWorkPhases'],1)
        self.act('summoning-cancel',contactId=cid)
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.reject('summoning-cancel',contactId=cid)
        self.assertNotIn('iona',self.state['people'])
        self.prepare();self.assertEqual(len(self.state['summoningContacts']),2)

    def test_stable_identity_and_closed_contact_cannot_reroll(self):
        self.contact();before=deepcopy(self.state['people']['iona']);funds=self.state['sharedFunds']
        self.act('summoning-close',contactId=self.cid);self.act('summoning-reopen',contactId=self.cid)
        self.assertEqual(self.state['people']['iona'],before);self.assertEqual(self.state['sharedFunds'],funds)
        self.reject('summoning-cancel',contactId=self.cid)
        self.reject('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread'])
        lines=deepcopy(self.state['summoningContacts'][self.cid]['conversation'])
        self.act('summoning-talk',contactId=self.cid,topic='home')
        self.assertEqual(self.state['summoningContacts'][self.cid]['conversation'],lines)

    def test_contact_without_beds_does_not_imply_visit(self):
        self.contact();self.reject('summoning-invite',contactId=self.cid,roomId='bedchamber')
        self.assertEqual(self.state['residency']['iona']['residencyStatus'],'remote')
        self.assertNotIn('iona',g.household_members(self.state));self.assertFalse(g.character_at_castle(self.state,'iona'))

    def test_visitor_is_present_without_workforce_or_allowance(self):
        self.visit();public=g.public_state(self.state)
        self.assertNotIn('iona',public['characterCatalog']);self.assertIn('iona',public['presentPeople'])
        self.assertEqual(public['housingSummary']['occupiedBeds'],3)
        self.assertEqual(self.state['personalFunds']['iona'],0)
        self.reject('assign-character',characterId='iona',assignment='archive')
        self.reject('train-skill',characterId='iona',skillId='artifice')
        self.reject('start-crafting',crafterId='iona',recipeId='pantry-seal',materials=['porous-clay','binding-thread'])
        self.assertEqual(self.state['characterDevelopment']['iona']['advancementAwards'],{})

    def test_both_membership_decisions_required_and_decline_stays_visit(self):
        self.visit();self.act('summoning-household-decision',contactId=self.cid,decision='do-not-invite')
        self.act('summoning-ask-stay',contactId=self.cid)
        self.assertNotIn('iona',g.household_members(self.state))
        self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')
        self.assertIn('iona',g.household_members(self.state))
        self.assertEqual(g.character_sheet(self.state,'iona')['availableAdvancement'],0)
        self.assertEqual(g.character_assignment(self.state,'iona'),'rest')
        self.assertFalse(g.augmentation_view(self.state,'iona')['offered'])
        self.assertEqual(g.spell_preparation_capacity(self.state,'iona'),2)

    def test_household_first_does_not_speak_for_candidate(self):
        self.visit();self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')
        self.assertEqual(self.state['residency']['iona']['residencyStatus'],'visiting')
        self.act('summoning-ask-stay',contactId=self.cid)
        self.assertEqual(self.state['residency']['iona']['residencyStatus'],'resident')

    def test_arrival_revalidation_and_cancellation_preserve_identity(self):
        self.contact();self.state['housingRooms']['garden-chamber']['status']='complete'
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber')
        self.state['housingRooms']['garden-chamber']['reservedBeds']=2
        self.advance();self.assertEqual(self.state['residency']['iona']['residencyStatus'],'arrival-agreed')
        self.assertNotIn('iona',self.state['bedroomAssignments'])
        before=deepcopy(self.state['people']['iona'])
        self.act('summoning-cancel-arrival',contactId=self.cid)
        self.assertEqual(self.state['people']['iona'],before);self.assertEqual(self.state['arrivalReservations'],{})

    def test_return_preserves_learning_funds_and_single_identity(self):
        self.recruit();self.state['personalFunds']['iona']=7
        g.award_advancement(self.state,'iona','test',2,'Test earned advancement')
        self.act('summoning-depart',contactId=self.cid)
        self.assertIn('iona',self.state['bedroomAssignments']);self.advance()
        self.assertNotIn('iona',self.state['bedroomAssignments']);self.assertNotIn('iona',g.household_members(self.state))
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber');self.advance()
        self.assertEqual(self.state['residency']['iona']['candidateStayDecision'],'undecided')
        self.act('summoning-ask-stay',contactId=self.cid);self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')
        self.assertEqual(self.state['personalFunds']['iona'],7)
        self.assertEqual(g.character_sheet(self.state,'iona')['availableAdvancement'],2)
        self.assertEqual(len(self.state['residency']['iona']['arrivals']),2)

    def test_learning_crafting_and_departure_commitments(self):
        self.recruit();g.award_advancement(self.state,'iona','test',2,'Earned test points')
        self.act('train-skill',characterId='iona',skillId='artifice')
        self.reject('summoning-depart',contactId=self.cid);self.advance(2)
        self.assertEqual(g.character_sheet(self.state,'iona')['skills']['artifice'],1)
        self.act('start-crafting',crafterId='iona',recipeId='pantry-seal',materials=['porous-clay','binding-thread'])
        self.reject('summoning-depart',contactId=self.cid);self.advance(3)
        self.assertEqual(self.state['craftedArtifacts']['pantry-seal'],1)
        self.act('summoning-depart',contactId=self.cid)

    def test_no_remote_conversation_and_preagreed_arrival_survives_absence(self):
        self.contact();self.state['housingRooms']['garden-chamber']['status']='complete'
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber')
        self.act('start-expedition');self.reject('summoning-talk',contactId=self.cid,topic='home');self.advance()
        self.assertEqual(self.state['residency']['iona']['residencyStatus'],'visiting')

    def test_schema20_migration_and_sqlite_idempotent_preparation(self):
        old=deepcopy(self.state);old['schemaVersion']=20
        for key in ('summoningContacts','residency','nextSummoningContactNumber'):old.pop(key)
        old['researchProjects'].pop('courteous-passage')
        g.learn_for_character(old,'founder','courteous-passage')
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(Path(directory)/'campaign.sqlite3') as db:
                db.execute('CREATE TABLE campaign(id INTEGER PRIMARY KEY,state TEXT NOT NULL)')
                db.execute('INSERT INTO campaign VALUES(1,?)',(json.dumps(old),))
            store=GameStore(directory);state=store.read()
            self.assertTrue((Path(directory)/f'campaign-before-schema-20-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
            for key in ('people','sharedFunds','dayNumber','currentDayPhase','bedroomAssignments'):self.assertEqual(state[key],old[key])
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':state['revision'],'action':{'type':'summoning-prepare','conductorId':'founder','materials':['porous-clay','binding-thread']}}
            once=store.action(payload);self.assertEqual(store.action(payload),once)
            self.assertEqual(len(GameStore(directory).read()['summoningContacts']),1)

    def test_authored_story_targets_and_initialization_cannot_be_duplicated(self):
        self.recruit();before=deepcopy(self.state)
        g.initialize_character_records(self.state,'iona',[],'A replacement tool')
        self.assertEqual(self.state,before)
        self.reject('start-resident-project',characterId='iona')
        self.reject('join-resident-scene',characterId='iona',sceneId='tea-and-margins')
        self.assertEqual(self.state['additionalResidents']['iona']['personalProject']['status'],'not-started')

    def test_personal_spell_proposal_accepts_registered_member_only(self):
        from dialogue import DialogueService,ProviderSettings
        self.recruit()
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.state),))
            settings=ProviderSettings(directory);settings.save({'enabled':True,'model':'example/model','apiKey':'test-key','maxOutputTokens':500})
            service=DialogueService(settings,lambda config,messages:{'text':json.dumps({'formId':'warm-twist','name':'A useful cord','explanation':'Bind plant fibres.','limitations':[]}), 'usage':{}})
            payload={'requestId':uuid.uuid4().hex,'expectedRevision':self.state['revision'],'purpose':'spell-proposal','ownerId':'iona','text':'A useful cord'}
            with self.assertRaisesRegex(g.RuleError,'Choose a spell in the Spellbook'):service.generate(store,payload)
            self.assertEqual(store.read(),self.state)
