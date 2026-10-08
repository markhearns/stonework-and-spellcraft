# v0.79 — Closer company

The splash landscape now covers the full viewport with its proportions preserved. Companion Overview pages put a new full-body conversational portrait on the left and existing overview information on the right, in equal columns. Narrow screens stack the portrait above the information without cropping it.

Kaede's corrected direction is a fit hourglass figure with a full bust, defined waist, rounded hips and subtle muscle definition. Her written appearance now reflects that direction. Her oni identity, clothing progression and training-yard association remain intact.

The artwork expresses growing warmth and ease across the existing wardrobe progression. Viewing a portrait does not unlock clothes, change affection or advance time. Accepted custom portraits take precedence; rolling an override back to its original image lets the new overview portrait appear. Unknown or generated residents retain their own artwork or a fallback.

The 42 new images are optimized WebP files under `static/assets/portraits/overview/`. `docs/ART_V079.json` records room mappings, sizes, checksums and available generation prompts. All images use the built-in image generator. Thirty completed portraits were recovered after the working files were lost; their original prompt text was not recoverable and is explicitly marked null.

No save schema change. Keep the complete existing `data/` directory, including `data/assets/`, when upgrading. Older bundled artwork and asset URLs remain available.

Automated verification results and limitations are in `docs/VERIFICATION_V079.json`. Headless UI tests verify controller behavior and markup, not rendered desktop/mobile appearance.

