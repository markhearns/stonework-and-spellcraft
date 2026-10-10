"""Finite personal ambitions integrated with saved quest work and real rewards."""
from copy import deepcopy
from companion_goal_content import GOALS

LEGACY_CREDIT={'mira':2,'merrin':2,'koharu':1}
CELEBRATION={
 'mira':'“Thank you for checking the evidence with me. Now I would like to enjoy the play without a pencil in my hand.”',
 'tamsin':'“Take another slice before I start cutting it into equal portions. I can enjoy a finished pie without measuring it.”',
 'iona':'“I have spent weeks asking where everything is. Tonight I know exactly where I want to be: at the table with you.”',
 'aurelia':'“I brought a flask for this. The keepers have their instructions; neither of us needs to spend the celebration on duty.”',
 'neris':'“Stay beside the basin a little longer. I would like company for the pleasant part, now that the testing is done.”',
 'sabine':'“A toast to my excellent taste in jewellery. And to your help. I can admit both without surrendering the necklace.”',
 'koharu':'“Did you hear them laugh when the dragon lost his hat? I had to bite my cheek to keep speaking. I am keeping that scene.”',
 'zahra':'“I want one good look at it, then supper. If I stay here I will invent a reason to polish it again.”',
 'fenna':'“Come and sit. I saved us some cake before the relay runners returned. That may have been my finest piece of planning.”',
 'kaede':'“You saw the last touch? I wanted to rush it. I waited. I will be telling that part of the story for quite some time.”',
 'elowen':'“I am relieved. When someone opens this case in a hurry, the labels and doses will be ready. Tonight we can close it.”',
 'nyssara':'“I managed not to interrupt the apprentice. Please include that achievement when you offer the toast.”',
 'sylva':'“I have counted the seeds twice. You may distract me before I decide a third count is necessary.”',
 'velis':'“The driver is paid, the stock is counted and nothing is awaiting my signature. Yes, I am available for a drink.”',
 'rhess':'“My replacement has the watch. I would like to sit somewhere I cannot see the duty board.”',
 'merrin':'“I had forgotten how hard it is to keep reading when people laugh at the previous line. A very pleasant problem to have again.”',
}

def initialize(s):
    s.setdefault('companionGoals',dict(achievements={},history={},kits=0,feastDay=None,meal=None))

def saved(s):return s.get('companionGoals',dict(achievements={},history={},kits=0,feastDay=None,meal=None))
def complete(s,who):return who in saved(s)['achievements']
def current(q):return GOALS[q['who']]['stages'][q['step']]

def definitions(s):
    import game as g,character_quests as quests
    out=[]
    for who,d in GOALS.items():
        if who not in g.household_members(s):continue
        key='ambition:'+who
        old=quests.saved(s)['records'].get(key)
        if old:out.append(old);continue
        legacy=quests.saved(s)['records'].get('personal:'+who,{})
        credit=LEGACY_CREDIT.get(who,0) if legacy.get('status')=='complete' else 0
        outcomes=[dict(obstacle=x['kind'],method='Completed in the earlier personal quest',result=x['result'],creditedFrom='personal:'+who) for x in d['stages'][:credit]]
        out.append(dict(id=key,who=who,kind='ambition',title=d['title'],purpose=d['want'],steps=[x['kind'] for x in d['stages']],
                        opening=d['why'],middle='',ending=d['ending'],flirt='',status='offered',step=credit,pending=None,outcomes=outcomes,memories=[],decisions={},goalVersion=1))
    return out

def opening(q):
    d=GOALS[q['who']]
    if q['status']=='ending':return d['ending']
    if q['status'] not in ('offered','interlude'):return ''
    intro=d['why'] if q['status']=='offered' else ''
    if q['status']=='offered' and q['outcomes']:
        intro='The work recorded in your earlier personal quest is already complete. '+('Merrin wants to bind the performance copy and host the full reading.' if q['who']=='merrin' else 'Koharu’s folding stage and wooden dragon are already made. She wants to finish the remaining cast and prepare a complete show.' if q['who']=='koharu' else 'The recovered script and attribution are complete. Mira wants to prepare the illustrated public edition and its reading.')
    return (intro+'\n\n' if intro else '')+current(q)['line']

def choices(q):
    d=GOALS[q['who']]
    if q['status']=='ending':return {'0':'Celebrate what she has finished.','1':'Ask her to show you the finished result.'}
    if q['status'] in ('offered','interlude'):return {str(i):x[0] for i,x in enumerate(current(q)['choices'])}
    return {}

def reply(q,choice):
    d=GOALS[q['who']]
    if q['status']=='ending':
        return CELEBRATION[q['who']] if choice=='0' else d['proof']+' '+d['after'][0][1]
    stage=current(q);q.setdefault('decisions',{})[str(q['step'])]=int(choice)
    return stage['choices'][int(choice)][1]+'\nNext: '+stage['work']

