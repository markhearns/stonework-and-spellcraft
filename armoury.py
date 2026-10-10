"""Unified physical equipment, atomic loadouts and funded work.

Legacy dictionaries are compatibility projections; new objects and slot occupancy
live here. Named legacy actions are reconciled after completion, never counted twice.
"""
from copy import deepcopy
from pathlib import Path
import json
DATA=json.loads(Path(__file__).with_name('equipment_catalogue.json').read_text())
SLOTS=DATA['slots']; MODES=('household','expedition','social')
CATALOG={d['id']:d for d in DATA['items']}
ENCHANTS={d['id']:d for d in DATA['newEnchantments']}
FOCUS_MAP={'founder':'field-staff','mira':'focus-clasp','tamsin':'engraving-tool','iona':'plain-pendant','aurelia':'plain-pendant','neris':'plain-pendant','sabine':'ward-key','koharu':'repair-hammer','zahra':'engraving-tool','fenna':'plain-pendant','kaede':'plain-pendant','elowen':'plain-pendant','nyssara':'engraving-tool','sylva':'plain-pendant'}
STARTERS={'velis':'field-staff','kaede':'steel-kanabo','aurelia':'steel-spear','zahra':'repair-hammer','koharu':'repair-hammer','sabine':'ward-key','nyssara':'engraving-tool','sylva':'steel-knife','mira':'field-staff','tamsin':'steel-knife','neris':'steel-spear','elowen':'field-staff'}
LEGACY_STOCK={'blade':'steel-sword','armour':'leather-coat','warded-armour':'leather-coat'}

def state(s):return s['armoury']
def initialize(s):
    s.setdefault('armoury',{'items':{},'loadouts':{},'mode':{},'jobs':{},'nextNumber':1,'starterGrants':[], 'workAgreements':[], 'patterns':{},'proofs':[], 'signatures':{},'memories':[], 'stockMirror':{},'legacyMirror':{},'receipts':[], 'commissionDelivered':False})
    sync(s)

def number(s,prefix='gear'):
    r=state(s);n=r['nextNumber'];r['nextNumber']+=1;return prefix+'-'+str(n)

def make(s,definition,owner='household',key=None,**kw):
    d=CATALOG[definition];key=key or number(s)
    item=dict(id=key,definitionId=definition,ownerId=owner,name=d['name'],location='armoury',fitOwner=owner if owner!='household' else None,capacity=1,enchantments={},locked=False,ownershipHistory=[owner],starter=False,legacy=None)
    item.update(kw);state(s)['items'][key]=item;return item

def loadout(s,who,mode=None):
    mode=mode or state(s)['mode'].get(who,'household')
    return state(s)['loadouts'].get(who,{}).get(mode,{'slots':{},'active':{}})

def ensure_person(s,who):
    r=state(s);r['loadouts'].setdefault(who,{k:{'slots':{},'active':{}} for k in MODES});r['mode'].setdefault(who,'household')

def stamp(s):return {'day':s['dayNumber'],'phase':s['currentDayPhase']}
def equipped(s,key):return any(key in loadout(s,w)['slots'].values() for w in state(s)['loadouts'])
def busy(s,key):
    item=state(s)['items'][key]
    if item['location'] in ('job','vault'):return True
    if any(key in (j.get('itemId'),j.get('signatureItem')) for j in state(s)['jobs'].values()):return True
    legacy=item.get('legacy') or {}
    if legacy.get('kind')=='tool':return any(p['itemId']==legacy['id'] for p in s.get('toolUpgradeProjects',{}).values())
    if legacy.get('kind')=='focus':return bool(s['focusProjects'].get(legacy['id']))
    if legacy.get('kind')=='public':
        import public_workshop as pw
        return pw.locked(s,legacy['id'])
    return False

def slots_for(item,hand='hand1'):
    if item.get('slotOverride'):return item['slotOverride']
    d=CATALOG[item['definitionId']]
    return [hand] if d['alternateHand'] else d['slots'][:]

def remove_from_loadouts(s,key):
    for modes in state(s)['loadouts'].values():
        for l in modes.values():
            l['slots']={k:v for k,v in l['slots'].items() if v!=key};l['active'].pop(key,None)

def put_in(s,who,key,mode,hand='hand1'):
    """Internal slot transaction; callers have validated intent and ownership."""
    ensure_person(s,who);l=loadout(s,who,mode);it=state(s)['items'][key];slots=slots_for(it,hand)
    displaced={l['slots'][sl] for sl in slots if sl in l['slots'] and l['slots'][sl]!=key}
    for old in displaced:
        l['slots']={sl:v for sl,v in l['slots'].items() if v!=old};l['active'].pop(old,None)
    l['slots']={sl:v for sl,v in l['slots'].items() if v!=key};l['slots'].update({sl:key for sl in slots})
    return sorted(displaced)

