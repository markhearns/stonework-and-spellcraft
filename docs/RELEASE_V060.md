# Development v0.60 — A place at the table

Shared conversations now develop persistent relationships with the founder and between companions. A new household story follows Mira and Tamsin through a disagreement, a negotiated arrangement, follow-through and a later invitation that no longer needs the founder to mediate.

## Where to begin

Open a **Character sheet** or **Life together → Conversations & friendships**. The new **Relationships & shared agreements** panel shows that person's preferences, boundaries, bonds and actual history. Home highlights a ready invitation.

With Mira and Tamsin resident and everyone home, **One table, two kinds of work** begins immediately. No friendship score, attribute, skill, room upgrade or spell is required. The story has six scenes; each later scene waits for at least one shared day phase after the preceding conversation. Only the existing Advance action advances time. Invitations have no deadlines.

## Three dimensions

- **Trust** records understanding and dependable follow-through.
- **Affection** records welcome company and warmth. It never automatically starts romance.
- **Respect** records honest differences, competence and boundaries. Candid disagreement does not incur a penalty.

Each dimension runs from 0 to 12. Zero means little newly tracked history, not dislike. Bonds describe mutual shared experience rather than a claim to know a person's private feelings. They are not consent, obedience or willingness to undertake a job.

Newly completed social-life conversations contribute once: curious responses add trust, warm responses affection and candid responses respect. Attribute alternatives follow their canonical response. A conversation with two companions also develops their bond with each other. Existing personal chapters, specialist chapters, pair chapters and room activities add trust once per distinct scene. Repeated room activities, rereading, deferred invitations and merely displaying a suggestion add nothing.

Practice and journey conversations also contribute once: noticing competence or giving thanks builds respect; discussing what was learned builds trust; celebration or company builds affection. No additional advancement, currency or supplies are awarded by talking. Assignments and world time do not change.

The history lists the actual changes for each pair. Scores stop at 12; a capped change is shown as +0. Existing ordinary dialogue and expedition methods remain available regardless of scores. Skills and attributes cannot override a personal boundary.

## Fourteen personal invitations

All fourteen established companions have individual preferences, boundaries, invitation openings and acceptance responses. Examples include Brakka inviting careful work with small pegs, Sabine telling an unpolished story, Kaede sharing an imperfect practice attempt, and Tamsin asking for company without hosting anyone.

After two distinct newly remembered moments involving the founder and that companion, an additional invitation becomes available. Accept on their terms, ask what would make them comfortable, or decline kindly without making a promise. Each response becomes a memory. This adds fourteen scenes and forty-two responses; it does not replace the existing social catalogue. Generated residents can accumulate bonds through supported shared scenes but do not borrow an established companion's authored personal invitation.

## One table, two kinds of work

Mira has spread fragile archive copies over a table Tamsin expected to use. The disagreement is about consideration and the kinds of work that get noticed. Neither person becomes the villain or requires a charisma check to be heard.

1. **One table, two kinds of work:** listen to what the interruption cost, name the misunderstanding, or offer company while they find words for it.
2. **What the room is for:** ask for reciprocal changes, protect the right to refuse, or include time without work.
3. **An agreement small enough to keep:** promise a planning conversation, a rehearsal of asking before taking space, or a break without work. Alternatively, offer support without promising your time.
4. **Returning to the table:** enact the promised conversation, renegotiate and complete a smaller agreement, or apologise and withdraw it. If no promise was made, hear how their independent trial went instead.
5. **The first awkward revision:** allow different habits, acknowledge each other's changes, or welcome an imperfect arrangement that is helping.
6. **A place left open:** join a conversation they began themselves, recognise their independence, or give them space without offence.

The story has nineteen authored response options across its branches. Later openings quote the actual previous choice. The final two scenes also recall the actual agreement and whether it was fulfilled, renegotiated, withdrawn or never promised.

Promises are specific social commitments fulfilled within the shared scene. They do not claim to finish construction, reserve rooms, change the work schedule or execute a spell. There is no expiry or automatic penalty for taking time. Withdrawing a promise with an apology reduces trust with each companion by one, with a floor of zero; the choice shows this beforehand. It does not reduce Mira and Tamsin's trust in each other. Both accept the apology without pretending the promise was fulfilled, and every later story scene remains reachable.

Later/restore controls are available. The most recently selected reply remains visible; other completed, set-aside and upcoming scenes can be expanded. Unavailable future scenes show their requirements but not their openings, choices or replies.

## Dialogue and saves

Optional generated dialogue receives only completed relationship memories and bonds involving the current speaker, plus the household agreement when that person participated. Future responses and unrelated private memories are excluded. Authored actions and relationship changes remain deterministic; generated dialogue does not decide their effects.

Release **0.60**, save schema **51**. Migration adds empty relationship records and preserves earlier memories, resources, assignments and unfinished work. Older scenes are not retrospectively scored. A fresh save and an upgraded save both begin accumulating this history through new shared moments.

Stop the old server, extract this release into a fresh directory, copy the complete existing `data` directory (including `data/assets`), then run `python server.py`. The store creates a pre-migration database backup. Keep the older release and backup for rollback. No offline time passes.

The archive retains all existing artwork, including the 38 spell and ritual icons. No new artwork was generated for this update.

## Verification

The Python suite passes **660 tests**, including all household-story choices and agreement branches, all fourteen invitations with each response, independent dimensions, NPC-to-NPC bonds, boundaries, caps, repeat protection, scoped dialogue context, deferred invitations, atomic rejection, schema migration, database backup, retry and reload.

Expedition regression now also completes the entire Stormwatch journey with four contrasting builds: minimum-attribute solo, scholar solo, an athletic pair and a diplomatic pair. Each encounter retains its patient method; the specialised builds use available alternatives. Merely adventuring does not invent a relationship conversation or award social scores.

**All 36 connected UI suites pass.** Results are recorded in `UI_REGRESSION_V060.json`. These tests exercise templates and controls against the real Python save/action layer, including the complete new story and a personal invitation. They do not inspect rendered layout. Browser review remains blocked by the previously observed missing local Chromium executable and inaccessible local server from the cloud browser. No new visual browser pass is claimed.
