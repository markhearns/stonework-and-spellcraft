# v0.103 — Status and wording review

## Important information together

- **Home:** crowns, provisions, days supplied, daily food use, automatic buying and Resonance share one panel. Each resource links to its controls. Current work shows up to three projects with progress, working/paused status, requirements, direct project links and validated resume controls. One link opens the full project list; commissions, work routines and companion improvements are next to it. The separate Home pantry panel is removed.
- **Character header:** field health (current vitality, 0–6) and available advancement points appear beside location and current task. Field health is explicitly distinguished from the Vitality attribute in Help.
- **Relationship summary:** trust, affection and respect have individual engraved icons, exact values and native labelled meters. Overview and Relationships use the same summary. It includes the latest score-changing event for that exact pair, romance status, whether invitations are paused, and requirements for the next invitation. The Relationships page keeps preferences, agreements, other companion bonds and history underneath. Repeated score lines, a repeated romance overview and duplicate next-invitation requirements/restore controls are removed. Other companion bonds also use the three icons and meters.
- **Day and phase:** morning, afternoon and evening have distinct icons, with a visible “Now” label and an accessible current-step marker. The day number remains explicit.

## Wording

UI labels prefer equipment set, current task, paid project and chapter project. Work points are distinguished from elapsed phases, so multi-worker progress does not promise an incorrect duration. Help explains these terms, field health, eight chapters and the current Resonance uses.

Romance labels are **Not romantically involved → Mutual attraction → Dating → Partners → Partners · private evening shared**. These describe chosen milestones. A zero relationship score means little recorded history, not dislike; affection may be platonic. No emotional tiers are inferred from numerical thresholds. Pausing invitations keeps recorded milestones. Existing dialogue, memories, milestone requirements and action IDs are preserved.

## Artwork and other useful visual cues

| System | Treatment |
| --- | --- |
| Trust, affection, respect | New handshake, carved heart and laurel icons; exact values and meters |
| Day phases | New rising sun, full sun and crescent icons; current phase named in text |
| Resonance | New engraved lantern icon; current total and gain on Advance |
| Crowns and food | Existing coin and provisions artwork reused beside amounts and supply details |
| Field health | Existing healing artwork reused beside a labelled 0–6 meter and recovery guidance |
| Advancement | Existing book artwork reused beside available training points |
| Projects | Native progress bars, explicit work status, requirements and direct controls |
| Equipment, rooms, chapters and field actions | Retain their existing illustrations and labelled controls; additional decorative icons would repeat information |

All seven new icons use the built-in image-generation tool, following the antique coloured engraving/woodcut style. Prompts are in `ICON_PROMPTS_V103.json`. Final assets and SHA-256 hashes are in `ART_V103.json`.

Full-resolution 1254 × 1254 masters are in the separate optional `stonework-and-spellcraft-icon-masters-v0.103.zip` archive. They are excluded from the game folder and release ZIP. Lossless WebP preserves every decoded RGBA pixel of the generated PNGs, including transparency. The masters total 6,197,538 bytes instead of 9,634,008 bytes for the source PNGs, a 35.7% reduction. Format selection compared lossless WebP with optimized PNG.

The game loads separate 128 × 128 display copies from `static/assets/status/`, shown at 24–48 CSS pixels. These seven files total 89,600 bytes. Their WebP encoding is lossless after Lanczos resampling; downsampling is not described as preserving the full source resolution. Full-size masters are retained separately for future exports. No existing images are recompressed or replaced.

## Verification and upgrading

51 focused Python tests and 11 headless UI suites passed. Checks cover exact relationship-pair history, visible numeric status, controls, milestone gates, pausing/restoring invitations, all character build workspaces, outfit portraits, equipment, chapter actions, project resumption and day progression. New artwork passes pixel, alpha, hash, HTTP byte and MIME checks. A fresh v0.102 campaign and a v0.102 campaign with all four romantic milestones and paused invitations reload with exactly the same stored state. Public views do not mutate either save. All 279 prior art assets are byte-identical.

Save schema remains 65. Stop the old server, preserve the complete `data/` directory, install this release and copy that directory into the game folder. Run `python server.py`. No live campaign data is bundled. Costs, rewards and gameplay progression rules are unchanged.

Rendered browser review remains deferred; headless checks do not establish pixel layout or real browser accessibility. See `VERIFICATION_V103.json` for the exact checks.

## Packaging correction

The corrected v0.103 package removes all seven master images, reducing the extracted game folder by 6,197,538 bytes before small documentation changes. Display assets are unchanged. `scripts/package_game.py` excludes master/source-art directories, artwork outside `static/assets/`, caches and live campaign data. The optional source-art ZIP must stay outside the game folder. If the first v0.103 was already installed, delete `docs/art-v103/masters/` or use a clean extraction and copy over the complete `data/` folder.
