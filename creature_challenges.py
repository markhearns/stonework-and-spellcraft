"""Explicit creature counters and encounter-local conditions.

Preview is pure; field_patrols commits its returned state only on Advance.
No condition changes equipment records or survives an encounter.
"""
from copy import deepcopy


def key(run):
    if not run or run['index'] >= len(run['enemies']):
        return None
    import bestiary
    return bestiary.ENCOUNTERS[run['enemies'][run['index']]].get('challenge')


def state(s, run):
    cid = key(run)
    if not cid:
        return {}
    saved = run.get('creatureState')
    if saved and saved.get('id') == cid:
        return deepcopy(saved)
    import bestiary
    return dict(id=cid, grappled=None, corrosion={}, imbalance={}, venom={}, stiffness={},
                tracked=0, revealed=0, grounded=0, heat=0, pinnedHeads=0,
                wards=2 if bestiary.knowledge(s, cid) >= 2 else 3)


def equipped(s, who, definition):
    import armoury
    a = armoury.state(s)
    return any((it := a['items'].get(item_id)) and it['definitionId'] == definition
               and it['ownerId'] == who and it['location'] == 'armoury'
               and not armoury.busy(s, item_id)
               for item_id in set(armoury.loadout(s, who, 'expedition')['slots'].values()))


def lantern(s, run):
    return any(equipped(s, who, 'field-lantern') for who in run['party'])


def route_blockers(s, route):
    import bestiary, field_patrols
    if bestiary.ROUTES.get(route, {}).get('challengeTier') == 'Difficult' and not field_patrols.chapter(s)['completedOn']:
        return ['Complete Chapter 8: The First Real Test before taking a difficult expedition.']
    return []


def intent(s, run, incoming):
    cid = key(run)
    if not cid or not incoming:
        return incoming
    import field_magic
    st = state(s, run)
    if cid == 'owlbear' and st['grappled'] and field_magic.vitality(s, st['grappled']) > 0:
        incoming['target'] = st['grappled']
    if cid == 'runebound-colossus':
        incoming['attack'] = 3 + st['wards']
        incoming['name'] = ('Ward-fed strike' if st['wards'] else 'Exposed mechanism: slow strike')
    if cid == 'marsh-hydra':
        heads = 3 - st['pinnedHeads']
        incoming['attack'] = 2 + heads
        party = [w for w in run['party'] if field_magic.vitality(s, w) > 0]
        if heads > 1:
            target = next((w for w in party if w != incoming['target']), incoming['target'])
            incoming['secondary'] = dict(target=target, attack=2, name='Second free head')
    return incoming


