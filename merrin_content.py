"""Merrin's authored content, registered with the existing companion systems."""
from copy import deepcopy


def register(g):
    import household_chapter_content as hc
    from household_chapter_content import beat
    hc.PROFILES['merrin']=dict(room='chapel',activity='reading',
      relaxed='“I put the register away and chose my plum dress for an evening of my own. Would you join me by the hearth? I have saved a scene from the comedy.”',
      daring='“I wanted to try the short wrap skirt and this halter top. I like how they look, and I hoped you might enjoy seeing me in them. Would you like some company?”',
      thanks='“Then come and sit with me. I would like to hear what you enjoyed today.”',
      tease='“That is a very persuasive invitation to stay. I had better put my book down.”',beats=[
      beat('A pot with blue pears','Merrin turns a small flowerpot in her hands. “They were meant to be plums. I made them narrower while correcting the first mistake, and now they are pears. I am considering leaving them alone.”','“Yes. The flowers will have to live with a little uncertainty about their neighbours.” She sets the brush aside.','“The brush was entirely innocent. Its operator, however, had a very confident plan.” She offers you a clean pot.','Suggest keeping the pears','Ask whether she blames the brush'),
      beat('The missing second act','Merrin has found a comedy with its middle pages missing. “The magistrate is hiding under the desk here. Six pages later, everyone congratulates the cook. I need to know what happened.”','“Then we compare the titles in the theatre catalogue. I would like the actual ending before I write a worse one.”','“The cook might have charged him rent for the desk. A public official ought to pay for his accommodation.” She writes your theory on a separate scrap.','Suggest looking for another copy','Invent a ridiculous explanation'),
      beat('An evening without a list','“I nearly brought a list of pleasant things to discuss,” Merrin admits. “Then I realised that you might arrive with a subject of your own. What has been on your mind?”','She listens without reaching for paper. “Would you like an opinion, or should I simply stay with you while you think?”','“It began with a flowerpot and ended with another flowerpot. I had mistaken an interest for an entire programme.” She laughs and leaves room for your story.','Tell her something you want to talk about','Ask what was on her abandoned list'),
      beat('Her name in the present tense','Merrin closes the register. “Someone asked what I used to enjoy. I said I enjoy comic plays. Present tense. It took me a moment to hear the difference.”','“A reading with more than two people. I would like to hear someone else attempt the magistrate. You have set a difficult standard.”','“Then I shall save you a part. It is a flattering role: only one pompous speech and an excellent excuse to sit beside me.”','Ask what she would like to do next','Ask whether there is a part for you')])
    hc.SPECIALIST_VOICES['merrin']=(
      '“A quiet room should help people rest. I can prepare a modest sanctuary ward, provided we test it with ordinary rest and keep its limits on the door.”',
      '“The ward is ready. It helps a person who has stopped to rest at home; it cannot mend exhaustion while they keep working.”',
      '“Food, time and a place to put the work down still matter. The ward supports those things. It does not replace them.”')
    hc.PERSPECTIVES['merrin']='“I am glad we made time for this. Tell me which part of your day you would like to keep.”'
    hc.ACTIVITY_THOUGHTS['merrin']={
      'chapel':'“We can leave the register shut. You do not need a reason to sit here.”',
      'common-room':'Merrin offers you the comic play. “Choose a part. I promise not to improve your performance while you are giving it.”',
      'conservatory':'“That pot is mine. The pears are intentional now.” Merrin turns it towards the light, amused.',
      'library':'“This shelf has room for something funny. I intend to make a well-documented case for it.”'}
    hc.PAIRS.append(('mira','merrin','library','A joke in the margin',
      'Mira finds a comic scene on the back of a chapel account. Merrin recognises the clerk’s lines but cannot remember who copied them. “Then we keep the joke and leave the name uncertain,” Mira says.',
      'Ask them to read the scene together','Mira takes the magistrate; Merrin plays the clerk who has filed his complaint under complaints about filing. They lose their places laughing.',
      'Ask how to preserve both sides of the page','Merrin proposes a loose protective sleeve. Mira records the account and the play separately, with neither treated as waste paper.',
      'A reading copy for the common room','Mira has copied the scene onto sturdy paper. Merrin adds the missing stage direction only where she can read it on the original. The unreadable line stays marked as a gap.'))
    hc.PAIR_FOLLOWUPS[('mira','merrin')]=('Ask which version they read aloud','“The copy,” Mira says. “The original deserves fewer tea cups.” Merrin agrees, then asks whether you will take the cook’s part.', 'Ask about the unreadable line','“We tried two guesses,” Merrin says. “Both are funny. Neither belongs in the transcription.” Mira has kept them on a separate sheet headed proposed jokes.')

    import romance_content as rc,romance,intimacy_content as ic
    rc.SCENES['merrin']=[
      ('An ordinary invitation','Merrin sets her book aside. “I keep hoping you will stay after the conversation ends. I would like to ask you on a date. Is that something you want too?”','You tell her the attraction is mutual. Merrin smiles. “Good. I have been making that question unnecessarily difficult. Would tomorrow evening suit you?”'),
      ('A seat beside the hearth','Merrin has borrowed a comedy for your date. After the final scene she leaves the book closed. “May I take your hand? I would like to sit with you a little longer.”','You take her offered hand. Later you ask to kiss her, and she says yes. The faint coolness of her fingers does not stop her from giving your hand an affectionate squeeze.'),
      ('A place in each other’s days','“I want to make time for you beyond the evenings that happen to be free,” Merrin says. “Would you like to call us partners? We can still ask for time on our own.”','You agree. Merrin kisses your cheek. “Then tell me when you need company, and when you need quiet. I will try to ask before arriving with three solutions and a chair.”'),
      ('The register stays closed','Merrin meets you at her door. “I would like a private evening with you. We can take our time, and stop whenever either of us wants. Would you like to stay?”','You accept and share a kiss. Merrin closes the door after you both agree to stay. The scene fades to black; the rest of the evening is private.')]
    romance.GREETINGS['merrin']='“There you are. I saved the funny passage because I wanted to hear you read it.”'
    ic.ROWS['merrin']=[
      ('A page between two chairs','Merrin moves her chair beside yours. “May I hold your hand while we read?”','You take her hand. The magistrate in the play loses his own petition, and Merrin gives him an offended voice until both of you laugh.',
       'Time she asks for','“I would like another evening like this,” Merrin says. “Would you choose the story next time?”','You agree and tell her what you would like to share. She asks to kiss your cheek before returning the book to its shelf.'),
      ('The place she leaves beside her','Merrin lifts the edge of a blanket on the common-room settee. “There is room here. Would you like to sit close?”','You settle beside her. She leans against your shoulder after asking, and you spend a quiet while comparing the worst jokes you know.',
       'Saying what is comfortable','“I like being close to you,” Merrin says. “Will you tell me if I reach for you when you wanted space?”','You agree to ask each other plainly. She offers a kiss, and waits for your answer before moving closer.'),
      ('A day with no polished account','Merrin has left a badly painted pot on her table. “I made a mess of that, and I am tired of explaining why. May I just be cross beside you for a minute?”','You make room. She complains about the paint, then rests against you. After a while she laughs at the blue mark on her own thumb.',
       'Welcome on an ordinary day','“Thank you for staying when I was poor company,” Merrin says. “I want you to know you can bring an unfinished day here too.”','You tell her you would like that. She takes your offered hand, and the two of you sit without needing to improve the afternoon.'),
      ('A private evening together','At her bedroom door, Merrin asks whether you would like to stay. “A quiet evening or something closer; please tell me what you want.”','You both choose closeness and share an unhurried kiss. The scene fades to black, leaving the evening private.',
       'Plans for the morning','Merrin asks for a private evening with you, then adds, “Tomorrow I would like to hear how your work is going. Tonight I would like us to put it down.”','You agree on the evening together. She kisses you, and the scene fades to black. In the morning, she remembers the conversation she wanted to have and asks how you slept.')]

    import character_quest_content as cq,signature_equipment as se
    cq.PERSONAL['merrin']=(
      'The comedy she wants to finish','find the missing second act and repair a reading copy for the household','search','repair',
      'Merrin has traced the incomplete comedy to a damaged box of chapel entertainments. “I want the ending because I enjoyed the beginning. It does not need to contain a secret.” She asks you to help sort the loose pages.',
      'The pages include two different endings. Merrin checks the numbering and keeps the older ending with the text; the later one goes in an appendix with its separate handwriting noted.',
      'Merrin opens the repaired reading copy. The cook has been impersonating the magistrate’s clerk to get the kitchen roof fixed. She insists on reading his indignant discovery aloud before thanking you.',
      '“Will you sit beside me for the next scene? I would like your company after the last page too.”')
    cq.REQUEST_FLIRT['merrin']='“The work is finished. I would be pleased if the company lasted a little longer.”'
    cq.QUEST_TEASING['merrin']='“An excellent result. I am recording that before you ask me to improve the compliment.”'
    se.ROOMS['merrin']='chapel'
    se.CONTENT['merrin']=('A signal she can control','Fit the bell so I can ring it deliberately and keep it quiet when someone is resting. A signal is useful only when people can trust what it means.','The bell is quiet until I ask it to sound. That is exactly the improvement I wanted.','restful-signal')

    import customization_content as custom,relationships,companion_participation as participation
    custom.PROFILES['merrin']=('plum','comic plays','pear cordial','chapel','a hand-painted flowerpot',
      '“I like comic plays, pear cordial and pots with imperfect pictures. The chapel matters to me, but I would be glad to spend an evening elsewhere.”',
      '“I hoped you would notice the dress. I also hoped you would stay long enough to hear the joke I saved.”')
    relationships.PREFERENCES['merrin']=('Accurate records and company that asks before helping','Being a spirit does not make her a source of certain answers about the past','The answer she can stand behind',
      'Merrin points to a gap in the register. “I could make a plausible guess. I would rather leave someone an honest question.”',
      '“I remember a voice and a blue coat. That may help if another record supplies a name. It is not enough to supply one myself.” She writes the remembered details separately.')
    
    participation.VOICES['merrin']='“Say what we know, then check what this approach requires. My memories are useful; they are not instructions for every ruin.”'

    import companion_conversations as cc,companion_almanac_content as ac
    cc.CHARACTER['merrin']=(
      'Preserve the surviving memorial records and enjoy a life that includes plays, friends and interests beyond chapel work.',
      'Keep uncertainty visible, respect private records and ask what kind of help someone wants.',
      'When worried, she starts organising another person’s time before hearing what they need.')
    cc.FAMILIAR['merrin']=cc.scene('Merrin is labelling a cover for private letters. “Some belong in the archive. That does not make them suitable for a public reading.”',
      ('Ask how she decides what can be shared','“Look for the writer’s wishes, and remember that a missing instruction is not an invitation. I can describe the document without repeating its confidences.”'),
      ('Ask what she keeps for pleasure','“The comic play and my flowerpots. One has blue pears that were meant to be plums. I want a shelf that can hold something I simply like.”'),
      ('Ask whether she remembers everything she recorded','“No. Dates blur together, and I have forgotten names I wish I knew. If I sound certain, you may ask what supports the memory. I should be able to tell you.”'))
    cc.TRUSTED['merrin']=(
      '“I am afraid of becoming useful enough that nobody asks whether I am happy. Then I catch myself doing the same thing to someone else: finding them a task instead of hearing them.”',
      ('Ask what helps her stop arranging things','“A direct question: did they ask for this? If they did, I can help. If they did not, I need to ask before clearing a space in their afternoon.”'),
      ('Ask what makes a good evening for her','“Company, a play that makes us laugh, and no expectation that I finish by explaining the castle’s history. I would like to ask about your day as well.”'),
      ('Say you may sometimes want practical help','“Then tell me. I have kept the useful skills. I am trying to leave you a choice about receiving them.”'))
    cc.PRIVATE['merrin']=(
      '“I like being wanted as the person I am now. You can ask about my past; please leave room for the plans I have not made yet.”',
      '“A direct invitation, patient humour and someone who remembers what I enjoy when there is no work to discuss.”',
      '“Ask to hold my hand or kiss me. I would rather answer a clear question than wonder whether I missed a hint.”',
      '“Please ask before touching me to test how solid I feel. I am your partner, not an experiment.”')
    cc.INITIATIVE_LABELS['merrin']=('Ask why she kept the imperfect pot','Suggest a place where she can enjoy it','Offer a second pot without offering to correct this one')
    cc.CAMP_QUESTIONS['merrin']=('Ask what she would like to do when you return','“Put the travel notes away and read the cook’s scene. We can discover whether a roof repair remains funny after an actual journey.”')
    cc.INVITATION_REPLIES['merrin']=(('Ask what she can verify about the recollection','“The blue coat appears in a repair note. The voice is only my memory. I will keep those claims separate.”'),'“Another time, then. I will put the notes away; the question does not need settling tonight.”')
    ac.PHYSICAL['merrin']=(162,None,(86,67,91),'A slender, softly translucent spirit form with an ordinary relaxed posture.','These are approximate clothing-fit measurements for her visible form. Her spirit has no fixed physical mass; no body measurement grants a gameplay advantage.')
    ac.PERSONAL['merrin']=dict(hand='Right',habit='Labels an uncertain recollection as a recollection, then checks it against the surviving page.',
      history='She kept the chapel’s memorial records before the castle was abandoned. She remembers particular people and daily habits, with gaps she does not disguise.',
      comfort='Pear cordial, comic readings and a shelf for her painted flowerpots.',worry='Being treated as the chapel’s permanent caretaker rather than a person with choices.',
      attraction='Patient humour, direct invitations and interest in her current life.',turnoff='Being treated as a supernatural curiosity or touched without asking.',affection='An offered hand, quiet company and a kiss she has agreed to.',private='She wants to be wanted for her company, not thanked into a relationship.',
      initiative=('The pot she kept','Merrin has put a small pot with blue pears on a windowsill. “I decided that enjoying it was a better reason to keep it than painting it perfectly.”','customization'),
      idle=['Reading the cook’s lines under her breath.','Labelling the uncertain date on a memorial page.','Turning a painted pot towards the window.'])
    ac.INITIATIVE_REPLIES['merrin']=(
      '“The paint went wrong, but the shape is sound. It holds a plant. More importantly, it makes me smile. That is enough work for one pot.”',
      'Merrin tries the windowsill you suggest. “Here I can see the pears from my chair. You have improved the arrangement without improving the pears.”',
      '“Yes, please. I would enjoy painting another. This one can stay as it is.” She begins considering colours rather than corrections.')

    import companion_threads_content as tc
    tc.PAIRS['mira:merrin']=tc.pair(['mira','merrin'],'Leave room for the laugh',[
      ('Mira wants to read the whole comedy after supper. Merrin suggests a single scene. “People may be tired,” she says. Mira closes a finger inside the book. “I would like them to hear the ending before they decide it is a play about a desk.”',[
        ('Ask Mira what makes the ending worth sharing','“The cook gets the roof repaired by making the magistrate sign his own complaint,” Mira says. Merrin laughs. “Then we need the scene that sets up the signature. I can see why my choice was too short.”'),
        ('Ask Merrin how long she wants the reading to last','“Long enough to enjoy, short enough that nobody stays out of politeness,” Merrin says. Mira suggests two scenes with a pause between them.'),
        ('Ask whether they could offer a second evening','Mira checks the scene breaks. “Yes. The first part ends with the magistrate under the desk.” Merrin says, “An excellent place to leave him while everyone gets some sleep.”')]),
      ('They try the first scene. Mira rushes into the next line while Merrin is laughing. “I am sorry,” Mira says. “I know what comes next and want to get there.” Merrin points to the pause. “I want a moment to enjoy what just happened.”',[
        ('Ask them to try the exchange more slowly','Mira waits after the clerk’s answer. Merrin supplies the offended silence of the magistrate. This time they both hear why the next line works.'),
        ('Suggest marking a pause in their reading copy','“Our copy, certainly,” Mira says, reaching for a pencil. Merrin adds a small mark after the joke. “We can change it if the audience needs less time.”'),
        ('Listen while they try each other’s parts','Merrin takes the clerk and discovers that she rushes too. Mira grins. “It is tempting, knowing the next joke.” They agree to watch each other before continuing.')]),
      ('Mira and Merrin agree on two short scenes, with a clear break for anyone who wants to leave. Merrin offers to introduce the play; Mira will invite people to take the smaller parts.',[
        ('Ask to hear how the reading goes','“We will tell you whether anyone volunteers for the cook,” Mira says. Merrin adds, “And whether we remembered to let them laugh.”'),
        ('Wish them a good evening','Merrin puts their marked copy beside the chairs. “Thank you. We have something we both want to try.” Mira begins practising a shorter introduction.')])
    ],'The audience finds its own timing',[
      ('The reading has finished. Mira reports that the audience laughed at a line neither of them had marked. Merrin says, “We waited. It was the best pause of the evening.”',[
        ('Ask which line surprised them','“The cook asked whether the desk counted as official accommodation,” Mira says. Merrin smiles. “Apparently several people have opinions about the magistrate’s living arrangements.”'),
        ('Ask whether the break helped people leave comfortably','“Two people left for an early start,” Merrin says. “They asked when we would read again.” Mira nods. “I was wrong to think stopping would lose them.”'),
        ('Ask whether they enjoyed performing together','“Yes,” Mira says. “I had someone to look at before the next line.” Merrin adds, “And I could laugh without worrying that I had missed three sentences.”')]),
      ('They want to read the final scenes next week. Merrin will keep the introduction short, and Mira has asked someone else to play the cook. They leave the chairs in a loose circle.',[
        ('Ask them to save you a place','“Gladly,” Merrin says. Mira puts a spare reading copy on the table. “A seat does not commit you to a part. The cook has been warned about recruiting the audience.”'),
        ('Leave them to choose the next passage','Mira opens the final act while Merrin fetches two cups. They begin disagreeing cheerfully about which voice the magistrate deserves.')])])
    tc.PERSONAL['merrin']=dict(title='The help she had already planned',
      opening='“I made a list after you said you had a difficult afternoon,” Merrin says. “I had not asked whether you wanted a list. May I start that conversation again?”',
      approaches=[('Ask what she hoped the list would do','“Give you a way to begin. It might help, but I made the decision before hearing whether you wanted to begin anything tonight.”'),('Tell her that company would have helped','“Then I can put the list away and stay. I am sorry I mistook having an answer for listening.”'),('Say a practical suggestion can be welcome','“I am glad. I still need to ask which kind of evening you want before offering one.”')],
      question='“When a day has gone badly, would you usually like me to listen first or offer one practical idea?”',
      options=[('Listen first','“Then I will hear you out. I can ask about practical help afterwards.”'),('Offer one practical idea','“One, then I ask whether it helps. I will keep the rest of the list to myself unless you want it.”')],
      uncertainty='“We can choose when it happens. You do not owe me a permanent rule for being tired.”',
      privacy='“Then I will ask each time. You can answer for that evening alone.”',
      decision='“I want you to feel welcome even when I cannot solve the problem. I can begin by asking whether you want company, help or space.”',
      endings=[('Support asking before making a plan','“Yes. A question leaves room for your answer; my completed list rather crowded it out.”'),('Point out that urgent problems sometimes need action','“They do. If the roof is leaking, we move the books. Afterwards I can still ask how you are instead of assuming the bucket settled everything.”'),('Invite her to sit with you now','“I would like that. The list can remain folded.”')],
      followups=['Merrin puts the notebook aside. “Listening first, as you asked. How was today?”','Merrin leaves the notebook closed. “Would one practical idea help today, or would you like another sort of company?”','“Company, an idea or time to yourself?” Merrin asks. “We can decide for this evening.”','Merrin asks whether you would like company, without repeating a private answer.'],
      unresolved='“You mentioned urgent problems. I kept that distinction: act on the immediate danger, then ask what the person needs next.”',
      tradition='Ask which kind of company would help before making plans for one another.')
    tc.FOLLOWUP['merrin']=([
      ('Tell her about one part of your day','She listens to the end before asking a question. “Would you like my thoughts on that, or should we stay with how it felt?”'),
      ('Ask how her own day has been','“I found the cook’s missing line. Then I spent an hour trying to improve a perfectly serviceable label. I am ready for company that has no margins.”'),
      ('Say you would prefer to read together','“Gladly. We can share something without turning either of us into tonight’s subject.” She brings the comedy.')],
      '“Shall we keep asking what sort of company would help? I would like the same choice when I have had a difficult day.”',
      ('Agree to ask each other','“Then we both get to answer. I am very pleased with that arrangement.”'),
      ('Keep it to this evening','“That is enough. We can ask again when we need to.”'))

    import social_content as sc
    sc.PERSONAL['merrin']=[
      sc.scene('A correction of her own','Merrin has crossed a date out of her notes. “I remembered the bell ringing on a winter morning. The repair account says it was midsummer. The cold belonged to a different day.”',
        ('Ask what made her check','“The flowers in another entry. I remembered snow, but someone had brought fresh meadow flowers. One of those details needed a second look.”'),('Thank her for keeping the correction visible','“I would rather you trust the work because you can see a correction than because I have hidden every one.”'),('Say another part may still be uncertain','“Yes. I have marked that too. Correcting one date does not make the rest infallible.”')),
      sc.scene('The question she could not answer','“Someone asked about a person who came here,” Merrin says. “I could not remember her name. I wanted very much to offer something better than I do not know.”',
        ('Ask what she could tell them','“Which page survives, what it actually says and where another record might be. I can give them a useful next step without pretending it is the answer.”'),('Offer company while she sits with the disappointment','“Please. I have finished checking for tonight. I would like to stop turning it over alone.”'),('Say admitting the gap was the right decision','“I think so too. I still wish the right decision felt less like failing someone.”')),
      sc.scene('Something for today','Merrin puts a new invitation beside the closed register. “A reading in the common room. I wrote my name as host, then remembered that I can ask someone else to help.”',
        ('Ask which part she would like help with','“Choosing a passage short enough that people can leave before it becomes a commitment. The cook’s scene, perhaps.”'),('Offer to read one of the roles','“The magistrate is yours if you want him. Please give him the dignity he repeatedly fails to deserve.”'),('Ask how she will leave room for people who decline','“An invitation with a clear time, and no questions for anyone who does not come. I want willing listeners.”'))]
    for key,row in sc.catalogue().items():
        if key.startswith('personal:merrin:'):sc.CATALOGUE[key]=row

    import resident_friendship_content as rf
    rf.PROJECTS['merrin|mira']=dict(title='A reading copy that can leave the archive',room='library',displayRoom='common-room',keepsake='Two-voice comedy booklet',
      invitation='Mira and Merrin want a sturdy reading copy of the comedy, so the fragile original can stay safely in the archive.',
      introduction=[['mira','Separate pages for the parts, or one booklet?'],['merrin','One booklet. We are already arguing about whose line comes next.'],['mira','Then I shall make the names especially clear.']],
      completion=[['merrin','The stage direction is legible at last. He hides under the desk, not behind the cook.'],['mira','A great loss to the theatre, but a gain for accuracy.'],['narrator','They bind the copy and sign the inside cover, leaving it on the common-room shelf.']],
      outing='Merrin and Mira want to try their booklet with an audience in the common room.',
      outingLines=[['mira','I have given the magistrate a very grand voice.'],['merrin','Then the clerk will need an exceptionally tired one.'],['narrator','They trade parts halfway through. By the last scene, each is imitating the other’s version with affectionate exaggeration.']],
      reflection=[['merrin','I had forgotten how much a pause can change the joke.'],['mira','You left room for the audience. I usually try to finish the sentence over them.'],['narrator','They mark a few pauses in their reading copy, keeping the original transcription intact.']])

    import personal_paths as pp
    from personal_path_content import t,branch
    pp.PEOPLE['merrin']={'room':'chapel','branches':[
      branch('merrin-sanctuary','Sanctuary keeper','Make a brief place to recover without pretending the danger has ended.','warded-cover',
        t('merrin-shelter','Sheltering chime','enemy',1,2,text='Ring a short ward while making a guarded attack.'),
        t('merrin-relief','A moment of relief','enemy',1,1,text='Keep pressure on the foe and restore 1 vitality to an injured companion.',healsAlly=1),
        'A clear rest signal','support'),
      branch('merrin-record','Record keeper','Distinguish a useful memory from a claim the party cannot verify.','clear-measure',
        t('merrin-compare','Compare the surviving marks','insight social',text='Compare surviving marks and records to identify a usable instruction.'),
        t('merrin-route','Mark the return route','trail gap height',text='Record and check a safe route the whole party can follow.'),
        'Notes another person can use','pace'),
      branch('merrin-bell','Bell warden','Use a controlled signal to interrupt a hostile working.','measured-force',
        t('merrin-strike','Measured bell pulse','enemy radiant',2,text='A focused ward pulse; +2 damage against undead.',bonusAgainst=['undead'],bonusDamage=2),
        t('merrin-release','Release the false binding','enemy insight',3,1,1,text='Interrupt a hostile binding under cover; costs 1 vitality.'),
        'A deliberate signal','damage')]}
    for branch_id,title,theme,enchant,root,advanced,passive in pp.PEOPLE['merrin']['branches']:
        for level,node in enumerate((root,advanced)):
            key,name,tags,damage,block,cost,description=node[:7]
            pp.CATALOG[key]=dict(id=key,who='merrin',branch=branch_id,branchName=title,theme=theme,enchantment=enchant,name=name,tags=tags,damage=damage,block=block,cost=cost,description=description,kind='technique',requires=root[0] if level else None,advanced=bool(level),**(node[7] if len(node)>7 else {}))
        key,name,description,effect=passive
        pp.CATALOG[key]=dict(id=key,who='merrin',branch=branch_id,branchName=title,theme=theme,enchantment=enchant,name=name,description=description,kind='passive',effect=effect,requires=root[0],advanced=False)

    import bathing_outfits
    bathing_outfits.OUTFITS['merrin']=('Lilac bathing two-piece','Opaque slate-lilac swim top and full-coverage bikini briefs; her spirit form keeps its pearly translucence around her hands and outline.')
    for key in ('merrin-outfit-2','merrin-outfit-3','merrin-bathing'):
        g['ORIGINAL_ASSETS'][key]='/assets/portraits/'+('bathing/merrin' if key=='merrin-bathing' else key)+'.webp'
        if key!='merrin-bathing':g['ORIGINAL_ASSETS']['overview-'+key]='/assets/portraits/overview/'+key+'.webp'

    import conversation_voice as cv
    cv.ROWS['merrin']=(
      '“That is what I remember. Let us check whether the surviving record agrees before we rely on it.”',
      '“For the next outing, I would like a clear return plan and a place to stop if someone needs rest.”',
      '“Write down who saw it and what they actually saw. We can add an explanation when we have one.”',
      'Merrin tells you about a chapel play in which the magistrate kept addressing the audience as his tax committee. “The cook had to remind him that nobody had agreed to pay for the performance.”',
      'Merrin closes her book. “Would you like to sit beside me? I would enjoy an evening with you that nobody needs to record.”',
      'Candid spirit chapel keeper with patient humour. Distinguishes memory from evidence, asks before helping, and enjoys plays and painted pots. Speaks plainly; never gives cryptic supernatural pronouncements.')

    import party_journey_content as journeys,signature_growth,foundation_chamber,provisions,armoury,art_catalogue
    if 'merrin' not in journeys.CAST:journeys.CAST.append('merrin')
    journeys.VOICES['merrin']=(
      'A keeper can be released from an old duty without treating the care they gave as a mistake.',
      'Keep the warning useful, and make sure someone can leave the post without abandoning the next traveller.',
      'An echo of a welcome is not an invitation from a person who can answer us. Let us record what it actually does.')
    journeys.CAMPS['merrin']=('A part for the journey home','Merrin folds a dry copy of the comedy. “I brought one page. If the magistrate follows us any farther, he will have to carry his own bag.”',
      'Merrin reads the clerk’s instructions for finding a missing petition: look under the magistrate. “He has been sitting on it for half the scene.” She offers you the pompous reply and waits until you are ready to read.')
    signature_growth.PERSONAL['merrin']=('Sheltering resonance','intercept','Interception adds 1 personal cover per rank.')
    foundation_chamber.INVITATION_REPLIES['merrin']='Yes. I want to share this evening with you. The castle may benefit, but that is not why I am saying yes. We can stop if either of us wants to.'
    provisions.PREFERENCES['merrin']='garden'
    armoury.FOCUS_MAP['merrin']='scholars-folio'
    armoury.STARTERS['merrin']='field-staff'
    art_catalogue.ART_ASSETS.update({k:v for k,v in g['ORIGINAL_ASSETS'].items() if 'merrin' in k})

    ac.PAIRS.append(('mira','merrin','Records people can use',[
      ('Two names on the copy','Mira has put her name on the new transcription. Merrin asks where the original copyist belongs. “Beside mine, with the work distinguished,” Mira replies. “You are right; the heading was too small.”','They make separate lines for the original copyist and the new transcription, leaving an unknown name explicitly unknown.'),
      ('A useful disagreement','Merrin thinks a smudged word is bell. Mira reads bowl. The sentence mentions something being polished. Neither considers that enough to settle it.','They keep both readings in a note and ask a later reader to compare the letter forms, rather than presenting a compromise word as certain.'),
      ('The reader’s question','A household reader asks why the comedy booklet has so many small notes. Merrin wonders whether they have made pleasure look like homework. Mira takes the question seriously.','They keep the reading copy clear and put the detailed notes on a separate page. Nobody has to study the transcription to enjoy the play.')]))
    cc.PAIR_CHOICES[('mira','merrin')]=[
      (('Ask which work each name identifies','“Copying the old text and making this transcription,” Mira says. Merrin adds, “And any correction should have its own date. A neat page can still tell us who did what.”'),('Thank them for keeping the first copyist visible','“She made the page we could read,” Merrin says. “I would like that labour to remain visible even when her name is missing.” Mira enlarges the heading.'),('Ask them to leave an unknown name unknown','“Yes,” Mira says. “We can keep looking without printing the name we hope to find.” Merrin labels the gap plainly.')),
      (('Ask them to compare another word in the same hand','Mira finds a clearly written bowl on the next page. Merrin checks the loop against the smudge. “Useful evidence. Still not a complete letter.” They record the comparison.'),('Say both readings can remain available','“Then the reader can see why we disagree,” Merrin says. Mira writes both words beside the image of the line, with neither hidden in a footnote.'),('Ask whether the word needs settling before anyone can read the play','“No,” Mira says. Merrin smiles. “The cook can polish an unspecified object while we continue laughing.”')),
      (('Suggest a clear reading copy with separate notes','“The play first, the evidence afterwards,” Mira says. Merrin puts the note page inside the back cover where an interested reader can find it.'),('Offer to try reading it aloud without the notes','You read the cook’s scene. Merrin waits until you finish before asking where you stumbled; Mira marks that line for a clearer layout.'),('Say some readers will enjoy the notes as much as the play','“Then they deserve good notes,” Mira says. “They do not need compulsory notes.” Merrin adds a short contents line so either kind of reader can choose.'))]
