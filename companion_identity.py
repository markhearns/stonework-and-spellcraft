"""One-time updates to authored identities; player-created people stay untouched."""
from copy import deepcopy
import re

AGES = {'tamsin': 20, 'zahra': 23, 'sylva': 21, 'velis': 22, 'rhess': 24}


def migrate(state):
    profiles = list(state.get('people', {}).items())
    for container in ('reviewedCandidates', 'localEncounterCandidates'):
        profiles.extend((who, record['profile']) for who, record in state.get(container, {}).items()
                        if isinstance(record, dict) and isinstance(record.get('profile'), dict))
    for who, profile in profiles:
        changes = {}
        # Only replace the old authored age, not a deliberately customized age.
        if who in AGES and profile.get('adultAgeYears') == 25:
            changes['adultAgeYears'] = AGES[who]
            changes['role'] = re.sub(r' · 25$', ' · ' + str(AGES[who]), profile.get('role', ''))
        if not any(profile.get(key) != value for key, value in changes.items()):
            continue
        profile.setdefault('identityHistory', []).append({key: deepcopy(profile.get(key))
            for key in ('adultAgeYears', 'role', 'appearanceDescription', 'identityRevision')})
        profile.update(changes)
        profile['identityRevision'] = profile.get('identityRevision', 1) + 1
        if 'adultAgeYears' in changes and isinstance(profile.get('generationIngredients'), dict):
            profile['generationIngredients']['adultAgeYears'] = changes['adultAgeYears']
