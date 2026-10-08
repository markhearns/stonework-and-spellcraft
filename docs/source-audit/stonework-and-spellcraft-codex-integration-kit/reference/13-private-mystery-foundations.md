# Alternative private castle foundations and evidence

Pack ID: `ss-private-mystery-foundations` · Initial target: **42 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Six mutually exclusive foundation options, six evidence fragments each. All records use visibility private-template, even when a field contains a possible player-facing observation. These are alternatives for future campaign generation, not six simultaneous truths. Do not inspect or expose a current campaign’s private lore.

The castle has a coherent unexplained affinity for consensual eroticism/intimacy but is not a speaking NPC and never controls desire. Evidence elaborates a fixed chosen foundation. No lost-heir retcon to player ownership, required trauma, ancient-age recruit or claims that an existing resident is secretly someone else. Do not reveal answers in filenames, public summaries, item names or ordinary prompt context.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `foundation-option.json` — recordType `foundation-option` — 6 entries

- `premise:string`
- `originalPurpose:string`
- `abandonmentExplanation:string`
- `sensualAffinityExplanation:string`
- `invariantFacts:string[]`
- `forbiddenRetcons:string[]`
- `compatibilityNotes:string[]`

### `evidence-fragment.json` — recordType `evidence-fragment` — 36 entries

- `foundationId:string`
- `playerFacingObservation:string`
- `privateMeaning:string`
- `interpretationAlternatives:string[]`
- `discoveryConditions:string[]`
- `disclosureScope:string`
- `contradictionChecks:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
