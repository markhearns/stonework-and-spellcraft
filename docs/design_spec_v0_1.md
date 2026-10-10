> Current direction, v0.116: solo play uses authored and scripted narrative; an LLM gamemaster is optional. See [SCRIPTED_SOLO_V116.md](SCRIPTED_SOLO_V116.md) and the v0.116 release notes. The dated implementation records below are historical. Eris/Selene co-op remains deferred.

# Castle Household RPG
## Consolidated design specification — v0.1

**Date:** 3 October 2026  
**Working title:** Castle Household RPG; no final game or castle name has been selected.  
**Basis:** The design conversation and the player's decisions through questions 1–92.  
**Purpose:** Preserve the agreed game identity, systems, and presentation as a reference for design and prototyping. This is a specification, not an implemented game.

### How to read this document

“Agreed” describes choices established in the conversation. Examples illustrate those choices without fixing names, quantities, or content that the player has not selected. Recommendations and unresolved implementation details are identified separately. In particular, numerical balance, exact character-sheet statistics, software choices, provider/model identifiers, and the castle's secret history are not invented here.

---

## 1. Core identity and priorities

An adult-cast, fanservice-forward, high-magic fantasy household RPG played through a self-hosted desktop-oriented webapp. A formerly dilapidated, mysterious castle becomes an increasingly comfortable headquarters and home. The campaign is open-ended: there is no requirement to finish a main story, fill every residential slot, or construct every possible expansion.

The central activities are castle restoration and management, staff development, deep character building, relationships and romance, magical research, rituals, artifact creation, and narrative expeditions. Adventuring brings knowledge, materials, wealth, and interesting people home. It supports household life rather than displacing it as the main attraction.

The emotional tone is warm, generous, and welcoming. Routine scarcity, jealousy, expiring obligations, repetitive maintenance, and unsolicited destruction of the home are not sources of engagement. Meaningful choices concern priorities, magical possibilities, personal ambitions, and shared undertakings.

Fanservice and ecchi presentation are a primary part of the game's identity, not a small reward gallery detached from otherwise unrelated gameplay. Character design, clothing, equipment, interiors, dialogue, romantic events, and side stories support that identity. The castle has an unexplained affinity for eroticism and intimacy, but does not override consent or autonomy. All romantic and fanservice subjects are unambiguously adults.

The core loop is: restore and personalize the estate; establish useful facilities; meet and recruit residents; develop abilities and relationships; undertake research, rituals, and expeditions; bring discoveries back to enrich the household.

**Decision basis:** Q1–15, Q17–28, Q39–56.

## 2. Campaign modes and founders

### Two separate campaign types

**Solo:** The human player's scholar arrives without Eris or Selene as fellow founders. Resident NPCs still have agency, form relationships, join expeditions, and participate in the same development systems. Solo mode does not use gamemaster-controlled imitations of the absent agents. A sole founder can approve founder-level decisions, without overriding residents' personal decisions.

**Co-op:** The human player, Eris, and Selene are an established group of adventurers and equal cofounders of one household. Eris and Selene are controlled by their actual external agents through dedicated game tools. They have their own ambitions, funds, equipment, relationships, and projects. They do not automatically agree with the human player.

The modes have separate saves. No joining a solo campaign, mode conversion, or retroactive insertion of founders is required. Solo opening tasks should be feasible for one inexperienced founder, rather than quietly assuming three characters' skills or action budgets. Exact mode-specific workload tuning remains open.

### Starting identities

| Founder | Established starting identity | Origin details |
|---|---|---|
| Human player's avatar | A 40-year-old human man; former scholar; inexperienced summoner/ritualist | Native to the fantasy world. The avatar's age is a fictional character specification. |
| Eris | Inexperienced occult scholar with a castellan/steward orientation | Chooses her own ancestry and compatible background. |
| Selene | Inexperienced artificer/explorer | Chooses her own ancestry and compatible background. |

The founders bring personal adventuring equipment and modest savings, not the resources or capabilities of established archmages. Character growth is a major part of play. Starting specialties provide strengths and identity, not exclusive classes: any magical discipline can be learned with sufficient investment.

In co-op, Eris and Selene are potential romantic partners only if they independently choose that relationship. They remain fellow players, not recruitable NPCs under the human player's control.