def sync(s):
    """Admit legacy objects/changes by stable ID, retaining paid projects."""
    r=state(s)
    for who in s.get('people',{}):ensure_person(s,who)
    mirror=r['legacyMirror']
    for key,o in s.get('personalEquipment',{}).items():
        ident='legacy:tool:'+key;old=mirror.get(ident);signature=[o['name'],o['ownerId'],o.get('inscription'),s.get('preparedEquipment',{}).get(o['ownerId'])==key]
        if old==signature:continue
        it=next((i for i in r['items'].values() if i.get('legacy')=={'kind':'tool','id':key}),None) or make(s,o['kind'],o['ownerId'],ident,legacy={'kind':'tool','id':key})
        object_id=it['id']
        if it['ownerId']!=o['ownerId']:remove_from_loadouts(s,object_id)
        it.update(name=o['name'],ownerId=o['ownerId'],fitOwner=o['ownerId'],ownershipHistory=deepcopy(o.get('ownershipHistory',[o['ownerId']])))
        if o.get('inscription'):it['enchantments']['legacy-tool']={'id':'legacy-tool','rank':1}
        if signature[-1]:
            for mode in MODES:
                put_in(s,o['ownerId'],object_id,mode)
                if o.get('inscription'):loadout(s,o['ownerId'],mode)['active'][object_id]=['legacy-tool']
        elif old and old[-1]:remove_from_loadouts(s,object_id)
        mirror[ident]=signature
    for who,o in s.get('signatureFocuses',{}).items():
        if o.get('publicItemId'):continue
        ident='legacy:focus:'+who;signature=[o['name'],o['capacity'],o['inscriptions'][:],o['householdLoadout'][:],o['expeditionLoadout'][:]]
        if mirror.get(ident)==signature:continue
        it=r['items'].get(ident) or make(s,FOCUS_MAP.get(who,'plain-pendant'),who,ident,legacy={'kind':'focus','id':who},locked=True)
        # Existing personal staffs and bodkins were one-hand foci. Preserve that mounting.
        if it['definitionId']=='field-staff':it['slotOverride']=['hand1']
        it.update(name=o['name'],capacity=max(o['capacity'],len(o['inscriptions']),1))
        for e in o['inscriptions']:it['enchantments'].setdefault('legacy:'+e,{'id':'legacy:'+e,'rank':1})
        for mode in ('household','expedition'):
            selected=['legacy:'+x for x in o[mode+'Loadout']]
            if selected:put_in(s,who,ident,mode)
            if selected:loadout(s,who,mode)['active'][ident]=selected
            else:loadout(s,who,mode)['active'].pop(ident,None)
        mirror[ident]=deepcopy(signature)
    for key,o in s.get('publicWorkshop',{}).get('items',{}).items():
        if o.get('kind')!='equipment':continue
        ident='legacy:public:'+key;signature=[o['name'],o['ownerId'],o.get('vaultStored',False),o.get('preparedInscription'),o.get('inscriptions',[])[:]]
        if mirror.get(ident)==signature:continue
        definition,mount=public_mount(o['definitionId'])
        it=r['items'].get(ident) or make(s,definition,o['ownerId'],ident,legacy={'kind':'public','id':key},slotOverride=mount)
        if it['ownerId']!=o['ownerId']:remove_from_loadouts(s,ident)
        it.update(name=o['name'],ownerId=o['ownerId'],fitOwner=o['ownerId'],location='vault' if o.get('vaultStored') else 'armoury',ownershipHistory=deepcopy(o.get('ownershipHistory',[o['ownerId']])))
        for e in o.get('inscriptions',[]):it['enchantments'].setdefault('public:'+e,{'id':'public:'+e,'rank':1})
        it['capacity']=max(1,len(it['enchantments']))
        for mode in MODES:
            if o.get('preparedInscription'):
                put_in(s,o['ownerId'],ident,mode);loadout(s,o['ownerId'],mode)['active'][ident]=['public:'+o['preparedInscription']]
            elif mirror.get(ident) and mirror[ident][3]:
                l=loadout(s,o['ownerId'],mode);l['slots']={sl:v for sl,v in l['slots'].items() if v!=ident};l['active'].pop(ident,None)
        mirror[ident]=deepcopy(signature)
    signature=r['signatures'].get('sabine')
    if signature and signature.get('completedOn') and s.get('headquarters',{}).get('stock',{}).get('specialty:sabine'):
        host=r['items'].get(signature['itemId'])
        if host and host['ownerId']=='sabine':
            host['enchantments'].setdefault('dungeon-keeper',{'id':'dungeon-keeper','rank':1});host['capacity']=max(host['capacity'],len(host['enchantments']))
    # Stock deltas only admit genuinely newly forged legacy output; new actions
    # update stockMirror together with their canonical changes.
    h=s.get('headquarters',{})
    for stock,definition in LEGACY_STOCK.items():
        n=h.get('stock',{}).get(stock,0);old=r['stockMirror'].get(stock,0)
        for _ in range(max(0,n-old)):
            it=make(s,definition,legacy={'kind':'stock','id':stock})
            if stock=='warded-armour':it['enchantments']['legacy-ward']={'id':'legacy-ward','rank':1}
        if n<old:
            candidates=[i for i in r['items'].values() if stock_kind(i)==stock and i['location']=='armoury' and not equipped(s,i['id'])]
            for it in candidates[:old-n]:it['location']='legacy-held'
        r['stockMirror'][stock]=n
    if h.get('armourEquipped') and not r.get('legacyWardImported'):
        it=next((i for i in r['items'].values() if stock_kind(i)=='warded-armour' and i['location']=='armoury'),None)
        if it:
            it['ownerId']='founder';it['fitOwner']='founder'
            for mode in ('household','expedition'):
                put_in(s,'founder',it['id'],mode);loadout(s,'founder',mode)['active'][it['id']]=['legacy-ward']
            r['legacyWardImported']=True
    # Previously funded armour conversions retain their exact object and receipt.
    import headquarters as hq
    for who,p in hq.projects(s).items():
        if p.get('id')=='enchant-armour' and not p.get('equipmentItemId'):
            it=next((i for i in r['items'].values() if i['location']=='legacy-held'),None) or make(s,'leather-coat',legacy={'kind':'stock','id':'armour'})
            it['location']='job';p['equipmentItemId']=it['id']

def stock_kind(it):
    if it['definitionId']=='steel-sword':return 'blade'
    if 'legacy-ward' in it['enchantments']:return 'warded-armour'
    if it['definitionId'] in ('leather-coat','mail-shirt','breastplate'):return 'armour'
    return None

