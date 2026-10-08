# Magic principles and bounded spell constructions

Pack ID: `ss-magic-principles-and-spells` · Initial target: **126 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Do not replace the magic system. Expand its reusable-principle grammar. Separate understanding, archive availability, personal mastery, preparation, testing and casting. New spell effects remain proposed rules. Ordinary practical magic should be useful without a tedious mana tax; exceptional feats justify clear bounds and investment.

Provide 24 spells using only existing principles, 36 exploring new principles and 12 exceptional concepts. These counts describe conceptual foundations, not existing effect support. Current executable forms are only warm-twist, root-song, luminous-copy and clarify-glass. Explanations must admit when a requested effect has no supported form. No arbitrary reality editing, mind control, resurrection-as-routine or free universal mastery.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `principle-concept.json` — recordType `principle-concept` — 24 entries

- `underlyingIdea:string`
- `teachesWhat:string`
- `doesNotPermit:string[]`
- `observationQuestions:string[]`
- `experimentIdeas:string[]`
- `neighbouringPrincipleIds:string[]`

### `spell-construction.json` — recordType `spell-construction` — 72 entries

- `desiredEffect:string`
- `principleIds:string[]`
- `componentPropertyIds:string[]`
- `method:string`
- `scopeLimits:string[]`
- `ordinaryOrExceptional:ordinary|exceptional`
- `partialMatchExplanation:string`
- `prerequisitesExplanation:string`

### `spell-explanation.json` — recordType `spell-explanation` — 30 entries

- `requestExample:string`
- `assessment:supported-baseline|partial-fit|requires-new-rule|not-permitted`
- `baselineFormId:string|null`
- `helpfulExplanation:string`
- `honestAlternative:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
