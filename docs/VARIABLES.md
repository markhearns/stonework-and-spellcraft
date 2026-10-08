# Human-readable variables

One concept per variable. Names describe the thing stored. States use words; numbers have defined units. Displayed values can be derived from canonical facts instead of duplicated.

| Variable | Meaning / unit | Allowed values or behavior |
|---|---|---|
| `schemaVersion` | Save-format version | Integer `15`; schemas 1 through 14 migrate automatically after a database backup. |
| `campaignMode` | The campaign's fixed mode | `solo` in this prototype; it is not a co-op toggle. |
| `campaignName` | Sample save's display title | A home in the old stones. Not the selected final game/castle name. |
| `revision` | Number of committed save mutations | Starts at 0; increases after every accepted action, including cosmetic ones, and once on a save migration. Not elapsed game time. |
| `dayNumber` | In-world calendar day | Starts at 1; increases only when evening advances. |
| `currentDayPhase` | Current portion of a day | `morning`, `afternoon`, `evening`. |
| `selectedRoomId` | Last room opened | `common-room`, `library`, `bedchamber`, and `conservatory` after restoration. |
| `roomFurnishings` | Chosen supported item for each room's fixed slot | Room-specific named variants; `none` clears that optional furnishing from the room inventory. |
| `wardrobe.ensembleName` | Name of the resident's base ensemble | The archivist. |
| `wardrobe.outerLayer` | Selected outer garment component | `none` or `plum-shawl`; no numeric costume codes. |
| `savedStyles` | Named saved garment configurations | Up to 8. Saving the same name updates it. |
| `sharedFunds` | Prototype shared money, in crowns | Starts at 80. The sample research project costs 20 once. |
| `researchCompletedPhases` | Resolved phases of work on the sample project | 0–3; cannot grow after completion. |
| `researchRequiredPhases` | Work duration in phases | 3 in this provisional project. |
| `researchStatus` | Project's lifecycle | `not-started`, `in-progress`, `complete`. |
| `resonancePoints` | Accumulated passive magical response to the household's erotic expression | Non-negative points; prototype-only scale, no finalized upper bound. |
| `completedDevelopments` | Named persistent developments already resolved | Currently `shared-flirtation`. Serves as a one-time event record. |
| `invitationStatus` | Availability of the sample personal invitation | `available` or `completed`; it does not expire. |
| `relationshipDescription` | Plain-language account of the relationship | No displayed affection number; not permission for unrelated activities. |
| `conversation` | Recent authored/scripted dialogue history | Speaker and text, most recent 60 entries. |
| `journal` | Recent significant resolved changes | Day, phase and text; most recent 100 entries. |
| `assetOverrides` | Current accepted replacement for an illustration | Local uploaded-image path, keyed by semantic asset ID. |
| `assetHistory` | Previous accepted images per asset | Stack of paths, used for rollback. Original art remains bundled. |
| `correctionRequests` | Saved illustration correction briefs | Asset, note, `awaiting-external-artwork`; up to 50 in this prototype. |
| `requestId` | Unique identifier for an API mutation | Used to safely replay the same request after a connection interruption. Not in-world data. |
| `expectedRevision` | Save version the caller based its action on | Must match current `revision`; stale actions are rejected for review. |

## Derived values, never independently writable

| Variable | Definition |
|---|---|
| `residentRoomId` | An active archive/garden assignment places Mira at that workplace. On her own routine she visits the library in the morning, common room in the afternoon, and guest chamber in the evening. |
| `resonancePerPhase` | 1 when shared flirtation is established AND the common room has the velvet settee; otherwise 0. Clothing does not factor into this prototype rule. |
| `resonanceStage` | `Quiet` at 0 points; `Stirring` from 1 to 5; `Awakening` at 6 or more. |

## Resolution order

1. Validate request identity and expected save revision.
2. Validate and apply the requested action inside one transaction.
3. For **Advance** only: resolve assigned castle work, garden production, facility work, personal-project contributions and learning; resolve expedition progress; check the living-wing milestone; calculate Resonance and its cosmetic unlock; then move to the next phase and update the day when needed.
4. Record resulting journal changes and increment save revision.
5. Commit and return state with derived display values.

Decoration, wardrobe, conversation and illustration correction are saves, but are not turns. Research cannot advance by reloading. An invitation cannot award its one-time points twice. Invalid actions commit nothing.

The frontend uses `currentView` for navigation, `reviewAssetId` for the illustration currently being inspected, and `proposedArtwork` for an unaccepted image preview. These are UI state, not game mechanics. An unaccepted preview is deliberately discarded on reload.


## Expansion variables (schema 2)

| Variable | Meaning and allowed values |
|---|---|
| `founderAssignment` | Scholar's one primary work choice: `rest`, `research`, `restoration`, `crafting`, `facilities`, `commissions`, `training`, `archive-project`, or rules-managed `expedition`. Starting a project selects it; completed work returns the scholar to `rest`. |
| `residentAssignment` | Mira's offered work: `rest` (own routine), `archive` (assist research), `garden`, `crafting`, `training`, `archive-project`, or expedition-controlled `expedition`. Archive assignment remains an archive routine if there is no active research. |
| `restorationStatus` | Conservatory lifecycle: `not-started`, `in-progress`, `complete`. |
| `restorationCompletedPhases` | Work phases contributed by the scholar, from 0 through 3. |
| `restorationRequiredPhases` | Total required work phases: 3 in the sample. |
| `gardenProductionChoice` | Persistent choice: `silver-ivy`, `surplus-sales`, or `stock-first`. Base staffed yields are one ivy or four crowns; installed upgrades and unattended tending are described below. |
| `materialInventory` | Non-negative whole item counts, keyed by readable material IDs. |
| `craftingProject` | Active recipe, committed material IDs, and `completedWorkPhases`, or `null`. |
| `craftedArtifacts` | Counts of completed artifacts keyed by recipe ID. |
| `lanternDisplayed` | Whether one owned warming lantern is shown in the common room. Boolean; does not consume the artifact or grant a mechanical bonus. |
| `lastPhaseSummary` | Human-readable account of the last resolved phase, retained in the save. |
| `availableRoomIds` | Derived list of accessible rooms, excluding the conservatory until restoration completes. |
| `nextPhaseForecast` | Derived plain-language forecast of work and production under the current assignments. |

A **work phase** is one character's contribution during one time phase. The scholar and Mira together can contribute two work phases to research during one Advance; the scholar alone contributes one to restoration or crafting. No character can contribute to two productive assignments at once.

During Advance, assigned work resolves before garden production; a room must have been restored at the start of the phase to produce. Resonance then resolves, followed by the phase/day change. Costs and components are committed once when a project starts. Paused projects keep committed materials and progress. There is no cancellation/refund for a started project in this slice; material purchases themselves can be reversed through individual sales.


## Expedition variables (schema 3)

