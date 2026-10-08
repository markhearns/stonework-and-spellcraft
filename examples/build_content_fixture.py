"""Create a deliberately small, valid importer fixture; not a production pack."""
import json
from pathlib import Path
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from content_packs import REGISTRY,SHARED,route


def fixture_files():
    files={};manifest={'schemaVersion':1,'packId':'stonework-spellcraft-integration-fixture','packVersion':'1.0.0','language':'en','status':'draft-for-integration','ancestries':[],'sharedPools':[],'vocabularyPath':'vocabulary.json','readmePath':'README.md','validationReportPath':'validation-report.json'}
    files['vocabulary.json']={'schemaVersion':1,'tags':[{'id':'practical','definition':'Enjoys useful, carefully checked work.'},{'id':'playful','definition':'Finds room for gentle humour.'}]}
    for key,label in REGISTRY.items():
        names=[];stories=[];appearances=[]
        if key in ('wolfkin','demon','golem'):
            for n,name in enumerate({'wolfkin':['Talvera','Roswen','Helvara'],'demon':['Zavelle','Nathira','Vesrala'],'golem':['Cerelle','Orlisse','Velluna']}[key],1):names.append({'id':key+'-name-00'+str(n),'name':name,'styleTags':['playful']})
            stories=[{'id':key+'-story-001','title':'A margin worth keeping','premise':'She wants to compare ways of leaving useful notes without crowding a page.','personalMotivation':'She wants her observations to be understandable to someone else.','openingHook':'She asks whether a little room could be found for a notebook experiment.','possibleDevelopments':['Compare two sample layouts.','Propose a small folio of clear examples.'],'backgroundTags':['practical'],'themeTags':['practical'],'toneTags':['playful'],'requirements':[],'continuityWarnings':['No notebook exists until gameplay establishes it.','An awakened golem has no prior lived career.']}]
            features={'wolfkin':['grey wolf ears','full grey wolf tail','human face and smooth human skin'],'demon':['swept horns','slender expressive tail'],'golem':['crafted porcelain surface','fine handmade joins']}[key]
            appearances=[{'id':key+'-appearance-001','summary':{'wolfkin':'An adult woman with warm brown skin, black curls, grey wolf ears and a full grey tail; athletic with soft mature curves.','demon':'An adult woman with warm copper skin, dark waves, swept horns and a slender tail; full-figured and poised.','golem':'A fully adult feminine porcelain golem with mature proportions, hand-painted eyes and fine visible maker’s joins.'}[key],'skin':'glazed porcelain' if key=='golem' else 'warm brown','hair':'dark waves','eyes':'amber','build':'athletic with soft mature curves','ancestryFeatures':features,'distinctiveDetails':['fine freckles' if key!='golem' else 'restrained violet glaze lines'],'styleTags':['playful']}]
        path='ancestries/'+key+'.json';files[path]={'schemaVersion':1,'ancestryId':key,'ancestryName':label,'arrivalMethod':route(key),'names':names,'storySeeds':stories,'appearanceDescriptions':appearances}
        manifest['ancestries'].append({'ancestryId':key,'ancestryName':label,'arrivalMethod':route(key),'path':path,'counts':{'names':len(names),'storySeeds':len(stories),'appearanceDescriptions':len(appearances)}})
    def row(key,label,description,**fields):
        return {'id':key,'label':label,'description':description,'expressionExamples':['Offers a useful suggestion with an amused smile.'],'compatibleTags':['practical'],'conflictsWith':[],'ancestryRestrictions':[],'excludedAncestries':[],'usageNotes':'A possible expression, never a completed event or automatic agreement.',**fields}
    pools={
      'personality-nuance':[row('personality-001','Playfully exacting','She enjoys a teasing aside, then checks her work with patient care.',coreTrait='Curious and playful.',counterpoint='Careful about promises.'),row('personality-002','Quietly adventurous','She speaks thoughtfully and welcomes unfamiliar techniques.',coreTrait='Reflective curiosity.',counterpoint='Willing to revise an elegant idea.')],
      'value-boundary':[row('boundary-001','Ask before borrowing','She likes sharing useful things when asked first.',kind='boundary',importance='central',welcomes=['A direct request to borrow a tool.'],declines=['Taking her notebook without asking.'],communicationStyle='Warm, clear and unambiguous.')],
      'habit-mannerism':[row('habit-001','A measured pause','She pauses briefly to find the useful part of a question.',trigger='Thinking through a difficult question.',frequency='occasional',avoidOveruse='Do not repeat in every reply.')],
      'conversational-voice':[row('voice-001','Dry warmth','She favours clear sentences and gentle, observant wit.',sentenceRhythm='Short observations followed by one considered detail.',directness='plainspoken',humourStyle='Dry and affectionate when welcome.',metaphorDomains=['practical'],avoid=['Repeated catchphrases.'])],
      'occupation-background':[row('background-001','Notebook conservator','She repairs everyday notebooks and studies their useful annotations.',occupation='Notebook conservator',originOutline='She learned careful repairs in a neighbourhood bindery, among well-used ledgers and patient teachers.',experienceThemes=['practical'],naturalAmbitionTags=['practical'],suggestedCapabilityPackageId='archive-reader',historyMode='lived-background',excludedAncestries=['golem']),row('background-002','Prospective notebook keeper','She may choose to study how people preserve useful observations.',occupation='Prospective notebook keeper',originOutline='A prospective vocation, with no previous employment or lived history implied.',experienceThemes=['practical'],naturalAmbitionTags=['practical'],suggestedCapabilityPackageId='archive-reader',historyMode='prospective-vocation',ancestryRestrictions=['golem'])],
      'ambition':[row('ambition-001','Clear notes for willing readers','Make a small folio explaining a useful observation clearly enough for another reader to check.',personalMotivation='She values sharing understanding without prescribing conclusions.',scope='small-project',possibleFirstSteps=['Choose an observation.','Compare two ways to explain it.'],possibleComplications=['The first layout may confuse more than it explains.'],satisfyingOutcomes=['A willing reader might suggest a useful correction.'])],
      'social-flirtation-style':[row('social-001','A knowing aside','She enjoys playful compliments when the interest is mutual.',mode='either',suitableContexts=['An unhurried, mutually welcome conversation.'],signalsToProceed=['Both people choose to continue the playful exchange.'],signalsToPause=['A change of subject or expressed discomfort.'],boundaryResponse='Accept the boundary immediately and continue on a comfortable subject.')],
    }
    for kind,(filename,target,extra) in SHARED.items():
        path='shared/'+filename+'.json';entries=pools.get(kind,[]);files[path]={'schemaVersion':1,'poolType':kind,'entries':entries};manifest['sharedPools'].append({'poolType':kind,'path':path,'count':len(entries)})
    files['manifest.json']=manifest
    files['validation-report.json']={'schemaVersion':1,'checksPerformed':['Fixture structure exercised by the prototype test suite.'],'automatedChecksRun':False,'duplicateIds':[],'duplicateNames':[],'brokenReferences':[],'countMismatches':[],'undeclaredTags':[],'contentWarnings':['Deliberately small integration fixture.'],'knownLimitations':['Only wolfkin, demon and golem can be generated. No production originality or semantic review is claimed.']}
    files['README.md']='# Integration fixture\n\nDeliberately incomplete: three names and one story/appearance per supported ancestry, a handful of shared traits. Only wolfkin, demon and golem have generation ingredients. Other arrays are empty and explicitly reported. No generated record is an established event. Full content production and mechanical mapping of the remaining pools remain future integration work.\n'
    return {path:json.dumps(obj,ensure_ascii=False,indent=2) if isinstance(obj,dict) else obj for path,obj in files.items()}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    with zipfile.ZipFile(root/'static/examples/content-pack-fixture.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path,raw in fixture_files().items():z.writestr('stonework-spellcraft-content-pack/'+path,raw)
