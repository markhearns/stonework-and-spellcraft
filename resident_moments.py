"""Authored adult household moments. Content is separate from authoritative rules."""
MOMENTS = {
    'mira-greenhouse': {
        'title': 'A room that grows back', 'participants': ['mira'], 'requirement': 'conservatory',
        'invitation': 'Mira has been looking at the restored Conservatory. She has a thought about keeping things alive.',
        'lines': [('Mira', '“Books survive by being left alone. Plants seem to take that personally.” She brushes a dry fleck of soil from her cuff.'), ('You', '“Has the garden won you over?”'), ('Mira', '“It has made a respectable argument. I like a room that can surprise us without another expedition.”')]},
    'mira-index': {
        'title': 'The book that refuses a category', 'participants': ['mira'], 'requirement': 'mira-project',
        'invitation': 'With her living index finished, Mira wants to discuss the things an archive should leave undecided.',
        'lines': [('Mira', '“The index works. Naturally, I am now defending one book from it.”'), ('You', '“What category does it belong in?”'), ('Mira', '“Travel, recipes, and a very unconvincing love affair. I want the next reader to find it by accident.”'), ('Narrator', 'You suggest listing the book under travel and adding a note about its recipes. Mira agrees, but insists the dreadful love affair belongs in the recommendation.')]},
    'mira-folio': {
        'title': 'A deliberately wrong order', 'participants': ['mira'], 'requirement': 'mira-keepsake',
        'invitation': 'Mira offers to show you a favourite page from her finished cloth folio.',
        'lines': [('Mira', '“I put the terrible poem first. It makes everything after it seem rather accomplished.”'), ('You', '“And is the terrible poem yours?”'), ('Mira', '“That information is not covered by your borrowing privileges.” Her smile gives away considerably more than the catalogue would.')]},
    'tamsin-settling': {
        'title': 'A door that closes', 'participants': ['tamsin'], 'requirement': 'resident',
        'invitation': 'Tamsin is ready to talk about settling into her own room.',
        'lines': [('Tamsin', '“I have found a place for my boots. That is usually when a room begins to feel like mine.”'), ('You', '“Anything else you need?”'), ('Tamsin', '“For now? The freedom to close the door without it meaning that anything is wrong.”'), ('You', '“Of course.”'), ('Tamsin', '“Then I think we will manage very well.”')]},
    'tamsin-notebook': {
        'title': 'Leave the repair visible', 'participants': ['tamsin'], 'requirement': 'tamsin-project',
        'invitation': 'Her repair notebook is complete. Tamsin would like to explain a choice in its stitching.',
        'lines': [('Tamsin', '“A repair need not pretend the damage never happened. Sometimes a visible seam is the honest part.”'), ('You', '“Is that why you chose the contrasting thread?”'), ('Tamsin', '“Yes. And because I liked the colour. Not every decision needs a lecture attached.”')]},
    'tamsin-case': {
        'title': 'The scrap worth keeping', 'participants': ['tamsin'], 'requirement': 'tamsin-keepsake',
        'invitation': 'Tamsin has an answer to why the smallest compartment in her finished case is still empty.',
        'lines': [('Tamsin', '“That space is for something I have not found yet.”'), ('You', '“Planning ahead?”'), ('Tamsin', '“Leaving room. There is a difference.” She shuts the little case with evident satisfaction. “I am trying to remember it myself.”')]},
    'shared-shelf': {
        'title': 'An argument about a shelf', 'participants': ['mira', 'tamsin'], 'requirement': 'resident',
        'invitation': 'Mira and Tamsin invite you to witness a very minor disagreement about books.',
        'lines': [('Mira', '“A shelf should invite browsing.”'), ('Tamsin', '“It should also survive it.”'), ('Narrator', 'Mira proposes a gloriously crooked row; Tamsin demonstrates why the heaviest volume cannot go on top. Their mock solemnity lasts until you offer to label the whole arrangement “under discussion.”'), ('Mira', '“An excellent category.”'), ('Tamsin', '“Provided it is written on a removable label.”')]},
    'shared-margins': {
        'title': 'Two kinds of marginal note', 'participants': ['mira', 'tamsin'], 'requirement': 'both-projects',
        'invitation': 'Their professional projects are finished. The two residents offer to share tea and compare their very different notes.',
        'lines': [('Tamsin', '“Mine says which stitch held.”'), ('Mira', '“Mine says the previous owner was clearly in love with somebody dreadful.”'), ('You', '“Both useful information.”'), ('Narrator', 'They exchange a glance, then begin comparing examples. Tamsin asks about the person behind a crooked annotation; Mira asks how the page was repaired. Neither abandons her own interests to become a copy of the other.'), ('Tamsin', '“Another cup?”'), ('Mira', '“Yes. I have several more objections to your punctuation.”')]},
    'mira-close-reading': {
        'title': 'A closer reading', 'participants': ['mira'], 'requirement': 'mira-flirt',
        'invitation': 'Mira offers a closer seat and a playful reading from her folio. This follows your already welcomed flirtation.',
        'lines': [('Mira', '“You may sit closer, if you like. The handwriting is unusually demanding.”'), ('Narrator', 'You accept the offered place beside her. She holds the folio between you, though her amused glance suggests the small print is only part of the invitation.'), ('You', '“I think I can read it from here.”'), ('Mira', '“How inconvenient for my excuse.” She leaves the choice to linger comfortably open.')]},
    'tamsin-loose-thread': {
        'title': 'One loose thread', 'participants': ['tamsin'], 'requirement': 'tamsin-flirt',
        'invitation': 'Tamsin has noticed a loose thread on your cuff—and offers a teasing excuse to sit together.',
        'lines': [('Tamsin', '“May I?” She indicates the thread, waiting for your nod before smoothing your cuff.'), ('You', '“Is this a professional consultation?”'), ('Tamsin', '“The thread is. The invitation to stay is personal.”'), ('Narrator', 'She withdraws her hand with a small, knowing smile and leaves you room beside her. You stay to talk; the unfinished work can keep its place.')]},
}

