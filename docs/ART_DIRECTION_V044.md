# v0.44 — painted artwork and restrained interface framing

This visual pass uses actual generated raster images. The built-in image-generation tool produced five PNG assets; no font glyph, CSS shape, or procedural SVG stands in for the new item/navigation artwork. CSS selects regions of the generated sprite sheets and sizes them, as it would any supplied game artwork. The originals were copied into the project without pixel edits.

## Visual changes

- Thirteen core crafted objects have individual painted icons, with larger recipe illustrations. Six core materials have individual painted icons in stores and material details. Additional book, key, map, ink, scroll and coin illustrations support navigation and utility contexts.
- The castle emblem replaces the former chess-rook symbol in the brand, title screen, loading screen, navigation and map. It also provides a clearly labelled missing-portrait fallback without inventing a character's face.
- Midnight paper supplies a faint page texture. Ordinary reading panels are solid and separated with thin functional borders. Existing decorative gradient effects are overridden by flat surfaces and the raster texture.
- A transparent botanical frame provides the actual painted corners and edges on selected major surfaces: the title introduction, character overview, castle plan and dialogs. It is deliberately omitted from routine task cards.
- Existing room and character illustrations remain unchanged. Their identities, accepted overrides and clothing variants are preserved. Character portraits now appear once per character within each paragraph/list entry/button, rather than at every repeated mention. Separate entries keep their own portraits.
- Public records use labelled category illustrations when no unique artwork has been accepted. These are representative category images, not claims that every public-pack object has bespoke art.
- Text labels, numerical values, accessible focus controls, functional checkmarks and arrows remain text. Navigation icons and core item images are generated PNG artwork.

## Asset paths and prompts

All five assets live in `static/assets/ui-v044/` in the release:

| Filename | Purpose | Actual pixels |
|---|---|---|
| workshop-atlas.png | 4 × 4 core object and utility sprite sheet | 1254 × 1254, RGBA |
| materials-atlas.png | 3 × 3 material and utility sprite sheet | 1254 × 1254, RGBA |
| midnight-paper.png | Subdued dark-paper surround | 1254 × 1254, RGB |
| botanical-frame.png | Transparent painted panel ornament | 1254 × 1254, RGBA |
| castle-emblem.png | Brand/navigation emblem | 1225 × 1284, RGBA |

The complete final prompt set, transparency requests, dimensions and checksums are recorded in `static/assets/ui-v044/manifest.json`. The built-in image tool was used; no CLI/API fallback or live image-generation service is required to run the game. Artwork remains local to the self-hosted app. The five PNGs total approximately 7.5 MiB; atlases are reused and cached by the browser.

## Verification and limitations

Generated outputs were visually inspected. PNG dimensions, transparency modes and atlas mappings were checked. The new connected UI test verifies raster assets for all core recipes/materials, removal of decorative font symbols, public-category artwork, preservation of editable text, and one portrait per character per independent text block.

All 22 headless UI suites pass, including the long campaign playthrough. JavaScript syntax checks pass. No game rules or save schema changed; the existing Python rules suite was not rerun for this presentation-only release.

Rendered desktop/mobile layout, sprite crops at actual device sizes, border scaling and touch/focus behaviour still require a real-browser review. The available browser could not reach the local game in earlier checks; this release does not claim rendered-browser QA. Source artwork inspection and headless tests do not replace it.

Existing saves, the integrated content packs and original source archives remain intact. Co-op is still deferred.
