# Development v0.61 — Quests and a little mischief

Character quests now come in two forms: fourteen authored personal adventures, and a procedural request board assembled from fixed, saved objectives. Both involve actual assigned work, alternative methods, remembered conversations and explicit rewards. Neither depends on runtime LLM interpretation.

## Where to start

Open a companion's **Character sheet**, or **Life together → Conversations & friendships**, and find **Stories, quests & a little mischief**. Home also highlights character quests and the current active adventure.

Each personal quest is available when its companion is a resident and both participants are home. Select a response to accept. Talking does not advance the day or assign work. At each obstacle, review the ordinary, skill and spell methods, then choose one. Starting work assigns the founder and companion to quest work only if both are currently free. **Advance** completes one shared work phase.

After the first obstacle, an optional conversation considers a new complication. After the second, an optional celebration completes the quest and awards the reward. Endings remember the opening response and the two methods actually used. Future scene text and replies are hidden from the quest interface until reached.

Only one quest is active at a time. **Set this quest aside** releases quest assignments and retains its progress, including paid spell components. Resume it later. If either participant is away or reassigned, progress pauses; the interface explains how to resume. Invitations never expire and no offline time passes.

## Personal quests

Each adventure has two work objectives and three conversation scenes, with a character-specific motive, complication, ending and flirtatious response.

Personal completions award **2 advancement to each participant** once and add a named keepsake to the quest collection. Keepsakes are remembered collectibles, not new equipment with unstated bonuses. These quests add to the older personal-story and relationship systems rather than replacing them.

## Procedural requests

**Generate today's requests** fills available spaces on a three-request board. It can be used once per in-game day. Unaccepted requests may be explicitly declined to make room; accepting, completing or declining a request never rerolls the remaining ones. Accepted quests may be set aside instead of discarded.

The generator combines a current authored companion, one of six request templates, one of six castle-ground locations and one of four social invitation hooks. Generation uses a deterministic saved seed, serial and day. The entire generated request is then stored: reads and reloads cannot change its patron, objectives, location, mood or reward. Different campaigns with the same inputs can produce the same sequence; this is procedural variation, not an AI narrator or a claim of limitless unique stories.

Templates cover a broken lantern, a mislabelled parcel, a rain-spoiled rehearsal area, a keepsake beyond an unsafe walkway, a jammed festival stand and an incomplete tune. Each has two objectives and an intervening conversation. Locations are small areas of the castle grounds, not claims to have unlocked a distant expedition site or restored a locked room.

Requests reward **2 binding thread** on completion. They do not award repeatable advancement. Relationship credit is granted only once for each companion/request-template combination, so regenerated requests cannot repeatedly farm affection. Each distinct finished request can earn its stated supplies through its actual assigned work. No reward is given for accepting, declining or merely reading it.

## Skills, spells and rituals

Seven obstacle families offer three methods each. All retain a free ordinary route. Skill methods require an attribute plus twice its skill rank to reach 9, including the existing +2 contribution from a capable present companion. Either participant can qualify.

| Obstacle | Ordinary work | Skill alternative | Spell alternative |
| --- | --- | --- | --- |
| Missing instructions | Compare and reconstruct pages | Intelligence + Scholarship | Lucid sight |
| Delicate mechanism | Clean, fit and test parts | Dexterity + Artifice | Borrowed hour |
| Heavy fitting | Move it on rollers | Might + Athletics | Giant's grasp |
| Misplaced keepsake | Search systematically | Intelligence + Fieldcraft | Wisp scout |
| Blocked water channel | Bail and clear by hand | Vitality + Athletics | Water jet |
| Damaged walkway | Secure a temporary crossing | Dexterity + Athletics | Windstep |
| Supplier's terms | Compare receipts and negotiate patiently | Charisma + Diplomacy | Silver suggestion |

Ordinary methods take **3 shared phases**. Qualified skill and spell methods take **1 shared phase**. Spell routes require one actual participant to have learned and prepared the spell and to know its principles. The interface shows the caster, components and blockers. Components are paid and the cast recorded once when the method is chosen; pausing or resuming does not recharge them. This fixed quest application replaces that cast's normal effect. It does not also create haste charges, summon a persistent wisp or influence unrelated conversations.

Relevant active household rituals reduce ordinary work to **2 shared phases**: archive for instructions and searches, maker for mechanisms, foundation for heavy fittings and walkway work, garden for water channels, and market for supplier negotiations. Spellbook and ritual descriptions list these additional applications. The duration and ritual contribution are saved when a method is chosen, so suspending a ritual afterward does not rewrite work already committed.

Quest workers do not simultaneously gain rest healing or perform a different assigned project. Progress eligibility is captured at the beginning of the work phase, and quest completion releases assignments after other work resolution. Changing assignments pauses progress without changing the saved method.

## Flirtation and fanservice

The personal endings include masquerade costumes, daring evening outfits, playful wagers, dancing, appreciative glances and romantic tension tailored to each companion. Sabine enjoys being admired without having her performance ignored; Tamsin enjoys dressing up without being put back to work; Kaede allows a little deliberate distraction during an imperfect attempt. The procedural celebrations have fourteen different companion flirt responses too.

Every conversation offers a flirtatious, warm or practical response. Friendly and practical completions earn exactly the same quest rewards. Flirting can develop affection; warmth builds trust and a practical appreciation builds respect. None automatically establishes romance or changes consent. The social reward is recorded once at completion.

Outfits described in a scene are narrative costumes for that occasion. They do not silently change equipped clothing, unlock wardrobe tiers or replace existing artwork. Existing portraits and the actual generated spell icons are used in the interface. No new quest illustration or costume art is claimed for this release.

## Saves and verification

Release **0.61**, schema **52**. Migration adds empty quest state without inventing completed tasks, generated offers or relationship rewards. Existing saves, stories, spells, relationships and unfinished work are preserved. The optional dialogue context includes only the speaking companion's actual quest memories and completed objective results, not future scene text.

Stop the old server, extract this release into a fresh directory, copy the complete existing `data` directory (including `data/assets`) into it, then run `python server.py`. A pre-migration database backup is automatic. Keep the older release and backup for rollback.

**677 Python tests and 37 connected UI suites pass.** See `VERIFICATION_V061.json` and `UI_REGRESSION_V061.json` for final checks. Coverage includes all fourteen personal quests in each social tone, all procedural templates, all seven spell routes and component costs, ordinary and skill alternatives, ritual acceleration and saved durations, assignment conflicts, phase conservation, pause/reload/resume, no retrospective migration rewards, duplicate requests, fixed procedural offers and restricted dialogue context.

Connected interface tests exercise the actual templates/controllers against the Python store. They are not a rendered browser review. The previously observed local Chromium and cloud-to-local access limitations remain unresolved; no new screenshot or visual-layout pass is claimed.

