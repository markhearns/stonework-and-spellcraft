# v0.105 — Creatures, peoples, bounties and rare materials

The bestiary contains 14 creatures and 21 ancestry references. Open **Adventures → Creatures and Peoples**, the Library, the Journal or a linked encounter. Creature entries include appearance, habitat, signs, behaviour, approach requirements, repeated attack patterns, spell damage and material uses. Names and illustrations are available as reference; reaching an encounter records a sighting. Resolving it completes its entry. After observing a creature, one assigned scholar phase of library study can also complete the entry. Browsing, waiting for an encounter decision and viewing Advance previews do not award discoveries.

The ancestry references use generic adult illustrations. They describe physical traits, accommodation, arrival routes and the existing training requirements. Named residents keep their individual portraits and identities. Raider encounters retain their thief or bandit role; a generic ancestry illustration does not change their combat statistics or imply that an ancestry is hostile.

## Creature encounters and bounties

All ordinary patrols and bounties use the same creature profiles. Marsh crossings and abandoned outbuildings add two patrol routes. Existing story opponent IDs remain supported, including patrols already underway in old saves. Each creature has a concrete peaceful approach with a displayed requirement. Successful peaceful and combat resolutions provide the same rewards.

**Adventures → Creature bounties** is a separate paid task, unlocked with field patrols after Chapter 7. Choose a request, review its client and reason, then dispatch one to four willing household members. Each request has one fixed creature encounter. Travel, encounter actions and return use the existing field-party rules. Payment occurs only after a successful return. Sample requests collect two rare components, deliver one to the client and leave one in stores. Clearance requests leave both in stores. Clients pay 14–28 crowns. Ordinary materials are also kept. Bounties do not provide food. Each request can be completed once per game day and has no deadline.

Household **Hunting** and **Foraging** retain their existing generic food production, yields and assignment rules. They do not select bestiary creatures or grant rare components.

## Rare materials and existing supplies

Every creature has a rare component with real advanced uses. These materials share the ordinary inventory, protected reserves, vault storage, sale controls and project refunds. Regular purchases and supply orders cannot obtain them. Their distinct properties prevent ordinary low-level recipes from consuming them. Successful patrol encounters recover one rare component; bounty contracts specify their larger collection and delivery quantities.

Existing supplies depend on the creature or its site: spiders provide ordinary silk spun into binding thread, hearth-ash hounds leave fireglass in their kilns, root mimics yield silver-ivy cuttings, and quarry or ruin encounters allow clay and moon-glass recovery. Entries explain whether a material comes from the creature, its habitat or recovered cargo. Drops appear in the bestiary, bounty reward description, return report and stores.

Rare components are required when strengthening supported enchantments to rank two, adding quiet mode to a rank-two inscription and upgrading signature refinements to rank two. Compatible components serve different magical functions; there is no universal material tier ladder. Equipment quotations select an available compatible component above reserves and name the exact committed materials. Cancellation returns the committed components and crowns. Already-funded older jobs finish with their original paid materials.

Three permanent late castle improvements also consume rare components:

| Improvement | Cost and work | Rare components | Effect |
|---|---|---|---|
| Warded watch network | 60 crowns; 4 assigned phases | 2 ward-stone chips, 2 old watch iron, 1 shed slate scale | +1 party cover; existing total cap of 3 remains |
| Controlled-heat enchanting bench | 70 crowns; 4 assigned phases | 2 tempered kiln cinders, 2 shed storm antlers, 1 lantern wing dust | +1 work per phase on enchantment strengthening, quiet-mode refinements and signature rank-two upgrades |
| Permanent infirmary recovery ward | 60 crowns; 4 assigned phases | 2 bridge moss, 2 grave silk, 1 shed wolf underfur | Rest at home restores +1 vitality per phase, capped at 6; food shortages still cap recovery at 1 |

Each improvement lists its room and personal principle requirements before funding. The watch network requires the watchtower, barracks and enchanting room. The bench requires the enchanting room and vault. The recovery ward requires the infirmary, enchanting room and vault. Each can be built once. Materials remain committed while paused and return on cancellation.

## Cheat, artwork and saves

The existing Cheats section has **Fill out the bestiary**. It uses the normal cheat enablement and modified-campaign record. It reveals all entries without granting resources, victories, sightings, recruits or story progress.

There are 35 new generated illustrations in the established antique engraving and coloured woodcut style. Entries and encounters reuse the same artwork. Runtime exports are 640 × 640 with separate 160 × 160 thumbnails, encoded as lossless WebP. Resizing reduces dimensions; encoding adds no further pixel loss. The optional source archive preserves exact full-resolution RGBA masters. No masters are included in the game folder or game ZIP. All 290 previous runtime images are unchanged.

Save schema 66 adds zero-count rare-material inventory and reserve entries. Bestiary and bounty history records are created when used. Existing campaign data, accepted artwork, funded work and in-flight patrols are retained. The server creates a schema-migration backup before upgrading an older database.

Stop the old server, extract this release into a clean folder, copy the complete `data/` directory from the old installation, and run `python server.py`. Keep the original data backup. See `VERIFICATION_V105.json` and `ART_V105.json` for checks and image details. Rendered browser review remains deferred; UI verification uses headless templates and connected action controllers.
