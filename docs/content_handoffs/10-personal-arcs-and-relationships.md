# Personal arcs and descriptive relationships

Pack ID: `ss-personal-arcs-and-relationships` · Initial target: **78 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Two arcs per ancestry, extending rather than duplicating the existing 25 seeds each. Every chapters array has 3–4 objects with exactly title, proposedActivity, requiredEstablishedFacts (string array), optionalInvitation, possibleResolution (all other fields strings). Across relationships include 12 friendship, 10 collaboration, 8 romance and 6 friendly-disagreement entries.

Each character has an independent reason to care. Do not write the player’s actions or another resident’s private thoughts as facts. Small households remain satisfying. Resolve a practical disadvantage without erasing personality; any mechanical disadvantage change is a proposal. Romance has reciprocal choices, no obedience/reward meter or mandatory jealousy.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `personal-arc.json` — recordType `personal-arc` — 42 entries

- `ancestryId:string`
- `personalQuestion:string`
- `openingInvitation:string`
- `chapters:object[]`
- `possibleChangedGoal:string`
- `resolvedDisadvantageProposal:string|null`

### `relationship-development.json` — recordType `relationship-development` — 36 entries

- `participants:two-npcs|npc-player`
- `relationshipTheme:friendship|collaboration|romance|friendly-disagreement`
- `startingContext:string`
- `mutualChoicePoints:string[]`
- `possibleSharedMemory:string`
- `comfortableAlternative:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
