# Neighbouring communities, services and recurring contacts

Pack ID: `ss-communities-services-and-visitors` · Initial target: **64 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Four recurring contact roles and three services per community. Use role IDs rather than fixed new resident names. If a role later becomes a recruit, a separate character-generation review establishes her adult identity; no common ancestry is silently summoned.

Communities have their own ordinary lives. Avoid absolute canon about rulers, wars, geography or castle ownership. Services and markets suggest options but do not alter prices/inventory without mapped mechanics. Trade should complement exploration, not bypass all research.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `community-template.json` — recordType `community-template` — 8 entries

- `character:string`
- `crafts:string[]`
- `everydayConcerns:string[]`
- `visitingEtiquette:string[]`
- `independentInterests:string[]`
- `relationshipToCastle:string`

### `contact-role.json` — recordType `contact-role` — 32 entries

- `communityId:string`
- `occupation:string`
- `ownAgenda:string`
- `conversationalStyle:string`
- `helpfulKnowledge:string[]`
- `limits:string[]`
- `recruitmentStatus:not-a-recruit|possible-future-candidate`

### `service-concept.json` — recordType `service-concept` — 24 entries

- `communityId:string`
- `serviceDescription:string`
- `whatItDoesNotSupply:string[]`
- `accessRequirements:string[]`
- `transactionNotes:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
