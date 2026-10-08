"""Read-only design proposals. Validation never installs mechanics into game rules."""
import json
import math
import re
import hashlib

COMMON={'id':'string','name':'string','summary':'string','tags':'string[]','ancestryRestrictions':'string[]','excludedAncestries':'string[]','visibility':'public-template|private-template','establishedFactRequirements':'fact[]','continuityWarnings':'string[]','references':'reference[]','mechanicsProposalId':'string|null'}
from expansion_schemas import SCHEMAS, PACK_TYPES as PUBLIC_TYPES, TARGETS
PACK_TYPES={k:set(v) for k,v in PUBLIC_TYPES.items()}
REFERENCE={'namespace':'baseline|pack|dependency','id':'string','purpose':'string'}
MECHANIC={'id':'string','name':'string','status':'proposed-not-implemented','designIntent':'string','existingRuleReferences':'string[]','prerequisites':'string[]','effects':'effect[]','costs':'cost','stackingRule':'string','cancellationRule':'string','repeatUseRule':'string','failureOrRecovery':'string','balanceRationale':'string','testScenarios':'string[]','implementationNeeds':'string[]'}
SHAPES={'fact':{'fact':'string','evidenceNeeded':'string'},'reference':REFERENCE,'effect':{'target':'string','trigger':'string','change':'string','magnitude':'number|null','unit':'string','cap':'number|null','exclusions':'string[]'},'cost':{'crowns':'nonnegative|null','materials':'input[]','workPhases':'positive|null','workOwner':'string'},'input':{'materialId':'string|null','propertyId':'string|null','quantity':'positive|null','consumption':'on-start|on-completion|not-consumed|undecided'}}