def rows(s, run):
    cid = key(run)
    if not cid:
        return []
    import field_magic, game
    st = state(s, run); turn = run.get('round', 0) % 3; result = []
    def add(who, action, name, damage=0, guard=1, inputs=None, blockers=None, control=False, **extra):
        inputs = inputs or {}; reasons = list(blockers or [])
        for material, amount in inputs.items():
            if s['materialInventory'].get(material, 0) - s['materialReserveTargets'].get(material, 0) < amount:
                reasons.append('Needs '+str(amount)+' unreserved '+game.MATERIALS[material]['name']+'.')
        result.append(dict(id=who+':creature:'+action, who=who, name=name, damage=damage,
                           block=guard, actionGuard=guard, cost=0, kind='creature-counter',
                           challengeAction=action, challengeControl=control, inputs=inputs,
                           blockers=reasons, **extra))
    for who in run['party']:
        if field_magic.vitality(s, who) <= 0:
            continue
        if cid == 'owlbear':
            add(who, 'brace', 'Brace against the charge', 1, 3, control=True,
                blockers=[] if turn == 0 else ['Use this when the owlbear announces a charge.'])
            if st['grappled']:
                add(who, 'free', 'Break the grip on '+game.character_profile(s, st['grappled'])['name'], guard=2, control=True)
        elif cid == 'rust-beetle':
            add(who, 'interrupt', 'Interrupt the corrosive spray', 1, 2, control=True,
                blockers=[] if turn == 0 else ['Use this when the beetle raises its mandibles to spray.'])
            if any(st['corrosion'].values()):
                add(who, 'wash', 'Wash corrosive residue from the party’s equipment', guard=2)
        elif cid == 'blink-lynx':
            add(who, 'track', 'Track the landing marks', 1, 2, control=True)
        elif cid == 'cliff-harpy':
            add(who, 'shelter', 'Take shelter below the ledge', 1, 3, control=True)
        elif cid == 'will-o-wisp':
            add(who, 'path', 'Mark the true path', guard=2, control=True)
        elif cid == 'basilisk':
            add(who, 'screen', 'Break line of sight and loosen stone stiffness', guard=3, avoidAttack=True)
        elif cid == 'manticore':
            add(who, 'cover', 'Take cover from the spine volley', 1, 3, control=True,
                blockers=[] if turn == 0 else ['Use this when the manticore raises its tail for a volley.'])
        elif cid == 'wyvern':
            add(who, 'snare', 'Snare the landing leg', 1, 2, inputs={'binding-thread':1}, control=True)
        elif cid == 'marsh-hydra':
            add(who, 'pin', 'Pin one head away from the party', 1, 2, inputs={'binding-thread':1}, control=True,
                blockers=[] if st['pinnedHeads'] < 2 else ['Two heads are already pinned; concentrate on the remaining head.'])
            add(who, 'heat', 'Apply a heat dressing to stop regeneration', 2, 1, inputs={'sun-amber':1})
        elif cid == 'runebound-colossus' and st['wards']:
            add(who, 'disconnect', 'Disconnect the next ward plate', guard=2, control=True)
        if cid in ('basilisk', 'manticore', 'wyvern', 'marsh-hydra', 'runebound-colossus'):
            for target in run['party']:
                if field_magic.vitality(s, target) < 6 or st['venom'].get(target) or st['stiffness'].get(target):
                    add(who, 'treat:'+target, 'First aid for '+game.character_profile(s, target)['name'],
                        inputs={'silver-ivy':1}, treatmentTarget=target)
                    import companion_goals
                    if cid in ('basilisk','manticore','wyvern') and companion_goals.complete(s,'elowen'):
                        add(who,'field-kit:'+target,'Use Elowen’s field kit for '+game.character_profile(s,target)['name']+' · restore 4 vitality and clear venom/stiffness',
                            treatmentTarget=target,goalKit=True,blockers=[] if companion_goals.saved(s)['kits']>0 else ['Restock a field kit at the infirmary.'])
    return result


