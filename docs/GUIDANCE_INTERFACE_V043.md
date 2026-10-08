# v0.43 — goals, phase briefings and context without losing your place

## Pinned goals and linked requirements

Goals is available in the main navigation. Pin up to three goals; Home shows their next unmet requirement. Pins belong to the campaign and survive reloads and backups. Pinning spends nothing, changes no assignment and advances no time. Completed goals stay pinned until you put them aside.

The initial goal catalogue covers a first lantern, the conservatory, the proper living wing, and welcoming Maren, Brakka or Fenna. Each goal exposes its steps and links to the appropriate activity. Fenna's sequence includes hearth research, a spare lantern, two binding threads above reserves, the footbridge delivery, a returned nursery discovery, the introduction, and agreed visiting/membership. Delivered supplies are not incorrectly requested again after consumption. Installed or expedition-carried lanterns do not count as spare delivery stock. Goals guide; existing rules still govern every action and every character agreement.

## Advance preview and completion summary

Preview Advance opens a read-only dialog with household assignments, tracked project progress, expected completions and changes in shared crowns/core materials. The preview resolves one normal Advance on a detached copy, so current work contributions and supply rules apply. It does not write the campaign, spend resources or call a model provider. Waiting choices show the actual Advance blocker. Resting is described neutrally.

Progress rows cover hearth and catalogue research, conservatory/facility/housing restoration, core crafting, training, focus projects, public-workshop jobs, personal stories and local introductions. The expandable existing forecast retains other work, travel and household systems; not every subsystem has a separate progress row. Speculative field discoveries and story prose are not shown.

The saved phase summary leads with tracked completions and newly available tasks. Up to three ready follow-up actions can be executed through the existing rules-checked task endpoint. Detailed events and routine production remain available under an expandable section. The phase board places waiting choices, ready results and newly available opportunities first, with continuing work and other opportunities underneath.

## Context, artwork and navigation

The household strip and inline character portraits outside other controls open a compact person panel. It shows current location/assignment, tracked work and ambition, with links to the character sheet, household work and conversations where applicable. Viewing it preserves the current screen. Full portraits and room illustrations can be expanded; accepted artwork and clothing variants remain respected. Native option controls retain their normal semantics.

Core workshop requirements link to material and principle panels. Materials show stock, protected reserves and purchase price, then link directly to their Stores row. Principles explain whether the current maker knows them, can study the archive, or needs to follow their source. These contextual links currently cover core workshop requirements; the larger public catalogue keeps its existing detailed requirement views.

The core workshop offers a ready-to-craft filter for the chosen maker. It checks knowledge, presence and sufficient compatible components, including quantities when the same material could fill both slots. Component defaults avoid choosing one remaining item for two slots. Existing per-recipe choices are retained while valid. Navigation remembers per-view scroll positions during the browser session; maker, recipe and existing draft/filter selections remain in memory. Goal pins are saved server-side; browser navigation position is not.

## Validation and remaining work

471 existing Python tests and five new guidance tests pass. All 21 connected UI suites pass, including the long campaign playthrough and the new guidance flow. New checks exercise nonmutating previews against actual completions and income, paused and blocked work, pin limits/persistence, the Fenna dependency chain, completion follow-up actions, context panels, recipe filtering, scroll memory and artwork expansion.

These are headless template/controller and SQLite checks. The available browser remains on a local-server error page; desktop/mobile layout, painting, touch interactions and actual focus behaviour were not verified. Responsive styles are included, but visual QA remains outstanding. Live providers and Docker were not exercised.

Existing saves remain schema 39, with optional goal pins and completion records under soloLife. Original public and example content-pack archives are unchanged. Co-op remains deferred. Future UI work includes a searchable action finder, broader public-catalogue context links, and more concise explanations for legacy disabled controls.
