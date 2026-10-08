"""The First Hearth: optional, evidence-driven opening; ordinary rules own all work.

Only new fresh starts opt in automatically. Earlier saves gain no invented scenes.
Reads never initialize records, advance time, or reveal undiscovered castle lore.
"""
from copy import deepcopy


def initialize(s):
    s['soloLife'].setdefault('firstHearth', {'enabled': True, 'company': None, 'memories': {}})


def record(s):
    return s.get('soloLife', {}).get('firstHearth')


def lantern_made(s):
    return bool(s['craftedArtifacts'].get('warming-lantern') or
                'artifact:warming-lantern' in s['characterDevelopment']['founder']['advancementAwards'])


def field_discovery(s):
    import game as g
    return any(g.discoveries_for(s, k) for k in g.EXPEDITION_SITES) or bool(s['publicWorkshop'].get('fieldDiscoveries'))


def step(key, title, detail, view='castle', action=None, label=None, **target):
    return {'id': key, 'title': title, 'detail': detail, 'target': {'view': view, **target},
            'action': action, 'actionLabel': label}


def income(s, cost, title, target):
    import game as g
    import commissions
    gain = g.copying_income(s)
    missing = max(0, cost - s['sharedFunds'])
    import daily_plan
    plan=daily_plan.saved(s)
    active = s['founderAssignment'] == 'commissions' and plan and not plan['completedOn'] and plan['target']==cost
    copying=step('income', 'Fund '+title,
                f"{s['sharedFunds']} / {cost} crowns available. Copying earns {gain} crowns per phase; "
                f"{(missing+gain-1)//gain} copying phase(s) before other spending. Food purchases or allowances can extend this estimate. "
                'Copying stops when the treasury reaches the target. You still choose when to fund the project; other paid work keeps its progress.',
                action={'type': 'advance'} if active else {'type': 'plan-income', 'targetCrowns':cost, 'purpose':title},
                label='Advance · earn copying income' if active else 'Earn for this project', **target)
    job=commissions.saved(s)['job']
    if job and job['workerId']=='founder':
        result=funded(s,'income',job['name'],job['done'],job['phases'],
                      g.character_at_castle(s,'founder') and s['founderAssignment']=='external-commission',
                      {'type':'commission-resume'},'commissions')
        result['detail']+=' Payment on completion: '+job['reward']['text']+' Treasury target for '+title+': '+str(cost)+' crowns.'
        result['incomeOptions']=[dict(title='Switch to copying',detail=copying['detail'],action={'type':'plan-income','targetCrowns':cost,'purpose':title},actionLabel='Pause commission and copy toward this target')]
        return result
    offers=[]
    for key,d in commissions.CATALOG.items():
        if commissions.blockers(s,key,'founder','crowns'):continue
        reward=commissions.rewards(s,key)['crowns']['crowns']
        inputs=', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in d['inputs'].items()) or 'none'
        offers.append(dict(title=d['name'],detail=f"{d['phases']} assigned phases; payment: {reward} crowns. Materials used: {inputs}. Stops when delivered. Other paid work keeps its progress.",
                           action={'type':'commission-start','commissionId':key,'workerId':'founder','payment':'crowns'},
                           actionLabel='Accept commission · '+str(reward)+' crowns on completion',
                           net=reward-sum(g.MATERIALS[k]['price']*n for k,n in d['inputs'].items()),phases=d['phases']))
    offers.sort(key=lambda row:(-row['net']/row['phases'],row['title']))
    # Recommend a finite job only when its net pay beats copying for the same time
    # and the remaining target justifies at least that much work. Every new job
    # still requires the player's explicit acceptance.
    best=next((row for row in offers if row['net']>gain*row['phases'] and missing>gain*(row['phases']-1)),None)
    if best:
        result=step('income','Fund '+title,f"{s['sharedFunds']} / {cost} crowns available. "+best['detail'],
                    'commissions',best['action'],best['actionLabel'])
        result['incomeOptions']=[dict(title='Copy records instead',detail=copying['detail'],action=copying['action'],actionLabel=copying['actionLabel'])]
        result['incomeOptions'] += [{k:v for k,v in row.items() if k not in ('net','phases')} for row in offers if row is not best]
        return result
    copying['incomeOptions']=[{k:v for k,v in row.items() if k not in ('net','phases')} for row in offers]
    return copying


def funded(s, key, title, done, total, working, resume, view, **target):
    return step(key, title+(' is underway' if working else ' is waiting'),
                f'{done} / {total} work complete. Costs are already committed. '+
                ('Advance resolves this work and everyone else’s current assignments.' if working else
                 'Resume to continue; any other assignment is paused with its progress kept.'), view,
                {'type': 'advance'} if working else resume,
                'Advance · continue work' if working else 'Resume funded work', **target)


