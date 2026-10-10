from copy import deepcopy
import json
import unittest
from unittest.mock import patch
import game as g
import headquarters as h
import household_chapters as home
import household_chapter_content as content
import local_encounters as local
import outfit_progression as outfits
import progression
import resident_specialties as specialties
import summoning
import work_arrangements as arrangements

class HouseholdChapterTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def share(self,who,stage,choice='gentle'):self.act('share-personal-chapter',characterId=who,sceneId=f'{who}:{stage}',choice=choice)
    def activity(self,who,room='common-room',choice='quiet'):self.act('share-room-activity',characterId=who,sceneId=who+':'+room,choice=choice)
    def member(self,who):
        if who=='mira':return
        if who=='merrin':
            import chapel_spirit
            self.s['localEncounterCandidates'][who]=chapel_spirit.definition(self.s)
        if who in ('sabine',):
            import containment
            self.s['reviewedCandidates'][who]=deepcopy(containment.CASES[who]['candidate'])
        if who in local.PEOPLE:
            self.s['localEncounterCandidates'][who]=local.definition(self.s,who)
            summoning.initialize_person(self.s,who,summoned=False)
        elif who!='tamsin':summoning.initialize_person(self.s,who)
        self.s['additionalResidents'][who]['status']='resident'
        if who in self.s['residency']:self.s['residency'][who]['residencyStatus']='resident'
    def room(self,key):
        if key=='conservatory':self.s['restorationStatus']='complete'
        elif key in ('kitchen','washroom'):self.s['facilityProjects'][key]['status']='complete'
        elif key not in ('library','common-room'):self.s['headquarters']['rooms'][key]='complete'
    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(self.s,before)
    def test_all_fourteen_routes_complete_without_paid_rooms_or_time(self):
        for who in content.PROFILES:
            with self.subTest(who=who):
                self.s=g.new_campaign();self.member(who)
                untouched={k:deepcopy(self.s[k]) for k in ('sharedFunds','dayNumber','currentDayPhase','materialInventory','headquarters','researchProjects','founderAssignment','residentAssignment')}
                self.share(who,0)
                self.act('accept-outfit-invitation',characterId=who,tier='2',responseChoice='playful')
                self.share(who,1,'playful');self.share(who,2)
                self.act('accept-outfit-invitation',characterId=who,tier='3',responseChoice='warm')
                self.share(who,3,'playful')
                p=next(p for p in home.view(self.s)['people'] if p['id']==who)
                self.assertEqual(p['completed'],4);self.assertIsNone(p['nextInvitation'])
                self.assertEqual(p['personal'][1]['callback'],p['personal'][0]['memory']['response'])
                self.assertEqual({k:self.s[k] for k in untouched},untouched)
                self.assertIsNone(outfits.current(self.s,who))
                self.assertEqual(self.s['outfitProgression'][who]['invitations']['2']['choice'],'playful')
    def test_distinct_authored_content_and_valid_rooms(self):
        self.assertEqual(len(content.PROFILES),16)
        for field in ('relaxed','daring'):
            self.assertEqual(len({p[field] for p in content.PROFILES.values()}),16)
        scenes=[b for p in content.PROFILES.values() for b in p['beats']]
        self.assertEqual(len({b['opening'] for b in scenes}),64)
        self.assertEqual(len({b['title'] for b in scenes}),64)
        self.assertTrue(set(content.ACTIVITIES)<=set(h.ROOMS))
    def test_repeat_activity_preserves_first_choice_and_does_not_farm(self):
        self.activity('mira');first=deepcopy(self.s['householdChapters']['activities']['mira:common-room'])
        self.act('accept-outfit-invitation',characterId='mira',tier='2')
        for _ in range(4):self.activity('mira',choice='playful')
        row=self.s['householdChapters']['activities']['mira:common-room']
        self.assertEqual(row['choice'],first['choice']);self.assertEqual(row['sequence'],first['sequence'])
        self.assertEqual(row['lastShared']['choice'],'playful');self.assertEqual(row['visits'],5)
        self.assertEqual(len(outfits.memories(self.s,'mira')),1)
        self.reject('accept-outfit-invitation',characterId='mira',tier='3')
    def test_invalid_out_of_order_and_absent_actions_are_atomic(self):
        for kw in ({'sceneId':'mira:3','characterId':'mira','choice':'gentle'}, {'sceneId':'tamsin:0','characterId':'mira','choice':'gentle'}, {'sceneId':'mira:0','characterId':'mira','choice':'invented'}, {'sceneId':[],'characterId':[],'choice':[]}):
            self.reject('share-personal-chapter',**kw)
        self.reject('share-personal-chapter',characterId='sylva',sceneId='sylva:0',choice='gentle')
        self.reject('share-room-activity',characterId='mira',sceneId='mira:smithy',choice='quiet')
        with patch('game.character_at_castle',return_value=False):
            self.reject('share-personal-chapter',characterId='mira',sceneId='mira:0',choice='gentle')
        self.share('mira',0)
        self.reject('share-personal-chapter',characterId='mira',sceneId='mira:0',choice='playful')
        self.reject('accept-outfit-invitation',characterId='mira',tier='2',responseChoice=[])
    def test_every_pair_followup_requires_later_activity_and_keeps_choice(self):
        for pair in content.PAIRS:
            a,b,room=pair[:3]
            with self.subTest(pair=a+'+'+b):
                self.s=g.new_campaign();self.member(a);self.member(b);self.room(room)
                self.share(a,0);self.share(b,0);self.activity(a)
                base=a+'+'+b
                self.act('share-household-pair',sceneId=base+':0',choice='meaning')
                self.reject('share-household-pair',sceneId=base+':1',choice='method')
                self.activity(a) # revisiting counts for timing, never adds a new wardrobe memory
                second=next(r for r in home.pair_rows(self.s) if r['id']==base+':1')
                self.assertTrue(second['available']);self.assertEqual(second['callback'],self.s['householdChapters']['pairs'][base+':0']['response'])
                self.act('share-household-pair',sceneId=base+':1',choice='method')
    def test_all_specialist_installation_and_later_use_gates(self):
        for who,d in specialties.SPECIALTIES.items():
            with self.subTest(who=who):
                self.s=g.new_campaign();self.member(who);self.room(d['room'])
                self.reject('share-specialist-chapter',characterId=who,sceneId=who+':0',choice='craft')
                self.s['livingStories']['memories'][who+':0']={'response':'Remembered original story.'}
                self.act('share-specialist-chapter',characterId=who,sceneId=who+':0',choice='company')
                self.reject('share-specialist-chapter',characterId=who,sceneId=who+':1',choice='craft')
                self.s['headquarters']['stock']['specialty:'+who]=1
                self.activity(who,d['room'])
                self.act('share-specialist-chapter',characterId=who,sceneId=who+':1',choice='craft')
                self.reject('share-specialist-chapter',characterId=who,sceneId=who+':2',choice='company')
                self.activity(who,d['room']);self.act('share-specialist-chapter',characterId=who,sceneId=who+':2',choice='company')
    def test_old_completed_specialist_can_share_installation(self):
        self.member('tamsin');self.room('kitchen');self.s['headquarters']['stock']['specialty:tamsin']=1
        self.act('share-specialist-chapter',characterId='tamsin',sceneId='tamsin:1',choice='company')
    def test_migration_and_roundtrip_preserve_prior_content_and_new_choices(self):
        self.s['schemaVersion']=45;self.s.pop('householdChapters');self.s.pop('workArrangements')
        before=deepcopy(self.s);g.migrate_state(self.s)
        for key in before:
            if key!='schemaVersion':self.assertEqual(before[key],self.s[key],key)
        self.share('mira',0,'playful');self.activity('mira');self.activity('mira',choice='playful')
        self.act('save-work-arrangement',name='Quiet afternoon')
        self.assertEqual(g.migrate_state(json.loads(json.dumps(self.s))),self.s)
        before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
    def test_dialogue_remembers_only_shared_completed_choices(self):
        from dialogue import dialogue_context
        self.member('tamsin');self.share('mira',0,'playful');self.share('tamsin',0)
        self.act('accept-outfit-invitation',characterId='mira',tier='2',responseChoice='playful')
        facts=json.loads(dialogue_context(self.s,'What do you remember?','mira')[0]['content'].split('Scene facts: ',1)[1])
        self.assertEqual(facts['rememberedPersonalChapters'][0]['response'],content.PROFILES['mira']['beats'][0]['choices']['playful']['response'])
        self.assertEqual(len(facts['rememberedPersonalChapters']),1)
        self.assertEqual(facts['rememberedWardrobeInvitations']['2']['choice'],'playful')

    def test_fresh_solo_has_no_phantom_residents(self):
        s=g.new_campaign('fresh');self.assertEqual(home.view(s),{'people':[],'pairs':[]})

