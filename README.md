# v0.119 — Companion goals with a finished result

All 16 named companions now have concrete personal ambitions with four work stages each (five for Elowen), two authored responses at each stage, explicit success conditions, individual celebrations and two conversations about the finished result. Goals appear on Overview, Talk and Quests. Completed works remain in their associated rooms. Friendship is sufficient; romance is optional.

Zahra forges Emberline, Sabine recovers her necklace, Tamsin finishes a usable cookbook menu, and Elowen produces a consumable field kit. Velis establishes standing deliveries. The other goals end in identifiable books, tested installations, a festival, a tournament title or a completed handover. Merrin explains how a massless spirit can handle real objects by concentrating.

Earlier overlapping quests contribute completed work, and saved memories remain intact. Help explains costs, work, rewards and limitations. No text model is required. See [the companion goal guide](docs/COMPANION_GOALS_V119.md), [release notes](docs/RELEASE_V119.md) and [verification](docs/VERIFICATION_V119.json). Earlier release notes follow.

# v0.118 — Merrin, world recruitment and interface repairs

Restore the chapel to discover Merrin, an adult spirit companion. She has normal visit and household decisions, authored dialogue and remembered preferences, quests, friendships, three wardrobe tiers plus bathing artwork, romance, signature work and three field disciplines. Her visual appearance follows the generic Spirit reference. Both individual and all-companion Cheats include her.

Normal procedural recruitment now begins with a saved rescue or bandit report, not custom character authoring. Rare exotics have a 1% chance. Golems and spirits never appear in these encounters; dryads and nymphs may be rescued but never appear as bandits. All four elemental variants have separate rescue and bandit art.

All 30 creatures have challenge ranks. Expedition cards have location artwork, repeated room portrait icons are fixed, and the header day number has moved beside the phase indicator. Settings supports configurable API endpoints and the documented text/image request formats, including compatible local servers. Help and Cheats reflect these changes.

See [release notes](docs/RELEASE_V118.md), [companion recruitment](docs/COMPANION_RECRUITMENT.md), [verification](docs/VERIFICATION_V118.json), and `START_HERE.md`. Earlier release notes follow.

# v0.117 — Creature challenges, combat magic and recruitment quests

Ten creatures add five intermediate and five difficult encounters, illustrated bestiary entries, bounties, materials and visible counters. Difficult expeditions unlock after Chapter 8. Their five rare materials make five powerful magical accessories with distinct effects; each needs two of its specific creature sample, binding materials, learned principles and six equipment-work phases.

New common-ancestry arrivals require a completed rescue or a bandit capture-and-release quest. Rescue invitations are optional. Captured bandits use the existing Quiet chamber and three scripted conversation topics with multiple responses before a possible voluntary invitation. No instant correspondence creates a new common recruit. Existing contacts, starting companions and established story arrivals remain intact. Koharu keeps her local kitsune workshop meeting; exotic summoning and golem awakening retain their separate paths.

Eight generic bandit illustrations cover Human, High elf, Dark elf, Drow, Catfolk, Wolfkin, Orc and Ogrekin. No new Bovinefolk bandit content was added while its replacement remains undecided. Creature, material, bandit and accessory runtime art is optimized WebP; masters and prompts are in the separate v0.117 source archive.

Six new spells add targeted protection, cleansing, snares, wind attacks, ward removal and chain lightning to patrol combat. Two repeatable preparation rituals provide limited protection or antidote doses for one outgoing patrol. Costs, remaining durations and effects appear in combat previews and the Spells & Rituals reference. The Catfolk bandit artwork has been corrected to show only feline top ears.

See [release notes](docs/RELEASE_V117.md), [verification](docs/VERIFICATION_V117.json), and `START_HERE.md`. The in-game Help and Cheats use the current catalogue. Earlier release notes follow.

---

# v0.116 — Residents, accommodation and scripted solo play

Oni is now **Ogrekin** (ancestry ID `ogrekin`), a common ancestry reached through ordinary introductions. Kaede remains the same person; meet her through the valley glassworks after completing the first hearth-ward study. No summoning ritual is required.

One Ember chamber and one Quiet chamber replace the duplicate fittings. Profiles and the full castle map show bedroom and quarters assignments. Each ancestry has a small, clearly explained capability bonus.

Koharu (`koharu`), a slight-built dark-haired kitsune stage-prop restorer, replaces Maren while keeping the workshop connection. Her identity, dialogue, goals and artwork have been recreated. Koharu, Tamsin and Fenna, plus their generic ancestry illustrations, have only animal ears.

Solo recruitment, character creation, personal-story preparation and phase accounts work without an LLM gamemaster. Created residents have saved conversation choices grounded in their interests and values. Eris/Selene co-op remains deferred. The requested Bovinefolk replacement is awaiting the user's ancestry choice.

See [release notes](docs/RELEASE_V116.md), [solo narrative direction](docs/SCRIPTED_SOLO_V116.md) and `START_HERE.md`. Install the complete release, restart the server and hard-refresh. Earlier release notes follow.

# v0.115 — Artwork and interface corrections

Updated Iona and Zahra bathing portraits and Zahra’s third outfit. Fixed missing navigation-card artwork, uneven card image frames, the Prepared magic background and the Foundation ritual icon. Task explanations now name the missing work and link to its setup screen. Mira’s portraits appear beside room scenes. A full map covers 61 locations across five views connected by stairs and passages, with rubble, repair progress and hidden special rooms. Help and Cheats have been updated and verified.

43 Python tests and six connected UI suites pass; all 44 navigation cards resolve artwork in fresh and demonstration games. Rendered browser layout remains unverified. See [release notes](docs/RELEASE_V115.md) and `START_HERE.md`. Restart the server and hard-refresh after installing this complete release.

Previous release notes follow.

# v0.114 — Progression and Zahra

Zahra is now the smithy’s Djinn companion, with internal ID `zahra`, a new profile, revised dialogue and four completely recreated portraits. No Brakka save migration is included, as requested.

The opening teaches equipment and an actual practical spell. Chapter 2 needs one chosen undertaking; extra communal construction is optional in Chapter 3; Chapter 4 only requires dungeon care when you choose an escorted capture or parley. Local patrols open after Chapter 4, the foundation ritual chamber after Chapter 5, and Rhess can help in Chapter 7 as a guest. Chapter 9 now investigates the castle’s old survey rooms. Friendship traditions open at 60 bonding.

Two complete campaign routes pass with earned resources, no cheats and no food shortages. The Spells & Rituals reference and optional fade-to-black chamber ritual remain connected. All 391 unrelated artwork files are unchanged. See [current release notes](docs/RELEASE_V114.md) and `START_HERE.md` for installation. This archive has not been deployed to a hosted server; rendered browser layout remains unverified.

The sections below describe previous releases and their original rules.

# v0.113 — Conversations to return to

All fifteen companions have new multi-exchange conversations and later visits: **46 conversations, 115 exchanges and 329 specific response choices**. Residents remember the preferences you explicitly share with them, acknowledge uncertainty or privacy, and accept corrections without rewriting your history. Disagreements can remain open. Shared jokes, revised plans and optional traditions give later conversations something new to discuss. Eight resident pairs also get continuing conversations in which they make their own decisions.

Open **Companions → a resident → Talk → Conversations to return to** after her first personal disclosure in About. Each response saves immediately. Home invitations, room links, profiles and the journal use the same saved exchanges. Completing a conversation gives its relationship reward once; conversations spend no time or supplies. The foundation blessing applies to eligible gains.

**245 Python tests and 12 connected UI suites pass.** All 398 artwork files are preserved. Rendered browser layout and audio performance remain unverified. Preserve the complete `data/` directory, install the full release, restart and hard-refresh. Schema 71 upgrades automatically with a backup. This package includes Chapter 9 and the ritual chamber and has not been deployed to a hosted server. See [release and installation notes](docs/RELEASE_V113.md).

# v0.112 — Companion dialogue and meaningful choices

Companion conversations now give all fifteen residents clearer goals, values, interests and shortcomings. Personal disclosures and resident-pair conversations offer three specific player responses with different replies; travel conversations include a second platonic response. Existing saved conversations retain their wording.

The editorial pass replaces unspecified stories, missing explanations, interchangeable reassurance and several incorrect callbacks. Open a companion’s **About** or **Talk** tab to find the revised conversations. Disclosed goals and values also appear in her profile.

Preserve the complete `data/` directory when upgrading, restart the Python server and hard-refresh. Schema 70 is unchanged. This archive is the full game, including Chapter 9 and the foundation ritual chamber; it does not deploy to your hosted server. See [release and verification notes](docs/RELEASE_V112.md).

# v0.111 — Resident friendships that lead somewhere

Open **Companions → Resident friendships**, or follow the link on a resident’s bonding card. Seven authored pair stories and general activities for other pairs turn bonding into optional invitations, shared keepsakes, later callbacks and modest cooperation benefits during real work.

Milestones open at 10, 25, 45 and 100 bonding. A keepsake costs 4 crowns and one shared phase; completing it unlocks +1 cooperation when both residents do the same supported task, rising to +2 at 70 bonding. Invitations wait for your decision, and completed memories appear in both profiles and the keepsake’s room.

The quality pass covers the new friendships, Chapter 9, the ritual, saved games, conversation context, navigation and responsive styles. 141 Python tests, including two earned routes through Chapters 1–9, and seven connected UI suites pass. Rendered browser layout is still unverified because the browser download failed.

Preserve the complete `data/` directory, install, restart the Python server and hard-refresh. Schema 70 upgrades automatically with a backup. See [release, installation and verification notes](docs/RELEASE_V111.md).

# v0.110 — Beneath the Hearth

Chapter 9 follows the supply-road defense into the castle foundations. Trace the old connections, recover the operating instructions, restore the ritual chamber, and test its separate power supply and household connections. Each step records its findings; prior research can shorten the work. Open **Castle rooms & household → Foundation ritual chamber**, also available from **Magic** and the Chapter 8 conclusion.

An optional, consensual intimacy ritual with an established adult partner takes one shared phase and fades to black. It grants **+20% positive relationship gains for the following nine phases (three game days)**, including bonds between residents. The page shows eligibility, costs, progress, discoveries and exact blessing expiry. Renewing refreshes the duration without stacking the percentage. Completing the chapter does not require romance.

Preserve the complete `data/` directory, install this release, restart the Python server and hard-refresh. Save schema 69 upgrades automatically with a backup. This is the complete game package; it has not been deployed to your hosted server. See [release, installation and verification notes](docs/RELEASE_V110.md).

# v0.109 — Bonds between residents

Each resident now has a mutual bonding score with every other resident. Open a character’s **Profile** or **Relationships** tab to see portraits, levels, progress and recent shared activities; **Overview** shows their strongest connections.

Conversations and shared work, lessons, ritual work, leisure, meals, gathering and expeditions build bonds automatically through the existing activity controls. Your deeper character relationships remain separate. Save schema 68 imports existing recorded relationship history and creates an automatic migration backup.

Preserve the complete `data/` directory, install this release, restart the Python server and hard-refresh. See [release, installation and verification notes](docs/RELEASE_V109.md).

# v0.108 — Recovered artwork and the magic reference

Open **Magic → Spells & Rituals** for 133 illustrated reference entries with in-character observations, effects, requirements, costs, filters and links to the working controls. All 77 recovered images and Sylva’s new third outfit are integrated as optimized runtime assets.

Preserve the complete existing `data/` directory, install this release, restart the Python server and hard-refresh. Save schema remains 67. See [release, installation and verification notes](docs/RELEASE_V108.md).

# v0.107 — Portrait overhaul and expanded field guide

See [release notes and installation](docs/RELEASE_V107.md).

# v0.106 — Clearer actions and more useful space

A rendered desktop review of v0.105 informed this update: less repeated page furniture, objective-led Home actions, clearer room workspaces and spell learning, correct bestiary breadcrumbs and scroll restoration, accurate equipment-action labels, fewer duplicate portraits, and bestiary/bounty Help. Existing artwork is reused; save schema remains 66.

Run `python server.py`. Stop the previous process and preserve the complete `data/` directory before upgrading. The small patch can be overlaid onto v0.105; follow its `APPLY_UI_PATCH.txt`. Hard-refresh after restarting. Extracting into `public_html` alone does not run the Python server.

See [release and review notes](docs/RELEASE_V106.md) and [verification](docs/VERIFICATION_V106.json). Eight existing UI suites and one new regression suite passed. The revised v0.106 desktop layout, mobile layout and late-game rendered states still need review after installation. Build with `python scripts/package_game.py ../stonework-and-spellcraft-v0.106.zip`.

# v0.105 — Illustrated bestiary and creature bounties

Browse 14 creatures and 21 ancestry references in **Adventures → Creatures and Peoples**. Encounters reuse the guide’s illustrations and creature profiles. Creature bounties pay crowns and supply rare components for advanced enchanting, signature upgrades and permanent castle improvements. Suitable creatures also provide existing materials. Household Hunting continues to produce generic food.

The bestiary lists material sources, quantities and advanced uses. The Cheats section can reveal every entry. Regular suppliers do not sell rare creature components.

Run `python server.py`. Stop the old server and preserve the complete `data/` directory before upgrading into a clean folder. Save schema 66 creates an automatic migration backup. Existing artwork, paid projects and in-flight patrols are preserved.

The game includes 640-pixel illustrations and 160-pixel thumbnails in lossless WebP. Full-resolution masters are kept in the separate optional `stonework-and-spellcraft-bestiary-masters-v0.105.zip`; do not place that archive in the game folder. Build with `python scripts/package_game.py ../stonework-and-spellcraft-v0.105.zip`.

See [release notes](docs/RELEASE_V105.md), [verification](docs/VERIFICATION_V105.json) and [art details](docs/ART_V105.json). Rendered browser review remains deferred.

# v0.104 — Illustrated choices and clearer comparisons

Equipment reviews show what will be stowed or equipped, active enchantment changes and exact patrol equipment bonuses. Empty slots use muted equipment illustrations. Temporary effects show their spell, recipient, effect and remaining matching work phases or field uses.

Advance previews pair resource artwork with current totals, projected totals and changes, including provisions and Resonance. Project bars show current and expected progress. Consistent status icons mark ready actions, paused work, decisions and invitations. Room illustrations show construction, available conversations and the people actually present. Journal entries use known location or artifact art; the new Crafted artifacts filter lists current holdings.

Four new engraved display icons total 55,374 bytes. All 286 previous runtime images are unchanged. Full-resolution masters remain in a separate optional source-art archive; none are included in the game. Save schema remains 65.

Run `python server.py`. Keep the complete `data/` directory when upgrading. Use `python scripts/package_game.py ../stonework-and-spellcraft-v0.104.zip` to build an archive that excludes masters and campaign data. See [release notes](docs/RELEASE_V104.md), [verification](docs/VERIFICATION_V104.json) and the [art manifest](docs/ART_V104.json). Rendered browser review remains deferred.

# v0.103 — Clear status, fewer scattered panels and engraved icons

Home now groups the treasury, food and Resonance with direct links to their controls. Current projects show progress, working or paused status, requirements and resume buttons. Character summaries put field health and available advancement points beside the current task.

Trust, affection and respect each have an engraved icon, exact 0–12 value and labelled meter. The same relationship summary appears on Overview and Relationships, with the latest change, romance status and next invitation’s requirements. Scores never establish romance. Morning, afternoon and evening have icons and a visible current-phase marker.

The wording pass replaces loadouts with equipment sets, clarifies chapter projects and work points, and updates Help. Seven new icons use 128-pixel display copies totalling 89,600 bytes. Pixel-identical lossless masters are kept in a separate source-art archive and are not included in the game. All 279 previous artwork files and save schema 65 are preserved.

See [release notes](docs/RELEASE_V103.md), [verification](docs/VERIFICATION_V103.json), [art manifest](docs/ART_V103.json), [generation prompts](docs/ICON_PROMPTS_V103.json) and the [writing guide](docs/WRITING_GUIDE.md). Rendered browser review remains deferred.

Package builds use `python scripts/package_game.py ../stonework-and-spellcraft-v0.103.zip`. Only runtime artwork belongs in the game; keep source masters outside its folder.

# v0.102 — Clear next steps and less repetitive funding

Chapter funding now offers finite paid commissions with their exact payment, duration and material cost. Copying remains available and stops at the chosen treasury target. Unfinished commissions are resumed with their original payment and progress.

Chapters 5–8 identify the next research, funded work, field choice or rest requirement. Advance previews flag waiting patrol decisions; the shared drill shows its actual assignment requirements. Paused equipment jobs can resume from the project list. Equipment-priority dialogue states that it records a preference, while Chapter 8 continues to quote its permanent rewards.

Two fresh eight-chapter routes completed without cheats or food shortages. Total phases fell from 309 to 294 and from 297 to 285; copying fell from 81/80 phases to 26/23. Costs, rewards, work durations and save schema 65 are unchanged. All 279 bundled art assets are preserved.

See [release notes](docs/RELEASE_V102.md), [pacing review](docs/PACING_REVIEW_V102.json), [verification](docs/VERIFICATION_V102.json) and the [writing guide](docs/WRITING_GUIDE.md). Rendered browser review remains deferred.

# v0.101 — Clear instructions and conversations with substance

The text review replaces vague UI labels and empty replies with explicit actions, real explanations and distinct character voices. All 15 named companions have individual responses to completed work and personal invitations. Training, patrols, household follow-ups, quests and personal stories now give the details their choices promise.

The writing guide and optional generation instructions require plain English, purposeful dialogue and an actual answer to the player’s choice. Saved conversations and approved proposals keep their existing text. Save schema remains 65; game costs, rewards, gates and all 279 images are unchanged.

See [release notes](docs/RELEASE_V101.md), [writing guide](docs/WRITING_GUIDE.md) and [verification](docs/VERIFICATION_V101.json). The rebuilt ZIP is checked for complete extraction. Rendered browser review remains deferred.

# v0.100 — Work, field objectives and remembered experiences