**Decision basis:** Q4–6, Q16, Q33, Q39, Q57, Q78–83.

## 3. The castle, estate, and opening milestone

### Setting and architecture

The castle begins as a dilapidated ancient structure, with perhaps one or two rooms sufficiently usable for initial accommodation. Its weathered, imposing architecture gradually gains warm, personalized interiors. The surrounding land is lush, slightly enchanted, and rich in history and stories.

The castle has otherworldly properties, but is not a speaking companion, conversational quest giver, or directly addressed personality. Its original purpose and abandonment have a hidden foundational explanation. Discoveries add to that explanation rather than continually replacing it.

The footprint and surrounding estate are bounded. Restoration and exploration reveal inaccessible sections. Customization primarily assigns purposes to existing rooms; the game is not a freeform wall-building or tile-based architectural editor.

Location matters at room scale. Distance, connections, and neighboring facilities can create practical synergies. A laboratory near a greenhouse is an illustrative synergy, not a demand that every campaign use one fixed layout. Synergies should be understandable through the interface rather than hidden placement traps.

### Progressive accommodation

| Category | Maximum | Capacity rule |
|---|---:|---|
| Main castle | Up to 25 residents, plus the participating founder or founders | Usable resident capacity is progressively unlocked through restoration and appropriate furnishing. Solo mode does not require absent founders to exist. |
| Optional annex | Up to 25 additional resident places | A later estate construction opportunity, not required progression. |
| Specialized dungeon/containment | Approximately 10 occupants at full development | Separate from residential slots; suitable usable chambers determine actual capacity. |
| Ordinary underground living spaces | Included in normal residential capacity | Underground location does not make a bedroom a confinement space. |

Fifty non-founder residents is an available long-term ceiling, not an intended minimum or equilibrium population. A smaller, deeply involved household remains fully viable. The annex may never be needed.

### First milestone: A Proper Living Wing

The milestone triggers at the end of a phase/turn once the required spaces and services are functional: safe sleeping accommodation, a proper washroom, a kitchen and dining area, a comfortable common room, and reliable basic magical services.

Separate personal suites and elaborate decorations are later improvements, not prerequisites. The starting shared accommodation is a practical arrangement, not an imposed romantic relationship. A celebration may follow the milestone, but no ceremony or extra dialogue interaction is required to trigger it.

The first recruit is selected by the gamemaster and connects to the castle mystery. Her exact identity and introductory circumstances remain undisclosed campaign content, not something this specification preselects.

### Sanctuary rule

Restored inhabited areas are a dependable sanctuary. The game does not maintain interest through surprise raids, recurring vandalism, stolen personal possessions, or arbitrary destruction of established living spaces. Uncertainty belongs in deliberately approached expeditions, sealed areas, and exceptional magical undertakings. Managed containment must not become a random source of danger to the living wing.

**Decision basis:** Q17–19, Q29–33, Q56, Q58–60, Q62–69.

## 4. Time, actions, and non-interrupting play

### Daily rhythm

Each day has **morning, afternoon, and evening** phases. Advancing the evening moves to the next morning; there is no separate manual sleep turn. Lighting, resident locations, and routine activities reflect the phase.

A phase is the working unit of a turn. Exact action-point quantities and task durations are not yet balanced. Work, research, construction, training, and expeditions use the shared phase framework and personal action budgets. Major activities can occupy multiple phases or days.

Conversation, intimate downtime, ordinary castle browsing, and decoration choices do not consume character action points. Selecting a furnishing variant is distinct from constructing an improvement: free interface interaction does not make materials, work, or functional upgrades free.

### Advancement gate

The world progresses only during active play. There is no offline catch-up, real-time production, or agent-driven advancement while the human player is away.

In solo play, the human player explicitly presses **Advance**. In co-op, advancement additionally requires both Eris and Selene to be ready. Their readiness means their relevant decisions for the phase are complete; it does not advance the phase by itself. They may act independently and in any order within the phase, but acting faster does not confer additional action budgets.

A proposed phase-resolution sequence is to validate committed choices and readiness, resolve rules-governed work and expedition progress, apply phase-based production and household effects, check milestones, and present resulting changes and available decisions. The exact processing order is an implementation detail that must be specified consistently.

