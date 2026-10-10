"""Small, explicit ancestry modifiers to capability checks; never base ranks."""
from copy import deepcopy
# Everyone receives one +1 check modifier. Individual aptitudes and training stay separate.
TRAITS = {
 'Human': ('Adaptable attention', 'intelligence'),
 'High elf': ('Patient attention', 'intelligence'),
 'Dark elf': ('Light step', 'dexterity'),
 'Drow': ('Low-light precision', 'dexterity'),
 'Catfolk': ('Sure-footed', 'dexterity'),
 'Bovinefolk': ('Steady strength', 'might'),
 'Orc': ('Sturdy constitution', 'vitality'),
 'Wolfkin': ('Trail endurance', 'vitality'),
 'Kitsune': ('Foxlike agility', 'dexterity'),
 'Golem': ('Constructed endurance', 'vitality'),
 'Demon': ('Steady inner fire', 'resolve'),
 'Seraph': ('Composed presence', 'charisma'),
 'Elemental': ('Elemental focus', 'resolve'),
 'Vampire': ('Measured poise', 'charisma'),
 'Fae': ('Nimble movement', 'dexterity'),
 'Djinn': ('Ember focus', 'resolve'),
 'Dragonkin': ('Draconic strength', 'might'),
 'Dryad': ('Rooted endurance', 'vitality'),
 'Nymph': ('Natural poise', 'charisma'),
 'Spirit': ('Unbroken concentration', 'resolve'),
 'Ogrekin': ('Powerful frame', 'might'),
}

def definition(label):
    label={'Angel':'Seraph','Water elemental':'Elemental','Construct':'Golem'}.get(label,label)
    row=TRAITS.get(label)
    if not row:return None
    name,attribute=row
    return {'ancestry':label,'name':name,'attribute':attribute,'amount':1,
            'description':'+1 to '+attribute.title()+' capability checks. Always active; listed separately from attributes, skills and equipment. No free ranks, actions or relationship gains.'}

def for_person(state,who):
    import game as g
    return definition(g.character_profile(state,who).get('ancestryLabel'))

def bonus(state,who,attribute):
    trait=for_person(state,who)
    return int(bool(trait and trait['attribute']==attribute))