def export(s):
    r=state(s)
    for it in r['items'].values():
        legacy=it.get('legacy') or {};kind=legacy.get('kind');key=legacy.get('id')
        if kind=='tool' and key in s['personalEquipment']:
            o=s['personalEquipment'][key];o.update(name=it['name'],ownerId=it['ownerId'],ownershipHistory=deepcopy(it['ownershipHistory']))
            for who,selected in list(s['preparedEquipment'].items()):
                if selected==key:s['preparedEquipment'].pop(who)
            if equipped(s,it['id']):s['preparedEquipment'][it['ownerId']]=key
        elif kind=='focus':
            o=s['signatureFocuses'][key];o['name']=it['name']
            for mode in ('household','expedition'):
                l=loadout(s,it['ownerId'],mode)
                o[mode+'Loadout']=[e.removeprefix('legacy:') for e in l['active'].get(it['id'],[]) if e.startswith('legacy:')] if it['id'] in l['slots'].values() else []
        elif kind=='public' and key in s['publicWorkshop']['items']:
            o=s['publicWorkshop']['items'][key];o.update(name=it['name'],ownerId=it['ownerId'],vaultStored=it['location']=='vault',ownershipHistory=deepcopy(it['ownershipHistory']))
            for who,selected in list(s['publicWorkshop']['preparedItems'].items()):
                if selected==key:s['publicWorkshop']['preparedItems'].pop(who)
            l=loadout(s,it['ownerId']);selected=next((e.removeprefix('public:') for e in l['active'].get(it['id'],[]) if e.startswith('public:')),None)
            o['preparedInscription']=selected if equipped(s,it['id']) else None
            if o['preparedInscription']:s['publicWorkshop']['preparedItems'][it['ownerId']]=key
    for k in LEGACY_STOCK:
        n=sum(stock_kind(i)==k and i['location']=='armoury' for i in r['items'].values())
        s['headquarters']['stock'][k]=n;r['stockMirror'][k]=n
    s['headquarters']['armourEquipped']=any(e['effect']=='legacy-ward' for e in effects(s,'founder','expedition'))
    r['legacyWardImported']=True
    # Capture projections to avoid replaying changes on the next reconciliation.
    for key,o in s['personalEquipment'].items():r['legacyMirror']['legacy:tool:'+key]=[o['name'],o['ownerId'],o.get('inscription'),s['preparedEquipment'].get(o['ownerId'])==key]
    for who,o in s['signatureFocuses'].items():r['legacyMirror']['legacy:focus:'+who]=[o['name'],o['capacity'],o['inscriptions'][:],o['householdLoadout'][:],o['expeditionLoadout'][:]]
    for key,o in s['publicWorkshop']['items'].items():
        if o.get('kind')=='equipment':r['legacyMirror']['legacy:public:'+key]=[o['name'],o['ownerId'],o.get('vaultStored',False),o.get('preparedInscription'),o.get('inscriptions',[])[:]]

def effects(s,who,mode=None):
    if 'armoury' not in s:return []
    l=loadout(s,who,mode);rows=[]
    for key in set(l['slots'].values()):
        it=state(s)['items'].get(key)
        if not it or it['ownerId']!=who or it['location']!='armoury' or busy(s,key):continue
        for e in l['active'].get(key,[]):
            enchant=it['enchantments'].get(e)
            if enchant and (mode is None or mode==state(s)['mode'].get(who,'household') or e.startswith(('legacy','public:'))):rows.append({'itemId':key,'name':it['name'],'effect':e,'rank':enchant['rank'],'refinement':enchant.get('refinement')})
    return rows

def has(s,who,e,mode=None):return any(x['effect']==e for x in effects(s,who,mode))
def approach_bonus(s,who,tags,mode='expedition'):
    rows=[x for x in effects(s,who,mode) if x['effect'] in ENCHANTS and ENCHANTS[x['effect']]['effectKind']=='score' and ENCHANTS[x['effect']]['stackingGroup'] in tags]
    return min(2,max((x['rank'] for x in rows),default=0)),rows

def channel_cost(effect):
    return effect['rank'] if effect['id'] in ENCHANTS else 1

def validate_loadout(s,who,l):
    import game as g
    g.require(isinstance(l,dict) and set(l)=={'slots','active'} and isinstance(l['slots'],dict) and isinstance(l['active'],dict),'Choose a complete slot and enchantment configuration.')
    g.require(set(l['slots'])<=set(SLOTS),'Use the nine equipment slots.')
    total=0;focus_families=set()
    for key in set(l['slots'].values()):
        it=state(s)['items'].get(key)
        g.require(it is not None and it['ownerId']==who,'A loadout item is missing or belongs to someone else.')
        g.require(it['location']=='armoury' and not busy(s,key),'Finish reserved work or retrieve the item from the vault first.')
        g.require(it['fitOwner'] in (None,who),'Refit this item for its new owner first.')
        occupied={sl for sl,v in l['slots'].items() if v==key}
        if CATALOG[it['definitionId']]['alternateHand']:g.require(occupied <= {'hand1','hand2'},'Hand equipment belongs in a hand slot.')
        expected=set(slots_for(it,next(iter(occupied))))
        g.require(occupied==expected,'A multi-slot object must occupy all of its slots.')
        selected=l['active'].get(key,[])
        g.require(isinstance(selected,list) and len(selected)==len(set(selected)) and all(e in it['enchantments'] for e in selected),'Select installed inscriptions once each.')
        for e in selected:
            total+=channel_cost(it['enchantments'][e])
            if e.startswith('legacy:'):focus_families.add('baseline')
            if e.startswith('public:'):focus_families.add('public')
    g.require(set(l['active'])<=set(l['slots'].values()),'Only equipped items can have selected inscriptions.')
    g.require(total<=4,'This loadout needs '+str(total)+' active channels; four are available.')
    g.require(len(focus_families)<=1,'Choose baseline or public focus inscriptions in this loadout, not both.')
    return total

def home(s,who='founder'):
    import game as g
    g.require(who in g.household_members(s),'Choose a current household member.')
    g.require(g.character_at_castle(s,'founder') and g.character_at_castle(s,who),'Return home together before changing equipment.')

def owned(s,key,who=None):
    import game as g
    g.require(isinstance(key,str) and key in state(s)['items'],'Choose an existing item.');it=state(s)['items'][key]
    if who is not None:g.require(it['ownerId']==who,'Choose this person’s own item.')
    return it

def review_starters(s,people=None):
    import game as g
    r=state(s)
    for who in (g.household_members(s) if people is None else people):
        if who in r['starterGrants'] or not g.character_at_castle(s,who):continue
        ensure_person(s,who);existing=[i for i in r['items'].values() if i['ownerId']==who]
        categories=[(STARTERS.get(who,'steel-sword'),lambda i:bool(set(CATALOG[i['definitionId']]['tags'])&{'weapon','tool'})),('work-shirt',lambda i:'shirt' in slots_for(i)),('work-trousers',lambda i:'pants' in slots_for(i))]
        if who!='sylva':categories.append(('field-boots',lambda i:'boots' in slots_for(i)))
        for definition,predicate in categories:
            if any(predicate(i) for i in existing):continue
            it=make(s,definition,who,starter=True);existing.append(it)
            for mode in MODES:
                if not any(sl in loadout(s,who,mode)['slots'] for sl in slots_for(it)):put_in(s,who,it['id'],mode)
        candidate=next((i for i in existing if set(CATALOG[i['definitionId']]['tags'])&{'weapon','tool'} and i['location']=='armoury'),None)
        if candidate:
            for mode in MODES:
                if not any(sl in loadout(s,who,mode)['slots'] for sl in slots_for(candidate)):put_in(s,who,candidate['id'],mode)
        r['starterGrants'].append(who)
    g.add_journal(s,'Reviewed the household’s ordinary equipment. Existing names, upgrades and fitted pieces were kept.')

