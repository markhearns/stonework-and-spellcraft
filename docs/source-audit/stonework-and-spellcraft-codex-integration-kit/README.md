# Stonework and Spellcraft — Codex integration kit

This kit accompanies seventeen generated expansion packs. It contains the controlling handoffs, the read-only prototype snapshot, the unchanged character-foundations dependency (original ZIP and an extracted copy), a portable standard-library content validator, and the actual structural validation reports.

The individual packs are complete content datasets. They are **draft-for-implementation**, not installed game features. The 319 mechanics records are review proposals, not an engine or executable effects. No runtime repository, UI, save migration, balance simulation, or gameplay test was available or executed here.

## Give Codex a pack

Use the public bundle for a convenient combined workspace, or extract this kit and the chosen pack ZIPs so their folders sit directly under `packs/`. The ZIP for each pack keeps its own named folder intact. Add all dependencies listed in its manifest. Read `CODEX-START-HERE.md`, then that pack’s `CODEX-HANDOFF.md`.

The public bundle contains all sixteen public packs plus this kit. Pack 13 is intentionally absent; keep its separate ZIP in a private workspace. A deliberate private validation workspace may include it, but ordinary public build and indexing paths must not.

## Validate content locally

Requires Python 3.10 or newer and the standard library only. From this kit’s root, with the pack folders under `packs/`, run:

```sh
python tools/validate_packs.py --packs packs --source reference --foundations dependencies/stonework-spellcraft-content-pack --report local-validation-summary.json
python tools/test_validator.py --packs packs --source reference --foundations dependencies/stonework-spellcraft-content-pack --report local-validator-selftest-report.json
```

The first command checks content structure and actual supplied references, and refreshes pack validation reports. Add `--no-write-pack-reports` to avoid that update. Exit status is nonzero on rejection. The second command exercises validator regressions in temporary copies without modifying the delivered packs. Private-only fixtures run only when the private pack is present. These are **content-validator tests**, not the sixty-four runtime acceptance scenarios in pack 16.

The validator is an offline review utility, not a hardened production import service. Codex must implement repository-appropriate typed parsing, authorization, transaction boundaries, migrations, and runtime tests rather than execute narrative fields as code. A null amount or duration means unresolved, not free, zero, infinite, or automatically successful.

## What is supplied

`reference/` contains all original numbered handoffs, the shared contract, the overview, and the baseline snapshot. `dependencies/` contains the unchanged foundation pack. `tools/` contains the reusable validator and its regression runner. `reports/` contains checks actually run on the full generated set. `PACK-INDEX.md` and `pack-index.json` list delivered counts and dependencies without revealing private premises.

The full delivery has 1,641 requested content records plus 319 mechanics proposals. The public bundle has 1,599 content records plus all 319 proposals. The separate private pack has 42 content records and no mechanics proposals.

## Known boundaries

Unknown costs and advanced effects still need design review. Some mechanics share one lifecycle proposal; narrative-only records intentionally have no proposal. Occupation 039 intentionally maps to null because no existing or new starter fits short storytelling without inventing unrelated abilities. Repeated continuity and consent safeguards are deliberate; semantic review is model-authored, not human acceptance or external originality clearance.

The baseline is a user-supplied snapshot captured 5 October 2026 UTC. Inspect the actual repository before relying on its current state; reconcile drift explicitly without silently changing these stable IDs or old saves.
