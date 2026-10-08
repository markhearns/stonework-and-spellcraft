from copy import deepcopy
import json
import unittest
import game as g
import summoning
import resident_projects


class IonaLifeTests(unittest.TestCase):
    def setUp(self):
        self.state=g.new_campaign()
        self.state['sharedFunds']=500
        for key in self.state['materialInventory']:self.state['materialInventory'][key]=20
        g.learn_for_character(self.state,'founder','courteous-passage')
        self.state['housingRooms']['garden-chamber']['status']='complete'

    def act(self,kind,**fields):return g.apply_action(self.state,{'type':kind,**fields})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def recruit(self):
        self.act('summoning-prepare',conductorId='founder',materials=['porous-clay','binding-thread']);self.advance(2)
        self.cid=next(iter(self.state['summoningContacts']))
        for topic in summoning.TOPICS:self.act('summoning-talk',contactId=self.cid,topic=topic)
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber');self.advance()
        self.act('summoning-ask-stay',contactId=self.cid)
        self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')
    def finish_atlas(self):
        self.act('start-iona-atlas');self.advance(3)
    def request(self,kind,**fields):return self.act(kind,requestId='iona-map-case',**fields)

    def test_unknown_visitor_and_protected_stock_do_not_start_project(self):
        self.reject('start-iona-atlas');self.assertIsNone(g.public_state(self.state)['ionaAtlasView'])
        self.recruit();self.state['residency']['iona']['residencyStatus']='visiting';self.state['additionalResidents']['iona']['status']='visiting'
        self.reject('start-iona-atlas')
        self.state['residency']['iona']['residencyStatus']='resident';self.state['additionalResidents']['iona']['status']='resident'
        self.state['materialReserveTargets']['binding-thread']=self.state['materialInventory']['binding-thread']
        self.reject('start-iona-atlas')

    def test_three_personal_phases_pause_resume_and_owner_only_rewards(self):
        self.recruit();before=deepcopy(self.state)
        self.state['characterSkills']['iona']['artifice']=2
        self.act('prepare-practice',characterId='iona',practiceId='careful-assembly',prepared=True)
        self.act('start-iona-atlas');self.advance()
        self.assertEqual(self.state['additionalResidents']['iona']['personalProject']['completedWorkPhases'],1)
        self.act('assign-character',characterId='iona',assignment='rest');self.advance()
        self.assertEqual(self.state['additionalResidents']['iona']['personalProject']['completedWorkPhases'],1)
        self.act('resume-iona-atlas');self.advance(2)
        self.assertIn('courteous-passage',g.character_principles(self.state,'iona'))
        self.assertNotIn('joined-fibres',g.character_principles(self.state,'iona'))
        self.assertEqual(self.state['characterDevelopment']['iona']['advancementAwards']['crossing-atlas']['points'],2)
        for who in ('mira','tamsin'):self.assertEqual(self.state['characterDevelopment'][who],before['characterDevelopment'][who])
        self.assertEqual(self.state['resonancePoints'],before['resonancePoints'])
        self.reject('start-iona-atlas');self.reject('cancel-iona-atlas')

    def test_cancel_exactly_refunds_and_preserves_other_assignment(self):
        self.recruit();before=deepcopy(self.state)
        self.act('start-iona-atlas');self.advance();self.act('assign-character',characterId='iona',assignment='rest')
        self.act('cancel-iona-atlas')
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.assertEqual(g.character_assignment(self.state,'iona'),'rest')
        self.assertEqual(self.state['characterDevelopment']['iona'],before['characterDevelopment']['iona'])
        self.reject('cancel-iona-atlas');self.act('start-iona-atlas')
        self.assertEqual(self.state['additionalResidents']['iona']['personalProject']['completedWorkPhases'],0)

    def test_departure_waits_for_both_professional_and_personal_commitments(self):
        self.recruit();self.act('start-iona-atlas')
        self.reject('summoning-depart',contactId=self.cid);self.advance(3)
        self.request('accept-personal-request');self.request('fund-personal-request',fundingSource='shared')
        self.reject('summoning-depart',contactId=self.cid)
        self.request('cancel-personal-request');self.act('summoning-depart',contactId=self.cid)

    def test_personal_funding_refund_returns_same_wallet_once(self):
        self.recruit();self.finish_atlas()
        self.request('accept-personal-request')
        self.state['personalFunds']['iona']=10;before=deepcopy(self.state)
        self.request('fund-personal-request',fundingSource='personal')
        self.assertEqual(self.state['personalFunds']['iona'],4)
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.advance();self.request('cancel-personal-request')
        self.assertEqual(self.state['personalFunds']['iona'],10)
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
        self.reject('cancel-personal-request',requestId='iona-map-case')

    def test_keepsake_and_completed_scenes_survive_departure_and_return(self):
        self.recruit();self.finish_atlas();self.request('accept-personal-request');self.request('fund-personal-request',fundingSource='shared');self.advance(2)
        self.request('read-personal-note');self.request('display-keepsake',displayed=True)
        self.act('join-resident-moment',momentId='iona-case')
        before=deepcopy(self.state['characterDevelopment']['iona'])
        self.act('summoning-depart',contactId=self.cid);self.advance()
        self.assertEqual(self.state['residentKeepsakes']['iona'],['iona-map-case'])
        self.assertTrue(g.resident_moment_view(self.state,'iona-case')['lines'])
        self.assertFalse(any('Iona' in item['name'] for item in g.room_furnishing_view(self.state,'garden-chamber')))
        self.act('summoning-invite',contactId=self.cid,roomId='garden-chamber');self.advance()
        self.assertFalse(g.resident_moment_view(self.state,'iona-return')['unlocked'])
        self.act('summoning-ask-stay',contactId=self.cid);self.act('summoning-household-decision',contactId=self.cid,decision='invite-to-stay')
        self.assertTrue(g.resident_moment_view(self.state,'iona-return')['unlocked'])
        self.assertEqual(self.state['characterDevelopment']['iona'],before)
        self.assertTrue(any('Iona' in item['name'] for item in g.room_furnishing_view(self.state,'garden-chamber')))
        self.assertEqual(json.loads(json.dumps(self.state))['residentKeepsakes']['iona'],['iona-map-case'])

    def test_shared_scene_is_optional_free_and_scoped_to_participants(self):
        self.recruit();self.finish_atlas();before=deepcopy(self.state)
        self.act('defer-resident-moment',momentId='iona-mira-map')
        self.reject('join-resident-moment',momentId='iona-mira-map')
        self.act('restore-resident-moment',momentId='iona-mira-map')
        self.act('join-resident-moment',momentId='iona-mira-map');after=deepcopy(self.state)
        self.act('join-resident-moment',momentId='iona-mira-map')
        self.assertEqual(self.state,after)
        self.assertEqual(self.state['additionalResidents']['tamsin']['conversation'],before['additionalResidents']['tamsin']['conversation'])
        for field in ('dayNumber','currentDayPhase','sharedFunds','resonancePoints','materialInventory','characterDevelopment'):self.assertEqual(self.state[field],before[field])
        self.assertTrue(any(row['participants']==['mira','iona'] for row in g.resident_friendships(self.state)))

    def test_migration_preserves_existing_contact_membership_and_accomplishments(self):
        self.recruit();old=deepcopy(self.state);old['schemaVersion']=21
        old['additionalResidents']['iona']['personalProject']={'status':'not-offered','completedWorkPhases':0,'requiredWorkPhases':0}
        old['people']['iona']['offeredAssignments'].remove('personal-project')
        old['personalRequests'].pop('iona-map-case')
        for key in list(old['residentMoments']):
            if key.startswith('iona-'):old['residentMoments'].pop(key)
        new=g.migrate_state(deepcopy(old))
        for key in ('summoningContacts','residency','sharedFunds','dayNumber','bedroomAssignments','characterDevelopment','personalFunds'):self.assertEqual(new[key],old[key])
        self.assertEqual(new['additionalResidents']['iona']['personalProject']['status'],'not-started')
        self.assertEqual(g.migrate_state(deepcopy(new)),new)

    def test_offered_gift_uses_shared_funds_and_persists_after_departure(self):
        self.recruit();before=deepcopy(self.state)
        self.act('give-personal-item',characterId='iona',itemId='travel-tea-tin')
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds']-3)
        self.assertEqual(self.state['personalFunds'],before['personalFunds'])
        self.assertEqual(self.state['personalPossessions']['iona'],['travel-tea-tin'])
        for key in ('dayNumber','currentDayPhase','resonancePoints','characterDevelopment','residency'):
            self.assertEqual(self.state[key],before[key])
        self.reject('give-personal-item',characterId='iona',itemId='travel-tea-tin')
        self.reject('buy-personal-item',characterId='iona',itemId='travel-tea-tin')
        self.act('summoning-depart',contactId=self.cid);self.advance()
        self.assertEqual(self.state['personalPossessions']['iona'],['travel-tea-tin'])

    def test_gifts_observe_owner_interests_presence_and_treasury_floor(self):
        self.recruit();self.reject('give-personal-item',characterId='iona',itemId='poetry-book')
        self.reject('give-personal-item',characterId='founder',itemId='scholar-journal')
        self.state['sharedFunds']=22;self.reject('give-personal-item',characterId='iona',itemId='travel-tea-tin')
        self.state['sharedFunds']=23;self.act('give-personal-item',characterId='iona',itemId='travel-tea-tin')
        self.assertEqual(self.state['sharedFunds'],20)
        self.act('start-expedition');self.reject('give-personal-item',characterId='mira',itemId='poetry-book')

    def test_atlas_refund_uses_saved_commitment_not_later_catalogue_cost(self):
        self.recruit();before=deepcopy(self.state)
        self.act('start-iona-atlas')
        old=deepcopy(resident_projects.IONA_ATLAS)
        try:
            resident_projects.IONA_ATLAS['costCrowns']=99
            resident_projects.IONA_ATLAS['materials']={'binding-thread':9}
            self.act('cancel-iona-atlas')
        finally:
            resident_projects.IONA_ATLAS.clear();resident_projects.IONA_ATLAS.update(old)
        self.assertEqual(self.state['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.state['materialInventory'],before['materialInventory'])
