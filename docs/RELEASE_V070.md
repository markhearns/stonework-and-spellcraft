# v0.70 — Organized, smaller artwork

This release reorganizes and optimizes every bundled raster image without changing gameplay. Save schema remains 58; no migration is introduced.

## Asset layout

`static/assets` now contains `portraits`, `rooms`, `locations`, `spells`, `objects`, `ui` and `placeholders`. Version-number directories are gone. Runtime catalogues, constructed spell paths, CSS, HTML, JavaScript and image tests use the organized paths. Lightweight old-URL aliases point directly to the canonical files and store no duplicate imagery.

The 156 raster images use WebP. The two existing SVG placeholders remain vectors. All 38 spell and ritual icons are 192px square, sufficient for their 40–56px display sizes at high pixel density. Object art is at most 256px; navigation images are 128px; the emblem is 192px. Atlas grids and transparency are preserved, with 256px cells for the largest 118px item display. Room and location illustrations retain up to 1600px width; portraits retain their existing full-size presentation, up to 1536px per side.

WebP quality 90, lossless alpha and Lanczos downsampling reduce weight while keeping image composition and proportions. An existing WebP is retained when re-encoding at the target size would make it larger. This is delivery optimization of the accepted artwork, not regenerated artwork.

## Size results

Decimal MB/KB are used here.

| Content | Before | After |
| --- | ---: | ---: |
| Runtime artwork | 153.16 MB | 39.29 MB |
| 38 spell/ritual icons | 75.00 MB | 0.633 MB |
| Average spell/ritual icon | 1.97 MB | 16.7 KB |
| Historical source images bundled under docs | 94.58 MB | Omitted from runtime package |

Original source images and references remain available in the complete v0.69 archive. Historical textual manifests are retained for provenance, and `ASSET_OPTIMIZATION_V070.json` records each current path, source path, dimensions, bytes and hashes. See `ASSET_GUIDE.md` for the policy for future artwork. Source art should not be copied back into the runnable distribution.

## Verification

All 156 raster images decode. Aspect ratios are preserved, and all 108 images with alpha retain their resized alpha channels exactly. Representative portrait, room, atlas and spell-icon comparisons were inspected at display size without a material visible difference. This is not a rendered browser UI review.

Automated checks verify every current game asset and legacy alias is served, image MIME types are correct, no version-named asset directories remain, and spell icons stay within their new size budget. Full rule and connected UI regression results are recorded in `VERIFICATION_V070.json` and `UI_REGRESSION_V070.json`. Rendered browser review remains unavailable in this environment.

## Install

Extract this release into a **fresh application folder**, then run `python server.py`. Simply overlaying an older installation leaves its unused version folders and source images on disk, defeating the cleanup. No existing saves need transferring at this development stage. The ZIP contains no campaign data.