Repeating an interface click, conversation, or image correction must not repeatedly grant production, advancement, or relationship rewards. Narrative regeneration must not resolve the same game action twice.

### Residents' initiative

Brief ambient greetings can occur when entering a room. Substantial conversations, shared activities, and personal developments appear as optional invitations. They do not unexpectedly open a long scene or interrupt decoration, another conversation, or an expedition decision.

Invitations and adventure leads have no expiry pressure. Residents outside the current spotlight continue routines and projects without requiring continual personal check-ins. Spending time with one person does not create an attention-decay punishment for everybody else.

**Decision basis:** Q6, Q22, Q28, Q43, Q55, Q68, Q91–92.

## 5. Shared governance and personal authority

The cofounders jointly own and manage the headquarters as equal partners. Major shared expenditures, changes affecting others' spaces, and commitments of collective resources require consensus.

Unapproved proposals are deferred, not forced through. The founders can bargain over scope, location, timing, funding, or prerequisites and pursue unrelated activities in the meantime. Objections should arise from actual goals and circumstances, not mandatory artificial disagreement.

Standing agreements and delegated budgets allow ordinary action without reopening the same conversation repeatedly. Acting within an agreed remit is different from committing additional shared resources or altering someone else's personal space. The precise thresholds and budgets are configurable game data, not fixed numbers in this document.

Readiness and agreement are separate. An agent can oppose one proposal and still be ready for the phase to advance. Conversely, lack of a response is not consent or readiness.

A recommended safeguard is that materially changing an approved proposal invalidates affected approvals. This avoids treating agreement to one cost or plan as a blank authorization for another.

**Implementation issue still open:** An agent connection failure cannot authorize proxy actions, waive readiness, or convert the campaign into solo mode. Recovery and reconnection controls must preserve this rule. Deferring a disputed project solves social deadlock; it does not define what the application should do when an agent is technically unavailable.

**Decision basis:** Q4–6, Q23, Q55, Q73, Q79, Q83.

## 6. Deep character development

### Shared rules, differentiated builds

Founders and residents use the same advancement system. Development is classless, with structured specialization paths and substantial customization. The character sheet includes attributes, skills, perks, magical affinities, known magical principles, equipment, and prepared abilities. The exact attribute names, point scales, and perk catalogue remain to be designed; referencing Dungeons & Dragons as an inspiration does not commit the project to its precise rules.

Attributes express underlying capabilities; skills express trained competence; affinities influence magical strengths; principles describe understood effects; perks provide distinctive capabilities and combinations. Specializations are earned through investment rather than imposed as exclusive starting classes.

Knowing an ability, preparing it, and using it on an assignment are separate layers. Broad long-term learning can coexist with meaningful loadout choices before an expedition. Exact preparation capacities remain open.

### Advancement

Meaningful accomplishments award advancement that can be invested deliberately. Research, exploration, completed projects, personal quests, and other substantial contributions can matter. Training supports entry into new disciplines. Routine repetition is not the intended leveling strategy.

Residents may have uneven expertise rather than automatically matching founder levels. An early recruit can be highly competent in one useful field while inexperienced elsewhere. She can teach principles and skills she knows without making every character instantly equally proficient.

Resident development is collaborative. Founders can inspect mechanical character sheets and propose training directions, perks, and builds. Residents' interests and ambitions influence their choices. Neither total puppeteering nor entirely opaque automatic builds is the intended default.

### Preparation and retraining

Build changes occur only at the castle. Switching available prepared abilities and equipment is straightforward. Reallocating substantial earned investments requires a simple, non-grindy retraining process or ritual. Acquired knowledge and completed personal histories are not erased by respecialization.

A remote management view does not imply that a character on an expedition can perform castle-only build changes.

### Personal growth and augmentation

Mechanical disadvantages associated with resident characters can be resolved through their personal quests. Resolving a disadvantage should not erase the underlying personality. A proud character can improve her cooperation while remaining proud.

Magical blessings and augmentation may develop skills, affinities, talents, forms, and visible supernatural features. Such transformations are reversible through another ritual rather than being permanently irreversible or simply free toggles. They are voluntary character developments, not imposed changes of loyalty or preference.

**Decision basis:** Q9, Q16, Q21, Q33, Q39–45, Q49–51, Q64, Q70.

