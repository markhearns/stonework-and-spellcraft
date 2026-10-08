# v0.88 — Personal paths

Open a resident’s **Development** section to develop a personal field build. This foundation gives Rhess, Kaede, and Sabine three authored paths each, with six techniques and three passives per resident: **27 talents** altogether.

| Resident | Paths |
| --- | --- |
| Rhess | Watchkeeper, Ember, Pathfinder |
| Kaede | Breaker, Stillness, Instructor |
| Sabine | Shadow, Restraint, Dungeon keeper |

## Learning and preparation

Restore the training yard, return home together, and choose a talent. Learning takes two of the learner’s assigned training phases. Pausing or changing assignments retains progress; the existing resume and cancel controls apply. No crowns or advancement points are spent. Household skills therefore retain their advancement budget.

Each branch has a starting technique, an advanced technique, and a passive. Advanced techniques require the branch’s starting technique and the resident’s completed signature-equipment request. The signature piece must also be owned and equipped in the expedition loadout to use the advanced technique in the field. Passives require the starting technique and two lifetime advancement points earned through accomplishments; these are an eligibility requirement, not a purchase. Spending existing advancement never removes eligibility.

Prepare up to three techniques and two passives. Mix branches freely. Changing or clearing this preparation at home is free and advances no time. Training never equips a talent automatically. Ordinary attribute/skill retraining keeps personal talent knowledge and preparation.

## Field use and equipment

Techniques are offered alongside existing methods when applicable at the Cinder aqueduct, Hollow Road, Watchtower Trail, and Broken Wardstones. Their rules are deterministic and shown before selection. The aqueduct supports damage, guard, counterattacks, controlled flame, and a technique that restores an injured companion. The chapter routes use safe work phases rather than simulated combat damage.

Matching **active expedition inscriptions** improve techniques. Each matching effect counts once, including equipment occupying both hands. Matching enchantments add one attack damage where the technique deals damage, and reduce applicable obstacle work from two phases to one. Branch passives add the effects listed on their cards. Guard reduces retaliation; an enemy defeated by the action does not retaliate. Flame cannot damage ember creatures. Some advanced attacks cost one vitality when resolved and cannot be chosen without enough vitality.

Every prepared technique can resolve once per obstacle. Retreat, returning, or reloading does not reset completed uses. Repeating different techniques at the same site does not repeat the advancement award: the first successfully resolved personal technique awards its performer two advancement once per site. Interrupted aqueduct work produces neither effects nor awards. Chapter route work retains its committed progress and result snapshot on retreat.

These paths do not shorten travel, skip encounters, or remove the sleep/homecoming requirements of Chapter 7. Ordinary methods remain available.

## Repeatable training-yard exercises

Five one-phase exercises let a build be explored even after its expeditions have been completed: guarded sparring, an armoured training dummy, a rope crossing, a practice ward lock, and braced lifting.

The exercise takes a snapshot of prepared talents and saved expedition equipment when agreed, then records deterministic results when its assigned phase resolves. It causes no injury, spends no supplies, and awards no advancement. A changed build can be tried again; this is a comparison tool, not a source of repeatable rewards. The latest result is saved under Personal paths.

## Interface and compatibility

Development contains the talent choices and yard exercises. Overview and Preparations show a compact prepared-build summary. Disabled choices explain their requirements. Existing optimized watchtower, training-yard, and dungeon illustrations are reused; no existing portrait or artwork file was changed. The layout stacks the branches on smaller screens.

Other residents keep their existing development systems. Secondary disciplines, expanded companion techniques, and personal-quest evolution choices are future extensions, not new features claimed by this release.

Schema **63** protects new training-project kinds from older executables. Opening a v0.87 campaign creates `campaign-before-schema-62-to-63.sqlite3`. New talent records are created only as needed; old state is preserved apart from the schema and revision upgrade. Keep your existing `data/` directory when installing. Do not reopen an upgraded campaign with an older executable.

Validation details are in `VERIFICATION_V088.json` and `REGRESSIONS_V088.json`. UI checks exercise templates, controllers, the saved-game API, and reload; they are not a rendered-browser layout review.