def prepare(s, run, original):
    """Return a private action copy, next condition state and visible notes."""
    cid = key(run)
    if not cid:
        return original, None, []
    row = deepcopy(original); old = state(s, run); st = deepcopy(old); notes = []
    turn = run.get('round', 0) % 3; action = row.get('challengeAction'); who = row['who']
    physical = row['kind'] != 'spell'
    for field in ('corrosion', 'imbalance', 'venom'):
        st[field] = {w:n-1 for w,n in old[field].items() if n > 1}
    for field in ('tracked', 'revealed', 'grounded', 'heat'):
        st[field] = max(0, old[field]-1)
    st['_venomDue'] = [w for w,n in old['venom'].items() if n > 0]
    if action == 'free': st['grappled'] = None; notes.append('The grip is broken.')
    if action == 'wash' or row.get('spellKind') == 'water':
        st['corrosion'] = {}; row['clearsCorrosion'] = True
        if old['corrosion']: notes.append('Corrosive residue is washed away; cover recovers after this exchange.')
    if action == 'track': st['tracked'] = 2; notes.append('Landing places remain tracked for the next two exchanges.')
    if action == 'shelter' or cid == 'cliff-harpy' and row.get('spellKind') == 'gust-strike': st['imbalance'] = {}; notes.append('The party regains stable footing below the ledge.')
    if action == 'path': st['revealed'] = 2; notes.append('The true path remains marked for the next two exchanges.')
    if action == 'screen':
        st['stiffness'] = {w:n-1 for w,n in old['stiffness'].items() if n > 1}
        notes.append('Sight is blocked; every party member loses one stone-stiffness level.')
    if action == 'snare' or cid == 'wyvern' and row.get('spellKind') in ('ice','gust-strike'):
        st['grounded'] = 2; notes.append('The wyvern is grounded for this exchange and the next two.')
    if action == 'pin':
        row['challengeAttackReduction'] = 1
        st['pinnedHeads'] = min(2, st['pinnedHeads']+1)
        notes.append('One head is pinned. '+str(3-st['pinnedHeads'])+' free heads remain.')
    if action == 'heat' or cid == 'marsh-hydra' and row.get('spellKind') in ('fire', 'ice'):
        st['heat'] = 2; notes.append('Regeneration is suppressed for this exchange and the next two.')
    if cid == 'runebound-colossus' and (action == 'disconnect' or row.get('spellKind') in ('lightning','chain-lightning','dispel-ward')):
        removed=min(st['wards'],2 if row.get('spellKind') in ('chain-lightning','dispel-ward') else 1)
        row['challengeAttackReduction'] = removed
        st['wards'] -= removed
        notes.append(str(removed)+' ward plate(s) disconnected; '+str(st['wards'])+' remain.')
    if row.get('spellKind')=='dispel-ward':
        if cid=='will-o-wisp':st['revealed']=2;notes.append('The wisp is revealed for the next two exchanges.')
        if cid=='blink-lynx':st['tracked']=2;notes.append('The lynx’s landing places are tracked for the next two exchanges.')
    if row.get('purifyTarget'):
        patient=row['purifyTarget']
        for field in ('venom','stiffness','corrosion','imbalance'):st[field].pop(patient,None)
        st['_venomDue']=[w for w in st['_venomDue'] if w!=patient]
        row['purified']=patient
        notes.append('Purifying light clears venom, stone stiffness, corrosion and imbalance before retaliation.')
    if row.get('treatmentTarget'):
        row['treatmentAmount'] = 4 if row.get('goalKit') else 3 if s['headquarters']['stock'].get('field-remedy-cabinet') else 2
        target = row['treatmentTarget']; st['venom'].pop(target, None); st['stiffness'].pop(target, None)
        st['_venomDue'] = [w for w in st['_venomDue'] if w != target]
    if physical and row['damage']:
        penalty = (2 if old['grappled'] == who and action != 'free' else 0)
        penalty += int(bool(old['imbalance'].get(who))) if action != 'shelter' else 0
        penalty += old['stiffness'].get(who, 0)
        if penalty:
            row['damage'] = max(0, row['damage']-penalty)
            notes.append('Current conditions reduce physical damage by '+str(penalty)+'.')
    hidden = (cid == 'blink-lynx' and turn != 1 and not (old['tracked'] or action == 'track' or row.get('control'))
              or cid == 'will-o-wisp' and not (old['revealed'] or action == 'path' or lantern(s, run))
              or cid == 'wyvern' and turn == 0 and not (old['grounded'] or st['grounded']))
    if hidden and physical and row['damage']:
        row['creatureDamageCap'] = 1
        notes.append('Position limits this physical attack to 1 damage. Use the creature counter or a spell.')
    if cid == 'manticore' and turn == 1 and row['damage']:
        row['damage'] += 2; notes.append('Recovery opening: +2 damage.')
    if cid == 'wyvern' and (turn != 0 or old['grounded'] or st['grounded']) and row['damage']:
        row['damage'] += 2; notes.append('Grounded opening: +2 damage.')
    if cid == 'runebound-colossus':
        if old['wards'] and row['damage']:
            row['creatureDamageCap'] = 1; notes.append('The active ward plates limit this attack to 1 damage.')
        elif not old['wards']:
            row['ignoreCreatureArmour'] = True
            if row['damage']: row['damage'] += 3; notes.append('Exposed mechanism: +3 damage and no physical armour.')
    return row, st, notes


