"""Optional pair milestones, actual cooperation, transactional saves and read-only views."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
import uuid

import game as g
import resident_bonds as b
import resident_friendships as f
import resident_friendship_content as content
import foundation_chamber as chamber
import provisions
import guidance
import field_patrols
import test_household_chapters as household
from server import GameStore


class FriendshipTests(unittest.TestCase):
    def setUp(self):
        self.s=g.new_campaign()
        field_patrols.initialize(self.s)
        self.member('tamsin');self.member('iona')
        self.s['sharedFunds']=100
        self.s['provisions']['stock']=500
        self.s['currentDayPhase']='morning'
        for who in g.household_members(self.s):g.set_character_assignment(self.s,who,'rest')

    def member(self,who):
        household.HouseholdChapterTests.member(self,who)
        self.s['housingRooms']['garden-chamber']['status']='complete'
        self.s['bedroomAssignments'][who]='garden-chamber'

    def act(self,kind,**kw):
        return g.apply_action(self.s,dict(type=kind,**kw))

    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(before,self.s)

    def points(self,key='mira|tamsin',value=25):
        b.saved(self.s)['pairs'].setdefault(key,b.empty_pair(*key.split('|')))['score']=value

    def meeting(self,key='mira|tamsin',choice=None):
        self.act('friendship-share',pairId=key,stage='meeting',**({'choice':choice} if choice else {}))

    def project(self,key='mira|tamsin'):
        self.points(key);self.meeting(key, None if key in content.PROJECTS else 'game')
        room=f.definition(self.s,key)['room'];household.HouseholdChapterTests.room(self,room)
        for who in key.split('|'):g.set_character_assignment(self.s,who,'rest')
        self.act('friendship-arrange',pairId=key,stage='project');self.act('advance')

    def test_thresholds_no_unearned_history_and_reads_are_pure(self):
        before=deepcopy(self.s);self.assertFalse(f.view(self.s)['pairs']);self.assertEqual(before,self.s)
        self.points(value=100)
        before=deepcopy(self.s);view=f.view(self.s);g.public_state(self.s)
        self.assertEqual(before,self.s)
        row=view['pairs'][0];self.assertEqual(row['stage'],'meeting');self.assertEqual(row['memories'],{})
        self.assertNotIn('glass drops',json.dumps(view));self.assertEqual(row['cooperation'],0)
        self.reject('friendship-arrange',pairId='mira|tamsin',stage='project')

    def test_meeting_is_free_and_only_resident_pair_gains(self):
        self.points(value=10);before=deepcopy(self.s)
        self.meeting()
        for key in ('dayNumber','currentDayPhase','sharedFunds','founderAssignment','residentAssignment','relationships','romance'):
            self.assertEqual(before[key],self.s[key],key)
        self.assertEqual(f.score(self.s,'mira|tamsin'),12)
        self.assertEqual(f.score(self.s,'iona|mira'),0)
        self.reject('friendship-share',pairId='mira|tamsin',stage='meeting')

    def test_names_custom_pairs_and_all_general_activities(self):
        for choice in content.HABITS:
            self.setUp();self.points('iona|tamsin',100)
            self.meeting('iona|tamsin',choice)
            self.assertEqual(f.record(self.s,'iona|tamsin')['habit'],choice)
            self.act('friendship-arrange',pairId='iona|tamsin',stage='project');self.act('advance')
            self.assertEqual(f.record(self.s,'iona|tamsin')['keepsake']['name'],content.HABITS[choice]['keepsake'])
            self.act('friendship-arrange',pairId='iona|tamsin',stage='visit');self.act('advance')
            self.act('friendship-share',pairId='iona|tamsin',stage='tradition')
            memories=f.record(self.s,'iona|tamsin')['memories']
            self.assertEqual(len(memories),4)
            self.assertNotEqual(memories['meeting']['lines'],memories['visit']['lines'])
        self.s['additionalResidents']['custom-person']={'status':'resident'}
        self.s['people']['custom-person']={'name':'Aster','adultAgeYears':23,'role':'Visiting maker'}
        self.points('custom-person|mira',10)
        self.meeting('custom-person|mira','reading')
        self.assertIn('meeting',f.record(self.s,'custom-person|mira')['memories'])

    def test_all_authored_pairs_deliver_four_distinct_memories_and_keepsakes(self):
        for key,d in content.PROJECTS.items():
            with self.subTest(pair=key):
                self.setUp()
                for who in key.split('|'):self.member(who);g.set_character_assignment(self.s,who,'rest')
                household.HouseholdChapterTests.room(self,d['room'])
                self.points(key,100);self.meeting(key)
                self.act('friendship-arrange',pairId=key,stage='project');self.act('advance')
                self.act('friendship-arrange',pairId=key,stage='visit');self.act('advance')
                self.act('friendship-share',pairId=key,stage='tradition')
                r=f.record(self.s,key)
                self.assertEqual(len(r['memories']),4)
                self.assertEqual(r['keepsake']['room'],d.get('displayRoom',d['room']))
                self.assertEqual(len({json.dumps(m['lines']) for m in r['memories'].values()}),4)
                self.assertIsNone(f.next_stage(self.s,key))

    def test_project_requires_room_funds_rest_and_two_current_residents(self):
        self.member('zahra');self.member('neris');key='neris|zahra';self.points(key);self.meeting(key)
        self.reject('friendship-arrange',pairId=key,stage='project')
        household.HouseholdChapterTests.room(self,'workshop')
        self.s['sharedFunds']=3;self.reject('friendship-arrange',pairId=key,stage='project')
        self.s['sharedFunds']=20;g.set_character_assignment(self.s,'zahra','commissions')
        self.reject('friendship-arrange',pairId=key,stage='project')
        for who in key.split('|'):g.set_character_assignment(self.s,who,'rest')
        self.act('friendship-arrange',pairId=key,stage='project');self.assertEqual(self.s['sharedFunds'],16)
        self.assertIsNone(f.record(self.s,key)['keepsake'])
        self.reject('friendship-arrange',pairId=key,stage='project')
        self.reject('friendship-share',pairId='founder|mira',stage='meeting')
        self.reject('friendship-share',pairId='mira|mira',stage='meeting')
        self.reject('friendship-share',pairId='absent|mira',stage='meeting')

    def test_pause_resume_cancel_and_refund_are_exact(self):
        self.points();self.meeting();self.act('friendship-arrange',pairId='mira|tamsin',stage='project')
        self.act('assign-character',characterId='tamsin',assignment='rest')
        self.act('advance');self.assertIsNotNone(f.saved(self.s)['job']);self.assertIsNone(f.record(self.s,'mira|tamsin')['keepsake'])
        self.act('friendship-resume');self.act('friendship-cancel')
        self.assertEqual(self.s['sharedFunds'],100)
        self.assertEqual(g.character_assignment(self.s,'mira'),'rest')
        self.assertEqual(g.character_assignment(self.s,'tamsin'),'rest')
        self.reject('friendship-cancel')
        self.act('friendship-arrange',pairId='mira|tamsin',stage='project');self.act('advance')
        self.assertIsNotNone(f.record(self.s,'mira|tamsin')['keepsake'])
        self.reject('friendship-arrange',pairId='mira|tamsin',stage='project')

    def test_resume_does_not_silently_replace_another_task(self):
        self.points();self.meeting();self.act('friendship-arrange',pairId='mira|tamsin',stage='project')
        g.set_character_assignment(self.s,'tamsin','commissions')
        self.reject('friendship-resume')
        self.act('friendship-cancel')
        self.assertEqual(g.character_assignment(self.s,'tamsin'),'commissions')

    def test_deferred_invitation_survives_time_and_cannot_be_completed(self):
        self.points(value=10)
        self.act('friendship-defer',pairId='mira|tamsin',stage='meeting')
        for _ in range(4):self.act('advance')
        self.assertTrue(f.view(self.s)['pairs'][0]['deferred'])
        self.reject('friendship-share',pairId='mira|tamsin',stage='meeting')
        self.act('friendship-restore',pairId='mira|tamsin',stage='meeting');self.meeting()

    def test_away_or_departed_participant_pauses_and_can_cancel_without_loss(self):
        self.points();self.meeting();self.act('friendship-arrange',pairId='mira|tamsin',stage='project')
        self.s['additionalResidents']['tamsin']['status']='away'
        self.assertTrue(f.job_blockers(self.s))
        summary=[];f.resolve(self.s,summary);self.assertEqual(summary,[])
        self.reject('friendship-resume');self.act('friendship-cancel');self.assertEqual(self.s['sharedFunds'],100)
        self.assertIn('meeting',f.record(self.s,'mira|tamsin')['memories'])

    def test_blessing_applies_once_to_milestone_and_respects_daily_cap(self):
        self.points(value=25)
        self.s['foundationChamber']['blessing']={'startsAt':chamber.stamp(self.s),'expiresAt':chamber.stamp(self.s)+9,'announcedEnd':False}
        self.meeting();self.assertEqual(f.score(self.s,'mira|tamsin'),27.4)
        self.act('friendship-arrange',pairId='mira|tamsin',stage='project');self.act('advance')
        self.assertEqual(f.score(self.s,'mira|tamsin'),29.8)
        self.assertEqual(f.record(self.s,'mira|tamsin')['memories']['project']['gain'],2.4)

    def test_cooperation_needs_keepsake_matching_work_home_and_active_research(self):
        self.points(value=100)
        for w in ('mira','tamsin'):g.set_character_assignment(self.s,w,'archive')
        self.assertEqual(f.bonus(self.s,'archive'),0)
        for w in ('mira','tamsin'):g.set_character_assignment(self.s,w,'rest')
        self.project()
        for w in ('mira','tamsin'):g.set_character_assignment(self.s,w,'archive')
        self.assertEqual(f.bonus(self.s,'archive'),0)
        self.act('start-research');self.assertEqual(f.bonus(self.s,'archive'),1)
        self.points(value=70);self.assertEqual(f.bonus(self.s,'archive'),2)
        g.set_character_assignment(self.s,'tamsin','rest');self.assertEqual(f.bonus(self.s,'archive'),0)
        g.set_character_assignment(self.s,'tamsin','archive')
        self.s['expedition']={'siteId':'old-waterworks','stage':'ready-to-return','partyIds':['founder','mira']}
        self.assertEqual(f.bonus(self.s,'archive'),0)

    def test_research_forecast_and_actual_work_include_one_capped_bonus(self):
        self.project();self.act('start-research');self.s['researchRequiredPhases']=30
        for who in ('mira','tamsin'):g.set_character_assignment(self.s,who,'archive')
        expected=g.research_work(self.s)
        before=self.s['researchCompletedPhases'];self.act('advance')
        self.assertEqual(self.s['researchCompletedPhases']-before,expected)
        self.s['researchCompletedPhases']=29;self.act('advance')
        self.assertEqual(self.s['researchCompletedPhases'],30)

    def test_gathering_bonus_is_once_per_task_not_per_resident_or_pair(self):
        self.project();self.project('iona|tamsin')
        self.points('mira|tamsin',70)
        for who in ('mira','tamsin','iona'):g.set_character_assignment(self.s,who,'forage')
        expected=sum(provisions.yield_for(self.s,w,'forage') for w in ('mira','tamsin','iona'))+2
        self.s['currentDayPhase']='morning';before=self.s['provisions']['stock'];self.act('advance')
        self.assertEqual(self.s['provisions']['stock']-before,expected)
        self.assertEqual(sum('additional provisions' in line for line in self.s['lastPhaseSummary']),1)
        g.set_character_assignment(self.s,'tamsin','hunt');self.assertEqual(f.bonus(self.s,'forage'),0)

    def test_garden_requires_actual_two_workers_and_selected_output(self):
        self.project();self.s['restorationStatus']='complete'
        for choice in ('silver-ivy','surplus-sales','provisions'):
            self.s['gardenProductionChoice']=choice
            for w in ('mira','tamsin'):g.set_character_assignment(self.s,w,'garden')
            enhanced=g.garden_harvest(self.s)
            g.set_character_assignment(self.s,'tamsin','rest');base=g.garden_harvest(self.s)
            self.assertEqual(enhanced['amount'],base['amount']+1)
            self.assertEqual(enhanced['cooperation'],1)

    def test_guidance_predicts_shared_completion_without_mutating_state(self):
        self.points();self.meeting();self.act('friendship-arrange',pairId='mira|tamsin',stage='project')
        before=deepcopy(self.s);preview=guidance.preview(self.s)
        self.assertEqual(before,self.s)
        row=next(r for r in preview['projects'] if r['id']=='resident-friendship')
        self.assertTrue(row['completes']);self.assertEqual(row['participants'],['mira','tamsin'])

    def test_schema_migration_preserves_bonds_blessing_art_and_existing_memories(self):
        self.points(value=100)
        self.s['assetOverrides']['mira']='/user-assets/owned.png'
        self.s['foundationChamber']['ritualCount']=3
        old=deepcopy(self.s);old.pop('residentFriendshipMilestones');old['schemaVersion']=69
        before=deepcopy(old);g.migrate_state(old)
        for k in before:
            if k!='schemaVersion':self.assertEqual(before[k],old[k],k)
        self.assertEqual(old['residentFriendshipMilestones'],f.EMPTY)
        self.assertEqual(old['schemaVersion'],g.CURRENT_SCHEMA_VERSION)

    def test_catalogue_and_living_index_research_receive_actual_capped_cooperation(self):
        self.project()
        self.s['researchStatus']='complete';key='root-rhythms'
        self.s['activeResearchId']=key
        project=self.s['researchProjects'][key];project.update(status='in-progress',completedWorkPhases=0,contributors=[])
        for who in ('mira','tamsin'):g.set_character_assignment(self.s,who,'archive')
        g.set_character_assignment(self.s,'founder','rest')
        base=sum(g.work_contribution(self.s,w,'archive-focus') for w in ('mira','tamsin'))
        self.assertLess(base,g.RESEARCH_CATALOG[key]['requiredWorkPhases'])
        summary=[];g.resolve_catalog_research(self.s,summary)
        self.assertEqual(project['completedWorkPhases'],base+1)
        self.assertTrue(any('resident cooperation' in line for line in summary))
        self.s['activeResearchId']=None
        self.s['miraArchiveProject'].update(status='in-progress',completedWorkPhases=0,requiredWorkPhases=20,contributors=[])
        for who in ('mira','tamsin'):g.set_character_assignment(self.s,who,'archive-project')
        expected=g.archive_project_work(self.s);summary=[];g.resolve_development(self.s,summary)
        self.assertEqual(self.s['miraArchiveProject']['completedWorkPhases'],expected)
        self.assertEqual(expected,base+1)

    def test_conversation_context_knows_only_own_completed_friendships(self):
        import dialogue
        self.project()
        before=deepcopy(self.s)
        self.assertEqual(f.context(self.s,'iona'),[])
        self.assertEqual(len(f.context(self.s,'mira')[0]['memories']),2)
        f.context(self.s,'mira')[0]['memories'].clear();self.assertEqual(self.s,before)
        self.points('iona|tamsin',100)
        visible=json.loads(dialogue.dialogue_context(self.s,'What did you make?','mira')[0]['content'].split('Scene facts: ',1)[1])
        self.assertEqual(len(visible['rememberedResidentFriendships']),1)
        self.assertNotIn('visit',visible['rememberedResidentFriendships'][0]['memories'])

    def test_store_backup_request_retries_and_reload_preserve_keepsake(self):
        self.points(value=25)
        with tempfile.TemporaryDirectory() as directory:
            store=GameStore(directory);old=deepcopy(self.s);old.pop('residentFriendshipMilestones');old['schemaVersion']=69
            with sqlite3.connect(store.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
            store=GameStore(directory)
            self.assertTrue(Path(directory,f'campaign-before-schema-69-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
            for action in ({'type':'friendship-share','pairId':'mira|tamsin','stage':'meeting'},
                           {'type':'friendship-arrange','pairId':'mira|tamsin','stage':'project'},{'type':'advance'}):
                request={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':action}
                store.action(request);before=store.read();store.action(request);self.assertEqual(before,store.read())
            loaded=GameStore(directory).read()
            self.assertEqual(loaded['sharedFunds'],96)
            self.assertIsNotNone(f.record(loaded,'mira|tamsin')['keepsake'])
            self.assertEqual(len(f.record(loaded,'mira|tamsin')['memories']),2)


if __name__=='__main__':unittest.main()
