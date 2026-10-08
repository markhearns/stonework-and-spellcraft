# v0.42 — character identity and understandable unavailable actions

This release adds a compact household strip with each resident's portrait, current assignment or absence, and a shortcut to their character sheet. It remains horizontally scrollable as the household grows.

Character mentions in rendered interface text now use shared portrait presentation, including headings, buttons, task descriptions, dialogue and journals. Inline portraits are 28 pixels (26 on small screens); headings use 36–44 pixels, the household strip and selected-person previews use 48 pixels, and character cards use a larger portrait. Supplied full-figure art is cropped toward the face for small portraits. Accepted portrait overrides and existing ensemble variants are respected. Editable values and native option labels are not rewritten; character selectors receive a selected-person portrait alongside the native control. Characters without accepted artwork have an explicitly labelled placeholder. The scholar now has an artwork slot in Settings → Illustration review.

Activity cards reuse existing room and character artwork. No new illustration files or external image service are required. The original content-pack archives are unchanged.

## Unavailable actions

Unavailable buttons are focusable, marked aria-disabled, and display an explanation on activation. Hover also exposes the reason through the title. The click handler prevents the normal button action, including form submission, and opens a labelled dialog. Native disabled form fields retain their disabled state and receive an adjacent disclosure. Disabled native options have an expandable explanation below their selector.

Where the rules already provide blocker arrays, the control uses those exact reasons. Common costs, absence, protected stock, project locks, preparation limits, pending drafts, and completed choices have explicit explanations. Legacy controls without a dedicated reason use their containing panel's current requirements and status in the popup; these longer contextual explanations remain candidates for more concise, action-specific wording.

Local introduction readiness and action validation now share a blocker function. Fenna needs a returned fern-nursery discovery; Brakka needs the restored conservatory; Maren is initially available. Pending appointments, scholar absence, completed introductions and legacy name collisions also have explicit reasons. Locked cards include a shortcut to the relevant route, restoration or research screen. Clicking Fenna's route shortcut selects the nursery and shows its own route-access requirements.

## Verification and limits

471 Python tests passed, including new recruitment reason checks. The 20 connected UI suites cover the existing campaign systems and the new presentation checks. These are headless template/controller and SQLite tests, not rendered-browser QA. New checks verify that unavailable recruitment opens an explanation without changing the revision; the nursery shortcut selects the correct route; portraits preserve editable fields; accepted overrides work; native options expose reasons; and main views render without missing image URLs.

Desktop/mobile layout, actual browser focus behaviour, and touch interaction still need a real-browser review. No live model service or Docker verification was performed.

Existing saves remain schema 39. Co-op is still deferred. This release implements the assignment strip and the requested portrait/unavailable-action pass. Pinned goals, a searchable action finder, richer context panels and broader crafting-form simplification remain future UI work.
