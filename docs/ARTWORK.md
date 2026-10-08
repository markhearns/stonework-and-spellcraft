> v0.50 update: the historical notes below describe earlier releases. Current bundled art uses the approved antique engraving aesthetic; obsolete raster versions and old style-only reference copies have been removed. See ARTWORK_V050.txt and ART_RESTYLE_V050.json. Saved user artwork remains untouched.

# Bundled artwork

Generated using the built-in image-generation tool for this prototype. Generated PNGs were encoded as WebP for local delivery; portrait transparency was retained. Room and character art can be replaced through the illustration review UI. The existing runtime artwork predates the user-provided Eris and Selene style references; Mira is a distinct sample character.

| Project path | Use |
|---|---|
| `static/assets/common-room.webp` | Common-room background |
| `static/assets/library.webp` | Research-library background |
| `static/assets/bedchamber.webp` | Guest-chamber background |
| `static/assets/mira.webp` | Sample resident in base ensemble |
| `static/assets/mira-shawl.webp` | Same resident with outer garment |

## Common room prompt

Use case: stylized-concept. Asset type: landscape background for an illustrated fantasy household RPG. Create a beautiful welcoming ancient castle common room at natural eye level, wide 3:2 composition. Hand-painted ink, watercolor and gouache on textured paper, refined adult fantasy concept illustration. Stone vaulted ceiling, tall mullioned window to left with lush enchanted trees outside, bookcases and deep plum drapery, warm fireplace on right, small candles, golden late afternoon light, midnight teal shadows, muted brass. IMPORTANT center foreground is open with a wide empty patterned rug: furniture variants will be layered there by the game. No people, no text, no UI, no watermark. Tactile painterly detail, quiet occult academia atmosphere, coherent straight architecture.

## Mira prompt

Use case: stylized-concept. Asset type: transparent full figure character asset for a fantasy household RPG. Single fictional unmistakably adult woman age 32, sample character Mira, a confident warm-hearted magical archivist. Mature proportions, expressive hazel eyes, wavy shoulder-length auburn hair, subtle mischievous closed-mouth smile. Elegant deep teal fitted long dress with tasteful sweetheart neckline, full opaque coverage, brass clasp and long flowing skirt with a modest side slit, ankle boots. Standing relaxed in three-quarter view, one hand holding a closed old book at her waist, other hand resting naturally. Exactly two arms and hands. Hand-painted ink and gouache illustration, textured brush edges, beautiful expressive face, subtle colored-pencil detail. Warm light from right. Whole figure from head to feet with margin, no cropping. Transparent background. No environment, no words, no symbols around figure, no second figure.

## Bedchamber prompt

Landscape 3:2 fantasy RPG room background. An intimate castle bedchamber, natural eye-level straight perspective. Hand-painted ink and gouache, textured paper, muted plum, warm brass, deep teal shadows. Canopied bed on right, arched forest-facing window left, warm stone, wood beams, layered opaque linen and plum blankets, candles and a modest vanity. Foreground clear rug for furniture overlay. No people, text or UI. Rich textured detail with welcoming dark-academia warmth, consistent with an old magical castle, never photorealistic.

## Library prompt

Landscape 3:2 fantasy RPG room background. An ancient castle research library, natural eye-level perspective, welcoming not threatening. Hand-painted ink and gouache, visible paper texture, dark-academia warmth. Tall wooden bookcases, a large central reading table with books and unlit brass apparatus, stone gothic arch window, green garden beyond, plum curtains, warm gold lamps, midnight teal shadows. Clear foreground for furniture overlay. No people, text or UI. Refined illustrative detail, not photo.

## Shawl variant prompt

Edit only the clothing accessory of this same adult fantasy archivist for an RPG wardrobe variant. Preserve her exact face, auburn hair, anatomy, pose, book, teal dress, full-body framing and painting style. Add an elegant opaque wine-plum shawl draped evenly around her shoulders and upper arms, fastened near collarbone with a small brass clasp. Keep the same silhouette and dress elsewhere. Transparent background. No new person, text or environment. This is the same person with a shawl added.

Input: generated Mira base portrait. The image tool received the original PNG as its edit target, with transparent output enabled.


## 0.2 art pass

Added `static/assets/conservatory.webp`, generated with the built-in image tool as a natural-eye-level restored stone-and-glass greenhouse with herbs, silver ivy, a potting bench and clear central walkway. Palette: muted brass, midnight teal, plum and warm light, with no people or lettering.

All four room assets and both Mira assets then received an image-to-image style pass with the built-in tool. Final paths remain the six named WebP files in `static/assets/`; no live image service is required. PNG outputs were encoded as WebP without changing image content.

Style-pass prompt template:

