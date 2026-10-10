"""Multi-use headquarters spaces. Additive saves, explicit projects, no automatic art replacement."""
from copy import deepcopy
import character_approaches

def room(name, group, use, views=(), cost=0, phases=0, needs=(), principles=(), benefit='', legacy=None):
    return dict(name=name,group=group,use=use,views=list(views),cost=cost,phases=phases,needs=list(needs),principles=list(principles),benefit=benefit,legacy=legacy)

ROOMS={
 'entry-hall':room('Entry hall & reception','Household','Arrivals, visitor reception, notices and waiting benches.',('contacts','localEncounters'),12,2),
 'common-room':room('Common room & tavern','Household','Drinks, board games, music, shared meals and informal company.',('householdWork','stories'),legacy='common-room'),
 'library':room('Library & archive','Learning','Research, correspondence, private study, shared reading and bookbinding.',('research','development','householdContent','requests'),legacy='library'),
 'kitchen':room('Kitchen & pantry','Household','Cooking, dining, food storage and household provisioning.',('stores','ledger','restoration'),legacy='kitchen'),
 'washroom':room('Washroom & laundry','Household','Private washing, laundry, linen storage and changing.',('ledger','wardrobe'),legacy='washroom'),
 'conservatory':room('Conservatory & potting benches','Household','Growing, potting, botanical study and garden stores.',('restoration',),legacy='conservatory'),
 'living-quarters':room('Living quarters','Accommodation','Private and shared bedrooms, sitting areas and personal storage. Existing chambers and annex rooms keep their own identities.',('housing',),legacy='housing'),
 'warehouse':room('Warehouse & stores','Work','General storage, receiving, expedition unpacking and stock reserves.',('stores','publicWorkshop'),18,2,benefit='Existing inventory remains accessible. Unlocks supplied workshops, the command room and vault.'),
 'workshop':room('Workshop & material library','Work','Assembly, repairs, sample drawers, woodwork and small artistic work.',('workshop','publicWorkshop','equipment'),28,3,('warehouse',),('steady-hearth-wards',),'+1 core artifact crafting work per assigned maker at home.'),
 'smithy':room('Smithy & armoury','Work','Forge metalware, arms and armour; repair and store field equipment.',(),40,4,('workshop','warehouse'),('steady-hearth-wards',),'Forge metalware, a field blade and fitted armour. Metalware can be sold; blade and armour enable an equipped drill.'),
 'enchanting-room':room('Enchanting room','Learning','Create magical equipment, inscribe owned gear, test spells and improve working tools.',('equipment','spells','publicWorkshop'),65,5,('workshop','smithy'),('field-calibration',),'Personal tool inscriptions gain +1 work per assigned phase. Enchant forged armour to shorten public-site investigations from two phases to one.'),
 'command-room':room('Command room & map table','Work','Expedition planning, maps, field reports and household assignments.',('expeditions','publicWorkshop','ledger'),26,3,('warehouse',),benefit='Prepare a field briefing: the next ordinary core survey takes one phase. It does not stack with a lantern or field notes.'),
 'infirmary':room('Infirmary & apothecary','Household','Quiet care, medicines, botanical supplies and voluntary recuperation.',('containment','restoration'),24,3,('washroom','conservatory'),benefit='A quiet recovery scene and direct access to specialized care. No invented injury or passive healing meter.'),
 'training-yard':room('Training yard','Defence','Guard drills, sparring, field practice and physical training.',('development',),20,2,('warehouse',),benefit='Complete basic and equipped drills for two separate, once-only advancement awards.'),
 'guard-barracks':room('Guard barracks & watchroom','Defence','Duty planning, kit lockers, off-duty seating and separately fitted sleeping places.',('housing','development'),30,3,('training-yard','smithy'),benefit='Unlocks a four-bed guard dormitory. Residence does not automatically assign guard duty.'),
 'underground-quarters':room('Underground living quarters','Accommodation','Ventilated lower living wing with dry passages, shared sitting space and separate private/shared bedrooms.',('housing',),45,4,('washroom',),('water-guidance','steady-hearth-wards'),'Unlocks one private lower suite and one four-bed lower chamber; bedrooms are fitted separately.'),
 'dungeons':room('Dungeon ward & secure workrooms','Defence','Lower secure rooms, ward maintenance and access to specialized Ember and Quiet chambers.',('containment','mystery'),38,4,('underground-quarters',),('steady-hearth-wards',),'Consolidates the dungeon level and existing specialized care. No automatic captives, guards or extra resident capacity.'),
 'vault':room('Warded vault','Work','Late-game storage for rare components and treasured crafted objects, with an inspection table.',(),100,6,('warehouse','enchanting-room'),('field-calibration','reference-binding'),'Deposit components or spare core artifacts outside crafting stock; withdraw the exact quantity. Requires discoveries from two core expedition sites.'),
 'hot-spring':room('Hot spring baths','Leisure','Thermal grotto, bathing pools, resting ledges and private changing alcoves.',(),60,5,('underground-quarters','washroom'),('water-guidance','steady-hearth-wards'),'An optional thermal bathing scene; no recurring fee or stat penalty for skipping it.'),
 'sauna':room('Sauna','Leisure','Heated timber benches, cooling vestibule and private changing.',(),25,3,('washroom',),('steady-hearth-wards',),'An optional quiet sauna scene.'),
 'pool':room('Swimming pool','Leisure','Swimming, exercise, poolside rest and changing spaces.',(),45,4,('washroom',),('water-guidance',),'An optional swimming scene and access to personal training.'),
 'chapel':room('Chapel & sanctuary','Household','Worship, quiet reflection, memorials and personal observances without an imposed faith.',('journal','rituals'),18,2,benefit='Choose a personal reflection. Existing magical rituals retain their own knowledge and material requirements.'),
}
MERGES={
 'study-alcove':'library','shared-reading-room':'library','binding-nook':'library','correspondence-room':'library',
 'material-library':'workshop','dry-assembly-room':'workshop','portrait-studio':'workshop','wet-laboratory':'enchanting-room',
 'cookhouse':'kitchen','tea-parlour':'common-room','music-room':'common-room','guest-sitting-room':'entry-hall',
 'entry-vestibule':'entry-hall','linen-room':'washroom','fitting-room':'washroom','potting-room':'conservatory',
 'map-room':'command-room','field-return-room':'warehouse','secure-sample-room':'vault','quiet-care-suite':'infirmary',
 'private-bedchamber':'living-quarters','common-room':'common-room','washroom':'washroom','conservatory':'conservatory'}
