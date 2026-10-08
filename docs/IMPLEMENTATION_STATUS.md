## v0.82 — Chapter 5 playability and balance

Equipment work can now stow and fund in one reviewed transaction; finished inscriptions can be equipped and activated together for the field. Reviews show missing components, reserve-aware purchase costs and assignment changes. The first watch-road upgrades now reach useful early thresholds, with named equipment and score evidence saved in the field notebook. See `docs/RELEASE_V082.md` and `docs/VERIFICATION_V082.json`.

Run `python server.py`. Keep your complete existing `data/` folder when upgrading. Schema remains 60. The local browser preview is still blocked; rendered layout is unverified.

## v0.81 — Arms of Our Own

Unified nine-slot equipment, 30 ordinary equipment designs, eight useful enchantments, personal signature requests and a playable fifth chapter are implemented. Run `python server.py` and open the address printed by the server. Start with **Equipment → Review starting equipment**; Chapter 5 opens after Chapter 4’s closing review.

Keep the **complete existing `data/` directory** when upgrading. Schema 60 creates a migration backup and retains existing names, inscriptions, paid work and accepted artwork. See `docs/RELEASE_V081.md`, `docs/EQUIPMENT_V081.md` and `docs/VERIFICATION_V081.json`. Browser-rendered layout remains unverified.

Earlier release notes below are historical.

## v0.80 — Opening campaign review

Connected Chapters 1–4 reviewed; preservation-study guidance repaired, Chapter 3 disabled reasons restored, and completed chapter summaries compacted. See `docs/RELEASE_V080.md` and `docs/CAMPAIGN_REVIEW_V080.md`. Preserve the complete existing `data/` directory. Rendered browser review remains unresolved.

## v0.79 — Companion overview portraits and splash layout

42 new room-specific, full-body portraits; equal overview columns; viewport-filling landscape. Kaede now has a fit, busty hourglass figure with subtle muscle definition. See `docs/RELEASE_V079.md`. Preserve the complete `data/` directory when upgrading.

# Historical release — v0.78

Chapter 4, Sabine’s dungeon specialty and additional resident content, and complete authored expedition image coverage are implemented. See [KEEPING_THE_HEARTH.md](KEEPING_THE_HEARTH.md), [RELEASE_V078.md](RELEASE_V078.md), [ART_V078.json](ART_V078.json) and [VERIFICATION_V078.json](VERIFICATION_V078.json). Earlier entries below are historical.

---

# Historical release — v0.77

Three connected chapters are implemented. See [ROOM_TO_GROW.md](ROOM_TO_GROW.md) for development planning and chapter continuity, [RELEASE_V077.md](RELEASE_V077.md) for changes, and [VERIFICATION_V077.json](VERIFICATION_V077.json) for current validation. All earlier entries below are historical checkpoints.

---

# Historical checkpoint — 0.76-dev (unreleased)

The playable opening chapter is documented in [FIRST_HEARTH.md](FIRST_HEARTH.md). Chapter two's three undertakings, six designs, shared work and compatibility rules are documented in [THE_HOUSE_TAKES_SHAPE.md](THE_HOUSE_TAKES_SHAPE.md). These use the established prototype history; its private lore packet is preserved. Both chapters, resident-led headquarters work and the pending v0.74 art/logo are included. The historical coverage records below retain the state of their original versions.

---

# Design implementation status — v0.38 development checkpoint

## v0.38: public workshop, practical magic and content in play

The **Public workshop** is now a main navigation destination. All **319 public proposal IDs** map to explicit prototype implementation paths, with a source-linked catalogue, resolved costs, real assignments, ownership, reservations and completion receipts. Uploaded proposals cannot change these fixed rules.

Make and own equipment, artifacts and functional furnishings; qualify materials; study public principles; build experimental setups; test, prepare and cast public forms; bind actual ritual roles; use reversible presentation trials; invest in earned methods; select capped room support; and agree funded services or delivery. Spell forms use explicit finite state transitions, preserve object identity and share existing preparation limits.

The broader catalogue now supports selected public field trips and leads, household book/meal/specimen/keepsake preparation, reviewed fictional correspondence, optional scenes and adapted narrative plans. Backgrounds, care cases and possible outcomes require review against actual play; notes do not automatically create people, knowledge, loot, capacity or accepted lore.

Save schema **36** preserves existing campaigns with an automatic migration backup. **433 Python tests and sixteen connected headless UI suites pass.** Rendered-browser layout, live models and Docker runtime remain unverified. See `docs/PUBLIC_RULES_IMPLEMENTATION.md` for exact coverage, balance decisions and limitations, and `docs/public-rule-coverage.json` for every proposal mapping. This is a substantial prototype expansion, not a claim of complete implementation of the original game design.

## v0.37: public expansion library and scene invitations

About & saves now validates and stages the included sixteen-pack public bundle in one atomic operation. The review browser exposes **1,599 content records and 319 disabled mechanics proposals**, with exact versions, dependency checks, typed references and readable nested fields. The original 3,595-record foundations pack is unchanged and is staged without automatic activation.

