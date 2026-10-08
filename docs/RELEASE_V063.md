# Development v0.63 — The forgotten lantern pavilion

A substantial companion adventure brings fieldwork, spells, relationships and the castle together. Mira wants to preserve the pavilion's overlooked history. Tamsin wants something people will actually use. Iona wants its music to be heard again. Their concerns can coexist, but you decide which purpose the recovered corner will serve at home.

## Start the adventure

Complete Hearth wards research, then open **Expeditions → The forgotten lantern pavilion**. Home also offers a shortcut.

The pavilion has its own party selector. Mira, Tamsin and Iona can travel together, any subset can join, or the founder can investigate alone. Each companion must be a current resident, at home, and have agreed to fieldwork. Mira's existing archive-story requirement still applies. Missing companions do not prevent the ordinary expedition route.

The party is real: every selected member is away from the castle, uses their own learned principles, prepared spells and skills, pauses their household work, and returns home explicitly. Other expeditions retain their existing party limits. No resident is assigned or taken along merely because the site is opened.

Travel takes one shared phase outward and one homeward. There are five field obstacles and a final legacy decision. There is no deadline, mandatory combat, random injury or required relationship score.

## Twenty-three methods

| Stage | Free ordinary method | Specialist route | Team route | Spell route |
| --- | --- | --- | --- | --- |
| Fallen festival arch | Clear loose pieces and move it on rollers | Intelligence / Artifice | Might / Athletics plus Dexterity / Artifice | Giant's grasp |
| Musicians' crossing | Follow the bank and secure a temporary crossing | Dexterity / Fieldcraft | Might / Athletics plus Dexterity / Athletics | Borne flight |
| Flooded programme chest | Drain the maintenance channel | Intelligence / Artifice | Vitality / Athletics plus Dexterity / Artifice | Undertide breath |
| Names behind the programme | Compare programmes and repair ledger | Intelligence / Scholarship | Intelligence / Scholarship plus Charisma / Diplomacy | Lucid sight |
| Repeating rehearsal echo | Observe the cycle and reset its stops | Resolve / Channeling | Resolve / Channeling plus Dexterity / Artifice | Calming tide |
| What the lantern will light | Choose reading, music or hospitality | All three purposes remain available | No companion or score required | No spell required |

Each ordinary obstacle method takes three phases without supplies. The fifteen specialist, teamwork and spell alternatives take one phase each. Each final-purpose choice takes one packing/preparation phase. This gives twenty obstacle methods plus three legacy choices.

Specialist routes use the existing score of 9: attribute plus twice skill, including eligible companion help. Teamwork requires two different people to meet their separate role scores of 8. A single highly skilled person cannot fill both roles. All five spell routes check the actual party member's learned spell, personal principles, preparation and components. Costs are displayed and paid once on choosing the method; the cast and actual caster are recorded.

Completed obstacles and unfinished paid work survive retreat. A saved team method needs its original participants and their role qualifications to resume. If they are no longer available, the ordinary method remains a valid replacement. Previously paid solo spell work resumes without charging again. Every completed obstacle records the people who actually contributed working phases.

Threshold fold supports the real party on the return journey, and on outward travel after the site has actually been reached. It does not finish obstacles or advance unrelated castle work.

## Conversations and competing hopes

Three optional group scenes develop the adventure:

- **Three reasons to follow a programme:** decide whether to emphasise the people behind the records, practical use, or an open mind.
- **A supper without a committee:** stop working long enough to enjoy company, discuss what would otherwise be lost, or acknowledge a changed opinion.
- **Whose name belongs above the door?:** preserve names, effort and delight together; give each perspective room; or explicitly preserve uncertainty where the record is incomplete.

When all three companions are present, they address one another directly. Mira and Tamsin initially disagree about what preservation should mean. Iona refuses to let delight become the least serious contribution. Their conversation moves toward complementarity without requiring the founder to pronounce a winner.

Only companions actually present speak. A solo expedition receives a coherent reflection without invented NPC participation. Later scenes recall the founder's actual earlier response. Choices are remembered and contribute to the relationships of the people sharing them; they do not advance time or alter work assignments.

