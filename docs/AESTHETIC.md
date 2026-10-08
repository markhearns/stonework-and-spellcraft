> v0.50 update: the historical notes below describe earlier releases. Current bundled art uses the approved antique engraving aesthetic; obsolete raster versions and old style-only reference copies have been removed. See ARTWORK_V050.txt and ART_RESTYLE_V050.json. Saved user artwork remains untouched.

# Current project aesthetic prompt

User-defined replacement, 5 October 2026. Use this exact prompt for new project art briefs. It supersedes conflicting rendering instructions in the historical notes below. Existing accepted artwork and character identities remain preserved.

> Natural eye-level perspective. Modest useful stone-and-timber castle, worn objects. Antique engraving–inspired fantasy illustration. Intricate etched linework, fine hatching and crosshatching, subtly worn print texture, and richly detailed aged materials. Historically grounded craftsmanship, understated fantasy, and believable proportions. Midnight navy and charcoal, muted violet, natural wood/plant/fabric colours, sparse dull brass. Dim but readable and welcoming. Avoid palatial luxury, glossy CGI, photorealism, glowing magic spectacle and crushing all detail into black.

---

# Historical art-direction notes

# Art direction: an inhabited archive of practical magic

User-defined direction, 3 October 2026:

> A handmade, enchanted library-workshop: dark academia with warmth, practical magic, and a little knowing mischief.

A place to read, build, keep unusual treasures, and turn complicated things into useful, understandable ones. Mysterious but welcoming; scholarly but alive; magical but useful. Quiet discovery, not theatrical menace. It should feel inhabited and gradually made one's own, not like a pristine fantasy palace.

## Material language

Dark grainy paper, aged archival surfaces, visible graphite underdrawing, imperfect ink contours, small smudges, watercolor and gouache washes, dry-brush edges, and colored-pencil accents. The hand of the maker remains visible. Gold resembles worn book tooling or restrained gold leaf rather than polished treasure.

## Palette and typography

Midnight navy and near-black form the foundation. Warm violet is the signature accent, with ghostly lavender for soft light and archival gold for emphasis. Rose and terminal cyan are occasional personal touches. Natural wood, skin, fabric and plant colors remain themselves; the world is not uniformly purple.

Headings follow the EB Garamond direction; body controls remain clean and legible. The offline CSS uses `"EB Garamond", Garamond, Georgia, serif`. EB Garamond is preferred when installed on the viewing device; the font file is not bundled in this release. There are no external font requests. A future bundled licensed font can replace the fallback without changing the visual hierarchy.

## Implemented in 0.2

- Midnight-paper interface surfaces with a subtle local SVG grain texture.
- Violet selected controls, lavender progress accents, restrained gold actions, and a small cyan-gray technical accent.
- Bookish serif headings and quiet italic marginal notes; clear body copy and visible focus rings.
- Ink-and-wash treatment of all four room illustrations and both character variants. Room geography and the resident's identity remain recognizable.
- Small practical objects and work forecasts connect the magical atmosphere to useful actions.

Avoid glossy CGI, plastic anime finishes, corporate dashboard sterility, excessive filigree, fantasy splash-art clutter, and darkness used as a substitute for personality. Keep grain subtle enough that controls are readable; do not obscure text with decorative scribbles.

> A place where a spellbook and a terminal both belong on the same desk.


## 0.3 correction: modest, dim, inhabited

The user rejected the 0.2 images as **too opulent and too bright**. This constraint supersedes any earlier interpretation that produced grand Gothic interiors or lavish warm illumination.

Room artwork now uses low weathered beams, plain stone, simple small windows, practical scarred tables, a small faded rug, ordinary linen, and localized dim lamplight. No huge ornate carpets, gilt tracery, royal canopies, palace-like conservatories or strong daylight. Worn materials and useful objects supply interest, rather than decorative expense. Character ensembles keep their identity but lose much of their ornate trim; plain teal cloth and a faded violet shawl fit the working household.

The revised art was regenerated from the prior assets using image editing; brightness filters alone were not used to stand in for the structural simplification. Preserve readability and welcoming warmth even in the dimmer palette.


## 0.4 working ledger

The new project panels use the existing midnight paper, narrow violet rules, worn-gold actions, serif headings and clear work counts. The expanded map remains a restrained ink diagram. Existing room and character artwork is preserved; the service spaces use practical ledger controls rather than bright new palace illustrations. Added keyboard focus outlines keep the workbench usable without a mouse.


