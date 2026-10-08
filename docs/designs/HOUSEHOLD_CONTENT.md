# Pack-based household life — v0.34

The original character-foundations ZIP is included unchanged under `static/examples/stonework-spellcraft-content-pack.zip`. In About & saves, choose **Validate included full character pack**, inspect its report/content, and activate it. Importing does not automatically grant items, create residents, change outfits or perform scenes.

## Invitations and shared history

Open **Household → Open household life**, select a resident, and load the active pack. Select an interaction seed and read its actual narrative prerequisites. Record a short basis for each requirement and confirm that it reflects established play and willing participation. These are human-reviewed narrative notes, not executable predicates or mechanical unlocks. The application still enforces household membership, presence, participant counts, ancestry restrictions, hard conflicts and pack revision.

Compose an invitation to create a persistent draft. This offline composer preserves the seed and offers simple editable response scaffolding; it is not a connected autonomous scene-writing model. Review/refine the opening and every response, save revisions, then approve the saved text. Approval creates a waiting invitation. Joining selects one reviewed conversation direction, with no time, resource, advancement, affection or Resonance reward. A response beginning with “Decline” is visibly treated as a decline branch and leaves the invitation deferred without a shared memory. The separate Another time control also defers without expiry or penalty. Other directions are conversation topics, not automatically completed activities.

Remembered conversations retain their source, prerequisite notes, selected response, date and clothing snapshot. A group's actual shared conversation creates descriptive shared history. It does not automatically establish friendship, romance, consent to touch, jealousy or private knowledge. Dialogue and personal-story prompts include only a participating resident's own shared scenes, limited to eight recent records. Source possible developments remain labelled future possibilities.

Source and cast identify a stable invitation; the same group cannot repeatedly mint that invitation from the same pack. A campaign keeps at most 100 records. Invitations wait while people travel and do not expire if a pack is deactivated. No absent external founder is simulated.

## Clothing

Choose a delivered ensemble or a custom combination of delivered garments. Inspect components and anatomy notes; confirm suitable coverage and willingness. A complete look needs a dress or top plus bottom, has no conflicting layers/non-accessory slots, and must satisfy every garment's ancestry restrictions and source-trait conflicts. Fitting to the particular individual remains an explicit visual/narrative review, not a guarantee from tags.

Save a named style, then separately choose to wear it with agreement. At most 20 styles per resident; restore the established look at any time when home together. A worn style cannot be deleted until another look is chosen. The exact component records and source version are frozen into the style, so pack changes do not rewrite it.

These are cosmetic clothing configurations: no new equipment powers, currencies, inventory items, purchases or crafting outcomes. Wardrobe text is included as the current clothing in dialogue context. Existing portraits remain independently reviewed illustrations and may not show the selected text configuration; no automatic image generation/editing is claimed.

## Story structure

Select a compatible story-development pattern and document its prerequisite basis. It supplies structure to future personal-story drafts; the existing supported package still sets exact costs, work and rewards. Offline outlines use the pattern's question as a proposed notebook exercise. Model context receives the reviewed pattern and actual shared conversation history. Accepted stories keep the pattern snapshot even after a new pattern is chosen or cleared. New quest mechanics are not inferred from possible resolutions.

## Persistence and limits

Save schema 33 initializes empty scene/style/pattern records while preserving the active content pack, people, time, funds, projects and established history. Writes use the existing revision/request-ID transaction boundary. The old authored household scenes and Tamsin styling actions remain separate and compatible.

The supplied pack has 50 interactions and 25 patterns, all with plain-language prerequisites. They are not silently assumed true. Thirty occupations remain unmapped and are excluded from candidate selection; the new expansion handoffs include a dedicated mapping assignment. Whole ancestry/appearance bundles and adult ages remain subject to individual content review.

Verification: 381 Python tests and twelve connected headless UI suites pass. The full pack's counts/references and three candidate compositions per ancestry are tested. Scene review, decline/defer, no-reward invariants, source persistence, participant-scoped history, garment constraints, story-pattern snapshots and save migration have regression coverage. Browser rendering, live-provider generation, Docker runtime and real co-op agents remain unverified.