BEDROOMS={
 'lower-suite':dict(name='Lower private suite',capacityBeds=1,costCrowns=18,requiredWorkPhases=2,region='main',zone='underground',hq='underground-quarters'),
 'lower-chamber':dict(name='Lower shared chamber',capacityBeds=4,costCrowns=34,requiredWorkPhases=4,region='main',zone='underground',hq='underground-quarters'),
 'guard-dormitory':dict(name='Guard dormitory',capacityBeds=4,costCrowns=34,requiredWorkPhases=4,region='main',zone='guard',hq='guard-barracks')}
JOBS={
 'metalware':dict(name='Forge a metalware batch',room='smithy',cost=8,phases=2,output='metalware',benefit='One batch, sellable for 12 crowns.'),
 'blade':dict(name='Forge a field blade',room='smithy',cost=16,phases=3,output='blade',benefit='Owned field equipment; together with armour enables the equipped drill.'),
 'armour':dict(name='Forge fitted armour',room='smithy',cost=24,phases=4,output='armour',benefit='Owned field equipment; can receive a field ward.'),
 'enchant-armour':dict(name='Inscribe a field ward',room='enchanting-room',cost=20,phases=3,output='warded-armour',benefit='Converts one forged armour into warded armour; equip it to investigate public field sites in one phase instead of two.'),
 'basic-drill':dict(name='Learn the basic field drill',room='training-yard',cost=0,phases=2,award=1,benefit='One advancement point for your scholar, once per campaign.'),
 'equipped-drill':dict(name='Practice with arms and armour',room='training-yard',cost=0,phases=3,award=2,benefit='Two advancement points for your scholar, once per campaign; requires an owned blade and armour.'),
 'briefing':dict(name='Prepare the next field briefing',room='command-room',cost=0,phases=1,benefit='One ordinary core survey at one phase; consumed only by a survey. Rainward methods are unaffected.')}
