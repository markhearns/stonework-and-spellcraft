# Seven-chapter flow and sleep audit

Two continuous routes used normal actions, earned crowns, actual equipment and save/reload after actions. One chose the ordinary Chapter 7 methods; one used prepared methods and Rhess’s contribution. No testing grants were used. Counts exclude preview simulations. These are simulated days and player actions, not measured human minutes. Optional personal quests, romance, reading time and free exploration are excluded.

| Chapter | Advances, route A / B | Copying-income advances, A / B |
|---|---:|---:|
| 1 | 25 / 25 | 5 / 5 |
| 2 (all three undertakings) | 70 / 70 | 28 / 28 |
| 3 | 28 / 33 | 16 / 19 |
| 4 | 54 / 42 | 28 / 24 |
| 5 | 49 / 53 | 20 / 20 |
| 6 | 20 / 19 | 0 / 0 |
| 7 | 29 / 27 | 0 / 0 |

Chapter boundaries use the first explicit start action for the next chapter. This means funding or optional recruitment between chapters belongs to the preceding chapter. Route A selected private accommodation and capture; route B selected shared accommodation and a peaceful departure. They are two meaningful routes, not an exhaustive shortest-path proof.

## Findings and changes

- Chapter 7 takes about 9–10 in-game days on these routes, with 56–58 total actions. Its two expeditions, seven field decisions, recruitment, tower restoration, relief drill, recovery nights and closing supper prevent an immediate sequence of completion clicks. A richer or highly prepared save may finish sooner; these are measured routes, not enforced minimum durations.
- Chapters 2–5 are not uniformly short. Copying income accounts for roughly 38–58% of advances in those chapters. Adding costs or arbitrary waits would make that repetition worse. Existing construction times remain intact.
- Some older routes chain up to twelve non-Advance actions and up to eight Advances. They warrant a future economy and scene-spacing pass, but reducing income or lengthening every job would not address that problem.
- Rest previously offered nearly identical recovery in every phase. Evening rest now explicitly includes overnight sleep and restores up to three vitality, respecting the existing low-food cap. Daytime rest remains useful. There is no extra mandatory Sleep turn, fatigue meter, death or relationship penalty.
- Optional tea, reading or quiet wind-down appears on the castle page in the evening. It pauses the scholar’s assignment without losing paid progress and does not advance time or farm relationship rewards. The main Advance button identifies sleep when appropriate.
- The final Chapter 7 outing requires recruitment and a rested morning for both the scholar and Rhess. The closing supper requires another night at home and an evening setting. Returning during an evening Advance does not count as having slept at home.

## Recommended next pacing work

Playtest these routes with reading and normal detours before assigning minute-based chapter targets. Review how much construction income comes from repeated copying, and surface existing companion activities during funded work. Preserve meaningful preparation and homecoming beats. Screenshots and a rendered browser acceptance pass remain outstanding.

Reproduce the route counts with `python scripts/audit_chapter_pacing.py pacing-report.json` from the game folder. Full metrics are in PACING_V087.json.
