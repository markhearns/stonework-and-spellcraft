# Prototype decisions

## Confirmed requirements carried into this build

- Self-hosted webapp with source and assets available for the user's server.
- Readable variables with concrete meanings and units.
- Direct room selection, eye-level illustrated interiors, fixed decoration slots, persistent visual identity, and named ensembles with configurable components.
- Morning, afternoon and evening; explicit advancement only; no real-world/offline production.
- Optional non-expiring invitations; free conversations and decoration; descriptive relationships.
- Resonance is linked to the adult residents' ecchi, lewd and erotic expression, sustained sensual atmosphere, and significant voluntary intimate developments. It is not generic happiness.
- State/rules authority remains distinct from generated narration and artwork.

## Provisional, reviewable choices

The first build demonstrates the visual milestone with three sample rooms and one adult archivist, Mira. Neither the castle's secret history nor the first campaign recruit has been invented. Solo is the only implemented mode, without substitutes for absent Eris or Selene agents.

For a visible Resonance demonstration, one voluntary playful invitation establishes a persistent flirtatious atmosphere (+2 once). With that atmosphere and a velvet settee in the common room, each Advance adds 1 point. Six points enable a violet glow overlay. Warm furnishings alone do not create erotic Resonance. This small rule demonstrates sustained conditions and duplicate prevention; it is not the final model for erotic household expression. Clothing variants award nothing, and essential facilities do not depend on this resource.

Research is a small functional example with 20 crowns and 3 phases, not the final character-action or component-magic system. Rooms are already restored to make the art and interaction easy to evaluate. Functional construction, budgets, research specialties and capacities remain future implementation work.

The implementation uses Python's standard library and SQLite to minimize self-hosting friction. It requires a server process, not just static file hosting. Vanilla JavaScript and CSS serve the frontend with local artwork and fonts. There are no remote model calls.

## Asset behavior

The room background is immutable unless the user accepts an imported correction. A furniture overlay changes only its fixed slot. These small furniture overlays are intentionally simple vector prototypes, unlike the painted backgrounds. The two portrait assets depict the same adult character and differ by a supported outer garment. More garment combinations need additional art rather than being implied by unsupported selectors.

Room phase lighting is a display filter; it does not generate a fresh picture. The castle plan is a diagram with room thumbnails, selectable areas, and an occupant marker. Unavailable wings do not expose hidden content.

Correction requests are saved briefs. Imported replacement artwork is previewed, uploaded, and accepted separately; acceptance stores the prior path for rollback. There is no live generation integration in this version.

## Next implementation boundaries

- Replace the private-prototype HTTP serving layer as appropriate for a deployed multi-user system; add access control and distinct campaign identity.
- Define authoritative action budgets, character statistics, construction and the component grammar for magic before integrating a gamemaster.
- Connect provider services only through explicit capability-checked server adapters.
- Implement real external-agent tools and co-op consensus/readiness on separate co-op saves. No co-op UI switch before those rules exist.
- Broaden visual variants while maintaining the same references and versioned acceptance workflow.


## 0.2 expansion (supersedes the earlier implementation limits above)

One actual restoration project and one component-governed artifact recipe are now implemented, plus assignment-based research contributions and a productive conservatory. Costs, 3 restoration work phases, 2 crafting work phases, material properties, prices, and garden outputs are explicitly provisional sample data. No new foundational lore, first recruit, co-op authority or complete magic system is established.

The scholar chooses one assignment per phase. Starting research/restoration/crafting switches that assignment, clearly stated in the UI; other projects pause. Mira has offered archives and garden work in the sample. Her research assistance obeys the same one-contribution budget; a completed research project does not silently switch her to another job.

The garden begins unavailable and cannot be entered or staffed before restoration. Only a staffed, previously restored garden produces, and production happens exclusively on Advance. Designated surplus is sold without consuming saved materials or personal items. Explicit individual material sales prevent purchases from unnecessarily locking up funds.

The warming-lantern recipe is validated by material properties and a known principle. It consumes components once, needs two assigned work phases, and produces a retained artifact. Its current visible use is a warm common-room glow; no unimplemented expedition advantage is claimed.