| Variable | Meaning and units |
|---|---|
| `expedition` | Current expedition record, or `null` when the scholar is home. |
| `expedition.siteId` | Named destination: `old-waterworks`, `reedbank-waystation`, or `hillfold-bindery`. |
| `expedition.stage` | `outbound`, `awaiting-choice`, `working`, `ready-to-return`, or `returning`. |
| `expedition.chosenApproach` | `survey`, `salvage`, or `null` before a choice. |
| `expedition.remainingWorkPhases` | Whole phases needed to finish the chosen on-site work. Survey needs 2 without a lantern or 1 with it; salvage needs 1. |
| `expedition.carriedLantern` | Whether an owned warming lantern was packed before departure. It cannot simultaneously be displayed at home if it is the only one. |
| `expedition.restoreLanternDisplay` | Whether to return that particular lantern to its prior home display upon arrival. |
| `expedition.discoveryReady` | Whether the on-site work finished and its finding is ready to bring home. Does not itself grant a reward. |
| `expedition.departureDay` | In-world day the journey was committed. |
| `waterworksDiscoveries` | Completed leads already returned to the household. Each named lead grants its reward once. |
| `lastExpeditionReport` | Last site, approach, return-resolution day, and plain-language rewards. |
| `founderKnownPrinciples` | Principles personally understood by the scholar, checked by crafting rules. |
| `archivePrinciples` | Principles recorded for the household; distinct from personal understanding. |
| `wateringCharmInstalled` | Whether an owned charm is installed in the restored conservatory. |
| `founderAtCastle` | Derived: `expedition` is `null`. Inspection is allowed while away; in-person work and conversation are not. |
| `gardenYield` | Derived from selected output and installed artifacts: 1 or 2 ivy; 4 base crowns + 2 for a watering charm + 2 for a pantry seal, per staffed surplus phase. |

`founderAssignment` additionally supports `expedition`, set only by the expedition rules. You cannot assign the scholar back to castle work until arrival. Mira can keep working under her existing assignment; neither character receives a second work contribution.

Advance stops at an unresolved `awaiting-choice` stage until you select an approach or turn homeward. Other stages progress only when Advance is pressed. A ready-to-return expedition can wait indefinitely; it never auto-departs or expires.

Research completed by Mira during the scholar's absence enters the shared archive first. The scholar reviews these elementary hearth findings on arrival; this is a provisional sample debrief, not a completed individual mastery/training system. Survey knowledge enters both the scholar's known principles and the archive upon return.

During Advance, resident/castle work (including learning and personal projects) resolves, expedition progress resolves, the living-wing milestone is checked, Resonance resolves, and the day phase changes. Reports date their events to the phase being resolved. Return rewards and lead completion are committed in the same transaction as the rest of that phase, with the existing retry protections.


## Living-wing variables (schema 4)

| Variable | Meaning and units |
|---|---|
| `facilityProjects` | Records keyed by `kitchen`, `washroom`, and `service-wards`. Each stores a named `status` and a whole `completedWorkPhases` count. |
| `facilityProjects[id].status` | `not-started`, `in-progress`, or `complete`. Funding changes status immediately; work only happens on Advance. |
| `facilityProjects[id].completedWorkPhases` | Scholar work contributions to that facility, 0–2 in this sample. Paused projects retain this count. |
| `activeFacilityId` | The facility selected for the scholar’s next living-wing work, or `null`. Work also requires `founderAssignment == facilities`; this pointer alone does not resolve anything. |
| `householdArtifactPlacements` | Boolean installed flags for `hearth-kettle` (washroom) and `pantry-seal` (kitchen). Each requires a completed destination and an owned artifact. Placement does not consume it; one bonus per kind. |
| `livingWingCompletedOn` | `null` until the first qualifying Advance; then the resolved phase’s `dayNumber` and `phase`. A persistent achievement, even if an artifact is later removed. |
| `livingWingCelebration` | `unavailable`, then `available` when the milestone is recorded, then `completed` when enjoyed. Never expires; does not award funds, points or work. |
| `waystationDiscoveries` | Named leads (`survey`, `salvage`) brought home from Reedbank. Independent from `waterworksDiscoveries`; each can reward once. |
| `facilityCatalog` | Read-only definitions: plain-language purpose and benefit, `costCrowns`, `requiredWorkPhases`, and optional `requiredPrinciple`. |
| `livingWingRequirements` | Derived checklist of current functional requirements. Historical milestone and current placement are deliberately separate. |
| `householdNextSteps` | Derived suggestions with readable title, explanation and destination view. No hidden quest state or deadline. |
| `principleGuide` | Read-only knowledge sources and practical uses, shared by the archive and crafting prerequisite messages. |
| `expeditionSites` | Read-only destination catalogue with descriptions and approach/reward explanations. |
| `siteAccess` | Derived map of whether each site is reachable. Reedbank requires the returned waterworks survey. |
| `siteDiscoveries` | Derived per-site view of the two canonical discovery lists. Never written separately. |

`commissions` means the scholar copies and mends local records: **4 shared crowns per assigned Advance**, with no materials or prerequisite. Assignment itself awards nothing. It replaces the scholar’s other work and cannot be performed while away. Mira’s separate assignment still resolves normally.

Facility work uses the same scholar contribution as research, restoration, crafting or an expedition. Starting or resuming a facility changes the assignment; finishing returns it to `rest`. Another unfinished facility never silently starts. Funding is one-time and cannot be refunded; progress is retained indefinitely.

The kitchen and wards are functional when restoration completes. The warm-washroom requirement additionally needs an installed hearth kettle. Installing the kettle does not itself record the milestone; the next Advance checks all five requirements after work resolves. Celebration is separate, optional and free. It is ordinary companionship, so it grants no erotic Resonance.

Frontend `selectedExpeditionSiteId` is the destination being inspected before departure. An active expedition’s saved `siteId` always determines its rules and displayed destination. Browsing a map cannot relocate a character or change an expedition.


## Character development (schema 5)

| Variable | Meaning and units |
|---|---|
| `characterDevelopment` | Canonical development records keyed by `founder` and `mira`. The same point, training and preparation rules apply to both. |
| `characterDevelopment[id].advancementAwards` | One-time source IDs mapped to `{points, reason}`. The durable earned-point ledger; unrelated to crowns or game time. |
| `characterDevelopment[id].learnedPractices` | Personally learned practice IDs. Mira’s `archive-focus` is starting expertise; later learned practices each invest 2 points. |
| `characterDevelopment[id].preparedPractices` | Up to two learned practices currently ready for use. Freely changed at home, independently from learning. |
| `trainingProjects[id]` | `null`, or `{kind, targetId, completedWorkPhases, requiredWorkPhases}` for that character. |
| `trainingProjects[id].kind` | `practice` reserves 2 advancement and needs 2 phases; `principle` uses shared notes and needs 2 phases with no point cost; `retraining` takes 1 phase. |
| `residentKnownPrinciples` | Mira’s personally understood principles. The scholar retains `founderKnownPrinciples`; both character sheets derive knowledge from their respective canonical list. |
| `hearthResearchContributors` | Records new-version Mira participation in the hearth study, used to award her contribution once. Older unknown contributions are not invented. |
| `craftingProject.crafterId` | The selected maker (`founder` or `mira`), fixed when components are committed. Only that character’s assignment and preparation progress the artifact. |
| `miraArchiveProject` | The resident ambition’s `status`, completed/required work contributions and participant IDs. |
| `miraArchiveProject.status` | `not-started`, `in-progress`, `ready-to-bind`, `complete`. Completion additionally requires the installed charm and the optional concluding conversation. |
| `libraryIndexInstalled` | Whether an owned index charm is installed in the Library. Adds 1 contribution per assigned researcher and 1 crown per scholar copying phase; never stacks with another copy. |
| `expedition.companionId` | `mira` when she accepted this trip, otherwise `null`. Fixed before departure. Existing older trips migrate with no companion. |
| `binderyDiscoveries` | Returned `survey` and/or `salvage` leads from Hillfold bindery. Each rewards once, like other sites. |
| `materialInventory.moon-glass` | Whole pieces owned. Each can fill a `vessel` or `heat-bearing` requirement; filling both slots consumes two pieces. |

