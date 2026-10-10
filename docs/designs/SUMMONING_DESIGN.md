> Current direction, v0.116: solo play uses authored and scripted narrative; an LLM gamemaster is optional. See [../SCRIPTED_SOLO_V116.md](../SCRIPTED_SOLO_V116.md) and the v0.116 release notes. The dated implementation records below are historical. Eris/Selene co-op remains deferred.

# Stonework and Spellcraft — summoning and persistent residents

Design draft · 4 October 2026 · based on the consolidated v0.1 specification and the v0.20 prototype.

**Status:** the first authored contact/visit/membership cycle is implemented in prototype 0.22. The broader generated-candidate design remains future work. Existing campaigns migrate without automatic contacts or arrivals. This does not establish the final first recruit, castle secret, a canonical summoned character, or working co-op. Costs and durations below are explicit provisional prototype values.

## 1. The experience

A summoning ritual opens an introduction, not ownership of a person. The player chooses a broad kind of contact, prepares a modest working, and meets an adult prospective visitor with an identity and interests that already exist. Conversation establishes what each person wants. Crossing into the castle, visiting, deciding to stay, and joining the household are separate events.

The invitation should feel like opening a door in a quiet library: a voice from elsewhere, a question about the room beyond, someone deciding whether to step through. Use the established dark paper, violet ink and restrained gold. No glossy portal spectacle, mandatory character animation, or furniture overlays. A new portrait remains optional and goes through the existing illustration review flow; a readable identity card works before approved art exists.

There are no expiration timers, recurring mana charges, forced service contracts, affection costs, or disappearance when a caster changes assignments. Contact can wait; a visitor can decline; a permanent resident does not become dependent on maintaining the ritual. Arrival never establishes romance or a work agreement.

## 2. First playable scope

Build one general contact ritual and one authored adult candidate fixture before enabling generated candidates. The fixture is explicitly sample content. It exercises the complete lifecycle and migration behavior without pretending that generated recruitment already works.

The general category is **a curious practical-magic visitor**. It sets a broad reason to meet, not a specific exotic ancestry, appearance, perfect skill list or romantic preference. Later categories can emphasize horticulture, craftsmanship or scholarship. Categories filter compatible candidates; they cannot rewrite an existing candidate to fulfill a new wish list.

The first ritual is **The Open Threshold**. Its discovery enters the shared archive as the principle **Courteous passage**; each conductor must study that principle personally. A proposed unlock is completing the existing concordant lesson, followed by an explicit archive research project. The existing lesson already requires the living index, personal understanding and coordinated work. This connects the new mechanic to established progression without requiring intimacy, a particular Resonance value, an augmentation or external agents.

Provisional first-slice numbers:

| Work | Cost | Assigned phases | Result |
|---|---|---|---|
| Research Courteous passage | 12 shared crowns | 3 research contributions | Records the principle in the archive; contributors still follow personal-mastery rules |
| Study the recorded principle | Existing principle-study rules | Existing duration, including the lesson tablet | Personal understanding only |
| Prepare one Open Threshold contact | 12 shared crowns; one vessel component and one binding component | 2 conductor phases | One stable contact channel with one candidate |
| Discuss intentions, accommodation and proposed visit | None | None | Recorded statements and decisions; no assumed agreement |
| Agree an arrival | None beyond the completed contact working | Resolves on the next Advance | The candidate crosses as a visitor into her reserved accommodation |
| Decide household membership | None | None | Separate recorded decisions from candidate and household |
| Agree a departure | None | Resolves on the next Advance | Removes physical occupancy while preserving the person and history |

These values should be tuned through a real playthrough. Contact preparation uses one primary assignment. It grants no parallel research or crafting action. No recurring upkeep is introduced.

## 3. Separate state tracks

Do not encode every decision in one ambiguous `summoned` boolean.

### Contact working

| `contactStatus` | Meaning | Available next action |
|---|---|---|
| `planning` | Category and conductor selected; nothing committed | Review costs, fund, or discard this uncommitted plan |
| `preparing` | Exact money and components committed; work can progress | Advance, change assignment to pause, resume, or cancel |
| `awaiting-candidate` | Ritual work complete; identity preparation has not yet produced a valid candidate | Prepare/validate a candidate explicitly; recover an interrupted request |
| `open` | A validated identity exists and contact can be used | Talk, discuss a visit, set contact aside, or close it |
| `closed` | Contact is no longer active | Read its history; explicitly reopen contact with the same person |
| `cancelled` | An unfinished preparation was cancelled and refunded | Read the record; create a new plan if wanted |

