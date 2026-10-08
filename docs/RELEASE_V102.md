# v0.102 — Progression and pacing review

This update makes existing work and chapter requirements easier to follow. It does not add another game system or change prices, rewards, work durations or chapter gates.

## Changes

- **Project funding offers a choice.** When a finite commission is worthwhile for the missing amount, the chapter shows its payment, assigned phases and materials. Copying remains available with an explicit treasury target. A small shortfall still recommends copying. An unfinished commission resumes with its original terms and progress; another resident’s commission is not reassigned.
- **Chapter 5 identifies the actual prerequisite or paid work.** Guidance names missing research or personal study, recognizes an active yard review, and resumes an unfinished equipment job. Its closing equipment priority is explicitly a remembered preference, without a stat bonus or automatic assignment.
- **Chapters 6–8 have a current next step.** Prompts distinguish travel, a field decision, construction, recruitment, a work agreement, overnight rest and the closing supper. Field methods and permanent rewards remain player choices.
- **Rest prompts name the people who need sleep.** They use the actual returning party and recorded overnight rest. Changing an assignment keeps paid work progress. Once the sleep requirement is met, the closing-supper prompt allows ordinary daytime work until evening.
- **Advance explains waiting patrol decisions.** The party does not select a method automatically. Household work can still resolve while a patrol waits. Site decisions appear once in the activity feed, and active patrol time is no longer described as the scholar resting.
- **Paused equipment work can resume from Projects.** Resuming keeps the committed cost and completed work. The shared relief drill also uses the same assignment requirements for its UI button and its action validation.

## Campaign findings

Two continuous fresh campaigns used earned resources through all eight chapters, then completed a paid escort objective. They covered different early choices, household membership, chapter resolutions, route plans and final improvements. Both ended without cheats or food shortages.

| Measure | Solo-opening route, before → after | Company-opening route, before → after |
| --- | --- | --- |
| Total phases, including the later objective | 309 → 294 | 297 → 285 |
| Copying phases | 81 → 26 | 80 → 23 |
| Chapter 2 phases | 70 → 64 | 70 → 64 |
| Chapter 3 phases | 28 → 25 | 33 → 29 |
| Chapter 4 phases | 54 → 49 | 42 → 37 |

Much of the copying became finite commission work. This adds explicit acceptance choices and reduces earning phases; it does not remove all repetition or make every chapter shorter. The different phase of day also changes food spending and the wait for evening. These counts describe automated routes, not human playtime.

Both routes used tested equipment to save two phases on the North watch road. The later guidance walkthrough also used Rhess’s knowledge at the wardstones. Existing route plans and Chapter 8 improvements retain their distinct, stated effects. Existing conversation checks confirm that remembered choices, participant identity and the promised substance of replies remain intact.

A separate walkthrough followed the new prompts through Chapters 6–8 from an earned checkpoint. It completed recruitment, construction, the drill, field decisions, rest and the closing reward using normal actions. The prompts never chose a field method, recruited a companion or spent money merely by being read.

## Verification and upgrade

- 114 targeted Python tests passed, including real action validation, commission payment, paused-work recovery, sleep requirements, combat, writing rules and HTTP version reporting.
- 10 headless UI suites passed, including button clicks through the persisted API. These are controller and template checks, not a rendered browser review.
- 16 v0.101 campaign checkpoints retained their exact JSON values through migration, public-state reads and SQLite reload.
- All 279 bundled art assets are unchanged, including Iona’s revised appearance. Save schema remains 65.

Stop the old server, preserve the complete existing `data/` directory, extract the update, restore that directory and run `python server.py`. The release contains no live campaign data.

The detailed results are in `PACING_REVIEW_V102.json` and `VERIFICATION_V102.json`. Rendered browser review remains deferred. That review should assess whether the chapter prompts, funding alternatives and companion invitations are easy to notice during play.
