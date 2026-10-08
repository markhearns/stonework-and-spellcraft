"""Authored adult visitors. Identity, personal voice and competence are distinct."""
from copy import deepcopy


def profile(who,name,age,ancestry,role,practice,ambition,origin,private=False):
    return {'personId':who,'name':name,'adultAgeYears':age,'lifeStage':'adult','ancestryLabel':ancestry,
        'role':f'{ancestry} {role} · {age}','identityRevision':1,'identitySource':'authored-summoning-sample',
        'startingPractices':[practice],'ambition':ambition,'origin':origin,
        'accommodationPreference':'private-room' if private else 'separate-bed',
        'offeredAssignments':['rest','archive','crafting','training','inscribing','spellwork']}

AURELIA={
    'profile':profile('aurelia','Aurelia',24,'Seraph','lantern conservator','archive-focus',
        'Record the useful lights that guide people home, including the imperfect ones.',
        'A seraph conservator from a dusk-lit hospice of travelling scholars.',True),
    'categoryId':'lantern-scholar','categoryName':'A keeper of useful light',
    'principles':['gentle-refraction'],'focusName':'Conservator’s shuttered lantern',
    'greeting':'“Aurelia. Your invitation arrived at dusk, which I consider good manners.” She sets a shuttered lantern beside her. “Tell me about this library of yours.”',
    'stayText':'“Yes. A private room, shared evenings, and useful work agreed between us. That sounds like a home I could choose.”',
    'departureText':'“I will leave by the next crossing. Keep a lamp in the window if you would like to see me again.”',
    'topics':{
        'intentions':{'label':'Ask about the lights she keeps','text':'“I restore lanterns and study the way light is guided. A beautiful instrument ought to be useful. I am equally fond of useful things becoming beautiful.”'},
        'home':{'label':'Discuss her private room','text':'“A room of my own, please. Wings need space and so do thoughts. I enjoy company; I also enjoy choosing when to close my door.”'},
        'visit':{'label':'Offer an introduction to the castle','text':'“A visit would please me. Show me the archive first. We can decide about staying once we have met properly.”'}},
    'personalTopics':{
        'light':{'label':'Ask about her favourite light','text':'“Lamplight, low enough that people lean closer.” Aurelia smiles. “Excellent for difficult texts. Among other things.”'},
        'wings':{'label':'Ask about travelling with wings','text':'“Doors are the real adventure. Everyone asks about the sky; no one asks about narrow staircases.” She folds her wings with practiced grace.'},
        'flirt':{'label':'Compliment her elegance','text':'Her eyes linger on yours. “You may admire me. I chose these clothes with rather more care than the lantern.” A warm smile. “And I do appreciate an attentive audience.”'}},
    'personality':'Measured, warmly teasing, elegant and practical; enjoys being admired, dislikes being treated as a sacred obligation.'}

NERIS={
    'profile':profile('neris','Neris',21,'Elemental','glassworker','careful-assembly',
        'Build a notebook of glass vessels that are a pleasure to hold and use.',
        'A water elemental glassworker from the canal workshops beyond the threshold.'),
    'categoryId':'vessel-maker','categoryName':'A maker of curious vessels',
    'principles':['water-guidance'],'focusName':'Glassworker’s tide cup',
    'greeting':'“Neris. I was testing a cup, not listening at the water, but here you are.” Her grin widens. “Is that a workshop behind you?”',
    'stayText':'“I would like that. My own bed, room for my cups, and people who can laugh when a first attempt is dreadful. Shall we try making a home of it?”',
    'departureText':'“Next crossing, then. I will pack the cups myself. Keep my place in the conversation; I may have a better joke when I come back.”',
    'topics':{
        'intentions':{'label':'Ask about her glasswork','text':'“Bowls, cups, curious little vessels. I like making something your hand wants to pick up. I know water guidance; shaping a new working still takes materials and practice.”'},
        'home':{'label':'Discuss a bed and workshop space','text':'“A separate bed is enough; a shared room is fine. And no, a basin is not accommodation.” She laughs. “I like blankets.”'},
        'visit':{'label':'Ask whether she would like to visit','text':'“Yes. Let me see the rooms and meet people first. I can bring a cup. One cup. I am exercising remarkable restraint.”'}},
    'personalTopics':{
        'glass':{'label':'Examine her favourite cup','text':'Neris turns the cup between her fingers. “A little uneven. It fits my hand better that way. Perfect things can be terribly hard to get comfortable with.”'},
        'water':{'label':'Ask about canal life','text':'“Everyone knows everyone along the canal. You cannot make a dramatic exit if three neighbours are waiting to borrow your good kettle.”'},
        'flirt':{'label':'Offer a teasing compliment','text':'“Oh, good. I was beginning to think you only liked my craftsmanship.” She tips her head, smiling. “I like being looked at like that. Your turn to come a little closer—if you like.”'}},
    'personality':'Lively, tactile, inventive and openly playful; enjoys mutual teasing and takes her craft seriously.'}


def catalogue(iona_profile,iona_topics,iona_personal):
    return {'iona':{'profile':iona_profile,'categoryId':'practical-magic-visitor','categoryName':'A surveyor of small crossings',
        'principles':['gentle-preservation'],'focusName':'Surveyor’s measuring cord','topics':iona_topics,'personalTopics':iona_personal,
        'greeting':'“Hello? I am Iona. Your invitation found my desk between two thoroughly unhelpful maps. Shall we introduce ourselves properly?”',
        'stayText':'“I would like to stay, if the household would like that too. My atlas can grow here. Let us keep work arrangements separate.”',
        'departureText':'“Of course. I will pack my case and take the next crossing. Keep the correspondence; a goodbye need not be the last page.”'},
        'aurelia':deepcopy(AURELIA),'neris':deepcopy(NERIS)}


AURELIA['profile']['appearanceDescription']='Warm golden-tan skin, amber eyes, white-gold braids, a thin worn-gold halo and folded feather wings; a slate-violet long-sleeved bodice, closed charcoal work skirt, belt and worn boots.'
NERIS['profile']['appearanceDescription']='Sea-glass teal skin, dark teal eyes, silver-white wavy bob, small fin-shaped ears; an indigo halter blouse and plum wrap skirt with a narrow bare midriff.'