def worker_blockers(s,who,magic=False):
    import game as g
    reasons=[]
    if who not in g.household_members(s) or not g.character_at_castle(s,who):return ['Choose a household worker at home.']
    if not g.character_at_castle(s,'founder'):reasons.append('Return home to agree this work.')
    if who!='founder' and who not in state(s)['workAgreements']:reasons.append('Agree equipment work with this resident first.')
    if who in state(s)['jobs']:reasons.append('Finish or cancel this worker’s funded equipment job first.')
    if magic and (s['focusProjects'].get(who) or s['toolUpgradeProjects'].get(who)):reasons.append('Finish existing focus or tool inscription work first.')
    return reasons

def recipe(s,a):
    """Pure quotation shared by previews and actions; no resource mutation."""
    import game as g, headquarters as h
    import bounty_contracts
    kind=a.get('operation','craft');g.require(kind not in ('craft','commission') or not a.get('itemId'),'New objects and client commissions do not reserve an owned host.');who=a.get('workerId','founder');key=a.get('itemId');it=state(s)['items'].get(key)
    reasons=worker_blockers(s,who,kind!='craft');cost=0;phases=1;properties=[];room='enchanting-room';name='Equipment work';effect=a.get('enchantmentId');extra={}
    if kind=='craft':
        d=CATALOG.get(a.get('definitionId'));g.require(d is not None,'Choose a catalogue object.')
        cost=d['baseCostCrowns'] or 0;phases=d['workPhases'];room=d['room'];name='Make '+d['name'];extra['definitionId']=d['id']
        import resident_specialties as specialties
        if room=='smithy' and specialties.active(s,'zahra'):phases=max(1,phases-1)
        if d['baseCostCrowns'] is None:
            properties=['vessel','binding'];extra['legacyTool']=True
            principle='reference-binding' if d['id']=='scholars-folio' else 'clear-instruction'
            if principle not in g.character_principles(s,who):reasons.append('The maker must have learned '+g.PRINCIPLE_NAMES[principle]+'.')
    elif kind=='commission':
        effect='sure-footing';cost=0;phases=2;name='Client’s sure-footed boots';extra['tutorial']=not state(s)['commissionDelivered']
        if any(j['operation']=='commission' for j in state(s)['jobs'].values()) or state(s).get('commissionReady'):reasons.append('Deliver or cancel the current equipment commission first.')
        if ENCHANTS[effect]['requiredPersonalPrinciple'] not in g.character_principles(s,who):reasons.append('The worker must have learned Water guidance.')
    else:
        if not it:reasons.append('Choose an existing owned item.')
        elif it['ownerId'] not in ('household',who) and it['ownerId'] not in g.household_members(s):reasons.append('The owner must be a current household member.')
        elif it['ownerId']!='household' and not g.character_at_castle(s,it['ownerId']):reasons.append('Bring the owner home to agree the work.')
        if it and (busy(s,key) or equipped(s,key)):reasons.append('Stow the item and finish its reserved work first.')
        if kind in ('enchant','strengthen'):
            d=ENCHANTS.get(effect);g.require(d is not None,'Choose a supported enchantment.')
            cost=8 if kind=='enchant' else 12;phases=2 if kind=='enchant' else 3;properties=['vessel','binding'];name=('Inscribe ' if kind=='enchant' else 'Strengthen ')+d['name']
            if kind=='strengthen' and effect in bounty_contracts.ENCHANT_PROPERTIES:properties.append(bounty_contracts.ENCHANT_PROPERTIES[effect])
            if d['requiredPersonalPrinciple'] not in g.character_principles(s,who):reasons.append('The worker must have learned '+g.PRINCIPLE_NAMES[d['requiredPersonalPrinciple']]+'.')
            if it and not set(d['hostAnyTag'])&set(CATALOG[it['definitionId']]['tags']):reasons.append('This effect needs a compatible host.')
            if it and kind=='enchant' and (effect in it['enchantments'] or len(it['enchantments'])>=it['capacity']):reasons.append('Use a free inscription setting; do not duplicate an effect.')
            if it and kind=='strengthen' and (effect not in it['enchantments'] or it['enchantments'][effect]['rank']!=1 or d['effectKind']!='score'):reasons.append('Choose an installed rank-one score effect.')
        elif kind=='expand':
            cost=10;phases=2;properties=['vessel','binding'];name='Expand inscription settings'
            if it and it['capacity']>=2:reasons.append('This item already has at least two settings.')
        elif kind=='refit':cost=4;phases=1;room='workshop';name='Refit equipment'
        elif kind=='extract':
            cost=4;properties=['binding'];name='Recover an inscription pattern'
            if it and (effect not in ENCHANTS or effect not in it['enchantments']):reasons.append('Choose an installed transferable inscription.')
        elif kind=='install-pattern':
            cost=4;properties=['vessel'];name='Install a recovered pattern';pattern=state(s)['patterns'].get(a.get('patternId'));extra['patternId']=a.get('patternId')
            if not pattern:reasons.append('Choose an available recovered pattern.')
            elif it:
                effect=pattern['id']
                if ENCHANTS[effect]['requiredPersonalPrinciple'] not in g.character_principles(s,who):reasons.append('Personally learn the recovered pattern’s principle before installing it.')
                if pattern.get('ownerId') not in (it['ownerId'],'household'):reasons.append('The pattern belongs to another owner.')
                if effect in it['enchantments'] or len(it['enchantments'])>=it['capacity'] or not set(ENCHANTS[effect]['hostAnyTag'])&set(CATALOG[it['definitionId']]['tags']):reasons.append('The pattern needs a free compatible setting.')
        elif kind=='refine':
            cost=6;phases=2;properties=['binding','rare-binding'];name='Refine the inscription’s control'
            if it and (effect not in ENCHANTS or effect not in it['enchantments'] or it['enchantments'][effect].get('refinement')):reasons.append('Choose an installed, unrefined new inscription.')
            # Concrete refinement: permits the ordinary rank-one mode of a rank-two
            # inscription, spending one channel instead of two, at home.
            if it and effect in it['enchantments'] and it['enchantments'][effect]['rank']!=2:reasons.append('Strengthen the score inscription before adding a selectable quiet mode.')
        else:raise g.RuleError('Choose a known equipment operation.')
        if kind not in ('refit',) and 'field-calibration' not in g.character_principles(s,who):reasons.append('The worker must have learned Field calibration.')
    if not h.ready(s,room):reasons.append('Restore '+h.ROOMS[room]['name']+' first.')
    materials=a.get('materials')
    import rare_accessories
    fixed=None
    if kind=='craft' and extra.get('definitionId') in rare_accessories.RECIPES:
        fixed,rare_blockers=rare_accessories.quote(s,extra['definitionId'],who);reasons+=rare_blockers
        if materials is not None and materials!=fixed:reasons.append('This rare accessory needs its exact listed creature samples and binding components.')
        materials=fixed[:]
    if materials is None:
        available={k:max(0,n-s['materialReserveTargets'].get(k,0)) for k,n in s['materialInventory'].items()};materials=[]
        for prop in properties:
            choices=sorted((k for k,n in available.items() if n and prop in g.MATERIALS[k]['properties']),key=lambda k:(g.MATERIALS[k]['price'],k))
            chosen=choices[0] if choices else min((k for k,d in g.MATERIALS.items() if prop in d['properties']),key=lambda k:(g.MATERIALS[k]['price'],k))
            materials.append(chosen);available[chosen]-=1
    if fixed is None and (not isinstance(materials,list) or len(materials)!=len(properties) or any(not isinstance(k,str) or k not in g.MATERIALS or prop not in g.MATERIALS[k]['properties'] for k,prop in zip(materials,properties))):
        reasons.append('Choose exactly the listed compatible components.');materials=[]
    shortfalls={m:max(0,materials.count(m)+s['materialReserveTargets'].get(m,0)-s['materialInventory'][m]) for m in set(materials)}
    shortfalls={m:n for m,n in shortfalls.items() if n}
    for material in set(materials):
        if s['materialInventory'][material]-s['materialReserveTargets'].get(material,0)<materials.count(material):reasons.append('Needs '+str(materials.count(material))+' unreserved '+g.MATERIALS[material]['name']+'.')
    if s['sharedFunds']<cost:reasons.append('Requires '+str(cost)+' available crowns.')
    return dict(operation=kind,workerId=who,itemId=key,effect=effect,name=name,cost=cost,phases=phases,done=0,materials=materials,supplyShortfalls=shortfalls,supplyCost=sum(g.MATERIALS[m]['price']*n for m,n in shortfalls.items() if not g.MATERIALS[m].get('rare')),room=room,blockers=list(dict.fromkeys(reasons)),**extra)

