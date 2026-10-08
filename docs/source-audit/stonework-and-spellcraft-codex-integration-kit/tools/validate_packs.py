from __future__ import annotations
import json,re,sys,argparse,hashlib
from pathlib import Path
from collections import Counter,defaultdict

def load_json(path):
    def pairs(xs):
        d={}
        for k,v in xs:
            if k in d:raise ValueError(f'Duplicate JSON key {k!r} in {path}')
            d[k]=v
        return d
    def reject_constant(value):
        raise ValueError(f'Non-JSON numeric constant {value!r} in {path}')
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=pairs,parse_constant=reject_constant)
COMMON={'id','name','summary','tags','ancestryRestrictions','excludedAncestries','visibility','establishedFactRequirements','continuityWarnings','references','mechanicsProposalId'}
MK={'id','name','status','designIntent','existingRuleReferences','prerequisites','effects','costs','stackingRule','cancellationRule','repeatUseRule','failureOrRecovery','balanceRationale','testScenarios','implementationNeeds'}
MANIFEST={'schemaVersion','packId','packVersion','status','language','dependencies','files','vocabularyPath','readmePath','validationReportPath'}
REPORT={'schemaVersion','checksPerformed','automatedChecksRun','duplicateIds','brokenReferences','undeclaredTags','countShortfalls','mechanicalUncertainties','semanticConcerns','knownLimitations'}
REF={'namespace','id','purpose'}
ID_RE=re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')

