# v0.74 — Illustrated navigation and an engraved landscape

Every previously missing card identified in this update now has artwork:

| Page | Card | Artwork |
|---|---|---|
| Castle rooms & household | Headquarters rooms | Existing entry hall |
| Castle rooms & household | Household ledger | New household ledger still life |
| Castle rooms & household | Stores & plans | Existing warehouse |
| Castle rooms & household | Specialized chambers | Existing dungeon ward |
| Magic | Spellbook | New open grimoire |
| Magic | Rituals | New ritual worktable |
| Adventures | Requests & letters | New correspondence still life |
| Adventures | Castle history | New architectural evidence and old key |
| Workshop | Workshop | Existing workshop interior |
| Workshop | Content workshop | New material sample library |
| Workshop | Focus & equipment | Existing enchanting room |
| Workshop | Workroom notes | New household ledger still life |
| Workshop | Equipment | New personal tools, notebook and focus rod |

Seven new card illustrations use antique engraving linework, restrained parchment, charcoal and violet hues, and practical castle objects. New cards are optimized to 800 pixels wide as WebP quality 82. Cards display their subjects at a consistent 3:2 proportion instead of a shallow top-biased crop. Existing room cards still honor saved artwork overrides.

A new low-contrast monochrome castle landscape inspired by Gustave Doré appears behind the top header, mobile phase/Advance bar, main section-heading banners, and title screen. It depicts a castle above a river and bridge, with wooded slopes and misty mountains. Dark overlays and solid button backgrounds protect control legibility. Detailed content panels retain the quieter paper treatment instead of repeating the landscape everywhere.

The nine added images total approximately 1.39 MiB (exact bytes in `ART_V074.json`). The full inventory is `ASSETS_V074.json`; generation briefs and card mappings are recorded in `ART_V074.json`. All 153 earlier artwork files are unchanged. There are now 162 bundled artwork files. No gameplay, campaign data, portrait selection, or schema rules change; save schema remains 59.

The sidebar and title-screen logo now use a restrained engraved doorway and parchment serif wordmark, guided by `AESTHETIC_PROMPT.txt`: useful stonework, worn timber, practical scholarship, muted violet and sparse dull brass. The previous logo remains available for compatibility. The replacement is optimized to 1200 × 800 WebP with transparency.

## Upgrade and verification

Stop the server and extract this release into a fresh application directory. Preserve your complete existing `data` directory, including `data/assets` and all campaign subdirectories. Run `python server.py` as usual.

See `VERIFICATION_V074.json` for checks. Generated images were visually reviewed, and automated checks verify asset inventory and card wiring. The environment still lacks an installed browser executable, so no rendered desktop/mobile layout review is claimed.