def recipe_step(s, recipe_id):
    """Offer available compatible components, not an unverified default recipe."""
    import game as g
    from itertools import product
    recipe = g.RECIPES[recipe_id]
    p = s['craftingProject']
    if p:
        who = p['crafterId']
        return funded(s, 'craft', g.RECIPES[p['recipeId']]['name'], p['completedWorkPhases'],
                      g.RECIPES[p['recipeId']]['requiredWorkPhases'],
                      g.character_at_castle(s, who) and g.character_assignment(s, who) == 'crafting',
                      {'type': 'assign-character', 'characterId': who, 'assignment': 'crafting'},
                      'fullWorkshop', recipeId=p['recipeId'], roomId='workshop')
    choices = [[k for k, d in g.MATERIALS.items() if prop in d['properties']] for prop in recipe['requiredProperties']]
    options = list(product(*choices))
    # Explicit crafting may use reserved stock, as the ordinary crafting screen does.
    def missing(combo):
        return {k: max(0, combo.count(k)-s['materialInventory'].get(k, 0)) for k in set(combo)}
    options.sort(key=lambda c: (sum(g.MATERIALS[k]['price']*n for k,n in missing(c).items()),
                                sum(g.MATERIALS[k]['price'] for k in c), c))
    combo = options[0]
    needs = {k:n for k,n in missing(combo).items() if n}
    target = {'view': 'fullWorkshop', 'recipeId': recipe_id, 'roomId': 'workshop'}
    if needs:
        cost = sum(g.MATERIALS[k]['price']*n for k,n in needs.items())
        key = next(k for k in combo if k in needs)
        if s['sharedFunds'] < cost:
            return income(s, cost, 'the missing components', {'view': 'stores', 'materialId': key, 'roomId': 'warehouse'})
        return step('components', 'Gather components for '+recipe['name'].lower(),
                    'Missing: '+', '.join(str(n)+' '+g.MATERIALS[k]['name'] for k,n in needs.items())+
                    f'. Buying one {g.MATERIALS[key]["name"].lower()} costs {g.MATERIALS[key]["price"]} crowns. '+
                    'You may instead choose other suitable materials at the workbench.',
                    'stores', {'type': 'buy-material', 'materialId': key},
                    'Buy one · '+str(g.MATERIALS[key]['price'])+' crowns', materialId=key, roomId='warehouse')
    names = ', '.join(g.MATERIALS[k]['name'].lower() for k in combo)
    return step(recipe_id, 'Make '+recipe['name'].lower(),
                f'Commit {names}; {recipe["requiredWorkPhases"]} assigned work phases. '+
                'This explicitly uses the listed stock, including protected reserves. Choosing work pauses your previous assignment.',
                action={'type': 'start-crafting', 'recipeId': recipe_id, 'materials': list(combo), 'crafterId': 'founder'},
                label='Commit components & craft', **target)


def repairs_step(s):
    import game as g
    for key,d in g.FACILITIES.items():
        p = s['facilityProjects'][key]
        if p['status'] == 'complete':
            continue
        target = {'view': 'ledger', 'roomId': 'kitchen' if key=='kitchen' else 'washroom' if key=='washroom' else 'living-quarters'}
        if p['status'] == 'in-progress':
            return funded(s, 'facility:'+key, d['name'], p['completedWorkPhases'], d['requiredWorkPhases'],
                          s['founderAssignment']=='facilities' and s['activeFacilityId']==key,
                          {'type': 'assign-facility', 'facilityId': key}, **target)
        if s['sharedFunds'] < d['costCrowns']:
            return income(s, d['costCrowns'], d['name'].lower(), target)
        return step('facility:'+key, 'Restore '+d['name'].lower(),
                    f'{d["costCrowns"]} crowns once; {d["requiredWorkPhases"]} assigned phases. '+d['benefit']+
                    ' Your scholar’s previous work is paused, with its progress kept.',
                    action={'type': 'start-facility', 'facilityId': key},
                    label=f'Fund & assign · {d["costCrowns"]} crowns', **target)
    if not s['householdArtifactPlacements']['hearth-kettle']:
        if g.spare_artifact_count(s, 'hearth-kettle'):
            return step('install-kettle', 'Warm water, at last',
                        'Fit your spare hearth kettle in the washroom. Installation costs no time or crowns.',
                        'ledger', {'type': 'place-household-artifact', 'artifactId': 'hearth-kettle', 'installed': True},
                        'Install the kettle · no time', roomId='washroom')
        if s['craftedArtifacts'].get('hearth-kettle'):
            return step('recover-kettle', 'Your kettle is already committed',
                        'Retrieve or release the existing kettle before installing it, or make another at the workbench.',
                        'fullWorkshop', recipeId='hearth-kettle')
        return recipe_step(s, 'hearth-kettle')
    return step('wing', 'A working home',
                'The living-wing requirements are met. The next Advance records the milestone and resolves current assignments.',
                'phaseTasks', {'type': 'advance'}, 'Advance · record the milestone')


