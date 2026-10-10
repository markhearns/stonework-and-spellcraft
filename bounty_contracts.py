"""Creature bounties: explicit clients, field completion, crown payment and samples."""
from copy import deepcopy
import bestiary

# Rare components use distinct properties so ordinary recipes cannot consume them.
# They share the existing inventory, reserve and project refund rules.
SAMPLES = {
 'briarback-boar': ('briar-bristle','Briar bristle',['rare-force'],24,'Gather stiff bristles shed against the scraped trees.'),
 'slatehide-lizard': ('slate-scale','Shed slate scale',['rare-guard'],28,'Collect intact plates shed beside its resting ledge.'),
 'storm-antler-stag': ('storm-antler','Shed storm antler',['rare-force'],36,'Collect a naturally shed antler from the now-accessible bedding ground.'),
 'giant-marsh-crab': ('marsh-shell','Marsh shell',['rare-guard'],28,'Recover sound pieces of moulted shell beside the crossing.'),
 'lantern-moth': ('lantern-dust','Lantern wing dust',['rare-focus'],32,'Brush loose wing dust from the abandoned lamp glass.'),
 'grave-silk-spider': ('grave-silk','Grave silk',['rare-binding'],32,'Gather intact abandoned silk after the spider has left the crossing.'),
 'reed-lurker': ('reed-membrane','Shed reed membrane',['rare-flow'],28,'Collect shed flexible skin from the cleared riverbank.'),
 'hearth-ash-hound': ('kiln-cinder','Tempered kiln cinder',['rare-heat'],36,'Collect cooled, heat-holding cinders after securing the kiln.'),
 'root-mimic': ('living-root-fibre','Living root fibre',['rare-binding'],28,'Gather loose fibres left where the roots crossed the path.'),
 'moss-troll': ('bridge-moss','Bridge moss',['rare-care'],28,'Collect moss from the cleared bridge stones, not from the troll’s body.'),
 'ruin-gargoyle': ('ward-stone-chip','Ward-stone chip',['rare-focus'],36,'Recover fallen carved chips from the cleared boundary post.'),
 'restless-sentry': ('watch-iron','Old watch iron',['rare-guard'],32,'Salvage abandoned watch fittings after securing the old post.'),
 'wolf': ('wolf-underfur','Shed wolf underfur',['rare-care'],24,'Collect shed underfur caught on the cleared track’s thorn bushes.'),
 'griffin': ('griffin-feather','Shed griffin feather',['rare-flow'],40,'Collect fallen flight feathers from the now-accessible ridge path.'),
 'flint-beak-cockatrice': ('flint-beak-splinter','Flint-beak splinter',['rare-force'],36,'Gather loose splinters from the stones used to hone its beak.'),
 'barrow-badger': ('burrow-down','Burrow down',['rare-care'],30,'Collect loose insulating down from an abandoned bedding hollow.'),
 'rimewing-bat': ('rime-membrane','Shed rime membrane',['rare-flow'],34,'Gather naturally shed wing membrane caught on an empty roost ledge.'),
 'siltback-tortoise': ('silt-scute','Shed silt scute',['rare-guard'],34,'Recover intact scutes shed beside the tortoise’s resting bank.'),
 'brass-wing-scarab': ('scarab-gear','Discarded scarab gear',['rare-focus'],38,'Salvage a discarded precision gear from the workshop sorting pile.'),
 'gloam-jelly': ('gloam-gel','Gloam gel',['rare-binding'],34,'Bottle detached gel beads from the cleared sluice channel.'),
}
BRIEFS = {
 'briarback-boar': ('Clear the cart track','Reedbank carriers','A boar has overturned two handcarts on the woodland track. Clear the route so carriers can collect the stranded loads.','clearance','woods',18),
 'slatehide-lizard': ('Fetch plates for a containment vessel','Hillfold alchemists','A high-pressure alchemical containment vessel needs mineral plates that hold a reinforced ward. Secure the quarry ledge and bring back a sound shed scale.','sample','road',18),
 'storm-antler-stag': ('Collect an antler for a charge vessel','Hillfold alchemists','An alchemist is testing an advanced enchantment that stores and releases an electrical charge. Recover a naturally shed antler from the stag’s bedding ground.','sample','border',24),
 'giant-marsh-crab': ('Reopen the marsh footbridge','Reedbank carriers','A large crab is grabbing packs at the lower footbridge. Move it away or defeat it so travellers can cross safely.','clearance','wetland',18),
 'lantern-moth': ('Collect dust for a precision enchantment','Hillfold enchanters','The enchanters need loose moth-wing dust to stabilise a precision lens used in advanced spellwork. Recover the dust from an abandoned lamp without taking wings from a living moth.','sample','woods',14),
 'grave-silk-spider': ('Supply silk for a healing ward','Brook apothecary','The apothecary needs strong, magically receptive fibres to reinforce a permanent healing ward. Secure the old cellar and recover intact abandoned silk.','sample','ruins',20),
 'reed-lurker': ('Make the reed crossing safe','Roadside refuge','Travellers report an amphibian lunging from the shallows beside the stepping stones. Secure a dry approach and clear the crossing.','clearance','wetland',20),
 'hearth-ash-hound': ('Recover heat-holding cinders','Hillfold alchemists','An elemental hound has occupied a disused kiln. Secure access and collect cooled cinders for a high-temperature enchanting furnace.','sample','ruins',26),
 'root-mimic': ('Clear the nursery supply path','Fern nursery','Moving roots have tangled the nursery’s delivery ropes and blocked its path. Clear access without damaging the nursery beds.','clearance','woods',20),
 'moss-troll': ('Settle the bridge dispute','Reedbank carriers','A troll claims the bridge stones are being damaged by overloaded carts. Agree safe passage or secure the crossing so the carriers can repair it.','clearance','border',24),
 'ruin-gargoyle': ('Recover an old boundary sample','Hillfold conservators','The conservators need a fallen ward-stone chip to restore a permanent protective ward. Secure the guardian’s post and recover a loose fragment.','sample','ruins',26),
 'restless-sentry': ('End the abandoned watch','Roadside refuge','An animated sentry has been challenging travellers at an abandoned watch post. Resolve its old duty and make the route safe.','clearance','ruins',22),
 'wolf': ('Move wolves off the supply track','Reedbank carriers','Hungry wolves are guarding a torn food sack beside the track. Secure the path so the carriers can remove the spilled food.','clearance','road',16),
 'griffin': ('Collect feathers for binding trials','Hillfold alchemists','The alchemists need a fallen griffin feather for an advanced spell-conducting binding. Secure access to the ridge path beneath the nest and recover a shed feather.','sample','border',28),
 'flint-beak-cockatrice': ('Clear the ridge survey path','Hillfold surveyors','A cockatrice is defending a dust hollow beside the survey markers. Clear a safe route so the surveyors can inspect the ridge without approaching its hollow.','clearance','border',24),
 'barrow-badger': ('Collect down for a recovery charm','Brook apothecary','An advanced recovery charm needs fine insulating burrow down. Secure the old bank and collect a clean sample from an abandoned bedding hollow.','sample','woods',20),
 'rimewing-bat': ('Supply a cold-channel membrane','Hillfold alchemists','A controlled-cooling enchantment needs a flexible membrane that retains cold. Reach an empty ledge beneath the colony and recover a naturally shed sample.','sample','ruins',24),
 'siltback-tortoise': ('Reopen the mill bank','Reedbank carriers','A large tortoise has blocked the narrow bank used to reach the mill. Mark a safe detour or clear the crossing so grain carriers can pass.','clearance','wetland',24),
 'brass-wing-scarab': ('Recover a ward-calibration gear','Hillfold conservators','A clockwork scarab guards a sorting pile in the ruined workshop. The conservators need a discarded gear for a precision ward instrument.','sample','ruins',26),
 'gloam-jelly': ('Clear the refuge sluice','Roadside refuge','A gloam jelly is clinging to the sluice steps and preventing routine maintenance. Secure the channel so the refuge can restore its water supply.','clearance','wetland',22),
}
# New creature records keep their sample and client brief beside their encounter.
for _cid, _creature in bestiary.CREATURES.items():
    if 'sample' in _creature:
        _sample = _creature['sample']; _brief = _creature['bounty']
        SAMPLES[_cid] = tuple(_sample[k] for k in ('id','name','properties','price','collection'))
        BRIEFS[_cid] = tuple(_brief[k] for k in ('name','client','reason','kind','route','crowns'))
