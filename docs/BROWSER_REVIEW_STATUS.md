# Browser usability review — access status

## Current checkpoint — 8 October 2026, v0.105 reviewed / v0.106 prepared

The user's running Codespace made a rendered desktop review possible. A separate demonstration campaign was used to inspect the main early-game screens, rooms, character workspaces, resources, bestiary, bounty requirements and Help. Screenshots record the original v0.105 build. The review found concrete navigation, labeling and information-hierarchy issues; v0.106 implements the fixes and passes automated UI checks.

The revised build has not been installed or rendered in the Codespace. Mobile layouts, broad keyboard/focus coverage, late-game combat remain pending. After the user approved enabling cheats in the separate review campaign, the revealed bestiary was checked and its persistence verified after reload. All 14 completed creature pages were inspected, with the 21 ancestry references and representative material/bounty links also checked. The campaign is marked TESTING MODIFIED. See [the full review and release notes](RELEASE_V106.md) and [current verification](VERIFICATION_V106.json).

The entries below are historical checkpoints. Their browser-access limitations do not describe the successful v0.105 Codespace review.

---

4 October 2026 · Stonework and Spellcraft v0.20

A real browser review was attempted using a separate test data directory. No player save or external provider account was used.

- No local Chromium, Chrome or Firefox executable was available. The runtime contains the Playwright package, but its expected Chromium binary is absent.
- A temporary local game server started successfully on port 8080.
- The available cloud Chrome browser refused navigation to that local server with `net::ERR_BLOCKED_BY_CLIENT`.
- No gameplay page was rendered in that browser. This was an access failure, not evidence of a game UI defect or a bot-detection challenge.
- The temporary server was stopped after the failed review attempt.

Consequently no new claims of visual layout, keyboard focus, scrolling, responsive behavior or real-browser usability verification can be made. The existing 213 rule/server tests and 23-view headless controller checks remain the latest automated evidence; they are not a substitute for visual testing.

## Next accessible-browser pass

Use an isolated sample save. Check the desktop layout first, then a narrower window. Walk through castle navigation, room text furnishing/effect panels, research, crafting component selection and disabled-state explanations, explicit charm installation, keyboard navigation and visible focus, phase-result dialog dismissal, character-sheet scrolling, personal projects, saved preparation sets, spell forms and review panels, and save/reload. Test validation errors and recovery without using a live paid provider.

Record viewport, exact reproduction steps, expected/actual behavior and before/after screenshots for any fixes. A browser that can reach the test build is needed; the user does not need to be present once that access exists. No public deployment, authentication change or exposure of a household save is required just to perform this review.

Later automated checkpoint (v0.22): 236 Python tests and a 24-view connected headless playthrough pass, including the authored summoning lifecycle. The earlier browser access blocker remains unresolved; this does not add visual verification.

Automated checkpoint 0.23: 247 Python tests and the extended 24-view controller playthrough pass. A clean staged runtime serves health, schema 22 state, the frontend and Iona’s PNG portrait. Image content was inspected directly, but its in-browser layout remains unverified.

## v0.33 checkpoint

No local Chromium, Chrome or Firefox executable is available in this workspace. The earlier cloud-browser access blocker has not been bypassed. The current checkpoint has 372 Python tests and eleven connected headless UI suites, including content import and editable character review. These do not verify layout, focus, scrolling or real-browser interactions.

## v0.46 checkpoint — 5 October 2026

The browser limitation was rechecked with an isolated local server. No installed browser executable was found; Playwright’s Chromium download failed as an invalid ZIP. Cloud Chrome navigation to the local server returned net::ERR_BLOCKED_BY_CLIENT. No page was rendered. All 486 Python tests and 23 headless UI suites pass, but desktop/mobile painting, real keyboard focus and touch behavior remain unverified. See USABILITY_V046.txt for the targeted review checklist.

## v0.47 checkpoint

501 Python tests and 24 connected headless UI suites pass. New portrait generation is tested with controlled responses, including local HTTP routes; no live paid provider or rendered-browser verification is claimed. The existing browser access blocker remains. Add character creation, portrait preview/review, generated-request recovery, long identity text and keyboard/touch use to the next desktop/mobile review.


## v0.48 headquarters changes

Connected headless checks cover headquarters navigation, construction, paused work, chapel reflection, room prerequisites, independent artwork targeting and housing locks. No installed browser executable was found in this environment. Rendered desktop/mobile layout, focus and touch verification remain outstanding; no screenshots or rendered QA are claimed.


## v0.49 room workspaces

New connected UI checks cover persistent room context, activity switching, actual first research/crafting and treasury guidance. Responsive room navigation has small-screen styles; actual desktop/mobile rendering, focus and touch testing remain outstanding under the previously documented browser blocker. No new rendered-browser claims are made.

## v0.50 artwork integration

526 Python tests and 26 headless UI suites pass. Reviewed 34 supplied room images and 23 generated restyles, preserving room hashes, raster dimensions and required alpha. Headquarters catalogue images, room activity headers, new specialist-chamber artwork slots and legacy URL compatibility are covered by template/HTTP checks. Actual desktop/mobile rendering, image cropping in the browser, keyboard focus and touch behavior remain outstanding. No screenshot approval is claimed.


## v0.51 checkpoint — 5 October 2026

Chromium headless-shell installation was retried. The download again produced an invalid ZIP (missing end-of-central-directory signature), leaving no usable browser executable. No rendered page or screenshot was obtained. The cloud-browser localhost restriction was not bypassed.

`scripts/browser_review.cjs` now provides an isolated, repeatable rendered check for a machine with Playwright Chromium. It creates temporary fresh saves, starts localhost servers on free ports, exercises character setup, both arrival choices, first research and lantern, room navigation and notebook pages, and checks reload persistence, script/HTTP errors, broken images and horizontal overflow at 1440, 390 and 320 pixels. It captures full-page screenshots and reports small controls and a keyboard focus sample. Inspect the output manually for image crops, legibility, focus visibility, dialog behavior and comfortable touch use. This runner has been syntax-checked but could not be executed here; it is not completed browser QA.

Install Playwright in a separate tooling directory if preferred, install its Chromium browser, then run from the game folder:

```
node scripts/browser_review.cjs /path/to/review-output
```

Set `PLAYWRIGHT_MODULE` to an absolute installed Playwright module path and `PYTHON` to the desired Python executable when needed. Game runtime dependencies are unchanged. The runner never opens the player's data directory or calls an image/text provider.


## v0.52 checkpoint — 5 October 2026 (Toronto)

The headless-shell download was retried and failed with an invalid ZIP. No usable local browser became available; no rendered screenshots, keyboard or touch results are claimed. The existing runner now includes Resident stories, Castle specialists and Projects & next improvements. It remains unexecuted. Check long specialist requirements, the eleven cards, unavailable portraits, paused-installation cancellation, and the four-stage service-road choices during the next desktop/mobile pass.
