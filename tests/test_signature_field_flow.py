"""Chapters 1–8, then signature field growth through ordinary paid work/actions."""
import test_eight_chapter_flow as eight
import field_patrols as p,armoury as a,signature_growth as growth,field_magic as f
from scripts.audit_patrol_balance import choose

class SignatureFieldFlowTests(eight.EightChapterFlowTests):
 def play_seven(self,company):
  super().play_seven(company)
  if company!='meet':return
  who='rhess';item=next(i for i in a.state(self.s)['items'].values() if i['ownerId']==who and 'weapon' in a.CATALOG[i['definitionId']]['tags']);key=item['id']
  for w in ('founder',who):self.act('assign-character',characterId=w,assignment='rest')
  self.act('gear-signature-choose',ownerId=who,itemId=key);self.act('gear-signature-fit',ownerId=who);self.advance();self.act('gear-equip',ownerId=who,itemId=key,mode='expedition',replaceConfirmed=True);self.act('gear-signature-proof',ownerId=who);self.advance();self.act('gear-signature-close',ownerId=who,choice='practical')
  self.act('gear-agree-work',workerId=who,enabled=True)
  # Learn the actual resident technique; no catalogue/state injection.
  self.act('path-train',characterId=who,talentId='spear-watch');self.advance(2);self.act('path-prepare',characterId=who,talentId='spear-watch',prepared=True)
  for attempt in range(25):
   if len(growth.history(growth.item(self.s,who),who)['enemyTypes'])>=2:break
   for _ in range(6):
    if all(f.vitality(self.s,w)==6 for w in ('founder',who)):break
    self.advance()
   self.act('watch-depart',participants=['founder',who],routeId='road')
   for _ in range(45):
    run=p.saved(self.s)['active']
    if not run:break
    if run['stage']=='decision':
     rows=[r for r in p.choices(self.s) if not r['blockers']];row=next((r for r in rows if r['kind']=='peace'),None) or choose(rows);self.act('watch-method',methodId=row['id'])
    self.advance()
  self.assertGreaterEqual(len(growth.history(growth.item(self.s,who),who)['enemyTypes']),2)
  quote=growth.quote(self.s,who,'guard',1);self.money(quote['cost'])
  for material,n in quote['materials'].items():
   # Existing immediate material purchase action if earned field stock is short.
   if self.s['materialInventory'][material]-self.s['materialReserveTargets'][material]<n:
    import game as g
    self.money(g.MATERIALS[material]['price']*n);self.act('buy-material',materialId=material,quantity=n)
  self.act('gear-signature-refine',ownerId=who,choice='guard',rank=1);self.advance(2);self.assertEqual(a.state(self.s)['items'][key]['fieldRefinement']['choice'],'guard');self.assertFalse(growth.effect(self.s,who));self.act('gear-equip',ownerId=who,itemId=key,mode='expedition',replaceConfirmed=True);self.assertEqual(growth.effect(self.s,who)['rank'],1);self.assertFalse(self.s['testing']['used'])
