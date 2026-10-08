"""Adult companion adventures: authored intimacy, deterministic objectives."""
# title, practical desire, first obstacle, second obstacle, invitation, complication,
# completion, flirt reply. All clothing remains covered; intimacy is optional.
PERSONAL = {
'mira': ('The scandal in the margins','recover a forgotten masquerade script and attribute it correctly','cipher','repair',
 'Mira has found an unsigned masquerade comedy in a damaged folio. “Everyone calls it frivolous. Someone worked very hard to be this funny.” She proposes reconstructing it for a private reading. “You may audition for the charming rogue. Do try not to look so qualified.”',
 'The recovered dedication names a woman the catalogue credited only as a copyist. Mira wants her authorship preserved before the performance. “An anonymous kiss in act two is a literary problem. An anonymous author is a real one.”',
 'The repaired script now carries its author’s name. Mira arrives for the reading in a dark evening dress, an ink ribbon tied at her wrist. The rescued comedy is better than either of you expected.',
 '“You have excellent timing when you stop trying to be respectable.” She offers you the rogue’s next line and smiles over the page. “Shall we see whether you can make me blush without skipping the dialogue?”'),
 'tamsin':('An evening that belongs to her','prepare a small courtyard supper she can actually enjoy','repair','bargain',
 'Tamsin wants a supper where she is a guest. She has chosen the menu; she asks you to help repair the folding table and settle the delivery, rather than leaving every detail to her. “If you ask me where the clean cloths are while I am dressed for dinner, I shall charge you.”',
 'The supplier offers a larger feast if Tamsin organises it. She refuses with visible relief. “A good evening is not measured in how many people I look after. Help me keep this one small.”',
 'The table holds, the delivery is settled, and Tamsin takes the best chair. Her new neckline and a glint of borrowed jewellery are deliberate choices. She watches you notice, then raises her cup.',
 '“Yes, I dressed up. No, this does not mean I am serving.” She draws the other chair closer with her foot. “You may, however, tell me I look lovely again.”'),
 'iona':('The dance nobody commissioned','restore an old dance score and a safe practice platform','cipher','repair',
 'Iona has found a dance written for people who never quite meet until the last measure. She wants to try it for herself. “There are simpler ways to invite someone close. I have chosen the one with footnotes and a dangerous amount of counting.”',
 'A missing measure makes the dancers pass each other forever. Iona laughs, then asks you to help restore the ending. “No tragic symbolism. We are fixing the music.”',
 'The repaired platform is steady and the completed score has a proper ending. Iona wears a swirling skirt with a daring slit over dance shorts, and offers you a hand.',
 '“Eyes up here until you know the steps.” She waits for your offered hand, then draws you into the opening turn. “After that, I may forgive an appreciative glance.”'),
 'aurelia':('Off duty, under the stars','repair a signal lantern and clear the courtyard lookout','repair','lift',
 'Aurelia wants the lookout fit for ordinary stargazing. She has already arranged her own time off. “This is not another patrol. If you bring a report, I shall use it to prop the lantern.”',
 'The old sighting marks make the lookout feel like a post instead of a place to rest. Aurelia chooses to preserve the useful marks while clearing a space with no duty attached.',
 'The lantern is steady and the chairs face the sky. Aurelia has traded her watch coat for an evening tunic and fitted trousers; her hair is loose for once.',
 '“You may admire the view.” Her smile makes the invitation deliberately ambiguous. She leaves her hand beside yours on the arm of the chair, close enough for you to ask.'),
 'neris':('A reflection of her own','repair an optical display that shows its viewer without distortion','cipher','repair',
 'Neris dislikes an old festival mirror that makes everyone look like someone else. She wants to rebuild it as a study of honest reflections. “There are more interesting ways to be flattering than lying.”',
 'The final lens looks impressive and introduces a subtle distortion. Neris chooses clarity over spectacle. She asks whether the frame can be beautiful without pretending the glass is infallible.',
 'The finished display catches lamplight without changing anyone’s face. Neris tests it in a fitted blue dress with an open back, then turns to compare the reflection with your expression.',
 '“A satisfactory instrument,” she says. “Although I appear to have found a more flattering observer.” She holds your gaze long enough to make the experiment decidedly personal.'),
 
 'sabine':('The second entrance','repair a costume clasp and recover the original ending of a performance','repair','cipher',
 'Sabine has agreed to perform a short comedy, then discovered that its heroine exists only to be admired. She wants to restore the sharper original ending. “I can look wonderful and have something to say. It is astonishing how often people ask me to choose.”',
 'The original ending gives the heroine the last joke and the decision to leave. Sabine asks you to keep it, even if the audience expected a simpler compliment.',
 'The clasp holds and the heroine gets her ending. Sabine returns from rehearsal in a wine-coloured dress with a sweeping slit, enjoying both the costume and the applause.',
 '“Well? Was it the delivery or the dress?” She laughs before you answer. “You may appreciate both. But if you remember my best line, I shall be much more impressed.”'),
 'maren':('A very impractical commission','build a reliable folding screen for a portrait sitting','lift','repair',
 'Maren wants to make a portable portrait screen that is beautiful as well as sound. Nobody commissioned it. “I am allowed one project whose only useful purpose is that I fancy it. You may be my highly distractible assistant.”',
 'The hinges work but the frame looks severe. Maren sketches a curling edge and refuses to call ornament wasted effort. She asks for help keeping the new curve balanced.',
 'The screen stands without a wobble. Maren emerges from behind it in an elegant waistcoat over a low-cut blouse and asks where the light falls best.',
 '“I built the screen so changing would be private, not so you would stop looking afterward.” She poses with one hand on its frame. “There. A completely legitimate quality inspection.”'),
 'brakka':('A delicate sort of strength','repair a music box and lift a sheltered bench into place','repair','lift',
 'Brakka has a music box small enough to hide in her palm. She wants its tune back for a quiet evening outside. “If you say we should simply hit it harder, you may sit somewhere else.”',
 'The mechanism needs patience; the bench needs leverage. Brakka likes that neither task asks her to be only one thing. She keeps the repaired spring beside the plans until both are ready.',
 'The bench is steady and the box plays clearly. Brakka wears a soft wrap dress and the tiny repaired ornament at her throat. She has chosen the snug fit herself.',
 '“Small things deserve attention too.” She catches your glance at the ornament and gives you a knowing smile. “You may come closer to admire the workmanship. Ask first.”'),
 'fenna':('The wager with no loser','recover a fairground token and mark a safe courtyard race','search','crossing',
 'Fenna proposes a treasure hunt followed by a ridiculous little race. The prize is choosing the music for an evening together. “No embarrassing forfeits. I intend to win because I am delightful, not because I wrote dishonest rules.”',
 'The shortest route crosses a damaged plank. Fenna stops the game until it is safe. “I like a little risk in my flirting. Considerably less in the floor.”',
 'The token is found and the course repaired. Fenna arrives in a short festival dress over fitted leggings, ribbons at her wrists, with a victory speech she may never need.',
 '“If I win, you dance. If you win, I ask very nicely.” Her grin makes it clear she likes both prospects. “You see? Impeccably balanced rules.”'),
 'kaede':('The unfinished flourish','restore a practice pavilion and decode a ceremonial step pattern','repair','cipher',
 'Kaede wants to learn a flourish she has always dismissed as unnecessary. It is graceful, difficult and of no tactical use. “I may have been calling it foolish because I could not do it.”',
 'The notation leaves room for a pause instead of a perfect final turn. Kaede decides to keep that freedom. She asks you to watch the attempt rather than judge the finish.',
 'The pavilion is ready. Kaede has chosen a sleeveless formal tunic with a high side opening over fitted practice trousers. She tries the movement, misses once, and begins again without hiding her smile.',
 '“You are meant to be watching my balance.” She lets the silence last a moment. “But I did choose this outfit. I cannot claim to be entirely innocent.”'),
 'elowen':('Flowers for no occasion','clear a blocked planter drain and recover a pressed-flower pattern','water','search',
 'Elowen wants flowers for an evening that celebrates nobody’s service. “Not a thank-you for being useful. Something lovely because we are here.” She asks you to help prepare the display rather than turn it into a household duty.',
 'The recovered pattern leaves an empty space for a flower not yet grown. Elowen keeps it. “We do not have to fill every corner to prove we cared.”',
 'The drainage is clear and the display stands ready. Elowen arrives in a light summer dress with narrow straps, a flower tucked into her hair and no basket of work.',
 '“I saved you the place beside me.” She smiles as you admire the flower. “And before you ask, yes, I chose the colour hoping you would notice.”'),
 'nyssara':('The mask she chooses','recover a masquerade design and repair its silver fastening','search','repair',
 'Nyssara has chosen a mask for an evening when she can decide what to reveal. The design is missing its last panel. “A disguise need not be a lie. Sometimes it is a way to choose your introduction.”',
 'The recovered panel would expose a private emblem. Nyssara removes that part of the design. She offers you the story she does want to tell, leaving the rest unasked.',
 'The repaired mask reveals her expression while keeping its emblem private. Nyssara wears a dark gown with a low back and turns so you can admire the fastening without touching it.',
 '“Some mysteries are meant to be enjoyed rather than solved.” She offers her hand. “This invitation is not one of them. Would you like the first dance?”'),
 'sylva':('An evening allowed to bloom','clear a rain channel and decode an old planting diagram','water','cipher',
 'Sylva wants to restore a small courtyard display without forcing the plants into an old decorative pattern. “We can make a place for an evening. We do not need to make everything perform.”',
 'The diagram leaves no space for the strongest new shoot. Sylva changes the border around it instead of uprooting it. She asks you to help preserve the useful measurements, not the old rigidity.',
 'The rain channel runs freely and the revised display leaves room to grow. Sylva wears a softly draped green dress and bare shoulders under a light shawl; she has saved the evening for herself.',
 '“You have been very attentive to the garden.” She lets the shawl settle loosely and smiles. “I would not object if some of that attention wandered.”'),
}
OBSTACLES = {
 'cipher':{'name':'Recover the missing instructions','ordinary':'Compare the surviving pages and reconstruct the sequence','attribute':'intelligence','skill':'scholarship','spell':'lucid-sight','result':'The sequence is restored, with uncertainties clearly marked.'},
 'repair':{'name':'Mend the delicate mechanism','ordinary':'Clean, fit and test the parts patiently','attribute':'dexterity','skill':'artifice','spell':'borrowed-hour','result':'The mechanism passes a careful working test.'},
 'lift':{'name':'Move the heavy fitting','ordinary':'Set rollers and move it a little at a time','attribute':'might','skill':'athletics','spell':'giant-grasp','result':'The fitting rests securely in its new place.'},
 'search':{'name':'Find the misplaced keepsake','ordinary':'Search the marked area systematically','attribute':'intelligence','skill':'fieldcraft','spell':'wisp-scout','result':'The keepsake is found and its owner can identify it.'},
 'water':{'name':'Clear the blocked water channel','ordinary':'Bail the channel and clear the obstruction by hand','attribute':'vitality','skill':'athletics','spell':'water-jet','result':'The channel runs freely without flooding the neighbouring beds.'},
 'crossing':{'name':'Cross the damaged walkway','ordinary':'Secure a temporary board crossing before retrieving the far-end fittings','attribute':'dexterity','skill':'athletics','spell':'wind-step','result':'The fittings are retrieved and the route is made safe.'},
 'bargain':{'name':'Settle the supplier’s terms','ordinary':'Compare the receipts and negotiate a fair exchange patiently','attribute':'charisma','skill':'diplomacy','spell':'silver-tongue','result':'The written terms are agreed and the exchange is closed.'},
}
TEMPLATES = [
 ('a lantern for the evening','repair','search','A lantern has lost its shutter pin. Find the matching piece and make it reliable before anyone relies on it.'),
 ('the parcel with the wrong label','cipher','bargain','A delivery was mixed up. Work out who owns it and agree the corrected exchange.'),
 ('the rain-soaked rehearsal','water','repair','Rain has spoiled a small rehearsal area. Clear the runoff and repair the damaged stand.'),
 ('a keepsake beyond the walkway','crossing','search','A dropped keepsake lies beyond an unsafe walkway. Reach it safely and search without trampling the beds.'),
 ('the stubborn festival stand','lift','repair','A folding display has jammed against its heavy base. Reposition it and repair the joint.'),
 ('a page for the missing tune','search','cipher','A tune survives in two incomplete copies. Find the loose page and reconstruct a playable ending.'),
]
PLACES = ['the outer courtyard','the covered entrance walk','the sheltered garden edge','the gatehouse alcove','the courtyard steps','the low terrace']
MOODS = ['a playful wager about who will spot the answer first','a request for unhurried company after the work','a promise to wear something festive for the little celebration','a joking invitation to be their charming assistant']

