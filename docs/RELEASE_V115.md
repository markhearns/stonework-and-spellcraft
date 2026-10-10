# v0.115 — Artwork, card layout and clearer task guidance

The complete game retains v0.114’s chapter progression, Zahra identity and smithy association, companion dialogue, friendships and ritual mechanics. Save schema remains 72.

- Iona and Zahra have revised opaque two-piece bathing outfits. Zahra’s third outfit is an indigo halter crop top and asymmetric wrap skirt. Display art and outfit descriptions match.
- The First Real Test, External commissions and Foundation ritual chamber navigation cards now resolve to existing artwork. The same audit fixed Resident friendships, Practical companion projects and Follow-up conversations. All 44 navigation cards have artwork in both fresh and demonstration games.
- Foundation chamber ritual has its own transparent engraved icon in Spells & Rituals. Navigation to the room continues to use the room illustration.
- Rooms to visit cards now share one 3:2 frame and top alignment. Headquarters and system cards keep their aspect ratios without image shrinking; field-patrol card illustrations use consistent frames. Prepared magic uses the same illustrated background treatment as equipment.
- Unavailable work explains the specific missing project, completed work or absent character and provides a direct setup link. Research says that no study is underway and opens Research. Opening this explanation never assigns work or spends resources.
- Mira’s full portrait appears beside the library, conservatory and conversation scenes. Opaque portrait backgrounds are no longer placed over room illustrations. The layouts stack on narrow screens.
- Removed 263 generated cache files (5,504,999 bytes). Preserved 112 obsolete or duplicated handoff files (2,857,095 bytes) outside the game in the companion source archive. Active runtime content bundles and canonical references remain. See `CLEANUP_V115.json` and `SOURCE_ARCHIVE.md`.

The full castle map replaces the six-slot sample. It covers 61 locations across ground floor, upper floor, lower level, grounds and annex. Stairs and passage buttons change the displayed level. Unrestored rooms show rubble; funded repairs show current progress and whether work is paused; ready rooms show their interiors. The foundation chamber and survey rooms remain ??? until their investigations identify them. Each discovered location opens its existing room or construction controls. Open **Castle rooms & household → Castle map**, or the expandable map on Home.

Help now covers the map, task setup, current chapter order, Zahra, resident bonding and the exact foundation blessing. Cheats can fit containment chambers without completing their care cases. The foundation room is listed only after its maintenance ledger is read; its construction shortcut updates the actual restoration record and retains both circuit tests and ritual eligibility. Ordinary generated residents use the same 51-person household limit as the game. These shortcuts are covered by transaction and reload checks.

## Install

Extract this full ZIP into a clean folder. If you have a save to keep, copy the complete `data/` folder from your existing installation before starting the new server. Run `python server.py`, open `http://127.0.0.1:8080/`, and hard-refresh the browser. Confirm v0.115 in the title screen or `/api/health`. This package has not been deployed to a hosted server.

## Verification

43 Python tests and six connected UI suites pass. Additional checks cover 88 navigation-card instances across fresh/demo states, 14 assignment-help destinations, three room/conversation DOM layouts and all artwork files. The research explanation → setup → begin research → available assignment flow passes without an unintended mutation. All 394 unrelated runtime images are byte-identical to v0.114; four display files changed and a ritual icon and rubble texture were added (400 total).

Image assets were visually inspected. UI template structure, routes and stylesheet rules were checked; rendered desktop/mobile layout remains unverified because no browser renderer is installed. Details are in `VERIFICATION_V115.json`.

## Source archive

`stonework-and-spellcraft-source-archive-v0.115.zip` contains exact full-resolution masters, successful generation prompts, hashes, archived handoffs and the additional verification script. Only lossless display-sized WebP assets ship inside the game.
