# v0.111 — Resident friendships that lead somewhere

Residents now propose shared activities as their bonding grows. Their choices lead to saved memories, keepsakes displayed in rooms and a modest benefit when they work together. The new page is available from **Companions → Resident friendships**, profile bond cards, Home invitations and the current-phase task list.

## Bonding milestones

| Bonding | Optional development | Time and cost | Result |
| --- | --- | --- | --- |
| 10 — Familiar | Hear their idea, or choose reading, a short game or a courtyard walk for a general pair | No work phase or payment | A recorded first conversation |
| 25 — Friendly | Make a shared keepsake | One shared phase for both residents; 4 crowns | A keepsake in its room, a completed scene and +1 cooperation |
| 45 — Close friends | Spend time using the keepsake together | One shared phase; no payment | A specific follow-up and saved memory |
| 70 — Trusted companions | Improved cooperation | No additional task | Cooperation rises from +1 to +2 |
| 100 — Deeply bonded | Return to their shared tradition | No work phase or payment | A final conversation recalling what they made and learned together |

Each completed milestone can award 2 base bonding points, within the existing 4-point daily base allowance. The foundation chamber's blessing increases these gains by 20%; it does not multiply cooperation output. The 100-point ceiling remains.

Invitations never expire and can be set aside or restored. They do not change assignments until a timed activity is explicitly arranged. Both residents must be home and resting before arranging a project or follow-up; the scholar can perform separate work while the residents complete it on Advance. One shared activity can be arranged at a time. Conversations cost no work phase and leave current tasks unchanged.

A changed task or absent participant pauses a shared activity. Resume checks both people again; it does not replace another current task without first setting that person to Rest. Cancelling returns committed crowns once and leaves the invitation available. Completed keepsakes and memories remain saved. High bonding alone never invents completed events or starts romance.

## Authored pair stories

| Residents | Shared keepsake |
| --- | --- |
| Brakka and Neris | A glass-and-brass chime with a four-note tune |
| Mira and Tamsin | An adjustable book rest that protects the spine |
| Iona and Kaede | A reversible route board with changing conditions |
| Aurelia and Maren | A practice lantern shutter that works with gloves |
| Elowen and Sylva | A mint cutting tray with dated labels |
| Fenna and Sabine | A reusable games-night notice |
| Mira and Nyssara | A folio separating observations from explanations |

These seven stories contain four distinct remembered events each. Other pairs, including generated residents, can choose reading, a game or a courtyard walk. Their selected activity determines their keepsake, later scene and final callback.

Keepsakes are persistent shared household objects shown in the associated room and both residents' friendship records. Their cooperation benefit comes from completing the shared project. Generated conversations receive only completed friendship events involving the person being addressed.

## Cooperation

A pair that has completed its keepsake contributes +1 when both residents are home and doing the same supported task. At 70 bonding, the contribution becomes +2.

Supported tasks are shared hearth/catalogue research, living-index research, gardening, hunting and foraging. Research gains work points, gardening gains its selected output, and hunting or foraging gains provisions. Research respects the work remaining. Each task receives only its strongest eligible pair bonus once; the benefit is not added separately for every resident or every possible pair.

The bonus requires an active research project or actual staffed work. It does not change crafting costs, training, spell work or combat. Profiles show the unlocked benefit, the friendship page shows eligible assigned work, research and garden screens explain current cooperation, and forecasts/results include the real output.

## Quality review

- Reviewed Chapter 9, the intimacy ritual, resident bonds and the new milestones together.
- Retained the complete Chapter 9 investigation, optional fade-to-black ritual, +20% household relationship blessing, exact nine-phase timer and non-stacking renewal.
- Fixed conversations failing when a resident occupies a Headquarters room such as the foundation ritual chamber. The dialogue screen and generated conversation context now resolve those room names.
- Added completed friendship memories to the relevant resident's generated conversation context. Private ritual memories are supplied only to their participant; the current household blessing can be understood by other residents.
- Kept the earlier friendship summaries compatible with the new save records.
- Added profile, room, Home, task-list and Companions links; clear requirements; pause/resume/refund controls; filters; and limited initial listing for larger households.
- Changed the foundation card grid to fit narrow containers. Added flexible pair portraits and wrapping controls for the new screens.
- Preserved all 398 runtime art assets without changes and all 134 illustrated Spells & Rituals reference entries.
- Reviewed new prose for concrete subjects, distinct character voices, delivered outcomes and callbacks. No future reply is shown before its event.

## Upgrade

1. Stop the running server and back up the complete data/ directory, including campaign subfolders, accepted artwork and provider settings.
2. Extract this complete release into a clean folder. Copy the existing data directory, or retain the existing external --data-dir configuration.
3. Restart with python server.py or the usual launch command and hard-refresh the browser.

Schema 70 creates an automatic migration backup and initializes the new milestone records. Existing bonding scores, relationship histories, Chapter 9 progress, ritual timers, projects and custom art are preserved. Existing high scores unlock invitations for the player to accept; no past scene or keepsake is fabricated. Use a migration backup when reverting to an older executable.

No live campaign data is included. This package has not been deployed to the hosted server.

## Verification

- **140 targeted Python tests pass**, including 19 resident-friendship tests, 15 foundation-chamber tests and regressions for bonds, relationships, social life, castle history, the magic reference, artwork, provisions, task guidance, generated dialogue and household chapters/work arrangements.
- **One full-flow regression test passes**, completing two earned routes through Chapters 1–9 with no cheats and a serialized reload after every action.
- **Seven connected UI suites pass:** resident friendships, foundation chamber, resident bonds, relationships, magic reference, task guidance and room navigation.
- New coverage checks all seven authored stories, all three general activities, strict gates, real costs, mutual scores, blessing interaction, exact cooperation output, paused/absent participants, refunds, non-expiring invitations, no repeated rewards, scoped conversation memory, migration backups, request retries and saved-state reloads.
- JavaScript syntax and runtime asset checks pass. Release packaging checks all ZIP entry CRCs and equality with source files.
- **Rendered desktop/mobile visual review remains unverified.** There is no browser executable in this environment, and the Chromium download failed. Connected UI tests verify templates/controllers with real saved state; they do not verify browser layout. The full historical test suite was not run.

See VERIFICATION_V111.json for test scope. Chapter 10 remains the next castle-story development; this release completes the resident friendship work and quality pass.

