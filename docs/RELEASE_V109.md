# v0.109 — Bonds between residents

Residents now have one mutual 0–100 bonding score per pair, visible from either person's Profile and Relationships tabs. Overview shows the three strongest connections. Every current resident appears, including new or generated residents, with their existing portrait, score, level and most recent gain. Larger households can expand the remaining connections.

Player relationships retain their existing trust, affection, respect and romance systems. Resident bond levels measure companionship and do not establish romantic relationships.

## Levels and gains

| Score | Level | Description |
| --- | --- | --- |
| 0 | 0 | New acquaintances |
| 10 | 1 | Familiar |
| 25 | 2 | Friendly |
| 45 | 3 | Close friends |
| 70 | 4 | Trusted companions |
| 100 | 5 | Deeply bonded |

Each pair can gain up to four points per game day. Bonding has no passive decay.

- Remembered group/pair conversations: +2. Existing social scenes, household chapters, relationship stories, companion almanac scenes and other systems already recording shared relationship events use the central hook. Only resident pairs among the actual participants receive points.
- Resident moments and approved content conversations: +2 when first shared. Deferring, rereading and retries do not award points.
- Explicit evening wind-down: +2 between selected residents.
- Active shared research, living-index study, gardening, matching hunting/foraging/road-watch assignments: +1 per completed phase for the actual coworkers.
- Agreed teacher/learner lessons, lasting ritual circles, shared household undertakings, saga projects and the Chapter 5 field-kit drill: +1 per working phase. Paused work does not count.
- Leisure: +1 per completed phase between residents resting in the same available library, common room, conservatory, hot spring, sauna or pool. Shared sleeping accommodation alone does not count.
- Meals: +1 between residents already at home when an evening phase begins, when the restored kitchen provides the full household meal. Travellers and later arrivals are excluded.
- Expeditions: +1 on outbound and return travel phases for resident party members. Field patrol travel and committed encounter exchanges also give +1; waiting at a decision does not.

All activity gains share the same daily cap. Sources and recent history are stored per pair, and the phase summary reports gains without listing hundreds of pairs. Scores are exposed even before a pair has earned points. A departed resident's records remain saved and reappear on their return.

## Upgrade and preservation

Save schema advances from 67 to 68. The normal server migration creates a pre-upgrade database backup. Existing resident-to-resident trust/affection/respect totals seed the simple score at two points per recorded point, capped at 100. Completed resident moments and approved household conversations also seed their recorded participants. Unrecorded past meals, work and travel are not invented.

Existing campaign fields are preserved, including the older relationship records used by story requirements, player relationships, custom artwork, funds, projects and expeditions. Reads do not manufacture history or advance time. New save data is incompatible with older executables; use the migration backup if reverting.

1. Stop the existing server and back up the entire `data/` directory.
2. Extract into a clean folder, copy the entire data directory or retain the external `--data-dir` configuration, and restart with the normal launch command.
3. Hard-refresh, then open a resident's Profile or Relationships tab.

No artwork has changed in this release. The v0.108 recovered artwork and 133-entry Spells & Rituals reference remain included. No live campaign data is packaged, and no remote server deployment was performed.

## Verification

- 17 resident-bond tests cover the complete pair graph, custom residents, actual activity gains, caps, thresholds, shared scores, read-only views, repeat protection, home/away membership, pauses, migration, migration backups, action retries and reloads.
- 73 related Python tests cover relationships, social life, household chapters, magic/rituals and provisions. Two scene-mutation contracts now allow the intended `residentBonds` change. Stale schema-number expectations in these related suites now use the engine's current schema constant.
- Four connected headless UI suites pass: resident bonds, relationship scenes, overview portraits and the magic reference.
- JavaScript syntax checks and ZIP integrity/source-equality checks pass.
- Rendered desktop/mobile visual QA remains unverified; the connected UI tests exercise templates and controllers, not browser layout. The full historical regression suite was not run.

The foundation-chamber intimacy ritual and Chapter 9 remain proposed design work. This release supplies the resident progression system that a future castle-wide blessing can modify; it does not claim that blessing is active.
