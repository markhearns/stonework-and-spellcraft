"""Optional authored social routes: no automatic time, assignments or resource rewards."""
from copy import deepcopy
from household_chapter_content import PROFILES, ACTIVITIES, PAIRS, SPECIALIST_VOICES, ACTIVITY_THOUGHTS, PERSPECTIVES, PAIR_FOLLOWUPS


def initialize(s):
    s.setdefault('householdChapters',{'personal':{},'activities':{},'pairs':{},'specialists':{}})


def memory_ids(s,who):
    records=s.get('householdChapters',{})
    return ['home:'+group+':'+key for group in ('personal','activities','pairs','specialists')
            for key,record in records.get(group,{}).items() if who in record.get('participants',[])]


def presence(s,people):
    import game as g
    members=g.household_members(s);reasons=[]
    for who in people:
        name=g.character_profile(s,who)['name'] if who in members else who.capitalize()
        if who not in members:reasons.append(name+' must be a castle resident.')
        elif not g.character_at_castle(s,who):reasons.append(name+' must return home.')
    if not g.character_at_castle(s,'founder'):reasons.append('Your scholar must return home.')
    return reasons


def room_reasons(s,room):
    import headquarters as h
    return [] if h.ready(s,room) else ['Restore '+h.ROOMS[room]['name']+' first.']


def personal_rows(s,who):
    import headquarters as h
    records=s.get('householdChapters',{}).get('personal',{});looks=s.get('outfitProgression',{}).get(who,{}).get('invitations',{})
    rows=[]
    for stage,definition in enumerate(PROFILES[who]['beats']):
        key=who+':'+str(stage);previous=records.get(who+':'+str(stage-1));reasons=presence(s,[who])
        if stage and not previous:reasons.append('Share “'+PROFILES[who]['beats'][stage-1]['title']+'” first.')
        if stage==2 and '2' not in looks:reasons.append('Share her relaxed wardrobe invitation first; this scene provides a new moment afterwards.')
        if stage==3 and '3' not in looks:reasons.append('Share her daring wardrobe invitation first.')
        room='library' if stage==1 else 'common-room'
        preferred=PROFILES[who]['room']
        if stage==3 and h.ready(s,preferred):room=preferred
        rows.append({'id':key,**deepcopy(definition),'personId':who,'participants':[who],'roomId':room,'stage':stage,
                     'memory':deepcopy(records.get(key)),'callback':previous['response'] if previous else None,
                     'blockers':reasons,'available':not reasons and key not in records})
    return rows


def activity_rows(s,who):
    records=s.get('householdChapters',{}).get('activities',{});rows=[]
    for room,d in ACTIVITIES.items():
        key=who+':'+room;reasons=presence(s,[who])+room_reasons(s,room)
        p=PROFILES[who]
        rows.append({'id':key,**deepcopy(d),'personId':who,'participants':[who],'roomId':room,'choices':{
            'quiet':{'label':'Enjoy the quieter company','response':ACTIVITY_THOUGHTS.get(who,{}).get(room,PERSPECTIVES.get(who,p['thanks']))},
            'playful':{'label':'Invite a little light-hearted company','response':p['tease']}},
            'memory':deepcopy(records.get(key)),'blockers':reasons,'available':not reasons,'repeatable':True})
    return rows


def pair_rows(s):
    import game as g
    import outfit_progression as outfits
    members=g.household_members(s);records=s.get('householdChapters',{}).get('pairs',{});rows=[]
    for a,b,room,title,opening,c1,r1,c2,r2,follow,reply in PAIRS:
        if a not in members and b not in members:continue
        base=a+'+'+b;first=records.get(base+':0');later=PAIR_FOLLOWUPS.get((a,b),(c1,r1,c2,r2))
        for stage in (0,1):
            key=base+':'+str(stage);reasons=presence(s,[a,b])+room_reasons(s,room)
            for who in (a,b):
                if not outfits.memories(s,who):reasons.append('Share a personal moment with '+who.capitalize()+' first.')
            if stage and not first:reasons.append('Join “'+title+'” first.')
            if stage and first and not any(k.startswith(a+':') and v.get('lastShared',v).get('sequence',0)>first.get('sequence',0) or k.startswith(b+':') and v.get('lastShared',v).get('sequence',0)>first.get('sequence',0) for k,v in s.get('householdChapters',{}).get('activities',{}).items()):
                reasons.append('Share a new room activity with either participant after their first conversation.')
            rows.append({'id':key,'participants':[a,b],'roomId':room,'title':title if not stage else follow,
                         'opening':opening if not stage else reply,'callback':first['response'] if stage and first else None,
                         'choices':{'method':{'label':c1 if not stage else later[0],'response':r1 if not stage else later[1]},
                                    'meaning':{'label':c2 if not stage else later[2],'response':r2 if not stage else later[3]}},
                         'memory':deepcopy(records.get(key)),'blockers':reasons,'available':not reasons and key not in records})
    return rows


