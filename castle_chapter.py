"""An optional solo chapter, using the existing travel, research and work rules."""
from copy import deepcopy

SITES = {
    'quarry-shelter': {'id':'quarry-shelter','name':'Quarry shelter',
        'description':'Above the cart track stands a stonecutters’ shelter. Rain has reached the floor, but papers beneath its old shutters remain dry. Ordinary repairs may have something to teach a working castle.',
        'approaches':{
            'survey':{'name':'Trace the shutter joints','description':'Record how overlapping seams turn rain away without sealing the room shut. Two work phases, or one with a lantern or prepared fieldwork.','reward':'Bring home observations for Weather sealing research; no principle is learned until the study is completed.'},
            'salvage':{'name':'Sort the repair chest','description':'Separate sound cord and clay packing from the ruined scraps. One work phase.','reward':'Recover 3 binding thread, 2 porous clay and 8 crowns, once.'}}},
    'ridge-cistern': {'id':'ridge-cistern','name':'Ridge cistern',
        'description':'A maintenance sketch from the waterworks leads uphill to a shallow settling tank. Water still finds its patient way through layers of gravel and rooted channels.',
        'approaches':{
            'survey':{'name':'Follow the settling channels','description':'Measure where the cloudy water becomes clear and where the overflow returns to the brook. Two work phases, or one with a lantern or prepared fieldwork.','reward':'Bring home observations for Settling flow research; the study unlocks a useful conservatory filter.'},
            'salvage':{'name':'Recover the spare fittings','description':'Lift intact clay fittings from a dry maintenance shelf. Leave the working channels undisturbed. One work phase.','reward':'Recover 3 porous clay, 2 silver ivy and 10 crowns, once.'}}},
}
RESEARCH = {
    'weather-sealing':{'name':'Weather sealing','costCrowns':10,'requiredWorkPhases':2,'requiredPrinciples':['steady-hearth-wards'],'principle':'weather-sealing',
        'requiredDiscovery':{'siteId':'quarry-shelter','approach':'survey'},'description':'Turn the quarry shelter’s practical shutter joints into a modest paper-drying working.','benefit':'Craft a weather screen: +1 crown per assigned copying phase when installed in the library. Extra copies do not stack.'},
    'settling-flow':{'name':'Settling flow','costCrowns':12,'requiredWorkPhases':3,'requiredPrinciples':['water-guidance'],'principle':'settling-flow',
        'requiredDiscovery':{'siteId':'ridge-cistern','approach':'survey'},'description':'Study the returned cistern measurements and adapt their slow channels for the conservatory.','benefit':'Craft a cistern filter: +1 silver ivy per staffed ivy harvest when installed. No bonus to automatic tending or surplus sales.'},
}
ARTIFACTS = {
    'weather-screen':{'name':'Weather screen','roomId':'library','benefit':RESEARCH['weather-sealing']['benefit']},
    'cistern-filter':{'name':'Cistern filter','roomId':'conservatory','benefit':RESEARCH['settling-flow']['benefit']},
}
SCENES = {
    'shutter-notes':{'title':'The practical margin','roomId':'library','text':'The shutter drawing fits on half a page. In the margin you find yourself listing all the small things a home should keep safe: dry paper, warm hands, a place to return to.',
        'choices':{'care':('Begin with care','You underline the smallest repairs. A sound home can begin with things that nobody needs to notice.'),'curiosity':('Leave room for questions','You leave a blank margin beside the measurements. Being useful need not mean being finished.')}},
    'first-rain':{'title':'A desk through the rain','roomId':'library','text':'Rain taps the window. The new screen keeps your papers dry without hiding the sound. For once the weather can be company instead of another repair.',
        'choices':{'work':('Write one unhurried page','You finish a page for yourself, with no client waiting for it. The room feels a little more like yours.'),'listen':('Listen for a while','You put the pen down and listen to the rain find its way over the stone. Nothing needs to be earned from this moment.')}},
    'clear-water':{'title':'The water takes its time','roomId':'conservatory','text':'A thin line of clear water reaches the planting bench. The filter is plain clay and careful channels; its usefulness is easy to overlook until you watch it work.',
        'choices':{'observe':('Keep a gardener’s note','You note the clean flow and leave space for what the next gardener discovers.'),'rest':('Sit among the leaves','You sit where the leaves catch the light. A working room can make space for resting, too.')}},
    'shared-desk':{'title':'Room at the dry desk','roomId':'library','shared':True,'text':'With the screen fitted, there is a dry corner for another notebook. You invite a resident to decide how the shared desk should be used.',
        'choices':{'space':('Leave space for separate work','Together you clear a second place. Sharing a room need not mean doing the same thing.'),'exchange':('Compare practical questions','You compare two questions: whether the screen can be cleaned without removing it, and where to leave wet coats so they do not drip on the books. You note both beside the drawing.')}},
    'garden-round':{'title':'A round of the growing benches','roomId':'conservatory','shared':True,'text':'The fitted filter gives you a reason to look around the conservatory together. There is room to discuss its care without turning the conversation into an assignment.',
        'choices':{'routine':('Discuss a comfortable routine','You suggest keeping the watering can beside the filter and leaving the bench by the door clear for sitting. Your companion points out that the can would block the handle. You move the proposed spot to the other side. Work assignments stay as they are.'),'growth':('Notice the new growth','You follow the new leaves along the bench. Neither of you needs to hurry the quiet.')}},
    'chapel-pause':{'title':'A place to be quiet','roomId':'chapel','shared':True,'text':'The restored chapel offers a bench out of the traffic of the castle. You invite a resident to share a pause; no belief or observance is presumed.',
        'choices':{'silence':('Share the quiet','For a little while, the room asks nothing of either of you.'),'thanks':('Name something worth keeping','You name the dry bench you are sitting on. Your companion chooses the door that closes without a draught. You sit a little longer, listening to the wind outside instead of feeling it at your backs.')}},
}