### Derived character values

| Value | Meaning |
|---|---|
| `characterSheets[id].earnedAdvancement` | Sum of unique award amounts. |
| `characterSheets[id].investedAdvancement` | 2 × learned practices excluding that character’s starting expertise. |
| `characterSheets[id].reservedAdvancement` | 2 during an unfinished practice-learning project, otherwise 0. |
| `characterSheets[id].availableAdvancement` | Earned − invested − reserved. Cannot be spent twice. |
| `characterSheets[id].offeredPractices` | All three for the scholar. Mira initially welcomes scholarship/artifice; completed archive story adds fieldcraft. |
| `characterSheets[id].atCastle` | Whether this person is physically home. Training/preparation planning requires presence, as does agreeing a new maker or personal development. |
| `residentAtCastle` | False while Mira is the expedition companion. In that case `residentRoomId` is `null`, so no home portrait marker is shown. |
| `craftingWorkPerPhase` | Selected maker’s base 1 plus prepared assembly’s 1, capped at remaining work; zero if paused or absent. |
| `archiveProjectWorkPerPhase` | Sum of present assigned contributors, capped at remaining study work. Base 1 each, +1 prepared scholarship, +1 installed index. |
| `copyingIncomePerPhase` | 4 base + 1 when the scholar prepares scholarship + 1 for an installed index + 2 for an installed scribe stone. This is income potential; only an assigned copying phase pays it. |

A work contribution is distinct from a calendar phase. Prepared practices can resolve two contributions in one assigned phase, but cannot create a second primary job. Learning always takes its stated number of phases; work bonuses do not accelerate it, prepare the result automatically, or grant another task on completion.

Founders gain 1 point for documented hearth understanding; Mira gains 1 for newly tracked hearth contribution. Each character earns 1 for their first creation of each recipe and 1 for each new lead returned as a party member. Establishing the living wing grants the scholar 2. Finishing Mira’s archive story grants Mira 3 and the scholar 1. These award sources remain recorded after retraining, so repetition cannot generate additional points.

The living-index study requires 4 contributions. Present contributors understand reference binding on completion; it is also deposited in the archive. Absent people and nonparticipants can study the notes later. Existing hearth-return review behavior remains the earlier limited introductory debrief; it does not extend to the new principle.

Expedition departure sets both participating characters’ primary assignments to `expedition`. Their paused projects retain progress. No at-home production, crafting or training resolves from Mira while she travels. Return sets each traveler to `rest`; there is no silent reassignment to old work. Her preparation cannot be changed remotely. In-person castle conversation waits for return.

Frontend `selectedCharacterId` controls the inspected sheet and `selectedMakerId` the proposed workshop maker. Neither changes authoritative character identity or an active artifact’s stored maker. Submitted hidden form fields identify the recipe and maker together.


## Research and household planning (schema 6)

| Variable | Meaning and units |
|---|---|
| `researchProjects` | Per-study records for `root-rhythms`, `luminous-impressions` and `shared-lessons`. The original hearth study retains its original fields for save compatibility. |
| `researchProjects[id].status` | `not-started`, `in-progress`, or `complete`. Funded projects retain progress when another becomes the focus. |
| `researchProjects[id].completedWorkPhases` | Total resolved character work contributions. Preparation/index bonuses can provide more than one contribution in a calendar phase. Capped at the study’s required work. |
| `researchProjects[id].contributors` | Character IDs that actually supplied positive work before completion. Their one-time advancement is credited even if they later leave; personal understanding additionally requires presence at completion. |
| `activeResearchId` | The one currently selected further study, or `null`. Researchers assigned to `research`/`archive` follow that focus. No further study can start before introductory hearth research is complete. |
| `utilityArtifactPlacements` | Installed flags for `root-tender`, `scribe-stone`, and `lesson-tablet`. Ownership and a restored destination are required; changing placement requires the scholar at home. |
| `materialReserveTargets` | Non-negative whole targets, 0–999, keyed by material ID. Protects inventory from individual sales; is neither an earmarked stock transfer nor a ban on using material for an explicit crafting project. |
| `workOrders` | Persistent plans containing `id`, `recipeId`, `crafterId`, `materials`, `requestedCount` and `completedCount`. At most 12 plans; 1–20 copies per plan. |
| `nextWorkOrderNumber` | Monotonically increasing integer used to give each plan a readable, unique `order-N` ID. Deleted plans do not recycle identifiers. |
| `craftingProject.workOrderId` | Optional link to the order whose current copy is being made. Direct workshop projects omit it. Cannot detach/delete the plan while its copy is in progress. |

### Derived planning values

| Value | Meaning |
|---|---|
| `researchCatalog` | Read-only study costs in crowns, work requirements, prerequisite principles, result and benefit. |
| `researchReadiness[study][character]` | Plain-language reasons that prevent choosing this character to fund/focus the study. The lead needs personal prerequisite knowledge. |
| `hasActiveResearch` | True for the original hearth study in progress or a selected further study. Used to enable research assignment controls. |
| `gardenForecast` | Actual upcoming harvest: `output`, whole `amount`, `staffed`, `automated`, and the ivy `reserveTarget`. Zero amount means no productive gardener/helper is available. |
| `gardenYield` | Retained compatibility field: potential quantity if the selected garden output were staffed. New interface forecasts use `gardenForecast` for actual staffing. |
| `principleStudyPhases` | Duration for a newly begun personal principle study: 2 normally, 1 with the lesson tablet. Stored durations of existing learning projects do not change. |
| `workOrderViews` | Derived plans with `missingMaterials`, `purchaseCostCrowns`, `underway`, `complete`, and readable `blockers`. Shortages are for the next copy only. |

A saved work order does not spend money, reserve actual components, assign a maker, or start production. “Buy missing” purchases exactly its next copy’s shortage at current catalogue prices in one atomic action. Duplicate component IDs count as multiple required items. Starting a copy reuses normal crafting validation and commits materials once. On completion, the linked count increases once; the maker becomes unassigned, and another copy waits for a new instruction. Retries cannot repeat purchases or completion rewards. Planned purchases and direct crafting may use shared stock protected from *sales* by a reserve.

For stock-first production, compare current silver-ivy inventory with its reserve target at the beginning of Advance. Below target, resolve a whole ivy harvest; at/above target, resolve a designated sale harvest. Never subtract existing ivy to make a sale. A staffed garden uses its normal watering/pantry bonuses. Otherwise an installed root tender yields 1 ivy or 2 crowns. No helper/staff means zero; staff and automation never produce two harvests together.

Further research is resolved before ordinary construction/crafting, using only characters assigned to its shared focus. Actual capped contributions determine the participant list. On completion, each participant earns one point under a stable `research:<id>` award source. Present participants learn the new principle, and the archive always receives it. Absent participants study it later; return does not silently grant these new findings. Completion clears the focus and releases assigned researchers to their own routines. Paused studies never auto-resume.

The lesson tablet affects only the required duration captured when a new *principle* study starts. Practice training still takes two phases; retraining still takes one. The scribe stone adds 2 crowns to an explicitly assigned scholar copying phase, up to 8 with both earlier bonuses. It does not pay for being installed or idle.

