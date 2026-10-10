"""Shared catalogue, discovery transactions, creature bounties and rare components."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import game as g,bestiary as b,bounty_contracts as c,field_patrols as p,field_magic as f,armoury as a,headquarters as h,provisions

class BestiaryTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'};self.s['provisions']['stock']=500;self.s['sharedFunds']=1000;self.s['currentDayPhase']='morning'
 def act(self,kind,**args):g.apply_action(self.s,dict(type=kind,**args))
 def reject(self,kind,**args):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**args)
  self.assertEqual(old,self.s)
 def test_shared_catalogue_and_pools(self):
  self.assertIs(p.ENEMIES,b.ENCOUNTERS);self.assertIs(p.ROUTES,b.ROUTES)
  self.assertEqual((len(b.CREATURES),len(b.ANCESTRIES)),(30,21))
  offered={k for r in b.ROUTES.values() for k in r['pool']}
  self.assertTrue(all(d['enemyId'] in offered for d in b.CREATURES.values()))
  for r in b.ROUTES.values():
   self.assertEqual(sum(r['weights']),100);self.assertTrue((Path(__file__).resolve().parents[1]/'static'/r['artPath'].lstrip('/')).is_file())
  for d in b.ENCOUNTERS.values():self.assertTrue(set(d['materials'])<=g.MATERIALS.keys())
 def test_browsing_and_forecast_do_not_discover(self):
  old=deepcopy(self.s);g.public_state(self.s);b.view(self.s);c.view(self.s);self.assertEqual(old,self.s)
  self.act('watch-depart',bountyId='wolf',participants=['founder']);self.assertEqual(b.knowledge(self.s,'wolf'),0)
  old=deepcopy(self.s);g.public_state(self.s);self.assertEqual(old,self.s)
  self.act('advance');self.assertEqual(b.knowledge(self.s,'wolf'),1)
  old=deepcopy(self.s);g.public_state(self.s);self.act('advance');self.assertEqual(old['bestiary'],self.s['bestiary'])
 def test_study_and_hunting_separate(self):
  self.reject('bestiary-study',entryId='wolf')
  b.learn(self.s,'wolf',1,'Fixture',sighting=True);self.act('bestiary-study',entryId='wolf')
  self.act('assign-founder',assignment='rest');self.act('advance');self.assertEqual(b.knowledge(self.s,'wolf'),1)
  self.act('bestiary-resume');self.act('advance');self.assertEqual(b.knowledge(self.s,'wolf'),2)
  knowledge=deepcopy(b.saved(self.s));inventory=deepcopy(self.s['materialInventory']);food=self.s['provisions']['stock'];self.s['currentDayPhase']='morning'
  self.act('food-assign',characterId='founder',assignment='hunt');yielded=provisions.yield_for(self.s,'founder','hunt');self.act('advance')
  self.assertEqual(self.s['provisions']['stock'],food+yielded);self.assertEqual(self.s['materialInventory'],inventory);self.assertEqual(b.saved(self.s),knowledge)
 def test_rare_material_properties_and_sources(self):
  for cid,(key,*_) in c.SAMPLES.items():
   d=g.MATERIALS[key];self.assertTrue(d['rare']);self.assertGreaterEqual(d['price'],24)
   self.assertTrue(c.uses(key));self.assertTrue(all(x.startswith('rare-') for x in d['properties']))
   self.assertFalse(any(set(d['properties'])&set(r['requiredProperties']) for r in g.RECIPES.values()))
   self.reject('buy-material',materialId=key)
  self.s['headquarters']['rooms']['supply-office']='complete'
  self.reject('food-order',materials={'grave-silk':1},quotedCost=1)
  self.s['materialInventory']['grave-silk']=2;self.s['materialReserveTargets']['grave-silk']=1
  funds=self.s['sharedFunds'];self.act('sell-material',materialId='grave-silk');self.assertEqual(self.s['sharedFunds'],funds+g.MATERIALS['grave-silk']['price']);self.reject('sell-material',materialId='grave-silk')
 def test_all_bounties_shared_profiles_and_exact_return_rewards(self):
  p.initialize(self.s);self.s['firstRealTest']['completedOn']={'dayNumber':1,'phase':'morning'}
  initial=deepcopy(self.s)
  for cid,contract in c.CONTRACTS.items():
   with self.subTest(creature=cid):
    self.s=deepcopy(initial);self.act('watch-depart',bountyId=cid,participants=['founder']);self.act('advance');run=p.saved(self.s)['active']
    self.assertEqual(run['enemies'],[contract['enemyId']]);self.assertEqual(b.encounter(self.s,run)['art'],b.CREATURES[cid]['art'])
    # Resolve the actual peaceful action and Advance, then process the return transaction.
    import character_builds
    character_builds.build(self.s,'founder')['attributes']={k:10 for k in character_builds.ATTRIBUTES}
    self.s['characterSkills']['founder']={k:4 for k in g.CHARACTER_SKILLS}
    if cid=='runebound-colossus':
     for _ in range(3):
      action=next(r for r in p.choices(self.s) if r.get('challengeAction')=='disconnect');self.act('watch-method',methodId=action['id']);self.act('advance')
    row=next(r for r in p.choices(self.s) if r['kind']=='peace' and not r['blockers'])
    self.act('watch-method',methodId=row['id']);self.act('advance');self.s['currentDayPhase']='morning'
    self.assertEqual(b.knowledge(self.s,cid),2);old=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds'];self.act('advance');r=p.saved(self.s)['reports'][-1]
    expected=dict(b.ENCOUNTERS[contract['enemyId']]['materials']);expected[contract['materialId']]=contract['collect']-contract['deliver']
    self.assertEqual(r['loot'],{'crowns':contract['crowns'],'food':0,'materials':expected});self.assertEqual(self.s['sharedFunds'],funds+contract['crowns'])
    for key,n in expected.items():self.assertEqual(self.s['materialInventory'][key],old[key]+n)
    self.assertEqual(len(c.saved(self.s)['receipts']),1);self.assertEqual(c.saved(self.s)['completed'][cid],self.s['dayNumber']);self.reject('watch-depart',bountyId=cid,participants=['founder'])
    self.act('advance');self.assertEqual(len(c.saved(self.s)['receipts']),1)
 def test_retreat_grants_no_sample_or_payment(self):
  old=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds'];self.act('watch-depart',bountyId='grave-silk-spider',participants=['founder']);self.act('watch-retreat');self.act('advance')
  self.assertEqual(self.s['materialInventory'],old);self.assertEqual(self.s['sharedFunds'],funds);self.assertFalse(c.saved(self.s)['receipts']);self.assertEqual(b.knowledge(self.s,'grave-silk-spider'),0)
 def test_reveal_cheat_does_not_grant_rewards_or_history(self):
  self.reject('cheat-bestiary')
  # Use the same testing toggle as other cheats.
  self.s['testing']['enabled']=True
  old=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds'];self.act('cheat-bestiary')
  self.assertEqual(b.view(self.s)['complete'],30);self.assertTrue(b.saved(self.s)['revealed']);self.assertEqual(self.s['materialInventory'],old);self.assertEqual(self.s['sharedFunds'],funds)
  self.assertTrue(all(r['sightings']==r['resolved']==0 for r in b.saved(self.s)['entries'].values()))
 def test_old_reports_knowledge_and_migration_backup(self):
  from server import GameStore
  s=deepcopy(self.s);s['schemaVersion']=65
  for key,*_ in c.SAMPLES.values():s['materialInventory'].pop(key);s['materialReserveTargets'].pop(key)
  s['fieldPatrols']={'active':None,'reports':[{'outcomes':[{'enemyId':'boar','rewarded':True}]}]}
  expected=deepcopy(s)
  with tempfile.TemporaryDirectory() as folder:
   st=GameStore(folder)
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(s),))
   actual=GameStore(folder).read();self.assertTrue(Path(folder,'campaign-before-schema-65-to-'+str(g.CURRENT_SCHEMA_VERSION)+'.sqlite3').is_file());self.assertEqual(actual['schemaVersion'],g.CURRENT_SCHEMA_VERSION)
   for k,v in expected.items():
    if k not in ('schemaVersion','revision','materialInventory','materialReserveTargets'):self.assertEqual(actual[k],v,k)
   self.assertEqual(b.knowledge(actual,'briarback-boar'),2)
   for key,*_ in c.SAMPLES.values():self.assertEqual(actual['materialInventory'][key],0)
 def test_advanced_enchantment_consumes_and_refunds_rare_component(self):
  self.s['headquarters']['rooms']['enchanting-room']='complete';self.s['founderKnownPrinciples']+=list(g.PRINCIPLE_NAMES)
  it=a.make(self.s,'steel-sword','founder');it['enchantments']['measured-force']={'id':'measured-force','rank':1}
  for key in self.s['materialInventory']:self.s['materialInventory'][key]=5
  action=dict(operation='strengthen',workerId='founder',itemId=it['id'],enchantmentId='measured-force')
  q=a.recipe(self.s,action);self.assertFalse(q['blockers']);self.assertTrue(any(g.MATERIALS[k].get('rare') for k in q['materials']))
  old=deepcopy(self.s['materialInventory']);self.act('gear-start-job',**action)
  for k in set(q['materials']):self.assertEqual(self.s['materialInventory'][k],old[k]-q['materials'].count(k))
  self.act('gear-cancel-job');self.assertEqual(self.s['materialInventory'],old)
  self.s['headquarters']['stock']['deep-heat-bench']=1;self.act('gear-start-job',**action);self.act('advance');self.assertEqual(a.state(self.s)['jobs']['founder']['done'],2);self.act('advance');self.assertEqual(a.state(self.s)['items'][it['id']]['enchantments']['measured-force']['rank'],2)
 def test_advanced_building_reserves_refund_and_effects(self):
  for room in h.ROOMS:self.s['headquarters']['rooms'][room]='complete'
  self.s['founderKnownPrinciples']+=list(g.PRINCIPLE_NAMES)
  for key in self.s['materialInventory']:self.s['materialInventory'][key]=5
  for key,d in c.IMPROVEMENTS.items():
   with self.subTest(improvement=key):
    old=deepcopy(self.s['materialInventory']);funds=self.s['sharedFunds'];m=next(iter(d['materials']));self.s['materialReserveTargets'][m]=5
    self.reject('hq-job',jobId=key);self.s['materialReserveTargets'][m]=0
    self.act('hq-job',jobId=key);self.assertEqual(self.s['materialInventory'][m],old[m]-d['materials'][m]);self.act('hq-cancel');self.assertEqual(self.s['materialInventory'],old);self.assertEqual(self.s['sharedFunds'],funds)
    self.act('hq-job',jobId=key)
    for _ in range(d['phases']):self.act('advance')
    self.assertEqual(self.s['headquarters']['stock'][key],1);self.reject('hq-job',jobId=key)
  self.assertEqual(p.cover(self.s,['founder'])[0],1)
  self.s['currentDayPhase']='morning';f.initialize(self.s)['vitality']['founder']=1;self.act('assign-founder',assignment='rest');self.act('advance');self.assertEqual(f.vitality(self.s,'founder'),3)

 def test_slatehide_armour_preview_matches_committed_damage(self):
  self.act('watch-depart',bountyId='slatehide-lizard',participants=['founder']);self.act('advance')
  row=next(r for r in p.choices(self.s) if r['id']=='founder:strike');self.assertEqual(row['preview']['damage'],max(1,row['damage']-1))
  expected=p.saved(self.s)['active']['hp']-row['preview']['damage'];self.act('watch-method',methodId=row['id']);self.act('advance');self.assertEqual(p.saved(self.s)['active']['hp'],expected)