After the crossing, each participating companion also has a private scene: Mira's unrecorded joke, Tamsin's invitation to sit without organising anything, and Iona's quieter encore. Friendship is always an available response. An affectionate alternative requires an existing mutual romantic milestone and uses the current relationship stage. It does not create romance merely because the character joined the expedition, and paused romantic interactions remain respected.

Skipped field conversations remain available after a completed return, reframed explicitly as discussions at home with the actual returning companions. Nothing claims an unshared conversation already happened in camp. Shared scenes remain rereadable and cannot be repeated for rewards. People left at home do not acquire private journey memories.

## A visible, useful castle legacy

All three finds—the lantern, working ledger and songbook—are preserved under every final choice. Your decision determines the purpose of a new common-room corner:

| Purpose | Matching ordinary character-quest work |
| --- | --- |
| Reading and discoveries corner | Deciphering instructions and searches |
| Music and rehearsal corner | Delicate repairs and walkway crossings |
| Supper and planning corner | Heavy lifting, water-channel work and supplier negotiations |

After completing the fieldwork and returning, choose **Fit the recovered lantern corner** on Home or in the common room. Installation and putting it away are explicit, reversible placement actions. The legacy purpose itself is the expedition decision; putting the corner away does not change that choice.

While installed, matching ordinary character-quest methods take **two phases instead of three**. Ritual support and the lantern corner do not stack: the ordinary method remains two phases if both apply. Skills and spells still provide their separate one-phase alternatives. The committed method records the support it used; changing the installation afterward does not rewrite work already begun.

The recovered feature has a persistent illustrated card on Home and in the common room, with its purpose, exact benefit, installation state and controls. It reuses the existing generated reading-lantern object illustration; no new room painting or bespoke pavilion artwork is claimed. It does not add crude furniture overlays to the room painting or silently create an equippable item.

Once installed, **The first evening under the recovered light** lets the actual returning companions use what they brought home. With the full cast present, Mira asks Iona about the notation while Tamsin claims a chair before offering an opinion. They no longer wait for the founder to mediate. This is an optional shared memory, not automatic relationship progress.

## Rewards and integration

The first completed return grants **3 advancement to each returning participant**, **2 moon glass**, **3 binding thread**, and access to the recovered corner. Turning home early grants no completion reward and preserves field progress. The completed site cannot be repeated to farm returns.

Spell descriptions include their pavilion applications. Completed pavilion discoveries can satisfy the existing journey-evidence trigger. Actual shared pavilion scenes contribute to wardrobe history. Optional generated dialogue receives only completed pavilion memories involving the current speaker, never future replies or another companion's private scene.

Existing expeditions, character quests, romance, wardrobe unlocks and household projects remain available. The new multi-companion party behaviour is scoped to this site.

## Saves and verification

Release **0.63**, save schema **54**. Migration adds empty pavilion progress and leaves existing saves, relationships, resources and unfinished work intact. It does not invent discoveries, rewards, fieldwork agreements or installed furniture.

Stop the old server, extract this release into a fresh directory, copy the entire existing `data` directory including `data/assets`, then run `python server.py`. The store creates a pre-migration database backup. Keep the earlier release and its backup for rollback.

Tests cover all 23 methods, all three minimum-attribute solo completions, an actual four-person party, distinct team roles, precise spell ownership and costs, paid retreat/resume, changed parties, group and private scene scope, romantic prerequisites, skipped conversations shared at home, installation, non-stacking quest support, teleporting the full party, migration, backup, duplicate requests and reload.

Connected UI checks complete the whole expedition with all three companions, share group and private scenes, bring home the legacy, install it and find it again in the common room after reloading. These are template/controller tests against the real Python store, not rendered browser inspection. The previously documented browser limitations remain unresolved; no new screenshot or visual-layout pass is claimed.

Verification passed: **705 Python tests** and **39 connected UI suites**, including 13 new focused adventure tests. Final results are recorded in `VERIFICATION_V063.json` and `UI_REGRESSION_V063.json`.
