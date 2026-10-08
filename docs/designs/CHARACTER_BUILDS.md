# Individual builds — v0.29

Character sheets now connect underlying attributes, trained skills, magical affinities, practices, principles, equipment and perks. Names and all costs are provisional game balance, not D&D rules. The founder and every authored or reviewed resident use the same records and calculations.

## Attributes

All start at rank 1. Each added rank costs **3 advancement and 3 own learning phases**, with a maximum of 3. Rank 2 qualifies for relevant perks; rank 3 also grants a direct bonus.

| Attribute | Meaning | Rank 3 effect |
|---|---|---|
| Insight | Patterns and complex ideas | +1 research/archive work contribution |
| Dexterity | Precise physical control | +1 crafting work contribution |
| Resolve | Sustained magical attention | +1 personal spell-preparation slot |

These are game capabilities, not judgments about a character's intelligence, beauty, kindness, willingness or worth. No ancestry, age or generated occupation grants additional ranks.

## Affinities

All start at rank 0. Each rank costs **2 advancement and 2 own learning phases**, with a maximum of 2. Personally understanding one qualifying principle is required; household archive availability alone is insufficient. Rank 1 opens perk prerequisites. Rank 2 grants the listed personal casting bonuses.

| Affinity | Qualifying knowledge | Rank 2 effect |
|---|---|---|
| Light | Gentle refraction or Luminous copying | Luminous transcription +2 crowns; Glass clarification +1 moon glass |
| Growth | Steady growth or Water guidance | Root-song tending +1 silver ivy |
| Hearth | Steady hearth wards or Gentle preservation | Warm-twist binding +1 binding thread |

Affinities do not supply unknown principles, learn or prepare spells, replace materials, speed spell testing or create extra casting phases. Outputs are computed for the actual caster. Spellbook entries, room casting controls and phase forecasts expose the same effective output that resolution uses.

## Perks

Each costs **3 advancement and 2 own learning phases**, can be learned once, and is passive after completion. All require the named attribute at rank 2, skill at rank 1 and affinity at rank 1.

| Perk | Attribute / skill / affinity | Effect |
|---|---|---|
| Archive synthesis | Insight / Scholarship / Light | +1 research/archive work |
| Living methods | Insight / Scholarship / Growth | +1 silver ivy per Root-song casting |
| Patient hands | Dexterity / Artifice / Hearth | +1 crafting work |
| Glasswright | Dexterity / Artifice / Light | +1 moon glass per Glass clarification |
| Spell repertoire | Resolve / Scholarship / Light | +1 personal spell-preparation slot |
| Hearth weaver | Resolve / Artifice / Hearth | +1 binding thread per Warm-twist casting |

Perk and rank bonuses stack only where explicitly stated. Work bonuses do not increase copying commissions, accelerate learning, personal story work or signature-focus projects. Casting perks stack with their matching affinity; mandatory inputs are still paid. These six paths are an initial catalogue, not the full eventual progression/content scope.

## Commitments and retraining

The existing `trainingProjects` record holds attribute, affinity and perk work. Points are reserved when agreed, invested at completion, and released on cancellation. One primary assignment per person applies. Changing assignments pauses the project. A completed training phase cannot also resolve another primary job. Reading, saving, replaying a request or reloading grants no progress.

The one-phase retraining ritual resets added attributes, affinities and perks together with invested skill ranks and non-starting practices. It retains starting expertise, earned advancement, personally known magical principles, tested spells, possessions, identity and history. If the prepared spells would exceed the capacity after retraining, the player must explicitly put spells aside. Both starting and resolving retraining validate this; the game never silently chooses which spells to remove.

Resident training remains offered/agreed through the existing solo planning controls. Richer personal negotiations and actual external-player authority are still separate unfinished requirements.

## Persistence and validation

Schema 26 adds independent baseline build records without altering existing work, money, knowledge or earned points. Introduced generated candidates get the same baseline once. The v0.29 release also migrates to schema 27 for the mystery ledger.

Tests cover reserved/invested accounting, prerequisites, personal versus shared knowledge, all output combinations, real casting inputs/output, primary work budgets, pause/cancel, retry/reload, resident identity preservation, retraining preparation limits and migration. A connected headless UI playthrough trains an attribute, affinity, skill and perk, checks work effects, retrains and reloads. It is not rendered-browser QA.