def finish_preview(s, run, row, st, result, notes):
    if st is None:
        return result
    import game, field_patrols, patrol_tactics, rare_accessories
    cid = key(run); old = state(s, run); turn = run.get('round', 0) % 3
    action = row.get('challengeAction'); target = result['target']; health = result['healthAfter']
    name = lambda w: game.character_profile(s, w)['name']
    due = st.pop('_venomDue', [])
    if row.get('treatmentTarget'):
        patient = row['treatmentTarget']
        notes.append(name(patient)+' receives first aid; venom and stone stiffness are cleared.')
    if row.get('spellKind') == 'heal':
        for healed in result['healing']:
            patient = healed['who']; st['venom'].pop(patient, None); st['stiffness'].pop(patient, None)
            due = [w for w in due if w != patient]
            notes.append(name(patient)+' is cleared of venom and stone stiffness by healing.')
    # Conditions end on resolution. There is no post-victory poison tick.
    if row['kind'] in ('peace', 'bypass') or result['enemyAfter'] <= 0:
        result.update(creatureState={}, challengeNotes=notes, otherInjuries=[])
        result['breakdown'] += notes
        return result
    other = []
    def lose(who, amount, reason):
        amount = min(health[who], amount)
        if amount:
            health[who] -= amount; other.append(dict(who=who, amount=amount, reason=reason))
            notes.append(name(who)+' loses '+str(amount)+' vitality: '+reason+'.')
    for patient in due:
        if rare_accessories.worn(s,patient) != 'wyvern-antivenom-locket':lose(patient, 1, 'venom')
    for patient, level in st['stiffness'].items():
        if level >= 3: lose(patient, 1, 'severe stone stiffness')
    if not result['cancelled']:
        injured = result['injury'] > 0
        if cid == 'owlbear' and turn == 1 and injured and not row.get('control'):
            st['grappled'] = target; notes.append(name(target)+' is held; break the grip to restore physical damage.')
        if cid == 'rust-beetle' and turn == 0 and injured and action != 'interrupt' and not row.get('clearsCorrosion'):
            st['corrosion'][target] = 2; notes.append(name(target)+' has corrosion: -1 cover for the next two exchanges.')
        if cid == 'cliff-harpy' and turn == 0 and injured and action != 'shelter':
            st['imbalance'][target] = 2; notes.append(name(target)+' is off balance: -1 physical damage for the next two exchanges.')
        if rare_accessories.worn(s,target) != 'basilisk-mirror-brooch' and cid == 'basilisk' and turn in (0, 2) and action != 'screen' and not (row.get('protect') and row.get('actionGuard', 0) >= 2):
            st['stiffness'][target] = min(3, st['stiffness'].get(target, 0)+1)
            notes.append(name(target)+' has stone stiffness '+str(st['stiffness'][target])+'/3. Break sight or provide first aid.')
        if rare_accessories.worn(s,target) != 'wyvern-antivenom-locket' and injured and (cid == 'manticore' and turn in (0, 2) or cid == 'wyvern' and turn == 2):
            if result['preparations'].get('antivenom'):
                result['preparations']['antivenom']-=1;notes.append('One prepared antidote prevents venom in '+name(target)+'.')
            else:st['venom'][target] = 2; notes.append(name(target)+' has venom: 1 vitality after each of the next two exchanges unless treated.')
        if cid == 'marsh-hydra' and 3-st['pinnedHeads'] > 1:
            original = next((w for w in run['party'] if w != result['originalTarget'] and health[w] > 0), result['originalTarget'])
            victim = row['who'] if row.get('protect') and health[row['who']] > 0 else original
            party = [w for w in run['party'] if health[w] > 0]
            block, _ = patrol_tactics.defence(s, victim, party, ignore_corrosion=row.get('purified')==victim)
            if victim == row['who']: block += row.get('actionGuard', 0)
            block+=row.get('extraCover',{}).get(victim,0)
            force = max(0, 2-(2 if row.get('control') else 0)-row.get('magicAttackReduction',0))
            lose(victim, max(0, force-block), 'second hydra head')
            if row.get('protect') and original != victim:
                base, _ = patrol_tactics.defence(s, original, party)
                result['protectedDamage'] += max(0, force-base)
    if cid == 'marsh-hydra' and not (old['heat'] or st['heat']):
        maximum = field_patrols.ENEMIES[cid]['hp']
        healed = min(2, maximum-result['enemyAfter']); result['enemyAfter'] += healed
        if healed: notes.append('The hydra regenerates '+str(healed)+' vitality. Heat or ice suppresses regeneration.')
    result.update(creatureState=st, challengeNotes=notes, otherInjuries=other)
    result['breakdown'] += notes
    return result