def working(s,who):
    import game as g
    import signature_equipment
    return who in state(s)['jobs'] and signature_equipment.job_ready(s,state(s)['jobs'][who]) and g.character_at_castle(s,who) and g.character_assignment(s,who)=='equipment-work'

def resolve(s,summary,eligible):
    import game as g
    sync(s)
    for who in eligible:
        if not working(s,who):continue
        j=state(s)['jobs'][who]
        import bounty_contracts
        j['done']=min(j['phases'],j['done']+1+int(bounty_contracts.advanced_work(s,j)))
        summary.append(g.character_profile(s,who)['name']+' · '+j['name']+': '+str(j['done'])+'/'+str(j['phases'])+' phases.')
        if j['done']<j['phases']:continue
        it=state(s)['items'].get(j['itemId']);effect=j['effect'];kind=j['operation']
        if kind=='craft':
            it=make(s,j['definitionId'],'household')
            if j.get('legacyTool'):
                # An individually owned folio/gauge uses the established work adapter.
                tid=number(s,'tool');it['ownerId']=who;it['fitOwner']=who;it['ownershipHistory']=[who];it['legacy']={'kind':'tool','id':tid}
                s['personalEquipment'][tid]={'kind':it['definitionId'],'ownerId':who,'name':it['name'],'ownershipHistory':[who],'inscription':None}
        elif kind=='commission':state(s)['commissionReady']={'pay':12 if j['tutorial'] else 8,'tutorial':j['tutorial'],'workerId':who}
        elif kind in ('signature-fit','signature-proof'):
            import signature_equipment
            signature_equipment.finish(s,j)
        elif kind=='signature-refinement':
            import signature_growth
            signature_growth.finish(s,j)
        elif kind=='enchant':it['enchantments'][effect]={'id':effect,'rank':1}
        elif kind=='strengthen':it['enchantments'][effect]['rank']=2
        elif kind=='expand':it['capacity']=2
        elif kind=='refit':it['fitOwner']=it['ownerId']
        elif kind=='extract':
            pattern=it['enchantments'].pop(effect);pattern['ownerId']=it['ownerId'];state(s)['patterns'][number(s,'pattern')]=pattern
        elif kind=='install-pattern':it['enchantments'][effect]=j['heldPattern']
        elif kind=='refine':it['enchantments'][effect]['refinement']='quiet-mode'
        if it:it['location']='armoury'
        state(s)['receipts'].append({**stamp(s),'operation':kind,'itemId':it['id'] if it else None,'effect':effect,'workerId':who})
        del state(s)['jobs'][who];g.set_character_assignment(s,who,'rest')
        summary.append(j['name']+' completed. Equipment activation remains your choice.')
    export(s)

def finish_hq(s,p,cancel=False):
    """Preserve the same armour through legacy paid warding jobs."""
    if 'armoury' not in s:return
    key=p.get('equipmentItemId')
    if key:
        it=state(s)['items'][key];it['location']='armoury'
        if not cancel:it['enchantments']['legacy-ward']={'id':'legacy-ward','rank':1}
        export(s)
    elif not cancel and p['id'] in ('blade','armour'):
        make(s,LEGACY_STOCK[p['id']],legacy={'kind':'stock','id':p['id']});export(s)