All **80 household scene templates** can create editable invitations. Review the setting and participants, compose the draft, then use Household life to edit, offer, defer or join it. Declining carries no penalty; no import or draft advances time, grants items, establishes future facts or changes relationships. Source records are frozen in each invitation. External players remain outside authored NPC participation.

Save schema remains **35**; no migration is required. **407 Python tests and fifteen connected headless UI suites pass**, including the public bundle HTTP route and scene transaction path. Rendered-browser, live-provider and Docker-runtime checks remain unverified. The supplied 64 acceptance scenarios are written content, not 64 newly executed tests.

The other public record types remain reviewable design content. Their equipment, spell, ritual, economy and background effects still require implementation. Next: select a coherent materials–recipe–equipment loop with explicit costs, ownership, reserve handling, cancellation and visible bonuses. See `docs/PUBLIC_PACK_INTEGRATION.md` for exact coverage.

## v0.36: discovery, research and personal inscription

The waterworks survey now feeds **Field calibration** research, which unlocks permanent inscriptions on personally owned folios and gauges. Names and ownership history persist. The owner commits 12 crowns, one vessel and one binding component above reserves, then performs two assigned inscription phases. A completed inscription replaces the prepared tool’s +1 contribution with +2. Pause/resume, exact cancellation refunds, transfer restrictions, workroom visibility and migration are implemented.

Resident completion creates an optional technical or playful conversation invitation. It does not expire or award resources or relationship points. Joined conversations become shared memories; optional model-written group scenes receive only history shared by every participant.

The Spellbook now offers **offline construction guidance** with exact personal effects, knowledge sources, facility/funding blockers and valid component combinations above reserves. Choosing a combination fills the manual form without committing an action. The four existing spell forms retain their rules.

Save schema **35** preserves existing progress. **400 Python tests and fourteen connected headless UI suites pass.** Rendered-browser, live-provider, Docker-runtime and actual-agent checks remain unverified. See `designs/FIELDCRAFT_LOOP.md` for the complete loop and limitations. New expansion content still needs reviewed implementation; staging a pack never installs its proposed mechanics.

## v0.35: personal tools, scene drafting and expansion review

**Focus & equipment → Personal working tools** now supports two craftable tools, individual ownership and names, one prepared tool per person, agreed transfers, and visible work bonuses. The folio supports assigned research/archive work; the gauge supports artifact crafting. Crafting uses existing knowledge, materials and assignments. Save schema 34 preserves ownership and preparation across reloads without advancing time.

**Household life** can request structured model-written scene prose from the optional configured provider, recover the same request, and apply reviewed wording to an unapproved invitation. Offering and joining remain separate actions. Five exact system-verifiable prerequisites now receive readable evidence; willingness and private permissions still require review.

**About & saves** adds read-only staging and inspection for expansion handoffs 01–04: materials, equipment, artifacts and magic. Proposed costs and effects remain data and do not become game rules. Includes dependency/version checks, quantity-shortfall reports, nested readable records, and a small fixture. Handoffs 05–17 still await import support.

**392 Python tests and thirteen connected headless UI suites pass**, including real local HTTP routes and mocked provider responses. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed. See `designs/EQUIPMENT_AND_DESIGN_REVIEW.md` for controls, rules and limitations.

## v0.34: full foundations pack and household life

The supplied **3,595-record character-foundations pack** is bundled unchanged. Validate it in About & saves, then activate it after review. **Household → Open household life** adds persistent scene drafts, reviewed narrative prerequisite notes, optional invitations, decline/defer, selected conversation responses and descriptive group history. The offline scene composer supplies editable scaffolding, not autonomous model-written scenes.

Residents can save and wear compatible clothing ensembles or custom garment combinations. Coverage, layering, ancestry restrictions and individual fitting/willingness are reviewed. These cosmetic styles grant no inventory or bonuses and do not repaint existing portraits. Selected story patterns guide future personal-story drafts while existing rule packages retain authority over costs and rewards. Source snapshots survive pack changes, departure and reload.

See `designs/HOUSEHOLD_CONTENT.md` and `FOUNDATIONS_PACK_REVIEW.md`. The `content_handoffs/` folder contains **17 further content-generation handoffs**, their shared schema, actual baseline rule references and the original character pack dependency. These new expansion formats are design proposals, not supported importers.

Save schema 33 adds empty household scene/style/pattern records without advancing time or rewriting identities. **381 Python tests and twelve connected headless UI suites pass.** No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.

## v0.33: imported character foundations and editable review

Content ZIPs following the gamemaster handoff can now be validated, browsed and explicitly activated in **About & saves**. Imports are campaign-specific and included in complete save backups. Errors block activation; honest quantity shortfalls and semantic-review limitations remain visible. The local fixture supports Wolfkin, Demon and Golem and deliberately reports its incomplete coverage.

Imported character generation combines compatible narrative ingredients, avoids established names and favours less-used records. It preserves selected records and pack versions with each identity. Ordinary recruitment, exotic summoning and fully adult golem construction retain their existing rules. Unmapped occupations and stories with unmapped narrative prerequisites are not selected.

Candidate review now supports individual prose and preference edits without another provider request. Locked age/ancestry/capability choices, campaign revisions and draft-edit revisions protect approval. Resident dialogue and personal-story prompts receive their own saved voice, habits, values/boundaries, social style and story ingredients; these possibilities are not completed events. Pack changes do not rewrite accepted people.

