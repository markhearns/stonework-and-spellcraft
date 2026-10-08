# Shared contract for every expansion handoff

These instructions are addressed to the content-generating LLM. Read this file, `README.md`, the assigned numbered handoff, and `prototype-reference.json`. Produce complete files, not suggestions about making them. You may work on one pack independently; do not claim the other packs are finished.

## Status and authority

These are **proposed expansion contracts**. The existing character-foundations importer does not accept these new pack types. Produce reviewable data for later implementation. Do not pretend an equipment, magic, quest or economy importer already exists. The supplied character-foundations pack is a dependency/reference; do not rewrite it or regenerate its names/ancestries. Existing saves and accepted identities override templates.

The game is **Stonework and Spellcraft**, a self-hosted, adult-cast fantasy household RPG. Warm practical magic, a handmade inhabited archive-workshop, midnight paper, violet ink, worn gold, graphite, ink and gouache. No bright opulent palace, glossy CGI, modern electronics or corporate dashboard aesthetic. Clear readable names are preferable to obscure pseudo-Latin terminology.

Recruitable NPCs are independent adult women aged 18–25, diverse and beautiful/cute/sexy. Keep confident sensuality and non-explicit fanservice present where appropriate; do not make every practical task a seduction scene. No childlike presentation, coercion, automatic intimacy, cruel/sadistic/evil recruitable residents or ancestry-prescribed morality. Golems awaken fully adult; adult-form age is not years lived. Never invent their childhood or previous employment. Seraph is the celestial ancestry name. Common wolfkin, exotic kitsune/oni, and constructed golems retain their routes. The exact registry is in the reference file.

Eris and Selene are real external-player identities, never GM-controlled NPCs. Do not write their actions, emotions or agreement. Other identities should be role slots, not newly invented recruits, unless a handoff explicitly requests people. Preserve the existing 21-ancestry character pack rather than making a competing identity pool.

## World and rules boundaries

Three phases: morning, afternoon, evening. Only explicit human Advance progresses work; no offline production or real-time timers. One primary assignment per person. Conversation/decorating are free interactions; constructing functional improvements and meaningful work still need actual supported costs and phases. Knowledge in the archive is not personal mastery; mastery is not preparation. Summoned people are persistent individuals, never disposable obedient effects.

Main estate capacity is 25 NPC residents plus participating founders, optional 25-place annex, and roughly ten separate specialized care places. Restored living areas are dependable sanctuary. No random raids, mandatory jealousy, attention decay, expired invitations or punishment for declining company. Ordinary underground bedrooms are not prisons. Containment must offer unconditional safe release/transfer; nobody owes labour or intimacy for care.

Resonance concerns consensual sensual atmosphere, not generic warmth, productivity, furniture value or affection currency. Content cannot grant/spend it. Do not introduce numerical romance, consent, obedience or loyalty meters. Resident agency, finances, accommodation, work and intimacy remain separate choices.

Do not resolve the castle's secret history globally. Alternative mystery templates are private candidates; only one reviewed foundation could be chosen for a future campaign. Never retcon existing saves or turn the castle into a speaking companion.

## Package structure and record format

Create a folder named by the assigned `packId`. Include `manifest.json`, `vocabulary.json`, `README.md`, `validation-report.json`, one JSON file per requested record type, and `proposed-mechanics.json` (an empty entries array if none). If possible, deliver a ZIP with that folder intact. Do not claim files exist when only text was produced.

Every content file has this exact wrapper:

```json
{"schemaVersion":1,"packId":"ss-example-expansion","recordType":"example","entries":[]}
```

Each entry has these common fields, plus exactly the fields listed for its record type in the numbered handoff:

```json
{
  "id":"example-001",
  "name":"A readable name",
  "summary":"A compact description of this candidate.",
  "tags":["practical"],
  "ancestryRestrictions":[],
  "excludedAncestries":[],
  "visibility":"public-template",
  "establishedFactRequirements":[],
  "continuityWarnings":["This is a possibility, not an event that has happened."],
  "references":[],
  "mechanicsProposalId":null
}
```

`visibility` is `public-template` or `private-template`; public-template means potentially player-visible prose, not permission to reveal an undiscovered clue. `ancestryRestrictions: []` means all; `excludedAncestries` denies particular ancestry IDs. Do not overlap the two. Optional inputs use explicit null; lists always use arrays. Do not add arbitrary keys.

`establishedFactRequirements` contains objects with exactly `fact` (the required state, <=300 chars) and `evidenceNeeded` (what actual gameplay record or human review could establish it, <=300 chars). This is non-executable narrative metadata. Say what is needed; never assert it has occurred.

