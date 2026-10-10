"""Authored companion routines and optional, remembered scene chains."""
from copy import deepcopy

# Lists rotate by day, skipping facilities not yet ready. They never assign work.
ROUTINES={
 'mira':{'morning':['library'],'afternoon':['library','common-room','conservatory'],'evening':['common-room','chapel','bedroom']},
 'koharu':{'morning':['workshop','library'],'afternoon':['training-yard','common-room'],'evening':['common-room','sauna','bedroom']},
 'zahra':{'morning':['conservatory','library'],'afternoon':['pool','conservatory','common-room'],'evening':['hot-spring','chapel','bedroom']},
 'fenna':{'morning':['command-room','library'],'afternoon':['training-yard','common-room'],'evening':['common-room','pool','bedroom']},
 'iona':{'morning':['command-room','library'],'afternoon':['library','common-room'],'evening':['chapel','common-room','bedroom']},
 'kaede':{'morning':['workshop','library'],'afternoon':['smithy','common-room'],'evening':['sauna','common-room','bedroom']},
 'tamsin':{'morning':['workshop','library'],'afternoon':['library','conservatory'],'evening':['common-room','chapel','bedroom']},
 'aurelia':{'morning':['library'],'afternoon':['chapel','conservatory'],'evening':['common-room','bedroom']},
 'neris':{'morning':['workshop','library'],'afternoon':['conservatory','pool'],'evening':['hot-spring','common-room','bedroom']},
}
GREETINGS={
 'mira':'“I am reading for pleasure. Please do not tell the catalogue.”',
 'koharu':'“Nothing needs mending this minute. I checked.”',
 'zahra':'“A useful pause. Those exist, you know.”',
 'fenna':'“No, I am not lost. This is the interesting way to the chair.”',
 'iona':'“I left the maps closed. We may have to find our own conversation.”',
 'kaede':'“Careful. I intend to enjoy myself with absolutely no improvements to show for it.”',
 'tamsin':'“There is room here. I made certain before settling in.”',
 'aurelia':'“The light is quite good here. So is the quiet.”',
 'neris':'“I was watching the reflections. You are welcome to interrupt them.”',
}

def chain(room,title,opening,choices,follow,echoes,reply,answers):
    return dict(roomId=room,title=title,opening=opening,choices=choices,follow=follow,echoes=echoes,reply=reply,answers=answers)

