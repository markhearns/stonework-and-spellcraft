# Stonework and Spellcraft — expansion content handoffs

The original character-foundations ZIP is available unchanged at [the downloadable example pack](../../static/examples/stonework-spellcraft-content-pack.zip). Give the other LLM that ZIP, this folder, and one or more numbered assignments. Tell it: **Read 00-shared-contract.md and the assigned handoff. Generate the requested complete content pack, validate it, and deliver its files. Do not implement game code or claim unsupported imports work.**

The supplied character pack passed the prototype's structural validation: 2,100 names, 525 appearances, 525 story seeds and 445 shared records (3,595 total). It already covers personality, boundaries, voices, ambitions, clothing, ensembles, interaction seeds and story patterns. Extend those categories with usable follow-through; do not commission duplicate pools just to increase counts.

These seventeen handoffs cover the useful adjacent content areas. They are a menu and phased backlog, not a recommendation to generate everything immediately. The current runtime only imports the established character-foundations contract; all new expansion contracts need code integration and mechanical review. The prototype-reference JSON records actual current IDs/rules to ground suggestions.

## Recommended order

1. Materials/properties (01), equipment (02), household artifacts (03), and magic (04): the most useful next mechanical foundation. Supply finished material IDs to subsequent authors; otherwise they must describe an unmet dependency without inventing references.
2. Rooms/furnishings (06), expeditions (07), personal arcs (10), and branching household scenes (11): immediately useful design breadth with clear gameplay connections.
3. Rituals (05), encounters/care (08), communities/services (09), letters/commissions/gifts (12).
4. Optional books/food/gardens/treasures (14), visual briefs (15), and help/QA (16). These should follow approved concepts rather than produce art or documentation for discarded mechanics.
5. Private mystery alternatives (13), separately from public content. Avoid reading those outputs yourself if you want the eventual mystery unspoiled.

Start with a complete pilot of 5–10 entries in the high-priority areas, check that the schema and concepts are useful, then fill the stated targets. This is a quality checkpoint the author can perform without waiting for repeated permission. More content is only useful when it has distinct purposes, coherent dependencies and usable integration boundaries.

Background mappings and earned development (17) are also high-value: the received pack leaves thirty occupations unmapped. Assign this after the material/equipment/magic pilots so new packages share a coherent balance baseline.

## Assignments

| File | Pack | Priority | Requested records |
|---|---|---|---:|
| 01-materials-and-properties.md | Materials and component properties | High | 72 |
| 02-equipment-and-signature-items.md | Equipment and evolving signature items | High | 96 |
| 03-artifacts-and-recipes.md | Household artifacts and crafting recipes | High | 80 |
| 04-magic-principles-and-spells.md | Magic principles and bounded spell constructions | High | 126 |
| 05-rituals-and-voluntary-augmentation.md | Rituals, voluntary augmentation and reversal | Medium | 42 |
| 06-rooms-furnishings-and-synergies.md | Room purposes, furnishings and understandable synergies | High | 120 |
| 07-expeditions-and-discoveries.md | Expedition sites, leads and reusable discoveries | High | 126 |
| 08-encounters-and-care.md | Field encounters, negotiation and specialized care | Medium | 72 |
| 09-communities-services-and-visitors.md | Neighbouring communities, services and recurring contacts | Medium | 64 |
| 10-personal-arcs-and-relationships.md | Personal arcs and descriptive relationships | High | 78 |
| 11-household-scenes-and-ambient-life.md | Household scenes, fanservice and ambient life | High | 160 |
| 12-letters-commissions-and-gifts.md | Correspondence, commissions, gifts and keepsakes | Medium | 100 |
| 13-private-mystery-foundations.md | Alternative private castle foundations and evidence | Later; avoid spoiling active play | 42 |
| 14-books-food-gardens-and-treasures.md | Books, food, gardens and unusual treasures | Optional breadth | 124 |
| 15-art-and-visual-production.md | Art briefs and visual continuity | Optional; after concepts are selected | 93 |
| 16-tutorials-explanations-and-qa.md | Tutorial copy, explanations and integration scenarios | Useful alongside implementation | 144 |
| 17-backgrounds-training-and-perks.md | Background capability mappings, training and earned perks | High after equipment and magic | 102 |

## Suggested assignment message

> Create packs 01–04 using the supplied shared contract and prototype-reference.json. Begin with materials, then use its real IDs in equipment, artifacts and magic. Keep every new mechanical effect a separate proposed-mechanics record. Preserve the established game's agency, time and ownership rules. Generate complete files in batches, validate what you can, report honest limitations, and deliver one ZIP per completed pack. Do not stop after outlining the work.

