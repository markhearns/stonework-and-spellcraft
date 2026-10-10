"""Bounded, data-only content packs. No extraction, executable predicates or rule grants."""
import base64
from collections import Counter
from copy import deepcopy
import hashlib
import io
import math
import json
from pathlib import PurePosixPath
import random
import re
import zipfile

REGISTRY = dict(zip(
    'human high-elf dark-elf drow catfolk bovinefolk orc wolfkin demon seraph elemental vampire fae djinn dragonkin spirit dryad nymph kitsune ogrekin golem'.split(),
    ['Human','High elf','Dark elf','Drow','Catfolk','Bovinefolk','Orc','Wolfkin','Demon','Seraph','Elemental','Vampire','Fae','Djinn','Dragonkin','Spirit','Dryad','Nymph','Kitsune','Ogrekin','Golem']))
RESERVED=set('eris selene mira tamsin iona aurelia neris sabine koharu zahra fenna kaede'.split())
PACKAGES={'archive-reader','light-maker','water-worker','unmapped'}
SLOTS='top bottom dress outer-layer footwear accessory'.split()
# Compact schema: string lengths or (minimum, maximum) array lengths.
COMMON={'id':80,'label':80,'description':600,'expressionExamples':(1,3),'compatibleTags':(0,100),'conflictsWith':(0,100),'ancestryRestrictions':(0,21),'excludedAncestries':(0,21),'usageNotes':600}
SHARED={
 'personality-nuance':('personality-nuances',50,{'coreTrait':600,'counterpoint':600}),
 'value-boundary':('values-boundaries',40,{'kind':40,'importance':40,'welcomes':(0,30),'declines':(0,30),'communicationStyle':600}),
 'habit-mannerism':('habits-mannerisms',50,{'trigger':600,'frequency':40,'avoidOveruse':600}),
 'conversational-voice':('conversational-voices',25,{'sentenceRhythm':600,'directness':40,'humourStyle':600,'metaphorDomains':(0,100),'avoid':(0,30)}),
 'occupation-background':('occupations-backgrounds',40,{'occupation':60,'originOutline':600,'experienceThemes':(0,100),'naturalAmbitionTags':(0,100),'suggestedCapabilityPackageId':40,'historyMode':40}),
 'ambition':('ambitions',50,{'personalMotivation':600,'scope':40,'possibleFirstSteps':(2,4),'possibleComplications':(1,3),'satisfyingOutcomes':(1,3)}),
 'social-flirtation-style':('social-flirtation-styles',25,{'mode':40,'suitableContexts':(0,30),'signalsToProceed':(0,30),'signalsToPause':(0,30),'boundaryResponse':600}),
 'household-interaction':('household-interactions',50,{'participants':40,'openingInvitation':600,'requirements':(0,30),'possibleResponses':(2,4),'possibleDevelopments':(2,4),'continuityWarnings':(0,30)}),
 'clothing-component':('clothing-components',60,{'slot':40,'materials':(1,3),'colours':(1,3),'silhouette':600,'coverage':600,'anatomyAccommodations':(0,30),'occasionTags':(0,100),'incompatibleSlots':(0,6)}),
 'ensemble':('ensembles',30,{'componentIds':(1,12),'occasionTags':(0,100),'stylingNotes':600,'anatomyAccommodations':(0,30)}),
 'story-development-pattern':('story-development-patterns',25,{'opening':600,'complication':600,'meaningfulChoice':600,'possibleResolutions':(2,4),'followupInvitation':600,'requiredEstablishedFacts':(0,30),'continuityWarnings':(0,30)})}
