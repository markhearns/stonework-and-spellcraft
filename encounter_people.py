"""One source for traveller pools and their encounter illustrations."""
COMMON=('human','high-elf','dark-elf','drow','catfolk','wolfkin','orc','ogrekin')
EXOTIC=('kitsune','demon','seraph','elemental','vampire','fae','djinn','dragonkin','dryad','nymph')
ELEMENTS=('water','fire','earth','air')
SUPPORTED=COMMON+EXOTIC
BANDIT_EXOTIC=tuple(a for a in EXOTIC if a not in ('dryad','nymph'))
BANDITS=COMMON+BANDIT_EXOTIC
EXOTIC_CHANCE=0.01

def choose(rng,kind='rescue'):
    rare=BANDIT_EXOTIC if kind=='capture' else EXOTIC
    ancestry=rng.choice(rare if rng.random()<EXOTIC_CHANCE else COMMON)
    return ancestry+'-'+rng.choice(ELEMENTS) if ancestry=='elemental' else ancestry

def ancestry(key):
    return 'elemental' if key.startswith('elemental-') else key

def art(key,kind):
    base=ancestry(key)
    if base not in (SUPPORTED if kind=='rescue' else BANDITS):return None
    if base=='elemental' and key not in tuple('elemental-'+x for x in ELEMENTS):key='elemental-water'
    folder='rescues' if kind=='rescue' else 'bandits'
    return '/assets/bestiary/'+folder+'/'+key+'.webp'

def profile_key(profile):
    import bestiary
    aid=bestiary.ancestry_id(profile.get('ancestryLabel'))
    return 'elemental-'+profile.get('elementalVariant','water') if aid=='elemental' else aid

def apply_element(profile,key):
    if not key.startswith('elemental-'):return
    element=key.removeprefix('elemental-')
    details={'water':'translucent turquoise skin and flowing water-like hair',
             'fire':'charcoal skin traced with amber ember lines and controlled flame-like hair',
             'earth':'brown living-stone skin, mineral veins and moss-dark hair',
             'air':'pale silver-blue skin, drifting white hair and faint currents around her hands'}
    profile['elementalVariant']=element
    profile['appearanceDescription']='An adult '+element+' elemental with '+details[element]+'. She wears practical opaque travelling clothes. Her elemental nature grants only the listed ancestry bonus and learned abilities.'
    profile['role']=profile['role'].replace('Elemental ',element.title()+' elemental ',1)
