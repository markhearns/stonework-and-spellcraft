# v0.106 — UI improvements from a rendered desktop review

8 October 2026

The v0.105 Codespace received a rendered desktop review using a separate demonstration campaign. Its artwork and overall visual identity work well. The strongest opportunities were clearer next actions, less repeated information above the controls, and more predictable navigation.

This update implements the findings below. It has passed automated UI checks but has not yet been installed or rendered in the Codespace. Screenshots in the patch's `review-evidence/` folder show the original v0.105 build, not the revised layout.

## Changes

| Area | Finding in v0.105 | Change in v0.106 |
| --- | --- | --- |
| Home | The prominent action did not consistently lead toward the displayed opening objective. | The primary action follows the objective; rooms and companions remain secondary choices. |
| Shared layout | Breadcrumbs, household controls, Help and repeated phase explanations consumed substantial vertical space. | Compact page utilities and desktop phase controls bring useful content higher. |
| Headquarters | Workforce information competed with choosing a room. | Workforce controls are an expandable section. |
| Rooms | Room titles, activity links and social panels repeated before the main work. | One room overview title, artwork before activity controls, and shorter headers in work screens. |
| Spellbook | An empty spellbook showed substantial guidance and planning controls before the learning form. | Learning comes first; guidance and assignment details follow. Irrelevant empty-state filters and casting plans are omitted. |
| Bestiary | Breadcrumbs named the first creature regardless of the current page; list and detail shared scroll positions. Cheat-revealed knowledge was labelled “observed.” | Correct list/detail breadcrumbs and independent navigation contexts. Filters now distinguish unlocked knowledge from the reference-only state without implying actual sightings. |
| Navigation | Search results persisted after navigation; the destination dropdown listed individual entries that all opened the same guide page. | Search clears when following a destination. The dropdown has one guide destination; individual entries remain searchable. |
| Equipment | “Review starting equipment” immediately issued and equipped gear. | Renamed to “Receive & equip starting gear” so the action is explicit. |
| Character identity | Automatic inline portraits duplicated portraits already present in several summaries. | Identity labels suppress the redundant inline portraits, including the bounty/patrol party selector. |
| This phase | All opportunities could be hidden inside a collapsed group. | Routine opportunities start expanded when no more urgent group is present. |
| Stores | Pantry information appeared above the page title; prices read “6 to buy crowns.” | Page title first and natural price wording. |
| Adventures | Bestiary, bounties and patrol destinations lacked specific artwork. | Existing creature artwork illustrates these destinations. |
| Help | No focused help for the bestiary and bounties. | Added discovery, study, rewards, materials and reveal-cheat guidance. |
| Welcome screen | The displayed build was still 0.89. | The welcome screen uses the current application version. |

No new artwork was needed. Existing artwork files and game rules are unchanged. Save schema remains 66. The server version header now identifies 0.106.

## Review coverage

Rendered review covered the welcome screen, Home, phase preview and Escape dismissal, headquarters, Library room and research workspace, Infirmary links, companion directory, Mira's overview/build/conversation/wardrobe, Magic hub, Spellbook, Workshop hub, Armoury, Journal, This phase, Stores, Adventures, bestiary search/list/details and ancestry references, bounty requirements, Help and Cheats.

The desktop viewport was approximately 1363 × 936. Images inspected on these screens loaded. No horizontal overflow was observed in the checked Stores and bestiary states. These observations do not certify every screen, image, keyboard path or screen-reader flow.

The separate “Browser review — v0.105” campaign received its starting equipment when the misleadingly named button was inspected. Other campaigns were not used for this review. Automatic approval review initially blocked enabling cheats because it would persistently change the save. The user subsequently authorized this exact action. Cheats were enabled and the bestiary was filled out only in the separate review campaign. It is now marked TESTING MODIFIED.

## Validation and remaining work

Eight existing headless UI suites passed: unified navigation, room navigation, magic, armoury, bestiary v105, visual status v104, polish and social life. The new v106 regression suite covers navigation context, breadcrumbs, direct destinations, room hierarchy, spellbook ordering, prices, the gear label, duplicate preview portraits, visible opportunities and reused artwork paths. JavaScript and Python syntax checks passed.

These are controller/template checks, not rendered verification of the update. Next steps:

1. Install v0.106, restart the server, and hard-refresh the browser.
2. Review the revised desktop layout and navigation in the rendered browser.
3. Review mobile widths, touch targets, keyboard navigation and focus throughout the main flows.
4. Late-game combat and unlocked bounty flows still need rendered review using a suitable test campaign.

## Authorized bestiary follow-up

After approval, all 14 completed creature detail pages were checked in the browser. Each exposed tracks, behaviour, advice, gathering information, rare materials, encounter values and field notes. The field notes retained zero sightings and zero resolved encounters. The 21 ancestry references remained available; ancestry search and the Drow detail were checked.

The Storm-antler stag linked to its correct bounty, the Enchanting room and its material stock row, which still held zero antlers. The completed bestiary persisted after a full browser reload. Day 1 afternoon, 80 crowns and the two-person household remained unchanged. No horizontal overflow appeared in the checked creature detail states. Stag and griffin illustrations were visually confirmed; this is not a claim that every full-size illustration received a new visual audit.

The follow-up found two additional presentation issues: unlocked knowledge was labelled as observed fieldwork, and party selectors repeated member portraits. Both are included in the refreshed v0.106 packages. The affected v106 and bestiary integration suites were rerun successfully. Screenshots still show v0.105; the corrected build is not installed in the Codespace.

## Install

For an existing v0.105 installation, use the small UI patch and follow `APPLY_UI_PATCH.txt`. Stop the server, back up the complete `data/` directory, and overlay the patch's `stonework-and-spellcraft/` contents onto your actual game folder. Retain `data/`; the patch contains no campaign data. Restart with `python server.py`, then hard-refresh.

For a clean installation, extract the full v0.106 archive. To continue existing campaigns, copy the complete old `data/` directory into the new game folder before starting it. The archive includes the runtime artwork and excludes source-art masters and live campaign data.

Extracting files into a web host's `public_html` folder alone does not start this Python application. The host must support a persistent Python process and route web requests to it. Static/PHP-only hosting cannot run this game server as-is. The Codespace continues to use its existing running Python process until restarted with the updated files.
