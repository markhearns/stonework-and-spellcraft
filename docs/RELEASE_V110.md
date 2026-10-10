# v0.110 — Beneath the Hearth

Chapter 9 gives the castle investigation a usable result: the foundation ritual chamber. Each task records evidence, restores a part of the room or verifies an operating condition. The chapter explains the chamber's purpose and opens a specific further question about the surveyors' connection beneath the castle.

## Investigation and restoration

Chapter 9 opens after Chapter 8: The First Real Test is complete. Reach it from the Chapter 8 conclusion, Home guidance, Castle rooms & household, Magic, navigation search, the Headquarters room card or the Spells & Rituals reference.

1. Trace the connections beneath the hearth: 2 phases, or 1 with personally learned Steady hearth wards.
2. Read the chamber's maintenance ledger: 2 phases, or 1 with recorded founding evidence from the earlier Castle history investigation.
3. Restore the room: 3 phases; 24 crowns, 2 binding-thread, 2 porous-clay and 1 fireglass. Materials must be unreserved.
4. Test the independent hearth supply: 1 phase.
5. Test the household connections: 1 phase.

The two tests can be completed in either order. The chapter takes 9 assigned phases by the manual methods, or 7 with both relevant earlier discoveries. Pausing preserves progress and committed costs; cancelling unfinished work refunds those costs. Completed findings remain recorded. Recording the conclusion grants the scholar 2 advancement points once and spends no additional phase. The ordinary castle wards work independently of the optional ritual.

No relationship milestone is required to complete the investigation, restore the room or finish the chapter. Earlier private castle lore and recorded discoveries are preserved.

## Optional intimacy ritual

After restoration and both tests, invite an established adult resident partner. Both participants must be home, resting, at least 18, and have shared the Private evening romantic milestone. Romantic invitations must be enabled. Resident bonding scores do not establish romance.

The invitation has a character-specific reply, remaining requirements and a clear choice to agree or leave it for another time. Agreeing assigns both participants; the next Advance resolves one private phase. The scene fades to black. There is no payment or material cost.

The ritual grants **+20% positive trust, affection, respect and resident bonding gains for the following nine elapsed phases — three game days**. It affects the entire household, including residents travelling away from the castle. A base gain of 1 becomes 1.2; a base resident gain of 2 becomes 2.4. Negative changes and existing score ceilings are unchanged.

Resident bonding keeps its limit of 4 base points per pair per day. The blessing adds up to 0.8 above that daily base allowance; it does not bypass the 100-point score ceiling. Player relationship scores retain their 12-point ceilings. Reading scenes and reopening screens award nothing.

Renewing refreshes the remaining duration to nine phases; the percentage never stacks. The timer, exact ending day and phase, and effect are shown in the chamber, Home and relationship panels. Changes to availability or romantic invitations pause an arranged ritual. Resume rechecks eligibility; cancellation releases participants still assigned to it.

## Writing, navigation and art

Task controls state their purpose, phases, cost and missing requirements. The notebook records completed findings. The room page connects the investigation, restoration and continuing ritual use. A new 1200 × 800 engraved room illustration follows the castle's worn stone, timber, muted violet and practical furnishings. It is encoded as a lossless WebP display copy; the exact generation prompt and source filename are in ART_V110.json.

All previous runtime artwork remains included. The game now contains 398 runtime assets and 134 illustrated Spells & Rituals reference entries. Resident profiles retain the v0.109 mutual bonding levels, progress and activity histories.

## Upgrade

1. Stop the server and back up the complete data/ directory, including campaign subfolders, accepted art and provider settings.
2. Extract this full release into a clean folder. Copy the complete data directory, or retain the existing external --data-dir configuration.
3. Restart with python server.py or the existing launch command, then hard-refresh the browser.

Schema 69 initializes Chapter 9 with an automatic database migration backup. Existing relationships, resident bonds, projects, discoveries, artwork and expedition state remain intact. New saves should not be opened with older executables; use the migration backup if reverting.

This archive includes no live campaign data. No remote server deployment was performed. Historical release notes describe their own versions; START_HERE.md and this document describe the current release.

## Verification

- 72 targeted Python tests pass across foundation_chamber, resident_bonds, relationships, social_life, castle_mystery, magic_reference and artwork.
- These include 14 new foundation tests covering requirements, costs and reserves, research shortcuts, pause/resume/refunds, both test orders, adult partner eligibility, invitations, one-phase resolution, fractional gains, score and daily limits, exact expiry, renewal, migration backups, action retries and saved-state reloads.
- One full-flow regression test passes with two earned routes through Chapters 1–9, no cheats, and a serialized reload after each action.
- Four connected headless UI suites pass: Chapter 9 and ritual use, resident bonds, relationship scenes and the magic reference. They exercise templates, controls and the real saved game state.
- JavaScript syntax, runtime image hashes and HTTP asset delivery pass. The release builder checks every ZIP entry's CRC and equality with its source and excludes live campaign data and source-art masters.
- Rendered desktop/mobile layout is not verified. The complete historical regression suite was not run. See VERIFICATION_V110.json for the exact scope.

