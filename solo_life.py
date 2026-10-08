"""Voluntary work roles and milestones for a household built in ordinary solo play."""
def initialize(s):
    s.setdefault('soloLife',{'agreements':{},'housewarming':None})

def offered(s,who,role):
    if who=='founder':return role=='garden'
    if who=='mira':return role=='garden' or (role=='fieldwork' and s['miraArchiveProject']['status']=='complete')
    return role in s['soloLife']['agreements'].get(who,[])

def companion_blockers(s,who):
    import game as g
    if not isinstance(who,str) or who=='founder' or who not in g.household_members(s):return ['Choose a resident household companion.']
    blockers=[]
    if not offered(s,who,'fieldwork'):blockers.append('Agree fieldwork together under Household work first.' if who!='mira' else 'Finish Mira’s archive story before she offers fieldwork.')
    if not g.character_at_castle(s,who):blockers.append('Your companion must be home.')
    return blockers

def view(s):
    import game as g
    import founder_setup
    return {'founderProfile':founder_setup.profile(s),'founderPortraitPrompt':founder_setup.portrait_prompt(s),'backgrounds':founder_setup.BACKGROUNDS,'people':{who:{'name':g.character_profile(s,who)['name'],'atHome':g.character_at_castle(s,who),'assignment':g.character_assignment(s,who),
         'gardenOffered':offered(s,who,'garden'),'fieldworkOffered':offered(s,who,'fieldwork'),
         'companionBlockers':companion_blockers(s,who) if who!='founder' else [],
         'agreements':list(s['soloLife']['agreements'].get(who,[]))} for who in g.household_members(s)},
         'gardeners':[who for who in g.household_members(s) if g.character_at_castle(s,who) and g.character_assignment(s,who)=='garden'],
         'housewarming':s['soloLife']['housewarming'],
         'moments':moments(s),
         'arrival':arrival_view(s),
         'canCelebrate':s.get('startType')=='fresh' and bool(s['livingWingCompletedOn']) and s['soloLife']['housewarming'] is None and all(g.character_at_castle(s,who) for who in g.household_members(s))}

def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind in ('choose-arrival', 'enter-castle', 'skip-arrival'):
        record=s.get('soloLife',{}).get('arrival')
        g.require(s.get('startType')=='fresh' and record is not None and not record['completed'], 'This arrival has already ended or belongs to an earlier campaign.')
        if kind=='choose-arrival':
            stage=next((r for r in ARRIVAL if r['id'] not in record['choices']),None)
            g.require(stage is not None and a.get('stageId')==stage['id'],'Choose the current part of your arrival.')
            option=next((r for r in stage['choices'] if r['id']==a.get('choiceId')),None)
            g.require(option is not None,'Choose one of the offered reflections.')
            record['choices'][stage['id']]=option['id']
            g.add_journal(s,'Arrival — '+stage['title']+': '+option['text'])
        else:
            g.require(kind=='skip-arrival' or len(record['choices'])==len(ARRIVAL),'Finish the arrival choices or choose to enter without the remaining choices.')
            record['completed']=True
            record['skipped']=kind=='skip-arrival'
            g.add_journal(s,'You set your notes on the library desk. The old hearth inscriptions offer a first practical question; the rest of the castle can wait.')
        return True
    if kind=='remember-solo-moment':
        key=a.get('momentId');choice=a.get('choiceId')
        row=next((r for r in moments(s) if r['id']==key),None)
        g.require(row is not None,'Choose a known household moment.')
        g.require(row['available'],'This moment is not ready, or has already been remembered. Return home after reaching its milestone.')
        option=next((c for c in row['choices'] if c['id']==choice),None)
        g.require(option is not None,'Choose how to remember this moment.')
        event={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'choiceId':choice,'text':row['opening']+' '+option['text']}
        s['soloLife'].setdefault('moments',{})[key]=event
        g.add_journal(s,event['text'])
        return True
    if kind=='agree-household-role':
        who=a.get('characterId');role=a.get('role');enabled=a.get('enabled')
        g.require(isinstance(who,str) and who in g.household_members(s) and who not in ('founder','mira'),'Choose a recruited resident. Mira’s work options are listed on her own sheet.')
        g.require(g.character_at_castle(s,'founder') and g.character_at_castle(s,who),'Return home together before discussing work.')
        g.require(role in ('garden','fieldwork') and type(enabled) is bool,'Choose a supported role and whether to agree it.')
        if enabled:g.require(a.get('willingnessReviewed') is True,'Confirm the resident willingly accepts this role. Membership alone grants no agreement.')
        roles=s['soloLife']['agreements'].setdefault(who,[])
        g.require((role in roles)!=enabled,'This agreement already has that status.')
        if enabled:roles.append(role)
        else:
            roles.remove(role)
            if role=='garden' and g.character_assignment(s,who)=='garden':g.set_character_assignment(s,who,'rest')
        g.add_journal(s,g.character_profile(s,who)['name']+(' agreed to ' if enabled else ' ended the agreement for ')+('garden tending' if role=='garden' else 'fieldwork')+'. No wages, romance or automatic assignment were implied.')
        return True
    if kind=='assign-gardener' or (kind in ('assign-founder','assign-resident','assign-character') and a.get('assignment')=='garden'):
        who='founder' if kind=='assign-founder' else 'mira' if kind=='assign-resident' else a.get('characterId')
        g.require(isinstance(who,str) and who in g.household_members(s),'Choose a household gardener.')
        g.require(g.character_at_castle(s,'founder') and g.character_at_castle(s,who),'Return home together before agreeing an assignment.')
        g.require(g.room_available(s,'conservatory'),'Restore the conservatory first.')
        g.require(offered(s,who,'garden'),'Agree garden tending with this resident first.')
        g.require(not any(p!=who for p in view(s)['gardeners']),'One gardener tends these beds. Pause the current gardener before assigning another.')
        g.set_character_assignment(s,who,'garden')
        return True
    if kind=='celebrate-solo-household':
        g.require(view(s)['canCelebrate'],'Finish the living wing and bring the household home before its first celebration.')
        people=g.household_members(s)
        event={'dayNumber':s['dayNumber'],'phase':s['currentDayPhase'],'participants':people[:],
            'text':'Warm water, a working kitchen and dependable light: the old wing is a home now. '+('You set the table for '+', '.join(g.character_profile(s,p)['name'] for p in people)+', taking a quiet moment to enjoy what you have built.' if len(people)>1 else 'You set a place by the hearth and take a quiet moment to enjoy what you have built.')}
        s['soloLife']['housewarming']=event;s['livingWingCelebration']='completed'
        g.add_journal(s,event['text'])
        return True
    return False


