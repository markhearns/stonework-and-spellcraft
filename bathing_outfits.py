"""Room-specific cosmetic outfits, derived from current presence without save changes."""
ROOMS = frozenset(('pool', 'sauna', 'hot-spring'))
OUTFITS = {
    'mira': ('Teal bathing wraps', 'Two-piece teal linen wraps.'),
    'tamsin': ('Plum bathing linen', 'Plum wrap top and short tied bathing trousers.'),
    'iona': ('Wine-coloured bathhouse wrap', 'Deep burgundy linen chest wrap and short tied bathing trousers.'),
    'aurelia': ('Violet bathing wraps', 'Slate-violet two-piece linen wraps fitted around her wings.'),
    'neris': ('Canal bathing wrap', 'Plum chest wrap and tied bathing trousers.'),
    'sabine': ('Wine bathhouse linen', 'Wine wrap top and charcoal bathing skirt over matching briefs.'),
    'maren': ('Joiner’s bathing wraps', 'Plum wrap top and charcoal tied shorts.'),
    'brakka': ('Practical bathing linen', 'Plum chest wrap and charcoal short bathing trousers.'),
    'fenna': ('Valley bathing wraps', 'Sage chest wrap and navy short bathing trousers.'),
    'kaede': ('Violet bathhouse wrap', 'Violet chest wrap and hip wrap over bathing briefs.'),
    'elowen': ('Sage bathing linen', 'Sage wrap top and violet bathing skirt over briefs.'),
    'nyssara': ('Deepwater bathing wraps', 'Petrol-blue wrap top and short bathing trousers.'),
    'sylva': ('Moss bathing wrap', 'Moss-green chest wrap and bathing trousers tied with plant-fibre cord.'),
    'velis': ('Roadside bathing linen', 'Teal wrap top and short bathing trousers with rust ties.'),
    'rhess': ('Keeper’s bathing wraps', 'Moss-green wrap top and separate bathing trousers with an exposed navel.'),
}


def view(state):
    import game
    import headquarters
    import room_life
    result = {}
    for who in game.household_members(state):
        if who not in OUTFITS or game.character_profile(state, who).get('adultAgeYears', 0) < 18:
            continue
        room = room_life.location(state, who)
        active = (room in ROOMS and headquarters.ready(state, room)
                  and game.character_at_castle(state, who)
                  and game.character_assignment(state, who) == 'rest')
        name, description = OUTFITS[who]
        result[who] = {'name': name, 'description': description, 'active': active,
                       'roomId': room if active else None,
                       'roomName': headquarters.ROOMS[room]['name'] if active else None,
                       'portraitId': who + '-bathing' if active else None}
    return result
