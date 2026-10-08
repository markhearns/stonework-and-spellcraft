# Stonework and Spellcraft — gamemaster content handoff

Version: 1.0 · 4 October 2026

Give this document to the content-generating LLM. The instructions below are addressed directly to it. Produce the content files, not merely suggestions about them.

This is a proposed content-pack contract for a future importer. The current v0.32 prototype does **not** import this format automatically. Existing saves, characters and rules remain authoritative; these files supply candidate narrative ingredients for later validation and integration.

## 1. Your task

Create a reusable, coherent content pack for **Stonework and Spellcraft**, a self-hosted fantasy household RPG. The player develops an inhabited castle, pursues practical magic, meets companions, and helps a household grow through work, discovery and personal stories.

Generate both:

1. **Ancestry-specific content:** 100 names, 25 story seeds and 25 physical appearance descriptions for each of the 21 ancestries below.
2. **Shared characterization and story content:** personality nuances, values and boundaries, habits, conversational voices, occupations/backgrounds, ambitions, social/flirtation styles, household interactions, clothing components, ensembles and story-development patterns.

Generate data in valid UTF-8 JSON. Work in complete-file batches. Do not squeeze the whole assignment into one response by abbreviating records, using ellipses, repeating filler, or claiming unproduced entries are complete.

## 2. Creative direction and firm boundaries

### Atmosphere

A handmade, enchanted library-workshop: dark academia with warmth, practical magic, and knowing mischief. Mysterious but welcoming, scholarly but alive. Midnight paper, violet ink, worn archival gold, graphite, ink contours and gouache. Think useful objects made with care and rooms people actually inhabit.

Avoid opulent palaces, excessive ornament, glossy plastic finishes, generic grimdark cruelty and grandiose prose. This is a fantasy setting: do not import modern electronics or clothing by default.

### Adult character direction

Recruitable NPCs are adult women aged **18–25**, with diverse faces, skin tones within ancestry constraints, mature builds, hair, tastes and personalities. Beautiful, cute, sexy, or combinations of these are central to the game's appeal. Cute must describe adult charm, never a childlike body, role or presentation.

Use confident sensuality, flattering clothing, playful teasing, affectionate warmth and non-explicit fanservice. Do not make everyone identical in body shape or expression. Oni should retain their specified powerful, generously curvy and large-busted direction.

**Golem exception:** a constructed companion awakens fully adult in form and cognition. An adult-form age of 18–25 describes presentation, not years of lived experience. Do not invent a childhood, previous career, former lover or years of memories for a newly awakened golem. Use prospective interests and capabilities supplied by the approved construction instead. Other ancestries, including vampires and spirits, must not use centuries-old histories to evade the agreed age range.

### Agency and continuity

Characters have independent goals, values and boundaries. An ancestry does not prescribe morality, submissiveness, aggression, loyalty, sexual availability or romantic interest. Flirtation is an expressive style, not blanket consent. Recruitment, accommodation, work and romance are separate choices.

Story seeds propose possibilities. Never assert that the player has kissed someone, accepted an invitation, completed work, visited a location, given a gift or established a relationship. Do not invent secrets about the castle or declare someone a lost heir to its ownership. Do not write Eris or Selene as NPCs: they are reserved external-player identities.

Do not attach numeric attributes, bonuses, costs, probabilities, mechanical rewards, unlock commands or code to prose. Do not grant money, artifacts, skills, spells, extra actions, affection or Resonance by describing them. Resonance concerns the household's consensual sensual atmosphere; these content records do not award or spend it.

## 3. Ancestry registry — use these IDs exactly

