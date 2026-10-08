"""Real-action opening playthroughs, branches, persistence and continuity."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
import game as g
import first_hearth as h
import guidance
import progression
import castle_mystery
from server import GameStore


class FirstHearthTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign('fresh')

    def act(self, kind, **kw):
        g.apply_action(self.s, {'type':kind, **kw})

    def advance(self, n=1):
        for _ in range(n):self.act('advance')

    def play(self, company='solo', approach='salvage', conclusion='history', reload_each=False):
        actions=[]; phased=[]
        for _ in range(180):
            before=deepcopy(self.s)
            v=h.view(self.s)
            self.assertEqual(self.s,before,'Guidance is read-only')
            if v['complete']:break
            if v['scene']:
                sc=v['scene'];key=sc['id']
                self.assertFalse(any('response' in c for c in sc['choices']))
                choice=company if key=='company' else conclusion if key=='conclusion' else sc['choices'][0]['id']
                a={'type':'first-hearth-choice','sceneId':key,'choiceId':choice}
            elif self.s['expedition']:
                p=self.s['expedition']
                if p['stage']=='awaiting-choice':a={'type':'choose-expedition-approach','approach':approach}
                elif p['stage']=='ready-to-return':a={'type':'return-expedition'}
                else:a={'type':'advance'}
            elif v['next']['id']=='fieldwork':
                a={'type':'start-expedition','siteId':'quarry-shelter','carryLantern':True}
            else:
                self.assertFalse(v['nextBlockers'],v)
                a=v['next']['action'];self.assertIsNotNone(a,v)
            actions.append(a)
            g.apply_action(self.s,a)
            if a['type']=='first-hearth-choice':
                for k in ('sharedFunds','materialInventory','dayNumber','currentDayPhase','founderAssignment','headquarters','relationships'):
                    self.assertEqual(self.s[k],before[k],k)
            if a['type']=='advance':phased.append({'day':self.s['dayNumber'],'phase':self.s['currentDayPhase'],'funds':self.s['sharedFunds']})
            if reload_each:self.s=g.migrate_state(json.loads(json.dumps(self.s)))
        else:self.fail('Opening did not complete: '+repr(h.view(self.s)))
        self.assertTrue(h.view(self.s)['complete'])
        self.assertTrue(self.s['livingWingCompletedOn'])
        self.assertIn('hearth-margin',self.s['castleMystery']['discoveries'])
        self.assertFalse(self.s['testing']['used'])
        self.assertGreaterEqual(self.s['sharedFunds'],0)
        self.assertLessEqual(len(phased),30)
        return actions,phased

    def test_solo_salvage_playthrough_no_cheats_or_extra_resources(self):
        actions,phased=self.play(reload_each=True)
        self.assertEqual(g.household_members(self.s),['founder'])
        self.assertEqual(self.s['materialInventory']['porous-clay'],1)
        self.assertFalse(any(a['type']=='buy-material' for a in actions))
        self.assertTrue(all(m['complete'] for m in h.view(self.s)['milestones']))

    def test_company_survey_playthrough_and_chosen_next_direction(self):
        actions,phased=self.play(company='meet',approach='survey',conclusion='household')
        self.assertEqual(self.s['localEncounters']['maren']['status'],'introduced')
        self.assertNotIn('maren',g.household_members(self.s),'A meeting is not membership')
        self.assertEqual(h.view(self.s)['next']['target']['view'],'peopleHub')
        self.assertEqual(h.record(self.s)['memories']['repair-notes']['personId'],'maren')
        self.assertTrue(any(a['type']=='buy-material' and a['materialId']=='porous-clay' for a in actions))

    def test_pausing_and_resuming_keeps_exact_funding_and_work(self):
        self.act('start-research');self.advance()
        self.act('assign-founder',assignment='commissions')
        v=h.view(self.s)['next'];self.assertEqual(v['action'],{'type':'assign-founder','assignment':'research'})
        funds=self.s['sharedFunds'];g.apply_action(self.s,v['action'])
        self.assertEqual(self.s['sharedFunds'],funds)
        self.assertEqual(self.s['researchCompletedPhases'],1)
        self.assertEqual(h.view(self.s)['next']['action'],{'type':'advance'})

    def test_skip_restore_and_legacy_opt_in_do_not_invent_history(self):
        self.act('first-hearth-guidance',enabled=False)
        self.act('start-research');self.advance(3)
        self.assertFalse(h.view(self.s)['enabled'])
        self.act('first-hearth-guidance',enabled=True)
        self.assertEqual(h.view(self.s)['scene']['id'],'intention')
        old=deepcopy(self.s);old['soloLife'].pop('firstHearth')
        before=deepcopy(old);g.migrate_state(old);h.view(old)
        self.assertEqual(old,before)
        self.assertFalse(h.view(old)['enrolled'])
        g.apply_action(old,{'type':'first-hearth-guidance','enabled':True})
        self.assertEqual(h.record(old)['memories'],{})
        self.assertEqual(old['researchCompletedPhases'],before['researchCompletedPhases'])
        self.assertIsNone(h.view(g.new_campaign('demo')))

    def test_invalid_early_repeat_and_away_choices_are_atomic(self):
        def reject(**a):
            before=deepcopy(self.s)
            with self.assertRaises(g.RuleError):g.apply_action(self.s,a)
            self.assertEqual(self.s,before)
        reject(type='first-hearth-choice',sceneId='conclusion',choiceId='history')
        reject(type='first-hearth-guidance',enabled='true')
        self.act('start-research');self.advance(3)
        reject(type='first-hearth-choice',sceneId='intention',choiceId='bogus')
        self.act('start-expedition',siteId='quarry-shelter')
        reject(type='first-hearth-choice',sceneId='intention',choiceId='comfort')
        self.act('return-expedition');self.advance()
        self.act('first-hearth-choice',sceneId='intention',choiceId='comfort')
        reject(type='first-hearth-choice',sceneId='intention',choiceId='comfort')

    def test_alternative_materials_and_exact_shortfall(self):
        self.s['materialInventory']['sun-amber']=0
        self.s['materialInventory']['fireglass']=1
        n=h.recipe_step(self.s,'warming-lantern')
        self.assertEqual(n['action']['type'],'start-crafting')
        self.assertIn('fireglass',n['action']['materials'])
        self.s['materialInventory']={k:0 for k in self.s['materialInventory']}
        self.s['sharedFunds']=0
        n=h.recipe_step(self.s,'warming-lantern')
        self.assertEqual(n['id'],'income');self.assertIn('crowns',n['detail'])

    def test_existing_unrelated_crafting_is_resumed_not_replaced(self):
        self.act('start-research');self.advance(3)
        self.act('buy-material',materialId='porous-clay')
        self.act('start-crafting',recipeId='hearth-kettle',materials=['sun-amber','porous-clay'])
        self.advance();self.act('assign-founder',assignment='rest')
        before=deepcopy(self.s['craftingProject'])
        n=h.recipe_step(self.s,'warming-lantern')
        self.assertEqual(n['target']['recipeId'],'hearth-kettle')
        g.apply_action(self.s,n['action'])
        self.assertEqual(self.s['craftingProject'],before)

    def test_mystery_in_preview_resume_and_solo_archive_continuation(self):
        self.play()
        self.act('assign-founder',assignment='commissions')
        while self.s['sharedFunds']<g.RESEARCH_CATALOG['archive-foundations']['costCrowns']:self.advance()
        self.act('focus-research',researchId='archive-foundations',leaderId='founder')
        self.advance(3)
        self.assertEqual(castle_mystery.blockers(self.s,'archive-leaf'),[])
        self.act('start-mystery',leadId='archive-leaf')
        self.advance();self.act('assign-founder',assignment='rest')
        p=next(p for p in guidance.preview(self.s)['projects'] if p['id']=='mystery')
        self.assertEqual(p['progress'],0)
        g.apply_action(self.s,progression.resume_action(self.s,'mystery'))
        p=next(p for p in guidance.preview(self.s)['projects'] if p['id']=='mystery')
        self.assertTrue(p['completes']);self.advance()
        self.assertIn('archive-leaf',self.s['castleMystery']['discoveries'])

    def test_no_undiscovered_lore_or_future_replies_in_public_view(self):
        public=json.dumps(g.public_state(self.s))
        self.assertNotIn(self.s['privateCastleLore']['foundation'],public)
        self.assertNotIn('You leave a chair beside the hearth.',public)
        self.assertNotIn(self.s['privateCastleLore']['evidence']['hearth-margin'],public)

    def test_declining_the_introduction_does_not_cancel_other_work(self):
        self.act('start-research');self.advance(3)
        self.act('first-hearth-choice',sceneId='intention',choiceId='comfort')
        self.act('start-crafting',recipeId='warming-lantern',materials=['sun-amber','binding-thread'])
        self.advance(2)
        self.act('first-hearth-choice',sceneId='company',choiceId='meet')
        self.act('start-local-visit',encounterId='maren')
        before=deepcopy(self.s['localVisit'])
        self.act('first-hearth-solo')
        self.assertEqual(self.s['localVisit'],before)
        self.assertEqual(self.s['founderAssignment'],'local-visit')
        self.assertEqual(h.view(self.s)['next']['id'],'fieldwork')

    def test_evening_waits_for_evening_and_survives_delay(self):
        self.play()
        h.record(self.s)['memories'].pop('conclusion')
        h.record(self.s)['memories'].pop('evening')
        while self.s['currentDayPhase']!='morning':self.advance()
        self.assertEqual(h.view(self.s)['next']['id'],'evening-waits')
        self.advance(2)
        self.assertEqual(h.view(self.s)['scene']['id'],'evening')
        self.advance(3)
        self.assertEqual(h.view(self.s)['scene']['id'],'evening')

    def test_dialogue_only_receives_the_speakers_actual_opening_scene(self):
        import dialogue
        import summoning
        self.play(company='meet')
        contact=next(k for k,c in self.s['summoningContacts'].items() if c['personId']=='maren')
        for topic in summoning.candidate_catalogue(self.s)['maren']['topics']:
            self.act('summoning-talk',contactId=contact,topic=topic)
        self.act('summoning-invite',contactId=contact,roomId='bedchamber');self.advance()
        self.act('summoning-ask-stay',contactId=contact)
        self.act('summoning-household-decision',contactId=contact,decision='invite-to-stay')
        context=dialogue.dialogue_context(self.s,'Remember the repair list?','maren')
        # dialogue_context returns the model message list; inspect its structured user facts.
        text=json.dumps(context)
        self.assertIn('The respectable end of the repair list',text)
        self.assertNotIn(h.record(self.s)['memories']['intention']['text'],text)
        self.assertNotIn(self.s['privateCastleLore']['evidence']['hearth-margin'],text)

    def test_saved_choices_retry_and_artwork_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory,start_type='fresh')
            art=Path(directory,'assets','kept.webp');art.parent.mkdir(exist_ok=True);art.write_bytes(b'saved artwork')
            payload={'requestId':'hearth-hide','expectedRevision':store.read()['revision'],'action':{'type':'first-hearth-guidance','enabled':False}}
            once=store.action(payload)
            self.assertEqual(store.action(payload),once)
            self.assertEqual(GameStore(directory).read(),once)
            self.assertFalse(h.view(once)['enabled'])
            self.assertEqual(art.read_bytes(),b'saved artwork')

if __name__=='__main__':unittest.main()
