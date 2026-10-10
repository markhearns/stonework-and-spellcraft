"""Authored Djinn companion and her practiced ember magic."""
KEY='zahra'

def authored(profile):return profile and profile.get('identitySource')=='authored-local-encounter'

def start_magic(s):
 """Zahra's practiced starter spell: ordinary preparation, input and casting rules."""
 if not authored(s.get('people',{}).get(KEY)):return
 import game as g
 for principle in ('water-guidance','steady-hearth-wards'):g.learn_for_character(s,KEY,principle)
 if not any(sp['ownerId']==KEY and sp['formId']=='warm-twist' for sp in s['spellbook']):
  s['spellbook'].append({'id':'spell-'+str(s['nextSpellNumber']),'ownerId':KEY,'formId':'warm-twist','name':'Warm-twist binding','intent':'Direct a small steady ember through prepared fibres.','materials':['sun-amber','binding-thread'],'status':'learned','completedWorkPhases':2,'castCount':0})
  s['nextSpellNumber']+=1