def scene(key, title, opening, choices, person=None):
    return {'id': key, 'title': title, 'opening': opening, 'personId': person,
            'choices': [{'id': k, 'label': label, 'response': text} for k,label,text in choices]}


def next_beat(s):
    import game as g
    import local_encounters
    r = record(s); memories = r['memories']
    if not g.character_at_castle(s, 'founder'):
        public = bool(s['publicWorkshop'].get('fieldTrip'))
        return step('journey', 'Bring your findings home',
                    'Finish a chosen lead, then Return and Advance to arrive home. Supplies and discoveries count only after your return.',
                    'publicWorkshop' if public else 'expeditions'), None
    if s['researchStatus'] != 'complete':
        if s['researchStatus']=='in-progress':
            return funded(s, 'hearth', 'Hearth wards', s['researchCompletedPhases'], s['researchRequiredPhases'],
                          s['founderAssignment']=='research', {'type': 'assign-founder', 'assignment': 'research'},
                          'research', roomId='library'), None
        if s['sharedFunds']<20:
            return income(s, 20, 'your first study', {'view':'research','roomId':'library'}), None
        return step('hearth', 'Read the old inscriptions',
                    'A warm room is a useful first ambition. Study the hearth wards: 20 crowns and three assigned work phases.',
                    'research', {'type':'start-research'}, 'Begin research · 20 crowns', roomId='library'), None
    if 'intention' not in memories:
        return None, scene('intention', 'An answer you can hold',
            'You can finally follow the hearth inscription without copying it. On the next page, you draw a small lantern. '
            'Its light would be useful at your desk—and on the paths beyond the gate.', [
                ('comfort','Begin with a little comfort','You mark a place for the lantern beside your chair. A home can begin with something small enough to carry.'),
                ('curiosity','Make something that can travel','You add a handle to the sketch. A useful answer ought to survive leaving the library.')])
    if not lantern_made(s):
        return recipe_step(s, 'warming-lantern'), None
    if r['company'] is None:
        return None, scene('company', 'Someone who knows the woodwork',
            'There is a joinery nearby. You could compare repair notes with its craftswoman before tackling the wing, '
            'or keep this first stretch of work to yourself. Either way, the unused rooms can wait.', [
                ('meet','Arrange an introduction','You leave room on the repair list for another person’s observations. The introduction is a separate, one-phase appointment.'),
                ('solo','Find my own rhythm first','You keep the first page to yourself. The joinery will still be there when you want company.')])
    if r['company']=='meet' and 'repair-notes' not in memories:
        introduced = s['localEncounters']['maren']['status']=='introduced'
        if not introduced:
            if s['localVisit']:
                p=s['localVisit']; name=local_encounters.PEOPLE[p['encounterId']]['name']
                return funded(s, 'introduction', 'Introduction to '+name, p['completedWorkPhases'], p['requiredWorkPhases'],
                              s['founderAssignment']=='local-visit', {'type':'resume-local-visit'}, 'localEncounters'), None
            reasons=local_encounters.start_blockers(s,'maren')
            n=step('introduction', 'Compare repair notes with Maren',
                   'One assigned phase, no crowns. Your previous assignment pauses. A meeting does not require a visit or membership.',
                   'localEncounters', None if reasons else {'type':'start-local-visit','encounterId':'maren'},
                   'Arrange the introduction', personId='maren')
            n['blockers']=reasons
            return n,None
        # Do not stage an in-person conversation while a previously met resident is away.
        if not g.character_at_castle(s,'maren') and s['additionalResidents'].get('maren',{}).get('status') in ('resident','visiting'):
            return step('wait-company','Repair notes can wait','Return together to compare notes, or continue this chapter on your own.','summoning',personId='maren'),None
        return None, scene('repair-notes', 'The respectable end of the repair list',
            'In the joinery correspondence, Maren considers your sketch. “A kitchen, a washroom, sound service wards. Disappointingly sensible.” '
            'She taps the kettle drawing. “Good clay, though. Don’t spend your last crowns on a pretty vessel that leaks.” '
            'The abandoned quarry shelter offers both reusable packing and shutter joints worth studying.', [
                ('practical','Ask what she would fix first','“The place you wash your hands,” she says. “Then the place you feed yourself. Hard to admire your work when you’re hungry and covered in it.”'),
                ('playful','Promise one magnificently unnecessary flourish','“One?” Maren’s smile widens. “I shall expect something thoroughly impractical once the pipes work.”'),
                ('independent','Thank her, and keep the work your own','“Of course. Advice isn’t a claim on the finished room.” She returns the sketch with a small, approving nod.')], 'maren')
    if not field_discovery(s):
        return step('fieldwork', 'Something worth bringing home',
                    'The quarry shelter has two useful approaches: salvage returns 2 porous clay, 3 binding thread and 8 crowns '
                    '(split by your departure wealth plan); surveying opens Weather sealing research. '
                    'Clay can become your washroom kettle. With a lantern, either route takes one outbound, one work and one return phase. '
                    'Other returned discoveries also count.', 'expeditions', siteId='quarry-shelter', roomId='command-room'), None
    if 'return' not in memories:
        salvage='salvage' in g.discoveries_for(s,'quarry-shelter')
        return None, scene('return','The shape of the journey',
            ('The quarry’s clay packing and sound cord now sit on your workbench. Things somebody once set aside can become part of a working home.' if salvage else
             'You spread the returned findings on your desk. The castle now has a connection to somewhere beyond its walls, and your next repair has a wider context.'), [
                ('use','Connect the findings to the repairs','You put the kettle sketch beside your inventory. Keep the warm-water vessel, the room and the materials on the same page; none is useful alone.'),
                ('notes','Keep a page for the next question','You separate the repair list from the unanswered questions. First a comfortable wing; then a little more time to follow the trail.')])
    if not s['livingWingCompletedOn']:
        return repairs_step(s), None
    if 'evening' not in memories:
        if s['currentDayPhase']!='evening':
            return step('evening-waits','An evening to enjoy the wing',
                        'The repairs are complete. The quiet evening invitation will be ready when evening arrives. '+
                        'Continue your chosen work, or rest; Advance resolves everyone’s current plans. The invitation never expires.',
                        'phaseTasks',{'type':'advance'},'Advance toward evening'),None
        callback=''
        repair=memories.get('repair-notes',{}).get('choiceId')
        if repair=='practical':callback=' You wash the last dust from your hands and remember Maren’s priorities with a smile.'
        elif repair=='playful':callback=' Remembering Maren’s challenge, you sketch an absurdly elaborate drawer pull in the margin. The flourish can remain a sketch for now.'
        elif repair=='independent':callback=' Maren’s advice helped, but the decisions—and the awkward joins—are recognizably yours.'
        return None, scene('evening', 'An evening without a repair list',
            'The range draws properly. The basin runs warm. Along the gallery, the service wards hold a modest, steady light. '
            'For once there is nothing on this page that must be done before you can sit down. '
            'A small mark beneath the hearth lintel can wait until you choose to investigate.'+callback, [
                ('rest','Leave the notebook closed','You put the repair list in a drawer. For this little while, the wing is simply somewhere to be.'),
                ('future','Leave a place for future company','You leave a chair beside the hearth. It is an invitation you may choose to make, not an empty place anyone owes you a duty to fill.')])
    if 'hearth-margin' not in s['castleMystery']['discoveries']:
        p=s['castleMystery']['project']
        if p:
            import castle_mystery
            return funded(s,'mystery',castle_mystery.LEADS[p['leadId']]['name'],p['completedWorkPhases'],p['requiredWorkPhases'],
                          s['founderAssignment']=='mystery',{'type':'resume-mystery'},'mystery'),None
        return step('mystery','A mark beneath the hearth lintel',
                    'Compare the maker’s mark with the restored wards. Two assigned phases; no crowns or materials. '
                    'This records evidence from your campaign’s existing history. It does not yet explain the castle.',
                    'mystery',{'type':'start-mystery','leadId':'hearth-margin'},'Begin the investigation · 2 phases'),None
    if 'conclusion' not in memories:
        opening='Your record of the hearth mark lies beside the first lantern sketch. You have a working home, a journey behind you and a question worth following.'
        opening+=(' The light you first imagined beside your chair has now travelled beyond the gate.' if memories['intention']['choiceId']=='comfort' else ' The lantern you designed to travel has found a place beside your chair as well.')
        if r['company']=='meet' and 'repair-notes' in memories:
            opening+=' You keep Maren’s repair advice in the margin; whether she ever lives here is a separate choice.'
        return None,scene('conclusion','The first hearth',opening,[
            ('history','Follow the house’s history','You turn to a clean page and write down what the hearth evidence actually supports. There is more to learn before the house’s story can be told.'),
            ('household','Make room for a household','The next page is a practical one: a suitable room, an invitation, work that can be shared. People will bring questions of their own.'),
            ('craft','Follow the next useful working','You return to your field notes. The next improvement can begin as this one did: a question, a patient journey and something made by hand.')])
    choice=memories['conclusion']['choiceId']
    view={'history':'mystery','household':'peopleHub','craft':'castleChapter'}[choice]
    return step('complete','A place to return to','Your first chapter is remembered. The House Takes Shape brings your interests into three useful rooms: an archive, a garden and a commission bench. Follow your chosen direction here, or open Chapter 2 from Home. Your earlier work counts.',view),None


