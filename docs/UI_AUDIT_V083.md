# UI audit — v0.83

The audit inspected live routed composition, controls, navigation, styles and asset references across the game. An established-household fixture provides a repeatable 62-screen inventory; fresh-start and system-specific behavior are exercised by the connected UI suites. Raw counts include controls inside closed disclosures; they are structural measurements, not a measure of visible screen height.

| Area | Finding | Implemented response |
|---|---|---|
| Home | The map disclosure embedded the older complete home screen, repeating goals, phase guidance, room cards and a primary heading. | Render the map and milestones directly; retain one home heading and one activity feed. Preserve the compact next-step prompt for older saves without chapter guidance. |
| Chapters | Completed summaries accumulated, Chapter 5 was absent from search/direct navigation, and chapter highlighting was inconsistent. | One completed-chapter history disclosure; one shared navigation catalogue; explicit chapter names and Castle section mapping. |
| Navigation | The armoury alias lost Workshop highlighting; breadcrumbs could display internal view names; Magic and Workshop shared a book icon. | Resolve aliases centrally, name the selected room/person, make room names searchable, and use distinct engraved icons. |
| Companions | Development rendered another character picker and header under the character frame; a household drawer repeated the same selection context. | Remove duplicate markup in embedded development, keep the frame's selector and active section when switching people, and omit the drawer on personal screens. |
| Equipment | Owner/worker selection needed an extra confirmation click, loadouts repeated six actions, and selected details appeared below the inventory. | Apply selectors immediately; consolidate loadout controls; move and focus item details above the list. |
| Equipment work | Irrelevant effect/pattern controls appeared for every operation; two-slot objects looked like duplicate pieces. | Show operation-specific fields; preserve drafts per item; mark linked occupied slots explicitly. |
| Equipment techniques | The entire earlier working-tool screen was embedded in the unified armoury. | Keep a dedicated linked techniques screen using the same backend records; preserve owner context. |
| Research | Every project repeated every household member's lead controls and knowledge links. | One lead selector, with per-study requirements and actions; fold completed studies. |
| Archive and rituals | A long archive notebook appeared in several screens; nested ritual/wardrobe sections introduced second primary headings. | Fold reference material; use section-level headings in embedded content. |
| Layout/accessibility | Two containers both applied substantial horizontal padding; selected items and reviews lacked focus targets; two dialogs had no accessible name. | Single outer gutter, wrapping controls, focusable detail/review regions, named dialogs. |
| Help/settings | Old build text described incomplete systems now present. | Describe five chapters and current navigation; leave hosting and backup instructions accessible. |

## Image review

Two new 128-pixel WebP icons, 16,734 bytes combined, provide useful destination identities. Their prompts, alpha status and hashes are in `ART_V083.json`. Originals were inspected; encoded icons were inspected at their runtime size.

Existing art now accompanies Character overview, Attributes & training, Character customization, Life together, Work arrangements, Household life & clothing, and Household stories & connections cards. Associated room imagery is used where appropriate. The available assets already cover room interiors, companion outfit portraits, item categories and authored expeditions; additional large banners would repeat information and lengthen these pages.

All 246 earlier runtime images are retained byte-for-byte. No accepted character design, wardrobe, associated-room portrait or splash image is regenerated in this pass.

## Boundaries

The work fixes interface friction without changing progression, equipment costs, enchantment effects or relationship rules. Some redundancy is deliberate: global phase controls remain available alongside contextual forecasts, and the home room shortcuts coexist with the full construction catalogue.

The browser's earlier `ERR_BLOCKED_BY_CLIENT` restriction remains unresolved. This audit cannot certify rendered breakpoints, clipping, real browser focus behavior or visual aesthetics in the running game. CSS and generated assets were inspected, and connected headless tests check controller behavior, composed markup, escaping and state preservation. No external deployment or browser-security bypass was used.
