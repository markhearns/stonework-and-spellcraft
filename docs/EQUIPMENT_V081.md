# Equipment and Chapter 5 implementation

## Play loop

Review existing gear → choose an owned host → stow it → review a compatible operation and worker → fund once → Advance assigned work → equip and select the inscription → test safely or use it on a field route. Names and ownership history stay with the physical item. Every slot category supports at least one enchantment.

| Operation | Crowns | Assigned phases | Components |
|---|---:|---:|---|
| New inscription | 8 | 2 | vessel + binding |
| Strengthen a score inscription | 12 | 3 | vessel + binding |
| Add second setting | 10 | 2 | vessel + binding |
| Refit for owner | 4 | 1 | included |
| Extract transferable pattern | 4 | 1 | binding |
| Install recovered pattern | 4 | 1 | vessel |
| Add selectable quiet mode | 6 | 2 | binding |
| Personal signature fitting | 4 | 1 | included |
| Signature proof | 0 | 1 | none |
| Supplied boot commission | 0 | 2 | client escrow |

The first commission pays 12 crowns; subsequent deliveries pay 8. Ordinary manufacture prices include mundane materials. Working folios and gauges retain their component recipe. Protected component reserves apply to all new paid work. Field calibration and personally learned effect principles gate inscription work. There is no random failure, durability tax, deadline or passive production.

Rank-one effects use one active channel; rank-two score effects use two. Two-handed objects count only once. A four-channel loadout may contain several installed but inactive inscriptions. A refined rank-two effect can be set to its quieter rank-one mode at home. Identical contextual bonuses do not stack beyond +2. Warded cover enables a teamwork role instead of adding a score.

The nine slots and three loadouts use item IDs. Stowing or transferring removes that item from all saved loadouts, so it cannot return through an obsolete preset. Missing or unavailable loadout entries are rejected with reasons. Transfers need agreement, and fitted items need refitting for a new wearer. Treasured and starter items cannot be sold; vault storage uses the existing vault prerequisite.

## Chapter sequence

The practice that nearly worked follows Chapter 4’s defensive construction. A 32-crown study allocation supports the first two inscriptions. The three undertakings are a supervised one-phase yard review, two distinct safe inscription proofs plus a supplied commission, and the returned North watch road report. An explicit closing priority completes the chapter. No resident recruitment or romance is required.

The road contains rain-cut steps, a jammed gate, an unstable warning seal and a padded watch sentinel. Every encounter offers free ordinary work; suitable active gear offers a one-phase alternative. The sentinel also supports two distinct people with cover and a disarming implement. Completed encounters and pending work survive retreat. Only a completed return deposits the once-only 18 crowns, one moon glass and two binding threads.

## Integration and efficiency review

- Canonical item identity, ownership, occupancy and new jobs live in armoury.py. Existing tool/focus/public/HQ records are compatibility adapters, reconciled by stable IDs rather than duplicated inventory. Legacy actions remain available and respect new reservations and configuration limits.
- One pure recipe quotation serves previews and commits. Normal campaign revision checks and request IDs protect against stale quotes and duplicate charges.
- Worker jobs reserve exact inputs once, pause when assignment changes and refund committed inputs on cancellation. Existing funded jobs retain their price and timing; no automatic restart or new charge occurs.
- Views are read-only. Work board, room presence, forecasts and project summaries share the saved jobs. Equipment preparation does not repaint portraits; the overview explains that wardrobe art represents presentation rather than a live paper doll.
- Optional signature work provides progress without requiring replacement loot or a material ladder. It grants capacity and remembered identity, not automatic affection. Generated residents receive a bounded generic request; authored residents keep distinct lines and room associations.
- Chapter guidance reuses research, personal study, construction and treasury rules. Ordinary field routes prevent an equipment build from becoming a campaign dead end.

## Deliberate bounds

This release does not add procedural loot, automatic best-gear selection, arbitrary spell-to-enchantment conversion, new damage/armour arithmetic, online trading or co-op. Existing public inscriptions retain their bounded uses; extraction applies to the eight new transferable effects. One funded equipment job per worker and one client commission at a time keep the economy legible. Legacy compatibility code remains explicit; deleting it before all older saves and action paths are retired would risk progress loss.
