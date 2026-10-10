# v0.116 — Resident identity, accommodation and scripted solo play

Oni is now **Ogrekin** (ancestry ID `ogrekin`), a common ancestry reached through ordinary introductions. Kaede remains the same person; meet her through the valley glassworks after completing the first hearth-ward study. No summoning ritual is required.

The castle has one Ember chamber and one Quiet chamber. The full map now contains 53 locations across its existing five views. Bedroom cards list assigned residents, independently of where those residents currently are. Quarters list their occupants, and character profiles show their bedroom, parent quarters and anyone sharing it.

Each ancestry grants one modest +1 bonus to a named capability check. Profiles, the ancestry catalogue and check explanations identify it. It does not raise base attributes, grant advancement or multiply relationship gains.

Koharu replaces Maren, including internal ID `koharu`. She remains associated with the workshop. She is a slight-built adult kitsune stage-prop restorer with dark chestnut hair worn down, matching dark fox ears and tail, and no human ears. Her dialogue, tastes, ambitions, personal project and Stagecraft path reflect her new identity. She is already local, so her opening introduction does not require an exotic crossing ritual. All four portraits were created without using Maren's art.

Koharu, Tamsin and Fenna have corrected ear anatomy across all three outfits and bathing portraits. Kitsune, Catfolk and Wolfkin ancestry illustrations and thumbnails are corrected too. Tamsin and Fenna retain their original character designs and tousled hairstyles; broad glamour-hair revisions were rejected. Bathing cutouts retain their alpha channels. Artwork descriptions explicitly prohibit human side ears for these three ancestries.

Solo play needs no LLM gamemaster. Candidate creation supplies coherent hobbies, values and difficulties; eligible created residents have three-response conversations and saved callbacks. The existing contact, visit, accommodation and joining sequence remains authoritative. Personal-story preparation and an exact account of the last phase work offline. Optional model-assisted writing remains available. See `SCRIPTED_SOLO_V116.md` for the original gamemaster responsibilities and their implementations. Eris/Selene co-op remains deferred.

Help explains ancestry bonuses, accommodation and scripted solo play. Cheats use the consolidated chamber catalogue and Koharu's new identity. Bovinefolk replacement is pending the user's choice among proposed candidates; no ancestry was selected on the user's behalf.

## Installation and saves

Extract the complete ZIP into a clean directory. Preserve the entire old `data/` directory if keeping a save. Run `python server.py`, restart any old server and hard-refresh the browser. Confirm v0.116 on the title screen or `/api/health`. No hosted deployment is included.

Schema 73 updates the authored identity and chamber records once. Earned character progress is retained on Koharu's new baseline. Duplicate completed chamber fittings are consolidated with their fixed costs returned; unfinished work is preserved where possible. Existing automatic migration backups remain available. Old custom art for the replaced character is kept in backup storage rather than shown as Koharu.

## Verification

The rules and narrative regression runs passed 171 and 65 tests respectively, with the seven release-specific tests appearing in both runs. Connected UI checks cover map routes, live accommodation moves and reload, profile and quarters occupancy, ancestry display, offline creation and visitor dialogue, journal acceptance, wardrobes and the build workspace. The final 95-test regression run also passes after the Ogrekin change, with 274 tests across the combined module set and six connected UI suites. Final asset checks validate every artwork reference, hash, size and cutout transparency.

The images were visually compared with the existing portraits and ancestry style. Connected UI behavior is tested through the shipped JavaScript and real Python game stores. Rendered desktop/mobile browser layout remains unverified because no browser renderer is installed.

The separate source archive contains final full-resolution masters and generation/edit prompts. Only display-sized WebP artwork belongs in the game package. See `ART_V116.json` and `VERIFICATION_V116.json` for exact records.

## Portrait file-size update

All 28 Koharu, Fenna, Tamsin and Zahra display portraits now use high-quality WebP compression (quality 92, method 6) instead of lossless export. Their combined size falls from 34.40 MB to 9.44 MB (72.6% smaller). Artwork and image dimensions are unchanged; the four bathing alpha channels are byte-identical. No portraits were regenerated. Original lossless exports are retained in the source archive. See `PORTRAIT_COMPRESSION_V116.json` for each file and its hashes.
