# v0.117 — Creature challenges, combat magic and recruitment quests

## Creatures and progression

The bestiary now has 30 creatures. The Outer valley circuit opens after Chapter 7 and includes Owlbear, Rust beetle, Blink lynx, Cliff harpy and Will-o’-wisp. Their counters address holds, corrosion, shifting position, unstable footing and misleading light.

After Chapter 8, Deep quarry offers Basilisk and Runebound colossus; High crags offers Manticore and Wyvern; Flooded basin offers Marsh hydra. Difficult bounties use the same chapter gate. These encounters add stone stiffness, venom, aerial attacks, multiple heads, regeneration and removable ward plates. The encounter screen explains the rules, threatened characters, available counters, material costs and predicted results. Waiting never advances combat.

Ten creature samples support material use, contracts and research. Ordinary counter-actions remain available without the new spells or rare equipment. A field-remedy cabinet improves expedition first aid. The colossus can also yield a one-time maintenance clue after a successful return.

## Five rare accessories

Each recipe needs two of its specific difficult-creature drop, one silver ivy, one binding thread, the restored enchanting room, completion of Chapter 8, learned principles and six equipment-work phases. Cancellation returns the committed costs. Equip the finished item in its owner's **expedition accessory** slot to activate it; a stored or vault item grants nothing.

| Accessory | Crowns | Equipped benefit |
|---|---:|---|
| Basilisk mirror brooch | 90 | +2 cover and immunity to the basilisk's gaze |
| Manticore barb ring | 95 | +2 damage on damaging physical attacks and techniques |
| Wyvern antivenom locket | 90 | Venom protection and +2 healing received |
| Hydra heart charm | 105 | Restore 1 vitality after each committed exchange while conscious |
| Colossus ward talisman | 110 | +2 damage from damaging spells and +1 cover |

Healing is capped at 6 vitality. The regeneration charm cannot revive an unconscious wearer. These effects need no additional enchantment channel.

## Six combat spells

Learn and test each spell personally, then use a prepared slot. The new forms work in field patrols, creature bounties, recruitment quests and Chapter 8 combat. They do not add new methods to the older Cinder aqueduct encounter system.

| Spell | Casting supplies | Effect |
|---|---|---|
| Stoneguard | 1 porous clay, 1 binding thread | One selected member gains +3 cover now and for two further exchanges |
| Gust strike | 1 binding thread | 2 base damage, reduces retaliation force by 2, opens the next damaging action for +1; grounds wyverns and clears harpy imbalance |
| Binding snare | 2 binding thread | A solid living enemy loses 2 attack force now and for two further exchanges; does not capture anyone |
| Purifying light | 1 silver ivy, 1 moon glass | Heal a selected member by 1 and clear venom, stone stiffness, corrosion and imbalance before retaliation |
| Dispel ward | 1 moon glass | Remove up to two colossus plates, reveal wisps or track blink lynxes, and temporarily suppress physical creature armour |
| Chain lightning | 2 fireglass, 1 binding thread | 5 base damage, 7 against constructs; +2 against raider groups or a hydra; remove up to two colossus plates |

Active colossus plates still cap the current damaging hit at 1, even when that hit removes plates. Chain lightning's extra arcs represent linked parts or a raider group within the existing encounter; they do not create a multi-enemy targeting interface. New effects and remaining durations are visible. Previews spend nothing; a pending cast reserves supplies, and retreat refunds an unresolved cast.

## Two preparation rituals

Two different residents prepare each ritual at home. The conductor needs both listed principles and the partner at least one. A batch takes two shared phases, reduced to one when both meet the Channeling aptitude requirement. Pauses retain progress; cancellation refunds unfinished work.

- **Expedition warding:** 10 crowns, 2 porous clay and 1 binding thread. Every member of the next outgoing patrol gains +1 cover for its first three committed exchanges.
- **Antivenom preparation:** 8 crowns, 2 silver ivy and 1 porous clay. The next outgoing patrol receives two shared doses, each preventing one new manticore or wyvern venom application. Initial attack damage still applies.

One ready batch of each ritual waits for a valid departure. Remaining charges end on return or retreat. Prepare another batch for another patrol. These are consumable preparations, separate from permanent household circles.

## Recruitment through quests

Approving a new common-ancestry character establishes a fixed identity and a lead. After Chapter 4, choose a rescue or bandit quest and dispatch a real field party. A rescue ends with an optional invitation after returning safely. Named common neighbours use authored rescue leads; their occupations and identities remain intact.

Bandit quests require a free Quiet chamber before departure. Weaken the group to half vitality or less, then secure a surrender using one unreserved binding thread. Returning places the named bandit in the reserved chamber. Three conversations cover her account, restitution and future goals, with three player responses in each. Conversations occur at most once per phase and retain their transcript. Release is always a separate decision. A possible household invitation follows release and sufficient agreement; custody never grants membership. Ordinary visits, available beds and both parties' decisions still govern joining.

Eight generic illustrations cover Human, High elf, Dark elf, Drow, Catfolk, Wolfkin, Orc and Ogrekin bandits. The corrected Catfolk illustration has feline top ears and opaque side hair, with no visible human ear. No exotic ancestry is assigned a bandit recruitment quest. Bovinefolk replacement remains undecided, so no new Bovinefolk bandit content was added. Existing contacts and starting companions remain valid; Koharu keeps her local workshop introduction and exotic contacts retain their own arrival paths.

## Help, artwork and installation

Help explains counters, rare equipment, recruitment, casting and preparations. Cheats expose current materials and equipment, reveal the expanded bestiary and can intentionally bypass recruitment. There are 51 new optimized runtime images: ten creature portraits, ten thumbnails, ten materials, eight bandits, five accessories and eight spell/ritual icons. The separate source archive contains this release's 41 final full-resolution masters and prompts.

Extract the complete game ZIP into a clean directory. Preserve the previous `data/` directory if keeping a save. Run `python server.py`, stop any old server and hard-refresh the browser. Confirm v0.117. Schema 74 initializes the new records without granting quest completions. The distribution excludes live campaign data and source-art masters. No hosted deployment is included.

Verification uses Python rule tests, real committed patrols and the shipped JavaScript connected to Python game stores. See `VERIFICATION_V117.json` for results and scope. Artwork was visually inspected; rendered desktop/mobile browser layout remains unverified. Eris/Selene co-op remains deferred.
