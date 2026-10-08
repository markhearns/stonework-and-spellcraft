"""Regression checks of the content validator, not game/runtime acceptance tests.

Run from the integration kit root. Tests use temporary copies and never mutate source packs.
"""
from __future__ import annotations
import argparse, importlib.util, json, shutil, tempfile
from pathlib import Path


def run(packs: Path, source: Path, foundations: Path, validator_path: Path) -> dict:
    spec=importlib.util.spec_from_file_location('ss_validator',validator_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[]
    baseline=module.validate(packs,source,foundations,write=False)
    results.append({'test':'Delivered packs pass content validation','passed':not baseline['errors'],'expected':'accept'})
    def first(root,pid,filename):return root/pid/filename
    mat='ss-materials-and-properties';dev='ss-backgrounds-training-and-perks';private='ss-private-mystery-foundations'
    def change(pid,filename,fn):
        def mutate(root):
            file=first(root,pid,filename);obj=json.loads(file.read_text());fn(obj);file.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
        return mutate
    def material_entry(key,value):return change(mat,'material.json',lambda x:x['entries'][0].__setitem__(key,value))
    cases=[
        ('Reject undeclared tag',material_entry('tags',['unlisted-test-tag'])),
        ('Reject extra content field',material_entry('unexpected',True)),
        ('Reject unresolved baseline reference',material_entry('references',[{'namespace':'baseline','id':'unknown-test-baseline','purpose':'Negative validation fixture.'}])),
        ('Reject duplicate global content ID',change(mat,'material.json',lambda x:x['entries'][1].__setitem__('id',x['entries'][0]['id']))),
        ('Reject count shortfall',change(mat,'material.json',lambda x:x['entries'].pop())),
        ('Reject unknown ancestry',material_entry('ancestryRestrictions',['not-an-ancestry'])),
        ('Reject zero work phases',change(mat,'proposed-mechanics.json',lambda x:x['entries'][0]['costs'].__setitem__('workPhases',0))),
        ('Reject unsupported schema version',change(mat,'material.json',lambda x:x.__setitem__('schemaVersion',2))),
        ('Reject Boolean schema version',change(mat,'material.json',lambda x:x.__setitem__('schemaVersion',True))),
        ('Reject changed foundational tag meaning',change(mat,'vocabulary.json',lambda x:x['tags'][0].__setitem__('definition','Intentionally conflicting test definition.'))),
        ('Reject self dependency',change(mat,'manifest.json',lambda x:x['dependencies'].append({'packId':mat,'packVersion':'0.1.0','reason':'Negative cycle fixture.'}))),
        ('Reject path traversal before opening it',change(mat,'manifest.json',lambda x:x['files'][0].__setitem__('path','../../outside.json'))),
    ]
    if (packs/dev).is_dir():
        cases.extend([
            ('Reject advanced starting practice',change(dev,'starting-package-concept.json',lambda x:x['entries'][0].__setitem__('startingPracticeCandidates',['measured-assembly']))),
            ('Reject erased source occupation exclusion',change(dev,'background-mapping.json',lambda x:x['entries'][0].__setitem__('excludedAncestries',[]))),
            ('Reject perk without separate proposal',change(dev,'perk-concept.json',lambda x:x['entries'][0].__setitem__('mechanicsProposalId',None))),
        ])
    if (packs/private).is_dir():
        cases.extend([
            ('Reject private record made public',change(private,'foundation-option.json',lambda x:x['entries'][0].__setitem__('visibility','public-template'))),
            ('Reject public dependency on private mystery',change(mat,'manifest.json',lambda x:x['dependencies'].append({'packId':private,'packVersion':'0.1.0','reason':'Negative disclosure fixture.'}))),
        ])
    def duplicate_key(root):
        path=first(root,mat,'material.json');s=path.read_text();path.write_text(s.replace('"schemaVersion": 1','"schemaVersion": 1, "schemaVersion": 1',1))
    cases.append(('Reject duplicate JSON key',duplicate_key))
    def non_json_number(root):
        path=first(root,mat,'proposed-mechanics.json');s=path.read_text();path.write_text(s.replace('"magnitude": null','"magnitude": NaN',1))
    cases.append(('Reject non-JSON NaN constant',non_json_number))
    for name,mutate in cases:
        with tempfile.TemporaryDirectory(prefix='ss-content-validator-test-') as td:
            root=Path(td)/'packs';shutil.copytree(packs,root);mutate(root)
            try:rejected=bool(module.validate(root,source,foundations,write=False)['errors'])
            except (ValueError,KeyError,TypeError,OSError,AttributeError):rejected=True
            results.append({'test':name,'passed':rejected,'expected':'reject'})
    with tempfile.TemporaryDirectory(prefix='ss-content-empty-test-') as td:
        results.append({'test':'Reject an empty pack directory','passed':bool(module.validate(Path(td),source,foundations,write=False)['errors']),'expected':'reject'})
    return {'schemaVersion':1,'testScope':'Content-validator regression tests only; not game runtime tests.','runtimeTestsExecuted':False,'tests':results,'passed':sum(t['passed'] for t in results),'failed':sum(not t['passed'] for t in results),'privateFixtureTestsIncluded':(packs/private).is_dir()}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packs',type=Path,default=Path('packs'))
    ap.add_argument('--source',type=Path,default=Path('reference'))
    ap.add_argument('--foundations',type=Path,default=Path('dependencies/stonework-spellcraft-content-pack'))
    ap.add_argument('--validator',type=Path,default=Path(__file__).with_name('validate_packs.py'))
    ap.add_argument('--report',type=Path,default=Path('validator-selftest-report.json'))
    args=ap.parse_args();report=run(args.packs,args.source,args.foundations,args.validator)
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    raise SystemExit(bool(report['failed']))
