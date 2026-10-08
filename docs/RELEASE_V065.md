# v0.65 — Stories between companions

Open **Household stories & connections** from Home, a character sheet, Household, Wardrobe or Equipment. The new collection gives all fourteen authored companions two or three central roles, with twelve overlapping casts and thirty-six scenes. Every scene has two authored choices: seventy-two responses across the collection.

These are deterministic authored stories. Optional language generation receives completed memories; it does not decide progression, costs, party presence or outcomes.

## The twelve stories

Every companion has a distinct part to play. Mira’s dry humour meets Neris’s elegant hypotheses and Nyssara’s suspicion of easy answers. Brakka is noticed for precision and thoughtfulness as well as strength. Tamsin gets to be a guest. Elowen gets the sharpest line in a rehearsal. Kaede practises recovering from an imperfect attempt without needing to conceal it. The fair lets four residents host together without appointing the founder to settle every exchange.

## Choices and actual history

The first choice establishes a practical or sociable approach and determines the optional project’s benefit. Later choices produce different remembered replies and develop trust or respect between the companions who are actually present. The founder witnesses these group scenes; they do not automatically grant romantic progress with the founder.

Later scenes quote the previous chosen response. When a participant has actually completed another story, a crossover recalls that story and the recorded choice, without inventing an unseen event. Room greetings can remember a shared story while a resident is resting. Existing relationship-aware romantic greetings retain precedence.

All central companions must be resident and home for their ensemble scenes. Let at least one explicit day phase pass between consecutive scenes. The final gathering requires its actual room to be restored. These are optional stories: other quests, ordinary expedition routes, recruitment and friendship interactions remain available without a specific cast or a romantic relationship.

Invitations can be set aside and restored. They never expire and never interrupt play. Reading a scene or preview, choosing a response and opening the relationship view do not advance time.

## Shared projects with actual workers

After the second scene, optionally agree a project:

- Four shared crowns and one **unreserved** binding thread, paid once.
- Two to four distinct workers chosen from the story’s cast and the founder.
- Two shared work phases. More workers do not make it faster.
- Every selected worker must be home and free to take the assignment. Other work is never silently replaced.
- Progress requires all selected workers to be present and assigned at the start of the phase. Completing another task during the phase cannot give a person a second action.
- Pause releases those assignments and retains paid progress. Resume uses the original workers and charges nothing again.
- Only one shared household project is active at a time; other household work can continue with other people.

Projects run on **Advance**. An NPC-only team can continue while the founder is travelling, provided no unresolved expedition choice is blocking Advance. Work appears in Advance preview and locates the workers in the relevant room. There is no automatic clock or autonomous offscreen scene resolution.

A practical project grants **+1 to the relevant approach score when two actual project workers are in the scored party**. It works alongside normal attributes, skills and helper contributions, but only one shared-project bonus applies to a check. Choose workers who can accompany one another on the routes you intend to use; existing expedition party limits are unchanged.

A sociable project supports matching **ordinary character-quest tasks for an actual worker**, reducing three phases to two. Ritual, lantern-corner and household support do not stack below two. The chosen method records its source of support and committed duration. Specialist and spell alternatives remain available.

You can instead choose **Gather without commissioning the project**, continuing the story with no project cost or mechanical benefit. The final room and presence requirements still apply. An unfunded project can be commissioned later, even after the story is remembered. A funded commitment keeps its progress and must be finished for that story’s initial concluding gathering; it can otherwise remain paused without obstructing unrelated play.

## Companion connections

The connection view shows actual established NPC-to-NPC bonds, with portraits, trust, affection and respect, and the events supporting them. Intermediate scenes can show different perspectives or friendly competition; concluding choices can establish easy company or professional regard. These descriptions reflect the most recent relevant shared scene, rather than an inferred hidden romance.

No bond, rivalry, secret or romantic relationship is invented on migration. Existing established bonds are also visible. Each scene’s contribution is applied once and respects the existing score cap. Reopening a remembered scene cannot farm relationship points.

## Fanservice and personal follow-ups

The stories include robe-and-ribbon teasing, a clothed fitting-screen evening, playful compliments, a bathhouse gathering, an evening costume rehearsal, capable-hands banter and a warm shared cloak. The tone is adult, flirtatious and non-explicit. Nobody has to romance a character to receive the complete ensemble story.

After a completed story, each of the fourteen companions can offer a distinct personal invitation. Mutual attraction opens it; the response reflects the actual relationship stage:

- Mutual attraction: a personal compliment and an invitation to draw closer.
- First date: a lingering kiss.
- Partnership: familiar affection and acknowledged togetherness.
- Established private intimacy: an unhurried private evening, described non-explicitly.

Quiet company remains an alternative within the invitation. Paused romance blocks these romantic follow-ups. The invitation never sets or advances a romantic milestone itself. There is one remembered personal coda per companion for this collection, not a repeatable affection reward for every story. The coda records the selected outfit and relationship stage; it does not equip clothing or generate new artwork.

## Company on the road

A travelling companion can recall a story they actually completed. If multiple members of that cast are travelling, only those actual party members speak. The founder is included as the present travelling listener. All fourteen companions have their own authored field lines.

The fair’s Mira/Iona pairing can converse together on the existing multi-companion lantern expedition. Other callbacks work on ordinary founder-plus-companion journeys. An absent participant receives no field memory or relationship credit. These optional conversations do not solve an obstacle, spend materials, change the party or advance time. Each story/speaker combination is remembered once.

## Integration and art

Completed story memories contribute to existing wardrobe history and can be displayed as genuine mementos in personal corners. Optional generated dialogue receives only completed group and field memories involving its speaker, plus that companion’s own personal coda. No future response or another person’s private follow-up is supplied.

The interface reuses existing approved portraits, the current fantasy-ledger framing and responsive layouts. There are no new character illustrations, room paintings or wardrobe assets in this release. Story prose does not grant outfits or replace persistent wardrobe selections. Rendered browser layout remains unverified under the previously documented environment limitations.

## Saves

Version **0.65**, save schema **56**. Migration initializes empty story records. Existing characters, artwork, relationships, resources, current work and earlier memories are preserved.

Stop the old server, extract the new release into a fresh directory, copy the entire previous `data` directory including `data/assets`, then run `python server.py`. The store creates a pre-migration backup. Keep the earlier release and backup for rollback.

**745 Python tests and 41 connected UI suites pass**, including 18 focused ensemble-story tests. Final automated results are recorded in `VERIFICATION_V065.json` and `UI_REGRESSION_V065.json`. Tests cover the whole cast, both choices in every scene, all twelve no-project endings, phase/presence gates, actual work assignments, exact costs, pause/resume, founder-away work, preview purity, bounded teamwork, ordinary-route support, romance stages, privacy, actual-party callbacks, migration and save retries.