The frontend `workOrderDraft` retains the proposed recipe, maker, quantity and component choices while editing the plan. Only submitting the form creates an authoritative saved work order. Public readiness and shortage values are explanations, not substitutes for server validation.


## Schema 7 — neighbour requests and nursery discovery

| Field | Human meaning and units |
|---|---|
| `neighbourRequestProgress[requestId].status` | `offered`, `accepted` or `delivered`. Availability is derived from the named prerequisite; acceptance does not reserve or spend goods. |
| `neighbourRequestProgress[requestId].deliveredOn` | Null until delivery, then the in-game `dayNumber` and named `phase`. Delivery itself does not advance time. |
| `nurseryDiscoveries` | Nursery leads brought home: `survey` and/or `salvage`. No credit for unfinished or unreturned work. |
| `completedHouseholdScenes` | Stable IDs of the two one-time optional authored conversations already joined. No numeric affection score or resource reward. |
| `utilityArtifactPlacements.capillary-mat` | Whether one owned mat is installed in the Conservatory. Adds one item to staffed silver-ivy harvests only. |
| `craftedArtifacts[recipeId]` | Current owned artifact count, including installed/displayed/packed copies. Delivery subtracts spare copies; this is not a lifetime production total. Existing `workOrders[].completedCount` remains a historical count of copies made for that plan, even after delivery. |

### Derived delivery and invitation values

`neighbourRequestCatalog` contains authored names, source descriptions, prerequisites, artifact/material quantities, crown/material rewards and letters. All amounts are explicit whole counts. `neighbourRequests` adds current availability, delivery date, exact spare/unreserved quantities and human-readable blockers. Letters are displayed after successful delivery.

`spareArtifacts` subtracts one per installation/display and any packed lantern from current ownership, bounded below by zero. Protected copies cannot be delivered; the player may explicitly remove an installation first. Material availability is inventory minus its reserve target, bounded below by zero. Unlike explicit crafting, delivery may not consume a material reserve. All checks finish before any inventory or reward change.

`householdInvitations` has named scene IDs, descriptions, `locked`/`available`/`completed` status and `canJoin`. Joining requires both characters at home and never consumes a phase, changes assignments or grants advancement/crowns/Resonance. Existing mutual flirtation selects a different line in the conservatory scene.

The capillary mat brings maximum staffed ivy output to 3 per Advance (1 base + 1 watering charm + 1 mat). Staffed sale yields remain unchanged. Root-tender output stays 1 ivy or 2 crowns. Whole stock-first harvests may exceed the reserve target by up to 2 ivy. No time passes during reads, reloads, migration or correspondence actions.


## Schema 8 — personal signature focuses

| Field | Meaning and units |
|---|---|
| `signatureFocuses[characterId].name` | Player-chosen label for the personal tool, 1–40 characters. No mechanical effect. |
| `signatureFocuses[characterId].capacity` | Prepared inscription slots per configuration: 1 initially, 2 after the capacity project. |
| `signatureFocuses[characterId].inscriptions` | Completed permanent inscription IDs. Known inscriptions are not automatically prepared. |
| `signatureFocuses[characterId].householdLoadout` | Unique prepared work inscription IDs, at most `capacity`. Bonuses apply only to the owner's named assignment. |
| `signatureFocuses[characterId].expeditionLoadout` | Prepared field inscription IDs, at most `capacity`. Currently the preservation case is the supported field inscription. |
| `focusProjects[characterId]` | Null or a committed project: `kind` (`inscription`/`capacity`), nullable `inscriptionId`, two component IDs in `materials`, `completedWorkPhases` and `requiredWorkPhases`. Cost is paid once on start. |
| `founderAssignment` / `residentAssignment` | Adds `inscribing`: one work phase per Advance at home for that person's active focus project. Switching away pauses progress. |
| `focusInscriptionCatalog` | Read-only names, personal principle requirements, component properties and exact benefits. |
| `focusViews[characterId]` | Saved tool plus active project, personal known principles and whether a home-only change is available. |

Scholarly thread adds 1 research/index contribution. Steady hand adds 1 artifact crafting contribution. Copying line adds 2 crowns to an assigned scholar copying phase. These can combine with the relevant learned practice and household utility. None accelerates focus work or personal study. A completed salvage lead with a prepared preservation case in the party deposits 1 extra binding thread on return, once per party, regardless of how many members prepared it. Early return and surveys do not qualify.

## Server campaign selection (outside campaign rules state)

`campaignId` is `default` for the original save or `c-` followed by 32 lowercase hexadecimal characters for another slot. It is an identifier, not a character or gameplay stat. `campaign-registry.sqlite3` records slot IDs and the immutable requested creation name for safe creation retries. The visible name comes from the slot's actual `campaignName`, which may be renamed.

The browser's `?campaign=` query is copied to state, action, upload, export, backup and uploaded-artwork requests. No process-global selected campaign exists. Revision checks and action request IDs are local to each slot. A campaign slot is not an authentication boundary. All slots in this private prototype are visible to clients authorized to reach the server.

`GET /api/backup` returns a SQLite snapshot plus only the uploaded files referenced by that snapshot's accepted artwork and rollback history. A missing referenced file rejects the complete backup rather than silently producing an incomplete archive. This endpoint changes no campaign state; restore is an explicit server-stopped file operation described inside the ZIP.


## v0.9 — optional dialogue service (state schema remains 8)

`provider-settings.json` lives at the server data root, outside every campaign. Fields: `enabled` (boolean), `model` (exact OpenRouter identifier), `maxOutputTokens` (100–1500 integer, default 500), and `apiKey` (server-only secret). Public settings expose only the first three and `hasApiKey`. Blank key input retains the stored key; `removeApiKey` removes it and disables generation. Settings changes spend no game resources and make no provider request.

Each campaign database adds `dialogue_drafts(id, payload, result)`. The stable 32-hex-character ID names one provider attempt; `payload` holds user text and the requested revision. The result contains `status` (`processing`, `ready`, `failed`, `accepted`), `userText`, `baseRevision`, `model`, generated `text`, reported token `usage` and a safe error when applicable. Drafts contain no provider credential. Recent-draft recovery reads the latest eight records.

Acceptance requires a ready draft and an unchanged base revision. It appends You/Mira lines, marks the generated line with `source: generated` and its model, increments revision once and marks the draft accepted in one SQLite transaction. It never calls the provider, changes time or applies model-authored game actions. Retrying accepted drafts returns the current saved state without appending again. A crashed in-flight request is not automatically resubmitted; manual fresh generation has a distinct ID.

A single-campaign save ZIP includes the draft journal but not root provider settings. Whole-server backups include settings and must be protected accordingly. Model context is explicitly assembled from scene-visible fields, not a serialized full campaign.


## Housing (schema 9)

