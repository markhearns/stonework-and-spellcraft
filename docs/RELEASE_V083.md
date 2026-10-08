# v0.83 — UI audit and simplification

This release improves navigation, the home page, research, character screens and equipment management. Game rules, item identities, prices, quests and save schema remain unchanged.

- Home no longer embeds a second home page beneath its castle map. Current chapter guidance stays prominent; completed Chapters 2–5 share one history disclosure. The map and opening milestones remain accessible.
- Search and direct navigation share the same destination catalogue. Chapter 5 is discoverable, chapter pages highlight Castle, and both armoury entry routes highlight Workshop. Breadcrumbs name the actual room or companion.
- Character pages use one title and one character selector. Redundant household drawers and the hidden duplicate development header are removed.
- Research uses one lead selector instead of repeating every resident for every study. Each study still displays the chosen person's exact eligibility. Completed studies and the shared archive are folded by default.
- Equipment selection brings item details above the inventory and moves focus to them. Reviews similarly receive focus. Selected items are highlighted; two-slot items explain which slots they share.
- Equipment owner and workshop worker selectors apply immediately. Loadout management uses one selector and two reviewed actions. Work fields show only what the chosen operation requires; item drafts remain separate. Inventory search submits with Enter and provides Clear filters.
- Transfer, storage and sale occupy a disclosure. Working-tool techniques have their own linked screen instead of reproducing an entire older equipment interface in the armoury. These controls still use the same authoritative item records.
- New transparent engraved Magic and Workshop icons distinguish the primary destinations. Existing room/card art fills seven previously text-only activity cards. Accepted character portraits and expedition illustrations are preserved.
- The layout loses its duplicated horizontal padding, equipment controls wrap on small screens, and result/help dialogs have accessible names. Settings and help no longer describe the game as an outdated early prototype.

See `UI_AUDIT_V083.md`, `UI_AUDIT_V083.json`, `ART_V083.json`, and `VERIFICATION_V083.json` for findings, comparison measurements, image prompts and verification boundaries.

## Upgrade

Stop the previous server. Extract this archive and copy the **complete existing data/ directory**, including campaign subfolders and accepted artwork, into the new game folder. Run `python server.py` and open the printed address. Schema remains 60. No new migration is required. The archive contains no live save data.

Rendered desktop/mobile acceptance remains outstanding: the existing local-browser restriction prevents opening the game. Automated checks exercise templates and controllers, not visual browser layout.
