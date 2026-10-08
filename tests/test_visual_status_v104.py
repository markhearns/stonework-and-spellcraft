from copy import deepcopy
import unittest

import game as g
import armoury
import field_patrols
import guidance
import test_armoury as equipment_tests
import test_romance as romance_tests


class VisualStatusTests(unittest.TestCase):
    def equipment(self):
        fixture=equipment_tests.ArmouryTests();fixture.setUp()
        return fixture

    def test_equipment_pictures_match_actual_multislot_displacement(self):
        t=self.equipment();dress=t.item('work-dress');before=deepcopy(t.s)
        old=set(armoury.loadout(t.s,'founder')['slots'].values())
        q=armoury.quote_action(t.s,{'type':'gear-equip','itemId':dress})
        self.assertEqual(t.s,before);self.assertFalse(q['blockers'])
        staged=deepcopy(t.s);g.apply_action(staged,q['action'])
        new=set(armoury.loadout(staged,'founder')['slots'].values())
        row=q['equipmentChanges'][0]
        self.assertEqual({i['id'] for i in row['removed']},old-new)
        self.assertEqual({i['id'] for i in row['added']},new-old)
        self.assertEqual(len(row['added']),1)
        self.assertEqual(row['added'][0]['icon'],armoury.view(staged)['items'][dress]['icon'])

    def test_blocked_equipment_preview_claims_no_changes(self):
        t=self.equipment();before=deepcopy(t.s)
        q=armoury.quote_action(t.s,{'type':'gear-equip','itemId':'missing-item'})
        self.assertTrue(q['blockers']);self.assertEqual(q['equipmentChanges'],[])
        self.assertTrue(all(r['before']==r['after'] for r in q['patrolBonuses'].values()))
        self.assertEqual(t.s,before)

    def test_patrol_preview_matches_equipment_after_commit(self):
        t=self.equipment();t.act('gear-apply-loadout',mode='expedition')
        shield=t.item('field-shield');q=armoury.quote_action(t.s,{'type':'gear-equip','itemId':shield,'hand':'hand2'})
        self.assertFalse(q['blockers']);self.assertEqual(q['patrolBonuses']['founder']['before'],field_patrols.equipment_bonuses(t.s,'founder'))
        g.apply_action(t.s,q['action'])
        self.assertEqual(q['patrolBonuses']['founder']['after'],field_patrols.equipment_bonuses(t.s,'founder'))

    def test_shield_and_armour_do_not_double_the_cover_bonus(self):
        t=self.equipment();t.act('gear-apply-loadout',mode='expedition')
        t.equip(t.item('field-shield'),hand='hand2');t.equip(t.item('leather-coat'))
        self.assertEqual(field_patrols.equipment_bonuses(t.s,'founder')['cover'],1)

    def test_advance_resource_tiles_match_real_night_resolution(self):
        t=romance_tests.RomanceTests();t.setUp();t.ready();t.share(0);t.s['roomFurnishings']['common-room']='velvet-settee'
        t.s['currentDayPhase']='evening';g.apply_action(t.s,{'type':'assign-founder','assignment':'commissions'})
        before=deepcopy(t.s);v=guidance.preview(t.s);self.assertEqual(t.s,before)
        rows={r['id']:r for r in v['resources']}
        self.assertTrue({'crowns','provisions','resonance'}.issubset(rows))
        g.apply_action(t.s,{'type':'advance'})
        actual={'crowns':t.s['sharedFunds'],'provisions':t.s['provisions']['stock'],'resonance':t.s['resonancePoints']}
        for key,value in actual.items():
            self.assertEqual(rows[key]['after'],value)
            self.assertEqual(rows[key]['change'],rows[key]['after']-rows[key]['before'])

    def test_blocked_advance_has_no_speculative_resource_changes(self):
        s=g.new_campaign('fresh');g.apply_action(s,{'type':'start-expedition','siteId':'old-waterworks'});g.apply_action(s,{'type':'advance'})
        before=deepcopy(s);v=guidance.preview(s)
        self.assertTrue(v['blocked']);self.assertEqual(v['resources'],[]);self.assertEqual(s,before)
