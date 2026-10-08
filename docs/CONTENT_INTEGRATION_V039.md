# Content integration — v0.39

All sixteen shipped public packs now have explicit gameplay, production, or reference routes. The inventory covers **1,599 content records and 319 fixed mechanics adapters**, with no unrouted public record types. The **3,595-record character foundations pack** remains bundled unchanged. New mappings and source-specific compatibility decisions live in application code, not rewritten source ZIPs.

This statement describes the bounded prototype workflows below. It does not mean that every source sentence is a simulated physical effect, that an imported possibility is already true, that artwork has been generated, or that the entire original game design is complete.

## What changed

| Content | Integrated use |
| --- | --- |
| 42 personal arcs | Resident-specific chapters. Each requires established prerequisites, a joined optional invitation, one assigned work phase, then an explicit outcome or revised goal. Later chapters require completion of the preceding chapter. |
| 36 relationship developments | Joined conversations and chosen, remembered outcomes. No numerical affection reward or automatic relationship status. Two-resident/group requirements are enforced. |
| 12 care cases | Voluntary support episodes with a practical work step and chosen conclusion. Support can end immediately, including while away; no fee, completion or recruitment condition. An unjoined care invitation is withdrawn when support ends. These cases do not create a visitor, confinement capacity or an automatic medical cure. |
| 54 discovery templates | Select and archive an actual returned observation from the matching lead. Retain uncertain interpretations, link to materials and principles, and prevent duplicate deposits. No inferred loot or personal mastery. |
| 8 communities, 32 contact roles | Two assigned introduction phases establish a chosen neighbour. One additional phase meets a named independent adult contact. Saved conversations expose their agenda or selected knowledge topics without recruiting them or granting magical mastery. |
| 30 background mappings | All 40 supplied occupations are available for generation. Only exact original source records receive the shipped mappings. Candidates preserve the original background and mapping alongside the effective package. Small story teller, left unresolved in the source, uses the bounded voluntary-teaching starter. Accepted residents are untouched. |
| 25 golem appearances | Exact, reviewed groups of five map to clay, porcelain, stone, living wood and metal. Altered or unknown appearance records cannot silently inherit a body-material mapping. |
| 525 character story seeds | Available for appropriate existing residents as continuing personal stories as well as their eligible generation use. The conditional living-wood gardening seed requires an actually awakened wood-bodied golem and reviewed evidence of her interest. Golem biography remains prospective or post-awakening. |
| 24 training opportunities | Start the actual lesson system with a personally knowledgeable teacher, willing learner and referenced subject. Both use their primary assignments. Lesson history retains source and exercise evidence. Further perk investments remain separately earned. |
| 93 art briefs | Produce an exportable prompt bound to an actual room, owned object or resident and its available accepted reference. The 21 wardrobe briefs can create compatible saved clothing styles. Wearing a style and accepting imported artwork remain separate choices. Owned objects now have individual illustration slots with import/review/rollback, preserved across ownership changes. No images are automatically generated. |
| 32 help cards, 48 feedback entries | Readable help and troubleshooting routes, accessible from the opening guide and searchable catalogue. Source explanations remain alongside current implementation costs and controls. |
| 64 acceptance scenarios | Executable by a tester with explicit passed/failed/blocked evidence records. These user-recorded manual checks are separate from the automated suite; reading a scenario never marks it passed. |
| 40 letters and owned reading | Editable letters, once-only in-game delivery and participant-scoped dialogue context. Owned books retain read status, excerpts and observations. Undelivered drafts and other residents’ correspondence are excluded from NPC context. |

Existing material, equipment, inscription, artifact, room, spell, ritual, presentation, service, commission, object, scene and earned-perk rules continue to run through their dedicated controls. The eight source records describing baseline spells/inscriptions link to the existing spellbook/focus rules; they do not create duplicate powers. Recipe aliases retain the artifact's original requirements. Reference-only adjacencies and decorative furnishings do not gain hidden bonuses.

