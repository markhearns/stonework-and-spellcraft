"""Deterministic, additive approaches. Existing methods never consult these checks."""
from copy import deepcopy
import character_builds as builds

# Attribute, skill, required score. Skills remain 0..2; attributes are 1..10.
def spec(attribute, skill, threshold=9):
    return {'attribute': attribute, 'skill': skill, 'threshold': threshold}

def score(s, who, requirement, party=(), magic=False):
    import game as g
    attr, skill = requirement['attribute'], requirement['skill']
    base = builds.build(s, who)['attributes'][attr]
    trained = 2 * g.skill_rank(s, who, skill)
    helpers = [p for p in party if p != who and builds.build(s,p)['attributes'][attr] + 2*g.skill_rank(s,p,skill) >= 6]
    help_bonus = 2 if helpers else 0
    buff = {'might':'strength', 'intelligence':'insight'}.get(attr)
    enchanted = 3 if magic and buff and s.get('fieldMagic',{}).get('aqueduct',{}).get('buffs',{}).get(who,{}).get(buff,0) else 0
    import character_customization
    specialist = character_customization.bonus(s,who,skill)
    import household_sagas
    familiar = next((p for p in party if p!=who and household_sagas.teamwork(s,who,p,skill)),None)
    chemistry = 1 if familiar else 0
    import party_journeys
    recovered = party_journeys.bonus(s,skill) if party and s.get('expedition') and who in g.expedition_party(s) else 0
    import armoury
    gear,_=armoury.approach_bonus(s,who,requirement.get('equipmentTags',[]))
    import ancestry_traits
    ancestry = ancestry_traits.bonus(s,who,attr)
    total = base + trained + help_bonus + enchanted + specialist + chemistry + recovered + gear + ancestry
    detail = f"{builds.ATTRIBUTES[attr]['name']} {base} + {g.CHARACTER_SKILLS[skill]['name']} {trained}"
    if ancestry: detail += ' + '+ancestry_traits.for_person(s,who)['name']+' (ancestry) 1'
    if gear: detail += ' + applicable equipment '+str(gear)
    if recovered: detail += ' + recovered expedition legacy 1'
    if chemistry: detail += ' + practised teamwork 1 ('+g.character_profile(s,familiar)['name']+')'
    if specialist: detail += ' + specialization 1'
    if help_bonus: detail += ' + help 2 (' + g.character_profile(s,helpers[0])['name'] + ')'
    if enchanted: detail += ' + spell 3'
    return {'total':total, 'required':requirement['threshold'], 'detail':detail+f" = {total} / {requirement['threshold']}",
            'qualified':total>=requirement['threshold'], 'buff':buff if enchanted else None,
            'helper':helpers[0] if helpers else None}

def party_blockers(s, requirement, party):
    if any(score(s,p,requirement,party)['qualified'] for p in party): return []
    return ['Additional route needs '+str(requirement['threshold'])+' combined '+builds.ATTRIBUTES[requirement['attribute']]['name']+' + twice '+requirement['skill'].title()+' (a capable companion adds 2). Existing methods remain available.']

# Two distinct routes per obstacle; success is deterministic and costs one assigned phase.
FIELD = {
 'fire': [('firebreak','Rake a firebreak while the others shelter','might','athletics','You pull the burning debris into the bare inspection trench. The party crosses behind the cleared firebreak.'),
          ('draft','Read the draught and close the service shutters','intelligence','artifice','You close the old air shutters in sequence. The flames subside and the party clears the gate.')],
 'caretaker': [('diplomacy','Offer a clear repair agreement','charisma','diplomacy','You agree who will inspect each sluice and promise a report on return. The caretaker opens the passage without a fee.'),
               ('credentials','Explain the fault using the keeper’s own diagrams','intelligence','scholarship','You identify the mismatch on her maintenance diagram. She recognizes that the party can help and opens the gate.')],
 'flood': [('balance','Cross the exposed braces and secure a handline','dexterity','fieldcraft','You follow the braces above the water and secure a line for everyone behind you.'),
           ('wade','Carry a handline through the cold gallery','vitality','athletics','Steady pacing and careful footing get the line across. The others use it to cross without injury.')],
 'submerged': [('divert','Rebuild the inspection bypass','intelligence','artifice','You use the dry service bypass to drain just the wheel housing, leaving the main channel running.'),
               ('reach','Work the wheel with a braced extension','might','athletics','Braced at the dry lip, you grip the wheel with the maintenance pole and haul it around. Nobody needs to dive.')],
 'gap': [('anchor','Traverse the side brace and anchor a rope','dexterity','athletics','You traverse the narrow side brace, then rig a secure crossing for the rest of the party.'),
         ('bridge','Recover and cantilever the broken bridge sections','intelligence','artifice','The fallen bridge still has usable spars. You reassemble a short supported span.')],
 'ember': [('vent','Lure the ember hound into the cooling flue','intelligence','fieldcraft','You open the cold flue and guide the hound toward its draught. It settles in the empty kiln; no retaliation.'),
           ('ward','Hold a measured warding rhythm','resolve','channeling','You sustain the survey staff’s warding rhythm until the hound retreats into its kiln. The party passes without retaliation.')],
 'briar': [('intimidate','Drive the stalker back with a commanding warning shout','charisma','diplomacy','You make yourself a convincing threat without approaching its nest. The stalker retreats up the empty stair; the party passes without retaliation.'),
           ('footfall','Lead the stalker away with thrown footsteps','dexterity','fieldcraft','A series of well-placed stones draws the stalker down an empty stair. You guide the party past its nest.'),
           ('screen','Hold the briar screen while the party passes','vitality','athletics','Using the broad maintenance screen, you keep the thorns at a distance until everyone is safely through.')],
 'tower': [('climb','Free-climb the sound joints and lower the safety rope','dexterity','athletics','You test every hold, reach the mooring, and lower a secured rope for the party.'),
           ('hoist','Restore the counterbalanced inspection hoist','intelligence','artifice','You reconnect the hoist’s return cable. The old cradle carries the party to the landing.')],
 'bones': [('release','Recite the watchman’s dismissal from the duty plaque','intelligence','scholarship','You reconstruct the shift-ending formula. The watchman salutes the empty gatehouse and returns to rest.'),
           ('command','Speak the watchword without yielding to its terror','resolve','channeling','You hold the old watchword steady against the spirit’s pressure. It recognizes relief and lets the party through.')],
 'stone': [('lift','Lift the counterweight onto its cradle','might','athletics','You brace the lift and roll the fallen weight onto its service cradle, freeing the door.'),
           ('purchase','Build a compound lever from the service rails','intelligence','artifice','The service rails provide a second fulcrum. With the load divided, the stone rises cleanly.')],
 'sentinel': [('latch','Slip behind the guard arm and release its service latch','dexterity','artifice','You reach the service latch between the sentinel’s slow sweeps. Its inspection lock engages without retaliation.'),
              ('protocol','Reconstruct the maintenance recognition signal','intelligence','scholarship','The inspection symbols specify a recognition sequence. You repeat it; the sentinel stands aside.')],
 'runes': [('cipher','Reconstruct the missing cipher from repeated marks','intelligence','scholarship','Repeated marks expose the missing key. You set the regulator without a false turn.'),
           ('resonance','Hold each rune’s resonance until the stops align','resolve','channeling','You sustain the regulator’s faint resonance while the mechanical stops settle into agreement.')],
}

