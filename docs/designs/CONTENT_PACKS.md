# Content packs and character review — v0.33

The game accepts the schemaVersion 1 content handoff in `docs/stonework-and-spellcraft-gamemaster-content-handoff.md`. This is a narrative ingredient importer, not an executable quest loader. The application remains a self-hosted Python-standard-library/SQLite webapp with local JavaScript and assets.

## Player workflow

1. Open **About & saves → Character content packs** in the intended campaign.
2. Choose the other LLM's ZIP and press **Validate selected ZIP**. Validation does not activate the pack, advance time, or contact a model.
3. Read the errors, shortfalls, author-reported limitations and integration limitations. Invalid packs cannot be activated. Production quantity shortfalls are warnings, so an honestly incomplete pack can be used.
4. **Browse actual content**. Choose a collection and open individual records; the browser shows 25 at a time. The author's notes are available as plain text.
5. Confirm review and activate the pack for future proposals.
6. In **People & arrivals → Propose & review a new visitor**, select the imported ingredient source. Choose an ancestry/arrival path and, for a golem, body material. Built-in background/temperament/story selectors do not apply in imported mode.
7. Compose offline or explicitly request a model-written proposal. Open **Source ingredients** to inspect the full records. Offline prose is shortened to the existing candidate field limits; the complete source is retained.
8. Use **Revise this draft** to edit individual narrative fields, accommodation and stay preferences. Saving edits rechecks the proposal without a provider call. Read the resulting identity and exact rules, then approve it as a contact plan. Arrival, housing and household membership still require their existing separate steps.

A deliberately small fixture can be downloaded in the pack panel. It supports Wolfkin, Demon and Golem and reports all shortfalls. It is a test/example pack, not the finished content collection. Regenerate it with `python examples/build_content_fixture.py`.

## Validation and storage

- Exactly one pack root, all 21 registry entries and all 11 shared-pool wrappers. Empty arrays are permitted but clearly reported as production shortfalls.
- Exact record fields, types, lengths and enumerated values; unique JSON keys; globally unique record IDs; unique case-folded names and reserved-character protection.
- Ancestry route mappings, manifest counts and paths; declared vocabulary tags; real, symmetric conflict references; allowed/excluded ancestry consistency; lived-background exclusion for golems.
- Real garment references, duplicate/exclusive slots, incompatible garments and ensemble ancestry restrictions.
- Supporting vocabulary, author validation report and README retained alongside narrative records. Author assertions are not treated as proof that this application ran those checks.
- ZIP read in memory, never extracted. At most 100 archive entries; at most 6 MB compressed and expanded; no traversal, links, ambiguous paths, duplicate members, executable files or non-UTF-8 content.
- Accepted packs are immutable content-addressed rows in each campaign's SQLite database. At most twelve validated versions per campaign. Validation stores a pack/report but does not change campaign revision; activation/deactivation uses existing transactional revision and request-ID checks.
- Pack status, source notes and hashes are not interpreted as instructions. Pack prose cannot change costs, abilities, time or game state.
- Complete SQLite save backups include the validated packs. Public state and diagnostic JSON expose only the active summary and character source snapshots, not the full collection. Provider secrets remain excluded as before.

Structural validation cannot prove adult presentation, ancestry anatomy, story coherence, consent, originality, absence of semantic instructions, or compatibility hidden in prose. The explicit content review remains necessary. Markup/control characters in entry fields are rejected; browser rendering escapes all imported and edited text.

## Generation

Generation chooses an unused name, a whole appearance bundle, an unconditional ancestry story, a mapped occupation, personality, value/boundary/preference record, habit, conversational voice, ambition and social/flirtation style. Ancestry restrictions and hard conflicts constrain selection; shared tags and usage history weight it. Backtracking has a fixed work budget and produces an understandable failure if no supported combination is found. It does not relax contradictory constraints.

Supported starting packages remain `archive-reader`, `light-maker` and `water-worker`. `unmapped` backgrounds stay browsable but are excluded from generation. Narrative prerequisites are not executable checks: stories with any `requirements` are excluded from new-character selection.

Golems require `prospective-vocation` backgrounds. The existing construction material controls their appearance, rather than guessing a material from appearance prose. Their 18–25 age is adult-form presentation, never years lived. Common ancestry recruitment, exotic-only summoning and golem construction remain authoritative.

The request ID stabilizes selection. Repeating a saved request returns the same draft, including after pack changes and restarts. Accepted characters retain their exact source records, selected tag definitions and pack digest/version. Later pack activation or deactivation cannot rewrite them. Saved roster usage discourages repeated ingredients; already accepted names cannot be selected again.

Imported draft defaults are a private room and visit-only. These are conservative composer defaults, not inferred consent or personality rules; review can change them before approval. A model-written draft may propose other supported preferences for review.

## Review and continuity

Narrative edits are allowed only on ready, unapproved drafts. Selected age, ancestry, occupation and capability package remain locked. The original proposal and source ingredients remain as provenance; reviewed prose becomes the accepted identity. An edit counter prevents stale tabs from overwriting or approving an unseen revision. Campaign revisions independently guard against changed world state.

The resident's own saved personality, value/boundary, habit, voice, ambition, social style and story seed are included in their dialogue and personal-story prompt context. Original source possibilities are not memories; reviewed identity prose takes precedence over source text when revised. Another resident's source data or private conversation is not added to that context. Imported source records are also inspectable on the resident's character sheet.

## Deliberately unfinished

Household-interaction seeds, clothing components/ensembles and story-development patterns are validated and browsable, but do not yet instantiate new scenes, wardrobes or quest mechanics. The general gamemaster, actual co-op agents and rendered-browser acceptance remain unfinished. No model provider is required to import, compose offline, review or approve a character; live-provider generation has not been exercised in this checkpoint.

## Verification

The importer regression suite covers malformed archives/schema, references, route mappings, incomplete packs, campaign isolation, explicit activation, backup preservation, migration, deterministic generation, compatibility failures, name exhaustion, usage weighting, edited-draft concurrency, HTTP routes and saved identities across pack versions. A connected headless UI test walks through upload, validation, browsing, activation, offline generation, editing, escaped rendering, approval and deactivation. It is controller/template integration, not rendered-browser or keyboard/layout testing.

## Later integration

v0.34 adds reviewed scene, cosmetic wardrobe and story-pattern flows; see HOUSEHOLD_CONTENT.md. The earlier unfinished list above describes the v0.33 checkpoint.
