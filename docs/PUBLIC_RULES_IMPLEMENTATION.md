# Public rules and content — v0.39

The v0.38 mechanical costs below remain authoritative. v0.39 adds the story, discovery, neighbour, training and production connections documented in [CONTENT_INTEGRATION_V039.md](CONTENT_INTEGRATION_V039.md). Save schema is now 37; 453 Python tests and 17 headless UI suites pass.

## Scope

All 319 proposal IDs map to fixed prototype adapters. The executable catalogue is a shipped application asset compiled from the reviewed public bundle. Uploaded revisions remain review-only; their English descriptions, magnitudes and null costs never become executable code. The original 1,599 content records and 319 proposals are preserved with source digests.

Coverage counts IDs mapped to an implementation path. The game represents most household conveniences through owned-object state, explicit local use and receipts. It does not simulate physical optics, chemistry or structural engineering. Narrative possibilities remain reviewed candidates until selected in actual play. The private mystery pack is not included and was not accessed.

## Mechanics coverage

| Adapter | Proposal IDs | Executable behavior |
| --- | ---: | --- |
| Artifact | 40 | 40 recipes create inactive owned instances. Install separately; manual use records a bounded function on an agreed target. |
| Augmentation | 18 | 18 requested presentation overlays. Original identity and portraits stay intact; immediate free removal works away from home and during work. |
| Commission | 1 | Actual matching owned output or allocated completed baseline casting; exact identity/custody and a single funded delivery. Existing-output delivery takes no extra work phases. |
| Equipment | 1 | One shared equipment/focus rule; 48 concrete equipment definitions can be fabricated, owned and transferred. Preparing an inscription excludes the baseline focus configuration. |
| Furnishing | 48 | 48 physical fittings consume real materials; placement requires available room, fit and permission. No decoration overlay or invented capacity. |
| Inscription | 44 | 44 installations with exact compatible hosts, personal principles, real component reservations and separate preparation/use. |
| Perk | 36 | 36 earned methods require appropriate rank 1, personal prerequisites, two advancement and two training phases. Existing two practice slots are reused; six fabrication methods share the alternative support channel. |
| Principle | 1 | 24 concepts have individual three-phase study; one registry proposal covers admission. No knowledge grant on import. |
| Qualification | 13 | Actual material sample, reviewed acceptance evidence, one assigned phase, reusable sample and admitted component mappings. New shipments require requalification. |
| Ritual | 24 | 24 protocols bind actual roles. Each participant performs independent phases; compatible multiple roles take sequential phases. Completed observations stay separate from unproven outcomes. |
| Service | 1 | Named household provider/client, owned object, two actual provider phases, fixed eight-crown personal escrow and separately accepted settlement. |
| Spell | 68 | 68 new forms plus principle registry are separated in this table. Each form has personal testing, shared preparation slots, reusable components, a scheduled cast and a fixed state transition. |
| Starter | 12 | 12 creation-only packages: one principle, one basic practice, zero ranks/earned advancement, one uninscribed focus. New NPC proposals can select these; golems retain prospective-only capabilities. |
| Support | 12 | 12 optional adjacency contributions; actual connected rooms, matching purposes and completed evidence. Craft support takes the maximum with binding press/perks. |
| **Total** | **319** | Fixed, source-linked prototype rules. |

## Additional content workflows

| Content | Current player use |
| --- | --- |
| 60 materials and 12 property concepts | Finite displayed supplier stock, bounded paid orders, actual inventory, reserve targets and sample qualification. Baseline recipes retain their original component registry. |
| 48 equipment concepts and 40 artifact recipes | Library fabrication, real inputs, ownership, compatible inscriptions and separate use/installation. Ordinary equipment without its own proposal uses a supplemental physical fabrication rule. |
| 24 room purposes and 72 furnishing concepts | Purpose/permission review, functional fitting or free decoration, and text lists in actual room views. Kitchen, washroom, garden, one-person bedroom and care purposes check existing supporting facilities. |
| 18 sites, 54 leads and 54 discovery templates | Actual outbound travel, selected lead work and return. Returned observations include related discovery candidates; neither hypotheses nor loot are awarded automatically. |
| 60 encounters | Select an actual observed encounter on the current trip, choose an approach, perform a field phase and retain uncertain interpretations. Safe return is always available. |
| 80 scenes and 80 ambient lines | Direct editable invitations using existing review/offer/join/defer controls; brief reviewed NPC asides reject immediate repeats. |
| 40 books, 30 meals, 24 specimens, 30 curiosities and 36 gifts | Paid acquisition/preparation produces owned instances. Reading takes an assigned phase without mastery; meals are served once; gifts transfer one existing owned object with agreement. |
| 40 letters | Reviewed drafts between actual household participants; explicit once-only in-game delivery. No external messages are sent. |
| Arcs, relationships, contacts, communities, care, backgrounds and training opportunities | Dedicated chapter, introduction, bounded starting-package and actual lesson workflows. Frozen optional planning notes remain available, but are not substitutes for completing those actions. |
| Art briefs, help, feedback, spell explanations and 64 acceptance scenarios | Subject-specific exportable production briefs, compatible wardrobe styles, searchable guidance and evidenced manual QA records. Art is not automatically generated or accepted; manual records are distinct from automated test results. |

