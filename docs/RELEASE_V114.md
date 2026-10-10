# v0.114 — A more useful progression, and Zahra

This is the complete game, including the earlier companion dialogue, resident friendships, castle investigations and optional intimacy ritual. It is an installable release, not a deployment to a hosted server.

## Progression

| Point in the campaign | Current behavior |
| --- | --- |
| Chapter 1: The First Hearth | Review and wear ordinary field equipment, then learn, prepare and cast Warm-twist binding through the regular rules before the first journey. Testing and casting consume their stated resources. |
| Chapter 2: The House Takes Shape | Finish one chosen undertaking and its closing scene to continue. The other two remain useful optional projects. The conclusion credits only completed work. |
| Chapter 3: Room to Grow | Choose private, shared or mixed bedrooms and a specialist facility. Use the existing common room, or choose an additional chapel or sauna. Required construction, prices and walkthrough stops follow that plan. The lower passage introduces the foundation mystery. |
| Chapter 4: Keeping the Hearth | Prepare the entrance, stores and training yard. Driving intruders away requires no dungeon. Capture or escorted parley first adds the care facilities that those choices need. Paid work remains available if the plan changes. |
| After Chapter 4 | A short local road patrol becomes available. Its pool contains wolves and lantern moths; extended routes, raiders, bounties and special operations wait until after Chapter 7. |
| Chapter 5: Arms of Our Own | Advanced equipment and field calibration retain their existing role. Completing the chapter now opens the foundation investigation. |
| Beneath the Hearth | Restore and test the foundation ritual chamber during the middle of the campaign. The optional ritual keeps its one-phase fade to black, +20% positive household relationship gains, nine-phase duration and non-stacking renewal. Completing the investigation requires no intimacy. |
| Chapter 6: The Roads We Keep | The caravan, Supply Office and roadside refuge follow equipment preparation. Recruitment remains a separate decision. |
| Chapter 7: The First Patrol | Rhess can join the wardstone expedition as an agreed guest ally. Recruitment is an alternative, not a chapter requirement. The guest agreement gives no general workforce access. |
| Chapter 8: The First Real Test | The supply-road defense follows the shared watch. Guidance explains full recovery, protective equipment and guarded strikes for solo parties. |
| Chapter 9: The Survey Rooms | Follow the foundation connection, compare the register with the founding evidence, test the reference plate and verify the closed crossing controls. Four tasks take seven assigned phases. Three closing choices preserve the findings for different purposes and award two advancement points once. No portal is opened. |

Resident friendship traditions now become available at 60 bonding. The earlier stages remain at 10, 25 and 45; cooperation improves at 70. Reaching a threshold offers an activity rather than inventing a past event.

## Zahra

Zahra replaces Brakka with the new internal ID `zahra`. Per the requested fresh-start scope, there is no Brakka-to-Zahra save migration or old character-ID alias.

She is a 23-year-old Djinn precision smith associated with the same **smithy**. Her design is short (155 cm), softly curvy and non-muscular, with warm brown skin, amber eyes and black curls that dissolve into smoke and small ember lights. Her limited ember magic complements careful measurement; it does not grant unrestricted wishes or replace practical work. She wants to build a small clockwork instrument and teach apprentices how to control heat.

Her ancestry, arrival, profile, physical details, attributes, focus, starter equipment, dialogue, personal paths, quests, room improvements, resident-pair content and artwork references use the new identity. Her contact follows the normal exotic summoning route after the conservatory is restored. She knows Warm-twist binding, which still needs normal preparation and casting supplies.

Four completely new portrait masters follow the Djinn illustration in Creatures and Peoples. The runtime has three wardrobe portraits in standard and overview sizes, plus a transparent bathing portrait. The seven old character images are removed. All 391 other runtime images are byte-for-byte unchanged. Full-resolution masters are in a separate source-art archive.

## Installation

1. Extract the complete release into a clean folder.
2. With Python 3.12 or later, open a terminal in `stonework-and-spellcraft` and run `python server.py`.
3. Open `http://127.0.0.1:8080/`, choose **New game → Fresh beginning**, and hard-refresh an already open browser tab.

The archive contains no live campaign data. The application reports v0.114 and uses schema 72. No old saves need to be transferred for this requested release.

## Verification

Two complete, earned-resource campaign routes reach the new Chapter 9, with a serialized reload after actions, zero unfed days and no cheats. One uses Rhess's guest alliance and solo Chapter 8 outings with crafted protective equipment; the other recruits a larger household. The foundation chamber is completed after Chapter 5 in both routes, without performing the ritual.

The checks also cover optional construction, capture and parley, all companion conversations, pair bonds, outfits, the new identity, exact ritual duration, chapter rewards, interrupted work, retries, and the Spells & Rituals link. 331 Python tests and 18 connected UI suites pass. Exact module counts and scope are recorded in `VERIFICATION_V114.json`.

Connected interface tests exercise HTML templates and click controllers against the real Python GameStore. No rendered desktop/mobile browser inspection or audio-performance review is claimed.
