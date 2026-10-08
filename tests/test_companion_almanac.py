from copy import deepcopy
import json,sqlite3,tempfile,unittest,uuid
from pathlib import Path
import game as g
import companion_almanac as a
import companion_almanac_content as c
import relationships,romance
import test_party_journeys as fixtures
import test_magic_overhaul as magic
from server import GameStore

class CompanionAlmanacTests(unittest.TestCase):
 def setUp(self):
  self.f=fixtures.PartyJourneyTests();self.f.setUp();self.s=self.f.s
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def share(self,key,choice='curious'):self.act('share-almanac',sceneId=key,choice=choice)
 def trust(self,w,n=4,respect=2):
  self.s['relationships']['bonds'][relationships.pair_id('founder',w)]={'participants':['founder',w],'trust':n,'respect':respect,'affection':4}
 def familiar(self,w):
  self.trust(w)
  if not a.row(self.s,'familiar:'+w)['memory']:self.share('familiar:'+w)
 def reject(self,kind,**kw):
  before=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(kind,**kw)
  self.assertEqual(self.s,before)
 def test_all_fourteen_have_realistic_individual_basics(self):
  v=a.views(self.s);self.assertEqual(len(v['people']),15);self.assertEqual(len(v['scenes']),87)
  self.assertEqual(set(c.PERSONAL),set(c.PHYSICAL))
  self.assertGreater(c.PHYSICAL['kaede'][0],c.PHYSICAL['brakka'][0]);self.assertGreater(c.PHYSICAL['brakka'][1],c.PHYSICAL['mira'][1])
  for w,p in v['people'].items():
   self.assertEqual(p['basic']['Ancestry'],g.character_profile(self.s,w)['ancestryLabel']);h,weight,(b,wa,hips),_,_=c.PHYSICAL[w]
   self.assertTrue(150<=h<=200);self.assertTrue(45<=weight<=130);self.assertTrue(wa<b and wa<hips)
 def test_read_only_views_and_context(self):
  before=deepcopy(self.s);a.views(self.s)
  for w in c.PERSONAL:a.context(self.s,w)
  g.public_state(self.s);self.assertEqual(self.s,before)
 def test_locked_personal_facts_absent_from_api_and_dialogue_context(self):
  v=json.dumps(g.public_state(self.s));ctx=json.dumps(a.context(self.s,'mira'))
  for value in [c.PERSONAL['mira']['history'],c.PERSONAL['mira']['worry'],c.PERSONAL['mira']['private'],c.PERSONAL['mira']['attraction']]:
   self.assertNotIn(value,v);self.assertNotIn(value,ctx)
  self.assertFalse(a.row(self.s,'trusted:mira')['opening']);self.assertFalse(a.row(self.s,'intimate:mira')['choices'])
 def test_familiarity_requires_real_bond_or_mutual_milestone(self):
  self.reject('share-almanac',sceneId='familiar:mira',choice='curious');self.trust('mira',2,0);self.share('familiar:mira')
  p=a.profile(self.s,'mira');self.assertTrue(p['sections'][0]['known']);self.assertFalse(p['sections'][1]['known']);self.assertEqual(p['sections'][2]['facts'],{})
 def test_trusted_disclosure_has_friendship_route_without_romance(self):
  for who in c.PERSONAL:
   self.familiar(who);self.share('trusted:'+who)
   self.assertTrue(a.profile(self.s,who)['sections'][1]['known']);self.assertEqual(romance.level(self.s,who),0)
   self.assertIn('Bust / waist / hips',a.profile(self.s,who)['sections'][1]['facts'])
 def test_full_bonds_never_substitute_for_intimate_milestone(self):
  self.familiar('mira');self.share('trusted:mira');self.trust('mira',12,12)
  self.reject('share-almanac',sceneId='intimate:mira',choice='warm')
 def test_intimate_requires_partnership_prior_disclosure_and_open_mode(self):
  self.s['romance']['people']['mira']={'level':3,'mode':'open','deferred':False}
  self.reject('share-almanac',sceneId='intimate:mira',choice='warm');self.share('familiar:mira');self.share('trusted:mira')
  self.s['romance']['people']['mira']['mode']='friendly';self.reject('share-almanac',sceneId='intimate:mira',choice='warm')
  self.s['romance']['people']['mira']['mode']='open';self.share('intimate:mira','warm')
  self.assertEqual(a.profile(self.s,'mira')['sections'][2]['facts']['Turn-ons'],c.PERSONAL['mira']['attraction'])
 def test_known_disclosures_are_remembered_when_romance_is_paused(self):
  self.familiar('mira');self.share('trusted:mira');self.s['romance']['people']['mira']={'level':3,'mode':'open','deferred':False};self.share('intimate:mira')
  self.s['romance']['people']['mira']['mode']='friendly';self.assertTrue(a.profile(self.s,'mira')['sections'][2]['known']);self.assertFalse(a.row(self.s,'intimate:mira')['available'])
 def test_all_three_responses_open_same_information_without_time_or_cost(self):
  for choice in a.CHOICES:
   self.setUp();self.trust('mira');before={k:deepcopy(self.s[k]) for k in ['dayNumber','currentDayPhase','sharedFunds','materialInventory','founderAssignment','residentAssignment']}
   self.share('familiar:mira',choice)
   self.assertEqual(before,{k:self.s[k] for k in before});self.assertTrue(a.profile(self.s,'mira')['sections'][0]['known'])
 def test_repeat_and_forged_choices_do_not_mutate_or_farm_bonds(self):
  self.trust('mira');self.reject('share-almanac',sceneId='familiar:mira',choice='force');self.reject('share-almanac',sceneId='intimate:unknown',choice='warm')
  self.share('familiar:mira');self.reject('share-almanac',sceneId='familiar:mira',choice='warm')
 def test_defer_restore_persists_and_never_expires(self):
  self.trust('mira');self.act('defer-almanac',sceneId='familiar:mira');self.s['dayNumber']+=100
  self.assertTrue(a.row(self.s,'familiar:mira')['deferred']);self.reject('share-almanac',sceneId='familiar:mira',choice='curious')
  self.act('restore-almanac',sceneId='familiar:mira');self.share('familiar:mira')
 def test_absent_participant_cannot_share_and_has_no_false_room_presence(self):
  self.familiar('mira');self.familiar('neris');self.act('start-expedition',siteId='old-waterworks',companionIds=['mira'])
  self.assertIsNone(a.ambient(self.s,'mira'));self.assertIsNone(a.views(self.s)['people']['mira']['roomId'])
  self.reject('share-almanac',sceneId='pair:mira:neris:0',choice='warm')
 def test_all_seven_pair_arcs_remember_choices_and_require_elapsed_phase(self):
  involved=set()
  for x,y,_,_ in c.PAIRS:
   involved.update([x,y]);self.familiar(x);self.familiar(y);self.share(f'pair:{x}:{y}:0','candid')
   self.assertIn(a.CHOICES['candid'][0],a.definition(self.s,f'pair:{x}:{y}:1')['opening'])
   self.reject('share-almanac',sceneId=f'pair:{x}:{y}:1',choice='warm');self.act('advance');self.share(f'pair:{x}:{y}:1','curious');self.act('advance');self.share(f'pair:{x}:{y}:2','warm')
   self.assertEqual(relationships.saved(self.s)['bonds'][relationships.pair_id(x,y)]['affection'],1)
  self.assertEqual(involved,set(c.PERSONAL))
 def test_initiatives_point_to_real_work_without_starting_or_paying(self):
  for who in c.PERSONAL:
   self.familiar(who);before=(self.s['sharedFunds'],g.character_assignment(self.s,who));self.share('initiative:'+who,'warm')
   self.assertEqual(before,(self.s['sharedFunds'],g.character_assignment(self.s,who)));self.assertTrue(a.row(self.s,'initiative:'+who)['target']['view'])
 def test_work_presence_respects_assignment(self):
  g.set_character_assignment(self.s,'mira','archive');self.assertEqual(a.ambient(self.s,'mira')['kind'],'work')
  self.assertIn('shared research',a.ambient(self.s,'mira')['text'])
 def test_magic_reaction_requires_own_actual_cast(self):
  g.set_character_assignment(self.s,'mira','rest');sp=magic.MagicTests.learned(self.f,'water-walk','mira')
  def kinds():
   result=set()
   for d in range(1,10):self.s['dayNumber']=d;result.add(a.ambient(self.s,'mira')['kind'])
   return result
  self.assertNotIn('magic',kinds());g.spell_by_id(self.s,sp)['castCount']=1;self.assertIn('magic',kinds())
 def test_journey_reaction_requires_actual_participation(self):
  g.set_character_assignment(self.s,'mira','rest');self.s['lastExpeditionReport']={'siteId':'old-waterworks','participants':['founder'],'rewards':[]}
  for d in range(6):self.s['dayNumber']=d+1;self.assertNotEqual(a.ambient(self.s,'mira')['kind'],'journey')
  self.s['lastExpeditionReport']['participants'].append('mira');self.assertTrue(any((self.s.update(dayNumber=d+1) or a.ambient(self.s,'mira')['kind']=='journey') for d in range(6)))
 def test_non_authored_and_nonadult_identity_get_no_invented_private_profile(self):
  self.assertIsNone(a.profile(self.s,'founder'));self.assertEqual(a.context(self.s,'unknown'),{})
  self.s['people']['mira']['adultAgeYears']=17;self.assertIsNone(a.profile(self.s,'mira'));self.reject('share-almanac',sceneId='familiar:mira',choice='warm')
 def test_migration_preserves_all_old_progress_and_assets(self):
  old=deepcopy(self.s);old['schemaVersion']=57;old.pop('companionAlmanac',None)
  with tempfile.TemporaryDirectory() as d:
   st=GameStore(d);asset=Path(d,'assets');asset.mkdir(exist_ok=True);(asset/'accepted.png').write_bytes(b'kept')
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(old),))
   upgraded=GameStore(d).read();self.assertTrue(Path(d,'campaign-before-schema-57-to-66.sqlite3').exists());self.assertEqual((asset/'accepted.png').read_bytes(),b'kept')
   expected=deepcopy(old);expected['schemaVersion']=66;expected['revision']+=1;expected['companionAlmanac']={'memories':{},'deferred':[]};__import__('armoury').initialize(expected);self.assertEqual(upgraded,expected)
 def test_retry_and_reload_awards_disclosure_once(self):
  self.trust('mira')
  with tempfile.TemporaryDirectory() as d:
   st=GameStore(d)
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   action={'requestId':uuid.uuid4().hex,'expectedRevision':self.s['revision'],'action':{'type':'share-almanac','sceneId':'familiar:mira','choice':'warm'}}
   first=st.action(action);again=st.action(action);self.assertEqual(first,again)
   self.assertTrue(a.profile(GameStore(d).read(),'mira')['sections'][0]['known']);self.assertEqual(len(a.saved(again)['memories']),1)

   import outfit_progression
   self.assertEqual(outfit_progression.memories(again,'mira').count('almanac:familiar:mira'),1)
   self.assertNotIn('almanac:familiar:mira',outfit_progression.memories(again,'neris'))
