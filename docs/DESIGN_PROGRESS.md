## v0.80 — Opening campaign review

Connected Chapters 1–4 reviewed; preservation-study guidance repaired, Chapter 3 disabled reasons restored, and completed chapter summaries compacted. See `docs/RELEASE_V080.md` and `docs/CAMPAIGN_REVIEW_V080.md`. Preserve the complete existing `data/` directory. Rendered browser review remains unresolved.

## v0.79 — Companion overview portraits and splash layout

42 new room-specific, full-body portraits; equal overview columns; viewport-filling landscape. Kaede now has a fit, busty hourglass figure with subtle muscle definition. See `docs/RELEASE_V079.md`. Preserve the complete `data/` directory when upgrading.

# Current release — v0.78

Chapter 4, Sabine’s dungeon specialty and additional resident content, and complete authored expedition image coverage are implemented. See [KEEPING_THE_HEARTH.md](KEEPING_THE_HEARTH.md), [RELEASE_V078.md](RELEASE_V078.md), [ART_V078.json](ART_V078.json) and [VERIFICATION_V078.json](VERIFICATION_V078.json). Earlier entries below are historical.

---

# Current release — v0.77

Three connected chapters are implemented. See [ROOM_TO_GROW.md](ROOM_TO_GROW.md) for development planning and chapter continuity, [RELEASE_V077.md](RELEASE_V077.md) for changes, and [VERIFICATION_V077.json](VERIFICATION_V077.json) for current validation. All earlier entries below are historical checkpoints.

---

# Current checkpoint — 0.76-dev (unreleased)

The playable opening chapter is documented in [FIRST_HEARTH.md](FIRST_HEARTH.md). Chapter two's three undertakings, six designs, shared work and compatibility rules are documented in [THE_HOUSE_TAKES_SHAPE.md](THE_HOUSE_TAKES_SHAPE.md). These use the established prototype history; its private lore packet is preserved. Both chapters, resident-led headquarters work and the pending v0.74 art/logo are included. The historical coverage records below retain the state of their original versions.

---

# Current checkpoint — v0.41

Read [SOLO_PHASES_V041.md](SOLO_PHASES_V041.md) for the phase task board, persistent new-phase notifications, voluntary resident work, generic field companions and solo housewarming. [SOLO_INTERFACE_V040.md](SOLO_INTERFACE_V040.md) covers the separate fresh start and navigation restructure. The older coverage matrix below remains historical. Co-op is deferred.

# Current checkpoint — v0.39

The detailed matrix below is historical through v0.32. For current public-pack integration and verification, read [CONTENT_INTEGRATION_V039.md](CONTENT_INTEGRATION_V039.md) and [PUBLIC_RULES_IMPLEMENTATION.md](PUBLIC_RULES_IMPLEMENTATION.md). All sixteen public packs have routes; the original game design still has separate co-op, authenticated-agent, live-provider, visual-browser and deployment acceptance work.

# Design coverage — v0.38 development checkpoint

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


**The full design is not complete.** The earlier 40–50% estimate was a broad engineering judgment, not a measured completion percentage. The checklist below replaces percentage-based reporting until every requirement has an agreed acceptance test. It is not weighted by effort; counting rows would give a misleading percentage.

The v0.1 specification is the baseline, with later user decisions taking precedence: title **Stonework and Spellcraft**; NPC adults aged 18–25; exotic summoned ancestries; diverse, attractive, sensual non-explicit characters; warm handmade archive-workshop art; furnishings represented by readable lists and effects rather than crude overlays. Co-op and real agents remain in scope.

**Implemented** means a bounded rules path exists and has automated checks, not that its content breadth, art, balance or live deployment has received final acceptance. **Partial** means material behavior/content is still missing. **Missing** means no playable path. **Unverified** means implementation or artifacts exist but the required real integration check has not passed.

