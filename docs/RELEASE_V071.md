# v0.71 — Character portrait cleanup

The fourteen authored companions now each have exactly three portrait files: `<name>.webp`, `<name>-outfit-2.webp` and `<name>-outfit-3.webp`, all in `static/assets/portraits`.

Six extra portraits were still referenced by older features: Mira and Tamsin’s shawl images, Aurelia and Neris’s evening images, and their lamplit/glasslight scene images. Their consumers now reuse the canonical portraits, and the six redundant files and review slots are removed. Personal scenes remain intact. A scene records the selected illustrated outfit when shared. Descriptive garment choices and saved styles remain available, but no longer promise a separate illustration; the UI explains this distinction. Historical URL aliases resolve without storing duplicate images.

Relaxed and daring portraits retain their existing relationship invitations. Choosing a descriptive shawl or ensemble does not unlock those portraits. Character appearance descriptions and outfit descriptions now match the new artwork. No gameplay attributes, quest rewards or spell rules changed; schema remains 58.

## Delivery

Generated artwork was edited using the built-in image generation tool, reviewed as complete sets and as Brakka face details, then delivered as transparent WebP at quality 90, maximum 1024 × 1536 pixels for the new images. Existing optimized images were not re-encoded. Generation drafts and source PNGs are not bundled. Selected prompts and final asset paths are in `PORTRAIT_PROMPTS_V071.json`; the full current inventory is `ASSETS_V071.json`.

Extract this release into a fresh application directory to avoid retaining deleted images from an older release. Run `python server.py`.

## Verification

See `VERIFICATION_V071.json` and `UI_REGRESSION_V071.json` for test results. Artwork was visually inspected in contact sheets and facial close-ups. UI checks use template/controller integration and a DOM test double; no rendered browser review was available in this environment.

