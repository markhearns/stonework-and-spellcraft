# Codex handoff — Stonework and Spellcraft room art v0.48

## STOP: this is a partial art return, not a completed 34-image delivery

The 30 independent outputs from Batches 1–3 have been preserved and packaged. **Batch 4 is still incomplete.** Do not describe the complete room-art task as finished, and do not substitute later unrelated images or montage crops for the four missing requests.

| Status | Count |
|---|---:|
| Original independent PNGs supplied | 30 |
| Opaque 1600 × 900 WebPs supplied | 30 |
| Candidates pending user review | 28 |
| Delivered candidates blocked by visual findings | 2 |
| Missing compliant Batch 4 images | 4 |
| Formally accepted / activated by this package | 0 |

## Read and verify

Read `manifest.json`, `integration-plan.json`, and `review/QA-REPORT.md`. Open `review/index.html` locally for the individual candidates, full-size master links and recovery links. Optional contact sheets live under `review/contact-sheets/` and must never be used as sources for room assets.

Run `python tools/verify_package.py .` from the package root. The command verifies checksums, expected files, image dimensions, opacity, distinct targets, preserved master hashes and explicit absence of missing assets. It reports technical integrity separately from artwork completeness. `--require-complete` must fail while the four requests are absent. Pillow is required only to rerun the image decoding checks; it is not required by the game to consume WebP files.

## Files and conversion

`masters/<id>.png` contains exact copies of the earlier individual outputs. Their measured dimensions are 1672 × 941. `rooms/<id>.webp` contains 1600 × 900 opaque runtime candidates, converted with Pillow using a tiny centred aspect crop and LANCZOS downsampling, quality 88 / method 6. All processing, byte counts, generation IDs, file IDs and SHA-256 values are recorded per asset. Exact generation prompts, seeds and model-version information were not returned and are null rather than invented.

The original request manifest remains at `asset-requests.json`; the full original written source is preserved under `source-handoff/`. The original reference-image folder and `verification-v048.json` were not included in the user's ZIP.

## Four outstanding requests

- `lower-chamber`: exactly four separate beds in comfortable dry underground housing; privacy screens, personal storage, ventilation and shared reading space.
- `guard-dormitory`: exactly four ordinary beds, privacy screens, personal lockers and sitting nook; no imposed uniforms or residents.
- `ember-chamber-family`: dignified heat-surge care room with heat-safe stone, subtle ward fittings and safe access; no chains, restraints, prison imagery or heat source under the bed.
- `quiet-chamber-family`: dignified echo/oath-isolation care room with soft sound-damping materials and subtle ward fittings; no bars or coercive imagery.

Use `missing-assets.json` and the individual `recovery/prompts/` briefs. Generate one independent full-canvas scene per request. Match original Batches 1–3, not the later photographic/CGI or labelled attempts. Do not relax bed counts or present composites as individual images. Record new source provenance, dimensions and transformations. Update the manifest, review report, checksums and completeness fields only after the actual files exist and pass review.

## Two earlier candidates need correction or an explicit user exception

`dungeons` is blocked because its barred inspection doors read as cells; `gallery-suite-family` is blocked because of the faint lower-right signature/watermark-like text. They remain in this package for comparison and traceability, not automatic acceptance. Do not silently remove these findings or replace them using another generic scene.

## Integration safeguards

Stage candidates for review, not activation. All entries in `integration-plan.json` are disabled. Existing accepted room overrides and all character artwork remain authoritative. Do not bulk overwrite an application's room folder simply because filenames match.

Use only the explicit `assetTargets` from the request manifest. There are 47 distinct current room IDs across 32 mapped requests; 45 IDs currently have candidate files here. The four bedroom families each remain independently overridable per room: the gallery suites and annex suites cover five targets each, upper chambers four, annex chambers five. A representative image must not merge room records, capacities or future override keys.

The Ember and Quiet studies retain empty `assetTargets`. There is no current individual care-chamber art slot in this handoff. Do not invent target IDs or attach their future artwork to a general room without separate integration work.

Do not infer new residents (including the painted dog), pets, ownership, equipment inventories, world geography, factions, compulsory beliefs, mechanics or bonuses from painted props. Preserve game records and saves. The illustration filename is not an authority for lore: for example, the original output named `cozy_dwarven_hallway_nook.png` maps only to `underground-quarters`, not a new dwarven location.

## Acceptance procedure

Review the full-size candidate and its 1600 × 900 runtime at desktop/mobile UI sizes. Check bed counts, privacy, circulation, visibility, icon/portrait overlays, crop, style consistency, text/watermarks and non-prison care intent. Get explicit acceptance before activating a replacement. Keep the existing image for any rejected, missing or unresolved candidate. Preserve per-room override precedence over family fallbacks.

No codebase was edited, no assets were installed, and no runtime UI verification was performed during packaging.