CHAINS={
 'koharu':chain('workshop','The repair worth keeping',
  'Koharu turns a repaired wooden clasp in her palm. “It holds. The question is whether to hide where it broke. People can be awfully rude to useful things once they see a scar.”',
  {'visible':('Let the repair show','“Good. Then someone can learn from it. And I need not sand away a perfectly respectable afternoon.”'), 'quiet':('Make it comfortable to use','“Exactly. No point making a monument of a handle if it bites your fingers.”')},
  'A margin for somebody else',
  {'visible':'“You wanted the repair to show. I remembered that when we wrote up our work.”','quiet':'“You asked whether the repair felt right in the hand. I tried applying that to our notes.”'},
  'After the research you both contributed to, Koharu leaves a generous blank margin beside the method. “For the next person to disagree in. What shall we give them first?”',
  {'method':('A clear starting method','“And permission to improve it. Otherwise we have only made a very tidy obstacle.”'), 'question':('The question still troubling us','“Oh, I like that. A useful invitation, with none of the sweeping.”')}),
 'zahra':chain('conservatory','An honest measurement',
  'Zahra lays a cord beside the growing bench. “Two measurements disagree. I could choose the prettier one, but the water will decline to cooperate.” She offers you the end of the cord.',
  {'repeat':('Measure again together','“Patient company. Much more useful than an audience.”'), 'note':('Record the uncertainty','“Good. A blank is better than a confident lie, provided we remember why it is blank.”')},
  'What the notes leave open',
  {'repeat':'“You were willing to take the measure twice. That helped when our research refused a neat answer.”','note':'“You let the uncertain part stay uncertain. Our new notes are better for it.”'},
  'With your shared research written up, Zahra rests the measuring cord on its hook. “There. Something dependable, and room to discover where it stops being dependable.”',
  {'rest':('Leave the next question for tomorrow','“A radical proposal.” Her smile is brief and warm. “I accept.”'), 'compare':('Ask which part surprised her','“How much easier it was to stop guessing once someone else was willing to say they did not know.”')}),
 'fenna':chain('command-room','A route with no grand name',
  'Fenna points to an unremarkable bend on the map. “This is where I stop when I do not want to arrive anywhere yet. It has no ancient title. I checked.”',
  {'unnamed':('Leave it unnamed','“Excellent. One less thing for an important person to put on a sign.”'), 'landmark':('Mark what makes it useful','“A flat stone and a dry place for the notebook. Cartography at its finest.”')},
  'The interesting way back',
  {'unnamed':'“We left that bend unnamed. I have been trying to leave our new discovery a little room too.”','landmark':'“You wanted the useful detail. So I kept the false starts in our research notes.”'},
  'Fenna has added a narrow path through the crossed-out versions of your shared study. “The answer is useful. So is knowing how we got stuck.”',
  {'detour':('Keep the detours','“Then the next person might recognise one before spending all afternoon there.”'), 'short':('Add a short route as well','“A proper map. One way for the hurried, and the interesting way for the rest of us.”')}),
 'mira':chain('library','A shelf with an exception',
  'Mira holds a book halfway between two shelves. “It is an excellent gardening manual until chapter six, which appears to be an apology. The index has taken a very firm position.”',
  {'crossref':('Give it two references','“Diplomacy. I was hoping for a scandal, but diplomacy will do.”'), 'browse':('Leave it where someone might stumble on it','“You understand the serious purpose of a little disorder.”')},
  'A footnote between friends',
  {'crossref':'“Two references, you said. Our new research deserves at least that much courtesy.”','browse':'“You defended the accidental discovery. I have kept one in our new notes.”'},
  'Mira has placed your shared research beside the awkward book. “A useful result and a rather good afternoon. The catalogue only has a space for one of those.”',
  {'afternoon':('Keep the afternoon in the margin','“In a small hand, then. We must preserve an appearance of scholarly restraint.”'), 'read':('Ask her to read the best passage','“The best scientific passage, or the best apology? Do consider your answer carefully.”')}),
 'iona':chain('command-room','A map that admits the rain',
  'Iona spreads a map without smoothing every crease. “That fold is where I sheltered it under my coat. Someone called it damage. I thought it a useful record of the weather.”',
  {'weather':('Keep the weather in the map','“Then it remains a map of a journey, rather than a claim that journeys are tidy.”'), 'copy':('Make a clean travelling copy','“And keep this one here. A home should be allowed to remember what the field case cannot carry.”')},
  'The place beside the map',
  {'weather':'“You said the rain belonged in the record. I kept the awkward parts of our joint study.”','copy':'“A travelling copy and a record at home. That turned out to be a useful way to finish our study.”'},
  'After the research you shared, Iona puts two notebooks side by side. “I like work that leaves room for the other person’s handwriting.”',
  {'compare':('Compare the different accounts','“Good. If they were identical, one of us might have missed something.”'), 'tea':('Leave room for a cup as well','“Now that is an improvement I can endorse without further measurements.”')}),
 'kaede':chain('workshop','Knowing when to stop',
  'Kaede turns a plain glass cup toward the light. “One more pass might improve the lip. Or it might give me a beautiful collection of pieces. Restraint is irritatingly difficult to show off.”',
  {'stop':('Let the useful cup be finished','“You deprive me of a magnificent excuse to make a mess. Thank you.”'), 'sample':('Try the idea on a spare sample','“Curiosity with a little manners. Yes. I can work with that.”')},
  'A finished question',
  {'stop':'“You let the cup be finished. I needed that reminder when our research started growing another appendix.”','sample':'“A spare sample, you suggested. That is where I put the question our shared work did not answer.”'},
  'Kaede closes the completed study with a palm flat on its cover. “There. Useful enough to share, unfinished enough to be interesting. Shall we celebrate our restraint?”',
  {'game':('Suggest a game in the common room','“Something with rules we may complain about. I am feeling admirably disciplined.”'), 'quiet':('Offer an unhurried conversation','“No measurements? No samples?” Her grin widens. “You make a persuasive case.”')}),
}