| Spec | Requirement | Status | Evidence or remaining acceptance work |
|---|---|---|---|
| 1 | Self-hosted webapp, persistent solo rules | Implemented | Python/SQLite application, real local HTTP tests and reopen tests |
| 1 | Warm household focus, no routine attention decay | Implemented | Phase rules and optional non-expiring scenes |
| 1 | Fanservice integrated with distinct adult characters | Partial | Portraits, ensembles and authored scenes exist; breadth and visual consistency need continued review |
| 1 | Restore → research/craft → explore → enrich home loop | Implemented | Connected headless playthrough; balance remains provisional |
| 2 | Solo without imitated Eris/Selene | Implemented | Solo campaigns reject co-op creation; neither agent is impersonated |
| 2 | Separate genuine co-op campaigns | Missing | Persistent founder ownership and actor-aware rules needed |
| 2 | Agent-chosen ancestry/background and individual founding assets | Missing | Requires actual Eris/Selene onboarding, not generated stand-ins |
| 3 | Bounded room-based estate and restoration | Partial | Small estate; larger room catalogue and adjacency synergies unfinished |
| 3 | 25 main residents plus founders | Partial | Solo rules support 25 residents + 1 founder; co-op founders and complete estate artwork remain unfinished |
| 3 | Optional 25-place annex | Implemented | Phased access/services, separately fitted rooms, named reservations and independent decoration; representative artwork |
| 3 | Approximately ten specialized containment places | Implemented | Ten optional one-person chambers, two ward types, independent of bedrooms |
| 3 | Proper Living Wing milestone at phase end | Implemented | Facilities and services checked without requiring celebration |
| 3 | Mystery-linked final first recruit | Missing | Mira remains a labelled sample, not a finalized opening recruit |
| 3 | Dependable sanctuary | Implemented | No random raids, theft or home-destruction loop |
| 4 | Three phases, explicit Advance, no offline catch-up | Implemented | Rules/reload tests |
| 4 | Individual primary work budgets and persistent long jobs | Implemented | Work, learning, rituals, investigations and projects |
| 4 | Co-op readiness with human-only Advance | Missing | Actual authenticated founder readiness and recovery needed |
| 4 | No repeated-click rewards | Implemented | Request idempotency and stable accomplishment/discovery keys |
| 4 | Optional non-expiring invitations | Implemented | Deferral, restoration and remembered scenes |
| 5 | Equal-founder consensus and revised-proposal invalidation | Missing | No co-op governance path |
| 5 | Delegated routine spending | Partial | Solo standing work orders, reserves and budgets; multi-founder approvals absent |
| 5 | Disagreement independent of readiness; no proxy on disconnection | Missing | Protocol and actual agent recovery tests needed |
| 6 | Attributes, skills, affinities and earned perks | Implemented | v0.29: 3 attributes, 3 affinities, 6 perks plus existing skills/practices |
| 6 | Shared classless advancement rules | Implemented | Same individual records and costs for founder/authored/generated residents |
| 6 | Knowledge, preparation and actual use kept separate | Implemented | Principles, practices, spells and focus loadouts |
| 6 | Accomplishment-based advancement and teaching | Implemented | One-time awards and coordinated personal lessons |
| 6 | Resident interests shape collaborative build choices | Partial | Offered training/professional paths; richer negotiation and evolving preferences absent |
| 6 | Castle-only changes and simple retraining | Implemented | Reserved points, one-phase reset and post-reset capacity checks |
| 6 | Quest-resolved disadvantages and continued ambitions | Partial | Professional projects exist; disadvantage mechanics and ongoing generated arcs absent |
| 6 | Voluntary reversible augmentation | Partial | Lamplit sight ritual/reversal; broader catalogue and actual matching artwork unfinished |
| 7 | Bounded natural-language spell proposals | Partial | Strict four-form proposals; broader grammar and exceptional effects unfinished |
| 7 | Shared archive, individual mastery | Implemented | Personal study and teaching; private conversations not copied to archive |
| 7 | Property-based component substitution | Implemented | Material validation for recipes, focus and spells |
| 7 | Signature items and separate prepared configurations | Implemented | Inscriptions, capacity, personal focus and saved preparation sets |
| 7 | Persistent summoned identities before contact | Implemented | Authored and reviewed candidate plans, bounded starting packages |
| 7 | Separate contact, visit and mutual membership | Implemented | Stable identity, bed reservations, visit-only preferences, departure and return |
| 8 | Coherent generated backgrounds and personal development | Partial | Reviewed identity/ambition; generated story and relationship evolution absent |
| 8 | Descriptive relationships, multiple consensual relationships | Partial | Authored personal/friendship scenes; general relationship simulation unfinished |
| 8 | Continued personal ambitions, secondary interests, autonomous downtime | Partial | Authored projects and routines; generalized choice model unfinished |
| 8 | Personal funds, belongings, requested purchases | Implemented | Allowances, explicit gifts, keepsakes and funded requests |
| 8 | Residents personalize rooms and choose component-based clothes | Partial | Supported styles and room arrangements; richer resident initiative/wardrobe variants absent |
| 8 | Manageable opportunity selection for large households | Partial | Invitation notice exists; full-capacity usability untested |
| 9 | Persistent output choices, reserves, forecast | Implemented | Garden, stock plans, non-stacking automation and work orders |
| 9 | Upgrades, staffing and understandable room synergies | Partial | Facility/artifact effects exist; adjacency-dependent placement decisions unfinished |
| 9 | Treasury, participant wealth shares and allowances | Implemented | Personal/shared accounts and standing allocations |
| 9 | Auto-convert mundane treasure, preserve significant objects | Implemented | Authored expedition reward rules and protected possessions |
| 10 | Persistent illustrated region and linked leads | Partial | Five authored routes; geography/content breadth unfinished |
| 10 | Separate parties led independently by each founder | Missing | Existing expedition state supports a single founder-led party |
| 10 | Consequential multi-step encounters with capability checks | Partial | Rainward path; broader risk/complication vocabulary unfinished |
| 10 | Recoverable setbacks and non-expiring outside contacts | Implemented | Authored encounter/neighbor paths; no routine permadeath |
| 10 | Plausible remote participation and private agent activity summaries | Missing | No communication-link system or actual agent scopes |
| 11 | Hostile/threatening occupants and compatible containment | Partial | Two authored report/escort cases and compatible chambers; field encounters and further cases unfinished |
| 11 | Separate threat resolution, release, recruitment and romance | Implemented | Practical care, unconditional release, free specialist transfer, separate normal visits and two-sided membership |
| 12 | Passive response to lasting voluntary sensual atmosphere | Partial | Authored flirtation contribution model; whole-cast enduring-condition model still narrow |
| 12 | Optional Resonance possibilities without essential dependence | Partial | Hearth glow; broader optional unlocks unfinished |
| 12 | Fixed private foundation and compatible discoveries | Implemented | v0.29 saved versioned sample history and four investigations |
| 12 | Undiscovered truth absent from public state/model contexts | Implemented | Real HTTP redaction tests; explicit person-specific evidence sharing |
| 12 | Final campaign mystery and recruit continuity | Missing | Sample demonstration is not final campaign canon |
| 13 | Illustrated plan, direct room entry, portraits and phase presentation | Implemented | Existing UI/assets; actual layout acceptance still unverified |
| 13 | Furnishing slots and readable bonuses | Implemented | User-requested text lists supersede low-quality overlays |
| 13 | Ensembles, configurable components and saved variants | Partial | Limited actually illustrated variants; full compatible wardrobe system unfinished |
| 13 | Character-dominant conversations and group scenes | Partial | Authored/UI paths; broader groups and live visual review needed |
| 13 | Correction review, retained accepted art and rollback | Implemented | Imported revisions, history, unchanged game mechanics |
| 13 | In-game image generation/correction provider | Missing | External generation/import exists; callable in-game image service absent |
| 14 | Rules are authoritative over generated text | Implemented | Durable reviewed dialogue, spell and candidate workflows |
| 14 | General validated gamemaster event proposals | Missing | No general event schema or consistent narrative correction pipeline |
| 14 | Dedicated authenticated Eris/Selene tools | Missing | Must share rules, constrain actors and avoid omniscient views |
| 14 | Agent-specific handoffs and fictional-memory provenance | Missing | Actual player scopes, outstanding decisions and reconnection records needed |
| 14 | Provider configuration, private keys, usage and recovery | Partial | Text configuration/durable requests work with fixtures; capability preflight and live verification missing |
| 15 | Separate saves, migrations and recoverable complete backups | Implemented | SQLite snapshots, campaign slots and archive reopening tests |
| 15 | Narrative/identity correction with audit history | Partial | Artwork correction exists; authoritative narrative correction not implemented |
| 16 | Visual slice acceptance in a real browser | Unverified | Prior cloud browser blocked local page; headless tests do not prove layout/accessibility |
| 16 | Real external-agent integration acceptance | Unverified | No real agents connected; cannot infer success from fixtures |
| 17 | Provisional balance represented as understandable data | Partial | Costs/effects documented; long-run balance and large-household tuning unfinished |
| Hosting | Container execution and private deployment acceptance | Unverified | Configuration exists; no successful Docker runtime check recorded |