`awaiting-candidate` is an integration state, not fictional punishment. A provider outage cannot consume a second ritual payment, advance time, invent a replacement person, or turn failed generation into an arrival. The authored fixture bypasses external generation while exercising the same validation boundary.

### Person’s relationship to the castle

| `residencyStatus` | Meaning |
|---|---|
| `remote` | Known through contact; no physical bed occupied |
| `arrival-agreed` | Both sides accepted a visit and a suitable bed is reserved |
| `visiting` | Physically present; has accommodation and personal downtime, but is not a staff member |
| `resident` | Candidate wants to stay and the household has separately accepted her |
| `departure-agreed` | A departure is recorded and awaits Advance |
| `away` | The person is elsewhere; identity, possessions and history remain recorded |

A candidate’s decision is separately recorded as `undecided`, `wants-to-stay` or `prefers-to-leave`. The household decision is `undecided`, `invite-to-stay` or `do-not-invite`. Only compatible positive decisions change a visitor to `resident`. Deferring either decision leaves her a visitor without a timer. A contradictory pair never silently resolves in the player’s favor.

An ordinary departure is not deletion, death, banishment, or loss of identity. Recontact points to the same person. Permanent removal of a person’s record is outside this feature.

## 4. Identity exists before conversation

Each candidate gets a stable `personId` and an immutable identity revision before the first line of conversation. A model may propose a candidate record; it cannot repeatedly rebuild her based on what the player asks for while speaking.

The first fixture must specify an unambiguous adult age and adult life stage, a coherent origin independent of the castle’s unknown secret, personal interests, capabilities, offered work, accommodation preferences, an initial ambition, and a reason to consider visiting. Do not reuse Eris or Selene as summoned NPCs.

A generated candidate goes through two distinct validations:

1. **Structural and mechanical validation:** supported fields and identifiers; allowed capability budget; coherent skill/principle combinations; bounded text; no unknown effect definitions or fabricated inventory.
2. **Content review:** an adult, coherent character within the warm household premise, with meaningful preferences and no promises of compulsory romance, obedience or cruelty. Passing a JSON schema alone does not establish these qualities.

The initial implementation uses a reviewed fixture. Generated candidates remain gated until an appropriate content-review workflow exists. Rejected proposals stay generation drafts and never become people in the campaign. Once accepted into the person registry, identity is stable and corrections must be explicit, attributable revisions.

Mechanical proposals use existing skill, practice and principle identifiers. New ancestry labels or prose cannot create immunity, extra action budgets, unrestricted magic, free artifact production or other uncatalogued advantages. Starting competence has its own explicit budget and provenance; do not disguise it as farmable earned advancement. The first fixture should demonstrate uneven expertise, not superior ranks in every discipline.

Public introductions contain what the candidate has shared. Private background, undisclosed ambition details and conversations with someone else stay in their own visibility scope. Category selection is not authority to inspect every hidden fact about every candidate.

## 5. A visit needs a real place

Contact is allowed without spare beds. The player can learn who someone is and return later with an appropriate invitation. An arrival cannot be agreed without compatible, available accommodation.

A visit offer specifies the room and its current occupancy. Preferences are validated against the actual housing record, including private-room requirements. One accepted offer creates one named reservation linked to the person and invitation. Neither a generic bed reservation nor another arrival can overwrite it.

On Advance, validate the reservation again before arrival. If it is no longer usable because of a correction or unexpected state conflict, keep the candidate remote with the invitation intact and show the exact blocker. Do not move another occupant, charge again, select a different room, or place the visitor in a fictional spare bed.

A visitor occupies a bed in the housing summary but is excluded from workforce selectors, automatic allowance plans and staff work orders. Household membership must not be inferred from being physically present. Food and ordinary necessities remain abstracted under the existing household design; no punitive visitor maintenance loop is added.

Withdrawing an arrival agreement releases only its named reservation and leaves the contact history intact. Nothing automatically draws personal funds. The first slice does not charge an arrival fee.

## 6. Conversation and agreement

The contact screen offers three substantial topics: reasons for meeting, practical household life, and the proposed visit. The candidate can ask questions in return. Work interests, privacy and personal plans are discussed before a membership invitation.

Authored dialogue supplies the first candidate’s decisions. Optional generated prose may phrase a response from established facts, but cannot change a preference, accept a visit, sign up for work, approve a room or establish romance. Those transitions require explicit rule-validated actions backed by the candidate’s recorded offer or decision.