NAME={'id':80,'name':40,'styleTags':(0,100)}
STORY={'id':80,'title':80,'premise':600,'personalMotivation':600,'openingHook':600,'possibleDevelopments':(2,4),'backgroundTags':(0,100),'themeTags':(0,100),'toneTags':(0,100),'requirements':(0,30),'continuityWarnings':(0,30)}
APPEARANCE={'id':80,'summary':500,'skin':600,'hair':600,'eyes':600,'build':600,'ancestryFeatures':(1,30),'distinctiveDetails':(1,3),'styleTags':(0,100)}
ENUMS={'kind':['value','boundary','preference'],'importance':['central','contextual','minor'],'frequency':['occasional','rare'],'directness':['gentle','plainspoken','forthright'],'suggestedCapabilityPackageId':list(PACKAGES),'historyMode':['lived-background','prospective-vocation','either'],'scope':['small-project','multi-chapter','long-term'],'mode':['social','flirtatious','either'],'participants':['npc-player','two-npcs','small-group'],'slot':SLOTS}
TAG_FIELDS={'compatibleTags','metaphorDomains','experienceThemes'}
MAX_BYTES=6_000_000


def fail(message):
    from game import RuleError
    raise RuleError(message)


def route(key):
    from character_pool import arrival_method
    return arrival_method(REGISTRY.get(key,key))


def decode_archive(encoded):
    """Read only bounded regular JSON/Markdown members; never extract paths."""
    if not isinstance(encoded,str) or len(encoded)>8_000_000:fail('Choose a content ZIP of at most 6 MB.')
    try:
        raw=base64.b64decode(encoded,validate=True)
        if len(raw)>MAX_BYTES:fail('Choose a content ZIP of at most 6 MB.')
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members=archive.infolist()
            if len(members)>100:fail('A pack may contain at most 100 archive entries.')
            if sum(x.file_size for x in members)>MAX_BYTES:fail('Expanded content must fit within 6 MB.')
            files={}
            for member in members:
                path=PurePosixPath(member.filename)
                if path.is_absolute() or '..' in path.parts or '\\' in member.filename or ':' in member.filename or str(path)!=member.filename.rstrip('/'):
                    fail('Unsafe or ambiguous archive path: '+member.filename[:100])
                mode=member.external_attr>>16
                if mode & 0o170000 not in (0,0o100000,0o040000):fail('Archive links and special files are not supported.')
                if member.is_dir():continue
                if member.filename in files:fail('Duplicate archive path: '+member.filename)
                if path.suffix not in ('.json','.md'):fail('Packs contain JSON and Markdown only.')
                files[member.filename]=archive.read(member).decode('utf-8-sig')
            roots=[p[:-len('manifest.json')] for p in files if p.endswith('manifest.json') and PurePosixPath(p).name=='manifest.json']
            if len(roots)!=1:fail('Include exactly one manifest.json.')
            root=roots[0]
            if any(not p.startswith(root) for p in files):fail('Keep all files under the pack folder.')
            return {p[len(root):]:v for p,v in files.items()}
    except (ValueError,UnicodeError,zipfile.BadZipFile,RuntimeError,NotImplementedError):
        fail('The ZIP could not be read as bounded UTF-8 content.')


