"""Explicit evening wind-down within the existing three-phase day."""
from copy import deepcopy
OPTIONS={'tea':('A last cup','You leave the work where it can be found tomorrow and take a last warm cup by the hearth.'),'reading':('A few pages for yourself','You close the working notebook and choose something to read for pleasure. There is no passage to master tonight.'),'quiet':('Let the house settle','You check the latch, set tomorrow’s things within reach and listen as the castle grows quiet.')}
def initialize(s):
 s.setdefault('overnightRest',{})
 s.setdefault('eveningRest',{'choices':{},'memories':[]})
def apply(s,a):
 if a.get('type')!='evening-rest':return False
 import game as g
 g.require(g.character_at_castle(s,'founder'),'Return home to wind down.');g.require(s['currentDayPhase']=='evening','Wind down during the evening.');key=a.get('choice');g.require(isinstance(key,str) and key in OPTIONS,'Choose a quiet evening activity.')
 participants=a.get('participants',['founder'])
 g.require(isinstance(participants,list) and participants and all(isinstance(w,str) for w in participants) and len(set(participants))==len(participants) and 'founder' in participants,'Choose yourself and distinct household members to rest.')
 import work_arrangements
 staged,changes,reasons=work_arrangements.preview(s,{w:'rest' for w in participants})
 g.require(not reasons,' '.join(reasons))
 day=str(s['dayNumber']);r=s['eveningRest'];g.require(day not in r['choices'],'Tonight’s wind-down is already remembered. Choose Rest in assignments if you changed plans.')
 for who in participants:g.set_character_assignment(s,who,'rest')
 import resident_bonds
 resident_bonds.award(s,participants,'wind-down:'+day,OPTIONS[key][0]+' together',2)
 r['choices'][day]=key;title,text=OPTIONS[key];r['memories'].append({'day':s['dayNumber'],'title':title,'text':text});r['memories']=r['memories'][-30:];g.set_character_assignment(s,'founder','rest');g.add_journal(s,title+': '+text+' Resting tonight: '+', '.join(g.character_profile(s,w)['name'] for w in participants)+'. Advance ends the evening and includes the night’s sleep.');return True
def resolve(s,summary,assignments,phase):
 if phase!='evening':return
 import game as g
 rested=[]
 for w,assignment in assignments.items():
  if assignment=='rest':s['overnightRest'][w]=s['dayNumber']+1;rested.append(g.character_profile(s,w)['name'])
 if rested:summary.append('Rested overnight at home: '+', '.join(rested)+'. Morning begins after sleep; no separate sleep turn.')
def view(s):
 import game as g
 return {'options':{k:{'title':v[0],'text':v[1]} for k,v in OPTIONS.items()},'available':g.character_at_castle(s,'founder') and s['currentDayPhase']=='evening' and str(s['dayNumber']) not in s['eveningRest']['choices'],'lastRestedMorning':s['overnightRest'].get('founder'),'memories':deepcopy(s['eveningRest']['memories'][-5:])}