The interface distinguishes:

- “She would consider visiting” from “She has accepted this visit.”
- “She likes restoration work” from “She has agreed to this assignment.”
- “She wants to stay” from “The household has accepted her.”
- “She is friendly” from any mutually established flirtation.

No persuasion score can purchase consent, and repeating a topic cannot manufacture agreement. Topics can be revisited without rewards. Preferences may develop later through authored personal stories or validated narrative developments, with history preserved; they do not adapt silently to whichever room is currently convenient.

## 7. Costs, pauses and recovery

Funding is atomic: validate the conductor, personal principle, room, money and the aggregate component quantities before changing anything. Default to unreserved shared materials. If the same item fills two property slots, require two copies. A failed validation changes no state.

Cancellation before completing contact preparation returns the exact committed crowns and components once and discards unfinished work. Once the preparation is complete, its cost is spent; closing a successful contact does not turn it into a refundable resource farm. Ordinary reopening of that saved contact costs no additional ritual materials in this first slice and does not reroll identity.

Provider requests are explicit, bounded, saved and idempotent, with credentials outside campaign exports. A lost response is recovered by request ID. An interrupted `processing` record never triggers an automatic second paid call. The completed working remains available for recovery or an explicit new generation request; the player is warned only about potential provider usage, not charged fictional resources again.

Every state-changing request has campaign ID, expected revision and request ID. Double clicks, stale tabs and reconnects cannot duplicate refunds, arrivals, reservations, residents or capability grants. Reopening a contact and restarting generation are visibly different actions.

## 8. Human-readable records

Proposed records, with names describing what they actually mean:

| Record | Important fields |
|---|---|
| `people[personId]` | `name`, `adultAgeYears`, `lifeStage`, `ancestryLabel`, `role`, `identityRevision`, `identitySource`, personal preferences and existing character-sheet references |
| `summoningContacts[contactId]` | `conductorId`, `categoryId`, `personId` or null, `contactStatus`, `completedWorkPhases`, `requiredWorkPhases`, `committedCrowns`, exact `committedMaterials`, `generationRequestId` or null |
| `residency[personId]` | `residencyStatus`, `candidateStayDecision`, `householdStayDecision`, `agreedRoomId`, arrival/departure phase records |
| `arrivalReservations[reservationId]` | `personId`, `roomId`, `sourceType`, `sourceId`, `reservedBeds` (exactly 1 in this slice) |
| `contactConversations[contactId]` | Authored/generated line provenance, disclosed topic IDs and visibility scope |
| `identityRevisions[personId]` | Explicit correction history; never an implicit conversational reroll |

Do not introduce names such as `obedience`, `summonOwnership`, `loyaltyPurchased`, or `manaTether`. These are neither the intended mechanics nor useful hidden shortcuts.

Existing wallets, spellbooks, skills, practices, preparation sets, focus work, augmentation and personal possessions should remain keyed by `personId`. A new resident starts with explicit defaults rather than inheriting another character’s work, romance, allowance or preparation. Any exceptional starting expertise is recorded as starting expertise, distinct from accomplishments earned during play.

## 9. Required architecture change

The current prototype has a fixed `CHARACTERS` catalogue and several loops/branches that assume founder, Mira and Tamsin. Adding a summoned person to only `additionalResidents` would not consistently initialize or resolve her learning, housing, magic, equipment or context.

Before shipping arrivals:

1. Introduce a campaign-owned person registry with stable IDs, retaining `founder`, `mira` and `tamsin` as compatibility IDs.
2. Separate selectors for physically present people, household members, visitors and candidates. Audit every use of `CHARACTERS`, `household_members`, `character_at_castle` and direct named-resident branches.
3. Centralize default character record creation. Initialize each subsystem once through that function; use an immutable starting-capabilities record plus earned development.
4. Generalize named arrival reservations so ordinary recruitment and summoned visitors use one capacity calculation.
5. Keep existing Mira/Tamsin authored scenes as content keyed to their identities. Do not accidentally grant those scenes, projects or ritual participation to every new resident.
6. Preserve old saves, original identities, balances, assignments, preparation, private conversations and completed history. Migration must not contact a candidate, occupy a bed, grant an allowance, create romance or advance time.

This is the main implementation dependency. A summoning button added before this change would be a misleading partial feature.

## 10. Interface route

