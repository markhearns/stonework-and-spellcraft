# Materials and component properties

Pack ID: `ss-materials-and-properties` · Initial target: **72 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Extend property-based substitution, not one-name-only shopping lists. Include mineral, botanical, textile, ceramic, glass, resin, ink and crafted substrates. Existing properties are heat-bearing, binding, botanical and vessel. New properties are proposals, never added to current rules merely by appearing here. Rare materials should open interesting options rather than make basic comfort grindy. No inherently sentient person or body part is a routine ingredient.

Give each material a distinct practical role. Separate physical material description from harvest yield, price or spell power; propose those separately only when useful. Explain at least one plausible substitution and one limit. Dependencies: none; this is a foundation pack.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `material.json` — recordType `material` — 60 entries

- `physicalDescription:string`
- `sourceContexts:string[]`
- `mundaneUses:string[]`
- `magicalAssociations:string[]`
- `propertyIds:string[]`
- `substitutionNotes:string`
- `handlingNotes:string`
- `rarityBand:ordinary|specialist|discovery`

### `property-concept.json` — recordType `property-concept` — 12 entries

- `definition:string`
- `suitableExamples:string[]`
- `unsuitableExamples:string[]`
- `acceptanceTest:string`
- `substitutionLimits:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