See `designs/CONTENT_PACKS.md` for the workflow and integration limits. Clothing, household-interaction and story-pattern pools are validated/browsable, but do not yet create scenes, outfits or quest mechanics automatically. Save schema 32 adds an initially inactive content-pack selection without advancing time or changing existing identities.

v0.33 verification: **372 Python tests and eleven connected headless UI suites pass**, plus JavaScript syntax checks. Real HTTP tests cover the importer and edited approvals. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.

**Current acceptance checklist:** `DESIGN_PROGRESS.md`. Historical release notes below retain the state of earlier versions.

This is a coverage record against `design_spec_v0_1.md`, not a replacement specification or a claim of a finished game. Numerical tuning and authored prototype content remain provisional. Existing design decisions remain in force.

| Design area | Implemented now | Still to build |
|---|---|---|
| Visual household | Selectable illustrated floor plan; six room views with six distinct interior illustrations; text-based furnishing/effect inventory, fixed slots and saved room arrangements; phased lighting; accepted-art review and rollback | Expanded room catalogue, expanded functional furnishing choices, occupation overlays for a larger cast; actual browser visual QA |
| Time and actions | Explicit human Advance; three phases per day; one primary task per person; persistent paused projects; no offline production | Multiple independent expedition parties; co-op readiness gate |
| Household economy | Shared treasury, personal wallets, daily allowances, departure-fixed cash shares, individual purchases and transfer history; bounded delegated artifact batches with held budgets; materials, reserves and productive facilities | Broader delegated project types, gifts, possessions and market catalogue |
| Restoration | Conservatory, three service projects, Proper Living Wing milestone and optional celebration; main-castle capacity for 25 residents + the solo founder, an optional phased 25-place annex, occupancy and named reservations | Room-purpose allocation, co-op founder scope, complete estate illustrations and floor plan |
| Character development | Three underlying attributes, three magical affinities, six earned specialization perks, individual principle mastery, earned advancement, practices, three personal skill tracks with two ranks, preparation, retraining, agreed personal principle/skill lessons, signature tools, two advanced practice paths, saved preparation sets and a reversible personal blessing | Broader perk paths, richer resident negotiations and augmentation catalogue |
| Research and magic | Hearth study, three further projects, shared archive, personal study, eleven property-based artifact recipes, four focus inscriptions; four bounded personal spell forms, testing/preparation/casting, finite agreed repeat-casting plans and one coordinated two-person ritual | Broader validated spell grammar, exceptional effects, further augmentation rituals and generated personal story arcs |
| Equipment | Personal named focus, permanent inscriptions, one/two prepared slots, separate household/expedition configurations | Broader signature items, equipment alternatives and visible loadout art |
| Resident life | Seven explicit adult sample NPCs plus reviewed generated exotic identities, capacity-backed invitation and arrival, independent routines/assignments/knowledge, personal archive and notebook projects, optional personal requests, owned keepsakes and bedroom shelves, companion fieldwork, independent wardrobe styles, progress-aware authored moments, optional personal invitations and descriptive resident friendships | Generated personal story arcs, broader recruitment, broader resident-to-resident relationships, generated group conversation and expanded consensual wardrobe configuration |
| Castle mystery | Versioned private sample foundation, four phased investigations, saved discoveries and explicit resident-specific sharing; public/diagnostic redaction | Final opening/first recruit, generated compatible discoveries and audited story correction |
| Specialized care | Ten optional compatible chambers, two authored cases, practical resolution, unconditional release, free specialist transfer and separate normal recruitment | More cases, interactive field encounters, specialist follow-up and illustrated chamber map |
| Resonance | Prototype passive rule tied to established mutual flirtation and furnishings; one-time development reward | Complete enduring-condition model and optional unlock catalogue, preserving independent essentials and personal agency |
| Exploration | Five persistent authored destinations, two one-time leads each, a three-encounter observatory with personal capability methods, optional recoverable complication, saved partial work, explicit approach/return and individual discoveries | Broader encounter catalogue, richer capability/risk evaluation and multiple parties |
| Neighbour connections | Four finite requests, exact protected deliveries, saved replies and a route unlocked by correspondence | Specialist contacts and richer voluntary agreements |
| Campaign saves | Separate solo sample slots, per-tab request scope, automatic schema migrations, request idempotency, restorable database/artwork ZIPs, readable JSON | Final opening campaign; co-op slots only after real agent control is implemented; correction tools for actual narrative/state errors |
| Gamemaster | Scripted dialogue plus reviewed OpenRouter NPC replies and result-scoped journal accounts and validated spell-form suggestions; server-side settings; scoped context; token usage; idempotent request recovery; authoritative rules remain separate | Full gamemaster, model capability preflight, validated content proposals and live provider verification |
| Real co-op | Solo saves never contain founder impersonations; no unsupported co-op creation | Authenticated character-scoped tools, proposals/consensus, readiness, reconnect handoffs and tests with actual Eris/Selene integrations |
| Hidden campaign facts | No invented castle truth or finalized first recruit exposed as canon | Private foundational lore storage, knowledge scopes and compatible discovery generation |
| Hosting | Python standard library, SQLite, local assets, Docker configuration and private-network instructions | Built-in authentication if needed; Docker runtime verification; automated backup scheduling if requested |

