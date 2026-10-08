# v0.91 — Clearer words, better help

This release revises the game's writing, adds a searchable game guide and brings the cheat menu up to date. The seven opening chapters keep their existing progression and pacing.

## Writing and legibility

Interface introductions, action labels, requirements and feedback now use more direct language. Descriptions explain what an action does, what it needs and what happens next. Character sheets use **Character summary** and **Personal corner**, and room improvements no longer advertise an outdated number of specialists.

All **64 personal scenes across 16 companions** were rewritten around specific incidents, interests and conversations. The choices and replies respond to those incidents. Titles were updated to match. The **Time together** revision includes 64 repeatable-scene responses, 16 first-milestone openings and 16 first-milestone endings, with additional edits to invitations and related dialogue. Existing adult, consent, privacy and relationship requirements remain in place.

The expanded crafting catalogue has **316 revised descriptions and feedback messages**, including outdated guidance that claimed only four spells were usable. Catalogue IDs, rules and every field other than these summaries are unchanged. These are substantial revisions, not a claim that every line in the game was replaced.

Already saved memories, conversation history and accepted custom dialogue remain intact. New wording appears when reading current descriptions or playing future scenes; old memories are not silently rewritten.

## Help

**Help** is available in the main navigation. It contains **20 searchable topics**, covering starting a game, time and sleep, chapters, construction, recruitment, work, food, supplies, expeditions, combat, equipment, enchanting, character builds, magic, relationships, personal corners, the dungeon, cheats, resonance and common terms.

**Help with this screen** opens the relevant topic. Articles link back to a related game screen, and the pantry has a direct food explanation. Opening, searching and reading Help do not change campaign state or advance time. Help explains current rules, including food shortages, overnight rest, equipment activation and the difference between resonance and advancement.

## Cheats

The menu now supports:

- Recruit one unique companion or all remaining unique companions.
- Add provisions alongside crowns and crafting materials.
- Complete current castle rooms, bedrooms and headquarters rooms.
- Create unified equipment for a selected household member.
- Give advancement points or restore a selected member to full health.
- Continue using the existing item, knowledge and generated-resident tools.

Recruitment keeps each established character's identity, development and relationship records. It supplies ordinary starter equipment and suitable available accommodation, restoring only necessary bedrooms when possible. It clears that person's pending visit, arrival reservation or dungeon occupancy, and cancels paid summoning preparation or care through the existing refund rules. It does not award recruitment quest rewards, finish personal stories or increase affection.

The shortcut provides a week's household food if the pantry holds less. Already recruited companions are skipped when recruiting all. Other residents and reserved beds are not displaced. If recruitment cannot fit the selected companions, the whole shortcut fails without partial changes. Cheats retain the save's modified label.

Recruitment also fixes Mira's presence when recruited directly into a fresh campaign. Later introductions reuse an existing recruited character instead of creating another copy.

## Updating and verification

Stop the old server. Preserve the complete existing `data/` directory, including campaign subfolders and `data/assets`. Extract v0.91, copy that directory into the game folder, then run `python server.py`.

Schema remains **64**; no migration is required. An actual v0.90 save opened with exact state preservation, including a saved build, completed personal-scene memory, conversations and accepted custom artwork and dialogue. All **268 runtime artwork files** are unchanged. The archive contains no live campaign data.

Verification details are in `VERIFICATION_V091.json`. The original 960-test gameplay run found two assertions expecting replaced wording; both passed after updating the assertions. Subsequent targeted runs covered the affected systems and 17 new cheat tests. All 61 UI integration suites passed, with wording assertions refreshed where necessary. These checks exercise templates, controls, SQLite actions and reloads; they are not rendered-browser screenshots. Browser layout review remains outstanding because the browser executable was unavailable.