## Using the release

1. Start the server as usual, then open **Public workshop**.
2. Open **Start here** for a progression-aware opening guide. It grants no resources or checkmark rewards.
3. Filter by pack, type, or text. Follow **What connects to this?** to prerequisites, related recipes, field sites and source records.
4. For a personal arc or relationship, select the resident and any required partners, establish its actual premise, and begin the episode. Open and join its chapter invitation, complete assigned work when required, then record the chosen outcome. Invitations do not expire. Pause or conclude voluntarily.
5. Bring field observations home before sharing a discovery. Follow its material/principle links to the normal acquisition or study controls.
6. Establish a community before naming and meeting its contact. Contacts are independent people, not free household workers.
7. Art briefs produce a downloadable JSON prompt. Send it and the actual accepted visual references through your image-production workflow, then use **Review artwork for this subject** to open its exact illustration slot. Owned-object pictures appear with that object; acceptance and rollback do not change its mechanics. Existing art remains unchanged until accepted.
8. The foundations ZIP still uses **About & saves → content pack validation and activation** for new character generation, shared interactions and ordinary wardrobe composition. The shipped public runtime and continuing character-story catalogue require no manual pack staging.

Completed scene memories no longer exhaust a 100-record lifetime cap. Up to 200 unresolved invitations can coexist; completed memories remain archived. Household conversation browsing shows 25 records per page, with active invitations first. Completed work receipts expose their actual outputs and evidence and remain selectable for later discoveries/support.

## Persistence and source boundaries

Save schema **37** adds journeys, shared discoveries, communities, contacts, production briefs and manual QA records. Opening an older save creates the normal migration backup. Existing money, identities, belongings, work and history are retained. New actions use the existing SQLite request IDs and revision checks. Failed actions roll back; replaying the same request cannot duplicate a chapter, contact, receipt or delivery.

Personal chapters retain the original source and digest. A saved draft, possible resolution or production brief is not an accepted event. NPC prompts receive completed chapters only for participants, owned reading only for the owner, and delivered letters only for sender/recipient. The unauthenticated solo server itself is still intended for a trusted private deployment; these narrative scopes are not a replacement for future authenticated player access.

The private mystery pack remains excluded. The pre-existing sample castle mystery is unchanged. Uploaded expansion revisions remain review-only until their executable adapters are deliberately updated.

## Verification

- **453 Python tests pass**, including the existing 433 and 20 integration tests. Catalogue subtests cover all 42 arcs, 36 relationship developments, 12 care cases, 54 discoveries, 8 communities, 32 contacts, 525 source stories, 25 golem appearance mappings, 21 wardrobe briefs and 72 room/object production briefs.
- **17 connected headless UI suites pass.** The new suite follows ordinary acquisition and work, field return, discovery sharing, chapter invitation/join/work/outcome, community introduction, named contact and wardrobe/art production. It renders each catalogue type. These are DOM/controller checks against real persistent game actions, not screenshots from a rendered browser.
- Fresh-campaign tests, without injected money/knowledge/items, cover fieldwork → returned discovery → fabricated owned tool and research → experiment → personal test → preparation → cast → artifact fabrication/installation/use. Existing arrival, recruitment, household, training and advancement suites also pass.
- The source-linked audit can be rebuilt with `python tools/audit_public_integration.py docs/content-integration-coverage.json`. It reports routing coverage, not automatic proof that all narrative meanings have been simulated.
- Rendered-browser verification was attempted against the local server; the cloud browser returned `net::ERR_BLOCKED_BY_CLIENT`. Visual layout, actual focus behavior and mobile rendering therefore remain unverified. Live-provider output, Docker runtime, long-run economy balance and real Eris/Selene co-op are also unverified or separate development work.

See `PUBLIC_RULES_IMPLEMENTATION.md` for the 319 adapters' exact costs and limits, and `content-integration-coverage.json` for every shipped public record's route and source digest.
