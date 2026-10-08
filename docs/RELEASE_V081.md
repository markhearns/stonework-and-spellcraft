# v0.81 — Arms of Our Own

The household now develops familiar equipment through fitting and inscriptions. Ordinary steel remains ordinary steel; useful enchantments and personal history provide progression.

- Nine shared slots: head, shirt, pants, hand 1, hand 2, boots, ring, necklace and accessory. Multi-slot objects replace every occupied piece atomically.
- Thirty ordinary designs; eight compatible enchantments. Strengthening, a second setting, controlled low-power modes, refitting, extraction and pattern installation are funded work with exact cancellation refunds.
- Household, expedition and social loadouts; four active channels; a +2 cap on contextual equipment score. Server previews show actual costs, displacements and effects before commitment.
- Supplied commissions teach a sustainable earning loop. Client equipment and materials cannot become free personal inventory; payment requires explicit delivery.
- Chapter 5 follows the yard and barracks: agree a practice party, review equipment, test two distinct inscriptions, deliver a supplied commission, reopen the North watch road and share an explicit closing review. All three undertakings are required. Solo completion is supported.
- All 14 established residents have distinct optional equipment requests, associated-room fittings, supervised proofs and remembered closing conversations. The founder can choose a personal signature piece too. Signature pieces keep their IDs and names and gain a second setting. Protection guards against accidental sale. Four completed signature silhouettes have dedicated art; other hosts keep their base or accepted art.
- Room presence, paused-work reminders, project progress, expedition scores and dialogue context include the new work. Brakka’s installed forge reduces newly agreed smithy manufacture time; Nyssara’s material supply remains useful; Sabine’s completed dungeon specialty supports her signature seal without duplicating its dungeon bonus.
- Thirty inventory icons, four signature variants and two feature illustrations are generated and optimized as WebP. Existing artwork and bundled content archives are preserved byte-for-byte.

## Starting or upgrading

Extract the archive. Run `python server.py`. For an upgrade, stop the old server and copy its entire `data/` directory into the new game folder before starting. Do not copy only the database: campaign subdirectories and accepted images belong with it. Migration 59 → 60 saves a backup automatically. No private save or provider credentials are bundled.

Use Equipment → Review starting equipment once for each newly available household member. The review fills missing ordinary categories without overwriting named pieces. It does not regenerate sold or transferred starter items.

Chapter 5 is available after Keeping the Hearth’s closing review. Signature requests remain optional and can continue after the chapter ends.

## Verification and limits

See VERIFICATION_V081.json for exact test results. Continuous solo and companion routes use normal actions and earned resources through all five chapters. A save created by the actual v0.80 archive was upgraded with partial research and accepted portrait bytes intact.

Connected headless interface checks exercise templates and controllers; they are not visual browser acceptance. The existing browser restriction remains unresolved. No live model-provider, Docker or full tactical combat acceptance is claimed. Existing field scores, safe ordinary routes and finite encounter work provide this chapter’s defensive play.
