# v0.64 — Personal expression and a place of your own

Open **Character customization** from Home, a character sheet, Household, Wardrobe or Equipment. The portrait selector keeps the chosen person consistent across seven tabs: Overview, Appearance, Wardrobe, Preparations, Development, Tastes & invitations, and Personal space. Existing individual controls remain available.

## Appearance and recruitment

Save hair styling, hair colour, eyes, complexion, build, markings and accessories for each household member. These are descriptive choices, not attribute changes. The screen supplies a portrait brief incorporating the saved details and selected ensemble. Founder portrait generation includes these details; existing artwork is only replaced through the established review/import flow. Established companions keep their identity, ancestry and adult age. Founder name, pronouns, age and background remain in the existing identity editor.

Curated recruit proposals now offer explicit hair and build choices, alongside ancestry, background, temperament and story. Automatic choices remain available. Imported content-pack character composition retains its existing compatibility rules. The draft review still allows appearance prose to be edited before approval.

## Wardrobe

The new screen brings the existing 28 illustrated relaxed/daring outfits for 14 companions together with personal ensembles for every household member, including the founder and generated residents. Existing illustration-based selections display their actual artwork and retain their established shared-history requirements.

Each person can save twelve named ensembles. Nineteen garment descriptions cover base garments, lower garments, footwear, outer layers and accessories. Five occasions—everyday, expedition, formal, leisure and private—organize them. Thirteen colours and free styling notes provide further variation. Layers are validated: one base, at most one lower garment/footwear/outer layer, no trousers under a full dress or slip, and a lower garment for shirts/blouses. Private garments belong to the private-evening occasion.

Private-evening ensembles for companions require an established mutual partnership; pausing romantic invitations prevents newly choosing them. An outfit does not create a relationship or grant statistics. Choosing an illustrated outfit clears a custom selection, and choosing a custom ensemble clears the illustrated selection. Imported descriptive wardrobe choices also participate in this exclusivity. Earlier component and ensemble controls remain accessible.

**Artwork limit:** custom garment combinations and appearance edits are saved descriptions, not automatically rendered paper dolls. Their screen explicitly retains and labels the established portrait. No new garment illustrations, character portraits or room paintings are claimed. Existing illustrations are reused; no crude overlays are added to room paintings.

## Complete preparations

Save up to eight named preparations per person, covering:

- Personally prepared core and imported spells, sharing the real slot limit.
- The two prepared practices.
- An individually owned working tool.
- Household and expedition signature-focus inscriptions.
- An owned imported focus and its installed inscription.

Loading works on a private candidate state and validates the existing rules before committing. Changed ownership, lost training, insufficient capacity, pending casting and locked equipment produce explanations without partially applying the set. Existing casting plans obey the usual preparation rules and may pause if their spell is put aside. Loading grants no spells, materials, equipment, work or time. This does not snapshot an entire inventory, clothing choice or every independent public-project configuration.

## Tastes, flirting and everyday life

All fourteen authored companions have distinct favourite colours, hobbies, refreshments, preferred rooms, keepsake ideas, conversational voices and flirtatious lines. Other generated residents can use the same systems with a modest general profile. Companion preferences are revealed by conversation; the founder can edit their own preferences.

Five optional invitation types cover discovering tastes, leisure without errands, a second opinion at the mirror, a personal corner and a private evening. These use each companion's preferences and voice; they are five shared scene structures with character-specific material, not seventy wholly separate stories. Shared replies remember the chosen response and actual participants. Completed scenes do not expire or repeat for relationship rewards.

Friendship activities remain available. Romantic responses require mutual attraction; the mirror scene's kiss requires a first date, and the private-evening scene requires an established partnership. Romantic pauses are respected. Content includes playful compliments, alluring opaque ensembles, teasing, affectionate proximity and kissing, with non-explicit private evenings.

After learning a companion's tastes, bringing their favourite refreshment costs two crowns and creates one remembered thoughtful gesture. Repeating it cannot farm trust. No gesture automatically advances a romantic milestone.

An agreed favourite room changes afternoon **rest** locations only. Work, expeditions and evening sleeping arrangements take precedence. The choice must be a restored communal room. Preferences and actual memories are supplied to optional dialogue generation; future scene replies are not.

## Specializations and mentorship

Seven selectable specializations require a related attribute of at least 6 and skill rank 2:

| Path | Requirements | Benefit |
| --- | --- | --- |
| Trail guide | Dexterity / Fieldcraft | +1 Fieldcraft approach score |
| Envoy | Charisma / Diplomacy | +1 Diplomacy approach score |
| Artificer | Dexterity / Artifice | +1 Artifice approach score |
| Lorekeeper | Intelligence / Scholarship | +1 Scholarship approach score |
| Wardkeeper | Resolve / Channeling | +1 Channeling approach score |
| Pathbreaker | Might / Athletics | +1 Athletics approach score |
| Healer | Intelligence / Channeling | +1 Mending light healing, still capped at 6 health |

Only one is selected at a time. Selection at home is reversible and does not cost an additional phase or advancement on top of the required training. Retraining below its prerequisites suspends the benefit. The approach bonus is visible in the existing calculation and never removes ordinary options. Healer adds to the existing restorative technique bonus, without also granting the Wardkeeper score bonus.

The Development tab retains attributes, skills, perks, principles, practices and the real lesson system. Completed lessons now offer a mentor–learner reflection using the actual teacher, learner and subject. Both people must be home. Each distinct teacher/learner/subject reflection is remembered once; opening a lesson offer never invents completion or a memory.

## Personal spaces and possessions

Six corner designs offer reading, making, music/games, greenery, quiet and dressing/keepsakes. Fit one active corner per person in its matching restored communal room or their assigned bedroom. Each design costs four crowns and one listed unreserved material once. Refitting an owned design, moving it to another valid location or putting it away is free. Buying a corner does not create a bed or change assignments.

Corners are visible as illustrated character cards on the room screen and in Personal space. Give them a title and optionally display a memento from the person's actual completed quest, returned lantern expedition or shared memory. False or other people's unshared history cannot be selected. Personal keepsake *ideas* in preferences are not silently awarded inventory items. The source of a displayed memento remains recorded.

## Saves and verification

Version 0.64, save schema 55. Migration adds empty customization state, preserving existing art, inventories, progression, relationships and unfinished work. It awards no outfits, specializations or furniture retroactively.

Stop the old server, extract this release into a fresh directory, copy the complete existing `data` directory including `data/assets`, then run `python server.py`. The store creates a pre-migration database backup. Keep the old release and backup for rollback.

Verification: the 725-test Python regression and all 40 connected UI suites pass. Subsequent focused checks pass 22 customization tests, nine existing household-content tests and the connected customization journey. The two final customization cases extend the suite to 727 collected tests; no second full 727-test run is claimed. JavaScript syntax checks pass.

Rendered browser layout remains unverified under the previously documented environment limitations. Connected tests exercise actual templates, controls and Python-store transitions; they do not substitute for a screenshot review. No live image-provider result is claimed.