CONTRACTS = {cid:dict(id=cid,creatureId=cid,enemyId=bestiary.CREATURES[cid]['enemyId'],name=row[0],client=row[1],reason=row[2],kind=row[3],route=row[4],crowns=row[5],materialId=SAMPLES[cid][0],collect=2,deliver=1 if row[3]=='sample' else 0) for cid,row in BRIEFS.items()}


def install(g):
    import headquarters
    headquarters.JOBS.update(deepcopy(IMPROVEMENTS))
    headquarters.ROOMS['library']['views'].append('bestiary')
    headquarters.ROOMS['watchtower']['views'].extend(['bounties','bestiary'])
    for cid,(key,name,properties,price,collection) in SAMPLES.items():
        g['MATERIALS'][key]={'name':name,'properties':properties[:],'price':price,'creatureId':cid,'collection':collection,'rare':True,'icon':'/assets/materials/'+key+'.webp'}


def initialize(s):
    for key,*_ in SAMPLES.values():
        s['materialInventory'].setdefault(key,0)
        s['materialReserveTargets'].setdefault(key,0)


def saved(s):
    return s.get('bounties', {'completed':{},'receipts':[]})


def blockers(s, key):
    import game as g,field_patrols
    if not isinstance(key,str) or key not in CONTRACTS:
        return ['Choose a posted creature bounty.']
    reasons=[]
    if not field_patrols.unlocked(s):reasons.append('Conclude Chapter 7 to unlock field bounties.')
    import creature_challenges
    reasons += creature_challenges.route_blockers(s, CONTRACTS[key]['route'])
    if not g.character_at_castle(s,'founder'):reasons.append('Return home before dispatching a bounty party.')
    if field_patrols.saved(s)['active']:reasons.append('Bring the active field party home first.')
    if saved(s)['completed'].get(key)==s['dayNumber']:reasons.append('This client’s request is complete today. Another request is available tomorrow.')
    return reasons