def view(s):
    if s.get('startType')!='fresh':
        return None
    r=record(s)
    if not r:
        return {'enrolled':False,'enabled':False,'title':'The First Hearth'}
    n,sc=next_beat(s)
    # Future responses stay private until the choice has actually been made.
    if sc:
        sc=deepcopy(sc)
        for c in sc['choices']:c.pop('response')
    memories=[deepcopy(m) for m in r['memories'].values()]
    done=[s['researchStatus']=='complete',lantern_made(s),r['company']=='solo' or 'repair-notes' in r['memories'],
          field_discovery(s),bool(s['livingWingCompletedOn']),'hearth-margin' in s['castleMystery']['discoveries']]
    milestones=[{'label':label,'complete':bool(d)} for label,d in zip(
        ['Understand the hearth','Make a useful light','Choose company or quiet','Bring something home','Make the wing comfortable','Record the first evidence'],done)]
    import game as g
    if n and n.get('action'):
        before={who:g.character_assignment(s,who) for who in g.household_members(s)}
        staged=deepcopy(s)
        try:
            g.apply_action(staged,n['action'])
            n['assignmentChanges']=[{'personId':who,'name':g.character_profile(s,who)['name'],'before':assignment,'after':g.character_assignment(staged,who)} for who,assignment in before.items() if assignment!=g.character_assignment(staged,who)] if n['action']['type']!='advance' else []
        except g.RuleError as error:
            n['blockers']=[str(error)]
    people=[who for who in g.household_members(s) if who!='founder']
    return {'enrolled':True,'enabled':r['enabled'],'title':'The First Hearth','complete':'conclusion' in r['memories'],
            'company':r['company'],'next':n,'scene':sc,'milestones':milestones,'memories':memories,
            'canChangeCompany':'repair-notes' not in r['memories'] and r['company']=='meet',
            'people':people, 'canShareEvening':bool(s['livingWingCompletedOn']) and bool(people) and not s['soloLife']['housewarming'],
            'nextBlockers':n.get('blockers',[]) if n else []}


