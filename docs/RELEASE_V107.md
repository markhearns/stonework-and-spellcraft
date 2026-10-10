# v0.107 — Portrait overhaul and expanded field guide

- Replaced all 45 established resident outfit portraits and their overview versions with detailed engraved illustrations. Neris uses translucent water-elemental anatomy; Sylva has living wood and leaf anatomy; Tamsin has cat ears and a narrow feline tail.
- Added flint-beak cockatrice, barrow badger, rimewing bat, siltback tortoise, brass-wing scarab and gloam jelly, bringing the catalogue to 20 creatures. Each has an encounter, peaceful approach, patrol pool, bounty and rare component connected to advanced crafting uses.
- Added 41 concrete observations by Scholar Elian Voss to creature and ancestry detail illustrations.
- Added 20 separate transparent material icons and corrected provisions basket transparency.
- Added five subdued monochromatic engraved motifs to Techniques and Passives, selected by ability theme. Equipment retains its item illustration over a faint shield background.

## Installation
Stop the game server, extract this archive over the existing application folder, then restart the server with the same data directory. Preserve your existing data folder and provider settings. Refresh the browser after restarting. This archive contains no live campaign saves. Existing accepted custom portrait overrides remain authoritative.

## Verification
Passed: 11 bestiary/bounty tests; four asset-release tests (including all runtime asset hashes, served URLs, and preservation of custom overrides); connected headless UI suites for bestiary, builds, personal paths, equipment ownership, and all 45 overview portrait tiers. All 128 changed raster images decode; all 20 material icons and the provisions basket contain transparent pixels. JavaScript syntax check passed.

Limitations: rendered desktop/mobile browser testing was unavailable because the browser executable is absent. The older equipment-playability suite fails the same `Stow Road <boots>` text assertion in both the untouched 0.106 baseline and this version. A broad Python suite was interrupted without a final result; no full-suite pass is claimed.