def enrich_methods(s,q,methods):
    import game as g,headquarters
    d=GOALS[q['who']];stage=current(q)
    shared=[]
    if not headquarters.ready(s,d['room']):shared.append('Restore '+headquarters.ROOMS[d['room']]['name']+' before starting this personal-goal work.')
    if q['who']=='zahra' and q['step']>=2 and not headquarters.ready(s,'enchanting-room'):shared.append('Restore the Enchanting room before inscribing Emberline.')
    crowns=stage['crowns']
    # The return agreement can instead be settled with a direct, declared purchase.
    if q['who']=='sabine' and q['step']==2 and q.get('decisions',{}).get('2')==1:crowns=32
    for key,m in methods.items():
        m['blockers']=shared+m['blockers'];m['crowns']=crowns
        for k,n in stage['materials'].items():m['cost'][k]=m['cost'].get(k,0)+n
        if s['sharedFunds']<crowns:m['blockers'].append('Need '+str(crowns)+' crowns for this stage.')
        for material,n in m['cost'].items():
            if s['materialInventory'].get(material,0)-s.get('materialReserveTargets',{}).get(material,0)<n:
                m['blockers'].append('Need '+str(n)+' unreserved '+g.MATERIALS[material]['name']+'.')
        if key=='patient':
            m['label']=stage['work'];m['detail']='Complete this named stage with preparation and careful work. No minimum skill or spell. The supplies and crowns shown are paid once when work starts.'
        elif key=='skilled':m['label']='Use trained skills: '+stage['title']
        else:
            m['detail']='The prepared spell helps with this stage; the remaining checks are still performed. Stage supplies and spell components are paid once.'
            if not stage['magic']:m['blockers'].append('This stage requires the stated practical test or voluntary agreement; a spell cannot replace it.')
        m['blockers']=list(dict.fromkeys(m['blockers']))
    return methods

def result(q):
    stage=current(q);choice=q.get('decisions',{}).get(str(q['step']))
    text=stage['result']
    if q['who']=='sabine' and q['step']==2 and choice==1:text='The collector accepts a direct purchase and signs the release of the necklace; Sabine’s claim against her former partner is recorded separately.'
    if choice is not None:text+=' Agreed approach: '+stage['choices'][choice][0]+'.'
    return text

def finish(s,q):
    import armoury,game as g
    initialize(s);who=q['who'];d=GOALS[who]
    if complete(s,who):return
    achievement=dict(who=who,title=d['title'],name=d['keepsake'],room=d['room'],proof=d['proof'],dayNumber=s['dayNumber'],phase=s['currentDayPhase'],decisions=deepcopy(q.get('decisions',{})),outcomes=deepcopy(q['outcomes']))
    saved(s)['achievements'][who]=achievement
    if who=='zahra':
        item=armoury.make(s,'steel-sword','zahra',name='Emberline — Zahra’s masterpiece',capacity=2,enchantments={'measured-force':{'id':'measured-force','rank':1}},goalReward='zahra')
        achievement['itemId']=item['id']
    elif who=='sabine':
        item=armoury.make(s,'plain-pendant','sabine',name='Sabine’s fox-clasp necklace',goalReward='sabine')
        achievement['itemId']=item['id']
    elif who=='elowen':saved(s)['kits']+=1
    for person in ('founder',who):g.award_advancement(s,person,'character-goal:'+who,2,d['title'])

def person(s,who):
    if who not in GOALS:return None
    import character_quests as quests,game as g
    if who not in g.household_members(s):return None
    d=GOALS[who];q=next(x for x in definitions(s) if x['who']==who)
    achievement=deepcopy(saved(s)['achievements'].get(who))
    return dict(who=who,title=d['title'],goal=d['want'],why=d['why'] if not q['outcomes'] else 'Completed work stays recorded; continue from the next unfinished step.',
                status=q['status'],completed=bool(achievement),room=d['room'],questId=q['id'],step=q['step'],totalSteps=len(d['stages']),
                stages=[dict(title=x['title'],done=i<q['step']) for i,x in enumerate(d['stages'])],achievement=achievement,
                afterChoices={str(i):x[0] for i,x in enumerate(d['after'])} if achievement else {},
                available=g.character_at_castle(s,'founder') and g.character_at_castle(s,who),history=deepcopy(saved(s)['history'].get(who,[])))

def view(s):
    people={who:p for who in GOALS if (p:=person(s,who)) is not None}
    return dict(people=people,achievements=deepcopy(saved(s)['achievements']),kits=saved(s)['kits'],feastDay=saved(s)['feastDay'],meal=saved(s)['meal'],
                feastUnlocked=complete(s,'tamsin'),kitUnlocked=complete(s,'elowen'),supplyBonus=2 if complete(s,'velis') else 0)

