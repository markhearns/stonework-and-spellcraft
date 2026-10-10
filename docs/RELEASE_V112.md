# v0.112 — Companion dialogue and meaningful choices

This release reviews companion writing across the fifteen named residents. It replaces empty summaries with actual dialogue, anecdotes, explanations and choices; gives each companion clearer motivations and values; and makes player responses more specific to the conversation.

## What changed

- Rewrote 175 existing passages across everyday and social conversations, household chapters, relationship invitations, travel scenes, romance and character voice examples.
- Rebuilt 45 personal disclosures: three per companion, each with three distinct player responses and answers. A question about a goal, an invitation to share an interest and a respectful challenge no longer produce the same list of facts.
- Rebuilt 27 resident-pair conversations with three specific responses each. The player can ask about the actual disagreement, contribute something relevant or question an assumption. The residents keep their own voices and decisions.
- Gave all 15 companion initiatives labels that say what the player will actually ask or offer. The exact displayed line is stored with the chosen response.
- Gave the 13 existing relationship invitations individual questions and replies, including character-specific responses to declining. Existing relationship dimensions and rewards remain unchanged.
- Added a second platonic response to each of the 15 companion travel conversations. Established affection remains a separate, gated option.
- Added goals and values to disclosed profile details, and a personal difficulty to the trusted section. Generated replies receive those details through existing knowledge-scoped context. Updated drafting instructions require direct answers and forbid writing an unchosen player answer.

The profile remains a summary of what has been learned; physical information stays there rather than being recited in every conversational reply. Private disclosures retain their existing partnership requirements. Listening, asking a question and choosing company do not start romance.

## Character direction

| Companion | Motivations and interests carried into the writing |
| --- | --- |
| Mira | Preserve overlooked people’s accounts; enjoy and argue about stories; learn when her urge to correct becomes an urge to win. |
| Tamsin | Make affordable, repairable bindings; have time for her own reading and games; stop promising the same hour twice. |
| Iona | Map shelter, music and welcoming people as well as distances; enjoy travelling with somewhere to return; answer difficult letters. |
| Aurelia | Make dependable lamps and handovers; enjoy dry humor and companionship; distinguish a useful check from repeated worry. |
| Neris | Make glass beautiful in use; enjoy colour, tactile experiments and teasing; acknowledge faults instead of defending a favourite feature. |
| Sabine | Make agreements understandable and invitations enjoyable; enjoy wordplay; notice when a clever line hurts its listener. |
| Maren | Build things their owners can repair; carve expressive creatures; ask before improving away something somebody values. |
| Brakka | Make careful fittings and small mechanisms; enjoy carvings and music; show the work she cares about beyond impressive strength. |
| Fenna | Remember the people who make a road welcoming; enjoy stories without betraying confidences; answer before escaping into a joke. |
| Kaede | Compete fairly and teach clearly; retain her interest in glasswork; allow herself to learn without coaching everyone else. |
| Elowen | Help people understand their own care and wards; grow flowers for colour and scent; listen before prescribing a solution. |
| Nyssara | Make work that can be questioned and checked; enjoy mysteries and dry humor; avoid discouraging an inexperienced questioner. |
| Sylva | Keep healthy plants and share responsibly; collect colours; state preferences before expecting others to infer them. |
| Velis | Arrange reliable supplies without unfairly charging the least powerful worker; enjoy letters and stargazing; leave room beyond business. |
| Rhess | Build a watch with proper relief; preserve personal keepsakes; name worry rather than silently taking another person’s shift. |

These motivations describe wishes and habits, not new quest completion, resource rewards or secret castle facts. Existing overlapping interests remain: for example, Kaede’s glasswork is compatible with her training role, and Tamsin’s bookbinding is compatible with her kitchen interests.

## Continuity corrections

- Neris’s repaired-cup follow-up no longer assumes the player invented the duck song on every branch. Only the matching saved choice supplies that callback.
- Fenna’s reassurance option now means what it says: enjoying her company without requiring a story, rather than answering “yes” to whether she is boring.
- Nyssara’s early affectionate callback refers to the warning-indicator anecdote actually shared, rather than assuming the later clock-charm story occurred.
- Rhess’s account of staying at the old boundary agrees with the quest record: most of the old watch had left before she arrived.
- Neris’s refund anecdote consistently says she returned the customer’s money and kept the faulty cup.

## Saves and installation

Schema 70 is unchanged. Existing memory records retain their saved opening, selected player line, answer, date and effects. Revisions apply to conversations not yet shared; no dialogue reset or replay reward is introduced. Legacy resident moments whose completed text is resolved from definitions were left unchanged to avoid rewriting saved history.

All 100 existing social scene IDs, choice keys and progression metadata were compared with v0.111. Existing personal chapter IDs, choice keys and room requirements are preserved. All 398 runtime artwork files match v0.111 byte for byte. Chapter 9, the foundation ritual chamber, resident bonding and friendship keepsakes remain included.

1. Stop the server and back up the complete `data/` directory, including campaign subfolders, accepted artwork and provider settings.
2. Extract the full release into a clean folder. Copy the existing complete `data/` folder into it, or retain your external `--data-dir` setting.
3. Restart with your usual command, such as `python server.py`.
4. Hard-refresh the browser. Open a companion’s **About** or **Talk** tab for the revised conversations.

No live campaign data is included. This archive has not been deployed to a hosted server.

## Verification

217 Python tests pass across dialogue, almanac, social life, household chapters, relationships, journeys, romance, intimacy, household sagas, resident bonding, friendships, the foundation chamber and release artwork. Seven new regression tests exercise the 135 personal disclosure branches and 81 pair branches, exact selected-line persistence, historical text preservation on reload, knowledge gates, the Neris callback and platonic camp questions. The final social-text changes also passed the affected 19-test subset.

Nine connected UI suites pass: almanac, social life, household chapters, relationships, party journeys, romance, intimacy, resident friendships and the foundation chamber. These exercise the real Python store with JavaScript templates and click handlers, including selected replies, hidden future text, navigation and reload. They are headless integration tests, not rendered browser tests. Desktop/mobile pixel layout remains unverified because the browser executable is unavailable.

Older tests with obsolete schema expectations or replaced wording were updated while retaining their state, cost, effect, gating and persistence assertions. `DIALOGUE_REVIEW_V112.json` records editorial scope and compatibility checks; `VERIFICATION_V112.json` records the test matrix.