All eight agreed refinements are included: varied external commissions, lasting companion improvements, practical spell conditions, patrol objectives, personal signature refinements, work routines, follow-up conversations and continued castle investigation with lamp restoration and an optional Resonance study.

New choices state their costs, duration, requirements and effects in plain English. Open **External commissions**, **Work arrangements** and **Practical companion projects** from Home. Objective jobs are in **Field patrols** after Chapter 7. Follow-up conversations appear in the activity feed and companion Relationships; the new investigations continue in **Castle mystery**.

Save schema remains 65. Existing campaign history, artwork overrides and all 279 bundled image assets are preserved. Stop the old server, keep the complete `data/` directory, install this version and restart with `python server.py`.

See [release notes](docs/RELEASE_V100.md) and [verification](docs/VERIFICATION_V100.json). Automated rules, controller checks and earned campaign routes have been exercised. Rendered browser review remains deferred.

## Previous releases

# v0.99 — Four character portrait revisions

Sylva, Velis, Rhess and Iona each have seven replacement illustrations: three standard portraits, three matching room overviews and one bathing portrait. The revised sets follow the Tamsin/Elowen engraving references with approachable adult faces and more natural proportions. Sylva retains celadon-green living skin and botanical leaf ears; her conservatory views place both bare feet on flagstones with contact shadows. Iona now has near-black hair, prominent dark horns and a visible spaded tail, with an alluring adult succubus design throughout.

Exports preserve the existing dimensions and image paths. Iona's outfit, bathing and new-contact appearance descriptions match the artwork. Existing campaign data and player artwork overrides remain intact; save schema remains 65. Saved identity descriptions are not overwritten.

Stop the old server, preserve the complete existing `data/` directory, install this version and restart with `python server.py`. See [release notes](docs/RELEASE_V099.md), [art manifest](docs/art-v099/manifest.json), [generation prompts](docs/art-v099/prompts.json) and [verification](docs/VERIFICATION_V099.json).

## Previous releases

# v0.98 — Fresh Sylva, Velis and Rhess artwork

All 21 portraits have been newly generated using Tamsin and Elowen as the style and quality references. This replaces the previous source artwork, rather than re-encoding it. Sylva now has celadon-green living-sapwood skin, a single pair of leaf ears and subtle natural woodgrain instead of vine-shaped skin markings.

Exports match the corresponding reference dimensions: standard portraits 1024×1536, room overviews 960×1440, and bathing portraits 768×1152. File sizes are optimized against the corresponding Tamsin/Elowen assets. Character identity, outfit progression and associated rooms remain consistent across each set.

Run `python server.py`. Preserve your complete existing `data/` directory. Schema remains 65. See [release notes](docs/RELEASE_V098.md), [art manifest](docs/art-v098/manifest.json), [generation prompts](docs/art-v098/prompts.json) and [verification](docs/VERIFICATION_V098.json).

## Previous releases

# v0.97 — Portrait compression fix

All 21 images for Sylva, Velis and Rhess have been rebuilt directly from their original 1024×1536 generated images. This release uses lossless WebP with no resizing. Every visible pixel and alpha value matches the source PNG, preserving the fine ink lines and handmade texture.

Comparisons at identical 768×1152 dimensions confirmed that v0.96's lossy compression damaged fine ink detail; the dimensions alone were not the problem. This quality correction keeps the same designs, outfits, image paths and game behaviour. The assets are intentionally larger. No sharpening, upscaling or new image generation is used.

Run `python server.py`. Preserve your existing `data/` directory. Schema remains 65. Read [release notes](docs/RELEASE_V097.md), [image manifest](docs/art-v097/manifest.json) and [verification](docs/VERIFICATION_V097.json).

## Previous releases

# v0.96 — Sylva redesign and handmade portraits

Sylva has a new adult dryad design: forest-green hair, amber eyes, leaf-shaped ears, ivory blossoms, budding twigs and delicate living woodgrain. All seven of her bundled portraits are replaced, with matching appearance and outfit descriptions.

Sylva, Velis and Rhess now share a more visible handmade engraving finish across their transparent outfit portraits, full-body room overviews and contextual bathing portraits. Their associated rooms remain the conservatory, supply office and watchtower. Exterior views show remote wilderness.

Run `python server.py`. Preserve your existing `data/` directory when upgrading. This artwork release keeps schema 65 and the existing gameplay systems. Read [release notes](docs/RELEASE_V096.md) and [art verification](docs/VERIFICATION_V096.json).

## Previous releases

# v0.95 — Combat roles and signature growth

Field patrols now show each enemy’s next attack and its target. Protective techniques intercept for allies, control weakens attacks and creates openings, and healing happens before retaliation. Choose an actor by portrait; each action previews its exact effects, with calculations available on demand.

A completed signature piece records the enemy types it has faced while equipped. Return from two types to unlock Precision, Shelter or Care; four types unlock rank two. Paid refinement uses the existing equipment work board and the same physical item. No replacement material tiers or new talent tree.

The homecoming card shows party recovery and contributions, earned refinements, and a reviewed way to prepare the same party again. Fifteen authored companions have bounded optional moments after notable patrol contributions or mythical encounters.

Run `python server.py`. Keep your existing `data/` folder when upgrading. Schema remains 65; optional fields initialize on use. Read [release notes](docs/RELEASE_V095.md), [balance notes](docs/BALANCE_V095.md), and [verification](docs/VERIFICATION_V095.json). Browser-rendered layout review remains outstanding.

## Previous releases

# v0.94 — The First Real Test & field patrols

Chapter 8 is a separate story after Chapter 7: investigate a missing delivery, choose a route plan, escort supplies and defend the castle approach. Three outings and required overnight breaks give the household time to recover. Conclude with supper and choose a permanent patrol improvement.

Repeatable field patrols unlock as soon as Chapter 7 concludes. Send one to four household members, including companions without the scholar. Encounter hostile animals, thieves, bandits and rare griffins or ember hounds. Equipment, personal techniques, prepared combat spells, retreat, injuries and return rewards share the existing character and resource systems.

Open **Adventures → Field patrols** or the **Watchtower**. Chapter 8 also appears on Home. Read [release notes](docs/RELEASE_V094.md), [pacing and verification](docs/VERIFICATION_V094.json), and in-game Help → Field patrols & Chapter 8.

Run `python server.py`. Preserve your existing `data/` folder when upgrading. Schema remains 65; new optional records are created when first used. No live save or credentials are included. Browser-rendered layout review remains outstanding; automated controller and game-state checks are included.

## Previous releases

# v0.93 — A clearer daily rhythm

Home now offers evening rest, morning links back to paid work, and bounded earning goals for chapter projects. Companion Overview shows actual room and activity, while the activity feed makes room for optional conversations. Old return notices no longer stay on Home indefinitely. Projects and Advance preview reuse one forecast.

Both seven-chapter routes retain their original durations; no prices, wages, construction times or expedition times were changed. Read the [pacing audit](docs/PACING_V093.md) and [release notes](docs/RELEASE_V093.md).

Run `python server.py`. Preserve your complete `data/` folder when upgrading. Schema remains 65. See `docs/VERIFICATION_V093.json` for targeted gameplay and UI integration checks. Browser-rendered review remains outstanding.

## Previous releases

# v0.92 — Companion portraits and bathing outfits

Fifteen unique companions now have automatic bathing outfits for personal time in the pool, sauna and hot springs. Each uses newly generated, barefoot, two-piece cloth bathing wear. The outfit follows the character’s actual location and restores their normal appearance when they leave or return to work. It never replaces a saved wardrobe choice.

Companion portraits now resolve correctly after recruitment. Each Overview shows the companion’s associated room, exact improvement benefit, requirements and installation status. Authored ages vary from 20 to 25. Veyra and her associated game content and images have been removed; shared household stories now use remaining companions.

Run `python server.py`. Preserve your existing `data/` directory when upgrading. Schema 65 updates the five revised authored ages; there is no Veyra save migration. See [release notes](docs/RELEASE_V092.md) and `docs/VERIFICATION_V092.json`. Browser-rendered layout review remains outstanding.

## Previous releases (historical counts)

# v0.91 — Clearer words, better help

Revised interface instructions, requirements and character conversations make the game easier to understand. All 64 personal companion scenes now have concrete situations and scene-specific choices. **Help** provides 20 searchable topics with links from the relevant screens. **Cheats** now includes instant recruitment for one or all 16 unique companions, provisions, current rooms, unified equipment, advancement and healing. See [release notes](docs/RELEASE_V091.md).

Run `python server.py`. Preserve your complete existing `data/` directory. Schema remains 64; an actual v0.90 save retained its exact state. Automated gameplay and UI integration results are recorded in `docs/VERIFICATION_V091.json`. Browser-rendered layout review remains outstanding.

## v0.90 — Time together

All 16 named residents now have four repeatable romantic scenes and four one-off closeness milestones: **128 new scenes**. Open **Relationships → Time together**. Scenes progress from early affection to private, non-graphic evenings, with fresh choices, meaningful pacing, remembered moments and no farmable rewards. See [release notes](docs/RELEASE_V090.md).

Run `python server.py`. Preserve your complete existing `data/` directory. Schema remains 64; v0.89 saves retain their state. Targeted verification is recorded in `docs/VERIFICATION_V090.json`. Browser-rendered visual review remains outstanding.

## v0.89 — A build of their own

A focused **Loadout / Personal paths / Training** workspace now serves the whole cast. Your scholar and all 16 named residents have **51 paths and 153 talents**, with effective-stat previews, direct slot replacement, and saved builds that restore equipment and talents together. See [release notes](docs/RELEASE_V089.md).

Run `python server.py`. Preserve your complete existing `data/` directory. Schema 64 creates an upgrade backup. Automated gameplay and UI checks are recorded in `docs/VERIFICATION_V089.json`; browser-rendered layout review remains outstanding.

## v0.88 — Personal character paths

Rhess, Kaede, and Sabine now have 27 personal talents across nine paths, limited field loadouts, signature-equipment gates, enchantment interactions, and repeatable training-yard exercises. See [release notes](docs/RELEASE_V088.md). Keep your existing `data/` folder when upgrading.

## v0.87 — The First Patrol

Chapter 7, Rhess the dragonkin watchkeeper, the restored watchtower and two connected expeditions are playable. Evening wind-down and overnight recovery make returning home a clearer part of the rhythm. See `docs/RELEASE_V087.md` and the measured seven-chapter flow audit in `docs/PACING_V087.md`.

Run `python server.py`. Preserve your complete existing `data/` directory. Schema 62 creates an upgrade backup. Browser screenshot review remains outstanding.

## v0.86 — Character artwork consistency

Audited all 90 resident illustrations; replaced 36 assets to correct footwear, soften selected adult faces, and give Velis three genuine transparent full-body portraits. See `docs/RELEASE_V086.md` and `docs/CHARACTER_ART_DIRECTION.md`.

Run `python server.py`. Preserve your complete existing `data/` directory. Schema remains 61.

## v0.85 — The Roads We Keep

Food, hunting/foraging, optional replenishment, Chapter 6, the Supply Office and Velis are playable. See `docs/RELEASE_V085.md` for controls, balance, resident content and the cohesion review; `docs/VERIFICATION_V085.json` records validation.

Run `python server.py`. Preserve your complete existing `data/` directory. Schema 61 creates an upgrade backup and grants a one-time food buffer. Rendered browser review remains outstanding. Earlier release entries below are historical.

## v0.84 — Prepare, venture, return

A unified party preparation checklist connects actual equipment, field enchantments, vitality, spells and supplies. Current encounters identify actors and combined component costs. Per-visit return receipts connect findings, expenses, equipment contributions and companion follow-ups. See `docs/RELEASE_V084.md` and `docs/VERIFICATION_V084.json`.

Run `python server.py`. Keep the complete existing `data/` directory. Schema remains 60; older in-flight trips receive explicitly partial receipts. Rendered screenshot review remains outstanding.

## v0.83 — UI audit and simplification

Clearer navigation, a quieter home page, fewer repeated research and equipment controls, context-aware item editing, and two new engraved navigation icons. See `docs/RELEASE_V083.md`, `docs/UI_AUDIT_V083.md` and `docs/VERIFICATION_V083.json`.

Run `python server.py`. Preserve the complete existing `data/` directory. Schema remains 60. Rendered browser acceptance remains outstanding. Earlier entries below are historical.

## v0.82 — Chapter 5 playability and balance

Equipment work can now stow and fund in one reviewed transaction; finished inscriptions can be equipped and activated together for the field. Reviews show missing components, reserve-aware purchase costs and assignment changes. The first watch-road upgrades now reach useful early thresholds, with named equipment and score evidence saved in the field notebook. See `docs/RELEASE_V082.md` and `docs/VERIFICATION_V082.json`.

Run `python server.py`. Keep your complete existing `data/` folder when upgrading. Schema remains 60. The local browser preview is still blocked; rendered layout is unverified.

## v0.81 — Arms of Our Own

Unified nine-slot equipment, 30 ordinary equipment designs, eight useful enchantments, personal signature requests and a playable fifth chapter are implemented. Run `python server.py` and open the address printed by the server. Start with **Equipment → Review starting equipment**; Chapter 5 opens after Chapter 4’s closing review.

Keep the **complete existing `data/` directory** when upgrading. Schema 60 creates a migration backup and retains existing names, inscriptions, paid work and accepted artwork. See `docs/RELEASE_V081.md`, `docs/EQUIPMENT_V081.md` and `docs/VERIFICATION_V081.json`. Browser-rendered layout remains unverified.

Earlier release notes below are historical.

## v0.80 — Opening campaign review

Connected Chapters 1–4 reviewed; preservation-study guidance repaired, Chapter 3 disabled reasons restored, and completed chapter summaries compacted. See `docs/RELEASE_V080.md` and `docs/CAMPAIGN_REVIEW_V080.md`. Preserve the complete existing `data/` directory. Rendered browser review remains unresolved.

## v0.79 — Companion overview portraits and splash layout

42 new room-specific, full-body portraits; equal overview columns; viewport-filling landscape. Kaede now has a fit, busty hourglass figure with subtle muscle definition. See `docs/RELEASE_V079.md`. Preserve the complete `data/` directory when upgrading.

# Stonework and Spellcraft — v0.78

**Keeping the Hearth** adds Chapter 4: a service-door intrusion by Sabine, the established vampire engraver, followed by training, barracks, entrance defenses and a working dungeon. Capture introduces the actual containment and separate recruitment systems. Campaigns that already know her keep their history.

Sabine gains a dungeon specialty, an additional personal quest and resident interactions. Six new optimized illustrations complete all 14 authored expedition destinations and remain visible during journeys.

Run `python server.py`. Preserve your **complete existing data directory**, including `data/assets` and every campaign subdirectory, when upgrading. Schema remains **59**; no live campaign data is bundled.

Read [release notes](docs/RELEASE_V078.md), [Chapter 4 and Sabine](docs/KEEPING_THE_HEARTH.md), [artwork prompts and paths](docs/ART_V078.json), and [verification](docs/VERIFICATION_V078.json). Earlier release notes below describe their historical versions.

---

# Stonework and Spellcraft — v0.77

Three connected chapters are now playable: **The First Hearth**, **The House Takes Shape**, and **Room to Grow**. Establish a home, complete all three working-room undertakings, then plan and restore a lower living wing with bedrooms, a communal room and a specialist facility.

The new estate plan compares actual costs, recognizes existing rooms, shows dependencies and named builders, and preserves paid work when priorities change. Chapter 2 now requires all three additions and a shared closing scene. Earlier completed work counts.

Run `python server.py`. Preserve your **complete existing data directory**, including `data/assets` and every campaign subdirectory, when upgrading. Schema remains **59**. This archive includes the previously pending artwork and logo; it contains no live campaign data.

Read [release notes](docs/RELEASE_V077.md), [Chapter 3 and chapter continuity](docs/ROOM_TO_GROW.md), and [verification](docs/VERIFICATION_V077.json). Earlier release and checkpoint records below describe their historical versions.

---

# Stonework and Spellcraft — v0.74

All previously missing cards in Castle rooms & household, Magic, Adventures and Workshop now have artwork. Seven new engraved card illustrations accompany a subtle monochrome castle landscape in the header, section banners, title screen and mobile phase bar. New assets are size-optimized WebP; previous artwork is unchanged.

Run `python server.py`. Preserve your complete existing **data directory, including data/assets**, when upgrading. Schema remains **59**. See [release notes](docs/RELEASE_V074.md), [art and optimization details](docs/ART_V074.json), and [verification](docs/VERIFICATION_V074.json).

---

# Stonework and Spellcraft — v0.73

The game logo now appears in the top-left navigation area. Textured backgrounds extend to the phase/Advance header, panels and dialogs. Full-body companion portraits are centered within correctly sized frames, and character names align with surrounding sentence text.

Run `python server.py`. Preserve your **complete existing data directory, including data/assets** when upgrading. Schema **59**, gameplay and all existing artwork are unchanged. See [release notes](docs/RELEASE_V073.md) and [verification](docs/VERIFICATION_V073.json).

---

# Stonework and Spellcraft — v0.72

Resident-led headquarters work: explicitly agree workers, fund construction or production in separate facilities, and let at-home residents continue while your scholar travels. Individual jobs support pause, resume, exact refunds, phase previews and saved work arrangements. A new engraved game logo appears on the title screen.

Run `python server.py`. When upgrading, preserve your **complete existing data directory, including data/assets and every campaign subdirectory**. Schema **59** creates the normal pre-migration backup and keeps all existing project costs, progress and artwork. All 152 previous bundled art files remain byte-for-byte unchanged; the logo is one new asset.

See [release notes](docs/RELEASE_V072.md), [verification](docs/VERIFICATION_V072.json), and [asset inventory](docs/ASSETS_V072.json). The earlier release history below remains historical.

---

# Stonework and Spellcraft — v0.71

Portrait cleanup: exactly three portraits for each of fourteen companions, with 23 replacement illustrations, clearer outfit progression and character-specific designs. Brakka retains youthful adult orc features with connected lower tusks; Sylva has a distinct botanical body.