Add **Summoning** beneath Rituals rather than hiding contact under the artifact workshop. The screen has three sections:

- **Prepare a contact:** conductor, broad category, prerequisites, supported component substitutions, exact payment and work forecast.
- **Known contacts:** name/identity card, status, last public conversation, deferred topics and the next available step.
- **Visitors and invitations:** actual accommodation, candidate’s stated wishes, household decision, arrival/departure readiness and plain-language blockers.

A contact card opens the conversation directly. It does not automatically launch a scene on Advance. The household overview can surface one invitation, with a count/link to the rest; it should not require speaking to every contact every phase.

Room views continue to use the illustrated background and readable occupancy/furnishings panels. Use a clearly labeled portrait placeholder until approved art exists. Candidate illustration requests must preserve the already-fixed identity instead of designing a different person and rewriting the record to match.

## 11. Acceptance checks

| Case | Required result |
|---|---|
| Unknown principle or wrong components | Clear blocker; no money or stock changes |
| Same component selected twice, only one owned | Atomic rejection |
| Switch conductor to another assignment | Preparation pauses with committed resources preserved |
| Cancel unfinished preparation twice | Exact refund once; second request cannot mint resources |
| Finish contact, then close and reopen | Same identity and history; no reroll or refund |
| Generation fails or response is lost | No arrival, extra ritual fee or automatic provider retry |
| Model asks to add an unknown skill/effect | Reject draft before creating a person |
| Model prose says “I accept” without a valid decision record | No arrival or membership transition |
| Contact with no spare room | Conversation allowed; arrival blocked |
| Two invitations compete for one bed | First valid reservation holds it; second is blocked |
| Visit accepted in a private room | Room preference and named bed are enforced on arrival |
| Visitor arrives | One physical occupant; no automatic workforce role or allowance |
| Only one side wants permanent membership | Visitor remains a visitor; no implied agreement |
| Both sides agree membership | One initialized resident; identity/history unchanged |
| Departure or later return | Stable person; no deletion, duplicate recruit or lost possessions |
| Contact while founder is away | Read history; no unestablished remote ritual/conversation power |
| Old save migration | Existing balances, residents, reservations and time preserved |
| Co-op mode requested without real agent integration | Remains unavailable; no proxy founder approvals |

## 12. Implementation order and boundary

**First:** registry, selectors, centralized initialization and housing reservation migration, covered by regressions for the current roster.

**Second:** authored contact ritual and one fixed adult fixture; complete the contact → agreed visit → visitor → two-sided membership lifecycle, including cancellation, departure and recovery.

**Third:** approved portrait and contextual household integration, offered personal development, private dialogue scope and normal work agreements.

**Fourth:** bounded generated candidate proposals and a content-review workflow, then actual provider verification. Generated identities cannot become residents merely because a response parsed successfully.

**Later:** additional categories, exceptional named contacts, more unusual ancestries, candidate-specific personal stories and genuine co-op proposals/approval. Those require their own content and integration work.

The first release should be called an authored summoning prototype. The final opening campaign, castle truth and canonical first recruit remain separate decisions and are not specified here.


### Implementation checkpoint — prototype 0.21

The first part of the foundation now exists: campaign-owned identities for the current authored cast, known-person and present-member selectors, runtime profile reads, named bed reservations, migration, cancellation/reinvitation, and arrival accommodation revalidation. The existing recruitment still uses its compatibility status record. Centralized subsystem initialization, generalized visitor/residency decisions, and the authored summoning contact cycle are not yet implemented. The full “First” milestone above remains open until those remaining registry integration points are covered.


### Implementation checkpoint — prototype 0.22

The authored lifecycle is now implemented with Iona, a 23-year-old demon threshold surveyor. Separate present-person/household selectors, centralized new-character initialization, generic named arrival reservations, individual development integration and identity-specific original scenes support the fourth character. Contact, visiting, two-sided membership, departure and same-person return are playable and tested.

Implementation scope choices: the authored fixture moves directly from completed preparation to `open`, with no provider or `awaiting-candidate` state. Its identity has no unshared private-background fields. Iona explicitly offers visiting and, when asked during a visit, staying; no persuasion score changes that authored decision. The household can defer or decline. Before departure, committed work must be finished or cancelled; allowances cease when departure is agreed and their planned amount is cleared on crossing. Her existing money and belongings remain saved. The portrait is a labelled placeholder, not generated art. The single enduring fixture prevents duplicate-Iona recruitment.

