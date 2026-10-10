"""Merrin is discovered in the restored chapel, never in random encounters."""
from copy import deepcopy

NAME='Merrin'
APPEARANCE='An adult spirit woman, appearing 24, with a slender ordinary build, pale pearly silver-grey skin, gently translucent hands and softly luminous edges along her figure and clothing, thoughtful brown eyes and a short dark wavy bob. She wears a dusty-lilac linen dress, a plain dark waistcoat, simple boots and a woven belt with a small brass bell. Her form is complete and recognisable; only its edges shimmer.'

INTRO=[
 dict(title='Someone at the chapel table',opening='A woman closes a small register as you enter the restored chapel. Light passes faintly through her fingers. “I can move the pages by concentrating on the contact,” she explains, setting the book down before relaxing her hand. “Merrin. I used to keep this room. The broken wards made it difficult to be heard; your repairs have helped. Before you ask, I am a spirit. I am also quite capable of an ordinary conversation.”',choices=[
  ('name','Introduce yourself and ask what she needs.','“A table where the records will stay dry, and someone willing to check them with me. I have forgotten some names. I would rather admit that than give a family the wrong answer.”'),
  ('history','Ask whether she remembers the castle before it was abandoned.','“Parts of it. I remember people who brought letters and the bench that caught the afternoon sun. I cannot give you a reliable account of every sealed room. Let me distinguish what I remember from what I only suspect.”'),
  ('space','Ask whether rebuilding the room disturbed her.','“The hammering did. The repair did not. I am glad the roof is sound. Please ask before discarding the register; the loose pages are worth keeping.”')]),
 dict(title='A room for the living',opening='Merrin opens the register to a list of names. “Some came here to remember someone. Some wanted ten minutes without being given work. I want the chapel to make room for both. It need not have one faith, and it should not become a museum of my preferences.”',choices=[
  ('open','Offer space for different observances and quiet visits.','“Then we can put the rules plainly by the door: respect other people’s time, ask before moving their tokens, and leave a place to sit.”'),
  ('ask','Ask what she would keep from the old chapel.','“The habit of asking what someone needs. And the little bell. It signals that a gathering is beginning; it does not order anyone to attend.”'),
  ('limits','Say that you cannot promise to recover every lost record.','“Nor can I. Let us protect what survives and label the gaps. I am asking for careful work, not a promise neither of us can keep.”')]),
 dict(title='Her own place here',opening='“I would like to help,” Merrin says. “But I do not want to spend every waking hour being the woman who died here. I enjoy comic plays, badly painted flowerpots and company that asks me about today. If I stay, I want a place of my own away from this table.”',choices=[
  ('trial','Offer a trial visit and discuss a private room.','“A visit first suits me. A door I can close matters. Being a spirit does not give other people permission to enter. We can talk about work after we know whether living together is comfortable.”'),
  ('interests','Ask which comic play she would like to hear again.','“The one where a magistrate disguises himself as his own clerk and has to take his own complaints. I forget the title. I remember laughing. I would enjoy finding it for that reason alone.”'),
  ('time','Tell her she has time to decide.','“Thank you. I can keep the register company while we think. The offer will be easier to consider when it has a room and ordinary terms attached to it.”')])
]