def view(s, run):
    cid = key(run)
    if not cid:
        return None
    import bestiary, game
    st = state(s, run); d = bestiary.CREATURES[cid]; conditions = []
    name = lambda w: game.character_profile(s, w)['name']
    if st['grappled']: conditions.append(name(st['grappled'])+' is held: physical damage reduced by 2 until the grip is broken.')
    for field, explanation in [('corrosion', '-1 cover'), ('imbalance', '-1 physical damage'), ('venom', 'lose 1 vitality after each action')]:
        for who, rounds in st[field].items():
            if rounds: conditions.append(name(who)+': '+field+' for '+str(rounds)+' further exchanges; '+explanation+'.')
    for who, level in st['stiffness'].items():
        if level: conditions.append(name(who)+': stone stiffness '+str(level)+'/3; physical damage reduced by '+str(level)+('. Lose 1 vitality after each action.' if level >= 3 else '.'))
    if cid == 'runebound-colossus': conditions.append(str(st['wards'])+' active ward plates. Disconnect them or use lightning.')
    if cid == 'marsh-hydra': conditions.append(str(3-st['pinnedHeads'])+' free heads; regeneration '+('suppressed for '+str(st['heat'])+' further exchanges.' if st['heat'] else 'active: up to 2 vitality per exchange.'))
    if cid == 'blink-lynx': conditions.append('Landing marks: '+(str(st['tracked'])+' tracked exchanges remain.' if st['tracked'] else 'not tracked.'))
    if cid == 'will-o-wisp': conditions.append('Wisp '+('revealed by an equipped hooded lantern.' if lantern(s, run) else 'revealed for '+str(st['revealed'])+' further exchanges.' if st['revealed'] else 'not yet revealed.'))
    if cid == 'wyvern': conditions.append('Wyvern '+('held on the ground for '+str(st['grounded'])+' further exchanges.' if st['grounded'] else 'follows the displayed dive, landing and sting cycle.'))
    return dict(tier=d['challengeTier'], preparation=d['preparation'], rules=d['mechanics'], conditions=conditions,
                note='Conditions advance only with a committed exchange and end when this encounter ends. Withdraw remains available.')


def returned(s, run, complete, summary):
    if not complete or not any(o.get('enemyId') == 'runebound-colossus' and o.get('rewarded') for o in run['outcomes']):
        return
    records = s.setdefault('creatureDiscoveries', {})
    if records.get('outwork-maintenance'):
        return
    import game
    text = 'The buried outwork records show that the guardian protected a water-inspection walkway. Each ward plate has its own maintenance disconnect. The castle’s builders planned for repairs by workers who could not cast the original enchantment.'
    records['outwork-maintenance'] = dict(day=s['dayNumber'], text=text)
    game.add_journal(s, text); summary.append(text); run['log'].append(text)