## 7. Research, rituals, crafting, and summons

### Component-governed invention

Players can propose magical effects in natural language. The game maps proposals onto understood principles and rule-governed components. Discovery of reusable principles is the main research driver, supported by proficiency, appropriate facilities, catalysts, and specialists.

The generative model may propose a construction or explain missing requirements; it does not grant an arbitrary effect just because it was described persuasively. Unknown principles cannot be bypassed by renaming the same desired result. Costs, prerequisites, and outcomes belong to the rules system.

Ordinary magic should be readily useful. Resource management mainly constrains exceptional feats and substantial rituals, rather than making common casting a constant mana-management chore. This does not abolish phase budgets or task duration: using magic to undertake meaningful work still follows the activity rules.

### Shared research, individual mastery

Research deposited in the collective archive becomes available to the household. Eris and Selene contribute their discoveries as part of the standing arrangement. Availability of a documented principle is distinct from any particular character's ability to use it.

Characters require relevant personal competence and preparation. Specialists can teach; the archive preserves shared knowledge. Private conversations and personal experiences are not automatically uploaded merely because magical findings are shared.

### Property-based materials

Routine supplies are broadly abstracted. Magical ingredients can retain names and properties such as affinities, binding qualities, or suitability as vessels. A requirement may accept multiple materials with the right properties; particularly appropriate components may improve or expand a supported result. Rare discoveries can have unique properties.

This is a flexible-substitution system, not a mandatory search for one precisely named ingredient for every ordinary effect. Exact property vocabularies and substitution rules remain open.

### Artifacts and equipment

Equipment emphasizes upgradable signature items plus occasional meaningful alternatives. A cherished staff or focus can develop through added inscriptions, changed components, or unlocked functions rather than being replaced solely by a larger number.

Artifact creation uses the same broad principle-based logic as magic: suitable vessels, understood effects, and capacity limits. New discoveries can therefore expand both spell invention and equipment customization.

### Persistent summoned people

Summons in the resident-recruitment system are persistent adult characters, with backgrounds, abilities, preferences, and ongoing development. They are not disposable spell effects, temporary obedient workers, or beings who disappear when the summoner's mana runs out.

General rituals contact categories of prospective residents; exceptional discoveries may identify a particular individual. The summoner communicates with the candidate before bringing her to the castle and can learn who she is and what abilities she has. The candidate's identity and capabilities should be coherently established before the conversation, rather than adapt to grant every requested trait.

Arrival, willingness to remain, and acceptance into the household are distinct. Familiar fantasy peoples and humans are more commonly met through ordinary recruitment; exotic residents primarily become accessible through rituals, with rare opportunities on unusual expeditions.

**Decision basis:** Q14, Q19–21, Q34–35, Q42, Q51–54, Q64, Q71, Q76.

## 8. Residents, relationships, and everyday life

Residents are generated by the gamemaster but have coherent, persistent identities: background, skills, interests, ambitions, opinions, loyalties, relationships, and evolving personal history. A generated character is not merely a random portrait with interchangeable statistics.

A broad range of adult personalities is welcome, excluding cruel, sadistic, or evil household members. Distinctive traits can create preferences and occasional practical differences without producing the hostile drama the player does not want.

Relationships are easy to begin. Deeper progression comes from understanding a person's history, supporting her aspirations, completing meaningful undertakings, and building a shared life. Consensual multiple relationships are normal in the setting. The game is primarily player-centered in its harem structure, while NPCs can develop their own friendships and romantic connections.

Relationship information is descriptive rather than a displayed affection score. Private simulation variables may be needed internally, but the interface should communicate through meaningful states, dialogue, and behavior. Increasing closeness supports comfort and openness without flattening distinct personalities.

Personal stories include ambitions and future projects as well as difficulties that need resolving. Finishing one quest does not exhaust a character's development. Mechanical disadvantages can be addressed through personal quests, while subsequent life and aspirations continue.

Each character generally has one primary assignment, a secondary training interest, and autonomous downtime. Founders use the same basic structure, with free social and cosmetic activities outside their work budgets. Exact assignment durations and scheduling rules remain open.

Residents own possessions, receive discretionary funds, pursue personal interests, choose clothing, and decorate their assigned rooms using the same supported options available to the player. Shared belongings and private property remain distinct.