def validate(files):
    errors=[];warnings=[];entries={};names=set();tags=set();ancestries={};shared={}
    def error(where,msg):
        if len(errors)<150:errors.append(where+': '+msg)
    def pairs(items):
        obj={}
        for k,v in items:
            if k in obj:raise ValueError('duplicate JSON key '+k)
            obj[k]=v
        return obj
    parsed={}
    for path,raw in files.items():
        if path.endswith('.json'):
            try:
                obj=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
                if not isinstance(obj,dict) or type(obj.get('schemaVersion')) is not int or obj['schemaVersion']!=1:raise ValueError('expected object with schemaVersion 1')
                parsed[path]=obj
            except (ValueError,RecursionError) as exc:error(path,str(exc)[:180])
    def string(value,limit):return isinstance(value,str) and bool(value.strip()) and len(value)<=limit and not re.search(r'<[^>]*>|[\x00-\x08\x0b\x0c\x0e-\x1f]',value)
    def shape(obj,schema,where):
        if not isinstance(obj,dict):error(where,'expected an object');return False
        if set(obj)!=set(schema):error(where,'missing or unsupported fields: '+', '.join(sorted(set(obj)^set(schema))));return False
        valid=True
        for k,spec in schema.items():
            v=obj[k]
            if isinstance(spec,tuple):
                ok=isinstance(v,list) and spec[0]<=len(v)<=spec[1] and all(string(t,200 if k=='expressionExamples' else 600) for t in v)
            else:ok=string(v,spec)
            if not ok:error(where,k+' has invalid type, length, or markup');valid=False
        return valid
    vocab=parsed.get('vocabulary.json',{})
    if set(vocab)!={'schemaVersion','tags'}:error('vocabulary.json','missing or unsupported fields')
    rows=vocab.get('tags',[])
    if not isinstance(rows,list):rows=[];error('vocabulary.json','tags must be an array')
    for row in rows:
        if shape(row,{'id':80,'definition':600},'vocabulary'):
            if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',row['id']) or row['id'] in tags:error('vocabulary', 'invalid or repeated tag '+row['id'])
            tags.add(row['id'])
    def records(rows,schema,where):
        if not isinstance(rows,list) or len(rows)>1000:error(where,'expected array of at most 1000 records');return []
        accepted=[]
        for i,obj in enumerate(rows):
            loc=where+'['+str(i)+']'
            if not shape(obj,schema,loc):continue
            key=obj['id']
            if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',key) or key in entries:error(loc,'invalid or repeated ID '+key)
            entries[key]=obj;accepted.append(obj)
            for k,v in obj.items():
                if k.endswith('Tags') or k in TAG_FIELDS:
                    if any(t not in tags for t in v):error(loc,k+' contains undeclared vocabulary tags')
                if k in ENUMS and v not in ENUMS[k]:error(loc,'invalid '+k)
            if 'ancestryRestrictions' in obj:
                allowed=obj['ancestryRestrictions'];excluded=obj['excludedAncestries']
                if any(a not in REGISTRY for a in allowed+excluded) or set(allowed)&set(excluded):error(loc,'invalid ancestry restrictions')
            if obj.get('historyMode')=='lived-background' and 'golem' not in obj['excludedAncestries']:error(loc,'lived backgrounds must exclude golem')
            if obj.get('suggestedCapabilityPackageId')=='unmapped':warnings.append(key+': source package is unmapped; the shipped background mapping is applied at generation when available.')
        return accepted
    manifest=parsed.get('manifest.json',{})
    required={'schemaVersion','packId','packVersion','language','status','ancestries','sharedPools','vocabularyPath','readmePath','validationReportPath'}
    if set(manifest)!=required:error('manifest','missing or unsupported fields')
    for k in ('packId','packVersion','language','status'):
        if not string(manifest.get(k),100):error('manifest','invalid '+k)
    if manifest.get('language')!='en':error('manifest','only en is supported')
    for k,path in [('vocabularyPath','vocabulary.json'),('readmePath','README.md'),('validationReportPath','validation-report.json')]:
        if manifest.get(k)!=path or path not in files:error('manifest','missing or incorrect '+k)
    arows=manifest.get('ancestries',[]);srows=manifest.get('sharedPools',[])
    if not isinstance(arows,list):arows=[];error('manifest','ancestries must be an array')
    if not isinstance(srows,list):srows=[];error('manifest','sharedPools must be an array')
    seen=set();seen_shared=set()
    for row in arows:
        if not isinstance(row,dict) or set(row)!={'ancestryId','ancestryName','arrivalMethod','path','counts'}:error('manifest','malformed ancestry record');continue
        key=row['ancestryId']
        if not isinstance(key,str) or key not in REGISTRY or key in seen:error('manifest','unknown or repeated ancestry');continue
        seen.add(key);path='ancestries/'+key+'.json';obj=parsed.get(path,{})
        if row['path']!=path or row['ancestryName']!=REGISTRY[key] or row['arrivalMethod']!=route(key):error(path,'incorrect registry mapping')
        if set(obj)!={'schemaVersion','ancestryId','ancestryName','arrivalMethod','names','storySeeds','appearanceDescriptions'}:error(path,'missing or unsupported ancestry fields')
        if obj.get('ancestryId')!=key or obj.get('ancestryName')!=REGISTRY[key] or obj.get('arrivalMethod')!=route(key):error(path,'file registry does not match')
        counts={};data={}
        for field,schema,target in [('names',NAME,100),('storySeeds',STORY,25),('appearanceDescriptions',APPEARANCE,25)]:
            result=records(obj.get(field),schema,path+'/'+field);data[field]=result;counts[field]=len(result)
            if len(result)!=target:warnings.append(key+' '+field+': '+str(len(result))+' / '+str(target)+' production target.')
        if row['counts']!=counts or not isinstance(row['counts'],dict) or any(type(v) is not int for v in row['counts'].values()):error(path,'manifest counts do not match records')
        for n in data['names']:
            normalized=n['name'].strip().casefold()
            if normalized in names or normalized in RESERVED:error(n['id'],'duplicate or reserved name')
            names.add(normalized)
        ancestries[key]=data
    for row in srows:
        if not isinstance(row,dict) or set(row)!={'poolType','path','count'}:error('manifest','malformed shared pool');continue
        kind=row['poolType']
        if not isinstance(kind,str) or kind not in SHARED or kind in seen_shared:error('manifest','unknown or repeated shared pool');continue
        seen_shared.add(kind);filename,target,extra=SHARED[kind];path='shared/'+filename+'.json';obj=parsed.get(path,{})
        if row['path']!=path or obj.get('poolType')!=kind or set(obj)!={'schemaVersion','poolType','entries'}:error(path,'incorrect shared wrapper or path')
        data=records(obj.get('entries'),{**COMMON,**extra},path);shared[kind]=data
        if type(row['count']) is not int or row['count']!=len(data):error(path,'manifest count does not match')
        if len(data)!=target:warnings.append(kind+': '+str(len(data))+' / '+str(target)+' production target.')
    if seen!=set(REGISTRY):error('manifest','include all 21 ancestry files (empty arrays are reported as shortfalls)')
    if seen_shared!=set(SHARED):error('manifest','include all 11 shared pool files')
    expected={'manifest.json','vocabulary.json','README.md','validation-report.json'}|{'ancestries/'+a+'.json' for a in REGISTRY}|{'shared/'+v[0]+'.json' for v in SHARED.values()}
    if set(files)!=expected:error('archive','missing or unexpected files')
    for key,obj in entries.items():
        for target in obj.get('conflictsWith',[]):
            if target==key or target not in entries or key not in entries[target].get('conflictsWith',[]):error(key,'missing or asymmetric conflict '+target)
    garments={o['id']:o for o in shared.get('clothing-component',[])}
    for obj in garments.values():
        if any(s not in SLOTS for s in obj['incompatibleSlots']):error(obj['id'],'unknown incompatible slot')
    for ensemble in shared.get('ensemble',[]):
        ids=ensemble['componentIds'];items=[garments[i] for i in ids if i in garments];slots=[g['slot'] for g in items]
        if len(items)!=len(ids) or len(set(ids))!=len(ids):error(ensemble['id'],'missing or duplicate garment reference')
        if any(n>1 and s!='accessory' for s,n in Counter(slots).items()) or ('dress' in slots and any(s in slots for s in ('top','bottom'))):error(ensemble['id'],'incompatible or duplicate clothing slots')
        for garment in items:
            others=[g for g in items if g['id']!=garment['id']]
            if any(g['slot'] in garment['incompatibleSlots'] or g['id'] in garment['conflictsWith'] for g in others):error(ensemble['id'],'conflicting garments')
            for a in REGISTRY:
                if compatible(ensemble,a) and not compatible(garment,a):error(ensemble['id'],'garment ancestry restriction is narrower than ensemble')
    supplied=parsed.get('validation-report.json',{})
    report_fields={'checksPerformed','duplicateIds','duplicateNames','brokenReferences','countMismatches','undeclaredTags','contentWarnings','knownLimitations'}
    if set(supplied)!=report_fields|{'schemaVersion','automatedChecksRun'} or type(supplied.get('automatedChecksRun')) is not bool:
        error('validation-report.json','missing fields or invalid automatedChecksRun flag')
    for field in report_fields:
        value=supplied.get(field)
        if not isinstance(value,list) or any(not string(v,2000) for v in value):error('validation-report.json','invalid '+field)
        elif field not in ('checksPerformed',):
            warnings.extend('Author report · '+field+': '+v for v in value[:25])
    for kind,field,targets in [('value-boundary','kind',{'value':15,'boundary':15,'preference':10}),('social-flirtation-style','mode',{'social':8,'flirtatious':9,'either':8}),('clothing-component','slot',{'top':12,'bottom':12,'dress':10,'outer-layer':8,'footwear':8,'accessory':10})]:
        actual=Counter(o[field] for o in shared.get(kind,[]))
        if actual!=targets:warnings.append(kind+' category targets differ: '+json.dumps(dict(actual),sort_keys=True))
    warnings.append('Structural checks cannot certify age presentation, anatomy, consent, prose originality or narrative coherence. Review the actual content before activation.')
    warnings.append('Interactions, clothing and story patterns require separate review; import alone creates no scenes, outfits, quests or rewards.')
    normalized={'manifest':manifest,'ancestries':ancestries,'shared':shared,'vocabulary':vocab,'readme':files.get('README.md',''),'authorValidationReport':supplied}
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    report={'valid':not errors,'errors':errors,'warnings':warnings,'digest':digest,'packId':manifest.get('packId','Unknown'),'packVersion':manifest.get('packVersion','Unknown'),'recordCount':len(entries),'counts':{'names':len(names),'records':len(entries)},'summary':{'packId':manifest.get('packId'),'packVersion':manifest.get('packVersion'),'digest':digest,'recordCount':len(entries)}}
    return normalized,report


