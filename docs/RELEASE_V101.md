# v0.101 — Clear instructions and conversations with substance

This release reviews the current interface and authored conversation systems against `WRITING_GUIDE.md`. It replaces opaque labels, missing explanations and interchangeable replies with direct instructions and specific exchanges.

## Interface

- Buttons and headings name the activity: garden restoration, research, artifact crafting, household projects and quest journal.
- Assignment displays show readable work names instead of internal keys.
- Allowances explain the minimum treasury balance and when payments are skipped. Expedition shares explain where indivisible crowns go.
- Training and return conversations display the actual relationship point each choice awards, its cap and its one-time limit.
- Shared-history choices explain whether they save a proposed patrol party or only remember a conversation. The proposed party names match the four-person limit. Preparing a suggestion does not send a party away.
- Spell, project and scene instructions describe the current controls and requirements. Provider settings no longer advertise the retired spell-suggestion flow.

## Dialogue

- All 15 named companions have distinct review, planning, credit, friendship and affection replies, plus voice guidance for optional generated dialogue.
- All 15 personal invitations have three specific replies. Neris compares cup handles, Kaede explains a game position, Iona tests where music carries, and Sabine designs an absurdly elaborate seal.
- All 12 training subjects have an actual lesson and an exercise to discuss. Travel replies refer to recorded methods and distinguish a reported journey from an outing the scholar attended.
- Patrol conversations discuss supplies, covering a companion or recording an unusual creature. New events retain the actual creature names and healing or protection totals where applicable.
- The 11 household pairs have individual follow-up exchanges rather than a shared generic conclusion.
- Revised closeness scenes deliver the poem, anecdote, repair explanation, preference or complaint promised by the player's choice. Quiet company remains a valid social choice.
- Quest acceptance identifies the next obstacle and an available ordinary method. Warm and playful replies reflect the companion's priorities. Rewards and romantic choices retain their existing rules.
- Six offline personal-story packages describe concrete work, completed notes and a demonstration. Approved proposals already stored in a campaign keep their original text.
- Several resident and castle scenes now supply the actual observation or answer instead of announcing that one was given.

## Writing rule

Plain English is required in UI text and conversations. A reply must answer the selected question. Characters should express a specific observation, opinion, request, joke or disagreement in their own voice. Saying that someone explains a method or tells a story does not provide that explanation or story. Social scenes can have substance without granting a reward.

The guide and generation instructions now make these requirements explicit. Generated drafts still need review; this release does not claim that a prompt guarantees good writing.

## Compatibility and verification

Save schema remains 65. Costs, rewards, progression gates, existing scene and choice IDs, artwork and accepted campaign text are preserved. All 279 bundled images are unchanged, including Iona's dark-haired succubus design.

192 affected Python tests pass, including seven editorial integration tests and the real HTTP version check. Seven headless UI integration scripts pass: refinements, companion participation, intimacy, household chapters, personal stories, companion almanac and character quests. These check templates, actions and persisted state; rendered browser review remains deferred.

A v0.100 save containing completed conversations and an approved personal story was read, migrated and reloaded through SQLite without changing its stored values. Existing story package costs and rewards match v0.100.

The previous ZIP was incomplete. This release rebuilds the archive from the intact working files and checks every compressed entry. Compatibility comparison used the CRC-checked v0.100 source entries; four unchanged remaining runtime modules were verified against v0.99.

To upgrade, stop the old server, keep the entire existing `data/` directory, install the new application files and restart with `python server.py`. This archive contains no live campaign data.
