"""Development-only compilation of reviewed, fixed public records into typed rules.
No runtime English interpretation; imported revisions never change these rules.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import public_content
ROOT=Path(__file__).resolve().parents[1]
_,_,packs=public_content.review_bundle(ROOT/'content/stonework-and-spellcraft-public-packs.zip')
records={k:{**r,'recordType':p['types'][k],'packId':report['packId']} for p,report in packs for k,r in p['entries'].items()}
# Adapters are selected by contract record type, never prose or a numerical expression.
KINDS={'material':'qualification','property-concept':'qualification','equipment-concept':'equipment','inscription-concept':'inscription','artifact-concept':'artifact','principle-concept':'principle','spell-construction':'spell','ritual-concept':'ritual','augmentation-concept':'augmentation','furnishing-concept':'furnishing','adjacency-synergy':'support','starting-package-concept':'starter','perk-concept':'perk'}
rules={}
for key,r in records.items():
 if r['recordType']!='mechanics-proposal':continue
 linked=[v for v in records.values() if v.get('mechanicsProposalId')==key and v['recordType'] in KINDS]
 kind=KINDS[linked[0]['recordType']] if linked else 'service' if key=='ss-comm-mechanics-explicit-service-agreement' else 'commission'
 cost=r['costs'];phases=cost['workPhases'];crowns=cost['crowns']
 if kind=='qualification':phases=1;crowns=0
 if kind=='equipment':phases=2;crowns=6
 if kind=='principle':phases=3;crowns=8
 if kind=='inscription':crowns=8
 if kind=='ritual':crowns=6 if crowns is None else crowns
 if kind=='spell' and phases is None:phases=3;crowns=12
 if kind in ('starter','support'):phases=0;crowns=0
 if kind=='service':phases=2;crowns=8
 if kind=='commission':phases=0;crowns=8
 materials=cost['materials']
 if kind=='equipment':materials=[{'materialId':None,'propertyId':p,'quantity':1,'consumption':'on-completion'} for p in ('binding','vessel')]
 rules[key]={'id':key,'name':r['name'],'kind':kind,'recordIds':[v['id'] for v in linked],'crowns':crowns,'workPhases':phases,'materials':materials,'effectSummary':r['designIntent'],'limitations':[t for e in r['effects'] for t in e['exclusions']]}
assert len(rules)==319
(ROOT/'content/public-runtime.json').write_text(json.dumps({'version':1,'sourceDigests':{r['packId']:r['digest'] for _,r in packs},'records':records,'rules':rules},ensure_ascii=False,indent=2)+'\n')
