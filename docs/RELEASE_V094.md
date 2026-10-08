# v0.94 — Chapter 8 and repeatable patrols

## Chapter 8: The First Real Test

The castle stands in remote country, far from settled markets. Rhess and Velis connect an overdue delivery to organized theft. Sabine contributes an interpretation of the false toll mark if she is resident; recruitment is never forced.

Three story outings use one shared patrol system: trace the missing delivery, reopen the supply route, hold the castle approach. The scholar joins each story outing. Between outings, the previous story party must actually sleep at home after returning. The closing supper requires another rested night and an evening at home. No timer, off-screen attack or automatic treasury penalty.

Choose a sheltered detour (one escort encounter bypass, no reward for that encounter), settlement offer (guaranteed escort negotiation), or interception (+1 escort damage). Castle defense uses barracks and watchtower cover, an optional named home watch, and the actual Chapter 4 entrance improvement (reduces each raider group's starting vitality by 2). Training, attributes, loadouts and personal techniques affect the same encounters used by regular patrols.

The ending pays 20 crowns, grants the final story party 2 advancement points, and installs one permanent benefit: linked signals (+1 party cover), recovery stores (+4 provisions per complete repeatable patrol), or road contracts (+2 crowns per complete repeatable patrol).

## Field patrols

Unlocked by Chapter 7 completion, independently of starting Chapter 8. Select 1–4 willing residents, including the scholar or a companion alone. Everyone must be home with at least 3 vitality. Companions use their existing fieldwork agreements. One field patrol at a time; another ordinary expedition may use a disjoint party.

Supply road: one encounter, ordinary animals/thieves/bandits. Woodland circuit: two encounters, 5% mythical probability per encounter. Boundary ridge: two harder encounters, 10% mythical probability per encounter. Random encounters are committed and saved at departure. Loading an in-progress patrol does not reroll them.

One Advance travels outward; select an action and Advance once per exchange; one final Advance returns. Decisions wait safely. Withdraw at any unfinished stage. Defeat causes withdrawal, no permanent injury or equipment loss. An unresolved spell's paid inputs are refunded when withdrawing. Completed encounter rewards remain; incomplete encounters award nothing.

Weapons, Might/Athletics qualification, Measured force, protection/shields, Warded cover, group cover, Rhess's installed watchtower specialty, prepared personal techniques, and supported prepared combat/healing spells all have explicit effects. Personal techniques are once per encounter; advanced techniques require the equipped completed signature item. Spell components respect reserves. Enemies retaliate only when still standing; ice prevents retaliation. Peaceful animal/human resolutions require the appropriate score, except the agreed story settlement.

Rewards per resolved encounter: 3–10 crowns, 3–8 provisions, and 1 crafting material or 2 mythical enchanting components. Peaceful resolutions pay equally. First resolution of each enemy type grants every returning party member 1 advancement point, capped naturally at six enemy types per character; repeat patrols award resources only. The last ten reports are retained.

## Integration and usability

Party members are truly away: household work, ordinary rest, overnight sleep, equipment edits, conversations and other departures respect that absence. Returning characters are assigned Rest and restore their previous equipment mode. Arrival never counts as a night at home. The normal pantry already feeds travellers; there is no separate ration tax or hunger meter.

The existing Road watch task remains passive household work. Field patrols are explicit encounters. Adventures, Watchtower, Barracks, Command room, Home activity feed, phase tasks, Advance forecast, Help and Chapter 8 link to the same controls. Actor actions are grouped under expandable headings; costs, requirements and predicted retaliation appear before selection. One activity-feed entry represents each patrol.

Returning companions offer a bounded after-patrol conversation. If the scholar stayed home, their dialogue is a report, not a memory of having travelled together.

## Artwork and verification

Two generated landscapes are installed as optimized WebP assets: `static/assets/expeditions/patrol-road.webp` and `static/assets/expeditions/patrol-wilds.webp`. Their revised scenery shows isolated wilderness, no neighbouring castle or settlement. Built-in image generation prompts and optimization details are in `ART_V094.json`.

See `VERIFICATION_V094.json` for exact checks and pacing. Browser screenshots/layout inspection remain outstanding; automated UI tests are headless template/controller tests through the real game API.