Save schema 2 adds these systems without deleting existing choices. Startup snapshots schema 1 databases before migration. Live AI, co-op and external-agent connections remain unimplemented. Browser visual verification and Docker execution remain unverified in the creation environment.


## 0.3 expansion

A single authored solo expedition now demonstrates departure, one meaningful on-site choice, phase-based work, early return and arrival. The destination and two leads are sample geography/content, not newly revealed canonical castle lore. There is no combat, injury system, party builder, AI narration or remote agent control in this slice.

Outward and return travel each cost one phase. On-site survey work takes two phases, or one with an owned warming lantern packed beforehand; accessible salvage takes one phase. Ordinary scholarly competence is sufficient, and there are no arbitrary failure rolls. Survey brings water guidance; salvage brings two fireglass and eight crowns. Each lead can be resolved once; a later trip can pursue the other one. Leads do not expire, and aborting unfinished work grants no reward.

The scholar's expedition blocks their castle work and in-person conversations without stopping resident production. No magical communication link is assumed. Household inspection remains available. Crafting knowledge is now checked against personal known principles, while shared archive knowledge is tracked separately.

Water guidance unlocks a self-watering charm (porous clay plus any binding material; two work phases). Installed in a restored conservatory, it improves staffed outputs from one ivy/four crowns to two ivy/six crowns. This makes a discovery practically useful at home. It does not add unattended production or upkeep.

All six character/room illustrations have been simplified and darkened in response to the user's explicit criticism of opulence and brightness. These are revised bundled defaults; user-imported accepted overrides remain intact.


## 0.4 expansion — A Proper Living Wing

The first household milestone now has functional requirements and persistent completion. Existing sample beds/common room qualify; the player restores kitchen/dining, washroom and service wards, and fits a crafted hearth kettle for warm water. The sample budgets are 18/18/10 crowns and two scholar work phases per facility. No new accommodation capacity or automatic resident recruitment is implied. Service spaces are working ledger panels within the existing wing, without new room illustrations.

A second sample expedition, Reedbank waystation, follows the returned waterworks survey. Its two one-time leads teach gentle preservation or recover ordinary supplies (3 binding thread, 2 porous clay, 12 crowns). This is modest provisional geography, not a revelation of the castle’s hidden history or a selection of the first recruit. Existing travel, presence, packing and return-only reward rules apply independently to both destinations.

A hearth kettle uses heat-bearing and vessel components with hearth knowledge. A pantry seal uses vessel and binding components with preservation knowledge; installed in the restored kitchen it adds 2 crowns to staffed garden surplus sales. Both require two work phases and have direct placement/removal controls under their destination facilities. Pantry and watering bonuses stack; additional copies do not. The pantry does not sell or consume existing stock, add ivy or create unattended production.

An optional copying assignment earns 4 crowns per scholar phase, without materials or unlocks. This is an explicit use of the same work budget, ensuring an empty treasury does not permanently block restoration. It is a provisional sample income source, not an invented background obligation or upkeep bill.

The milestone is checked on Advance and retained historically. Its authored celebration remains optional, does not expire, takes no time and grants no Resonance. Ordinary comfort and companionship are not substituted for erotic household expression. Existing Resonance behavior is unchanged.

Schema 4 adds only new state; old game facts remain intact. Startup backs up schema 1/2/3 databases before migrating. The phase order is castle work/production/facility work, expedition resolution, milestone check, Resonance, calendar advance. New projects begin unfunded; no new recipe, discovery, funds or achievement is retroactively granted.

Actual co-op agents, generative NPCs, new residents, character advancement, campaign creation and the foundational mystery remain future work. This release expands the authored solo demonstration and preserves the quieter artwork direction.


## 0.5 expansion — People, practice, and a living archive

The prototype now uses accomplishment ledgers for both scholar and Mira, plus introductory classless practices, individual principle study, preparation and simple retraining. Exact attribute scales, a full perk tree, affinities and equipment progression remain open. Three deliberately plain practices demonstrate distinct useful builds without inventing a complete RPG ruleset. They cost two earned points and two learning phases; two may be prepared. Mira’s initial scholarship expertise is a sample-character fact, starts unprepared and costs no earned points.

