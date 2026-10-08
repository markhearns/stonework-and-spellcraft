# Correspondence, commissions, gifts and keepsakes

Pack ID: `ss-letters-commissions-and-gifts` · Initial target: **100 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Letters invite, report already established results, compare ideas or offer optional work. No fake deadlines, attention decay or unseen mandatory promises. Commissions need actual accepted work and bounded rewards; a flattering letter cannot deliver goods.

Gifts express attention without purchasing affection. Keep personal/shared wallets distinct and require actual acquisitions. A keepsake belongs to its owner through travel and departure; display needs permission. Avoid 36 flowers/jewels differing only by colour.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `letter-template.json` — recordType `letter-template` — 40 entries

- `senderRole:string`
- `reasonForWriting:string`
- `subject:string`
- `body:string`
- `replyDirections:string[]`
- `disclosureLimits:string[]`

### `commission-concept.json` — recordType `commission-concept` — 24 entries

- `clientRole:string`
- `requestedOutcome:string`
- `supportedWorkReferences:reference[]`
- `acceptanceCriteria:string[]`
- `optionalAlternatives:string[]`
- `returnPolicy:string`

### `gift-or-keepsake.json` — recordType `gift-or-keepsake` — 36 entries

- `kind:gift|personal-keepsake`
- `appearance:string`
- `whySomeoneMightValueIt:string`
- `preferencesToCheck:string[]`
- `ownershipAndDisplay:string`
- `noObligationText:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
