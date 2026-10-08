# Background capability mappings, training and earned perks

Pack ID: `ss-backgrounds-training-and-perks` · Initial target: **102 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

The supplied foundations pack has thirty occupations labelled unmapped. Propose a mapping for each of those exact occupation IDs, referencing the supplied dependency; do not regenerate the occupations. A mapping may stay null when none of the current or proposed packages fits. New starting packages are design proposals, not instant grants.

Existing starting packages are archive-reader, light-maker and water-worker. Keep them as the balance baseline: limited initial knowledge/practice, skill ranks zero, no earned advancement and one focus slot. Perks are earned investments, not free ancestry bonuses. Do not create automatic sex-based talents, forced personality changes, knowledge transfers through romance or compulsory training. Golem vocations remain prospective. Each new mechanical benefit must reference a separate mechanics proposal.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `background-mapping.json` — recordType `background-mapping` — 30 entries

- `sourceOccupationId:string`
- `suggestedStartingPackageId:string|null`
- `rationale:string`
- `knowledgeThatMustStillBeLearned:string[]`
- `historyCompatibility:string`
- `unresolvedNeeds:string[]`

### `starting-package-concept.json` — recordType `starting-package-concept` — 12 entries

- `vocationTheme:string`
- `startingKnowledgeCandidates:string[]`
- `startingPracticeCandidates:string[]`
- `signatureToolIdea:string`
- `doesNotGrant:string[]`
- `comparableBaselinePackage:string`

### `perk-concept.json` — recordType `perk-concept` — 36 entries

- `disciplineTheme:string`
- `investmentPrerequisites:string[]`
- `proposedBenefit:string`
- `exclusions:string[]`
- `ancestryBasis:string|null`
- `retrainingBehaviour:string`

### `training-opportunity.json` — recordType `training-opportunity` — 24 entries

- `teacherRole:string`
- `learnerChoice:string`
- `personalKnowledgeRequirements:string[]`
- `proposedExercises:string[]`
- `evidenceOfUnderstanding:string`
- `consentAndAvailability:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