The scholar’s earlier documented accomplishments are credited once on schema-5 migration. Unknown historical resident contributions are not guessed. No practice is automatically prepared, so upgrades retain existing work rates. Shared archive findings remain separate from each person’s mastery; the workshop now validates the selected maker and uses that person’s one primary assignment. Mira has offered practical artifact binding as an extension of her archive work. One shared artifact can be in progress at a time.

Mira’s authored personal ambition is an archive index, offered after the living-wing milestone. Accepting assigns her to its four-contribution study; the scholar may assist. The resulting reference-binding principle supports a three-contribution index charm. Its installation is direct in the Library. Completing the story requires a voluntary concluding conversation, awards Mira three advancement and the scholar one, deepens the descriptive collaboration, and opens her offer of expedition companionship and fieldcraft study. It does not grant Resonance or rewrite her personality. No recruit or castle secret is selected by this content.

Hillfold bindery is a third provisional destination revealed by the completed archive. It provides fresh shared fieldwork after earlier sites may be exhausted. Survey grants two dual-property moon-glass pieces and sixteen crowns; salvage grants four binding thread, one fireglass and twelve crowns. Both leads remain one-time and return-gated. The material is a flexible component alternative, not an unexplained statistical power increase.

Mira’s companion flag is chosen before departure and cannot be changed remotely. Actual absence suppresses her workplace production, portraits and castle conversations. Returned discoveries credit actual party members. Prepared field notes on either person shorten ordinary survey to one phase; a lantern gives the same benefit and cannot stack below one. Both travelers return unassigned, with earlier project progress intact.

A one-phase retraining ritual releases invested points while preserving starting expertise, learned principles, personal history and award source IDs. Unfinished learning can be cancelled to release its point reservation; completed learning cannot be refunded by clicking cancel. These rules keep build experimentation inexpensive without letting repeated actions manufacture advancement.

All content is still an authored solo sample. Real external agents, co-op governance, a generative gamemaster, recruitment, personal finances, combat and the complete character system remain future work.


## 0.6 expansion — Useful magic, planned with care

Further research now has a small data-driven catalogue while retaining the earlier hearth fields for save compatibility. Only one further study is the household’s research focus at a time. Switching it is a deliberate shared-work planning action: already assigned researchers follow the new focus; other funded studies pause. The chosen lead must personally know the prerequisites and be at home. Assisting researchers may learn through their contribution. Each actual contributor earns one advancement once; people absent at completion retain their contribution credit but study the new archive notes later.

The three provisional studies connect earlier discoveries to everyday use: hearth/water knowledge unlocks steady growth; hearth/reference binding unlocks luminous copying; reference binding/preservation unlocks clear instruction. Costs are 12/14/10 crowns and work totals 5/5/4. Each produces a three-contribution artifact recipe. The root tender supports smaller unattended harvests on explicit Advance, the scribe stone improves assigned copying, and the lesson tablet shortens newly begun principle studies. This gives the library index and trained researchers useful continuing applications.

Automation is deliberately modest and understandable: a root tender gives one ivy or two crowns when nobody tends the garden. Staffed output replaces, rather than stacks with, that harvest; staffed watering/pantry bonuses do not apply to the tender. It uses the existing production priority and does nothing in real time. The new stock-first mode replenishes whole ivy harvests to a target and then designates fresh harvests for sale. Existing inventories and personal belongings are never automatically sold.

Material reserves protect against accidental manual disposal while allowing explicit crafting to consume the protected stock. Work orders are saved plans, not authority to buy or act autonomously. Each copy requires a separate start, preserves the maker’s one-primary-assignment budget, and uses normal knowledge/property validation. The market can buy exactly the next copy’s missing components as a single priced operation. Removing a plan does not remove its artifacts or supplies.

Schema 6 starts with zero reserves, no work orders, unfunded further studies and no new installations. Existing staffing, output priority, preparation, active learning/crafting and expeditions are preserved. Work-order linkage exists only for newly started planned copies. No earlier accomplishment credit is recalculated in a schema-5-to-6 migration.

This remains the solo authored prototype. No co-op approval proxy, live generative action authority, resident recruitment, private finances or complete spell-invention grammar has been substituted into the design. Balance and the three new practical principles are sample content for review.


