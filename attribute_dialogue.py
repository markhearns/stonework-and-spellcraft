"""Authored alternatives with visible deterministic qualifications and remembered delivery."""
from character_approaches import score, spec

def option(label, response, attribute, skill, follows='warm'):
    return dict(label=label,response=response,requirement=spec(attribute,skill,8),follows=follows)

PERSONAL = {
'mira': [
 option('Separate the date, the account and the interpretation with three small marks.', 'Mira studies your suggested marks. “A correction, a recollection, an argument. Three different things pretending to be one sort of ink.” She restores your description and writes her disagreement beside it. “There. We can both be present on the page.”', 'intelligence','scholarship','curious'),
 option('“I trust your precision. I would like it to protect my voice as carefully as the date.”', 'Mira rests the pen across the open book. “That is a rather exact compliment.” After a moment she adds, “And a fair request.” She asks which words you want restored, rather than choosing them for you.', 'charisma','diplomacy')],
 'tamsin': [
 option('Work out four small suppers from the leftovers, including one for her.', 'You divide what is actually on the table, without pretending it is a feast. Tamsin checks the portions and takes her own back. “A plan with me in it. Yes. I could get used to those.”', 'intelligence','artifice','curious'),
 option('“Your seat belongs at this table even when someone else arrives hungry.”', 'Tamsin looks at the empty chairs, then pulls hers in. “You make that sound so obvious.” She begins eating before the food cools. Together you agree that the next late supper can be someone else’s kindness.', 'charisma','diplomacy')],
 'iona': [
 option('Draw a detour that keeps the omitted road entirely optional.', 'Iona follows the alternative with a fingertip. “You have managed to be helpful without being curious at my expense.” She leaves the old road blank. The new line is enough for today.', 'intelligence','fieldcraft','curious'),
 option('“A map can tell us where we can go without telling us where you have been.”', 'Iona’s shoulders loosen. “Good. Because the second map would need several arguments in the margins.” She folds this one towards you, with the blank still intact.', 'charisma','diplomacy')],
 'aurelia': [
 option('Demonstrate a slow attention exercise, and let her decide whether to try it.', 'You keep the exercise simple: name the sound, find its source, return to the room. Aurelia tries it once. “A way back,” she says. “I had only been practising ways to leave quickly.”', 'resolve','channeling','curious'),
 option('“You can come back frightened. We still want you at the table.”', 'Aurelia looks as though she had expected a speech about courage. Your shorter invitation takes longer to answer. “Then I should like to come back,” she says.', 'charisma','diplomacy')],
 'neris': [
 option('Find where the glaze hid the crack, without taking the cup from her.', 'Neris turns the cup as you describe the stress line. “That is the part I hoped nobody would notice.” She pauses. “It is also the part I need to understand.” She asks you to hold the cloth while she examines it.', 'intelligence','artifice','curious'),
 option('“Your eye for beauty is real. So is your ability to learn from this.”', 'Neris gives the leaking cup a reluctant smile. “Two true things. I was hoping one would cancel the other.” She keeps it on the workbench as a study piece, with the cloth underneath.', 'charisma','diplomacy')],
 
 'sabine': [
 option('Return a precise compliment about the thought she chose to notice.', '“You listened to the part I was struggling to say.” Sabine’s polished answer fails to arrive. Her smaller smile does. “Yes,” she says. “I did.” For once neither of you improves the wording.', 'charisma','diplomacy'),
 option('Let the compliment stand through a comfortable silence.', 'You resist the urge to rescue either of you with another sentence. Sabine eventually laughs under her breath. “It appears a compliment can survive without a supporting performance.”', 'resolve','channeling','candid')],
 'maren': [
 option('Sketch a reversible repair that keeps the old cushion.', 'Maren checks the joints in your sketch. “I could have made the repair independent of my taste.” She sets the new cushion aside and begins drafting a question for the chair’s owner.', 'intelligence','artifice','curious'),
 option('Help her phrase an apology that offers restoration without demanding gratitude.', '“I fixed what was broken and changed what was yours. Which parts would you like put back?” Maren reads the words once. “That leaves the answer with them.” She keeps the note.', 'charisma','diplomacy','candid')],
 'brakka': [
 option('Ask about the skill behind the anvil work, rather than the feat of strength.', 'You ask how she knew where the load would fall. Brakka explains, slowly at first, then with pleasure. “That is the part nobody asks about.” The broken anvil becomes a story about judgement.', 'intelligence','artifice','curious'),
 option('“Tell me the story you would choose if you did not have to earn a laugh.”', 'Brakka rubs her thumb along the table. “There was a winter I learned to mend tiny bells.” She watches your face, then continues when you do not turn it into a joke.', 'charisma','diplomacy')],
 'fenna': [
 option('Hold the awkward pause without rushing to fill it for her.', 'Fenna starts a second joke, then stops. “I was worried you were annoyed with me.” You explain what bothered you. She listens, asks one question, and keeps the joke for later.', 'resolve','channeling'),
 option('Offer her a graceful way to correct the joke without making herself the next target.', '“That came out sideways. Can I try again?” Fenna tests the words. “No self-inflicted punchline?” she asks. You shake your head. She tries again, and this time says what worried her.', 'charisma','diplomacy','candid')],
 'kaede': [
 option('Break the game into a slow practice round where each movement is explained.', 'You make the sequence small enough to try without an audience. Kaede misses a turn, notices that nothing terrible follows, and asks to repeat it. “Teaching the rules should count as part of the game.”', 'dexterity','athletics','curious'),
 option('“You have explained the rules patiently to other people. Let me explain this one, and you can ask as many questions as you need.”', 'Kaede starts to object, then recognises the double standard before you name it. “One practice round,” she says. “And then you may invite the others.”', 'charisma','diplomacy')],
 'elowen': [
 option('Distinguish the question you need answered from the experience you need heard.', 'You explain where advice would help and where it would interrupt. Elowen listens to the whole distinction. “I have been treating the absence of a solution as a gap I must fill.” She asks you to continue your story.', 'intelligence','scholarship','curious'),
 option('“I value your judgement. Right now, I would value your company.”', 'Elowen puts the remedies aside. “Company I can offer without diagnosing anything.” She pulls her chair closer and asks what happened next.', 'charisma','diplomacy')],
 'nyssara': [
 option('Redesign the label so the hazard identifies a process, and the maker’s mark identifies her work.', 'You separate the operating warning from the attribution. Nyssara checks that neither has become smaller. “Clearer, and nobody has had to pretend there is no hazard.” She approves the wording after changing one technical term.', 'intelligence','artifice','curious'),
 option('“We can insist on safe handling and insist that your name receives fair treatment.”', 'Nyssara taps the two parts of the label. “Yes. Both.” She asks you to bring that exact distinction when the label is discussed, rather than speaking on her behalf without her there.', 'charisma','diplomacy','candid')],
 'sylva': [
 option('Describe the difference between a plant surviving a cut and flourishing after one.', 'Sylva relaxes as you name the difference. “Capacity is not an invitation.” She shows you where this specimen is putting its new growth; the demonstration involves no cutting.', 'intelligence','scholarship','curious'),
 option('Help her offer a clear refusal with no promise of a later gift.', '“I am not offering cuttings from this plant.” Sylva repeats it without adding an excuse. “That feels unfinished,” she says, then smiles. “Perhaps it is allowed to end there.”', 'charisma','diplomacy','candid')],
}
PAIR = {
'mira-tamsin': ('Write down what changes with the weather and what signs to look for.', 'Mira makes a place for observations beside the quantities. Tamsin supplies three concrete signs instead of “you will know.” They test the new instruction aloud and each catches something the other missed.', 'intelligence','scholarship'),
'iona-fenna': ('Agree on a simple leaving word and a place to reunite.', 'Iona chooses the meeting place; Fenna chooses a phrase she will actually remember to use. Neither has to stop enjoying the journey. They try the agreement once before discussing anything more ambitious.', 'charisma','diplomacy'),
'aurelia-kaede': ('Make the invitation specific: company now, training only if both ask later.', 'Aurelia accepts the company. Kaede moves the practice notes off the bench herself. “I can leave them there,” she says. Aurelia sits beside her without checking the notes.', 'charisma','diplomacy'),

'sabine-elowen': ('Find the sentence that is truthful but unnecessarily accusatory.', 'You point to the sentence and leave the pen with Elowen. Sabine offers two ways to soften the accusation without weakening the answer. Elowen writes a third version, and asks them to read it again.', 'charisma','diplomacy'),
'neris-elowen': ('Suggest that each name her preferred temperature before either prepares a drink.', 'Neris requests cool; Elowen requests warm. They exchange cups and laugh at how simple that solution was. “An astonishing breakthrough in asking,” Neris says.', 'intelligence','artifice'),
'maren-brakka': ('Suggest a temporary grip mock-up before either commits to the final tool.', 'Brakka winds scrap cord around a wooden blank. Maren tests it and identifies the awkward edge immediately. The next sketch includes both their notes, and neither has had to reject a finished gift.', 'dexterity','artifice'),
'nyssara-sylva': ('Compare the support’s intended load with the stem’s actual direction.', 'Nyssara finds a joint that can move without losing its support. Sylva checks that the new clearance leaves room for growth. They agree to observe it before making another alteration.', 'intelligence','artifice'),
'mira-brakka': ('Act out the repair slowly while Mira annotates the awkward moments.', 'You brace the mock assembly while Brakka demonstrates the troublesome hand position. Mira adds room for fingers, a warning about the slip, and a small note: “Ask the person who has done it.”', 'might','athletics'),
'iona-nyssara': ('Add a map key that shows both time saved and conditions of passage.', 'Nyssara lists the threshold’s conditions. Iona marks the ordinary road with equal care. The result lets a traveller decide without having to guess which line the mapmaker approves of.', 'intelligence','fieldcraft'),
 'tamsin-sabine': ('Help turn the compliment into recognition of a specific piece of work.', 'Sabine names the changing portions, the late arrivals and the effort of remembering. Tamsin nods. “That was what I wanted you to see.” The list stays closed until they have finished talking.', 'charisma','diplomacy'),
}

def definitions(key):
    parts=key.split(':')
    if len(parts)==3 and parts[0]=='personal' and parts[2]=='0':
        return {'approach:'+str(i):v for i,v in enumerate(PERSONAL.get(parts[1],[]))}
    if len(parts)==3 and parts[0]=='pair' and parts[2]=='1' and parts[1] in PAIR:
        label,response,attribute,skill=PAIR[parts[1]]
        return {'approach:0':option(label,response,attribute,skill,'curious')}
    return {}

def choices(s,key):
    out={}
    for name,d in definitions(key).items():
        check=score(s,'founder',d['requirement'])
        out[name]={**d,'check':check,'blockers':[] if check['qualified'] else [check['detail']+'. This is an additional approach; the original responses remain available.']}
    return out
