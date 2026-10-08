# v0.97 — Portrait compression fix

The v0.96 lossy export damaged the fine engraving texture in Sylva, Velis and Rhess's portraits. Comparing each default portrait with its source resized to the same 768×1152 dimensions showed blotchy colour and lost ink detail in the exported WebP. The dimensions alone do not explain the problem: artwork can look good at 768×1152. This release removes the verified compression damage and also retains the native source resolution.

All 21 portraits are now rebuilt from their original generated PNGs at their native 1024×1536 resolution. Lossless WebP reduces file size without changing any visible colour or alpha value. The character designs, poses, outfits, associated rooms and game image paths are unchanged. There is no regeneration, artificial upscaling, sharpening or painted-in detail.

The image manifest records source PNG hashes, source and decoded pixel hashes, native dimensions and final file hashes. Pixel comparison normalizes RGB only in fully transparent pixels, which cannot be seen; every alpha value and every visible colour channel must match the source exactly. All 12 cutouts preserve transparency, and all nine environmental overviews remain opaque.

Files are intentionally larger than v0.96. Future portrait exports should preserve native resolution and use lossless encoding when fine ink detail matters. Keep display thumbnails separate from the full-detail portrait source rather than replacing that source with a smaller image.

This is an artwork quality correction. No gameplay, save schema, wardrobe selection or custom artwork override behaviour has changed. Schema remains 65. Preserve the existing data directory when upgrading and restart the server.

The final quality manifest is `art-v097/manifest.json`; the original generation prompts remain in `art-v096/prompts.json`. See `VERIFICATION_V097.json` for checks. Browser-rendered layout review remains outstanding.
