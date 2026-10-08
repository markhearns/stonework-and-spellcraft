"""Earned eight-chapter campaigns with commission income and a paid field objective."""
import json
import os
from pathlib import Path
import commissions
import field_magic
import field_objectives
import field_patrols
import game as g
import test_eight_chapter_flow as eight


class RefinementCampaignTests(eight.EightChapterFlowTests):
    def money(self,n):
        self.commission_count=getattr(self,'commission_count',0)
        while self.s['sharedFunds']<n:
            key=next((k for k in commissions.CATALOG if not commissions.blockers(self.s,k,'founder','crowns')),None)
            if key:
                self.act('commission-start',commissionId=key,workerId='founder',payment='crowns')
                self.advance(commissions.CATALOG[key]['phases']);self.commission_count+=1
            else:
                self.act('assign-founder',assignment='commissions');self.advance()
        self.act('assign-founder',assignment='rest')

    def play_seven(self,company):
        super().play_seven(company)
        party=['founder','rhess']
        for who in party:self.act('assign-character',characterId=who,assignment='rest')
        for _ in range(8):
            if all(field_magic.vitality(self.s,w)==6 for w in party):break
            self.advance()
        self.act('watch-depart',participants=party,objectiveId='escort');self.advance()
        run=field_patrols.saved(self.s)['active']
        row=next(r for r in field_objectives.site_choices(self.s,run) if r['id']=='founder:site-work')
        self.act('watch-site-method',methodId=row['id']);self.advance(row['phases'])
        for _ in range(4):
            run=field_patrols.saved(self.s)['active']
            if run['stage']=='returning':break
            rows=[r for r in field_patrols.choices(self.s) if r.get('objectiveStep') and not r['blockers']]
            row=min(rows,key=lambda r:r['preview']['injury'])
            self.act('watch-method',methodId=row['id']);self.advance()
        self.advance()
        report=field_patrols.saved(self.s)['reports'][-1]
        self.assertTrue(report['complete']);self.assertEqual(report['objectiveId'],'escort')
        self.assertFalse(any(r['rewarded'] for r in report['outcomes']))
        self.assertFalse(self.s['testing']['used']);self.assertGreater(self.commission_count,0)
        if os.environ.get('STONEWORK_REFINEMENT_AUDIT_DIR'):
            out=Path(os.environ['STONEWORK_REFINEMENT_AUDIT_DIR']);out.mkdir(parents=True,exist_ok=True)
            (out/('refinement-campaign-'+company+'.json')).write_text(json.dumps(dict(route=company,commissionsCompletedCumulative=self.commission_count,day=self.s['dayNumber'],funds=self.s['sharedFunds'],provisions=self.s['provisions']['stock'],unfedDays=self.s['provisions']['unfedDays'],cheats=False,objective=report),indent=2))
