# Delivery index

All seventeen content packs are complete at their requested targets. Mechanics are additional, unimplemented proposals. An empty dependency list does not remove the shared contract or read-only baseline snapshot.

| Pack | Scope | Content | Mechanics | Required sibling packs |
|---|---|---:|---:|---|
| 01 | Materials and component properties | 72 | 13 | None |
| 02 | Equipment and evolving signature items | 96 | 45 | 01 |
| 03 | Household artifacts and crafting recipes | 80 | 40 | 01 |
| 04 | Magic principles and bounded spell constructions | 126 | 69 | 01 |
| 05 | Rituals, voluntary augmentation and reversal | 42 | 42 | None |
| 06 | Room purposes, furnishings and understandable synergies | 120 | 60 | 01 |
| 07 | Expedition sites, leads and reusable discoveries | 126 | 0 | 01 |
| 08 | Field encounters, negotiation and specialized care | 72 | 0 | None |
| 09 | Neighbouring communities, services and recurring contacts | 64 | 1 | None |
| 10 | Personal arcs and descriptive relationships | 78 | 0 | foundations |
| 11 | Household scenes, fanservice and ambient life | 160 | 0 | foundations |
| 12 | Correspondence, commissions, gifts and keepsakes | 100 | 1 | 03 |
| 13 | Private mystery foundations (separate, opt-in) | 42 | 0 | None |
| 14 | Books, food, gardens and unusual treasures | 124 | 0 | None |
| 15 | Art briefs and visual continuity | 93 | 0 | 02, 06, foundations |
| 16 | Tutorial copy, explanations and integration scenarios | 144 | 0 | None |
| 17 | Background capability mappings, training and earned perks | 102 | 48 | 03, 02, foundations |

## Suggested implementation order

Start with the existing foundations dependency, then 01 → 02 → 03 → 04 → 17. Continue with 06 → 07 → 10 → 11, then 05 → 08 → 09 → 12 → 14 → 15. Use 16 alongside all implementation work, not only at the end. This sequence is advisory; each manifest contains the actual required dependency edges.

Pack 13 is separate, private, and optional. It is not required by any public pack. No alternative is selected as canon. Do not expose its contents in ordinary summaries, client assets, public indexes, or logs.

## Runtime boundary

Importing a pack must never grant money, inventory, knowledge, focus slots, relationships, accepted history, resident capacity, or elapsed work. Candidate data and instantiated save state are separate concerns. Versions here are content contract versions, not assertions about the live repository.
