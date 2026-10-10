# v0.118 — Chapel companion, world recruitment and interface repairs

Merrin (`merrin`) is a fully authored adult spirit companion discovered by restoring the chapel. Her three-exchange introduction leads to an ordinary agreed trial visit, a private bedroom and a separate household decision. She is never generated as a bandit or rescue target.

Her content includes four household scenes, three continuing social conversations, personal disclosures, remembered player preferences and follow-ups, a three-part conversation with Mira, a joint reading-copy keepsake, resident bonding, four romance milestones and eight non-graphic closeness scenes. Private intimacy fades to black. Friendship does not require romance. Pausing romance also prevents private invitations and Foundation rituals.

She has a personal quest to recover and repair a comic play, a paid register-repair project, the chapel sanctuary improvement, signature-equipment fitting and refinement, three field disciplines with nine trainable talents, expedition reflections and camp conversations. She uses the existing work, training, equipment, housing, friendship and save systems. Her ancestry gives the existing Spirit trait; her spectral appearance grants no free passage through obstacles or combat immunity.

Four distinct portraits show her everyday, evening-dress, daring and bathing clothing. All use the generic Spirit illustration's pearly, translucent appearance and retain her short dark bob and ordinary slender build. The first three have matching overview images. The second wardrobe tier is **Plum evening dress**. The third is **Plum halter and wrap skirt**, with a cropped halter top and short wrap skirt. Bathing is a separate room-dependent appearance. Outfits retain the normal memory and invitation requirements. Both individual recruitment and **All remaining unique companions** in Cheats include Merrin exactly once.

## World recruitment

The ordinary **Review a new visitor** authoring screen is replaced by **Recruitment quests & contacts**. After Chapter 4, a scholar phase spent collecting local reports saves a rescue or capture quest. New reports are available once per day; at most three unfinished leads remain open. Reading and reloading do not reroll a saved identity. The request takes an actual assignment and can be paused, resumed or cancelled.

Common ancestries normally appear. Each report or random ordinary patrol raider has a **1% exotic ancestry chance**. Golems and spirits are excluded from both encounter types. Dryads and nymphs are rescue targets only, never bandits. Bovinefolk is excluded from the new encounter pool while its replacement remains undecided.

There are 19 bandit portraits and 21 separate rescue portraits. Elementals have water, fire, earth and air variants in both sets. Kitsune and animal-eared illustrations have no human side ears. A rescue still needs the journey and safe return. Captured bandits need a free Quiet chamber, an actual surrender, discussion and release before a voluntary introduction. No quest automatically recruits someone.

Magical invitations create one saved identity for an exotic ancestry; the existing paid summoning process is still required. Golem plans retain construction and awakening. Custom identity authoring is available only with Cheats enabled, including backend review and acceptance checks. Accepting a custom plan marks the save as modified.

## Interface and reference

- All 30 creatures have ranks: 11 Standard, 14 Intermediate and 5 Difficult. The bestiary sorts by rank/name and supports rank filtering. Unlearned combat advice remains hidden.
- Every expedition destination card uses its corresponding location artwork in a consistent frame.
- The day number sits beside the phase indicator. Explicit resident portrait icons no longer receive a second automatic icon beside the same name.
- Settings & artwork describes the current nine-chapter build. Text and portrait API settings are both available there.
- Text supports OpenAI-compatible chat, Anthropic Messages and Gemini generateContent. Images support OpenAI-compatible base64 images, OpenRouter chat images and Gemini images. Each has a complete endpoint, model and authentication setting; compatible local endpoints are supported. This is not a universal adapter for arbitrary proprietary APIs.
- Changing endpoint or format clears the previously stored key unless a new one is supplied. Keys are absent from public settings and campaign exports. Saving a configuration makes no model request. Provider tests use mocked responses; no paid live provider calls were made.
- **Portrait description · optional** explains that saving descriptive text does not replace or generate artwork.
- Help documents recruitment, encounter exclusions, named companion discovery, Merrin, outfits, APIs and Cheats. See [the companion recruitment guide](COMPANION_RECRUITMENT.md).

## Save and delivery

Schema 75 adds empty report and chapel-discovery records. Existing residents, artwork overrides, memories and campaign progress remain. Merrin's optional systems initialize through their established lazy state. Extract into a clean folder and preserve the complete old `data/` directory if needed; restart and hard-refresh.

The full game archive excludes live campaign data, caches and source-art masters. The companion source archive contains only v0.118 artwork masters, prompts and references; previous artwork archives remain separate. This package has not been deployed. Automated rules, real HTTP routes and connected template/controller tests are recorded in `VERIFICATION_V118.json`; no rendered desktop/mobile layout review or exhaustive balance claim is made. Eris/Selene co-op remains deferred.