class WorkArrangementTests(unittest.TestCase):
    def setUp(self):self.s=g.new_campaign()
    def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
    def reject(self,kind,**kw):
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act(kind,**kw)
        self.assertEqual(self.s,before)
    def test_save_preview_restore_preserves_funding_progress_and_time(self):
        self.act('start-research');self.act('assign-resident',assignment='archive')
        self.act('save-work-arrangement',name='Research afternoon')
        self.act('assign-founder',assignment='commissions');self.act('assign-resident',assignment='rest')
        before=deepcopy(self.s);view=arrangements.view(self.s);self.assertEqual(before,self.s)
        self.assertEqual(len(view['plans'][0]['changes']),2)
        self.act('apply-work-arrangement',name='Research afternoon')
        self.assertEqual(self.s['founderAssignment'],'research');self.assertEqual(self.s['residentAssignment'],'archive')
        for key in ('researchCompletedPhases','sharedFunds','dayNumber','currentDayPhase','materialInventory'):self.assertEqual(self.s[key],before[key])
        self.reject('apply-work-arrangement',name='Research afternoon')
    def test_partial_failure_is_atomic_and_new_arrivals_untouched(self):
        self.s['workArrangements']['Invalid']={'founder':'commissions','mira':'crafting'}
        self.reject('apply-work-arrangement',name='Invalid')
        self.s['workArrangements']['Solo']={'founder':'commissions'}
        self.act('apply-work-arrangement',name='Solo');self.assertEqual(self.s['residentAssignment'],'rest')
        self.s['workArrangements']['Departed']={'founder':'rest','sylva':'rest'}
        self.reject('apply-work-arrangement',name='Departed')
    def test_away_duplicate_limit_name_and_delete_guards(self):
        with patch('game.character_at_castle',return_value=False):self.reject('save-work-arrangement',name='Away')
        for name in ('',[],None,'x'*41):self.reject('save-work-arrangement',name=name)
        for i in range(8):self.act('save-work-arrangement',name=str(i))
        self.reject('save-work-arrangement',name='0');self.reject('save-work-arrangement',name='Nine')
        self.act('delete-work-arrangement',name='0');self.act('save-work-arrangement',name='Replacement')
        self.reject('delete-work-arrangement',name='Unknown')
    def test_project_resume_previews_exact_assignment_change(self):
        self.act('start-research');self.act('assign-founder',assignment='commissions')
        before=deepcopy(self.s);v=progression.view(self.s);self.assertEqual(before,self.s)
        p=next(p for p in v['projects'] if p['id']=='hearth')
        self.assertEqual(p['assignmentImpact'][0]['before'],'commissions');self.assertEqual(p['assignmentImpact'][0]['after'],'research')
        self.act('resume-project',projectId='hearth');self.assertEqual(self.s['sharedFunds'],before['sharedFunds'])
    def test_lesson_resume_previews_both_people_and_preserves_reserved_work(self):
        g.learn_for_character(self.s,'mira','gentle-preservation')
        self.act('start-lesson',learnerId='founder',teacherId='mira',subjectKind='principle',targetId='gentle-preservation')
        self.act('assign-founder',assignment='commissions');self.act('assign-resident',assignment='rest')
        before=deepcopy(self.s);p=next(p for p in progression.view(self.s)['projects'] if p['id']=='training:founder')
        self.assertEqual({r['personId'] for r in p['assignmentImpact']},{'founder','mira'})
        self.assertEqual(before,self.s);self.act('resume-project',projectId='training:founder')
        self.assertEqual(self.s['founderAssignment'],'training');self.assertEqual(self.s['residentAssignment'],'teaching')
        self.assertEqual(self.s['trainingProjects'],before['trainingProjects'])

    def test_housing_resume_selects_the_requested_funded_room(self):
        room='garden-chamber';self.s['housingRooms'][room]['status']='in-progress'
        self.act('resume-project',projectId='housing:'+room)
        self.assertEqual(self.s['activeHousingRoomId'],room);self.assertEqual(self.s['founderAssignment'],'housing')

if __name__=='__main__':unittest.main()
