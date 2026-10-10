"""Chapter progression and exact, reversible household-blessing mechanics."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
import uuid

import game as g
import foundation_chamber as f
import resident_bonds
import relationships
import magic_reference
import headquarters
import field_patrols
import test_household_chapters as household
from server import GameStore


class FoundationChamberTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign()
        field_patrols.initialize(self.s)
        self.s['firstRealTest']['completedOn']={'dayNumber':1,'phase':'morning'}
        self.s['sharedFunds']=100
        self.s['provisions']['stock']=200
        for key in ('binding-thread','porous-clay','fireglass'):
            self.s['materialInventory'][key]=6

    def act(self,kind,**fields):
        return g.apply_action(self.s,dict(type=kind,**fields))

    def reject(self,kind,**fields):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**fields)
        self.assertEqual(before,self.s)

    def step(self,key,method='careful'):
        self.act('foundation-task',stepId=key,methodId=method)
        count=f.saved(self.s)['job']['phases']
        for _ in range(count):self.act('advance')
        self.assertIn(key,f.saved(self.s)['completed'])
        return count

    def chapter(self):
        self.act('foundation-start')
        phases=sum(self.step(key) for key in f.STEPS)
        self.act('foundation-conclude')
        return phases

    def ready_partner(self):
        self.s['romance']['people']['mira']={'level':4,'mode':'open','deferred':False}
        for who in ('founder','mira'):g.set_character_assignment(self.s,who,'rest')

    def ritual(self):
        self.ready_partner()
        self.act('foundation-invite',characterId='mira')
        self.act('foundation-ritual-start')
        self.act('advance')
        self.assertTrue(f.active(self.s))

    def test_full_chapter_has_real_costs_evidence_room_and_reward_without_romance(self):
        lore=deepcopy(self.s['privateCastleLore']);funds=self.s['sharedFunds']
        self.assertEqual(self.chapter(),9)
        self.assertEqual(self.s['sharedFunds'],funds-24)
        self.assertEqual(self.s['materialInventory']['binding-thread'],4)
        self.assertEqual(self.s['materialInventory']['porous-clay'],4)
        self.assertEqual(self.s['materialInventory']['fireglass'],5)
        self.assertTrue(headquarters.ready(self.s,f.ROOM))
        self.assertTrue(f.view(self.s)['complete'])
        self.assertFalse(f.active(self.s))
        self.assertEqual(self.s['romance']['people'],{})
        self.assertEqual(self.s['characterDevelopment']['founder']['advancementAwards']['beneath-the-hearth']['points'],2)
        self.assertEqual(self.s['privateCastleLore'],lore)
        self.reject('foundation-conclude')

    def test_chapter_gate_order_method_and_reserves_are_enforced(self):
        self.s['firstRealTest']['completedOn']=None
        self.reject('foundation-start')
        self.s['firstRealTest']['completedOn']={'dayNumber':1,'phase':'morning'}
        self.reject('foundation-task',stepId='connections')
        self.act('foundation-start')
        self.reject('foundation-task',stepId='restoration')
        self.reject('foundation-task',stepId='connections',methodId='imaginary')
        self.step('connections');self.step('instructions')
        self.s['materialReserveTargets']['porous-clay']=6
        self.reject('foundation-task',stepId='restoration')
        self.assertFalse(headquarters.ready(self.s,f.ROOM))
        self.reject('hq-build',roomId=f.ROOM)

    def test_earlier_knowledge_saves_time_but_never_required(self):
        self.s['founderKnownPrinciples'].append('steady-hearth-wards')
        self.s['castleMystery']['discoveries']['founding-record']={'title':'Existing founding evidence','text':'Saved campaign evidence.'}
        self.act('foundation-start')
        self.assertEqual(self.step('connections','wards'),1)
        self.assertEqual(self.step('instructions','archive'),1)
        self.assertEqual(self.s['castleMystery']['discoveries']['founding-record']['text'],'Saved campaign evidence.')

    def test_restoration_pauses_resumes_cancels_and_refunds_once(self):
        self.act('foundation-start');self.step('connections');self.step('instructions')
        before=deepcopy(self.s)
        self.act('foundation-task',stepId='restoration');self.act('advance')
        self.act('assign-founder',assignment='rest');self.act('advance')
        self.assertEqual(f.saved(self.s)['job']['done'],1)
        self.act('foundation-resume');self.act('advance')
        self.assertEqual(f.saved(self.s)['job']['done'],2)
        self.act('foundation-cancel')
        self.assertEqual(self.s['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.s['materialInventory'],before['materialInventory'])
        self.reject('foundation-cancel')
        self.assertNotIn('restoration',f.saved(self.s)['completed'])

    def test_tests_can_be_completed_in_either_order(self):
        self.act('foundation-start')
        for key in ('connections','instructions','restoration'):self.step(key)
        self.step('distribution')
        self.reject('foundation-conclude')
        self.step('isolation');self.act('foundation-conclude')
        self.assertTrue(f.ready(self.s))

    def test_ritual_requires_adults_milestone_presence_rest_and_fresh_agreement(self):
        self.chapter()
        self.reject('foundation-invite',characterId='mira')
        self.ready_partner();self.s['romance']['people']['mira']['mode']='friendly'
        self.reject('foundation-invite',characterId='mira')
        self.s['romance']['people']['mira']['mode']='open'
        g.set_character_assignment(self.s,'mira','archive')
        self.reject('foundation-invite',characterId='mira')
        g.set_character_assignment(self.s,'mira','rest')
        self.s['people']['mira']['adultAgeYears']=17
        self.reject('foundation-invite',characterId='mira')
        self.s['people']['mira']['adultAgeYears']=22
        self.reject('foundation-ritual-start')
        self.act('foundation-invite',characterId='mira')
        self.act('foundation-decline')
        self.assertFalse(f.active(self.s));self.assertEqual(f.saved(self.s)['ritualCount'],0)

    def test_scheduling_uses_one_real_phase_and_exact_duration(self):
        self.chapter();self.ready_partner();before=deepcopy(self.s)
        self.act('foundation-invite',characterId='mira');self.act('foundation-ritual-start')
        self.assertEqual(f.stamp(self.s),f.stamp(before));self.assertFalse(f.active(self.s))
        self.act('advance')
        self.assertEqual(f.stamp(self.s),f.stamp(before)+1)
        self.assertEqual(f.bonus_view(self.s)['remainingPhases'],9)
        self.assertEqual(self.s['sharedFunds'],before['sharedFunds'])
        self.assertEqual(self.s['materialInventory'],before['materialInventory'])
        self.assertIn('fades to black',f.saved(self.s)['lastRitual']['response'])
        for expected in range(8,-1,-1):
            self.act('advance')
            self.assertEqual(f.bonus_view(self.s)['remainingPhases'],expected)
            self.assertEqual(f.active(self.s),expected>0)
        self.assertTrue(any('blessing has ended' in x for x in self.s['lastPhaseSummary']))

    def test_bonus_has_exact_fractional_gains_and_preserves_losses_caps_and_romance(self):
        self.chapter();self.ritual()
        row=relationships.saved(self.s)['bonds']['founder|mira'];start=row['trust']
        relationships.remember(self.s,'boosted',{'title':'Shared study','participants':['founder','mira']},'trust')
        self.assertEqual(row['trust'],round(start+1.2,1))
        relationships.remember(self.s,'loss',{'title':'Broken promise','participants':['founder','mira']},'trust',-1)
        self.assertEqual(row['trust'],round(start+.2,1))
        row['trust']=11.7
        relationships.remember(self.s,'cap',{'title':'Shared work','participants':['founder','mira']},'trust')
        self.assertEqual(row['trust'],12)
        self.assertEqual(relationships.saved(self.s)['events']['cap']['effects'][0]['change'],.3)
        self.assertEqual(self.s['romance']['people']['mira']['level'],4)

    def test_resident_bonus_adds_above_daily_allowance_without_double_multiplication(self):
        self.chapter();self.ritual()
        household.HouseholdChapterTests.member(self,'tamsin')
        self.s['bedroomAssignments']['tamsin']='garden-chamber'
        relationships.remember(self.s,'pair-one',{'title':'A shared conversation','participants':['founder','mira','tamsin']})
        row=resident_bonds.saved(self.s)['pairs']['mira|tamsin']
        self.assertEqual(row['score'],2.4)
        relationships.remember(self.s,'pair-two',{'title':'Another shared conversation','participants':['mira','tamsin']})
        self.assertEqual(row['score'],4.8)
        self.assertEqual(row['daily']['earned'],4)
        self.assertEqual(row['daily']['bonusEarned'],.8)
        resident_bonds.award(self.s,['mira','tamsin'],'over-cap','More work')
        self.assertEqual(row['score'],4.8)
        self.assertEqual(self.s['romance']['people'].get('tamsin'),None)

    def test_renewal_refreshes_nine_phases_without_stacking(self):
        self.chapter();self.ritual()
        for _ in range(4):self.act('advance')
        self.assertEqual(f.bonus_view(self.s)['remainingPhases'],5)
        self.ritual()
        self.assertEqual(f.bonus_view(self.s)['remainingPhases'],9)
        self.assertEqual(f.multiplier(self.s),1.2)
        self.assertEqual(f.saved(self.s)['ritualCount'],2)

    def test_arranged_ritual_pauses_when_consent_or_work_changes_and_can_cancel(self):
        self.chapter();self.ready_partner();self.act('foundation-invite',characterId='mira');self.act('foundation-ritual-start')
        self.act('pause-romance',characterId='mira');self.act('advance')
        self.assertFalse(f.active(self.s));self.assertTrue(f.saved(self.s)['ritual'])
        self.reject('foundation-ritual-resume')
        self.act('foundation-ritual-cancel')
        self.assertIsNone(f.saved(self.s)['ritual']);self.assertEqual(g.character_assignment(self.s,'mira'),'rest')

    def test_reading_profiles_and_reference_never_activates_or_spends_bonus(self):
        self.chapter();self.ritual();before=deepcopy(self.s)
        g.public_state(self.s);g.public_state(self.s)
        self.assertEqual(before,self.s)
        entry=next(x for x in magic_reference.view(self.s)['entries'] if x['id']=='foundation-intimacy')
        self.assertEqual(entry['destination'],f.VIEW);self.assertIn('9 phases',entry['status'])
        self.assertTrue(Path('static'+entry['art']).is_file())

    def test_migration_preserves_all_existing_fields_and_does_not_finish_chapter(self):
        self.s.pop('foundationChamber');self.s['schemaVersion']=68
        self.s['assetOverrides']['mira']='/user-assets/my-mira.webp'
        before=deepcopy(self.s);g.migrate_state(self.s)
        for key,value in before.items():
            if key!='schemaVersion':self.assertEqual(self.s[key],value,key)
        self.assertEqual(self.s['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertFalse(f.ready(self.s))
        after=deepcopy(self.s);g.migrate_state(self.s);self.assertEqual(after,self.s)

    def test_store_upgrade_backup_retry_and_active_blessing_reload(self):
        self.chapter();self.ready_partner()
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory)
            old=deepcopy(self.s);old.pop('foundationChamber');old['schemaVersion']=68
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
            store=GameStore(directory)
            self.assertTrue(Path(directory,f'campaign-before-schema-68-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
            store=GameStore(directory)
            for action in ({'type':'foundation-invite','characterId':'mira'},{'type':'foundation-ritual-start'},{'type':'advance'}):
                request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action}
                store.action(request);before=store.read();store.action(request);self.assertEqual(before,store.read())
            loaded=GameStore(directory).read()
            self.assertEqual(f.bonus_view(loaded)['remainingPhases'],9)
            self.assertEqual(f.saved(loaded)['ritualCount'],1)


    def test_dialogue_in_chamber_uses_room_name_and_keeps_private_ritual_memory_scoped(self):
        import dialogue
        self.chapter();self.ready_partner()
        household.HouseholdChapterTests.member(self,'tamsin')
        self.s['bedroomAssignments']['tamsin']='garden-chamber'
        self.act('foundation-invite',characterId='mira');self.act('foundation-ritual-start')
        def facts(who):
            return json.loads(dialogue.dialogue_context(self.s,'What have we been doing?',who)[0]['content'].split('Scene facts: ',1)[1])
        self.assertEqual(facts('mira')['room'],'Foundation ritual chamber')
        self.assertIsNone(facts('mira')['ownFoundationRitualMemory'])
        self.act('advance')
        self.assertIsNotNone(facts('mira')['ownFoundationRitualMemory'])
        self.assertIsNone(facts('tamsin')['ownFoundationRitualMemory'])
        self.assertTrue(facts('tamsin')['householdRelationshipBlessing']['active'])


if __name__=='__main__':unittest.main()
