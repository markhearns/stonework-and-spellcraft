"""Persistent procedural companions with authored, branching everyday dialogue.

Only selected public ingredients and the speaking person's own saved replies
are used. Ancestry never determines values, preferences, consent or personality.
"""
from copy import deepcopy

# hobby, value, difficulty, an anecdote about the hobby, a question for the player
LIVES = {
 'playful': ('word games', 'Humour should include the person being teased.', 'She sometimes keeps a joke going after the moment has passed.', 'I like changing one word in a proverb. A stitch in time saves embarrassment is my current favourite. Less elegant, much more honest.', 'Do you enjoy guessing games, or would you rather hear the answer?'),
 'poised': ('drawing little architectural details', 'Curiosity matters more than looking knowledgeable.', 'She rehearses questions until an ordinary conversation feels like a presentation.', 'I draw door handles. Someone must have decided that a sleeping fish was the correct thing to grasp before entering a pantry. I want to know that person.', 'Would you rather sketch with me, or walk and point out things to draw?'),
 'bold': ('singing lively songs', 'An enthusiastic invitation must leave room for a refusal.', 'She proposes ambitious plans before checking how tired everyone is.', 'I like songs with a chorus a stranger can join. The high notes are optional; conviction is considerably easier to share.', 'Would you join the chorus, or listen while I try the tune?'),
 'coy': ('card tricks', 'A trick is only fun when everyone knows it is a game.', 'She can hide a sincere request inside too much teasing.', 'I can hide a card in my sleeve. The difficult part is not grinning at the sleeve before the reveal. That needs more practice than my hands do.', 'Would you like to guess the trick, or have me explain it?'),
 'quiet': ('watching birds', 'An attentive answer is worth more than filling a silence.', 'She sometimes assumes a small kindness needs no spoken thanks.', 'I like watching birds decide whether a twig is worth carrying. Some turn it three times before rejecting it. I recognise that working method.', 'Would you watch with me, or talk while we walk?'),
 'sunny': ('baking savoury biscuits', 'Hospitality includes asking what someone actually likes.', 'She can mistake giving advice for helping.', 'I put rosemary in savoury biscuits. Just enough to smell it when you break one. Too much and the biscuit starts making promises only a hedge can keep.', 'Would you rather compare recipes, or help taste the next batch?'),
 'restless': ('finding short walking routes', 'People should be free to change plans after learning something new.', 'She starts a new experiment before writing down the result of the last one.', 'I like short walks with one unfamiliar turning. A grand expedition needs packing; a small detour needs noticing where I started.', 'Would you rather plan our route, or choose a turning as we go?'),
 'romantic': ('collecting and sharing poems', 'Affection needs attention to the particular person.', 'She can overprepare a small occasion and miss the pleasure of being there.', 'I like poems about ordinary objects. A declaration about the moon is easy; making me care about a chipped blue cup takes observation.', 'Would you rather read a poem aloud, or hear me read it?'),
}
# Concrete professional dilemma and three genuine answers.
WORK = {
 'bookbinder': ('A repair someone can repeat','When I repair a hinge, I want the next owner to see where the new stitch goes. A beautiful repair that cannot be repeated has left out half its instructions.',
  [('Ask which step beginners usually miss','Leaving enough slack to open the book. Tight stitching looks tidy while it is closed, then pulls at the paper when somebody reads it. I mark the open angle in the instructions.'),('Suggest preserving an awkward original stitch','I would ask what matters about it before cutting. It may be somebody’s first repair. If it holds, I can show the difference on a sample instead.'),('Ask to watch before trying it yourself','Of course. Watch where the thread bends at the hinge. Then tell me which part I moved too quickly to follow.')]),
 'lampwright': ('Light that does not dazzle','I want a lamp people can read beside without squinting. A bright flame is easy to admire from across the room and rather less pleasant above the page.',
  [('Ask how she tests the shade','I read the same small print with the lamp on each side. Then I look up. If I can still see the flame when my eyes close, the shade needs changing.'),('Suggest making the room brighter instead','For a shared table, yes. For one reader, it wastes light and wakes everyone else. I would start by asking how many people need the lamp.'),('Ask what makes a lamp comfortable to carry','A handle with room for gloves and a latch I can find without looking down. Pretty catches are not always kind to cold fingers.')]),
 'glassworker': ('The rim against the hand','I keep coming back to the edge of a cup. The colour gets noticed first; the rim decides whether anyone reaches for it again.',
  [('Ask how she checks the rim','I turn it against a folded cloth and feel for a snag, then check its thickness against the light. A smooth thick edge can be comfortable. A sharp thin one is merely impressive.'),('Say you like visible imperfections','So do I, if they are not cracks. An uneven colour can make a cup recognisable. A weak joint will only make it memorable in an expensive way.'),('Ask about her colour notes','I compare pieces at the same window and record the hour. Otherwise I may congratulate a mixture for something the afternoon light did.')]),
 'courier': ('A route someone can follow','A delivery note should tell the next courier which door actually opens. The grand front entrance is often the least useful fact about a building.',
  [('Ask which landmarks she records','A bridge, a public sign and the side of the building where someone answers. Trees change and private gardens are poor directions for a stranger.'),('Suggest asking people on the way','Certainly. But I would rather ask one good question than send the next courier knocking on five wrong doors.'),('Ask what happens when the route is blocked','I record the detour after travelling it. A plausible line on a map is not evidence that a loaded cart fits through the gate.')]),
 'gardener': ('A comparison worth keeping','I want to know whether a plant improved because I changed the water or because the weather changed. Changing everything at once makes a wonderful story and a poor comparison.',
  [('Ask how she keeps the comparison fair','Similar pots, the same light and one change in watering. I date the notes before I decide which plant looks happier.'),('Suggest trusting her experience','Experience tells me where to look. The comparison tells me whether I was right. I would like to keep both.'),('Ask what she grows just for pleasure','Flowers with an interesting scent. Not every pot needs a useful yield. I can enjoy a plant and still keep sensible notes about it.')]),
 'waterkeeper': ('Where the water goes','I measure at the far end of a channel as well as the gate. Opening a gate wider means little if the water is escaping before it reaches anyone.',
  [('Ask what she checks first','The joints and the low places where water sits. Then I compare the flow before and after the bend. I want to find the loss before promising more supply.'),('Suggest using a larger channel','If the present one is too small, yes. If it leaks, a larger channel only gives the leak more water.'),('Ask how she explains a measurement','A marked cup and a fixed interval. People can repeat that. I would rather give them a checkable result than an impressive-looking number.')]),
 'mapmaker': ('A map that admits uncertainty','I want my notes to distinguish a route I walked from one somebody described to me. Both are useful, but they are different kinds of evidence.',
  [('Ask how she marks the difference','A solid line for a walked route, a broken line for a report, with the source and date beside it. The legend belongs on the same page.'),('Say too many notes can obscure the route','Agreed. The route must remain readable. I put the explanation in the margin and keep only the warning beside the actual turning.'),('Ask what small detail she would include','Where a person can turn a loaded barrow around. Grand maps love distances and forget the width of a doorway.')]),
 'conservator': ('The mark worth preserving','Before cleaning an old object, I want to know which marks belong to its use. A stain can be damage; a faded tally can be the reason someone kept it.',
  [('Ask how she decides what to clean','I ask the owner, record the marks and test a small edge. If the answer is uncertain, I would rather pause than remove the evidence.'),('Suggest making it look new','If that is what the owner wants and the material can bear it, we can discuss it. Looking new is a choice, not the automatic meaning of repaired.'),('Ask how she records a failed treatment','With the conditions and a clear warning, not a flattering description. The next person should not pay for my mistake a second time.')]),
}