## 0.7 expansion — neighbours and useful surplus

Four one-time authored requests connect the existing workshop and its batch plans to outside households. They are finite content, not a repeatable income or advancement farm. Accepting and putting aside are reversible planning decisions; delivery is an explicit atomic inventory exchange with immediately recorded rewards and a saved authored reply. No external message is sent. There is no courier timer, reputation meter, resource decay, random request generation or expiry pressure.

Delivery protects installed, displayed and packed artifacts, and respects material reserves. This differs deliberately from explicit crafting, which may consume protected materials. Each successful delivery removes the exact displayed goods, awards its listed crowns and materials once, and records its in-game date. Existing idempotent request handling also prevents duplicate exchange after a network retry. Completed work-order totals describe historical production and are not reduced by delivery.

The brook keepers’ first reply opens the fern nursery. The nursery is a provisional public teaching garden, not a disclosure of the castle’s hidden history or a new recruit. Its channel survey teaches capillary wicking; offered cuttings form the other one-time lead. Existing party, travel, early-return and return-only reward rules apply. The resulting capillary mat adds one ivy to staffed ivy harvests; no sales or unattended bonus. A final request gives a second crafted mat a destination.

Two optional scenes add quiet resident life to the practical loop. They are authored sample conversations, require both characters home, wait without expiry, and have no repeatable economy or advancement benefit. The conservatory scene is playful only when the existing mutual flirtation has been established. Neighbourly gratitude does not create erotic Resonance.

Schema 7 adds only request progress, nursery discoveries, completed-scene IDs and a capillary installation flag. Existing schema-6 values are retained. Older migrations still run sequentially; new catalogue entries do not manufacture historical accomplishment credit.


## 0.8 expansion — signature equipment and campaign continuity

Signature focuses begin as plain personal tools. Their initial names, four inscriptions, prices and two-slot ceiling are provisional sample content. They are separate from communal deliverable artifacts and do not imply a new portrait, clothing change or resident identity. The owner needs personal principle mastery; components use the existing material-property vocabulary. An inscription takes 6 crowns and 2 assigned phases; a capacity project takes 18 crowns and 3 phases. Both use two selected components. Materials may be drawn from reserves because this is an explicit construction commitment, just like crafting.

Completed inscriptions are permanent tool knowledge; preparation is a separate home-only choice. Work and expedition configurations are distinct. The four effects are bounded and named, with no arbitrary spell generation or numerical-stat system implied. Focus work grants no advancement, cannot benefit from its own bonuses, and pauses without deterioration. There is one focus project per person. The preservation case gives one bonus component on a new salvage return per party, never on merely leaving, waiting at a site or returning early.

The original save stays at its existing path. An independent registry introduces additional solo sample slots, each with separate SQLite actions/state and artwork. Slot creation uses a stable client request ID and serialized registry transaction so concurrent retries cannot create duplicates. Every data endpoint resolves its own campaign parameter. There is no mutable active-save variable shared between tabs, no solo-to-co-op conversion and no fake agent campaign option.

The save ZIP snapshots SQLite through its backup API and copies the artwork referenced by that exact snapshot, including image rollback history. It also includes restoration instructions. Restore requires a stopped server; the UI does not overwrite a live campaign. Full-directory backups preserve all slots and registry together. Downloadable backups and campaign creation do not move game time.


## 0.9 — title and optional generated NPC prose

This release adopted **Stone and Spell**, superseded in v0.10. Historical specification titles and technical save directories remain as historical/compatibility identifiers; they do not override the selected title.

OpenRouter supplies optional, explicitly requested text drafts for the sample resident. A preview/accept workflow is used while the richer gamemaster authority boundary is being built. The generated prose has no mechanical authority, tools or ability to execute actions. Scene revision checks prevent accepting a delayed draft after another tab or action changes the campaign. Replies are non-explicit and identity-preserving; actual consent and project commitments are never inferred as mechanical actions from generated text.

Draft request IDs and outcomes are stored in the campaign database before/after network work, avoiding an open game-state transaction during provider latency. Repeated or concurrent checks do not repeat the provider call. A process crash may leave an in-flight record without a result: the app deliberately does not guess whether a paid request completed or silently bill another attempt. Recent saved drafts remain recoverable. Tokens are displayed when reported; cost is not invented from a guessed model price.