REQUEST_FLIRT = {
 'mira':'“You are a very distracting research assistant.” Mira closes the notes with deliberate care. “Fortunately, we have finished the research.”',
 'tamsin':'“Sit beside me. I am finished organising things.” Tamsin smooths her skirt and smiles. “You may organise a compliment, if you like.”',
 'iona':'“A successful partnership deserves a dance.” Iona offers a hand. “A little closer than the working distance, if that suits us both.”',
 'aurelia':'“Competent, dependable, and apparently determined to make me smile.” Aurelia lets you see that she is succeeding at the last part too.',
 'neris':'“That is an unusually flattering assessment.” Neris tilts her head. “Would you care to repeat it while I am paying properly personal attention?”',
 
 'sabine':'“I was hoping you would notice.” Sabine makes a small, theatrical turn. “I refuse to believe good work and a good entrance are mutually exclusive.”',
 'maren':'“You can stop pretending you are inspecting the craftsmanship now.” Maren brushes sawdust from her waistcoat. “Unless that really was your best compliment.”',
 'brakka':'“I like someone who notices the careful work.” Brakka’s smile grows warmer. “And I am not opposed to being admired when the tools are put away.”',
 'fenna':'“Careful. I shall start thinking you enjoy my company.” Fenna leans closer to hear your answer. “A scandalous accusation. Do defend yourself.”',
 'kaede':'“That was almost smooth.” Kaede lets you wonder which part she means. “You may try again. I am enjoying the practice.”',
 'elowen':'“I was rather hoping this would become an evening together.” Elowen offers the place beside her. “The request was real. So is the invitation.”',
 'nyssara':'“No need to make a riddle of it.” Nyssara offers her hand, smiling. “Ask me to dance. I have been considering saying yes.”',
 'sylva':'“We have given the work enough attention.” Sylva settles beside you, her shawl loose around her shoulders. “I would like a little of yours now.”',
}

