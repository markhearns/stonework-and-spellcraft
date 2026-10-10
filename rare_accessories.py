"""Five scarce creature-made accessories, one equipment slot and real field effects."""
from copy import deepcopy
RECIPES={
 'basilisk-mirror-brooch':dict(name='Basilisk mirror brooch',drop='basilisk-scale',principle='field-calibration',cost=90,description='+2 personal cover on patrols and immunity to the basilisk’s stiffening gaze.',cover=2),
 'manticore-barb-ring':dict(name='Manticore barb ring',drop='manticore-spine',principle='field-calibration',cost=95,description='+2 damage on physical patrol attacks and techniques. Does not increase spells or non-damaging actions.',physical=2),
 'wyvern-antivenom-locket':dict(name='Wyvern antivenom locket',drop='wyvern-venom-crystal',principle='gentle-preservation',cost=90,description='Prevents manticore and wyvern venom. Healing received restores 2 additional vitality, up to the normal maximum.',healing=2),
 'hydra-heart-charm':dict(name='Hydra heart charm',drop='hydra-resin',principle='gentle-preservation',cost=105,description='Restores 1 vitality after each committed patrol exchange while its wearer remains conscious. Cannot revive an incapacitated wearer.',regeneration=1),
 'colossus-ward-talisman':dict(name='Colossus ward talisman',drop='colossus-ward-key',principle='reference-binding',cost=110,description='+2 damage on damaging patrol spells and +1 personal cover. Enemy ward and visibility limits still apply.',spell=2,cover=1),
}

def install():
 import armoury as a
 for key,d in RECIPES.items():
  a.CATALOG[key]=dict(id=key,name=d['name'],slots=['accessory'],alternateHand=False,materials='Two '+d['drop'].replace('-',' ')+' samples, silver ivy and binding thread',baseCostCrowns=d['cost'],workPhases=6,room='enchanting-room',tags=['wearable','rare-accessory'],enchantable=True,initialStorageCapacity=1,iconId='equipment-'+key,recipePolicy='fixed-rare-components',status='implemented',rarity='Rare',description=d['description'],requiredMaterials={d['drop']:2,'silver-ivy':1,'binding-thread':1})

def quote(s,definition,who):
 import game as g,field_patrols as p,headquarters as h
 d=RECIPES[definition];b=[]
 if not p.chapter(s)['completedOn']:b.append('Complete Chapter 8, The First Real Test, before making rare creature accessories.')
 for key in set(('field-calibration',d['principle'])):
  if key not in g.character_principles(s,who):b.append('The maker must have learned '+g.PRINCIPLE_NAMES[key]+'.')
 materials=[d['drop'],d['drop'],'silver-ivy','binding-thread']
 return materials,b

def worn(s,who):
 import armoury as a
 l=a.loadout(s,who,'expedition');it=a.state(s)['items'].get(l['slots'].get('accessory'),{})
 if it.get('definitionId') not in RECIPES or it.get('ownerId')!=who or it.get('location')!='armoury' or a.busy(s,it['id']):return None
 return it['definitionId']

def effect(s,who,key):return RECIPES.get(worn(s,who),{}).get(key,0)

def enrich(s,row):
 bonus=effect(s,row['who'],'spell' if row['kind']=='spell' else 'physical') if row['damage']>0 and row['kind'] in ('spell','attack','technique','protect') else 0
 row['damage']+=bonus
 if bonus:row['accessoryDamage']=bonus

def healing(s,who):return effect(s,who,'healing')

def finish(s,result):
 for who,hp in result['healthAfter'].items():
  if 0<hp<6 and effect(s,who,'regeneration'):
   result['healthAfter'][who]+=1;result['healing'].append({'who':who,'amount':1})
   result.setdefault('challengeNotes',[]).append('The hydra heart charm restores 1 vitality to its conscious wearer.')
 return result
