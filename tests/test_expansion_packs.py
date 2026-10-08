from copy import deepcopy
import json
import tempfile
import unittest
import expansion_packs as e
import game
from server import GameStore
from examples.build_expansion_fixture import fixture_files
from test_content_packs import zip_payload,change

class ExpansionPackTests(unittest.TestCase):
 def test_review_roundtrip_does_not_install_anything(self):
  files=fixture_files();pack,r=e.validate(files);self.assertTrue(r['valid'],r['errors']);self.assertEqual(r['recordCount'],2)
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);before=store.read();catalogue=deepcopy(game.MATERIALS)
   r=store.validate_expansion_pack(zip_payload(files));self.assertTrue(r['valid'],r['errors'])
   self.assertEqual(store.validate_expansion_pack(zip_payload(files)),r)
   self.assertEqual(store.read(),before);self.assertEqual(game.MATERIALS,catalogue)
   self.assertEqual(len(GameStore(d).expansion_pack_catalogue()['packs']),1)
   self.assertEqual(store.expansion_pack_preview(r['digest']),pack)
   changed=deepcopy(files);changed['README.md']+=' Revised.'
   with self.assertRaises(game.RuleError):store.validate_expansion_pack(zip_payload(changed))
   change(changed,'manifest.json',lambda x:x.update(packVersion='0.1.1'))
   self.assertTrue(store.validate_expansion_pack(zip_payload(changed))['valid'])
 def test_malformed_nested_fields_return_errors_without_exceptions(self):
  for field in ['references','tags','ancestryRestrictions','mechanicsProposalId','propertyIds','physicalDescription']:
   for value in [None,True,{},[{'id':'binding','namespace':{},'purpose':'Invalid'}]]:
    files=fixture_files();change(files,'material.json',lambda x:x['entries'][0].update({field:value}))
    report=e.validate(files)[1]
    if field=='mechanicsProposalId' and value is None:continue
    self.assertFalse(report['valid'],(field,value))
  files=fixture_files();change(files,'validation-report.json',lambda x:x.update(automatedChecksRun='yes'))
  self.assertFalse(e.validate(files)[1]['valid'])
 def test_dependency_exact_version_missing_and_reference_resolution(self):
  foundation,_=e.validate(fixture_files());foundation['manifest']['packId']='ss-foundation-example'
  foundation['entries']={k+'-dependency':{**v,'id':k+'-dependency'} for k,v in foundation['entries'].items()}
  foundation['types']={k+'-dependency':v for k,v in foundation['types'].items()}
  files=fixture_files()
  change(files,'manifest.json',lambda x:x.update(dependencies=[{'packId':'ss-foundation-example','packVersion':'0.1.0','reason':'Uses its material.'}]))
  change(files,'material.json',lambda x:x['entries'][0].update(references=[{'namespace':'dependency','id':'ss-property-wicking-dependency','purpose':'Reviewed dependency.'}]))
  self.assertFalse(e.validate(files)[1]['valid']);self.assertTrue(e.validate(files,[foundation])[1]['valid'])
  foundation['manifest']['packVersion']='0.2.0';self.assertFalse(e.validate(files,[foundation])[1]['valid'])
 def test_numeric_proposal_remains_data_and_invalid_numbers_fail(self):
  files=fixture_files()
  proposal={'id':'ss-mechanic-sample','name':'Test proposal','status':'proposed-not-implemented','designIntent':'Test staged data.','existingRuleReferences':['binding'],'prerequisites':[],'effects':[{'target':'Shared funds','trigger':'Proposed test trigger','change':'A design suggestion only.','magnitude':99,'unit':'crowns','cap':99,'exclusions':[]}],'costs':{'crowns':0,'materials':[],'workPhases':1,'workOwner':'Owner assignment'},**{k:'Fixture only.' for k in ['stackingRule','cancellationRule','repeatUseRule','failureOrRecovery','balanceRationale']},'testScenarios':['Start.','Cancel.','Repeat.'],'implementationNeeds':['A reviewed implementation.']}
  change(files,'proposed-mechanics.json',lambda x:x['entries'].append(proposal))
  change(files,'manifest.json',lambda x:next(r for r in x['files'] if r['recordType']=='mechanics-proposal').update(count=1))
  self.assertTrue(e.validate(files)[1]['valid'])
  with tempfile.TemporaryDirectory() as d:
   store=GameStore(d);before=store.read();store.validate_expansion_pack(zip_payload(files));self.assertEqual(store.read(),before)
  change(files,'proposed-mechanics.json',lambda x:x['entries'][0]['costs'].update(crowns=True))
  self.assertFalse(e.validate(files)[1]['valid'])