CHAINS['tamsin']=chain('library','A reference that survives use',
 'Tamsin lays two repairs side by side. “This one is prettier. That one will survive being opened every day. I would rather hear what you think before I put either in the collection.”',
 {'durable':('Choose the repair meant for daily use','“Then we agree what the collection is for. I can make it tidy without making it precious.”'),'both':('Keep both, with an honest explanation','“A comparison instead of a rule. That should save somebody a disappointing afternoon.”')},
 'Notes with room for another hand',
 {'durable':'“You wanted references that survive daily use. Our joint research belongs among them.”','both':'“You asked to keep the comparison. I have done the same with our shared research.”'},
 'Tamsin slides the completed study into a plain cover. “I left space for corrections. A useful collection should be willing to learn from its reader.”',
 {'use':('Put it where people will use it','“Within reach, then. That is the most important part of the catalogue.”'),'read':('Offer to read it through together','“Yes. You may find the sentence I have been pretending is perfectly clear.”')})

def initialize(s):
    s.setdefault('livingStories',{'memories':{},'sharedWork':{}})
    for who in ('elowen','nyssara','sylva'):s['localEncounters'].setdefault(who,{'status':'available','completedOn':None})
    # User-requested identity revision; retain person ID, story, possessions and artwork history.
    if 'tamsin' in s['people']:
        p=s['people']['tamsin']
        if p.get('ancestryLabel')!='Catfolk':
            p.setdefault('identityHistory',[]).append({k:deepcopy(p.get(k)) for k in ('ancestryLabel','role','appearanceDescription','identityRevision')})
            p['identityRevision']=p.get('identityRevision',1)+1
        p['ancestryLabel']='Catfolk';p['role']='Catfolk bookbinder · '+str(p['adultAgeYears'])
        p['appearanceDescription']='Adult catfolk woman; preserve Tamsin’s established face, auburn curls, green eyes, build and bookbinder clothing. Exactly two feline ears on top of her head and one softly furred cat tail; humanlike face and smooth human skin. Her short, tousled auburn curls cover the side-ear areas without increasing her hair volume. No human ears, ear lobes, muzzle or paws.'


def record_shared_work(s,participants):
    if 'founder' not in participants:return
    for who in participants:
        if who!='founder':s['livingStories']['sharedWork'][who]=s['livingStories']['sharedWork'].get(who,0)+1

def routine(s,who):
    import headquarters as h
    phase=s['currentDayPhase'];choices=ROUTINES.get(who,{}).get(phase)
    if not choices:return None
    offset=(s['dayNumber']-1)%len(choices)
    for room in choices[offset:]+choices[:offset]:
        if room=='bedroom':return s.get('bedroomAssignments',{}).get(who,'living-quarters')
        if h.ready(s,room):return room
    return None

def rows(s):
    import game as g
    import headquarters as h
    memories=s.get('livingStories',{}).get('memories',{});out=[]
    for who,d in CHAINS.items():
        if who not in g.household_members(s):continue
        for stage in (0,1):
            key=who+':'+str(stage);previous=memories.get(who+':0');memory=memories.get(key)
            if stage and not previous:continue
            unlocked=h.ready(s,d['roomId']) and (stage==0 or s.get('livingStories',{}).get('sharedWork',{}).get(who,0)>0)
            opening=d['opening'] if stage==0 else d['echoes'][previous['choice']]+' '+d['reply']
            blockers=[]
            if not h.ready(s,d['roomId']):blockers.append('Restore '+h.ROOMS[d['roomId']]['name']+'.')
            if stage and not s['livingStories']['sharedWork'].get(who):blockers.append('Contribute to the same research phase, or complete a shared review of a principle you both know.')
            if not all(g.character_at_castle(s,p) for p in ('founder',who)):blockers.append('Return home together.')
            out.append({'id':key,'personId':who,'name':g.character_profile(s,who)['name'],'roomId':d['roomId'],'title':d['title'] if stage==0 else d['follow'],'opening':opening,
                'choices':{k:v[0] for k,v in (d['choices'] if stage==0 else d['answers']).items()},'memory':deepcopy(memory),'unlocked':unlocked,'blockers':blockers,'available':not blockers and not memory})
    return out

