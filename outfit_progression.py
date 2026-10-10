"""Authored wardrobe invitations grounded in remembered relationship events."""
from copy import deepcopy
import json
from pathlib import Path

CATALOGUE=json.loads(Path(__file__).with_name('outfit_catalogue.json').read_text())

def initialize(s):
    s.setdefault('outfitProgression',{})

def memories(s,who):
    from resident_moments import MOMENTS
    events={key for key in s.get('livingStories',{}).get('memories',{}) if key.startswith(who+':')}
    events.update('moment:'+key for key,r in s.get('residentMoments',{}).items() if r.get('status')=='complete' and who in MOMENTS.get(key,{}).get('participants',[]))
    events.update('story:'+key for key,r in s.get('personalStories',{}).items() if r.get('ownerId')==who and r.get('status')=='complete' and r.get('sceneStatus')=='remembered')
    events.update('household:'+key for key,r in s.get('householdScenes',{}).items() if r.get('status')=='remembered' and who in r.get('participants',[]))
    import household_chapters
    events.update(household_chapters.memory_ids(s,who))
    events.update('conversation:'+key for key,record in s.get('socialLife',{}).get('memories',{}).items() if who in record.get('participants',[]))
    events.update('relationship:'+key for key,r in s.get('relationships',{}).get('memories',{}).items() if who in r.get('participants',[]))
    events.update('participation:'+key for key,r in s.get('companionParticipation',{}).get('memories',{}).items() if who in r.get('participants',[]))
    for q in s.get('characterQuests',{}).get('records',{}).values():
        if q['who']==who:
            source=q['id'] if q['kind'] in ('personal','ambition') else 'request:'+who+':'+str(q['template'])
            events.update('quest:'+source+':'+m['stage'] for m in q['memories'])
    for group in ('memories','dates'):
        events.update('romance:'+group+':'+key for key,r in s.get('romance',{}).get(group,{}).items() if who in r['participants'])
    events.update('lantern:'+key for key,r in s.get('lanternAdventure',{}).get('memories',{}).items() if who in r['participants'])
    events.update('customization:'+key for key,r in s.get('customization',{}).get('memories',{}).items() if who in r['participants'])
    for group in ('memories','codas','fieldMemories'):
        events.update('saga:'+group+':'+key for key,r in s.get('householdSagas',{}).get(group,{}).items() if who in r['participants'])
    for site,r in s.get('partyJourneys',{}).items():
        events.update('journey:'+site+':'+key for key,m in r['memories'].items() if who in m['participants'])
    events.update('almanac:'+key for key,r in s.get('companionAlmanac',{}).get('memories',{}).items() if who in r.get('participants',[]))
    events.update('thread:'+key for key,r in s.get('companionThreads',{}).get('records',{}).items() if r.get('completed') and who in r.get('participants',[]))
    return sorted(events)

def blockers(s,who,tier):
    import game as g
    reasons=[]
    if who not in g.household_members(s):reasons.append('She must choose to live at the castle first.')
    if not all(g.character_at_castle(s,p) for p in ('founder',who)):reasons.append('Return home together to share this invitation.')
    record=s.get('outfitProgression',{}).get(who,{})
    events=memories(s,who)
    if tier=='2' and not events:reasons.append('Share one remembered resident conversation, household moment or personal-story scene.')
    if tier=='3':
        accepted=record.get('invitations',{}).get('2')
        if not accepted:reasons.append('Share her relaxed-outfit invitation first.')
        if len(events)<3:reasons.append('Share three distinct remembered moments together ('+str(len(events))+'/3).')
        if accepted and not set(events)-set(accepted.get('evidence',[])):reasons.append('Share a new remembered moment after her relaxed-outfit invitation.')
    return reasons

def view(s):
    import game as g
    from household_chapter_content import PROFILES
    result={}
    for who,looks in CATALOGUE.items():
        if who not in g.household_members(s):continue
        record=s.get('outfitProgression',{}).get(who,{})
        rows=[]
        for tier,d in looks.items():
            unlocked=tier in record.get('invitations',{})
            reasons=blockers(s,who,tier)
            rows.append({**d,'tier':tier,'unlocked':unlocked,'blockers':reasons,'canInvite':not unlocked and not reasons,
                         'invitation':PROFILES[who]['relaxed' if tier=='2' else 'daring'],
                         'responses':{'warm':'Tell her you enjoy being comfortable together','playful':'Return her flirtation'},
                         'memory':deepcopy(record.get('invitations',{}).get(tier))})
        selected=record.get('selected')
        result[who]={'name':g.character_profile(s,who)['name'],'selected':selected,'portraitId':looks[selected]['id'] if selected in looks else who,
                     'memories':len(memories(s,who)),'looks':rows,'canChange':all(g.character_at_castle(s,p) for p in ('founder',who))}
    return result

def current(s,who):
    selected=s.get('outfitProgression',{}).get(who,{}).get('selected')
    return deepcopy(CATALOGUE.get(who,{}).get(selected))

def apply(s,a):
    if a.get('type') not in ('accept-outfit-invitation','choose-outfit'):return False
    import game as g
    who=a.get('characterId');tier=a.get('tier')
    g.require(isinstance(who,str) and who in CATALOGUE and who in g.household_members(s),'Choose an established household companion.')
    g.require(all(g.character_at_castle(s,p) for p in ('founder',who)),'Return home together to discuss clothing.')
    g.require(tier is None or isinstance(tier,str) and tier in CATALOGUE[who],'Choose an existing outfit.')
    if a['type']=='accept-outfit-invitation':
        g.require(tier is not None,'Choose an invitation.')
        g.require(tier not in s.get('outfitProgression',{}).get(who,{}).get('invitations',{}),'This invitation is already remembered.')
        reasons=blockers(s,who,tier);g.require(not reasons,' '.join(reasons))
        from household_chapter_content import PROFILES
        answer=a.get('responseChoice','warm')
        g.require(isinstance(answer,str) and answer in ('warm','playful'),'Choose a warm or playful response.')
        record=s.setdefault('outfitProgression',{}).setdefault(who,{'selected':None,'invitations':{}})
        record['invitations'][tier]={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'evidence':memories(s,who),'choice':answer,'opening':PROFILES[who]['relaxed' if tier=='2' else 'daring'],'response':PROFILES[who]['thanks' if answer=='warm' else 'tease']}
        g.add_journal(s,g.character_profile(s,who)['name']+' shared her '+CATALOGUE[who][tier]['name']+' wardrobe invitation. The outfit is available; wearing it remains a separate choice.')
    else:
        g.require(tier is None or tier in s.get('outfitProgression',{}).get(who,{}).get('invitations',{}),'Share her invitation before choosing this outfit.')
        record=s.setdefault('outfitProgression',{}).setdefault(who,{'selected':None,'invitations':{}})
        record['selected']=tier
        import character_customization
        character_customization.clear_style(s,who)
        s.get('residentCurrentStyles',{}).pop(who,None)
    return True


def clear_selection(s,who):
    record=s.get('outfitProgression',{}).get(who)
    if record:record['selected']=None
