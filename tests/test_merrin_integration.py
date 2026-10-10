"""Merrin's actual chapel route and cross-system progression, without recruitment cheats."""
from copy import deepcopy
import json
import unittest
import game as g
import romance
import intimacy
import companion_threads as threads
import resident_bonds as bonds
import resident_friendships as friendships
import character_quests as quests
import personal_paths as paths
import foundation_chamber
import bathing_outfits
import character_customization as custom
import room_life

class MerrinIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.s=g.new_campaign();self.s['provisions']['stock']=500;self.s['sharedFunds']=200
  self.s['headquarters']['rooms']['chapel']='complete'
  self.s['housingRooms']['west-chamber']['status']='complete'
  for choice in ('name','open','trial'):self.act('chapel-spirit-talk',choice=choice)
  self.act('chapel-spirit-introduce')
  for topic in ('intentions','home','visit'):self.act('summoning-talk',contactId='introduced-merrin',topic=topic)
  self.act('summoning-invite',contactId='introduced-merrin',roomId='west-chamber');self.advance()
  self.act('summoning-ask-stay',contactId='introduced-merrin')
  self.act('summoning-household-decision',contactId='introduced-merrin',decision='invite-to-stay')
  self.assertFalse(self.s['testing']['enabled']);self.assertIn('merrin',g.household_members(self.s))
 def act(self,kind,**kw):g.apply_action(self.s,dict(type=kind,**kw))
 def advance(self):self.act('advance')
 def chapter(self,n):self.act('share-personal-chapter',characterId='merrin',sceneId='merrin:'+str(n),choice='gentle')
 def established(self):
  self.chapter(0);self.act('accept-outfit-invitation',characterId='merrin',tier='2',responseChoice='warm');self.chapter(1)
  self.act('share-almanac',sceneId='familiar:merrin',choice='warm')
  self.act('share-relationship',sceneId='invitation:merrin',choice='join')
  self.chapter(2);self.act('accept-outfit-invitation',characterId='merrin',tier='3',responseChoice='playful');self.chapter(3)
  for i,choice in enumerate(('warm','candid','candid')):
   self.act('share-social-conversation',sceneId='personal:merrin:'+str(i),choice=choice);self.advance()
 def test_authored_history_unlocks_outfits_romance_and_all_closeness_stages(self):
  self.established()
  self.act('choose-outfit',characterId='merrin',tier='3')
  for i in range(4):
   self.assertEqual(romance.blockers(self.s,'merrin',i),[])
   self.act('share-romance',characterId='merrin',index=i,choice='romantic');self.advance()
  self.assertEqual(romance.level(self.s,'merrin'),4)
  for stage in range(4):
   for kind in ('moment','milestone'):
    for _ in range(15):
     if not intimacy.blockers(self.s,'merrin',stage,kind):break
     self.advance()
    self.assertEqual(intimacy.blockers(self.s,'merrin',stage,kind),[])
    self.act('intimacy-begin',characterId='merrin',stage=stage,sceneKind=kind)
    self.act('intimacy-resolve',characterId='merrin',choice='close');self.advance()
  self.assertEqual(len(intimacy.person(self.s,'merrin')['milestones']),4)
  self.assertIn('fades to black',intimacy.person(self.s,'merrin')['milestones']['3']['response'])
  r=foundation_chamber.saved(self.s);r['completed']={k:{} for k in foundation_chamber.STEPS}
  for who in ('founder','merrin'):g.set_character_assignment(self.s,who,'rest')
  self.assertEqual(foundation_chamber.partner_blockers(self.s,'merrin'),[])
  before=deepcopy(self.s);g.public_state(self.s);self.assertEqual(before,self.s)
  loaded=g.migrate_state(json.loads(json.dumps(self.s)))
  for key in ('romance','intimacy','outfitProgression','householdChapters'):self.assertEqual(loaded[key],self.s[key])
  self.act('pause-romance',characterId='merrin')
  self.assertTrue(foundation_chamber.partner_blockers(self.s,'merrin'))
 def test_preferences_threads_quest_training_and_bathing_use_the_same_identity(self):
  self.established();key='personal:merrin'
  for _ in range(3):
   row=threads.row(self.s,key)
   self.act('thread-answer',sceneId=key,expectedTurn=row['turn'],choice='0')
  self.assertTrue(threads.saved(self.s)['records'][key]['completed'])
  self.advance()
  for _ in range(2):
   row=threads.row(self.s,'followup:merrin')
   self.act('thread-answer',sceneId='followup:merrin',expectedTurn=row['turn'],choice='0')
  self.assertTrue(threads.saved(self.s)['records']['followup:merrin']['completed'])
  qid='personal:merrin'
  for _ in range(2):
   self.act('talk-character-quest',questId=qid,choice='practical')
   self.act('choose-quest-method',questId=qid,methodId='patient')
   for _ in range(4):
    if quests.saved(self.s)['records'][qid]['status']!='working':break
    self.advance()
  self.act('talk-character-quest',questId=qid,choice='warm')
  self.assertEqual(quests.saved(self.s)['records'][qid]['status'],'complete')
  self.s['headquarters']['rooms']['training-yard']='complete'
  self.act('path-train',characterId='merrin',talentId='merrin-shelter');self.advance();self.advance()
  self.act('path-prepare',characterId='merrin',talentId='merrin-shelter',prepared=True)
  self.assertIn('merrin-shelter',paths.record(self.s,'merrin')['techniques'])
  self.s['headquarters']['rooms']['pool']='complete';g.set_character_assignment(self.s,'merrin','rest')
  custom.write_person(self.s,'merrin')['leisureRoom']='pool';self.s['currentDayPhase']='afternoon'
  self.assertEqual(room_life.location(self.s,'merrin'),'pool')
  self.assertTrue(bathing_outfits.view(self.s)['merrin']['active'])
  self.assertIn('merrin',g.public_state(self.s)['characterCatalog'])
 def test_resident_bonding_and_mira_keepsake_include_merrin(self):
  self.chapter(0)
  self.act('share-personal-chapter',characterId='mira',sceneId='mira:0',choice='gentle')
  self.act('share-household-pair',sceneId='mira+merrin:0',choice='method')
  key='merrin|mira';self.assertGreater(self.s['residentBonds']['pairs'][key]['score'],0)
  # Isolate threshold integration; ordinary bonding awards are exercised above.
  self.s['residentBonds']['pairs'][key]['score']=25
  self.act('friendship-share',pairId=key,stage='meeting',choice='named')
  self.act('friendship-arrange',pairId=key,stage='project');self.advance()
  self.assertEqual(friendships.saved(self.s)['pairs'][key]['keepsake']['name'],'Two-voice comedy booklet')
