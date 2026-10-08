# v0.72 — A household that works together

Willing residents can now lead headquarters construction and production. Separate facilities can work concurrently while your scholar researches, spends time with companions, or travels. Work still resolves only when you explicitly Advance.

## How to use it

1. Open **Estate → Headquarters rooms** or enter a room. In **Arrange headquarters work**, choose a worker.
2. For a resident, select **Agree headquarters work** while both people are home. This is a work agreement only: it spends nothing and assigns no job. It can be ended after their funded job is finished or cancelled.
3. Review the room or production job. It lists the selected worker, their current assignment, the replacement assignment, costs and every unmet requirement. **Fund & assign** commits the stated costs once and pauses that worker’s previous task without deleting its progress.
4. Review all funded headquarters jobs in the room screens, **Projects & next improvements**, **This phase**, or **Preview Advance**. Each job names its worker and shows progress and blockers. Pause, resume, or cancel a specific worker’s job.

A person can hold one funded headquarters job, even while it is paused. Each headquarters facility can hold one such job. A paused job reserves its facility until completed or cancelled. Separate workers and facilities can progress simultaneously. Existing crafting, spell, housing and research systems keep their own rules; this is not a global room-capacity simulation.

## Workers, qualifications and travel

- A worker must be a current resident and at home to begin. Residents need an explicit headquarters work agreement. Ordinary construction is available to any agreed worker; magical construction requires that worker’s own knowledge of the listed principles.
- Production at the smithy, workshop and enchanting room requires an existing crafting offer (or the relevant specialist’s own job). The scholar retains all existing production access. Construction uses the actual builder’s existing Might/Athletics or Intelligence/Artifice expertise and personal support effects. Production and installations keep their fixed durations.
- A specialist improvement can be installed by the scholar or that specialist. The specialist must remain resident and home while installation progresses. Only the chosen worker spends their primary assignment; completed improvements remain permanent.
- Existing personal drills and their one-time rewards remain the scholar’s. Residents retain the existing personal training system. Forged stock and its ownership rules are unchanged; crafting on behalf of the household does not silently transfer equipment.
- When the scholar travels, agreed work continues for workers who remain home. Travelling workers pause their own jobs. Their commitments appear in the departure roster; their funded work is retained on return and waits for explicit resumption.
- Changing work arrangements requires the scholar and affected worker to be home. Ending residency requires finishing or cancelling that resident’s committed headquarters job. Taking an expedition does not require cancelling it.
- Cancelling returns exactly the saved crowns and held goods once. Completion stops the job, releases the worker and facility, and never automatically funds another copy. Duplicate request IDs remain idempotent.
- The two existing field-briefing facilities cannot fund duplicate briefings at the same time.

## Compatibility and artwork

Save schema **59** adds empty `headquarters.workerProjects` and `headquarters.workAgreements`. The original `headquarters.project` slot remains the scholar’s project, including its exact cost, held inputs, progress, agreed duration and legacy flags. No old job is copied or reassigned. No phase passes during migration. Old completed specialist improvements and their legacy benefits remain available.

The new engraved **Stonework and Spellcraft** logo appears on the title screen. It is a transparent 1536 × 1024 WebP, quality 90, approximately 420 KiB. The original emblem remains available elsewhere. All **152 previously bundled artwork files are byte-for-byte unchanged**, including all 42 companion portraits. There are now 153 bundled artwork files. Prompt and provenance are in `LOGO_V072.json`; the full inventory is `ASSETS_V072.json`.

## Upgrade

Stop the old server. Extract this release into a fresh application folder. Keep your **complete existing data directory, including data/assets and all campaign subdirectories**. Either copy that directory into the fresh release or run:

```sh
python server.py --data-dir /path/to/existing/data
```

Do not overlay or replace your saves with an empty directory. The server makes its normal pre-migration database backup for each upgraded campaign. Retain the full original data directory as well because a database-only backup does not contain uploaded artwork. The release ZIP contains application files, not a live campaign. Run `python server.py` to start normally.

## Verification

See `VERIFICATION_V072.json` and `UI_REGRESSION_V072.json` for exact results. New coverage exercises independent workers and facilities, pause/resume, knowledge and work agreements, travel, refunds, saved arrangements, specialist installation, retries, persistence and migration with custom artwork. UI controller tests follow the selected worker through funding, simultaneous jobs, completion and reload.

Rendered browser/layout verification remains unavailable in this environment: no installed browser executable was found. UI tests use the actual controllers and Python rules with a DOM test double. No rendered desktop/mobile, Docker-runtime or live-provider success is claimed.