Extract into a fresh folder and run `python server.py`. Schema 58 and relationship unlock rules are unchanged. See [release notes](docs/RELEASE_V071.md) and the [asset guide](docs/ASSET_GUIDE.md).

---

# Stonework and Spellcraft — v0.70

Organized, optimized artwork: purpose-based asset folders, WebP delivery, correctly sized spell and UI icons, and no bundled source-art duplicates. Runtime artwork shrinks from **153.2 MB to 39.3 MB**; all 38 spell icons together shrink from **75 MB to 633 KB**.

Extract into a **fresh application folder** so old asset directories do not remain on disk. Run `python server.py`. Gameplay and schema 58 are unchanged. See [release notes](docs/RELEASE_V070.md) and the [asset guide](docs/ASSET_GUIDE.md).

---

# Stonework and Spellcraft — v0.69

Progressive profiles and everyday castle life for all fourteen companions: 42 personal disclosures, 14 individual initiatives and seven three-part NPC relationship arcs. Open a companion’s **Profile** tab to learn more as trust and mutual relationships develop.

Run `python server.py`. Preserve your **complete existing `data` directory, including `data/assets`**, when upgrading. Schema **58** migrates existing saves with an automatic backup. See [release notes](docs/RELEASE_V069.md) for disclosure rules, content and verification limits.

---

# Stonework and Spellcraft — v0.68

A playability polish pass: clearer phase feedback, a next-phase work panel, per-companion tab scroll restoration, direct conversation invitation targeting, retained spell recipients and decision-first expedition screens.

Run `python server.py`. Preserve your **complete existing `data` directory, including `data/assets`**, when upgrading. Save schema **57** is unchanged. See [release notes](docs/RELEASE_V068.md) for verification details and the remaining rendered-browser review.

---

# Stonework and Spellcraft — v0.67

A unified interface for the expanded game: six main destinations, a calmer Home, companion workspaces, a searchable stories-and-quests journal, practical spell filters, clearer expedition choices and responsive navigation.

Run `python server.py`. Keep your **complete existing `data` directory, including `data/assets`**, when upgrading. Save schema **57** is unchanged. See [release notes](docs/RELEASE_V067.md) for the changes and browser-verification limitation.

---

# Stonework and Spellcraft — v0.66

Take up to three willing companions on core expeditions. Three new adventures add 18 obstacles with ordinary, specialist, teamwork, spell and ritual routes, optional camp conversations, actual-party memories and practical discoveries for the castle.

Open **Beyond the walls** after completing Hearth wards research. The departure roster shows preparation and unfinished commitments. All fourteen authored companions can participate; solo routes remain available throughout.

Keep your complete existing `data` directory, including `data/assets`. Schema **57** preserves existing saves and adds empty journey records. See [release notes](docs/RELEASE_V066.md) for the 99 methods, support magic, party rules and verification limits.

---

# Stonework and Spellcraft — v0.65

Open **Household stories & connections** from Home or a character sheet. Twelve intersecting stories give all fourteen companions two or three central roles, with 36 ensemble scenes, 72 authored choices, shared projects, remembered NPC bonds and optional relationship-aware personal follow-ups.

Keep your complete existing `data` directory, including `data/assets`. Schema **56** preserves current progress and adds empty ensemble-story records. See [release notes](docs/RELEASE_V065.md) for story casts, project rules, artwork limits and verification.

---

# Stonework and Spellcraft — v0.64

Open **Character customization** from Home or a character sheet. Seven tabs bring together appearance, illustrated and descriptive wardrobes, atomic saved preparations, earned specializations, mentorship, preferences, relationship-aware invitations and personal spaces.

Keep the complete existing `data` directory, including `data/assets`. Save schema **55** adds empty customization records and preserves previous progress. See [release notes](docs/RELEASE_V064.md) for exact mechanics, artwork limits and verification.

---

# Stonework and Spellcraft — development v0.63

The forgotten lantern pavilion: travel with Mira, Tamsin and Iona, a smaller party or alone; solve five obstacles in multiple ways; share relationship-aware journey scenes; and bring home a useful common-room legacy. See [Release v0.63](docs/RELEASE_V063.md).

Run `python server.py`. To upgrade, stop the old server and copy the complete existing `data` directory (including `data/assets`) into this release. Saves migrate to schema **54** with an automatic database backup.

## Earlier release history

## New in development v0.58

Six attributes (1–10), six trainable skills, distinct companion strengths, 32 added expedition methods and 38 added dialogue responses. Original choices remain. Attributes also contribute to building, casting, recovery and rituals. See [Release v0.58](docs/RELEASE_V058.md) for rules, examples and safe save upgrading.

# Stonework and Spellcraft — development v0.57

**106 new authored conversations** deepen life with all fourteen companions: personal arcs, friendships between residents, reactions to actual gameplay, everyday banter and household gatherings. Your choices are remembered in later dialogue. Invitations wait, and later chapters open after time passes.

Open **People → Life together → Conversations & friendships**, or follow an invitation on Home. See [the v0.57 release notes](docs/RELEASE_V057.md) for content, controls and save compatibility.

Run `python server.py` and open the local address it prints. When upgrading, stop the old server and copy your complete existing `data` directory, including `data/assets`, into a fresh release folder. Save schema **48** preserves earlier progress and creates the normal pre-migration backup. The v0.56 magic overhaul and all 38 spell/ritual icons are included.

---

# Stonework and Spellcraft — development v0.56

This release adds **30 authored spells**, **eight lasting rituals**, **38 individual icons**, the multi-approach **Cinder aqueduct** expedition, and a second pass connecting magic to research, crafting, construction, recovery, travel and personal work. Spell effects are fixed in code; a runtime LLM does not decide their powers.

See [the v0.56 release notes](docs/RELEASE_V056.md) for the full spell catalogue, ritual effects, gameplay audit and upgrade instructions. Start with `python server.py`, then open the local address printed by the server. Existing saves upgrade to schema **47** with the normal database backup. Copy the entire existing `data` directory, including accepted artwork, when moving to a fresh release folder.

---

# Stonework and Spellcraft — v0.55

## v0.55 — life together

Open **People → Life together** for four personal chapters for every authored companion, shared room activities, conversations between residents and specialist follow-ups. All fourteen routes can progress through the starting common room and library after recruitment. Wardrobe invitations now have individual dialogue and a choice of response. Earlier choices remain available to reread and are carried into optional generated dialogue only for the person who shared them.

There are 56 personal chapters, 16 scenes between residents, 33 specialist conversations and 13 types of shared room activity. Specialist conversations follow planning, installation and a later visit to the improved room. Their practical benefits still come from the existing funded improvements. Activities can be revisited; only the first distinct activity counts towards wardrobe progress. These optional scenes do not advance time, alter assignments or grant free resources.

Open **People → Work arrangements** to save up to eight named sets of current assignments. Review changes before restoring one; an unavailable assignment or absent saved participant blocks the whole change. Later arrivals keep their current work. **Projects & next improvements** now supports more funded-project types and shows assignment changes before resumption. Use **Preview Advance** to inspect what the next phase will do.

Save schema **46** preserves existing progress, selected outfits, accepted artwork and older conversation memories. Stop the server, extract this release into a fresh program folder, copy your complete existing **data** directory (including **data/assets**) into it, and run `python server.py`. The server creates its normal pre-migration database backup. No offline game time elapses.

All 121 bundled artwork files are unchanged from v0.54. See `docs/RELEASE_V055.md` and `docs/VERIFICATION_V055.json` for checks and scope. Browser/layout verification remains deferred as requested.

---

# Stonework and Spellcraft — v0.54

## v0.54 — illustrated wardrobe progression

The fourteen authored adult companions each have three distinct portraits: their original look, a relaxed look, and a bolder flirtatious look. Find **People → Companion wardrobes**. One remembered shared scene opens the relaxed invitation. The daring invitation needs three distinct remembered scenes, including one new scene after accepting the relaxed invitation. Accepting an invitation unlocks the look; selecting it is a separate, free action while both people are home. Earlier outfits remain available. Repeat clicks and passing time do not unlock outfits.

This release integrates 28 alternate portraits, 10 restyled defaults, the Old service road illustration, the castle arrival illustration and eight labelled navigation icons. Four recent default portraits are retained. Clothing previews and disabled-action explanations are included. Save-owned artwork overrides and the older shawl/ensemble controls remain supported.

Upgrade with the server stopped into a fresh program folder; retain the complete existing `data` directory. Schema 45 initializes wardrobe progress without replacing accepted art, possessions, relationship memories or work. The server backs up older databases before migration. Old bundled portrait URLs remain aliases to the new defaults.

Rendered desktop/mobile verification remains outstanding: the included browser review runner cannot launch because Chromium is not installed in this environment. See `docs/RELEASE_V054.md` for the final automated check results.


The artwork is now part of the game: six expedition illustrations, fourteen exact object icons and five character portraits. Catalogue illustrations appear on their exact records and owned instances; saved overrides take precedence. The complete quarry/cistern return replaces the partial weather-screen return.

Tamsin’s two portraits now depict her as Catfolk. Elowen has her high-elf portrait. **Nyssara is a drow enchanter**, with equipment inscriptions and a practical enchanting focus. **Sylva is a green dryad**, with leaf veins, bark features and clothing made from leaves, vines and bark. The identity migration retains history, earned knowledge, possessions, relationships and accepted image overrides.

All sixteen public packs match their bundled source files; 1,599 content records, 319 mechanical adapters and 3,595 foundations records are accounted for. Reference/production records remain reference/production tools rather than invented gameplay effects. The separate private mystery pack remains reserved for opt-in future campaigns and is not injected into current castle canon.

**562 Python tests and 29 headless UI suites pass.**

**Save schema 44.** Stop the server and keep your entire **data** directory, including **data/assets**, when upgrading into a new program folder. Run `python server.py`. Existing saves receive the normal pre-migration backup. Co-op remains deferred.

See **docs/DEVELOPMENT_V053.txt**, **docs/PACK_AUDIT_V053.json**, **docs/ART_INTEGRATION_V053.json** and **docs/verification-v053.json**. Rendered desktop/mobile verification remains outstanding; automated checks are not screenshot approval.

---

# Stonework and Spellcraft — v0.52

This release also adds **24 optional resident scenes**, phase routines, shared research reviews, a persistent four-stage branching **Old service road** expedition, and **Projects & next improvements** with safe resume controls. Specialist installation requires residency and presence; completed improvements remain permanent.

The supplied **weather-screen icon** is integrated unchanged. The cistern-filter icon and the Quarry shelter/Ridge cistern scenes are still missing from the partial art return. Character and room artwork remain unchanged; five pending portraits have a separate external-art handoff. No artwork was generated here.

**557 Python tests and 28 connected headless UI suites pass.** Rendered desktop/mobile verification remains outstanding because the browser download failed. No screenshots, real keyboard-focus or touch QA are claimed.

**Save schema 43.** Stop the server, extract into a new program folder, copy over your entire **data** directory (including **data/assets**), then run `python server.py`. Existing campaigns, funded work and accepted artwork are preserved; migration creates the normal database backup. Co-op remains deferred.

Read **docs/DEVELOPMENT_V052.txt**, **docs/verification-v052.json**, **docs/ART_INTEGRATION_V052.json** and **docs/BROWSER_REVIEW_STATUS.md**.

---

# Stonework and Spellcraft — v0.51

**Weatherproofing the castle** adds two expeditions, two studies, two practical artifacts and six optional saved reflections. Open **Castle notebook** through **Go directly to** or the Library; Home introduces it after your first lantern. The whole chapter can be completed solo through ordinary play.

Rooms now describe the current phase and show who is actually home and working. **Household work** explains personal knowledge, skill effects and funded projects. Expedition destinations use a responsive card grid with accurate unlock requirements, and opening crafting guidance explains reserved stock.

**536 Python tests and 27 connected headless UI suites pass.** Rendered desktop/mobile verification remains blocked by unavailable browser binaries. An isolated Playwright review runner is included; screenshots and human visual sign-off remain outstanding.

**Save schema 41** preserves existing campaigns, funded work and accepted artwork. Keep your complete **data** directory, including **data/assets**, when moving to a new program folder. Run `python server.py`. No artwork was generated or changed; co-op remains deferred.

See **docs/DEVELOPMENT_V051.txt**, **docs/verification-v051.json** and **docs/BROWSER_REVIEW_STATUS.md**.

---

# Stonework and Spellcraft — v0.50

The new antique engraving artwork is integrated: **34 room illustrations across 57 individual room slots**, plus **23 restyled character, scene and interface assets**. All headquarters spaces have pictures, and Ember/Quiet chambers now support individual artwork review. Eighteen superseded files have been removed; old bundled URLs resolve to the current artwork.

This release also includes the completed room activity navigation and fresh-game guidance described in v0.49 below. Imported artwork and save data are preserved; character restyles retain the established identities. Save schema remains **40**, and co-op remains deferred.

**526 Python tests and 26 connected headless UI suites pass.** Artwork has been visually inspected. Rendered desktop/mobile application verification remains outstanding; see **docs/BROWSER_REVIEW_STATUS.md**.

Upgrade into a new program folder and carry over your complete **data** directory with the server stopped. This avoids keeping obsolete assets from earlier ZIP overlays. Do not delete **data/assets**. Run `python server.py` as before.

See **docs/ARTWORK_V050.txt**, **docs/ART_RESTYLE_V050.json** and **docs/verification-v050.json** for the changes, artwork prompts, cleanup and verification details.

---

# Stonework and Spellcraft — v0.49

## Work inside the room

Headquarters activities now share a persistent room header and activity navigation. Enter the Library to research, switch to letters or study, and return to the room’s facilities without losing your place. Other spaces reuse their established crafting, equipment, stock, garden, expedition and household controls. Existing systems remain usable before optional room upgrades; bonuses still require construction.

## A clearer route through the opening

Home offers an optional route from your first lantern through the kitchen, warm washroom and service wards, then a returned expedition discovery and a local introduction. It explains treasury shortfalls, copying income, committed crafting materials and separate visiting/membership decisions. Headquarters construction and jobs now appear in the detailed Advance preview.

Keep your complete **data** directory. Save schema remains **40**. Existing saves, accepted artwork, character identities and the current antique engraving aesthetic are preserved. No new images were generated; the v0.48 artwork handoff remains valid. Co-op, combat and autonomous guards remain deferred.

See **docs/USABILITY_V049.txt** and **docs/verification-v049.json**. Rendered desktop/mobile verification remains outstanding.

---

# Stonework and Spellcraft — v0.48

Current aesthetic: antique engraving–inspired fantasy illustration. The exact user-approved prompt is saved in **docs/AESTHETIC_PROMPT.txt** and the room-art handoff (updated 5 October 2026). This documentation update does not replace any artwork.

## A headquarters made of useful rooms

Open **Estate → Headquarters rooms**, the Home shortcut or **Go directly to**. The new catalogue consolidates small room concepts into **22 multi-use headquarters spaces**, including a library/archive, common room/tavern, workshop/material library, warehouse, smithy/armoury, enchanting room, command room, infirmary, training yard, guard barracks, underground living quarters, dungeon ward, late-game vault, hot spring, sauna, pool and chapel.

Rooms show their uses, costs, work phases and exact prerequisites before funding. Construction and room jobs use your scholar’s assignment and explicit Advance; pause keeps progress, cancellation refunds committed costs. Advanced facilities require relevant completed rooms, personally learned principles and, for the vault, returned discoveries. Ordinary chapel use requires no magical knowledge or prescribed faith.

The workshop improves core artifact work. The smithy produces metalware, blades and armour; the enchanting room improves working-tool inscriptions and can ward forged armour for public fieldwork. The command room offers a one-survey briefing. Two finite training drills award advancement. The vault separates stored goods from usable stock, including individually owned public objects without changing identity or art. Social and bathing activities offer optional saved reflections. Combat and autonomous guard behaviour are not implemented.

Underground services and barracks unlock three separately fitted bedrooms: a private lower suite, four-bed lower chamber and four-bed guard dormitory. These are accommodation alternatives within the existing main-castle population limit, not automatically recruited residents. Existing bedrooms, personal belongings and specialist-care access remain intact.

## Upgrade and artwork

**Save schema 40** adds the room records. Keep your complete existing **data** directory: older databases receive an automatic pre-migration backup. Accepted character and room artwork is preserved. No images were generated or replaced; new spaces display labelled placeholders and accept individually reviewed imports. Co-op remains deferred.

The separate **room-art-handoff-v0.48.zip** supplies 34 independent illustration briefs, exact asset targets and the six existing castle-room reference images. Repeated bedroom families use representative images while retaining individual room override slots. Ember/Quiet chamber studies are explicitly marked for later illustration integration.

**517 Python tests and 25 connected headless UI suites pass.**

See **docs/HEADQUARTERS_V048.txt**, **docs/ROOM_ART_HANDOFF_V048.txt** and **docs/verification-v048.json**. Rendered desktop/mobile verification remains outstanding; headless checks are not visual-browser QA.

---

# Stonework and Spellcraft — v0.47

## Choose who arrives

New fresh campaigns now open **Your character** before the arrival scene. Choose a name and adult human age (18–120), with optional pronouns, appearance notes and a descriptive background. You can leave the default identity and placeholder in place, save the details and continue. Backgrounds give no stat bonuses or class restrictions; the arrival still lets you choose why you came and what caught your attention.

Your identity stays attached to the same `founder` character, possessions and progress. Names and ages are read from the saved profile, including optional NPC dialogue context. Private background notes are not automatically passed to NPCs. Existing saves continue normally and can use **Settings & artwork → Your character**; the arrival also has a link back to character setup.

## Three portrait options

- **Placeholder:** start immediately and add an illustration later.
- **Import:** choose a PNG, JPEG or WebP up to 6 MB, inspect the preview, then accept it. Previous artwork remains recoverable.
- **Generate:** save your details, configure an image-capable OpenRouter model and key in the separate image-provider settings, then explicitly request one portrait draft. The request uses the displayed appearance brief. Generation may incur charges and never accepts an image automatically. Review and accept the result yourself. You can also copy the brief into another image-generation app and import its result.

