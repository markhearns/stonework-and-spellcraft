from copy import deepcopy
import json, sqlite3, tempfile, unittest, uuid
from pathlib import Path
from unittest.mock import patch
import game as g
import relationships as r
import relationship_content as content
import social_life
import test_household_chapters as household
import test_companion_participation as company
from server import GameStore

class RelationshipTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();household.HouseholdChapterTests.member(self,'tamsin')
  self.s['housingRooms']['garden-chamber']['status']='complete';self.s['bedroomAssignments']['tamsin']='garden-chamber'
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def share(self,key,choice):self.act('share-relationship',sceneId=key,choice=choice)
 def reject(self,**fields):
  old=deepcopy(self.s)
  with self.assertRaises(g.RuleError):self.act(**fields)
  self.assertEqual(old,self.s)
 def story(self,agreement='turns',follow='keep'):
  for d in content.STORY:
   choice=agreement if d['id']=='agreement' else follow if d['id']=='followthrough' else next(iter(d['choices']))
   protected={k:deepcopy(v) for k,v in self.s.items() if k not in ('relationships','journal','residentBonds')}
   self.share('story:'+d['id'],choice)
   self.assertEqual(protected,{k:self.s[k] for k in protected})
   self.act('advance')
 def test_all_agreements_and_followthrough_branches_remain_playable(self):
  for agreement in ('turns','askfirst','company','no_promise'):
   for follow in ('keep','renegotiate','apologise') if agreement!='no_promise' else ('keep',):
    with self.subTest(agreement=agreement,follow=follow):
     self.setUp();self.story(agreement,follow)
     self.assertEqual(len(r.saved(self.s)['memories']),6)
     status=r.saved(self.s)['promise']['status']
     self.assertEqual(status,'not promised' if agreement=='no_promise' else {'keep':'fulfilled','renegotiate':'renegotiated and fulfilled','apologise':'withdrawn with apology'}[follow])
     callback=r.saved(self.s)['memories']['story:callback']
     self.assertIn(status,callback['opening']);self.assertIn('Last time you chose',callback['opening'])
     self.assertGreater(r.saved(self.s)['bonds']['mira|tamsin']['respect'],0)
 def test_all_story_responses_and_visible_effects(self):
  for i,d in enumerate(content.STORY):
   for choice in d['choices']:
    self.setUp()
    for prev in content.STORY[:i]:
     self.share('story:'+prev['id'],next(iter(prev['choices'])));self.act('advance')
    row=next(x for x in r.rows(self.s) if x['id']=='story:'+d['id'])
    self.assertTrue(row['choices'][choice]['effect']);self.share(row['id'],choice)
    self.assertTrue(r.saved(self.s)['memories'][row['id']]['response'])
 def test_story_requires_real_presence_and_later_phase_and_retries_are_atomic(self):
  self.reject(kind='share-relationship',sceneId='story:needs',choice='ask')
  self.share('story:table','listen')
  self.reject(kind='share-relationship',sceneId='story:table',choice='name')
  self.reject(kind='share-relationship',sceneId='story:needs',choice='ask')
  self.act('advance')
  with patch('game.character_at_castle',side_effect=lambda s,p:p!='tamsin'):
   row=next(x for x in r.rows(self.s) if x['id']=='story:needs')
   self.assertFalse(row['available']);self.assertEqual(row['opening'],'');self.assertEqual(row['choices'],{})
   self.reject(kind='share-relationship',sceneId=row['id'],choice='ask')
  for key,choice in (([], 'ask'),('imaginary','ask'),('story:needs',[]),('story:needs','invented')):
   self.reject(kind='share-relationship',sceneId=key,choice=choice)
 def test_defer_restore_and_read_have_no_relationship_effect(self):
  old=deepcopy(self.s);r.view(self.s);r.context(self.s,'mira');g.public_state(self.s);self.assertEqual(old,self.s)
  self.act('defer-relationship',sceneId='story:table');self.assertEqual(r.saved(self.s)['events'],{})
  self.reject(kind='defer-relationship',sceneId='story:table')
  self.s['dayNumber']+=1000
  self.act('restore-relationship',sceneId='story:table');self.assertEqual(r.saved(self.s)['events'],{})
  self.share('story:table','listen')
 def test_independent_dimensions_and_no_penalty_for_candid_disagreement(self):
  self.act('share-social-conversation',sceneId='personal:mira:0',choice='candid')
  bond=r.saved(self.s)['bonds']['founder|mira'];self.assertEqual([bond[k] for k in r.DIMENSIONS],[0,0,1])
  self.act('share-social-conversation',sceneId='everyday:mira',choice='warm')
  self.assertEqual([bond[k] for k in r.DIMENSIONS],[0,1,1])
  self.assertTrue(next(x for x in r.rows(self.s) if x['id']=='invitation:mira')['available'])
  self.share('invitation:mira','decline');self.assertEqual([bond[k] for k in r.DIMENSIONS],[0,1,2])
  self.assertNotIn('romance',bond)
 def test_all_fourteen_invitations_have_three_responses_and_remember_boundaries(self):
  for who in content.PREFERENCES:
   for choice in ('join','ask','decline'):
    self.setUp();household.HouseholdChapterTests.member(self,who)
    self.act('share-social-conversation',sceneId='personal:'+who+':0',choice='curious')
    self.act('share-social-conversation',sceneId='everyday:'+who,choice='warm')
    row=next(x for x in r.rows(self.s) if x['id']=='invitation:'+who)
    self.assertEqual(len(row['choices']),3);self.assertNotIn(content.PREFERENCES[who][4],json.dumps(row))
    self.share(row['id'],choice)
    memory=r.saved(self.s)['memories'][row['id']]
    if choice=='ask':
     self.assertEqual(memory['response'],r.invitation_definition(who)['choices']['ask'][1]);self.assertEqual(memory['playerLine'],r.invitation_definition(who)['choices']['ask'][0])
    self.assertTrue(memory['response']);self.assertFalse(next(x for x in r.rows(self.s) if x['id']==row['id'])['available'])
 def test_repeated_room_activity_cannot_farm_relationships(self):
  household.HouseholdChapterTests.activity(self,'mira')
  before=deepcopy(r.saved(self.s));household.HouseholdChapterTests.activity(self,'mira')
  self.assertEqual(before,r.saved(self.s))
 def test_peer_memories_build_actual_connections(self):
  self.act('share-social-conversation',sceneId='pair:mira-tamsin:0',choice='warm')
  self.assertEqual(r.saved(self.s)['bonds']['mira|tamsin']['affection'],1)
  self.assertEqual(r.saved(self.s)['bonds']['founder|mira']['affection'],1)
 def test_withdrawal_does_not_damage_npc_pair_and_leaves_all_routes_open(self):
  for d in content.STORY[:3]:
   self.share('story:'+d['id'],next(iter(d['choices'])));self.act('advance')
  old=deepcopy(r.saved(self.s)['bonds']);self.share('story:followthrough','apologise')
  self.assertEqual(old['mira|tamsin'],r.saved(self.s)['bonds']['mira|tamsin'])
  for who in ('mira','tamsin'):
   self.assertEqual(r.saved(self.s)['bonds']['founder|'+who]['trust'],old['founder|'+who]['trust']-1)
  self.assertTrue(social_life.row(self.s,'personal:mira:0')['available'])
  self.act('advance');self.assertTrue(next(x for x in r.rows(self.s) if x['id']=='story:review')['available'])
 def test_relationship_caps_and_only_actual_delta_is_recorded(self):
  for n in range(15):r.remember(self.s,str(n),{'title':'Fixture','participants':['founder','mira']},'respect')
  self.assertEqual(r.saved(self.s)['bonds']['founder|mira']['respect'],12)
  self.assertEqual(r.saved(self.s)['events']['14']['effects'][0]['change'],0)
 def test_context_is_scoped_and_has_no_future_replies(self):
  self.act('share-social-conversation',sceneId='personal:mira:0',choice='warm')
  self.assertEqual(r.context(self.s,'tamsin'),{'bonds':[],'memories':[],'promise':None})
  self.share('story:table','listen')
  context=r.context(self.s,'mira');self.assertEqual(len(context['memories']),1)
  self.assertNotIn('The first awkward revision',json.dumps(context))
  context['memories'][0]['response']='mutated';self.assertNotEqual(r.saved(self.s)['memories']['story:table']['response'],'mutated')
 def test_migration_preserves_old_memories_without_retroactive_scoring(self):
  self.act('share-social-conversation',sceneId='personal:mira:0',choice='warm')
  self.s.pop('relationships');self.s['schemaVersion']=50;old=deepcopy(self.s)
  g.migrate_state(self.s);self.assertEqual(self.s['schemaVersion'],g.CURRENT_SCHEMA_VERSION);self.assertEqual(r.saved(self.s)['events'],{})
  for k,v in old.items():
   if k!='schemaVersion':self.assertEqual(self.s[k],v)
  current=deepcopy(self.s);g.migrate_state(self.s);self.assertEqual(current,self.s)
 def test_store_migration_backup_retry_and_reload(self):
  with tempfile.TemporaryDirectory() as directory:
   st=GameStore(directory);self.s.pop('relationships');self.s['schemaVersion']=50
   with sqlite3.connect(st.database) as db:db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(self.s),))
   st=GameStore(directory);self.assertTrue(Path(directory,f'campaign-before-schema-50-to-{g.CURRENT_SCHEMA_VERSION}.sqlite3').exists())
   action={'requestId':uuid.uuid4().hex,'expectedRevision':st.read()['revision'],'action':{'type':'share-relationship','sceneId':'story:table','choice':'listen'}}
   st.action(action);before=st.read();st.action(action);self.assertEqual(before,st.read())
   self.assertEqual(GameStore(directory).read()['relationships'],before['relationships'])

