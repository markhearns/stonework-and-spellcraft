from copy import deepcopy
import unittest
from game import new_campaign, apply_action, public_state, RuleError, award_advancement, character_sheet, work_contribution, learn_for_character

class SkillTests(unittest.TestCase):
    def setUp(self):self.state=new_campaign()
    def act(self,kind,**fields):return apply_action(self.state,{'type':kind,**fields})
    def advance(self,count=1):
        for _ in range(count):self.act('advance')
    def points(self,who='founder'):award_advancement(self.state,who,'fixture',20,'Fixture accomplishments')
    def train(self,skill,who='founder'):
        self.act('train-skill',characterId=who,skillId=skill);self.advance(2)
    def reject(self,kind,**fields):
        before=deepcopy(self.state)
        with self.assertRaises(RuleError):self.act(kind,**fields)
        self.assertEqual(self.state,before)
    def test_points_reserved_cancelled_and_invested_without_double_spending(self):
        self.reject('train-skill',characterId='founder',skillId='scholarship');self.points()
        self.act('train-skill',characterId='founder',skillId='scholarship')
        sheet=character_sheet(self.state,'founder');self.assertEqual((sheet['availableAdvancement'],sheet['reservedAdvancement'],sheet['investedAdvancement']),(18,2,0))
        self.reject('train-skill',characterId='founder',skillId='artifice');self.advance()
        self.act('cancel-training',characterId='founder');self.assertEqual(character_sheet(self.state,'founder')['availableAdvancement'],20)
        self.train('scholarship');sheet=character_sheet(self.state,'founder')
        self.assertEqual((sheet['availableAdvancement'],sheet['reservedAdvancement'],sheet['investedAdvancement']),(18,0,2))
    def test_training_pauses_maximum_is_two_and_units_are_personal(self):
        self.points();self.act('train-skill',characterId='founder',skillId='artifice');self.advance()
        self.act('assign-founder',assignment='rest');self.advance(2)
        self.assertEqual(self.state['characterSkills']['founder']['artifice'],0)
        self.act('assign-founder',assignment='training');self.advance();self.train('artifice')
        self.assertEqual(work_contribution(self.state,'founder','careful-assembly'),3)
        self.assertEqual(work_contribution(self.state,'mira','careful-assembly'),1)
        self.assertEqual(work_contribution(self.state,'founder','archive-focus'),1)
        self.reject('train-skill',characterId='founder',skillId='artifice')
    def test_research_bonus_does_not_accelerate_personal_learning(self):
        self.points();self.train('scholarship');self.train('scholarship')
        self.assertEqual(work_contribution(self.state,'founder','archive-focus'),3)
        self.act('start-research');self.advance();self.assertEqual(self.state['researchStatus'],'complete')
        self.act('train-skill',characterId='founder',skillId='fieldcraft');self.advance()
        self.assertEqual(self.state['trainingProjects']['founder']['completedWorkPhases'],1)
        self.assertEqual(self.state['characterSkills']['founder']['fieldcraft'],0)
    def test_mira_offers_fieldcraft_before_her_story_with_separate_investment(self):
        self.points('mira');self.assertIn('fieldcraft',character_sheet(self.state,'mira')['offeredSkills'])
        self.train('artifice','mira');self.assertEqual(self.state['characterSkills']['mira']['artifice'],1)
        self.train('fieldcraft','mira')
        self.assertEqual(character_sheet(self.state,'mira')['investedAdvancement'],4)
        self.assertEqual(character_sheet(self.state,'founder')['investedAdvancement'],0)
    def test_retraining_releases_skill_and_practice_points_preserving_history(self):
        self.points('mira');self.train('artifice','mira');learn_for_character(self.state,'mira','gentle-refraction')
        self.act('start-training',characterId='mira',practiceId='careful-assembly');self.advance(2)
        self.act('prepare-practice',characterId='mira',practiceId='careful-assembly',prepared=True)
        before=deepcopy(self.state['characterDevelopment']['mira']['advancementAwards'])
        self.act('start-retraining',characterId='mira');self.advance()
        sheet=character_sheet(self.state,'mira');self.assertEqual(sheet['investedAdvancement'],0)
        self.assertEqual(sheet['learnedPractices'],['archive-focus']);self.assertEqual(sheet['preparedPractices'],[])
        self.assertEqual(sheet['advancementAwards'],before);self.assertIn('gentle-refraction',sheet['knownPrinciples'])
    def test_fieldcraft_is_nonstacking_on_ordinary_surveys_and_unlocks_encounter_methods(self):
        self.points();self.train('fieldcraft');self.act('start-expedition');self.advance()
        self.act('choose-expedition-approach',approach='survey');self.assertEqual(self.state['expedition']['remainingWorkPhases'],1)
        self.act('return-expedition');self.advance();self.state['binderyDiscoveries']=['survey']
        self.act('start-expedition',siteId='rainward-observatory');self.advance();self.act('choose-expedition-approach',approach='survey')
        self.act('choose-encounter-method',methodId='trace-channels');self.advance()
        self.reject('choose-encounter-method',methodId='handle-lenses');self.act('return-expedition');self.advance()
        self.train('fieldcraft');self.act('start-expedition',siteId='rainward-observatory');self.advance();self.act('choose-expedition-approach',approach='survey')
        self.act('choose-encounter-method',methodId='handle-lenses');self.assertEqual(self.state['expedition']['remainingWorkPhases'],1)
    def test_away_planning_and_malformed_skill_are_rejected(self):
        self.points()
        for skill in (None,[],{},'unlimited-power'):self.reject('train-skill',characterId='founder',skillId=skill)
        self.act('start-expedition');self.reject('train-skill',characterId='founder',skillId='artifice')
        self.reject('train-skill',characterId='mira',skillId='artifice')

if __name__=='__main__':unittest.main()
