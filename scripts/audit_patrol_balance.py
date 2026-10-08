"""Fixed battle fixtures, not earned campaign progression; output JSON only."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
import game as g,field_patrols as p,field_magic as f,armoury as a,personal_paths as paths
from test_field_patrols import FieldPatrolTests
BUILDS={'founder':['scholar-ward'],'kaede':['measured-blow','settled-stance','turning-counter'],'rhess':['spear-watch','banked-flame','relief-signal'],'sabine':['checked-strike','disarming-turn'],'tamsin':['tamsin-wrap','tamsin-snare','tamsin-feint'],'elowen':['elowen-dressing','elowen-recovery','elowen-balance'],'nyssara':['nyssara-score','nyssara-buffer','nyssara-discharge']}
PARTIES=[['founder'],['kaede'],['sabine'],['rhess','kaede'],['sabine','tamsin'],['rhess','elowen'],['founder','rhess','elowen','nyssara']]

def choose(rows):
 def score(r):
  q=r['preview'];new_down=sum(q['healthBefore'][w]>0 and n==0 for w,n in q['healthAfter'].items())
  return 100 if q['enemyAfter']==0 else q['damage']*2+sum(h['amount'] for h in q['healing'])*1.5-q['injury']*1.5-q['exertion']-new_down*10+int(q['opening'])
 return max(rows,key=score)

def run(party,enemy,trained=True):
 t=FieldPatrolTests();t.setUp();s=t.s
 for w in party:
  if w!='founder':t.member(w)
  t.equip(w)
  if trained:
   s=t.s;keys=BUILDS[w];s.setdefault('personalPaths',{})[w]=dict(learned=keys[:],techniques=keys[:],passives=[])
   it=next(i for i in a.state(s)['items'].values() if i['ownerId']==w and i['definitionId']=='steel-sword');it['signatureOwner']=w;a.state(s)['signatures'][w]={'itemId':it['id'],'completedOn':{'day':1},'fitted':True,'proved':True,'replacements':[]}
 t.depart(party);t.enemy(enemy);start=t.s['provisions']['stock'];turns=0;methods=[]
 for _ in range(45):
  r=p.saved(t.s)['active']
  if not r:break
  if r['stage']=='decision':
   rows=[x for x in p.choices(t.s) if not x['blockers'] and x['kind'] not in ('peace','bypass')];row=choose(rows);methods.append(row['role']);t.act('watch-method',methodId=row['id'])
  t.act('advance');turns+=1
 report=p.saved(t.s)['reports'][-1];health={w:f.vitality(t.s,w) for w in party};return dict(party=party,enemy=enemy,trained=trained,completed=report['complete'],advances=turns,health=health,methods=methods,contributions=report.get('contributions',{}),loot=report['loot'],foodUsed=start-t.s['provisions']['stock']+report['loot']['food'])

if __name__=='__main__':
 rows=[run(party,key,trained) for trained in (False,True) for party in PARTIES for key in p.ENEMIES]
 out={'kind':'84 deterministic combat fixtures: 7 party configurations × 6 enemy types × baseline/trained builds. No peaceful shortcuts. Each action commits through the normal rules and reloads the save. This is not an earned-campaign audit.','scenarios':rows}
 Path(sys.argv[1]).write_text(json.dumps(out,indent=2));print('Scenarios',len(rows),'completed',sum(r['completed'] for r in rows))
 for trained in (False,True):
  subset=[r for r in rows if r['trained']==trained];print('trained',trained,'wins',sum(r['completed'] for r in subset),'of',len(subset),'range',min(r['advances'] for r in subset),max(r['advances'] for r in subset))