## Remaining implementation order

1. Extend the implemented reviewed NPC dialogue into a full gamemaster with validated content proposals, explicit model capability checks and live provider verification. Preserve credentials outside exports and keep generated prose separate from rules authority.
2. Extend the implemented independent resident records and capacity-backed invitation into validated generated candidates, while preserving established identity and individual preferences.
3. Extend the four validated spell forms and first cooperative ritual into a broader grammar, preserving personal knowledge, component properties, facilities and preparation constraints.
4. A complete character mathematics layer with understandable attributes and tested perk/affinity effects; preserve current acquired knowledge and accomplishment records during migration.
5. Dedicated real-agent authentication, private visible-state views, consensus and readiness, then separate co-op campaign creation and actual integration testing.
6. The final opening campaign, private castle truth and first-recruit content, once those foundations can enforce their access and continuity requirements.

These are implementation dependencies, not requests to reopen settled aesthetic or campaign preferences. The sample remains playable while the remaining systems are developed. No step authorizes proxy consent or treating an unavailable agent as ready.

## Verification at this checkpoint

247 Python tests pass, including migrations from schemas 1–21, rule validation, persistence, HTTP campaign isolation and a save-ZIP restore on a fresh server. Headless UI checks cover 24 views and the connected gameplay/form flows, including equipment preparation and a lost campaign-creation response. They do not verify real browser painting, layout, focus behavior, Docker execution or external-agent/model integration.

The user selected **Stonework and Spellcraft** as the title. Provider tests use controlled responses; they do not establish live account connectivity or response quality. The v0.23 development checkpoint expansion uses state schema 22, preserving the separate SQLite draft journal. Housing checks cover restoration, bed reservations, bedroom choices, absence, room access and persistent migration/reload.

Spellcraft verification covers exact costs and output, personal owners, property/quantity validation, pause/resume, cancellation/refunds, ritual cooperation, room controls, scoped dialogue context and persisted migration/reload. The two new room images were inspected directly; UI layout remains unverified because no local browser executable was available.

## Development checkpoint additions

Rainward survey and salvage each require three encounters. Taking the optional auxiliary lens creates a recoverable complication; no random death, timed loss or irreversible failure was added. Manual methods always remain available. Returning early retains work but does not mint rewards. Fast choices evaluate actual party knowledge and carried equipment.

The recruitment route requires a mutually accepted private room. Named arrival reservations cannot be overwritten by general bed planning. Tamsin arrives only on Advance and receives no automatic assignment, romance or Resonance. Her professional preservation notes are shared as agreed; private personal histories are not combined. The two-person ritual still has exactly the original participants, and its capacity benefit is scoped accordingly.

Tamsin’s optional scenes and clothing have dedicated state. Her flirtation can contribute to the existing Resonance rule, but it does not modify Mira’s relationship. NPC generation remains optional and reviewed; each resident has separate history and draft listings. Authoritative actions remain the only way to change resources, advancement or relationship developments.

New images were directly inspected and integrated as local WebP assets. Browser layout and Docker execution remain unverified. No live provider charges or external-agent actions were performed. The game still lacks full generative GM authority, co-op, complete character mathematics and final campaign content; those are not implied by the new sample systems.

## Bounded delegation

One open work-order agreement can reserve shared money and buy only the chosen components for the chosen finite batch. The maker keeps their normal primary assignment and personal work bonuses. Protected material stock is not consumed automatically; purchases never exceed the remaining held budget. Other work/absence pauses progress, and no second copy uses leftover work in the same phase. Explicit pause, resume, top-up and revoke controls preserve committed work. Finishing or revoking returns unspent money. Older orders migrate as manual plans.

This is a bounded first implementation of delegated budgets, not unrestricted NPC purchasing or a general task scheduler. The test package includes START_HERE.md with launch/upgrade instructions and focused user test routes. Browser visual QA, Docker and live integrations remain unverified.

## Teaching and finite spell routines

Professional teaching uses the teacher’s actual personal knowledge or trained rank. Learners retain normal advancement costs and interest restrictions. Both people commit primary work, with pauses on absence or competing assignments; new knowledge is not automatically shared to every character. Lessons and repeat casting are solo household agreements, not implementations of real-agent co-op consent.

Workroom notes exposes active and paused personal projects, lesson readiness and delegated budgets without creating a second source of simulation truth. Finite casting plans consume only unreserved inputs on explicit Advance, do not purchase materials, and stop at their agreed counts. Preparation removal pauses a plan until explicit resumption. Inputs are committed before production, preventing same-phase loops.

Browser visual layout, Docker and live model/agent integrations remain unverified. The new checks are rule/persistence tests and a headless controller playthrough; they do not imply visual QA. No new generated art was required for these functional controls.

## Personal requests and journal accounts

Two authored optional personal projects consume an explicitly chosen wallet and unreserved shared materials. The owner contributes two primary phases; competing work or absence pauses progress. Cancellation refunds unfinished work exactly once. Completed keepsakes belong to the resident, can be displayed in their current bedroom, and have no productive or relationship bonus. Character sheets distinguish these from shared inventory.

