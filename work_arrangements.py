"""Named assignment arrangements, previewed and committed atomically."""
from copy import deepcopy


def initialize(s):s.setdefault('workArrangements',{})


def preview(s,plan):
    import game as g
    staged=deepcopy(s);changes=[];reasons=[]
    members=g.household_members(s)
    if not g.character_at_castle(s,'founder'):reasons.append('Your scholar must return home before changing household work.')
    for who,assignment in plan.items():
        name=g.character_profile(s,who)['name'] if who in members else who.capitalize()
        if who not in members:reasons.append(name+' is no longer a resident.');continue
        if not g.character_at_castle(s,who):reasons.append(name+' is away; their assignment is not changed.');continue
        current=g.character_assignment(s,who)
        # Unchanged assignments are not revalidated: a completed task may be awaiting reassignment.
        if current==assignment:continue
        try:g.apply_action(staged,{'type':'assign-character','characterId':who,'assignment':assignment})
        except g.RuleError as error:reasons.append(name+': '+str(error))
        else:changes.append({'personId':who,'name':name,'before':current,'after':assignment})
    return staged,changes,reasons


def view(s):
    import game as g
    plans=[]
    for name,plan in s.get('workArrangements',{}).items():
        _,changes,reasons=preview(s,plan)
        plans.append({'name':name,'members':list(plan),'assignments':deepcopy(plan),'changes':changes,'blockers':reasons,'canApply':not reasons and bool(changes)})
    return {'plans':plans,'current':[{'personId':who,'name':g.character_profile(s,who)['name'],'assignment':g.character_assignment(s,who),'atHome':g.character_at_castle(s,who)} for who in g.household_members(s)],'limit':8}


def apply(s,a):
    if a.get('type') not in ('save-work-arrangement','apply-work-arrangement','delete-work-arrangement'):return False
    import game as g
    name=g.text_value(a.get('name'),40);kind=a['type'];plans=s.get('workArrangements',{})
    if kind=='save-work-arrangement':
        g.require(name not in plans,'That name is already saved. Choose a new name or remove the old arrangement first.')
        g.require(len(plans)<8,'Keep up to eight arrangements. Remove an old one first.')
        members=g.household_members(s)
        g.require(all(g.character_at_castle(s,who) for who in members),'Bring everyone home before saving their current arrangement.')
        plan={who:g.character_assignment(s,who) for who in members}
        initialize(s);s['workArrangements'][name]=plan
    else:
        g.require(name in plans,'Choose a saved work arrangement.')
        if kind=='delete-work-arrangement':del s['workArrangements'][name]
        else:
            staged,changes,reasons=preview(s,plans[name]);g.require(not reasons,' '.join(reasons));g.require(bool(changes),'This arrangement is already in place.')
            # No partial changes if one resident/assignment is no longer available.
            s.clear();s.update(staged)
            g.add_journal(s,'Applied work arrangement “'+name+'”. '+ '; '.join(r['name']+': '+r['before']+' → '+r['after'] for r in changes)+'. No time or funding spent; project progress is retained.')
    return True