Settings are server-wide, owner-readable on disk, and excluded from campaign exports and per-campaign backup ZIPs. The existing private-network/authenticated-proxy deployment assumption still applies; this release does not add a separate administrator login. The endpoint is fixed to OpenRouter HTTPS rather than accepting arbitrary user-supplied outbound destinations. Docker includes the new dialogue module.


## 0.10 — renamed game and capacity-backed accommodation

The user renamed the game **Stonework and Spellcraft** because the earlier choice matched an existing business. This records their choice, not an independent name-availability check. Current presentation and download names use the new title; campaign names and technical data/Compose identifiers remain compatible.

Two provisional accommodation projects extend the completed living wing. Their price includes beds and basic furnishings; explicit assigned phases restore them without upkeep, decay or offline production. The original chamber has two separate beds. Occupancy is distinct from reservations, and both constrain room choices. Mira's offered choices are authored consent for these specific bedroom options, not general permission to dictate resident preferences. Restoration does not move anyone automatically.

Schema 9 adds housing records while preserving earlier state and backing up the previous database. This five-bed sample is not the full design's resident capacity or annex. Reservations are planning only; general resident records and recruitment remain unfinished. No first recruit or foundational castle secret is invented. The two extensions visibly reuse guest-chamber concept art while retaining separate furnishings and accepted-image overrides.


## 0.11 — bounded invention and coordinated ritual work

The user requested larger increments before delivery and encouraged image generation when useful. This release builds a complete small loop from free spell design through testing, personal preparation and one-shot casting, plus a two-person ritual and two unique accommodation illustrations. These remain provisional sample forms, not a claim that the full design is implemented.

Written spell names and intentions are descriptive. The user explicitly selects the supported rule form; there is no hidden natural-language mapper or model authority. Personal mastery, room access, properties, quantities and funding are validated before mutation. Repeating a name cannot grant new mechanics or advancement. One design per person per form bounds storage and prevents duplicate advancement farming; these activities currently grant no advancement at all.

Ordinary magic consumes a work phase instead of a mana-management budget. Only the physical ivy-to-cord process has a casting input; root tending and copying have no routine component fee. Testing is a one-time investment. Casting resolves once, with exact outputs independent of copying/focus/practice bonuses; separate unattended household production still occurs. Inputs are committed on scheduling and returned on explicit cancellation, avoiding competing use of the same material. Changing tasks or leaving home pauses work.

Mira has an authored offer to undertake these practical forms and the concordant lesson. The shared ritual requires both participants' personal knowledge and simultaneous home assignments. If either is unavailable or assigned elsewhere, both contributions wait. Completion changes spell preparation capacity only, with no romance, personality, bodily transformation, upkeep or automatic preparation.

Schema 10 adds empty spell records and an unfunded ritual. Earlier progress, image overrides, draft conversations and housing are preserved. Two dim room paintings replace the default reuse of guest-chamber art; accepted user artwork still takes precedence. Original character references and modest established rooms are unchanged. General recruitment, larger spell grammars, augmentation, summons and genuine external-agent co-op remain unfinished.

## 0.12 — consequences that remain understandable

Additive skill ranks describe trained expertise, not innate worth. Each cost and duration is explicit. Fieldwork rewards require a completed return; partial progress survives retreat. Optional risks produce recoverable work, not hidden random punishment.

Recruitment is an introduction, a discussion of preferences, an available agreed private bed and an explicit arrival. The new resident has independent knowledge, preparation, work and personal development. Tamsin is provisional authored sample content, never the canonical first recruit. Her existence does not expand the two-person ritual’s participant list or benefit.

Personal scenes, wardrobe choices and model-generated replies are distinct from work. Tamsin’s offered flirtation follows optional tea, awards only once and does not alter Mira’s relationship. The voluntary atmosphere contributes through the existing readable Resonance rule. Nothing requires pursuing either NPC romantically.

## 0.14 — specific permission, bounded spending

