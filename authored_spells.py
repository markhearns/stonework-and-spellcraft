"""The original four authored household spells retain their save identities."""
IDEAS={'warm-twist':('Warmth','Binding'),'root-song':('Growth','Rhythm'),'luminous-copy':('Light','Impression'),'clarify-glass':('Refraction','Separation')}
def install(forms):
 for key,d in forms.items():
  d['ideas']=list(IDEAS[key]);d['requiredPrinciples']=[d['requiredPrinciple']]
