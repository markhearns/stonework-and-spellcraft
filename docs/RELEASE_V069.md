# v0.69 — Getting to know the household

All fourteen authored adult companions now have a Profile tab, personal disclosures, an individual initiative and a central role in a three-conversation NPC relationship arc. The release adds 77 conversation beats: 42 disclosures, 14 initiatives and 21 NPC scenes. Disclosure responses use shared conversation framing around character-specific facts.

## Progressive profiles

At introduction, profiles show age, ancestry, height, approximate weight, build and dominant hand. Measurements account for the character's established physique and anatomy, including wings, tails, horns and elemental embodiment. These are approximate descriptive details, not ability bonuses.

- **Getting to know her:** habits, personal history and comforts. Opens at trust 2 or mutual attraction, then requires sharing the conversation.
- **In her confidence:** bust/waist/hip measurements, anatomical fit notes, vulnerabilities and preferred affection. Requires the first disclosure and either trust 4 plus respect 2, or a mutual first date. Friendship can reach this tier without romance.
- **Private affection:** adult attraction preferences, turn-offs and a personal admission. Requires the trusted disclosure and an established mutual partnership with romantic invitations open.

Undisclosed facts are omitted from public profile data and optional dialogue context. Previously shared facts remain remembered if romance pauses. Preferences describe the individual; they do not grant permission for an interaction. Generated residents and the founder retain their existing information without invented authored measurements.

## Living castle

Home and room visits now show phase-aware idle activities, current work, and contextual recollections grounded in actual spell use, expedition participation or remembered conversations. These descriptions respect existing assignments and locations. They do not simulate new work or alter schedules.

Conversations appear in companion workspaces, Home invitations and the combined journal. They require the actual participants to be home. Curious, warm and candid responses remain available and contribute once to trust, affection or respect respectively. NPC scenes also develop the pair's own relationship. Memories count toward existing relationship progression, including wardrobe and romance milestone evidence. Sharing a scene spends no phase, money or materials. Deferred invitations can be restored.

## Verification and upgrade

Automated rule, migration and connected UI checks are recorded in `VERIFICATION_V069.json` and `UI_REGRESSION_V069.json`. The new checks cover all fourteen profiles, progressive disclosure, friendship and romantic gates, all seven NPC arcs, actual presence, duplicate requests, reloads and preservation of campaign assets.

No rendered browser review was possible: the cloud browser blocked the local server and local browser binaries are unavailable. Connected UI tests exercise controllers using a DOM test double, not a real mobile or desktop rendering engine.

Stop the old server, replace application files, and retain the **complete existing `data` directory, including `data/assets`**. Run `python server.py`. Schema 58 adds empty companion memory records and automatically backs up a schema-57 campaign before migration. All existing bundled artwork and spell icons are retained. This ZIP does not include a live campaign or deploy the game.

