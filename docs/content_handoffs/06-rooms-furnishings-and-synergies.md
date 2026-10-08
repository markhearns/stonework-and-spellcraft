# Room purposes, furnishings and understandable synergies

Pack ID: `ss-rooms-furnishings-and-synergies` · Initial target: **120 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Use existing bounded rooms, not a wall-building simulator. Provide 24 purely decorative and 48 functional furnishing concepts. Explain bonuses through a text list; do not require crude furniture overlays. Visual rooms should feel inhabited and handmade, with natural eye-level composition.

Synergy is a modest understandable option, never a hidden placement trap or penalty for a small household. Bedrooms respect privacy and real capacity; twenty chairs do not create twenty resident places. Do not equate dungeon location with confinement. Keep restoration costs and new bonuses in proposed mechanics.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `room-purpose.json` — recordType `room-purpose` — 24 entries

- `dailyUse:string`
- `architecturalNeeds:string[]`
- `serviceDependencies:string[]`
- `suitableAdjacencies:string[]`
- `privateOrShared:private|shared|either`
- `illustrationBrief:string`

### `furnishing-concept.json` — recordType `furnishing-concept` — 72 entries

- `roomPurposeIds:string[]`
- `materialDescription:string`
- `decorativeChoice:string`
- `functionalProposal:string|null`
- `footprintNotes:string`
- `privacyConsiderations:string[]`

### `adjacency-synergy.json` — recordType `adjacency-synergy` — 24 entries

- `firstRoomPurposeId:string`
- `secondRoomPurposeId:string`
- `explanation:string`
- `absenceBehaviour:string`
- `maximumScope:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