class PartyBuildRegressionTests(unittest.TestCase):
 def test_different_party_builds_all_complete_without_changing_relationships(self):
  import beacon_expedition as b
  for style in ('minimum-solo','scholar-solo','athlete-pair','diplomat-pair'):
   t=company.CompanionParticipationTests();t.setUp()
   for who in ('founder','mira'):
    t.s['characterBuilds'][who]['attributes']={k:1 for k in g.character_builds.ATTRIBUTES}
    t.s['characterSkills'][who]={k:0 for k in g.CHARACTER_SKILLS}
   if style=='scholar-solo':
    t.s['characterBuilds']['founder']['attributes']['intelligence']=9
   elif style=='athlete-pair':
    t.s['characterBuilds']['founder']['attributes']['might']=8
    t.s['characterBuilds']['mira']['attributes']['dexterity']=8
   elif style=='diplomat-pair':
    t.s['characterBuilds']['founder']['attributes']['charisma']=9
    t.s['characterBuilds']['mira']['attributes']['intelligence']=9
   old=deepcopy(r.saved(t.s));t.start('mira' if style.endswith('pair') else None)
   selected=[]
   for d in b.STEPS:
    viable=[k for k,c in d['choices'].items() if not c.get('castForm') and not b.blockers(t.s,c)]
    self.assertIn('patient',viable)
    key=next((k for k in viable if k!='patient'),'patient');selected.append(key);t.method(key)
   t.act('return-expedition');t.advance()
   self.assertEqual(b.saved(t.s)['discoveries'],['survey']);self.assertEqual(old,r.saved(t.s))
   if style=='minimum-solo':self.assertEqual(selected,['patient']*6)
   else:self.assertTrue(any(k!='patient' for k in selected))