SCENES=[
 dict(id='touch',title='How she holds the book',opening='Merrin turns a page with a faintly translucent finger. “I have no physical weight. I can still press against things when I concentrate. Books are familiar; carrying a full tray while answering questions takes more attention.”',choices=[
  dict(id='tired',label='Ask whether physical work tires her.',reply='“Fine work does, after a while. Reading is easy now. Sewing a binding needs breaks, especially if I am holding the pages as well. A support on the table helps more than telling me to try harder.”'),
  dict(id='hand',label='Offer your hand and ask whether she would like to demonstrate.',reply='“Yes, if you keep it still.” She rests her fingers in your offered palm. You feel cool, light pressure. “That is deliberate contact. It does not mean I have agreed to every other sort of touch.”'),
  dict(id='release',label='Ask what happens when her concentration slips.',reply='“A page can slip through my fingers. A cup would fall. I put things down before I stop holding them. Familiar motions need so little attention that I can enjoy the conversation instead of inspecting my own hand.”')]),
 dict(id='form',title='Her clothes, her bell and ordinary objects',opening='“The clothes you see and this small bell are part of the form I make,” Merrin explains. “The book and the flowerpot are ordinary objects. They stay on the table when I leave.”',choices=[
  dict(id='clothes',label='Ask how she chooses a different outfit.',reply='“I practise the appearance until it is familiar. Then it takes little effort to keep. I choose colours and cuts because I enjoy them. Real armour and tools still have to be made, carried and fitted; imagining a sword does not give me one.”'),
  dict(id='limits',label='Ask whether being a spirit protects her in a fight.',reply='“No. Holding a form steady enough to act gives a blow something to disrupt. Hostile magic can hurt me too. I need cover, equipment and time to recover. I cannot make the rest of the party pass through a locked gate, either.”'),
  dict(id='bell',label='Ask whether the bell can actually ring.',reply='“Yes. I concentrate on making the sound, just as I concentrate on pressing a page. It is a small signal I know well. It does not compel anyone to listen or turn me into a source of unlimited force.”')]),
 dict(id='craft',title='A name without an answer',opening='“There is a line here with a date and no name,” Merrin says. “I keep wanting to fill it. Wanting an answer is not evidence for one.”',choices=[
  dict(id='record',label='Keep the gap and record what is known.',reply='“The date, the surviving handwriting and where the page was found. That gives the next reader something to work with without turning my guess into a fact.”'),
  dict(id='search',label='Suggest comparing it with other household records.',reply='“Yes. We can look for the same hand in the library. If we find only a resemblance, I will write resemblance. I used to be less careful about that distinction.”'),
  dict(id='leave',label='Ask whether the name needs to be found at all.',reply='“Perhaps not. The person may have wanted privacy. I can preserve the page without deciding that every silence is a puzzle somebody owes me an answer to.”')]),
 dict(id='values',title='Helping without taking over',opening='“When someone is upset, I reach for a task. A chair, a cup, a list. Sometimes they wanted me to listen. I am trying to ask before arranging their entire afternoon.”',choices=[
  dict(id='ask',label='Ask what question helps her pause.',reply='“Would you like company, practical help or some time alone? Then I need to accept the answer. That second part takes more practice.”'),
  dict(id='own',label='Tell her that you sometimes need quiet company.',reply='“Then I can sit with you without trying to improve the silence. You can tell me when you are ready to talk.”'),
  dict(id='challenge',label='Say her help can still be useful.',reply='“It can. I am keeping the chairs and the lists. I am learning to offer them instead of deciding that everyone needs them.”')]),
 dict(id='company',title='The magistrate and his clerk',opening='Merrin has found a comic scene copied on the back of a household account. “The magistrate sends himself an angry letter. His clerk answers it. They are the same man. Would you read one part with me?”',choices=[
  dict(id='join',label='Read the indignant magistrate.',reply='You demand an explanation for the delay. Merrin, as the clerk, explains that the magistrate has been too busy complaining to sign his own order. She laughs before she can finish the line.'),
  dict(id='listen',label='Ask her to read both parts first.',reply='She gives the magistrate a grand voice and the clerk an exhausted one. Halfway through, she switches them by mistake. “A promotion neither of them deserved. Shall I start that sentence again?”'),
  dict(id='pass',label='Pass on the reading and ask about her flowerpots.',reply='“A fair choice. I painted one with blue pears. They were meant to be plums. I am keeping it; the flowers have not complained.”')])
]

def initialize(s):s.setdefault('chapelSpirit',dict(choices=[],history=[],introduced=False))
def saved(s):return s.get('chapelSpirit',dict(choices=[],history=[],introduced=False))
def unlocked(s):
    import headquarters
    return headquarters.ready(s,'chapel')

def definition(s):
    import character_pool as pool,candidate_proposals as cp
    selection=pool.select(s,'authored-merrin',{'ancestry':'Spirit','background':'conservator','temperament':'quiet'})
    p=pool.offline(s,selection,'authored-merrin')
    p.update(name=NAME,adultAgeYears=24,occupation='chapel keeper',appearanceDescription=APPEARANCE,
      personality='Candid, patient and quietly funny. Values accurate records, freedom of observance and help that is asked for. Enjoys comic plays and painting flowerpots. When worried, she can organise a person’s day before asking what they need.',
      origin='A former adult chapel keeper whose spirit remained near the castle’s memorial records. Restoring the chapel lets her speak clearly again. She remembers particular people and habits, but does not claim knowledge of every castle secret.',
      ambition='Preserve the surviving memorial records and open the chapel to living residents, while building a life beyond her old duties.',
      accommodationPreference='private-room',stayPreference='open-to-staying',introduction='“I would like to try living here. Let us discuss a private room and what each of us expects before we decide.”',
      personalTopic='“I want the chapel to welcome different observances and people who simply need quiet. I also want evenings when nobody expects me to be its keeper.”')
    c=cp.approved_definition(p,'merrin','authored-chapel','chapel-merrin')
    c['profile'].update(identitySource='authored-local-encounter',arrivalMethod='recruitment',generationIngredients=selection)
    c.update(principles=['clear-instruction','steady-hearth-wards'],focusName='Small brass chapel bell',departureText='“I will keep the chapel records safe. We can talk again when the household has room.”')
    return c

