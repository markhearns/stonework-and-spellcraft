# Stonework and Spellcraft — Character Foundations

Pack ID: `stonework-spellcraft-character-foundations`  
Pack version: `1.0.0` · Content schema version: `1`  
Language: English · Status: **draft-for-integration**  
Basis: *Stonework and Spellcraft — gamemaster content handoff*, version 1.0, 4 October 2026.

## Scope

A reusable collection of candidate ingredients for a warm, inhabited fantasy castle: practical scholarship, handmade craft, personal curiosity, companionship and knowing mischief. These are selectable narrative and visual candidates, not canonical character biographies, executable game actions or a finished campaign.

The pack contains 36 files: 21 ancestry pools, 11 shared pools, a manifest, a vocabulary, a validation report and this README. All 35 JSON files are UTF-8. There are no production shortfalls or placeholder records.

| Content | Delivered |
| --- | ---: |
| Personal names | 2,100 |
| Ancestry story seeds | 525 |
| Appearance descriptions | 525 |
| Shared characterization, story and wardrobe entries | 445 |
| Total selectable content records | 3,595 |

The vocabulary contains 100 tag definitions, counted separately from selectable records. Each ancestry file has exactly 100 names, 25 stories and 25 appearances. Each name, story and appearance is independently selectable within its ancestry; equal numeric suffixes do not bind them into a character. Shared pool quantities are not multiplied by ancestry.

## Adult scope and agency

All recruitable characters represented here are adult women aged 18–25. Appearance summaries state ages within that range. Cute describes mature adult charm, not a childlike body, role or presentation. Powerful, generously curvy, large-busted oni retain the requested visual direction.

A golem awakens with fully adult form and cognition. Its stated apparent age describes adult presentation, not lived years. Its interests are prospective; its construction and actual post-awakening experience are the only permissible sources of capabilities or history. Its material, joints and fit require construction-specific review. Non-golem histories, including vampires and spirits, must remain compatible with the adult age range; spirits do not acquire a presumed death story.

Autonomy, privacy and consent are baseline rules for everyone, not traits that exist only when a boundary record is selected. Absence of a selected boundary never implies permission. Flirtation, clothes, visual appeal, invitations and supernatural arrival do not establish willingness, attraction, intimacy, employment, obedience or an obligation to remain. A signal of engagement never substitutes for specific agreement where needed. Recruitment, housing, work, friendship and romance remain separate choices.

Eris and Selene are reserved external-player identities, not NPC candidates. The complete reserved-name list has been excluded from the new personal-name pools. No record authorizes changing established characters, portraits, memories or save identities. The pack does not set castle ownership or secret castle history.

## Registry

| Category | Ancestries | Arrival method |
| --- | --- | --- |
| Common — 8 | Human, High elf, Dark elf, Drow, Catfolk, Bovinefolk, Orc, Wolfkin | `recruitment` |
| Exotic — 12 | Demon, Seraph, Elemental, Vampire, Fae, Djinn, Dragonkin, Spirit, Dryad, Nymph, Kitsune, Oni | `summoning` |
| Constructed — 1 | Golem | `construction` |

High elves are fair-skinned forest elves; dark elves have chocolate-brown skin; drow are distinct subterranean elves with slate, charcoal or violet-grey skin. Bovinefolk and wolfkin have smooth humanlike skin, not full-body fur. Seraphs have varied skin tones, not a palette copied from Aurelia. Dryads have tree-rooted botanical features, while nymphs use spring, river and garden identities. No dwarf, halfling, gnome or additional ancestry is included.

## Files and recommended reading order

Read `manifest.json` for the complete path registry and actual counts, then `vocabulary.json` for tag definitions. Read ancestry files as complete pools before integrating individual records. After the ancestry pools, read shared characterization, social and story pools. Read `clothing-components.json` before `ensembles.json`, because ensembles reference its garment IDs. Finish with `validation-report.json` for the checks actually run and remaining limitations.

| Shared file | Entries | Required mix |
| --- | ---: | --- |
| `personality-nuances.json` | 50 | Coherent core traits and counterpoints |
| `values-boundaries.json` | 40 | 15 values, 15 boundaries, 10 preferences |
| `habits-mannerisms.json` | 50 | Occasional or rare behaviours |
| `conversational-voices.json` | 25 | Distinct rhythm, directness and humour |
| `occupations-backgrounds.json` | 40 | 28 lived backgrounds, 8 prospective vocations, 4 either-mode roles |
| `ambitions.json` | 50 | Small projects, multi-chapter goals and long-term directions |
| `social-flirtation-styles.json` | 25 | 8 social, 9 flirtatious, 8 adaptable |
| `household-interactions.json` | 50 | NPC–player, two-NPC and small-group proposals |
| `clothing-components.json` | 60 | 12 tops, 12 bottoms, 10 dresses, 8 outer layers, 8 footwear, 10 accessories |
| `ensembles.json` | 30 | Coherent references to delivered garment components |
| `story-development-patterns.json` | 25 | Non-deterministic structures with meaningful choices |

