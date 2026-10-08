# Stonework and Spellcraft v0.40 — solo interface and fresh opening

Co-op with Eris and Selene is deferred. This release concentrates on navigation, a distinct beginning, and explicit testing tools.

## Interface review and changes

The previous sidebar mixed 29 destinations across room management, relationships, advanced magic, reference material and administration. The permanent right column repeated resources, forecasts and journal entries while assuming Mira was always present. The demonstration household and the new-game creation flow did not offer a solo opening.

The primary navigation now has Home and four activity groups. Each group describes actions in terms of what the player wants to do. Existing systems remain reachable, including all integrated content packs. Fresh saves fold less immediately relevant systems into a clearly labeled expandable area rather than treating them as current tasks. The content workshop separates its catalogue from expandable work, inventory, correspondence and history sections. Settings puts content configuration and optional generation behind named disclosures.

A fresh Home screen presents one recommended next step, a small sequence of milestones, the actual next-phase forecast and optional starting-room details. The initial research and lantern screens teach assignment and Advance without displaying the entire research/crafting catalogue. The full workshop remains accessible. The shared permanent right column has been removed; treasury and household count stay in the header. Focus styles, labeled forms, semantic details/summary controls and responsive layouts accompany the changes.

## Fresh start

Opening the base address shows a title screen. New game defaults to Fresh beginning; the demonstration household is explicitly selectable. Continue lists independent saved campaigns and labels fresh/demo/testing state. Creation keeps its request identifier across a lost response and rejects reuse for a different start type.

The fresh campaign begins on day 1, morning: the founder alone, 40 crowns, two sun amber and two binding thread. The library, common room and sleeping chamber are usable; other facilities need restoration. There is no Mira membership, bedroom assignment, active invitation, shared conversation or fabricated social history. Normal three-phase hearth research and two-phase lantern crafting work with the supplied resources. Local introductions, visits and mutual membership provide a first recruit through play.

Later progression also has a solo route: Arrange the first archive costs 12 crowns and three assigned work phases after hearth study, grants Reference binding and opens Hillfold bindery. Installing a crafted living index charm satisfies the fresh-game archive prerequisite for Courteous passage research; the normal personal knowledge, crowns and research work remain required. The demonstration’s Mira story and concordant lesson retain their original requirements.

The opening uses existing representative interiors. It is a development opening, not a declaration of final campaign lore or final introductory artwork.

## Testing tools

At your desk → Cheats must be enabled per save. Tools operate through the same revision-checked, retry-safe action endpoint as normal play. They do not advance time. Each successful mutation creates a testing journal entry and a permanent testing-modified marker.

| Tool | Effect and limits |
| --- | --- |
| Resources | Adds shared crowns, Resonance, core materials or public materials; bounded integer quantities. Public qualification rules remain in effect. |
| Instant construction | Completes the conservatory, west/garden guest chambers or core living-wing facilities. Clears the completed active construction assignment. Already committed costs stay spent. |
| Objects | Creates a core artifact in shared stock, or a public artifact, furnishing or equipment instance owned by a selected household member. Installation, preparation and use remain separate. |
| Knowledge | Grants a selected core principle to one actual household member and records it in the archive; granting hearth wards completes that introductory study. |
| Characters | Generates a distinct adult offline NPC of a selected ancestry, initializes personal records and places them directly in the household with a suitable free bed. All 21 ancestries are supported. Golems receive no invented past or learned principles. |

No provider or co-op service is required. Disabling cheats does not reverse changes or remove the marker. Download the complete save backup before experimentation if rollback is wanted. Cheat character arrival is explicitly testing data and bypasses the ordinary introduction/arrival sequence.

## Packaging and migration

The new archive extracts into `stonework-and-spellcraft/`. The old working title is removed from shipped text and archive paths, including checked embedded source packs. Earlier release downloads are preserved separately. The two original content-pack source ZIPs are unchanged. Save schema 38 adds start type, testing state and the independent archive project while preserving prior game state; server migration creates a pre-migration database backup. Existing saves remain demonstration campaigns and are never converted into fresh beginnings.

## Verification

458 Python tests and 18 connected headless UI suites pass. These include fresh opening research/crafting, a normal first visit and household membership, independent archive progression, save isolation/retry/migration, testing permission/quantity validation, spawning all 21 ancestries, public and core objects, title/new-game controls, fresh-screen rendering, and the existing integrated content workflows. The UI navigation test follows the new group hierarchy. The content audit retains 1,599 public content records and 319 fixed mechanics adapters with no unrouted records.

Headless UI checks exercise real templates/controllers and SQLite-backed actions; they do not verify rendered layout. Rendered desktop/mobile, visual accessibility and browser focus verification remain outstanding because the available cloud browser blocked the local server. Live text providers, Docker and co-op were not exercised.

## Remaining interface work

This is the first structural simplification pass. Some advanced legacy screens still contain dense forms. The next useful review is playing the fresh opening in a normal browser at desktop and narrow widths, then prioritizing the advanced screens that players actually reach: ownership/target selection in the content workshop, the full research catalogue, and recruitment/arrival details. Opening-specific artwork can then reflect the modest starting rooms more precisely.