For a prose-focused LLM, assign 10–12 instead. For a visual specialist, assign 15 only after the relevant item/room/wardrobe references are supplied. Multiple authors should own different pack namespaces and exchange actual dependency files; they must not independently invent competing materials or rule IDs.

## What not to commission yet

Do not ask a content author to write an entirely new magic engine, combat engine, economy, co-op protocol or autonomous gamemaster as if it were content data. Those need implementation and testing. Do not multiply each shared content count by 21 ancestries. Do not generate another 2,100 names or another base personality collection until actual play reveals a shortage. Do not create final castle canon that overwrites an active campaign.


---

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


---

# Materials and component properties

Pack ID: `ss-materials-and-properties` · Initial target: **72 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Extend property-based substitution, not one-name-only shopping lists. Include mineral, botanical, textile, ceramic, glass, resin, ink and crafted substrates. Existing properties are heat-bearing, binding, botanical and vessel. New properties are proposals, never added to current rules merely by appearing here. Rare materials should open interesting options rather than make basic comfort grindy. No inherently sentient person or body part is a routine ingredient.

Give each material a distinct practical role. Separate physical material description from harvest yield, price or spell power; propose those separately only when useful. Explain at least one plausible substitution and one limit. Dependencies: none; this is a foundation pack.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `material.json` — recordType `material` — 60 entries

- `physicalDescription:string`
- `sourceContexts:string[]`
- `mundaneUses:string[]`
- `magicalAssociations:string[]`
- `propertyIds:string[]`
- `substitutionNotes:string`
- `handlingNotes:string`
- `rarityBand:ordinary|specialist|discovery`

### `property-concept.json` — recordType `property-concept` — 12 entries

- `definition:string`
- `suitableExamples:string[]`
- `unsuitableExamples:string[]`
- `acceptanceTest:string`
- `substitutionLimits:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

# Equipment and evolving signature items

Pack ID: `ss-equipment-and-signature-items` · Initial target: **96 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Prefer 16 signature foci, 16 useful tools, 8 field kits and 8 accessories. A cherished staff, lamp, notebook case or measuring instrument should gain functions over time. Avoid disposable loot tiers and +1/+2 ladders. Some equipment may be elegant, alluring or personally expressive, without forced body changes or consent effects.

An inscription is not automatically prepared, known, installed or granted. Describe ownership, preparation, castle-only changes, capacity and stacking through mechanics proposals. Include broad anatomy accommodations and component alternatives. Exclude wardrobe-only garments already covered by the foundations pack.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `equipment-concept.json` — recordType `equipment-concept` — 48 entries

- `equipmentKind:focus|tool|field-gear|accessory`
- `appearance:string`
- `intendedUse:string`
- `wearerRequirements:string[]`
- `componentIdeas:string[]`
- `upgradeThemes:string[]`
- `ownershipNotes:string`
- `anatomyAccommodations:string[]`

### `inscription-concept.json` — recordType `inscription-concept` — 48 entries

- `visualMotif:string`
- `principleIds:string[]`
- `intendedFunction:string`
- `validHosts:string[]`
- `incompatibilities:string[]`
- `upgradePath:string[]`
- `limits:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

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


---

# Magic principles and bounded spell constructions

Pack ID: `ss-magic-principles-and-spells` · Initial target: **126 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Do not replace the magic system. Expand its reusable-principle grammar. Separate understanding, archive availability, personal mastery, preparation, testing and casting. New spell effects remain proposed rules. Ordinary practical magic should be useful without a tedious mana tax; exceptional feats justify clear bounds and investment.

Provide 24 spells using only existing principles, 36 exploring new principles and 12 exceptional concepts. These counts describe conceptual foundations, not existing effect support. Current executable forms are only warm-twist, root-song, luminous-copy and clarify-glass. Explanations must admit when a requested effect has no supported form. No arbitrary reality editing, mind control, resurrection-as-routine or free universal mastery.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `principle-concept.json` — recordType `principle-concept` — 24 entries

- `underlyingIdea:string`
- `teachesWhat:string`
- `doesNotPermit:string[]`
- `observationQuestions:string[]`
- `experimentIdeas:string[]`
- `neighbouringPrincipleIds:string[]`

### `spell-construction.json` — recordType `spell-construction` — 72 entries

