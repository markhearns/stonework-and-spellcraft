# Persistent evidence and hidden history — v0.29

The **Castle history** page provides four authored investigations demonstrating one internally consistent prototype history. This is explicitly sample campaign content, not a claim that the finalized first recruit or opening has been selected.

## Rules

The history packet is established once in each save before discovery. A fixed versioned packet contains the foundation and compatible evidence. Resolving investigations copies evidence from that saved packet; neither reload, dialogue generation, candidate generation nor later prose rewrites the explanation.

The first lead requires A Proper Living Wing. Later leads require the first evidence, the completed living-index study or the scholar's personal Gentle refraction knowledge. The final synthesis requires all three sources. No intimacy, romantic relationship, crowns or Resonance is required. The mystery can be pursued by a non-romantic household.

An investigation uses the founder's own primary assignment for two or three phases. Research bonuses cannot shorten it. Switching assignments pauses it; cancellation discards only unfinished progress. Previously recorded evidence stays. Each first discovery awards one advancement using a stable award ID. Reading and sharing are free and do not create rewards. All leads wait without expiry.

## Scope boundaries

- `privateCastleLore` contains the undiscovered history packet and is removed from ordinary public state, successful actions, revision-conflict responses and the visible diagnostic export.
- `castleMystery.discoveries` contains only actually discovered text, source version and discovery time.
- NPC dialogue receives only evidence explicitly shared with that specific resident in person. A title in the journal does not grant an NPC the full discovery. Generated candidate context receives no mystery packet.
- Full SQLite backups necessarily preserve hidden lore. The UI labels their possible spoilers and distinguishes them from diagnostic JSON. Use a complete backup for restoration, not redacted JSON.
- This is application-level narrative scoping. The host administrator can inspect the database and source. It is not multi-user authentication or a substitute for future character-scoped agent APIs.

The packet is immutable through existing game actions. Story correction tooling and validated generated additions are still to be designed; no arbitrary rewrite control is exposed.

## Migration and verification

Schema 27 initializes an empty ledger and one sample packet without inventing completed discoveries or changing existing people, histories, projects, finances or phase. Reload keeps the packet; backups preserve it.

Tests cover the full four-investigation path, prerequisites, personal knowledge, pause/cancel, non-mutating reads, no intimacy requirement, one-time awards, explicit person-scoped sharing, exact saved evidence, upgrade and backup reopening. Real HTTP tests verify hidden packet removal from normal state, diagnostics, action and conflict responses. Connected UI tests verify hidden content absence before discovery, escaped discovered prose, progress, sharing, final synthesis and reload. Live provider behavior and browser layout are not inferred from these checks.