MOMENTS['mira-refraction']={
    'title':'What the light brings home','participants':['mira'],'requirement':'refraction',
    'invitation':'The returned discovery of Gentle refraction has given Mira something to wonder about.',
    'lines':[('Mira','“A little borrowed starlight, made useful for reading. I approve of this direction for grand discoveries.”'),
        ('You','“Less grand than an observatory?”'),
        ('Mira','“More intimate. Someone built a place to look at the sky. We get to decide what that knowledge means here.”'),
        ('Narrator','Mira asks which lens you would try first. You compare a reading lamp with a small projector until she sketches a design in the margin.')]}

MOMENTS.update({
    'iona-settling': {
        'title':'A place to leave the field case','participants':['iona'],'requirement':'resident',
        'invitation':'Iona has found a corner for her field case. She invites you to see a small change in how she unpacks.',
        'lines':[('Iona','“Usually I leave the clasp facing the door. It saves a moment when I am going.”'),('You','“And today?”'),('Iona','“Today it is facing the desk.” She considers this, then smiles. “Do not make a ceremony of it. I shall become unbearable.”')]},
    'iona-atlas-finished': {
        'title':'The page with no grand discovery','participants':['iona'],'requirement':'iona-atlas',
        'invitation':'Her atlas is finished. Iona wants to show you the page she thinks travellers will actually use.',
        'lines':[('Iona','“This mark means the step is slippery. This one means someone keeps a dry seat nearby.”'),('You','“No dragons?”'),('Iona','“A dragon is usually quite good at announcing itself. A loose step prefers an ambush.”'),('Narrator','Iona shows you the note beside each hazard: loose step, deep rut, dry shelter. She has left enough space for the next traveller to add corrections.')]},
    'iona-mira-map': {
        'title':'A map with room for a story','participants':['mira','iona'],'requirement':'iona-atlas',
        'invitation':'Mira and Iona have spread a map across the table. They invite you into a friendly dispute over its margins.',
        'lines':[('Mira','“If the ferry keeper was secretly writing love letters, surely that belongs on the map.”'),('Iona','“Only if the letters change where the ferry stops.”'),('You','“An appendix?”'),('Mira','“A very important appendix.”'),('Iona','“Fine. But you are drawing the little hearts.”'),('Narrator','Iona draws the ferry landing clearly. Mira adds the keeper’s story beneath it, then asks whether the appendix can have an illustration.')]},
    'iona-case': {
        'title':'The map that will not lie flat','participants':['iona'],'requirement':'iona-keepsake',
        'invitation':'Iona offers to show you the contents of her new map case, including one particularly uncooperative sheet.',
        'lines':[('Iona','“It has spent so long folded that it considers being flat an unreasonable demand.”'),('You','“Should we press it under a book?”'),('Iona','“Later. For now, I rather like that it remembers where it has been.”'),('Narrator','She folds the map along its familiar creases and slips it into the case. The worn corners remain visible.')]},
    'iona-return': {
        'title':'The same desk, another arrival','participants':['iona'],'requirement':'iona-return',
        'invitation':'After returning and choosing to stay again, Iona has a thought about familiar places.',
        'lines':[('Iona','“I knew which floorboard would complain. It complained exactly on schedule.”'),('You','“A dependable welcome.”'),('Iona','“Yes. You kept the correspondence, too.” She rests a hand on her field case. “It is pleasant to come back without having to become a new person first.”')]},
})

