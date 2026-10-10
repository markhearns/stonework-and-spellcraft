"""One-time authored replacement and chamber consolidation. No rewards replayed."""
from copy import deepcopy
import re


def migrate(s):
    import game as g, local_encounters, character_builds, containment
    # Replace only the authored identity; content/custom character names are not identity keys.
    def key(text):
        return re.sub(r'(?<![A-Za-z])maren(?![A-Za-z])','koharu',text)
    def remap(value):
        if isinstance(value,dict):
            return {key(k):remap(v) for k,v in value.items()}
        if isinstance(value,list):return [remap(v) for v in value]
        if isinstance(value,str):return key(value).replace('Maren','Koharu')
        return value
    has_old='maren' in s.get('people',{}) or 'maren' in s.get('localEncounters',{})
    if has_old:
        rewritten=remap(s);s.clear();s.update(rewritten)
        fresh=local_encounters.definition(s,'koharu')
        if 'koharu' in s.get('localEncounterCandidates',{}):s['localEncounterCandidates']['koharu']=deepcopy(fresh)
        if 'koharu' in s.get('people',{}):
            old=s['people']['koharu'];revision=old.get('identityRevision',1)
            old.update(deepcopy(fresh['profile']));old['identityRevision']=revision+1
            # Carry earned increases onto her new baseline; training and expenditure stay saved.
            record=s.get('characterBuilds',{}).get('koharu')
            if record:
                previous=dict(zip(character_builds.ATTRIBUTES,(5,7,5,6,4,3)))
                record['attributes']={a:min(10,base+max(0,record['attributes'][a]-previous[a])) for a,base in character_builds.baseline('koharu').items()}
                if 'powerful-frame' in record['perks']:
                    record['perks'].remove('powerful-frame')
                    if 'patient-hands' not in record['perks']:record['perks'].append('patient-hands')
            project=s.get('trainingProjects',{}).get('koharu')
            if project and project.get('targetId')=='powerful-frame':
                if record and 'patient-hands' in record['perks']:
                    s['trainingProjects']['koharu']=None
                    if g.character_assignment(s,'koharu')=='training':g.set_character_assignment(s,'koharu','rest')
                else:project['targetId']='patient-hands'
        # Old authored artwork does not depict the new person. Keep custom files in backup storage.
        for bucket in ('assetOverrides','assetHistory'):
            for asset in list(s.get(bucket,{})):
                if 'koharu' in asset:s[bucket].pop(asset)
    # Horned local people use ordinary introductions, including already reviewed plans.
    profiles=list(s.get('people',{}).values())
    for bucket in ('reviewedCandidates','localEncounterCandidates'):
        profiles.extend(c['profile'] for c in s.get(bucket,{}).values())
    for profile in profiles:
        if profile.get('ancestryLabel') in ('Oni','Ogrekin'):
            profile['ancestryLabel']='Ogrekin'
            for field in ('role','appearanceDescription','origin','introduction'):
                if isinstance(profile.get(field),str):profile[field]=re.sub(r'\boni\b','ogrekin',re.sub(r'\bOni\b','Ogrekin',profile[field]))
            profile['arrivalMethod']='recruitment'
            if isinstance(profile.get('generationIngredients'),dict):profile['generationIngredients'].update(ancestry='Ogrekin',arrivalMethod='recruitment')
        if profile.get('personId')=='kaede' and profile.get('identitySource')=='authored-local-encounter':
            profile['origin']=local_encounters.PEOPLE['kaede']['origin']
    data=s.get('containment',{})
    if not data:return
    old=data['chambers'];new={}
    for ward in ('heat','echo'):
        target=ward+'-1';ready=[k for k,v in old.items() if k.startswith(ward+'-') and v['status']=='ready']
        new[target]={'status':'ready' if ready else 'sealed'}
        # Retired completed duplicates return their fixed construction costs once.
        for extra in ready[1:]:
            d=containment.CHAMBERS[target];s['sharedFunds']+=d['costCrowns']
            for item,count in d['materials'].items():s['materialInventory'][item]+=count
        for case in data['cases'].values():
            if (case.get('chamberId') or '').startswith(ward+'-'):case['chamberId']=target
        p=data.get('project')
        if p and p['kind']=='chamber' and p['targetId'].startswith(ward+'-'):
            if ready:containment.cancel(s)
            else:p['targetId']=target
    data['chambers']=new
    for bucket in ('assetOverrides','assetHistory'):
        for asset in list(s.get(bucket,{})):
            if re.fullmatch(r'(heat|echo)-[2-5]',asset):s[bucket].pop(asset)