def attach(run, key):
    d=CONTRACTS[key]
    run.update(bountyId=key,bountyContract=deepcopy(d))


def collect(s, run, creature_id):
    """Collect only after a rewarded resolution; skipped enemies grant nothing."""
    if creature_id not in SAMPLES:return
    material_id=SAMPLES[creature_id][0]
    quantity=run['bountyContract']['collect'] if run.get('bountyId')==creature_id else 1
    run['loot']['materials'][material_id]=run['loot']['materials'].get(material_id,0)+quantity


def returned(s, run, complete):
    if not run.get('bountyId'):return None
    d=run['bountyContract'];loot=run['loot']
    if not complete or not any(o.get('rewarded') for o in run['outcomes']):return d['client']+': bounty unfinished; no contract payment.'
    n=d['deliver'];key=d['materialId']
    if loot['materials'].get(key,0)<n:return d['client']+': the requested sample was not recovered; no contract payment.'
    if n:
        loot['materials'][key]-=n
        if not loot['materials'][key]:del loot['materials'][key]
    loot['crowns']+=d['crowns']
    r=s.setdefault('bounties',deepcopy(saved(s)));r['completed'][d['id']]=s['dayNumber']
    r['receipts']=(r['receipts']+[dict(id=d['id'],name=d['name'],client=d['client'],crowns=d['crowns'],delivered=n,kept=d['collect']-n,materialId=key,day=s['dayNumber'],party=run['party'][:])])[-20:]
    import game as g
    return d['client']+' paid '+str(d['crowns'])+' crowns for '+d['name'].lower()+'. '+str(n)+' '+g.MATERIALS[key]['name']+' delivered; '+str(d['collect']-n)+' kept for crafting.'


