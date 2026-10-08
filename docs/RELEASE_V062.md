# Development v0.62 — Closeness, at your own pace

This update connects the newer social systems to wardrobe progression and adds a mutual romantic progression for all fourteen established adult companions: four individually authored milestones each, relationship-aware greetings and quest celebrations, and optional dates in three leisure rooms.

## Start here

Open a companion's **Character sheet** or **Life together → Conversations & friendships**. **Closeness, at your own pace** shows the current stage and the next invitation. Home highlights an available invitation. Requirements are visible without exposing future openings or replies.

The four milestones are mutual attraction, a first date and kiss, agreement to become partners, and a private evening that establishes deep partnership. Each companion has her own invitation, response and title for every milestone: **56 authored scenes**. The scenes remain non-explicit, with teasing, affectionate closeness, kissing and private evenings.

## What advances a relationship

Existing trust, affection and respect make invitations available, alongside distinct remembered experiences. Scores do not automatically establish attraction, romance or partnership. You must select the mutual response in each authored scene. Every later milestone also requires at least one shared day phase after its predecessor.

| Invitation | Distinct shared memories | Trust | Affection | Respect |
| --- | ---: | ---: | ---: | ---: |
| Mutual attraction | 2 | 1 | 1 | 0 |
| First date and kiss | 4 | 2 | 2 | 1 |
| Become partners | 6 | 3 | 3 | 1 |
| Private evening / deep partnership | 8 | 4 | 4 | 2 |

Each accepted milestone adds one affection, subject to the existing cap of 12. Its memory can contribute toward subsequent history requirements. Trust and respect still come from the wider shared life. Re-reading does not grant anything again.

**Later** sets the next invitation aside without a deadline. **Keep our time together non-romantic for now** pauses romantic invitations and does not accept the milestone or reduce any relationship score. You may explicitly reopen the invitations later; reopening does not accept a scene or advance time.

The same preference control is available after romance has begun. Pausing suppresses romantic greetings, new milestones and dates, while retaining actual earlier memories and milestone history. Reopening restores the established context. This is an interaction preference, not an implemented breakup, reconciliation or exclusivity system; it does not fabricate such a story.

Ordinary conversations, friendships, work, spellcasting and expedition routes remain available. No romance is required for a gameplay reward. Conversations and dates do not move the clock, spend funds, reassign work or consume materials. The shared phase changes only through Advance.

## One connected history

Wardrobe evidence now includes:

- Completed scenes in the newer relationship system.
- Actual shared training and expedition-return conversations.
- The opening, interlude and completion conversations actually shared during character quests.
- Accepted romantic milestones and completed leisure dates.
- All previously supported personal stories, household chapters and social conversations.

A generated request contributes evidence by companion, template and conversation stage. Repeating the same procedural template cannot manufacture additional wardrobe evidence. Merely generating a quest or reading a future scene contributes nothing.

The existing relaxed and daring outfit invitation rules remain in place. Previously unlocked outfits remain unlocked, selected outfits remain selected, and migration does not invent relationship points or romance from old evidence. A remembered wardrobe invitation still precedes the separate choice to wear an outfit.

## Everyday behaviour and quest celebrations

Resting companions now have individual romantic greetings after mutual attraction. After the first date, the greeting can include an offered hand; established partners can greet the founder with a familiar kiss. Work greetings are not replaced with automatic romantic interruptions. Pausing romantic interactions restores the ordinary greeting.

Character-quest celebrations now draw on the actual milestone at the moment the celebration is shared:

- At acquaintance, the original light flirtation remains.
- After mutual attraction, the reply acknowledges interest both people have already expressed.
- While dating, the reply recalls the actual first date and an affectionate kiss.
- Partners celebrate with familiar affection and a recognised relationship.
- Deep partners can let the celebration become a quiet private evening.

When romantic interactions are paused, even a selected compliment is received as friendly. Previously saved quest replies remain unchanged; later milestones never rewrite an old memory. Quest rewards and the ordinary, skill, spell and ritual solutions remain identical across social choices.

## Dates and illustrated outfits

After the first mutual date, three optional outings become available for each companion:

- **An afternoon by the pool:** swimming, conversation and optional affection beside the water.
- **The quiet after the heat:** a comfortable break in the sauna's cooling vestibule.
- **Lanterns by the spring:** an unhurried evening on the hot spring's resting ledge.

The actual room must be restored, and both people must be current residents at home. These are three shared date templates usable with all fourteen companions, not forty-two independently written plots. Choose an affectionate date or quiet conversation. The latter does not erase the relationship or advance a romantic milestone. Each person/location memory is recorded once; rereading never farms points.

The date panel uses the existing generated room illustrations. Once dating, unlocked illustrated ensembles can be reviewed and explicitly selected from the same panel. The actual outfit catalogue and existing clothing artwork are used, including the more daring ensembles where already unlocked. A scene never claims to unlock a costume for which there is no implemented wardrobe entry.

Milestone and date memories save the outfit identifier and name actually selected at the time. Changing clothes later does not rewrite that memory. The regular character portrait continues to reflect current clothing. No automatic outfit changes occur.

No new art was generated for this release. All existing room artwork, outfit illustrations, portraits and 38 spell/ritual icons remain bundled. This release does not claim bespoke illustrations for all 56 milestone scenes.

## Saves, privacy and review

Release **0.62**, save schema **53**. Migration adds empty romantic-progression state and preserves existing quest, social, wardrobe and relationship records. Older friendships are not automatically converted to romances. No invitation is accepted or dialogue generated during migration.

Optional generated dialogue receives only the speaking character's actual milestones, date memories and current romantic-interaction preference. It does not receive another companion's private scenes or the text of unshared future milestones. All milestones and their effects remain authored and deterministic.

Stop the old server, extract the new release into a fresh directory, copy the complete existing `data` directory including `data/assets`, and run `python server.py`. The store creates a pre-migration database backup. Keep the older release and backup for rollback.

Verification includes all 56 authored milestones, all three date locations for every companion, score and history requirements, elapsed-phase gates, explicit friendly choices, later/restore, absence, invalid requests, preservation of resources and assignments, repeat prevention, actual outfit snapshots, shared wardrobe evidence, procedural evidence deduplication, scoped dialogue, migration, backup, idempotent requests and reload.

**692 Python tests and 38 connected UI suites pass.** See `VERIFICATION_V062.json` and `UI_REGRESSION_V062.json` for final results. Connected UI checks use the real templates/controllers and Python store. The previously documented browser setup limitations remain unresolved; no new rendered browser review or screenshot pass is claimed.

