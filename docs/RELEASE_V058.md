# Development v0.58 — Different strengths, more ways through

Six attributes now underpin character development, expedition approaches, conversation alternatives, construction and casting. Existing expedition methods and the original conversation responses remain available with their previous requirements. New attribute qualifications apply only to added approaches.

## Character sheets

Open **Work & study → Character sheets**, or open a resident's character sheet from their portrait.

| Attribute | Main uses |
|---|---|
| Might | Lifting, leverage, hauling; Athletics strengthens ordinary staff attacks and building work |
| Dexterity | Agility, precision, delicate mechanisms; Artifice helps crafting, Channeling helps offensive casting |
| Vitality | Endurance routes; at 8, resting and receiving first aid restore one extra health |
| Intelligence | Scholarship, engineering, deciphering and reasoned social approaches; Channeling helps healing |
| Resolve | Concentration, magical control, sustained enchantments and rituals |
| Charisma | Diplomacy, precise compliments, negotiation, mediation and a creature-intimidation route |

Attributes range from 1 to 10. The founder and fourteen established companions each have a 30-point starting profile; companions have individual strengths rather than ancestry modifiers. Other generated or imported residents receive a neutral 5 in every attribute. Training adds one point for 3 advancement and 3 assigned phases, up to 10. Starting attributes cost no advancement. Retraining restores each person's own profile and releases only paid investments.

Scholarship, Artifice and Fieldcraft are joined by **Athletics, Diplomacy and Channeling**. All residents can train all six skills, including Fieldcraft without a personal-story prerequisite. Skill ranks remain 0–2, each costing 2 advancement and 2 assigned phases. Teaching can pass these skills between residents through the existing lesson system. Attributes do not automatically confer skill ranks.

At Intelligence 8, research/archive work gains one contribution; at Dexterity 8, crafting gains one; at Resolve 8, preparation gains one spell slot. Relevant perk attribute prerequisites are now 6; existing skill and affinity prerequisites remain. Completed perks stay learned.

## Clear approach scores

**Attribute + twice the relevant skill**, plus **2 for a capable present expedition helper**. The helper must have at least 6 in the same attribute/skill combination. Only one helper bonus applies. An incapacitated aqueduct companion cannot help. Household residents left at home never qualify an expedition route.

New expedition routes require 9; authored social alternatives require 8 and use the founder's own capability. These are deterministic requirements, not hidden dice rolls. The UI shows the calculation and explains unavailable alternatives. Looking at a choice does not spend resources, advance time or change a memory.

## 32 additional expedition methods

The Cinder aqueduct has **25 new methods** across all twelve obstacles. Each takes one assigned phase, uses no components and avoids injury. Existing ordinary, equipment, paid, risky and magical methods remain.

Examples:

- Lift the fallen counterweight with Might and Athletics, or build a compound lever with Intelligence and Artifice.
- Secure a crossing using Dexterity and Athletics, or rebuild the broken span with engineering.
- Negotiate a repair agreement with the caretaker, or demonstrate expertise using her diagrams.
- Lure the ember hound into a cooling flue, rather than fight it.
- Intimidate the briar stalker into retreat with a commanding warning shout, or distract it with thrown footsteps.
- Reconstruct an undead watchman's shift-ending formula and release it from duty.
- Slip behind a sentinel's guard arm and engage its service lock.

Four new methods also serve Rainward observatory, including recovery from a misaligned lens rack. Three serve the old service road. Their previous routes, rewards and ordinary methods are preserved. No reward is awarded early or twice.

Giant's grasp adds **3 Might** and Lucid sight adds **3 Intelligence** to matching additional aqueduct approach scores while charged. Choosing a boosted approach spends one charge. Their existing ordinary-action effects remain. Boosts do not become permanent attribute points or bypass spell learning, preparation and component requirements.

## 38 additional conversation responses

All fourteen personal opening scenes gain two authored alternatives. Ten resident-pair middle scenes gain one each. The original three responses in every scene remain. There are now **356 response options across the existing 106 conversations**.

Examples include distinguishing a correction from an interpretation with Mira, designing a reversible repair with Maren, helping Sabine give an unpolished but sincere compliment, practising a clear boundary with Sylva, and helping Mira and Brakka annotate the difficult hand position in a repair diagram.

High Charisma does not grant affection, rewrite personality or override a person's wishes. New approaches have specific authored responses. An accepted alternative records its actual wording, response, approach and score; subsequent callbacks and scoped dialogue context retain that memory. Final arc branches continue through the alternative's corresponding conversational intent. Already completed scenes are not reopened or rewritten.

## Work, magic and rituals

- **Building:** Might + twice Athletics of 9, or Intelligence + twice Artifice of 9, adds one work to funded headquarters construction, living facilities, housing and conservatory restoration. The bonus is capped at one, even if both combinations qualify. Forecasts show the actual capped work. It does not accelerate drills, training or specialist installations.
- **Ordinary attacks:** Might + twice Athletics of 9 adds one staff damage. Existing Giant's grasp damage can still apply.
- **Offensive casting:** Dexterity + twice Channeling of 9 adds one damage to a valid offensive hit. Immunities and invalid targets remain enforced.
- **Healing:** Intelligence + twice Channeling of 9 adds one healing to Mending light, both at home and in the aqueduct. Health is capped at 6.
- **Recovery:** Vitality 8 adds one health to the recipient's first aid and their own rest recovery, capped at 6. Health and the Vitality attribute have separate UI labels.
- **Enchantments:** Resolve + twice Channeling of 9 adds one charge to a caster's finite work enchantments and field boosts. Wayfinder's one survey briefing remains a single briefing. This never grants a second action.
- **Lasting rituals:** When both participants reach Resolve + twice Channeling of 9, a newly begun lasting ritual takes one fewer shared phase. Costs, knowledge, presence and assignments remain required. The selected pair's time is shown before commitment and saved with the project; existing unfinished rituals retain their agreed time.

Builders use innate expertise and active permanent-circle help before spending finite construction enchantments; a charge is preserved if it cannot contribute remaining work.

## Saves and upgrading

Schema **49** renames Insight to Intelligence, assigns the new starting profiles, preserves old attribute expenditure and earned high-rank benefits, adds the three new skills at rank 0, and translates unfinished Insight training. An old rank-2-to-rank-3 project still reaches its promised high-score benefit when completed. Reopening a migrated save does not repeat the conversion.

Stop the old server. Extract this release into a fresh folder and copy the entire existing `data` directory, including `data/assets`, before starting `python server.py`. The normal pre-migration database backup is automatic. Keep the old release and backup if you want to roll back. No offline time passes.

All existing artwork, including the 38 spell and ritual icons, is retained. This release does not change character portraits.

## Verification

**630 Python tests and 34 connected UI suites pass.** See `VERIFICATION_V058.json` and `UI_REGRESSION_V058.json` for the final automated results. Tests cover migration and saved retries, point accounting and retraining, all 25 new aqueduct routes and all 38 conversation alternatives, retained ordinary choices at low scores, companion presence, finite magic, building work, ritual timing, recovery, read-only previews and connected UI actions. Connected UI tests exercise templates/controllers against the Python store; they are not a visual browser-layout review.