SCENES={
 'common-room':{'drink':'You settle by the hearth with a drink. For a while, the castle has nothing urgent to ask of you.','games':'You lay out a board and consider the next move. There is room at the table whenever someone chooses to join.'},
 'infirmary':{'rest':'Clean linen, a quiet seat and the scent of dried herbs make a little room for recovery.'},
 'hot-spring':{'soak':'Warm mineral water gathers around the stone ledge. Steam softens the edges of the old masonry.'},
 'sauna':{'warmth':'The timber creaks softly in the warmth. Beyond the door, a cool bench waits.'},
 'pool':{'swim':'You take an unhurried length of the pool, then rest at the broad stone steps.'},
 'chapel':{'reflect':'You sit in the quiet sanctuary and consider what you want this home to stand for.','remember':'You leave a small token of remembrance. Its meaning is yours to keep.','observe':'You make space for your own observance, without asking the household to share it.'}}

def initialize(s):
    s.setdefault('headquarters',{'rooms':{},'project':None,'stock':{},'vault':{},'completedDrills':[],'briefing':False,'armourEquipped':False,'memories':{}})
    s['headquarters'].setdefault('workerProjects',{})
    s['headquarters'].setdefault('workAgreements',[])


def projects(s):
    """The original project slot remains the founder's, without copying paid work."""
    h=s.get('headquarters',{})
    result={'founder':h['project']} if h.get('project') else {}
    result.update(h.get('workerProjects',{}))
    return result


def project_for(s,who='founder'):
    return projects(s).get(who)


def project_room(p):
    return p['id'] if p['kind']=='hq-build' else JOBS[p['id']]['room']


def put_project(s,who,p):
    if who=='founder':s['headquarters']['project']=p
    elif p:s['headquarters']['workerProjects'][who]=p
    else:s['headquarters']['workerProjects'].pop(who,None)


def worker_blockers(s,who,kind,key,existing=False):
    import game as g
    import resident_specialties
    if not isinstance(who,str) or who not in g.household_members(s):return ['Choose a current household member.']
    reasons=[]
    if not g.character_at_castle(s,who):reasons.append('The worker must be home.')
    if who!='founder' and who not in s['headquarters'].get('workAgreements',[]):reasons.append('Agree headquarters work with this resident first.')
    if not existing and project_for(s,who):reasons.append('Finish or cancel this worker’s funded headquarters job first.')
    d=(ROOMS if kind=='hq-build' else JOBS)[key]
    if kind=='hq-build':
        for principle in d['principles']:
            if principle not in g.character_principles(s,who):reasons.append('Worker must personally learn '+g.PRINCIPLE_NAMES[principle]+'.')
    elif who!='founder':
        if d.get('award'):reasons.append('This personal drill belongs to your scholar; residents retain their own training controls.')
        elif key.startswith('specialty-'):
            if who!=key.removeprefix('specialty-'):reasons.append('Choose this specialist or your scholar to install their improvement.')
        elif d['room'] in ('smithy','enchanting-room','workshop'):
            offered=g.character_profile(s,who).get('offeredAssignments',[])
            if 'crafting' not in offered and who!='mira' and who!=resident_specialties.JOB_OWNERS.get(key):reasons.append('This worker must offer crafting work for this production job.')
    return reasons


def work_blockers(s,who='founder'):
    import game as g
    import resident_specialties
    p=project_for(s,who)
    if not p:return ['No funded headquarters job for this worker.']
    reasons=worker_blockers(s,who,p['kind'],p['id'],existing=True)
    if not resident_specialties.project_ready(s,p):reasons.append('The specialist must be a resident and at home during installation.')
    room_id='workshop' if p['id']=='prepare-fireglass' and resident_specialties.legacy(s,'kaede') else project_room(p)
    if p['kind']=='hq-job' and not ready(s,room_id):reasons.append('The work facility must be available.')
    if g.character_assignment(s,who)!='headquarters':reasons.append('Resume this worker’s headquarters assignment.')
    return reasons


def management_blockers(s,who):
    import game as g
    reasons=[]
    if not g.character_at_castle(s,'founder'):reasons.append('Return home before changing work arrangements.')
    if who not in g.household_members(s):reasons.append('This worker is no longer a household member.')
    elif not g.character_at_castle(s,who):reasons.append('The worker must return home before changing this job.')
    return reasons


def occupancy_blockers(s,who,room_id,key):
    reasons=[]
    for worker,p in projects(s).items():
        if project_room(p)==room_id:reasons.append('This facility already has a funded headquarters job; finish or cancel it first.')
        elif key in ('briefing','watch-briefing') and p['id'] in ('briefing','watch-briefing'):reasons.append('A field briefing is already funded elsewhere.')
    return reasons


