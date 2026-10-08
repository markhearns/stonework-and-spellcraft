# Household artifacts and crafting recipes

Pack ID: `ss-artifacts-and-recipes` · Initial target: **80 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Pair each new artifact with one recipe, without remaking the existing eleven artifacts. Cover reading, bathing, cooking, textiles, correspondence, storage, practical laboratory work, gardens and comfortable shared spaces. Furnishings that simply look attractive are not artifacts.

Crafting, ownership and installation are separate. Give human-readable benefits and explicit non-stacking limits. Automation must respect Advance and avoid secretly adding a second worker. Novel outputs/costs require separate mechanics proposals; already supported effects may be referenced accurately.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `artifact-concept.json` — recordType `artifact-concept` — 40 entries

- `appearance:string`
- `householdProblem:string`
- `proposedFunction:string`
- `installationContext:string`
- `materialPropertyNeeds:string[]`
- `principleIds:string[]`
- `operatingLimits:string[]`

### `recipe-concept.json` — recordType `recipe-concept` — 40 entries

- `artifactId:string`
- `stages:string[]`
- `requiredKnowledge:string[]`
- `propertyRequirements:string[]`
- `substitutionExamples:string[]`
- `installationStep:string`
- `cancellationNotes:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
