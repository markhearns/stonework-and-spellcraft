"""Behavioral tests for roles, exact previews, physical signature history and homecoming."""
from copy import deepcopy
import unittest,json
import test_field_patrols as old
import game as g,field_patrols as p,patrol_tactics as tactics,field_magic as f,armoury as a,personal_paths as paths,signature_growth as growth,patrol_homecoming as home

class RefinementTests(unittest.TestCase):
 def setUp(self):
  self.t=old.FieldPatrolTests();self.t.setUp();self.t.member('rhess');self.t.member('elowen');self.t.equip('founder');self.t.equip('rhess');self.t.equip('elowen');self.t.s['sharedFunds']=100;self.t.s['bedroomAssignments'].update({'rhess':'bedchamber','elowen':'bedchamber'})
  self.t.s['headquarters']['rooms'].update({'enchanting-room':'complete','training-yard':'complete'})
 @property
 def s(self):return self.t.s
 def act(self,*args,**kw):return self.t.act(*args,**kw)
 def prep(self,w,*keys):
  self.s.setdefault('personalPaths',{})[w]={'learned':list(keys),'techniques':list(keys),'passives':[]}
 def begin(self,key='bandit',party=None):
  self.t.depart(party or ['founder','rhess','elowen']);self.t.enemy(key);self.act('advance')
 def row(self,key):return next(x for x in p.choices(self.s) if x['id']==key)
 def sig(self,w='founder',types=None):
  it=next(i for i in a.state(self.s)['items'].values() if i['ownerId']==w and i['definitionId']=='steel-sword')
  a.state(self.s)['signatures'][w]={'itemId':it['id'],'fitted':True,'proved':True,'completedOn':{'day':1,'phase':'morning'},'replacements':[]};it['signatureOwner']=w;it['locked']=True
  if types is not None:it['fieldHistory']={'ownerId':w,'enemyTypes':types,'returns':[]}
  return it['id']
 def test_intent_stable_across_browsing_waiting_and_reload(self):
  self.begin();first=tactics.intent(self.s,p.saved(self.s)['active']);self.assertEqual(first['target'],'founder')
  for _ in range(2):
   before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s);self.act('advance');self.assertEqual(first,tactics.intent(self.s,p.saved(self.s)['active']))
 def test_guard_only_protects_actor(self):
  self.begin();a1=self.row('founder:guard')['preview'];a2=self.row('rhess:guard')['preview'];self.assertEqual(a2['target'],'founder');self.assertGreater(a2['injury'],a1['injury'])
 def test_protector_takes_the_named_attack(self):
  self.prep('rhess','spear-watch');self.begin();row=self.row('rhess:spear-watch');q=row['preview'];self.assertTrue(q['intercepted']);self.assertEqual(q['target'],'rhess');self.assertGreater(q['protectedDamage'],0)
  self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),q['healthAfter']['founder']);self.assertEqual(f.vitality(self.s,'rhess'),q['healthAfter']['rhess']);self.assertEqual(p.saved(self.s)['active']['contributions']['rhess']['protected'],q['protectedDamage'])
 def test_control_reduces_attack_and_opens_only_next_damage(self):
  self.prep('founder','scholar-unbinding');self.sig();self.begin();row=self.row('founder:scholar-unbinding');self.assertEqual(row['preview']['attack'],1)
  self.act('watch-method',methodId=row['id']);self.act('advance');self.assertTrue(p.saved(self.s)['active']['opening']);nextrow=self.row('rhess:strike');self.assertGreater(nextrow['preview']['damage'],nextrow['damage']);self.act('watch-method',methodId=nextrow['id']);self.act('advance');self.assertFalse(p.saved(self.s)['active']['opening'])
 def test_healing_happens_before_retaliation(self):
  self.prep('elowen','elowen-dressing');self.begin();f.initialize(self.s)['vitality']['founder']=1;row=self.row('elowen:elowen-dressing');self.assertEqual(row['preview']['healing'][0],{'who':'founder','amount':1});self.assertEqual(row['preview']['healthAfter']['founder'],1)
  self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),1)
 def test_lethal_action_has_no_retaliation(self):
  self.begin();p.saved(self.s)['active']['hp']=1;q=self.row('rhess:strike')['preview'];self.assertTrue(q['cancelled']);self.assertEqual(q['injury'],0);self.act('watch-method',methodId='rhess:strike');self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),6)
 def test_preview_matches_resolution_for_every_legal_action(self):
  self.prep('rhess','spear-watch','banked-flame');self.prep('elowen','elowen-dressing');self.begin('griffin');f.initialize(self.s)['vitality']['founder']=3;start=deepcopy(self.s)
  for row in p.choices(self.s):
   if row['blockers']:continue
   with self.subTest(action=row['id']):
    self.t.s=deepcopy(start);q=row['preview'];self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual({w:f.vitality(self.s,w) for w in start['fieldPatrols']['active']['party']},q['healthAfter']);self.assertEqual(p.saved(self.s)['active']['hp'],q['enemyAfter'])
 def test_threat_skips_incapacitated_party_member(self):
  self.begin();f.initialize(self.s)['vitality']['founder']=0;self.assertEqual(tactics.intent(self.s,p.saved(self.s)['active'])['target'],'rhess');self.assertFalse(any(r['who']=='founder' for r in p.choices(self.s)))
 def test_signature_proofs_require_equipped_completed_piece_and_return(self):
  key=self.sig();self.begin('wolf');self.assertNotIn('fieldHistory',a.state(self.s)['items'][key]);self.t.finish();it=a.state(self.s)['items'][key];self.assertEqual(it['fieldHistory']['enemyTypes'],['wolf'])
  self.act('gear-stow',ownerId='founder',itemId=key);self.begin('thief');self.t.finish();self.assertEqual(a.state(self.s)['items'][key]['fieldHistory']['enemyTypes'],['wolf'])
 def test_retreat_keeps_completed_proofs_but_not_unfinished(self):
  key=self.sig();self.begin('wolf');self.act('watch-retreat');self.act('advance');self.assertNotIn('fieldHistory',a.state(self.s)['items'][key])
 def test_signature_funding_reserves_and_cancellation(self):
  self.sig(types=['wolf','thief']);self.s['materialInventory']['binding-thread']=3;self.s['materialReserveTargets']['binding-thread']=3;self.t.reject('gear-signature-refine',ownerId='founder',choice='edge',rank=1)
  self.s['materialReserveTargets']['binding-thread']=1;before=(self.s['sharedFunds'],self.s['materialInventory']['binding-thread']);self.act('gear-signature-refine',ownerId='founder',choice='edge',rank=1);self.assertEqual(self.s['sharedFunds'],before[0]-6);self.assertFalse(growth.effect(self.s,'founder'));self.act('gear-cancel-job',workerId='founder');self.assertEqual((self.s['sharedFunds'],self.s['materialInventory']['binding-thread']),before)
 def test_signature_pauses_completes_and_requires_re_equip(self):
  key=self.sig(types=['wolf','thief']);self.act('gear-signature-refine',ownerId='founder',choice='guard',rank=1);self.act('assign-founder',assignment='rest');self.act('advance');self.assertEqual(a.state(self.s)['jobs']['founder']['done'],0);self.act('gear-resume-job',workerId='founder');self.act('advance');self.act('advance');self.assertFalse(growth.effect(self.s,'founder'));self.act('gear-equip',ownerId='founder',itemId=key,mode='expedition');self.assertEqual(growth.effect(self.s,'founder')['choice'],'guard')
 def test_signature_rank_two_and_switch_preserve_item(self):
  key=self.sig(types=['wolf','thief','bandit','boar']);it=a.state(self.s)['items'][key];it['fieldRefinement']={'ownerId':'founder','choice':'edge','rank':1};self.s['materialInventory']['moon-glass']=2
  self.t.reject('gear-signature-refine',ownerId='founder',choice='care',rank=2);self.s['materialInventory']['wolf-underfur']=1
  self.act('gear-signature-refine',ownerId='founder',choice='care',rank=2);self.act('advance');self.act('advance');self.assertEqual(a.state(self.s)['signatures']['founder']['itemId'],key);self.assertEqual(a.state(self.s)['items'][key]['fieldRefinement']['rank'],2)
  self.act('gear-signature-refine',ownerId='founder',choice='guard',rank=2);self.assertEqual(a.state(self.s)['jobs']['founder']['cost'],4);self.act('advance');self.assertEqual(a.state(self.s)['items'][key]['fieldRefinement']['choice'],'guard')
 def test_foreign_refinement_never_activates(self):
  key=self.sig(types=['wolf','thief']);a.state(self.s)['items'][key]['fieldRefinement']={'ownerId':'rhess','choice':'edge','rank':2};self.assertFalse(growth.effect(self.s,'founder'))
 def test_care_does_not_grant_free_healing_or_bypass_cost(self):
  key=self.sig(types=['wolf','thief']);a.state(self.s)['items'][key]['fieldRefinement']={'ownerId':'founder','choice':'care','rank':2};self.begin();self.assertFalse(any(r['preview']['healing'] for r in p.choices(self.s) if r['who']=='founder'))
 def test_homecoming_rest_exact_party_and_repeatable_dismiss(self):
  self.begin(party=['rhess']);self.act('watch-retreat');self.act('advance');v=home.view(self.s);self.assertTrue(v['visible']);self.act('assign-founder',assignment='commissions');self.act('watch-rest-party',reportId=v['reportId']);self.assertEqual(g.character_assignment(self.s,'founder'),'commissions');self.assertEqual(g.character_assignment(self.s,'rhess'),'rest');self.act('watch-dismiss-return',reportId=v['reportId']);self.assertFalse(home.view(self.s)['visible']);self.assertEqual(len(p.saved(self.s)['reports']),1)
 def test_homecoming_stale_action_and_away_party_are_atomic(self):
  self.begin(party=['rhess']);self.act('watch-retreat');self.act('advance');v=home.view(self.s);self.t.reject('watch-rest-party',reportId=v['reportId']+1);self.t.depart(['rhess']);self.t.reject('watch-rest-party',reportId=v['reportId'])
 def test_personal_moments_bounded_and_consumed_once(self):
  import companion_participation as cp
  self.begin();run=p.saved(self.s)['active'];run['contributions']={'elowen':{'healed':2}};report={};home.returned(self.s,run,report);home.returned(self.s,run,report)
  events=[e for e in cp.saved(self.s)['events'].values() if e['kind']=='patrol-moment'];self.assertEqual(len(events),1)
  self.act('watch-retreat');self.act('advance');key=events[0]['id'];self.act('share-participation',eventId=key,choice='notice');self.t.reject('share-participation',eventId=key,choice='notice')
 def test_all_authored_companions_have_homecoming_voices(self):
  self.assertEqual(set(__import__('conversation_voice').ROWS),set(paths.PEOPLE)-{'founder'})
 def test_precision_refinement_changes_actual_damage_only_when_equipped(self):
  key=self.sig(types=['wolf','thief']);a.state(self.s)['items'][key]['fieldRefinement']={'ownerId':'founder','choice':'edge','rank':1};self.begin();row=self.row('founder:strike');damage=row['preview']['damage'];self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual(p.saved(self.s)['active']['hp'],10-damage);self.assertEqual(row['signatureDamage'],1)
 def test_shelter_refinement_reduces_target_injury(self):
  key=self.sig(types=['wolf','thief']);self.begin();before=self.row('rhess:strike')['preview']['injury'];a.state(self.s)['items'][key]['fieldRefinement']={'ownerId':'founder','choice':'guard','rank':1};after=self.row('rhess:strike')['preview']['injury'];self.assertEqual(after,max(0,before-1))
 def test_care_refinement_improves_existing_healing(self):
  key=self.sig(w='elowen',types=['wolf','thief']);a.state(self.s)['items'][key]['fieldRefinement']={'ownerId':'elowen','choice':'care','rank':1};self.prep('elowen','elowen-dressing');self.begin();f.initialize(self.s)['vitality']['founder']=2;row=self.row('elowen:elowen-dressing');self.assertEqual(row['preview']['healing'],[{'who':'founder','amount':2}]);self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),3)
