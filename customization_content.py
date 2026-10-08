"""Authored tastes and optional adult companionship; deterministic content."""
# colour, hobby, refreshment, room, keepsake, individual voice, flirt
PROFILES = {
'mira':('teal','bad poetry','spiced tea','library','annotated poems','“A book may be serious. Its owner need not be serious every minute.”','“The dress has no pockets. You will have to hold my book while I distract you.”'),
'tamsin':('plum','mending','honey tea','common-room','a repaired ribbon','“Something soft, something useful, and a chair nobody needs me to mend.”','“I left the apron on its hook. Try to think of a compliment that has nothing to do with my work.”'),
'iona':('amber','music','apple cordial','common-room','a handwritten refrain','“An evening deserves a song that nobody has commissioned.”','“This neckline is not a musical notation. Though I appreciate your concentration.”'),
'aurelia':('ivory','quiet walks','mint tea','chapel','a pressed feather sketch','“I like a place where being still is not mistaken for being on guard.”','“My wings are folded. You may stop leaving quite so much room between us.”'),
'neris':('blue','puzzles','citrus water','library','a glass puzzle','“A beautiful problem should offer a satisfying answer and an excuse to stay.”','“Yes, I noticed you looking. No, I have not yet decided how difficult to make your next move.”'),

'sabine':('violet','word games','rose cordial','common-room','a folded calling card','“A little elegance is useful. It gives a thoroughly improper joke somewhere respectable to sit.”','“You may admire the ribbon. A good compliment, however, should reach the person wearing it.”'),
'maren':('copper','sketching','ginger tea','workshop','a small mechanism drawing','“I want a corner where an unfinished idea is allowed to remain unfinished.”','“I know how this fastening works. I was waiting to see whether you would lose your train of thought.”'),
'brakka':('green','carving','barley tea','common-room','a carved wooden bird','“A sturdy chair. Something warm to drink. Company that can enjoy a comfortable silence.”','“Come here. You look as though you could use a very unprofessional hug.”'),
'fenna':('blue','trail stories','berry cordial','conservatory','a trail sketch','“I like seeing the door, hearing the rain, and knowing I do not have to go anywhere.”','“You keep glancing at my tail. It is not going to rescue you from answering whether you like the outfit.”'),
'kaede':('crimson','strategy games','smoked tea','common-room','a polished game stone','“Leave room for the board. I prefer a worthy opponent to an ornamental victory.”','“I dressed for a pleasant evening. If you wish to surrender already, at least make it charming.”'),
'elowen':('green','flower arranging','herbal tea','conservatory','a pressed blossom','“A growing thing, a comfortable seat, and someone who notices both.”','“You have been very attentive to the flowers. Shall I give you something else to compliment?”'),
'nyssara':('silver','stargazing','blackberry cordial','library','a constellation drawing','“Soft light helps. I prefer a conversation that does not hurry to explain itself.”','“The invitation was to sit beside me. You may interpret that particular sentence quite literally.”'),
'sylva':('moss','gardening','honey water','conservatory','a fallen seed pod','“Let the room feel lived in. A leaf on the table is not a failed household.”','“I saved the warm patch for both of us. You need not hover at its edge.”'),
}
COLOURS=('teal','plum','amber','ivory','blue','burgundy','violet','copper','green','crimson','silver','moss','charcoal')
HAIR=('Keep established hair','Loose','Braided','Pinned up','Half tied','Short and tousled')
OCCASIONS={'everyday':'Everyday','expedition':'Expedition','formal':'Formal evening','leisure':'Leisure','private':'Private evening'}
GARMENTS={
 'linen-shirt':('base','Linen shirt','everyday'), 'travel-tunic':('base','Travel tunic','expedition'),
 'evening-dress':('base','Draped evening dress','formal'), 'soft-blouse':('base','Soft open-neck blouse','leisure'),
 'silk-slip':('base','Opaque silk slip with lace edging','private'), 'open-shoulder':('base','Off-shoulder evening blouse','formal'),
 'trousers':('lower','Tailored trousers','everyday'), 'long-skirt':('lower','Long wrap skirt','everyday'),
 'shorts':('lower','Leisure shorts','leisure'), 'slit-skirt':('lower','Side-slit skirt','formal'),
 'boots':('feet','Walking boots','expedition'), 'slippers':('feet','Soft slippers','leisure'), 'barefoot':('feet','Bare feet','leisure'),
 'shawl':('outer','Soft shawl','everyday'), 'cloak':('outer','Travel cloak','expedition'), 'robe':('outer','Loose evening robe','private'),
 'ribbon':('accessory','Silk ribbon','formal'), 'pendant':('accessory','Personal pendant','everyday'), 'stockings':('accessory','Patterned stockings','formal'),
}
SPACES={
 'reading':{'name':'Reading nook','room':'library','cost':4,'material':'binding-thread','detail':'A cushion, a book rest and a place for the next page.'},
 'craft':{'name':'Personal making shelf','room':'workshop','cost':4,'material':'binding-thread','detail':'Small trays and a cloth keep unfinished ideas together.'},
 'music':{'name':'Music and games corner','room':'common-room','cost':4,'material':'binding-thread','detail':'A place for handwritten songs, game pieces and easy company.'},
 'green':{'name':'Little indoor garden','room':'conservatory','cost':4,'material':'silver-ivy','detail':'A small planted bowl and space for a fallen leaf.'},
 'quiet':{'name':'Quiet retreat','room':'chapel','cost':4,'material':'binding-thread','detail':'A soft seat and an uncluttered surface for a private thought.'},
 'dressing':{'name':'Dressing and keepsake corner','room':'common-room','cost':4,'material':'binding-thread','detail':'A folded cloth, a small mirror and a place for treasured ribbons.'},
}
SPECIALIZATIONS={
 'healer':{'name':'Healer','attribute':'intelligence','skill':'channeling','description':'Mending light restores 1 additional health, up to the existing maximum of 6.'},
 'trail-guide':{'name':'Trail guide','attribute':'dexterity','skill':'fieldcraft','description':'+1 to your Fieldcraft approach scores.'},
 'envoy':{'name':'Envoy','attribute':'charisma','skill':'diplomacy','description':'+1 to your Diplomacy approach scores.'},
 'artificer':{'name':'Artificer','attribute':'dexterity','skill':'artifice','description':'+1 to your Artifice approach scores.'},
 'lorekeeper':{'name':'Lorekeeper','attribute':'intelligence','skill':'scholarship','description':'+1 to your Scholarship approach scores.'},
 'wardkeeper':{'name':'Wardkeeper','attribute':'resolve','skill':'channeling','description':'+1 to your Channeling approach scores.'},
 'pathbreaker':{'name':'Pathbreaker','attribute':'might','skill':'athletics','description':'+1 to your Athletics approach scores.'},
}
SCENES={
 'tastes':('The things that make a day yours',0),
 'leisure':('An evening without an errand',0),
 'style':('A second opinion at the mirror',1),
 'space':('A corner with your name on it',0),
 'private':('The evening can wait',3),
}