def compatible(obj,ancestry,selected=()):
    return (not obj.get('ancestryRestrictions') or ancestry in obj['ancestryRestrictions']) and ancestry not in obj.get('excludedAncestries',[]) and all(s['id'] not in obj.get('conflictsWith',[]) and obj['id'] not in s.get('conflictsWith',[]) for s in selected)


def select(state,request_id,choices,pack):
    """Backtracking with a fixed work budget; selected records are frozen into drafts."""
    allowed={'contentSource','ancestry','arrivalMethod','bodyMaterial'}
    if set(choices)-allowed:fail('Imported content uses its own backgrounds, personalities and stories. Leave built-in choices automatic.')
    from character_pool import GOLEM_MATERIALS
    if any(not isinstance(value,str) for value in choices.values()):fail('Choose text identifiers for imported ingredients.')
    if choices.get('ancestry') and choices['ancestry'] not in REGISTRY.values():fail('Unknown imported ancestry.')
    if choices.get('arrivalMethod') and choices['arrivalMethod'] not in ('recruitment','summoning','construction'):fail('Unknown arrival path.')
    if choices.get('bodyMaterial') and choices['bodyMaterial'] not in GOLEM_MATERIALS:fail('Unknown golem body material.')
    rng=random.Random(hashlib.sha256(request_id.encode()).digest())
    used=Counter()
    profiles=[c['profile'] for c in state.get('reviewedCandidates',{}).values()]
    for p in profiles:
        used.update(o['id'] for o in p.get('generationIngredients',{}).get('records',{}).values())
    existing=RESERVED|{p['name'].strip().casefold() for p in list(state['people'].values())+profiles}
    wanted=choices.get('arrivalMethod',next((route(k) for k,v in REGISTRY.items() if v==choices.get('ancestry')),'summoning'))
    if choices.get('bodyMaterial') and wanted!='construction':fail('Body material applies only to golems.')
    keys=[k for k,d in pack['ancestries'].items() if route(k)==wanted and choices.get('ancestry',REGISTRY[k])==REGISTRY[k]]
    ancestry_counts=Counter(p.get('ancestryLabel') for p in profiles)
    keys.sort(key=lambda k:-math.log(max(rng.random(),1e-12))*(1+ancestry_counts[REGISTRY[k]]))
    import public_integration
    attempts=0
    for key in keys:
        # Only exact shipped golem appearances use the reviewed body-material mapping.
        golem_looks=public_integration.golem_appearances(pack,choices.get('bodyMaterial','clay')) if key=='golem' else []
        pools={
            'name':[o for o in pack['ancestries'][key]['names'] if o['name'].strip().casefold() not in existing],
            'story':[o for o in pack['ancestries'][key]['storySeeds'] if not o['requirements']],
            **({'appearance':golem_looks} if golem_looks else {} if key=='golem' else {'appearance':pack['ancestries'][key]['appearanceDescriptions']}),
        }
        import public_integration
        effective_backgrounds=public_integration.mapped_backgrounds(pack)
        mapping={'background':'occupation-background','personality':'personality-nuance','value':'value-boundary','habit':'habit-mannerism','voice':'conversational-voice','ambition':'ambition','social':'social-flirtation-style'}
        for label,kind in mapping.items():
            pools[label]=[o for o in (effective_backgrounds if label=='background' else pack['shared'][kind]) if compatible(o,key) and (label!='background' or (o['suggestedCapabilityPackageId']!='unmapped' and (key!='golem' or o['historyMode']=='prospective-vocation')))]
        def search(todo,selected):
            nonlocal attempts
            if not todo:return selected
            label=todo[0]
            candidates=[o for o in pools[label] if compatible(o,key,selected.values())]
            context={t for obj in selected.values() for field,values in obj.items() if field.endswith('Tags') or field in TAG_FIELDS for t in values}
            ranked=sorted(candidates,key=lambda o:-math.log(max(rng.random(),1e-12))*(1+used[o['id']])**2/(1+len(context&set(o.get('compatibleTags',[])))))
            for obj in ranked:
                attempts+=1
                if attempts>12000:fail('No compatible combination found within the selection budget. Review pack restrictions or choose another ancestry.')
                result=search(todo[1:],{**selected,label:obj})
                if result is not None:return result
            return None
        selected=search(list(pools),{})
        if selected:
            mapping_record=public_integration.background_mapping(selected['background']['id'])
            if mapping_record:
                selected['backgroundMapping']=mapping_record
                selected['sourceBackground']=next(o for o in pack['shared']['occupation-background'] if o['id']==selected['background']['id'])
            selected_tags={tag for obj in selected.values() for field,values in obj.items() if field.endswith('Tags') or field in TAG_FIELDS for tag in values}
            definitions={row['id']:row['definition'] for row in pack['vocabulary']['tags'] if row['id'] in selected_tags}
            return {'contentSource':'imported','version':1,'pack':deepcopy(state['activeContentPack']),'ancestry':REGISTRY[key],'arrivalMethod':route(key),'adultAgeYears':rng.randint(18,25),'records':deepcopy(selected),'tagDefinitions':definitions,**({'bodyMaterial':choices.get('bodyMaterial','clay')} if key=='golem' else {})}
    fail('No compatible unused character is available for that arrival path. Check names, unconditional stories, mapped backgrounds and shared traits; golems need prospective vocations.')


