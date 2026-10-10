# v0.113 — Conversations to return to

All eight proposed improvements to companion dialogue are implemented across the fifteen named residents. This is the complete installable game, including the castle investigation, Chapter 9 and the foundation ritual chamber, resident bonding, friendship activities, existing chapters and all artwork. It has not been deployed to a hosted server.

## Find the new content

Open **Companions → a resident → Talk → Conversations to return to**. Share her first personal disclosure in **About** to open the new personal conversation. A conversation between two residents opens after both first disclosures. Home invitations and room links lead directly to an available exchange.

There are **46 new conversations**, comprising **115 exchanges** and **329 authored response choices**:

- Fifteen personal conversations with three exchanges each.
- Fifteen personal follow-ups with two exchanges each.
- Eight conversations between residents with three exchanges each, covering all fifteen companions.
- Eight later conversations between those residents with two exchanges each.

Each exchange offers two to four specific responses with distinct replies. Follow-ups become available one day phase after the preceding conversation finishes. Nothing expires. Every answer saves immediately, so changing pages, setting an invitation aside or restarting the server preserves your place. Everyone involved must be home to continue.

## What the conversations do

| Improvement | Result in this release |
| --- | --- |
| Deeper conversations | Multi-exchange conversations let the player question an opinion, share or withhold a preference, then respond to the companion’s decision. A later visit develops the subject. |
| Remembered player preferences | Each resident asks her own concrete question. Her later invitation reflects the answer, including uncertainty or privacy. About and Talk show the latest answer and allow a correction. Knowledge is scoped to the resident who heard it. |
| Competing motivations | A favourite book can be comforting yet unconvincing; a beautiful cup can pinch; wanting a rematch can conflict with being a fair opponent. Companions make their own choices. |
| Lasting disagreement | Respectful disagreement earns the same trust as agreement. Later personal conversations acknowledge the disagreement without pretending the player changed their mind. |
| Shared history | Later visits bring a revised drawing, a finished story, a tested explanation or the missing notes of a tune. Shared jokes recur in context. A follow-up can establish a specific tradition, or remain a single visit. |
| Emotional range | Pride, embarrassment, curiosity, amusement, irritation, pleasure and quiet company arise from concrete events. Conversation is not always advice or reassurance. |
| Independent resident relationships | Residents compare work, negotiate games, protect another person’s story and arrange exchanges directly. The player can contribute, question or listen without deciding everything for them. |
| Editorial review | Every authored node and response was reviewed against the writing guide and established voices, with attention to actual answers, distinct choices, ordinary language, callbacks and spoken cadence. Cadence was reviewed as text; no audio performance is claimed. |

## Personal subjects

| Companion | Conflict or interest | Preference she asks about |
| --- | --- | --- |
| Mira | Her favourite ending versus the ending she considers easier to defend | Hopeful or convincing, possibly unhappy endings |
| Tamsin | Finishing an agreed repair while keeping time for her own enjoyment | Games or reading side by side |
| Iona | The pleasure of a detour versus the route someone agreed to | A stated plan or an optional detour |
| Aurelia | Improving the light versus enjoying the view and company | Reading light or the window seat |
| Neris | A graceful handle versus a comfortable cup | Striking colour or comfort in use |
| Sabine | The pleasure of theatrical wording versus a clear invitation | Plain invitations or playful flourishes |
| Maren | Correcting a harmless mistake versus keeping its expression | Marks with a history or neat repairs |
| Brakka | Keeping the pause she likes versus wanting approval | An explanation or trying the work first |
| Fenna | Telling a good story while protecting somebody else’s confidence | Openly invented comedy or an awkward true account |
| Kaede | Enjoying a rematch versus recovering wounded pride | Serious competition or a relaxed trial game |
| Elowen | Growing flowers for pleasure versus defending their usefulness | Listening first or a practical next step |
| Nyssara | Preserving reasoning while making an answer accessible | A short answer or the reasoning from the beginning |
| Sylva | Preserving a leaf picture versus watching it change | Tending plants or looking without a task |
| Velis | Checking work thoroughly versus inventing unnecessary business | A market outing or a quiet evening with the stars |
| Rhess | Keeping watch out of habit versus enjoying her own chair and keepsakes | Conversation or quiet company |