| ancestryId | ancestryName | arrivalMethod | Required direction |
| --- | --- | --- | --- |
| human | Human | recruitment | Varied human appearances and cultures |
| high-elf | High elf | recruitment | Fair-skinned forest elves; distinct woodland traditions |
| dark-elf | Dark elf | recruitment | Elegant elves with chocolate-brown skin; their own varied traditions |
| drow | Drow | recruitment | Subterranean elves, distinct from dark elves; slate, charcoal or violet-grey skin are suitable; no prescribed evil disposition |
| catfolk | Catfolk | recruitment | Humanlike women with feline ears and tails; varied feline markings/features, without turning every character into a fully furred animal |
| bovinefolk | Bovinefolk | recruitment | Strong humanoid women with bovine horns, ears and tails; human faces and smooth skin without a fur coat |
| orc | Orc | recruitment | Green skin, sturdy builds and endurance; small tusks are suitable; personality remains individual |
| wolfkin | Wolfkin | recruitment | Humanlike wolf women with wolf ears and tails; smooth human skin; no compulsory pack behaviour |
| demon | Demon | summoning | Infernal traits such as horns and tails; varied personalities, not mandatory cruelty |
| seraph | Seraph | summoning | Celestial women with feathered wings and restrained light/halo motifs; use “Seraph,” not “Angel” |
| elemental | Elemental | summoning | Adult humanoid forms with coherent fire, water, earth, air or other carefully described elemental features |
| vampire | Vampire | summoning | Subtle fangs and nocturnal character; no mandatory predation or ancient age |
| fae | Fae | summoning | Otherworldly ears, markings or iridescence; distinct from ordinary elves |
| djinn | Djinn | summoning | Supernatural shimmer, smoke or air-associated features; no automatic wish-granting or servitude |
| dragonkin | Dragonkin | summoning | Humanoid women with draconic horns, scales and related accents; no free dragon powers |
| spirit | Spirit | summoning | Ghostly or softly luminous adult forms; do not presume a traumatic death or secret castle connection |
| dryad | Dryad | summoning | Woodland/tree-rooted identity, botanical markings and wood/leaf features; do not assume immobility or compulsory attachment to the castle |
| nymph | Nymph | summoning | Natural-place identities associated with springs, rivers, gardens and similar places; distinguish these from dryads |
| kitsune | Kitsune | summoning | Supernatural fox women, fox ears and tails; illusion/transformation may be interests or traditions, never automatically granted abilities |
| oni | Oni | summoning | Horns, imposing strength, pronounced mature curves and large busts; powerful physical style without compulsory brutality |
| golem | Golem | construction | Clearly adult feminine crafted forms: clay, porcelain, carved stone, living wood or enchanted metal; visible handmade detail |

There are **8 common ancestries, 12 exotic ancestries and 1 constructed ancestry**. Wolfkin are common. Kitsune and oni are exotic. Golems are constructed rather than summoned. Do not add dwarves, halflings, gnomes or further ancestries to this pack without a separate instruction.

Aurelia's established warm-tanned appearance is specific to her, not a skin-colour restriction on every seraph. Do not rewrite any established character through these pools.

## 4. Deliverables and quantities

### Ancestry files

Create `ancestries/<ancestryId>.json` for each registry entry:

- 100 names.
- 25 story seeds.
- 25 physical appearance descriptions.

That is **2,100 names, 525 story seeds and 525 appearance descriptions**. These are initial production targets, not a reason to pad weak material. Flag any genuine shortfall rather than silently reducing quality.

### Shared files

| File under shared/ | poolType | Entries |
| --- | --- | ---: |
| personality-nuances.json | personality-nuance | 50 |
| values-boundaries.json | value-boundary | 40 |
| habits-mannerisms.json | habit-mannerism | 50 |
| conversational-voices.json | conversational-voice | 25 |
| occupations-backgrounds.json | occupation-background | 40 |
| ambitions.json | ambition | 50 |
| social-flirtation-styles.json | social-flirtation-style | 25 |
| household-interactions.json | household-interaction | 50 |
| clothing-components.json | clothing-component | 60 |
| ensembles.json | ensemble | 30 |
| story-development-patterns.json | story-development-pattern | 25 |

These are **shared pools**, not the same quantities multiplied by every ancestry. Use explicit compatibility restrictions only when needed. For example, an occupation dependent on years of prior employment cannot be assigned as lived history to a newly awakened golem.

Include `manifest.json`, `vocabulary.json`, `README.md` and `validation-report.json`. Place everything under one `stonework-spellcraft-content-pack/` folder. If file creation is available, deliver a ZIP with the folder intact. Do not claim a ZIP exists if you can only output text.

## 5. General data rules