Image-provider settings are independent of text-draft settings, disabled by default, and server-wide. Keys stay on the server and are excluded from per-campaign save backups. A whole-data-directory backup includes settings files; protect it accordingly. A normal text-only model cannot produce a portrait.

Generation requests have saved identifiers: checking/retrying the same request does not issue another provider call. Recover saved drafts after reload. If a request is still processing after a server interruption, you can explicitly put it aside before requesting another; this does not cancel or refund provider usage. A portrait generated before the campaign changed must be downloaded/imported for fresh review or regenerated. Accepted portraits and previous accepted versions are included in restorable save backups; unaccepted draft image files are not guaranteed by those backups.

## Compatibility and verification

Save schema remains **39**. Old saves are not forced through setup. No bundled artwork was generated or changed, and the separate artwork handoff remains independent. Co-op is still deferred.

**501 Python tests and 24 connected headless UI suites pass.** The provider transport, preview, acceptance and retry flows were tested with controlled responses, not a live paid account. Rendered desktop/mobile verification remains outstanding due to the documented browser-access blocker. See **docs/CHARACTER_CREATION_V047.txt** for coverage and details.

Keep your complete existing `data` directory when upgrading. Run `python server.py` as before; no additional package is required.

---

# Stonework and Spellcraft — v0.46

## An arrival before the interface

New fresh games now begin with a short illustrated arrival. You are an independent scholar of practical magic, coming to make a home and workplace in the old castle. Choose what brought you here and what first catches your attention. The two reflections are saved as you go, can be resumed after reload, and give no bonuses or restrictions. You can enter without making the remaining choices.

Before opening Home, **Getting settled** explains the first research and lantern, comfortable living areas, expeditions and returned discoveries, willing residents and suitable beds, copying income, assignments and explicit phase advancement. **Journal → Your arrival & getting-settled guide** lets you reread it. This is authored development prose, without revealing or establishing the castle’s hidden history.

Existing saves continue normally; the arrival record is initialized only for newly created fresh campaigns. Demonstration saves keep their existing opening.

## Find the next step

- **Go directly to** reaches individual systems without opening a category first. On narrow screens, **Navigate** expands the menu; desktop secondary tools sit under **At your desk**.
- Home puts the opening guidance first and responds to active projects, paused research, insufficient research funds and travel.
- **Advance** names the next phase and day. Home and This phase show expected work, paused projects and the next forecast. A required field choice explains why Advance is unavailable.
- Phase actions name what they do. Deliveries list the exact goods given and rewards received. Existing revision checks and normal action rules still apply.
- Four additional optional scenes cover understanding hearth wards, settling into the wing, arranging the first archive and welcoming an actual resident. There are now eight solo milestone scenes, each with two reflections. They never expire or spend time/resources.

## Upgrade and checks

Keep your existing **data** directory. Save schema remains **39**. No artwork was generated or replaced; all bundled artwork and source-content bytes are unchanged. Co-op remains deferred.

See **docs/USABILITY_V046.txt** for verification results, scope and the outstanding rendered desktop/mobile review. Run `python server.py` as before. Choose **New game → Fresh beginning** to see the arrival.

---

# Stonework and Spellcraft — v0.45

## Phase filters and small moments at home

**This phase** now offers All, New this phase, Ready now, Paused work and Invitations filters with counts. Required expedition choices remain visible under every filter. The Home summary stays unfiltered. Filters are local to the current browser session; they spend no resources and do not change the save. Keyboard focus returns to the selected filter after rendering.

Fresh campaigns gain four optional scenes under **People → Household work → Small moments at home**: your first warming lantern, the restored conservatory, a discovery brought home from the old waterworks, and a completed neighbour request. Each offers two authored reflections, saves your choice and adds it to the journal. Scenes have no deadline, phase cost or resource reward. Eligible scenes appear on the phase board; their links open the relevant scene directly. Existing campaigns started with New game can access milestones already reached. Demonstration campaigns do not receive these scenes.

Public-pack material records now use material category artwork instead of the generic book fallback. Bespoke artwork from the separate art handoff can be integrated later.

Keep your existing data directory when upgrading. Save schema remains **39**; the optional scene memory is created when first used. No new art generation or model service is required.

Verification: 479 Python tests passed. See docs/USABILITY_V045.txt for the UI check results and remaining visual-review limits.

---

# Stonework and Spellcraft — v0.44

## Painted interface artwork

The interface now uses generated PNG artwork for core item/material icons, navigation, the castle emblem, dark-paper texture and restrained botanical framing. The first lantern and full workshop share the same object artwork. Ordinary panels stay quiet and readable; repeated character mentions within a paragraph share one portrait.

The artwork is bundled locally under `static/assets/ui-v044/`. No image-generation service is needed when playing. Public-pack records without bespoke illustrations use explicitly labelled category art. See [v0.44 art direction and asset notes](docs/ART_DIRECTION_V044.md) for the prompt manifest, coverage and visual-QA limits.

## Goals and a clearer next phase

Use **Goals** to pin up to three objectives. Home keeps each next requirement within reach, including the full route to Fenna's introduction and eventual agreed membership.

**Preview Advance** shows current assignments, expected progress, completions and shared resource changes without changing your save. Phase results now lead with completions and follow-up actions; routine details are expandable.

Click a character portrait for a compact detail panel, expand room/character artwork, or follow material and principle links from the core workshop. The workshop also offers **Show what this maker can craft now**. Navigation remembers your scroll position during the session.

See [v0.43 guidance and interface notes](docs/GUIDANCE_INTERFACE_V043.md) for exact coverage and verification limits. Desktop/mobile visual QA is still outstanding.

## Portraits and unavailable actions

A compact household strip shows portraits and current assignments, with shortcuts to character sheets. Portraits accompany character mentions and selected-person controls; activity cards reuse room artwork. Characters without accepted art have labelled placeholders, and the scholar now has an illustration-review slot.

Click or focus and activate an unavailable button to see its explanation. Hover shows the same reason. Native disabled fields and options have adjacent help. Local introductions list exact blockers and link to the next step: Fenna requires a discovery brought back from the fern nursery, Brakka requires the conservatory, and Maren is initially available.

See [the v0.42 interface notes](docs/VISUAL_INTERFACE_V042.md) for coverage and remaining UI work. Browser layout and touch/focus QA remain outstanding.

## This phase: the place to find your next actions

Home now includes **This phase**, also available in the sidebar and beside Advance. It gathers current field choices, paused work, ready deliveries/installations, new contacts, invitations, recently completed public-pack work and affordable next projects.

- **Do this** executes a currently valid task immediately. Project descriptions show costs and assignment changes; work itself still requires Advance.
- **Review & choose** opens the relevant screen when a choice, discussion or content review is needed.
- **Put aside this phase** removes an optional task from the current list; you can restore it. It returns next phase if still relevant. Required expedition choices cannot be hidden.
- After Advance, the phase summary names newly available tasks and opens the board with one button. **New this phase** markers are saved with the campaign and survive reloads. Completed or no-longer-valid tasks disappear automatically.

Task buttons use the normal revision-checked action endpoint. Readiness is checked against a detached state using the real rules, and checked again when you execute the task. Browsing never spends resources, advances time or calls a model.

## Solo household features

**People → Household work** lets you record a recruited resident’s willingness to tend the garden or accompany expeditions. Agreeing a role does not assign work. Agreements can be ended at home without penalty. Mira retains her existing authored offers.

Your scholar can tend the conservatory alone. A willing resident can tend it while the scholar travels. One gardener produces the normal harvest per phase; a root tender supplies its existing smaller fallback harvest when unstaffed.

**Beyond the walls → Expeditions** now offers a field-companion selector for actual residents with agreed fieldwork. Their home work pauses. Their own skills, prepared practices and equipment contribute; returned knowledge, advancement and agreed money shares go to the actual party. Early returns give no unfinished rewards. Both return unassigned, with paused projects preserved.

A fresh household can also celebrate its completed living wing, alone or with its actual residents. The optional, non-expiring scene records who was there and spends no phase or resources.