The resident pairs are Mira/Nyssara, Tamsin/Brakka, Iona/Rhess, Aurelia/Sylva, Neris/Kaede, Sabine/Velis, Maren/Elowen and Fenna/Rhess. Each has an initial disagreement or shared activity followed by a new outcome.

## Effects and boundaries

Conversation spends no phase, supplies or crowns and changes no work assignment. Completing a conversation gives Trust +1 to each participating pair once, capped at 12. The two residents in a pair conversation also receive the normal scene bonding contribution of up to 2 within their existing daily allowance. The foundation blessing increases eligible gains by 20%; the conversation displays the boosted amounts while it is active. Respectful disagreement, uncertainty and privacy do not reduce the completion reward.

Individual answers, rereading, preference corrections and setting invitations aside grant no additional reward. Completed conversations count as distinct shared memories for the existing outfit invitation requirements. They do not establish romance or bypass any private disclosure requirement.

An agreed tradition records an intention to share a specific kind of future visit. It informs the profile and scoped generated dialogue; it does not automatically schedule recurring events, reserve time, construct an object or grant an item. Companions retain their own opinions. Asking about an alternative during one visit does not silently replace a stored preference.

## History and presentation

The active exchange shows the previous selected response and the companion’s reply. Earlier exchanges remain in an expandable transcript. Finished conversations appear in **Journal → Memories**; unfinished ones appear among shared stories and can be resumed. Preference corrections also have journal entries. All saved words remain historical records when authored copy changes.

The Talk page uses collapsible conversation cards, readable prose, full-width response buttons, visible progress, clear requirements and keyboard focus when following an invitation. Only reached dialogue and offered response labels are sent to the client; future answers and unchosen replies stay out of the public view. Generated dialogue receives only the participating resident’s actual conversation history and latest shared preference.

The quality pass removed an unearned claim that Rhess witnessed Fenna’s old journey, replaced labels that assumed the player had already objected, and corrected wording that tied a follow-up to yesterday or a visible night sky despite phase-independent availability. The interface version, server header, health endpoint and browser asset cache versions now consistently identify this release.

## Installation and saves

1. Stop the old server and back up the complete **data/** directory, including campaign subfolders, accepted artwork and provider settings.
2. Extract this full release into a clean folder. Copy the complete existing **data/** folder into it, or keep your existing external `--data-dir` setting.
3. Start the server with your usual command, such as `python server.py`, then hard-refresh the browser.
4. Open a companion’s Talk tab. Existing chapters, completed conversations and relationship history remain available.

Schema **70 → 71** adds a separate empty conversation store without rewriting any existing campaign fields or text. GameStore makes an automatic pre-migration SQLite backup. Use the complete upgrade backup if returning to an older application; an older engine cannot open a schema-71 save. No live campaign data or private settings are included in this distribution. All 398 runtime artwork files match v0.112 byte for byte.

## Verification

**245 unique Python tests pass** across the new conversations, existing dialogue and social systems, journeys, romance, intimacy, resident bonding, friendships, outfits, the foundation chamber, artwork and HTTP health. The new branch tests exercise **1,812 complete path combinations**, covering every personal approach/preference/stance combination, every preference-aware follow-up outcome and every resident-pair branch. They also test knowledge scope, current-node visibility, correction history, no time or inventory changes, one-time rewards, the blessing, daily bonding caps, travel/defer gates, save migration, duplicate requests and stale revisions.

**Twelve connected UI suites pass.** The new suite completes all 46 conversations through rendered HTML controls and the real Python GameStore. It checks 115 saved exchanges, profile corrections, later callbacks, journal links, interruption/reload, a lost-response retry, escaping and direct navigation. Existing UI suites cover almanac, social life, household chapters, relationships, journeys, romance, intimacy, resident friendships, the foundation chamber, outfits and resident bonds.

These are headless template/controller integration checks, not rendered browser layout tests. Desktop/mobile pixel layout remains unverified because no browser executable is available. No actual audio or voiced performance test was performed. See `VERIFICATION_V113.json` and `DIALOGUE_REVIEW_V113.json` for the scope and results.