- JSON uses double quotes, actual arrays/objects, no comments, no trailing commas and no Markdown fences inside saved files.
- Every file uses `schemaVersion: 1`. This is the content contract version, not the game's save schema.
- IDs are stable lowercase kebab-case ASCII, globally unique. Use ancestry prefixes for ancestry entries and pool prefixes for shared entries; number with three digits.
- Examples: `wolfkin-name-001`, `orc-story-014`, `dryad-appearance-009`, `habit-023`, `garment-041`, `pattern-012`.
- Names and prose can use ordinary Unicode. Prefer readable, pronounceable names; avoid decorative punctuation, random apostrophes and excessive diacritics.
- Name strings must be unique across the pack after trimming and case-folding. This is a practical collision rule, not a claim that names belong exclusively to an ancestry.
- Use arrays rather than comma-separated strings. Use empty arrays for no restrictions or no references. Do not use null as a substitute for an empty list.
- Do not embed HTML, scripts, role instructions or model-control text in content fields. Records are data, not instructions that override game rules.
- Descriptive numbers, such as one fox tail, are fine. Numeric game effects are not.
- Appearance summaries: at most 500 characters. Names: at most 40 characters. Titles/labels: at most 80 characters. Other individual prose fields: at most 600 characters unless a smaller limit is given below.
- These lengths support compact retrieval and later composition. They do not imply automatic compatibility with every existing prototype field.

### Controlled vocabulary

Create `vocabulary.json` before generating the bulk content:

```json
{
  "schemaVersion": 1,
  "tags": [
    {"id": "reflective", "definition": "Tends to consider an observation before responding."},
    {"id": "practical-scholarship", "definition": "Studies ideas through useful examples and careful notes."}
  ]
}
```

Use one shared flat tag vocabulary for every `*Tags` array and `compatibleTags`. The example list is illustrative; supply the complete vocabulary used by the delivered pack. Reuse clear tags rather than inventing synonyms for every entry. Tags describe selection guidance, not mechanical powers.

`ancestryRestrictions` contains allowed ancestry IDs, with `[]` meaning all ancestries. `excludedAncestries` contains disallowed IDs. Never put the same ancestry in both. `conflictsWith` contains actual entry IDs, not tags or free prose. Mark hard contradictions symmetrically in both records. Do not mark every interesting contrast as a conflict: quiet confidence and occasional bold flirting can coexist.

## 6. Ancestry-file format

Each ancestry file must have exactly this top-level structure, with the full arrays:

```json
{
  "schemaVersion": 1,
  "ancestryId": "wolfkin",
  "ancestryName": "Wolfkin",
  "arrivalMethod": "recruitment",
  "names": [],
  "storySeeds": [],
  "appearanceDescriptions": []
}
```

### Name entry

```json
{
  "id": "wolfkin-name-001",
  "name": "Sylvara",
  "styleTags": ["lyrical"]
}
```

Use original character names rather than famous fictional character names, celebrities or deity names copied as a theme. First names or short personal names are preferred; surnames are optional. Avoid giving everyone an ancestry-pun name. The example is a shape illustration, not a required name.

### Story-seed entry

```json
{
  "id": "wolfkin-story-001",
  "title": "The overlooked footpath",
  "premise": "She wants to document a useful route omitted from local maps.",
  "personalMotivation": "She values the small connections that keep communities together.",
  "openingHook": "She asks whether the household keeps reliable field notes.",
  "possibleDevelopments": [
    "Compare conflicting route descriptions.",
    "Propose fieldwork to check an unresolved observation."
  ],
  "backgroundTags": ["courier", "mapmaker"],
  "themeTags": ["exploration", "practical-scholarship"],
  "toneTags": ["warm", "playful"],
  "requirements": [],
  "continuityWarnings": [
    "Do not claim a route has been explored until gameplay establishes it."
  ]
}
```

Use 2–4 possible developments. `requirements` is an array of **plain-language narrative prerequisites**, for example “She has previously shared a completed notebook.” They are suggestions awaiting mapping to supported game checks, not executable predicates. If none are needed, use `[]`.