def ingredients(profile):
    selection=profile.get('generationIngredients',{})
    return selection.get('background'),selection.get('temperament')


def eligible(state,who):
    p=state.get('people',{}).get(who,{})
    if who=='merrin':return p.get('identitySource')=='authored-local-encounter'
    b,t=ingredients(p)
    return (p.get('identitySource')=='reviewed-candidate-proposal' and b in WORK and t in LIVES
            and LIVES[t][0] in p.get('personality','') and LIVES[t][1] in p.get('personality',''))


def life(selection):
    return LIVES.get(selection.get('temperament','quiet'),LIVES['quiet'])


def scenes(state,who):
    if who=='merrin':
        from chapel_spirit import SCENES
        return deepcopy(SCENES)
    p=state['people'][who];b,t=ingredients(p);hobby,value,difficulty,anecdote,question=LIVES[t]
    title,opening,choices=WORK[b]
    preference=state.get('scriptedCompanions',{}).get(who,{}).get('companyChoice')
    reminder=('Last time you chose '+('taking part' if preference=='join' else 'watching or listening')+'. That was for that occasion; you can choose differently today. ' if preference in ('join','listen') else '')
    return [dict(id='craft',title=title,opening=opening,choices=[dict(id=str(i),label=q,reply=a) for i,(q,a) in enumerate(choices)]),
      dict(id='values',title='What matters to her',opening=value+' '+{'playful':'I sometimes keep a joke going after the moment has passed.','poised':'I can rehearse a question until it sounds like a presentation.','bold':'I sometimes propose a grand plan before asking how tired everyone is.','coy':'I can hide a sincere request under too much teasing.','quiet':'I sometimes forget that thanks need to be said aloud.','sunny':'I have a habit of giving advice when someone wanted a listener.','restless':'I can start the next experiment before writing down the last result.','romantic':'I can prepare an occasion so carefully that I forget to enjoy it.'}[t],choices=[
       dict(id='ask',label='Ask how she catches herself doing that',reply='I try to ask what the other person wants before offering my next idea. If I have already rushed ahead, I can name it and start the question again.'),
       dict(id='challenge',label='Say good intentions do not always prevent a mistake',reply='No. If I get it wrong, I need to hear what happened and change what I do. Explaining what I meant is not the same as putting it right.'),
       dict(id='own',label='Say you may need her to ask directly',reply='Then I will ask directly. You can tell me when you want company, when you want advice and when you want to be left to work. I would rather hear it than guess.')]),
      dict(id='company',title='Away from work · '+hobby,opening=reminder+anecdote+' '+question,choices=[
       dict(id='join',label='I would enjoy taking part',reply='Then we can try it together when we choose a time. I will explain the first step, and you can tell me what you would change.'),
       dict(id='listen',label='I would rather watch or listen first',reply='Of course. I enjoy showing someone what caught my interest. Watching does not commit you to taking a turn.'),
       dict(id='pass',label='It is not for me, but I am glad you enjoy it',reply='Fair enough. I can enjoy it without recruiting you. We can find something else to share.')])]