The interface surfaces a small, relevant selection of household opportunities rather than demanding that the entire possible roster be visited every phase. Any resident remains accessible even when not in the current spotlight. The larger capacity permits collection-oriented play without making maximum occupancy a requirement.

**Decision basis:** Q8–12, Q24–26, Q34, Q43–46, Q59, Q64, Q68, Q70, Q75, Q89–92.

## 9. Economy, production, and staffing

Castle upgrades can generate several kinds of passive benefits: useful materials, everyday supplies, and income. Productive capacity can be allocated among outputs. A garden dividing effort among food, ritual ingredients, and sales is the established example.

Allocation plans persist until changed. Updating priorities is free planning, while production occurs through phase resolution. Upgrades, staffing, skills, and room synergies can affect facility performance. Exact formulas, allocation granularity, and whether every facility uses identical controls remain open.

A recommended interface refinement is reserve targets: retain supplies for agreed plans and sell designated surplus. This complements ratios without forcing repeated manual adjustments. Forecasts should show expected outputs before a player commits to a new allocation.

Major improvements require discoveries, specialists, meaningful projects, or unusual materials rather than repetitive grinding. Ordinary life becomes increasingly self-sustaining. The game should not require a unique employee for every room; related facilities and ordinary enchanted upkeep can prevent staffing from becoming a population-filling chore. Exact automation upgrades remain content to design.

### Shared and personal finances

Productive castle facilities fund the shared treasury. An agreed share of expedition wealth supports the household, with the remainder distributed to participants under a standing arrangement. Founders receive discretionary allowances so that sustained research and household work are not financially penalized compared with adventuring.

The household provides residents' necessities and required work equipment. Residents have personal spending money for interests, clothing, possessions, and room decoration. They can raise requests for exceptional purchases or personal projects rather than silently spend beyond their authority.

Ordinary expedition treasure converts to wealth automatically. Significant artifacts, unusual components, and research discoveries remain individual objects worth inspecting. Automatic sale must not consume personal possessions, gifts, reserved materials, or unexplored special objects.

The precise wealth unit, income rates, shares, allowances, and budgeting thresholds are balancing decisions, not settled numbers.

**Decision basis:** Q7, Q18–19, Q23–24, Q54, Q72–76.

## 10. Exploration, encounters, and outside connections

Exploration combines a persistent illustrated regional map with a journal connecting locations and leads to research, rare resources, recruitment, and personal projects. Named places remain consistent across visits. Discoveries can reveal new sites or previously unknown possibilities within familiar ones.

The founders can each lead separate parties. Expeditions can span multiple in-game days. A leader chooses the party's approaches; the gamemaster does not replace that player's meaningful decisions. Routine continuation can eventually use explicit standing instructions, but any such automation must preserve player control over new consequential choices.

Routine obstacles generally use one decision. Significant encounters unfold through multiple exchanges where party composition, skills, preparations, artifacts, and magical approaches matter.

The outcome philosophy is **guaranteed competence with uncertainty at the margins**. Clearly sufficient capability reliably handles an ordinary challenge. Unfamiliar situations or improvised approaches can introduce uncertainty. The interface describes suitability and risk rather than foregrounding exact percentages or thresholds.

Setbacks usually mean a complication, an alternative route, a recoverable injury, delay, or returning without the main prize. Losing a beloved character or destroying the home is not the intended routine consequence of an unsuccessful encounter.

Outside diplomacy remains limited to a relatively private household's circle of contacts. Its purpose is access to knowledge, specialists, rare resources, and useful agreements—not compulsory regional rule or conquest. Leads and obligations should not create expiry pressure.

### Viewing events versus participating in them

The human player can inspect household information while the avatar is away. In-character remote participation requires a plausible magical communication link. Such a link does not grant physical presence or permit all castle-only activities from an expedition.

The human player normally sees short summaries of Eris and Selene's independent activity. More detail is learned when the agents choose to share. Private conversations and discoveries must not leak through a supposedly omniscient activity log.

**Decision basis:** Q2–3, Q27–28, Q36–38, Q47, Q53, Q55, Q77.

## 11. Dungeon occupants and recruitment transitions