- `desiredEffect:string`
- `principleIds:string[]`
- `componentPropertyIds:string[]`
- `method:string`
- `scopeLimits:string[]`
- `ordinaryOrExceptional:ordinary|exceptional`
- `partialMatchExplanation:string`
- `prerequisitesExplanation:string`

### `spell-explanation.json` — recordType `spell-explanation` — 30 entries

- `requestExample:string`
- `assessment:supported-baseline|partial-fit|requires-new-rule|not-permitted`
- `baselineFormId:string|null`
- `helpfulExplanation:string`
- `honestAlternative:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

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


---

# Room purposes, furnishings and understandable synergies

Pack ID: `ss-rooms-furnishings-and-synergies` · Initial target: **120 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Use existing bounded rooms, not a wall-building simulator. Provide 24 purely decorative and 48 functional furnishing concepts. Explain bonuses through a text list; do not require crude furniture overlays. Visual rooms should feel inhabited and handmade, with natural eye-level composition.

Synergy is a modest understandable option, never a hidden placement trap or penalty for a small household. Bedrooms respect privacy and real capacity; twenty chairs do not create twenty resident places. Do not equate dungeon location with confinement. Keep restoration costs and new bonuses in proposed mechanics.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `room-purpose.json` — recordType `room-purpose` — 24 entries

- `dailyUse:string`
- `architecturalNeeds:string[]`
- `serviceDependencies:string[]`
- `suitableAdjacencies:string[]`
- `privateOrShared:private|shared|either`
- `illustrationBrief:string`

### `furnishing-concept.json` — recordType `furnishing-concept` — 72 entries

- `roomPurposeIds:string[]`
- `materialDescription:string`
- `decorativeChoice:string`
- `functionalProposal:string|null`
- `footprintNotes:string`
- `privacyConsiderations:string[]`

### `adjacency-synergy.json` — recordType `adjacency-synergy` — 24 entries

- `firstRoomPurposeId:string`
- `secondRoomPurposeId:string`
- `explanation:string`
- `absenceBehaviour:string`
- `maximumScope:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

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


---

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


---

# Neighbouring communities, services and recurring contacts

Pack ID: `ss-communities-services-and-visitors` · Initial target: **64 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Four recurring contact roles and three services per community. Use role IDs rather than fixed new resident names. If a role later becomes a recruit, a separate character-generation review establishes her adult identity; no common ancestry is silently summoned.

Communities have their own ordinary lives. Avoid absolute canon about rulers, wars, geography or castle ownership. Services and markets suggest options but do not alter prices/inventory without mapped mechanics. Trade should complement exploration, not bypass all research.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `community-template.json` — recordType `community-template` — 8 entries

- `character:string`
- `crafts:string[]`
- `everydayConcerns:string[]`
- `visitingEtiquette:string[]`
- `independentInterests:string[]`
- `relationshipToCastle:string`

### `contact-role.json` — recordType `contact-role` — 32 entries

- `communityId:string`
- `occupation:string`
- `ownAgenda:string`
- `conversationalStyle:string`
- `helpfulKnowledge:string[]`
- `limits:string[]`
- `recruitmentStatus:not-a-recruit|possible-future-candidate`

### `service-concept.json` — recordType `service-concept` — 24 entries

- `communityId:string`
- `serviceDescription:string`
- `whatItDoesNotSupply:string[]`
- `accessRequirements:string[]`
- `transactionNotes:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

# Personal arcs and descriptive relationships

Pack ID: `ss-personal-arcs-and-relationships` · Initial target: **78 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Two arcs per ancestry, extending rather than duplicating the existing 25 seeds each. Every chapters array has 3–4 objects with exactly title, proposedActivity, requiredEstablishedFacts (string array), optionalInvitation, possibleResolution (all other fields strings). Across relationships include 12 friendship, 10 collaboration, 8 romance and 6 friendly-disagreement entries.

Each character has an independent reason to care. Do not write the player’s actions or another resident’s private thoughts as facts. Small households remain satisfying. Resolve a practical disadvantage without erasing personality; any mechanical disadvantage change is a proposal. Romance has reciprocal choices, no obedience/reward meter or mandatory jealousy.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `personal-arc.json` — recordType `personal-arc` — 42 entries

- `ancestryId:string`
- `personalQuestion:string`
- `openingInvitation:string`
- `chapters:object[]`
- `possibleChangedGoal:string`
- `resolvedDisadvantageProposal:string|null`

### `relationship-development.json` — recordType `relationship-development` — 36 entries

- `participants:two-npcs|npc-player`
- `relationshipTheme:friendship|collaboration|romance|friendly-disagreement`
- `startingContext:string`
- `mutualChoicePoints:string[]`
- `possibleSharedMemory:string`
- `comfortableAlternative:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

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