## Balance decisions

- Ordinary/specialist/discovery material units cost 3/6/10 shared crowns. The initial supplier stock is 8/4/2 per material. Further orders are explicit batches of 1–4 units, cost the unit total plus 2 crowns, and take 2 phases (3 for discovery materials). No refresh restocks a shop. Discovery materials require a returned field discovery.
- Qualification reserves and returns one real sample, takes one assigned phase and costs no crowns. The player records acceptance evidence; this is a reviewed game abstraction, not a physical laboratory simulation.
- Equipment fabrication: 6 shared crowns, one binding unit, one vessel unit and two phases. Inscriptions: 8 crowns, the proposed components and two phases. Artifact and furnishing inputs/durations follow their resolved source rules.
- Principle study: 8 crowns and three phases. Building a bounded experimental setup: 4 crowns, binding and vessel components, two phases. Personal testing: 4 crowns and two phases. Ordinary casting: one phase, no crown fee; exceptional casting: 12 crowns and three phases. Components are reserved and reused where specified.
- Experimental setups describe finite owned inert samples and actual reference evidence. Exact state transitions live in `public_spell_effects.py`. Freight requires two compatible local circle setups in connected rooms and moves the same owned parcel. Recovery moves an existing tool; removal requires a registered label or finish. Attended effects end on the next Advance; state changes and receipts persist.
- Rituals with previously unset crown costs reserve 6 crowns. Each actual role takes the stated three phases; a single actor filling two roles takes six. No participant is generated or silently borrowed. Withdrawal returns unsettled costs once and preserves recorded observations.
- Technical methods require two unspent advancement, appropriate earned rank 1, prerequisite knowledge/practices, review evidence and two personal phases. Their preparation occupies existing practice slots. Acquisition does not create an earned rank.
- A service fee is 8 crowns from the named client's personal wallet, held until acceptance. Delivery of an existing matching commissioned object uses the same 8-crown escrow. A luminous-copy output receipt adds no payment to the baseline income. No payer budget is invented; baseline output allocation checks actual available stock and completed cast provenance.
- Books cost 6 crowns/two phases; meals 4/one; specimens 8/two; curiosities 6/two; keepsakes 4/two. These prices include modest ordinary supplies, subject to source/permission review. Meals require the restored kitchen; specimens require the restored conservatory. These objects grant no work, romance or Resonance bonus.

## Persistence and controls

Save schema 36 adds the public workshop state. The existing automatic migration backup preserves the pre-migration database. Migration retains accepted identities, money, inventory, projects and history; its revision increment invalidates stale tabs. SQLite request IDs and revision guards cover every new action. Jobs reserve real inputs, pause with assignments, recheck eligibility and refund unsettled inputs once on cancellation. Original ownership and receipts survive departure, reload and backup.

Public work uses the actor's one primary assignment. Personal learning does not accelerate from tools or room support. Imported and baseline spellbooks share the existing preparation capacity. Public focus preparation cannot coexist with baseline prepared inscriptions. Changing room labels creates no bed, resident, service or care capacity.

## Verification and limits

453 Python tests and seventeen connected headless UI suites pass. Catalogue loops exercise all physical fabrication definitions, 44 inscriptions, 60 material qualifications, 68 public spell forms, 18 presentation trials, 24 rituals, 12 starters, 36 earned methods, 12 room supports and all 18 field sites. Additional tests cover actual funded delivery, service cancellation, stale eligibility, protected stock, duplicate receipts, migration, source-version isolation, personal slots, recipe-alias prerequisites, conditional room purposes, letter delivery and finite meals.

The connected interface checks include real SQLite-backed actions for purchases, fabrication, pause/resume, owned reading, departure, lead work and return. They do not establish rendered-browser layout, keyboard/focus behavior, real model quality or Docker deployment success. Those remain unverified. The 64 supplied QA records remain written test designs; they were not executed as a separate suite.

The runtime currently uses modest local experimental setups for the new spells and reviewed scope for household services. Wider simulations, independently operating community providers, unreviewed autonomous narrative resolution, automatic artwork generation and real Eris/Selene co-op tools are not supplied by this release. The original design is not claimed to be 100% complete.
