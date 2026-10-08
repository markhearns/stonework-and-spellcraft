# v0.104 — Useful images and clear visual status

## Equipment comparisons

The review panel now places stowed and equipped item pictures side by side. Multi-slot items appear once, so a dress or two-handed weapon is not counted twice. Empty slots reuse muted illustrations of the relevant equipment type and retain the “Empty” label.

Active enchantments have a before/after comparison with readable names and rank or route-bonus values. Changes to patrol damage and cover supplied by equipment are shown separately from skill, party and action bonuses. The preview and patrol actions share the same equipment calculation. The comparison preserves group limits and the rule that physical armour and shields do not double the same protection bonus. Blocked actions claim no equipment changes, and confirmation still uses the existing validated action.

## Temporary effects

Spell summaries and character overviews show the spell artwork, affected character, exact effect and remaining uses. Work enchantments count matching work phases, which remain available through unrelated phases. Field effects count matching field uses and end on return. Empty or spent field effects are hidden. A character’s overview shows that character’s effects. Permanent rituals remain separate.

## Advance preview

Resource cards display current total, expected total and gain or expenditure. Crowns, materials, provisions and Resonance use their existing artwork. Food and Resonance changes are calculated by the same simulated Advance that already drives the preview. Project bars show current and expected progress, with explicit labels for finishing, progressing or paused work. A blocked Advance shows its requirement instead of speculative changes.

## Tasks, invitations and castle rooms

Ready actions use a wax seal, paused work a resting hourglass, decisions a forked signpost, and invitations a sealed letter. Working projects reuse the repair-hammer illustration. Each marker includes a plain-English label; colour is never its only meaning.

The existing floor plan and room cards show construction or paused work, available unshared conversations and current occupants. Markers use the same public room and activity data as the existing room screens. Already-shared and unavailable conversations do not increase the count. Rooms still open through their existing controls.

## Journal and discoveries

Known expedition locations have thumbnails. Remembered scenes use their recorded room when available. A Crafted artifacts filter lists actual artifact holdings with existing item illustrations and links to their recipes. Return reports reuse the visited location artwork. Existing portrait identities, search, pagination and record controls remain available. No future discoveries or scenes are added by the visual layer.

## Artwork and packaging

Four new icons were generated with the built-in image-generation tool in the established antique engraving/coloured woodcut style: ready, paused, choice and invitation. They use etched linework, worn materials, muted natural colours, dull brass and violet. See `ICON_PROMPTS_V104.json` for the full prompts and `ART_V104.json` for hashes and dimensions.

The game contains only 128 × 128 losslessly encoded WebP display copies in `static/assets/status/`, totalling 55,374 bytes. Display downsampling uses Lanczos; its encoding introduces no further pixel changes. Exact full-resolution RGBA masters total 4,352,954 bytes and remain in the separate optional `stonework-and-spellcraft-icon-masters-v0.104.zip`. That archive contains only the four new masters, their prompts and checksums. The earlier seven masters remain in the v0.103 source archive. Neither source archive belongs in the game folder.

All 286 prior runtime images are byte-identical. The packaging script excludes masters, source-art directories, non-runtime images, caches and live campaign data. Costs, durations, rewards and save schema 65 are unchanged. Reading and reviewing the new panels does not change campaign state.

## Verification and upgrade

Focused Python and headless UI checks are listed in `VERIFICATION_V104.json`. They cover previews against committed results, multi-slot equipment, protection limits, real spell charges, field action uses, room counts, journal navigation, previous-release saves and artwork delivery. Rendered browser review remains deferred.

Stop the old server, preserve the complete `data/` directory, install this release and copy that directory into the new game folder. Run `python server.py`. If an earlier v0.103 installation still has `docs/art-v103/masters/`, remove that folder or extract this release into a clean folder before copying your data.
