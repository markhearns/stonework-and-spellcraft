# v0.41 — phase tasks and a working solo household

## Phase task board

Home presents four priority tasks and a link to the complete board. The sidebar and header provide a This phase shortcut with the current available count. Tasks group into waiting choices, ready results, paused/unassigned work, optional invitations and new opportunities. They are built from actual state and validated with the authoritative rules on a detached copy; merely rendering the board cannot spend resources or advance work.

Direct task actions cover introductory and catalogue research, first-lantern crafting, resuming common work, facilities and guest rooms, ordinary introductions, installations, deliveries and original expedition choices/return. Tasks that need detailed choices open their existing screen, with the relevant person or public record selected where available. This includes visitors, scene invitations and recent public-workshop completions. The full content catalogue still handles its detailed component, target and participant selections; the board does not enumerate every possible recipe or spell configuration.

After each Advance, a saved notice records the newly available task IDs. The phase summary names up to five and links to all tasks. New this phase labels persist through a reload and disappear when their tasks stop being valid. Optional tasks can be put aside for the current phase and restored; the next phase clears their dismissal. Required field choices cannot be hidden. There are no expiry penalties, automatic task execution or desktop-notification permission requests.

Executing a task rechecks its current availability and then uses the existing action rules. Stale task IDs, insufficient funds, absent actors and unfinished prerequisites are rejected atomically. Request-ID retries cannot spend the costs twice. Starting/resuming work changes that person’s primary assignment; other project progress is preserved. Costs and work durations appear before execution.

## Household work and field companions

People → Household work records explicit willingness for recruited NPCs to take on garden tending and fieldwork. Agreements imply neither automatic assignments, personal relationships nor wages. They can be withdrawn while everyone involved is home; ending a garden agreement stops that assignment. Existing authored Mira offers retain their progression requirements.

The founder can staff the conservatory. Recruited residents can staff it after agreeing the role, including while the founder travels. One gardener produces one normal harvest; garden improvements and reserve priorities retain their effects. The root tender remains an unstaffed fallback, not a second harvest.

The original expedition system now uses the selected actual companion throughout: away/present state, suspended work, skill checks, prepared practices, focus effects, advancement, personal learning, money shares and return reports. One companion travels with the founder. The companion must be a resident, have agreed fieldwork and be at home. Ordinary sites and the multi-stage observatory use the actual party. Early return grants no unfinished discovery. On return, the party is at home and unassigned; other projects remain paused until resumed.

## A home worth celebrating

Fresh campaigns gain an optional one-time housewarming after the Proper Living Wing milestone. Everyone must be home; the event records the actual participants and phase. It works for the scholar alone, creates no phantom demonstration resident, and spends no time, crowns or Resonance. It appears on the task board and household progress panel. The event remains available until chosen.

## Save compatibility and scope

Schema 39 adds solo household state. Existing campaign mode, resources, identities, projects and histories are preserved, with automatic pre-migration backups. Phase notices and current-phase dismissals are saved with the campaign. New packages still extract into `stonework-and-spellcraft/`; no save data is bundled. The sixteen public packs, 1,599 public content records, 319 fixed mechanics adapters and original source ZIPs remain intact. Co-op and Eris/Selene integration remain deferred.

## Verification

468 Python tests and 19 connected headless UI suites pass. Added coverage includes rules-checked task readiness without mutation; stale task and duplicate-request rejection; new-phase detection, dismissal and persisted labels; quick research/crafting/installation; public completion notices; voluntary roles; founder/resident garden production; no duplicate gardeners; companion absence, skill contributions, personal learning and financial shares; normal/early/observatory return; and an actual-participant housewarming without repeat rewards.

The connected UI flow starts research through the board, checks the new-phase lantern notification, executes crafting and installation, agrees resident roles, harvests with a resident and returns from an expedition with the actual companion’s learning. Existing content, recruitment, household, equipment, story and campaign flows remain covered. These are template/controller and SQLite integration checks. Rendered desktop/mobile layout, focus behavior and real browser interaction remain unverified because the available browser could not reach the local server. Live providers and Docker were not exercised.
