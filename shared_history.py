"""Concrete follow-up invitations drawn from completed work and actual field events."""
from copy import deepcopy
from conversation_voice import voice

TOPICS={
 'commission:translate':'“A readable translation still needs to show where a damaged place name is uncertain. I do not want the next traveller following our best guess as though it were a signpost.”',
 'commission:restore':'“The lantern has to survive the road, not just light up on a workbench. The binding was the part worth checking before delivery.”',
 'commission:remedies':'“The labels matter as much as the contents. Someone opening a medicine kit in a hurry needs to know which dressing to reach for.”',
 'commission:ward':'“The client is doing the installation. Our repair instructions need to say which connection to check first.”',
 'project:iona':'“The detours are marked now. If the main road is blocked, I can lead an objective patrol around its enemy after we clear the site obstacle.”',
 'project:zahra':'“The gauges give me the same fit every time. I can tighten the straps before a patrol without asking everyone to stand still while I measure them again.”',
 'project:sylva':'“The divided beds keep each cutting in the soil it needs. Specimens from observation and repair trips can now supply more ivy.”',
 'objective:escort':'“The crate reached its destination. For the next delivery, I want the route notes to say where a laden party can stop safely.”',
 'objective:rescue':'“The surveyor is home. The route record needs to be readable by someone who has never been down that passage.”',
 'objective:observe':'“We have completed the griffin study. Let us keep the observations separate from any explanation we still need to test.”',
 'objective:repair':'“The crossing is usable again. The next inspection should check the latch as well as the surface people walk on.”',
 'library-lamp':'“The lamp lets us read the fine survey marks. I want to compare those marks with the routes in the cylinder before claiming we know where every crossing went.”',
}

def topic(e):
    source=e.get('source','')
    key=':'.join(source.split(':')[:2]) if source.startswith('commission:') else source
    return TOPICS.get(key,'“The report records who covered the others. Keep that beside the outcome; a successful return alone does not explain the protection.”' if e['kind']=='protection' else '')


def saved(s):return s.get('sharedHistory',{'events':{},'memories':{},'deferred':[]})


def record(s,key,people,title,detail,kind):
    import game as g
    actual=list(dict.fromkeys(w for w in people if w in g.household_members(s)))
    r=s.setdefault('sharedHistory',deepcopy(saved(s)))
    # A fixed category per companion keeps repeated paid work from filling the feed.
    for who in actual:
        if who=='founder':continue
        event_id=who+':'+kind
        if event_id in r['events']:continue
        r['events'][event_id]=dict(id=event_id,source=key,personId=who,people=actual,title=title,detail=detail,
                                  kind=kind,day=s['dayNumber'],phase=s['currentDayPhase'])


def returned(s,run,report):
    if not report['complete']:return
    import game as g
    for who,stats in run.get('contributions',{}).items():
        if stats.get('protected',0):
            record(s,'patrol:'+str(run['id']),run['party'],'Protection on '+run['name'],
                   g.character_profile(s,who)['name']+' intercepted attacks that would have caused '+str(stats['protected'])+' vitality loss to companions.','protection')
    if run.get('objectiveId'):
        record(s,'objective:'+run['objectiveId'],run['party'],'Completed '+run['name'],report.get('objectiveText','The party completed its agreed objective.'),'fieldwork')


def view(s,who=None):
    import game as g, romance
    r=saved(s);rows=[]
    for key,e in r['events'].items():
        if who and e['personId']!=who:continue
        if e['personId'] not in g.household_members(s):continue
        people=list(dict.fromkeys(['founder']+e['people']))
        b=[] if all(g.character_at_castle(s,w) for w in people) else ['Bring everyone named in this memory home before discussing it.']
        name=g.character_profile(s,e['personId'])['name']
        v=voice(e['personId'])
        opening=name+' reads the completed record with you. '+e['detail']+' '+topic(e)+' '+v['review']
        party=list(dict.fromkeys(['founder']+e['people']))[:4]
        party_names=', '.join(g.character_profile(s,w)['name'] for w in party)
        contributors=', '.join(g.character_profile(s,w)['name'] for w in e['people'])
        choices=[dict(id='plan',label='Suggest this group for another patrol',reply=v['proposal']+' You put '+party_names+' on the proposed party list.',effect='Saves this party for review in Field patrols: '+party_names+'. Does not depart or change assignments.'),
                 dict(id='credit',label='Record the participants and this result',reply=v['credit']+' You record '+contributors+' beside the completed result: '+e['detail'],effect='Saves this conversation in the journal. No work, training or relationship reward.')]
        if romance.level(s,e['personId'])>=1:
            choices.append(dict(id='affection',label='Thank her and ask to sit together',reply=v['affection'],effect='Saves an affectionate conversation; does not change relationship progress.'))
        else:choices.append(dict(id='company',label='Put the report aside and share a drink',reply=v['company'],effect='Saves a friendly conversation; does not change relationship progress.'))
        rows.append(dict(**deepcopy(e),opening=opening,choices=choices,blockers=b,memory=deepcopy(r['memories'].get(key)),deferred=key in r['deferred']))
    return rows


def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind not in ('history-share','history-defer','history-restore'):return False
    key=a.get('eventId');g.require(isinstance(key,str),'Choose a remembered event.')
    e=next((x for x in view(s) if x['id']==key),None);g.require(e,'Choose an available follow-up.')
    r=s.setdefault('sharedHistory',deepcopy(saved(s)))
    if kind!='history-share':
        if kind=='history-defer' and key not in r['deferred']:r['deferred'].append(key)
        if kind=='history-restore' and key in r['deferred']:r['deferred'].remove(key)
        return True
    g.require(not e['memory'],'This conversation is already remembered. Read it without replaying its effects.')
    g.require(not e['blockers'],' '.join(e['blockers']))
    option=next((c for c in e['choices'] if c['id']==a.get('choiceId')),None);g.require(option,'Choose a listed response.')
    text=e['opening']+' '+option['reply']
    r['memories'][key]=dict(text=text,choice=option['id'],day=s['dayNumber'],people=e['people'])
    if option['id']=='plan':r['suggestedParty']=list(dict.fromkeys(['founder']+e['people']))[:4]
    if key in r['deferred']:r['deferred'].remove(key)
    g.add_journal(s,e['title']+': '+text)
    return True


def context(s,who):
    return [deepcopy(m) for key,m in saved(s)['memories'].items() if key.startswith(who+':') or who in m['people']][-4:]