## 0.5 character notebook

Character sheets, learning plans and the resident project continue the existing archive treatment. The scholar uses a restrained pen mark rather than an invented portrait. Mira’s established artwork remains unchanged. No new bright or opulent images are introduced. The regional diagram gains a fourth map label with alternating placement and a two-column arrangement at small widths.


## 0.6 shelves and research leaves

The new stores and research panels keep the same paper texture, restrained rules, serif headings and small labels. Exact quantities, protected stock and prerequisites remain legible. Utility artifacts use direct controls in their destination rooms; room and character images are unchanged. No bright effects or elaborate new decoration are introduced.


## Character rendering references — 4 October 2026

The four user-supplied images in `character-style-references/` establish the direction for future character rendering. They are art-style references only: do not import their modern clothing, tools, background environments, written lore, or character identities into the game. They do not revise the established modest, dim castle environment direction.

- **Faces and expression:** anime-influenced facial construction with expressive eyes, delicately drawn noses and mouths, subtle blush, and small changes of brows, eyelids and smile that communicate personality. Preserve clearly adult character design and each resident's individual identity.
- **Drawing:** fine dark contours of varying weight, loose overlapping hair strands, lightly sketchlike interior marks, and readable silhouettes. Retain the drawing beneath the paint.
- **Painting:** soft, layered tonal modeling combined with firmer illustrated shadow shapes; fine grain and gentle unevenness within skin, hair and fabric. Avoid plastic skin, hard digital sheen or flat vector-like fills.
- **Light and color on the figure:** natural warm skin against muted dark colors, restrained highlights that describe form, and darker hair masses articulated with individual strands. Adapt figure lighting to the actual dim game scene rather than copying the reference environments or their brightness.
- **Presence:** relaxed, expressive posture and knowing, playful warmth. Expression and gesture should carry personality without relying on copied costumes, props or poses.

The Eris sheet is particularly useful for readable silhouettes and an expression range. The three painted studies guide richer facial modeling, hair detail and tactile surface treatment. Together the target is **fine ink drawing with softly painted, textured anime-influenced character rendering**. These references clarify that anime influence is welcome; the earlier restriction concerns a glossy plastic finish.

For production: retain the resident's established adult identity, choose setting-appropriate clothing separately, use consistent proportions across expressions and outfit variants, and preserve clean transparency for character overlays. Paper texture belongs within the painted figure, without a rectangular background.

The references are bundled for future art work. The existing runtime portraits have not been regenerated in v0.6.


## 0.7 correspondence

Requests are quiet paper panels with explicit quantities; replies use a modest violet rule and bookish text. No ornate seals, bright reward effects or new character illustrations are introduced. The region map makes room for a fourth destination, with a two-column layout on narrow screens. The supplied character references remain the rendering brief for future portrait work.


## 0.8 personal tools and campaign notebooks

Equipment preparation and campaign slots use the same subdued paper panels, serif titles, plain quantities and explicit controls. Focus names and descriptions communicate identity; no new glossy equipment icons or portrait variants are introduced. Character reference guidance remains unchanged.


## Game title

The user selected **Stone and Spell** as the game title on 3 October 2026 (America/Toronto). This replaces the working title in current presentation; it does not rename individual campaigns or reinterpret the original specification.


### Current title and accommodation artwork — v0.10

The current title is **Stonework and Spellcraft**, superseding Stone and Spell at the user's request. Retain the warm, modest archive-workshop direction. The two accommodation extensions reuse the existing dim guest-chamber concept illustration with an explicit interface disclosure. They do not introduce brighter or more opulent interiors or claim bespoke artwork.


### Distinct accommodation illustrations — v0.11

West chamber now shows one plain bed, worn timber and a small writing desk. Garden chamber shows two separate beds, individual storage and subdued fern-facing windows. Both use low amber lamplight, muted violet/navy shadows and a textured painted surface. They replace the default shared bedroom concept while preserving existing image overrides. No brighter or opulent palette pass was applied to established assets.

### Fieldwork and a second resident — v0.12

The observatory is a small, rain-worn weather workshop: dull lenses, a wooden rack, rough stone and restrained lamplight. Tamsin’s portrait uses visible pencil/ink contours and matte gouache, muted work clothes and a plain wool shawl. These additions retain the inhabited, useful and modest direction; no polished palace materials or bright gold spectacle were introduced. Each portrait variant can be reviewed independently without changing character facts.
