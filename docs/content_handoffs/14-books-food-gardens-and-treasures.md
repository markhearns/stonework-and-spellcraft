# Books, food, gardens and unusual treasures

Pack ID: `ss-books-food-gardens-and-treasures` · Initial target: **124 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Give the household useful things to discuss, collect and live with. These are descriptive candidates, not inventory grants or mandatory hunger/maintenance systems. An interesting book is not automatic principle mastery. Food is not an aphrodisiac or consent tool.

Keep botanical flavour distinct from material-property records and reference those only when delivered. Strange treasures need not be powerful. No copied long quotations, real book excerpts or lyrics; create original short passages. Avoid default gold-plated relics and excessive clutter.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `book-or-document.json` — recordType `book-or-document` — 40 entries

- `documentKind:string`
- `physicalDescription:string`
- `topic:string`
- `excerpt:string`
- `discussionQuestion:string`
- `knowledgeLimits:string[]`

### `food-or-drink.json` — recordType `food-or-drink` — 30 entries

- `sensoryDescription:string`
- `ingredientsDescription:string`
- `servingContext:string`
- `preferenceNotes:string[]`
- `preparationIdea:string`

### `garden-specimen.json` — recordType `garden-specimen` — 24 entries

- `appearance:string`
- `growingContext:string`
- `observationHook:string`
- `mundaneUse:string`
- `magicalClaimsToAvoid:string[]`

### `curiosity.json` — recordType `curiosity` — 30 entries

- `appearance:string`
- `possibleProvenance:string`
- `practicalOrPersonalInterest:string`
- `unresolvedQuestion:string`
- `displayNotes:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
