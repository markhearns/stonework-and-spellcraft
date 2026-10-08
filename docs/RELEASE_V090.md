# v0.90 — Time together

Every established resident now has **four repeatable affectionate scenes and four one-off closeness milestones**: **128 new authored scenes across 16 companions**. These are optional, non-graphic romantic scenes between your adult scholar and an adult companion. Later evenings fade out while the characters choose to remain together.

Open **Companions → a character → Relationships → Time together**. The interface shows one stage at a time, then one invitation with three choices: accept the affectionate invitation, choose quiet company, or leave it for another time. A new eligible moment or milestone can also appear in the existing invitation feed. Replays do not repeatedly advertise themselves there.

| Closeness stage | Existing relationship required | Tone |
| --- | --- | --- |
| First affection | Mutual attraction | Personal visits, sincere compliments and making time |
| Affectionate closeness | Dating | Shared hands, kisses and familiar activities |
| At ease together | Partners | Trust, listening, accepting care and comfortable embraces |
| Private evenings | Deep partnership | Unhurried time together with a private, non-graphic ending |

## Progression and repetition

Share a stage's repeatable moment before its one-off ending. The next stage requires the preceding closeness milestone and its corresponding mutual relationship milestone. An existing relationship is not automatically advanced, and existing romantic milestones do not fabricate new closeness memories.

- Only one accepted affectionate scene per companion per day phase.
- A newly shared relationship milestone and its closeness invitation cannot be completed in the same phase.
- A stage's ending waits until a later phase than its first repeatable moment.
- Later closeness endings also wait for a new day after the previous ending.
- Repeatable moments remain available at later stages. First memories are preserved, the replay count increases, and the latest response acknowledges familiarity.
- Milestone endings complete once. Rereading a memory neither repeats the event nor changes progress.

Only **Advance** moves time. These scenes award no crowns, materials, relationship points, advancement, healing or chapter progress. They cannot be farmed to bypass relationship gates. Memory storage retains each scene's first occurrence and the latest replay with a count, instead of appending an unlimited transcript.

## Choice, privacy and rest

Opening an invitation does not accept it. Both characters must be established adults and present at home; every accepted scene checks the current conditions again. Choosing quiet company makes no milestone progress, spends no phase allowance, and leaves the original scene available. Leaving or putting invitations aside removes no relationship points or existing progress. Invitations do not expire.

Pausing romance also closes an open closeness invitation. Reopening romance restores the possibility of asking; it does not accept a scene. Existing memories remain readable.

Private evenings require the evening phase, **Rest** for both characters, and a restored bedroom assigned only to either or both participants, with no other resident or arriving guest assigned there. Another person's accommodation is not commandeered. If the available room changes while an invitation is open, reopen it in the newly available space. Assignment and bedroom controls are linked from the explanation panel.

Scenes do not automatically change assignments, complete paid work or count as sleep. Advance still ends the evening and resolves the existing overnight-rest rules, including Chapter 7's homecoming requirements.

## Integration and artwork

New memories appear in the existing journal and in the companion's remembered dialogue context. The relationship page keeps the most recent scene visible and earlier memories collapsed. Locked buttons explain their requirements. Quiet invitations stay in the existing feed and never interrupt another activity.

The scene reader reuses the appropriate room illustration. Earlier stages use the companion's associated room; private evenings use the actual selected bedroom. All **268 runtime artwork files** are unchanged. Existing character portraits, wardrobes, equipment builds and quests are retained.

## Installation and verification

Stop the old server, preserve the complete existing `data/` folder, extract v0.90, restore that folder into the game directory, and run `python server.py`.

Schema remains **64**. New closeness state is created only when you use the feature. An actual v0.89 save was opened with exact state preservation, including established romance, saved builds, accepted artwork and dialogue history. This release does not generate a schema-upgrade backup because no schema migration is needed.

The release's targeted validation results are in `VERIFICATION_V090.json`. They cover all 128 scene resolutions, progression and replay limits, adult/presence/privacy checks, quiet choices, pausing, request retries, save/reload, journal deduplication, all 16 UI panels and the existing romance, almanac, customization and Chapter 7 systems. These are automated gameplay and UI integration checks. Browser-rendered visual review has not been performed.

