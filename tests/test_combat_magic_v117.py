"""Timed protection, cleansing, ward removal and consumable field preparations."""
from copy import deepcopy
import unittest
import game as g, field_patrols as p, field_magic as f, combat_magic as m
import creature_challenges as c, lasting_rituals as rituals, patrol_tactics as tactics
import test_content_v117 as content, test_magic_overhaul as magic

class CombatMagicTests(unittest.TestCase):
 setUp=content.ContentV117Tests.setUp
 act=content.ContentV117Tests.act
 reject=content.ContentV117Tests.reject
 member=content.ContentV117Tests.member
 depart=content.ContentV117Tests.depart
 enemy=content.ContentV117Tests.enemy
 equip=content.ContentV117Tests.equip
 start_creature=content.ContentV117Tests.start_creature
 learned=magic.MagicTests.learned
 def spellrow(self,kind,target=None):
  return next(r for r in p.choices(self.s) if r.get('spellKind')==kind and (target is None or r.get('magicGuardTarget',r.get('purifyTarget'))==target))
 def commit(self,row):
  expected=deepcopy(row['preview']);self.assertFalse(row['blockers']);self.act('watch-method',methodId=row['id']);self.act('advance')
  run=p.saved(self.s)['active'];self.assertEqual({w:f.vitality(self.s,w) for w in run['party']},expected['healthAfter'])
  if run['stage']=='decision':
   self.assertEqual(run['hp'],expected['enemyAfter']);self.assertEqual(run['combatMagic'],expected['combatMagic']);self.assertEqual(run['preparations'],expected['preparations'])
  return expected
 def guard(self):return next(r for r in p.choices(self.s) if r['id']=='founder:guard')
 def test_all_six_spell_previews_are_pure_and_resolve_exactly(self):
  base=deepcopy(self.s)
  for kind,cid in [('stoneguard','owlbear'),('gust-strike','wyvern'),('binding-snare','marsh-hydra'),('purifying-light','basilisk'),('dispel-ward','runebound-colossus'),('chain-lightning','runebound-colossus')]:
   with self.subTest(spell=kind):
    self.s=deepcopy(base);sid=self.learned(kind);self.equip('founder');self.start_creature(cid)
    if kind=='purifying-light':f.initialize(self.s)['vitality']['founder']=5
    before=deepcopy(self.s);row=self.spellrow(kind);g.public_state(self.s);self.assertEqual(self.s,before)
    self.commit(row);self.assertEqual(g.spell_by_id(self.s,sid)['castCount'],1)
    for key,n in m.SPELLS[kind]['inputs'].items():self.assertEqual(self.s['materialInventory'][key],before['materialInventory'][key]-n)
 def test_stoneguard_target_and_three_exchange_duration(self):
  self.learned('stoneguard');self.member('rhess');self.depart(['founder','rhess']);self.enemy('thief');self.act('advance')
  p.saved(self.s)['active']['hp']=99
  target='founder';baseline=self.guard()['preview']['cover'];preview=self.commit(self.spellrow('stoneguard',target))
  self.assertEqual(preview['cover'],baseline+2) # Guard's own +1 is replaced by the spell's +3.
  self.assertEqual(m.state(p.saved(self.s)['active'])['wards'],{target:2})
  self.assertTrue(self.spellrow('stoneguard',target)['blockers'])
  self.assertNotIn('rhess',m.state(p.saved(self.s)['active'])['wards'])
  before=deepcopy(p.saved(self.s)['active']);self.act('advance');self.assertEqual(p.saved(self.s)['active'],before)
  for remaining in (1,0):
   self.commit(self.guard());self.assertEqual(m.state(p.saved(self.s)['active'])['wards'].get(target,0),remaining)
  self.assertEqual(self.guard()['preview']['cover'],baseline)
 def test_binding_reduces_both_hydra_attacks_and_rejects_inapplicable_targets(self):
  self.learned('binding-snare');self.start_creature('marsh-hydra');row=self.spellrow('binding-snare');old=self.guard()['preview']
  self.assertEqual(row['preview']['attack'],old['attack']-2)
  self.assertFalse(any(x['reason']=='second hydra head' for x in row['preview']['otherInjuries']))
  self.commit(row);self.assertTrue(self.spellrow('binding-snare')['blockers'])
  for cid in ('runebound-colossus','will-o-wisp','skeleton'):
   run=p.saved(self.s)['active'];run['enemies']=[cid];run.pop('creatureState',None);run.pop('combatMagic',None)
   if cid not in p.ENEMIES:continue
   self.assertTrue(self.spellrow('binding-snare')['blockers'])
 def test_gust_grounds_wyvern_and_opens_next_attack(self):
  self.learned('gust-strike');self.start_creature('wyvern');row=self.spellrow('gust-strike')
  self.assertEqual(row['preview']['creatureState']['grounded'],2);self.assertEqual(row['preview']['opening'],1)
  self.commit(row);self.assertGreater(self.guard()['preview']['damage'],1)
 def test_full_health_purification_clears_before_retaliation_without_inventing_cover(self):
  self.learned('purifying-light');self.start_creature('basilisk');run=p.saved(self.s)['active'];run['round']=1
  st=c.state(self.s,run)
  for key,n in [('venom',2),('stiffness',3),('corrosion',2),('imbalance',2)]:st[key]['founder']=n
  run['creatureState']=st
  row=self.spellrow('purifying-light','founder');self.assertFalse(row['blockers']);preview=row['preview']
  self.assertFalse(preview['otherInjuries']);self.assertEqual(preview['cover'],0)
  for key in ('venom','stiffness','corrosion','imbalance'):self.assertNotIn('founder',preview['creatureState'][key])
  self.commit(row)
 def test_dispel_disconnects_two_plates_and_suppresses_armour(self):
  self.learned('dispel-ward');self.start_creature('runebound-colossus');row=self.spellrow('dispel-ward')
  self.assertEqual(row['preview']['creatureState']['wards'],1);self.assertEqual(row['preview']['combatMagic']['unwarded'],2)
  self.commit(row)
  self.assertFalse(self.spellrow('dispel-ward')['blockers']) # The remaining plate can be removed.
  run=p.saved(self.s)['active'];run['enemies']=['rust-beetle'];run['hp']=13;run.pop('creatureState',None)
  attack=next(r for r in p.choices(self.s) if r['id']=='founder:strike')
  self.assertFalse(any('Creature plates' in x for x in attack['preview']['breakdown']))
 def test_chain_arcs_have_specific_targets_and_ward_caps(self):
  self.learned('chain-lightning');self.start_creature('owlbear');run=p.saved(self.s)['active']
  for cid,expected in [('owlbear',5),('bandit',7),('marsh-hydra',7),('runebound-colossus',7)]:
   run['enemies']=[cid];run['hp']=p.ENEMIES[cid]['hp'];run.pop('creatureState',None)
   row=self.spellrow('chain-lightning');self.assertEqual(row['damage'],expected,cid)
   if cid=='runebound-colossus':self.assertEqual(row['preview']['damage'],1);self.assertEqual(row['preview']['creatureState']['wards'],1)
 def test_unprepared_and_reserved_magic_unavailable_and_pending_cast_refunded(self):
  sid=self.learned('chain-lightning');self.start_creature('owlbear');self.s['preparedSpells']['founder']=[]
  self.assertFalse(any(r.get('spellKind')=='chain-lightning' for r in p.choices(self.s)))
  self.s['preparedSpells']['founder']=[sid];self.s['materialReserveTargets']['fireglass']=self.s['materialInventory']['fireglass']
  self.assertTrue(self.spellrow('chain-lightning')['blockers']);self.s['materialReserveTargets']['fireglass']=0
  old=deepcopy(self.s['materialInventory']);self.act('watch-method',methodId=self.spellrow('chain-lightning')['id']);self.act('watch-retreat')
  self.assertEqual(self.s['materialInventory'],old);self.assertEqual(g.spell_by_id(self.s,sid).get('castCount',0),0)
 def prepare_ritual(self,key):
  for principle in rituals.CATALOGUE[key]['principles']:g.learn_for_character(self.s,'mira',principle)
  self.s['restorationStatus']='complete';self.s['headquarters']['rooms']['library']='complete'
  self.act('begin-lasting-ritual',ritualId=key,leaderId='founder',partnerId='mira')
  for _ in range(rituals.state(self.s)['project']['requiredPhases']):self.act('advance')
  self.assertIn(key,self.s['fieldPreparations']);self.assertFalse(rituals.active(self.s,key))
 def test_repeatable_preparations_charge_once_on_valid_departure_and_expire(self):
  for key in m.RITUALS:self.prepare_ritual(key)
  self.reject('begin-lasting-ritual',ritualId='expedition-warding',leaderId='founder',partnerId='mira')
  self.reject('watch-depart',routeId='missing',participants=['founder']);self.assertEqual(len(self.s['fieldPreparations']),2)
  self.equip('founder');self.depart();self.assertFalse(self.s['fieldPreparations']);self.enemy('thief');self.act('advance');p.saved(self.s)['active']['hp']=99
  for remaining in (2,1,0):
   self.commit(self.guard());self.assertEqual(m.preparations(p.saved(self.s)['active'])['warding'],remaining)
  self.act('watch-retreat');self.act('advance');self.assertIsNone(p.saved(self.s)['active']);self.prepare_ritual('expedition-warding')
 def test_preparation_cancel_refunds_and_antivenom_doses_prevent_only_new_poison(self):
  for principle in m.RITUALS['antivenom-preparation']['principles']:g.learn_for_character(self.s,'mira',principle)
  before=deepcopy(self.s['materialInventory']);money=self.s['sharedFunds'];self.act('begin-lasting-ritual',ritualId='antivenom-preparation',leaderId='founder',partnerId='mira');self.act('cancel-lasting-ritual',ritualId='antivenom-preparation')
  self.assertEqual(self.s['materialInventory'],before);self.assertEqual(self.s['sharedFunds'],money);self.assertNotIn('antivenom-preparation',self.s.get('fieldPreparations',{}))
  self.prepare_ritual('antivenom-preparation');self.start_creature('manticore');run=p.saved(self.s)['active'];run['hp']=99
  for remaining in (1,0):
   run=p.saved(self.s)['active'];run['round']=0;f.initialize(self.s)['vitality']['founder']=6
   preview=self.commit(self.guard());self.assertGreater(preview['injury'],0);self.assertFalse(preview['creatureState']['venom']);self.assertEqual(preview['preparations']['antivenom'],remaining)
  run=p.saved(self.s)['active'];run['round']=0;f.initialize(self.s)['vitality']['founder']=6
  self.assertEqual(self.guard()['preview']['creatureState']['venom'],{'founder':2})

if __name__=='__main__':unittest.main()
