# v0.74 update

Current asset inventory: `ASSETS_V074.json`. Seven new 800 × 533 card images and a 2048 × 683 castle landscape use WebP quality 82, method 6. Full prompt briefs, card mappings, exact byte sizes and optimization settings are in `ART_V074.json`. No source PNGs are bundled and all prior artwork remains unchanged.

---

# v0.72 update

The title-screen logo is `static/assets/ui/stonework-and-spellcraft-logo-v072.webp` (1536 × 1024, transparent WebP quality 90). The existing castle emblem is retained. The current inventory is `ASSETS_V072.json`; `LOGO_V072.json` records the generation brief. All 152 v0.71 assets are unchanged.

---

# Runtime artwork

Store images by purpose under `static/assets`, never by release number:

| Directory | Content | Delivery size |
| --- | --- | --- |
| `portraits/` | Exactly three portraits per authored companion | Preserve existing proportions, up to 1536px per side |
| `rooms/` | Castle interiors | Up to 1600 × 1000px, usually 1600 × 900 |
| `locations/` | Expedition destinations and arrival scenes | Up to 1600 × 1000px |
| `spells/` | Spells and ritual icons | 192 × 192px for 40–56px UI display |
| `objects/` | Equipment, food, materials, furnishings and projects | Up to 256 × 256px |
| `ui/` | Navigation, icon atlases, texture, emblem and border | Navigation 128px; emblem 192px; paper 900px; frame 512px; 4×4 atlas 1024px; 3×3 atlas 768px |
| `placeholders/` | Existing vector placeholders | SVG |

Use descriptive stable filenames. Keep gameplay asset IDs unchanged. New portrait variants belong beside other portraits, not in a release-specific folder. Keep originals and generation references outside the runtime distribution; v0.69 is the original-source archive for this optimization pass.

For raster delivery use WebP at quality 90 with lossless alpha. Preserve aspect ratio, transparency and composition; use Lanczos downsampling, never upscale. The icon atlases retain their exact grid layout, providing 256px cells for the largest 118px UI presentation. Keep an existing WebP if re-encoding it at the target dimensions makes it larger. Review a representative before/after comparison at display size before accepting compression. Do not repeatedly re-encode optimized files for later releases: work from original sources when another size is needed.

Update `art_catalogue.py`, `room_art.py`, the spell path construction in `game.py`, and direct UI references when adding artwork. `asset_aliases.py` contains lightweight legacy URL mappings only; no duplicate image files are required. Tests verify every current asset slot and alias is served with the correct image MIME type. `docs/ASSETS_V071.json` is the current inventory and checksum manifest. `docs/ASSET_OPTIMIZATION_V070.json` records the earlier optimization pass. Use `<name>.webp`, `<name>-outfit-2.webp` and `<name>-outfit-3.webp`; scene illustrations reuse these portraits. Selected artwork generation prompts are recorded in `docs/PORTRAIT_PROMPTS_V071.json`.

The historical artwork manifests describe original releases and are retained as provenance, not as current paths or checksums. Their large source images are available in `stonework-and-spellcraft-development-v0.69.zip` and are intentionally omitted from v0.70. Pillow was used for the one-time image conversion; running the game does not require Pillow.