def ready(s,key):
    d=ROOMS[key];legacy=d['legacy']
    if legacy in ('common-room','library','housing'):return True
    if legacy=='conservatory':return s['restorationStatus']=='complete'
    if legacy:return s['facilityProjects'][legacy]['status']=='complete'
    return s.get('headquarters',{}).get('rooms',{}).get(key)== 'complete'

def blockers(s,key,who='founder'):
    import game as g
    d=ROOMS[key];r=[]
    if key=='foundation-chamber':
        return ['Already restored. Visit the chamber to use its ritual.'] if ready(s,key) else ['Restore this room through the foundation-chamber investigation, available after Chapter 5.']
    if not g.character_at_castle(s,'founder'):r.append('Return home first.')
    if key=='watchtower' and not s.get('patrolJourneys',{}).get('watchtower-trail',{}).get('discoveries'):r.append('Meet Rhess and return from the watchtower trail first.')
    if ready(s,key):r.append('Already available.')
    r+=worker_blockers(s,who,'hq-build',key)+occupancy_blockers(s,who,key,key)
    for dep in d['needs']:
        if not ready(s,dep):r.append('Complete '+ROOMS[dep]['name']+'.')
    if key in ('enchanting-room','underground-quarters','vault') and not s['livingWingCompletedOn']:r.append('Complete A Proper Living Wing first.')
    if key=='vault' and sum(bool(g.discoveries_for(s,k)) for k in g.EXPEDITION_SITES)<2:r.append('Return discoveries from two different core expedition sites.')
    if s['sharedFunds']<d['cost']:r.append('Requires '+str(d['cost'])+' shared crowns.')
    return r

def job_blockers(s,key,who='founder'):
    import game as g
    h=s['headquarters'];d=JOBS[key];r=[]
    if key=='roadside-refuge' and not (s.get('hollowRoad',{}).get('discoveries') and s.get('roadsWeKeep',{}).get('agreement')):r.append('Rescue the caravan and agree supplier terms first.')
    import resident_specialties
    if key.startswith('specialty-'):r.extend(resident_specialties.blockers(s,key.removeprefix('specialty-')))
    owner=resident_specialties.JOB_OWNERS.get(key)
    old_fireglass=key=='prepare-fireglass' and resident_specialties.legacy(s,'kaede')
    if owner and not resident_specialties.active(s,owner) and not old_fireglass:r.append('Complete '+resident_specialties.SPECIALTIES[owner]['name']+' first.')
    if not g.character_at_castle(s,'founder'):r.append('Return home first.')
    if not ready(s,'workshop' if old_fireglass else d['room']):r.append('Restore '+ROOMS[d['room']]['name']+'.')
    r+=worker_blockers(s,who,'hq-job',key)+occupancy_blockers(s,who,d['room'],key)
    if s['sharedFunds']<d['cost']:r.append('Requires '+str(d['cost'])+' crowns for materials and supplies.')
    for room_id in d.get('needs',[]):
        if not ready(s,room_id):r.append('Restore '+ROOMS[room_id]['name']+'.')
    for principle in d.get('principles',[]):
        if principle not in g.character_principles(s,who):r.append('The worker must learn '+g.PRINCIPLE_NAMES[principle]+'.')
    for material,n in d.get('materials',{}).items():
        if s['materialInventory'].get(material,0)-s['materialReserveTargets'].get(material,0)<n:r.append('Needs '+str(n)+' unreserved '+g.MATERIALS[material]['name']+'.')
    if d.get('once') and (h['stock'].get(d['output']) or any(p['id']==key for p in projects(s).values())):r.append('This permanent improvement is already built or funded.')
    if key=='sorting-bench':
        if 'survey' not in s.get('serviceRoad',{}).get('discoveries',[]):r.append('Complete the old service road and bring the sorting-bench plan home.')
        if h['stock'].get('sorting-bench',0):r.append('The sorting bench is already fitted.')
    if key in h['completedDrills']:r.append('This drill award is already earned.')
    if key=='enchant-armour' and h['stock'].get('armour',0)<1:r.append('Forge an armour first.')
    if key in ('equipped-drill','advanced-control-drill') and (not h['stock'].get('blade',0) or not (h['stock'].get('armour',0)+h['stock'].get('warded-armour',0))):r.append('Own both a field blade and an armour.')
    if key in ('briefing','watch-briefing') and h['briefing']:r.append('A briefing is already prepared.')
    return r