def register(g):
    g['EXPEDITION_SITES'].update(SITES)
    g['RESEARCH_CATALOG'].update(RESEARCH)
    g['UTILITY_ARTIFACTS'].update(ARTIFACTS)
    for key,d in RESEARCH.items():
        g['PRINCIPLE_NAMES'][key]=d['name']
        g['PRINCIPLE_GUIDE'][key]={'source':'Complete '+d['name']+' research after returning its survey.','view':'research','use':d['benefit']}
    for key,principle,props in [('weather-screen','weather-sealing',['vessel','binding']),('cistern-filter','settling-flow',['vessel','botanical'])]:
        g['RECIPES'][key]={'name':ARTIFACTS[key]['name'],'requiredPrinciple':principle,'requiredProperties':props,'requiredWorkPhases':2,'description':ARTIFACTS[key]['benefit']}

def initialize(s):
    chapter=s.setdefault('castleChapter',{})
    chapter.setdefault('memories',{})
    discoveries=chapter.setdefault('discoveries',{})
    for key in SITES:discoveries.setdefault(key,[])
    for key in RESEARCH:s['researchProjects'].setdefault(key,{'status':'not-started','completedWorkPhases':0,'contributors':[]})
    for key in ARTIFACTS:
        s['utilityArtifactPlacements'].setdefault(key,False)
        s['craftedArtifacts'].setdefault(key,0)

def available(s,key):
    return s['researchStatus']=='complete' if key=='quarry-shelter' else 'survey' in s.get('waterworksDiscoveries',[])

def hint(key):
    return 'Complete your first hearth-ward study to follow the quarry track.' if key=='quarry-shelter' else 'Survey the old waterworks and bring its maintenance sketch home.'

def return_rewards(s,key,approach):
    import game as g
    if approach=='survey':return ['Observations brought home. Study '+RESEARCH['weather-sealing' if key=='quarry-shelter' else 'settling-flow']['name']+' at the research desk to understand their practical use.']
    materials,crowns=({'binding-thread':3,'porous-clay':2},8) if key=='quarry-shelter' else ({'porous-clay':3,'silver-ivy':2},10)
    for item,n in materials.items():s['materialInventory'][item]+=n
    return [g.distribute_expedition_wealth(s,crowns),'Recovered '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in materials.items())+'.']

