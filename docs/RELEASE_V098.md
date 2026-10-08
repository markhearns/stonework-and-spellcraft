# v0.98 — Fresh character artwork

Sylva, Velis and Rhess each receive seven newly generated illustrations: three standard portraits, three corresponding room overviews and one contextual bathing outfit. Tamsin and Elowen provide the visual style and quality references. This is a new generation pass, not a resize or lossless re-export of v0.96/v0.97 artwork.

Sylva's skin is visibly celadon green, including her face, hands and feet. Her single pair of leaf ears replaces human ears; subtle natural woodgrain replaces tattoo-like vine patterns. The rejected initial human-toned design is not included. Her written appearance and wardrobe descriptions match the corrected design.

Velis keeps her chocolate-brown complexion, auburn side braid, amber eyes and supply-office association. Rhess keeps her copper scales, horns, single tail, reptilian slit pupils and watchtower association. Rhess wears separate tops and bottoms with an exposed navel throughout. Sylva's room portraits remain in the conservatory. Exterior views depict remote wilderness.

## Game exports

| Asset type | Dimensions | Reference files |
| --- | --- | --- |
| Standard portraits | 1024×1536 | Corresponding Tamsin and Elowen outfits |
| Room overviews | 960×1440 | Corresponding Tamsin and Elowen overviews |
| Bathing portraits | 768×1152 | Tamsin and Elowen bathing portraits |

WebP exports target the size range of the two corresponding reference files, preserving quality within that range and checking the exported detail at native scale. There is no noise filter, sharpening or artificial upscaling. Transparent portraits retain alpha; room overviews are opaque. Exact sizes, encoding quality, reference sizes and hashes are recorded in `art-v098/manifest.json`. The built-in image-generation prompts and source filenames are recorded in `art-v098/prompts.json`.

Image paths and wardrobe-selection behaviour remain unchanged. Bathing outfits still appear only during the existing pool, sauna and hot-spring activity. Custom artwork overrides continue to take precedence. No gameplay rules or save schema have changed; schema remains 65. Stop the old server, preserve the complete `data/` directory and restart after upgrading.

See `VERIFICATION_V098.json` for the checks performed. Browser-rendered game layout review remains outstanding.