ARRIVAL = [
    {'id':'purpose','title':'What brought you here?',
     'opening':'You are an independent scholar of practical magic: the kind that warms a room, preserves a book or helps a garden grow. You have come to this old castle to make a home and a place to work. Its history is still mostly unknown to you. For now, there is a sound roof over a small wing, a neglected library, and more repair work than one person could finish in a season.',
     'choices':[
         {'id':'home','label':'A home I can make my own','description':'Begin with the wish to belong somewhere.', 'text':'You did not come for a finished home. You came for the chance to make one, slowly enough to recognize yourself in it.'},
         {'id':'study','label':'Work worth giving my days to','description':'Begin with curiosity about useful magic.', 'text':'You want to understand how these old workings were made, then discover what your own hands can do with that understanding.'},
         {'id':'beginning','label':'Room for a different life','description':'Leave the details of your past open.', 'text':'You need not explain everything that came before. For today, a key, a quiet room and a blank page are enough.'}]},
    {'id':'attention','title':'Inside the quiet wing',
     'opening':'The door opens onto cool stone and the smell of old paper. You arrive alone with your notes, forty crowns, two pieces of sun amber and two lengths of binding thread. A common room, sleeping chamber and library are usable. Beyond them, the castle waits for care. There is no household yet; the people you may meet will have their own lives and reasons for coming.',
     'choices':[
         {'id':'hearth','label':'The marks around the hearth','description':'Old magic, made for an ordinary comfort.', 'text':'You crouch beside the hearth and trace the pattern with your eyes. Before grand discoveries, perhaps you can learn to keep a room warm.'},
         {'id':'shelves','label':'The library’s worn shelves','description':'A place for questions that need time.', 'text':'You clear a space for your notebook. The shelves need patience more than ceremony, and you have brought at least a little of that.'},
         {'id':'window','label':'The path beyond the window','description':'A reminder that the castle is part of a wider world.', 'text':'You watch the path disappear beyond the gate. In time there may be journeys, visitors and letters. First, somewhere worth returning to.'}]}
]


def arrival_view(s):
    record=s.get('soloLife',{}).get('arrival')
    if record is None:return None
    memories=[{'title':r['title'],'text':c['text']} for r in ARRIVAL for c in r['choices'] if record['choices'].get(r['id'])==c['id']]
    return {'completed':record['completed'],'skipped':record.get('skipped',False),'memories':memories,
            'stage':next((r for r in ARRIVAL if r['id'] not in record['choices']),None)}