`references` entries have exactly `namespace` (`baseline`, `pack`, or `dependency`), `id` (a real record ID), and `purpose` (<=200 chars). Baseline IDs must exist in `prototype-reference.json`; pack references must resolve within this output; dependency references must resolve to a delivered dependency named in the manifest. If a dependency is unavailable, do not invent its IDs: put the missing integration need in the report and write the concept without that reference. No recursive dependency on this same pack. Names are not substitutes for IDs.

Use UTF-8 JSON, unique keys, stable lowercase kebab-case ASCII IDs with pack/type prefixes, no executable scripts/HTML/role instructions. IDs must be globally unique across expansion packs. Names <=80 characters; summary <=500; other strings <=600 unless a smaller limit is stated. Arrays of prose usually 1–5 items unless the category specifies another range. Do not fill counts with cosmetic duplicates.

`vocabulary.json`: `{ "schemaVersion":1, "tags":[{"id":"practical","definition":"Useful, careful everyday work."}] }`. Define every tag used in this pack; reuse existing foundational tags where they actually fit. Do not overwrite meanings or use tags as hidden powers.

`manifest.json` has exactly: `schemaVersion` (1), `packId`, `packVersion` ("0.1.0"), `status` ("draft-for-implementation"), `language` ("en"), `dependencies` (array of objects with `packId`, `packVersion`, `reason`), `files` (array of `path`, `recordType`, `count` objects), `vocabularyPath`, `readmePath`, `validationReportPath`. Relative paths only. Supporting paths name their corresponding files above. Declare every content file including proposed mechanics; counts must match delivered records, not requested targets.

`validation-report.json` has `schemaVersion:1`, `checksPerformed` (string array), `automatedChecksRun` (boolean), and string-array fields `duplicateIds`, `brokenReferences`, `undeclaredTags`, `countShortfalls`, `mechanicalUncertainties`, `semanticConcerns`, `knownLimitations`. State which checks actually ran. A model's own prose review is not human review or external originality clearance.

## Proposed mechanics: separate and explicitly provisional

Narrative objects contain no executable effects or unreviewed numeric bonuses. When a concept needs a new rule, reference a record in `proposed-mechanics.json`, using the same wrapper with `recordType: "mechanics-proposal"`. Such records have exactly:

- `id`, `name`, `status` (always `proposed-not-implemented`).
- `designIntent` (string), `existingRuleReferences` (array of real baseline IDs).
- `prerequisites` (string array) and `effects` (array of effect objects).
- `costs`: object with `crowns` (nonnegative integer or null for undecided), `materials` (array of input objects), `workPhases` (positive integer or null), `workOwner` (string describing whose existing assignment is used).
- `stackingRule`, `cancellationRule`, `repeatUseRule`, `failureOrRecovery`, `balanceRationale` (strings).
- `testScenarios` (array of 3–6 strings), `implementationNeeds` (string array).

Each effect object has `target` (readable variable/resource description), `trigger` (exact point of application), `change` (plain-language deterministic proposal), `magnitude` (number or null), `unit` (string), `cap` (number or null), `exclusions` (string array). No JavaScript, SQL, formulas evaluated as code or arbitrary commands. Each material input has `materialId` (real ID or null), `propertyId` (real/proposed property ID or null), `quantity` (positive integer or null), `consumption` (`on-start`, `on-completion`, `not-consumed`, or `undecided`). Exactly one of materialId/propertyId is non-null. Proposed IDs require references to actual delivered records.

New numeric values are **design suggestions**, never claims of implemented balance. Compare against the supplied actual baseline when relevant; name assumptions. Use null where deciding a number would be false precision. Do not assign costs to ordinary affection, undressing, consent, refusal or being attractive. Do not convert fanservice flavour into compulsory obedience or a production multiplier. No unlimited action loops, duplicate rewards or free respecs erasing memories. Always address cancellation/refunds, repeatability, stacking, ownership and save persistence.

A record that merely describes an existing item still references its real baseline ID and has `mechanicsProposalId:null`; do not clone or alter the current rules. A new appearance/name does not grant a stronger effect.

## Production and quality

First build vocabulary and a small complete pilot file. Then complete the requested files in batches; stop at file boundaries if output limits interrupt work. Check JSON, exact field sets/types, counts, IDs, dependency references, tags and ancestry restrictions. Compare near-duplicate concepts and identify genuine exceptions. Avoid hidden mandatory story outcomes. Frame resolutions as possibilities that wait for player decisions and actual gameplay.

Write every new field listed in the numbered handoff. Field declarations such as `string[]` mean an actual array of strings; `reference[]` means entries using the common reference object. Nested object shapes are specified inline. Leave no TODOs disguised as finished entries. If you cannot meet a target without filler, deliver fewer strong entries and report the exact shortfall. Do not request routine approval between files; continue the assigned pack until complete.
