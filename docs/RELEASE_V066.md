# v0.66 — A party worth travelling with

Open **Beyond the walls** and select a destination. All core expeditions now accept the founder and up to three willing resident companions. Every authored companion can participate; resident characters from supported content packs can also travel under their existing fieldwork agreements. Public Workshop field trips retain their separate rules.

## Three new journeys

Complete Hearth wards research to reveal all three leads. Each journey has six obstacles, five methods per obstacle, and a final choice among three commitments: **18 obstacles, 21 decisions and 99 method choices** across the release. Each requires one outbound phase and one return phase. Nothing advances without an explicit action.

| Destination | Obstacles | Lasting discovery |
| --- | --- | --- |
| The monastery beneath the rain | Flooded court, submerged wheel, lamp-room fire, undead bell keeper, caretaker’s account, pinned bell cradle | The rainkeeper’s atlas, siphon model and memorial names |
| The frozen skybridge | Iced ascent, broken span, conductive sentinel, pressure vane, damaged weather log, paired signals | Survey rig, climbing tackle and weather log |
| The manor after the last dance | Enchanted doorkeeper, mirror corridor, echo dancers, blocked garden stair, staff ledger, unfinished farewell | Invitation cabinet, music roll and staff account book |

All finds survive every final choice. The chosen commitment is remembered in the return report and home conversation. It does not discard equipment or close another mechanical route.

## Five routes through every obstacle

- **Ordinary:** three safe phases, no attribute threshold, supplies, spell or companion needed. All three journeys are completable solo with minimum attributes and empty stores.
- **Specialist:** one phase. A present participant needs score 9 in the listed attribute plus twice the skill rank, with applicable help, specialization, practised teamwork, displayed legacy and field boosts.
- **Teamwork:** one phase. Two different present participants must meet the two listed role scores of 8. The selected workers are recorded.
- **Prepared spell:** one phase. A present caster must personally know the principles, have learned and prepared the exact spell, and pay its existing component costs once.
- **Field ritual:** two phases, one moon glass and one binding thread from unreserved stores. One present conductor must personally know both listed principles. The completed inscription records a permanent, specific change at that site. It is not an unlisted global production bonus.

The field rituals are additional routes; they do not replace the existing two-person household circles. Their duration is not shortened by haste or scouting.

Examples include Waterwalk and Undertide breath at the monastery, Fire lance and Arc bolt at the skybridge, and Silver suggestion and Mirror decoy at the manor. Dawn lance can break the undead keeper’s binding; patiently completing its memorial roll is equally valid. Magic has authored targets and outcomes. It never determines romance or turns a living character’s refusal into agreement.

## Support magic and honest timing

The new journeys also permit one-phase support casts of Mending light, Borrowed hour, Giant’s grasp, Lucid sight and Wisp scout. The caster and recipient must be present, and components are committed once.

Healing restores 3 vitality, or 4 with the existing active healer specialization, capped at 6. Strength and clarity provide +3 to matching scores for two qualifying actions. Haste shortens three ordinary obstacles by one phase; scouting shortens two and previews the next obstacle. Haste and scouting do not stack on a method. Existing home-prepared haste can also supply a charge. Method buttons show the actual shortened duration before selection, and Advance previews show the work that will resolve.

Field boosts end on returning home. Home-prepared work enchantments retain their normal remaining charges. Threshold fold carries the actual whole party, with the existing learned/prepared/component requirements and previously reached outbound destination restriction; it never completes fieldwork or advances castle projects.

## Party selection and unfinished commitments

The departure roster shows portraits, useful roles, prepared spells, current assignments and known unfinished projects for selected people. The detailed attribute/skill comparison remains available. Willingness is checked individually; membership alone is insufficient. Mira retains her existing archive-story prerequisite.

Travellers are genuinely away: their castle assignments stop, and their funded work stays saved. They return to rest until reassigned. Ordinary old destinations teach their survey principles to all actual returning companions. Existing multi-stage destinations use the expanded party for checks, rewards and return handling. The pavilion retains its authored trio-specific dialogue while allowing other willing travellers.

Completed obstacles and paid unfinished work survive retreat and reload. Original casters and ritual conductors must return to finish their paid method; original teamwork workers must remain qualified. A changed party can replace an unavailable method with an ordinary route, without refunding committed costs. Support casting similarly retains its original caster and recipient. Outcomes record actual contributors, including people who performed earlier phases before a retreat.

## Company along the way

Each destination has arrival, camp, credit and home conversations, plus a private exchange available for each of the fourteen authored companions. The collection contains **42 destination-specific companion remarks**, **14 personal camp openings reused with destination-specific framing**, and **seven authored companion-pair exchanges**. Actual shared household-story choices and established bonds can appear as callbacks.

Only present participants speak or receive relationship credit. No conversation spends a phase or supplies. A remembered scene cannot be farmed for additional bonds. Unshared conversations remain available at home after a completed return; private conversations need only the founder and that actual returning companion present.

Camp scenes include teasing, costume half-masks, ribbons, blankets and affectionate quiet moments. Romantic responses follow already-established mutual milestones; pausing romance retains the friendly choice. These scenes do not advance relationship stages. Intimacy remains non-explicit. No absent companion is assigned a private memory.

Actual journey memories feed dialogue context, wardrobe history, home greetings and personal-space mementos. Existing romantic greetings retain precedence.

## Bringing something useful home

Each completed return grants 3 advancement to each actual returning participant, 2 moon glass, 3 binding thread and practical knowledge: Water guidance, Field calibration or Clear instruction, depending on the destination. Rewards occur once. Partial returns grant no completion reward.

Display the recovered legacy in its restored room to activate its benefits. Displaying or storing it is explicit, reversible and free.

| Legacy and room | Expedition approach benefit | Ordinary character-quest support |
| --- | --- | --- |
| Rainkeeper’s atlas — Library | +1 Channeling | Water and search work: two phases |
| Skybridge survey rig — Workshop | +1 Fieldcraft | Crossing and lifting: two phases |
| Open invitation cabinet — Common room | +1 Diplomacy | Bargaining and ciphers: two phases |

A check gains at most one recovered-legacy point. These points do not improve castle training or ritual qualification. The two-phase quest duration does not stack with household rituals, lantern corners or shared-project support; the selected duration is saved with the method.

## Save compatibility and verification

Version 0.66 uses schema **57**. Migration adds empty journey records and preserves old single-companion and existing multi-companion expeditions, resources, assignments, stories and accepted artwork. The existing migration backup and request-id retry protections remain in place.

Keep the complete existing `data` directory, including `data/assets`, when replacing application files. No deployment or data replacement is performed by this release.

Detailed test results are in `VERIFICATION_V066.json` and `UI_REGRESSION_V066.json`. The focused journey tests exhaust all 99 methods and cover ordinary solo completion, all fourteen participants, component payment, changed parties, pending work, support charges, relationship gates, legacy benefits, migration and retry/reload.

UI checks execute the real JavaScript templates and controllers against the Python store. They are not rendered browser or visual layout testing. The previously documented browser limitation remains; no new successful browser inspection is claimed. Existing portraits and spell icons are reused; this release does not add destination paintings.
