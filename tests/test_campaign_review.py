"""Continuous opening routes and guide behavior outside the default path."""
from copy import deepcopy
import json
import unittest
import game as g
import keeping_hearth as hearth
import test_first_hearth as first
import test_house_shape as shape
import test_room_to_grow as grow
import test_keeping_hearth as security

class PreservationGuidanceTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign()
  g.learn_for_character(self.s,'mira','gentle-preservation')
 def follow(self):
  before=deepcopy(self.s);n=hearth.preservation_step(self.s);self.assertEqual(before,self.s)
  g.apply_action(self.s,n['action']);return n
 def test_archived_method_studies_without_another_expedition(self):
  self.assertNotIn('gentle-preservation',g.character_principles(self.s,'founder'))
  self.assertEqual(self.follow()['id'],'study-preservation')
  for _ in range(4):
   if 'gentle-preservation' in g.character_principles(self.s,'founder'):break
   self.follow()
  self.assertIn('gentle-preservation',g.character_principles(self.s,'founder'));self.assertIsNone(self.s['expedition'])
 def test_paused_study_resumes_without_losing_progress(self):
  self.follow();g.apply_action(self.s,{'type':'advance'});g.apply_action(self.s,{'type':'assign-founder','assignment':'rest'})
  before=deepcopy(self.s['trainingProjects']['founder']);self.follow()
  self.assertEqual(before,self.s['trainingProjects']['founder']);self.assertEqual(self.s['founderAssignment'],'training')
 def test_paused_shared_lesson_resumes_both_assignments(self):
  g.apply_action(self.s,{'type':'start-lesson','learnerId':'founder','teacherId':'mira','subjectKind':'principle','targetId':'gentle-preservation'})
  g.apply_action(self.s,{'type':'assign-resident','assignment':'rest'})
  self.assertEqual(self.follow()['action']['type'],'resume-lesson');self.assertEqual(self.s['residentAssignment'],'teaching')
  self.follow();self.assertIn('gentle-preservation',g.character_principles(self.s,'founder'))

class ContinuousCampaignTests(unittest.TestCase):
 def test_four_chapters_from_fresh_with_alternate_routes(self):
  for route in [('solo','salvage','private','infirmary','barriers','capture'),('meet','survey','shared','smithy','wards','drive-away')]:
   with self.subTest(route=route):
    company,approach,layout,specialist,defense,resolution=route
    one=first.FirstHearthTests();one.setUp();one.play(company=company,approach=approach,reload_each=True)
    two=shape.HouseShapeTests();two.s=one.s;two.beginning=deepcopy(one.s)
    order=[('scholarship','table'),('cultivation','nursery'),('craftsmanship','production')]
    if company=='meet':order.reverse()
    for key,design in order:two.run_chapter(key,design)
    self.assertFalse(grow.grow.available(two.s));two.act('shape-conclude')
    three=grow.RoomToGrowTests();three.s=two.s;three.plan(layout=layout,specialist=specialist);three.play()
    four=security.KeepingHearthTests();four.s=three.s;four.play(defense=defense,choice=resolution)
    s=g.migrate_state(json.loads(json.dumps(four.s)))
    self.assertEqual(hearth.stage(s),'complete');self.assertFalse(s['testing']['used']);self.assertGreaterEqual(s['sharedFunds'],0)
    self.assertNotIn('sabine',g.household_members(s));self.assertEqual(hearth.case(s)['status'],'released' if resolution=='capture' else 'unmet')
