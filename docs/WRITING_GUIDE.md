# Writing for Stonework and Spellcraft

Standing rule: use plain English in instructions and conversations. State what an action does. Do not hide requirements or effects behind vague phrasing.

Player-facing text should help the player understand a choice while giving the characters something worth saying.

## Interface text

- Name the action: **Buy provisions**, **Assign to foraging**, **Equip sword**.
- State the result, cost, duration and missing requirement where they matter. Use values supplied by the rules instead of duplicating changing numbers in prose.
- Name the person, room, resource or task. Avoid vague references to a stronger bond, a quieter rhythm or something becoming possible when the actual effect can be stated.
- Use established terms consistently: crowns, provisions, advancement points, phases, equipment sets and personal corners.
- Distinguish owning, equipping, preparing and activating. Do not imply an item in storage gives a character its benefit.
- Keep brief instructions beside the action. Put longer explanations in Help and link to the relevant topic.
- Write the reason an action is unavailable so the player knows what to do next.

## Dialogue and scenes

- Give each conversation a concrete subject: a repaired object, a letter, a disagreement, a mistake or a remembered event.
- Let the character's priorities, knowledge and reactions show her personality. Do not make every character praise usefulness, safety or quiet company in the same words.
- Tell the anecdote rather than saying that the character tells an amusing story.
- Make each choice a specific response to the current scene. The reply should acknowledge that response.
- Deliver the promised content. If the player asks for an explanation, give the explanation. If a character tells a story, include what happened and how it ended. “She explains in practical detail” is a placeholder, not an explanation.
- Give the exchange a purpose: solve a disagreement, compare observations, ask for something, reveal a preference, share a joke or make a decision. A social scene does not need a gameplay reward to have substance.
- Let people disagree, be mistaken, take pride in a detail and enjoy things outside their work. Avoid giving the whole cast the same speech about trust, usefulness, quiet or being allowed to rest.
- Use the character's established voice and interests. `conversation_voice.py` contains directions for the named companions; these guide style and do not establish new past events.
- Keep game effects beside the choice. Characters should discuss the event in their own words, rather than reciting resource summaries or interface instructions as dialogue.
- Keep warmth, humor and affection, but make them arise from what the characters say and do.
- Match the title to the event and use the character's associated room when appropriate.
- Keep intimate scenes adult, mutually chosen and non-graphic. Declining or choosing quiet company should remain understandable and respectful.

## Maintenance

Preserve stable IDs, choice keys, progression gates and historical save text during editorial changes. Review Help whenever a rule changes. Check the affected action and its feedback together; update wording assertions without weakening behavior checks. Historical release notes describe their own versions and should not be rewritten as current instructions.

Before accepting a scene, ask: What are they talking about? What does the response actually tell the player? Could another companion say it unchanged? Does the reply answer the selected question? Revise any answer that depends on an unspecified “detail”, “lesson”, “feeling” or “change”.

## Status and navigation

- Call each full cycle a **day**, with **morning**, **afternoon** and **evening** phases. Advance moves one phase.
- Prefer **current task**, **paid project**, **chapter project** and **equipment set** to primary assignment, funded undertaking and loadout. Stable code IDs do not change.
- Work points measure crafting or construction progress, not elapsed time. Do not promise one phase per point when bonuses or several workers can contribute.
- Show relationship icons alongside names, exact values and accessible meters. Never make colour or an unexplained symbol the only status cue.
- Trust, affection and respect run from 0 to 12. Zero is little recorded history, not dislike. Affection can be platonic. Do not invent emotional tiers from score thresholds.
- Describe romance using the milestones actually chosen. High scores alone do not make someone a romantic partner; paused invitations preserve past milestones.
- Put the current status, latest relevant change and next requirements together. Link directly to the controls. Keep past conversations and future requirements in expandable sections.
- Reuse established artwork where its meaning fits. New icons follow the engraved art style; keep exact full-resolution masters in a separate source-art archive outside the game folder. Ship only appropriately sized, losslessly encoded display copies.

- Use the actual duration unit: matching work phases, field uses or elapsed phases. A charge-based effect must not appear to expire on every Advance. Name its recipient and effect beside its icon.
- Equipment comparisons must come from the same rules as the action. Distinguish equipment bonuses from skill, party and action bonuses, and do not add together effects that do not stack.
- Room conversation markers count available, unshared conversations. Journal thumbnails show known places and owned artifacts; do not suggest an undiscovered reward.
- Keep master artwork outside the game folder. Verify package contents before every release, while preserving the pixels of runtime assets.
