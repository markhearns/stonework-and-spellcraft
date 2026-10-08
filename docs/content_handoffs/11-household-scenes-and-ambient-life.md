# Household scenes, fanservice and ambient life

Pack ID: `ss-household-scenes-and-ambient-life` · Initial target: **160 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Extend the existing 50 interaction seeds with actual branching scenes. Each choices array contains 2–4 objects with exactly id, label, residentResponse, establishesFacts (string array) and doesNotEstablish (string array). Player labels express selectable intent; never prescript a kiss or other action not chosen. Every scene needs a comfortable decline/defer path stated in followupPossibilities.

Target 20 ordinary, 20 playful, 25 flirtatious and 15 romantic scenes. Romantic contexts require an actually welcomed relationship, not merely attractive participants. Include scholarly teasing, alluring evening styling, shared craft, confidences, hobbies and gentle disagreements. Sensual, non-explicit, diverse voices; no wardrobe change inferred from narrative. Ambient lines are brief and cannot secretly resolve a scene, demand attention or imply a missed obligation.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `scene-template.json` — recordType `scene-template` — 80 entries

- `participants:npc-player|two-npcs|small-group`
- `context:string`
- `invitation:string`
- `opening:string`
- `choices:object[]`
- `followupPossibilities:string[]`
- `intimacyLevel:ordinary|playful|flirtatious|romantic`

### `ambient-line.json` — recordType `ambient-line` — 80 entries

- `speakerRole:string`
- `suitableContext:string`
- `line:string`
- `avoidWhen:string[]`
- `repeatAvoidance:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.