def field_options(s, who):
    import field_magic as f, game as g
    d=f.step(s)
    if not d:return []
    party=[p for p in g.expedition_party(s) if f.vitality(s,p)>0]
    return [dict(id='aptitude:'+key, name=name, requirement=field_requirement(d['id'],key,attr,skill), result=result,
                 check=score(s,who,field_requirement(d['id'],key,attr,skill),party,True)) for key,name,attr,skill,result in FIELD[d['id']]]

def field_option(s,who,key):
    return next((r for r in field_options(s,who) if r['id']==key),None)

def install_existing():
    import game as g, service_road as road
    additions=[
      (g.OBSERVATORY_STEPS[0], 'read-gradient','Reconstruct the dry route from channel gradients','intelligence','fieldcraft'),
      (g.OBSERVATORY_STEPS[1], 'steady-mount','Release the lens mount with a counterbalanced grip','dexterity','artifice'),
      (g.OBSERVATORY_STEPS[2], 'compare-ledger','Rebuild the ledger index from repeated references','intelligence','scholarship'),
      (g.OBSERVATORY_RECOVERY, 'balance-rings','Balance the mounting rings by touch','dexterity','artifice'),
      (road.STEPS['channel'],'brace-survey','Brace the measuring frame against the current','might','athletics'),
      (road.STEPS['orchard'],'climb-survey','Traverse the retaining stones and sight the old steps','dexterity','fieldcraft'),
      (road.STEPS['shelter'],'infer-joints','Reconstruct the hidden joints from the tool marks','intelligence','artifice'),
    ]
    for step,key,name,attr,skill in additions:
        step['choices']['aptitude:'+key]={'name':name,'phases':1,'aptitude':spec(attr,skill),
          'description':'One phase; '+builds.ATTRIBUTES[attr]['name']+' + twice '+g.CHARACTER_SKILLS[skill]['name']+' needs 9. A capable present companion adds 2. Ordinary methods remain available.'}


def construction_bonus(s, who='founder'):
    """One capped extra unit from a builder's physical or technical expertise."""
    return int(any(score(s,who,spec(a,k,9))['qualified'] for a,k in [('might','athletics'),('intelligence','artifice')]))


def work_step(s, who, kind, done, total, summary=None):
    """Preview and resolution share a cap; spend only charges that actually add work."""
    import spell_support, lasting_rituals
    room=max(0,total-done)
    work=min(1,room)
    innate=min(construction_bonus(s,who),max(0,room-work))
    work+=innate
    if summary is not None and innate:
        summary.append('Builder expertise: +1 work from Might + Athletics or Intelligence + Artifice.')
    permanent=int(who=='founder' and lasting_rituals.active(s,'foundation-circle'))
    work+=min(permanent,max(0,room-work))
    for effect in (kind,'haste'):
        record=s.get('spellSupports',{}).get(who,{}).get(effect,{})
        amount=record.get('amount',0) if record.get('remaining',0)>0 else 0
        extra=min(amount,max(0,room-work))
        work+=extra
        if extra and summary is not None:spell_support.consume(s,who,effect,summary,include_haste=False)
    return work


def precision_bonus(s,who):
    return int(score(s,who,spec('dexterity','channeling'))['qualified'])


def healing_bonus(s,who):
    import character_customization as custom
    extra=int(custom.person(s,who).get('specialization')=='healer' and not custom.specialization_blockers(s,who,'healer'))
    return extra+int(score(s,who,spec('intelligence','channeling'))['qualified'])


def field_requirement(step,key,attr,skill):
    tags={('fire','firebreak'):['heat-exposure'],('flood','wade'):['wet-exposure'],('flood','balance'):['footing'],('gap','anchor'):['footing'],('tower','climb'):['footing'],('runes','resonance'):['channel-control'],('stone','lift'):['controlled-force']}
    return {**spec(attr,skill),'equipmentTags':tags.get((step,key),[])}
