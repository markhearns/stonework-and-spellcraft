"""Read-only public bundle review and explicit, non-mechanical scene instantiation."""
import hashlib
import json
import zipfile
from copy import deepcopy
from pathlib import PurePosixPath
import content_packs
import expansion_packs


def foundation_dependency(pack):
    entries={}
    def collect(value):
        if isinstance(value,dict):
            if isinstance(value.get('id'),str):entries[value['id']]=value
            for v in value.values():collect(v)
        elif isinstance(value,list):
            for v in value:collect(v)
    collect(pack)
    return {'manifest':pack['manifest'],'entries':entries,'sourceFiles':{'vocabulary.json':json.dumps(pack.get('vocabulary',{}))}}


def review_bundle(path):
    from game import RuleError
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        if len(members)>500 or sum(i.file_size for i in members)>15_000_000:raise RuleError('Public bundle exceeds review limits.')
        files={}
        for i in members:
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or i.external_attr>>16&0o170000 not in (0,0o100000,0o040000):raise RuleError('Unsafe public bundle path.')
            if i.is_dir():continue
            if i.filename in files:raise RuleError('Repeated public bundle path.')
            files[i.filename]=z.read(i)
    prefix='stonework-and-spellcraft-public-packs/'
    foundation_files={k[len(prefix+'dependencies/stonework-spellcraft-content-pack/'):]:v.decode('utf-8') for k,v in files.items() if k.startswith(prefix+'dependencies/stonework-spellcraft-content-pack/')}
    foundation,fr=content_packs.validate(foundation_files)
    if not fr['valid']:raise RuleError('Bundled foundations failed validation: '+'; '.join(fr['errors'][:3]))
    folders={k.split('/')[2] for k in files if k.startswith(prefix+'packs/')}
    if folders!=set(expansion_packs.PACK_TYPES):raise RuleError('The public bundle must contain exactly the sixteen supported public packs; no private mystery pack.')
    pending={name:{k[len(prefix+'packs/'+name+'/'):]:v.decode('utf-8') for k,v in files.items() if k.startswith(prefix+'packs/'+name+'/')} for name in folders}
    deps=[foundation_dependency(foundation)];reviewed=[];global_ids=set()
    while pending:
        ready=[]
        for name,source in pending.items():
            m=json.loads(source['manifest.json'])
            if all(any(d['manifest']['packId']==ref['packId'] and d['manifest']['packVersion']==ref['packVersion'] for d in deps) for ref in m['dependencies']):ready.append(name)
        if not ready:raise RuleError('Public bundle has missing, mismatched or cyclic dependencies.')
        for name in sorted(ready):
            pack,report=expansion_packs.validate(pending.pop(name),deps)
            if not report['valid']:raise RuleError(name+': '+'; '.join(report['errors'][:4]))
            if global_ids&set(pack['entries']):raise RuleError('Public expansion IDs must be globally unique.')
            global_ids.update(pack['entries']);deps.append(pack);reviewed.append((pack,report))
    return foundation,fr,reviewed


def compose_scene(state,action,pack,report):
    import game as g
    import household_content as h
    key=action.get('recordId');g.require(isinstance(key,str) and pack['types'].get(key)=='scene-template','Choose a staged household scene template.')
    r=pack['entries'][key]
    g.require(r['visibility']=='public-template' and r['mechanicsProposalId'] is None,'This template is not supported for a public conversation.')
    people=action.get('participants');who=action.get('ownerId')
    g.require(isinstance(people,list) and all(isinstance(p,str) for p in people) and len(set(people))==len(people) and who in people,'Choose distinct residents including the inviting resident.')
    limits={'npc-player':(1,1),'two-npcs':(2,2),'small-group':(2,3)}[r['participants']]
    g.require(limits[0]<=len(people)<=limits[1] and all(h.present(state,p) for p in people),'Choose the required household residents and return home together.')
    for person in people:
        ancestry=h.ancestry(state,person)
        g.require(ancestry not in r['excludedAncestries'] and (not r['ancestryRestrictions'] or ancestry in r['ancestryRestrictions']),'This template does not fit every participant’s ancestry.')
    g.require(action.get('templateReviewed') is True,'Review the template against these residents’ established voices and preferences.')
    requirements=[x['fact'] for x in r['establishedFactRequirements']]+['Scene context: '+r['context']]
    evidence=h.review_requirements(requirements,action)
    scene_id=hashlib.sha256(json.dumps([report['digest'],key,sorted(people)]).encode()).hexdigest()[:24]
    g.require(scene_id not in state['householdScenes'],'This group already has this invitation or memory.')
    g.require(sum(r['status'] not in ('remembered','withdrawn') for r in state['householdScenes'].values())<h.MAX_ACTIVE_SCENES,'This campaign supports two hundred unresolved invitations; completed memories remain archived.')
    choices=[{'label':c['label'],'kind':'decline' if c['id'].endswith('-defer') or c['label'].lower().startswith('decline') else 'discussion','reply':c['residentResponse'],'possibleNextStep':'Continue only by another explicit choice; no follow-up is completed.'} for c in r['choices']]
    g.require(any(c['kind']=='decline' for c in choices),'A supported decline branch is required.')
    state['householdScenes'][scene_id]={'title':r['name'],'invitation':r['invitation'],'opening':r['opening'],'participants':people,'ownerId':who,'status':'draft','source':{'packId':report['packId'],'packVersion':report['packVersion'],'digest':report['digest']},'seed':deepcopy(r),'prerequisiteEvidence':evidence,'createdOn':h.stamp(state),'choices':choices}
