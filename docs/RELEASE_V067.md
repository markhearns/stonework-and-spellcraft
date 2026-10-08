# v0.67 — A clearer home for a larger game

The interface now groups the game around six destinations: **Castle, Companions, Adventures, Magic, Workshop and Journal**. Search finds screens and resident characters. Secondary screens remain available under **All screens & settings**, and breadcrumbs show where a screen belongs.

## Home and companions

Home has a compact activity feed with separate decisions, work and invitation filters, four entries per page. Goals, household assignments and room visits have dedicated areas. Older castle guidance and social collections remain accessible in expandable sections. Invitations retain their existing optional, non-expiring rules.

The companion directory filters people at home or away. Each resident has one workspace with eight sections: Overview, Conversation, Relationships, Quests & stories, Development, Preparations, Appearance & wardrobe, and Personal space. Existing training, wardrobe, quest and conversation actions use their established controllers. Portraits and accepted artwork are reused.

## Stories and magic

The combined Journal searches personal quests, shared stories, known expeditions, remembered scenes and the chronological log. Filter collections by companion, and follow a record back to its existing activity. Remembered dates retain separate identities. Future scene prose is not exposed through the memory collection. The original journal and story tools remain accessible.

The Spellbook filters by practical use and by learned, prepared, usable-here or missing-supplies status. Preparation is distinct from current eligibility: location, actual party, learned principles, target and supplies still matter. Spell cards show casting time, component costs and readiness. Threshold fold shows instant eligible travel and the current field component cost, including an active anchor-circle reduction.

Current expedition decisions appear before optional conversations and supporting panels. Method cards present duration, costs and requirements together. The destination map can be expanded while travelling. Ordinary, specialist, teamwork, spell and ritual routes remain intact.

## Interaction and presentation

The existing engraved fantasy style now uses more consistent spacing, typography, panels, focus indicators and action cards. Small screens receive collapsible navigation, scrolling character tabs, larger touch targets and a persistent phase-control bar. Time still moves only through explicit Advance actions.

Rendering now reconciles existing elements instead of replacing the full interface for each update. Keyed controls retain identity, focused text selections are preserved, and expanded details and unfinished form fields are kept in local memory. Drafts are scoped by screen and character; successful campaign form submissions clear the associated draft. Pending-save retries retain that submission association. Drafts are not persistent across a browser reload.

Unavailable-action explanations include relevant routes to knowledge, preparations, stores, rooms or the current expedition. These links navigate; they do not perform the blocked action.

## Upgrade and verification

Keep the **complete existing `data` directory, including `data/assets`**, when replacing application files. Run `python server.py`. This release uses unchanged save schema **57** and changes no authored gameplay rules or save migration behavior.

Verification results are included in `VERIFICATION_V067.json` and `UI_REGRESSION_V067.json`. The connected JavaScript suites use the Python campaign store. New coverage exercises all resident tabs, navigation and journal search, filters, date identities, read-only browsing and spell timing. Reconciliation tests use a deterministic DOM tree double for focus, drafts, checkboxes, keyed reordering, replacement and screen isolation.

**No rendered browser inspection was available.** These checks verify templates, controllers and reconciliation contracts, not screenshot appearance or actual mobile-browser layout. The responsive styling still needs a visual browser pass.
