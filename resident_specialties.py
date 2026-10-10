"""Authored residents unlock permanent improvements within existing rooms."""
from copy import deepcopy

def specialty(person,room,name,cost,benefit):return dict(personId=person,room=room,name=name,cost=cost,phases=3,benefit=benefit,output='specialty:'+person)
SPECIALTIES={
 'sabine':specialty('sabine','dungeons','Sabine’s release-key register',28,'New specialized chamber and care projects take one fewer scholar phase, to a minimum of one. Already funded work keeps its duration; admission, release and recruitment rules remain separate.'),
 'koharu':specialty('koharu','workshop','Koharu’s restoration bench',24,'Adds +1 core artifact work per assigned maker at home.'),
 'zahra':specialty('zahra','smithy','Zahra’s fitted forge stations',30,'New metalware, blade and armour jobs take one fewer assigned phase, to a minimum of one. Already funded work keeps its agreed duration.'),
 'fenna':specialty('fenna','common-room','Fenna’s travellers’ exchange',22,'Each newly completed core expedition lead returns 1 extra binding thread through the tavern’s exchange of route notes and supplies. Once per lead, not per participant; no repeat-visit reward.'),
 'iona':specialty('iona','command-room','Iona’s correspondence and dispatch desk',26,'Adds 2 crowns per assigned scholar copying phase through organised correspondence. No passive income; personal wallets remain separate.'),
 'kaede':specialty('kaede','training-yard','Kaede’s controlled-strength circle',30,'Unlocks an advanced control drill: three assigned phases, awarding the scholar 2 advancement once. Practice requires an owned field blade and armour.'),
 'tamsin':specialty('tamsin','kitchen','Tamsin’s preserving pantry',28,'Adds 2 crowns to each staffed surplus harvest by preserving produce for sale. No automatic sales or consumption of existing stock.'),
 'elowen':specialty('elowen','infirmary','Elowen’s restorative ward alcove',36,'A quiet, warded preparation space adds one prepared-spell slot per household member. Does not teach spells or add practice slots; no injury meter is introduced.'),
 'nyssara':specialty('nyssara','enchanting-room','Nyssara’s enchantment assay bench',32,'Unlocks repeatable two-phase material jobs: one moon glass or two fireglass for 6 crowns per batch.'),
 'neris':specialty('neris','hot-spring','Neris’s balanced thermal pools',30,'Unlocks a guided thermal-balance study: two assigned phases and 1 scholar advancement, once. Bathing itself remains optional and free.'),
 'aurelia':specialty('aurelia','guard-barracks','Aurelia’s shuttered watch lanterns',32,'Unlocks a watch drill: two assigned phases and 2 scholar advancement, once. Also prepares an ordinary field briefing here. Does not automatically assign guards.'),
 'sylva':specialty('sylva','conservatory','Sylva’s living propagation beds',28,'Adds 1 silver ivy to each staffed binding-plant harvest. Does not increase unattended root-tender production or surplus-sale income.'),
}
NAMES={'sabine':'Sabine','elowen':'Elowen','nyssara':'Nyssara','koharu':'Koharu','zahra':'Zahra','fenna':'Fenna','iona':'Iona','kaede':'Kaede','tamsin':'Tamsin','neris':'Neris','aurelia':'Aurelia','sylva':'Sylva'}
JOB_OWNERS={'advanced-control-drill':'kaede','thermal-balance-study':'neris','watch-drill':'aurelia','watch-briefing':'aurelia','assess-deep-samples':'nyssara','prepare-fireglass':'nyssara'}

def initialize(s):
    # Existing paid facilities keep their original benefits, in addition to their updated room association.
    h=s['headquarters']
    h.setdefault('legacySpecialties', [who for who in ('zahra','kaede','tamsin') if active(s,who)])
    p=h.get('project')
    if p and p.get('id') in ('specialty-zahra','specialty-kaede','specialty-tamsin'):
        p.setdefault('legacySpecialty',p['id'].removeprefix('specialty-'))
    s['localEncounters'].setdefault('sylva',{'status':'available','completedOn':None})
    s['localEncounters'].setdefault('nyssara',{'status':'available','completedOn':None})

def legacy(s,who):return who in s.get('headquarters',{}).get('legacySpecialties',[])

def job_phases(s,key):
    import headquarters as h
    return max(1,h.JOBS[key]['phases']-int(active(s,'zahra') and key in ('metalware','blade','armour')))

def active(s,who):return bool(s.get('headquarters',{}).get('stock',{}).get('specialty:'+who,0))

def blockers(s,who):
    import game as g
    import headquarters as h
    r=[];d=SPECIALTIES[who]
    if who not in g.household_members(s):r.append(NAMES[who]+' must agree to live at the castle. A visit is not membership.')
    elif not g.character_at_castle(s,who):r.append(NAMES[who]+' must be home to plan this improvement.')
    if who+':0' not in s.get('livingStories',{}).get('memories',{}):r.append('Share '+NAMES[who]+'’s first castle conversation under Resident stories.')
    if active(s,who):r.append('This specialist improvement is already complete.')
    return r

def project_ready(s,p):
    import game as g
    key=p.get('id','')
    if not key.startswith('specialty-'):return True
    who=key.removeprefix('specialty-')
    return who in g.household_members(s) and g.character_at_castle(s,who)

def view(s):
    import headquarters as h
    import game as g
    return [{'id':'specialty-'+who,**deepcopy(d),'nameOfPerson':NAMES[who],'complete':active(s,who),'resident':who in g.household_members(s),'blockers':h.job_blockers(s,'specialty-'+who)} for who,d in SPECIALTIES.items()]

def field_reward(s,rewards):
    if active(s,'fenna'):
        s['materialInventory']['binding-thread']+=1
        rewards.append('Fenna’s fitted routekeeper board helped secure 1 additional binding thread; once for this newly returned core lead.')

def register():
    import headquarters as h
    for who,d in SPECIALTIES.items():h.JOBS['specialty-'+who]=deepcopy(d)
    h.JOBS.update({
      'assess-deep-samples':dict(name='Assay an enchanting mineral sample',room='enchanting-room',cost=6,phases=2,benefit='Recover one moon glass. Requires Nyssara’s enchantment assay bench.',coreOutput={'moon-glass':1}),
      'prepare-fireglass':dict(name='Prepare a fireglass batch',room='enchanting-room',cost=6,phases=2,benefit='Produce two fireglass. Requires Nyssara’s enchantment assay bench; previously completed Kaede stations also retain access.',coreOutput={'fireglass':2}),
      'advanced-control-drill':dict(name='Practice Kaede’s controlled-strength drill',room='training-yard',cost=0,phases=3,award=2,benefit='Two scholar advancement, once; requires blade and armour.'),
      'thermal-balance-study':dict(name='Study thermal balance with Neris’s pools',room='hot-spring',cost=0,phases=2,award=1,benefit='One scholar advancement, once; no mandatory bathing or recovery meter.'),
      'watch-drill':dict(name='Practice Aurelia’s watch drill',room='guard-barracks',cost=0,phases=2,award=2,benefit='Two scholar advancement, once; guards remain voluntarily assigned.'),
      'watch-briefing':dict(name='Prepare a watchroom field briefing',room='guard-barracks',cost=0,phases=1,benefit='Prepare the same one-survey briefing as the command room; cannot stockpile or stack briefings.'),
    })