| Variable | Human meaning and units |
|---|---|
| `housingRooms[roomId].status` | `not-started`, `in-progress` or `complete`; only complete rooms supply usable beds. |
| `completedWorkPhases` | Number of assigned restoration phases completed for this room; one per explicit Advance at home. |
| `reservedBeds` | Whole vacant beds held for future planning, from zero to capacity minus occupants. No resident is created. |
| `bedroomAssignments[characterId]` | Room containing this person's bed. Initially both people have separate beds in `bedchamber`. |
| `activeHousingRoomId` | Funded unfinished room selected for restoration, or null. Other funded rooms remain paused. |
| `founderAssignment: housing` | The scholar spends the next phase restoring the selected accommodation while at home. |
| `housingCatalog` | Read-only room descriptions, total bed capacity, crown cost and required work phases. |
| `housingSummary.usableBeds` | Total beds in completed accommodation. Starts at 2; reaches 5 after both projects. |
| `housingSummary.occupiedBeds` | Beds assigned to existing household members; currently 2. |
| `housingSummary.reservedBeds` | Vacant beds protected by explicit reservations. |
| `housingSummary.availableBeds` | Usable minus occupied minus reserved beds. |
| `housingSummary.rooms[roomId]` | Room progress, occupant character IDs, usable and available bed counts. |
| `residentCount` / `founderCount` | Household counts in the summary; currently one resident and one founder. |

West chamber: 16 crowns, 2 work phases, 1 bed. Garden chamber: 24 crowns, 3 work phases, 2 beds. Both require the completed living-wing milestone. Funding pays once and selects the work assignment. Resume selects a funded unfinished project without another payment. Completion never moves people automatically. Bedroom and reservation changes take no time; they require the scholar at home, and bedroom choices also require the person at home. Mira's room-choice responses are authored offered choices. Housing does not alter intimacy, Resonance or recruitment state.


## Spellcraft (schema 10)

| Variable | Human meaning and units |
|---|---|
| `spellbook` | Saved designs, individually owned. One design per supported form per person. |
| `nextSpellNumber` | Next unique numeric suffix for a local `spell-N` identifier. Discarding a draft never recycles an ID. |
| `spellbook[].ownerId` / `formId` | Person who must understand and test it, and the supported rule form that fixes its effect. |
| `name` / `intent` | Descriptive text: at most 60 / 500 characters. Neither field grants powers; both are escaped in HTML. |
| `materials` | Two planned material IDs in required-property order. Repeated IDs require multiple copies. |
| `status` | `draft` (no cost committed), `testing` (funded work), or `learned` (successfully tested). |
| `completedWorkPhases` | Assigned testing phases, from 0 to 2. One per explicit Advance at home; never production or advancement. |
| `castCount` | Number of resolved castings, not scheduled attempts. Cancellation does not increment it. |
| `preparedSpells[characterId]` | Distinct learned personal spell IDs; initially at most 2, or 3 after the ritual. |
| `spellWork[characterId]` | Null or one pending job: `kind` is `test` or `cast`, with a saved `spellId`. A cast also records `committedInputs` for exact cancellation refunds. |
| Assignment `spellwork` | Spend this person's next home phase on the saved job. Switching away pauses it. Completion sets the person to `rest`. |
| `spellRitual.status` | `not-started`, `in-progress`, or `complete`. The concordant lesson is funded once and has no recurring charge. |
| `spellRitual.contributions[characterId]` | 0–2 coordinated ritual phases contributed by this participant. Both must be home and assigned for either to progress. |
| Assignment `ritual` | Participate in the coordinated lesson; not simultaneous spell testing, crafting or research. |
| `spellPreparationCapacity` | Read-only count: 2 initially, 3 once the concordant lesson is complete. |
| `spellViews` | Saved designs plus human-readable test/cast blockers computed from current knowledge, room availability, preparation, resources and pending work. |
| `spellForms` / `spellRitualBlockers` | Read-only exact form rules and current ritual prerequisites. UI explanations do not replace server validation. |

Warm-twist: Steady hearth wards, heat-bearing + binding testing components, common room; cast 1 ivy into 2 thread. Root-song: Steady growth, botanical + binding testing components, conservatory; cast for 2 ivy. Luminous transcription: Luminous copying, vessel + heat-bearing testing components, library; cast for 6 crowns. Every test costs 4 crowns and two components once and takes two assigned phases. Every casting is one assigned phase; only warm-twist commits an input.

Concordant lesson: 18 crowns + vessel/binding/vessel/binding components. Both participants know Reference binding; at least one knows Clear instruction; living index installed. Two coordinated phases unlock a third preparation slot per participant without altering existing preparation. This authored offer does not imply consent to other personal changes.

## Fieldwork and skills (schema 11)

| Variable | Meaning / unit | Behavior |
|---|---|---|
| `characterSkills[person][skill]` | Extra trained expertise, in ranks | Scholarship, Artifice or Fieldcraft; 0–2. Rank zero is baseline competence. Each rank invests 2 advancement. |
| `trainingProjects[person]` with `kind: skill` | The next rank being learned | Two assigned phases. Reserved advancement is released on cancellation; other assignments pause progress. |
| `observatoryDiscoveries` | Fully completed and returned Rainward leads | Survey and salvage, each once. Partial work is not a discovery. |
| `observatoryProgress[lead].completedSteps` | Resolved encounter IDs | Saved across early return and revisit. |
| `pendingWork` | Chosen step/method and remaining work phases | Capability must still be present when resuming. Choosing another method restarts only that step. |
| `complication` | Recoverable current obstacle | Empty or `misaligned-rack`. Explicit recovery required. |
| `bonusMoonGlass` | Auxiliary lens reward held in the field | Granted only on a completed return, not when discovered. |
| `utilityArtifactPlacements.reading-prism` | Whether one prism is installed | +2 crowns to normal assigned scholar copying. Not spell income; does not stack. |

## Additional resident and household life (schema 12)

| Variable | Meaning / unit | Behavior |
|---|---|---|
| `additionalResidents.tamsin.status` | Introduction/arrival lifecycle | `unknown`, `contacted`, `arriving`, `resident`. |
| `assignment` | Tamsin’s agreed primary activity | Own routine, archive, crafting, training, inscribing, spellwork or personal project. Not garden/expedition. |
| `knownPrinciples` | Tamsin’s personally understood principles | Shared archive access does not automatically teach her or anyone else. |
| `discussedTopics` | Offered introduction topics already discussed | Work, home and plans; all required before invitation. No phase cost. |
| `conversation` | This resident’s own recent dialogue | Up to 60 lines. Separate from Mira’s legacy conversation field. |
| `pendingResidentArrival` | Named occupant and reserved room | Empty or one accepted arrival. Bed is held until the next Advance. |
| `housingSummary.rooms[room].arrivalReservedBeds` | Beds committed to accepted arrivals | Derived separately from general planned reservations; cannot be reassigned. |
| `personalProject` | Repair-notebook progress | Three assigned phases, 8 crowns and 2 thread committed once; completion grants Tamsin 2 advancement and Joined fibres. |
| `wardrobe.outerLayer` | Tamsin’s offered outer garment | `none` or `plum-shawl`; free and independent of Mira’s wardrobe. |
| `savedStyles` | Named copies of this resident’s styling | Up to 20; same name replaces its configuration. No abilities or relationship effects. |
| `completedScenes` | Tea and playful scene IDs remembered | Optional, no expiry; repeated actions grant no additional rewards. |
| `sharedFlirtation` | Explicitly established mutual flirtation | Only the offered authored scene sets this; generated text cannot. |
| `relationshipDescription` | Descriptive relationship context | No affection score and no implied permission for further intimacy. |
| `resonancePerPhase` | Castle response expected on Advance | With the plum settee, 1 per established voluntary flirtation (currently Mira/Tamsin); otherwise 0. |
| `spellPreparationCapacities[person]` | Derived personal prepared spell limit | 2 normally; 3 only for completed Concordant lesson participants. |
| `utilityArtifactPlacements.binding-press` | Installed library press | +1 artifact work contribution for the assigned maker, nonstacking. No effect on spell tests/focus work. |
| Draft `characterId` | NPC whose prose is being drafted | Mira or Tamsin. Legacy drafts without this field mean Mira; acceptance writes only to that person’s conversation. |