MOMENTS.update({
    'aurelia-settling':{'title':'A door and a lamp','participants':['aurelia'],'requirement':'resident',
        'invitation':'Aurelia has found a place for her lantern and invites you to see her room.',
        'lines':[('Aurelia','“A door of my own. A lamp that stays lit when I am reading. I am surprisingly easy to please.”'),('You','“Surprisingly?”'),('Aurelia','“Do not spread it around. I have a reputation for exquisite standards.”')]},
    'neris-settling':{'title':'The cup beside the bed','participants':['neris'],'requirement':'resident',
        'invitation':'Neris has unpacked exactly one cup. She wants an opinion on her restraint.',
        'lines':[('Neris','“One cup. One shelf. A triumph of moderation.”'),('You','“How many are still in your bag?”'),('Neris','“That is a private matter between me and the bag.”')]},
    'aurelia-lamplit':{'title':'A flattering light','participants':['aurelia'],'requirement':'companion-project','illustrationId':'aurelia',
        'invitation':'Her lantern study is complete. Aurelia offers to demonstrate a particularly flattering light, with you as her invited audience.',
        'lines':[('Aurelia','“Stand there a moment. Yes—just where I can see you.”'),('Narrator','She turns the lantern shutter. Warm light catches the curve of her bare shoulder and the knowing smile she makes no effort to hide.'),('You','“Is this still a demonstration?”'),('Aurelia','“It is. I am demonstrating that useful light can also be terribly distracting.”'),('Narrator','She leaves a welcoming space beside the desk. The evening can be unhurried.')]},
    'neris-glasslight':{'title':'A very personal assessment','participants':['neris'],'requirement':'companion-project','illustrationId':'neris',
        'invitation':'Neris has finished her glass studies and invites you to admire the results. She seems amused about what, exactly, you might be admiring.',
        'lines':[('Neris','“The glass is up here.” Her smile makes the gentle accusation an invitation to laugh.'),('You','“I was taking in the whole composition.”'),('Neris','“Excellent answer. You may stay.”'),('Narrator','She leans against the worktable, relaxed and pleased, turning the little cup so that lavender reflections slip across her hand.'),('Neris','“Now tell me which you like best. I promise only to tease you a little.”')]},
    'aurelia-mira-light':{'title':'Where the margin begins','participants':['aurelia','mira'],'requirement':'resident',
        'friendshipDescription':'Aurelia and Mira share a fondness for intimate lamplight and increasingly elaborate excuses to keep reading together.',
        'invitation':'Mira and Aurelia are comparing notes about the correct light for a late-night book.',
        'lines':[('Mira','“Enough to read the small print.”'),('Aurelia','“Not enough to discourage someone from sitting closer.”'),('Mira','“A defensible scholarly position.”'),('Narrator','They solemnly move the lamp half an inch and dissolve into laughter.')]},
    'neris-iona-cup':{'title':'The map and the water ring','participants':['neris','iona'],'requirement':'resident',
        'friendshipDescription':'Neris and Iona trade practical observations and gentle mischief; a cup ring has become a running joke in their shared notes.',
        'invitation':'Iona and Neris have found an unexpected new island on a map.',
        'lines':[('Iona','“It appeared shortly after you put your cup down.”'),('Neris','“A discovery! Do we get to name it?”'),('Iona','“The Isle of Please Use a Coaster.”'),('Narrator','Neris sketches a tiny harbour beside the ring. Iona keeps it.')]},
    'aurelia-neris-evening':{'title':'The virtues of a little vanity','participants':['aurelia','neris'],'requirement':'resident',
        'friendshipDescription':'Aurelia and Neris enjoy each other’s confidence, exchanging compliments and clothing opinions without competing for attention.',
        'invitation':'Aurelia and Neris are discussing evening clothes, and offer you a place in the conversation.',
        'lines':[('Neris','“You chose that neckline on purpose.”'),('Aurelia','“Of course. Did you think the lantern dressed me?”'),('Narrator','Neris laughs and turns a little to show the drape of her own skirt. The compliments are generous and the teasing mutual.'),('Aurelia','“There is room for more than one beautiful thing in a household.”'),('Neris','“An excellent rule. We should keep it.”')]},
    'aurelia-return':{'title':'A familiar light in the window','participants':['aurelia'],'requirement':'companion-return',
        'invitation':'Aurelia has returned and chosen to stay again. There is a familiar warmth to her greeting.',
        'lines':[('Aurelia','“I wondered whether my favourite corner would still feel like mine.”'),('You','“Does it?”'),('Aurelia','“Come and stand beside me. I will tell you.”')]},
    'neris-return':{'title':'The promised better joke','participants':['neris'],'requirement':'companion-return',
        'invitation':'Neris has returned with the better joke she promised. Her expression suggests it may be dreadful.',
        'lines':[('Neris','“I brought a better joke.”'),('You','“And another cup?”'),('Neris','“Two cups. The joke is that I thought you would be surprised.”')]},
})
