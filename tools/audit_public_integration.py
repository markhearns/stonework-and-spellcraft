"""Rebuild the source-linked integration inventory; this is not a playtest."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import public_integration as integration
import public_workshop as workshop

def report():
    coverage=integration.coverage()
    foundation,validation=integration.foundation()
    result={**coverage,'release':'0.53','schemaVersion':44,'foundation':{'recordCount':validation['recordCount'],'digest':validation['digest'],'occupations':len(integration.mapped_backgrounds(foundation)),'unmappedOccupations':[r['id'] for r in integration.mapped_backgrounds(foundation) if r['suggestedCapabilityPackageId']=='unmapped'],'storySeeds':len(integration.source_stories()),'golemAppearanceMappings':{k:[r['id'] for r in integration.golem_appearances(foundation,k)] for k in ('clay','porcelain','stone','wood','metal')}},'records':[]}
    for key,r in workshop.catalogue()['records'].items():
        route=integration.ROUTES.get(r['recordType'])
        result['records'].append({'id':key,'packId':r['packId'],'recordType':r['recordType'],'sourceDigest':workshop.catalogue()['sourceDigests'][r['packId']],'workflow':route[0] if route else None,'use':route[1] if route else None,'mechanicsProposalId':r['id'] if r['recordType']=='mechanics-proposal' else r.get('mechanicsProposalId')})
    return result

if __name__=='__main__':
    result=report()
    if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    else:print(json.dumps(result,ensure_ascii=False,indent=2))
    if result['unroutedRecordIds'] or result['foundation']['unmappedOccupations']:raise SystemExit(1)