## Delegated work orders (schema 14)

| Variable | Meaning / unit | Behavior |
|---|---|---|
| `workOrders[].delegation` | The current bounded agreement for this order | Empty for manual orders. One open agreement at a time. Existing orders migrate empty. |
| `status` | Agreement lifecycle | `active`, `paused`, `complete`, `revoked`. Active also waits when blocked by assignment, absence, budget or workbench. |
| `allocatedCrowns` | Total money committed to this agreement | 0–1000 whole shared crowns, including explicit additions. Removed from available shared funds when reserved. |
| `remainingBudgetCrowns` | Held money still available for components | No automatic refill; separate from personal wallets and spendable shared funds. |
| `spentCrowns` | Actual component purchases under this agreement | Increases only on an Advance that can start the next copy. |
| `returnedCrowns` | Unspent money released to the treasury | Returned once on completion or revocation. |
| `delegationView.nextPurchaseCostCrowns` | Cost of missing unreserved components for one new copy | A quote, not the whole batch cost. Current reserve targets apply at phase resolution. |
| `delegationView.blockers` | Human-readable reasons the next copy cannot start | Personal principle, presence, primary assignment, budget, status, remaining count or occupied workbench. |

For the current agreement, allocated = remaining + spent + returned. Components already committed to an artifact are not refunded as money. Work continues only through explicit Advance and grants no extra primary actions. A completed copy waits until a later Advance before another starts. Revocation keeps the current artifact as manual work; it does not destroy materials or completed items.

## Shared and personal finance (schema 13)

| Variable | Meaning / unit | Behavior |
|---|---|---|
| `personalFunds[person]` | Discretionary whole crowns | Zero by default. Never used implicitly for shared costs. |
| `personalPossessions[person]` | Individually owned purchase IDs | Each offered item once; never sold by shared-material controls. |
| `householdAllowancePlan.dailyCrowns[person]` | Daily transfer in crowns | 0–10; at evening-to-morning Advance, after income. New arrivals start at zero. |
| `minimumTreasuryCrowns` | Shared funds retained after discretionary transfers | 0–1000, default 20. Does not block explicitly funded household projects. |
| `expeditionWealthPlan` | Future departure arrangement | `shared`, `quarter-personal`, `half-personal`. |
| `expedition.wealthPlan` | Arrangement saved on departure | Cash only. Whole personal shares are divided equally; the remainder stays shared. |
| `moneyJournal` | Up to 80 transfer records | Day, phase, reason, crowns, source and destination. |

Allowances transfer money, not create it. If the full payment crosses the floor, everyone’s payment is skipped for the day with no arrears. Personal purchases change only the owner’s wallet and possessions, never affection, skills or Resonance.

## Shared lessons and finite casting (schema 15)

| Variable | Meaning / unit | Behavior |
|---|---|---|
| Learning project `teacherId` | Person offering this lesson | Optional; absent for ordinary personal study. Teacher and learner must be distinct actual members. |
| Learning project `targetRank` | Exact added skill rank being taught | Teacher must retain at least this rank. Learner still reserves 2 advancement; ranks are not transferred away from teacher. |
| Assignment `teaching` | Primary work devoted to an agreed lesson | Set by lesson agreement/resumption, released on completion/cancellation if still teaching. Other work cannot resolve for this person simultaneously. |
| `lessonHistory` | Completed shared lessons | Up to 60 records, containing people, subject, day and phase. Not a relationship or teacher-XP score. |
| `lessonOffers[learner]` | Derived eligible teacher/subject combinations | Includes personal knowledge, offered learner skills, presence, existing commitments and advancement blockers. |
| `lessonReadiness[learner]` | Derived progress blockers | Both primary roles and presence required; skill teacher must still be qualified. |
| `castingPlans[person]` | One current or last finite spell agreement | Empty by default; includes `spellId`, `requestedCount`, `completedCount`, `status`. |
| Casting plan `requestedCount` | Number of agreed castings | Whole number 1–12; one per assigned phase, no offline resolution. |
| Casting plan `status` | Agreement lifecycle | `active`, `paused`, `complete`, `cancelled`. Active can wait on assignment, presence or supplies. |
| Casting job `fromPlan` | This committed casting belongs to the standing plan | Internal phase-resolution marker; successful output increments the plan exactly once. |
| `castingPlanViews[person]` | Derived spell name, exact effect and blockers | No duplicated balance or progress authority. |

Workroom notes derives its cards from existing canonical assignments and project records. Casting plans reserve no future stock or money; protected inputs are checked and committed at the start of each Advance. Existing artifact agreements have first claim, then casting plans in household order. Production from that phase is only available to plans on a later phase. Personal knowledge, preparation and restored-room requirements still apply.

## Personal requests and keepsakes (schema 16)

`personalRequests[requestId]` holds `status` (offered, deferred, accepted, in-progress, complete), `completedWorkPhases` (0–2), `fundingSource` (shared, personal, or null), and `noteRead` (boolean). The fixed request catalogue names its owner, crown cost, exact shared components, two-phase duration, keepsake and authored closing note. Funding validates the chosen wallet and unreserved components before committing anything. An unfinished cancellation restores the original funds/components and resets progress; completion cannot be refunded.

`residentKeepsakes[characterId]` is the list of completed request IDs owned by that character. `displayedKeepsakes[characterId]` is its displayed subset. Display follows the owner’s current bedroom; neither list is shared craft inventory. They grant no numerical benefit. No deadline, affection penalty or passive cost exists. Each work phase requires the owner home and assigned `personal-request`; other assignments pause progress.

A saved draft with `purpose: journal` contains `sourceResults`, a copy of the latest `lastPhaseSummary`. Legacy drafts without a purpose remain NPC dialogue. Journal draft context sends only these results and the bounded editorial brief. Acceptance appends a journal entry with `source: generated`, `model` and `sourceResults` at the acceptance day/phase; this timestamp records when the account was saved. It changes only journal and revision. Source results remain available for comparison; prose is never parsed into game actions. Draft request IDs, revision checks and persistence use the existing SQLite draft journal.

## Room decoration and arrangements (schema 17)

`roomFurnishings[roomId]` retains the existing main furnishing. `roomDecorations[roomId]` contains `floor` and `wall`, each holding a supported catalogue ID or `none`. The Conservatory offers a reed mat; other rooms offer faded violet or ink-blue textiles. Bedroom wall choices include a mending sampler; shared rooms offer a star chart. Fern studies are shared decorative options. All new choices are cosmetic with no numerical bonus.

`savedRoomArrangements[roomId][name]` holds `{furnishing, decorations}` as an independent snapshot. Names have 1–40 characters; each room holds at most six. Saving the same name replaces that snapshot. Loading validates all choices before updating the main furnishing and two decorative slots. Deletion only removes the snapshot. No phase passes, no materials change, and no artifact installation, artwork, bedroom assignment or keepsake state is captured.