def apply(s,a):
    import game as g
    kind=a.get('type','')
    if not isinstance(kind,str) or not kind.startswith('gear-'):return False
    who=a.get('ownerId','founder');home(s,who);r=state(s);key=a.get('itemId');mode=a.get('mode',r['mode'].get(who,'household'))
    g.require(mode in MODES,'Choose household, expedition or social equipment.')
    if kind=='gear-review':review_starters(s)
    elif kind=='gear-agree-work':
        target=a.get('workerId',who);home(s,target);g.require(type(a.get('enabled')) is bool,'Choose whether to agree equipment work.')
        g.require(a['enabled'] or target not in r['jobs'],'Finish or cancel funded work first.')
        if a['enabled'] and target not in r['workAgreements']:r['workAgreements'].append(target)
        elif not a['enabled'] and target in r['workAgreements']:r['workAgreements'].remove(target)
    elif kind in ('gear-equip','gear-ready','gear-stow','gear-activate','gear-quiet-mode'):
        it=owned(s,key,who);g.require(not busy(s,key),'Finish reserved work or retrieve this item first.')
        if kind=='gear-stow':
            for m in MODES:
                l=loadout(s,who,m);l['slots']={sl:v for sl,v in l['slots'].items() if v!=key};l['active'].pop(key,None)
        elif kind in ('gear-equip','gear-ready'):
            g.require(a.get('hand','hand1') in ('hand1','hand2'),'Choose a hand.')
            displaced=put_in(s,who,key,mode,a.get('hand','hand1'))
            g.require(not displaced or a.get('replaceConfirmed') is True,'Review the pieces that will be stowed before replacing them.')
            if kind=='gear-ready':
                e=a.get('enchantmentId');g.require(e in it['enchantments'],'Choose an installed inscription.')
                chosen=loadout(s,who,mode)['active'].setdefault(key,[])
                if e not in chosen:chosen.append(e)
            validate_loadout(s,who,loadout(s,who,mode));r['mode'][who]=mode
        elif kind=='gear-activate':
            l=loadout(s,who,mode);g.require(key in l['slots'].values(),'Equip this item in this loadout first.')
            l['active'][key]=a.get('enchantments');validate_loadout(s,who,l)
        else:
            e=a.get('enchantmentId');g.require(e in it['enchantments'] and it['enchantments'][e].get('refinement')=='quiet-mode','Add a quiet-mode refinement first.')
            g.require(type(a.get('quiet')) is bool,'Choose the operating mode.')
            it['enchantments'][e]['rank']=1 if a['quiet'] else 2
            for m in MODES:validate_loadout(s,who,loadout(s,who,m))
    elif kind=='gear-save-loadout':
        source=a.get('sourceMode',r['mode'].get(who,'household'));g.require(source in MODES,'Choose a source loadout.')
        proposal=deepcopy(a.get('loadout',loadout(s,who,source)));validate_loadout(s,who,proposal);r['loadouts'][who][mode]=proposal
    elif kind in ('gear-apply-loadout','gear-party-loadout'):
        people=a.get('participants',[who]) if kind=='gear-party-loadout' else [who]
        g.require(isinstance(people,list) and 1<=len(people)<=30 and len(people)==len(set(people)),'Choose distinct household members.')
        for w in people:home(s,w);validate_loadout(s,w,loadout(s,w,mode))
        for w in people:r['mode'][w]=mode
    elif kind in ('gear-rename','gear-lock','gear-transfer','gear-allocate','gear-sell','gear-vault','gear-remove-enchantment'):
        it=owned(s,key);g.require(it['ownerId'] in (who,'household'),'Choose your own or household equipment.')
        if kind=='gear-rename':it['name']=g.text_value(a.get('name'),60)
        elif kind=='gear-lock':g.require(type(a.get('locked')) is bool,'Choose whether to protect this item.');it['locked']=a['locked']
        else:
            g.require(not busy(s,key) or (kind=='gear-vault' and it['location']=='vault'),'Finish reserved work before moving this item.')
            g.require(not equipped(s,key),'Stow equipped items first.')
            if kind in ('gear-transfer','gear-allocate'):
                target=a.get('recipientId');home(s,target)
                g.require(target!=it['ownerId'],'Choose a different owner.');g.require(a.get('agreed') is True,'Both owners must agree the transfer.')
                remove_from_loadouts(s,key);it['ownerId']=target;it['ownershipHistory'].append(target)
                if it['fitOwner'] is None:it['fitOwner']=target
                if it['locked']:it['signatureRetired']=True
            elif kind=='gear-sell':
                g.require(not it['locked'] and not it.get('legacy') and not it['starter'],'This treasured, legacy or starter item cannot be sold.')
                g.require(a.get('confirmed') is True,'Confirm the displayed sale price.')
                s['sharedFunds']+=(CATALOG[it['definitionId']]['baseCostCrowns'] or 0)//2;remove_from_loadouts(s,key);del r['items'][key]
            elif kind=='gear-vault':
                import headquarters as h
                g.require(h.ready(s,'vault'),'Restore the warded vault first.');it['location']='armoury' if it['location']=='vault' else 'vault';remove_from_loadouts(s,key)
            else:
                e=a.get('enchantmentId');g.require(e in ENCHANTS and e in it['enchantments'],'Choose a removable new inscription.');g.require(a.get('confirmed') is True,'Confirm permanent removal without recovery.');it['enchantments'].pop(e)
                for l in r['loadouts'][who].values():
                    if key in l['active']:l['active'][key]=[x for x in l['active'][key] if x!=e]
    elif kind=='gear-start-job':
        prepare_host(s,a)
        quote=recipe(s,a);g.require(not quote['blockers'],' '.join(quote['blockers']));quote.pop('blockers');worker=quote['workerId']
        if key:owned(s,key);r['items'][key]['location']='job'
        s['sharedFunds']-=quote['cost']
        for k in quote['materials']:s['materialInventory'][k]-=1
        if quote['operation']=='install-pattern':quote['heldPattern']=r['patterns'].pop(quote['patternId'])
        r['jobs'][worker]=quote;g.set_character_assignment(s,worker,'equipment-work');g.add_journal(s,quote['name']+': '+str(quote['cost'])+' crowns and listed components committed; Advance performs the work.')
    elif kind in ('gear-resume-job','gear-cancel-job'):
        worker=a.get('workerId','founder');home(s,worker);j=r['jobs'].get(worker);g.require(j is not None,'Choose an unfinished equipment job.')
        if kind=='gear-resume-job':
            if j.get('signatureOwner'):
                home(s,j['signatureOwner'])
                if j['operation']=='signature-fit' and j['signatureOwner']!='founder':g.set_character_assignment(s,j['signatureOwner'],'signature-fitting')
            g.set_character_assignment(s,worker,'equipment-work')
        else:
            import signature_equipment
            signature_equipment.cancel(s,j)
            s['sharedFunds']+=j['cost']
            for k in j['materials']:s['materialInventory'][k]+=1
            if j.get('heldPattern'):r['patterns'][j['patternId']]=j['heldPattern']
            if j['itemId']:r['items'][j['itemId']]['location']='armoury'
            del r['jobs'][worker]
            if g.character_assignment(s,worker)=='equipment-work':g.set_character_assignment(s,worker,'rest')
    elif kind=='gear-deliver-commission':
        ready=r.get('commissionReady');g.require(ready is not None,'Finish a client commission first.');s['sharedFunds']+=ready['pay'];r['commissionReady']=None;r['commissionDelivered']=True
        g.add_journal(s,'Returned the client’s boots. Earned '+str(ready['pay'])+' crowns for skilled work; no client equipment entered the armoury.')
    elif kind=='gear-test':
        import headquarters as h
        g.require(h.ready(s,'training-yard') or h.ready(s,'enchanting-room'),'Restore the training yard or enchanting room for a safe proof.')
        it=owned(s,key,who);effect=a.get('enchantmentId');g.require(has(s,who,effect,mode),'Equip and activate this inscription before testing it.')
        g.require(effect in it['enchantments'] and any(e['itemId']==key and e['effect']==effect for e in effects(s,who,mode)),'Test the selected item’s active inscription.')
        proof={'itemId':key,'effect':effect,'ownerId':who}
        if not any(all(x.get(k)==v for k,v in proof.items()) for x in r['proofs']):r['proofs'].append({**proof,**stamp(s)});g.add_journal(s,it['name']+' passed a supervised '+enchantment_name(effect)+' test. No components consumed.')
    else:
        import signature_equipment
        import signature_growth
        if not (signature_growth.apply(s,a) or signature_equipment.apply(s,a)):raise g.RuleError('Unknown equipment action.')
    export(s);return True