Across each ancestry's 25 seeds, vary domestic life, scholarship, craft, exploration, correspondence, community, humour and personal growth. A seed should contain a usable tension or question, not merely “she wants to learn magic.” Do not make every demon story temptation, every vampire story blood, or every wolfkin story pack loyalty. Ancestry should matter where natural without dominating every story. Do not transplant the same plot across 21 files with only the species word changed.

### Appearance entry

```json
{
  "id": "wolfkin-appearance-001",
  "summary": "An adult woman with warm brown skin, dark waves, grey wolf ears and a full grey tail.",
  "skin": "warm brown",
  "hair": "shoulder-length dark waves",
  "eyes": "amber",
  "build": "athletic with soft curves",
  "ancestryFeatures": [
    "grey wolf ears",
    "full grey wolf tail",
    "human face and smooth human skin"
  ],
  "distinctiveDetails": [
    "a faint freckle cluster across her nose"
  ],
  "styleTags": ["confident", "cute"]
}
```

Physical descriptions must not contain fixed names, occupations, biographies, personalities, outfits, relationship states, locations or scene actions. Keep them usable for portrait creation. Appearance tags describe visual impression, not proof of temperament or willingness.

Use 1–3 distinctive details. Make all 25 entries meaningfully different. The complete description is a coherent bundle; its component fields may be recombined later **only with compatibility review**. Do not assume arbitrary recombination will preserve anatomy or ancestry. For golems, `skin` describes crafted surface/material rather than flesh.

## 7. Shared-pool format

Each shared file uses this wrapper:

```json
{
  "schemaVersion": 1,
  "poolType": "personality-nuance",
  "entries": []
}
```

Every shared entry has these common fields:

```json
{
  "id": "personality-001",
  "label": "Quiet confidence",
  "description": "Comfortable with her abilities without needing to announce them.",
  "expressionExamples": [
    "Offers a clear practical suggestion.",
    "Accepts praise with a small, amused smile."
  ],
  "compatibleTags": ["reflective", "direct"],
  "conflictsWith": [],
  "ancestryRestrictions": [],
  "excludedAncestries": [],
  "usageNotes": "Do not interpret quietness as shyness or lack of initiative."
}
```

Give 1–3 short expression examples, no more than 200 characters each. Examples are possible expressions, never canonical events. Add the category-specific fields below to each entry in the corresponding file. Do not invent additional fields.

### A. Personality nuances — 50

Additional fields:

- `coreTrait`: string.
- `counterpoint`: string describing a coherent contrasting side.

Write combinations rather than single adjectives. For example, “adventurous about new techniques, meticulous about recording results.” Contradictions should make a person believable, not cause arbitrary behaviour reversals.

### B. Values and boundaries — 40

Additional fields:

- `kind`: one of `value`, `boundary`, `preference`.
- `importance`: one of `central`, `contextual`, `minor`.
- `welcomes`: array of strings.
- `declines`: array of strings.
- `communicationStyle`: string.

Include 15 values, 15 boundaries and 10 preferences. Cover privacy, possessions, work, promises, friendship, hospitality, affection and autonomy. No boundary is an obstacle the player is supposed to wear down. A preference does not determine another person's consent.

### C. Habits and mannerisms — 50

Additional fields:

- `trigger`: string describing a suitable context.
- `frequency`: one of `occasional`, `rare`.
- `avoidOveruse`: string.

Include small behaviours while thinking, working, relaxing or conversing. Avoid making every gesture a seductive pose or mentioning the same tail twitch in every line. Do not turn disabilities or trauma symptoms into decorative quirks.

### D. Conversational voices — 25

Additional fields:

- `sentenceRhythm`: string.
- `directness`: one of `gentle`, `plainspoken`, `forthright`.
- `humourStyle`: string.
- `metaphorDomains`: array of vocabulary tags.
- `avoid`: array of strings.

Distinguish rhythm, humour and attention without exaggerated phonetic accents or ancestry stereotypes. Do not rely on catchphrases. A voice must still answer the actual conversation.

### E. Occupations and backgrounds — 40

Additional fields:

- `occupation`: string, at most 60 characters.
- `originOutline`: string.
- `experienceThemes`: array of vocabulary tags.
- `naturalAmbitionTags`: array of vocabulary tags.
- `suggestedCapabilityPackageId`: one of `archive-reader`, `light-maker`, `water-worker`, or `unmapped`.
- `historyMode`: one of `lived-background`, `prospective-vocation`, `either`.

These package IDs are integration suggestions, not grants of mechanics. Do not stretch every profession into an unsuitable package; use `unmapped` when appropriate. Any `lived-background` entry must exclude `golem`. Include some prospective vocations that an awakened adult could choose without fabricated experience. Stay plausible within the age range; avoid careers requiring decades of mastery.

### F. Ambitions — 50

Additional fields:

- `personalMotivation`: string.
- `scope`: one of `small-project`, `multi-chapter`, `long-term`.
- `possibleFirstSteps`: array of 2–4 strings.
- `possibleComplications`: array of 1–3 strings.
- `satisfyingOutcomes`: array of 1–3 conditional possibilities.

Ambitions need motivations beyond pleasing the player. Let them concern making, understanding, belonging, exploration, independent work and relationships. Outcomes are possible resolutions, not predetermined rewards or romance.

### G. Social and flirtation styles — 25

Additional fields:

- `mode`: one of `social`, `flirtatious`, `either`.
- `suitableContexts`: array of strings.
- `signalsToProceed`: array of strings describing mutual engagement.
- `signalsToPause`: array of strings.
- `boundaryResponse`: string.

Include 8 primarily social, 9 flirtatious and 8 adaptable styles. Keep confident, sexy fanservice present without making every resident constantly flirt. Examples may include bold compliments, dry teasing, coy playfulness, quiet confidence, affectionate warmth or shared enthusiasm. Do not script the player's reply, feelings or physical actions. A “signal” is narrative guidance, not a substitute for explicit agreement where needed.

### H. Household interaction seeds — 50

Additional fields:

- `participants`: one of `npc-player`, `two-npcs`, `small-group`.
- `openingInvitation`: string.
- `requirements`: array of plain-language narrative prerequisites.
- `possibleResponses`: array of 2–4 optional directions, not player dialogue forced as fact.
- `possibleDevelopments`: array of 2–4 strings.
- `continuityWarnings`: array of strings.

Cover quiet company, playful disagreement, craft collaboration, shared hobbies, correspondence, celebrations and mundane household details. Invitations can wait without expiry. Do not impose jealousy, attention decay, emergencies or punishments for declining. For multiple NPCs, do not assume one character knows another's private thoughts or conversations.

### I. Clothing components — 60

Additional fields:

- `slot`: one of `top`, `bottom`, `dress`, `outer-layer`, `footwear`, `accessory`.
- `materials`: array of 1–3 strings.
- `colours`: array of 1–3 strings.
- `silhouette`: string.
- `coverage`: string describing non-explicit coverage.
- `anatomyAccommodations`: array of strings for wings, horns, tails or crafted joints where relevant.
- `occasionTags`: array of vocabulary tags.
- `incompatibleSlots`: array of slot names.

Target 12 tops, 12 bottoms, 10 dresses, 8 outer layers, 8 footwear entries and 10 accessories. Include practical, relaxed and alluring choices. Clothing should feel tactile: linen, wool, soft leather, silk accents, worn metal fittings. Avoid making every outfit purple or covered in gold. No armor statistics, crafting recipes, prices or enchanted bonuses.

### J. Ensembles — 30

Additional fields:

- `componentIds`: array of actual garment IDs from the delivered component file.
- `occasionTags`: array of vocabulary tags.
- `stylingNotes`: string.
- `anatomyAccommodations`: array of strings.

Combine garments coherently: no mutually exclusive slots, accidental duplicate shoes, incompatible layers or ignored wings/tails. Include working, leisure, evening and social styles. Keep clothing independent of identity so characters can change outfits. Ensembles are design candidates, not permission to alter an established portrait or automatically dress a character.

### K. Story-development patterns — 25

Additional fields:

- `opening`: string.
- `complication`: string.
- `meaningfulChoice`: string.
- `possibleResolutions`: array of 2–4 strings.
- `followupInvitation`: string.
- `requiredEstablishedFacts`: array of plain-language prerequisites.
- `continuityWarnings`: array of strings.

