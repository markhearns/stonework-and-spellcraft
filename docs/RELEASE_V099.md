# v0.99 — Sylva, Velis, Rhess and Iona

All four characters receive seven replacement images: three progressive standard outfits, three corresponding room portraits and one contextual bathing portrait. All 28 images were generated with the built-in image tool and inspected before export.

Sylva, Velis and Rhess use softer, approachable adult faces and more natural proportions, following the Tamsin and Elowen engraving references. Sylva retains green living-sapwood skin, botanical leaf ears, forest-green hair, small blossoms and physical vine strands. Her three conservatory portraits show both bare feet against the floor with contact shadows. Velis remains in the supply office and Rhess in the watchtower.

Iona now has near-black wavy hair, dark horns, pointed ears, warm rose-toned skin and one slender spade-tipped tail. Her expression and progressive outfits establish an alluring adult succubus while preserving her surveyor identity and command-room setting. Her outfit, bathing and new-contact appearance descriptions match the new artwork.

## Installation

Stop the old server. Preserve the complete existing `data/` directory, including every campaign and custom artwork override. Install this version, restore that directory and run `python server.py`.

Save schema remains 65. No gameplay rules or saved relationships, quests, equipment, identities or wardrobe selections are migrated. Previously saved appearance descriptions are preserved; new contacts use the revised description. Custom artwork overrides continue to take priority over bundled artwork.

## Assets and checks

The existing image paths and dimensions remain stable: standard portraits 1024×1536, room portraits 960×1440, bathing portraits 768×1152. WebP exports retain generated transparency where applicable and use quality 90–97 to preserve etched detail while keeping sizes close to the corresponding Tamsin/Elowen references. No sharpening or noise filters were applied.

The full prompt set is in `art-v099/prompts.json`; export sizes, quality settings and hashes are in `art-v099/manifest.json`. `VERIFICATION_V099.json` records image validation and targeted Python and headless UI checks. A browser-rendered game layout review was not performed for this artwork-only release.
