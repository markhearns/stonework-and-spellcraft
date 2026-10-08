# Stonework and Spellcraft — Room Art Return Handoff v0.48

This return package contains all 34 requested room-art images as **independent image files**. No composite-sheet crops are used as masters.

## Contents
- `masters/<id>.png` — generated PNG masters at their actual native dimensions.
- `rooms/<id>.webp` — 1600×900 opaque runtime WebP files using the exact paths/IDs requested by `asset-requests.json`.
- `manifest.json` — target mappings, dimensions, processing, SHA-256 hashes, provenance notes, unresolved issues, and review status.
- Original specification files are included for Codex reference.

## Integration instructions for Codex
1. Read `manifest.json` and `asset-requests.json`; use the exact IDs and runtime paths.
2. Treat all images as **generated/pending integration review**, not automatically accepted canonical overrides.
3. Preserve character art and any currently accepted per-room overrides unless Mark explicitly replaces them.
4. Generic family art may map to several room IDs as listed in `assetTargets`; retain the ability to override each room independently later.
5. `ember-chamber-family` and `quiet-chamber-family` intentionally have no current `assetTargets`; keep them as future integration art unless a chamber-art slot has since been added.
6. Do not infer new lore, residents, ownership, mechanics, religion, heraldry, or gameplay facts from incidental painted props.
7. Runtime images are already web-ready 1600×900 WebP. Do not upscale or re-export masters as though they were higher-resolution originals.

## Batch 4 corrections incorporated
- `lower-chamber`: underground, no windows; exactly four separate beds; privacy/storage/ventilation/shared reading area.
- `guard-dormitory`: exactly four ordinary beds with privacy/storage and sitting space.
- `ember-chamber-family`: underground, no windows, **no wood and no plants**; heat-safe stone/metal construction and restrained ward fittings.
- `quiet-chamber-family`: underground, no windows; soft sound-damping treatment and restrained ward fixtures.

## Known source-material limitation
The original ZIP referred to six files under `references/`, but those reference images were not present in the supplied archive. The affected replacements were therefore generated from the written briefs and established project style rather than direct visual comparison. This is recorded per asset in the manifest.
