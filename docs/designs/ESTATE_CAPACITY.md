# Bounded accommodation and optional annex — v0.30

The solo estate now has the design's functional housing ceiling: **25 non-founder places in the main castle plus one founder place, and 25 optional annex places**. Ten specialized containment places remain entirely separate. A full roster is never required and creates no routine upkeep.

## Fixed room catalogue

| Region | Rooms | Total beds |
|---|---|---:|
| Existing main wing | Guest chamber, West chamber, Garden chamber | 5 |
| Restored main galleries | Five one-bed Gallery suites, four four-bed Upper chambers | 21 |
| Optional annex | Five one-bed suites, five four-bed chambers | 25 |

The main total is 26 beds: one founder plus up to 25 non-founders. Region checks include occupied beds and named arrivals; moving the founder into the annex does not turn the reserved main founder place into a 26th resident entitlement. The annex has at most 25 non-founder places and 25 physical beds. If the founder chooses an annex bed, it is occupied like any other bed.

Private-room preferences now apply generically to **every** character during bedroom moves as well as arrival reservations. The previous move restriction checked Tamsin specifically; Aurelia, Sabine and reviewed private-room candidates now receive the same protection.

## Work and costs

Gallery suites cost 18 crowns / 2 phases each. Upper chambers cost 36 crowns / 4 phases each. These use the existing housing projects and own scholar assignment, including paused funded work. Basic beds, storage, privacy and furnishings are included.

The optional annex first needs Water guidance and Steady hearth wards personally understood by the scholar, the Proper Living Wing, and **80 crowns / 5 own phases** for access and services. This foundation produces no usable beds. Only afterwards can its suites (16 crowns / 2 phases) and four-bed chambers (32 crowns / 4 phases) be funded individually. Unfinished foundation work can pause or be cancelled for the exact saved crown commitment; a completed annex cannot be refunded. The existing individual room project workflow remains funded/pause/resume, without a new room-demolition/refund action.

All accommodation progresses only on explicit Advance. No population threshold forces construction. The main castle and annex have separate UI filters. Up to fifty enduring reviewed candidate plans are supported; plans do not grant beds or compel recruitment.

## Illustrations and saved choices

The original room illustrations remain unchanged. Expanded rooms explicitly reuse the existing private/shared room studies as **representative illustrations**. The images do not purport to show all four beds in a new four-person chamber. Actual capacity, occupants and furnishing effects are authoritative text. A distinct illustration can be imported and reviewed for each persistent room ID. Furnishings, decoration slots, saved arrangements and accepted-art histories are independent between rooms.

The floor plan still represents the original wing; expanded restored rooms are accessible as direct room cards and through housing. A complete multi-wing illustrated floor plan and distinct expanded-room paintings remain visual work.

## Saves and checks

Schema 29 initializes only the new unfunded rooms, their independent decoration/arrangement records and an unfunded annex. Prior bedrooms, reservations, funded room progress and personal preferences remain unchanged.

Tests cover exact ceiling arithmetic, no free rooms or early entry, independent decoration, annex prerequisite/funding gates, phased services followed by phased fitting, pause/refund, generic private preferences, region reservations and old-save preservation. A full-capacity fixture admits and recruits 49 reviewed people beside Mira, reaching 50 residents and one founder with 25 non-founders in each region. It rejects another arrival, renders public sheets and frees a bed on agreed departure. This validates rules scale, not large-roster browser performance or unique character content.

A connected UI flow checks room funding, moving a person, representative-art labels, region filters, annex construction/fitting and reload. Co-op founder counts and actor authority remain unimplemented; this ceiling is explicitly the solo implementation.
