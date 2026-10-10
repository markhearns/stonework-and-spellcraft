# v0.108 — Recovered artwork and the magic reference

## What is now available

Open **Magic → Spells & Rituals**. This read-only reference is available from the beginning of a campaign and is linked from both the Spellbook and ritual arrangements.

- 30 castle spells, all eight lasting household circles, the concordant lesson, Lamplit sight and its reversal: 41 castle entries.
- 68 additional workshop spell constructions and 24 workshop ritual studies: 92 workshop entries. The four baseline spell-study duplicates are represented by their live castle spells.
- 133 entries in total. Each has an illustration, an in-character annotation from Scholar Elian Voss, current effect, costs, duration, requirements, limitations, and a link to its action workspace.
- Type filters, collection selector, text search, detail/back navigation, and global navigation-search results. Reference browsing changes no phase, materials, knowledge, relationships or campaign state.

Costs and effects are drawn from executable catalogues. A workshop reference explains its bounded effect; reading its entry does not award a spell or ritual result. Recruitment, arrival and construction procedures remain in People & arrivals.

## Artwork integration

All 77 recovered source images are integrated into the runtime paths: 38 spell/ritual illustrations, 21 equipment icons, 15 bathing portraits and third-outfit revisions for Tamsin, Neris and Maren. Sylva has a newly generated third outfit with a cropped botanical top and short woven-leaf shorts. Each of the four outfit revisions has both standard and overview exports.

There are 82 changed runtime files totalling 7,364,074 bytes (about 7 MiB). Spell/ritual art is 384×384, equipment 256×256, bathing portraits 768×1152, standard outfit portraits 640×960, and overview portraits 960×1440. Alpha and proportions are preserved. The other 15 existing equipment/signature icons remain in the existing set; this release does not claim that they were newly generated. The game contains no full-resolution PNG masters.

Outfit and bathing descriptions now match these revisions. The existing 15-character bathing selection remains tied to a restored pool, sauna or hot spring, being at home, and personal rest. Accepted custom artwork overrides remain authoritative.

## Installation

1. Stop the old game server and back up the complete existing `data/` directory, including campaign subfolders, accepted artwork and provider settings.
2. Extract this release into a clean game directory and copy the complete existing `data/` directory into it, or configure the same external data path as before.
3. Run `python server.py` (or your existing server command with its data path).
4. Hard-refresh the browser. Open **Magic → Spells & Rituals**.

Save schema remains **67**, as in the recovered v0.107. No campaign reset or new migration is introduced. This archive does not contain live saves and does not deploy itself to a hosted server. Frontend cache versions and the server version now identify v0.108.

## Verification

- Three new catalogue/save-preservation tests pass.
- Four asset-release tests pass, covering all 397 runtime files, their declared hashes, served asset URLs and preservation/rollback of custom artwork.
- Six bathing-outfit tests and ten wardrobe tests pass.
- Six connected headless UI suites pass: the new magic reference, bestiary/bounties, 45 overview portrait tiers, character builds, personal paths and wardrobes.
- The reference suite checks all 133 illustrated/quoted details, fresh-game access, filters, search, back navigation, global search targets, action destinations, and unchanged campaign state.
- HTTP smoke check confirms the v0.108 server/frontend, 133 reference entries and successful requests for every referenced magic illustration; the campaign state is unchanged after browsing.
- All 82 changed images decode; JavaScript syntax validation passes.

The wardrobe test contained an outdated schema-66 assertion, also failing in untouched v0.107. It now checks the existing CURRENT_SCHEMA_VERSION (67) while retaining its preservation assertions.

Rendered desktop/mobile browser QA remains unavailable: no browser executable was installed and the browser download failed. No full regression-suite pass is claimed. Historical equipment-playability limitations documented in v0.107 were not changed by this release. The user's hosted server was not modified.
