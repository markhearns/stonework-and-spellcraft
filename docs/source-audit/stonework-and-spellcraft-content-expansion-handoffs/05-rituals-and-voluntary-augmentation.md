# Rituals, voluntary augmentation and reversal

Pack ID: `ss-rituals-and-voluntary-augmentation` · Initial target: **42 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Include six cooperative research rituals, six practical service rituals, six contact/construction refinements and six reversal/reconfiguration rituals. Augmentations must reference a real delivered reversal ritual; one reversal ritual may support several related augments. Consent is a prerequisite, never a reward or something magic manufactures.

Keep independent personal work budgets, supplied participants and supported costs. Contact is not arrival; arrival is not membership. Golem construction is not enslavement. Reversible form changes preserve identity, knowledge, histories and owned things. Do not implicitly alter accepted portraits or a founder’s chosen identity.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `ritual-concept.json` — recordType `ritual-concept` — 24 entries

- `purpose:string`
- `roles:string[]`
- `personalKnowledgeRequirements:string[]`
- `stages:string[]`
- `invitationAndAgreement:string`
- `interruptionRecovery:string`
- `visibleSigns:string[]`
- `boundedOutcome:string`

### `augmentation-concept.json` — recordType `augmentation-concept` — 18 entries

- `proposedChange:string`
- `willingParticipantRequirements:string[]`
- `appearanceEffect:string`
- `personalAgencyLimits:string[]`
- `reversalRitualId:string`
- `equipmentConsequences:string[]`
- `identityContinuity:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
