import json
import tempfile
import unittest
import uuid
from pathlib import Path
import game as g
import public_workshop as w
import character_pool
from server import CampaignLibrary, GameStore

class SoloStartTests(unittest.TestCase):
    def test_fresh_opening_is_playable_without_mira_or_cheats(self):
        s=g.new_campaign('fresh')
        self.assertEqual(g.household_members(s),['founder'])
        self.assertEqual(g.known_people(s),['founder'])
        self.assertNotIn('mira',s['bedroomAssignments'])
        self.assertFalse(g.character_at_castle(s,'mira'))
        self.assertEqual(s['currentDayPhase'],'morning')
        g.apply_action(s,{'type':'start-research'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['researchStatus'],'complete')
        g.apply_action(s,{'type':'start-crafting','recipeId':'warming-lantern','materials':['sun-amber','binding-thread']})
        for _ in range(2):g.apply_action(s,{'type':'advance'})
        self.assertEqual(s['craftedArtifacts']['warming-lantern'],1)
        self.assertFalse(s['testing']['used'])
        self.assertFalse(any('Mira' in e['text'] for e in s['journal']))
        self.assertEqual(list(g.public_state(s)['presentPeople']),['founder'])

    def test_solo_archive_route_and_first_normal_household_arrival(self):
        s=g.new_campaign('fresh')
        g.apply_action(s,{'type':'start-research'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        g.apply_action(s,{'type':'focus-research','researchId':'archive-foundations','leaderId':'founder'})
        for _ in range(3):g.apply_action(s,{'type':'advance'})
        self.assertIn('reference-binding',g.character_principles(s,'founder'))
        self.assertTrue(g.site_available(s,'hillfold-bindery'))
        s['founderKnownPrinciples']+=['clear-instruction','gentle-refraction']
        s['sharedFunds']=20
        self.assertTrue(any('index charm' in b for b in g.research_blockers(s,'courteous-passage','founder')))
        g.apply_action(s,{'type':'buy-material','materialId':'porous-clay'})
        g.apply_action(s,{'type':'start-crafting','recipeId':'index-charm','materials':['porous-clay','binding-thread']})
        for _ in range(g.RECIPES['index-charm']['requiredWorkPhases']):g.apply_action(s,{'type':'advance'})
        g.apply_action(s,{'type':'install-index-charm','installed':True})
        self.assertEqual(g.research_blockers(s,'courteous-passage','founder'),[])
        g.apply_action(s,{'type':'start-local-visit','encounterId':'maren'})
        g.apply_action(s,{'type':'advance'})
        contact=next(k for k,c in s['summoningContacts'].items() if c['personId']=='maren')
        import summoning
        for topic in summoning.candidate_catalogue(s)['maren']['topics']:
            g.apply_action(s,{'type':'summoning-talk','contactId':contact,'topic':topic})
        g.apply_action(s,{'type':'summoning-invite','contactId':contact,'roomId':'bedchamber'})
        g.apply_action(s,{'type':'advance'})
        g.apply_action(s,{'type':'summoning-ask-stay','contactId':contact})
        g.apply_action(s,{'type':'summoning-household-decision','contactId':contact,'decision':'invite-to-stay'})
        self.assertEqual(g.household_members(s),['founder','maren'])
        self.assertFalse(s['testing']['used'])
        self.assertNotIn('mira',g.public_state(s)['characterCatalog'])

    def test_new_game_retry_isolation_and_schema_backup(self):
        with tempfile.TemporaryDirectory() as d:
            library=CampaignLibrary(d);old=library.get('default').read()
            p={'campaignId':'c-'+uuid.uuid4().hex,'mode':'solo','name':'First morning','startType':'fresh'}
            library.create(p);library.create(p)
            s=library.get(p['campaignId']).read()
            self.assertEqual(s['startType'],'fresh');self.assertEqual(s['revision'],0)
            self.assertEqual(library.get('default').read(),old)
            with self.assertRaises(g.RuleError):library.create({**p,'startType':'demo'})
            self.assertEqual(CampaignLibrary(d).get(p['campaignId']).read(),s)
            self.assertEqual(library.list()[1]['startType'],'fresh')
            legacy=dict(old);legacy['schemaVersion']=37;legacy.pop('testing');legacy.pop('startType')
            store=library.get('default')
            with store.connect() as db:db.execute('UPDATE campaign SET state=?',(json.dumps(legacy),))
            migrated=GameStore(d).read()
            self.assertEqual(migrated['startType'],'demo');self.assertIn('mira',g.household_members(migrated))
            self.assertTrue(Path(d,'campaign-before-schema-37-to-66.sqlite3').exists())

    def test_testing_transaction_retry_validation_and_marking(self):
        with tempfile.TemporaryDirectory() as d:
            store=GameStore(d,start_type='fresh')
            def action(a,request=None):return store.action({'requestId':request or uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':a})
            with self.assertRaises(g.RuleError):action({'type':'cheat-resource','resourceId':'crowns','quantity':10})
            action({'type':'cheat-toggle','enabled':True})
            p={'requestId':uuid.uuid4().hex,'expectedRevision':store.read()['revision'],'action':{'type':'cheat-resource','resourceId':'crowns','quantity':25}}
            once=store.action(p);self.assertEqual(store.action(p),once)
            for q in (True,-1,0,10001,1.5,'20'):
                before=store.read()
                with self.assertRaises(g.RuleError):action({'type':'cheat-resource','resourceId':'crowns','quantity':q})
                self.assertEqual(store.read(),before)
            action({'type':'cheat-build','buildingId':'west-chamber'})
            action({'type':'cheat-character','ancestry':'Human','name':'Testing Reader'})
            s=store.read();self.assertEqual(len(g.household_members(s)),2)
            self.assertEqual(s['dayNumber'],1);self.assertEqual(s['currentDayPhase'],'morning')
            self.assertEqual(s['sharedFunds'],65)
            action({'type':'cheat-toggle','enabled':False})
            self.assertTrue(GameStore(d).read()['testing']['used'])
            with self.assertRaises(g.RuleError):action({'type':'cheat-resource','resourceId':'crowns','quantity':1})

    def test_spawns_all_ancestries_and_core_and_public_objects(self):
        for ancestry in character_pool.ANCESTRIES:
            s=g.new_campaign('fresh');g.apply_action(s,{'type':'cheat-toggle','enabled':True})
            g.apply_action(s,{'type':'cheat-character','ancestry':ancestry})
            g.apply_action(s,{'type':'advance'});v=g.public_state(s)
            who=g.household_members(s)[1]
            self.assertTrue(g.character_at_castle(s,who));self.assertEqual(v['people'][who]['ancestryLabel'],ancestry)
            self.assertGreaterEqual(v['people'][who]['adultAgeYears'],18)
            if ancestry=='Golem':self.assertEqual(g.character_principles(s,who),[])
        for key in ('conservatory','west-chamber','garden-chamber',*g.FACILITIES):g.apply_action(s,{'type':'cheat-build','buildingId':key})
        for kind in ('artifact','furnishing','equipment'):
            r=next(r for r in w.catalogue()['records'].values() if w.rule_for(r) and w.rule_for(r)['kind']==kind and not r['ancestryRestrictions'])
            g.apply_action(s,{'type':'cheat-object','recordId':r['id'],'ownerId':'founder'})
        g.apply_action(s,{'type':'cheat-object','recordId':'warming-lantern'})
        material=next(iter(w.records('material')))
        g.apply_action(s,{'type':'cheat-resource','resourceId':material,'quantity':5})
        self.assertEqual(w.stock(s,material)[material],5)
        g.apply_action(s,{'type':'cheat-knowledge','ownerId':'founder','principleId':'steady-hearth-wards'})
        self.assertEqual(s['researchStatus'],'complete')
        self.assertEqual(len(g.public_state(s)['publicWorkshopView']['items']),3)
        self.assertEqual(s['craftedArtifacts']['warming-lantern'],1)