def enchantment_name(e):
    if e in ENCHANTS:return ENCHANTS[e]['name']
    return {'legacy-tool':'Working-tool calibration','legacy-ward':'Field ward','dungeon-keeper':'Dungeon keeper’s seal (+1 precise seal work; dungeon specialty does not stack)'}.get(e,e.removeprefix('legacy:').removeprefix('public:').replace('-',' ').capitalize())

def preview(s,a):
    import game as g
    copy=deepcopy(s)
    try:apply(copy,a);return []
    except (g.RuleError,TypeError,KeyError,ValueError) as e:return [str(e)]

def item_art(s,it):
    """Use the same artwork for inventory and read-only equipment previews."""
    icon='/assets/equipment/'+CATALOG[it['definitionId']]['iconId']+'.webp'
    if (it.get('legacy') or {}).get('kind')=='public':
        from art_catalogue import OBJECT_ART
        legacy=s['publicWorkshop']['items'][it['legacy']['id']]
        icon=s.get('assetOverrides',{}).get('public-'+legacy['id']) or OBJECT_ART.get(legacy['definitionId'],icon)
    signatures={'rhess':'steel-spear','velis':'field-staff','founder':'field-staff','kaede':'steel-kanabo','sabine':'ward-key','nyssara':'engraving-tool'}
    if it.get('signatureOwner') in signatures and it['definitionId']==signatures[it['signatureOwner']]:
        icon='/assets/equipment/signature-'+it['signatureOwner']+'.webp'
    return icon