---

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


---

# Alternative private castle foundations and evidence

Pack ID: `ss-private-mystery-foundations` · Initial target: **42 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Six mutually exclusive foundation options, six evidence fragments each. All records use visibility private-template, even when a field contains a possible player-facing observation. These are alternatives for future campaign generation, not six simultaneous truths. Do not inspect or expose a current campaign’s private lore.

The castle has a coherent unexplained affinity for consensual eroticism/intimacy but is not a speaking NPC and never controls desire. Evidence elaborates a fixed chosen foundation. No lost-heir retcon to player ownership, required trauma, ancient-age recruit or claims that an existing resident is secretly someone else. Do not reveal answers in filenames, public summaries, item names or ordinary prompt context.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `foundation-option.json` — recordType `foundation-option` — 6 entries

- `premise:string`
- `originalPurpose:string`
- `abandonmentExplanation:string`
- `sensualAffinityExplanation:string`
- `invariantFacts:string[]`
- `forbiddenRetcons:string[]`
- `compatibilityNotes:string[]`

### `evidence-fragment.json` — recordType `evidence-fragment` — 36 entries

- `foundationId:string`
- `playerFacingObservation:string`
- `privateMeaning:string`
- `interpretationAlternatives:string[]`
- `discoveryConditions:string[]`
- `disclosureScope:string`
- `contradictionChecks:string[]`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

# Books, food, gardens and unusual treasures

Pack ID: `ss-books-food-gardens-and-treasures` · Initial target: **124 content records**, plus only the necessary separate mechanics proposals.

Read `00-shared-contract.md` first; its fields and restrictions are mandatory. This assignment creates candidate content, not implemented rules.

## Purpose and direction

Give the household useful things to discuss, collect and live with. These are descriptive candidates, not inventory grants or mandatory hunger/maintenance systems. An interesting book is not automatic principle mastery. Food is not an aphrodisiac or consent tool.

Keep botanical flavour distinct from material-property records and reference those only when delivered. Strange treasures need not be powerful. No copied long quotations, real book excerpts or lyrics; create original short passages. Avoid default gold-plated relics and excessive clutter.

## Files and exact additional fields

Every record includes all common fields from the shared contract. Add the fields below for its type; do not invent additional fields. Unless overridden, strings use the shared 600-character limit and string arrays use 1–5 items. References use the common reference shape. An optional empty collection is allowed when genuinely inapplicable and explained in usage/report notes.

### `book-or-document.json` — recordType `book-or-document` — 40 entries

- `documentKind:string`
- `physicalDescription:string`
- `topic:string`
- `excerpt:string`
- `discussionQuestion:string`
- `knowledgeLimits:string[]`

### `food-or-drink.json` — recordType `food-or-drink` — 30 entries

- `sensoryDescription:string`
- `ingredientsDescription:string`
- `servingContext:string`
- `preferenceNotes:string[]`
- `preparationIdea:string`

### `garden-specimen.json` — recordType `garden-specimen` — 24 entries

- `appearance:string`
- `growingContext:string`
- `observationHook:string`
- `mundaneUse:string`
- `magicalClaimsToAvoid:string[]`

### `curiosity.json` — recordType `curiosity` — 30 entries

- `appearance:string`
- `possibleProvenance:string`
- `practicalOrPersonalInterest:string`
- `unresolvedQuestion:string`
- `displayNotes:string`

## Deliver and validate

Deliver every listed file, `proposed-mechanics.json`, the manifest, complete vocabulary, README and validation report. Keep quantities in the manifest honest. Ensure references resolve and every new mechanical claim points to a separate proposal. Check for near-duplicates, implicit player actions, presumed ownership, forced relationships, unavailable prerequisites and contradictions with actual current rules.

Include in README: an overview, reading order, dependencies actually supplied, strongest distinct concepts, concepts intentionally excluded, exact shortfalls and what integration code is still required. Mark all proposals provisional. If a dependency is not supplied, do not invent records or replace it with a fake ID; document the missing dependency and continue useful self-contained work.

Do not send a plan in place of the requested files. Complete one valid file at a time and continue until the assigned pack is done.


---

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


---

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


---

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
