# Stonework and Spellcraft — expansion content handoffs

The original character-foundations ZIP is included unchanged under `dependencies/`. Give the other LLM this folder, and one or more numbered assignments. Tell it: **Read 00-shared-contract.md and the assigned handoff. Generate the requested complete content pack, validate it, and deliver its files. Do not implement game code or claim unsupported imports work.**

The supplied character pack passed the prototype's structural validation: 2,100 names, 525 appearances, 525 story seeds and 445 shared records (3,595 total). It already covers personality, boundaries, voices, ambitions, clothing, ensembles, interaction seeds and story patterns. Extend those categories with usable follow-through; do not commission duplicate pools just to increase counts.

These seventeen handoffs cover the useful adjacent content areas. They are a menu and phased backlog, not a recommendation to generate everything immediately. The current runtime only imports the established character-foundations contract; all new expansion contracts need code integration and mechanical review. The prototype-reference JSON records actual current IDs/rules to ground suggestions.

## Recommended order

1. Materials/properties (01), equipment (02), household artifacts (03), and magic (04): the most useful next mechanical foundation. Supply finished material IDs to subsequent authors; otherwise they must describe an unmet dependency without inventing references.
2. Rooms/furnishings (06), expeditions (07), personal arcs (10), and branching household scenes (11): immediately useful design breadth with clear gameplay connections.
3. Rituals (05), encounters/care (08), communities/services (09), letters/commissions/gifts (12).
4. Optional books/food/gardens/treasures (14), visual briefs (15), and help/QA (16). These should follow approved concepts rather than produce art or documentation for discarded mechanics.
5. Private mystery alternatives (13), separately from public content. Avoid reading those outputs yourself if you want the eventual mystery unspoiled.

Start with a complete pilot of 5–10 entries in the high-priority areas, check that the schema and concepts are useful, then fill the stated targets. This is a quality checkpoint the author can perform without waiting for repeated permission. More content is only useful when it has distinct purposes, coherent dependencies and usable integration boundaries.

Background mappings and earned development (17) are also high-value: the received pack leaves thirty occupations unmapped. Assign this after the material/equipment/magic pilots so new packages share a coherent balance baseline.

## Assignments

| File | Pack | Priority | Requested records |
|---|---|---|---:|
| 01-materials-and-properties.md | Materials and component properties | High | 72 |
| 02-equipment-and-signature-items.md | Equipment and evolving signature items | High | 96 |
| 03-artifacts-and-recipes.md | Household artifacts and crafting recipes | High | 80 |
| 04-magic-principles-and-spells.md | Magic principles and bounded spell constructions | High | 126 |
| 05-rituals-and-voluntary-augmentation.md | Rituals, voluntary augmentation and reversal | Medium | 42 |
| 06-rooms-furnishings-and-synergies.md | Room purposes, furnishings and understandable synergies | High | 120 |
| 07-expeditions-and-discoveries.md | Expedition sites, leads and reusable discoveries | High | 126 |
| 08-encounters-and-care.md | Field encounters, negotiation and specialized care | Medium | 72 |
| 09-communities-services-and-visitors.md | Neighbouring communities, services and recurring contacts | Medium | 64 |
| 10-personal-arcs-and-relationships.md | Personal arcs and descriptive relationships | High | 78 |
| 11-household-scenes-and-ambient-life.md | Household scenes, fanservice and ambient life | High | 160 |
| 12-letters-commissions-and-gifts.md | Correspondence, commissions, gifts and keepsakes | Medium | 100 |
| 13-private-mystery-foundations.md | Alternative private castle foundations and evidence | Later; avoid spoiling active play | 42 |
| 14-books-food-gardens-and-treasures.md | Books, food, gardens and unusual treasures | Optional breadth | 124 |
| 15-art-and-visual-production.md | Art briefs and visual continuity | Optional; after concepts are selected | 93 |
| 16-tutorials-explanations-and-qa.md | Tutorial copy, explanations and integration scenarios | Useful alongside implementation | 144 |
| 17-backgrounds-training-and-perks.md | Background capability mappings, training and earned perks | High after equipment and magic | 102 |

## Suggested assignment message

> Create packs 01–04 using the supplied shared contract and prototype-reference.json. Begin with materials, then use its real IDs in equipment, artifacts and magic. Keep every new mechanical effect a separate proposed-mechanics record. Preserve the established game's agency, time and ownership rules. Generate complete files in batches, validate what you can, report honest limitations, and deliver one ZIP per completed pack. Do not stop after outlining the work.

For a prose-focused LLM, assign 10–12 instead. For a visual specialist, assign 15 only after the relevant item/room/wardrobe references are supplied. Multiple authors should own different pack namespaces and exchange actual dependency files; they must not independently invent competing materials or rule IDs.

## What not to commission yet

Do not ask a content author to write an entirely new magic engine, combat engine, economy, co-op protocol or autonomous gamemaster as if it were content data. Those need implementation and testing. Do not multiply each shared content count by 21 ancestries. Do not generate another 2,100 names or another base personality collection until actual play reveals a shortage. Do not create final castle canon that overwrites an active campaign.
