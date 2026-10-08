# Seven-chapter flow audit — v0.93

Two continuous fresh-campaign routes use normal actions, earned resources, and save/reload throughout the original route. Route A uses private accommodation, capture and ordinary Chapter 7 methods; route B uses shared accommodation, a peaceful departure and prepared methods. No cheats or resource grants are used.

| Chapter | Before: advances A / B | After: advances A / B | Copying advances A / B |
| --- | ---: | ---: | ---: |
| 1 | 25 / 25 | 25 / 25 | 5 / 5 |
| 2 | 70 / 70 | 70 / 70 | 28 / 28 |
| 3 | 28 / 33 | 28 / 33 | 16 / 19 |
| 4 | 54 / 42 | 54 / 42 | 28 / 24 |
| 5 | 49 / 53 | 49 / 53 | 20 / 20 |
| 6 | 20 / 19 | 20 / 19 | 0 / 0 |
| 7 | 29 / 27 | 29 / 27 | 0 / 0 |

The ordinary routes finish on day 92 and day 90, both in the evening. Counts are simulated game phases, not human playtime. Reading, exploration and optional relationship scenes are not measured in minutes. These routes are repeatable integration checks, not an exhaustive fastest-route proof.

## Findings

- Chapters 2–5 spend about 46% of their advances earning copying income on these routes. Increasing prices or adding arbitrary waits would lengthen that repetition. Work duration, wages, chapter gates and rewards are unchanged in this release.
- Funding guidance previously assigned open-ended copying. It now offers a treasury target: work stops after a phase reaches the target, after ordinary expenses. Nothing is bought automatically. Home shows progress, pause/resume and the current income estimate.
- Evening wind-down was available in expedition and patrol screens but absent from the main Home page. It is now on Home. A separate, clearly labelled button can rest the actual returning party or the scholar and Rhess. It changes only the named participants.
- A rested morning now offers links to resume unfinished paid projects. Resumption uses the same validated action as Projects; it does not recharge costs or advance time.
- Companion Overview now uses authoritative location and assignment data. Room specialty and available invitations remain alongside that status. Missing ambient dialogue no longer serves as a proxy for location.
- Work entries previously pushed optional conversations to the back of the activity feed. The Overview filter now alternates work and invitations after pending decisions. Dedicated filters remain unchanged, and entries are not duplicated.
- Old homecoming notices now leave Home after the following day. The full return report remains on Expeditions. Finished earning receipts appear only on the completion day while the target funds remain available.
- Public-state generation now reuses one Advance forecast for both the Projects panel and Advance preview, instead of simulating the same phase twice. The forecast remains read-only.

## Downtime routes

Two additional playthroughs deliberately take a night at home between each pair of chapters. They use ordinary Rest and Advance actions and choose an available optional conversation when one exists. Both complete all seven chapters without cheats, starvation or blocked progression: day 96 and day 94. Each route includes six additional nights together; the companion route also shares two optional conversations. There is no imposed minimum chapter duration or automatic scene selection in the game.

## Verification and limits

All targeted gameplay and controller checks pass after correcting a test-runner module name. The original and downtime routes complete. Browser-rendered visual review and human reading-time measurements remain outstanding. No new images were necessary: these changes use the existing room and companion illustrations.

Reproduce the original routes with `python scripts/audit_chapter_pacing.py pacing-report.json` and the downtime routes with `python scripts/audit_chapter_pacing.py pacing-downtime.json --with-downtime`. Machine-readable results are in PACING_V093.json.
