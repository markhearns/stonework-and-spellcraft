# v0.92 — Companion portraits, room specialties and bathing outfits

- Removed Veyra from recruitment, authored identities, quests, conversations, relationships, equipment, personal paths, group content, art catalogues and portrait assets. No save migration for her is included.
- Preserved all twelve shared household stories: Sabine joins the supper story, Maren the evening watch, and Elowen the lantern fair. Their casts and callbacks agree. Aurelia now shares the lamp conversation with Maren; Neris and Elowen discuss their different preferences in the window-and-tea conversations.
- Fixed authored portraits being overwritten by a generic reviewed-candidate placeholder after recruitment. Iona, Aurelia, Neris and Sabine retain their own art.
- Overview now exposes room specialty, exact benefit, installation state, project progress and unmet requirements. Directory cards show the associated room. Mira’s living index has its own Library explanation.
- Adjusted authored ages: Tamsin 20, Brakka 23, Sylva 21, Velis 22, Rhess 24. All companions are adults. Schema 65 changes only those old authored ages of 25 and preserves custom ages.
- Added fifteen optimized WebP bathing portraits. All wear period-inspired, opaque two-piece cloth wraps and are barefoot. The image service rejected the topless variant; covered variants were used.
- Appearance is derived from actual room presence during Rest, in a restored pool, sauna or hot springs. Work, travel and leaving the room restore normal art without altering wardrobe progression or saved outfits. Opening a room page alone does not change anyone’s clothes.
- Overview combines bathing art with the actual room illustration. Style and Help explain the automatic behaviour and afternoon leisure preference.

Current roster: fifteen unique companions, plus the player. Existing gameplay systems remain available, including all seven chapters, 48 personal paths / 144 talents across the player and companions, 60 personal chapter scenes, and 120 intimacy scenes (four repeatable plus four milestones for each companion).

## Verification

See VERIFICATION_V092.json. Checks cover actual location changes, restored-room requirements, working/away companions, read-only appearance calculation, all roster art, portrait resolution, room specialty panels and existing gameplay/controller regressions. These are automated checks, not a browser-rendered layout review.

## Art

BATHING_ART_V092.json records the built-in generation prompts, dimensions and optimized file sizes. There are no live campaign saves or provider credentials in the archive.