## Completed in this expansion

- Individual attributes, affinities and six perk paths, tied to effective work/casting/preparation and the existing advancement budget.
- Safe retraining across the new investments, including explicit spell-capacity handling.
- Versioned sample castle history, four persistent investigations, first-discovery awards and explicit evidence sharing.
- Hidden lore removed from ordinary state, action/conflict responses, NPC contexts and diagnostic JSON; retained in complete restoration backups.
- Schemas 26 and 27 preserve prior progress. **306 Python tests and five connected headless UI suites pass.** Real browser layout, live providers, Docker execution and real agents remain unverified.

## Dependency order for remaining development

1. Actor-aware campaign authority and authenticated real-agent API, then genuinely separate co-op onboarding, decisions/readiness and handoffs. Do not bolt proxy agents onto the solo save.
2. Independent expedition parties and capability-based encounter expansion on those actor scopes.
3. Separate containment capacity and a voluntary release/recruitment lifecycle; then main-castle and optional annex scale.
4. Broader validated GM content/correction schemas, generated personal arcs and private/public context tests.
5. Richer Resonance conditions, clothing/component variants, room synergies and final campaign opening/history content.
6. Real integration, rendered-browser/accessibility, deployment and long-run balance acceptance. Automated fixtures cannot close these gates.

No finite set of authored stories constitutes all future content in an open-ended game. Completion means implementing and validating every promised system and a coherent launch catalogue, not generating an unlimited number of NPCs. The current prototype does not yet meet that bar.