Optional journal generation uses only resolved results. Preview, source comparison, escaped display, acceptance, stale-revision rejection, persisted recovery and NPC/journal separation are implemented. Accepted accounts only append labeled journal prose and increment revision. Controlled provider responses were used in tests; this does not establish narrative fidelity from a live model. The connected controller exercises the new personal projects and account review/reload flow.

## Text-based furnishings and saved arrangements

The latest user direction replaces low-quality furniture overlays with a text panel listing furnishings and their effects. Room paintings remain atmosphere; selected main furnishings, floor textiles and wall displays are represented in the list. Installed artifacts and owner-displayed keepsakes are included, with conditional benefits stated. No generic furniture SVG or lantern overlay is rendered.

Six named arrangements per room remember only main furnishing and decorative slot choices. Loading does not consume resources or restore artifacts, consumables, bedroom assignments or personal possessions. Deletion forgets the preset without changing current furnishings. Schema 16→17 starts new slots empty and preserves existing choices. Rule checks cover bounded snapshots, invalid choices, closed rooms, migration, persistence and conditional effects. The connected controller covers selection, save/load/delete, escaped names, text-only presentation and reload. Browser painting remains unverified.

## Household moments

Eleven progress-gated scenes provide contextual dialogue, two resident-to-resident interactions and two follow-ups to individually established flirtation. Invitations wait indefinitely and support defer/restore; completed scenes remain readable. The household overview shows new conversations, assignments and paused personal work. Existing work is not reassigned by a scene. Shared history changes only descriptive friendship text, without numerical bonuses or assumed romance.

Rule tests cover eligibility, absence, indefinite deferral, personal context separation, non-rewarding completion, rereading while away, migration and duplicate-request recovery. The connected interface playthrough exercises defer/restore/join, both friendship scenes, a personal follow-up, resident-specific panels and reload. All 247 Python tests and the 24-view connected playthrough pass. These remain controlled rule/controller checks; no live model or browser painting verification is implied.

## Specialization and personal augmentation

Two advanced practices require relevant prior practice and a trained skill rank, consume existing earned advancement and preparation slots, and apply narrowly to research or artifact work. The shared contribution breakdown now supplies crafting duration estimates. Six saved preparation sets per person preserve names through retraining while rejecting unavailable practices.

Lamplit sight is the first authored voluntary augmentation example: personal understanding, explicit shared costs, protected materials, two primary work phases and one extra spell-preparation slot. It is recorded textually rather than changing portrait art. One-phase reversal waits for excess spell preparation to be put aside. Pauses, exact cancellation refunds, no duplicate stacking, owner-specific benefits and independent resident work are implemented. It does not claim a full transformation or affinity system.

All 247 Python tests and the connected 24-view playthrough pass. Checks include prerequisite rejection, individual prepared effects, unchanged unrelated outputs, invalid saved sets after retraining, migration, exact ritual commitment/refunds, presence, reversal capacity blocking and persistent request retries. The UI flow follows advanced training, set restoration, retraining invalidation, receiving a blessing, reload and reversal. Browser painting, Docker and live provider/agent integration remain unverified.

## Bounded spell-construction advice

Optional natural-language suggestions choose among four existing spell forms or return no fit. Structured output validation rejects unsupported identifiers, extra fields and malformed/oversized responses. The rules separately calculate and display mechanics and prerequisite status. This is a reviewed mapping aid, not an unlimited spell grammar. Generated explanatory prose can still be mistaken and is presented as such.

Using a suggestion populates an unsaved manual form; saving, testing and casting retain all existing server rules. Draft recovery is campaign/owner/purpose scoped and retries do not generate again. NPC/journal acceptance rejects spell suggestions. Context excludes unrelated private campaign data. State schema remains 19.

All 213 rule/server tests and the 24-view connected controller playthrough pass, including suggestion preview, escaping, retry/recovery, copying into the form and separate free design persistence. Controlled provider responses do not establish live model fidelity or account connectivity. Browser painting and Docker remain unverified.

## Summoning design and browser access review

`designs/SUMMONING_DESIGN.md` specifies the next summoning subsystem: stable adult identities before conversation, separate contact/visit/membership decisions, real bed reservations, visitor-versus-workforce selectors, costs and recovery, provider boundaries, and acceptance checks. It identifies the fixed character registry as an implementation prerequisite. This is a design only; no summoning controls or new residents have been added.

A real browser review was attempted on 4 October 2026. The local browser binary was unavailable, and cloud Chrome blocked navigation to the temporary local test server with `net::ERR_BLOCKED_BY_CLIENT`. No gameplay page rendered. The server was stopped; see `BROWSER_REVIEW_STATUS.md`. Visual usability remains unverified, and the attempt did not modify a player save or expose the game publicly.

## v0.21: identity and arrival groundwork

Implemented campaign-owned `people` records for the existing three adult sample characters. Live profile and starting-practice reads use these records; household membership and actual presence remain separate selectors. Runtime learning/contribution loops use household membership. This does not yet admit arbitrary new characters: authored projects, assignment offers and other individual systems still need generalization and centralized initialization.

