"""Shared fixture follows the actual rescue and optional invitation transactions."""
def rescue_and_invite(s,who):
 import game as g,field_patrols as p,character_builds
 s['firstPatrol']['completedOn']={'dayNumber':1,'phase':'morning'}
 s['provisions']['stock']=300
 old=character_builds.build(s,'founder')['attributes']['charisma'];character_builds.build(s,'founder')['attributes']['charisma']=10
 g.apply_action(s,dict(type='recruit-lead',characterId=who,questKind='rescue'))
 g.apply_action(s,dict(type='recruit-depart',characterId=who,participants=['founder']))
 g.apply_action(s,dict(type='advance'))
 row=next(r for r in p.choices(s) if r['kind']=='peace' and not r['blockers'])
 g.apply_action(s,dict(type='watch-method',methodId=row['id']));g.apply_action(s,dict(type='advance'));g.apply_action(s,dict(type='advance'))
 character_builds.build(s,'founder')['attributes']['charisma']=old
 g.apply_action(s,dict(type='recruit-invite',characterId=who))