## v0.30 additions and limits

Specialized chambers and two authored care/release paths now work through the normal persistent identity and later household lifecycle. Two new adult portraits are bundled. Ordinary release needs no crowns or bedroom; safe specialist transfer is available without recruitment and refunds unfinished care. Transferred cases have no invented automatic return storyline.

Solo housing now supports the functional 25 + 25 resident ceiling plus the scholar. The annex is optional and separately serviced/fitted. Generic private-room protection replaces an old Tamsin-only move check. New rooms retain separate state while explicitly reusing representative room artwork; a complete estate floor plan and distinct room paintings remain unfinished. Candidate plan capacity is now fifty.

The scale fixture reaches 50 residents plus the founder, checks regional ceilings and another arrival rejection, and preserves separate containment capacity. Co-op is not inferred from this solo-scale test. The earlier dependency list's containment/capacity step now concerns broader encounter content, specialist follow-up and visual completion rather than a missing baseline lifecycle.


v0.30 verification: **327 Python tests and seven connected headless UI suites pass**, including the full 50-resident capacity fixture, containment release/recruitment and annex construction. JavaScript syntax passes. No live-provider, rendered-browser, Docker-runtime or real-agent success is claimed.


## v0.31 additions and limits

Curated generation now combines versioned compatible ancestries, backgrounds, temperaments, appearances and ambition seeds, with weighted variety, durable offline/model drafts and bounded starting packages. Common recruitment (including three distinct elven ancestries and catfolk), exotic summoning (including kitsune, dryads and nymphs), and constructed adult golem awakening use different enforced entry paths. Seraph replaces Angel without changing Aurelia's accepted appearance. Five golem body materials, prerequisite knowledge, six assigned phases, refunds before awakening and a capacity check at awakening are implemented.

Reviewed personal stories now serve authored and generated household members through four bounded packages, exact funding, independent phased work, pause/cancel, once-only awards and optional non-expiring follow-ups. Prompts include owner-scoped completed stories and public/shared evidence. This advances the generated-personal-arcs part of the checklist; it does not complete the general gamemaster, co-op, authenticated agents, arbitrary expedition creation or semantic prose validation.

New identities still need reviewed portrait imports. Compatibility and age/package checks are mechanical; human review checks whether prose actually expresses the selected style, background and preferences. Offline story variety is finite. See the new ancestry/arrival and personal-story design documents for exact scope.


v0.31 verification: **350 Python tests and nine connected headless UI suites pass.** Coverage includes real HTTP draft/review routes, offline generation, route separation, golem funding and awakening, retries, migration, personal stories, refunds, membership and persistence. JavaScript syntax passes. These are not rendered-browser, live-provider, Docker-runtime or real-agent acceptance tests; those remain unverified.


## v0.32: ancestry expansion and illustrated local introductions

Added common bovinefolk, orcs and wolfkin, plus exotic oni. Four named adult characters now have individual bundled portraits: Maren (24), Brakka (25), Fenna (22) and Kaede (24). Open **Local introductions** for phased meetings and a threshold letter, unlocked by actual restoration, returned discoveries or passage knowledge. Ordinary introductions still require separate visits and membership; Kaede uses the normal exotic ritual.

Three optional earned ancestry perks express controlled strength, sustained story work and keen observation. They use existing advancement and training requirements and display bounded effects. Two new personal-story chapters unlock from completed work and scenes actually shared, retaining references to earlier accomplishments. Neither previews nor deferred invitations count as shared history.

Schema 31 preserves prior campaigns. See `docs/designs/LOCAL_CAST_AND_ANCESTRY_TRAINING.md` for exact costs, effects, lead prerequisites and limits; `docs/LOCAL_CAST_ART.md` records built-in image prompts and the four portrait paths. Broader procedural encounters, semantic prose validation, full co-op and actual agent integration remain unfinished.


v0.32 verification: **358 Python tests and ten connected headless UI suites pass.** JavaScript syntax passes. The new local-introduction suite covers portraits, pause/resume, ordinary correspondence, two-sided membership, ancestry training display, shared-history chapter unlocking and persistent continuity. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.
