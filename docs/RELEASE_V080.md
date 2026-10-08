# v0.80 — Opening campaign review

This release reviews the connected opening through Chapters 1–4 and improves guidance found during that review.

- Chapter 4 now offers personal study when Gentle preservation is already in the shared archive. It continues an existing learning project before proposing another trip, and resumes both participants in an agreed shared lesson. Existing progress is preserved.
- Disabled Chapter 3 actions now expose their reasons through the standard explanatory tooltip and accessibility attributes.
- Completed Chapters 2–4 use compact, expandable home-page summaries, matching Chapter 1. Their choices, notebooks and normal chapter pages remain accessible while current work is easier to find.

Two continuous routes start from a fresh campaign and complete every chapter with normal gameplay actions and serialization/reload checks: solo/salvage/private wing/infirmary/barriers/capture-and-release, and company/survey/shared wing/smithy/warning seals/drive-away. Chapter 2's undertakings run in opposite orders. Neither route grants test resources or forces Sabine to become a resident. Existing branch tests cover specialist transfer, established Sabine, separate recruitment, specialty installation, quests and household scenes.

A save created with the actual v0.79 release was reopened with this build. Its raw campaign state, partial research, accepted portrait and portrait bytes were unchanged; the portrait remained in a complete backup. Schema remains 59. Keep your **entire existing data directory**, including all campaign folders and `data/assets`, when upgrading.

All 210 shipped artwork files, including the corrected Kaede overview set, remain byte-for-byte unchanged. No new image generation was necessary.

Browser limitation: the cloud browser previously refused the local preview, and there is no local browser executable. This release does not claim rendered desktop/mobile, accessibility or visual-layout acceptance. Controller tests and static CSS review cannot replace that check. See `CAMPAIGN_REVIEW_V080.md` and `VERIFICATION_V080.json` for scope and results.