def view(s):
    import game as g, signature_equipment
    r=state(s);items={}
    for key,it in r['items'].items():
        if it['location']=='legacy-held':continue
        d=CATALOG[it['definitionId']];items[key]={**deepcopy(it),'slots':slots_for(it),'tags':d['tags'],'icon':item_art(s,it),'equipped':equipped(s,key),'busy':busy(s,key),'salePrice':0 if it['starter'] or it.get('legacy') else (d['baseCostCrowns'] or 0)//2,'enchantmentNames':{e:enchantment_name(e) for e in it['enchantments']}}
        if (it.get('legacy') or {}).get('kind')=='public':items[key]['imported']=True
    workers={w:{'name':g.character_profile(s,w)['name'],'atHome':g.character_at_castle(s,w),'agreed':w=='founder' or w in r['workAgreements'],'knownPrinciples':g.character_principles(s,w)} for w in g.household_members(s)}
    recipes={w:{k:recipe(s,{'definitionId':k,'workerId':w}) for k in CATALOG} for w in workers}
    return {'slots':SLOTS,'modes':list(MODES),'items':items,'loadouts':deepcopy(r['loadouts']),'mode':deepcopy(r['mode']),'catalogue':deepcopy(CATALOG),'enchantments':deepcopy(ENCHANTS),'workers':workers,'recipes':recipes,'recentCompleted':deepcopy(r['receipts'][-6:]),'jobs':[{**deepcopy(j),'working':working(s,w)} for w,j in r['jobs'].items()],'patterns':deepcopy(r['patterns']),'proofs':deepcopy(r['proofs']),'commission':{w:recipe(s,{'operation':'commission','workerId':w}) for w in workers},'commissionReady':deepcopy(r.get('commissionReady')),'starterGrants':r['starterGrants'][:],'signatures':signature_equipment.view(s),'memories':deepcopy(r['memories'][-30:]),'effects':{w:effects(s,w) for w in workers}}

def forecast(s):
    import game as g,bounty_contracts
    return [g.character_profile(s,w)['name']+' · '+j['name']+(': +'+str(min(j['phases']-j['done'],1+int(bounty_contracts.advanced_work(s,j))))+' equipment work.' if working(s,w) else ': paused; resume on the equipment work board.') for w,j in state(s)['jobs'].items()]

def quote_action(s,action):
    """Read-only server preview, with the revision rechecked by normal commit."""
    import game as g
    g.require(isinstance(action,dict),'Provide an equipment action.')
    g.require(isinstance(action.get('type'),str) and action['type'].startswith('gear-'),'Preview a supported equipment action.')
    action=deepcopy(action);copy=deepcopy(s)
    if action['type'] in ('gear-equip','gear-ready'):action['replaceConfirmed']=True
    before={w:deepcopy(loadout(s,w)) for w in state(s)['loadouts']};cost=s['sharedFunds'];materials=deepcopy(s['materialInventory'])
    quoted=deepcopy(s)
    try:prepare_host(quoted,action)
    except g.RuleError:pass
    q=recipe(quoted,action) if action['type']=='gear-start-job' else None
    blockers=preview(s,action)
    if not blockers:apply(copy,action)
    changes=[]
    for w,l in before.items():
        after=loadout(copy,w)
        if l!=after:
            old=set(l['slots'].values());new=set(after['slots'].values())
            changes.extend('Stow '+state(s)['items'][k]['name'] for k in sorted(old-new))
            changes.extend('Equip '+state(copy)['items'][k]['name'] for k in sorted(new-old))
    equipment_changes=[]
    def pictured(state_value,key):
        it=state(state_value)['items'][key]
        return {'id':key,'name':it['name'],'icon':item_art(state_value,it)}
    for who,old_loadout in before.items():
        after_loadout=loadout(copy,who)
        old=set(old_loadout['slots'].values());new=set(after_loadout['slots'].values())
        old_mode=state(s)['mode'].get(who,'household');new_mode=state(copy)['mode'].get(who,'household')
        if old!=new or old_mode!=new_mode:
            equipment_changes.append({'personId':who,'beforeMode':old_mode,'afterMode':new_mode,
                'removed':[pictured(s,key) for key in sorted(old-new)],
                'added':[pictured(copy,key) for key in sorted(new-old)]})
    assignments=[{'workerId':w,'name':g.character_profile(s,w)['name'],'before':g.character_assignment(s,w),'after':g.character_assignment(copy,w)} for w in g.household_members(s) if g.character_assignment(s,w)!=g.character_assignment(copy,w)]
    import field_patrols
    patrol_bonuses={w:{'before':field_patrols.equipment_bonuses(s,w),'after':field_patrols.equipment_bonuses(copy,w)} for w in before}
    return {'patrolBonuses':patrol_bonuses,'equipmentChanges':equipment_changes,'assignments':assignments,'action':action,'revision':s['revision'],'blockers':blockers,'quote':q,'cost':cost-copy['sharedFunds'],'materials':{k:n-copy['materialInventory'][k] for k,n in materials.items() if n!=copy['materialInventory'][k]},'changes':changes,'effectsBefore':{w:effects(s,w) for w in before},'effectsAfter':{w:effects(copy,w) for w in before}}

def legacy_armour_toggle(s,enabled):
    r=state(s)
    if enabled:
        it=next((i for i in r['items'].values() if stock_kind(i)=='warded-armour' and i['location']=='armoury' and i['ownerId'] in ('household','founder')),None)
        if it:
            it['ownerId']='founder';it['fitOwner']='founder'
            for mode in ('household','expedition'):
                put_in(s,'founder',it['id'],mode);loadout(s,'founder',mode)['active'][it['id']]=['legacy-ward']
    else:
        for mode in MODES:
            l=loadout(s,'founder',mode)
            for key in list(l['active']):l['active'][key]=[e for e in l['active'][key] if e!='legacy-ward']
    r['legacyWardImported']=True

def public_mount(definition_id):
    """Explicit host silhouettes for the admitted public catalogue; portable
    legacy foci retain a hand-carried mounting and never acquire extra bonuses."""
    key=definition_id.removeprefix('ss-eq-equipment-concept-')
    mapping={
      'hearth-spoke-staff':('field-staff',['hand2']), 'margin-lantern':('field-lantern',['hand2']),
      'root-window-crook':('field-staff',['hand2']), 'waxfield-notebook':('scholars-folio',['hand2']),
      'double-leaf-slate':('scholars-folio',['hand2']), 'sunline-ruler':('makers-gauge',['hand2']),
      'seam-compass':('makers-gauge',['hand2']), 'section-cut-calipers':('makers-gauge',['hand2']),
      'joint-depth-gauge':('makers-gauge',['hand2']), 'quiet-tap-hammer':('repair-hammer',['hand2']),
      'capillary-brush-handle':('engraving-tool',['hand2']), 'courteous-threshold-token':('plain-pendant',['necklace']),
      'quiet-chime-token':('plain-pendant',['necklace']), 'focus-docking-ring':('plain-ring',['ring']),
      'wet-page-recovery-folio':('scholars-folio',['hand2']), 'sample-scent-hood':('cloth-cap',['head']),
      'source-tag-brooch-case':('focus-clasp',['necklace']), 'personal-seal-blank':('ward-key',['hand2'])}
    return mapping.get(key,('field-kit',['hand2']))

LEGACY_CONFIG_ACTIONS={'prepare-working-tool','stow-working-tool','transfer-working-tool','configure-focus','public-prepare-item','public-stow','public-transfer'}
def legacy_guard(s,act):
    """Old controls share item reservations with the unified work board."""
    import game as g
    kind=act.get('type');key=act.get('itemId');owner=act.get('ownerId',act.get('characterId'))
    family='tool' if kind in {'prepare-working-tool','transfer-working-tool','upgrade-working-tool'} else 'focus' if kind in {'configure-focus','start-focus-inscription','upgrade-focus'} else 'public' if kind in {'public-prepare-item','public-transfer','public-stow','public-use-item','public-start'} and key else None
    if not family:return
    ident=owner if family=='focus' else key
    host=next((i for i in s.get('armoury',{}).get('items',{}).values() if i.get('legacy')=={'kind':family,'id':ident}),None)
    if host:g.require(host['location'] not in ('job','vault') and not any(host['id'] in (j.get('itemId'),j.get('signatureItem')) for j in state(s)['jobs'].values()),'Finish or cancel the reserved equipment work before changing this piece.')


def prepare_host(s,action):
    """Optional, explicitly reviewed stowing; the enclosing action is atomic."""
    import game as g
    if action.get('type')!='gear-start-job' or not action.get('stowBeforeWork'):return
    g.require(action.get('stowBeforeWork') is True,'Choose whether to stow before work.')
    g.require(action.get('operation') not in ('craft','commission'),'A new object has no owned host to stow.')
    it=owned(s,action.get('itemId'))
    g.require(it['ownerId']=='household' or it['ownerId'] in g.household_members(s),'Choose household or resident equipment.')
    if it['ownerId']!='household':home(s,it['ownerId'])
    g.require(not busy(s,it['id']),'Finish reserved work or retrieve this piece first.')
    remove_from_loadouts(s,it['id'])

import rare_accessories
rare_accessories.install()