ENCHANT_PROPERTIES = {'sure-footing':'rare-flow','clear-measure':'rare-focus','measured-force':'rare-force','seal-hand':'rare-binding','steady-channel':'rare-focus','weather-seal':'rare-guard','heat-ward':'rare-heat'}
SIGNATURE_PROPERTIES = {'edge':'rare-force','guard':'rare-guard','care':'rare-care','personal':'rare-flow'}
PROPERTY_NAMES = {'rare-flow':'Advanced movement and channel control','rare-focus':'Advanced precision enchantments','rare-force':'Advanced force enchantments','rare-binding':'Advanced inscription binding','rare-guard':'Advanced protective enchantments','rare-heat':'Advanced heat enchantments','rare-care':'Advanced healing equipment'}
IMPROVEMENTS = {
 'field-remedy-cabinet': dict(name='Stock an advanced field-remedy cabinet',room='infirmary',cost=80,phases=4,output='field-remedy-cabinet',once=True,needs=['enchanting-room'],principles=['gentle-preservation'],materials={'hydra-resin':2,'wyvern-venom-crystal':1,'owlbear-down':2},benefit='First aid during difficult creature encounters restores 3 vitality instead of 2, still clears venom and stone stiffness, and still costs 1 unreserved silver ivy.'),
 'warded-watch-network': dict(name='Build a warded watch network',room='watchtower',cost=60,phases=4,output='warded-watch-network',once=True,needs=['guard-barracks','enchanting-room'],principles=['field-calibration'],materials={'ward-stone-chip':2,'watch-iron':2,'slate-scale':1},benefit='Adds 1 party cover on field patrols and bounties. Total party cover remains capped at 3.'),
 'deep-heat-bench': dict(name='Build a controlled-heat enchanting bench',room='enchanting-room',cost=70,phases=4,output='deep-heat-bench',once=True,needs=['vault'],principles=['field-calibration'],materials={'kiln-cinder':2,'storm-antler':2,'lantern-dust':1},benefit='Strengthening enchantments, adding quiet mode and upgrading signature equipment to rank 2 each gain 1 extra work per assigned phase.'),
 'recovery-ward': dict(name='Build a permanent infirmary recovery ward',room='infirmary',cost=60,phases=4,output='recovery-ward',once=True,needs=['enchanting-room','vault'],principles=['water-guidance','field-calibration'],materials={'bridge-moss':2,'grave-silk':2,'wolf-underfur':1},benefit='Resting at the castle restores 1 extra vitality per phase, up to the normal maximum of 6. Food shortages still cap recovery at 1.'),
}

def choose(s, prop):
    import game as g
    options=sorted((k for k,d in g.MATERIALS.items() if prop in d['properties']),key=lambda k:(g.MATERIALS[k]['price'],k))
    return next((k for k in options if s['materialInventory'].get(k,0)>s['materialReserveTargets'].get(k,0)),options[0])

def advanced_work(s, job):
    return bool(s['headquarters']['stock'].get('deep-heat-bench')) and (job['operation'] in ('strengthen','refine') or (job['operation']=='signature-refinement' and job.get('refinementRank')==2))

def uses(material_id):
    import game as g,armoury
    props=set(g.MATERIALS[material_id]['properties']);rows=[]
    for key,prop in ENCHANT_PROPERTIES.items():
        if prop in props:rows.append(dict(id=key,name='Strengthen '+armoury.ENCHANTS[key]['name']+' to rank 2',view='armoury',quantity=1))
    if 'rare-binding' in props:rows.append(dict(id='refine',name='Add quiet mode to a rank-2 inscription',view='armoury',quantity=1))
    for key,prop in SIGNATURE_PROPERTIES.items():
        if prop in props:rows.append(dict(id=key,name='Upgrade signature equipment to rank 2: '+{'edge':'Precision','guard':'Shelter','care':'Care','personal':'personal refinement'}[key],view='armoury',quantity=1))
    for key,d in IMPROVEMENTS.items():
        if material_id in d['materials']:rows.append(dict(id=key,name=d['name'],view='hqRoom',roomId=d['room'],quantity=d['materials'][material_id]))
    import rare_accessories
    for key,d in rare_accessories.RECIPES.items():
        if material_id==d['drop']:rows.append(dict(id=key,name='Craft rare '+d['name'],view='armoury',quantity=2))
    return rows


def view(s):
    import game as g
    return {'offers':[{**deepcopy(d),'challengeTier':bestiary.CREATURES[cid].get('challengeTier','Standard'),'preparation':bestiary.CREATURES[cid].get('preparation',''),'creatureName':bestiary.CREATURES[cid]['name'],'art':bestiary.CREATURES[cid]['thumbnail'],'materialName':g.MATERIALS[d['materialId']]['name'],'keep':d['collect']-d['deliver'],'ordinaryMaterials':deepcopy(bestiary.ENCOUNTERS[d['enemyId']]['materials']),'blockers':blockers(s,cid)} for cid,d in CONTRACTS.items()], 'receipts':deepcopy(saved(s)['receipts'])}