def shortened(text,limit):
    if len(text)<=limit:return text
    cut=text[:limit-1].rsplit(' ',1)[0].rstrip(' ,;:')
    return cut+'…'


def offline(selection):
    r=selection['records'];b=r['background'];story=r['story'];name=r['name']['name'].strip()
    if selection['ancestry']=='Golem':
        from character_pool import GOLEM_MATERIALS
        appearance=r['appearance']['summary'] if r.get('appearance') else 'A clearly adult feminine golem made from '+GOLEM_MATERIALS[selection['bodyMaterial']]['appearance']+', with mature proportions and fine handmade joins. An opaque fitted bodice and practical skirt.'
        origin='A proposed companion who will awaken fully adult, with no lived past. Her prospective vocation is '+b['occupation']+'.'
    else:appearance=r['appearance']['summary'];origin=b['originOutline']
    return {'name':name,'adultAgeYears':selection['adultAgeYears'],'ancestryLabel':selection['ancestry'],'occupation':b['occupation'],'personality':shortened(r['personality']['description'],400),'appearanceDescription':appearance,'origin':shortened(origin,400),'ambition':shortened(r['ambition']['description'],300),'accommodationPreference':'private-room','capabilityPackageId':b['suggestedCapabilityPackageId'],'stayPreference':'visit-only','introduction':'“'+name+'. I would like to introduce myself and hear about the household.”','personalTopic':shortened(story['openingHook'],500)}


def narrative_context(profile):
    selection=profile.get('generationIngredients',{})
    if selection.get('contentSource')!='imported':return None
    return {k:deepcopy(v) for k,v in selection['records'].items() if k in ('personality','value','habit','voice','ambition','social','story')}
