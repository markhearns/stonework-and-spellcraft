# Fieldcraft loop — v0.36

This release connects an existing expedition, a new research project, owned equipment, assigned work, and optional resident conversations. It remains a self-hosted Python/SQLite webapp; the new rules and construction guidance work without any provider.

## Play the loop

1. Complete the introductory hearth study and obtain Reference binding through the existing archive path.
2. Survey the old waterworks and return home. Observations are not recorded while still in the field. Returning early grants no discovery. Existing saves with the returned survey already satisfy this prerequisite.
3. At the research desk, choose **Field calibration**. Its lead researcher personally needs Water guidance and Reference binding. Funding costs 12 shared crowns; completion takes four research contributions. Existing research skills, preparation and tools can help.
4. Craft and claim a Scholar’s working folio or Maker’s alignment gauge under the existing recipe rules. Crafting knowledge remains Reference binding for the folio and Clear instruction for the gauge.
5. The intended inscription maker must personally understand Field calibration. Actual research contributors learn it on completion; other residents study it from the archive using the existing learning system.
6. Open **Focus & equipment → Personal working tools**. Choose the owner, expand the tool’s inscription, select a vessel and a binding component, and commit 12 crowns. Both components must be available above protected stock reserves.
7. Advance two phases with the owner assigned to inscription work. Prepare the finished tool, then assign matching research/archive or artifact work to receive the improved contribution.

The journey appears in the research desk, personal equipment and waterworks screens. Workroom notes and the phase forecast show unfinished inscriptions. Relevant next-step suggestions point to research, paused work or a waiting conversation.

## Exact upgrade rules

| Item | Permanent inscription | Benefit when prepared |
| --- | --- | --- |
| Scholar’s working folio | Cross-reference inscription | +2 assigned research/archive contributions, replacing the original +1 |
| Maker’s alignment gauge | True-measure inscription | +2 assigned artifact crafting contributions, replacing the original +1 |

Each item has one supported permanent inscription. Repeated upgrade attempts are rejected. Only one working tool is prepared per owner, and its bonus is separate from signature-focus bonuses. Learning, copying income, spell testing, personal stories and inscriptions do not receive the working-tool bonus.

The owner performs their own inscription using the existing inscription assignment. They cannot have simultaneous signature-focus and working-tool inscription projects. Work progresses by exactly one phase per Advance, without skill acceleration. Choosing another assignment pauses it; returning to inscription resumes it. Away owners do no household work. Residents at home can continue assigned work during the founder’s expedition.

Cancellation returns the exact committed crowns and components once, including after partial progress. Elapsed phases are not returned, no inscription or invitation is awarded, and restarting begins from zero. The item retains its identity, name, ownership and existing base benefit. Unfinished tool work must be completed or cancelled before ownership transfer. Completed inscriptions retain their maker and completion date after renaming, transferring and reloading; recipients may use the finished tool without repeating its construction study.

## Invitations grounded in completed work

Completing an inscription on a resident’s tool creates a non-expiring invitation from that maker. It remembers the item’s name at completion and survives later transfer. The household and equipment pages expose it.

Choose a technical conversation or a playful compliment, defer it, or bring it back later. Joining requires the founder and resident home. Authored responses grant no funds, materials, time, affection, knowledge or Resonance. Only a joined conversation enters the resident’s shared-memory context. Mira has a distinct teasing response; other supported residents currently share a bounded fallback response.

Optional model-written household scenes now receive relevant already-shared scene history. A group draft receives only memories shared by every participant, not one participant’s private conversation with the founder. This is limited context selection, not a general gamemaster memory engine.

## Offline spell construction guidance

The Spellbook compares the four implemented forms and displays:

- The exact personal casting output and scope limits.
- Required personal knowledge, where it comes from, and the required facility.
- Test cost (4 crowns), two assigned testing phases and component properties.
- Up to six complete component combinations available above reserves, accounting for repeated use of the same material.
- Missing funds, facilities, knowledge or other pending spell work.
- Existing designs and their current status, avoiding redundant suggestions.

Selecting a combination fills the manual design form; it does not save, spend, learn, prepare or cast. The normal server rules recheck the actual action. Guidance respects reserves when suggesting combinations; the pre-existing manually chosen spell-testing rules remain authoritative. Free-text model advice is still optional and bounded to the same supported forms. This release adds no arbitrary new spell effects or natural-language intent classifier.

## Save and validation

Schema 35 adds inscription project and invitation records plus the new research project. Existing equipment, identities, phase and resources are preserved. SQLite request IDs protect cancellation and other mutations against duplicate retries. Complete save backups include all new records.

The tests cover the actual expedition → research → crafting → inscription → prepared research effect, independent personal learning, pause/cancel/refund, migration and retries, ownership, away work, invitation rewards and privacy, and offline component guidance. Connected headless UI checks exercise the controls through Python/SQLite. Rendered-browser layout and live-provider generation remain unverified.

Expansion handoffs 01–04 retain their v0.35 read-only review support. No additional generated expansion pack was supplied during this release, and proposed mechanics are not automatically installed. Handoffs 05–17, broader inscription choices and general spell invention remain future work.
