# v0.54 — Wardrobes and illustrated navigation

Integrated into the game, not a separate art handoff.

- Fourteen authored adult characters each have three distinct portrait files: original, relaxed and daring. Ten defaults were restyled; four recent defaults were preserved. All 28 alternate portraits are new.
- Two new location illustrations: Old service road and castle arrival.
- Eight labelled navigation illustrations: Home, This phase, Estate, Work & study, People, Expeditions, Journal and Settings.
- People → Companion wardrobes previews later outfits, explains blockers, and links to shared scenes and personal stories.
- One distinct remembered moment unlocks the relaxed invitation. Three moments, including a new moment after accepting that invitation, unlock the daring invitation. Accepting unlocks a look; choosing it is separate and free while both people are home. Repeated clicks do not count. Original looks and component/style controls remain available.
- Selected portraits follow characters across identity panels and scenes, persist through reloads, and support imported artwork and rollback independently per look.
- Twelve superseded default files were removed. Their old URLs resolve through compatibility aliases. Room art, object art, personal possessions and imported artwork are preserved.

## Character coverage

## Validation

570 Python tests verified. The last full run passed 569 tests and found one obsolete filename expectation in the local-expansion test. That assertion now resolves the registered artwork path; all eight tests in that module then passed. Earlier stale fixture/rollback expectations were likewise updated to current defaults.

All 30 connected headless UI suites passed, including the new wardrobe progression suite. The containment suite was rerun after updating its two default portrait filename expectations. These are template/controller integration checks, not rendered browser tests.

All 48 new runtime files decode, match their recorded SHA-256 values, and have live artwork slots. Portraits and icons have alpha transparency. A dedicated test verifies 42 different portrait hashes. Compatibility HTTP tests verify old URLs and artwork rollback.

Rendered desktop/mobile checks remain outstanding. The included `scripts/browser_review.cjs` cannot launch here because the Playwright Chromium executable is missing. No rendered-layout sign-off is claimed.

## Upgrade

Stop the server. Use a fresh program folder and retain the complete existing `data` directory. The server backs up the database before upgrading to schema 45. Existing wardrobe styles, relationship memories, art overrides/history, possessions and funded work are retained.

## Artwork records

`ART_INTEGRATION_V054.json` records final prompts, source/runtime hashes and exact runtime filenames. The built-in image generator produced the artwork; runtime WebP exports retain transparency. `art-v054/requests.json` retains the original production briefs. Fenna’s relaxed look uses a buttoned high-collar blouse and long skirt; Neris’s third look uses an opaque violet evening dress. Their in-game descriptions match the final images.