`roomFurnishingViews[roomId]` is a derived list of `{name, effect}` for the interface, not persistent simulation state. It includes placed furniture, decorative slots, installed utilities and displayed resident keepsakes. The common-room settee reports the current conditional Resonance contribution. The illustration is atmospheric and does not redraw to match this list.

## Resident moments (schema 18)

`residentMoments[momentId]` stores `status` (`waiting`, `deferred`, `complete`) and `completedOn` (null, or completion day and phase). Availability is derived from actual household membership and a named progress requirement. New scenes require the scholar and all participants home. Deferred scenes require explicit restoration first; completion is one-time and grants no resources, advancement, Resonance or new romance flags. Completed records remain readable while away.

`residentMomentViews` exposes title, participants, invitation, current status, `unlocked`, `canJoin`, `waitingForReturn`, and completed scene lines. Unplayed lines are not sent in these views. `residentFriendships` is a derived descriptive record for Mira and Tamsin based on their shared scenes; it is not a numerical affinity score. Joining appends authored dialogue to participating residents only and records a journal note. Existing request revision/idempotency handling still applies.

The eleven authored definitions in `resident_moments.py` contain a readable title, participants, requirement, invitation and speaker/text lines. Optional NPC context includes titles of completed moments involving the current NPC, not private moments belonging to another resident. Scene text cannot run actions.

## Advanced practices, preparation sets and augmentation (schema 19)

`PRACTICES` now includes `comparative-study` and `measured-assembly`. Each defines a readable `requiredPractice`, `requiredSkill` and `requiredRank` (1). Training validates personal prerequisites before reserving the existing 2 advancement cost. Learned and prepared remain separate; the preparation capacity remains two practices. `practiceRequirementViews` reports readable prerequisite and blocker lists.

`workContributionViews[characterId][workKind]` lists named positive contributions and integer amounts. The authoritative `work_contribution` sums the same parts. Advanced study adds one research/archive work; advanced assembly adds one artifact work. Neither modifies copying income, training, spell work, focus inscription, augmentation or personal requests. The existing skill, basic practice, facility and prepared focus bonuses remain separate parts. Away characters contribute zero castle work. Crafting estimates use these totals.

`practicePreparationSets[characterId][name]` stores a snapshot of up to two prepared practice IDs. Each person may keep six names of 1–40 characters. Saving an existing name replaces it; deletion does not unprepare the current set. Loading requires both scholar and owner at home and all practices personally learned. `preparationSetViews` describes unavailable practices after retraining. Saved sets neither alter spell preparation nor focus configurations.

`personalAugmentations[characterId]` stores `active` and `project`. A project is null or `{kind, completedWorkPhases, requiredWorkPhases}` where `kind` is `receive` (2 phases) or `reverse` (1 phase). Receiving commits 10 shared crowns and one each of moon glass and binding thread above protected stock. Only the owner’s `augmentation` primary assignment at home progresses it. Completed receiving adds one personal spell slot; active blessings cannot stack with themselves. The scholar and owner must be home to plan, resume, cancel or agree reversal. A resident’s already agreed work may proceed while the scholar is away.

Reversal costs no material and waits while prepared spells exceed `base_spell_capacity`. The player puts spells aside explicitly; no spell is automatically unprepared. Cancelling unfinished receiving refunds the exact original cost once; cancelling reversal keeps the active blessing. `augmentationViews` lists eligibility, work blockers, current and base capacities. Retraining does not remove magical principles, this blessing or personal history. NPC context receives only its own active blessing description. No generation can activate one.

## Reviewed spell proposals (v0.20; campaign schema remains 19)

Draft journal records with `purpose: spell-proposal` have `ownerId`, `userText`, `baseRevision`, status, model and usage, plus a validated `proposal` and rules-built `ruleReview` when ready. The proposal contains exactly `formId` (supported ID or null), `name` (1–60 characters), `explanation` (1–500) and `limitations` (at most five strings, each 1–300). Unsupported fields, unknown forms or invalid structure fail closed. Generated explanation semantics are not certified; the visible exact effect is authoritative.

`ruleReview` is built from `SPELL_FORMS` and current saved facts: name, exact effect, required principle, personally-known flag, room name/availability, component properties, testing crowns/phases and whether the owner already designed that form. It does not accept mechanical values from model output. Context includes only the supported catalogue with the owner’s relevant personal knowledge and the submitted idea.

Draft identity includes purpose and owner as well as text and revision. Recovery supports `purpose=spell-proposal&owner=founder|mira|tamsin`, filtering before the eight-result limit. The existing accept endpoint rejects these records. The browser can copy a fresh reviewed suggestion into its unsaved manual form; existing `draft-spell` validation remains the only way to save that design. No state schema change, provider auto-call, background generation or new simulation authority is introduced.


## Persistent identities and arrivals (schema 20)

| Variable | Meaning |
| --- | --- |
| `people[personId]` | Campaign-owned adult identity: stable ID, name, role, ambition, age, ancestry, starting practices and accommodation preference. This is not household membership. |
| `identityRevision` | Revision of the established identity; starts at 1. No identity-editing action exists yet. |
| `identitySource` | `authored-sample` for the current cast. No generated candidate is implemented. |
| `accommodationPreference` | `private-room` requires a one-bed room; `separate-bed` allows a separate bed in a shared room. |
| `arrivalReservations[reservationId]` | Named hold containing person ID, room ID, origin type and ID, and exactly one reserved bed. Included in housing capacity independently of general planning reservations. |
| `pendingResidentArrival` | Compatibility pointer for Tamsin’s existing authored arrival. Reservation capacity comes from `arrivalReservations`. |
| `arrivalReservationViews` | Derived person/room labels and current blockers for Rooms & beds. |

`known_people` selects introduced people; `household_members` selects members; `present_household_members` excludes household members currently away. Unknown sample contacts remain stored but do not acquire membership through the registry. No currency, work assignment, romance, knowledge or passage of time is granted by migration or reservation cancellation.


## Authored summoning (schema 21)

| Variable | Human meaning |
| --- | --- |
| `summoningContacts[contactId]` | One paid preparation and the enduring introduction it produces. Contains conductor, exact committed costs, progress, status, person ID, disclosed topics and authored conversation. |
| `contactStatus` | `preparing`, `open`, `closed` or `cancelled` in this authored slice. Generation-only planning/recovery states are not needed yet. |
| `nextSummoningContactNumber` | Monotonic identifier counter; cancelled preparations are kept rather than overwriting history. |
| `residency[personId].residencyStatus` | `remote`, `arrival-agreed`, `visiting`, `resident`, `departure-agreed` or `away`. Presence is distinct from workforce membership. |
| `candidateStayDecision` | Authored candidate statement: `undecided` or `wants-to-stay` for Iona. No player-authored acceptance text changes this. |
| `householdStayDecision` | Player household decision: `undecided`, `invite-to-stay` or `do-not-invite`. Both positive decisions are needed for membership. |
| `agreedRoomId` | The bedroom reserved or occupied for this visit; cleared on departure or withdrawn arrival. |
| `arrivals`, `departures` | Saved phase records of actual crossings, resolved only by Advance. |
| `summoningView` | Derived preparation blockers, contact cards, eligible rooms, work status and departure blockers. |
| `presentPeople` | Public display catalogue for people physically present, including visitors without workforce sheets. |

