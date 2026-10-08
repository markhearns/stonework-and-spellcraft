# v0.73 — Branding, surfaces and portrait alignment

The engraved game logo now replaces the castle emblem, separate game-name text and tagline in the top-left sidebar. The title-screen logo remains. On narrow screens the sidebar logo is visible alongside Navigate.

The top bar and mobile phase/Advance bar now use the existing midnight-paper artwork with shaded navy layers and a muted brass dividing line. Main panels, dialogs and companion cards receive a quieter version of the same texture; nested panels remain plain. Companion tabs have a subtle shaded backing.

Full-body portraits in companion headers, cards and castle-life rows now fill their own frames consistently. Previously, the header placed a 110 × 150 image at the top left of a 144 × 180 frame; narrow-screen rules also disagreed about the frame and image sizes. Frame dimensions now match their intended presentation, while images fill the frame using centered containment. Wardrobe images explicitly retain centered containment. No artwork is cropped, repainted or replaced.

Inline character-name text now uses the normal sentence baseline. The old rule applied middle alignment to both the portrait badge and the text span, pushing names out of line. Portrait badges retain their separate middle alignment.

## Compatibility and upgrade

Schema remains **59**. Gameplay, headquarters jobs, campaign progress, custom artwork and all **153 bundled artwork files** are unchanged from v0.72. The asset inventory remains `ASSETS_V072.json`.

Stop the server, extract into a fresh program directory, and retain your **complete existing data directory**, including `data/assets` and every campaign subdirectory. Run `python server.py` or point it to the existing data directory with `--data-dir`.

## Verification

See `VERIFICATION_V073.json`. JavaScript syntax and the existing affected UI controller checks were run. This environment still has no installed browser executable, so these checks do not constitute rendered desktop/mobile verification. The CSS corrections follow the identified frame-size and baseline conflicts; no screenshot-based sign-off is claimed.
