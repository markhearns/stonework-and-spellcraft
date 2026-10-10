"""Read-only, optional guidance through a fresh headquarters campaign."""
def view(s):
    import game as g
    made=bool(s['craftedArtifacts'].get('warming-lantern') or 'artifact:warming-lantern' in s['characterDevelopment']['founder']['advancementAwards'])
    learned=s['researchStatus']=='complete'
    returned=any(g.discoveries_for(s,k) for k in g.EXPEDITION_SITES) or bool(s['publicWorkshop'].get('fieldDiscoveries'))
    residents=len(g.household_members(s))>1
    wing=bool(s['livingWingCompletedOn'])
    milestones=[{'label':name,'complete':bool(done)} for name,done in [('Understand the hearth wards',learned),('Make a warming lantern',made),('Establish the living wing',wing),('Bring a discovery home',returned),('Welcome a willing resident',residents)]]
    def next_step(key,title,detail,view,room=None,action=None,**target):
        row={'id':key,'title':title,'detail':detail,'target':{'view':view,**target}}
        if room:row['target']['roomId']=room
        if action:row['action']=action
        return row
    def income(cost,goal,target):
        gain=g.copying_income(s);missing=max(0,cost-s['sharedFunds'])
        return {'id':'income','title':'Fund '+goal,'detail':f"You have {s['sharedFunds']} of {cost} crowns. Copying earns {gain} crowns per assigned phase; {(missing+gain-1)//gain} phase(s) cover this shortfall. Choosing copying pauses your other scholar work; its progress is kept.", 'target':target,'action':{'type':'assign-founder','assignment':'commissions'},'costTarget':cost,'copyingAssigned':s['founderAssignment']=='commissions'}
    if not g.character_at_castle(s,'founder'):
        public=bool(s['publicWorkshop'].get('fieldTrip'))
        n=next_step('journey','Bring your findings home','Choose a lead at the site, finish the work, then choose Return. Discoveries become usable on arrival home. Your home projects keep their progress.','publicWorkshop' if public else 'expeditions','command-room')
    elif not learned:
        n=next_step('hearth','Understand the hearth wards','20 crowns and three assigned work phases begin your practical study.','research','library')
        if s['researchStatus']=='not-started' and s['sharedFunds']<20:n=income(20,'your first study',n['target'])
    elif not made:n=next_step('lantern','Make your first lantern','Use one sun amber and one binding thread. Assign your scholar, then Advance to do the work.','workshop','workshop')
    elif not wing:
        n=None
        for key in ('kitchen','washroom','service-wards'):
            r=s['facilityProjects'][key];d=g.FACILITIES[key]
            if r['status']=='complete':continue
            n=next_step('facility:'+key,('Resume ' if r['status']=='in-progress' else 'Restore ')+d['name'],f"{d['costCrowns']} crowns once; {d['requiredWorkPhases']} assigned phases. "+d['benefit'],'ledger','washroom' if key=='washroom' else 'kitchen' if key=='kitchen' else 'living-quarters',{'type':'assign-facility' if r['status']=='in-progress' else 'start-facility','facilityId':key})
            if r['status']=='not-started' and s['sharedFunds']<d['costCrowns']:n=income(d['costCrowns'],d['name'].lower(),n['target'])
            break
        if n is None:
            if s['craftingProject']:
                p=s['craftingProject'];kettle=p['recipeId']=='hearth-kettle'
                n=next_step('kettle' if kettle else 'finish-crafting','Continue '+g.RECIPES[p['recipeId']]['name'],'Components are already committed. Finish or resume the funded crafting project before purchasing another set.','fullWorkshop','workshop',{'type':'assign-founder','assignment':'crafting'} if p['crafterId']=='founder' else None,recipeId=p['recipeId'])
            elif g.spare_artifact_count(s,'hearth-kettle'):
                n=next_step('install-kettle','Bring warm water to the washroom','Install your spare hearth kettle. This takes no phase.','ledger','washroom',{'type':'place-household-artifact','artifactId':'hearth-kettle','installed':True})
            elif not s['householdArtifactPlacements']['hearth-kettle']:
                # Default purchasable recipe; alternative suitable materials remain selectable.
                required=['sun-amber','porous-clay'];missing=[k for k in required if s['materialInventory'].get(k,0)<1]
                if missing:
                    cost=sum(g.MATERIALS[k]['price'] for k in missing)
                    n=next_step('kettle-materials','Gather kettle components','A straightforward recipe uses one sun amber and one porous clay. Explicit crafting may use reserved stock. Buy missing components or choose other suitable materials in crafting.','stores','warehouse',materialId=missing[0])
                    if s['sharedFunds']<cost:n=income(cost,'the missing kettle components',n['target'])
                else:n=next_step('kettle','Craft a hearth kettle','One sun amber and one porous clay make a warm-water vessel. Craft it, then install it in the washroom.','fullWorkshop','workshop',recipeId='hearth-kettle')
            else:n=next_step('wing','Your living wing is ready','All basic facilities are in place. The next Advance records the living-wing milestone and also resolves any assigned work. Review the phase before advancing.','phaseTasks')
    elif not returned:n=next_step('first-expedition','Take your first expedition','The old waterworks are open. Carry an available lantern to shorten survey work, investigate, and return with Water guidance. Travel and work each use Advance.','expeditions','command-room',siteId='old-waterworks')
    elif not residents:
        if s['localEncounters']['koharu']['status']=='introduced':
            n=next_step('membership','Offer a visit, then discuss staying','A visit uses an available bed; membership is a separate conversation. Nobody is recruited or assigned work automatically.','summoning','entry-hall',personId='koharu')
        else:n=next_step('introduction','Meet someone nearby','A local introduction takes one assigned phase. Koharu is available from the beginning; other introductions list their own requirements.','localEncounters','entry-hall')
    else:n=next_step('settled','Choose what grows next','Your basic home, first discovery and household are established. Explore useful headquarters rooms, pursue research, or agree work with a willing resident.','headquarters')
    return {'milestones':milestones,'next':n,'complete':all(r['complete'] for r in milestones),'optional':True}