A delegated batch specifies the maker, recipe, components, count and a finite held budget. It grants authority to buy those missing components and continue assigned crafting, not to redirect wallets, use reserved stock or choose new projects. The maker’s personal knowledge and one-assignment limit still apply. A standing agreement may operate during the scholar’s absence, but never offline or without Advance. Existing plans stay manual, and revocation returns unused money without undoing committed work.

## 0.15 — people teach; routines stay bounded

A lesson is a mutually offered professional activity occupying both primary assignments. It can shorten elapsed study time, but cannot create advancement or confer universal household mastery. Skill teachers must remain qualified and learners retain their own investment and interests. Teaching does not create affection or establish intimacy.

Repeat casting is a finite standing agreement for an exact personal prepared spell. It confers neither purchase authority nor access to protected stock. Its output cannot chain into another plan in the same phase. Workroom notes makes pauses and commitments visible without silently resuming a different job.

## 0.16 — things people choose for themselves

Personal requests are finite authored interests with clear costs and no urgency. They are not service-for-affection exchanges. The owner spends their own primary work and keeps the result; the player explicitly chooses an offered source of funding. Keepsakes remain descriptive personal possessions, avoiding invented productivity bonuses for every enjoyable activity.

The narrator may describe only settled results, with human review and visible source events. It has no simulation authority. Generated accounts stay labeled in the journal and cannot establish discoveries, rewards or consent. The journal draft context excludes private conversations and unrelated campaign records.

## 0.17 — furnishings as an understandable inventory

Mark explicitly preferred a text box listing furnishings and bonuses over the low-quality overlays. The implementation removes the generic furniture and lantern overlays. Room paintings establish atmosphere, while the actual saved contents and effects appear in a readable panel. This direction supersedes the prototype’s assumption that every furnishing needs a composited illustration. No new furnishings are painted into the background when selected.

Independent decorative slots and named room arrangements remain useful even without overlays. They are descriptive styling; functional artifacts still require crafting and explicit installation. An arrangement records supplied furniture choices only, so loading one cannot manufacture artifacts, transfer another person’s keepsake or alter bedroom consent. Existing settee/Resonance rules remain visible and unchanged.

## 0.18 — personal attention without a progress meter

Contextual conversation follows events that actually happened. Authored residents can have differing interests, make jokes and become friends without turning every shared cup of tea into a productivity boost. Private follow-ups require that person’s earlier welcomed flirtation and offer only the interaction described. Nobody is automatically romanced through professional work or recruitment.

The player explicitly joins substantial scenes. Deferral carries no penalty or deadline; rereading is a memory, not another event or reward. Shared scenes enter both participating residents’ histories, while private scenes remain scoped to their participants. Eris and Selene are still absent from solo play; no substitute co-op actors were added.

## 0.19 — investment, preparation and reversible change

Advanced practices deepen an existing discipline rather than inventing unexplained character statistics. The prerequisite and each work contribution are readable. Learned abilities, prepared abilities and assigned work remain distinct; routine repetition does not create advancement. Named preparation sets are convenience snapshots, never a way around learning or castle-only build changes.

Lamplit sight is a deliberately bounded, authored offer of personal magical development. It adds one spell-preparation slot and a described appearance detail, without rewriting personality or implying romantic consent. Receiving and reversing both require explicit assigned work. Protected supplies cannot be consumed without release, and unfinished commitments can be cancelled exactly once. Reversal waits for an explicit preparation choice instead of choosing which spells the character should forget. This is a sample foundation for the broader voluntary augmentation design, not a completed transformation catalogue.

## 0.20 — proposals explain rules; they do not write them

A natural-language idea can receive a model-suggested construction, but every executable effect is selected from the existing catalogue. The model cannot supply a price, resource delta or replacement rule. A strict response schema rejects fields that would pretend otherwise. No-fit and partial-fit answers are supported; the exact catalogue effect is always shown separately from fallible prose.

Review is an actual step: a suggestion only fills an unsaved design form. The player still chooses components, saves a draft, begins testing, prepares and casts through ordinary rule-checked actions. Knowledge is not granted by a fluent explanation, and names do not confer extra powers. Legacy NPC drafts keep their original identity and behavior. This is a bounded first content-proposal path, not a claim that the full generative gamemaster is complete.