The managed dungeon is a small specialized containment area, ultimately around ten occupants, not the entire underground castle. Appropriate chambers support different kinds of magical or practical confinement. Ordinary underground residences are separate spaces using normal housing capacity.

Potential dungeon recruits are NPCs initially encountered as hostile or threatening. Once a person is no longer regarded as a threat, she may become eligible for recruitment if her individual requirements are met. Those requirements differ by character and can involve resolving circumstances, obligations, magical conditions, or personal goals.

Hostility does not necessarily imply an evil personality. The system can support misunderstanding, defensive behavior, conflicting duties, or dangerous magical circumstances without making cruelty a desired household trait.

Threat resolution, release, household membership, and romantic interest are separate decisions. Romance is not a condition of release or a substitute for recruitment requirements. A person who is safe to release can leave without joining. A willing new resident requires available residential accommodation, even if she prefers an underground room.

Recruitment should not silently erase established character facts. Resolving a problem can change someone's situation and perspective without replacing her personality. The gamemaster narrates the process; rules track eligibility, capacity, and accepted changes.

**Decision basis:** Q9–12, Q44, Q65–67.

## 12. The castle mystery and passive Resonance

**Resonance** is a working system label, not a confirmed in-world name. It represents the castle's passive response to enduring household conditions and significant relationship developments.

The castle's affinity for eroticism and intimacy is a real part of its unusual nature. The resource or state it produces can awaken additional possibilities. Its exact formula, display, thresholds, and unlock catalogue remain undesigned.

It should not be generated by repeatedly clicking the same interaction or measuring how many dialogue scenes were played. Free conversations and intimate downtime remain free of action-point costs without becoming repeatable resource exploits.

The castle does not manufacture willingness, overwrite preferences, or make residents accept attention to receive necessities. Essential housing, safety, and ordinary household functioning should remain independently sustainable. Affinity and voluntary participation provide atmosphere and possibilities, not coercion.

The foundational truth about the castle is established privately for the campaign and remains consistent. The gamemaster may add discoveries compatible with it, but should not retcon the explanation whenever a new scene is needed. Hidden lore is not exposed in agent handoffs, public tool responses, or generated UI summaries.

The first recruit can contribute a meaningful clue while retaining her own useful role, aspirations, and personal story. She need not explain the castle on arrival.

**Decision basis:** Q17, Q26, Q29–31, Q60, Q69.

## 13. Visual experience and interaction design

### Overall direction

The game is desktop-first and follows the established illustrated visual identity of Eris and Selene. Interface framing uses restrained fantasy/ledger details around readable controls and uncluttered character sheets. The artwork, rather than heavily ornamental menus, carries most of the visual richness.

There is no walking-avatar requirement, continuous navigation animation, or movable-furniture grid. Room placement matters in the simulation, while access and decoration remain direct.

### Three connected views

**Castle view:** An illustrated floor plan with selectable rooms, functions, occupant portraits, and relevant activity indicators. Clicking a destination immediately opens its room. Unknown or sealed sections do not expose their undiscovered contents.

**Room view:** A persistent natural-perspective interior, approximately at eye level, with a consistent composition. Restoration state, purpose, and selected furnishings determine its appearance. Occupant portraits provide access to conversations; management controls handle appropriate assignments, upgrades, production, and decoration.

**Conversation view:** The resident's detailed portrait or full figure occupies most of the screen, with the room supplying context. Dialogue and input occupy a smaller area. Group conversations are encouraged; a suggested presentation emphasizes the current speaker while retaining other participants in smaller portraits. The precise group layout is not yet a final UI specification.

### Fixed-slot decoration

Rooms have fixed furnishing slots with selectable variants. Choosing a different bed changes the bed at its established slot; it does not redraw the entire room or let the player move it on a grid. Room types have appropriate slot sets. Upgrades may unlock additional supported options.

The game should distinguish a functional improvement from an aesthetic variation of equal function. Residents use the same system to personalize their rooms. Exact furniture lists, slot counts, and statistical effects remain content decisions.

### Ensembles and visible wardrobe state

Clothing uses named ensembles with configurable components and saved styling variants. An ensemble can specify compatible garments, accessories, colors, optional underlayers, hem variants, and fastening states. It records both the components worn and their supported configuration, rather than treating every look as an unrelated character image.