def view(s):
    import game as g
    import resident_specialties
    h=deepcopy(s.get('headquarters',{}))
    workers=g.household_members(s)
    h['workers']=[{'id':who,'name':g.character_profile(s,who)['name'],'assignment':g.character_assignment(s,who),
        'agreed':who=='founder' or who in h.get('workAgreements',[]),'blockers':management_blockers(s,who),
        'hasProject':bool(project_for(s,who))} for who in workers]
    h['catalogue']={k:{**deepcopy(d),'ready':ready(s,k),'blockers':blockers(s,k),'scenes':SCENES.get(k,{}),
        'workers':{who:blockers(s,k,who) for who in workers} if not d['legacy'] else {}} for k,d in ROOMS.items()}
    h['jobs']={k:{**d,'phases':resident_specialties.job_phases(s,k),'blockers':job_blockers(s,k),
        'workers':{who:job_blockers(s,k,who) for who in workers}} for k,d in JOBS.items()}
    h['projects']=[{**deepcopy(p),'workerId':who,'workerName':g.character_profile(s,who)['name'],'roomId':project_room(p),
        'working':working(s,who),'workBlockers':work_blockers(s,who),'managementBlockers':management_blockers(s,who),
        'resumeBlockers':management_blockers(s,who)+worker_blockers(s,who,p['kind'],p['id'],existing=True)+([] if resident_specialties.project_ready(s,p) else ['The specialist must be a resident and at home.']),
        'assignment':g.character_assignment(s,who)} for who,p in projects(s).items()]
    h['bedroomBlockers']={k:[] if ready(s,BEDROOMS[k]['hq']) else ['Complete '+ROOMS[BEDROOMS[k]['hq']]['name']+' before fitting this room.'] for k in BEDROOMS}
    h['working']=bool(h.get('project') and working(s))
    return h


def working(s,who='founder'):
    return bool(project_for(s,who)) and not work_blockers(s,who)

