# Equipment and evolving signature items

Pack ID: `ss-equipment-and-signature-items` · Initial target: **96 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Prefer 16 signature foci, 16 useful tools, 8 field kits and 8 accessories. A cherished staff, lamp, notebook case or measuring instrument should gain functions over time. Avoid disposable loot tiers and +1/+2 ladders. Some equipment may be elegant, alluring or personally expressive, without forced body changes or consent effects.

An inscription is not automatically prepared, known, installed or granted. Describe ownership, preparation, castle-only changes, capacity and stacking through mechanics proposals. Include broad anatomy accommodations and component alternatives. Exclude wardrobe-only garments already covered by the foundations pack.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `equipment-concept.json` — recordType `equipment-concept` — 48 entries

- `equipmentKind:focus|tool|field-gear|accessory`
- `appearance:string`
- `intendedUse:string`
- `wearerRequirements:string[]`
- `componentIdeas:string[]`
- `upgradeThemes:string[]`
- `ownershipNotes:string`
- `anatomyAccommodations:string[]`

### `inscription-concept.json` — recordType `inscription-concept` — 48 entries

- `visualMotif:string`
- `principleIds:string[]`
- `intendedFunction:string`
- `validHosts:string[]`
- `incompatibilities:string[]`
- `upgradePath:string[]`
- `limits:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