Named `arrivalReservations` now own housing capacity holds. The previous pending-arrival record remains as a compatibility pointer for the existing Tamsin story. Migration preserves that invitation and all prior gameplay values. Arrival resolution rechecks accommodation and waits on missing reservations, unusable rooms, or insufficient capacity. Rooms & beds exposes named arrivals, blockers, cancellation and compatible room changes. Cancellation preserves identity and conversations and permits reinvitation.

Eight additional rule/persistence regressions cover identity isolation, migration and backup, capacity changes, missing/unusable accommodation, cancellation, repeat reservations and invalid/remote changes. The connected headless UI playthrough additionally cancels and repeats the invitation through rendered controls. No real-browser visual review or live model request was performed.

## v0.22: authored summoning is playable

The Open Threshold introduces Iona, an explicitly adult authored sample surveyor. Courteous passage research follows the concordant lesson; personally knowledgeable conductors prepare contact with exact material/crown escrow, two assigned phases, pause/resume and one-time cancellation refunds. The same identity survives closing, departure and return. This version makes no live provider call for summoning.

Visitors, household members and physically present people have distinct selectors. Named reservations validate actual accommodation; visitor occupancy does not grant work, money, romance or personal development access. Candidate and household membership decisions are recorded independently. Departure is explicit, waits for Advance, requires committed work to be resolved, and preserves identity and possessions. A later visit requires fresh membership decisions. Departure clears the discretionary allowance plan for this person, not their wallet.

A centralized new-character initializer creates each subsystem record once. Current workforce actions use household membership rather than the fixed authored catalogue. Original resident scenes remain identity-specific. A new member can craft, study, use equipment and spells, and receive explicit personal allocations. Spell proposal ownership supports the campaign registry; summoning conversation remains authored. No new generated NPC dialogue integration is claimed.

Fifteen new rule/service tests cover research gating, atomic costs, protected stock, pause/refund, immutable identity, capacity, visitors, both membership decision orders, cancellation, departure/return, learning/crafting, original story isolation, idempotent preparation, migration and fourth-character spell proposals. The connected 24-view headless playthrough follows research through contact, occupied rooms, membership screens, departure, reload and return. Real-browser painting/keyboard usability remains blocked by the previously recorded environment restriction.

Remaining: generated candidate review, more categories, a portrait and individual story content for Iona, a broader room catalogue, actual provider verification and co-op. The original campaign opening and canonical first recruit are still undecided.

Packaging correction: Docker now copies all top-level Python runtime modules, including resident moments, spell proposals and summoning. A clean staged runtime import/server smoke check verifies the copied application can serve health and campaign state. This is not a Docker engine/build verification.

## v0.23: Iona’s household life, possessions and gifts

Implemented Iona’s own three-phase atlas ambition, exact saved-cost cancellation/refund, personal Courteous passage mastery and a unique 2-point advancement award. Tamsin’s old repair-notebook resolver is explicitly restricted to Tamsin so Iona never inherits its principle or rewards. The existing personal-request framework now supports Iona’s optional map case with explicit funding source, safe cancellation, closing note and personal bedroom shelf.

Five authored moments include a Mira/Iona scene and a return-home conversation. Scenes remain voluntary, non-expiring and non-rewarding. Shared dialogue is written only to participants’ records; the shared scene has a descriptive friendship entry. Completed records and possessions survive departure. Departure now checks funded professional and personal work as well as earlier teaching, spells, tools and delegated commitments.

An explicit gift action buys a resident’s already offered personal interest from shared funds while preserving their wallet and the treasury floor. Ownership is unique across the purchase/gift routes. Added Iona’s travelling tea tin. No numerical relationship or work benefit is attached.

A generated, inspected ink-and-gouache-style portrait ships as `static/assets/iona.png` and participates in illustration correction/rollback. Source prompt and provenance: `docs/IONA_ART.md`. This is a static bundled asset; the app makes no image-generation requests.

Eleven additional rule tests cover unknown/visiting eligibility, protected materials, individual work phases and rewards, exact refunds including later catalogue changes, departure commitments, personal-wallet refunds, preserved keepsakes/scenes, shared-scene scope, schema migration and gifts. The extended connected playthrough earns funds through ordinary commissions, completes the atlas and case, joins scenes, displays the keepsake, gives the tea tin, then departs and returns. Browser visual verification remains blocked; no Docker-engine verification or live provider test is claimed.

Final staged-runtime check: all top-level application modules plus static assets start independently and serve version 0.23 health, schema 22 state, the frontend and Iona’s image with its PNG content type. No source files or browser storage outside the staged package are needed.

## v0.24: adult NPC identities, exotic summoning and portrait revision
Mira is 22, Tamsin 25, and Iona 23 with demon ancestry. Five new local PNGs cover their base portraits and both shawl variants. UI age labels and optional dialogue context use campaign-owned identity fields. NPC admission validates adult ages 18–25; summoned profiles additionally require an approved exotic ancestry. The authored ancestry set is extensible through reviewed code changes. Diversity and individual beautiful/cute/sexy adult appeal are standing design requirements in designs/SUMMONING_DESIGN.md; they are editorial criteria, not a numeric attractiveness score.