def validate(files,dependencies=()):
    import game
    import content_packs
    errors=[];warnings=[];objects={};entries={};types={}
    def error(where,why):
        if len(errors)<100:errors.append(where+': '+why)
    def pairs(rows):
        result={}
        for k,v in rows:
            if k in result:raise ValueError('duplicate key '+k)
            result[k]=v
        return result
    for path,raw in files.items():
        if path.endswith('.json'):
            try:objects[path]=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('non-finite number')))
            except (ValueError,RecursionError):error(path,'invalid JSON or repeated fields')
    def check(value,kind,where):
        if kind.endswith('[]'):
            if not isinstance(value,list) or len(value)>1000:error(where,'expected bounded array');return
            for i,item in enumerate(value):check(item,kind[:-2],where+'['+str(i)+']')
        elif kind=='object':
            schema=SHAPES['chapter'] if '.chapters[' in where else SHAPES['choice'] if '.choices[' in where else None
            if schema:shape(value,schema,where)
            else:error(where,'unsupported object shape')
        elif kind in SHAPES:shape(value,SHAPES[kind],where)
        elif kind=='string':
            limit=80 if where.endswith('.name') else 500 if where.endswith('.summary') else 300 if where.endswith(('.fact','.evidenceNeeded')) else 200 if where.endswith('.purpose') else 600
            if not isinstance(value,str) or not value.strip() or len(value)>limit or re.search(r'<[^>]*>|[\x00-\x08]',value):error(where,'invalid plain text or length')
        elif kind=='boolean':
            if type(value) is not bool:error(where,'expected boolean')
        elif kind in ('number','nonnegative','positive'):
            if type(value) not in (int,float) or (type(value) is float and not math.isfinite(value)) or (kind!='number' and (type(value) is not int or value<(1 if kind=='positive' else 0))):error(where,'invalid number')
        elif '|' in kind:
            if value is None and 'null' in kind.split('|'):return
            alternatives=[k for k in kind.split('|') if k!='null']
            if len(alternatives)==1 and alternatives[0] in ('string','number','positive','nonnegative','reference'):check(value,alternatives[0],where)
            elif not isinstance(value,str) or value not in alternatives:error(where,'unsupported value')
        elif value!=kind:error(where,'expected '+kind)
    def shape(value,schema,where):
        if not isinstance(value,dict) or set(value)!=set(schema):error(where,'missing or unsupported fields');return False
        for k,t in schema.items():check(value[k],t,where+'.'+k)
        return True
    manifest=objects.get('manifest.json',{})
    if not isinstance(manifest,dict):manifest={}
    expected={'schemaVersion','packId','packVersion','status','language','dependencies','files','vocabularyPath','readmePath','validationReportPath'}
    if set(manifest)!=expected:error('manifest','missing or unsupported fields')
    pack_id=manifest.get('packId')
    if not isinstance(pack_id,str) or pack_id not in PACK_TYPES:error('manifest','choose a supported public expansion pack; private mystery content is not accepted');pack_id='unsupported'
    if type(manifest.get('schemaVersion')) is not int or manifest.get('schemaVersion')!=1 or manifest.get('status')!='draft-for-implementation' or manifest.get('language')!='en':error('manifest','incorrect version/status/language')
    check(manifest.get('packVersion'),'string','manifest.packVersion')
    for k,path in [('vocabularyPath','vocabulary.json'),('readmePath','README.md'),('validationReportPath','validation-report.json')]:
        if manifest.get(k)!=path or path not in files:error('manifest','missing '+path)
    vocab=objects.get('vocabulary.json',{});tags=set()
    if not isinstance(vocab,dict) or set(vocab)!={'schemaVersion','tags'} or type(vocab.get('schemaVersion')) is not int or vocab.get('schemaVersion')!=1 or not isinstance(vocab.get('tags'),list):error('vocabulary','invalid wrapper')
    else:
        for row in vocab['tags']:
            if shape(row,{'id':'string','definition':'string'},'vocabulary') and isinstance(row['id'],str):
                if row['id'] in tags:error('vocabulary','duplicate tag')
                tags.add(row['id'])
    author_report=objects.get('validation-report.json')
    report_schema={'schemaVersion':'positive','checksPerformed':'string[]','automatedChecksRun':'boolean',**{k:'string[]' for k in ('duplicateIds','brokenReferences','undeclaredTags','countShortfalls','mechanicalUncertainties','semanticConcerns','knownLimitations')}}
    if shape(author_report,report_schema,'validation-report') and author_report.get('schemaVersion')!=1:error('validation-report','unsupported schema')
    declarations=manifest.get('files',[])
    if not isinstance(declarations,list):declarations=[];error('manifest.files','expected array')
    paths=set();declared_types=set()
    for row in declarations:
        if not shape(row,{'path':'string','recordType':'string','count':'nonnegative'},'manifest.files'):continue
        path=row['path'];kind=row['recordType']
        if not isinstance(path,str) or not isinstance(kind,str):continue
        if kind not in PACK_TYPES.get(pack_id,set())|{'mechanics-proposal'} or path!=kind+'.json' and not (kind=='mechanics-proposal' and path=='proposed-mechanics.json'):error('manifest.files','unsupported type or filename');continue
        if path in paths or kind in declared_types:error(path,'duplicate declaration')
        paths.add(path);declared_types.add(kind)
        obj=objects.get(path,{})
        if not isinstance(obj,dict) or set(obj)!={'schemaVersion','packId','recordType','entries'} or type(obj.get('schemaVersion')) is not int or obj.get('schemaVersion')!=1 or obj.get('packId')!=pack_id or obj.get('recordType')!=kind or not isinstance(obj.get('entries'),list):error(path,'invalid wrapper');continue
        if len(obj['entries'])!=row['count']:error(path,'declared count mismatch')
        schema=MECHANIC if kind=='mechanics-proposal' else {**COMMON,**SCHEMAS[kind]}
        for record in obj['entries']:
            if not shape(record,schema,path):continue
            key=record['id']
            if not isinstance(key,str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',key):error(path,'invalid ID');continue
            if key in entries:error(key,'duplicate ID')
            entries[key]=record;types[key]=kind
    if declared_types!=PACK_TYPES.get(pack_id,set())|{'mechanics-proposal'}:error('manifest.files','include all assigned record types and proposed-mechanics.json')
    support={'manifest.json','vocabulary.json','README.md','validation-report.json','CODEX-HANDOFF.md','reference/00-shared-contract.md','reference/prototype-reference.json'}
    from expansion_schemas import HANDOFF_FILES
    support.add('reference/'+HANDOFF_FILES.get(pack_id,'unsupported.md'))
    if set(files)-paths-support:error('archive','unexpected files')
    baseline=set(content_packs.REGISTRY)|set(game.ROOMS)|set(game.PRINCIPLE_NAMES)|set(game.MATERIALS)|set(game.RECIPES)|set(game.SPELL_FORMS)|{k for k in game.PRACTICES if not k.startswith('ss-dev-perk-concept-')}|set(game.FOCUS_INSCRIPTIONS)|{p for m in game.MATERIALS.values() for p in m['properties']}
    from candidate_proposals import PACKAGES
    baseline|={k for k in PACKAGES if not k.startswith('ss-dev-starting-package-concept-')}
    deps=manifest.get('dependencies',[]);resolved=set()
    if not isinstance(deps,list):deps=[];error('dependencies','expected array')
    for dep in deps:
        if not shape(dep,{'packId':'string','packVersion':'string','reason':'string'},'dependency'):continue
        match=next((d for d in dependencies if d['manifest']['packId']==dep['packId'] and d['manifest']['packVersion']==dep['packVersion']),None)
        if not match:error('dependencies','stage the exact dependency version before this pack');continue
        if dep['packId']==pack_id:error('dependencies','self dependency')
        resolved.update(match['entries'])
    for key,record in entries.items():
        if types[key]=='mechanics-proposal':
            if isinstance(record.get('existingRuleReferences'),list) and any(not isinstance(x,str) or x not in baseline for x in record['existingRuleReferences']):error(key,'unknown baseline rule')
            cost=record.get('costs')
            if isinstance(cost,dict) and isinstance(cost.get('materials'),list):
                for item in cost['materials']:
                    if isinstance(item,dict):
                        a,b=item.get('materialId'),item.get('propertyId')
                        if (a is None)==(b is None):error(key,'each input needs exactly one material or property')
                        target=a if a is not None else b
                        if not isinstance(target,str) or target not in baseline|set(entries)|resolved:error(key,'unknown mechanical input')
            if not isinstance(record.get('testScenarios'),list) or not 3<=len(record['testScenarios'])<=6:error(key,'supply 3–6 proposed test scenarios')
            continue
        if isinstance(record.get('tags'),list) and any(not isinstance(t,str) or t not in tags for t in record['tags']):error(key,'undeclared tag')
        allowed=record.get('ancestryRestrictions');excluded=record.get('excludedAncestries')
        if isinstance(allowed,list) and isinstance(excluded,list) and all(isinstance(x,str) for x in allowed+excluded):
            if set(allowed)&set(excluded) or any(x not in content_packs.REGISTRY for x in allowed+excluded):error(key,'invalid ancestry restrictions')
        mechanics=record.get('mechanicsProposalId')
        if mechanics is not None and (not isinstance(mechanics,str) or types.get(mechanics)!='mechanics-proposal'):error(key,'missing mechanics proposal')
        for ref in record.get('references',[]) if isinstance(record.get('references'),list) else []:
            if isinstance(ref,dict) and isinstance(ref.get('id'),str) and isinstance(ref.get('namespace'),str):
                scope={'baseline':baseline,'pack':set(entries),'dependency':resolved}.get(ref.get('namespace'),set())
                if ref['id'] not in scope:error(key,'unresolved '+ref['id'])
        for field in ('artifactId','baselineFormId','principleIds','propertyIds','componentPropertyIds','neighbouringPrincipleIds'):
            if field not in record or record[field] is None:continue
            values=record[field] if isinstance(record[field],list) else [record[field]]
            if any(not isinstance(x,str) or x not in baseline|set(entries)|resolved for x in values):error(key,'unresolved '+field)
    for kind in PACK_TYPES.get(pack_id,set()):
        count=sum(t==kind for t in types.values())
        if count<TARGETS[kind]:warnings.append(f'{kind}: {count} of {TARGETS[kind]} requested records; shortfall {TARGETS[kind]-count}.')
    warnings.append('Design review only: no proposed cost, effect, spell, material property or equipment bonus is installed or executed.')
    warnings.append('Passing structure checks does not establish balance, semantic coherence, novelty or fit with current gameplay.')
    digest=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
    semantic_checks(entries,types,dependencies,deps,baseline,tags,objects,error)
    report={'valid':not errors,'errors':errors,'warnings':warnings,'packId':pack_id,'packVersion':manifest.get('packVersion'),'recordCount':len(entries),'contentCount':sum(t!='mechanics-proposal' for t in types.values()),'mechanicsCount':sum(t=='mechanics-proposal' for t in types.values()),'digest':digest}
    return {'manifest':manifest,'entries':entries,'types':types,'sourceFiles':files},report


SHAPES['choice']={'id':'string','label':'string','residentResponse':'string','establishesFacts':'string[]','doesNotEstablish':'string[]'}
SHAPES['chapter']={'title':'string','proposedActivity':'string','requiredEstablishedFacts':'string[]','optionalInvitation':'string','possibleResolution':'string'}

def semantic_checks(entries,types,dependencies,declared,baseline,tags,objects,error):
    import game,content_packs
    from candidate_proposals import PACKAGES
    registry={};declared_ids={d.get('packId') for d in declared if isinstance(d,dict) and isinstance(d.get('packId'),str)}
    for dep in dependencies:
        if dep['manifest']['packId'] not in declared_ids:continue
        for key,row in dep['entries'].items():registry[key]=(dep.get('types',{}).get(key),row)
    base_types={**{k:'principle-concept' for k in game.PRINCIPLE_NAMES},**{k:'material' for k in game.MATERIALS},**{k:'property-concept' for m in game.MATERIALS.values() for k in m['properties']},**{k:'spell-construction' for k in game.SPELL_FORMS},**{k:'starting-package-concept' for k in PACKAGES},**{k:'room-purpose' for k in game.ROOMS}}
    singles={'artifactId':'artifact-concept','baselineFormId':'spell-construction','reversalRitualId':'ritual-concept','siteId':'site-template','leadId':'lead-template','communityId':'community-template','firstRoomPurposeId':'room-purpose','secondRoomPurposeId':'room-purpose','sourceOccupationId':'occupation','suggestedStartingPackageId':'starting-package-concept','comparableBaselinePackage':'starting-package-concept'}
    multiple={'propertyIds':'property-concept','principleIds':'principle-concept','componentPropertyIds':'property-concept','neighbouringPrincipleIds':'principle-concept','roomPurposeIds':'room-purpose','garmentReferenceIds':'garment','startingKnowledgeCandidates':'principle-concept'}
    def resolves(key,expected):
        if not isinstance(key,str):return False
        typ=types.get(key) or registry.get(key,(None,None))[0] or base_types.get(key)
        if expected in ('occupation','garment'):return key in registry and key.startswith(expected+'-')
        return typ==expected
    def check_reference(ref,key):
        if not isinstance(ref,dict) or not isinstance(ref.get('id'),str) or not isinstance(ref.get('namespace'),str):return
        rid=ref['id'];scope=ref['namespace']
        if not (rid in baseline if scope=='baseline' else rid in entries if scope=='pack' else rid in registry if scope=='dependency' else False):error(key,'unresolved reference '+rid)
        target=entries.get(rid) or registry.get(rid,(None,{}))[1]
        if target and target.get('visibility')=='private-template':error(key,'public reference to private candidate')
    for key,r in entries.items():
        if types[key]=='mechanics-proposal':
            costs=r.get('costs',{})
            for row in costs.get('materials',[]) if isinstance(costs,dict) and isinstance(costs.get('materials'),list) else []:
                if isinstance(row,dict):
                    for field,typ in [('materialId','material'),('propertyId','property-concept')]:
                        if row.get(field) is not None and not resolves(row[field],typ):error(key,'wrong input reference type')
            continue
        if r.get('visibility')!='public-template':error(key,'private candidates require a separate private workflow')
        if key in registry or key in baseline:error(key,'ID collides with baseline or dependency')
        for field,typ in singles.items():
            if r.get(field) is not None and not resolves(r[field],typ):error(key,'wrong reference type: '+field)
        for field,typ in multiple.items():
            if isinstance(r.get(field),list) and any(not resolves(x,typ) for x in r[field]):error(key,'wrong reference type: '+field)
        if 'ancestryId' in r and (not isinstance(r['ancestryId'],str) or r['ancestryId'] not in content_packs.REGISTRY):error(key,'unknown ancestry')
        if isinstance(r.get('relatedBaselineIds'),list) and any(not isinstance(x,str) or x not in baseline for x in r['relatedBaselineIds']):error(key,'unknown baseline rule')
        for field in ('references','principleOrMaterialReferences','supportedWorkReferences'):
            for ref in r.get(field,[]) if isinstance(r.get(field),list) else []:check_reference(ref,key)
        if r.get('subjectReference') is not None:check_reference(r['subjectReference'],key)
        if 'choices' in r and isinstance(r['choices'],list):
            ids=[c.get('id') for c in r['choices'] if isinstance(c,dict)]
            if not 2<=len(r['choices'])<=4 or any(not isinstance(x,str) for x in ids) or len({str(x) for x in ids})!=len(ids):error(key,'invalid choices')
        if 'chapters' in r and isinstance(r['chapters'],list) and not 3<=len(r['chapters'])<=4:error(key,'expected 3–4 chapters')
        if types[key]=='starting-package-concept':
            if not isinstance(r.get('startingKnowledgeCandidates'),list) or len(r['startingKnowledgeCandidates'])!=1:error(key,'one starting knowledge candidate required')
            if not isinstance(r.get('startingPracticeCandidates'),list) or len(r['startingPracticeCandidates'])!=1 or any(p not in ('archive-focus','careful-assembly','field-notes') for p in r['startingPracticeCandidates']):error(key,'one supported basic practice required')
    seen=set()
    for d in declared:
        if isinstance(d,dict) and isinstance(d.get('packId'),str):
            if d['packId'] in seen:error('dependencies','duplicate dependency')
            seen.add(d['packId'])
    current=objects.get('vocabulary.json',{});definitions={t['id']:t['definition'] for t in (current.get('tags') if isinstance(current.get('tags'),list) else []) if isinstance(t,dict) and isinstance(t.get('id'),str) and isinstance(t.get('definition'),str)} if isinstance(current,dict) else {}
    for dep in dependencies:
        raw=dep.get('sourceFiles',{}).get('vocabulary.json')
        if raw:
            for row in json.loads(raw).get('tags',[]):
                if row['id'] in definitions and definitions[row['id']]!=row['definition']:error('vocabulary','changed declared tag meaning '+row['id'])