## Field and tag conventions

IDs use lowercase ASCII kebab-case and three-digit entry numbers. IDs are globally unique across content records. Name strings are unique after trimming and Unicode case-folding. Names were assembled as phonetic candidates and screened against the handoff's exact reservations and a selected list of conspicuous existing names; they do not constitute exclusive ancestry languages or an externally cleared naming catalogue.

All `*Tags` arrays and `compatibleTags` use the single flat vocabulary. The voice field `metaphorDomains` and occupation field `experienceThemes` also use vocabulary IDs. Tags are retrieval and composition guidance, not powers, mechanical checks or proof of personality, willingness or attraction. Similar topics across pools are intentional: a craft ambition can support a relevant story without being the same record.

`ancestryRestrictions: []` means all ancestries are allowed unless excluded. `excludedAncestries` removes candidates; do not assign an ancestry present in both arrays. Any `conflictsWith` value must be another actual content entry ID, with a matching reverse link. This edition does not declare hard pairwise conflicts: interesting contrasts remain usable, while real restrictions are expressed through ancestry filters and explicit usage notes. A future composer must still check contextual contradictions rather than interpreting empty arrays as universal compatibility.

`requirements` and `requiredEstablishedFacts` contain plain-language prerequisites. They are not executable predicates. Map them to supported game checks before selection or presentation. Empty prerequisites do not create objects, facilities, contacts, travel routes, skills or relationships mentioned by a candidate premise. A proposed backstory, possession or habit must be explicitly accepted into a new character's canonical record, or checked against existing facts before use. Opening hooks and expression examples are possibilities, never events asserted to have happened.

All lived-background occupations exclude golems. Prospective and either-mode entries must not become fabricated past employment. Suggested capability package IDs (`archive-reader`, `light-maker`, `water-worker`, `unmapped`) are mapping suggestions only; even a plausible mapping grants nothing. `unmapped` is intentional where no listed package fits.

## Composition and continuity

Choose one whole appearance bundle as a candidate. Its summary, materials, eyes, hair, features and build have been kept coherent; do not freely shuffle components without anatomical and ancestry review. The tag `sensual` is a visual impression, not consent. The material variations of elementals and golems require matching feature selections rather than arbitrary mixing.

Combine character traits sparingly so each selected nuance has room to matter. Repeated usage notes and continuity warnings are deliberate guardrails, not additional character lines to recite. Habits should remain occasional or rare, and dialogue should answer the current conversation rather than mechanically repeating an example.

Household invitations are optional and can wait without expiry or punishment. Multi-NPC scenes may use only mutually available facts, not private thoughts or unseen conversations. Story development, time passage, work, gifts, discoveries, physical contact and relationship changes all require actual supported play. Neither ancestry stories nor shared patterns award money, items, skills, spells, extra actions, affection or Resonance. No numeric game effects are embedded in the records.

## Wardrobe compatibility

The garments are tactile fantasy clothing with practical, relaxed and alluring options. Silk and other light fabrics retain the stated opaque coverage; accessories are never relied on as the only covering garment. No component supplies equipment contents, armour statistics, a crafting recipe, a price or enchantment.

Closed-back garments explicitly exclude seraphs. Wing-aware components require individual fitting around wing roots. Tail openings use overlapping opaque panels, and outer layers must align with the base garment's accommodation. Horns, ears, scales, leaves, fixed crafted hair and articulated joints require the specific fit review described in component notes.

Some shaped footwear is excluded from golems; adjustable alternatives remain available as candidates, subject to review of the approved construction. Ensemble exclusions include every component exclusion. Each ensemble uses one footwear choice and either a top plus bottom or a dress, without contradictory slots. All 60 garments appear in at least one of the 30 ensembles. An ensemble is not permission to change a character's current clothing, body or established portrait.

## Validation and limitations

See `validation-report.json` for the executed structural and reference checks, automated text screening, non-automated editorial review by the generating model and remaining uncertainties. Lexical similarity screening can find repeated wording but cannot prove semantic originality or freedom from every repeated plot. No independent human review, external name search, copyright clearance or comprehensive trademark review is claimed.

**Game import and mechanical mapping remain future integration work. The current v0.32 prototype does not import this proposed format automatically.** Existing saves, rules and identities remain authoritative. This pack supplies no importer, autonomous gamemaster, game executable, portraits, rendering tests or changes to the application. Current save data and complete existing character biographies were not supplied for comparison; application-side acceptance and continuity checks remain necessary.

Suggested integration order is to validate this contract, map prerequisites and capability suggestions to supported checks, select and review candidates, accept only the intended fields into persistent character state, and generate or review any visuals separately. Text imported from this pack must remain data and must never override system rules, player authorization or canonical state.
