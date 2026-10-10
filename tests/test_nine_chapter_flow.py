"""Earned routes through Chapters 1–9, with a serialized reload after each action."""
from copy import deepcopy
import test_eight_chapter_flow as eight
import foundation_chamber as f
import game as g


class NineChapterFlowTests(eight.EightChapterFlowTests):
    def play_seven(self, company):
        super().play_seven(company)
        self.assertTrue(f.unlocked(self.s))
        self.act('foundation-start')
        for key in f.STEPS:
            d=f.STEPS[key]
            material_cost=sum(max(0,n-self.s['materialInventory'].get(k,0)+self.s['materialReserveTargets'].get(k,0))*g.MATERIALS[k]['price'] for k,n in d.get('materials',{}).items())
            self.money(d.get('cost',0)+material_cost)
            for material,n in d.get('materials',{}).items():
                while self.s['materialInventory'][material]-self.s['materialReserveTargets'][material]<n:
                    self.act('buy-material',materialId=material)
            method=next((r for r in reversed(f.methods(self.s,key)) if not r['blockers']),None)
            self.act('foundation-task',stepId=key,methodId=method['id'])
            self.advance(method['phases'])
            self.assertIn(key,f.saved(self.s)['completed'])
        self.act('foundation-conclude')
        self.assertTrue(f.ready(self.s));self.assertTrue(f.saved(self.s)['concludedOn'])
        self.assertFalse(self.s['testing']['used']);self.assertFalse(f.active(self.s))
        before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
