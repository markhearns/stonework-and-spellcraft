"""Optional equipment requests with real fitting and supervised proof work."""
from copy import deepcopy
ROOMS=dict(zip('mira tamsin iona aurelia neris sabine koharu zahra fenna kaede elowen nyssara sylva'.split(),'library kitchen command-room guard-barracks hot-spring dungeons workshop smithy common-room training-yard infirmary enchanting-room conservatory'.split()))
ROOMS['founder']='workshop'
CONTENT={'founder':('A familiar weight','Choose the piece you want to carry forward. Let its fitting reflect the work you have learned to do.','You mark the proven fitting in your own hand. The familiar object carries a little more of your history.','personal-control'),
'mira':('Notes within reach','A familiar tool should let me look up from the page. Help me find the right mark by touch.','Now the notes can support a conversation instead of interrupting it.','reference'),
'tamsin':('A grip that knows the hand','I use the small things often. I would rather have one good grip than something impressive that catches my sleeve.','You listened to the small complaint. That is usually where useful work begins.','precision'),
'iona':('A signal someone can read','If a plan needs explaining during the retreat, the plan is late. Let us make the signal unmistakable.','Good. I can trust that without having to raise my voice.','signal'),
'aurelia':('Room to turn','Protection must leave room for the person wearing it. Especially when she needs to turn quickly.','A guard should be able to face someone without knocking over the furniture.','cover'),
'neris':('Sure hands in the rain','A grip that behaves beautifully when dry has told us only half its story. Bring a basin.','It seems we have persuaded it to be useful in my sort of weather.','footing'),

'sabine':('The keeper’s margin','The important line is the one you do not cross. I want a tool that makes that boundary easy to keep.','It opens as carefully as it closes. I rather insist on that distinction.','seals'),
'koharu':('Keep the useful wear','Do not polish its history away. Just mend the part that makes me fight it.','Still mine. Only a little less stubborn. I suppose that is a compliment to both of us.','repair'),
'zahra':('An honest line','A steady ember is no excuse for a crooked fitting. Mark the line; I will tell you when it sits right.','Good. It does what the mark promises. We can build on that.','measure'),
'fenna':('Nothing to catch on the path','If it catches every branch, I will remember the branches instead of the route. A quieter arrangement, please.','That is much better. Now I can pay attention to where we are going.','route'),
'kaede':('Exactly there','Anyone can make a loud strike. I want to stop this one exactly where I mean to. Hold the chalk, not the target.','There. I told you the interesting part was knowing when to stop.','restraint'),
'elowen':('A warning that reassures','Someone depending on a ward should be able to tell whether it is ready. A quiet sign is enough.','Clear to the person using it. Reassuring to the person being helped.','care'),
'nyssara':('A result worth writing down','We will measure it twice, then let someone else read the result. A convincing shimmer has no place in the notebook.','Repeatable. That is a much lovelier word than spectacular.','assay'),
'sylva':('A fitting that can grow with me','Leave room for the living part. It is quite capable of disagreeing with a buckle.','It has learned a little patience. We should reward it by making something useful.','living-fit')}
def record(s,who):return s['armoury']['signatures'].get(who)
def stage(s,who):
 r=record(s,who)
 return 'offered' if not r else 'complete' if r.get('completedOn') else 'closing' if r.get('proved') else 'proof' if r.get('fitted') else 'fitting'
def lines(who):return CONTENT.get(who,('Something made my own','Help me fit this to the work I actually do.','That feels like mine now. Let us see what we can make of it.','personal'))
def remember(s,who,title,text):
 import game as g, armoury as a
 s['armoury']['memories'].append({'who':who,'title':title,'text':text,**a.stamp(s)})
 s['conversation'].append({'speaker':g.character_profile(s,who)['name'],'text':text});g.add_journal(s,title+': '+text)
def view(s):
 import game as g, armoury as a, headquarters as h,signature_growth
 rows=[]
 for who in g.household_members(s):
  title,request,response,theme=lines(who);room=ROOMS.get(who,'workshop');st=stage(s,who);r=record(s,who);blockers=[]
  if not all(g.character_at_castle(s,w) for w in ('founder',who)):blockers.append('Return home together for this invitation.')
  if not h.ready(s,room):blockers.append('Restore '+g.ROOMS.get(room,{'name':room})['name']+' first.')
  if r and (r['itemId'] not in a.state(s)['items'] or a.state(s)['items'][r['itemId']]['ownerId']!=who):blockers.append('The chosen item has changed owner. Agree a replacement to continue the same project.')
  if st=='fitting' and (g.character_assignment(s,who)!='rest' or g.character_assignment(s,'founder')!='rest'):blockers.append('Free both participants before the shared fitting.')
  if st=='proof' and not h.ready(s,'training-yard'):blockers.append('Restore the training yard for the supervised proof.')
  rows.append({'growth':signature_growth.view(s,who),'who':who,'title':title,'request':request,'response':response if st=='complete' else None,'room':room,'theme':theme,'stage':st,'record':deepcopy(r),'blockers':blockers,'items':[i['id'] for i in a.state(s)['items'].values() if i['ownerId']==who and i['location']=='armoury']})
 return rows
