# v0.68 — Making the next action clearer

This release follows the v0.67 UI overhaul with a focused review of castle work, companion interaction and expedition decisions. It changes presentation and navigation, not authored rules, character progress or spell effects. Save schema remains **57**.

## Changes

- **Castle work:** Home now shows progressing projects from the existing Advance preview, including completion estimates and a count of paused or waiting projects. Waiting choices receive a direct route to the task board. Browsing this panel spends no time or resources.
- **Phase feedback:** the Advance dialog shows the first four saved phase events under “What changed,” with the complete event list still available below. Existing completion actions display their descriptions and consequences beside their buttons.
- **Companion navigation:** scroll positions belong to the actual screen, character and tab. Opening a new tab starts at its heading; returning to a visited tab restores that tab’s position.
- **Conversation invitations:** Home and combined-journal links to social conversations select the intended scene and reset incompatible conversation filters. The scene is promoted within the list and receives scroll/focus targeting when a real DOM is available.
- **Spell recipients:** recipient selections outside forms are now retained through interface updates and navigation within their existing screen context. This does not change target eligibility or casting costs.
- **Expeditions:** the current field decision and travel controls appear before supplementary field-magic information. Dedicated aqueduct decisions retain their actual field-magic controls. Supplementary condition information is expandable on other routes. Large destination paintings remain visible when reviewing destinations before departure.

All existing ordinary methods remain available. No invitations expire, no relationship gates change, and only explicit Advance actions move time.

## Review and remaining limitation

The cloud browser could not open the temporary local server: `ERR_BLOCKED_BY_CLIENT`. The local runtime has Playwright libraries but no installed Chromium or Firefox executable. No rendered browser walkthrough, screenshot inspection or actual mobile layout validation was completed.

Connected controller checks cover the new navigation and feedback, including an ordinary expedition method and preserved campaign state while browsing. Existing connected suites cover the broader castle, companion and expedition loops. Reconciliation remains covered by the deterministic tree tests introduced in v0.67. Exact results are in `VERIFICATION_V068.json` and `UI_REGRESSION_V068.json`.

The optional `scripts/browser_review.cjs` has been expanded for a browser-capable environment. With Node, Python, Playwright and Chromium already installed, run from the project root:

```sh
node scripts/browser_review.cjs /path/to/review-output
```

It creates disposable fresh and established test campaigns at desktop, 390-pixel and 320-pixel widths. It checks navigation, character styling drafts, journal typing focus, spell filters, an ordinary expedition route, return and reload. It records screenshots and overflow/broken-image findings. Inspect the resulting screenshots, focus visibility, touch targets and dialogs before treating the browser review as complete. This expanded script passed syntax checking here; its rendered scenarios have not run.

## Upgrade

Stop the old server, replace the application files, and retain the **complete existing `data` directory, including `data/assets`**. Run `python server.py`. The release includes all existing bundled portraits, room artwork and spell icons. It does not replace a live campaign or deploy the game.