`initialize_character_records` creates personal development, knowledge, wallet, possessions, focus, spell, preparation and augmentation records once when the identity is established. Starting practices are excluded from refundable advancement investment. Joining and returning do not reinitialize these records. All variables are local campaign data; no provider credentials or background timers are involved.


## Iona’s professional and personal life (schema 22)

| Variable | Human meaning |
| --- | --- |
| `additionalResidents.iona.personalProject` | Her optional crossing atlas: status, completed/required personal work phases, and the exact committed crown/material amounts while funded. |
| `committedCrowns`, `committedMaterials` | Original atlas payment, saved at funding and used for cancellation even if future catalogue prices change. |
| `ionaAtlasView` | Derived title, description, exact costs, funding blockers, progress and assignment readiness. |
| `personalRequests['iona-map-case']` | Independent personal comfort project, funded from the explicitly selected shared or personal wallet. |
| `residentKeepsakes.iona`, `displayedKeepsakes.iona` | Personal ownership and bedroom display choices; not shared artifact stock. |
| `residentMoments['iona-*']` | Five authored scene records. Waiting/deferred/completed history persists without expiry or replay rewards. |
| `personalPossessions[personId]` | Unique personal-interest items, acquired either by the owner’s purchase or an explicit household gift. |
| `moneyJournal` | Gift payments identify their source as the household and name the recipient and item. Their wallet is untouched. |

The atlas grants exactly 2 earned advancement to Iona once and her own understanding of Courteous passage. The map case, tea tin, portrait and scenes grant no advancement or Resonance. Gifts obey the same discretionary treasury floor as allocations. Membership is still required before agreeing Iona’s project or giving an offered household gift.

### Iona’s conversations (v0.25)
- `summoningView.personalTopics`: authored conversation choices, each with a readable label and reply; presentation data, not a stat or reward.
- `additionalResidents.iona.conversation`: Iona’s own saved personal conversation, retaining the most recent 60 lines. Separate from the contact’s introduction and membership decisions. Authored lines record `source: authored` and `topicId`; reviewed model lines record `source: generated` and the model identifier.
- `residency.iona.arrivals` / `departures`: persistent day and phase records used for the chronological visits display. Viewing them does not move time.
- Dialogue draft `characterId: iona`: scopes provider context, recovery and acceptance to Iona. A draft has no campaign effect until explicitly accepted against its original campaign revision.


### Authored candidate catalogue (v0.26)
- `summoningContacts[id].candidateId`: the particular person this paid contact is preparing to reach. Missing on older saves means Iona until a personId is present. Never rerolled when reopening.
- `summoningView.candidates`: readable profile previews, category names, starting principles and per-conductor preparation blockers.
- Contact `topics` and `personalTopics` in the public view come from that candidate’s authored definition; they are not skill gains or rewards.
- `selectedSummoningPerson`: browser-only contact selection, initially Iona. Does not mutate the campaign or advance time.
- `people[id].appearanceDescription`: authored appearance continuity supplied to optional dialogue drafts; cannot create mechanical powers.


### Companion life (v0.27)
- `additionalResidents[id].personalProject`: each companion’s own project status, completed and required phases. `committedCrowns` and `committedMaterials` capture the actual payment for exact cancellation refunds, even if catalogue costs later change.
- `wardrobe.ensembleId`: `working` or `evening`; selects an authored clothing list and actual local portrait. No stat, time or currency effect.
- `savedStyles`: up to eight records of readable name and ensembleId, owned by that person. Reusing a name updates its saved look.
- `companionLifeViews`: derived project blockers/progress and wardrobe choices for introduced Aurelia and Neris. It does not create identities or grant membership.
- Moment `illustrationId`: selected when an illustrated moment is joined, retained for replay independently of later clothing changes.
- `companionSection`: browser-only project/wardrobe/moments tab; never changes campaign time.


### Reviewed candidates (v0.28)
- `reviewedCandidates[personId]`: fixed approved contact definition. It is a plan until paid contact preparation finishes; it is not membership.
- Draft `purpose: candidate-proposal`: saved proposal, model, usage and rule review. `baseRevision` guards approval; `generationRevision` retains original request identity after recheck.
- `approvedCandidateId`: durable ID derived from the saved draft ID. Retrying approval cannot duplicate it.
- `capabilityPackageId`: one of three human-labelled starting packages; no arbitrary effect definitions.
- `stayPreference`: `open-to-staying` or `visit-only`. Visit-only yields `prefers-to-leave` when asked about membership and cannot be overridden by a household invitation.
- `textSource: reviewed-candidate`: provenance for the accepted candidate’s introductory prose.


## v0.29: individual builds and evidence

- `characterBuilds[personId].attributes`: Insight, Dexterity and Resolve ranks, starting at 1 and capped at 3. Added ranks cost 3 advancement each.
- `characterBuilds[personId].affinities`: Light, Growth and Hearth ranks, starting at 0 and capped at 2. Added ranks cost 2 advancement each.
- `characterBuilds[personId].perks`: individually earned perk IDs, each costing 3 advancement. No race/ancestry or prose-derived ranks.
- `trainingProjects[personId].kind`: additionally supports `attribute`, `affinity`, `perk`; the existing personal assignment and completed/required phase fields apply.
- `investedAdvancement` and `reservedAdvancement`: derived totals include build ranks/perks and current study commitments. Cancelling releases reservations; completing invests the same amount.
- `privateCastleLore`: campaign-owned versioned prototype foundation and undiscovered evidence; not returned in ordinary public state or diagnostic JSON. Complete backups preserve it.
- `castleMystery.project`: current founder investigation, lead ID and own phase progress; `null` when none.
- `castleMystery.discoveries`: discovered evidence only, with source version and discovery day/phase.
- `castleMystery.sharedWith[personId]`: IDs of evidence explicitly shared with that person. NPC prompts receive only those discovered records.
- `characterBuildViews`, `castleMysteryView` and spell `personalEffect`: derived public summaries and blockers, never authority to bypass the underlying rules.


## v0.30: specialized chambers and bounded estate

- `containment.chambers[chamberId].status`: sealed or ready; one compatible non-residential place per chamber. There are five heat and five echo chambers.
- `containment.cases[personId].status`: unmet, arrival-pending, contained, safe, release-pending, released, transfer-pending or transferred. Ordinary release and specialist transfer remain different outcomes.
- `containment.cases[personId].chamberId`: the reserved/occupied chamber, cleared only when departure resolves. No normal bedroom is implied.
- `containment.cases[personId].discussedTopics`, `conversation`, `history`: distinct account/plan discussions and persistent case continuity, without affection or obedience values.
- `containment.project`: one chamber or care project; target ID, own completed/required phases and exact committed crowns/materials for refund.
- Contact `contactOrigin: outside-encounter`: no summoning fee; normal contact controls require that person's case status to be released.
- `estateAnnex.status`: not-started, in-progress or complete. Its saved committed crowns are refunded only if unfinished work is cancelled.
- Housing catalogue `region`: main or annex; omitted legacy values mean main. Each region allows at most 25 non-founders, with a separate physical founder place in the solo main castle.
- Room `illustrationIsRepresentative`: reused interior concept artwork; actual beds/occupants/effects remain in authoritative text and independent room records.
- `housingRegionFilter`: local UI selection only, main or annex; changes neither time nor capacity.
- Reviewed candidate plan limit: 50. Contact plans, people, visitors, residents, residential beds and specialized occupants remain distinct counts.