Schema 23 migrates old NPC identities and records previous identity fields. Active character portrait overrides move into artwork history, allowing the revised defaults to appear while preserving uploaded files and rollback. Progression, membership and time are retained. Original generated portraits and prompts are bundled; no external image service is needed at runtime.

Validation: 250 Python tests pass, including age/ancestry gates, profile/context consistency and migration idempotence. JavaScript syntax passes. Actual browser visual review remains blocked as documented in BROWSER_REVIEW_STATUS.md.

The connected 24-view headless UI regression also passes after updating portrait expectations. This is functional verification, not rendered-browser visual QA.

Portrait follow-up: Iona now uses iona-v3.png, a more sensual revision with fitted clothing, open collarbones and a knowing expression. Her age, ancestry and gameplay state are unchanged. The previous portrait remains bundled.

## v0.25: Iona’s personal conversations and remembered visits
The Summoning page now offers four authored personal topics: river-town life, surveying, quiet company and welcomed playful flirtation. They work during visits, residency and agreed departure, require both people home, save only to her own conversation, and never award resources or advance time. Free-text lines use the same history. Her dialogue remains readable while away or the contact is closed. A chronological crossing history shows previous visits and departures.

Optional provider drafts now support Iona, using her campaign age/ancestry, residency, own introduction, work and conversation history. Other residents’ private conversations are excluded. Draft recovery routes back to Summoning; SQLite revision guards and idempotent generation/acceptance remain in force. No schema change is required: existing persistent conversations and crossing records are reused. The authored summoning fixture remains the only candidate; generated candidate review is still future work.

Validation: 254 Python tests, including personal-history isolation, no-cost authored interactions, absence/invalid-topic rejection, provider retries and acceptance/reload. Provider tests use a controlled response; live provider connectivity is not claimed.

## v0.26: three authored exotic contacts
Aurelia, 24, angel lantern conservator, and Neris, 21, water elemental glassworker, join the authored contact catalogue. Aurelia starts with Gentle refraction and Patient scholarship; Neris starts with Water guidance and Methodical assembly. Each has a distinct focus, ambition, introduction, room preference, three personal conversation topics and an approved bundled portrait. Aurelia uses the user-requested warm-tan revision. Their appearance descriptions also inform reviewed dialogue context.

Summoning is keyed by durable candidate ID. Duplicate enduring contacts are rejected. A conductor can have one unfinished preparation; separate conductors each contribute one own phase to their respective contact. Cancelled preparations refund exactly once. Existing Iona records without candidateId resolve through the backward-compatible Iona default, without a migration or new costs. Each contact has its own topics, speakers, visits, separate membership decisions, departure blockers and history. The selected contact controls dialogue input, draft recovery and navigation from room/household cards; only one active conversation form is rendered.

The five-person household path supports all three summoned characters beside founder and Mira, with private-room and shared-bed capacity checks. Existing player choices may leave no private room for Aurelia; the UI explains that her invitation can wait. Joining never displaces another resident. The new characters use ordinary independent work/development rules. Iona retains her own atlas and scenes; those are not copied to other identities.

Validation: 263 Python tests; full 24-view connected UI regression; focused three-contact UI regression covering individual generated draft routing/acceptance, five-person household views, unique input IDs and retained conversations after departure. All pass. Generated dialogue is tested with controlled provider responses; no live provider or actual rendered-browser layout test is claimed. The authored expansion is complete; generated candidate proposals, new personal project storylines and new wardrobe variants remain future work.

## v0.27: Aurelia and Neris at home
The two companions now have distinct professional studies, each costing explicit shared crowns and unreserved materials, taking three own primary phases, earning 2 advancement once and recording a principle personally and in the shared archive. Aurelia learns Luminous copying; Neris learns Gentle refraction. This opens existing recipes without granting free artifacts or another resident’s mastery. Funding, pause/resume, exact saved-cost cancellation and departure blocking are covered.

Two new evening portraits and two landscape illustrations are bundled. Wardrobe choices are limited to the two actually illustrated ensembles per person, with human-readable component lists and up to eight named presets. The artwork shown on character/room/household cards follows saved clothing. Optional dialogue context receives that clothing. New resident-life pages provide direct project, wardrobe and invitation access from occupied rooms and character/contact pages. A non-interrupting notice lists waiting household invitations.

Nine authored scenes include two settling conversations, two illustrated post-project invitations, three shared scenes and two return greetings. Three shared scenes produce descriptive friendship records, with no affection score. Deferral is non-expiring. Joined scenes save prose only to participants’ histories. A completed illustrated moment retains its selected image; changing clothes later does not rewrite the remembered scene. The current evening portrait is used when its outfit was worn for that moment.

Schema 24 initializes offered project/wardrobe records for existing Aurelia/Neris identities and adds new moments with setdefault. Existing finances, ongoing work, identity, membership and histories survive. New arrivals initialize these records once. 273 Python tests pass; the full existing UI playthrough and the expanded new-cast UI playthrough pass. The latter covers funding, completion, clothing, saved presets, illustrated invitations, room shortcuts, reload and departure. JavaScript syntax passes. Browser layout, Docker runtime and live provider verification remain unverified.

