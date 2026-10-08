# v0.82 — Chapter 5 playability and balance

This release reviews the equipment-to-expedition loop introduced in v0.81. Existing item identities, prices, paid projects, artwork and save schema are retained.

## Fewer bookkeeping actions

The item work review can stow a piece from its loadouts and fund the selected job in one atomic confirmation. The preview lists displaced equipment, removed active effects, worker assignment changes, exact costs and any blockers. A failed confirmation leaves both equipment and funds intact.

After a job finishes, the work board links directly to its physical item. Each installed inscription offers **Review equip & activate for the field**. The same slot and four-channel rules apply; the preview exposes displacement before confirmation. Safe testing remains an explicit choice and never advances time.

Supply reviews show exact missing quantities and the cost to buy them without dipping into protected reserves. Individual purchases use the existing market action. Refresh the review after a purchase or another campaign change; stale confirmations remain blocked. Cancellation labels identify refunds clearly.

## Equipment now pays off in the early expedition

The rain-cut steps and jammed gate now require score 6 with the appropriate active enchantment, down from 8. The two continuous campaign tests verify that a normally progressed solo scholar can benefit from basic Sure footing and Measured force. The seal and sentinel retain score 8 and their safe ordinary alternatives. No success or reward is automatic.

Method cards name the equipped items that enable the chosen approach and state the phase saving against the ordinary method. Completed results retain those names, effects and approach scores in the Chapter 5 field proof notebook and return report. Savings compare the chosen method's normal cost with the ordinary route; they do not subtract travel or work abandoned under another method. Ordinary shield/disarm teamwork also records the actual equipment used.

The chapter guide recommends boots plus a staff or weapon for the first two proofs, while retaining other valid choices. Having an enchanting room already built no longer hides the need to learn Field calibration personally. Navigation retains the guide's destination, including a specific expedition site.

## Economy review

| Activity | Crowns | Work phases | Interpretation |
|---|---:|---:|---|
| One basic inscription, buying clay and thread | 16 | 2 | 8 service + 5 clay + 3 thread |
| Two introductory inscriptions | 32 | 4 | Exactly covered by the one-time study allocation |
| First supplied commission | +12 | 2 | Client equipment and inputs stay separate |
| Subsequent supplied commission | +8 | 2 | Matches base scholar copying at 4 crowns per phase |
| Strengthening with bought clay and thread | 20 | 3 | Three repeat commissions can fund it with 4 crowns left |

Prices and work durations stay unchanged. The practical improvement is fewer interface steps and a visible benefit from the first upgrades. The 32-crown allocation covers inscriptions and their components, not construction or prerequisite research. Reserved supplies can raise the amount that must be purchased, and the review displays that shortfall.

## Verification

See VERIFICATION_V082.json for exact focused test results and scope. New tests cover atomic combined actions, read-only previews, protected-reserve shopping costs, early upgrade payoff, named outcome evidence and the completed-work interface. Both earned-resource campaign routes through Chapters 1–5 are replayed with the recommended equipment and assert at least two field phases saved. A save created by the actual v0.81 archive opens unchanged, retaining partial work and accepted portrait bytes.

The 877-test / 53-UI-suite full regression record belongs to v0.81. v0.82 uses the targeted regression set listed in its verification report; those baseline counts are not presented as a new full rerun.

A fresh browser attempt returned ERR_BLOCKED_BY_CLIENT for the local preview. No browser protection was bypassed. Rendered desktop/mobile layout remains unverified. All 246 existing runtime images and five bundled content archives are retained byte-for-byte; no new illustration was needed for this interface pass.

## Upgrade

Stop the old server, extract this version, copy the complete existing data/ directory—including all campaign folders and accepted image files—into the new game folder, then run python server.py. Schema remains 60; no additional migration or save rewrite is required.
