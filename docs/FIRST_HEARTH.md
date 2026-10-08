# The First Hearth — unreleased development checkpoint

A connected, optional opening on the existing Home screen. No new top-level menu, separate quest currency, global work queue, automatic recruitment, or hidden time advancement is introduced. Pending v0.74 card artwork, landscapes and logo remain included. Release delivery is on hold.

## Play the chapter

Create a fresh solo campaign, finish or skip the arrival reflections, and follow **The First Hearth** on Home. Put guidance aside whenever you want; restore it from Home. Other game actions remain available throughout. Earlier fresh saves can explicitly choose to follow the chapter. Demonstration households retain their existing experience.

1. Study the hearth wards using the ordinary 20-crown, three-phase research project.
2. Choose a remembered intention and make a warming lantern from compatible components.
3. Compare repair notes with Maren through the existing one-phase introduction, or continue alone. The authored exchange has practical, playful and independent responses. Its advice is remembered later. A visit, membership and work agreement remain distinct optional actions.
4. Visit the quarry shelter, or bring back a discovery from another available expedition. Salvage provides clay and binding thread for household work; surveying opens Weather sealing research. The quarry salvage's eight crowns use the existing departure wealth plan. Nothing counts as returned before arriving home.
5. Repair the kitchen, washroom and service wards. Craft and install a hearth kettle. When funds run short, guidance shows the exact shortfall and required copying phases. The living-wing milestone still resolves through ordinary Advance.
6. When evening arrives, take an optional quiet moment in the restored wing. If residents have joined, the existing housewarming is also available once everyone is home; headquarters work is linked nearby. Neither is accepted automatically.
7. Investigate the hearth mark using the existing two-phase mystery action. The chapter reads the campaign's established evidence, never replaces its lore, and offers a final choice of history, household or practical research as the next direction.

The chapter contains six authored remembered moments on the meeting route, five on the solo route, with fourteen response options across all six moments. Responses are shown only after selection. Later scenes recall the chosen intention and Maren's actual advice. No scene awards free materials, attributes or relationship points. A shared opening memory enters optional NPC dialogue context only for its actual participant; private reflections and undiscovered lore are excluded.

## Simpler systems

- One primary chapter suggestion stays visible on Home. The old opening panel is replaced for enrolled saves; completed chapter content folds into a notebook.
- Already funded research, crafting, repairs, introductions and mystery work show progress and a real Resume or Advance action. Resuming does not pay twice or discard another project's progress.
- Compatible crafting components are selected from available inventory, with the cheapest missing components offered if needed. Alternative materials remain available in the normal workbench. As with explicit ordinary crafting, listed protected stock may be consumed; the action states this before commitment.
- Costs, assignment changes and blockers are computed from current state. Review links open the existing room/destination, without spending resources or advancing time.
- Chapter memories appear in the existing journal, with a return link to the chapter notebook.
- Mystery investigations now appear in shared project previews and resumption controls.
- **Arrange the first archive** qualifies a solo scholar for the second mystery investigation. The previously supported living-index route still qualifies. This removes an unintended dependence on Mira's old study path without changing evidence or rewards.

## Continuity

Save schema stays 59. An optional `soloLife.firstHearth` record holds visibility, the company choice and the selected memories. It is initialized for new fresh starts or explicit opt-in only. Read-only views do not add records. Older fresh campaigns are not enrolled automatically, and their achievements are recognized without fabricating conversations. Demo campaigns receive no chapter.

Dismissing guidance changes only visibility. Changing the early meeting choice to solo does not silently cancel a funded appointment. All other work, money, relationships, identities, art overrides, saved lore and campaign files remain governed by the existing rules. No existing artwork or content-pack bytes are changed.

## Verified paths and limits

Four clean starts use only ordinary actions, with a serialization/reload after every action:

| Company | Field approach | Advances | Completion | Remaining crowns | Material purchases |
|---|---|---:|---|---:|---|
| Solo | Salvage | 25 | Day 9, afternoon | 2 | None |
| Meet Maren | Salvage | 25 | Day 9, afternoon | 2 | None |
| Solo | Survey | 28 | Day 10, afternoon | 1 | One porous clay |
| Meet Maren | Survey | 28 | Day 10, afternoon | 1 | One porous clay |

These are reproducible baseline routes with the default build and wealth plan, not promises about real-time playing duration. Free conversations, browsing and reading add no phases; other work and visits can change the day count. The final investigation happens after the evening reflection. Introductory resource values and existing project costs are unchanged.

`VERIFICATION_FIRST_HEARTH.json` records the regression and preservation checks. The complete connected UI playthrough uses the actual JavaScript controllers, Python rules and saved campaign, with a DOM test double. It covers portraits, navigation, choices, costs, phases, pause/resume, journal, dismissal, reload and the chosen next direction.

A rendered browser run was attempted but cannot launch: the Playwright Chromium executable is absent. No desktop/mobile visual verification is claimed. Live-provider dialogue, co-op agents and Docker runtime are outside this checkpoint's verification.
