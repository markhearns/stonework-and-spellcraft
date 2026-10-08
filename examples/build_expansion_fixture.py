"""A small honest design-review fixture; these objects are not playable items."""
import json
from pathlib import Path
import zipfile

def fixture_files():
 pack_id='ss-materials-and-properties'
 common={'tags':['practical'],'ancestryRestrictions':[],'excludedAncestries':[],'visibility':'public-template','establishedFactRequirements':[],'continuityWarnings':['Proposed material; no stock, recipe or price is installed.'],'references':[{'namespace':'baseline','id':'binding','purpose':'Existing component property.'}],'mechanicsProposalId':None}
 material={**common,'id':'ss-material-waxed-linen','name':'Waxed linen cord','summary':'A waxed thread for binding a dry workshop assembly.','physicalDescription':'Matte flax fibres rubbed with a thin wax coating.','sourceContexts':['A textile workshop.'],'mundaneUses':['Binding a folio.'],'magicalAssociations':['Holding joined parts together.'],'propertyIds':['binding'],'substitutionNotes':'Might replace binding thread in a dry assembly, subject to implementation.','handlingNotes':'Keep away from open flame.','rarityBand':'ordinary'}
 prop={**common,'id':'ss-property-wicking','name':'Capillary wicking','summary':'A proposed property for carrying moisture through fine pores.','definition':'Moves moisture along a connected porous path.','suitableExamples':['Untreated cotton cord.'],'unsuitableExamples':['A solid glass rod.'],'acceptanceTest':'A wet end gradually moistens the adjacent dry section.','substitutionLimits':'Does not produce water, cross a broken path or establish an implemented new rule.'}
 records={'material':[material],'property-concept':[prop],'mechanics-proposal':[]}
 files={};declarations=[]
 for kind,entries in records.items():
  path='proposed-mechanics.json' if kind=='mechanics-proposal' else kind+'.json'
  files[path]=json.dumps({'schemaVersion':1,'packId':pack_id,'recordType':kind,'entries':entries},indent=2)
  declarations.append({'path':path,'recordType':kind,'count':len(entries)})
 files['manifest.json']=json.dumps({'schemaVersion':1,'packId':pack_id,'packVersion':'0.1.0','status':'draft-for-implementation','language':'en','dependencies':[],'files':declarations,'vocabularyPath':'vocabulary.json','readmePath':'README.md','validationReportPath':'validation-report.json'},indent=2)
 files['vocabulary.json']=json.dumps({'schemaVersion':1,'tags':[{'id':'practical','definition':'Useful everyday workshop materials.'}]})
 files['README.md']='Small importer fixture: two design records, no mechanics. Shortfalls: 59 materials and 11 properties. These remain proposals, not stock or executable rules.'
 files['validation-report.json']=json.dumps({'schemaVersion':1,'checksPerformed':['Manual fixture review.'],'automatedChecksRun':False,'duplicateIds':[],'brokenReferences':[],'undeclaredTags':[],'countShortfalls':['59 materials; 11 properties.'],'mechanicalUncertainties':['No price or harvesting yield is proposed.'],'semanticConcerns':[],'knownLimitations':['Importer fixture only.']})
 return files

if __name__=='__main__':
 with zipfile.ZipFile(Path('static/examples/expansion-design-fixture.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for path,raw in fixture_files().items():z.writestr('ss-materials-and-properties/'+path,raw)
