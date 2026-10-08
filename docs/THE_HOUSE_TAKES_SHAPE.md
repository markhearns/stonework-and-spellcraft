# v0.77 update: all three undertakings form Chapter 2

Complete all three, in any order, then record **Three rooms, one home** to finish the chapter and open Room to Grow. Existing completed undertakings count. Enrolled First Hearth campaigns now finish their closing choice before Chapter 2 becomes available. Known evidence and deliveries are not repeated. See [ROOM_TO_GROW.md](ROOM_TO_GROW.md) for the current chapter sequence. The original checkpoint notes below are historical; their per-undertaking costs and rules remain applicable.

---

# The House Takes Shape — chapter two, 0.76-dev

An optional, persistent shared undertaking. Open it from Home after establishing the living wing and recording the hearth mark, or through **Go directly to → The House Takes Shape**. Older campaigns qualify from their actual accomplishments without replaying chapter one. This remains an unreleased development checkpoint; delivery of a release is on hold.

## Three paths, six designs

Choose one undertaking, discuss its purpose, bring back its required field findings, prepare its room, and decide how to use the limited space. The initial adviser is an already known appropriate companion, when one exists; otherwise the proposal comes from the scholar's notebook. Correspondence does not create a resident or a work agreement.

| Path | Existing expedition lead | Installation budget | Design | Lasting benefit |
|---|---|---|---|---|
| Working archive | Quarry shelter survey | 16 crowns, 1 porous clay, 2 binding thread | Indexed reference wall | +1 work per assigned shared researcher |
| Working archive | Same | Same | Shared copying table | +2 crowns per assigned founder copying phase |
| Kitchen garden | Old waterworks survey | 18 crowns, 2 porous clay, 2 silver ivy | Botanical propagation beds | +1 silver ivy per staffed ivy harvest |
| Kitchen garden | Same | Same | Kitchen plots and surplus bench | +2 crowns per staffed surplus harvest |
| Commission bench | Old waterworks salvage | 20 crowns, 1 fireglass, 2 binding thread | Continuous assembly bench | +1 work per assigned core-artifact crafter |
| Commission bench | Same | Same | Maker's alcove and commission desk | +2 crowns per assigned founder copying phase |

The budgets cover the chapter installation, not ordinary prerequisites. The archive uses **Arrange the first archive**, or the demonstration household's existing living-index study. The garden requires the normal 25-crown conservatory restoration. The workshop uses the normal warehouse and workshop restoration chain. Guidance reuses the existing rules, costs, prerequisites, pause/resume actions and room controls.

The design choice is a real trade-off: a reference wall takes space from a copying table; propagation trays compete with varied crops and sorting baskets; a continuous production run leaves less room for drawings and commission records. The selected design, description, precise benefit and actual contributor credits appear in the room workspace. Existing illustrations remain representative; no room image or accepted artwork is repainted or replaced.

Copying bonuses from separately completed installations stack. Research and crafting benefits do not alter personal learning, spell work or public-pack projects. Garden bonuses require a present assigned gardener and the matching production choice; they do not enhance unattended root-tender harvests. Benefits activate at construction completion, not at proposal, funding or conversation.

## Agree and fund shared work

- Agree one to three named contributors from current household members. The scholar can do the entire project alone. **Agree & include** establishes participation only.
- The fixed installation needs **six contributor-work**. Each present, assigned contributor supplies one work on an explicit Advance. Three contributors can finish it in two phases; one needs six. Work on the last phase is capped at the remaining requirement, and credit records only work actually done.
- Funding requires the selected workers to be home and resting, the full stated treasury budget, and materials above protected reserves. The interface offers explicit pause controls for other work. Funding commits costs once and assigns the agreed contributors.
- Travel or another assignment pauses only that contributor. Other assigned workers at home can continue. Existing funded tasks of other kinds keep their progress and never receive a second contribution from the same person in the same phase.
- Pause all contributors, resume individuals, or revise the contributor roster. Previously earned contributions retain the worker's name and amount even after removal or departure. If no contributors remain, work waits for an agreed replacement.
- Cancellation releases assignments and returns exactly the held crowns and materials once; unfinished construction progress is discarded. The design and conversation memories remain. Completed installations cannot be cancelled for refunds or funded repeatedly.
- Shared work appears in phase previews, project resumption, work arrangements, room presence and expedition departure commitments. Contributor agreements are distinct from existing headquarters or garden agreements.