QUEST_RITUALS = {'cipher':'archive-circle','search':'archive-circle','repair':'maker-circle','lift':'foundation-circle','crossing':'foundation-circle','water':'garden-circle','bargain':'market-circle'}


# Additional authored quests keep existing quest IDs, rewards and memories intact.
EXTRA_PERSONAL={
 'sabine-keys':{'who':'sabine','room':'dungeons','data':(
 'The key that comes back','restore a release mechanism and catalogue its obsolete seal without inheriting an obligation','cipher','repair',
 'Sabine brings a drawing of an old release mechanism. “The lock is beautifully documented. Its way out receives half a sentence. I would like to correct that imbalance. With company, if you have an afternoon.”',
 'The recovered instructions distinguish a warning from a binding oath. Sabine crosses out the old claim of perpetual service. “Preserve the evidence. Retire the demand. Those are quite different operations.”',
 'The release mechanism passes its test. Sabine closes the corrected folio and keeps a labelled demonstration key as a shared keepsake. “There. A small, dependable piece of freedom. Shall we go somewhere without a lock to discuss it?”',
 '“I invited you because I like your company.” Sabine turns the demonstration key between her fingers and smiles. “I thought I would make the terms unusually easy to understand.”')}
}

# Early quest replies must not claim the work has already finished.
QUEST_TEASING = {'mira': '“You may charm the archivist after we have settled the attribution.”',
 'tamsin': '“A compliment and an offer to help. I accept both, in that order.”',
 'iona': '“Careful. I may expect you to be as entertaining when the work starts.”',
 'aurelia': '“I was asking for help, but I shall graciously accept the compliment too.”',
 'neris': '“A promising opening. Let us see whether your observations are as good.”',
 'sabine': '“An elegant acceptance. I reserve the right to be more impressed by the result.”',
 'maren': '“You can be charming and hold the other end. I have faith in your range.”',
 'brakka': '“Keep talking like that and I may forget where I put the plans.”',
 'fenna': '“I accept. The help, I mean. We can negotiate how insufferably pleased you are allowed to look.”',
 'kaede': '“A confident beginning. I look forward to seeing what you do with it.”',
 'elowen': '“You have made that sound considerably more inviting. Shall we begin?”',
 'nyssara': '“I understood the invitation beneath the compliment. Yes, I would like your company.”',
 'sylva': '“You may stay and distract me, provided we eventually remember why we came.”',
 'velis': '“I had prepared a persuasive argument. How inconvenient of you to agree so charmingly.”',
 'rhess': '“That was a very roundabout way to say yes.” Rhess smiles. “I liked it.”'}
