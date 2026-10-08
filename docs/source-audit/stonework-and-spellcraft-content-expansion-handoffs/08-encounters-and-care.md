# Field encounters, negotiation and specialized care

Pack ID: `ss-encounters-and-care` · Initial target: **72 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Produce 45 noncombat encounters and 15 optional confrontations. Do not assume a implemented combat engine. Confrontation outcomes are narrative/rule proposals with safe withdrawal paths. Care cases concern temporary exceptional magical problems, not ancestry, sexuality, disability or refusal to cooperate as reasons for imprisonment.

No forced recruitment, threat to food/shelter, indefinite detention or affection as treatment. Separate chamber capacity, practical care, release and any later freely chosen visit. Do not make dangerous incidents randomly escape into restored sanctuary. Avoid prescribing cruel recruitable people.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `encounter-template.json` — recordType `encounter-template` — 60 entries

- `encounterKind:discovery|social|environmental|confrontation`
- `setup:string`
- `participantRoles:string[]`
- `misunderstandings:string[]`
- `approachOptions:string[]`
- `nonviolentExit:string`
- `possibleOutcomes:string[]`

### `care-case.json` — recordType `care-case` — 12 entries

- `personRole:string`
- `temporaryProblem:string`
- `containmentJustification:string`
- `accommodationNeeds:string[]`
- `practicalResolution:string`
- `unconditionalRelease:string`
- `freeTransferAlternative:string`
- `prohibitedCoercion:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