MOMENTS = [
    {'id':'hearth-understood','title':'The shape of a useful answer','art':'library',
     'requirement':'Complete the hearth-ward research.',
     'opening':'The marks by the hearth no longer seem like an ornament you are copying. You can follow what each part is doing. The stone has not changed, but the question you brought to it has become an answer.',
     'choices':[{'id':'explain','label':'Explain it in your own words','text':'Your first explanation is untidy. You cross out a sentence and try again until the page says something you actually understand.'},
                {'id':'imagine','label':'Imagine something you could make','text':'You sketch a small lantern in the margin. Understanding has made the next question pleasantly practical.'}]},
    {'id':'second-morning','title':'A room becoming familiar','art':'library',
     'requirement':'Reach the second day and return home.',
     'opening':'You have begun to recognize the little sounds of the wing: the window fastening, the chair on the uneven floor, the pause before the kettle settles. The castle is still unfamiliar, but this corner no longer feels quite like borrowed space.',
     'choices':[{'id':'ritual','label':'Choose a small daily ritual','text':'You decide to clear the desk before opening the notebook. A small kindness to whoever you will be tomorrow.'},
                {'id':'unhurried','label':'Leave the day open','text':'You let the next page stay blank a little longer. There will be work, but it need not fill every silence.'}]},
    {'id':'own-archive','title':'A place for the unfinished questions','art':'library',
     'requirement':'Finish Arrange the first archive.',
     'opening':'The first arrangement of the archive is done. You can find the notes you need without unpacking half the desk. Just as satisfying is the small space you have deliberately left for questions without answers.',
     'choices':[{'id':'index','label':'Give the questions an index','text':'You make a short list of loose ends. It is not a promise to solve them all, only a way of finding them again.'},
                {'id':'margin','label':'Keep room for surprises','text':'You leave a section unnamed. Not everything worth keeping will arrive in the form you expected.'}]},
    {'id':'shared-roof','title':'More than one place at the table','art':'library',
     'requirement':'Welcome your first resident through agreed membership.',
     'opening':'There is another person living under this roof now. That does not make the castle finished, or make either of you responsible for filling every quiet moment. It does make the ordinary shape of home a little different.',
     'choices':[{'id':'space','label':'Value the room to be separate','text':'A shared home can hold closed doors and separate plans. You hope to make that as welcome as company.'},
                {'id':'company','label':'Welcome the possibility of company','text':'You find yourself looking forward to small encounters on the way to somewhere else, with no need to turn each one into an occasion.'}]},
    {'id':'first-light','title':'A light of your own','art':'library',
     'requirement':'Make your first warming lantern.',
     'opening':'For a moment you stop checking the lantern for faults. Its steady warmth is a small answer to the cold stone around your desk. This is something you made here.',
     'choices':[{'id':'craft','label':'Remember the work','text':'You note the awkward join you would improve next time, then leave room beneath it for another design.'},
                {'id':'home','label':'Remember the feeling','text':'You close the notebook. Tonight, it is enough that the room feels a little more like yours.'}]},
    {'id':'green-room','title':'Rain against the glass','art':'conservatory',
     'requirement':'Restore the conservatory.',
     'opening':'A passing shower taps the conservatory panes. With the repairs behind you, you can hear the different notes of glass, leaf and stone instead of counting what still needs mending.',
     'choices':[{'id':'observe','label':'Listen for a while','text':'You stay until the shower softens, learning the sound of the room without making a project of it.'},
                {'id':'sketch','label':'Sketch a possibility','text':'You sketch an idea for a comfortable corner on a scrap of paper. It is only an idea for now; the room can grow slowly.'}]},
    {'id':'field-notes','title':'The journey on the page','art':'library',
     'requirement':'Bring a discovery home from the old waterworks.',
     'opening':'Back at your desk, you lay out the waterworks notes. The damp corners have curled. A place that once existed only beyond the gate now has details you can remember without looking.',
     'choices':[{'id':'precision','label':'Keep the precise account','text':'You separate what you observed from what you merely suspect. The unanswered questions deserve their own space.'},
                {'id':'impression','label':'Keep a personal margin','text':'Beside the measurements you write about the sound of the stream. An account of a place can have room for both.'}]},
    {'id':'neighbour-reply','title':'An ordinary connection','art':'library',
     'requirement':'Complete a neighbour request.',
     'opening':'You revisit the record of your first completed neighbour request. The castle has become part of someone else’s ordinary day: a useful place to write to, rather than a distant roof above the trees.',
     'choices':[{'id':'record','label':'Keep it with the household record','text':'You give the record a place among the practical papers. Useful work is part of the household’s story too.'},
                {'id':'pause','label':'Take a quiet moment','text':'You leave the papers alone for a while and look toward the gate. There is no need to turn a good beginning into another obligation.'}]}
]

def moments(s):
    import game as g
    unlocked={
        'hearth-understood':s['researchStatus']=='complete',
        'second-morning':s['dayNumber']>=2,
        'own-archive':s['researchProjects'].get('archive-foundations',{}).get('status')=='complete',
        'shared-roof':len(g.household_members(s))>1,
        'first-light':bool(s['craftedArtifacts'].get('warming-lantern') or s['characterDevelopment']['founder']['advancementAwards'].get('artifact:warming-lantern')),
        'green-room':g.room_available(s,'conservatory'),
        'field-notes':bool(g.discoveries_for(s,'old-waterworks')),
        'neighbour-reply':any(r['status']=='delivered' for r in s['neighbourRequestProgress'].values())}
    saved=s.get('soloLife',{}).get('moments',{})
    return [{**r,'unlocked':unlocked[r['id']], 'memory':saved.get(r['id']),
             'available':s.get('startType')=='fresh' and unlocked[r['id']] and r['id'] not in saved and g.character_at_castle(s,'founder')} for r in MOMENTS]
