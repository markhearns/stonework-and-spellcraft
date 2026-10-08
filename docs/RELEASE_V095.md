# v0.95 — Combat, character builds and homecoming

## Readable tactical decisions

Enemies follow three-step attack patterns. Their next attack, target, force and cover penetration are visible before you choose. Patterns advance only when an exchange resolves. Reading, waiting or reloading changes nothing.

One action still takes one Advance. An ordinary guarded strike protects its actor. Protective personal techniques can intercept the announced attack using their own equipment and technique guard; an equipped shield or a prepared protective technique also enables a repeatable Cover action for the threatened ally. Control techniques reduce incoming force by 2 and create a +1 opening for the next damaging action. Healing takes place before retaliation, making an injured target safer in the current exchange. Defeating the enemy prevents retaliation.

These roles come from existing prepared techniques and gear. No additional character class, skill tree, combat point pool or role assignment was added. The build sheet identifies prepared roles and explains the new patrol applications. Other expedition rules retain their existing behavior.

The action preview and resolution share one calculation. It accounts for real targeting, interception, counterattacks, exertion, healing caps, cover penetration, elemental spell damage, signature refinements and lethal blows. Detailed calculations and resulting vitality are expandable. The portrait row selects one actor at a time, so all party members’ actions are not shown simultaneously.

## A signature piece that grows through use

After completing the existing fitting/proof/conversation request, equip the signature piece on patrol. Only resolved, rewarded encounters count, and the record is committed when the item and owner return. Unfinished encounters, bypasses and equipment left at home do not count. History follows the physical piece and its owner; transfer does not give another person its bonuses.

Two different enemy types unlock rank one. Four unlock rank two. Choose one refinement:

| Refinement | Effect per rank |
| --- | --- |
| Precision | +1 damage to damaging patrol actions |
| Shelter | +1 personal cover, including interception |
| Care | +1 healing from an existing restorative action; grants no new action |

Rank one costs 6 crowns, 1 binding thread and 2 assigned equipment phases. Rank two costs 10 crowns, 1 moon glass, 1 binding thread and 2 phases. Changing focus at the current rank costs 4 crowns and 1 phase. The enchanting room, unreserved components, available owner and companion equipment-work agreement are required. Refinement stows the piece; equip it again on completion. Cancellation refunds the ordinary funded costs. Only one refinement is active, and it does not consume an inscription channel.

The Armoury and character’s existing signature section show the history, requirements and exact costs. Existing names, materials, ownership, inscriptions and signature identity remain intact.

## Coming home

The compact homecoming card shows returned loot, current vitality, whether each person has slept since returning, and actual damage/healing/protection/control contributions. It links earned refinements to the owner’s Armoury.

“Set this returning party to Rest” affects exactly the reported party, preserves other paid projects, and consumes no time. “Prepare this party again” opens a reviewed selection, marks unavailable members and never departs automatically. Recent cards expire after two days or can be dismissed; reports remain available. Travel still does not count as sleep, and normal pantry consumption already covers travellers.

Each authored companion has a distinct opening line for occasional optional homecoming moments. A maximum of three new invitations per person cover protection, care and rare encounters. They neither expire nor farm affection or advancement. Reports distinguish whether the scholar joined the outing or stayed home.

## Verification and practical limits

152 distinct targeted Python checks passed, including 22 new refinement tests. Five headless UI/controller scripts passed, using the real API bridge for state persistence. Both earned Chapter 1–8 routes completed; an additional full-route run continued through ordinary signature fitting, real training, patrol-earned history, paid refinement and re-equipping. No cheats were used in earned progression tests.

The balance audit contains 84 fixed battle scenarios and is separate from earned playthroughs. See BALANCE_V095.md/JSON. Browser screenshots and rendered layout review remain outstanding. No new artwork was needed: the combat and homecoming views reuse existing character portraits, equipment icons and the corrected remote-wilderness route art.
