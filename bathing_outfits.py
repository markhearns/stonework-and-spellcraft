"""Room-specific cosmetic outfits, derived from current presence without save changes."""
ROOMS = frozenset(('pool', 'sauna', 'hot-spring'))
OUTFITS = {
    'mira': ('Teal bathing linen', 'Teal two-piece bathing ensemble.'),
    'tamsin': ('Plum bathing linen', 'Plum halter bathing top and matching short bottoms, with her feline tail free.'),
    'iona': ('Wine-red bathing two-piece', 'Wine-red scoop-neck swim top and matching bikini bottoms, with her tail free.'),
    'aurelia': ('Violet bathing linen', 'Violet two-piece bathing ensemble fitted around her wings.'),
    'neris': ('Plum tide', 'Plum two-piece bathing ensemble over her translucent teal water-elemental form.'),
    'sabine': ('Wine bathhouse linen', 'Wine-red bathing top and charcoal bottoms.'),
    'koharu': ('Teal bathing ribbons', 'Opaque teal halter swim top and matching standard bikini briefs, with her single dark brown fox tail free, long loose dark chestnut hair covering the sides of her head and only two fox ears on top; no human ears.'),
    'zahra': ('Indigo bathing two-piece', 'Indigo halter swim top and matching bikini briefs with muted gold trim; her smoky curls drift above the water.'),
    'fenna': ('Valley bathing linen', 'Sage bathing top and dark bottoms, with her wolfkin tail free.'),
    'kaede': ('Violet bathhouse linen', 'Violet two-piece bathing ensemble.'),
    'elowen': ('Sage bathing linen', 'Sage-green two-piece bathing ensemble.'),
    'nyssara': ('Deepwater bathing linen', 'Petrol-blue two-piece bathing ensemble.'),
    'sylva': ('Living-leaf bathing ensemble', 'Overlapping leaves and delicate vines over her living wood form.'),
    'velis': ('Roadside bathing linen', 'Teal two-piece bathing ensemble.'),
    'rhess': ('Keeper’s bathing linen', 'Moss-green two-piece bathing ensemble fitted around her dragonkin tail.'),
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