Patterns describe reusable narrative structure, not a whole prewritten quest or deterministic outcome. Vary discovery, revision, collaboration, changing priorities, friendly disagreement, experimentation and gradual understanding. Support modest meaningful stories as well as larger arcs. Include ways for a character to revise a goal without failure or humiliation. Resolutions must wait for actual gameplay; no automatic advancement, intimacy, item delivery or time passage.

## 8. Manifest and supporting files

`manifest.json` must contain:

- `schemaVersion`: 1.
- `packId`: `stonework-spellcraft-character-foundations`.
- `packVersion`: `1.0.0`.
- `language`: `en`.
- `status`: `draft-for-integration`.
- `ancestries`: the full registry, each object containing `ancestryId`, `ancestryName`, `arrivalMethod`, `path`, and `counts` with `names`, `storySeeds`, `appearanceDescriptions`.
- `sharedPools`: objects with `poolType`, `path`, `count`.
- `vocabularyPath`: `vocabulary.json`.
- `readmePath`: `README.md`.
- `validationReportPath`: `validation-report.json`.

Paths are relative to the pack folder, use `/`, and must name real delivered files. Counts must match actual records, not requested targets if production is incomplete. `README.md` should explain scope, file order, tag conventions and known limitations. It must state that game import and mechanical mapping remain future integration work.

Use this structure for `validation-report.json`:

```json
{
  "schemaVersion": 1,
  "checksPerformed": [],
  "automatedChecksRun": false,
  "duplicateIds": [],
  "duplicateNames": [],
  "brokenReferences": [],
  "countMismatches": [],
  "undeclaredTags": [],
  "contentWarnings": [],
  "knownLimitations": []
}
```

Each issue array contains descriptive strings. Empty arrays mean no issue was found by the checks actually performed, not a guarantee of perfection. Set `automatedChecksRun` to true only if you really executed checks. State whether originality/near-duplicate review was manual or automated; do not claim external copyright clearance.

## 9. Quality and validation checklist

Before delivery:

1. Parse every JSON file if execution tools are available. Verify required fields, types and counts. Otherwise say syntax was manually reviewed.
2. Check all IDs, names, manifest paths, garment references, conflict references and vocabulary tags.
3. Check the full ancestry/path registry, especially common wolfkin, exotic kitsune/oni and constructed golems.
4. Check each appearance against anatomy, skin-direction constraints, adult presentation and internal consistency.
5. Check that golem stories/backgrounds do not invent a lived past.
6. Review near-duplicate plots, personalities and descriptions, including duplicates disguised by different ancestry labels.
7. Check that no story determines the player's actions, establishes unearned discoveries or awards game effects.
8. Check that compatibility allows interesting variety and does not make every ancestry one personality type.
9. Check ensemble references and layering against garment slots and anatomy.
10. Report shortfalls and uncertainties honestly. Never replace missing records with empty placeholders while claiming the requested count is complete.

## 10. Recommended generation sequence

1. Prepare the registry, field conventions and initial vocabulary.
2. Generate **one complete ancestry file** as a format and quality pilot. Human or wolfkin is a suitable first choice; do not make the pilot a required user-approval bottleneck unless requested.
3. Generate remaining ancestry files in small complete batches. Explicitly check golems, the three elven ancestries and the new common/exotic distinctions.
4. Generate shared personality, values, habits, voice, occupation, ambition and social pools.
5. Generate interactions and story patterns, using the same tags.
6. Generate garment components, then ensembles referencing those finished components.
7. Finalize the vocabulary, manifest, README and validation report. Recheck references after any edits.
8. Deliver the files and a concise count/quality summary.

If output limits interrupt work, end at a file boundary and state the exact next file. Do not truncate a JSON object. If asked to continue, continue the missing files without replacing finished IDs or regenerating finished content.

## 11. What this pack does not do

It does not implement an autonomous gamemaster, establish final castle lore, authorize external-player actions, generate or attach portraits, import content into v0.32, or change existing save identities. It gives the gamemaster varied, coherent, reviewable ingredients. Selection rules, persistence, prompts, mechanics, image review and acceptance remain the application's responsibility.

