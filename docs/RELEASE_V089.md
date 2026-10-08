# v0.89 — A build of their own

Character building now uses one **Build** workspace for your scholar and every resident. Rhess, Kaede and Sabine keep their original talents, while the rest of the established cast gains personal paths. There are **17 authored builds, 51 paths and 153 talents**: six techniques and three passives per person.

## A quieter character page

- **Loadout** shows three technique slots, two passive slots, signature equipment and prepared magic. Practices, saved builds and household contributions expand when needed.
- **Personal paths** shows three branch selectors, three talents in the selected branch, and one detailed talent. Requirements start with the next blocker; full requirements and calculations are expandable.
- **Training** contains the yard exercises, skills, attributes, lessons and specialization options. Only the selected yard exercise has a preview.
- The current learning project stays above these sections, with progress and resume/cancel controls. Each character's section and branch selection are remembered during the current session.

The former separate Preparation tab redirects to Loadout. Relationships, personal quests and companion conversations use their existing dedicated tabs. Professional projects, including Mira's archive, are available under **Quests & stories**. Equipment still has one central editor, reached from Loadout.

Prepared techniques show effective values using their prepared branch passives and saved expedition equipment. Target-specific bonuses remain explicit in the talent description and live encounter preview. When slots are full, choose the prepared talent to replace directly; learned talents are never forgotten by this operation.

## Personal identities

The paths use existing room associations and signature equipment. Their field roles include guarding, counters, elemental matchups, healing another traveller, recovering personal vitality, and resolving suitable obstacles. For example, Neris can direct water against ember creatures, Elowen emphasizes companion recovery, Brakka exploits construct joints, and Velis supports routes and field supplies. Generated residents retain their shared skills, practices, magic and specialization systems.

## Build rules and pacing

Restore the training yard to learn a talent. Each talent takes **two assigned training phases** and spends no crowns or advancement. Each branch has a starting technique, an advanced technique and a passive. Advanced learning requires the starting technique and a completed signature-equipment request; advanced field use also requires the owned signature piece in the expedition loadout. Passives require the starting technique and two lifetime advancement points, which remain available to spend elsewhere.

Prepare three techniques and two passives, mixing branches freely. Each technique resolves once per obstacle. A character's first successful personal technique at a supported site earns two advancement once at that site. Retreating, reloading and changing preparation do not reset those limits. Matching active enchantments and matching branch passives use the same calculation for previews and field resolution.

Field techniques currently work at the Cinder aqueduct, Hollow Road, Watchtower Trail and Broken Wardstones. Five repeatable yard exercises let completed campaigns try builds in one assigned phase without injury, supply costs or advancement rewards. This release preserves travel, chapter progress, food, homecoming and sleep requirements. Optional training adds choices without adding mandatory chapter gates.

## Saved builds

Saved builds now include personal talents and all physical equipment arrangements, together with the existing spells, practices, working tool and focus configuration. Loading revalidates the whole set before changing anything. If equipment was transferred or another requirement is no longer met, the current build stays intact and the reason is shown. Older preparation sets continue to load their original contents and leave newer talent/equipment choices unchanged.

## Artwork and installation

The workspace reuses optimized associated-room thumbnails and equipment icons. All **268 runtime artwork files** remain byte-for-byte identical to v0.88, including accepted character designs.

1. Stop the old server and preserve the **complete `data/` directory**, including campaign subfolders and `data/assets`.
2. Extract v0.89 and copy that complete directory into the game folder.
3. Run `python server.py` and open the printed local address.
4. Open **Companions → a character → Build**.

Schema **64** creates `campaign-before-schema-63-to-64.sqlite3` when upgrading a v0.88 campaign. An actual v0.88 save was upgraded with exact state preservation apart from schema/revision; pending original techniques, training, old preparation sets, accepted artwork and database history were retained. Keep the automatic backup if you need to return to an older executable.

Validation results are in `VERIFICATION_V089.json` and `REGRESSIONS_V089.json`. UI validation covers templates, parsed structure, controllers, API actions and SQLite reload. Browser-rendered layout review remains outstanding because a browser executable is unavailable in this environment.