def unlocked(s,key):
    import headquarters as h
    return {'shutter-notes':'survey' in s.get('castleChapter',{}).get('discoveries',{}).get('quarry-shelter',[]),
        'first-rain':s['utilityArtifactPlacements'].get('weather-screen',False),
        'clear-water':s['utilityArtifactPlacements'].get('cistern-filter',False),
        'shared-desk':s['utilityArtifactPlacements'].get('weather-screen',False),
        'garden-round':s['utilityArtifactPlacements'].get('cistern-filter',False),
        'chapel-pause':h.ready(s,'chapel')}[key]

def view(s):
    import game as g
    steps=[]
    for site,research,artifact in [('quarry-shelter','weather-sealing','weather-screen'),('ridge-cistern','settling-flow','cistern-filter')]:
        steps.extend([
            {'id':site,'label':'Survey '+SITES[site]['name']+' and return','complete':'survey' in g.discoveries_for(s,site),'target':{'view':'expeditions','siteId':site,'roomId':'command-room'},'detail':hint(site)},
            {'id':research,'label':'Research '+RESEARCH[research]['name'],'complete':s['researchProjects'][research]['status']=='complete','target':{'view':'research','roomId':'library'},'detail':str(RESEARCH[research]['costCrowns'])+' crowns · '+str(RESEARCH[research]['requiredWorkPhases'])+' assigned work phases. Requires the returned survey and personal prerequisite knowledge.'},
            {'id':artifact,'label':'Craft and install a '+ARTIFACTS[artifact]['name'].lower(),'complete':bool(s['utilityArtifactPlacements'].get(artifact)),'target':{'view':'fullWorkshop','recipeId':artifact,'roomId':'workshop'},'detail':ARTIFACTS[artifact]['benefit']},
        ])
    people=[{'id':who,'name':g.character_profile(s,who)['name']} for who in g.household_members(s) if who!='founder' and g.character_at_castle(s,who)]
    memories=s.get('castleChapter',{}).get('memories',{})
    scenes=[]
    for key,d in SCENES.items():
        if not unlocked(s,key) and key not in memories:continue
        scenes.append({'id':key,**deepcopy(d),'choices':{k:v[0] for k,v in d['choices'].items()},'memory':deepcopy(memories.get(key)),
            'available':g.character_at_castle(s,'founder') and (not d.get('shared') or bool(people))})
    return {'title':'Weatherproofing the castle','steps':steps,'complete':all(r['complete'] for r in steps),'scenes':scenes,'people':people}

def apply(s,a):
    if a.get('type')!='chapter-reflection':return False
    import game as g
    key=a.get('sceneId');choice=a.get('choice');who=a.get('personId')
    g.require(isinstance(key,str) and key in SCENES,'Choose an available castle reflection.')
    d=SCENES[key]
    g.require(isinstance(choice,str) and choice in d['choices'],'Choose one of this reflection’s responses.')
    g.require(unlocked(s,key),'Complete the associated discovery or room improvement first.')
    g.require(key not in s['castleChapter']['memories'],'This reflection is already remembered.')
    g.require(g.character_at_castle(s,'founder'),'Return home before taking a quiet moment.')
    if d.get('shared'):
        g.require(isinstance(who,str) and who!='founder' and who in g.household_members(s) and g.character_at_castle(s,who),'Choose a resident who is home and available.')
    else:g.require(who is None,'This is a private reflection.')
    text=d['choices'][choice][1]
    if d.get('shared'):text='With '+g.character_profile(s,who)['name']+': '+text
    s['castleChapter']['memories'][key]={'choice':choice,'personId':who,'text':text,'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
    g.add_journal(s,d['title']+': '+text+' No time or resources spent.')
    return True
