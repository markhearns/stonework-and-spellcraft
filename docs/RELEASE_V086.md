# v0.86 — Character artwork consistency

Audited all 90 illustrations for 15 residents, three outfits and two formats. Replaced 36 images; 222 other runtime images remain byte-identical to v0.85.

- Corrected raised footwear in the affected Velis, Aurelia, Kaede, Fenna, Mira, Sabine, Brakka, Maren and Neris variants.
- Softened Velis, Aurelia and Fenna facial treatment while retaining clearly adult identities and ancestry details.
- Replaced Velis's three opaque square crops with genuine transparent full-body portraits. Her three Supply Office overview illustrations remain separate.
- Optimized all replacements to WebP, preserving real alpha in all 18 cutouts. Replacement assets total 8,382,756 bytes.
- Added permanent character art direction and flat-footwear constraints to future portrait briefs; resident briefs specify youthful adult faces. Founder details remain player-authored.
- Artwork verification now resolves the latest manifest by asset path, retaining historical manifests rather than rewriting old checksums.
- Corrected the welcome dialog's chapter count to six.

Generation used built-in image_gen. Exact prompts, source filenames, dimensions and checksums are in ART_V086.json. Rejected drafts are not bundled.

Validation: 52 Python tests across six focused suites and four headless UI suites passed. All 258 runtime assets passed hash/use checks. Portraits were visually reviewed separately; rendered browser layout was not reviewed. No campaign mechanics changed; the full gameplay suite was not rerun for this artwork release.

Keep the complete existing data directory when upgrading. Schema remains 61. Save-owned accepted artwork and its history are preserved.