def context(s,who):
    p=person(s,who)
    if not p:return {}
    data={k:deepcopy(p[k]) for k in ('goal','status','step','totalSteps','achievement','history')}|{'guidance':'Only completed outcomes happened. The goal remains finished after success. Earlier outings and hobbies are separate from this finite ambition. Do not request already completed work.'}
    if who=='merrin':data['spiritInteraction']='Merrin is massless but can exert force by concentrating. Familiar book handling is easy; heavy or precise unfamiliar work requires attention and rest. Her visible clothes and bell are manifested. Real objects remain physical. This does not bypass locks, injury rules or consent.'
    return data

def household_scene(s,who,stage,definition):
    """Unplayed scenes follow current accomplishments; recorded memories stay intact."""
    d=deepcopy(definition)
    if who=='merrin' and complete(s,who) and stage in (1,3):
        d['opening']=('Merrin opens the complete performance copy. “We found the last act and read the whole play here. I still laugh at the magistrate answering his own letter. Would you read that scene again?”' if stage==1 else '“I enjoyed our chapel performance,” Merrin says. “Tonight I would like a smaller audience: you, if you would like to stay. We can read a scene or simply talk.”')
        if stage==1:
            d['title']='The complete comedy'
            d['choices']={
                'gentle':dict(label='Read the magistrate again',response='“Then I will be the clerk and try not to laugh before your last line.”'),
                'playful':dict(label='Ask whether the cook still charges rent for the desk',response='“Only in our alternative ending. I kept that note beside the original; I still think the cook made an excellent case.”')}
        else:
            d['choices']={
                'gentle':dict(label='Stay and talk about your day',response='“I would like that. The book will keep.” She puts it on the table and listens.'),
                'playful':dict(label='Offer to read the funniest scene together',response='“The onions, then. I want to hear you complain with the magistrate’s entire misplaced authority.”')}
    return d

def apply(s,a):
    kind=a.get('type')
    if kind not in ('goal-revisit','goal-meal','goal-craft-kit'):return False
    import game as g,headquarters,provisions
    g.require(g.character_at_castle(s,'founder'),'Return home before arranging a personal-goal activity.')
    initialize(s)
    if kind=='goal-revisit':
        who=a.get('characterId');choice=a.get('choice')
        g.require(isinstance(who,str) and who in GOALS and complete(s,who),'Complete this companion’s personal goal first.')
        g.require(who in g.household_members(s) and g.character_at_castle(s,who),'Return home together before revisiting this achievement.')
        g.require(isinstance(choice,str) and choice in ('0','1'),'Choose one of the displayed questions.')
        label,reply=GOALS[who]['after'][int(choice)]
        row=dict(title=GOALS[who]['keepsake'],playerLine=label,response=reply,dayNumber=s['dayNumber'],phase=s['currentDayPhase'])
        history=saved(s)['history'].setdefault(who,[]);history.append(row);del history[:-12]
        g.add_journal(s,g.character_profile(s,who)['name']+': '+label+' '+reply)
    elif kind=='goal-meal':
        g.require(complete(s,'tamsin'),'Finish Tamsin’s cookbook and first feast to unlock its menu.')
        g.require(headquarters.ready(s,'kitchen'),'Restore the kitchen before choosing its menu.')
        g.require(a.get('menu') in ('ordinary','tamsin'),'Choose ordinary household meals or Tamsin’s four-dish menu.')
        saved(s)['meal']=a['menu'];g.add_journal(s,'Household menu: '+('Tamsin’s herb broth, mushroom pie, oat rolls and pear tart.' if a['menu']=='tamsin' else 'Ordinary household meals.')+' The normal daily provision cost applies; no immediate meal or bonus is granted.')
    else:
        g.require(complete(s,'elowen'),'Finish Elowen’s three-treatment field kit first.')
        g.require(headquarters.ready(s,'infirmary'),'Restore the infirmary before restocking kits.')
        g.require(saved(s)['kits']<10,'Keep at most ten field kits ready.')
        for k,n in {'silver-ivy':3,'binding-thread':1}.items():g.require(s['materialInventory'].get(k,0)-s['materialReserveTargets'].get(k,0)>=n,'Restocking one kit needs 3 unreserved silver ivy and 1 binding thread.')
        for k,n in {'silver-ivy':3,'binding-thread':1}.items():s['materialInventory'][k]-=n
        saved(s)['kits']+=1;g.add_journal(s,'Elowen’s tested formulae: one three-treatment field kit restocked. Use it through the matching creature encounter’s First aid options.')
    return True

def register():
    import companion_conversations as cc
    for who,d in GOALS.items():
        _,value,flaw=cc.CHARACTER[who]
        cc.CHARACTER[who]=(d['want'],value,flaw)
    # Her existing music-box scenes remain a hobby, while the main ambition is explicit.
    opening,options=cc.FAMILIAR['zahra']['opening'],cc.FAMILIAR['zahra']['choices']
    for row in options.values():
        if 'make for herself' in row['label']:
            row['response']='“A masterpiece sword, Emberline. I want to forge it, prove it and put my whole name on it. The music box is for pleasure between serious pieces; I still intend to carve its bird myself.”'