> A careful style and surface-treatment pass on this existing [adult character portrait / castle room illustration] for a handmade enchanted library-workshop RPG. Preserve [the exact adult woman's identity, auburn hair, expression, facial proportions, pose, opaque clothing, accessories and full-body composition / the room's exact architecture, perspective, object placements, recognizable furniture, paths and composition]. Change the rendering substantially from polished realism to clearly handmade illustrative art: visible graphite underdrawing, fine imperfect ink contours, watercolor and gouache washes, broken dry-brush edges, colored-pencil accents, subtle smudges and textured dark archival paper within painted areas. The hand of the maker must be evident; more artist's working sketchbook than fantasy splash art. Midnight navy and near-black shadows, warm violet accents and soft ghostly lavender highlights, restrained worn archival gold rather than shiny metal. Keep natural skin, wood, plant and fabric colors and warm welcoming light; do not tint everything purple. Quietly magical, warm, inhabited, useful, and a little mischievous. No glossy CGI, plastic finishes, pristine palace sheen, added filigree, words, letters, signatures, logos, or watermark.

Portrait suffix: Keep a clean transparent background outside the character, remove any stray background glow or blocky residue; paper grain belongs INSIDE the character paint only.
Room suffix: Keep the image filled edge to edge; no text or new frame.

The code-native `paper-grain.svg` supplies subtle interface grain. Furniture overlays and the lantern remain small provisional vector assets.


## 0.3 replacement pass: lower opulence and brightness

All six current WebP assets were edited using the built-in image-generation tool, then encoded locally for the self-hosted app. Paths remain unchanged, so no runtime downloads are needed.

Shared prompt direction: The current result is TOO OPULENT AND TOO BRIGHT. Substantial redesign toward modest everyday comfort and useful worn objects. Dramatically lower overall illumination: mostly deep midnight navy and charcoal shadows with only small local pools of dim warm lamplight. No strong daylight, sunbeams, glowing gold surfaces, white highlights, saturated orange wash or shiny luxury. Warm violet ink accents, ghostly muted lavender, sparse dull archival gold. Preserve readable forms and welcoming quiet warmth. Very visibly hand-drawn fine ink contours, graphite sketch marks, dry-brush gouache, thin watercolor, grainy dark handmade paper texture. Not photorealistic or glossy CGI. No writing, watermark or UI.

Asset-specific changes:

- Common room: low timber-and-stone ceiling, modest plain left window, worn shelves, small right hearth, no huge ornate carpet or gilt tracery; clear central overlay area.
- Library: low rough beams, plain uneven book shelves, scarred central oak table, practical tools and one narrow window; remove busts, towering vaults and palace ornament.
- Bedchamber: simple wooden right-hand bed, plain charcoal linen and faded violet blanket, narrow left window and small stool; no ornate canopy, gilded mirror or royal carpets.
- Conservatory: small lean-to greenhouse, weathered timber, plain glass, stone half-walls, central path, useful herb beds, ivy and a scarred right-hand workbench; no palatial arches or complex tracery.
- Mira: preserve the same adult face, auburn hair, proportions, pose and identity; plain practical teal cloth, worn leather book and small brass clasp; remove decorative gilding/brocade. Retain full figure and transparent background.
- Mira with shawl: same treatment, retaining a plain faded violet wool shawl without embroidery.


## User-provided character style references

Original reference copies are bundled in `docs/character-style-references/`:

- `eris-character-sheet-library-workshop.png`
- `eris_study_01.png`
- `selene_study_01.png`
- `selene_study_03.png`

These are user-supplied references, not generated prototype assets or runtime portraits. Use their character rendering style only. Modern clothing, tools, background environments, sheet text and identities are outside this instruction. See `AESTHETIC.md` for the adopted rendering brief. Current room and Mira assets remain the v0.3 artwork.


## v0.11 accommodation artwork

`static/assets/west-chamber.webp` and `static/assets/garden-chamber.webp` are new distinct generated interiors, inspected before integration. They were produced with the built-in image generation tool and converted from its PNG outputs to WebP at quality 90 without cropping or repainting. Existing accepted artwork overrides remain authoritative. The prompts and workspace asset paths are recorded in `ARTWORK_v0_11_PROMPTS.md`. Original generated PNGs remain outside the distributable; the app includes optimized local WebP assets and needs no generation service at runtime.

## v0.12 fieldwork and resident artwork

Rainward observatory, Tamsin’s work clothes and her matching shawl variant are bundled local WebP assets. Full prompts and generation provenance appear in `ARTWORK_v0_12_PROMPTS.md`. All three were directly inspected. Tamsin is an authored adult sample identity, not a copy of the supplied style-reference characters.
