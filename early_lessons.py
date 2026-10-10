"""Small practical lessons before the first journey, using ordinary spell and gear rules."""
def next_step(s):
    import game as g, first_hearth as f, armoury as a
    r=f.record(s)
    if not r or 'conclusion' in r['memories'] or f.field_discovery(s):return None
    if not r.get('equipmentReviewed'):
        return f.step('field-kit','Check your ordinary travelling kit','Review your staff or weapon, shirt, trousers and boots, then wear your saved expedition set. Existing equipment and fitted inscriptions are kept. No crowns or time.','armoury',{'type':'opening-equipment'},'Review and wear field equipment')
    spell=next((x for x in s['spellbook'] if x['ownerId']=='founder' and x['formId']=='warm-twist'),None)
    if not spell:
        return f.step('first-spell','Turn hearth knowledge into a spell','Draft Warm-twist binding. Testing uses 4 crowns, one sun amber and one binding thread over two assigned phases. A later casting turns one silver ivy into two binding thread.','spells',{'type':'inscribe-spell','characterId':'founder','formId':'warm-twist','materials':['sun-amber','binding-thread']},'Draft Warm-twist binding')
    job=s['spellWork']['founder']
    if job:
        return f.funded(s,'first-spell','Your first practical spell',0 if job['kind']=='cast' else spell.get('completedWorkPhases',0),1 if job['kind']=='cast' else 2,s['founderAssignment']=='spellwork',{'type':'assign-founder','assignment':'spellwork'},'spells')
    if spell.get('castCount',0):return None
    if spell['status']=='draft':
        for key in spell['materials']:
            n=spell['materials'].count(key)
            if s['materialInventory'][key]<n:
                cost=g.MATERIALS[key]['price']
                if s['sharedFunds']<cost:return f.income(s,cost,'the spell components',{'view':'spells'})
                return f.step('first-spell','Gather the testing component','Buy one '+g.MATERIALS[key]['name']+' for '+str(cost)+' crowns.','stores',{'type':'buy-material','materialId':key},'Buy one testing component')
        if s['sharedFunds']<4:return f.income(s,4,'your first spell test',{'view':'spells'})
        return f.step('first-spell','Test Warm-twist binding','Commit the listed components and 4 crowns. Two assigned phases establish the learned spell; testing produces no cord.','spells',{'type':'test-spell','spellId':spell['id']},'Fund the two-phase test')
    if spell['id'] not in s['preparedSpells']['founder']:
        current=s['preparedSpells']['founder']
        if len(current)+len(s['publicWorkshop']['preparedSpells'].get('founder',[]))>=g.spell_preparation_capacity(s,'founder'):
            return f.step('first-spell','Choose a preparation slot','Prepare Warm-twist binding in Spells. Review which currently prepared spell to put aside; learned knowledge is kept.','spells')
        return f.step('first-spell','Prepare your learned spell','Preparing is separate from learning. Add Warm-twist binding to a free preparation slot; no time or crowns.','spells',{'type':'prepare-spells','characterId':'founder','spellIds':current+[spell['id']]},'Prepare Warm-twist binding')
    if not s['materialInventory']['silver-ivy']:
        cost=g.MATERIALS['silver-ivy']['price']
        if s['sharedFunds']<cost:return f.income(s,cost,'silver ivy for casting',{'view':'spells'})
        return f.step('first-spell','Get the casting ingredient','One silver ivy becomes two binding thread after a single assigned casting phase.','stores',{'type':'buy-material','materialId':'silver-ivy'},'Buy one silver ivy · '+str(cost)+' crowns')
    return f.step('first-spell','Make useful cord with magic','Consume one silver ivy and spend one assigned phase to produce two binding thread. This is an actual casting, and the cord can be used in your repairs.','spells',{'type':'cast-spell','spellId':spell['id']},'Schedule the first casting')

def apply(s,a):
    if a.get('type')!='opening-equipment':return False
    import game as g,first_hearth as f,armoury
    r=f.record(s)
    g.require(r and not r.get('equipmentReviewed') and g.character_at_castle(s,'founder'),'Review the opening kit once while at home.')
    armoury.review_starters(s)
    armoury.apply(s,{'type':'gear-party-loadout','participants':['founder'],'mode':'expedition'})
    r['equipmentReviewed']=True
    return True