def specialist_rows(s,who):
    import resident_specialties as specialties
    if who not in SPECIALIST_VOICES:return []
    d=specialties.SPECIALTIES[who];records=s.get('householdChapters',{}).get('specialists',{});rows=[]
    complete=specialties.active(s,who)
    for stage,line in enumerate(SPECIALIST_VOICES[who]):
        key=who+':'+str(stage);reasons=presence(s,[who])+room_reasons(s,d['room'])
        if stage and not complete:reasons.append('Complete '+d['name']+' through Headquarters rooms.')
        if stage==2 and who+':1' not in records:reasons.append('Share the installation conversation first.')
        if stage==0 and who+':0' not in s.get('livingStories',{}).get('memories',{}):reasons.append('Share her first Resident stories conversation first.')
        if stage==2 and who+':1' in records:
            activity=s.get('householdChapters',{}).get('activities',{}).get(who+':'+d['room'],{})
            if activity.get('lastShared',activity).get('sequence',0)<=records[who+':1'].get('sequence',0):
                reasons.append('Share a room activity here after the installation conversation; a repeat visit also counts for this follow-up.')
        previous=records.get(who+':'+str(stage-1))
        rows.append({'id':key,'participants':[who],'personId':who,'roomId':d['room'],'title':('Plan: ','Installed: ','Life with: ')[stage]+d['name'],
                     'opening':line,'callback':previous['response'] if previous else None,'benefit':d['benefit'],
                     'choices':{'craft':{'label':'Ask how the improvement helps with her work','response':('She draws the proposed arrangement beside the costed plan. Nothing is ordered yet. Together you review what it will make possible: '+d['benefit']) if stage==0 else SPECIALIST_VOICES[who][2]},
                                'company':{'label':'Tell her what working together means to you','response':PROFILES[who]['thanks']}},
                     'memory':deepcopy(records.get(key)),'blockers':reasons,'available':not reasons and key not in records,
                     'complete':complete,'projectId':'specialty-'+who})
    return rows


def view(s):
    import game as g
    import outfit_progression as outfits
    members=g.household_members(s);people=[]
    for who,p in PROFILES.items():
        if who not in members:continue
        route=personal_rows(s,who);next_scene=next((r for r in route if not r['memory']),None)
        invites=s.get('outfitProgression',{}).get(who,{}).get('invitations',{})
        # The invitation is the next step when it is actionable, not a circular blocked scene.
        next_invite=next((tier for tier in ('2','3') if tier not in invites and not outfits.blockers(s,who,tier)),None)
        people.append({'id':who,'name':g.character_profile(s,who)['name'],'preferredRoom':p['room'],
                       'personal':route,'activities':activity_rows(s,who),'specialists':specialist_rows(s,who),
                       'completed':sum(bool(r['memory']) for r in route),'nextSceneId':next_scene['id'] if next_scene else None,
                       'nextInvitation':next_invite,'nextHint':('Share her '+('relaxed' if next_invite=='2' else 'daring')+' wardrobe invitation.' if next_invite else 'All four personal chapters are remembered.' if not next_scene else 'Next: '+next_scene['title']+'. '+(' '.join(next_scene['blockers']) if next_scene['blockers'] else 'Ready whenever you want company.'))})
    return {'people':people,'pairs':pair_rows(s)}


def apply(s,a):
    groups={'share-personal-chapter':'personal','share-room-activity':'activities','share-household-pair':'pairs','share-specialist-chapter':'specialists'}
    kind=a.get('type')
    if kind not in groups:return False
    import game as g
    key=a.get('sceneId');choice=a.get('choice');who=a.get('characterId')
    g.require(isinstance(key,str) and isinstance(choice,str),'Choose a known scene and response.')
    if kind=='share-household-pair':rows=pair_rows(s)
    else:
        g.require(isinstance(who,str) and who in PROFILES,'Choose an authored companion.')
        rows={'personal':personal_rows,'activities':activity_rows,'specialists':specialist_rows}[groups[kind]](s,who)
    row=next((r for r in rows if r['id']==key),None)
    g.require(row is not None,'That scene does not belong to this invitation.')
    g.require(row['available'],' '.join(row['blockers']) or 'This moment is already remembered; you can reread it any time.')
    g.require(choice in row['choices'],'Choose one of the offered responses.')
    initialize(s);all_records=s['householdChapters'];sequence=1+max((r.get('lastShared',r).get('sequence',0) for group in all_records.values() for r in group.values()),default=0)
    record={'title':row['title'],'opening':row['opening'],'participants':row['participants'],'roomId':row['roomId'],'choice':choice,
            'response':row['choices'][choice]['response'],'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'sequence':sequence}
    if kind=='share-room-activity' and key in all_records['activities']:
        original=all_records['activities'][key]
        original['lastShared']=record
        original['visits']=min(999,original.get('visits',1)+1)
    else:all_records[groups[kind]][key]=record
    import relationships
    relationships.remember(s,'chapter:'+groups[kind]+':'+key,{**record,'participants':['founder',*record['participants']]})
    g.add_journal(s,'Shared '+row['title']+'. '+record['response'])
    return True
