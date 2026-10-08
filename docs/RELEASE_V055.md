# v0.55 — life together

This release develops the six requested areas: individual wardrobe conversations, complete companion routes, resident friendships, specialist follow-ups, shared room activities, and less repetitive work management.

## What changed

- **14 complete personal routes / 56 scenes.** Each companion has four distinct authored chapters with two responses. The common room and library provide a complete route after recruitment, so an expensive specialist room cannot block the wardrobe journey. Later scenes retain the previous response as a callback.
- **28 individual wardrobe invitations.** Warm and playful responses are remembered. Unlocking and wearing remain separate choices. Existing unlock thresholds are unchanged; a repeated activity cannot manufacture additional relationship evidence.
- **8 resident pairings / 16 scenes.** Each pairing has an initial conversation and a follow-up after a later shared activity with either participant. Both participants must be residents, home, and have an established shared memory. Their room must be available.
- **11 specialist journeys / 33 conversations.** Planning follows the original specialist introduction; installation follows the completed room enhancement; the last conversation follows a visit to that room after installation. Already-completed enhancements can go directly to the installation scene. Construction requirements, prices and practical benefits are retained.
- **13 shared room activities.** First visits and responses are recorded. Repeat visits preserve the original memory and record the latest visit without adding a new wardrobe unlock event. Practical work remains linked to existing research, training, harvest, crafting and room-job controls.
- **Named work arrangements.** Save up to eight sets of current resident assignments, inspect proposed changes, then apply atomically. An absent saved member or invalid assignment blocks the whole change. New arrivals are untouched. Removing a saved arrangement does not change current work. Jobs requiring their own specialized controls may need to be resumed there if the saved assignment cannot be restored through ordinary assignment validation; the blocker is shown before any change.
- **Broader project resumption.** Funded housing, personal study, two-person lessons, focus inscription, public workshop jobs, reviewed personal stories, shared research reviews and local introductions now join existing resume controls. The preview lists every changed assignment, including both people in a lesson. Resumption spends no additional funding or time.
- **Dialogue continuity.** Optional generated dialogue receives completed chapters, activity memories and wardrobe responses involving that companion. Unplayed scenes and other residents' private choices are excluded. No provider configuration or call is needed for authored scenes.
- **Household visibility.** Home and work pages show available personal next steps. Rooms link to activities with a selected companion. Leisure routines follow current specialist roles while preserving work priority and Brakka's existing pool visits.

## Save compatibility

Schema 46 adds `householdChapters` and `workArrangements`. Migration retains existing relationship records, accepted art, selected wardrobes, possessions, resources and funded work. No old choice is rewritten or invented. Older wardrobe invitations remain readable without newly authored opening text. Export/reload retains new choices, repeat-visit chronology and arrangements.

Stop the server, extract into a fresh program folder, copy the complete existing `data` directory (including `data/assets`), then run `python server.py`. The standard pre-migration SQLite backup is created automatically. Keep the previous release as a rollback copy. Game time moves only on Advance.

## Verification

- **586 Python tests passed** in the final full run.
- **31 connected headless UI suites passed**, including the complete new Mira route, wardrobe response controls, room filters, repeat visits, saved arrangements, reload, escaping and assignment previews.
- New rule tests cover all fourteen full routes, all eight pair follow-ups, all eleven specialist sequences, missing people/rooms, out-of-order choices, repeated-activity anti-farming, atomic arrangement failures, migration, scoped dialogue context, and two-person lesson assignment previews.
- **All 121 bundled artwork files are byte-for-byte unchanged from v0.54.** Existing portrait and retired-URL tests pass.
- Browser/rendered desktop/mobile checks remain deferred at the user's request. Headless controller checks are not visual approval.

Machine-readable reports: `VERIFICATION_V055.json` and `UI_CHECKS_V055.json`.