def view(state):
    import game as g
    return {who:{'scenes':scenes(state,who),'history':deepcopy(state.get('scriptedCompanions',{}).get(who,{}).get('history',[])),
                 'available':g.character_at_castle(state,'founder') and g.character_at_castle(state,who)}
            for who in state['people'] if eligible(state,who)}


def apply(state,action):
    if action.get('type')!='talk-scripted-companion':return False
    import game as g
    who=action.get('characterId');g.require(isinstance(who,str) and eligible(state,who),'Choose an introduced companion with a prepared conversation.')
    g.require(g.character_at_castle(state,'founder') and g.character_at_castle(state,who),'Return home together before having this conversation.')
    scene=next((r for r in scenes(state,who) if r['id']==action.get('topicId')),None)
    g.require(scene is not None,'Choose an available conversation topic.')
    choice=next((r for r in scene['choices'] if r['id']==action.get('choiceId')),None)
    g.require(choice is not None,'Choose one of the displayed responses.')
    record=state.setdefault('scriptedCompanions',{}).setdefault(who,{'history':[]})
    if scene['id']=='company':record['companyChoice']=choice['id']
    transcript=[{'speaker':state['people'][who]['name'],'text':scene['opening']},{'speaker':'You','text':choice['label']},{'speaker':state['people'][who]['name'],'text':choice['reply']}]
    record['history'].append({'topicId':scene['id'],'choiceId':choice['id'],'title':scene['title'],'lines':transcript,'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
    del record['history'][:-24]
    state['additionalResidents'][who]['conversation'].extend(deepcopy(transcript))
    del state['additionalResidents'][who]['conversation'][:-60]
    return True