def validate(root,source,found,write=True,selected=None):
    base=load_json(source/'prototype-reference.json')
    bids=set(base['MATERIAL_PROPERTY_IDS'])
    for v in base.values():
        if isinstance(v,dict):bids.update(v)
    bids.update(x['roomId'] for x in base['SPELL_FORMS'].values())
    ancestry=set(base['ancestries']);foundation={}
    def collect(x):
        if isinstance(x,dict):
            if isinstance(x.get('id'),str): foundation[x['id']]=x
            for v in x.values():collect(v)
        elif isinstance(x,list):
            for v in x:collect(v)
    for f in found.rglob('*.json'):collect(load_json(f))
    fm=load_json(found/'manifest.json');fpid=fm['packId']
    ftags={x['id']:x['definition'] for x in load_json(found/'vocabulary.json')['tags']}
    specs={}
    for f in sorted(source.glob('[0-9][0-9]-*.md')):
        if f.name.startswith('00'):continue
        text=f.read_text();pid=re.search(r'Pack ID: `([^`]+)`',text).group(1);typ={}
        for m in re.finditer(r'### `([^`]+\.json)` — recordType `([^`]+)` — (\d+) entries\n(.*?)(?=\n### |\n## Deliver)',text,re.S):
            fname,t,n,fields=m.groups();fs={}
            for line in fields.splitlines():
                z=re.match(r'- `([^:]+):(.+)`',line)
                if z:fs[z.group(1)]=z.group(2)
            typ[t]=(fname,int(n),fs)
        specs[pid]=typ
    registry={};packs={};all_duplicates=[]
    for path in sorted(root.iterdir()):
        if not path.is_dir() or not (path/'manifest.json').exists():continue
        m=load_json(path/'manifest.json');content={}
        if m.get('packId') in packs:raise ValueError('Duplicate packId: '+m['packId'])
        for f in m['files']:
            relative=Path(f['path'])
            if relative.is_absolute() or '..' in relative.parts or not (path/relative).resolve().is_relative_to(path.resolve()):
                raise ValueError('Unsafe manifest path: '+f['path'])
            if f['recordType'] in content:raise ValueError('Duplicate manifest recordType: '+f['recordType'])
            obj=load_json(path/relative);content[f['recordType']]=obj
            for x in obj['entries']:
                if x['id'] in registry:all_duplicates.append(x['id'])
                registry[x['id']]=(m['packId'],f['recordType'],x)
        packs[m['packId']]=(path,m,content)
    errors=[];summary=[]
    if not packs:errors.append('No expansion packs found.')
    global_tags={}
    for pid,(path,m,content) in packs.items():
        if selected and pid not in selected:continue
        bad=[];broken=[];undeclared=[];short=[];checks=[]
        def check(ok,msg):
            if not ok:bad.append(msg)
        def text(v,label,maxn=600):check(isinstance(v,str) and 0<len(v)<=maxn,f'{label}: expected nonempty text <= {maxn}')
        def arr(v,label):check(isinstance(v,list),f'{label}: expected array');return v if isinstance(v,list) else []
        def exact(v,keys,label):check(isinstance(v,dict) and set(v)==set(keys),f'{label}: wrong field set')
        check(set(m)==MANIFEST,'manifest: exact field set')
        check(type(m['schemaVersion']) is int,'manifest: schemaVersion must be an integer')
        if pid!='ss-private-mystery-foundations':
            check(all(d['packId']!='ss-private-mystery-foundations' for d in m['dependencies']),'public pack depends on private mystery pack')
        check(m['schemaVersion']==1 and m['packVersion']=='0.1.0' and m['status']=='draft-for-implementation' and m['language']=='en','manifest: version/status/language')
        check(pid in specs,'manifest: unknown pack')
        ds={d['packId']:d for d in m['dependencies']}
        check(len(ds)==len(m['dependencies']),'manifest: duplicate dependency')
        check(pid not in ds,'manifest: self dependency')
        for d in ds.values():
            exact(d,{'packId','packVersion','reason'},'dependency');text(d['reason'],'dependency reason')
            if d['packId']==fpid:check(d['packVersion']==fm['packVersion'],'dependency foundations version')
            else:check(d['packId'] in packs and d['packVersion']==packs.get(d['packId'],(None,{},None))[1].get('packVersion'),'dependency missing or version mismatch '+d['packId'])
        def resolve(ident,ns=None,expect=None):
            if ns=='baseline' or (ns is None and ident in bids):
                ok=ident in bids
                if expect=='principle':ok=ident in base['PRINCIPLE_NAMES']
                if expect=='property':ok=ident in base['MATERIAL_PROPERTY_IDS']
                if expect=='material':ok=ident in base['MATERIALS']
                if expect=='spell':ok=ident in base['SPELL_FORMS']
                if expect=='package':ok=ident in base['CAPABILITY_PACKAGES']
            elif ident in foundation:
                ok=ns in (None,'dependency') and fpid in ds
                if expect=='occupation':ok=ok and ident.startswith('occupation-')
                if expect=='garment':ok=ok and ident.startswith('garment-')
            elif ident in registry:
                owner,typ,_=registry[ident]
                ok=(owner==pid and ns in (None,'pack')) or (owner in ds and ns in (None,'dependency'))
                expected={'property':'property-concept','material':'material','principle':'principle-concept','spell':'spell-construction','package':'starting-package-concept','mechanic':'mechanics-proposal','artifact':'artifact-concept','ritual':'ritual-concept','site':'site-template','lead':'lead-template','community':'community-template','foundation':'foundation-option','room':'room-purpose'}
                if expect in expected:ok=ok and typ==expected[expect]
            else:ok=False
            if not ok:broken.append(f'{ident} (namespace={ns}, expected={expect})')
        def reference(r,label):
            exact(r,REF,label)
            if not isinstance(r,dict) or set(r)!=REF:return
            check(r['namespace'] in ('baseline','pack','dependency'),label+': namespace')
            text(r['purpose'],label+'.purpose',200);resolve(r['id'],r['namespace'])
        def dtype(v,kind,label):
            if kind=='string':text(v,label)
            elif kind=='string[]':
                values=arr(v,label);check(len(values)<=5,label+': at most five prose items')
                for q in values:text(q,label+'[]')
            elif kind=='reference[]':
                for q in arr(v,label):reference(q,label+'[]')
            elif kind=='reference|null':
                if v is not None:reference(v,label)
            elif kind=='string|null':
                if v is not None:text(v,label)
            elif kind=='object[]':arr(v,label)
            elif '|' in kind:check(v in kind.split('|'),label+': enum')
            else:bad.append(label+': unhandled declared type '+kind)
        v=load_json(path/'vocabulary.json');exact(v,{'schemaVersion','tags'},'vocabulary')
        check(type(v['schemaVersion']) is int and v['schemaVersion']==1,'vocabulary schemaVersion')
        vt={x['id']:x['definition'] for x in v['tags']}
        check(len(vt)==len(v['tags']),'vocabulary duplicate tags')
        for q in v['tags']:
            exact(q,{'id','definition'},'vocabulary tag');check(bool(ID_RE.fullmatch(q['id'])),'tag id syntax');text(q['definition'],'tag definition')
            if q['id'] in ftags:check(q['definition']==ftags[q['id']],'changed foundational tag meaning '+q['id'])
            if q['id'] in global_tags:check(q['definition']==global_tags[q['id']],'changed cross-pack tag meaning '+q['id'])
            global_tags[q['id']]=q['definition']
        use_tags=set();names=[]
        expected_types=set(specs[pid])|{'mechanics-proposal'}
        check(set(content)==expected_types,'content record types mismatch')
        for f in m['files']:
            exact(f,{'path','recordType','count'},'manifest file')
            check(not Path(f['path']).is_absolute() and '..' not in Path(f['path']).parts,'unsafe path')
            obj=content[f['recordType']];t=f['recordType'];es=obj['entries']
            exact(obj,{'schemaVersion','packId','recordType','entries'},t+' wrapper')
            check(type(obj['schemaVersion']) is int,'wrapper schemaVersion must be integer')
            check(obj['schemaVersion']==1 and obj['packId']==pid and obj['recordType']==t,t+' wrapper values')
            check(type(f['count']) is int and f['count']==len(es),t+': manifest count')
            if t in specs[pid]:
                fname,count,fields=specs[pid][t]
                check(f['path']==fname,t+': filename')
                if len(es)!=count:short.append(f'{t}: {len(es)}/{count}')
            else:fields={};check(f['path']=='proposed-mechanics.json','mechanics filename')
            for e in es:
                ident=e.get('id','');text(ident,'id');check(bool(ID_RE.fullmatch(ident)) and ident.startswith('ss-'),ident+': id grammar')
                text(e.get('name'),ident+'.name',80)
                if t=='mechanics-proposal':
                    exact(e,MK,ident)
                    check(e['status']=='proposed-not-implemented',ident+': status')
                    for k in ('designIntent','stackingRule','cancellationRule','repeatUseRule','failureOrRecovery','balanceRationale'):text(e[k],ident+'.'+k)
                    for k in ('prerequisites','testScenarios','implementationNeeds'):
                        for s in arr(e[k],k):text(s,ident+'.'+k)
                    check(3<=len(e['testScenarios'])<=6,ident+': 3-6 tests')
                    for bid in e['existingRuleReferences']:resolve(bid,'baseline')
                    for eff in arr(e['effects'],'effects'):
                        exact(eff,{'target','trigger','change','magnitude','unit','cap','exclusions'},ident+' effect')
                        for k in ('target','trigger','change','unit'):text(eff[k],ident+' effect '+k)
                        for k in ('magnitude','cap'):check(eff[k] is None or type(eff[k]) in (int,float),ident+' effect '+k)
                        for s in arr(eff['exclusions'],'exclusions'):text(s,ident+' exclusion')
                    c=e['costs'];exact(c,{'crowns','materials','workPhases','workOwner'},ident+' costs')
                    check(c['crowns'] is None or (type(c['crowns']) is int and c['crowns']>=0),ident+' crowns')
                    check(c['workPhases'] is None or (type(c['workPhases']) is int and c['workPhases']>0),ident+' phases')
                    text(c['workOwner'],ident+' workOwner')
                    for inp in c['materials']:
                        exact(inp,{'materialId','propertyId','quantity','consumption'},ident+' input')
                        check((inp['materialId'] is None)!=(inp['propertyId'] is None),ident+' input xor')
                        check(inp['quantity'] is None or type(inp['quantity']) is int and inp['quantity']>0,ident+' quantity')
                        check(inp['consumption'] in ('on-start','on-completion','not-consumed','undecided'),ident+' consumption')
                        if inp['materialId']:resolve(inp['materialId'],expect='material')
                        if inp['propertyId']:resolve(inp['propertyId'],expect='property')
                    continue
                exact(e,COMMON|set(fields),ident)
                names.append((t,e['name'].casefold(),e['summary'].casefold()))
                text(e['summary'],ident+'.summary',500)
                check(e['visibility'] in ('private-template','public-template'),ident+' visibility')
                if pid=='ss-private-mystery-foundations':check(e['visibility']=='private-template',ident+' private leak')
                for k in ('tags','ancestryRestrictions','excludedAncestries','continuityWarnings'):
                    for s in arr(e[k],k):text(s,ident+'.'+k)
                check(len(set(e['tags']))==len(e['tags']),ident+' duplicate tags')
                use_tags.update(e['tags']);undeclared.extend(set(e['tags'])-set(vt))
                check(set(e['ancestryRestrictions'])<=ancestry and set(e['excludedAncestries'])<=ancestry,ident+' unknown ancestry')
                check(not set(e['ancestryRestrictions'])&set(e['excludedAncestries']),ident+' overlapping ancestry')
                for q in e['establishedFactRequirements']:
                    exact(q,{'fact','evidenceNeeded'},ident+' fact')
                    text(q['fact'],ident+' fact',300);text(q['evidenceNeeded'],ident+' evidence',300)
                for q in e['references']:
                    reference(q,ident+' reference')
                    if e['visibility']=='public-template' and q.get('id') in registry:
                        target=registry[q['id']][2]
                        check(target.get('visibility')!='private-template',ident+' public reference to private candidate')
                if e['mechanicsProposalId']:resolve(e['mechanicsProposalId'],'pack','mechanic')
                for k,kind in fields.items():dtype(e[k],kind,ident+'.'+k)
                singles={'artifactId':'artifact','reversalRitualId':'ritual','siteId':'site','leadId':'lead','communityId':'community','foundationId':'foundation','sourceOccupationId':'occupation','suggestedStartingPackageId':'package','comparableBaselinePackage':'package','baselineFormId':'spell','firstRoomPurposeId':'room','secondRoomPurposeId':'room'}
                multiples={'propertyIds':'property','principleIds':'principle','componentPropertyIds':'property','neighbouringPrincipleIds':'principle','roomPurposeIds':'room','garmentReferenceIds':'garment'}
                for k,ex in singles.items():
                    if e.get(k):resolve(e[k],expect=ex)
                for k,ex in multiples.items():
                    if k in e:
                        for q in e[k]:resolve(q,expect=ex)
                if 'ancestryId' in e:check(e['ancestryId'] in ancestry,ident+' ancestryId')
                for q in e.get('relatedBaselineIds',[]):resolve(q,'baseline')
                if 'chapters' in e:
                    check(3<=len(e['chapters'])<=4,ident+' chapter count')
                    for c in e['chapters']:
                        exact(c,{'title','proposedActivity','requiredEstablishedFacts','optionalInvitation','possibleResolution'},ident+' chapter')
                        for k in ('title','proposedActivity','optionalInvitation','possibleResolution'):text(c[k],ident+' chapter '+k)
                        for q in arr(c['requiredEstablishedFacts'],'chapter facts'):text(q,ident+' chapter fact')
                if 'choices' in e:
                    check(2<=len(e['choices'])<=4,ident+' choice count')
                    check(len(set(c['id'] for c in e['choices']))==len(e['choices']),ident+' choice IDs')
                    for c in e['choices']:
                        exact(c,{'id','label','residentResponse','establishesFacts','doesNotEstablish'},ident+' choice')
                        for k in ('id','label','residentResponse'):text(c[k],ident+' choice '+k)
                        for k in ('establishesFacts','doesNotEstablish'):
                            for q in arr(c[k],k):text(q,ident+' choice '+k)
        check(len(names)==len(set(names)),'duplicate type/name/summary concept tuple')
        def entries(t):return content.get(t,{}).get('entries',[])
        def dist(t,k,want):
            if t in content:check(dict(Counter(x[k] for x in entries(t)))==want,t+' required distribution')
        dist('equipment-concept','equipmentKind',{'focus':16,'tool':16,'field-gear':8,'accessory':8})
        dist('relationship-development','relationshipTheme',{'friendship':12,'collaboration':10,'romance':8,'friendly-disagreement':6})
        dist('scene-template','intimacyLevel',{'ordinary':20,'playful':20,'flirtatious':25,'romantic':15})
        if 'spell-construction' in content:
            es=entries('spell-construction');check(sum(x['ordinaryOrExceptional']=='exceptional' for x in es)==12,'spell exceptional count')
            check(sum(x['ordinaryOrExceptional']=='ordinary' and set(x['principleIds'])<=set(base['PRINCIPLE_NAMES']) for x in es)==24,'spell existing-principle count')
            check(sum(x['ordinaryOrExceptional']=='ordinary' and not set(x['principleIds'])<=set(base['PRINCIPLE_NAMES']) for x in es)==36,'spell new-principle count')
        if 'furnishing-concept' in content:
            check(sum(x['functionalProposal'] is None for x in entries('furnishing-concept'))==24,'decorative furnishings count')
        if 'encounter-template' in content:check(sum(x['encounterKind']=='confrontation' for x in entries('encounter-template'))==15,'confrontation count')
        if 'personal-arc' in content:check(Counter(x['ancestryId'] for x in entries('personal-arc'))==Counter({a:2 for a in ancestry}),'two arcs per ancestry')
        if 'lead-template' in content:
            check(Counter(x['siteId'] for x in entries('lead-template'))==Counter({x['id']:3 for x in entries('site-template')}),'three leads per site')
            check(Counter(x['leadId'] for x in entries('discovery-template'))==Counter({x['id']:1 for x in entries('lead-template')}),'one discovery per lead')
        if 'contact-role' in content:
            check(Counter(x['communityId'] for x in entries('contact-role'))==Counter({x['id']:4 for x in entries('community-template')}),'four contacts per community')
            check(Counter(x['communityId'] for x in entries('service-concept'))==Counter({x['id']:3 for x in entries('community-template')}),'three services per community')
        if 'foundation-option' in content:check(Counter(x['foundationId'] for x in entries('evidence-fragment'))==Counter({x['id']:6 for x in entries('foundation-option')}),'six evidence fragments per option')
        if 'background-mapping' in content:
            want={k for k,v in foundation.items() if k.startswith('occupation-') and v.get('suggestedCapabilityPackageId')=='unmapped'}
            check(set(x['sourceOccupationId'] for x in entries('background-mapping'))==want,'exact thirty unmapped occupation IDs')
            for x in entries('background-mapping'):
                src=foundation[x['sourceOccupationId']]
                check(set(x['excludedAncestries'])>=set(src['excludedAncestries']),x['id']+' source history exclusion')
        if 'wardrobe-art-brief' in content:
            check(Counter(x['ancestryId'] for x in entries('wardrobe-art-brief'))==Counter({a:1 for a in ancestry}),'one wardrobe brief per ancestry')
            for x in entries('wardrobe-art-brief'):
                clothes=[foundation[g] for g in x['garmentReferenceIds'] if g in foundation]
                slots=[g.get('slot') for g in clothes]
                check(len(slots)==len(set(slots)),x['id']+' conflicting garment slots')
                for g in clothes:
                    check(not (set(g.get('incompatibleSlots',[])) & (set(slots)-{g.get('slot')})),x['id']+' incompatible garments')
        if 'starting-package-concept' in content:
            for x in entries('starting-package-concept'):
                check(len(x['startingKnowledgeCandidates'])==1,x['id']+' one initial principle')
                check(len(x['startingPracticeCandidates'])==1,x['id']+' one initial practice')
                for q in x['startingKnowledgeCandidates']:resolve(q,expect='principle')
                for q in x['startingPracticeCandidates']:check(q in ('archive-focus','careful-assembly','field-notes'),x['id']+' limited basic practice')
                check(x['mechanicsProposalId'] is not None,x['id']+' missing separate starting proposal')
        if 'perk-concept' in content:
            for x in entries('perk-concept'):check(x['mechanicsProposalId'] is not None,x['id']+' missing separate perk proposal')
        for key in ('vocabularyPath','readmePath','validationReportPath'):
            check(not Path(m[key]).is_absolute() and '..' not in Path(m[key]).parts,key+' unsafe path')
            check((path/m[key]).is_file(),key+' missing')
        existing=load_json(path/'validation-report.json');exact(existing,REPORT,'report')
        own_dups=[d for d in all_duplicates if registry[d][0]==pid]
        checks=['Parsed every manifest-listed UTF-8 JSON file with duplicate-key rejection.','Checked exact wrappers, exact field sets, declared types, enums, and bounded string lengths.','Checked manifest counts against both actual entries and every numbered handoff target.','Checked global expansion ID uniqueness and lowercase kebab-case syntax.','Resolved baseline, same-pack, and declared-version dependency references, including typed identifier fields.','Checked mechanics effect/input shapes, material/property input exclusivity, costs, and 3-6 test specifications.','Checked complete vocabulary and unchanged definitions of reused foundations tags.','Checked ancestry registry membership, exclusion overlap, private visibility, and source occupation exclusions.','Checked required per-category distributions and site/community/ancestry/foundation relationships.','Checked chapter/choice nested schemas and duplicate type/name/summary tuples.','Checked cross-pack tag consistency, public/private reference separation, garment compatibility, and bounded starting-package and perk links.']
        if write:
            existing.update(checksPerformed=checks,automatedChecksRun=True,duplicateIds=own_dups,brokenReferences=sorted(set(broken)),undeclaredTags=sorted(set(undeclared)),countShortfalls=short)
            # Structural errors are disclosed separately instead of silently claiming a clean validation.
            existing['knownLimitations']=[s for s in existing['knownLimitations'] if not s.startswith('STRUCTURAL ERROR:')]+['STRUCTURAL ERROR: '+s for s in bad]
            (path/'validation-report.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n')
        packerrs=bad+['broken: '+s for s in broken]+['undeclared tag: '+s for s in undeclared]+short+own_dups
        errors.extend([pid+': '+s for s in packerrs])
        summary.append({'packId':pid,'contentRecords':sum(len(o['entries']) for t,o in content.items() if t!='mechanics-proposal'),'mechanicsProposals':len(entries('mechanics-proposal')),'structuralErrors':len(packerrs)})
    # Dependency DAG across delivered packs, with foundations as a terminal dependency.
    done=set();active=set()
    def visit(pid):
        if pid in active:errors.append('Dependency cycle involving '+pid);return
        if pid in done:return
        active.add(pid)
        for d in packs[pid][1]['dependencies']:
            if d['packId'] in packs:visit(d['packId'])
        active.remove(pid);done.add(pid)
    for pid in packs:visit(pid)
    return {'schemaVersion':1,'validationKind':'content-structure-and-references-only','runtimeTestsExecuted':False,'packs':summary,'errors':errors,'totalContentRecords':sum(s['contentRecords'] for s in summary),'totalMechanicsProposals':sum(s['mechanicsProposals'] for s in summary)}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='Validate expansion content data, not gameplay implementation. Run from the integration kit root or provide explicit paths.')
    ap.add_argument('--packs',type=Path,default=Path('packs'))
    ap.add_argument('--source',type=Path,default=Path('reference'))
    ap.add_argument('--foundations',type=Path,default=Path('dependencies/stonework-spellcraft-content-pack'))
    ap.add_argument('--report',type=Path,default=Path('validation-summary.json'))
    ap.add_argument('--no-write-pack-reports',action='store_true',help='Do not update each pack validation report.')
    a=ap.parse_args()
    try:
        report=validate(a.packs,a.source,a.foundations,write=not a.no_write_pack_reports)
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        report={'schemaVersion':1,'validationKind':'content-structure-and-references-only','runtimeTestsExecuted':False,'packs':[],'errors':[str(exc)],'totalContentRecords':0,'totalMechanicsProposals':0}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));sys.exit(bool(report['errors']))