Household clothing and adventure equipment have separate saved configurations. Roles requiring functional equipment, such as guards, may retain it while at home. Cosmetic styling is a free castle activity; mechanical loadout changes remain subject to the castle-only preparation rules.

Wardrobe state and visible appearance are distinct. A concealed component change need not alter the visible illustration. A visible change should preserve the person's face, proportions, and unrelated identifying details. Increasing closeness can influence personal comfort and choices without forcing every character into one style.

### Text and invitations

Conversation supports both free text and suggested responses or actions. Ordinary exchanges are brief and characterful, with occasional narration. Meaningful developments can support longer scenes. The artwork carries immediate visual description; prose contributes intention, personality, and information rather than endlessly repeating what is visible.

Mechanical commitments should be clearly identified rather than silently inferred from casual dialogue. Residents' substantial invitations wait for selection and do not expire. Brief ambient interaction adds presence without taking over the screen.

### Consistent assets and correction

Each character has a persistent visual identity/reference. Expressions, outfits, equipment, and ritual transformations create supported variants of that person. Existing assets are reused where appropriate rather than regenerating a new face for every exchange.

The interface offers image review and a request-correction workflow for conspicuous errors such as extra limbs, malformed anatomy, or identity mismatch. A proposed revision should retain the accepted version for comparison and rollback. Corrections do not consume an in-world turn, rewrite a scene, or change character statistics.

Inside-game generation and external imports can coexist. Ordinary play need not be blocked by mandatory approval of every image. Large scene illustrations supplement persistent room and wardrobe state rather than becoming a second contradictory source of truth.

**Decision basis:** Q11–13, Q26, Q46, Q61, Q75, Q81–82, Q84–92.

## 14. Game rules, the gamemaster, and external agents

### Authority boundaries

The game's rules and persistent state determine resources, inventory, character abilities, capacity, action budgets, construction, advancement, and outcomes. The AI gamemaster runs NPC characterization and narrative, proposes content within the rules, and describes resolved changes.

Natural-language output is not automatically authority to change the database. Generated proposals must resolve through the same validated game rules used by the player interface. This is an architectural requirement, not a commitment to a particular framework or database.

The castle's foundational truth, NPC private information, and character-visible facts require distinct access scopes. Model context should contain only information appropriate to its role and the scene being processed.

### Agent participation

Eris and Selene use dedicated game tools, not browser automation. They inspect their visible state, converse, propose projects, make their own choices, manage preparations and assignments, and report readiness. Their tools must not grant omniscient lore access or special outcome privileges.

The visual interface and agent tools should reach one rules system. Their dedicated character control must remain separate from the gamemaster's control of other NPCs.

### Handoffs and memory

The game creates agent-specific session handoffs to make reconnection efficient. A recommended content set is campaign identity, phase, relevant character state, known recent events, outstanding commitments, pending decisions, and pointers to supporting records. A checkpoint after a resolved phase is a useful recovery recommendation, not a substitute for persistent game state.

The agents decide how and what to retain in Mnemosyne or another memory system. The game supplies continuity records rather than imposing their long-term memory strategy. Campaign experiences should remain identifiable as fictional events, distinct from real-world facts and server obligations.

The human player wants to discuss adventures with the agents outside the game. Such recollections can persist beyond a session, but actual campaign changes still pass through game tools and rules. Handoffs must not disclose another character's private conversations or the hidden castle explanation.

### Provider configuration

External model services are acceptable. OpenRouter is the intended initial provider. The application includes a configuration page for provider credentials and model selection, rather than hard-coding one model.

Recommended configurable roles are gamemaster/NPC text, image generation or correction, and optional summaries/handoffs. These are game-service settings; they do not replace the external agents' own model configurations. Provider/model capabilities and pricing have not been researched or selected in this specification.

Recommended safeguards include server-side credential storage, capability checks, explicit error messages, usage visibility, and recovery from failed requests without consuming an action or advancing the phase. Keys should not appear in campaign exports or character prompts. These are implementation requirements to refine, not claims of completed functionality.

**Decision basis:** Q14, Q37, Q46–48, Q55, Q78–81.

## 15. Saves, correction, and continuity

Separate solo and co-op saves preserve campaign identity, founders, residents, possessions, rooms, relationships, discoveries, and hidden truth. A generated illustration or agent memory entry does not replace the saved rules state.

