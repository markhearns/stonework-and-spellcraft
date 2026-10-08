"""Deterministic construction advice from implemented forms, never semantic promises."""
from collections import Counter
from itertools import product

LIMITS={
 'warm-twist':'Binds a small batch of fibres into cord. It does not repair buildings, control people or create material from nothing.',
 'root-song':'Supports a small ivy harvest in the Conservatory. It does not instantly grow forests or heal a person.',
 'luminous-copy':'Produces checked archive copies for a copying commission. It does not reveal unknown information or counterfeit money.',
 'clarify-glass':'Clarifies the supported glass component. It does not grant remote sight or reveal hidden facts.'}

def view(state,who):
    import game as g
    rows={}
    for key,form in g.SPELL_FORMS.items():
        options=[[m for m,d in g.MATERIALS.items() if prop in d['properties']] for prop in form['requiredProperties']]
        combinations=[]
        for parts in product(*options):
            counts=Counter(parts)
            if all(state['materialInventory'][m]-state['materialReserveTargets'][m]>=n for m,n in counts.items()):
                combinations.append(list(parts))
        selected=combinations[0] if combinations else [choices[0] for choices in options]
        spell={'ownerId':who,'formId':key,'materials':selected,'status':'draft','id':'guide-only'}
        blockers=g.spell_blockers(state,spell)
        if not combinations:blockers.append('No complete component combination is currently available above protected reserves. Gather materials or explicitly review reserves.')
        existing=next((s for s in state['spellbook'] if s['ownerId']==who and s['formId']==key),None)
        rows[key]={'name':form['name'],'effect':form['effect'],'personalEffect':g.character_builds.output_description(state,who,key),
          'ideas':form['ideas'],'principles':[{'id':p,'name':g.PRINCIPLE_NAMES[p],'known':p in g.character_principles(state,who),'source':g.PRINCIPLE_GUIDE.get(p,{'source':'Study this principle personally.','view':'development'})} for p in form['requiredPrinciples']],
          'principleId':form['requiredPrinciple'],'principleKnown':all(p in g.character_principles(state,who) for p in form['requiredPrinciples']),
          'source':g.PRINCIPLE_GUIDE.get(form['requiredPrinciple'],{'source':'Learn this principle through its existing research or personal study path.','view':'development'}),
          'requiredProperties':form['requiredProperties'],'componentOptions':options,'availableCombinations':combinations[:6],
          'testingBlockers':blockers,'roomId':form['roomId'],'testingCrowns':4,'testingPhases':2,
          'castingInputs':form['castingInputs'],'limits':form.get('limits',LIMITS.get(key,'Only the listed effect is produced.')),
          'existingSpellId':existing['id'] if existing else None,'existingStatus':existing['status'] if existing else None}
    return rows