def apply(s,a):
    import game as g
    kind=a.get('type')
    if kind in ('assign-character','assign-founder','assign-resident') and a.get('assignment')=='headquarters':
        who=a.get('characterId') if kind=='assign-character' else ('founder' if kind=='assign-founder' else 'mira')
        return apply(s,{'type':'hq-resume','workerId':who})
    if kind=='fund-housing' and isinstance(a.get('roomId'),str) and a.get('roomId') in BEDROOMS:
        g.require(ready(s,BEDROOMS[a['roomId']]['hq']),'Restore the associated headquarters living space first.')
    if not isinstance(kind,str) or not kind.startswith('hq-'):return False
    g.require(g.character_at_castle(s,'founder'),'Return home before changing headquarters work.')
    h=s['headquarters']
    who=a.get('workerId','founder')
    g.require(isinstance(who,str) and who in g.household_members(s),'Choose a current household worker.')
    if kind=='hq-agree-work':
        g.require(who!='founder' and type(a.get('enabled')) is bool,'Choose a resident and whether to agree work.')
        g.require(g.character_at_castle(s,who),'Discuss work together at home.')
        g.require(a['enabled'] or not project_for(s,who),'Finish or cancel this worker’s funded job before ending the agreement.')
        agreements=h.setdefault('workAgreements',[])
        if a['enabled'] and who not in agreements:agreements.append(who)
        if not a['enabled'] and who in agreements:agreements.remove(who)
        g.add_journal(s,g.character_profile(s,who)['name']+(' agreed to headquarters work. Each job still needs explicit funding and assignment.' if a['enabled'] else ' ended the headquarters work agreement.'))
    elif kind in ('hq-build','hq-job'):
        key=a.get('roomId' if kind=='hq-build' else 'jobId');catalogue=ROOMS if kind=='hq-build' else JOBS
        g.require(isinstance(key,str) and key in catalogue,'Choose a known room or job.')
        d=catalogue[key]
        if kind=='hq-build':g.require(not d['legacy'],'Use this room’s existing restoration controls.')
        reasons=blockers(s,key,who) if kind=='hq-build' else job_blockers(s,key,who)
        g.require(not reasons,' '.join(reasons))
        held={}
        if key=='enchant-armour':held={'armour':1};h['stock']['armour']-=1
        import resident_specialties
        phases=d['phases'] if kind=='hq-build' else resident_specialties.job_phases(s,key)
        s['sharedFunds']-=d['cost'];put_project(s,who,{'kind':kind,'id':key,'name':d['name'],'cost':d['cost'],'phases':phases,'done':0,'held':held})
        if d.get('materials'):
            project_for(s,who)['materials']=deepcopy(d['materials'])
            for k,n in d['materials'].items():s['materialInventory'][k]-=n
        g.set_character_assignment(s,who,'headquarters');g.add_journal(s,'Started '+d['name']+' with '+g.character_profile(s,who)['name']+'; '+str(d['cost'])+' crowns committed. Advance performs the work.')
    elif kind in ('hq-resume','hq-pause','hq-cancel'):
        p=project_for(s,who);g.require(p is not None,'No unfinished headquarters project for this worker.')
        reasons=management_blockers(s,who);g.require(not reasons,' '.join(reasons))
        if kind=='hq-resume':
            import resident_specialties
            reasons=worker_blockers(s,who,p['kind'],p['id'],existing=True)
            g.require(not reasons,' '.join(reasons))
            g.require(resident_specialties.project_ready(s,p),'The specialist must be a resident and at home before installation can resume.')
            g.set_character_assignment(s,who,'headquarters')
        elif kind=='hq-pause':
            if g.character_assignment(s,who)=='headquarters':g.set_character_assignment(s,who,'rest')
        else:
            s['sharedFunds']+=p['cost']
            for k,n in p.get('materials',{}).items():s['materialInventory'][k]+=n
            for k,n in p['held'].items():h['stock'][k]=h['stock'].get(k,0)+n
            import armoury
            armoury.finish_hq(s,p,cancel=True)
            put_project(s,who,None)
            if g.character_assignment(s,who)=='headquarters':g.set_character_assignment(s,who,'rest')
            g.add_journal(s,'Cancelled '+p['name']+'; committed funds and goods returned. Time already spent is not restored.')
    elif kind=='hq-sell-metalware':
        g.require(ready(s,'smithy') and h['stock'].get('metalware',0)>0,'Forge a metalware batch first.')
        h['stock']['metalware']-=1;s['sharedFunds']+=12;g.add_journal(s,'Sold one forged metalware batch for 12 crowns.')
    elif kind=='hq-equip-armour':
        g.require(type(a.get('equipped')) is bool,'Choose whether to equip warded armour.')
        g.require(not a['equipped'] or h['stock'].get('warded-armour',0)>0,'Inscribe a field ward on an owned armour first.')
        h['armourEquipped']=a['equipped']
    elif kind in ('hq-deposit','hq-withdraw'):
        g.require(ready(s,'vault'),'Restore the warded vault first.')
        key=a.get('itemId');n=a.get('quantity');g.require(type(n) is int and 1<=n<=999,'Choose a whole quantity from 1 to 999.')
        g.require(isinstance(key,str) and key in {**g.MATERIALS,**g.RECIPES},'Choose a core component or crafted artifact.')
        inventory=s['materialInventory'] if key in g.MATERIALS else s['craftedArtifacts']
        available=inventory.get(key,0)-s['materialReserveTargets'].get(key,0) if key in g.MATERIALS else g.spare_artifact_count(s,key)
        if kind=='hq-deposit':
            g.require(available>=n,'Only unreserved stock can enter the vault; installed and carried artifacts stay in use.')
            inventory[key]-=n;h['vault'][key]=h['vault'].get(key,0)+n
        else:
            g.require(h['vault'].get(key,0)>=n,'The vault does not hold that quantity.')
            h['vault'][key]-=n;inventory[key]=inventory.get(key,0)+n
        g.add_journal(s,('Vault deposit: ' if kind=='hq-deposit' else 'Vault withdrawal: ')+str(n)+' '+key+'.')
    elif kind in ('hq-store-object','hq-retrieve-object'):
        import public_workshop as w
        g.require(ready(s,'vault'),'Restore the warded vault first.')
        key=a.get('itemId');items=s['publicWorkshop']['items']
        g.require(isinstance(key,str) and key in items,'Choose an existing owned object.')
        obj=items[key];g.require(obj['ownerId']=='founder','Only your scholar’s own objects can be moved by this control.')
        if kind=='hq-store-object':
            g.require(not obj.get('vaultStored'),'This object is already in the vault.')
            g.require(not w.locked(s,key) and not obj.get('roomId') and not obj.get('active') and key not in s['publicWorkshop']['preparedItems'].values(),'Stow the object and finish any reserved work or delivery first.')
            obj['vaultStored']=True
        else:
            g.require(obj.get('vaultStored'),'This object is not in the vault.')
            obj['vaultStored']=False
        g.add_journal(s,('Stored in vault: ' if kind=='hq-store-object' else 'Retrieved from vault: ')+obj['name']+'. Ownership and accepted artwork are unchanged.')
    elif kind=='hq-scene':
        key=a.get('roomId');choice=a.get('choice')
        g.require(isinstance(key,str) and key in SCENES and isinstance(choice,str) and choice in SCENES[key],'Choose an offered room activity.')
        g.require(ready(s,key),'Restore this room first.')
        token=key+':'+choice;g.require(token not in h['memories'],'This reflection is already remembered.')
        h['memories'][token]=SCENES[key][choice];g.add_journal(s,SCENES[key][choice])
    else:raise g.RuleError('Unknown headquarters action.')
    return True