The player prefers accepting established events, with correction tools reserved for actual mistakes. Useful corrections include contradictory lore, an accidentally changed character background, invalid state changes, and conspicuous visual errors. The default is not unrestricted authorial rewriting of inconvenient events or other players' choices.

A correction to an image is distinct from a narrative correction, and both are distinct from an in-world action. Versioned accepted assets and recoverable saves are recommended. Exact save storage, backup cadence, migration format, and audit history remain implementation details.

The phase model must not convert elapsed real-world time into production or events when reloading a campaign. Resuming returns to the actual saved phase and state.

**Decision basis:** Q6, Q37, Q48, Q55, Q80–83.

## 16. Visual-first development milestone

The first development priority is the visual experience. This is separate from the first campaign milestone, which remains restoration of a proper living wing.

### Recommended first prototype

Build a small, coherent visual slice: an illustrated floor plan; several selectable room interiors; fixed furnishing slots with variants; one stable adult character identity with detailed portrait/full-figure presentation; configurable ensemble examples; a character-focused conversation interface; morning/afternoon/evening presentation; non-interrupting invitations; and persistence for selected room and wardrobe states.

A correction/review panel should demonstrate how an accepted image and proposed revision are distinguished. Prototype content may use clearly labeled sample data; it must not pretend that a stub is the real gamemaster, that mock agents are Eris and Selene, or that the sample resident is a secretly finalized first recruit.

### Acceptance criteria

| Test | Desired result |
|---|---|
| Select a room on the castle plan | Its illustrated interior opens immediately; no walking simulation is required. |
| Change a furnishing variant | Only the appropriate fixed slot changes; the room remains recognizable. |
| Change a supported outfit component | The character remains recognizably the same person and the saved clothing state matches the display. |
| Begin or leave a conversation | The character dominates the conversation view, and returning to the room preserves context. |
| Receive a substantial invitation | It appears as an option rather than interrupting the current interaction. |
| Advance or reload | Phase and cosmetic choices persist; browsing and conversations do not advance time. |
| Review a visual correction | The accepted image remains recoverable; the correction does not change game mechanics. |

The next implementation layer can add authoritative solo rules, real gamemaster integration, productive facilities, research, recruitment, and an opening expedition. Dedicated real-agent participation and co-op readiness/consensus must be tested as actual integrations rather than inferred from simulated dialogue.

This staging is a recommendation, not a delivery promise or a change to the full game's co-op requirement. The project should not start by building all fifty residents, the annex, a large perk catalogue, or extensive dungeon content before validating the chosen visual experience.

## 17. Open implementation and balance decisions

The game's broad design is settled enough to prototype. Remaining work is specification and testing, not a requirement to keep asking foundational preference questions.

| Area | Still to define |
|---|---|
| Character mathematics | Exact attributes, scales, advancement costs, perk prerequisites, affinity effects, and prepared-loadout limits. |
| Work and time | Action budgets, activity durations, phase-resolution order, routine scheduling, and expedition continuation controls. |
| Economy | Wealth denomination, production rates, allocation granularity, reserves, allowances, and revenue-sharing numbers. |
| Magic | Initial principles, component grammar, material properties, validation rules, and exceptional-effect costs. |
| Resonance | Internal representation, growth conditions, display, unlocks, and anti-repetition rules. |
| Housing and containment | Exact room catalogue, per-room capacity, restoration requirements, annex costs, and specialized chamber compatibility. |
| Technical stack | Hosting process, database, frontend/rendering approach, authentication, backups, and exact agent-tool transport. |
| Model integration | Selected text and image models, feature support, request budgets, context assembly, and failure recovery. |
| Visual pipeline | Reference assets, layer/variant composition, correction workflow, supported wardrobe combinations, and asset versioning. |
| Co-op reconnection | Recovery when an agent is unavailable, without bypassing its authority or the explicit readiness requirement. |
| Campaign content | Starting geography, undisclosed castle truth, first recruit, opening discoveries, and initial ancestry/background options. |

### Final design test

The game should offer **deep choices with light routine obligations**. It succeeds when improving the castle, knowing its residents, experimenting with magic, and living alongside independent companions remain rewarding—even during a session with no combat, no new recruit, and no major construction completion.