Full-design coverage is still estimated at 40–50%, with 70–80% of the core solo loop represented; see DESIGN_PROGRESS.md. This is scope coverage, not an estimate of development hours remaining.

## v0.28: reviewed candidate plans and admission
Saved structured candidate proposals now pass strict mechanical validation and explicit content review before approval as fixed contact plans. Reviewed plans use the existing paid contact, visit, membership, personal development, work, departure and return lifecycle. Visit-only preferences cannot be overridden. Three defined starting packages bound competence; no arbitrary abilities or free resources are accepted. Portrait import/review remains separate, with an explicit placeholder.

Rechecking unchanged proposals against current state uses no provider call. Generation and approval are idempotent; request provenance survives recheck. Public cast facts are scoped separately from private dialogue. Generated identities are escaped throughout older generic screens. The real HTTP review route and draft-purpose filters are tested with a controlled provider response. Schema 25 adds an empty plan catalogue to old saves without altering existing work, money or people.

286 Python tests pass. The full existing connected UI playthrough, companion-life UI suite and new candidate-review UI suite pass, including malicious-markup names, checked approval, recheck, paid preparation, membership, scoped dialogue, portrait review and departure/reload. JavaScript syntax passes. Live model/provider verification and actual browser layout remain unverified. Full details: designs/CANDIDATE_REVIEW.md.

## v0.29: individual builds and persistent castle evidence

Character sheets now offer Insight, Dexterity and Resolve; Light, Growth and Hearth affinities; and six earned specialization perks. Advancement costs and own learning phases are explicit. Work breakdowns and personal spell results include the real bonuses. Cancellation releases reserved points, and retraining checks the resulting spell capacity before changing a build.

Castle history now provides a versioned sample mystery with four phased investigations, saved evidence, one-time advancement and explicit resident-specific sharing. Undiscovered lore is excluded from ordinary public responses and diagnostic JSON. Complete restoration backups retain it and can contain spoilers. This is labelled prototype history, not the finalized opening or first recruit.

Schemas 26–27 preserve existing progress. 306 Python tests and five connected headless UI suites pass. Live providers, rendered-browser layout, Docker execution and real external agents remain unverified. The full design is still incomplete; see the requirement checklist in docs/DESIGN_PROGRESS.md and the detailed designs in docs/designs/CHARACTER_BUILDS.md and docs/designs/CASTLE_MYSTERY.md (paths relative to the project root).

## v0.30: specialized care, release and estate capacity

The main solo castle can now be restored to 25 non-founder places plus the founder. An optional 25-place annex requires separately funded access/services and separately fitted rooms. Named arrivals and regional ceilings are enforced. Private-room preferences now apply to every character's bedroom move. New rooms use explicitly labelled representative illustrations with independent furnishings and correction histories. Reviewed candidate plan capacity is fifty.

Schemas 28–29 preserve prior saves. See `docs/designs/CONTAINMENT.md`, `docs/designs/ESTATE_CAPACITY.md` and `docs/CONTAINMENT_ART.md` (paths from the project root). Real browser layout, Docker, live providers and actual Eris/Selene integration remain unverified; the whole design is not complete.

v0.30 verification: **327 Python tests and seven connected headless UI suites pass**, including the full 50-resident capacity fixture, containment release/recruitment and annex construction. JavaScript syntax passes. No live-provider, rendered-browser, Docker-runtime or real-agent success is claimed.

v0.31 verification: **350 Python tests and nine connected headless UI suites pass.** Coverage includes real HTTP draft/review routes, offline generation, route separation, golem funding and awakening, retries, migration, personal stories, refunds, membership and persistence. JavaScript syntax passes. These are not rendered-browser, live-provider, Docker-runtime or real-agent acceptance tests; those remain unverified.

## v0.32: ancestry expansion and illustrated local introductions

Added common bovinefolk, orcs and wolfkin, plus exotic oni. Four named adult characters now have individual bundled portraits: Maren (24), Brakka (25), Fenna (22) and Kaede (24). Open **Local introductions** for phased meetings and a threshold letter, unlocked by actual restoration, returned discoveries or passage knowledge. Ordinary introductions still require separate visits and membership; Kaede uses the normal exotic ritual.

Three optional earned ancestry perks express controlled strength, sustained story work and keen observation. They use existing advancement and training requirements and display bounded effects. Two new personal-story chapters unlock from completed work and scenes actually shared, retaining references to earlier accomplishments. Neither previews nor deferred invitations count as shared history.

Schema 31 preserves prior campaigns. See `docs/designs/LOCAL_CAST_AND_ANCESTRY_TRAINING.md` for exact costs, effects, lead prerequisites and limits; `docs/LOCAL_CAST_ART.md` records built-in image prompts and the four portrait paths. Broader procedural encounters, semantic prose validation, full co-op and actual agent integration remain unfinished.

v0.32 verification: **358 Python tests and ten connected headless UI suites pass.** JavaScript syntax passes. The new local-introduction suite covers portraits, pause/resume, ordinary correspondence, two-sided membership, ancestry training display, shared-history chapter unlocking and persistent continuity. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.

