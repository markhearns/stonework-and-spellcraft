# v0.100 — Work, field objectives and remembered experiences

This release implements the eight agreed system refinements. Instructions and conversations follow the standing rule in `WRITING_GUIDE.md`: use plain English and state what an action does, what it costs and what stops it from working.

## 1. External commissions

Open **External commissions** from Home or household work. Four clients offer translation, lantern repair, medicine preparation and ward diagnosis. Choose a worker and crowns, materials or a lesson as payment. Each order takes two assigned work phases; its payment is fixed when accepted. One order can be active, and each client offers another order the day after delivery. Orders do not expire. Cancelling returns committed materials. A client's lesson grants that worker one advancement point once.

The crown payment is twice the current copying income plus four crowns. Copying remains available. Trade orders require their listed room, skill and unreserved materials; translation is available from the opening.

## 2. Lasting companion improvements

Open **Practical companion projects**, or the relevant companion's Quests tab. Each project costs 10 crowns plus its listed materials and takes its owner three assigned phases.

- Iona adds safe detours after completing her crossing atlas. With Iona present, an objective patrol can bypass its enemy after clearing the site obstacle. The completed objective pays its reward; the bypass gives no enemy loot.
- Brakka makes fitting gauges after a completed patrol. When she joins a patrol, each conscious party member receives one extra personal cover against the first actual enemy attack in each encounter. A cancelled attack does not use it up.
- Sylva plants specimen beds after a fern-nursery discovery or observation patrol. Completed observation and crossing-repair patrols bring home two extra silver ivy while she remains resident and the conservatory is available.

## 3. Practical spell combinations

Objective patrols contain a damaged bridge support, hot ward mechanism or smoke-filled passage. Ordinary work takes three phases, or two with Fieldcraft rank 1. Suitable prepared ice, water or wind spells change the condition in one phase. Any conscious party member can then finish the practical work in one more phase.

Casting consumes the actual spell components. Retreat returns components committed to an unfinished cast; completed casts are not refunded. Waiting at a decision does not advance the obstacle or cause attacks.

## 4. Patrol objectives

After Chapter 7, **Field patrols** offers delivery, rescue, creature observation and crossing repair. Each uses a fixed route with a practical obstacle and one encounter. Two task steps secure the objective. The action preview shows any retaliation; observation is safe with Fieldcraft rank 1 or a prepared Wisp scout. On repairs, protection or control with two conscious party members also advances the work.

Fighting, negotiation or Iona's available detour can also complete an objective. Returning successfully pays the stated objective reward. Finishing through task work grants no enemy loot. Retreat grants no objective payment. Each participant earns one advancement point for their first completion of each objective.

## 5. Personal signature refinements

The scholar and all 15 authored companions have an additional refinement suited to their abilities, with its numerical effect shown in the Armoury. Existing Precision, Shelter and Care remain available. Only one refinement is installed at a time, on the same physical signature item, through the existing paid equipment work queue.

Different commissions, practical projects, field tasks, protection, healing and control can contribute accomplishments alongside enemy types. Two different accomplishments unlock rank one; four unlock rank two. Repeating the same accomplishment does not add another. The completed piece must be equipped in the household loadout for work or the expedition loadout for field accomplishments. Stowed equipment earns nothing. Refining removes the piece from loadouts; equip it again after completion.

## 6. Work routines

In **Work arrangements**, choose an existing individual project or a provision target. At the stopping point, the worker rests or resumes one agreed, already funded project for the next phase. Evening rest pauses work for sleep and resumes unfinished work the next morning. Manual reassignment and travel pause the routine. Resume it explicitly after returning home.

Routines only run when you press **Advance**. They do not purchase supplies, fund new projects or dispatch anyone. The Advance preview includes their assignment changes. Multiple workers can keep separate routines. Saved work arrangements can also resume the new commission, companion-project and lamp assignments.

## 7. Follow-up conversations

Completed companion work, protection during patrols, successful objectives and shared castle discoveries create conversations about the recorded event. They appear in the activity feed, Relationships, the journal and **Follow-up conversations**. Each companion receives at most one invitation per event category, so repeat work does not fill the feed.

Choose to record contributions, plan another outing or spend friendly or affectionate time together. Planning saves a suggested party for review on the patrol preparation form; nobody leaves automatically. Invitations can be deferred and restored. They do not expire or award repeatable relationship points. Accepted memories enter that companion's dialogue context.

## 8. Castle investigation and restoration

Three investigations continue after the original four clues: trace the disconnected ward, read the survey cylinder and recover the reading-lamp plan. Existing campaign-owned history and recorded discoveries are preserved. Unseen evidence remains outside public state and dialogue context.

Repairing the library lamp costs six crowns and one binding thread and takes two scholar phases. It restores the light and lets the scholar share the discovered survey with companions.

The optional lens study requires the repaired lamp and 12 accumulated Resonance. It costs eight crowns and one moon glass and takes two phases. It teaches Field calibration, grants one advancement point once and permits amber or violet library lighting. Resonance is not spent. The light colour is cosmetic. Established mutual affection with other residents can now contribute to the existing Resonance generation, with the existing settee requirement and cap of three per phase.

## Upgrade and verification

Stop the old server, preserve the complete `data/` directory including campaign subfolders and artwork, extract this release and restore that directory. Start with `python server.py`. Save schema stays at 65; new records are added only when used. No live save or credentials are included.

A save produced by the actual v0.99 code was checked for exact migration and read-only state, then used to complete a commission and resume its prior research. All 279 existing image assets match v0.99 byte for byte, including Iona's revised design.

Automated checks cover rules, refunds, save retries, controllers and two earned eight-chapter campaigns. See `VERIFICATION_V100.json` for scope and results. These are headless checks; rendered browser review remains deferred at the user's request.