def apply(s,a):
    kind=a.get('type')
    if kind not in ('first-hearth-guidance','first-hearth-choice','first-hearth-solo'):
        return False
    import game as g
    g.require(s.get('startType')=='fresh','This chapter belongs to fresh solo campaigns.')
    if kind=='first-hearth-guidance':
        g.require(type(a.get('enabled')) is bool,'Choose whether to show the chapter guidance.')
        initialize(s);record(s)['enabled']=a['enabled']
        return True
    r=record(s)
    g.require(r is not None,'Choose to follow The First Hearth first.')
    if kind=='first-hearth-solo':
        g.require(r['company']=='meet' and 'repair-notes' not in r['memories'],'That introduction choice is already resolved.')
        r['company']='solo'
        g.add_journal(s,'The First Hearth: you chose to continue on your own. Existing appointments and acquaintances are kept.')
        return True
    _,sc=next_beat(s)
    g.require(sc is not None and sc['id']==a.get('sceneId'),'Choose the current chapter moment; earlier choices are already remembered.')
    c=next((c for c in sc['choices'] if c['id']==a.get('choiceId')),None)
    g.require(c is not None,'Choose one of the offered responses.')
    m={'id':sc['id'],'title':sc['title'],'opening':sc['opening'],'choiceId':c['id'],
       'choiceLabel':c['label'],'text':c['response'],'personId':sc['personId'],
       'participants':['founder']+([sc['personId']] if sc['personId'] else []),
       'dayNumber':s['dayNumber'],'phase':s['currentDayPhase']}
    r['memories'][sc['id']]=m
    if sc['id']=='company':r['company']=c['id']
    g.add_journal(s,sc['title']+': '+c['response'])
    return True
