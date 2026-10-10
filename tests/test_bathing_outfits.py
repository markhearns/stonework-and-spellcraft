from copy import deepcopy
from pathlib import Path
import unittest
import game as g, bathing_outfits as b, character_customization as custom, headquarters as h, room_life, cheat_tools

class BathingTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign('fresh')
  g.apply_action(self.s,{'type':'cheat-toggle','enabled':True})
  g.apply_action(self.s,{'type':'cheat-recruit','characterId':'all'})
  self.s['currentDayPhase']='afternoon'
  for room in b.ROOMS:
   legacy=h.ROOMS[room]['legacy']
   if legacy:self.s['facilityProjects'][legacy]['status']='complete'
   else:self.s['headquarters']['rooms'][room]='complete'
  for who in b.OUTFITS:g.set_character_assignment(self.s,who,'rest')
 def test_every_companion_switches_in_each_real_room_without_changing_wardrobe(self):
  self.assertEqual(set(b.OUTFITS),set(cheat_tools.unique_ids()))
  for room in b.ROOMS:
   for who in b.OUTFITS:custom.write_person(self.s,who)['leisureRoom']=room
   before=deepcopy(self.s);rows=b.view(self.s)
   self.assertEqual(self.s,before)
   for who,row in rows.items():
    self.assertTrue(row['active']);self.assertEqual(row['roomId'],room)
    self.assertEqual(room_life.location(self.s,who),room)
    self.assertTrue(Path('static/assets/portraits/bathing',who+'.webp').is_file())
 def test_leaving_or_working_restores_normal_portrait(self):
  custom.write_person(self.s,'mira')['leisureRoom']='pool'
  self.assertTrue(b.view(self.s)['mira']['active'])
  custom.write_person(self.s,'mira')['leisureRoom']='library'
  self.assertFalse(b.view(self.s)['mira']['active'])
  custom.write_person(self.s,'mira')['leisureRoom']='pool'
  g.set_character_assignment(self.s,'mira','archive')
  self.assertFalse(b.view(self.s)['mira']['active'])
  self.assertIsNone(b.view(self.s)['mira']['portraitId'])
 def test_away_companion_does_not_use_bathing_art(self):
  custom.write_person(self.s,'mira')['leisureRoom']='pool'
  self.s['expedition']={'partyIds':['founder','mira']}
  self.assertFalse(b.view(self.s)['mira']['active'])
 def test_unrestored_room_does_not_activate_outfit(self):
  custom.write_person(self.s,'mira')['leisureRoom']='pool'
  legacy=h.ROOMS['pool']['legacy']
  if legacy:self.s['facilityProjects'][legacy]['status']='not-started'
  else:self.s['headquarters']['rooms'].pop('pool',None)
  self.assertFalse(b.view(self.s)['mira']['active'])
 def test_portraits_and_roster(self):
  view=g.public_state(self.s)
  self.assertNotIn('veyra',str(view).lower())
  for who in ('iona','aurelia','neris','sabine'):
   self.assertNotIn('placeholder',view['originalAssets'][who])
  self.assertEqual(len(view['characterCatalog']),17)
  ages={who:g.character_profile(self.s,who)['adultAgeYears'] for who in b.OUTFITS}
  self.assertTrue(all(age>=18 for age in ages.values()))
  self.assertGreaterEqual(len(set(ages.values())),5)
  self.assertFalse(list(Path('static/assets').rglob('*veyra*')))
 def test_authored_age_update_preserves_custom_ages_and_is_idempotent(self):
  import companion_identity
  self.s['people']['tamsin']['adultAgeYears']=25
  self.s['people']['zahra']['adultAgeYears']=28
  companion_identity.migrate(self.s)
  self.assertEqual(self.s['people']['tamsin']['adultAgeYears'],20)
  self.assertEqual(self.s['people']['zahra']['adultAgeYears'],28)
  before=deepcopy(self.s);companion_identity.migrate(self.s);self.assertEqual(before,self.s)