def resolve(s,summary,eligible=None):
    import game as g
    h=s['headquarters']
    # Snapshot eligibility before any other system resolves. A returning traveller
    # cannot also work at home in the same phase, and no completion starts a new job.
    eligible=eligible if eligible is not None else [who for who in projects(s) if working(s,who)]
    for who in eligible:
        p=project_for(s,who)
        if not p or not working(s,who):continue
        work=character_approaches.work_step(s,who,'construction',p['done'],p['phases'],summary) if p['kind']=='hq-build' else 1
        p['done']=min(p['phases'],p['done']+work)
        summary.append(g.character_profile(s,who)['name']+' · '+p['name']+': '+str(p['done'])+' / '+str(p['phases'])+' phases.')
        if p['done']<p['phases']:continue
        if p['kind']=='hq-build':h['rooms'][p['id']]='complete'
        else:
            d=JOBS[p['id']]
            for item,n in d.get('coreOutput',{}).items():s['materialInventory'][item]+=n
            if d.get('output'):h['stock'][d['output']]=h['stock'].get(d['output'],0)+1
            if d.get('award'):
                h['completedDrills'].append(p['id']);g.award_advancement(s,who,'headquarters:'+p['id'],d['award'],d['name'])
            if p['id'] in ('briefing','watch-briefing'):h['briefing']=True
            if p.get('legacySpecialty') and p['legacySpecialty'] not in h['legacySpecialties']:h['legacySpecialties'].append(p['legacySpecialty'])
        import armoury
        armoury.finish_hq(s,p)
        summary.append('Completed: '+p['name']+'.');g.add_journal(s,'Completed headquarters work: '+p['name']+' by '+g.character_profile(s,who)['name']+'.')
        put_project(s,who,None);g.set_character_assignment(s,who,'rest')


def forecast(s):
    import game as g
    rows=[]
    for who,p in projects(s).items():
        work=character_approaches.work_step(s,who,'construction',p['done'],p['phases']) if p['kind']=='hq-build' else 1
        rows.append(g.character_profile(s,who)['name']+' · '+p['name']+(': +'+str(work)+' work this phase.' if working(s,who) else ': paused; '+' '.join(work_blockers(s,who))))
    return rows

def register(g):
    for key,d in ROOMS.items():
        if key not in g['ORIGINAL_ASSETS']:g['ORIGINAL_ASSETS'][key]='/assets/ui/castle-emblem.webp'
    for key,d in BEDROOMS.items():
        d['illustrationIsRepresentative']=True
        d['description']='A dry, ventilated room with '+str(d['capacityBeds'])+' separate bed(s), personal storage and a closing door. Shared rooms include privacy screens. Beds are fitted separately from district services.'
        g['HOUSING_ROOMS'][key]=d
        g['estate_expansion'].ROOMS[key]=d
        g['ROOMS'][key]={'name':d['name'],'purpose':'Headquarters accommodation.','description':d['description'],'furnishings':['oak-bench','velvet-bench','none'],'illustrationIsRepresentative':True}
        g['ORIGINAL_ASSETS'][key]='/assets/rooms/bedchamber.webp'