def apply(s,act):
 import game as g, armoury as a, headquarters as h
 kind=act.get('type')
 if kind not in ('gear-signature-choose','gear-signature-fit','gear-signature-proof','gear-signature-close'):return False
 who=act.get('ownerId');a.home(s,who)
 row=next(x for x in view(s) if x['who']==who);r=record(s,who)
 if kind=='gear-signature-choose':
  g.require(h.ready(s,row['room']),'Restore the resident’s associated room first.');it=a.owned(s,act.get('itemId'),who);g.require(not a.busy(s,it['id']),'Finish work on the chosen item first.')
  if r:
   old=a.state(s)['items'].get(r['itemId']);g.require(not old or old['ownerId']!=who,'Keep the chosen piece, or agree its transfer before selecting a replacement.');r['itemId']=it['id'];r['replacements'].append(it['id'])
  else:
   s['armoury']['signatures'][who]={'itemId':it['id'],'fitted':False,'proved':False,'completedOn':None,'replacements':[],'chosenOn':a.stamp(s)};remember(s,who,row['title'],row['request'])
  it['locked']=True
 else:
  g.require(r is not None,'Choose an owned piece first.');g.require(not row['blockers'],' '.join(row['blockers']));it=a.owned(s,r['itemId'],who)
  if kind=='gear-signature-fit':
   g.require(stage(s,who)=='fitting','This fitting is already complete or underway.');g.require(s['sharedFunds']>=4,'The fitting needs 4 crowns.');g.require('founder' not in a.state(s)['jobs'],'Finish the scholar’s funded equipment work first.')
   s['sharedFunds']-=4;a.state(s)['jobs']['founder']={'operation':'signature-fit','workerId':'founder','itemId':it['id'],'effect':None,'name':row['title']+' · shared fitting','cost':4,'phases':1,'done':0,'materials':[],'room':row['room'],'signatureOwner':who}
   it['location']='job';g.set_character_assignment(s,'founder','equipment-work');g.set_character_assignment(s,who,'equipment-work' if who=='founder' else 'signature-fitting')
  elif kind=='gear-signature-proof':
   g.require(stage(s,who)=='proof','Finish the personal fitting first.');g.require(a.equipped(s,it['id']),'Equip the chosen piece for the proof.');g.require(g.character_assignment(s,who)=='rest','Free this resident for the supervised exercise.');g.require(who not in a.state(s)['jobs'],'Finish the resident’s funded equipment work first.')
   a.state(s)['jobs'][who]={'operation':'signature-proof','workerId':who,'itemId':None,'signatureItem':it['id'],'effect':None,'name':row['title']+' · '+row['theme']+' exercise','cost':0,'phases':1,'done':0,'materials':[],'room':'training-yard','signatureOwner':who};g.set_character_assignment(s,who,'equipment-work')
  else:
   g.require(stage(s,who)=='closing','Complete the supervised proof first.');choice=act.get('choice');g.require(choice in ('practical','personal','playful'),'Choose an offered response.')
   r.update(completedOn=a.stamp(s),choice=choice);it['capacity']=max(2,it['capacity']);it['signatureOwner']=who
   text=lines(who)[2]+' '+{'practical':'You record the proven fitting together.','personal':'You tell her you wanted it to feel like hers. She keeps that thought with the finished piece.','playful':'You suggest the tool has become rather particular. Her look suggests she knows whom it learned that from.'}[choice];text=lines(who)[2] if who=='founder' else text;remember(s,who,row['title']+' · made personal',text)
   if who=='sabine':
    import resident_specialties as rs
    if rs.active(s,'sabine'):it['enchantments']['dungeon-keeper']={'id':'dungeon-keeper','rank':1};it['capacity']=max(it['capacity'],len(it['enchantments']))
 return True
def job_ready(s,j):
 import game as g, armoury as a
 who=j.get('signatureOwner')
 if not who:return True
 if who not in g.household_members(s) or not g.character_at_castle(s,who):return False
 if j['operation']=='signature-fit':return g.character_assignment(s,who)==('equipment-work' if who=='founder' else 'signature-fitting')
 if j['operation']=='signature-proof':return a.equipped(s,j['signatureItem']) and a.state(s)['items'][j['signatureItem']]['ownerId']==who
 return True
def finish(s,j):
 import game as g, armoury as a
 who=j['signatureOwner'];r=record(s,who)
 if j['operation']=='signature-fit':
  r['fitted']=True;a.state(s)['items'][j['itemId']]['fitOwner']=who
  if g.character_assignment(s,who)=='signature-fitting':g.set_character_assignment(s,who,'rest')
 else:r['proved']=True
def cancel(s,j):
 import game as g
 who=j.get('signatureOwner')
 if who and g.character_assignment(s,who)=='signature-fitting':g.set_character_assignment(s,who,'rest')
def context(s,who):return [deepcopy(m) for m in s.get('armoury',{}).get('memories',[]) if m['who']==who][-8:]
