# Tutorial copy, explanations and integration scenarios

Pack ID: `ss-tutorials-explanations-and-qa` · Initial target: **144 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Plain language and human-readable variables. Cover craft/install distinctions, missing personal knowledge, incompatible garments, full rooms, deferred invitations, duplicate clicks, stale drafts, departures, separate wallets and explicit Advance.

Current answers must match the reference; uncertain rules are future proposals, not invented help. QA scenarios are written test designs, not claims of executed tests. Include happy paths, cancellation/refund, retries, stale tabs, save/reload, ownership, semantic contradictions and inaccessible controls. Do not write runnable scripts or fabricate pass counts.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `help-card.json` — recordType `help-card` — 32 entries

- `playerQuestion:string`
- `currentAnswer:string`
- `relatedBaselineIds:string[]`
- `implementationStatus:current-rule|future-proposal`
- `commonMistake:string`

### `feedback-copy.json` — recordType `feedback-copy` — 48 entries

- `situation:string`
- `playerMessage:string`
- `suggestedNextAction:string`
- `mustNotImply:string[]`

### `acceptance-scenario.json` — recordType `acceptance-scenario` — 64 entries

- `feature:string`
- `setupFacts:string[]`
- `attemptedAction:string`
- `expectedOutcome:string`
- `invariants:string[]`
- `requiresImplementation:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
