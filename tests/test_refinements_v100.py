"""Behavior checks for the eight v0.100 refinements, including normal save reloads."""
from copy import deepcopy
import json
import tempfile
import unittest
import uuid

import game as g
import armoury as gear
import castle_mystery
import castle_reawakening as castle
import commissions
import field_magic as magic
import field_objectives as objectives
import field_patrols as patrol
import household_routines as routines
import practical_projects as projects
import shared_history as history
import signature_growth as growth
import test_household_chapters as household
from server import GameStore


class RefinementTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign('fresh')
        self.s['provisions']['stock']=500

    def act(self,kind,**kwargs):
        g.apply_action(self.s,dict(type=kind,**kwargs))
        self.s=g.migrate_state(json.loads(json.dumps(self.s)))

    def advance(self,n=1):
        for _ in range(n):self.act('advance')

    def reject(self,kind,**kwargs):
        old=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kwargs)
        self.assertEqual(old,self.s)

    def member(self,who):
        household.HouseholdChapterTests.member(self,who)
        if who!='mira':self.act('agree-household-role',characterId=who,role='fieldwork',enabled=True,willingnessReviewed=True)
        self.s['bedroomAssignments'].setdefault(who,None)
        gear.sync(self.s)

    def room(self,which):household.HouseholdChapterTests.room(self,which)

    def fund(self):
        self.s['sharedFunds']=300
        for k in self.s['materialInventory']:self.s['materialInventory'][k]=20

    def field_ready(self):
        self.s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'}
        magic.initialize(self.s)['vitality']['founder']=6

    def spell(self,who,form):
        self.fund()
        for p in g.SPELL_FORMS[form]['requiredPrinciples']:g.learn_for_character(self.s,who,p)
        key='test-'+who+'-'+form
        self.s['spellbook'].append(dict(id=key,ownerId=who,formId=form,name=g.SPELL_FORMS[form]['name'],status='learned',castCount=0,completedWorkPhases=2,components=[],materials=[],intent=g.SPELL_FORMS[form]['description']))
        self.s['preparedSpells'][who].append(key)
        return key

    def signature(self,who='founder',choice=None,rank=1):
        gear.sync(self.s)
        it=gear.make(self.s,'steel-knife',who)
        it['signatureOwner']=who
        gear.state(self.s)['signatures'][who]={'itemId':it['id'],'completedOn':{'day':1}}
        for mode in ('household','expedition'):
            self.act('gear-equip',ownerId=who,itemId=it['id'],mode=mode,replaceConfirmed=True)
        it=gear.state(self.s)['items'][it['id']]
        if choice:it['fieldRefinement']=dict(ownerId=who,choice=choice,rank=rank)
        return it['id']

    def depart(self,key,party=None):
        self.field_ready()
        if key=='observe':self.s['characterSkills']['founder']['fieldcraft']=1
        self.act('watch-depart',participants=party or ['founder'],objectiveId=key)
        self.advance()
        self.assertEqual(patrol.saved(self.s)['active']['stage'],'site-decision')

    def site_manual(self,who='founder'):
        row=next(r for r in objectives.site_choices(self.s,patrol.saved(self.s)['active']) if r['id']==who+':site-work')
        self.act('watch-site-method',methodId=row['id']);self.advance(row['phases'])
        self.assertEqual(patrol.saved(self.s)['active']['stage'],'decision')

    def finish_tasks(self,who='founder'):
        for _ in range(4):
            run=patrol.saved(self.s)['active']
            if run['stage']=='returning':break
            row=next(r for r in patrol.choices(self.s) if r['id']==who+':objective')
            expected=deepcopy(row['preview']['healthAfter'])
            self.act('watch-method',methodId=row['id']);self.advance()
            self.assertEqual({w:magic.vitality(self.s,w) for w in expected},expected)
        self.assertEqual(patrol.saved(self.s)['active']['stage'],'returning')
        self.advance()

    def test_commission_quotes_payment_cooldown_and_repeat_reward(self):
        before=self.s['sharedFunds'];q=commissions.rewards(self.s,'translate')['crowns']['crowns']
        self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns')
        self.assertEqual(self.s['sharedFunds'],before)
        self.advance(2)
        self.assertEqual(self.s['sharedFunds'],before+q)
        self.assertEqual(g.character_assignment(self.s,'founder'),'rest')
        self.reject('commission-start',commissionId='translate',workerId='founder',payment='crowns')
        self.advance();self.act('commission-start',commissionId='translate',workerId='founder',payment='materials');self.advance(2)
        self.assertEqual(self.s['materialInventory']['moon-glass'],1)

    def test_commission_lesson_once_per_worker(self):
        self.act('commission-start',commissionId='translate',workerId='founder',payment='knowledge');self.advance(2)
        awards=deepcopy(self.s['characterDevelopment']['founder']['advancementAwards']);self.advance()
        self.reject('commission-start',commissionId='translate',workerId='founder',payment='knowledge')
        self.assertEqual(awards,self.s['characterDevelopment']['founder']['advancementAwards'])

    def test_companion_commission_agreement_and_paused_work(self):
        self.member('zahra');self.reject('commission-start',commissionId='translate',workerId='zahra',payment='crowns')
        self.act('commission-start',commissionId='translate',workerId='zahra',payment='crowns',agreed=True)
        self.advance();self.act('assign-character',characterId='zahra',assignment='rest');self.advance()
        self.assertEqual(commissions.saved(self.s)['job']['done'],1)
        self.act('commission-resume');self.advance()
        self.assertTrue(history.view(self.s,'zahra'))

    def test_commission_refund_and_protected_materials(self):
        self.fund();self.room('workshop');self.s['characterSkills']['founder']['artifice']=1
        before=deepcopy(self.s['materialInventory'])
        self.act('commission-start',commissionId='restore',workerId='founder',payment='materials');self.advance()
        self.act('commission-cancel');self.assertEqual(before,self.s['materialInventory'])
        self.s['materialReserveTargets']['binding-thread']=self.s['materialInventory']['binding-thread']
        self.reject('commission-start',commissionId='restore',workerId='founder',payment='materials')

    def test_project_routine_sleeps_resumes_and_stops(self):
        self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns')
        self.s['currentDayPhase']='evening'
        self.act('routine-start',workerId='founder',mode='project',projectId='commission',restEvenings=True)
        old=deepcopy(self.s);preview=g.public_state(self.s)['advancePreview'];self.assertEqual(old,self.s)
        self.assertTrue(preview['routineChanges'])
        self.advance();self.assertEqual(commissions.saved(self.s)['job']['done'],0)
        self.assertEqual(self.s['overnightRest']['founder'],self.s['dayNumber'])
        self.assertEqual(g.character_assignment(self.s,'founder'),'external-commission')
        self.advance(2);self.assertEqual(routines.saved(self.s)['founder']['status'],'complete')
        self.assertEqual(g.character_assignment(self.s,'founder'),'rest')

    def test_gather_routine_resumes_paid_project_only_next_phase(self):
        self.act('start-research');target=self.s['provisions']['stock']+1
        self.act('routine-start',workerId='founder',mode='provisions',target=target,assignment='forage',afterProject='hearth',restEvenings=False)
        self.advance();self.assertEqual(self.s['researchCompletedPhases'],0)
        self.assertEqual(g.character_assignment(self.s,'founder'),'research')
        self.advance();self.assertGreater(self.s['researchCompletedPhases'],0)

    def test_routine_stops_when_stock_arrives_before_next_phase(self):
        self.act('start-research');target=self.s['provisions']['stock']+1
        self.act('routine-start',workerId='founder',mode='provisions',target=target,afterProject='hearth',restEvenings=False)
        self.s['provisions']['stock']=target
        self.advance()
        self.assertEqual(self.s['researchCompletedPhases'],0)
        self.assertEqual(routines.saved(self.s)['founder']['status'],'complete')
        self.assertEqual(g.character_assignment(self.s,'founder'),'research')
        self.assertTrue(any('already has the agreed provision stock' in x for x in self.s['lastPhaseSummary']))

    def test_two_sleeping_routines_survive_nested_resumption(self):
        self.member('zahra');self.fund();self.room('smithy')
        self.s.setdefault('fieldPatrols',dict(serial=0,active=None,reports=[]))['reports']=[dict(party=['zahra'],complete=True)]
        self.act('practical-start',characterId='zahra')
        self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns')
        for who,key in [('founder','commission'),('zahra','practical:zahra')]:
            self.act('routine-start',workerId=who,mode='project',projectId=key,restEvenings=True)
        self.s['currentDayPhase']='evening';self.advance()
        for who in ('founder','zahra'):
            self.assertFalse(routines.saved(self.s)[who]['sleeping'])
            self.assertEqual(routines.saved(self.s)[who]['status'],'active')
        self.assertEqual(commissions.saved(self.s)['job']['done'],0)
        self.assertEqual(projects.saved(self.s)['zahra']['done'],0)
        self.advance();self.assertEqual(commissions.saved(self.s)['job']['done'],1)
        self.assertEqual(projects.saved(self.s)['zahra']['done'],1)

    def test_work_arrangement_restores_new_assignments_and_work_rooms(self):
        import room_life,work_arrangements
        self.member('zahra');self.fund();self.room('smithy');self.room('workshop')
        self.s.setdefault('fieldPatrols',dict(serial=0,active=None,reports=[]))['reports']=[dict(party=['zahra'],complete=True)]
        self.s['characterSkills']['founder']['artifice']=1
        self.act('practical-start',characterId='zahra')
        self.act('commission-start',commissionId='restore',workerId='founder',payment='crowns')
        self.act('save-work-arrangement',name='Paid jobs')
        for who in ('founder','zahra'):self.act('assign-character',characterId=who,assignment='rest')
        self.assertTrue(work_arrangements.view(self.s)['plans'][0]['canApply'])
        self.act('apply-work-arrangement',name='Paid jobs')
        self.assertEqual(room_life.location(self.s,'founder'),'workshop')
        self.assertEqual(room_life.location(self.s,'zahra'),'smithy')
        self.reject('assign-character',characterId='zahra',assignment='external-commission')
        self.s['castleMystery']['discoveries']['lamp-plan']={'text':'Found repair plan'}
        self.act('castle-lamp-start');self.act('assign-founder',assignment='rest')
        self.act('assign-founder',assignment='castle-lamp')
        self.assertEqual(g.character_assignment(self.s,'founder'),'castle-lamp')

    def test_manual_reassignment_and_travel_pause_routines(self):
        self.act('routine-start',workerId='founder',mode='provisions',target=900,assignment='forage',restEvenings=False)
        self.act('assign-founder',assignment='commissions');self.advance()
        self.assertEqual(routines.saved(self.s)['founder']['status'],'paused')
        self.assertEqual(g.character_assignment(self.s,'founder'),'commissions')
        self.act('routine-resume',workerId='founder');self.field_ready();self.act('watch-depart',participants=['founder'],routeId='road');self.advance()
        self.assertEqual(routines.saved(self.s)['founder']['status'],'paused')

    def test_routine_rejects_unfunded_and_wrong_owner_without_side_effects(self):
        self.reject('routine-start',workerId='founder',mode='project',projectId='made-up',restEvenings=True)
        self.reject('routine-start',workerId='founder',mode='provisions',target=True,assignment='forage')
        self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns')
        self.member('zahra');self.reject('routine-start',workerId='zahra',mode='project',projectId='commission')

    def test_all_objectives_pay_without_enemy_loot_and_do_not_repeat_advancement(self):
        for key,d in objectives.OBJECTIVES.items():
            self.depart(key);self.site_manual();funds=self.s['sharedFunds'];self.finish_tasks()
            r=patrol.saved(self.s)['reports'][-1]
            self.assertTrue(r['complete']);self.assertEqual(r['loot']['crowns'],d['crowns'])
            self.assertEqual(self.s['sharedFunds'],funds+d['crowns'])
            self.assertFalse(r['outcomes'][0]['rewarded'])
        awards=deepcopy(self.s['characterDevelopment']['founder']['advancementAwards'])
        self.depart('escort');self.site_manual();self.finish_tasks()
        self.assertEqual(awards,self.s['characterDevelopment']['founder']['advancementAwards'])

    def test_all_site_spell_conditions_need_followup_work(self):
        for key,form in [('escort','ice-bind'),('rescue','wind-step'),('repair','water-jet')]:
            self.s=g.new_campaign('fresh');self.s['provisions']['stock']=500;spell=self.spell('founder',form)
            self.depart(key);before=deepcopy(self.s['materialInventory'])
            row=next(r for r in objectives.site_choices(self.s,patrol.saved(self.s)['active']) if r.get('spellId')==spell)
            self.act('watch-site-method',methodId=row['id']);self.assertFalse(patrol.saved(self.s)['active']['siteWork']['condition'])
            for k,n in row['inputs'].items():self.assertEqual(self.s['materialInventory'][k],before[k]-n)
            self.advance();self.assertTrue(patrol.saved(self.s)['active']['siteWork']['condition']);self.assertEqual(g.spell_by_id(self.s,spell)['castCount'],1)
            row=objectives.site_choices(self.s,patrol.saved(self.s)['active'])[0];self.assertEqual(row['phases'],1)
            self.act('watch-site-method',methodId=row['id']);self.advance();self.assertTrue(patrol.saved(self.s)['active']['siteWork']['complete'])

    def test_different_member_can_finish_spell_prepared_site(self):
        self.member('neris');spell=self.spell('neris','water-jet');self.depart('repair',['founder','neris'])
        row=next(r for r in objectives.site_choices(self.s,patrol.saved(self.s)['active']) if r.get('spellId')==spell)
        self.act('watch-site-method',methodId=row['id']);self.advance()
        self.act('watch-site-method',methodId='founder:site-work');self.advance()
        run=patrol.saved(self.s)['active'];self.assertIn('practical-spell',run['workProofs']['neris']);self.assertIn('site-repair',run['workProofs']['founder'])

    def test_retreat_refunds_only_unresolved_cast_and_no_objective_payment(self):
        spell=self.spell('founder','ice-bind');self.depart('escort')
        materials=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds']
        row=next(r for r in objectives.site_choices(self.s,patrol.saved(self.s)['active']) if r.get('spellId')==spell)
        self.act('watch-site-method',methodId=row['id']);self.act('watch-retreat');self.advance()
        self.assertEqual(materials,self.s['materialInventory']);self.assertEqual(funds,self.s['sharedFunds'])
        self.depart('escort');self.act('watch-site-method',methodId=row['id']);self.advance();used=deepcopy(self.s['materialInventory'])
        self.act('watch-retreat');self.advance();self.assertEqual(used,self.s['materialInventory'])
        self.assertFalse(patrol.saved(self.s)['reports'][-1]['complete'])

    def test_waiting_and_reading_never_change_site_conditions(self):
        self.depart('repair');before=deepcopy(patrol.saved(self.s)['active'])
        for _ in range(2):
            old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s);self.advance()
        self.assertEqual(before,patrol.saved(self.s)['active'])

    def test_scout_observation_is_safe_and_components_are_paid(self):
        spell=self.spell('founder','wisp-scout');self.depart('observe');self.site_manual()
        before=self.s['materialInventory']['sun-amber']
        for _ in range(2):
            row=next(r for r in patrol.choices(self.s) if r.get('spellId')==spell)
            self.assertTrue(row['preview']['cancelled']);self.act('watch-method',methodId=row['id']);self.advance()
        self.assertEqual(magic.vitality(self.s,'founder'),6)
        self.assertEqual(self.s['materialInventory']['sun-amber'],before-2)
        self.advance();self.assertEqual(patrol.saved(self.s)['reports'][-1]['loot']['crowns'],12)

    def test_companion_improvements_actual_effects_and_refunds(self):
        self.fund()
        for who in projects.PROJECTS:self.member(who);self.room(projects.PROJECTS[who]['room'])
        self.s['additionalResidents']['iona']['personalProject']['status']='complete'
        self.s.setdefault('fieldPatrols',dict(serial=0,active=None,reports=[]))['reports']=[dict(party=['zahra'],complete=True)]
        self.s['fieldObjectiveHistory']={'observe':True}
        for who in projects.PROJECTS:
            funds=self.s['sharedFunds'];materials=deepcopy(self.s['materialInventory'])
            self.act('practical-start',characterId=who);self.advance();self.act('practical-cancel',characterId=who)
            self.assertEqual(funds,self.s['sharedFunds']);self.assertEqual(materials,self.s['materialInventory'])
            self.act('practical-start',characterId=who);self.advance(3);self.assertTrue(projects.active(self.s,who))
            self.reject('practical-start',characterId=who)
        self.depart('escort',['founder','iona','zahra']);self.site_manual()
        row=next(r for r in patrol.choices(self.s) if r['id']=='iona:atlas-route')
        self.assertTrue(row['preview']['cancelled'])
        import patrol_tactics
        self.assertTrue(any('fitted straps' in x for x in patrol_tactics.defence(self.s,'founder',['founder','zahra'])[1]))
        self.act('watch-method',methodId=row['id']);self.advance(2)
        self.assertEqual(patrol.saved(self.s)['reports'][-1]['loot']['crowns'],16)
        self.depart('observe');self.site_manual();self.finish_tasks()
        self.assertEqual(patrol.saved(self.s)['reports'][-1]['loot']['materials']['silver-ivy'],2)

    def test_signature_work_proofs_require_equipped_actual_piece(self):
        key=self.signature();self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns');self.advance(2)
        it=gear.state(self.s)['items'][key];self.assertEqual(it['fieldHistory']['workTypes'],['commission:translate'])
        self.advance();self.act('commission-start',commissionId='translate',workerId='founder',payment='crowns');self.advance(2)
        self.assertEqual(growth.proof_count(growth.history(gear.state(self.s)['items'][key],'founder')),1)
        self.act('gear-stow',ownerId='founder',itemId=key,mode='household')
        growth.record_work(self.s,'founder','new-proof')
        self.assertEqual(growth.proof_count(growth.history(gear.state(self.s)['items'][key],'founder')),1)

    def test_personal_refinement_preview_and_resolved_result_match(self):
        key=self.signature(choice='personal');self.spell('founder','water-jet');self.depart('repair');self.site_manual()
        row=next(r for r in patrol.choices(self.s) if r.get('spellKind')=='water')
        self.assertEqual(row['personalDamage'],1);expected=row['preview']['enemyAfter']
        self.act('watch-method',methodId=row['id']);self.advance()
        self.assertEqual(patrol.saved(self.s)['active']['hp'],expected)
        self.assertEqual(len(growth.PERSONAL),16)
        self.assertTrue(all('personal' in growth.choices_for(w) for w in growth.PERSONAL))

    def test_work_only_patrol_reports_unlocked_refinement(self):
        key=self.signature();growth.record_work(self.s,'founder','commission:translate')
        self.depart('observe');self.site_manual();self.finish_tasks()
        report=patrol.saved(self.s)['reports'][-1]
        self.assertFalse(any(r['rewarded'] for r in report['outcomes']))
        self.assertTrue(any(r['itemId']==key and r['rank']==1 for r in report['signatureUnlocks']))

    def test_zahra_cover_waits_for_first_actual_retaliation(self):
        import patrol_tactics
        self.member('zahra');self.fund();self.room('smithy')
        self.s.setdefault('fieldPatrols',dict(serial=0,active=None,reports=[]))['reports']=[dict(party=['zahra'],complete=True)]
        self.act('practical-start',characterId='zahra');self.advance(3)
        self.spell('founder','ice-bind');self.depart('rescue',['founder','zahra']);self.site_manual()
        ice=next(r for r in patrol.choices(self.s) if r.get('spellKind')=='ice')
        self.act('watch-method',methodId=ice['id']);self.advance()
        self.assertTrue(any('fitted straps' in x for x in patrol_tactics.defence(self.s,'founder',['founder','zahra'])[1]))
        self.act('watch-method',methodId='founder:objective');self.advance()
        self.assertFalse(any('fitted straps' in x for x in patrol_tactics.defence(self.s,'founder',['founder','zahra'])[1]))

    def test_owner_refinements_keep_one_paid_equipment_job(self):
        key=self.signature();self.room('enchanting-room');self.fund()
        growth.record_work(self.s,'founder','commission:translate');growth.record_work(self.s,'founder','site-repair')
        q=growth.quote(self.s,'founder','personal',1);self.assertFalse(q['blockers'])
        self.act('gear-signature-refine',ownerId='founder',choice='personal',rank=1)
        self.assertFalse(growth.effect(self.s,'founder'));self.advance(2)
        self.assertEqual(gear.state(self.s)['items'][key]['fieldRefinement']['choice'],'personal')
        self.assertFalse(growth.effect(self.s,'founder'))
        self.act('gear-equip',ownerId='founder',itemId=key,mode='expedition',replaceConfirmed=True)
        self.assertEqual(growth.personal_effect(self.s,'founder'),'spell')

    def test_history_is_specific_bounded_and_does_not_dispatch(self):
        self.member('zahra');history.record(self.s,'actual-repair',['founder','zahra'],'Repaired the wagon','Zahra replaced the split axle bracket.','work')
        history.record(self.s,'later-repair',['founder','zahra'],'Another wagon','Another fact.','work')
        rows=history.view(self.s);self.assertEqual(len(rows),1);self.assertIn('split axle bracket',rows[0]['opening'])
        self.act('history-defer',eventId=rows[0]['id']);self.advance(3);self.assertTrue(history.view(self.s)[0]['deferred'])
        self.act('history-restore',eventId=rows[0]['id']);before=self.s['currentDayPhase'];points=deepcopy(self.s['relationships'])
        self.act('history-share',eventId=rows[0]['id'],choiceId='plan')
        self.assertEqual(self.s['currentDayPhase'],before);self.assertEqual(self.s['relationships'],points);self.assertFalse(patrol.saved(self.s)['active'])
        self.assertEqual(history.saved(self.s)['suggestedParty'],['founder','zahra'])
        self.reject('history-share',eventId=rows[0]['id'],choiceId='plan')

    def test_history_requires_present_participants_and_romance_for_affection(self):
        self.member('zahra');history.record(self.s,'actual',['zahra'],'Finished work','The repaired lantern passed its test.','work')
        e=history.view(self.s)[0];self.assertNotIn('affection',[c['id'] for c in e['choices']])
        self.reject('history-share',eventId=e['id'],choiceId='affection')
        self.field_ready();self.act('watch-depart',participants=['zahra'],routeId='road')
        self.reject('history-share',eventId=e['id'],choiceId='credit')

    def test_full_mystery_restoration_study_and_old_truth_preserved(self):
        self.fund();self.room('workshop');self.s['livingWingCompletedOn']={'dayNumber':1,'phase':'morning'}
        self.s['researchProjects']['archive-foundations']['status']='complete'
        for p in ('gentle-refraction','courteous-passage'):g.learn_for_character(self.s,'founder',p)
        foundation=self.s['privateCastleLore']['foundation'];old=deepcopy(self.s['privateCastleLore']['evidence'])
        for key in castle_mystery.LEADS:
            self.act('start-mystery',leadId=key);self.advance(castle_mystery.LEADS[key]['phases'])
        self.assertEqual(self.s['privateCastleLore']['foundation'],foundation)
        self.assertTrue(all(self.s['privateCastleLore']['evidence'][k]==v for k,v in old.items()))
        self.assertEqual(len(self.s['castleMystery']['discoveries']),7)
        self.act('castle-lamp-start');self.advance(2);self.assertTrue(castle.saved(self.s)['restored'])
        self.reject('castle-lamp-study');self.s['resonancePoints']=12;self.act('castle-lamp-study');self.advance(2)
        self.assertEqual(self.s['resonancePoints'],12);self.assertIn('field-calibration',g.character_principles(self.s,'founder'))
        self.act('castle-lamp-colour',colour='violet');self.assertEqual(self.s['roomFurnishings']['library'],'violet-lamp')
        self.member('zahra');self.act('castle-lamp-share',characterId='zahra');self.assertTrue(history.view(self.s,'zahra'))
        self.reject('castle-lamp-share',characterId='zahra');self.reject('castle-lamp-study')

    def test_private_new_evidence_never_leaks_before_discovery(self):
        self.s['privateCastleLore']['evidence']['ward-junction']='UNSEEN_WARD_SENTINEL'
        from dialogue import dialogue_context
        self.assertNotIn('UNSEEN_WARD_SENTINEL',json.dumps(g.public_state(self.s)))
        self.assertNotIn('UNSEEN_WARD_SENTINEL',json.dumps(dialogue_context(g.new_campaign(),'hello')))

    def test_resonance_all_authored_romances_contribute_with_cap_and_no_double_count(self):
        self.s=g.new_campaign();self.s['roomFurnishings']['common-room']='velvet-settee'
        self.s['romance']={'people':{},'memories':{},'dates':{}}
        for who in ('mira','zahra','neris','sylva'):
            self.member(who);self.s['romance']['people'][who]={'level':1,'mode':'open','deferred':False}
        self.s['completedDevelopments'].append('shared-flirtation')
        self.assertEqual(g.resonance_forecast(self.s),3)
        self.s['roomFurnishings']['common-room']='reading-table';self.assertEqual(g.resonance_forecast(self.s),0)

    def test_v099_save_read_is_exact_and_new_action_retry_is_idempotent(self):
        import zipfile
        from pathlib import Path
        # A clean schema-65 save with no optional v0.100 records changes only after an action.
        before=deepcopy(self.s);self.assertEqual(g.migrate_state(deepcopy(before)),before)
        g.public_state(self.s);self.assertEqual(before,self.s)
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory,start_type='fresh');s=store.read()
            payload=dict(requestId=uuid.uuid4().hex,expectedRevision=s['revision'],action=dict(type='commission-start',commissionId='translate',workerId='founder',payment='crowns'))
            first=store.action(payload);again=store.action(payload);self.assertEqual(first,again)
            self.assertEqual(GameStore(directory).read(),first)

if __name__=='__main__':unittest.main()