No offline time passes, and no repeat project is funded automatically.

## Finish, use and investigate

After construction, choose how to mark the completed room. Actual contributors who are present may share the gathering; absent people are not silently included. Ordinary work must then put the selected benefit to use: shared research, core crafting, copying or a matching staffed harvest. This use is recorded from real phase resolution, including the worker and time. Previously completed knowledge is not rewritten.

For an established campaign that has already completed every current shared research project, the indexed archive offers an explicit **Record existing mastery** exception. It states that no new demonstration occurred and awards no resources, time or advancement. This prevents the optional chapter becoming permanently stuck after the research catalogue is exhausted.

The craftsmanship path additionally uses the established **A lamp for the footbridge** request. Accepting a conversation does not complete it: one spare warming lantern and two unreserved binding threads must actually be delivered. Its existing one-time reward—24 crowns, one porous clay and access to the fern nursery—provides the neighbour connection. A previously completed delivery is respected, not rewarded twice.

Each path offers a different perspective on the same next historical source: the uncatalogued archive leaf. Arrange or study the archive, then complete the existing two-phase investigation. Evidence is copied from the campaign's existing private history packet. The chapter does not replace the underlying lore, reveal undiscovered evidence, or automatically share it with residents. If the leaf was already discovered, it is reread without another reward.

The final memory recalls the purpose chosen at the start. Finish the undertaking to choose another path; all completed room benefits, memories and contributor credits remain. The other existing game systems are available throughout. Chapter guidance can be hidden and restored without stopping assigned work.

## Continuity and presentation

Save schema remains **59**. The optional `houseShape` record is created only on an explicit chapter action. Read-only views do not initialize it. Existing campaign records, identities, relationships, money, projects, accepted artwork and private lore are preserved. The checkpoint includes both chapters and all pending v0.74 artwork and logo changes; it contains no live campaign data.

Chapter notes appear in the existing journal. Optional NPC dialogue receives only the chapter memories that the speaker participated in, plus the visible improvements in their current room. Private founder reflections and undiscovered historical evidence remain excluded.

Keep the complete existing **data directory**, including `data/assets` and every campaign subdirectory, whenever upgrading. The server and title screen identify this checkpoint as **0.76-dev**.

## Verification

All six designs completed from the end of a normally played First Hearth campaign, without cheats, with serialization/reload after each action:

| Path | Design | Additional Advances | Crowns at conclusion |
|---|---|---:|---:|
| Scholarship | Indexed reference wall | 24 | 0 |
| Scholarship | Shared copying table | 22 | 8 |
| Cultivation | Propagation beds | 35 | 2 |
| Cultivation | Kitchen plots | 33 | 0 |
| Craftsmanship | Continuous assembly bench | 35 | 13 |
| Craftsmanship | Maker's alcove | 34 | 18 |

These are reproducible solo baseline routes, not real-time duration estimates. They include earning funds, normal room restoration, field travel, research, actual output and the historical investigation. Agreed additional workers can shorten the six-work installation. Exploring or sharing optional scenes changes the route naturally.

`VERIFICATION_HOUSE_SHAPE.json` records the broad regression run, final focused checks, UI results and file preservation. Coverage includes all designs, shared and solo work, exact refunds, protected reserves, invalid actions, serialization, idempotent requests, custom artwork, travel, individual pausing, concurrent headquarters work, saved arrangements, later paths, hidden history and exhausted-research compatibility.

The connected UI playthrough covers the real controllers, Python rules and saved campaign with a DOM test double. It follows a shared garden undertaking through funding, travel, construction, harvest, evidence, installed room description and reload. No rendered desktop/mobile review is claimed: the environment lacks the browser executable identified during the preceding checkpoint. No live-provider, co-op-agent or Docker-runtime acceptance is claimed.
