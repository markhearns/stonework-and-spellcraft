from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest
import game as g
import house_shape as h
import headquarters
import guidance
import progression
import room_life
import work_arrangements
import castle_mystery
from server import GameStore
import test_first_hearth as first_chapter


class HouseShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t=first_chapter.FirstHearthTests();t.setUp();t.play();cls.beginning=deepcopy(t.s)

    def setUp(self):self.s=deepcopy(self.beginning)
    def act(self,kind,**kw):g.apply_action(self.s,{'type':kind,**kw})
    def advance(self,n=1):
        for _ in range(n):self.act('advance')
    def money(self,n):
        if self.s['sharedFunds']>=n:return
        self.act('assign-founder',assignment='commissions')
        while self.s['sharedFunds']<n:self.advance()
        self.act('assign-founder',assignment='rest')
    def buy_for(self,inputs):
        for key,n in inputs.items():
            while self.s['materialInventory'][key]-self.s['materialReserveTargets'][key]<n:
                self.money(g.MATERIALS[key]['price']);self.act('buy-material',materialId=key)
    def recruit(self):
        import summoning
        if self.s['localEncounters']['koharu']['status']!='introduced':
            self.act('start-local-visit',encounterId='koharu');self.advance()
        contact=next(k for k,c in self.s['summoningContacts'].items() if c['personId']=='koharu')
        for topic in summoning.candidate_catalogue(self.s)['koharu']['topics']:self.act('summoning-talk',contactId=contact,topic=topic)
        self.act('summoning-invite',contactId=contact,roomId='bedchamber');self.advance()
        self.act('summoning-ask-stay',contactId=contact)
        self.act('summoning-household-decision',contactId=contact,decision='invite-to-stay')
        self.act('assign-character',characterId='koharu',assignment='rest')

    def run_chapter(self,key,design,shared=False,stop=None):
        if not h.record(self.s,key):self.act('shape-start',pathId=key)
        phases=0
        for _ in range(180):
            before=deepcopy(self.s);v=h.view(self.s);self.assertEqual(before,self.s)
            r=h.record(self.s,key);stage=v['stage']
            if stage==stop or stage=='complete':break
            if self.s['expedition']:
                p=self.s['expedition'];status=p['stage']
                if status=='awaiting-choice':self.act('choose-expedition-approach',approach=h.PATHS[key]['approach'])
                elif status=='ready-to-return':self.act('return-expedition')
                else:self.advance();phases+=1
            elif stage=='proposal':self.act('shape-purpose',choice='welcome')
            elif stage=='design':self.act('shape-design',choice=design)
            elif stage=='planning':
                self.money(h.PATHS[key]['cost']);self.buy_for(h.PATHS[key]['inputs']);self.money(h.PATHS[key]['cost'])
                self.act('assign-founder',assignment='rest')
                if shared and 'koharu' not in r['workers']:self.act('shape-include',characterId='koharu')
                self.act('shape-fund')
            elif stage=='construction':self.advance();phases+=1
            elif stage=='gathering':self.act('shape-gather',choice='credit')
            elif stage=='ending':self.act('shape-finish')
            else:
                n=v['next'];self.assertIsNotNone(n,v)
                self.assertFalse(n.get('blockers'),n)
                if n['id']=='field':self.act('start-expedition',siteId=h.PATHS[key]['site'],carryLantern=bool(self.s['craftedArtifacts'].get('warming-lantern')))
                else:
                    self.assertIsNotNone(n['action'],n);g.apply_action(self.s,n['action']);phases+=int(n['action']['type']=='advance')
            self.s=g.migrate_state(json.loads(json.dumps(self.s)))
        else:self.fail(repr(h.view(self.s)))
        if not stop:
            self.assertTrue(r['finished']);self.assertIsNotNone(r['used']);self.assertFalse(self.s['testing']['used'])
            self.assertEqual(self.s['privateCastleLore'],self.beginning['privateCastleLore'])
            self.assertEqual(self.s['castleMystery']['discoveries']['archive-leaf']['text'],self.s['privateCastleLore']['evidence']['archive-leaf'])
        return phases

    def test_all_six_designs_complete_using_ordinary_actions_and_reload(self):
        for key,d in h.PATHS.items():
            for design in d['designs']:
                with self.subTest(path=key,design=design):
                    self.s=deepcopy(self.beginning);self.run_chapter(key,design)
                    self.assertEqual(sum(h.record(self.s,key)['project']['contributions'].values()),6)
                    self.assertTrue(h.room_improvements(self.s,d['room']))
                    if key=='craftsmanship':self.assertEqual(self.s['neighbourRequestProgress']['brook-lamps']['status'],'delivered')

    def test_agreed_resident_and_solo_progress_are_real(self):
        self.recruit();self.run_chapter('scholarship','table',shared=True)
        r=h.record(self.s,'scholarship')
        self.assertEqual(r['project']['contributions'],{'founder':3,'koharu':3})
        self.assertEqual(r['project']['names']['koharu'],'Koharu')
        self.assertTrue(any('koharu' in m['participants'] for m in h.context(self.s,'koharu')))

    def test_cancel_refunds_exact_inputs_once_and_retains_other_work(self):
        self.run_chapter('cultivation','nursery',stop='construction');self.advance(2)
        r=h.record(self.s,'cultivation');p=deepcopy(r['project']);before=deepcopy(self.s)
        self.act('shape-cancel')
        self.assertEqual(self.s['sharedFunds'],before['sharedFunds']+p['crowns'])
        for k,n in p['inputs'].items():self.assertEqual(self.s['materialInventory'][k],before['materialInventory'][k]+n)
        self.assertEqual(r['design'],'nursery');self.assertEqual(h.bonus(self.s,'ivy'),0)
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act('shape-cancel')
        self.assertEqual(before,self.s)
        self.act('shape-fund');self.assertEqual(r['project']['done'],0)

    def test_travel_and_reassignment_only_pause_the_affected_contributor(self):
        self.recruit();self.run_chapter('scholarship','table',shared=True,stop='construction')
        self.act('start-expedition',siteId='old-waterworks',carryLantern=True)
        before=deepcopy(self.s);preview=guidance.preview(self.s);self.assertEqual(before,self.s)
        p=next(x for x in preview['projects'] if x['id']=='house-shape');self.assertEqual(p['progress'],1)
        self.advance();self.assertEqual(h.record(self.s,'scholarship')['project']['contributions'],{'koharu':1})
        self.act('return-expedition');self.advance()
        self.act('shape-resume',characterId='founder');self.advance()
        r=h.record(self.s,'scholarship');self.assertEqual(r['project']['contributions'],{'koharu':3,'founder':1})
        self.act('shape-pause');done=r['project']['done'];self.advance();self.assertEqual(r['project']['done'],done)
        self.act('shape-resume',characterId='koharu');self.assertEqual(room_life.location(self.s,'koharu'),'library')
        self.advance(2);self.assertEqual(r['project']['status'],'complete')

    def test_reserves_invalid_choices_and_out_of_order_actions_are_atomic(self):
        self.act('shape-start',pathId='scholarship')
        for action in ({'type':'shape-design','choice':'index'},{'type':'shape-fund'},{'type':'shape-finish'},
                       {'type':'shape-purpose','choice':[]},{'type':'shape-include','characterId':'unknown'},
                       {'type':'shape-visibility','enabled':'yes'}):
            before=deepcopy(self.s)
            with self.assertRaises(g.RuleError):g.apply_action(self.s,action)
            self.assertEqual(before,self.s)
        self.run_chapter('scholarship','index',stop='planning')
        self.money(100)
        for k,n in h.PATHS['scholarship']['inputs'].items():self.s['materialReserveTargets'][k]=self.s['materialInventory'][k]
        before=deepcopy(self.s)
        with self.assertRaises(g.RuleError):self.act('shape-fund')
        self.assertEqual(before,self.s)

    def test_completed_bonuses_only_affect_the_declared_work(self):
        self.run_chapter('cultivation','nursery')
        self.assertEqual(h.bonus(self.s,'ivy'),1);self.assertEqual(h.bonus(self.s,'copy'),0)
        self.act('garden-production',choice='silver-ivy');self.act('assign-gardener',characterId='founder')
        ordinary=deepcopy(self.s);ordinary.pop('houseShape')
        self.assertEqual(g.garden_harvest(self.s)['amount'],g.garden_harvest(ordinary)['amount']+1)
        self.act('assign-founder',assignment='rest');self.assertEqual(g.garden_harvest(self.s)['amount'],0)
        self.s['utilityArtifactPlacements']['root-tender']=True
        self.assertEqual(g.garden_harvest(self.s)['amount'],1,'The staffed bonus must not affect automation')

    def test_arrangements_departure_and_no_double_work(self):
        import party_journeys
        self.recruit();self.run_chapter('craftsmanship','production',shared=True,stop='construction')
        self.act('save-work-arrangement',name='Shared fitting')
        self.assertEqual(next(r for r in party_journeys.departure(self.s) if r['id']=='koharu')['commitments'][0]['name'],'A working commission bench')
        self.act('shape-pause');self.act('apply-work-arrangement',name='Shared fitting')
        self.assertEqual(set(h.eligible(self.s)),{'founder','koharu'})
        self.act('hq-agree-work',workerId='koharu',enabled=True)
        self.money(20);self.act('hq-build',workerId='koharu',roomId='chapel')
        self.act('shape-resume',characterId='founder')
        prior=deepcopy(h.record(self.s,'craftsmanship')['project']['contributions'])
        self.advance()
        contributions=h.record(self.s,'craftsmanship')['project']['contributions']
        self.assertEqual(contributions.get('founder',0),prior.get('founder',0)+1)
        self.assertEqual(contributions.get('koharu',0),prior.get('koharu',0))
        self.assertEqual(headquarters.project_for(self.s,'koharu')['done'],1)

    def test_later_paths_remain_available_and_do_not_remove_completed_benefits(self):
        self.run_chapter('scholarship','table');self.run_chapter('cultivation','kitchen')
        self.assertEqual(h.bonus(self.s,'copy'),2);self.assertEqual(h.bonus(self.s,'garden-sales'),2)
        self.assertTrue(h.record(self.s,'scholarship')['finished'])

    def test_legacy_reads_and_hidden_history_stay_unchanged(self):
        before=deepcopy(self.s);v=h.view(self.s);g.migrate_state(self.s)
        self.assertEqual(before,self.s);self.assertNotIn('houseShape',self.s)
        text=json.dumps(v);self.assertNotIn(self.s['privateCastleLore']['evidence']['archive-leaf'],text)
        self.assertNotIn(h.PATHS['cultivation']['ending'],text)
        self.assertNotIn(h.PATHS['scholarship']['designs']['table']['response'],text)
        demo=g.new_campaign();demo['livingWingCompletedOn']={'dayNumber':1};demo['castleMystery']['discoveries']['hearth-margin']={}
        self.assertTrue(h.available(demo));demo['miraArchiveProject']['status']='ready-to-bind';self.assertTrue(h.archive_ready(demo))

    def test_established_archive_with_all_studies_complete_has_honest_exit(self):
        self.run_chapter('scholarship','index',stop='gathering')
        for p in self.s['researchProjects'].values():p['status']='complete'
        self.act('shape-gather',choice='enjoy')
        r=h.record(self.s,'scholarship');self.assertIsNone(r['used'])
        n=h.view(self.s)['next'];self.assertEqual(n['action']['type'],'shape-acknowledge-mastery')
        before=deepcopy(self.s)
        g.apply_action(self.s,n['action'])
        for key in ('sharedFunds','materialInventory','dayNumber','currentDayPhase','characterDevelopment'):self.assertEqual(self.s[key],before[key])
        self.assertIsNone(r['used']);self.assertTrue(r['masteryAcknowledged'])
        self.assertEqual(h.view(self.s)['stage'],'evidence')

    def test_save_retry_and_custom_art_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            store=GameStore(folder)
            with store.connect() as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
            art=Path(folder,'assets','custom.webp');art.parent.mkdir(exist_ok=True);art.write_bytes(b'custom-art')
            action={'expectedRevision':self.s['revision'],'requestId':'chapter-two-start','action':{'type':'shape-start','pathId':'cultivation'}}
            once=store.action(action);self.assertEqual(store.action(action),once)
            self.assertEqual(GameStore(folder).read(),once);self.assertEqual(art.read_bytes(),b'custom-art')

if __name__=='__main__':unittest.main()
