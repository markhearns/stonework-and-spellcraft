# v0.96 — Sylva redesign and handmade portraits

Sylva has been redesigned as a beautiful adult dryad of 21. Her new identity has forest-green wavy hair, amber-gold eyes, leaf-shaped ears, ivory blossoms, a small crown of budding twigs, and delicate living woodgrain. She is barefoot in every outfit. Appearance, almanac and wardrobe descriptions match the new design; personality, quests, relationships, advancement and the conservatory bonus are unchanged.

The release replaces 21 bundled images: seven each for Sylva, Velis and Rhess. Each set contains three transparent outfit portraits, three full-body overviews in the associated room, and one transparent bathing portrait. Velis and Rhess retain their established identities and outfits. Rhess retains vertical slit pupils, horns, scales, a tail and two-piece outfits with a visible navel.

The new artwork uses visible etched lines, contour hatching, irregular ink marks and restrained colour washes to restore the handmade print finish. Overview backgrounds remain the conservatory, supply office and watchtower. Exterior views show remote wilderness rather than other castles or settlements. Bathing images continue to appear only during personal time in a restored pool, sauna or hot springs.

All assets are optimized WebP files at the existing game paths. Cutouts retain alpha transparency. Overview images are 960×1440; transparent portraits are 768×1152. The current package contains no superseded image copies. Save-owned custom art remains governed by the existing override controls. No save schema change or gameplay rebalance is included.

Artwork was generated with the built-in image-generation tool, then resized and encoded for the game. The final prompt set and asset checksums are in `art-v096/prompts.json` and `art-v096/manifest.json`.

Verification covers the 21 replacements, transparency, dimensions, image references, authored Sylva appearance updates, outfits, bathing contexts and the almanac. Existing headless UI checks cover all 45 normal portrait tiers, wardrobe selection and artwork integration. Individual image inspection was performed; browser-rendered layout review remains outstanding. See `VERIFICATION_V096.json` for results.

Run `python server.py`. Preserve your complete existing `data/` directory when upgrading. The game remains on schema 65.