def view(s):
    import game as g
    if not unlocked(s):return None
    r=saved(s);i=len(r['choices'])
    return dict(introduced=r['introduced'],history=deepcopy(r['history']),scene=deepcopy(INTRO[i]) if i<len(INTRO) else None,canIntroduce=i==len(INTRO) and not r['introduced'],atHome=g.character_at_castle(s,'founder'))

def apply(s,a):
    if a.get('type') not in ('chapel-spirit-talk','chapel-spirit-introduce'):return False
    import game as g,arrivals
    initialize(s);r=saved(s)
    g.require(unlocked(s),'Restore the chapel before discovering its keeper.')
    g.require(g.character_at_castle(s,'founder'),'Return home to speak with Merrin.')
    g.require(not r['introduced'],'Continue Merrin’s existing visit or household conversation.')
    if a['type']=='chapel-spirit-talk':
        i=len(r['choices']);g.require(i<len(INTRO),'The discovery conversation is complete.')
        d=INTRO[i];c=next((x for x in d['choices'] if x[0]==a.get('choice')),None)
        g.require(c is not None,'Choose one of Merrin’s displayed responses.')
        r['choices'].append(c[0]);r['history'].append(dict(title=d['title'],opening=d['opening'],playerLine=c[1],response=c[2]))
    else:
        g.require(len(r['choices'])==len(INTRO),'Finish the discovery conversation before offering a visit.')
        g.require('merrin' not in s['people'],'Merrin already has a saved identity.')
        s['localEncounterCandidates']['merrin']=definition(s)
        arrivals.contact(s,'merrin','chapel-discovery');r['introduced']=True
        g.add_journal(s,'Merrin, the chapel’s spirit keeper, agreed to discuss a trial visit. A private room and a separate household invitation are still required.')
    return True

def register(g):
    import living_stories as ls,resident_specialties as rs,headquarters as h
    import companion_life as life
    g['ORIGINAL_ASSETS'].update({'merrin':'/assets/portraits/merrin.webp','overview-merrin':'/assets/portraits/overview/merrin.webp'})
    ls.ROUTINES['merrin']={'morning':['chapel','library'],'afternoon':['conservatory','common-room'],'evening':['common-room','chapel','bedroom']}
    ls.GREETINGS['merrin']='“I put the register away. Tell me about your day.”'
    ls.CHAINS['merrin']=ls.chain('chapel','What belongs in the register',
      'Merrin lays a memorial entry beside a private letter. “They were kept together. That does not mean they should both be put on display. What would you do?”',
      {'private':('Keep the private letter out of the display.','“A public name is not permission to publish every confidence. I will keep it in a labelled cover.”'), 'ask':('Look for the writer’s wishes before deciding.','“Then we look carefully and keep it private until we have a reason to do otherwise.”'), 'context':('Display a summary with the personal details removed.','“That may tell the useful part without taking more than the writer offered. I will mark it as a summary.”')},
      'A register people can use',
      {'private':'“You asked me to protect the private letter.”','ask':'“You asked whose wishes the display should respect.”','context':'“You suggested a summary that leaves the confidence private.”'},
      'Merrin shows you a repaired cover. “I have made space for corrections and a separate place for private pages. I want the living to trust this room too.”',
      {'read':('Read the public entries together.','“Take the chair by the window. We can stop whenever either of us needs to.”'),'closed':('Suggest closing the register for the evening.','“Gladly. I would like to hear a story whose ending I do not have to verify.”')})
    rs.NAMES['merrin']=NAME
    d=rs.specialty('merrin','chapel','Merrin’s restful sanctuary ward',28,'Adds 1 vitality recovered per phase of rest at home when food is sufficient, up to the normal maximum of 6. Does not heal people away on patrol or restore vitality while working.')
    rs.SPECIALTIES['merrin']=d;h.JOBS['specialty-merrin']=deepcopy(d)
    life.PROJECTS['merrin']=dict(name='A register with room for the living',description='Merrin repairs the memorial register, labels uncertain entries and separates private letters from the public record. Gentle preservation protects what remains without inventing what is missing.',costCrowns=10,materials={'binding-thread':2,'sun-amber':1},requiredWorkPhases=3,principle='gentle-preservation',awardId='merrin-register-study',result='Merrin gains 2 advancement and learns Gentle preservation, which is also recorded in the archive. No missing names or hidden castle facts are invented.')
    life.ENSEMBLES['merrin']={'working':dict(name='The chapel keeper',portraitId='merrin',components=['Dusty-lilac linen dress','Plain dark waistcoat','Woven belt and small brass bell','Simple boots'])}

    import merrin_content
    merrin_content.register(g)
