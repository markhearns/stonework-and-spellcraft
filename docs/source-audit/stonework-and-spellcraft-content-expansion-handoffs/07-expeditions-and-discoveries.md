# Expedition sites, leads and reusable discoveries

Pack ID: `ss-expeditions-and-discoveries` · Initial target: **126 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Three leads and three discoveries per site. Cover ruins, workshops, groves, waterworks, observatories, archives, unusual markets and quiet settlements. Trips bring knowledge, materials, wealth and relationships home. No random devastation of the home while exploring.

Distinguish observing, understanding, returning, depositing knowledge and personal mastery. Unknown loot is not auto-owned. Requirements and rewards await rule mapping. Retreat, alternate approaches and revisiting should preserve completed discoveries without duplicate awards. Lead discovery does not automatically reveal all destinations.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `site-template.json` — recordType `site-template` — 18 entries

- `environment:string`
- `reasonToVisit:string`
- `approachOptions:string[]`
- `voluntaryHazards:string[]`
- `retreatOptions:string[]`
- `illustrationBrief:string`

### `lead-template.json` — recordType `lead-template` — 54 entries

- `siteId:string`
- `openingLead:string`
- `investigationQuestion:string`
- `routeChoices:string[]`
- `requirements:string[]`
- `nonExpiryExplanation:string`

### `discovery-template.json` — recordType `discovery-template` — 54 entries

- `leadId:string`
- `observation:string`
- `possibleInterpretations:string[]`
- `principleOrMaterialReferences:reference[]`
- `returnAndShareConditions:string[]`
- `repeatabilityLimit:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
