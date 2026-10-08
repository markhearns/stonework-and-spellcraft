"""Creation-only small packages. Never a respec, occupation inference or golem grant."""
import public_workshop as w

def initialize_new_scholar(s,key):
    import game as g
    r=w.definition(key,'starting-package-concept')
    g.require(s['revision']==0 and 'publicStarter' not in s,'Choose a starter only during new campaign creation.')
    principle=r['startingKnowledgeCandidates'][0];practice=r['startingPracticeCandidates'][0]
    focus_id=next(x['id'] for x in r['references'] if x['id'] in w.records('equipment-concept'))
    focus=w.definition(focus_id)
    s['people']['founder']['startingPractices']=[practice]
    s['characterDevelopment']['founder']={'learnedPractices':[practice],'preparedPractices':[],'advancementAwards':{}}
    s['characterSkills']['founder']={k:0 for k in s['characterSkills']['founder']}
    s['founderKnownPrinciples']=[principle]
    s['signatureFocuses']['founder']={'name':focus['name'],'capacity':1,'inscriptions':[],'householdLoadout':[],'expeditionLoadout':[]}
    key=w.owned_object(s,{'recordId':focus_id,'ownerId':'founder','kind':'equipment','id':'creation-starter'},'equipment')
    s['signatureFocuses']['founder']['publicItemId']=key
    s['publicStarter']={'recordId':r['id'],'principleId':principle,'practiceId':practice,'itemId':key}