The generated-content validation/recovery path, broader categories, additional authored decisions and personal stories, and approved character art remain open. No full generative gamemaster or final campaign canon is implied.


### Implementation checkpoint — prototype 0.23

Iona now has a bundled portrait, her own atlas ambition, an optional personal map-case request, offered tea-tin possession, five authored household moments and a shared scene with Mira. These use her persistent personal records and preserve history/ownership across departure and return. Funded professional and personal work blocks departure until completed or cancelled. Illustration updates remain separate from identity, costs, relationships and time. Generated candidates and a larger category catalogue remain unimplemented.


## Standing NPC and portrait rules (v0.24)
All NPCs are clearly adult, aged 18–25 inclusive. All summoned NPCs have exotic ancestries: demons, seraphs, dryads, nymphs, elementals, vampires and other deliberately authored exotic peoples; common ancestries cannot enter through summoning. Ordinary recruitment can include humans. The player character is separately configured.

Strive for a diverse ensemble: vary facial features, skin tones, body builds, heights, hair textures, hairstyles, cultural influences, temperaments and exotic silhouettes. NPCs should be young and beautiful, cute, sexy, or a combination, with individual adult appeal. Cute means an adult aesthetic, never childlike anatomy or presentation. Do not reduce ancestry or skin tone to a personality, morality, occupation or sexual stereotype. Preserve personal preferences and agency; attractiveness is not consent or a mechanical reward.

Portraits retain the handmade ink/gouache aesthetic, midnight paper, muted violet and worn gold. Varied appeal comes through expression, posture, silhouette and practical fantasy clothing, with restrained lighting. Avoid interchangeable faces or bodies, glossy finishes and opulence. Future cast design should review variety across the ensemble before accepting a new portrait.

Current revisions: Mira, human archivist, 22; Tamsin, human bookbinder, 25; Iona, demon threshold surveyor, 23. Iona has muted violet skin, small swept horns and pointed ears. Both original residents and their shawl variants have revised adult portraits. Schema 23 updates existing identities without resetting progression and archives active portrait overrides for optional rollback. This user-directed revision is distinct from in-world summoning and does not grant ancestry powers.

Iona’s personal visual direction: sensual, self-possessed and knowingly playful, with a fitted plum bodice, a flattering low neckline and a relaxed bare shoulder. Preserve her recognizable face, horns, muted violet skin and practical survey equipment. Her sensuality is part of her individual character presentation.

### Implementation checkpoint — prototype 0.25
Iona has authored everyday conversations, optional reviewed personal dialogue, remote read-only history and a crossing timeline. Draft context is scoped to her own records and introduced household facts; membership remains separate from flirtation or conversation. Generated candidate proposals remain the next major summoning milestone.


### Implementation checkpoint — prototype 0.26
The authored catalogue now contains Iona, Aurelia and Neris. Candidate selection precedes paid preparation. Each person has a unique contact and persistent personal state. Conductor budgets cannot be multiplied by opening multiple concurrent workings. New contacts share the ordinary visit/residency lifecycle with candidate-specific topics and independent accommodation choices. This catalogue is deliberately authored; no model candidate is admitted automatically.

Adult fanservice is a central visual and tonal direction: glamorous fitted fantasy clothing, alluring expressions, bare shoulders or midriff, draped necklines and graceful silhouettes, with distinct individual styles. Aurelia’s accepted design uses warm golden-tan skin, pale braids, feather wings and a violet wrap dress. Neris has sea-glass skin, a silver bob and an indigo halter with plum wrap skirt. Preserve the dark handmade surface treatment and readable, useful interface. Both retain their own interests and chosen conversational warmth.


### Implementation checkpoint — prototype 0.27
Aurelia and Neris now have their own professional projects, illustrated clothing choices, saved personal styles, independent invitations, shared household scenes and return greetings. All use their existing persistent identities. No wardrobe choice is imposed by joining, and no portrait change affects mechanics. The authored lifecycle is ready for future candidate-review work; generated candidate admission remains unimplemented.


### Implementation checkpoint — prototype 0.28
Bounded generated proposals now support saved recovery, mechanical validation, human content review and approval into a fixed contact plan. The plan is reviewed before funding; contact preparation then introduces the person using the ordinary lifecycle. This staging avoids spending game resources on failed provider calls. Generated identities can be visit-only. Optional personal dialogue and separately reviewed portrait uploads work for introduced candidates. See CANDIDATE_REVIEW.md for the full workflow and remaining limitations.
