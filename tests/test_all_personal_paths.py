from copy import deepcopy
import json,unittest
import game as g,personal_paths as p,armoury as a,field_magic as f,character_customization as c
import test_household_chapters as household

class AllPathTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['researchStatus']='complete'
  for who in p.PEOPLE:
   if who not in ('founder','mira'):household.HouseholdChapterTests.member(self,who)
   self.s['bedroomAssignments'][who]='bedchamber'
  self.s['headquarters']['rooms']['training-yard']='complete';a.sync(self.s)
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def reject(self,kind,**kw):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(old,self.s)
 def ready(self,who):
  r=p.ensure(self.s,who);r['learned']=[k for k,d in p.CATALOG.items() if d['who']==who]
  it=a.make(self.s,'field-staff',who);a.put_in(self.s,who,it['id'],'expedition');a.state(self.s)['signatures'][who]={'itemId':it['id'],'completedOn':{'day':1}}
  a.state(self.s)['mode'][who]='expedition';return it
 def at(self,who,tag,enemy=None):
  d=next(d for d in f.STEPS if d['tag']==tag and (enemy is None or d.get('enemy')==enemy))
  self.s['expedition']={'siteId':f.SITE,'partyIds':['founder']+([] if who=='founder' else [who]),'stage':'encounter-choice','discoveryReady':False,'chosenApproach':'survey','restoreLanternDisplay':False}
  m=f.initialize(self.s);m['aqueduct']={'completed':[x['id'] for x in f.STEPS[:f.STEPS.index(d)]],'enemyHp':{},'pending':None,'discoveries':[],'buffs':{}};m['vitality']={w:6 for w in g.household_members(self.s)};return d
 def test_all_seventeen_identities_have_three_distinct_paths_and_nine_talents(self):
  import signature_equipment as sig
  self.assertEqual(set(p.PEOPLE),set(sig.ROOMS));self.assertEqual(len(p.CATALOG),144)
  self.assertEqual(len({d['name'] for d in p.CATALOG.values()}),144)
  for who,person in p.PEOPLE.items():
   nodes=[d for d in p.CATALOG.values() if d['who']==who]
   self.assertEqual(len(nodes),9);self.assertEqual(len({d['branch'] for d in nodes}),3);self.assertEqual(person['room'],sig.ROOMS[who])
   for d in nodes:
    if d['requires']:self.assertEqual(p.CATALOG[d['requires']]['who'],who)
 def test_each_person_can_train_through_existing_assignment_and_reload(self):
  for who in p.PEOPLE:
   key=next(k for k,d in p.CATALOG.items() if d['who']==who and not d['requires'])
   before=g.character_sheet(self.s,who)['availableAdvancement'];self.act('path-train',characterId=who,talentId=key)
   self.act('advance');self.s=g.migrate_state(json.loads(json.dumps(self.s)));self.act('advance')
   self.assertIn(key,p.record(self.s,who)['learned']);self.assertFalse(p.record(self.s,who)['techniques']);self.assertEqual(before,g.character_sheet(self.s,who)['availableAdvancement'])
 def test_every_active_technique_resolves_in_a_supported_encounter(self):
  for who in p.PEOPLE:self.ready(who)
  base=deepcopy(self.s)
  for key,d in p.CATALOG.items():
   if d['kind']!='technique':continue
   with self.subTest(talent=key):
    self.s=deepcopy(base);who=d['who'];self.act('path-prepare',characterId=who,talentId=key,prepared=True)
    tag=next(t for t in d['tags'] if t!='trail');step=self.at(who,tag,'living' if tag=='enemy' else None)
    self.act('field-method',characterId=who,method='personal:'+key)
    for _ in range(2):
     if self.s['expedition']['stage']=='working':self.act('advance')
    self.assertIn(p.use_key({'site':f.SITE,'step':step['id']},who,key),self.s['personalPathUses'])
    self.assertEqual(g.character_sheet(self.s,who)['earnedAdvancement'],2)
    if tag!='enemy':self.assertIn(step['id'],f.progress(self.s)['completed'])
 def test_replace_is_atomic_same_slot_family_and_does_not_forget(self):
  self.ready('kaede')
  for k in ('measured-blow','settled-stance','steady-hands'):self.act('path-prepare',characterId='kaede',talentId=k,prepared=True)
  self.reject('path-prepare',characterId='kaede',talentId='gate-breaker',prepared=True,replaceId='unshaken')
  self.act('path-prepare',characterId='kaede',talentId='gate-breaker',prepared=True,replaceId='measured-blow')
  self.assertEqual(p.record(self.s,'kaede')['techniques'],['gate-breaker','settled-stance','steady-hands']);self.assertIn('measured-blow',p.record(self.s,'kaede')['learned'])
 def test_saved_build_restores_talents_and_gear_or_rolls_back_everything(self):
  it=self.ready('mira');self.act('path-prepare',characterId='mira',talentId='mira-lamp',prepared=True)
  self.act('save-complete-preparation',characterId='mira',name='Lamplight');snap=deepcopy(c.snapshot(self.s,'mira'))
  self.act('path-clear',characterId='mira');self.act('gear-stow',ownerId='mira',itemId=it['id']);self.act('load-complete-preparation',characterId='mira',name='Lamplight');self.assertEqual(c.snapshot(self.s,'mira'),snap)
  self.act('path-clear',characterId='mira');self.act('gear-stow',ownerId='mira',itemId=it['id']);a.state(self.s)['items'][it['id']]['ownerId']='founder'
  self.reject('load-complete-preparation',characterId='mira',name='Lamplight')
 def test_older_preparation_keeps_new_talents_unchanged(self):
  self.ready('mira');self.act('save-complete-preparation',characterId='mira',name='Older');saved=c.person(self.s,'mira')['preparations']['Older'];saved.pop('paths');saved.pop('gear')
  self.act('path-prepare',characterId='mira',talentId='mira-lamp',prepared=True);self.act('load-complete-preparation',characterId='mira',name='Older');self.assertEqual(p.record(self.s,'mira')['techniques'],['mira-lamp'])
 def test_preview_drill_and_live_elemental_damage_agree(self):
  self.ready('neris');self.act('path-prepare',characterId='neris',talentId='neris-pressure',prepared=True);self.at('neris','enemy','ember')
  fx=p.target_effect(self.s,'neris','neris-pressure','ember');self.assertEqual(fx['damage'],4)
  self.act('field-method',characterId='neris',method='personal:neris-pressure');self.act('advance');self.assertEqual(f.progress(self.s)['enemyHp']['ember'],2)
 def test_all_passives_match_their_branch_and_preview_is_pure(self):
  for who in p.PEOPLE:self.ready(who)
  for key,d in p.CATALOG.items():
   if d['kind']!='passive':continue
   who=d['who'];r=p.ensure(self.s,who);r['passives']=[key];root=d['requires'];fx=p.preview(self.s,who,root)
   self.assertIn(d['name'], ' '.join(fx['breakdown']))
  old=deepcopy(self.s);v=p.view(self.s);self.assertEqual(self.s,old);self.assertEqual(len(v),16)
 def test_old_pending_technique_and_existing_choices_are_preserved(self):
  self.ready('kaede');self.act('path-prepare',characterId='kaede',talentId='turning-counter',prepared=True);self.at('kaede','enemy','undead');self.act('field-method',characterId='kaede',method='personal:turning-counter')
  for k in ('counter','healsAlly','restoresSelf','immune'):f.progress(self.s)['pending']['personal']['effects'].pop(k,None)
  self.s['schemaVersion']=63;old=deepcopy(self.s);g.migrate_state(self.s);old['schemaVersion']=66;self.assertEqual(old,self.s);self.act('advance');self.assertEqual(f.progress(self.s)['enemyHp']['bones'],3)
if __name__=='__main__':unittest.main()