def apply(s,a):
    if a.get('type')!='choose-living-scene':return False
    import game as g
    key=a.get('sceneId');choice=a.get('choice')
    g.require(isinstance(key,str),'Choose a known scene.')
    row=next((r for r in rows(s) if r['id']==key),None)
    g.require(row is not None,'This resident has no such invitation.')
    g.require(row['available'],' '.join(row['blockers']) or 'This conversation is already remembered.')
    g.require(isinstance(choice,str) and choice in row['choices'],'Choose an offered response.')
    who,stage=key.split(':');d=CHAINS[who];response=(d['choices'] if stage=='0' else d['answers'])[choice][1]
    s['livingStories']['memories'][key]={'choice':choice,'opening':row['opening'],'response':response,'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
    g.add_journal(s,'Shared '+row['title']+' with '+row['name']+'. '+response)
    return True

ROUTINES['elowen']={'morning':['enchanting-room','library'],'afternoon':['chapel','conservatory'],'evening':['common-room','chapel','bedroom']}
ROUTINES['nyssara']={'morning':['underground-quarters','command-room','library'],'afternoon':['warehouse','common-room'],'evening':['hot-spring','common-room','bedroom']}
GREETINGS['elowen']='“A little quiet is useful. You need not turn it into a discipline.”'
GREETINGS['nyssara']='“Nothing to report. An underrated sort of report.”'
CHAINS['elowen']=chain('library','A ward with room to breathe',
 'Elowen traces a modest ward diagram without illuminating it. “Preparation is not holding everything more tightly. Sometimes it is knowing exactly what may be left alone.”',
 {'space':('Leave each working its own space','“Then the circle should serve its practitioners, rather than make them resemble one another.”'),'check':('Make the boundaries easy to check','“Yes. Reliability should be visible to the person relying on it.”')},
 'A second place in the circle',
 {'space':'“You wanted room for different workings. Our shared research made that more than a pleasant phrase.”','check':'“You asked for boundaries we could check. I used that question when we compared our research.”'},
 'Elowen closes the study and shifts a spare sheet toward you. “There is still room for another question. I would rather prepare for that than pretend the last answer was final.”',
 {'question':('Keep a place for the next question','“With pleasure. An empty space need not be a defect.”'),'rest':('Leave the sheet blank this evening','“An excellent use of preparation: knowing that it can wait.”')})
CHAINS['nyssara']=chain('library','An honest enchantment',
 'Nyssara places an inscribed focus on a folded cloth. “The enchantment should steady a working tool. It does not make the tool infallible. I find that distinction worth keeping.”',
 {'test':('Ask how she would test the claim','“A comparison, a record, and somebody willing to be disappointed. The last is often the rarest tool.”'),'origin':('Ask why she chose that material','“Because a dependable enchantment starts with a material you understand. The inscription cannot make an unsuitable host honest.”')},
 'The useful disappointment',
 {'test':'“You asked how to test the claim. I remembered when our shared study gave us a less exciting answer.”','origin':'“You asked why I chose the host material. I kept that question beside our shared research and the finished inscription.”'},
 'Nyssara has set one crossed-out result beside the finished research. “This was wrong. Knowing why is rather useful. I am trying to become less offended by useful things.”',
 {'keep':('Keep the correction with the result','“Then somebody else may be spared the same very convincing mistake.”'),'laugh':('Admit to an equally convincing mistake','“Oh, good. I was worried I might be the only expert in the room.”')})


def review_blockers(s,who):
    import game as g
    r=[]
    if who not in CHAINS or who not in g.household_members(s):return ['Choose an established resident.']
    if who+':0' not in s['livingStories']['memories']:r.append('Share the first resident conversation first.')
    if not all(g.character_at_castle(s,p) for p in ('founder',who)):r.append('Both people must be home.')
    if not set(g.character_principles(s,'founder')) & set(g.character_principles(s,who)):r.append('Both people must have learned at least one common principle to compare their notes.')
    if s['livingStories'].get('review'):r.append('Finish or cancel the existing shared review first.')
    if s['livingStories']['sharedWork'].get(who):r.append('Your shared work already qualifies this resident’s follow-up conversation.')
    return r


def apply_review(s,a):
    import game as g
    kind=a.get('type')
    if kind not in ('start-shared-review','resume-shared-review','cancel-shared-review'):return False
    record=s['livingStories'].get('review')
    if kind=='start-shared-review':
        who=a.get('characterId');g.require(isinstance(who,str),'Choose an established resident.')
        reasons=review_blockers(s,who);g.require(not reasons,' '.join(reasons))
        previous={p:g.character_assignment(s,p) for p in ('founder',who)}
        s['livingStories']['review']={'personId':who,'previousAssignments':previous}
        for p in previous:g.set_character_assignment(s,p,'shared-review')
        g.add_journal(s,'Agreed one shared review phase with '+g.character_profile(s,who)['name']+'. Current assignments are held; they resume after this review. No resources committed.')
    else:
        g.require(record is not None,'No shared review is waiting.')
        who=record['personId']
        g.require(g.character_at_castle(s,'founder'),'Return home to change this review.')
        if kind=='resume-shared-review':
            g.require(g.character_at_castle(s,who),'Return home together to resume this review.')
            g.require(who in g.household_members(s),'The reviewer must remain a resident.')
            for p in ('founder',who):g.set_character_assignment(s,p,'shared-review')
        else:
            for p in record['previousAssignments']:
                if g.character_assignment(s,p)=='shared-review':g.set_character_assignment(s,p,'rest')
            s['livingStories']['review']=None
            g.add_journal(s,'Cancelled the shared review. No resources lost; other funded work is kept.')
    return True


def resolve_review(s,summary):
    import game as g
    r=s['livingStories'].get('review')
    if not r:return
    who=r['personId'];party=['founder',who]
    if who not in g.household_members(s) or not all(g.character_at_castle(s,p) and g.character_assignment(s,p)=='shared-review' for p in party):return
    record_shared_work(s,party)
    # Called last: restoring earlier work cannot give either person two jobs this phase.
    for p,assignment in r['previousAssignments'].items():g.set_character_assignment(s,p,assignment)
    s['livingStories']['review']=None
    summary.append('Compared research notes with '+g.character_profile(s,who)['name']+'. Your previous assignments resume next phase; the follow-up conversation is now available.')

# The resident's enhancement conversation is reached from their associated room.
for _who,_room in {'zahra':'smithy','fenna':'common-room','kaede':'training-yard','tamsin':'kitchen','elowen':'infirmary','nyssara':'enchanting-room'}.items():
    CHAINS[_who]['roomId']=_room
for _who,_room in {'zahra':'smithy','fenna':'common-room','iona':'command-room','kaede':'training-yard','tamsin':'kitchen','elowen':'infirmary','nyssara':'enchanting-room','neris':'hot-spring','aurelia':'guard-barracks','sylva':'conservatory'}.items():
    ROUTINES.setdefault(_who,{'morning':['library'],'afternoon':['common-room'],'evening':['common-room','bedroom']})['morning']=[_room,'common-room']
CHAINS['neris']=chain('hot-spring','Warmth in the right places',
 'Neris tests the water with a plain glass vessel. “A warm pool should have a cooler place to sit. Comfort is a choice, not a test of endurance.”',
 {'choice':('Keep a range of temperatures','“And easy steps between them. Nobody should have to announce that they have had enough.”'),'quiet':('Make room for quiet bathing','“A sheltered ledge, then. Some conversations are better left to the water.”')},
 'A useful balance',{'choice':'“You wanted people to choose their own warmth. Our notes leave room for that.”','quiet':'“You asked for quiet corners. I found myself thinking about that during our study.”'},
 'After your shared work, Neris sets the measuring vessel aside. “Reliable measurements make it easier to stop measuring for an evening.”',
 {'rest':('Enjoy the quiet','“An excellent practical application.”'),'compare':('Compare your favourite part of the study','“Only if we include the part where we finally stopped arguing with the numbers.”')})
CHAINS['aurelia']=chain('guard-barracks','A light that lets you see',
 'Aurelia turns a lantern shutter. “A watch light should show the path without blinding the person watching it. Brilliance is not the same as vigilance.”',
 {'shade':('Fit an adjustable shade','“Useful for different eyes and different nights.”'),'signal':('Agree a simple signal','“Something a tired person can remember. That is when it matters.”')},
 'The end of a watch',{'shade':'“You wanted the light to suit the keeper. Our shared work had the same good sense.”','signal':'“You asked for a signal people could remember. I kept our research notes equally plain.”'},
 'Aurelia closes the completed notes. “A dependable watch should also have a dependable ending. Shall we leave the desk?”',
 {'tea':('Suggest tea in the common room','“Yes. The lantern can manage without an audience.”'),'walk':('Take a quiet turn through the castle','“Together, then. No inspection required.”')})
CHAINS['sylva']=chain('conservatory','Room for the next leaf',
 'Sylva eases a rooted cutting from its pot. “Too much help can leave a plant with nowhere to grow. I would like these beds to provide room as well as water.”',
 {'space':('Give the roots room','“Generosity measured in soil. I approve.”'),'cuttings':('Keep a separate bench for cuttings','“Then the young plants can be demanding without inconveniencing everybody else.”')},
 'What we leave growing',{'space':'“You wanted room for the roots. I left room for corrections in our shared notes.”','cuttings':'“You asked for a place for new growth. Our shared research deserves one too.”'},
 'Sylva tucks a paper marker beside the completed study. “An answer is useful. So is the next question, provided we remember to water it.”',
 {'question':('Write down the next question','“In pencil. Questions enjoy changing their minds.”'),'rest':('Let it grow without watching for a while','“You are learning the difficult part of gardening.”')})
GREETINGS['sylva']='“I am letting the seedlings get on with it. Shall we try the same?”'

CHAINS['zahra']['opening']='Zahra lays a measuring cord beside the forge’s cooling trough. “Two measurements disagree. I could choose the prettier one, but hot metal will decline to cooperate.” She offers you the end of the cord.'
CHAINS['fenna']['opening']='Fenna spreads a small map on a tavern table beside a half-finished game. “Travellers bring better stories when there is somewhere comfortable to sit. This bend has no grand name. Shall we keep it that way?”'
CHAINS['kaede']['opening']='Kaede sets a glass cup beside the training rail. “Strong hands can break this without trying. The difficult part is holding it steadily after a drill. Restraint is irritatingly difficult to show off.”'
CHAINS['tamsin']['opening']='Tamsin lays two repaired recipe books on the pantry counter. “This one is prettier. That one will survive being opened every day. I would rather hear what you think before I put either beside the flour.”'

# Leisure preferences follow the current specialist roles. Assigned work still takes priority.
ROUTINES.update({
 'zahra':{'morning':['smithy','library'],'afternoon':['pool','common-room'],'evening':['sauna','common-room','bedroom']},
 'fenna':{'morning':['common-room','library'],'afternoon':['common-room','conservatory'],'evening':['common-room','pool','bedroom']},
 'kaede':{'morning':['training-yard','library'],'afternoon':['training-yard','common-room'],'evening':['sauna','common-room','bedroom']},
 'tamsin':{'morning':['kitchen','library'],'afternoon':['conservatory','common-room'],'evening':['common-room','chapel','bedroom']},
 'elowen':{'morning':['infirmary','library'],'afternoon':['conservatory','common-room'],'evening':['chapel','common-room','bedroom']},
 'nyssara':{'morning':['enchanting-room','library'],'afternoon':['workshop','library'],'evening':['common-room','bedroom']},
 'sylva':{'morning':['conservatory','library'],'afternoon':['conservatory','common-room'],'evening':['common-room','bedroom']},
 'aurelia':{'morning':['guard-barracks','library'],'afternoon':['training-yard','chapel'],'evening':['common-room','bedroom']},
 
 'sabine':{'morning':['library'],'afternoon':['entry-hall','library'],'evening':['common-room','library','bedroom']},
})
GREETINGS.update({'elowen':'“Nothing needs treating just now. We can simply talk.”','nyssara':'“The tools are away. You need not bring a technical question.”','sylva':'“Come and see what grew while nobody was watching.”','sabine':'“How pleasant. Company without an appointment.”'})


CHAINS['sabine']=chain('dungeons','A key with an owner',
 'Sabine lays two labelled keys beside a blank register. “One admits a person; one opens the way out. I suggest we give the second just as much attention.” She taps the empty line. “And I am offering advice as a resident, not applying to live behind this door.”',
 {'release':('Make the release route clear','“Excellent. A sound ward should know when its work is finished.”'),
  'record':('Record each key and its purpose','“A catalogue that prevents confusion. At last, a use for my more irritating habits.”')},
 'An obligation crossed out',
 {'release':'“You wanted a clear way out. I kept that beside our shared research.”','record':'“You asked what every key was for. Our research deserved the same question.”'},
 'After contributing to a shared study with you, Sabine closes the register and keeps a small blank space beneath her signature. “For changing my mind. I recommend it as a general design principle.”',
 {'tea':('Invite her upstairs for tea','“A door, a staircase, and an invitation with no paperwork. How extravagantly well planned.”'),
  'joke':('Ask whether she has catalogued the teacups','“Only the troublesome ones. Yours has an extensive history of attracting my attention.”')})
ROUTINES['sabine']={'morning':['dungeons','library'],'afternoon':['library','entry-hall'],'evening':['common-room','chapel','bedroom']}