Extract into **stonework-and-spellcraft/** and run `python server.py`. Keep your existing data directory when upgrading. Save schema **39** adds solo-role records and phase notices; older saves receive a migration backup. Co-op remains deferred. All sixteen public packs and their original source archives remain included.

See [the release notes](docs/SOLO_PHASES_V041.md). The v0.40 fresh-start instructions remain below.

---

# Stonework and Spellcraft — v0.40

## Start here

1. Extract the ZIP. The folder is **stonework-and-spellcraft**.
2. Open a terminal in that folder and run `python server.py` (or use your existing Docker setup).
3. Open `http://127.0.0.1:8080/`. The title screen offers **New game** and **Continue a saved game**.
4. Leave the starting point at **Fresh beginning · scholar alone**, give the campaign a name, and choose **Begin new game**.

The fresh opening starts on the first morning with 40 crowns, two sun amber, two binding thread, three usable rooms and no resident companion. Begin hearth research, advance through its three phases, then craft a warming lantern. The Home screen follows your progress. Local introductions can lead to a first guest and eventual household membership through ordinary play. The opening is a playable development scenario; final story prose and room-specific opening artwork remain subject to revision.

**Demonstration household · includes Mira** is a separate starting choice. Existing campaigns remain available under Continue; creating a new game never resets one. An explicit campaign URL reopens that selected save. Opening `/` shows the title screen.

## What changed

- Four activity groups replace the long system-by-system sidebar: **Estate**, **Work & study**, **People**, and **Beyond the walls**. Secondary systems remain available through those groups; less relevant fresh-game options sit under Explore later systems.
- Home presents the current opening goal and the next phase’s work. The permanent invitation/resource/news column is removed. Settings and the content workshop use named expandable sections for secondary detail.
- **At your desk → Cheats** provides save-scoped testing tools: resources, instant core rooms/facilities, core and public crafted objects, personal principles, and distinct adult characters from all 21 ancestries. Enable the tools before use. Character spawning requires a suitable free bed. Changes persist, are journaled, and permanently mark the save as testing modified; disabling tools does not undo changes.
- The fresh scholar has an independent **Arrange the first archive** research route. It grants Reference binding and opens the bindery lead. A living index charm replaces the demonstration-only concordant-lesson prerequisite for fresh-game Courteous passage research; other knowledge and costs still apply.
- All sixteen public packs remain connected. Source archives and their digests are unchanged.
- Co-op and Eris/Selene integration are deferred.

## Keeping your existing saves

Stop the old server first. Keep its entire data directory and point this release at it with `python server.py --data-dir /path/to/existing/data`, or copy that data directory into the new application folder before starting. The renamed program folder does not move your data automatically. Do not replace or delete the old data directory until you have verified the saved campaigns in this release.

Schema **38** preserves existing campaigns as demonstration saves and creates a database backup before migration. New fresh campaigns are separate slots. Export a complete save backup before experimenting with cheats if you want to restore the exact previous state.

See [the interface and opening report](docs/SOLO_INTERFACE_V040.md) for the review, testing scope and remaining work.

---

## Earlier release notes and detailed system reference

## v0.39: connected content integration

The sixteen shipped public packs now have dedicated gameplay, production or reference routes for all **1,599 content records**, alongside the **319 fixed mechanics adapters**. This release closes the saved-note-only gap for personal arcs, relationships, care and neighbours: optional chapter invitations connect to actual work and chosen outcomes; field discoveries connect to their returned evidence and follow-up references; communities and independent contacts require completed introductions.

The unchanged foundations pack now uses all 30 occupation mappings and all 25 material-compatible golem appearances. All 525 character story seeds can also support continuing stories for eligible existing residents. Training opportunities use real lessons; wardrobe art briefs can create compatible saved styles; art production exports preserve actual subject/reference context. Letters can be revised before delivery, and delivered correspondence and owned reading inform only the relevant NPC contexts.

Open **Public workshop → Start here** for the opening progression guide. Pack/text filters and reference links connect related content. Joined chapters, saved outcomes and community contacts appear below the catalogue. Production and QA records are explicitly distinguished from generated artwork and executed automated tests. Completed memories remain archived and do not exhaust a lifetime scene cap.

Schema **37** preserves older saves with an automatic migration backup. **453 Python tests and 17 connected headless UI suites pass.** Fresh-campaign tests use normal resources for discovery, fabrication, study, spell testing/preparation/casting, and artifact installation/use. The cloud browser blocked the local server, so rendered-browser layout/focus/mobile verification remains outstanding; live providers, Docker and real agent co-op are not claimed. See [the complete integration report](docs/CONTENT_INTEGRATION_V039.md) and [the record-by-record inventory](docs/content-integration-coverage.json).

## v0.38: public workshop, practical magic and content in play

The **Public workshop** is now a main navigation destination. All **319 public proposal IDs** map to explicit prototype implementation paths, with a source-linked catalogue, resolved costs, real assignments, ownership, reservations and completion receipts. Uploaded proposals cannot change these fixed rules.

Make and own equipment, artifacts and functional furnishings; qualify materials; study public principles; build experimental setups; test, prepare and cast public forms; bind actual ritual roles; use reversible presentation trials; invest in earned methods; select capped room support; and agree funded services or delivery. Spell forms use explicit finite state transitions, preserve object identity and share existing preparation limits.

The broader catalogue now supports selected public field trips and leads, household book/meal/specimen/keepsake preparation, reviewed fictional correspondence, optional scenes and adapted narrative plans. Backgrounds, care cases and possible outcomes require review against actual play; notes do not automatically create people, knowledge, loot, capacity or accepted lore.

Save schema **36** preserves existing campaigns with an automatic migration backup. **433 Python tests and sixteen connected headless UI suites pass.** Rendered-browser layout, live models and Docker runtime remain unverified. See `docs/PUBLIC_RULES_IMPLEMENTATION.md` for exact coverage, balance decisions and limitations, and `docs/public-rule-coverage.json` for every proposal mapping. This is a substantial prototype expansion, not a claim of complete implementation of the original game design.

## v0.37: public expansion library and scene invitations

About & saves now validates and stages the included sixteen-pack public bundle in one atomic operation. The review browser exposes **1,599 content records and 319 disabled mechanics proposals**, with exact versions, dependency checks, typed references and readable nested fields. The original 3,595-record foundations pack is unchanged and is staged without automatic activation.

All **80 household scene templates** can create editable invitations. Review the setting and participants, compose the draft, then use Household life to edit, offer, defer or join it. Declining carries no penalty; no import or draft advances time, grants items, establishes future facts or changes relationships. Source records are frozen in each invitation. External players remain outside authored NPC participation.

Save schema remains **35**; no migration is required. **407 Python tests and fifteen connected headless UI suites pass**, including the public bundle HTTP route and scene transaction path. Rendered-browser, live-provider and Docker-runtime checks remain unverified. The supplied 64 acceptance scenarios are written content, not 64 newly executed tests.

The other public record types remain reviewable design content. Their equipment, spell, ritual, economy and background effects still require implementation. Next: select a coherent materials–recipe–equipment loop with explicit costs, ownership, reserve handling, cancellation and visible bonuses. See `docs/PUBLIC_PACK_INTEGRATION.md` for exact coverage.

## v0.36: discovery, research and personal inscription

The waterworks survey now feeds **Field calibration** research, which unlocks permanent inscriptions on personally owned folios and gauges. Names and ownership history persist. The owner commits 12 crowns, one vessel and one binding component above reserves, then performs two assigned inscription phases. A completed inscription replaces the prepared tool’s +1 contribution with +2. Pause/resume, exact cancellation refunds, transfer restrictions, workroom visibility and migration are implemented.

Resident completion creates an optional technical or playful conversation invitation. It does not expire or award resources or relationship points. Joined conversations become shared memories; optional model-written group scenes receive only history shared by every participant.

The Spellbook now offers **offline construction guidance** with exact personal effects, knowledge sources, facility/funding blockers and valid component combinations above reserves. Choosing a combination fills the manual form without committing an action. The four existing spell forms retain their rules.

Save schema **35** preserves existing progress. **400 Python tests and fourteen connected headless UI suites pass.** Rendered-browser, live-provider, Docker-runtime and actual-agent checks remain unverified. See `docs/designs/FIELDCRAFT_LOOP.md` for the complete loop and limitations. New expansion content still needs reviewed implementation; staging a pack never installs its proposed mechanics.

## v0.35: personal tools, scene drafting and expansion review

**Focus & equipment → Personal working tools** now supports two craftable tools, individual ownership and names, one prepared tool per person, agreed transfers, and visible work bonuses. The folio supports assigned research/archive work; the gauge supports artifact crafting. Crafting uses existing knowledge, materials and assignments. Save schema 34 preserves ownership and preparation across reloads without advancing time.

**Household life** can request structured model-written scene prose from the optional configured provider, recover the same request, and apply reviewed wording to an unapproved invitation. Offering and joining remain separate actions. Five exact system-verifiable prerequisites now receive readable evidence; willingness and private permissions still require review.

**About & saves** adds read-only staging and inspection for expansion handoffs 01–04: materials, equipment, artifacts and magic. Proposed costs and effects remain data and do not become game rules. Includes dependency/version checks, quantity-shortfall reports, nested readable records, and a small fixture. Handoffs 05–17 still await import support.

**392 Python tests and thirteen connected headless UI suites pass**, including real local HTTP routes and mocked provider responses. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed. See `docs/designs/EQUIPMENT_AND_DESIGN_REVIEW.md` for controls, rules and limitations.

## v0.34: full foundations pack and household life

The supplied **3,595-record character-foundations pack** is bundled unchanged. Validate it in About & saves, then activate it after review. **Household → Open household life** adds persistent scene drafts, reviewed narrative prerequisite notes, optional invitations, decline/defer, selected conversation responses and descriptive group history. The offline scene composer supplies editable scaffolding, not autonomous model-written scenes.

Residents can save and wear compatible clothing ensembles or custom garment combinations. Coverage, layering, ancestry restrictions and individual fitting/willingness are reviewed. These cosmetic styles grant no inventory or bonuses and do not repaint existing portraits. Selected story patterns guide future personal-story drafts while existing rule packages retain authority over costs and rewards. Source snapshots survive pack changes, departure and reload.

See `docs/designs/HOUSEHOLD_CONTENT.md` and `docs/FOUNDATIONS_PACK_REVIEW.md`. The `docs/content_handoffs/` folder contains **17 further content-generation handoffs**, their shared schema, actual baseline rule references and the original character pack dependency. These new expansion formats are design proposals, not supported importers.

Save schema 33 adds empty household scene/style/pattern records without advancing time or rewriting identities. **381 Python tests and twelve connected headless UI suites pass.** No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.


## v0.33: imported character foundations and editable review

Content ZIPs following the gamemaster handoff can now be validated, browsed and explicitly activated in **About & saves**. Imports are campaign-specific and included in complete save backups. Errors block activation; honest quantity shortfalls and semantic-review limitations remain visible. The local fixture supports Wolfkin, Demon and Golem and deliberately reports its incomplete coverage.

Imported character generation combines compatible narrative ingredients, avoids established names and favours less-used records. It preserves selected records and pack versions with each identity. Ordinary recruitment, exotic summoning and fully adult golem construction retain their existing rules. Unmapped occupations and stories with unmapped narrative prerequisites are not selected.

Candidate review now supports individual prose and preference edits without another provider request. Locked age/ancestry/capability choices, campaign revisions and draft-edit revisions protect approval. Resident dialogue and personal-story prompts receive their own saved voice, habits, values/boundaries, social style and story ingredients; these possibilities are not completed events. Pack changes do not rewrite accepted people.

See `docs/designs/CONTENT_PACKS.md` for the workflow and integration limits. Clothing, household-interaction and story-pattern pools are validated/browsable, but do not yet create scenes, outfits or quest mechanics automatically. Save schema 32 adds an initially inactive content-pack selection without advancing time or changing existing identities.

v0.33 verification: **372 Python tests and eleven connected headless UI suites pass**, plus JavaScript syntax checks. Real HTTP tests cover the importer and edited approvals. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.


A self-hosted, desktop-first webapp prototype based on the supplied game specification. All artwork, frontend code, rules, and save storage run from your own server. No API keys, CDN, cloud hosting, JavaScript build step, or third-party Python packages are required.

## Current scope

v0.29 adds individual attributes, magical affinities, earned specialization perks and a persistent sample castle mystery with private lore boundaries. `docs/DESIGN_PROGRESS.md` is the current requirement checklist. Full co-op, real agents and the general gamemaster remain unfinished. v0.30 adds bounded containment/release cases and solo estate capacity; broader encounter content and complete estate artwork remain in progress. Later sections retain the development history; they do not supersede that checklist.

## Summoning prototype

See `docs/designs/SUMMONING_DESIGN.md` for the summoning implementation design, including stable identities, contact, visits, two-sided membership decisions and accommodation. Three authored contacts and strictly reviewed generated candidates use paid contact preparation, visits, separate membership decisions, departure and return. See `docs/designs/CANDIDATE_REVIEW.md` for generated admission. `docs/BROWSER_REVIEW_STATUS.md` records the attempted real-browser review and the local-server access blocker; visual usability remains unverified.

## New in 0.23 — a life beyond the introduction

Iona now has an illustrated portrait in the same restrained, dark-paper direction, available in the existing correction/rollback workflow. The image ships locally and needs no provider while playing. Its generation prompt and provenance are recorded in `docs/IONA_ART.md`.

Once she joins the household, her optional **Atlas of small crossings** costs 10 shared crowns, 2 binding thread and 1 porous clay from unreserved stock. It takes exactly three of her own assigned phases. Pause or resume it freely; cancellation returns the saved original payment once. Completion gives Iona 2 advancement and personal understanding of Courteous passage, without teaching other people or granting new travel powers. Her character sheet, Summoning and Workroom notes show the project.

After the atlas, Iona offers a personal **travelling map case**: 6 crowns from an explicitly chosen shared or personal wallet, 1 binding thread, 1 porous clay, and two personal work phases. The finished case is hers. Read her closing note and optionally display it in her bedroom. Departure preserves the case and its display choice; it reappears with her agreed bedroom after she returns and rejoins. Finish or cancel funded projects before agreeing departure.

Five new optional, non-expiring household moments cover settling in, her finished atlas, a shared map discussion with Mira, the map case, and choosing to stay again after a return. They grant no currency, advancement, affection or Resonance. The shared scene contributes a descriptive friendship entry, without a relationship score.

The Household ledger also supports **offered gifts**. A resident’s listed personal interest may be bought with their wallet or given explicitly from shared funds. Gifts respect the discretionary treasury floor, cannot duplicate an owned item, and do not change relationships or abilities. Iona’s tea tin joins the existing personal-interest catalogue. These possessions stay with their owner through departure.

Schema 22 adds the new scene/request records and Iona’s optional project offer. It preserves current contacts, visits, membership, funds, completed learning and time; it does not fund work or play scenes automatically.

## New in 0.22 — the Open Threshold

Summoning now has a complete authored contact and visit cycle. Finish the concordant lesson, research **Courteous passage** (12 shared crowns, three research contributions), and use a conductor who personally understands it. Under **Summoning**, prepare the Open Threshold for 12 shared crowns, one vessel and one binding component from unreserved stock, and two conductor phases. Changing assignment pauses it; cancelling unfinished preparation refunds exactly what was committed once.

The contact introduces **Iona**, a 38-year-old human threshold surveyor. This fixed adult fixture is sample content, not a generated recruit or the final first companion. Discuss her intentions, household life and a visit. Contact needs no bed; an agreed arrival reserves a real bed and rechecks accommodation on Advance. Iona accepts a separate bed in a shared chamber. She arrives as a visitor, excluded from household work and allowances.

Ask whether she wishes to stay, then record the household's decision separately. Only both positive decisions create membership. As a member she has independent learning, crafting, focus, spell and money records; no assignment, allowance or romance starts automatically. She does not inherit Mira or Tamsin’s stories, rituals or personal rewards. Starting Methodical assembly is distinguished from earned advancement.

An agreed departure happens on Advance after committed work is finished or cancelled. The bed is freed while identity, knowledge, money, possessions and correspondence remain. Invite her again through the same contact; the new visit has fresh membership decisions. Closing and reopening remote contact is free and never rerolls identity. Household and room panels distinguish visitors from members. Iona’s portrait and personal content were added in 0.23.

The self-hosted app requires no model provider for any of this. Save schema 21 adds empty summoning records to existing campaigns without spending money, introducing anyone or advancing time. Generated candidates and co-op remain future work.

## New in 0.21 — persistent identities and safer arrivals

Each campaign now owns the identity records for its adult sample cast. Names, roles, starting practices, ages and accommodation preferences persist with the save rather than being read exclusively from the application catalogue. Existing character IDs, progress and relationships are preserved.

Rooms & beds now lists expected arrivals by name and room. You can put an arrival aside, release its bed and invite the same person again later without losing conversations. An arrival can be moved to another compatible vacant room when one exists. Each explicit Advance rechecks the room, capacity and accommodation preference before admitting anyone; a blocked arrival waits without displacing an occupant. The current private-room candidate has only one compatible chamber in this build.

Schema 20 migrates the old pending invitation into the shared named-reservation collection. This was the first summoning foundation; version 0.22 builds the authored visit cycle on it. Browser visual testing remains blocked as recorded below.

## New in 0.20 — reviewed spell-construction suggestions

The Spellbook now accepts an ordinary-language idea through the optional text provider and requests a structured construction suggestion. The model can select one of the four supported forms or report that none fits. It supplies a short name, explanation and limitations; unknown forms, extra fields, malformed JSON and oversized values fail validation. This validates the shape and catalogue reference, not the truth of every generated sentence.

The review panel separately shows rules-owned effects, personal principle knowledge, required room and component properties, the 4-crown testing cost and two assigned testing phases. Descriptive prose cannot add powers or change these values. Suggestions may identify missing knowledge but never grant it. No private conversations, wallet records or hidden campaign facts enter the construction prompt.

Requesting, retrying or recovering a suggestion does not change game state. Use suggestion in design form copies a reviewed name and intent into the manual designer; it explicitly replaces unsaved fields for that form. Choose components and save a design separately. All existing tests, personal knowledge, stock checks, preparation and casting rules still apply. Existing forms are not duplicated. Stale suggestions cannot be copied after the campaign changes. A suggestion can never be accepted as NPC dialogue or a journal account.

Requests are scoped to a current, at-home owner and saved per campaign in the existing draft journal. Retries recover the original result without another provider call. Recovery filters owner and purpose before limiting results. Configured provider usage may incur charges; no background request or automatic retry is added. Manual spell design remains fully offline. Live provider output quality remains unverified; tests use controlled responses.

The 0.20 release retained state schema 19; the saved draft journal supports the new purpose without a campaign migration. There is no full natural-language spell grammar or rules-authoritative gamemaster yet.

## Previously in 0.19 — specialization and voluntary personal magic

**Advanced practices:** Comparative study requires personally learned Patient scholarship and Scholarship rank 1; Measured assembly requires Methodical assembly and Artifice rank 1. Each costs 2 earned advancement and takes two assigned training phases. Learning does not prepare it automatically. When prepared, each adds one contribution to its relevant work, using the existing two practice slots. The study practice does not add copying income; neither speeds training, spell tests, focus work or personal keepsakes. Residents offer these professional paths while retaining their existing fieldwork interests.

**Readable contributions:** character sheets break research/archive and artifact work into base effort, skill ranks, prepared practices, installed utilities and focus effects. Crafting duration estimates now use these same totals. Remaining work caps the amount actually used; faster work does not create extra primary actions or another delegated copy in the same phase.

**Preparation sets:** save up to six named sets per person, capturing currently prepared practices. Loading replaces those two slots only and requires the scholar and owner home. Spell and focus preparation remain separate. Retraining preserves saved names but blocks loading practices that must be learned again; it cannot restore forgotten expertise. Saving an existing name explicitly replaces its snapshot.

**Lamplit sight:** an optional, reversible personal blessing. The owner must personally understand Gentle refraction; residents offer it after their professional projects. Receiving costs 10 shared crowns, 1 unreserved moon glass and 1 unreserved binding thread, with two personal ritual phases. It adds one spell-preparation slot and describes a faint violet glint in the eyes. Portraits remain unchanged. Personality, consent, relationships and Resonance are unaffected.

The blessing uses one primary assignment. Changing assignments pauses progress; resuming restores the ritual role. Cancelling unfinished receiving returns the exact committed cost once. Reversal needs one assigned phase and no material fee. If too many spells are prepared for the restored capacity, reversal waits for the owner to put some aside; nothing is silently removed. Cancelling reversal leaves the blessing active. The blessing stacks with the existing concordant lesson’s base capacity and cannot stack with itself. Agreed resident work may continue during the scholar’s expedition, but never without explicit Advance.

Schema 18→19 adds empty preparation sets and inactive personal augmentation records, without spending money, learning practices or starting rituals. Existing preparations, skills, knowledge and accomplishments persist. Numerical tuning and this sample blessing remain provisional.

## Previously in 0.18 — a household with things to say

Eleven authored moments respond to real progress: the restored Conservatory, the returned Gentle refraction discovery, completed professional projects and personal keepsakes. Two shared scenes let Mira and Tamsin disagree, exchange interests and develop a descriptive friendship. Two private follow-ups require the relevant resident’s existing welcomed flirtation and personal keepsake; neither establishes additional consent or adds Resonance.

Open Household for a consolidated view of invitations and remembered scenes. Individual conversations also show that resident’s private invitations. Join explicitly, leave something for later, or bring a deferred invitation back. Everyone involved must be home for a new scene. There is no deadline, time cost, work interruption, resource reward or affection score. Completed scenes can be reread even while away, without replaying the action.

The household overview shows assignments, pending conversation counts and the state of personal requests and learning, with a link to all work commitments. Shared friendship descriptions reflect the scenes actually joined. Optional generated replies receive the titles of completed moments involving that speaker only; private histories are not merged.

Schema 17→18 adds waiting interaction records without replaying scenes or altering relationships. The scene catalogue lives in `resident_moments.py`, separate from the rules. Existing artwork and text-based furnishing panels remain unchanged.

## Previously in 0.17 — furnishings you can read

Room illustrations remain atmospheric paintings. Per the latest design direction, low-quality furniture and lantern overlays have been removed. A **Furnishings & effects** panel records the actual main furnishing, textiles, wall display, installed magical utilities and personal keepsakes. It states each effect, distinguishes purely decorative items, and shows the common-room settee’s current conditional Resonance contribution. Existing installation controls and rules remain in force.

Each room now has independent floor-textile and wall-display slots. Choose modest supplied rugs, a reed mat for the Conservatory, botanical studies, a star chart or a bedroom mending sampler. These are descriptive choices with no numerical bonus, cost or time advancement. They do not alter the background painting.

Save up to six named arrangements per room. Each remembers its main furnishing and both decorative slots. Loading restores that room’s choices; deleting a saved arrangement leaves its current contents alone. Saving an existing name replaces that snapshot. Installed magical utilities, consumable inventory, personal keepsakes, bedroom assignments and artwork are excluded from arrangements.

Schema 16→17 adds empty decorative slots and empty arrangement lists while preserving existing main furnishings, artifacts and saves. This is a deliberate presentation change from the original overlay prototype; the original design document remains preserved.

## Previously in 0.16 — personal projects and reviewed journal accounts

Mira and Tamsin each offer an optional project after finishing their professional notebook work. Mira wants a cloth reading folio (6 crowns and 2 binding thread); Tamsin wants an offcut case (8 crowns, 1 binding thread and 1 porous clay). Each takes two phases of its owner’s primary work. Requests & letters shows prerequisites, costs, the chosen wallet and protected material shortages. Accept or defer freely, with no expiry or relationship penalty.

Choose shared funds or the owner’s personal wallet explicitly. Components always come from unreserved household stores. Changing assignments pauses work; resuming restores the assignment. Cancelling unfinished work refunds the exact components and original wallet once. Completion leaves a personal keepsake and an authored closing note. Display it on the owner’s bedroom shelf or put it away freely. It follows their room choice and grants no skill, affection or Resonance. Character sheets list personal purchases and keepsakes.

The Journal can request an optional account of the last Advance through the existing text provider. Review the draft beside its resolved source events before saving. Generated prose is labeled and preserved with its source events; it never executes actions or grants rewards. The provider sees only the selected resolved results and editorial brief for this request, not private conversations or wallet records. Draft recovery separates accounts from NPC replies. Stale drafts cannot be accepted, and retries recover the original result without another provider call. No generation runs automatically; a configured account is optional.

Schema 15→16 adds offered personal requests and empty keepsake/shelf lists without spending funds or progressing time. Older NPC drafts remain recoverable. Live provider quality and browser painting remain unverified.

## Previously in 0.15 — shared teaching and practical routines

- **Agreed lessons:** a housemate can teach a personally known principle or a higher skill rank the learner has offered to study. A lesson takes one phase of both people’s primary assignments. Skill lessons still reserve and invest the learner’s normal 2 earned advancement. Teachers receive no farmable advancement, and no other character inherits the result.
- **Pausing and continuity:** leaving or changing either assignment pauses the lesson. Resume restores both agreed roles. Cancellation releases reserved learner points and the teaching assignment without undoing completed knowledge. A teacher who retrains below the agreed rank can no longer finish that lesson until qualified again. A saved lesson history records the people, subject and completion phase.
- **Workroom notes:** a new overview shows every household member’s current assignment, unfinished personal projects, teaching commitments, held work budgets and the next phase’s forecast. It links to the authoritative project controls and can pause an assignment without destroying progress.
- **Finite casting plans:** agree 1–12 castings of one personally tested and prepared spell. Each still consumes one primary phase. Missing inputs must be available above protected stock; plans do not buy supplies or use wallets. Residents can continue agreed castings while the scholar travels. A shortage waits; another assignment or absence pauses progress. Putting the spell aside pauses the plan until explicitly resumed. Completion stops at the agreed count, while cancellation keeps completed outputs.
- **Predictable resolution:** an agreed artifact batch claims its inputs first, then casting plans commit available inputs in household order before production. One plan cannot use another’s same-phase output. There is no offline work or additional action allowance.

The interface now has 24 views. Existing ordinary study, manual castings and crafting remain available. Cancel an open casting plan before scheduling separate spell work for that person.

## Previously in 0.14 — bounded household delegation

Start with **START_HERE.md** for launching, preserving an existing save and a short testing route.

Saved work orders can now become standing agreements. Agree an exact maker, recipe, components, quantity and reserved budget; one open agreement is supported. The maker must personally know the principle. Reserving funds assigns crafting but starts no work until Advance.

On each Advance, an idle workbench can start one agreed copy and apply the maker’s normal contribution. Protected stock stays aside; missing unreserved components are bought only from this order’s held budget. Neither personal wallets nor additional shared funds are drawn automatically. A fast maker still completes at most one copy per phase. Residents can continue agreed work while the scholar travels.

Changing the maker’s assignment or leaving pauses their contribution. Pause/resume preserves work and budget. Budget exhaustion waits for explicit funding. Completion returns unused money. Revocation refunds unused money and leaves any committed copy as manual work. Revoke before using manual controls on that order or removing it. There is no offline production. Existing orders remain manual on upgrade.

## Personal money included from 0.13

The ledger separates individual discretionary wallets from the shared treasury. Daily allowances of 0–10 crowns per current household member resolve together only at evening-to-morning Advance, after work and return income. The whole payment is skipped if it would cross the chosen treasury floor; no debt or arrears accumulate. New arrivals start with zero allowances until explicitly included. One-time allocations respect the same floor.

Three offered expedition arrangements allocate 100%, 75% or 50% to shared funds, dividing the rest equally among returning participants in whole crowns. Indivisible crowns remain shared. The agreement is captured at departure; materials and discoveries are not liquidated. Three bounded personal-interest purchases use only the owner’s wallet and grant no relationship or ability bonus. All balances and dated transfers persist.

The ledger also shows money held by work agreements. Those budgets are explicitly funded projects; the discretionary-allowance floor does not block a deliberate project commitment.

## Previously in 0.12 — fieldwork, personal skills and a growing household

This development checkpoint continues the existing self-hosted game. It is not a final campaign or a new canonical cast.

- **Rainward observatory:** a fifth destination reached through the Hillfold survey. Each of two finite leads has three encounters with explicit methods. Personal principles, carried tools and Fieldcraft open faster approaches. An optional extra lens introduces a recoverable alignment problem. Returning early saves completed encounters and remaining work; rewards arrive only after completing the lead and returning home. A changed party must still satisfy the saved method’s requirements.
- **Personal skills:** Scholarship, Artifice and Fieldcraft each support two added ranks. A rank costs 2 earned advancement and two assigned learning phases. Scholarship adds research contribution; Artifice adds artifact crafting contribution; Fieldcraft opens field methods and shortens ordinary surveys. Rank zero retains baseline competence. These are individual benefits, not household-wide scores. Training can pause or be cancelled, and retraining releases the investment.
- **Two new artifacts and a fourth spell:** the Reading prism adds 2 crowns to assigned scholarly copying. Gentle glass clarification turns 1 fireglass into 2 moon glass per prepared, assigned casting. Tamsin’s notebook unlocks a Binding press, adding one artifact work contribution for the active maker. Install artifacts in the library; duplicate installations do not stack.
- **Optional resident recruitment:** returning with the Hillfold salvage introduces Tamsin, a 35-year-old human bookbinder. Discuss work, home preferences and plans before offering her an available private one-bed room. An accepted invitation reserves that specific bed. She arrives on the next Advance and chooses her own routine until an offered assignment is agreed. She is authored demonstration content, not the final first recruit.
- **Independent work and knowledge:** Tamsin has her own advancement, tools, learned principles, skill ranks, preparation and projects. She offers archive work, binding, learning and practical magic; she does not offer gardening or expeditions. Her three-phase repair notebook costs 8 crowns and 2 binding thread after installation of the living index. Completion grants her 2 advancement and personal knowledge of Joined fibres, with professional notes available for others to study.
- **Household life:** Tamsin has independent conversation history, saved wardrobe choices, optional tea and a separate mutually welcomed flirtation. Styling and tea cost no phase and grant no mechanical reward. Flirtation awards 2 Resonance once; the existing settee rule counts each established voluntary flirtation independently. No recruitment, work or essential facility requires intimacy.
- **Resident-specific NPC drafts:** optional generated replies can address Mira or Tamsin. Each sees her own recent conversation and relevant public facts. Draft review, retry, stale-state checks and explicit acceptance remain in place. Acceptance adds prose only. No live provider was used in verification.
- **Subdued local artwork:** a modest observatory, Tamsin’s stable portrait and a matching shawl variant. All assets ship locally and can be reviewed/replaced independently.

The current catalogue contains 22 navigation views, five expedition destinations, eleven artifact recipes and four bounded spell forms. The original two-person ritual increases preparation only for its actual participants; Tamsin retains two spell slots. Skills do not accelerate spell tests, personal projects or ritual work.

## Previously in 0.11 — a working spellbook and cooperative ritual

This larger expansion connects personal knowledge, materials, preparation, household work and room views. It also supplies distinct West chamber and Garden chamber illustrations, keeping the dim, modest archive-workshop direction.

- **Personal spell designs:** give a spell a name and written intention, select one of three supported forms, and choose components by their properties. Saving a draft is free. The selected form fixes the rules; prose cannot grant additional powers or bypass requirements. Each person can keep one design per form. Uncommitted drafts can be discarded and revised.
- **Test before using:** commit 4 crowns and two compatible components, then spend two assigned Advance phases testing. Personal understanding and an available room are required. Testing pauses on another assignment or absence, consumes no further components, and grants no output or advancement.
- **Prepare deliberately:** each person initially has two spell slots. Only that person's tested spells can be prepared. Completing a test does not automatically prepare it.
- **Three useful workings:** Warm-twist binding uses 1 silver ivy to produce 2 binding thread; Root-song tending produces 2 silver ivy in the restored conservatory; Luminous transcription earns 6 shared crowns in the library. Each requires one assigned phase per casting. There is no mana meter or casting fee for the latter two.
- **Explicit casting:** scheduling reserves any input immediately and assigns the caster. Only Advance resolves it, once. Switching assignments pauses it; cancellation returns its committed input. A pending casting must be resolved or cancelled before changing spell preparation. No automatic repeat queue is started.
- **Cooperative ritual:** the Concordant lesson expands each participant's spell preparation to three slots. Both must personally know Reference binding, at least one must know Clear instruction, and the living index charm must be installed. It costs 18 crowns and four components once, then requires two coordinated phases with both at home and assigned. Neither participant can substitute for the other. The benefit has no upkeep or expiry.
- **Connected controls:** room views show compatible tested spells and direct casting controls; character sheets link to each person's spellbook. Forecasts, summaries, journals, routine locations and saved progress follow the new work. Optional NPC dialogue receives only Mira's tested spell names/forms/preparation and the shared ritual status, never private design intentions or the scholar's spell notes.
- **Distinct accommodation art:** the one-bed West chamber and two-bed Garden chamber now have separate local illustrations. Existing accepted image overrides remain untouched. Generation prompts and provenance are recorded in `docs/ARTWORK_v0_11_PROMPTS.md`.

### Try the spellcraft loop

1. Complete hearth-ward research, then open **Spellbook → Your scholar → Warm-twist binding**.
2. Write a name and intention. Select a heat-bearing and a binding component. Save the design and review its exact effect and blockers.
3. Choose **Begin test**, then Advance twice while assigned to spell work. Prepare the learned spell.
4. With at least 1 silver ivy, schedule a casting from the spellbook or common room. Advance once to receive 2 binding thread. The caster then becomes unassigned; repeating requires another explicit instruction.
5. Research Steady growth and Luminous copying for the other forms. Each person must study principles individually before testing their own designs.
6. Open **Rituals** after installing the living index and meeting its personal knowledge requirements. Choose components, begin together, and Advance for two coordinated phases. Prepare a third spell afterwards.

Spell outputs are exact base outputs; focus/practice/copying/garden-staffing bonuses do not multiply them. Unattended garden artifacts remain separate production. Explicit spell and ritual actions may consume reserved materials, as explicit crafting already does. Drafting and preparation never award advancement. This is a bounded first spell-invention system; arbitrary natural-language rule generation and broader rituals remain future work.

## Earlier: 0.10 — Stonework and Spellcraft, rooms and beds

The game title is now **Stonework and Spellcraft**, superseding Stone and Spell at the user's request.

- **Rooms & beds:** track usable, occupied, reserved and available beds with explicit counts. The starting guest chamber holds separate beds for the scholar and Mira.
- **Two accommodation projects:** after completing the Proper Living Wing milestone, restore the West chamber for 16 crowns and two assigned phases, or the Garden chamber for 24 crowns and three assigned phases. Prices include beds and basic furnishings. Only explicit Advance resolves assigned work; switching tasks or leaving home pauses it.
- **Five beds in total:** the West chamber adds one bed and the Garden chamber adds two. Restoring a room does not move anyone automatically.
- **Bedroom choices:** move the scholar or accept Mira's authored offered room choice while the relevant characters are home. Mira's evening routine follows her selected bedroom. Occupied and reserved beds cannot be assigned to someone else.
- **Future planning:** reserve vacant beds and release reservations without advancing time. Reservations do not promise or create recruits; recruitment remains unfinished.
- **Room customization:** restored chambers have independent furnishing selections and artwork overrides. They reuse the existing modest guest-chamber concept illustration, clearly disclosed in the interface.
- **Save compatibility:** schema 9 adds housing records without changing existing progress, money or time. Existing campaign names, save paths and Compose volume configuration remain unchanged.

Open **Rooms & beds** to see prerequisites, fund a chamber, resume paused work, choose bedrooms and reserve vacancies. The full castle capacity and annex catalogue remain future work.

## Earlier: 0.9 — optional NPC dialogue

This release originally adopted the title Stone and Spell. Existing campaign names, save paths and Compose volume configuration remain unchanged. The extracted application directory retains its historical name for compatibility; update the application inside your existing directory when using Compose.

- **Optional OpenRouter NPC drafts:** configure a chat-capable model and API key under About & saves. Generation is disabled by default. The scripted game remains fully playable without provider access.
- **Review before accepting:** type a line in Mira’s conversation input and choose Request NPC reply draft. Neither your line nor the generated reply enters the conversation until you accept the preview. Generated replies are labelled; HTML-like text is escaped.
- **Rules remain authoritative:** the provider has no tools or database access. Acceptance appends only the two dialogue lines and increments the save revision. It cannot advance time, change funds, award knowledge, complete projects or establish mechanical consent.
- **Small, scoped context:** the request includes Mira’s authored identity, both characters’ adult ages, current room/day/phase, described relationship, her personally known principles, archive-project status and up to 12 recent You/Mira dialogue entries. Hidden lore, other private records and credentials are not included.
- **Explicit requests and bounded output:** configure 100–1500 output tokens per request (default 500). Reported token usage appears with the draft. No model, pricing estimate, automatic fallback or background generation is assumed.
- **Recoverable requests:** each draft has a saved identifier. Checking/retrying that identifier returns its recorded state instead of making another provider call. Recover the eight most recent drafts from the conversation panel after reloading. A failed or interrupted provider operation may have incurred usage; starting fresh is a deliberate new request.
- **Stale-scene protection:** if any campaign action changes the revision while a draft is being generated or reviewed, it cannot be accepted. Generate a new draft for the current scene. Acceptance itself is idempotent.
- **Server-side credentials:** settings are shared across this private server and stored in `data/provider-settings.json` with owner-only permissions on POSIX. This file is not encrypted; protect the server directory. Keys never appear in the settings response, model context, campaign JSON or single-campaign backup ZIP. A whole-directory server backup does include this settings file.

### Try optional dialogue

1. Open **About & saves → NPC dialogue through OpenRouter**. Enter your account’s exact text-model identifier and API key, select an output limit, enable drafts and save.
2. Saving settings does not call the provider. Open Mira’s conversation with both characters at home, enter a line, then choose **Request NPC reply draft**. This explicitly sends the scoped conversation to OpenRouter and may incur charges.
3. Review the prose and reported token usage. Choose **Accept these two dialogue lines**, or discard the preview. Ordinary scripted topics and Save line continue to work separately.
4. If the connection breaks, use **Check / retry the same request**. After reloading, use **Recover recent saved drafts**. A server interruption can leave a draft marked processing; it is never automatically re-issued. You may deliberately start fresh, understanding that the earlier provider request may have been billed.
5. To remove credentials, check **Remove stored key** and save. This also disables generation.

No live paid request was made during development. Provider transport and failure behavior were tested with controlled responses; actual model compatibility, availability, billing and response quality must be checked with your chosen account. The full gamemaster, generated rules proposals, recruitment and co-op remain unfinished.

## Earlier: 0.8 — Personal tools and separate stories

This release adds signature equipment progression, independent solo campaign slots and downloadable restorable backups. It keeps the same self-hosted Python standard-library/SQLite architecture and all earlier gameplay.

- **Focus & equipment:** the scholar begins with a plain Ash staff and Mira with an Archive clasp. These are personal tools, separate from shared deliverable artifacts. Rename a tool at home without changing its function. They are recorded equipment, not new portrait variants.
- **Four permanent inscriptions:** Scholarly thread adds 1 contribution to assigned research/index work; Steady hand adds 1 contribution to the owner's assigned artifact crafting; Copying line adds 2 crowns to the scholar's assigned copying; Preservation case adds 1 binding thread to a new completed salvage return per party. Each requires its named personally understood principle, two property-compatible components, 6 crowns and 2 assigned phases.
- **Capacity upgrade:** reference binding, two vessel components, 18 crowns and 3 assigned phases increase a focus from one prepared slot to two. Using one material for both component slots consumes two copies.
- **Separate preparation:** household and expedition configurations are saved independently. Work inscriptions belong to household preparation; preservation cases belong to expedition preparation. Learning an inscription does not prepare it automatically. Changes are free at home; there are no remote equipment changes.
- **One primary assignment:** each owner works on their own focus. Beginning inscription work pauses their other task. Switching tasks or leaving home keeps progress. Focus work always takes one contribution per assigned Advance; research/crafting bonuses do not accelerate it. It earns no advancement and has no repeated upkeep.
- **Independent campaign slots:** use About & saves to create and open up to 20 separate solo sample campaigns, including the original. Each has its own database, time, resources, projects, conversations and uploaded artwork. New campaigns begin with the furnished sample, not the final campaign opening. Co-op cannot be created or simulated in this release.
- **Safe per-tab selection:** the URL identifies the selected campaign. Every action, state read, export and artwork request stays scoped to that campaign. No server-global active-save switch can redirect another tab. Creation requests reuse their identifier after a lost response.
- **Restorable save ZIP:** download a consistent SQLite snapshot together with accepted uploaded artwork, rollback images and restore instructions. The readable JSON export remains available for inspection. Downloading either changes no state or phase.
- **Schema 8 migration:** all prior values are retained; each person receives a plain uninscribed one-slot tool and no active focus work. The original database remains at its existing path.

### Continue from v0.7

1. Open **Focus & equipment**, choose the scholar or Mira, and review their personal principles. Study a missing principle on the character sheet if needed.
2. Choose **Steady hand** after learning hearth wards. Supply a heat-bearing component and a binding component, pay 6 crowns, then Advance twice while the owner is assigned to inscription work.
3. Prepare the completed inscription in the **Household configuration**. That character contributes one extra unit when assigned to craft an artifact.
4. Build other inscriptions and the capacity upgrade as desired. A Preservation case must be prepared in **Expedition configuration** before leaving. It gives one extra binding thread on a completed salvage return, without stacking across the party.
5. Open **About & saves** to rename the current campaign, download its save ZIP, or begin a separate solo sample. Existing campaigns are kept.

See `docs/IMPLEMENTATION_STATUS.md` for a section-by-section account of the design's implemented and remaining systems.

## Earlier: 0.7 — Useful things, finding their people

A connected expansion from workshop output to neighbour correspondence, field discoveries and household life. The self-hosted Python/SQLite stack and existing subdued artwork are retained.

- **Requests & letters:** four optional, one-time deliveries. Accepting commits no goods; putting a request aside has no penalty. Requests and their rewards never expire. All senders and replies are authored game content, not external messages.
- **Safe, explicit delivery:** the button lists every artifact and material consumed and every reward received. Installed/displayed artifacts, packed lanterns and material reserve targets are protected. Delivery is immediate and costs no phase; crafting and expeditions still require Advance. Replies remain on the request board.
- **A lamp for the footbridge:** complete hearth research, then supply a spare warming lantern and 2 binding thread. Receive 24 crowns, 1 porous clay and directions to the fern nursery.
- **Dry shelves at Reedbank:** after returning with the storage-seal survey, supply a spare pantry seal and 2 unreserved ivy. Receive 28 crowns and 1 moon glass.
- **Lessons for a pair of desks:** after Lessons that stay clear, supply 2 spare lesson tablets. Receive 44 crowns and 2 fireglass. A library installation remains protected.
- **Fern nursery:** a fourth expedition destination. Survey its watering channels to learn capillary wicking, or collect offered supplies for 4 ivy, 2 clay and 14 crowns. Findings and each party member’s one-time advancement arrive only on return. Each lead can be completed once.
- **Capillary mat:** a ninth recipe, requiring botanical and binding components and 3 work contributions. Install it directly in the Conservatory for +1 silver ivy per staffed ivy harvest. With the watering charm, this yields 3 ivy. It does not improve sales or the root tender’s unattended production.
- **Nursery exchange:** after the channel survey, send a spare capillary mat back to the teaching beds for 24 crowns and 2 moon glass. Crafting two copies via a work order lets you keep one installed at home.
- **Two optional Mira scenes:** a neighbour’s reply prompts a shared reading; the nursery survey and restored conservatory prompt a quiet moment among the plants. Find them in Household or Requests & letters. They wait until both people are home, cost no time, and grant no resource or advancement rewards. The garden dialogue acknowledges existing mutual flirtation when established.
- **Schema 7 migration:** existing work, orders, research, installations, reserves and expeditions are preserved. New requests begin unaccepted; the nursery is closed until its introductory delivery. Migration advances no time and grants no automatic deliveries or rewards.

### Continue from v0.6

1. Keep your `data` directory when upgrading. Open **Requests & letters** after completing the introductory hearth research.
2. Accept **A lamp for the footbridge**. Craft a spare lantern (or explicitly put away your displayed one), and keep 2 binding thread above its reserve target. Use the crafting and stores links on the board.
3. Choose **Deliver listed goods**. Read the saved reply, then choose **Follow the nursery directions**.
4. Set out, survey the channels, and return home. You can invite Mira after her existing archive story; each traveler learns the principle on return.
5. Craft a **Capillary mat** in the Workshop and install it in the **Conservatory**. Assign Mira to the garden and choose ivy production to use its bonus.
6. Check **Household** for the new optional scenes. The remaining requests give spare artifacts useful destinations whenever you feel like making them.

## Earlier: 0.6 — Useful magic, planned with care

A connected research and household-planning expansion. Everything still runs locally on the same Python/SQLite stack, with no new service or dependency.

- **Three further studies:** Steady growth cycles (12 crowns, 5 work), Luminous impressions (14 crowns, 5 work), and Lessons that stay clear (10 crowns, 4 work). A qualified scholar or Mira can lead. One shared research focus is active at a time; other funded studies keep their progress. Funding is charged once.
- **Research actually develops people:** each contributor gains 1 advancement once. Present contributors personally learn the resulting principle; an absent contributor keeps the accomplishment but studies the shared notes after returning. Existing preparation and the library index improve work contributions.
- **Root tender:** a botanical component plus a vessel, using steady growth; 3 crafting contributions. Install it directly in the Conservatory. With no gardener, it produces 1 silver ivy or 2 crowns on Advance. A staffed harvest replaces this smaller output; it is never doubled.
- **Scribe stone:** heat-bearing component plus vessel, using luminous copying; 3 crafting contributions. Install it in the Library for +2 crowns per assigned scholar copying phase. With prepared scholarship and the living index, copying earns 8 crowns per phase. There is no unattended copying income.
- **Lesson tablet:** vessel plus binding component, using clear instruction; 3 crafting contributions. Install it in the Library to reduce new personal principle studies from two phases to one. Practice training and already-started learning are unchanged.
- **Stores & plans:** reserve targets for every material, plus saved artifact work orders with selected maker, components and copy count. Reserves block manual sales below target; explicit crafting can use the protected stock.
- **Stock-first garden priority:** replenish silver ivy in whole harvests until its reserve target is reached, then sell only newly designated harvests. Existing inventory is never automatically sold. This works with either Mira or the root tender.
- **Work orders:** plan up to 20 copies without committing anything. Buy exactly the missing components for the next copy at the displayed total, then explicitly start it. The order tracks completed copies; further copies never begin automatically. Removing a plan keeps completed artifacts and stock.
- **Compatible schema 6 saves:** new studies begin unfunded, reserve targets start at zero, no utility is installed automatically and existing production choices are retained.

### Try this expansion

1. Open **Research → Further studies**. The lead must understand each listed prerequisite. The character sheets show which archive notes can be studied.
2. Complete **Steady growth cycles** after learning hearth wards and water guidance. Craft a **Root tender** and install it in the **Conservatory**.
3. Open **Stores & plans**, set a silver-ivy reserve (for example 4), then choose **Replenish ivy, then sell harvests** in the Conservatory. Its next-harvest forecast states the actual output under the current staffing.
4. Continue the other research branches after Mira’s index project and the preservation discovery. Craft and install their artifacts in the **Library**.
5. In **Stores & plans**, save an artifact work order. Use **Buy missing**, then **Start one copy**. Advance with the selected maker assigned; the next copy waits until you choose it.

Staffed garden output remains 1/2 ivy or 4/6/8 crowns, depending on its existing upgrades. The root tender’s unattended output is always 1 ivy or 2 crowns; staffed bonuses do not apply to that smaller harvest. Stock-first may exceed its ivy target by one item because it uses whole harvests. No production occurs offline.

## Earlier: 0.5 — People, practice, and a living archive

This expansion adds character development and a resident story to the existing household loop. The same self-hosted Python/SQLite stack and subdued artwork remain in place.

- **Character sheets for both people:** individual knowledge, earned advancement, learning projects, prepared practices, ambitions and an accomplishment ledger. Values have plain-language meanings; there is no affection meter.
- **Accomplishment-based advancement:** first artifacts per maker, returned expedition leads, hearth understanding/contribution, the living wing, and Mira’s project award points once. Repeated crafting, ordinary production, commissions, conversations and retraining do not generate additional advancement.
- **Three learnable practices:** Patient scholarship, Methodical assembly and Prepared field notes. Each new practice costs 2 advancement points and 2 assigned learning phases. Learn broadly, then prepare up to two at home. Mira starts knowing Patient scholarship; nobody is automatically prepared.
- **Concrete preparation benefits:** scholarship adds 1 research contribution and, for the scholar’s commissions, 1 crown; assembly adds 1 crafting contribution; field notes reduce a party’s survey from two phases to one. A lantern and field notes do not stack below one phase.
- **Personal mastery:** any recorded principle can be studied on a character sheet for two assigned phases, without an advancement fee. A shared archive entry does not automatically qualify every maker to use it.
- **Mira at the workbench:** choose the scholar or Mira as an artifact’s maker. Only that person’s assignment, personal knowledge and preparation apply. There is still one shared crafting project. The other person can work independently.
- **Mira’s living archive:** after A Proper Living Wing, accept her project, contribute four study units, craft the resulting Living index charm, install it directly in the Library, and show Mira the result. She earns 3 advancement; the scholar earns 1. All stages wait without expiry.
- **Useful library index:** adds 1 contribution per assigned researcher and 1 crown to copying commissions. Together with prepared Patient scholarship, commissions pay 6 crowns per assigned scholar phase (4 base + 1 practice + 1 index).
- **Shared expeditions:** after her story, Mira offers to join. Her household work stops while she is away; no garden harvest, archive work, crafting or training happens from an absent character. Both return home unassigned. Party members receive the relevant one-time discovery advancement and personally learn survey principles on return.
- **Hillfold bindery:** Mira’s completed index reveals a third destination, even if both older sites are exhausted. Read its kiln catalogue for 2 moon glass and 16 crowns, or salvage 4 binding thread, 1 fireglass and 12 crowns. Moon glass can serve as either a vessel or heat-bearing component; using it twice consumes two pieces.
- **Simple retraining:** one assigned phase at home releases invested advancement. Starting expertise, magical knowledge and accomplishments remain. Learning can pause; cancellation releases reserved points but discards that unfinished project’s progress.

### Continue from v0.4

1. Open **Character sheets**. Existing accomplishments are credited once during migration. Review the scholar’s available advancement and Mira’s starting scholarship practice.
2. Finish **A Proper Living Wing** if needed, then open **Character sheets → Mira → An archive worth getting lost in**.
3. Accept the project. Mira assigns herself to its study; your scholar can help. Prepare Mira’s Patient scholarship for a larger contribution. Each person still has one primary assignment.
4. When the study finishes, select **Living index charm** in the Workshop. Choose a maker who personally understands reference binding (a contributor at home, or someone who studies the archived notes). Supply a vessel and a binding material.
5. Open the **Library**, install the finished charm, then return to Mira’s project for its concluding conversation.
6. Train and prepare practices as desired. On the expedition map, select **Hillfold bindery**, check **Invite Mira along**, and set out. The choice and rewards still resolve through explicit Advance and return.

All numbers, practices and authored content remain provisional. These are working introductory specialization choices, not a claim that the complete attribute/perk/magic system is finished. The project adds no live AI, co-op impersonations, new recruit, combat, or hidden castle-history revelation.

## Earlier: 0.4 — A Proper Living Wing

A larger connected progression slice, keeping the modest, dim artwork and self-hosted stack.

- **Household ledger:** an accessible milestone checklist, three projects, placement controls, next-step suggestions and a readable principle notebook. Open it from the sidebar or castle floor plan.
- **Three practical improvements:** kitchen & dining nook (18 crowns, 2 work phases), washroom (18 crowns, 2 phases), and basic service wards (10 crowns, 2 phases; requires learned hearth wards). Funding assigns the scholar; switching work pauses other projects without losing progress.
- **Hearth kettle:** a heat-bearing component plus a vessel, using hearth knowledge; 2 crafting work phases. Install it in the restored washroom for warm water.
- **A Proper Living Wing:** beds, a comfortable common room, a kitchen, a warm washroom and basic services. The supplied sample already has beds and the common room. The milestone records automatically on Advance once all requirements are met, then offers a non-expiring celebration with Mira. No extra ceremony, fee or Resonance is needed.
- **Reedbank waystation:** waterworks survey notes reveal a second destination. Study storage seals to learn gentle preservation, or recover 3 binding thread, 2 porous clay and 12 crowns. As at the waterworks, one lead per visit, no expiry, and rewards only on return.
- **Pantry seal:** vessel plus binding component, using gentle preservation; 2 crafting phases. Install it in the restored kitchen to add 2 crowns per staffed garden surplus harvest. With the watering charm, this makes 8 crowns per harvest; silver-ivy production is unaffected by the pantry seal.
- **Copying commissions:** the scholar can copy and mend records for 4 crowns per Advance, with no prerequisite or material cost. This replaces their other work for the phase, and provides a way forward if the treasury is empty.
- **Migration:** existing saves upgrade to schema 4 after an automatic database snapshot. Old projects, discoveries, installed charms, accepted images and expeditions in flight are retained.

### Start exploring this expansion

1. Keep your current save and open **Household ledger**.
2. Complete hearth research if needed, then fund the living-wing projects in whichever order you prefer.
3. In the Workshop, craft a **Hearth kettle** from sun amber or fireglass plus porous clay. Return to the ledger’s **Washroom** panel to install it.
4. Once all five comforts are ready, press **Advance**. Mira’s celebration remains available in the ledger until you choose it.
5. Under **Beyond the walls**, survey the waterworks and return if you have not already. Select **Reedbank waystation** on the map, then bring its storage-seal discovery home.
6. Craft a **Pantry seal**, install it under **Kitchen & dining nook**, and choose staffed surplus sales in the Conservatory to use the bonus.

Both new artifacts have explicit craft/install/remove controls and prerequisite explanations. Installation takes no time and consumes no copy; a placed copy remains included in the completed-artifact count. Extra copies do not multiply bonuses. The new service spaces are represented as working ledger panels, not additional illustrated interiors.

## Conservatory charm placement in 0.3.2

The Conservatory now has its own Self-watering charm panel: craft a missing charm, install a completed one, or remove it. The panel shows placement status and explains the next staffed harvest bonus. Installation is free and takes no time. The Workshop placement control remains available.

Keep your existing `data` directory when updating; this patch uses the same save schema as v0.3 and v0.3.1.

## Crafting usability fix in 0.3.1

The workshop now lists every unmet prerequisite beside the crafting form, links to research or the expedition, explicitly selects an owned component, preserves material choices across redraws, and offers a Resume crafting action for a paused project. Crafting errors stay visible beside the form. The submitted recipe comes from the displayed form rather than a separate navigation variable.

For a warming lantern: complete Hearth-ward research, keep the scholar at home, select one heat-bearing material and one binding material, and press Start crafting. Advance twice while assigned to crafting. For a watering charm: survey the waterworks and return, then provide porous clay and a binding component.

This patch uses the same save schema as v0.3; keep your data directory unchanged. The regression test now submits both recipes through the registered submit handler using fields extracted from rendered HTML, rather than calling the crafting API directly. It remains a headless controller test, not real-browser QA.

## New in 0.3

- **Less opulent, less bright artwork:** all four rooms now use modest beams, plain stone, practical furniture, worn cloth and small pools of lamplight. Both Mira illustrations have simpler clothing and greatly reduced decorative trim.
- **Beyond the walls:** a persistent region map and one authored expedition to the old waterworks, with two distinct leads.
- **Consequential preparation:** a packed warming lantern reduces inscription work from two phases to one. Accessible salvage needs one phase with or without the lantern.
- **Return matters:** findings enter shared stores or the archive only after the return journey. You can turn back early; incomplete leads remain available. Completed leads cannot be farmed.
- **Discovery becomes useful:** the survey teaches water guidance, unlocking a self-watering charm. Craft it from a vessel material and a binding material; install it to improve staffed garden output.
- **Presence rules:** the scholar cannot perform castle work or in-person conversations while away. Mira's assigned work can continue. No remote communication is pretended.

### Try the new loop

Open **Beyond the walls**, optionally pack a crafted warming lantern, and set out. Advance to reach the waterworks, then choose an approach. Advance to finish its work, choose the journey home, and advance once more to arrive. The survey unlocks **Workshop → Self-watering charm**. Buy porous clay, choose a binding component, and craft the charm for two assigned work phases. Install it in the restored conservatory: staffed harvests become 2 ivy or 6 crowns rather than 1 or 4. Revisit for the other lead if desired.

The encounter is deliberately authored and deterministic; it is not a connected AI gamemaster. One solo location demonstrates the expedition-to-household loop, not the full exploration system.

## Earlier additions in 0.2

- **Restoration:** fund a conservatory and assign three work phases to unlock its interior and garden.
- **Assignments:** your scholar has one productive task per phase. Mira can follow her own routine, assist research, or tend the restored garden. Projects pause without losing progress.
- **Garden:** keep silver ivy for crafting or sell designated harvest for shared funds. Priorities persist, and forecasts explain the next Advance.
- **Practical magic:** learn hearth wards, then craft a warming lantern from heat-bearing and binding materials. Sun amber/fireglass and binding thread/silver ivy are interchangeable where their properties match. Display the completed lantern in the common room.
- **Readable phase results:** see exactly which work and production resolved. Buy or sell individual shared materials without automatic disposal of possessions.
- **Aesthetic:** midnight paper, warm violet, worn gold, hand-inked room artwork, and textured character illustrations. See `docs/AESTHETIC.md`.
- **Compatible saves:** v0.1 saves are backed up and migrated automatically.

## Upgrade from v0.1 through v0.10

Stop the old server. Back up its entire `data` directory (or Docker volume). Replace the application files with this version while keeping that data. Restart with the same data location. For Docker, retain the existing Compose project name/directory and volume, then run `docker compose up --build -d`.

The current v0.34 release uses state schema 33. Earlier migration history follows. Schema 21→22 adds unfunded personal content and waiting scenes for Iona while keeping established identity and gameplay intact. Schema 20→21 adds empty summoning and residency records plus the unfunded Courteous passage study; no contact is created during migration. Schema 19→20 copies the authored identities into each campaign and migrates any pending invitation into a named arrival reservation, without changing time, costs, assignments or relationships. Schema 14→15 adds empty lesson history and no casting plans, preserving existing assignments and learning projects without advancing time. Schema 12→13 adds empty personal wallets and possessions, zero allowances, a 20-crown discretionary treasury floor and the previous all-shared expedition arrangement; existing trips retain that arrangement. Schema 13→14 adds empty delegation records to work orders, without spending money, changing assignments or starting work. Schema 10→11 adds zero-rank personal skills, empty observatory checkpoints and an uninstalled Reading prism. Schema 11→12 adds the uncontacted optional resident, independent records, an empty arrival reservation and an uninstalled Binding press. These changes do not recruit anyone or grant discoveries. The schema-9-to-10 upgrade adds empty personal spellbooks, preparation and work records, and an unfunded ritual. It preserves existing housing, spells do not appear automatically, and no time passes. The earlier schema-8-to-9 upgrade adds the two unfunded accommodation projects, assigns each existing character a separate bed in the original chamber, and initializes reservations to zero. Existing draft journals are preserved. Earlier schema migrations still apply. Before a state-schema migration, the app creates `campaign-before-schema-N-to-33.sqlite3`, where `N` is the existing save schema (1–32). Keep the complete `data` directory, including artwork. Existing room choices, conversations, research/crafting/restoration progress, inventory, milestones, discoveries, character development, personal learning and expedition stages are preserved. No time passes during migration.

The schema-7-to-8 upgrade adds plain one-slot signature focuses, empty household/expedition configurations and no focus projects. Existing crafting, work orders, research, reserves, discoveries and active expeditions remain unchanged. Earlier saves also receive all preceding migrations, without advancing time. The original campaign is registered as `default`; its database and uploaded artwork stay at their existing paths.

When upgrading from v0.4 or earlier, the prior schema-5 development migration also credits the scholar’s documented accomplishments once. It does not guess Mira’s historical contributions or automatically prepare any practice. Existing crafting makers and expedition presence are retained; older artifacts without an explicit maker belong to the scholar. v0.1 saves retain the original starter-material grant.

The backup is a database snapshot, not a separate copy of uploaded images; retain the complete data directory when backing up. If rolling back to the old application, stop the server and restore its matching database snapshot too. Do not open a migrated save with the old executable.

## Start with Python

Install Python 3.12 or later. Extract this package, open a terminal inside `stonework-and-spellcraft`, and run:

```bash
python server.py
```

On Windows you can also use `py -3 server.py`. Open **http://localhost:8080** in your browser. Stop with Ctrl+C. Changes save automatically to `data/campaign.sqlite3`; imported illustrations go in `data/assets/`.

To serve devices on a trusted private network:

```bash
python server.py --host 0.0.0.0 --port 8080
```

Then visit `http://YOUR-SERVER-IP:8080`. This prototype serves separate solo sample campaigns and has no built-in login. Campaign selection is state isolation, not user authentication. Keep it on your private network, or put an authenticated reverse proxy in front of it. It is not intended for unauthenticated public internet exposure. A file share alone cannot run the backend; the host needs a Python process or Docker container.

## Start with Docker Compose

From the extracted directory:

```bash
docker compose up --build -d
```

Open **http://localhost:8080** on the host. The supplied mapping binds to host loopback, suitable for local access or a reverse proxy running on the host. To allow direct trusted-LAN access, change the port mapping in `compose.yaml` to `"8080:8080"` and restrict access with your host/network configuration. A containerized proxy on the same Docker network can reach `castle:8080`.

Stop with `docker compose down`. This retains the `castle-data` volume. Do not add `-v` unless you intend to delete that volume and its save.

The image runs as an unprivileged user and stores durable data at `/data`. Python's standard HTTP server is used for this private prototype; replace or front it appropriately before broader deployment.

## Try the prototype

1. Select **Common room**, **Library**, or **Guest chamber** on the floor plan. Interiors open directly.
2. Change a fixed-slot furnishing. The Furnishings & effects list updates; the room painting remains stable.
3. Open **Household** to meet Mira, an adult sample archivist, or click her portrait in a room.
4. Use scripted dialogue options. Free text is saved and explicitly receives a prototype notice, not a fabricated AI response.
5. Open **Wardrobe**, add or remove her plum shawl, and save a styling by name.
6. Join the optional tea invitation. It has no expiry and establishes a one-time playful development.
7. Put the plum velvet settee in the common room. With the development established, this enables the provisional passive Resonance rule.
8. Start the hearth-ward project under **Research**. It spends 20 sample crowns once and needs three work phases; Mira can assist. Only assigned characters contribute work.
9. Press **Advance**. Morning → afternoon → evening → next morning. Mira's location follows the phase; room lighting adjusts. A resolution summary appears.
10. Reload or restart the server. The phase and all committed choices remain saved. No offline time passes.
11. Under **Illustrations**, import a proposed correction, compare it with the accepted version, accept it, and restore the previous image if desired. You may record a correction brief for external generation.

## Scope and boundaries

Implemented:

- Illustrated selectable floor plan and four natural-perspective interiors, one unlocked through restoration.
- Fixed-slot furnishing variants; no freeform furniture movement.
- One consistent adult sample resident, two illustrated garment combinations, and named saved styling variants.
- Resident schedule, character-focused conversation, scripted choices, stored free text and optional reviewed OpenRouter NPC replies.
- Optional non-expiring invitations and descriptive relationship state.
- Four finite neighbour requests, reserve-aware deliveries, saved replies and a request-unlocked expedition route.
- Explicit phase advancement, research, restoration, assignments, garden production, nine component recipes with either maker, four branching expeditions with an optional companion, three living-wing facilities, copying commissions, a household milestone and celebration, a shared principle archive, and a transparent experimental Resonance rule.
- Personal character advancement, archive study, prepared practices, retraining and Mira’s authored personal project.
- Three further research projects, useful utility installations, reserve-aware garden priorities, protected stock and persistent workshop orders.
- Server-authoritative, transactional SQLite saves; revision checks across tabs; idempotent request retries.
- Illustration import, comparison, acceptance, version history, rollback, and saved correction requests.
- Independent solo campaign slots, per-tab campaign scope, restorable database/artwork ZIP backups, readable JSON export, Docker configuration, tests, and source documentation.
- Personal signature focuses, four inscriptions, a capacity upgrade, per-character focus work and separate household/expedition preparation.

Deliberately not implemented in this visual slice:

- A complete generative gamemaster, validated generated game-content proposals, or live image generation. Optional reviewed NPC prose is available.
- Co-op, Eris/Selene tools or readiness gates, or fake agents impersonating them.
- A complete attribute/perk/affinity catalogue, a complete construction catalogue, recruitment, free-form magic invention, a full expedition catalogue, or an opening campaign.
- Co-op campaign creation, campaign-mode conversion, login, or JSON import.

The furnished wing and Mira are explicitly sample content. Mira is not the finalized first recruit. The character, research project, 80 starting crowns, costs, room choices, and Resonance numbers are prototype decisions, not new campaign canon. An adult resident's style choices are presented as agreed options; this does not create a general player power to override her preferences.

## Saves and backups

For the Python launch, stop the server and copy the entire `data` directory. Restore by replacing that directory while the server is stopped. Keep artwork and the database together. Back up the Docker volume using your host's volume backup tools while the container is stopped. The app does not currently schedule backups. For one selected campaign, **About & saves → Download restorable save & artwork** produces a consistent SQLite snapshot without stopping play. Restore with the server stopped, following the ZIP’s `RESTORE.txt`. To preserve every slot together, back up the whole data directory while the server is stopped, including `campaign-registry.sqlite3`, the original `campaign.sqlite3`/`assets`, and `campaigns/`. Each additional slot has its own database and assets under `campaigns/c-…/`. A single-campaign ZIP can also be extracted into a fresh empty data directory and opened as that server’s original campaign. It does not bundle the application’s built-in artwork; use this application release or newer.

**About & saves → Download a readable campaign snapshot** exports JSON for inspection. It is not a full backup: uploaded artwork and request-retry records are separate, and there is no snapshot-import interface.

Data directory, host and port are configurable by arguments or these environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `CASTLE_HOST` | `127.0.0.1` | Network address the server listens on; Docker uses `0.0.0.0` inside its container. |
| `CASTLE_PORT` | `8080` | HTTP port. |
| `CASTLE_DATA_DIR` | `./data` beside the server | Save database and imported art; Docker uses `/data`. |

The app assumes it is served at the root of its own origin, such as `https://castle.example/`, rather than under a `/castle/` subpath.

## Source map

| File | Responsibility |
|---|---|
| `game.py` | Explicit game variables, sample content, validations and phase resolution. |
| `server.py` | HTTP API, SQLite transaction boundary, request deduplication and local image uploads. |
| `static/app.js` | View templates and interaction controllers. |
| `static/style.css` | Responsive layout, typography, room layers and lighting. |
| `static/assets/` | Bundled generated artwork; no runtime image downloads. |
| `docs/VARIABLES.md` | Human-readable state definitions and units. |
| `docs/PROTOTYPE_DECISIONS.md` | Confirmed requirements versus provisional implementation choices. |
| `docs/ARTWORK.md` | Artwork locations, generation method and prompt set. |
| `docs/design_spec_v0_1.md` | Original supplied specification, unchanged. |
| `tests/` | Rule, persistence, HTTP and headless controller checks. |

## Verification

From this directory:

```bash
python -m unittest discover -s tests -v
```

Optional developer checks with Node.js (not needed to run the game):

```bash
node --check static/app.js
node tests/test_ui.cjs
```

Verification at this development checkpoint: 247 Python tests passed and JavaScript syntax passed. The headless controller playthrough checks 24 views at home and with Mira away; all eleven recipes use fields extracted from rendered forms. It follows the three research branches through crafting and installation, exercises stock-first automated production, learns a principle with the tablet, and plans/purchases/starts/completes a two-copy work order without automatically starting the second copy. It also accepts/defers/delivers a neighbour request, reads its reply, surveys the newly opened nursery, crafts and installs a capillary mat, verifies protected delivery controls, joins both optional scenes and reloads their saved state. Earlier living-wing, character, resident-story and party-expedition flows remain covered.

Rules tests cover prerequisite validation, one-time funding and awards, paused research, personal mastery after absence, reserves versus explicit crafting, automated/staffed harvest exclusivity, unchanged inventory during surplus sales, copying and study bonuses, duplicate-component counts, exact purchase prices, insufficient-funds atomicity, request retries, persistent orders and migration of schemas 1–9. Additional rules tests cover all four deliveries, exact rewards, installed/packed artifacts, reserve protection, duplicate delivery rejection, the nursery’s early return and one-time salvage, companion knowledge, mat output, scene presence and reward invariants. The schema-6 fixture includes an unfinished work-order copy; its automatic snapshot, continuation, delivery retry and reload are verified. The schema-5 fixture includes active learning and an unfinished artifact. HTTP checks use a real temporary local server. New tests cover per-campaign state/action/export/artwork/conflict isolation, concurrent creation retries, unsupported co-op rejection, preservation of the original save, backup extraction and reopening on a fresh server, image rollback history and missing-image backup rejection. Focus tests cover personal prerequisites, component quantities, cost atomicity, pausing, absence, capacity, preparation, work bonuses, non-stacking return-only salvage benefits and schema-7 migration. The rendered UI flow inscribes and upgrades a tool, prepares it, reloads, and retries campaign creation after a simulated lost response without making a duplicate.

Browser rendering/layout and Docker build/runtime could not be exercised in the creation environment. The controller test uses a minimal DOM adapter and the actual Python save/rules layer; it is not a substitute for real-browser QA.


### Optional provider verification

Tests cover settings validation and key retention/removal, owner-only settings permissions, secret exclusion from model context and campaign backups, nonmutating generation, idempotent acceptance, stale revision rejection, campaign isolation, failed/disabled/away requests, concurrent checks of an in-flight request, bounded transport payloads and unusable provider replies. Local HTTP and headless UI flows cover settings, escaped preview, saved draft recovery and acceptance. These use controlled provider responses; no external account was contacted.

API implementation reference: [OpenRouter chat completions documentation](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request). The app uses the fixed HTTPS chat endpoint with bearer authentication, explicit model selection, messages and a maximum output-token count.

Housing tests cover prerequisite and cost validation, paused restoration, reservations, bedroom capacity, evening location, independent furnishings, absence, idempotent funding and schema-8 migration. The UI playthrough restores both chambers, reserves and releases a bed, selects Mira’s bedroom, opens the restored room and verifies persistence after reload.

Spellcraft tests cover free drafts, property substitutions, duplicate component quantities, personal knowledge and room prerequisites, costs, pausing, cancellation/refunds, one-shot exact production, preparation capacity, independent owners, away-state restrictions, cooperative ritual contributions, schema-9 snapshots, retries and reload. Dialogue tests verify only Mira's tested spells enter provider context. The headless playthrough uses rendered form fields for all three forms and the ritual, exercises both characters, room casting controls, character-sheet navigation, escaped prose and persisted preparation. Real browser layout/painting and Docker runtime remain unverified; a local Playwright launch could not run because its browser executable was unavailable. No live paid provider request was made.

The expanded connected playthrough additionally covers both Rainward leads, saved partial fieldwork, the recoverable lens complication, personal skill training, the Reading prism and fourth spell, recruitment through private-bed reservation and arrival, Tamsin’s independent notebook and Binding press, her saved wardrobe and optional scenes, and per-resident generated-draft recovery/acceptance. See `docs/IMPLEMENTATION_STATUS.md` for remaining design work. Headless tests do not verify browser painting or Docker runtime behavior.

Delegation verification covers bounded spending and refunds, protected stock, zero-budget pauses, resident work during travel, personal knowledge and roster checks, manual-workbench contention, assignment changes, one-copy-per-phase limits, revocation, migration and idempotent funding/reload. The rendered UI playthrough exercises agreement forms, pause/resume, explicit top-up and exact completion refunds.

Lesson verification covers personal ownership, advancement reservation, two-person work, pause/resume, absence, resident-pair work during travel, cancellation, overbooking, teacher retraining, migration and safe retries. Casting-plan checks cover exact finite outputs, protected stock, independent assignments/preparation, own-spell requirements, manual work conflicts, resident work during travel, no same-phase input chaining, competition for supplies and persisted idempotent counts. The connected interface playthrough exercises both systems and Workroom notes.

NPC update: Mira (22), Tamsin (25), and Iona (23, demon) have revised portraits. Existing campaigns migrate automatically; previous custom portraits remain in artwork history. See docs/designs/SUMMONING_DESIGN.md for the standing age, diversity and exotic-summoning rules.

Iona’s conversations: open Summoning during her visit or household stay for four authored topics, a saved personal line, or an optional reviewed NPC draft. Her remembered conversations and crossing history remain readable while she is away. Generated replies require your configured provider; authored conversations work entirely offline.


### Three exotic contacts — v0.28
Open Summoning and select Iona (23, demon surveyor), Aurelia (24, seraph lantern conservator) or Neris (21, water elemental glassworker). Each introduction costs 12 shared crowns, one vessel and one binding component, plus two conductor phases. The conductor must know Courteous passage. One unfinished contact preparation per conductor; different conductors can work independently. Reopening an established contact is free and keeps the same person.

Aurelia needs a private one-bed room. Iona and Neris accept their own bed in a shared chamber. Existing occupants are never displaced. All three have distinct starting knowledge, authored introductions and flirtatious conversations, individual character records, portraits and optional reviewed text replies. Shared work, study, focuses, spells and allowances become available only after both sides agree to membership. New ancestry artwork does not create unlisted powers.

Aurelia’s current portrait uses the requested warm-tan skin revision. Both new portraits follow the handmade violet-and-midnight aesthetic with glamorous fitted clothing and playful adult presentation. No API is needed for artwork or authored conversations. Aurelia and Neris now offer personal studies, two illustrated ensembles each, named saved styles and optional illustrated household moments. Existing schema-23 saves load directly; old unfinished summoning preparations still lead to Iona.


### Companion life expansion — v0.28
Use **Her project**, **Clothes & saved styles**, or **Invitations & shared moments** on Aurelia’s or Neris’s room card. These also appear on her character sheet and Summoning contact. All choices are explicit; browsing and styling do not advance time.

Aurelia’s lantern study costs 12 crowns, 1 fireglass and 1 binding thread. Neris’s glass study costs 10 crowns, 1 fireglass and 2 porous clay. Each takes three own work phases and earns the worker 2 advancement plus a personally understood principle recorded in the archive: Luminous copying for Aurelia, Gentle refraction for Neris. Existing related artifacts still require separate crafting and installation. Pausing preserves work; cancelling unfinished work returns the exact committed costs once. These projects block departure while funded.

Both companions offer an everyday and an evening ensemble, with up to eight named style presets. Their wardrobe choices and completed illustrated moments survive departure, return and reload. Nine new optional scenes include individual invitations, mutual teasing, shared friendships and return greetings. Invitations never expire; leaving them for later has no penalty. The quiet household notice helps you find them.

Schema 24 adds project/wardrobe defaults and new waiting invitations to old saves without spending money or time. See docs/DESIGN_PROGRESS.md for the full-design coverage estimate and the still-unimplemented systems.


### Reviewed visitors — v0.28
Summoning now offers **Propose & review a new visitor**. A configured text provider produces a bounded adult exotic candidate proposal. Review her identity and exact starting package before approving a durable contact plan. Approval spends no ritual costs and creates no resident. Fund the normal contact separately; visiting, membership and work still require their own agreements. Visit-only preferences are enforced. Recheck a stale proposal without another model call. New portraits remain explicitly pending until imported in Illustration review. See docs/designs/CANDIDATE_REVIEW.md for the workflow, validation, recovery and limitations. Schema 25 preserves existing progress and introduces an empty plan catalogue.


## v0.29: individual builds and persistent castle evidence

Character sheets now offer Insight, Dexterity and Resolve; Light, Growth and Hearth affinities; and six earned specialization perks. Advancement costs and own learning phases are explicit. Work breakdowns and personal spell results include the real bonuses. Cancellation releases reserved points, and retraining checks the resulting spell capacity before changing a build.

Castle history now provides a versioned sample mystery with four phased investigations, saved evidence, one-time advancement and explicit resident-specific sharing. Undiscovered lore is excluded from ordinary public responses and diagnostic JSON. Complete restoration backups retain it and can contain spoilers. This is labelled prototype history, not the finalized opening or first recruit.

Schemas 26–27 preserve existing progress. 306 Python tests and five connected headless UI suites pass. Live providers, rendered-browser layout, Docker execution and real external agents remain unverified. The full design is still incomplete; see the requirement checklist in docs/DESIGN_PROGRESS.md and the detailed designs in docs/designs/CHARACTER_BUILDS.md and docs/designs/CASTLE_MYSTERY.md (paths relative to the project root).


## v0.30: specialized care, release and estate capacity

The main solo castle can now be restored to 25 non-founder places plus the founder. An optional 25-place annex requires separately funded access/services and separately fitted rooms. Named arrivals and regional ceilings are enforced. Private-room preferences now apply to every character's bedroom move. New rooms use explicitly labelled representative illustrations with independent furnishings and correction histories. Reviewed candidate plan capacity is fifty.

Schemas 28–29 preserve prior saves. See `docs/designs/CONTAINMENT.md`, `docs/designs/ESTATE_CAPACITY.md` and `docs/CONTAINMENT_ART.md` (paths from the project root). Real browser layout, Docker, live providers and actual Eris/Selene integration remain unverified; the whole design is not complete.


v0.30 verification: **327 Python tests and seven connected headless UI suites pass**, including the full 50-resident capacity fixture, containment release/recruitment and annex construction. JavaScript syntax passes. No live-provider, rendered-browser, Docker-runtime or real-agent success is claimed.


## v0.31: curated people, personal stories and golem awakening

Open **People & arrivals → Propose & review a new visitor**. Choose an ancestry or arrival path and optional compatible background, temperament and story seed. Offline composition works without a provider; model-written prose remains optional. Review identity and exact capabilities before approval. Ordinary recruits open free correspondence, exotic beings use the existing contact ritual, and golems use construction and awakening. Membership remains a separate two-sided decision.

Implemented common ancestries: humans, fair forest high elves, chocolate-skinned dark elves, subterranean drow and catfolk. Exotic pool: demons, seraphs, elementals, vampires, fae, djinn, dragonkin, spirits, dryads, nymphs and kitsune. Golems are constructed in clay, porcelain, stone, living wood or enchanted metal. The golem age field describes an adult form; they awaken fully adult with no invented lived years. Aurelia's terminology changes to seraph without changing her portrait.

Open **Personal stories** for offline or reviewed model-written ambitions. Approval creates an offer, funding starts exact-cost personal work, and completion opens a non-expiring optional scene. Pause, resume and exact unfinished-work refunds are supported. Generated household members can use the same system.

This release uses schema 30. Existing saves receive a pre-migration SQLite backup and retain progress. New generated characters use portrait placeholders until a reviewed illustration is imported. Full co-op, real agents, automatic image generation and the complete general gamemaster remain unfinished. Detailed rules: `docs/designs/CHARACTER_POOL_AND_ARRIVALS.md` and `docs/designs/PERSONAL_STORIES.md`.


v0.31 verification: **350 Python tests and nine connected headless UI suites pass.** Coverage includes real HTTP draft/review routes, offline generation, route separation, golem funding and awakening, retries, migration, personal stories, refunds, membership and persistence. JavaScript syntax passes. These are not rendered-browser, live-provider, Docker-runtime or real-agent acceptance tests; those remain unverified.


## v0.32: ancestry expansion and illustrated local introductions

Added common bovinefolk, orcs and wolfkin, plus exotic oni. Four named adult characters now have individual bundled portraits: Maren (24), Brakka (25), Fenna (22) and Kaede (24). Open **Local introductions** for phased meetings and a threshold letter, unlocked by actual restoration, returned discoveries or passage knowledge. Ordinary introductions still require separate visits and membership; Kaede uses the normal exotic ritual.

Three optional earned ancestry perks express controlled strength, sustained story work and keen observation. They use existing advancement and training requirements and display bounded effects. Two new personal-story chapters unlock from completed work and scenes actually shared, retaining references to earlier accomplishments. Neither previews nor deferred invitations count as shared history.

Schema 31 preserves prior campaigns. See `docs/designs/LOCAL_CAST_AND_ANCESTRY_TRAINING.md` for exact costs, effects, lead prerequisites and limits; `docs/LOCAL_CAST_ART.md` records built-in image prompts and the four portrait paths. Broader procedural encounters, semantic prose validation, full co-op and actual agent integration remain unfinished.


v0.32 verification: **358 Python tests and ten connected headless UI suites pass.** JavaScript syntax passes. The new local-introduction suite covers portraits, pause/resume, ordinary correspondence, two-sided membership, ancestry training display, shared-history chapter unlocking and persistent continuity. No rendered-browser, live-provider, Docker-runtime or actual-agent success is claimed.
