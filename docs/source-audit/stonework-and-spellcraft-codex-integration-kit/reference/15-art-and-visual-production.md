# Art briefs and visual continuity

Pack ID: `ss-art-and-visual-production` · Initial target: **93 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Write briefs, not claims that images were generated. Follow tactile ink/pencil/gouache on dark paper, restrained violet and worn gold. No glossy CGI, excessive filigree or bright palace ornament. Use consistent eye-level room perspectives and readable object silhouettes.

Wardrobe briefs are templates for one adult per ancestry; reference actual supplied garment IDs only. Identity-preserving edits require accepted portrait references at execution time: do not invent faces or claim you saw missing images. No image itself equips an item or changes a scene. Keep overlays optional; furnishing effects remain text.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `room-art-brief.json` — recordType `room-art-brief` — 24 entries

- `subjectReference:reference|null`
- `composition:string`
- `eyeLevelAndFraming:string`
- `palette:string[]`
- `materialsAndWear:string[]`
- `lightingVariants:string[]`
- `exclusions:string[]`

### `object-art-brief.json` — recordType `object-art-brief` — 48 entries

- `subjectReference:reference|null`
- `silhouette:string`
- `constructionDetails:string[]`
- `wearPattern:string`
- `backgroundTreatment:string`
- `scaleCue:string`
- `exclusions:string[]`

### `wardrobe-art-brief.json` — recordType `wardrobe-art-brief` — 21 entries

- `ancestryId:string`
- `identityPreservation:string`
- `garmentReferenceIds:string[]`
- `anatomyChecks:string[]`
- `poseAndExpression:string`
- `coverageRequirements:string`
- `exclusions:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
