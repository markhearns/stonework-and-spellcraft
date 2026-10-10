"""Authoritative, dependency-free rules for the visual prototype.
All numerical balance in this module is provisional, not campaign canon.
"""
from resident_moments import MOMENTS
import summoning
import resident_projects
import companion_life
import character_builds
import castle_mystery
import containment
import estate_expansion
import personal_stories
import arrivals
import local_encounters
import equipment
import public_workshop
import public_progression
import public_fieldwork
import household_content
import character_pool
import headquarters
import house_shape
import room_to_grow
import keeping_hearth
import armoury
import arms_of_our_own
import provisions
import roads_we_keep
import first_patrol
import household_rest
import personal_paths
import resident_bonds
import foundation_chamber
import resident_friendships as friendship_milestones
from copy import deepcopy

CURRENT_SCHEMA_VERSION = 76

DAY_PHASES = ('morning', 'afternoon', 'evening')
ROOMS = {
    'common-room': {'name': 'Common room', 'purpose': 'Meet residents, share conversations and rest.', 'description': 'A fire burns in the hearth. Chairs and a shared table stand between the old stone walls, with space to put aside the day’s work.', 'furnishings': ['reading-table', 'velvet-settee', 'none']},
    'library': {'name': 'Library', 'purpose': 'Research principles, copy records for income and investigate castle history.', 'description': 'Reading lamps light the desks. Labelled shelves hold the household’s books, maps and research notes.', 'furnishings': ['brass-lamp', 'violet-lamp', 'none']},
    'bedchamber': {'name': 'Guest chamber', 'purpose': 'A quiet place of one’s own.', 'description': 'A small lamp warms the rough stone. Plain linen, a place for treasured things, and a door that closes.', 'furnishings': ['velvet-bench', 'oak-bench', 'none']},
}
ROOMS['conservatory'] = {'name': 'Conservatory', 'purpose': 'Assign garden work to harvest silver ivy or sell surplus produce.', 'description': 'Growing benches stand beneath the glass roof. Water channels run between the beds of silver ivy and kitchen plants.', 'furnishings': ['none']}
FURNISHING_NAMES = {'reading-table': 'Oak reading table', 'velvet-settee': 'Plum velvet settee', 'brass-lamp': 'Amber reading lamp', 'violet-lamp': 'Violet reading lamp', 'velvet-bench': 'Velvet bed-end bench', 'oak-bench': 'Carved oak bench', 'none': 'Leave open'}
ORIGINAL_ASSETS = {**{room: f'/assets/{room}.webp' for room in ROOMS}, 'founder': '/assets/placeholders/visitor-placeholder.svg', 'mira': '/assets/portraits/mira.webp'}

class RuleError(ValueError):
    pass

def new_campaign(start_type="demo"):
    state = {
        'schemaVersion': 1, 'campaignMode': 'solo', 'campaignName': 'A home in the old stones',
        'revision': 0, 'dayNumber': 1, 'currentDayPhase': 'afternoon',
        'selectedRoomId': 'common-room',
        'roomFurnishings': {'common-room': 'reading-table', 'library': 'brass-lamp', 'bedchamber': 'velvet-bench'},
        'wardrobe': {'ensembleName': 'The archivist', 'outerLayer': 'none'}, 'savedStyles': [],
        'sharedFunds': 80, 'researchCompletedPhases': 0, 'researchRequiredPhases': 3,
        'researchStatus': 'not-started', 'resonancePoints': 0,
        'completedDevelopments': [], 'invitationStatus': 'available',
        'relationshipDescription': 'New acquaintances, easy conversation',
        'assetOverrides': {}, 'assetHistory': {}, 'correctionRequests': [],
        'conversation': [],
        'journal': [{'dayNumber': 1, 'phase': 'afternoon', 'text': 'Demonstration campaign started with Mira already in the household.'}],
    }

    migrate_state(state)
    if start_type == "fresh":
        import solo_tools
        solo_tools.initialize_fresh(state)
    else:
        require(start_type == "demo", "Choose a fresh beginning or demonstration household.")
    return state

def add_journal(state, text):
    state['journal'].append({'dayNumber': state['dayNumber'], 'phase': state['currentDayPhase'], 'text': text})
    state['journal'] = state['journal'][-100:]

def resident_room(state):
    import room_life
    return room_life.location(state,'mira')

def resonance_forecast(state):
    # Warm furnishings alone do not create erotic resonance. The voluntarily
    # established playful atmosphere is a separate, lasting development.
    atmosphere_established = 'shared-flirtation' in state['completedDevelopments']
    tamsin=state.get('additionalResidents',{}).get('tamsin',{})
    contributors=int(atmosphere_established)+int(tamsin.get('status')=='resident' and tamsin.get('sharedFlirtation',False))
    import romance
    for who in household_members(state):
        already_counted=(who=='mira' and atmosphere_established) or (who=='tamsin' and tamsin.get('sharedFlirtation',False))
        if who!='founder' and not already_counted and romance.level(state,who)>=1:contributors+=1
    contributors=min(3,contributors)
    return contributors if state['roomFurnishings']['common-room'] == 'velvet-settee' else 0

def public_state(state):
    result = deepcopy(state)
    import companion_almanac
    result['companionAlmanacView']=companion_almanac.views(state)
    import companion_threads
    result['companionThreadsView']=companion_threads.views(state)
    import survey_rooms
    result['surveyRoomsView']=survey_rooms.view(state)
    import household_sagas
    result['householdSagasView']=household_sagas.views(state)
    import character_customization
    result['customizationView']=character_customization.view(state)
    import outfit_progression
    result['outfitProgressionView']=outfit_progression.view(state)
    import bathing_outfits
    result['bathingOutfitView']=bathing_outfits.view(state)
    import household_chapters, work_arrangements
    result['householdChaptersView']=household_chapters.view(state)
    import social_life
    result['socialLifeView']=social_life.view(state)
    import relationships
    result['relationshipsView']=relationships.view(state)
    result['residentBondsView']=resident_bonds.view(state)
    result['foundationChamberView']=foundation_chamber.view(state)
    result['residentFriendshipsView']=friendship_milestones.view(state)
    import character_quests
    result['characterQuestsView']=character_quests.view(state)
    import companion_goals
    result['companionGoalsView']=companion_goals.view(state)
    for quest in result.get('characterQuests',{}).get('records',{}).values():
        if quest.get('kind')=='ambition':
            for private_key in ('opening','middle','ending','flirt'):quest.pop(private_key,None)
    import romance
    result['romanceView']=romance.views(state)
    import lantern_adventure
    result['lanternAdventureView']=lantern_adventure.adventure_view(state)
    import party_journeys
    result['partyJourneysView']=party_journeys.views(state)
    result['departureParty']=party_journeys.departure(state)
    import companion_participation
    result['companionParticipationView']=companion_participation.view(state)
    result['workArrangementsView']=work_arrangements.view(state)
    import solo_life
    result['soloLifeView']=solo_life.view(state)
    result['headquartersView']=headquarters.view(state)
    import opening_guide
    result['openingGuide']=opening_guide.view(state)
    import first_hearth
    result['firstHearthView']=first_hearth.view(state)
    result['houseShapeView']=house_shape.view(state)
    result['roomToGrowView']=room_to_grow.view(state)
    result['keepingHearthView']=keeping_hearth.view(state)
    import castle_chapter, room_life
    result['castleChapterView']=castle_chapter.view(state)
    result['roomLifeView']=room_life.view(state)
    result['householdWorkView']=room_life.work_view(state)
    import living_stories, progression
    result['livingStoryView']=living_stories.rows(state)
    result['sharedReviewView']={'project':deepcopy(state['livingStories'].get('review')),'options':[{'personId':who,'name':character_profile(state,who)['name'],'blockers':living_stories.review_blockers(state,who)} for who in living_stories.CHAINS if who in household_members(state)]}
    import resident_specialties
    result['residentSpecialtyView']=resident_specialties.view(state)
    import guidance
    result['advancePreview']=guidance.preview(state)
    result['progressionView']=progression.view(state,result['advancePreview'])
    result['siteUnlockHints']={key:site_unlock_hint(key,state) for key in EXPEDITION_SITES}
    result.pop('privateCastleLore',None)
    result['localEncounterView']=local_encounters.view(state)
    result['arrivalPathViews']=arrivals.view(state)
    import recruitment_quests
    result['recruitmentView']=recruitment_quests.view(state)
    import world_recruitment
    result['worldRecruitmentView']=world_recruitment.view(state)
    result['worldRecruitment'].pop('seed',None)
    import chapel_spirit
    result['chapelSpiritView']=chapel_spirit.view(state)
    result['publicWorkshopView']=public_workshop.view(state)
    result['equipmentView']=equipment.view(state)
    result['armouryView']=armoury.view(state)
    result['armsOfOurOwnView']=arms_of_our_own.view(state)
    result['provisionsView']=provisions.view(state)
    result['roadsWeKeepView']=roads_we_keep.view(state)
    result['firstPatrolView']=first_patrol.view(state)
    result['fieldPatrolView']=field_patrols.view(state)
    import bestiary
    result['bestiaryView']=bestiary.view(state)
    import bounty_contracts
    result['bountyView']=bounty_contracts.view(state)
    result['eveningRestView']=household_rest.view(state)
    import daily_plan
    result['dailyPlanView']=daily_plan.view(state)
    import commissions,practical_projects,household_routines,shared_history,castle_reawakening
    result['commissionView']=commissions.view(state)
    result['practicalProjectView']=practical_projects.view(state)
    result['routineView']=household_routines.view(state)
    result['sharedHistoryView']=shared_history.view(state)
    result['castleReawakeningView']=castle_reawakening.view(state)
    result['personalPathsView']=personal_paths.view(state)
    import spell_guidance
    result['spellGuidance']={who:spell_guidance.view(state,who) for who in household_members(state)}
    result['householdContentView']=household_content.view(state)
    result['personalStoryView']=personal_stories.view(state)
    result['characterPool']=character_pool.catalogue()
    result['estateAnnexView']=estate_expansion.view(state)
    result['containmentView']=containment.view(state)
    result['castleMysteryView']=castle_mystery.view(state)
    result['expeditionWealthPlans']=deepcopy(EXPEDITION_WEALTH_PLANS)
    result['personalPurchaseCatalog']=deepcopy(PERSONAL_PURCHASES)
    result['castingPlanViews']={who:casting_plan_view(state,who) for who in household_members(state)}
    result['lessonOffers']={who:lesson_offers(state,who) for who in household_members(state)}
    result['lessonReadiness']={who:lesson_blockers(state,who) for who in household_members(state) if state['trainingProjects'][who] and state['trainingProjects'][who].get('teacherId')}
    result['personalRequestViews']={key:personal_request_view(state,key) for key in PERSONAL_REQUESTS}
    result['personalRequestCatalog']=deepcopy(PERSONAL_REQUESTS)
    result['residentRoomId'] = resident_room(state)
    result['resonancePerPhase'] = resonance_forecast(state)
    result['resonanceStage'] = 'Awakening' if state['resonancePoints'] >= 6 else ('Stirring' if state['resonancePoints'] else 'Quiet')
    result['rooms'] = ROOMS
    result['availableRoomIds'] = [room for room in ROOMS if room_available(state, room)]
    result['materialCatalog'] = MATERIALS
    result['recipeCatalog'] = RECIPES
    result['nextPhaseForecast'] = armoury.forecast(state)+house_shape.forecast(state)+phase_forecast(state)+summoning.forecast(state)+resident_projects.forecast(state)+companion_life.forecast(state)+castle_mystery.forecast(state)+containment.forecast(state)+estate_expansion.forecast(state)+personal_stories.forecast(state)+arrivals.forecast(state)+local_encounters.forecast(state)+public_workshop.forecast(state)+public_fieldwork.forecast(state)+field_patrols.forecast(state)
    result['summoningView'] = summoning.view(state)
    result['companionLifeViews'] = companion_life.views(state)
    result['ionaAtlasView'] = resident_projects.view(state)
    result['presentPeople'] = {who:deepcopy(character_profile(state,who)) for who in summoning.present_people(state)}
    result['residentMomentViews'] = {key:resident_moment_view(state,key) for key in MOMENTS}
    result['residentFriendships'] = resident_friendships(state)
    result['furnishingNames'] = FURNISHING_NAMES
    result['roomFurnishingViews'] = {room:room_furnishing_view(state,room) for room in ROOMS}
    result['roomDecorationCatalog'] = ROOM_DECORATION_CATALOG
    result['roomDecorationSlots'] = {room:decoration_slots(room) for room in ROOMS}
    result['originalAssets'] = {**ORIGINAL_ASSETS,**public_workshop.asset_slots(state),**{who:'/assets/placeholders/visitor-placeholder.svg' for who in state.get('reviewedCandidates',{}) if who not in ORIGINAL_ASSETS}}
    result['founderAtCastle'] = character_at_castle(state,'founder')
    result['expeditionSite'] = EXPEDITION_SITES[state['expedition']['siteId']] if state['expedition'] else EXPEDITION_SITE
    result['expeditionSites'] = EXPEDITION_SITES
    result['siteAccess'] = {site_id: site_available(state, site_id) for site_id in EXPEDITION_SITES}
    result['siteDiscoveries'] = {site_id: discoveries_for(state, site_id) for site_id in EXPEDITION_SITES}
    result['facilityCatalog'] = FACILITIES
    result['livingWingRequirements'] = living_wing_requirements(state)
    result['principleGuide'] = deepcopy(PRINCIPLE_GUIDE)
    if state.get('startType')=='fresh':
        result['principleGuide']['reference-binding'].update(source='Research Arrange the first archive after understanding the hearth wards.',view='research')
        result['principleGuide']['courteous-passage'].update(source='Install a living index charm, then study Courteous passage with its required knowledge.',view='research')
    result['householdNextSteps'] = household_next_steps(state)
    result['gardenYield'] = garden_yield(state)
    result['principleNames'] = PRINCIPLE_NAMES
    result['residentAtCastle'] = character_at_castle(state, 'mira')
    result['characterCatalog'] = {key:deepcopy(character_profile(state,key)) for key in household_members(state)}
    result['arrivalReservationViews'] = arrival_reservation_views(state)
    result['candidateView'] = candidate_view(state)
    result['roomOccupants'] = {room:[who for who in summoning.present_people(state) if who!='founder' and household_resident_room(state,who)==room] for room in ROOMS}
    result['augmentationViews']={who:augmentation_view(state,who) for who in household_members(state)}
    result['practiceCatalog'] = PRACTICES
    result['practiceRequirementViews']={who:{key:practice_requirements(state,who,key) for key in PRACTICES} for who in household_members(state)}
    result['workContributionViews']={who:{kind:work_contribution_parts(state,who,kind) for kind in ('archive-focus','careful-assembly')} for who in household_members(state)}
    result['preparationSetViews']={who:{name:preparation_set_blockers(state,who,items) for name,items in state['practicePreparationSets'][who].items()} for who in household_members(state)}
    result['characterBuildViews'] = {who:character_builds.view(state,who) for who in household_members(state)}
    result['skillCatalog'] = CHARACTER_SKILLS
    result['characterSheets'] = {key: character_sheet(state, key) for key in household_members(state)}
    result['archiveProjectWorkPerPhase'] = archive_project_work(state)
    result['craftingWorkPerPhase'] = crafting_work(state)
    result['copyingIncomePerPhase'] = copying_income(state)
    result['researchCatalog'] = {k:v for k,v in RESEARCH_CATALOG.items() if k!='archive-foundations' or state.get('startType')=='fresh'}
    result['hasActiveResearch'] = state['researchStatus'] == 'in-progress' or state['activeResearchId'] is not None
    result['utilityArtifactCatalog'] = UTILITY_ARTIFACTS
    result['gardenForecast'] = garden_harvest(state)
    result['principleStudyPhases'] = principle_study_phases(state)
    result['workOrderViews'] = [work_order_view(state, order) for order in state['workOrders']]
    result['researchReadiness'] = {key: {who: research_blockers(state, key, who) for who in household_members(state)} for key in RESEARCH_CATALOG}
    result['neighbourRequests'] = {key: neighbour_request_view(state, key) for key in NEIGHBOUR_REQUESTS}
    result['neighbourRequestCatalog'] = NEIGHBOUR_REQUESTS
    result['householdInvitations'] = household_invitations(state)
    result['spareArtifacts'] = {key: spare_artifact_count(state, key) for key in RECIPES}
    result['focusInscriptionCatalog'] = FOCUS_INSCRIPTIONS
    result['focusViews'] = {key: focus_view(state, key) for key in household_members(state)}
    import scripted_companions
    result['scriptedCompanionsView']=scripted_companions.view(state)
    import ancestry_traits
    result['ancestryTraits'] = {who:ancestry_traits.for_person(state,who) for who in household_members(state)}
    result['housingCatalog'] = HOUSING_ROOMS
    result['housingSummary'] = housing_summary(state)
    result['encounterView'] = encounter_view(state)
    result['spellForms'] = SPELL_FORMS
    result['spellSupportView'] = spell_support.view(state)
    result['magicOpportunities'] = spell_support.opportunities(state)
    result['fieldMagicView'] = field_magic.view(state)
    result['lastingRitualsView'] = lasting_rituals.view(state)
    import magic_reference
    result['magicReferenceView'] = magic_reference.view(state)
    result['materialPurchasePrices'] = {k:d['price'] for k,d in MATERIALS.items()}
    result['spellViews'] = [spell_view(state, spell) for spell in state['spellbook']]
    result['spellPreparationCapacity'] = spell_preparation_capacity(state)
    result['spellPreparationCapacities'] = {who:spell_preparation_capacity(state,who) for who in household_members(state)}
    result['spellRitualBlockers'] = spell_ritual_blockers(state)
    import phase_tasks
    result['phaseTasks']=phase_tasks.build(state)
    import guidance
    import cheat_tools
    result['cheatsView']=cheat_tools.view(state) if state['testing']['enabled'] else None
    result['goalViews']=guidance.goals(state)
    import expedition_loop
    expedition_loop.encounter_details(state,result['encounterView'])
    result['expeditionPreparation']=expedition_loop.preparation(state)
    result['expeditionFollowups']=expedition_loop.followups(state,result)
    return result

def require(condition, message):
    if not condition:
        raise RuleError(message)

def text_value(value, maximum=600):
    require(isinstance(value, str) and 0 < len(value.strip()) <= maximum, f'Enter between 1 and {maximum} characters.')
    return value.strip()

def _apply_action_legacy(state, action):
    kind = action.get('type')
    import daily_plan
    if daily_plan.apply(state,action):return
    if keeping_hearth.apply(state,action):return
    if room_to_grow.apply(state,action):return
    if house_shape.apply(state,action):return
    import companion_almanac
    if companion_almanac.apply(state,action):return
    import household_sagas
    if household_sagas.apply(state,action):return
    import character_customization
    if character_customization.apply(state,action):return
    if field_magic.apply(state,action) or lasting_rituals.apply(state,action):return
    import household_chapters, work_arrangements
    if household_chapters.apply(state,action) or work_arrangements.apply(state,action):return
    import outfit_progression
    if outfit_progression.apply(state,action):return
    import castle_chapter
    if castle_chapter.apply(state,action):return
    import living_stories, service_road, progression
    if living_stories.apply(state,action) or living_stories.apply_review(state,action) or service_road.apply(state,action) or progression.apply(state,action):return
    import solo_tools, solo_life, phase_tasks, guidance
    if guidance.apply(state,action):return
    import first_hearth
    if first_hearth.apply(state,action):return
    import social_life
    if social_life.apply(state,action):return
    import relationships
    if relationships.apply(state,action):return
    import character_quests
    if character_quests.apply(state,action):return
    import companion_goals
    if companion_goals.apply(state,action):return
    import romance
    if romance.apply(state,action):return
    import party_journeys
    if party_journeys.apply(state,action):return
    import lantern_adventure
    if lantern_adventure.apply(state,action):return
    import beacon_expedition, companion_participation
    if beacon_expedition.apply(state,action) or companion_participation.apply(state,action):return
    if phase_tasks.apply(state,action):return
    import founder_setup
    if headquarters.apply(state, action):return
    if founder_setup.apply(state, action):return
    if solo_life.apply(state, action):return
    if solo_tools.apply(state, action):
        return
    if (state['expedition'] is not None or state.get('publicWorkshop',{}).get('fieldTrip') or field_patrols.away(state,'founder')) and kind in ('start-research', 'start-restoration', 'start-crafting', 'assign-founder', 'start-facility', 'assign-facility', 'place-household-artifact', 'celebrate-living-wing', 'accept-invitation', 'talk', 'free-text'):
        raise RuleError('Your scholar is away. Return to the castle before taking this in-person action.')
    if kind in ('accept-invitation', 'talk', 'free-text', 'celebrate-living-wing', 'start-archive-project', 'finish-archive-story'):
        require(character_at_castle(state, 'mira'), 'Mira must be present for this interaction.')
    if kind == 'rename-campaign':
        state['campaignName'] = text_value(action.get('name'), 70)
    elif kind == 'select-room':
        room = action.get('roomId')
        require(room_available(state, room), 'Restore this room before entering it.')
        state['selectedRoomId'] = room
    elif kind == 'decorate':
        room = action.get('roomId')
        require(room_available(state, room) and action.get('furnishing') in ROOMS[room]['furnishings'], 'Unsupported furnishing for this slot.')
        state['roomFurnishings'][room] = action['furnishing']
    elif public_workshop.apply(state,action):
        pass
    elif equipment.apply(state,action):
        pass
    elif household_content.apply(state,action):
        pass
    elif local_encounters.apply(state,action):
        pass
    elif arrivals.apply(state,action):
        pass
    elif personal_stories.apply(state,action):
        pass
    elif estate_expansion.apply(state,action):
        pass
    elif containment.apply(state,action):
        pass
    elif castle_mystery.apply(state,action):
        pass
    elif companion_life.apply(state,action):
        pass
    elif resident_projects.apply(state,action):
        pass
    elif summoning.apply(state,action):
        pass
    elif apply_room_arrangement_action(state,action):
        pass
    elif kind == 'wardrobe':
        require(action.get('outerLayer') in ('none', 'plum-shawl'), 'Unsupported garment component.')
        state['wardrobe']['outerLayer'] = action['outerLayer']
        import outfit_progression
        outfit_progression.clear_selection(state,'mira')
        import character_customization
        character_customization.clear_style(state,'mira')
        state.get('residentCurrentStyles',{}).pop('mira',None)
    elif kind == 'save-style':
        name = text_value(action.get('name'), 40)
        existing = next((style for style in state['savedStyles'] if style['name'] == name), None)
        require(existing is not None or len(state['savedStyles']) < 8, 'Eight saved styles are available in this prototype.')
        if existing:
            existing['outerLayer'] = state['wardrobe']['outerLayer']
        else:
            state['savedStyles'].append({'name': name, 'outerLayer': state['wardrobe']['outerLayer']})
    elif kind == 'wear-style':
        style = next((style for style in state['savedStyles'] if style['name'] == action.get('name')), None)
        require(style is not None, 'Saved style not found.')
        state['wardrobe']['outerLayer'] = style['outerLayer']
        import outfit_progression
        outfit_progression.clear_selection(state,'mira')
        import character_customization
        character_customization.clear_style(state,'mira')
        state.get('residentCurrentStyles',{}).pop('mira',None)
    elif kind == 'start-research':
        require(state['researchStatus'] == 'not-started', 'This project has already been started.')
        require(state['sharedFunds'] >= 20, 'This project needs 20 shared crowns.')
        state['sharedFunds'] -= 20
        state['researchStatus'] = 'in-progress'
        state['founderAssignment'] = 'research'
        add_journal(state, 'Committed 20 crowns to studying the hearth wards. Work resolves over three phases.')
    elif kind == 'advance':
        known_projects=guidance.projects(state)
        previous_tasks={t['id'] for t in phase_tasks.build(state)['tasks']}
        require(not state['expedition'] or state['expedition']['stage'] not in ('awaiting-choice','encounter-choice'), 'Choose an expedition approach or begin the return journey before advancing.')
        resolve_delegated_order(state)
        begin_planned_castings(state)
        resolve_work(state)
        resolve_expedition(state)
        resolve_resident_arrivals(state)
        summoning.resolve_visits(state)
        resolve_allowances(state)
        daily_plan.resolve(state)
        check_living_wing_milestone(state)
        state['soloLife']['lastCompletions']=[p for p in guidance.changes(known_projects,state) if p['completes']]
        previous_points = state['resonancePoints']
        gain = resonance_forecast(state)
        state['resonancePoints'] += gain
        if gain:
            state['lastPhaseSummary'].append(f'Resonance +{gain}: the established sensual atmosphere endures.')
        if previous_points < 6 <= state['resonancePoints']:
            add_journal(state, 'Resonance awakened the violet hearthlight: a cosmetic glow in the common room.')
        phase_index = DAY_PHASES.index(state['currentDayPhase'])
        state['currentDayPhase'] = DAY_PHASES[(phase_index + 1) % 3]
        if phase_index == 2:
            state['dayNumber'] += 1
        foundation_chamber.after_advance(state)
        add_journal(state, 'The household settles into ' + state['currentDayPhase'] + '.')
        state['soloLife']['phaseNotice']={'phase':phase_tasks.phase_key(state),'newIds':[t['id'] for t in phase_tasks.build(state)['tasks'] if t['id'] not in previous_tasks]}
    elif kind == 'accept-invitation':
        require(state['invitationStatus'] == 'available', 'This invitation has already been enjoyed.')
        state['invitationStatus'] = 'completed'
        state['completedDevelopments'].append('shared-flirtation')
        state['relationshipDescription'] = 'Comfortable with a little mutual flirtation'
        state['resonancePoints'] += 2
        state['conversation'].append({'speaker': 'Mira', 'text': '“There. Tea, a warm hearth, and excellent company.” She moves her book aside with a smile. “I was hoping you would take the hint.”'})
        add_journal(state, 'Shared a playful invitation with Mira. An enduring flirtatious atmosphere begins; Resonance +2, once only.')
    elif kind == 'talk':
        topic = action.get('topic')
        lines = {
            'home': ('How are you settling in?', '“Rather well. The shelves are wonky, the cushions are excellent, and nobody has asked me to alphabetize a ghost. Yet.”'),
            'research': ('What are you working on?', '“The hearth wards. Ordinary comfort is an underrated kind of magic. I want to understand how this place keeps its warmth.”'),
            'flirt': ('You make this room rather distracting.', '“How inconvenient for your scholarship.” Her smile lingers. “Perhaps you ought to put the book down.”'),
        }
        require(topic in lines, 'Choose one of the available scripted topics.')
        question, answer = lines[topic]
        state['conversation'].extend([{'speaker': 'You', 'text': question}, {'speaker': 'Mira', 'text': answer}])
    elif kind == 'free-text':
        message = text_value(action.get('text'))
        state['conversation'].extend([{'speaker': 'You', 'text': message}, {'speaker': 'Prototype', 'text': 'Your line has been saved without generation. Use the separate NPC draft controls to request and review a generated reply, or choose a scripted topic.'}])
    elif kind == 'request-correction':
        asset = action.get('assetId')
        require(asset in ORIGINAL_ASSETS or asset in state.get('reviewedCandidates',{}) or asset in public_workshop.asset_slots(state), 'Unknown illustration.')
        require(len(state['correctionRequests']) < 50, 'The prototype correction queue is full.')
        state['correctionRequests'].append({'assetId': asset, 'note': text_value(action.get('note')), 'status': 'awaiting-external-artwork'})
    elif kind == 'accept-artwork':
        asset, path = action.get('assetId'), action.get('assetPath')
        require(asset in ORIGINAL_ASSETS or asset in state.get('reviewedCandidates',{}) or asset in public_workshop.asset_slots(state), 'Unknown illustration.')
        # Server separately verifies this path belongs to an uploaded asset.
        require(isinstance(path, str) and path.startswith('/user-assets/'), 'Upload the proposed artwork first.')
        history = state['assetHistory'].setdefault(asset, [])
        history.append(state['assetOverrides'].get(asset, ORIGINAL_ASSETS.get(asset,public_workshop.asset_slots(state).get(asset,'/assets/placeholders/visitor-placeholder.svg'))))
        state['assetOverrides'][asset] = path
    elif kind == 'rollback-artwork':
        asset = action.get('assetId')
        history = state['assetHistory'].get(asset, [])
        require(len(history) > 0, 'There is no previous accepted version.')
        state['assetOverrides'][asset] = history.pop()
    elif __import__('scripted_companions').apply(state,action):
        pass
    elif character_builds.apply_action(state,action):
        pass
    elif apply_augmentation_action(state,action):
        pass
    elif apply_preparation_set_action(state,action):
        pass
    elif apply_resident_moment_action(state,action):
        pass
    elif apply_personal_request_action(state, action):
        pass
    elif apply_casting_plan_action(state, action):
        pass
    elif apply_lesson_action(state, action):
        pass
    elif apply_delegation_action(state, action):
        pass
    elif apply_finance_action(state, action):
        pass
    elif apply_recruitment_action(state, action):
        pass
    elif apply_encounter_action(state, action):
        pass
    elif apply_expedition_action(state, action):
        pass
    elif apply_spell_action(state, action):
        pass
    elif apply_housing_action(state, action):
        pass
    elif apply_focus_action(state, action):
        pass
    elif apply_neighbour_action(state, action):
        pass
    elif apply_planning_action(state, action):
        pass
    elif apply_development_action(state, action):
        pass
    elif apply_household_action(state, action):
        pass
    elif apply_management_action(state, action):
        pass
    else:
        raise RuleError('Unknown action.')
    if state['miraArchiveProject']['status'] == 'complete':
        state['relationshipDescription'] = 'Trusted collaborators, with an easy mutual flirtation' if 'shared-flirtation' in state['completedDevelopments'] else 'Trusted collaborators in a home made together'
    state['conversation'] = state['conversation'][-60:]
    return state


# Expansion 0.2: explicit assignments, restoration, production, and components.
MATERIALS = {
    'sun-amber': {'name': 'Sun amber', 'properties': ['heat-bearing'], 'price': 6},
    'fireglass': {'name': 'Fireglass', 'properties': ['heat-bearing'], 'price': 9},
    'binding-thread': {'name': 'Binding thread', 'properties': ['binding'], 'price': 3},
    'silver-ivy': {'name': 'Silver ivy', 'properties': ['binding', 'botanical'], 'price': 4},
}
RECIPES = {
    'warming-lantern': {'name': 'Warming lantern', 'requiredPrinciple': 'steady-hearth-wards',
        'requiredProperties': ['heat-bearing', 'binding'], 'requiredWorkPhases': 2,
        'description': 'A reusable lantern that gives gentle warmth without an open flame. Its visible glow can be placed in the common room.'},
}

def migrate_state(state):
    version = state.get('schemaVersion', 1)
    if version > CURRENT_SCHEMA_VERSION:
        raise RuleError('This save is newer than this application. Use a compatible release.')
    if version == 1:
        state.update({
            'schemaVersion': 2,
            'founderAssignment': 'research' if state['researchStatus'] == 'in-progress' else 'rest',
            'residentAssignment': 'rest',
            'restorationStatus': 'not-started', 'restorationCompletedPhases': 0,
            'restorationRequiredPhases': 3, 'gardenProductionChoice': 'silver-ivy',
            'materialInventory': {'sun-amber': 2, 'fireglass': 0, 'binding-thread': 2, 'silver-ivy': 0},
            'craftingProject': None, 'craftedArtifacts': {}, 'lanternDisplayed': False,
            'lastPhaseSummary': [],
        })
        state['roomFurnishings']['conservatory'] = 'none'
    if state['schemaVersion'] == 2:
        state['schemaVersion'] = 3
        state['expedition'] = None
        state['waterworksDiscoveries'] = []
        state['lastExpeditionReport'] = None
        known = ['steady-hearth-wards'] if state['researchStatus'] == 'complete' else []
        state['founderKnownPrinciples'] = known.copy()
        state['archivePrinciples'] = known.copy()
        state['wateringCharmInstalled'] = False
        state['materialInventory']['porous-clay'] = 0
    if state['schemaVersion'] == 3:
        state['schemaVersion'] = 4
        state['waystationDiscoveries'] = []
        state['facilityProjects'] = {key: {'status': 'not-started', 'completedWorkPhases': 0} for key in FACILITIES}
        state['activeFacilityId'] = None
        state['householdArtifactPlacements'] = {'hearth-kettle': False, 'pantry-seal': False}
        state['livingWingCompletedOn'] = None
        state['livingWingCelebration'] = 'unavailable'
    if state['schemaVersion'] == 4:
        initialize_development(state)
        state['schemaVersion'] = 5
    if state['schemaVersion'] == 5:
        state['researchProjects'] = {key: {'status':'not-started', 'completedWorkPhases':0, 'contributors':[]} for key in RESEARCH_CATALOG}
        state['activeResearchId'] = None
        state['utilityArtifactPlacements'] = {key: False for key in UTILITY_ARTIFACTS}
        state['materialReserveTargets'] = {key: 0 for key in MATERIALS}
        state['workOrders'] = []
        state['nextWorkOrderNumber'] = 1
        state['schemaVersion'] = 6
    if state['schemaVersion'] == 6:
        state['neighbourRequestProgress'] = {key: {'status': 'offered', 'deliveredOn': None} for key in NEIGHBOUR_REQUESTS}
        state['nurseryDiscoveries'] = []
        state['completedHouseholdScenes'] = []
        state['utilityArtifactPlacements'].setdefault('capillary-mat', False)
        state['schemaVersion'] = 7
    if state['schemaVersion'] == 7:
        state['signatureFocuses'] = {key: {'name': 'Ash staff' if key == 'founder' else 'Archive clasp', 'capacity':1,
            'inscriptions':[], 'householdLoadout':[], 'expeditionLoadout':[]} for key in CHARACTERS}
        state['focusProjects'] = {key:None for key in CHARACTERS}
        state['schemaVersion'] = 8
    if state['schemaVersion'] == 8:
        state['housingRooms'] = {key:{'status':'complete' if key=='bedchamber' else 'not-started', 'completedWorkPhases':0, 'reservedBeds':0} for key in HOUSING_ROOMS}
        state['bedroomAssignments'] = {'founder':'bedchamber','mira':'bedchamber'}
        state['activeHousingRoomId'] = None
        for key in ('west-chamber','garden-chamber'): state['roomFurnishings'][key]='oak-bench'
        state['schemaVersion'] = 9
    if state['schemaVersion'] == 9:
        state['spellbook'] = []
        state['nextSpellNumber'] = 1
        state['preparedSpells'] = {key:[] for key in CHARACTERS}
        state['spellWork'] = {key:None for key in CHARACTERS}
        state['spellRitual'] = {'status':'not-started', 'contributions':{key:0 for key in RITUAL_PARTICIPANTS}}
        state['schemaVersion'] = 10
    if state['schemaVersion'] == 10:
        state['characterSkills'] = {who:{key:0 for key in CHARACTER_SKILLS} for who in CHARACTERS}
        state['observatoryDiscoveries'] = []
        state['observatoryProgress'] = {key:{'completedSteps':[], 'pendingWork':None, 'complication':None, 'bonusMoonGlass':0} for key in ('survey','salvage')}
        state['utilityArtifactPlacements'].setdefault('reading-prism', False)
        state['schemaVersion'] = 11
    if state['schemaVersion'] == 11:
        initialize_recruitment(state)
        state['schemaVersion'] = 12
    if state['schemaVersion'] == 12:
        state['personalFunds']={who:0 for who in CHARACTERS}
        state['personalPossessions']={who:[] for who in CHARACTERS}
        state['householdAllowancePlan']={'dailyCrowns':{who:0 for who in CHARACTERS},'minimumTreasuryCrowns':20}
        state['expeditionWealthPlan']='shared'
        state['moneyJournal']=[]
        if state['expedition']:state['expedition']['wealthPlan']='shared'
        state['schemaVersion']=13
    if state['schemaVersion']==13:
        for order in state['workOrders']:order['delegation']=None
        state['schemaVersion']=14
    if state['schemaVersion']==14:
        state['lessonHistory']=[]
        state['castingPlans']={who:None for who in CHARACTERS}
        state['schemaVersion']=15
    if state['schemaVersion']==15:
        state['personalRequests']={key:{'status':'offered','completedWorkPhases':0,'fundingSource':None,'noteRead':False} for key in PERSONAL_REQUESTS}
        state['residentKeepsakes']={who:[] for who in CHARACTERS}
        state['displayedKeepsakes']={who:[] for who in CHARACTERS}
        state['schemaVersion']=16
    if state['schemaVersion']==16:
        state['roomDecorations']={room:{slot:'none' for slot in decoration_slots(room)} for room in ROOMS}
        state['savedRoomArrangements']={room:{} for room in ROOMS}
        state['schemaVersion']=17
    if state['schemaVersion']==17:
        state['residentMoments']={key:{'status':'waiting','completedOn':None} for key in MOMENTS}
        state['schemaVersion']=18
    if state['schemaVersion']==18:
        state['practicePreparationSets']={who:{} for who in CHARACTERS}
        state['personalAugmentations']={who:{'active':False,'project':None} for who in CHARACTERS}
        state['schemaVersion']=19
    if state['schemaVersion']==19:
        initialize_person_registry(state)
        state['schemaVersion']=20
    if state['schemaVersion']==20:
        summoning.initialize(state)
        state['schemaVersion']=21
    if state['schemaVersion']==21:
        resident_projects.initialize(state)
        for key in PERSONAL_REQUESTS:state['personalRequests'].setdefault(key,{'status':'offered','completedWorkPhases':0,'fundingSource':None,'noteRead':False})
        for key in MOMENTS:state['residentMoments'].setdefault(key,{'status':'waiting','completedOn':None})
        state['schemaVersion']=22
    if state['schemaVersion']==22:
        for who, age, ancestry in [('mira',22,'Human'),('tamsin',20,'Catfolk'),('iona',23,'Demon')]:
            if who not in state['people']:continue
            person=state['people'][who]
            if person.get('adultAgeYears')==age and person.get('ancestryLabel')==ancestry:continue
            person.setdefault('identityHistory',[]).append({key:deepcopy(person.get(key)) for key in ('adultAgeYears','ancestryLabel','role','identityRevision')})
            person.update(adultAgeYears=age, ancestryLabel=ancestry, lifeStage='adult',
                role=summoning.PROFILE['role'] if who=='iona' else CHARACTERS[who]['role'],
                identityRevision=person.get('identityRevision',1)+1)
            if who=='iona':person['origin']=summoning.PROFILE['origin']
        for asset in ('mira','mira-shawl','tamsin','tamsin-shawl','iona'):
            previous=state['assetOverrides'].pop(asset,None)
            if previous:state['assetHistory'].setdefault(asset,[]).append(previous)
        state['schemaVersion']=23
    if state['schemaVersion']==23:
        companion_life.initialize(state)
        for key in MOMENTS:state['residentMoments'].setdefault(key,{'status':'waiting','completedOn':None})
        state['schemaVersion']=24
    if state['schemaVersion']==24:
        state.setdefault('reviewedCandidates',{})
        state['schemaVersion']=25
    if state['schemaVersion']==25:
        character_builds.initialize(state)
        state['schemaVersion']=26
    if state['schemaVersion']==26:
        castle_mystery.initialize(state)
        state['schemaVersion']=27
    if state['schemaVersion']==27:
        containment.initialize(state)
        state['schemaVersion']=28
    if state['schemaVersion']==28:
        estate_expansion.initialize(state)
        state['schemaVersion']=29
    if state['schemaVersion']==29:
        character_pool.migrate_ancestry_names(state)
        personal_stories.initialize(state)
        arrivals.initialize(state)
        state['schemaVersion']=30
    if state['schemaVersion']==30:
        local_encounters.initialize(state)
        state['schemaVersion']=31
    if state['schemaVersion']==31:
        state['activeContentPack']=None
        state['schemaVersion']=32
    if state['schemaVersion']==32:
        household_content.initialize(state)
        state['schemaVersion']=33
    if state['schemaVersion']==33:
        equipment.initialize(state)
        state['schemaVersion']=34
    if state['schemaVersion']==34:
        equipment.initialize(state)
        state['schemaVersion']=35
    if state['schemaVersion']==35:
        public_workshop.initialize(state)
        state['schemaVersion']=36
    if state['schemaVersion']==36:
        import public_journeys
        public_journeys.initialize(state)
        state['schemaVersion']=37
    if state['schemaVersion']==37:
        state.setdefault('startType','demo')
        state.setdefault('testing',{'enabled':False,'used':False,'nextNumber':1,'history':[]})
        state['researchProjects'].setdefault('archive-foundations',{'status':'not-started','completedWorkPhases':0,'contributors':[]})
        state['schemaVersion']=38
    if state['schemaVersion']==38:
        import solo_life
        solo_life.initialize(state)
        state['schemaVersion']=39
    if state['schemaVersion']==39:
        headquarters.initialize(state)
        for key in headquarters.BEDROOMS:
            state['housingRooms'].setdefault(key,{'status':'not-started','completedWorkPhases':0,'reservedBeds':0})
            state['roomFurnishings'].setdefault(key,'oak-bench')
            state['roomDecorations'].setdefault(key,{slot:'none' for slot in decoration_slots(key)})
            state['savedRoomArrangements'].setdefault(key,{})
        state['schemaVersion']=40
    if state['schemaVersion']==40:
        import castle_chapter
        castle_chapter.initialize(state)
        state['schemaVersion']=41
    if state['schemaVersion']==41:
        import living_stories, service_road
        living_stories.initialize(state)
        service_road.initialize(state)
        state['schemaVersion']=42
    if state['schemaVersion']==42:
        resident_specialties.initialize(state)
        state['schemaVersion']=43
    if state['schemaVersion']==43:
        local_encounters.revise_nyssara(state)
        local_encounters.revise_sylva(state)
        state['schemaVersion']=44
    if state['schemaVersion']==44:
        import outfit_progression
        outfit_progression.initialize(state)
        state['schemaVersion']=45
    if state['schemaVersion']==45:
        import household_chapters, work_arrangements
        household_chapters.initialize(state)
        work_arrangements.initialize(state)
        state['schemaVersion']=46
    if state['schemaVersion']==46:
        import field_magic, lasting_rituals
        field_magic.initialize(state)
        lasting_rituals.initialize(state)
        state.setdefault('spellSupports',{})
        state['schemaVersion']=47
    if state['schemaVersion']==47:
        import social_life
        social_life.initialize(state)
        state['schemaVersion']=48
    if state['schemaVersion']==48:
        character_builds.migrate(state)
        state['schemaVersion']=49
    if state['schemaVersion']==49:
        import beacon_expedition, companion_participation
        beacon_expedition.initialize(state)
        companion_participation.initialize(state)
        state['schemaVersion']=50
    if state['schemaVersion']==50:
        import relationships
        relationships.initialize(state)
        state['schemaVersion']=51
    if state['schemaVersion']==51:
        import character_quests
        character_quests.initialize(state)
        state['schemaVersion']=52
    if state['schemaVersion']==52:
        import romance
        romance.initialize(state)
        state['schemaVersion']=53
    if state['schemaVersion']==53:
        import lantern_adventure
        lantern_adventure.initialize(state)
        state['schemaVersion']=54
    if state['schemaVersion']==54:
        import character_customization
        character_customization.initialize(state)
        state['schemaVersion']=55
    if state['schemaVersion']==55:
        import household_sagas
        household_sagas.initialize(state)
        state['schemaVersion']=56
    if state['schemaVersion']==56:
        import party_journeys
        party_journeys.initialize(state)
        state['schemaVersion']=57
    if state['schemaVersion']==57:
        import companion_almanac
        companion_almanac.initialize(state)
        state['schemaVersion']=58
    if state['schemaVersion']==58:
        headquarters.initialize(state)
        state['schemaVersion']=59
    if state['schemaVersion']==59:
        armoury.initialize(state)
        arms_of_our_own.initialize(state)
        state['schemaVersion']=60
    if state['schemaVersion']==60:
        provisions.initialize(state)
        roads_we_keep.initialize(state)
        state['localEncounters'].setdefault('velis',{'status':'available','completedOn':None})
        state['schemaVersion']=61
    if state['schemaVersion']==61:
        first_patrol.initialize(state)
        state['schemaVersion']=62
    if state['schemaVersion']==62:
        # Talent records are lazy; the version gate protects in-flight training
        # from older executables that do not recognize the new project kinds.
        state['schemaVersion']=63
    if state['schemaVersion']==63:
        # New named talents and complete build snapshots require this engine.
        state['schemaVersion']=64
    if state['schemaVersion']==64:
        import companion_identity
        companion_identity.migrate(state)
        state['schemaVersion']=65
    if state['schemaVersion']==65:
        # New patrol creature IDs require an engine that knows the shared catalogue.
        # Bestiary records are lazy, preserving all existing campaign fields.
        import bounty_contracts
        bounty_contracts.initialize(state)
        state['schemaVersion']=66
    if state['schemaVersion']==66:
        # Six new encounters and their materials must not be opened by older engines.
        # Preserve existing stock, reserves, field records and active expeditions.
        import bounty_contracts
        bounty_contracts.initialize(state)
        state['schemaVersion']=67
    if state['schemaVersion']==67:
        resident_bonds.initialize(state)
        state['schemaVersion']=68
    if state['schemaVersion']==68:
        foundation_chamber.initialize(state)
        state['schemaVersion']=69
    if state['schemaVersion']==69:
        friendship_milestones.initialize(state)
        state['schemaVersion']=70
    if state['schemaVersion']==70:
        import companion_threads
        companion_threads.initialize(state)
        state['schemaVersion']=71
    if state['schemaVersion']==71:
        import survey_rooms
        survey_rooms.initialize(state)
        state['schemaVersion']=72
    if state['schemaVersion']==72:
        import release_v116_migration
        release_v116_migration.migrate(state)
        state['schemaVersion']=73
    if state['schemaVersion']==73:
        import bounty_contracts
        bounty_contracts.initialize(state)
        import recruitment_quests
        recruitment_quests.initialize(state)
        state['schemaVersion']=74
    if state['schemaVersion']==74:
        import world_recruitment
        world_recruitment.initialize(state)
        import chapel_spirit
        chapel_spirit.initialize(state)
        state['schemaVersion']=75
    if state['schemaVersion']==75:
        import companion_goals
        companion_goals.initialize(state)
        state['schemaVersion']=76
    return state

def room_available(state, room):
    if room in HOUSING_ROOMS and room!='bedchamber':
        return state.get('housingRooms', {}).get(room, {}).get('status') == 'complete'
    return room in ROOMS and (room != 'conservatory' or state.get('restorationStatus') == 'complete')

def phase_forecast(state):
    rows = headquarters.forecast(state)
    if state.get('worldRecruitment',{}).get('report'):
        rows.append('Local recruitment reports: one phase remaining.' if state['founderAssignment']=='local-reports' else 'Local recruitment reports are paused; resume them on the recruitment board.')
    rows.extend(foundation_chamber.forecast(state))
    import survey_rooms
    rows.extend(survey_rooms.forecast(state))
    rows.extend(friendship_milestones.forecast(state))
    review=state.get('livingStories',{}).get('review')
    if review:
        party=['founder',review['personId']]
        working=review['personId'] in household_members(state) and all(character_at_castle(state,p) and character_assignment(state,p)=='shared-review' for p in party)
        rows.append('Shared research-note review: '+('completes this phase; held assignments resume next phase.' if working else 'paused; return together and resume from Resident stories.'))
    for who in household_members(state):
        view=augmentation_view(state,who)
        if view['project']:rows.append(character_profile(state,who)['name']+' · '+view['project']['kind']+' Lamplit sight: '+(' '.join(view['workBlockers']) if view['workBlockers'] else '+1 ritual phase.'))
    if state['expedition']:
        rows.append(expedition_forecast(state))
    if state['researchStatus'] == 'in-progress':
        work = research_work(state)
        if work:
            rows.append(f"Hearth-ward research: +{min(work, state['researchRequiredPhases'] - state['researchCompletedPhases'])} work phase(s).")
        else:
            rows.append('Research paused: nobody is assigned to it.')
    if state['restorationStatus'] == 'in-progress':
        rows.append('Conservatory restoration: +'+str(character_approaches.work_step(state,'founder','restoration',state['restorationCompletedPhases'],state['restorationRequiredPhases']))+' work phase(s).' if state['founderAssignment'] == 'restoration' else 'Restoration paused: your scholar is assigned elsewhere.')
    if state['craftingProject']:
        rows.append(RECIPES[state['craftingProject']['recipeId']]['name'] + f': +{crafting_work(state)} work phase(s).' if crafting_work(state) else 'Crafting paused: its maker is assigned elsewhere.')
    harvest = garden_harvest(state)
    if harvest['amount']:
        rows.append(garden_summary(harvest))
    if state['activeResearchId']:
        research_id = state['activeResearchId']
        remaining = RESEARCH_CATALOG[research_id]['requiredWorkPhases'] - state['researchProjects'][research_id]['completedWorkPhases']
        rows.append(RESEARCH_CATALOG[research_id]['name'] + f': +{min(research_work(state), remaining)} work contribution(s).')
    if state['founderAssignment'] == 'commissions':
        rows.append(f'Copying commissions: +{copying_income(state)} shared crowns from your scholar’s work.')
    if state['founderAssignment'] == 'facilities' and state['activeFacilityId']:
        facility=FACILITIES[state['activeFacilityId']];project=state['facilityProjects'][state['activeFacilityId']]
        rows.append(facility['name'] + ': +'+str(character_approaches.work_step(state,'founder','construction',project['completedWorkPhases'],facility['requiredWorkPhases']))+' work phase(s).')
    elif any(project['status'] == 'in-progress' for project in state['facilityProjects'].values()):
        rows.append('Living-wing work paused: choose a project in the household ledger to resume.')
    if state['activeHousingRoomId']:
        room=state['housingRooms'][state['activeHousingRoomId']];definition=HOUSING_ROOMS[state['activeHousingRoomId']]
        work=character_approaches.work_step(state,'founder','housing',room['completedWorkPhases'],definition['requiredWorkPhases'])
        rows.append(definition['name'] + (': +'+str(work)+' restoration phase(s).' if state['founderAssignment']=='housing' and character_at_castle(state,'founder') else ': restoration paused.'))
    rows.extend(delegation_forecast(state))
    rows.extend(allowance_forecast(state))
    rows.extend(personal_request_forecast(state))
    rows.extend(resident_project_forecast(state))
    rows.extend(casting_plan_forecast(state))
    for who,project in state.get('toolUpgradeProjects',{}).items():
        working=character_at_castle(state,who) and character_assignment(state,who)=='inscribing'
        rows.append(state['personalEquipment'][project['itemId']]['name']+(': tool inscription +'+str(1+int(headquarters.ready(state,'enchanting-room')))+' work.' if working else ': tool inscription paused.'))
    rows.extend(spell_forecast(state))
    rows.extend(development_forecast(state))
    for who, project in state['focusProjects'].items():
        if project:
            working = character_at_castle(state, who) and character_assignment(state, who) == 'inscribing'
            rows.append(character_profile(state,who)['name'] + ': focus work +1 phase.' if working else character_profile(state,who)['name'] + ': focus work paused; assign inscription work at home.')
    import character_quests
    quest=character_quests.active(state)
    if quest and quest['status']=='working':
        rows.append(quest['title']+(': shared quest work +1 phase.' if character_quests.working(state) else ': quest work paused; bring both participants home and resume with them free.'))
    rows.extend(provisions.forecast(state))
    import bestiary
    if bestiary.saved(state)['research']:
        rows.append('Bestiary study: '+('complete the entry on Advance.' if bestiary.working(state) else 'paused; resume in Creatures and Peoples.'))
    if not rows:
        rows.append('Resting at home. No project work is assigned for this phase.')
    return rows

def resolve_work(state):
    armoury.sync(state)
    bond_snapshot = resident_bonds.phase_groups(state)
    food_assignments={w:character_assignment(state,w) for w in household_members(state) if character_at_castle(state,w)}
    food_phase=state['currentDayPhase']
    import character_quests
    hq_eligible=[who for who in headquarters.projects(state) if headquarters.working(state,who)]
    gear_eligible=[who for who in armoury.state(state)['jobs'] if armoury.working(state,who)]
    drill_eligible=arms_of_our_own.drill_working(state)
    quest_eligible=character_quests.working(state)
    import household_sagas
    saga_eligible=household_sagas.eligible(state)
    shape_workers=house_shape.eligible(state)
    shape_usage=house_shape.usage_snapshot(state)
    growth_before=room_to_grow.snapshot(state)
    summary = []
    used_supports=spell_support.snapshot(state)
    for who in household_members(state):
        if character_at_castle(state,who) and character_assignment(state,who)=='rest' and field_magic.vitality(state,who)<6:
            field_magic.heal(state,who,1 if provisions.short(state) else (3 if food_phase=='evening' or lasting_rituals.active(state,'sanctuary-circle') else 1)+int(character_builds.build(state,who)['attributes']['vitality']>=8)+int(bool(state['headquarters']['stock'].get('recovery-ward')))+int(bool(state['headquarters']['stock'].get('specialty:merrin'))))
            summary.append(character_profile(state,who)['name']+' recovered vitality while resting at home: '+str(field_magic.vitality(state,who))+'/6.')
    harvest = garden_harvest(state)
    if state['researchStatus'] == 'in-progress':
        work = research_work(state)
        work = min(work, state['researchRequiredPhases'] - state['researchCompletedPhases'])
        state['researchCompletedPhases'] += work
        for who in household_members(state):
            if who!='founder' and work and character_assignment(state,who)=='archive' and who not in state['hearthResearchContributors']:
                state['hearthResearchContributors'].append(who)
        if work:
            summary.append(f'Hearth-ward research: +{work} work phase(s).')
        if state['researchCompletedPhases'] == state['researchRequiredPhases']:
            state['researchStatus'] = 'complete'
            if state['expedition'] is None:
                learn_principle(state, 'steady-hearth-wards')
            elif 'steady-hearth-wards' not in state['archivePrinciples']:
                state['archivePrinciples'].append('steady-hearth-wards')
            if 'steady-hearth-wards' in state['founderKnownPrinciples']:
                award_advancement(state, 'founder', 'hearth-understood', 1, 'Understood steady hearth wards')
            for who in state['hearthResearchContributors']:
                if character_at_castle(state,who):
                    learn_for_character(state,who,'steady-hearth-wards')
                    award_advancement(state,who,'hearth-study',1,'Contributed to hearth research')
            summary.append('Research complete: steady hearth wards, a reusable magical principle.')
            if state['founderAssignment'] == 'research':
                state['founderAssignment'] = 'rest'
            for who in household_members(state):
                if who!='founder' and character_assignment(state,who)=='archive':set_character_assignment(state,who,'rest')
    resolve_catalog_research(state, summary)
    if state['restorationStatus'] == 'in-progress' and state['founderAssignment'] == 'restoration':
        work=character_approaches.work_step(state,'founder','restoration',state['restorationCompletedPhases'],state['restorationRequiredPhases'],summary)
        state['restorationCompletedPhases'] += work
        summary.append('Conservatory restoration: +'+str(work)+' work phase(s).')
        if state['restorationCompletedPhases'] == state['restorationRequiredPhases']:
            state['restorationStatus'] = 'complete'
            state['founderAssignment'] = 'rest'
            summary.append('The conservatory is restored. Its garden and interior are now available.')
    project = state['craftingProject']
    work = crafting_work(state)
    if project and work:
        maker_id = project['crafterId']
        project['completedWorkPhases'] += work
        summary.append(RECIPES[project['recipeId']]['name'] + f': +{work} work phase(s) from {character_profile(state,maker_id)["name"]}.')
        if project['completedWorkPhases'] >= RECIPES[project['recipeId']]['requiredWorkPhases']:
            item = project['recipeId']
            state['craftedArtifacts'][item] = state['craftedArtifacts'].get(item, 0) + 1
            continue_delegation=False
            if project.get('workOrderId'):
                order = next(item for item in state['workOrders'] if item['id'] == project['workOrderId'])
                order['completedCount'] += 1
                agreement=order.get('delegation')
                if agreement and agreement['status'] in ('active','paused'):
                    if order['completedCount']>=order['requestedCount']:
                        release_delegation_budget(state,order,'complete')
                    else:continue_delegation=agreement['status']=='active'
                summary.append(f'Work order {order["id"]}: {order["completedCount"]} / {order["requestedCount"]} finished. '+('Next copy waits for another Advance under the standing agreement.' if continue_delegation else 'No additional copy starts automatically.'))
            state['craftingProject'] = None
            set_character_assignment(state, maker_id, 'crafting' if continue_delegation else 'rest')
            award_advancement(state, maker_id, 'artifact:' + item, 1, 'First crafted ' + RECIPES[item]['name'].lower())
            summary.append('Crafted: ' + RECIPES[item]['name'] + '. Ready for use at home.')
    if harvest['amount']:
        if harvest['output']=='provisions':
            provisions.add(state,harvest['amount'])
        elif harvest['output'] == 'silver-ivy':
            state['materialInventory']['silver-ivy'] += harvest['amount']
        else:
            state['sharedFunds'] += harvest['amount']
        summary.append(garden_summary(harvest))
    if state['founderAssignment'] == 'commissions':
        state['sharedFunds'] += copying_income(state)
        summary.append(f'Copying commissions: +{copying_income(state)} shared crowns for careful transcription and record repair.')
    resolve_facility_work(state, summary)
    resolve_development(state, summary)
    resolve_focus_work(state, summary)
    equipment.resolve(state, summary)
    headquarters.resolve(state, summary, hq_eligible)
    resolve_augmentations(state,summary)
    resolve_housing_work(state, summary)
    for who,kind in used_supports:spell_support.consume(state,who,kind,summary)
    resolve_spell_work(state, summary)
    resolve_resident_project(state, summary)
    resolve_personal_requests(state,summary)
    summoning.resolve_work(state,summary)
    resident_projects.resolve(state,summary)
    companion_life.resolve(state,summary)
    castle_mystery.resolve(state,summary)
    containment.resolve(state,summary)
    estate_expansion.resolve(state,summary)
    personal_stories.resolve(state,summary)
    arrivals.resolve(state,summary)
    local_encounters.resolve(state,summary)
    public_workshop.resolve(state,summary)
    public_fieldwork.resolve(state,summary)
    import living_stories
    living_stories.resolve_review(state,summary)
    lasting_rituals.resolve(state,summary)
    character_quests.resolve(state,summary,quest_eligible)
    household_sagas.resolve(state,summary,saga_eligible)
    armoury.resolve(state,summary,gear_eligible)
    arms_of_our_own.resolve_drill(state,summary,drill_eligible)
    room_to_grow.record_work(state,growth_before)
    house_shape.record_usage(state,shape_usage)
    house_shape.resolve(state,summary,shape_workers)
    provisions.resolve(state,summary,food_assignments,food_phase)
    import bestiary
    bestiary.resolve(state,summary,food_assignments)
    import world_recruitment
    world_recruitment.resolve(state,summary,food_assignments)
    first_patrol.resolve_home(state,summary,food_assignments,food_phase)
    household_rest.resolve(state,summary,food_assignments,food_phase)
    field_patrols.resolve(state,summary)
    import commissions,practical_projects,castle_reawakening
    commissions.resolve(state,summary,food_assignments)
    practical_projects.resolve(state,summary,food_assignments)
    castle_reawakening.resolve(state,summary,food_assignments)
    foundation_chamber.resolve(state,summary)
    import survey_rooms
    survey_rooms.resolve(state,summary)
    friendship_milestones.resolve(state,summary)
    resident_bonds.resolve_phase(state,bond_snapshot,summary)
    state['roadsWeKeep']['refugeDone']=bool(state['headquarters']['stock'].get('roadside-refuge'))
    state['lastPhaseSummary'] = summary or ['A restful phase. No project work or production was resolved.']
    for line in summary:
        add_journal(state, line)

def apply_management_action(state, action):
    kind = action.get('type')
    if kind == 'start-restoration':
        require(state['restorationStatus'] == 'not-started', 'Restoration has already begun.')
        require(state['sharedFunds'] >= 25, 'Restoration needs 25 shared crowns.')
        state['sharedFunds'] -= 25
        state['restorationStatus'] = 'in-progress'
        state['founderAssignment'] = 'restoration'
        add_journal(state, 'Committed 25 crowns to the conservatory; your scholar is assigned to its three-phase restoration.')
    elif kind == 'assign-founder':
        assignment = action.get('assignment')
        require(assignment in ('rest', 'research', 'restoration', 'crafting', 'facilities', 'commissions', 'training', 'archive-project', 'inscribing', 'housing', 'spellwork', 'ritual', 'mystery', 'containment', 'estate', 'awakening', 'local-visit', 'headquarters'), 'Unknown assignment.')
        require(assignment != 'headquarters' or state['headquarters']['project'] is not None, 'Start a headquarters project first.')
        require(assignment != 'local-visit' or state['localVisit'] is not None,'Arrange an introduction first.')
        require(assignment != 'awakening' or any(r['status']=='in-progress' for r in state['golemProjects'].values()), 'Fund an adult golem construction plan first.')
        require(assignment != 'estate' or state['estateAnnex']['status']=='in-progress', 'Fund the annex first.')
        require(assignment != 'containment' or state['containment']['project'] is not None, 'Fund a chamber or care project first.')
        require(assignment != 'mystery' or state['castleMystery']['project'] is not None, 'Start an investigation first.')
        require(assignment != 'research' or state['researchStatus'] == 'in-progress' or state['activeResearchId'] is not None, 'Start a research project first.')
        require(assignment != 'restoration' or state['restorationStatus'] == 'in-progress', 'Start restoration first.')
        require(assignment != 'crafting' or (state['craftingProject'] is not None and state['craftingProject']['crafterId'] == 'founder'), 'Start an artifact with your scholar as maker first.')
        require(assignment != 'housing' or state['activeHousingRoomId'] is not None, 'Fund or select a housing project first.')
        validate_development_assignment(state, 'founder', assignment)
        require(assignment != 'facilities' or (state['activeFacilityId'] is not None and state['facilityProjects'][state['activeFacilityId']]['status'] == 'in-progress'), 'Choose an unfinished living-wing project first.')
        state['founderAssignment'] = assignment
    elif kind == 'assign-resident':
        assignment = action.get('assignment')
        require(character_at_castle(state, 'mira'), 'Mira is away. Her work can resume after she returns.')
        require(assignment in ('rest', 'archive', 'garden', 'crafting', 'training', 'archive-project', 'inscribing', 'spellwork', 'ritual', 'personal-story'), 'Mira has not offered that assignment.')
        require(assignment != 'garden' or room_available(state, 'conservatory'), 'Restore the conservatory first.')
        require(assignment != 'archive' or state['researchStatus'] == 'in-progress' or state['activeResearchId'] is not None, 'There is no active research project to assist.')
        require(assignment != 'crafting' or (state['craftingProject'] is not None and state['craftingProject']['crafterId'] == 'mira'), 'Start an artifact with Mira as maker first.')
        validate_development_assignment(state, 'mira', assignment)
        state['residentAssignment'] = assignment
    elif kind == 'garden-production':
        require(room_available(state, 'conservatory'), 'Restore the conservatory first.')
        require(action.get('choice') in ('silver-ivy', 'surplus-sales', 'stock-first','provisions'), 'Unsupported production choice.')
        state['gardenProductionChoice'] = action['choice']
    elif kind == 'buy-material':
        material = action.get('materialId')
        require(material in MATERIALS, 'Unknown material.')
        require(not MATERIALS[material].get('rare'), 'Rare creature materials must be recovered through bounties or field encounters.')
        price = MATERIALS[material]['price']
        require(state['sharedFunds'] >= price, 'The treasury cannot cover this purchase.')
        state['sharedFunds'] -= price
        state['materialInventory'][material] += 1
        add_journal(state, f"Purchased 1 {MATERIALS[material]['name']} for {price} crowns.")
    elif kind == 'sell-material':
        material = action.get('materialId')
        require(material in MATERIALS, 'Unknown material.')
        require(state['materialInventory'][material] > state['materialReserveTargets'][material], 'This sale would use reserved stock. Lower the reserve target in Stores & plans first.')
        state['materialInventory'][material] -= 1
        state['sharedFunds'] += MATERIALS[material]['price']
        add_journal(state, f"Sold 1 {MATERIALS[material]['name']} for {MATERIALS[material]['price']} crowns.")
    elif kind == 'start-crafting':
        require(state['craftingProject'] is None, 'Finish the active artifact before beginning another.')
        require(action.get('recipeId') in RECIPES, 'Unknown recipe.')
        maker_id = action.get('crafterId', 'founder')
        require(maker_id in household_members(state), 'Choose an available maker.')
        require(character_at_castle(state, maker_id), 'The maker must be at the castle.')
        require(RECIPES[action['recipeId']]['requiredPrinciple'] in character_principles(state, maker_id), 'The selected maker must learn this recipe’s principle before crafting it.')
        selected = action.get('materials')
        require(isinstance(selected, list) and len(selected) == 2 and all(isinstance(x, str) and x in MATERIALS for x in selected), 'Choose two supported components.')
        recipe = RECIPES[action['recipeId']]
        for component, property_name in zip(selected, recipe['requiredProperties']):
            require(property_name in MATERIALS[component]['properties'], f'The component must have the {property_name} property.')
        for material in set(selected):
            require(state['materialInventory'][material] >= selected.count(material), 'Not enough of the selected material.')
        for material in selected:
            state['materialInventory'][material] -= 1
        state['craftingProject'] = {'recipeId': action['recipeId'], 'materials': selected, 'completedWorkPhases': 0, 'crafterId': maker_id}
        set_character_assignment(state, maker_id, 'crafting')
        add_journal(state, 'Components committed to ' + recipe['name'].lower() + '. ' + character_profile(state,maker_id)['name'] + ' is assigned to crafting.')
    elif kind == 'install-watering-charm':
        require(room_available(state, 'conservatory'), 'Restore the conservatory first.')
        require(state['craftedArtifacts'].get('watering-charm', 0) > 0, 'Craft a watering charm first.')
        require(type(action.get('installed')) is bool, 'Choose whether to install the charm.')
        state['wateringCharmInstalled'] = action['installed']
    elif kind == 'display-lantern':
        require(state['craftedArtifacts'].get('warming-lantern', 0) > int(bool(state['expedition'] and state['expedition']['carriedLantern'])), 'There is no warming lantern available at home.')
        require(type(action.get('displayed')) is bool, 'Choose whether to display the lantern.')
        state['lanternDisplayed'] = action['displayed']
    else:
        return False
    return True


# 0.3: sample expedition. Narrative is authored; transitions remain rules-owned.
MATERIALS['porous-clay'] = {'name': 'Porous clay', 'properties': ['vessel'], 'price': 5}
RECIPES['watering-charm'] = {'name': 'Self-watering charm', 'requiredPrinciple': 'water-guidance',
    'requiredProperties': ['vessel', 'binding'], 'requiredWorkPhases': 2,
    'description': 'A porous clay vessel bound to guide water to roots. Installed in the conservatory, it improves each staffed harvest: 2 silver ivy or 6 crowns instead of 1 or 4.'}
PRINCIPLE_NAMES = {'steady-hearth-wards': 'Steady hearth wards', 'water-guidance': 'Water guidance'}
EXPEDITION_SITE = {
    'id': 'old-waterworks', 'name': 'The old waterworks',
    'description': 'A short walk beyond the estate, an abandoned sluice house still hums when the stream rises. Practical enchantments remain in its stone channels.',
    'approaches': {
        'survey': {'name': 'Trace the water inscriptions', 'description': 'Your scholarly background is sufficient to record the channel runes. A warming lantern dries the damp inscriptions and reduces on-site work from two phases to one.', 'reward': 'Learn water guidance, unlocking a self-watering charm for the garden.'},
        'salvage': {'name': 'Recover loose components', 'description': 'The accessible control box contains two loose fireglass lenses and ordinary brass salvage. Straightforward careful work; one phase.', 'reward': 'Bring home 2 fireglass and 8 shared crowns.'},
    },
}

def learn_principle(state, principle):
    for field in ('founderKnownPrinciples', 'archivePrinciples'):
        if principle not in state[field]:
            state[field].append(principle)

def garden_yield(state):
    # Backward-compatible potential yield for a staffed garden.
    return garden_harvest(state, assume_staffed=True)['amount']

def expedition_forecast(state):
    expedition = state['expedition']
    stage = expedition['stage']
    if stage == 'encounter-choice':
        return 'Expedition: an encounter decision awaits. Choose a method or return home.'
    if stage == 'outbound':
        return 'Expedition: reach ' + EXPEDITION_SITES[expedition['siteId']]['name'].lower() + '; a choice awaits.'
    if stage == 'awaiting-choice':
        return 'Expedition: choose an approach or return home before advancing.'
    if stage == 'working':
        return f"Expedition: +1 work phase; {expedition['remainingWorkPhases']} remaining."
    if stage == 'ready-to-return':
        return 'Expedition: waiting at the site until you choose to return.'
    return 'Expedition: arrive home and deposit any discoveries.'

def apply_expedition_action(state, action):
    kind = action.get('type')
    if kind == 'start-expedition':
        require(character_at_castle(state,'founder'),'Your scholar must return home before another expedition.')
        require(state['expedition'] is None and not state['publicWorkshop'].get('fieldTrip'), 'An expedition is already underway.')
        site_id = action.get('siteId', 'old-waterworks')
        require(site_id in EXPEDITION_SITES, 'Unknown destination.')
        require(site_available(state, site_id), site_unlock_hint(site_id,state))
        site = EXPEDITION_SITES[site_id]
        require(len(discoveries_for(state, site_id)) < len(site['approaches']), 'All leads at this site are complete.')
        carry = action.get('carryLantern', False)
        require(type(carry) is bool, 'Choose whether to carry a lantern.')
        require(not carry or state['craftedArtifacts'].get('warming-lantern', 0) > 0, 'Craft a warming lantern before packing it.')
        import party_journeys
        selected=party_journeys.party_selection(state,action)
        companion_id=selected[0] if selected else None
        was_displayed = bool(carry and state['lanternDisplayed'] and state['craftedArtifacts'].get('warming-lantern', 0) == 1)
        if was_displayed:
            state['lanternDisplayed'] = False
        state['expedition'] = {'siteId': site_id, 'stage': 'outbound', 'chosenApproach': None,
            'remainingWorkPhases': 0, 'carriedLantern': carry, 'restoreLanternDisplay': was_displayed,
            'discoveryReady': False, 'wealthPlan':state['expeditionWealthPlan'], 'departureDay': state['dayNumber'], 'companionId': companion_id}
        if 'companionIds' in action:state['expedition']['partyIds']=['founder',*selected]
        for who in selected:set_character_assignment(state,who,'expedition')
        state['founderAssignment'] = 'expedition'
        add_journal(state, 'Your scholar set out for ' + site['name'].lower() + '. Castle projects retain their progress.')
    elif kind == 'choose-expedition-approach':
        expedition = state['expedition']
        require(expedition is not None and expedition['stage'] == 'awaiting-choice', 'There is no expedition choice waiting.')
        approach = action.get('approach')
        site = EXPEDITION_SITES[expedition['siteId']]
        require(approach in site['approaches'], 'Unknown approach.')
        require(approach not in discoveries_for(state, expedition['siteId']), 'This discovery has already been brought home.')
        expedition['chosenApproach'] = approach
        import party_journeys
        if party_journeys.active(state):
            party_journeys.resume(state)
            return True
        if expedition['siteId']=='lantern-pavilion':
            import lantern_adventure
            lantern_adventure.resume(state)
            return True
        if first_patrol.active(state):
            first_patrol.resume(state)
            return True
        if roads_we_keep.active(state):
            roads_we_keep.resume(state)
            return True
        if expedition['siteId']==arms_of_our_own.SITE:
            arms_of_our_own.resume(state)
            return True
        if expedition['siteId']=='stormwatch-beacon':
            import beacon_expedition
            beacon_expedition.resume(state)
            return True
        if expedition['siteId']==field_magic.SITE:
            field_magic.resume(state)
            return True
        if expedition['siteId']=='old-service-road':
            import service_road
            service_road.resume(state)
            return True
        if expedition['siteId']=='rainward-observatory':
            resume_observatory(state)
            return True
        party = expedition_party(state)
        prepared_survey = any('field-notes' in state['characterDevelopment'][key]['preparedPractices'] or skill_rank(state,key,'fieldcraft')>=1 for key in party)
        briefing = approach == 'survey' and state['headquarters']['briefing']
        expedition['remainingWorkPhases'] = 1 if approach == 'salvage' or expedition['carriedLantern'] or prepared_survey or briefing else 2
        if briefing:state['headquarters']['briefing']=False
        expedition['stage'] = 'working'
        add_journal(state, 'Expedition approach chosen: ' + site['approaches'][approach]['name'] + '.')
    elif kind == 'return-expedition':
        require(state['expedition'] is not None and state['expedition']['stage'] != 'returning', 'There is no expedition ready to turn homeward.')
        state['expedition']['stage'] = 'returning'
        add_journal(state, 'Your scholar began the journey home. Arrival resolves on the next Advance.')
    else:
        return False
    return True

def resolve_expedition(state):
    expedition = state['expedition']
    if not expedition:
        return
    stage = expedition['stage']
    if stage in ('outbound', 'returning'):
        changes = resident_bonds.award(state, expedition_party(state),
            'expedition:' + state['currentDayPhase'] + ':' + stage,
            'Travelling together: ' + EXPEDITION_SITES[expedition['siteId']]['name'])
        resident_bonds.summarize(state, changes, state['lastPhaseSummary'])
    if stage=='outbound':
        visited=field_magic.initialize(state)['visited']
        if expedition['siteId'] not in visited:visited.append(expedition['siteId'])
    import party_journeys
    if party_journeys.active(state) and stage in ('working','returning'):
        party_journeys.resolve(state)
        return
    if expedition['siteId']=='lantern-pavilion' and stage in ('working','returning'):
        import lantern_adventure
        lantern_adventure.resolve(state)
        return
    if first_patrol.active(state) and stage in ('working','returning'):
        first_patrol.resolve_expedition(state)
        return
    if roads_we_keep.active(state) and stage in ('working','returning'):
        roads_we_keep.resolve_expedition(state)
        return
    if expedition['siteId']==arms_of_our_own.SITE and stage in ('working','returning'):
        arms_of_our_own.resolve_expedition(state)
        return
    if expedition['siteId']=='stormwatch-beacon' and stage in ('working','returning'):
        import beacon_expedition
        beacon_expedition.resolve(state)
        return
    if expedition['siteId']==field_magic.SITE and stage in ('working','returning'):
        field_magic.resolve(state)
        return
    if expedition['siteId']=='old-service-road' and stage in ('working','returning'):
        import service_road
        service_road.resolve(state)
        return
    if expedition['siteId']=='rainward-observatory' and stage in ('working','returning'):
        resolve_observatory(state)
        return
    if stage == 'outbound':
        expedition['stage'] = 'awaiting-choice'
        text = 'Reached ' + EXPEDITION_SITES[expedition['siteId']]['name'].lower() + '. Choose a lead; neither expires.'
    elif stage == 'working':
        expedition['remainingWorkPhases'] -= 1
        if expedition['remainingWorkPhases'] == 0:
            expedition['discoveryReady'] = True
            expedition['stage'] = 'ready-to-return'
            text = 'The selected work is finished. Its discovery will be deposited when you return home.'
        else:
            text = 'Careful fieldwork continues; one more work phase remains.'
    elif stage == 'returning':
        approach = expedition['chosenApproach']
        rewards = []
        discoveries = discoveries_for(state, expedition['siteId'])
        if expedition['discoveryReady'] and approach not in discoveries:
            discoveries.append(approach)
            for character_id in expedition_party(state):
                award_advancement(state, character_id, expedition['siteId'] + ':' + approach, 1, EXPEDITION_SITES[expedition['siteId']]['approaches'][approach]['name'])
            import castle_chapter
            if expedition['siteId'] in castle_chapter.SITES:
                rewards.extend(castle_chapter.return_rewards(state,expedition['siteId'],approach))
            elif expedition['siteId'] == 'fern-nursery':
                if approach == 'survey':
                    learn_principle(state, 'capillary-wicking')
                    rewards.append('Capillary wicking learned and recorded; craft a capillary mat for staffed ivy harvests.')
                else:
                    state['materialInventory']['silver-ivy'] += 4
                    state['materialInventory']['porous-clay'] += 2
                    rewards.append(distribute_expedition_wealth(state,14))
                    rewards.append('4 silver ivy, 2 porous clay and 14 crowns recovered; materials deposited in shared stores.')
            elif expedition['siteId'] == 'hillfold-bindery':
                if approach == 'survey':
                    state['materialInventory']['moon-glass'] += 2
                    rewards.append(distribute_expedition_wealth(state,16))
                    rewards.append('2 moon glass and 16 crowns recovered from the marked storage kiln. Moon glass can serve as a vessel or heat-bearing component.')
                else:
                    state['materialInventory']['binding-thread'] += 4
                    state['materialInventory']['fireglass'] += 1
                    rewards.append(distribute_expedition_wealth(state,12))
                    rewards.append('4 binding thread, 1 fireglass and 12 crowns recovered; materials deposited in shared stores.')
            elif expedition['siteId'] == 'reedbank-waystation':
                if approach == 'survey':
                    learn_principle(state, 'gentle-preservation')
                    rewards.append('Gentle preservation learned and recorded; the pantry seal recipe is available.')
                else:
                    state['materialInventory']['binding-thread'] += 3
                    state['materialInventory']['porous-clay'] += 2
                    rewards.append(distribute_expedition_wealth(state,12))
                    rewards.append('3 binding thread, 2 porous clay and 12 crowns recovered; materials deposited in shared stores.')
            elif approach == 'survey':
                learn_principle(state, 'water-guidance')
                rewards.append('Water guidance learned and recorded in the household archive.')
            elif approach == 'salvage':
                state['materialInventory']['fireglass'] += 2
                rewards.append(distribute_expedition_wealth(state,8))
                rewards.append('2 fireglass and 8 crowns recovered; materials deposited in shared stores.')
            resident_specialties.field_reward(state,rewards)
            if approach == 'salvage' and any(focus_effect_active(state, who, 'field-case', 'expedition') for who in expedition_party(state)):
                state['materialInventory']['binding-thread'] += 1
                rewards.append('The party’s preservation inscription secured 1 extra binding thread. Multiple cases do not stack.')
        for returning_companion in expedition_party(state)[1:]:
            if expedition['discoveryReady'] and approach == 'survey':
                principle = {'old-waterworks':'water-guidance', 'reedbank-waystation':'gentle-preservation', 'fern-nursery':'capillary-wicking'}.get(expedition['siteId'])
                if principle:
                    learn_for_character(state, returning_companion, principle)
            set_character_assignment(state,returning_companion,'rest')
        if expedition['restoreLanternDisplay']:
            state['lanternDisplayed'] = True
        state['lastExpeditionReport'] = {'siteId': expedition['siteId'], 'approach': approach,
            'returnedDay': state['dayNumber'], 'participants':expedition_party(state), 'rewards': rewards or ['Returned safely without a new discovery.']}
        state['expedition'] = None
        if 'steady-hearth-wards' in state['archivePrinciples'] and 'steady-hearth-wards' not in state['founderKnownPrinciples']:
            learn_principle(state, 'steady-hearth-wards')
            award_advancement(state, 'founder', 'hearth-understood', 1, 'Understood steady hearth wards')
            state['lastExpeditionReport']['rewards'].append('Reviewed the household’s completed hearth research on returning home.')
        state['founderAssignment'] = 'rest'
        text = 'Your scholar returned safely. ' + ' '.join(state['lastExpeditionReport']['rewards'])
    else:
        return
    # Replace a no-work placeholder when an expedition did perform work.
    state['lastPhaseSummary'] = [line for line in state['lastPhaseSummary'] if not line.startswith('A restful phase.')]
    state['lastPhaseSummary'].append(text)
    add_journal(state, text)


# 0.4: practical living-wing projects and a second authored field destination.
FACILITIES = {
    'kitchen': {'name': 'Kitchen & dining nook', 'costCrowns': 18, 'requiredWorkPhases': 2,
        'requiredPrinciple': None, 'description': 'Repair a small range, scrub the pantry shelves and set a sturdy shared table.',
        'benefit': 'Makes everyday meals possible and provides a place for a pantry seal.'},
    'washroom': {'name': 'Washroom', 'costCrowns': 18, 'requiredWorkPhases': 2,
        'requiredPrinciple': None, 'description': 'Repair the basin, privacy screen and clean-water pipes in an existing alcove.',
        'benefit': 'Fit a hearth kettle here for reliable warm washing water.'},
    'service-wards': {'name': 'Basic service wards', 'costCrowns': 10, 'requiredWorkPhases': 2,
        'requiredPrinciple': 'steady-hearth-wards', 'description': 'Restore modest household lighting and safe, steady heat along the occupied gallery.',
        'benefit': 'Completes the living wing’s basic magical services. No fuel meter or recurring upkeep.'},
}
RECIPES['hearth-kettle'] = {'name': 'Hearth kettle', 'requiredPrinciple': 'steady-hearth-wards',
    'requiredProperties': ['heat-bearing', 'vessel'], 'requiredWorkPhases': 2,
    'description': 'A gentle heat vessel for the restored washroom. Install it there to provide reliable warm water for the Proper Living Wing milestone.'}
RECIPES['pantry-seal'] = {'name': 'Pantry seal', 'requiredPrinciple': 'gentle-preservation',
    'requiredProperties': ['vessel', 'binding'], 'requiredWorkPhases': 2,
    'description': 'A bound clay seal that keeps designated garden surplus fresh for sale. Installed in the kitchen, it adds 2 crowns to each staffed surplus harvest; stored materials are untouched.'}
PRINCIPLE_NAMES['gentle-preservation'] = 'Gentle preservation'
PRINCIPLE_GUIDE = {
    'steady-hearth-wards': {'source': 'Complete Hearth-ward research.', 'view': 'research',
        'use': 'Warming lantern, hearth kettle and basic service wards.'},
    'water-guidance': {'source': 'Survey the old waterworks and return home.', 'view': 'expeditions',
        'use': 'Self-watering charm and the path to Reedbank waystation.'},
    'gentle-preservation': {'source': 'Survey Reedbank waystation and return home.', 'view': 'expeditions',
        'use': 'Pantry seal for the kitchen.'},
}
EXPEDITION_SITES = {
    'old-waterworks': EXPEDITION_SITE,
    'reedbank-waystation': {
        'id': 'reedbank-waystation', 'name': 'Reedbank waystation',
        'description': 'The waterworks notes mark a disused supply stop farther along the brook. Beneath its low roof, old storage jars still carry traces of practical magic.',
        'approaches': {
            'survey': {'name': 'Study the storage seals', 'description': 'Read the preservation marks on the jar lids. Two work phases, or one with a warming lantern to dry the labels.', 'reward': 'Learn gentle preservation, unlocking a pantry seal for the kitchen.'},
            'salvage': {'name': 'Sort the abandoned supplies', 'description': 'Pack intact clay fittings, binding cord and reusable brass. One work phase; no special tool required.', 'reward': 'Bring home 3 binding thread, 2 porous clay and 12 shared crowns.'},
        },
    },
}

def discoveries_for(state, site_id):
    if site_id in first_patrol.SITES:return state.get('patrolJourneys',{}).get(site_id,{}).get('discoveries',[])
    if site_id==roads_we_keep.SITE:return state.get('hollowRoad',{}).get('discoveries',[])
    if site_id==arms_of_our_own.SITE:return state.get('watchRoad',{}).get('discoveries',[])
    import party_journeys
    if site_id in party_journeys.SITES:return party_journeys.saved(state,site_id)['discoveries']
    if site_id=='lantern-pavilion':return state.get('lanternAdventure',{}).get('discoveries',[])
    if site_id=='stormwatch-beacon':return state.get('beaconJourney',{}).get('discoveries',[])
    if site_id==field_magic.SITE:return field_magic.progress(state)['discoveries']
    import castle_chapter
    if site_id=='old-service-road':return state.get('serviceRoad',{}).get('discoveries',[])
    if site_id in castle_chapter.SITES:return state.get('castleChapter',{}).get('discoveries',{}).get(site_id,[])
    return state.get({'rainward-observatory':'observatoryDiscoveries', 'old-waterworks':'waterworksDiscoveries', 'reedbank-waystation':'waystationDiscoveries', 'hillfold-bindery':'binderyDiscoveries', 'fern-nursery':'nurseryDiscoveries'}[site_id], [])

def site_available(state, site_id):
    if site_id in first_patrol.SITES:return not first_patrol.departure_blockers(state,site_id)
    if site_id==roads_we_keep.SITE:return roads_we_keep.available(state) and state.get('roadsWeKeep',{}).get('started',False)
    if site_id==arms_of_our_own.SITE:return bool(arms_of_our_own.saved(state) and all(arms_of_our_own.chapter_status(state)[:2]))
    import party_journeys
    if site_id in party_journeys.SITES:return state['researchStatus']=='complete'
    if site_id=='lantern-pavilion':return state['researchStatus']=='complete'
    if site_id=='stormwatch-beacon':return state['researchStatus']=='complete'
    if site_id==field_magic.SITE:return state['researchStatus']=='complete'
    import castle_chapter
    if site_id=='old-service-road':
        import service_road
        return service_road.available(state)
    if site_id in castle_chapter.SITES:return castle_chapter.available(state,site_id)
    if site_id == 'rainward-observatory':
        return 'survey' in state.get('binderyDiscoveries',[])
    if site_id == 'fern-nursery':
        return state.get('neighbourRequestProgress', {}).get('brook-lamps', {}).get('status') == 'delivered'
    return site_id == 'old-waterworks' or (site_id == 'reedbank-waystation' and 'survey' in state['waterworksDiscoveries']) or (site_id == 'hillfold-bindery' and (state['miraArchiveProject']['status'] == 'complete' or (state.get('startType')=='fresh' and state['researchProjects']['archive-foundations']['status']=='complete')))

def living_wing_requirements(state):
    return [
        {'name': 'Safe sleeping accommodation', 'complete': True, 'detail': 'Your sleeping chamber is ready.', 'view': 'castle'},
        {'name': 'Comfortable common room', 'complete': True, 'detail': 'The common room is ready for company.', 'view': 'castle'},
        {'name': 'Kitchen & dining', 'complete': state['facilityProjects']['kitchen']['status'] == 'complete', 'detail': 'Restore the kitchen and dining nook.', 'view': 'ledger'},
        {'name': 'Warm, private washroom', 'complete': state['facilityProjects']['washroom']['status'] == 'complete' and state['householdArtifactPlacements']['hearth-kettle'], 'detail': 'Restore the washroom and install a crafted hearth kettle.', 'view': 'ledger'},
        {'name': 'Reliable magical services', 'complete': state['facilityProjects']['service-wards']['status'] == 'complete', 'detail': 'Learn hearth wards and repair the gallery services.', 'view': 'ledger'},
    ]

def check_living_wing_milestone(state):
    if state['livingWingCompletedOn'] is None and all(item['complete'] for item in living_wing_requirements(state)):
        state['livingWingCompletedOn'] = {'dayNumber': state['dayNumber'], 'phase': state['currentDayPhase']}
        state['livingWingCelebration'] = 'available' if 'mira' in household_members(state) else 'unavailable'
        award_advancement(state, 'founder', 'living-wing', 2, 'Established a Proper Living Wing')
        text = 'Milestone: A Proper Living Wing. Safe beds, shared meals, warm water and dependable wards. ' + ('Mira has offered a small celebration whenever you are ready.' if 'mira' in household_members(state) else 'Your home is ready for a growing household.')
        state['lastPhaseSummary'].append(text)
        add_journal(state, text)

def apply_household_action(state, action):
    kind = action.get('type')
    if kind in ('start-facility', 'assign-facility'):
        facility_id = action.get('facilityId')
        require(facility_id in FACILITIES, 'Choose a supported living-wing project.')
        facility = FACILITIES[facility_id]
        project = state['facilityProjects'][facility_id]
        if kind == 'start-facility':
            require(project['status'] == 'not-started', 'This facility has already been funded.')
            require(facility['requiredPrinciple'] is None or facility['requiredPrinciple'] in state['founderKnownPrinciples'], 'Learn steady hearth wards before restoring these services.')
            require(state['sharedFunds'] >= facility['costCrowns'], f"This project needs {facility['costCrowns']} shared crowns.")
            state['sharedFunds'] -= facility['costCrowns']
            project['status'] = 'in-progress'
            add_journal(state, f"Committed {facility['costCrowns']} crowns to {facility['name'].lower()}. Your scholar is assigned to the work.")
        else:
            require(project['status'] == 'in-progress', 'Fund an unfinished project before assigning it.')
        state['activeFacilityId'] = facility_id
        state['founderAssignment'] = 'facilities'
    elif kind == 'place-household-artifact':
        artifact_id = action.get('artifactId')
        require(artifact_id in state['householdArtifactPlacements'], 'Choose a supported household artifact.')
        require(type(action.get('installed')) is bool, 'Choose whether to install the artifact.')
        facility_id = 'washroom' if artifact_id == 'hearth-kettle' else 'kitchen'
        require(state['facilityProjects'][facility_id]['status'] == 'complete', 'Restore the destination facility first.')
        require(state['craftedArtifacts'].get(artifact_id, 0) > 0, 'Craft this artifact before installing it.')
        state['householdArtifactPlacements'][artifact_id] = action['installed']
    elif kind == 'celebrate-living-wing':
        require(state['livingWingCelebration'] == 'available', 'There is no unclaimed living-wing invitation.')
        state['livingWingCelebration'] = 'completed'
        state['conversation'].extend([
            {'speaker': 'Mira', 'text': '“A table that does not wobble. Warm water. Lamps that stay lit.” She sets two cups down with exaggerated ceremony. “We are in danger of becoming respectable.”'},
            {'speaker': 'You', 'text': 'We can keep a few crooked shelves. For character.'},
            {'speaker': 'Mira', 'text': '“For character,” she agrees, smiling over her cup. “I think I shall like making a life here.”'},
        ])
        add_journal(state, 'Shared an unhurried living-wing celebration with Mira. No time or resources spent.')
    else:
        return False
    return True

def resolve_facility_work(state, summary):
    facility_id = state['activeFacilityId']
    if state['founderAssignment'] != 'facilities' or facility_id is None:
        return
    project = state['facilityProjects'][facility_id]
    if project['status'] != 'in-progress':
        return
    facility = FACILITIES[facility_id]
    work=character_approaches.work_step(state,'founder','construction',project['completedWorkPhases'],facility['requiredWorkPhases'],summary)
    project['completedWorkPhases'] += work
    summary.append(f"{facility['name']}: +{work} work phase(s).")
    if project['completedWorkPhases'] >= facility['requiredWorkPhases']:
        project['status'] = 'complete'
        state['founderAssignment'] = 'rest'
        state['activeFacilityId'] = None
        summary.append(f"Ready for use: {facility['name']}. {facility['benefit']}")

def household_next_steps(state):
    steps = []
    if state['expedition']:
        steps.append({'title': 'Continue the expedition', 'detail': expedition_forecast(state), 'view': 'expeditions'})
    if state['researchStatus'] != 'complete':
        steps.append({'title': 'Understand the hearth wards', 'detail': 'Research unlocks a warming lantern, hearth kettle and service wards.', 'view': 'research'})
    if state['restorationStatus'] != 'complete':
        steps.append({'title': 'Restore the conservatory', 'detail': 'A staffed garden supplies components or crowns for household projects.', 'view': 'restoration'})
    if state['craftingProject']:
        steps.append({'title': 'Finish ' + RECIPES[state['craftingProject']['recipeId']]['name'].lower(), 'detail': 'Resume crafting and Advance; committed components stay with the project.', 'view': 'workshop'})
    if 'survey' not in state['waterworksDiscoveries']:
        steps.append({'title': 'Read the waterworks inscriptions', 'detail': 'Return with water guidance to unlock the watering charm and another destination.', 'view': 'expeditions'})
    elif 'survey' not in state['waystationDiscoveries']:
        steps.append({'title': 'Explore Reedbank waystation', 'detail': 'The storage seals offer a useful principle for the kitchen.', 'view': 'expeditions'})
    if state.get('toolUpgradeProjects'):
        steps.append({'title':'Finish a personal tool inscription','detail':'Resume the owner’s work or cancel and recover committed materials. Progress is preserved while paused.','view':'equipment'})
    elif 'survey' in state['waterworksDiscoveries'] and state['researchProjects']['field-calibration']['status']!='complete':
        steps.append({'title':'Make sense of the field measurements','detail':'Research Field calibration to unlock permanent personal tool inscriptions.','view':'research'})
    if any(r['status']=='waiting' for r in state.get('toolMoments',{}).values()):
        steps.append({'title':'Admire her finished work','detail':'A resident has a completed tool to show you. The invitation waits without expiry.','view':'household'})
    if state['livingWingCelebration'] == 'available':
        steps.append({'title': 'A small celebration', 'detail': 'Mira’s invitation is waiting below. There is no expiry and no turn cost.', 'view': 'ledger'})
    if 'mira' in household_members(state) and state['livingWingCompletedOn'] and state['miraArchiveProject']['status'] != 'complete':
        steps.append({'title': 'Mira’s living archive', 'detail': 'Support her study, bind its index charm and show her the finished library.', 'view': 'archiveProject'})
    if state['miraArchiveProject']['status'] == 'complete' and len(state['binderyDiscoveries']) < 2:
        steps.append({'title': 'Visit Hillfold bindery', 'detail': 'Mira’s notes reveal another destination. Invite her along when planning the party.', 'view': 'expeditions'})
    if character_sheet(state, 'founder')['availableAdvancement'] >= 2:
        steps.append({'title': 'Develop your scholar’s practice', 'detail': 'Invest earned advancement, then prepare a learned practice to use it.', 'view': 'development'})
    if state['researchStatus'] == 'complete' and any(project['status'] != 'complete' for project in state['researchProjects'].values()):
        steps.append({'title':'Make household magic more useful', 'detail':'Further studies unlock a root tender, scribe stone and lesson tablet.', 'view':'research'})
    if any(order['completedCount'] < order['requestedCount'] for order in state['workOrders']):
        steps.append({'title':'Review saved work orders', 'detail':'Buy missing components or start the next copy when its maker is ready.', 'view':'stores'})
    if any(progress['status'] == 'accepted' for progress in state['neighbourRequestProgress'].values()):
        steps.append({'title':'Prepare a neighbour’s delivery', 'detail':'Review spare artifacts and unreserved materials. Each request waits without a deadline.', 'view':'requests'})
    elif state['researchStatus'] == 'complete' and state['neighbourRequestProgress']['brook-lamps']['status'] != 'delivered':
        steps.append({'title':'Put useful magic into other hands', 'detail':'The brook keepers have a request for a warming lantern. Their reply opens another path.', 'view':'requests'})
    if site_available(state, 'fern-nursery') and len(state['nurseryDiscoveries']) < 2:
        steps.append({'title':'Visit the fern nursery', 'detail':'A neighbour’s letter marks a public teaching garden with two undated field leads.', 'view':'expeditions'})
    if any(scene['status'] == 'available' for scene in household_invitations(state)):
        steps.append({'title':'A moment with Mira', 'detail':'An optional conversation is waiting in the household. It will not expire.', 'view':'household'})
    if not steps:
        steps.append({'title': 'Make the household your own', 'detail': 'Finish optional salvage, choose furnishings, or spend time with Mira. There is no deadline.', 'view': 'household'})
    return steps


# 0.5: explicit personal mastery, earned practices and an authored resident ambition.
CHARACTERS = {
    'founder': {'name': 'Your scholar', 'role': 'Human scholar · 40', 'startingPractices': [],
        'ambition': 'Make a dependable home and learn what useful magic can do.'},
    'mira': {'name': 'Mira', 'role': 'Human archivist · 22', 'startingPractices': ['archive-focus'],
        'ambition': 'Build an archive worth getting lost in, then bring overlooked knowledge home.'},
}
PRACTICES = {
    'archive-focus': {'name': 'Patient scholarship', 'description': '+1 work contribution to hearth research or the living index, and +1 crown per copying commission when prepared.', 'discipline': 'Scholarship'},
    'careful-assembly': {'name': 'Methodical assembly', 'description': '+1 crafting work contribution when prepared by the artifact’s maker.', 'discipline': 'Artifice'},
    'field-notes': {'name': 'Prepared field notes', 'description': 'Survey work takes one phase instead of two when a party member has this prepared. Does not stack with a warming lantern.', 'discipline': 'Fieldcraft'},
}
RECIPES['index-charm'] = {'name': 'Living index charm', 'requiredPrinciple': 'reference-binding',
    'requiredProperties': ['vessel', 'binding'], 'requiredWorkPhases': 3,
    'description': 'A bound catalogue vessel that guides readers to the right shelf. Install it in the library: each assigned researcher gains +1 work contribution, and copying commissions gain +1 crown. It also completes the practical part of Mira’s archive project.'}
PRINCIPLE_NAMES['reference-binding'] = 'Reference binding'
PRINCIPLE_GUIDE['reference-binding'] = {'source': 'Accept Mira’s archive project and finish the living-index study.', 'view': 'archiveProject', 'use': 'Living index charm for the library.'}

def initialize_development(state):
    state['characterDevelopment'] = {key: {'learnedPractices': list(value['startingPractices']), 'preparedPractices': [], 'advancementAwards': {}} for key, value in CHARACTERS.items()}
    state['trainingProjects'] = {'founder': None, 'mira': None}
    state['residentKnownPrinciples'] = []
    state['hearthResearchContributors'] = []
    state['miraArchiveProject'] = {'status': 'not-started', 'completedWorkPhases': 0, 'requiredWorkPhases': 4, 'contributors': []}
    state['libraryIndexInstalled'] = False
    state['binderyDiscoveries'] = []
    state['materialInventory']['moon-glass'] = 0
    if state['craftingProject']:
        state['craftingProject']['crafterId'] = 'founder'
    if state['expedition']:
        state['expedition']['companionId'] = None
    # Credit only accomplishments already evidenced by older authoritative saves.
    if 'steady-hearth-wards' in state['founderKnownPrinciples']:
        award_advancement(state, 'founder', 'hearth-understood', 1, 'Understood steady hearth wards')
    for recipe_id, count in state['craftedArtifacts'].items():
        if count:
            award_advancement(state, 'founder', 'artifact:' + recipe_id, 1, 'First crafted ' + RECIPES[recipe_id]['name'].lower())
    for site_id in EXPEDITION_SITES:
        for approach in discoveries_for(state, site_id):
            award_advancement(state, 'founder', site_id + ':' + approach, 1, EXPEDITION_SITES[site_id]['approaches'][approach]['name'])
    if state['livingWingCompletedOn']:
        award_advancement(state, 'founder', 'living-wing', 2, 'Established a Proper Living Wing')

def character_at_castle(state, character_id):
    if character_id == 'mira' and state.get('startType') == 'fresh' and state.get('additionalResidents',{}).get('mira',{}).get('status')!='resident':return False
    if state.get('expedition') and character_id in expedition_party(state):return False
    if public_fieldwork.away(state,character_id) or field_patrols.away(state,character_id):return False
    if character_id in state.get('residency',{}):
        return state['residency'][character_id]['residencyStatus'] in ('visiting','resident','departure-agreed')
    if character_id not in ('founder','mira'):
        return state.get('additionalResidents',{}).get(character_id,{}).get('status')=='resident'
    return state['expedition'] is None if character_id == 'founder' else not (state['expedition'] and state['expedition'].get('companionId') == 'mira')

def character_principles(state, character_id):
    if character_id not in ('founder','mira'):return state.get('additionalResidents',{}).get(character_id,{}).get('knownPrinciples',[])
    return state['founderKnownPrinciples'] if character_id == 'founder' else state['residentKnownPrinciples']

def character_assignment(state, character_id):
    if character_id not in ('founder','mira'):return state.get('additionalResidents',{}).get(character_id,{}).get('assignment','rest')
    return state['founderAssignment'] if character_id == 'founder' else state['residentAssignment']

def set_character_assignment(state, character_id, assignment):
    if character_id not in ('founder','mira'):
        state['additionalResidents'][character_id]['assignment']=assignment
        return
    state['founderAssignment' if character_id == 'founder' else 'residentAssignment'] = assignment

def award_advancement(state, character_id, source, points, reason):
    awards = state['characterDevelopment'][character_id]['advancementAwards']
    if source not in awards:
        awards[source] = {'points': points, 'reason': reason}

def character_sheet(state, character_id):
    development = state['characterDevelopment'][character_id]
    earned = sum(item['points'] for item in development['advancementAwards'].values())
    invested = 2 * len(set(development['learnedPractices']) - set(character_profile(state,character_id)['startingPractices'])) + 2 * sum(state['characterSkills'][character_id].values()) + character_builds.invested(state,character_id)
    project = state['trainingProjects'][character_id]
    public_reserved=2 if state.get('publicWorkshop',{}).get('jobs',{}).get(character_id,{}).get('kind')=='perk' else 0
    reserved = 2 if project and project['kind'] in ('practice','skill') else character_builds.reserved(project)
    reserved+=public_reserved
    return {**deepcopy(development), 'skills':deepcopy(state['characterSkills'][character_id]),
        'offeredSkills':list(CHARACTER_SKILLS), 'earnedAdvancement': earned, 'investedAdvancement': invested,
        'reservedAdvancement': reserved, 'availableAdvancement': earned - invested - reserved,
        'knownPrinciples': list(character_principles(state, character_id)), 'atCastle': character_at_castle(state, character_id),
        'assignment': character_assignment(state, character_id), 'trainingProject': deepcopy(project),
        'offeredPractices': [key for key in PRACTICES if key!='field-notes' or character_id=='founder' or (character_id=='mira' and state['miraArchiveProject']['status']=='complete')]}

def work_contribution(state, character_id, practice):
    if not character_at_castle(state, character_id):
        return 0
    return sum(item['amount'] for item in work_contribution_parts(state,character_id,practice))

def research_work(state):
    return sum(work_contribution(state, key, 'archive-focus') for key, assignment in [(who,'research' if who=='founder' else 'archive') for who in household_members(state)] if character_assignment(state, key) == assignment) + friendship_milestones.bonus(state,'archive')

def archive_project_work(state):
    if state['miraArchiveProject']['status'] != 'in-progress':
        return 0
    work = sum(work_contribution(state, key, 'archive-focus') for key in household_members(state) if character_assignment(state, key) == 'archive-project') + friendship_milestones.bonus(state,'archive-project')
    return min(work, state['miraArchiveProject']['requiredWorkPhases'] - state['miraArchiveProject']['completedWorkPhases'])

def crafting_work(state):
    project = state['craftingProject']
    if not project or character_assignment(state, project['crafterId']) != 'crafting':
        return 0
    return min(work_contribution(state, project['crafterId'], 'careful-assembly'), RECIPES[project['recipeId']]['requiredWorkPhases'] - project['completedWorkPhases'])

def validate_development_assignment(state, character_id, assignment):
    require(assignment != 'personal-story' or personal_stories.active_story(state,character_id) is not None, 'Fund this person’s story project first.')
    require(assignment != 'spellwork' or state['spellWork'][character_id] is not None, 'Begin a spell test or schedule a casting first.')
    require(assignment != 'ritual' or state['spellRitual']['status'] == 'in-progress', 'Begin the concordant lesson ritual first.')
    require(assignment != 'inscribing' or (state['focusProjects'][character_id] is not None or state.get('toolUpgradeProjects',{}).get(character_id)), 'Start a focus or working-tool inscription first.')
    require(assignment != 'training' or state['trainingProjects'][character_id] is not None, 'Choose a learning or retraining project on this character’s sheet first.')
    require(assignment != 'archive-project' or state['miraArchiveProject']['status'] == 'in-progress', 'Accept Mira’s archive project before assigning its study.')

def learn_for_character(state, character_id, principle):
    known = character_principles(state, character_id)
    if principle not in known:
        known.append(principle)
    if principle not in state['archivePrinciples']:
        state['archivePrinciples'].append(principle)

def apply_development_action(state, action):
    kind = action.get('type')
    if kind=='start-training' and str(action.get('practiceId','')).startswith('ss-dev-'):
        raise RuleError('Use the public workshop method investment controls.')
    supported = ('train-skill', 'start-training', 'study-principle', 'start-retraining', 'cancel-training', 'prepare-practice', 'start-archive-project', 'install-index-charm', 'finish-archive-story')
    if kind not in supported:
        return False
    require(character_at_castle(state, 'founder'), 'Return your scholar to the castle before planning this in-person development.')
    if kind in ('start-archive-project', 'finish-archive-story'):
        require(character_at_castle(state, 'mira'), 'Mira must be home for this conversation.')
        project = state['miraArchiveProject']
        if kind == 'start-archive-project':
            require(state['livingWingCompletedOn'] is not None, 'Complete the Proper Living Wing milestone first.')
            require(project['status'] == 'not-started', 'Mira’s archive project has already begun.')
            project['status'] = 'in-progress'
            state['residentAssignment'] = 'archive-project'
            state['conversation'].append({'speaker':'Mira', 'text':'“There are books here I have only met by accident. I would like an index that remembers where things belong.” She opens a battered notebook. “I can handle the catalogue. Help me turn it into something useful?”'})
            add_journal(state, 'Accepted Mira’s living-index project. She has chosen to work on it; your scholar may help.')
        else:
            require(project['status'] == 'ready-to-bind' and state['libraryIndexInstalled'], 'Finish the index study and install its charm in the library first.')
            project['status'] = 'complete'
            award_advancement(state, 'mira', 'living-index', 3, 'Realized her living archive ambition')
            award_advancement(state, 'founder', 'living-index', 1, 'Supported Mira’s living archive')
            state['conversation'].append({'speaker':'Mira', 'text':'“It found the volume on migratory moss. Nobody has found that on purpose in years.” Her smile is quietly triumphant. “Next time you go out, ask me along. I should like to see where the next shelf’s worth of stories comes from.”'})
            add_journal(state, 'Mira’s living archive is complete. She has offered to join expeditions and explore fieldcraft. Mira earned 3 advancement; your scholar earned 1.')
        return True
    if kind == 'install-index-charm':
        require(state['craftedArtifacts'].get('index-charm', 0) > 0, 'Craft a living index charm first.')
        require(type(action.get('installed')) is bool, 'Choose whether to install the charm.')
        state['libraryIndexInstalled'] = action['installed']
        return True
    character_id = action.get('characterId')
    require(character_id in household_members(state), 'Choose a supported character.')
    require(character_at_castle(state, character_id), 'This character is away. Preparation and training plans can change at home.')
    development = state['characterDevelopment'][character_id]
    project = state['trainingProjects'][character_id]
    if kind == 'prepare-practice':
        practice = action.get('practiceId')
        require(practice in development['learnedPractices'], 'Learn this practice before preparing it.')
        require(type(action.get('prepared')) is bool, 'Choose whether to prepare the practice.')
        if action['prepared'] and practice not in development['preparedPractices']:
            require(len(development['preparedPractices']) < 2, 'Two practices can be prepared. Put one aside before adding another.')
            development['preparedPractices'].append(practice)
        elif not action['prepared'] and practice in development['preparedPractices']:
            development['preparedPractices'].remove(practice)
    elif kind == 'cancel-training':
        require(project is not None, 'There is no learning project to cancel.')
        release_teacher(state,project)
        state['trainingProjects'][character_id] = None
        if character_assignment(state, character_id) == 'training':
            set_character_assignment(state, character_id, 'rest')
    else:
        require(project is None, 'Finish or cancel the current learning project first.')
        target_id = action.get('skillId') if kind=='train-skill' else action.get('practiceId') if kind == 'start-training' else action.get('principleId')
        if kind=='train-skill':
            require(isinstance(target_id,str) and target_id in CHARACTER_SKILLS, 'Choose an available skill.')
            require(target_id in character_sheet(state,character_id)['offeredSkills'], 'This skill is not currently offered by this character.')
            require(skill_rank(state,character_id,target_id)<2, 'This skill has reached the prototype maximum of two added ranks.')
            require(character_sheet(state,character_id)['availableAdvancement']>=2, 'The next skill rank requires 2 unspent advancement points.')
            project_kind,duration='skill',2
        elif kind == 'start-training':
            require(isinstance(target_id,str) and target_id in PRACTICES, 'Choose a supported practice.')
            require(not practice_requirements(state,character_id,target_id)['blockers'],' '.join(practice_requirements(state,character_id,target_id)['blockers']))
            require(target_id not in development['learnedPractices'], 'This practice is already learned.')
            require(target_id in character_sheet(state, character_id)['offeredPractices'], 'Mira is interested in archive and workshop study for now. Her archive story opens fieldwork.')
            require(character_sheet(state, character_id)['availableAdvancement'] >= 2, 'This practice needs 2 unspent advancement points from accomplishments.')
            project_kind, duration = 'practice', 2
        elif kind == 'study-principle':
            require(target_id in state['archivePrinciples'], 'Bring this principle into the shared archive first.')
            require(target_id not in character_principles(state, character_id), 'This character already understands that principle.')
            project_kind, duration = 'principle', principle_study_phases(state)
        else:
            require(character_sheet(state,character_id)['investedAdvancement']>0, 'There are no invested developments to retrain.')
            require(not character_builds.retraining_blockers(state,character_id), ' '.join(character_builds.retraining_blockers(state,character_id)))
            project_kind, duration, target_id = 'retraining', 1, None
        state['trainingProjects'][character_id] = {'kind': project_kind, 'targetId': target_id, 'completedWorkPhases': 0, 'requiredWorkPhases': duration}
        set_character_assignment(state, character_id, 'training')
        add_journal(state, character_profile(state,character_id)['name'] + ' began ' + ('a one-phase retraining ritual.' if project_kind == 'retraining' else f'a {duration}-phase learning project.'))
    return True

def development_forecast(state):
    rows = []
    for key in household_members(state):
        project = state['trainingProjects'][key]
        if project and project.get('teacherId'):
            blockers=lesson_blockers(state,key)
            rows.append(character_profile(state,key)['name']+' with '+character_profile(state,project['teacherId'])['name']+': '+(' '.join(blockers) if blockers else 'one coordinated lesson phase; both primary assignments committed.'))
        elif project and project['kind']=='retraining' and character_builds.retraining_blockers(state,key):
            rows.append(character_profile(state,key)['name']+': '+ ' '.join(character_builds.retraining_blockers(state,key)))
        elif project:
            rows.append(character_profile(state,key)['name'] + (': +1 learning phase.' if character_assignment(state, key) == 'training' and character_at_castle(state, key) else ': learning paused; progress is kept.'))
    if state['miraArchiveProject']['status'] == 'in-progress':
        rows.append(f'Living-index study: +{archive_project_work(state)} work contribution(s).')
    return rows

def resolve_development(state, summary):
    # Snapshot contributions before finishing learning; newly learned practices are
    # never auto-prepared and cannot grant a second job in their completion phase.
    work = archive_project_work(state)
    if work:
        project = state['miraArchiveProject']
        project['completedWorkPhases'] += work
        for key in household_members(state):
            if character_assignment(state, key) == 'archive-project' and key not in project['contributors']:
                project['contributors'].append(key)
        summary.append(f'Living-index study: +{work} work contribution(s).')
        if project['completedWorkPhases'] >= project['requiredWorkPhases']:
            project['status'] = 'ready-to-bind'
            if 'reference-binding' not in state['archivePrinciples']:
                state['archivePrinciples'].append('reference-binding')
            for key in project['contributors']:
                if character_at_castle(state, key):
                    learn_for_character(state, key, 'reference-binding')
                if character_assignment(state, key) == 'archive-project':
                    set_character_assignment(state, key, 'rest')
            summary.append('The living-index study is complete. Craft its charm, install it in the library, then show Mira the finished archive.')
    for key in household_members(state):
        project = state['trainingProjects'][key]
        if not project or character_assignment(state, key) != 'training' or not character_at_castle(state, key):
            continue
        if project.get('teacherId') and lesson_blockers(state,key):continue
        if project['kind']=='retraining' and character_builds.retraining_blockers(state,key):continue
        extra=min(int(lasting_rituals.active(state,'archive-circle')),project['requiredWorkPhases']-project['completedWorkPhases']-1) if project['kind'] in ('principle','practice') else 0
        if project['kind'] in ('principle','practice') and not project.get('teacherId'):extra+=spell_support.haste_extra(state,key,project['completedWorkPhases'],project['requiredWorkPhases'],summary,1+extra)
        project['completedWorkPhases'] += 1+extra
        summary.append(character_profile(state,key)['name'] + ': +'+str(1+extra)+' learning phase(s).'+(' Taught by '+character_profile(state,project['teacherId'])['name']+'.' if project.get('teacherId') else ''))
        if project['completedWorkPhases'] >= project['requiredWorkPhases']:
            development = state['characterDevelopment'][key]
            target = project['targetId']
            if project['kind']=='personal-drill':
                personal_paths.finish_drill(state,key,project,summary)
            elif project['kind']=='personal-technique':
                personal_paths.complete(state,key,project,summary)
            elif project['kind'] in character_builds.KINDS:
                character_builds.complete(state,key,project,summary)
            elif project['kind'] == 'practice':
                development['learnedPractices'].append(target)
                summary.append(character_profile(state,key)['name'] + ' learned ' + PRACTICES[target]['name'] + '. Prepare it on the character sheet to use it.')
            elif project['kind']=='skill':
                state['characterSkills'][key][target]+=1
                summary.append(character_profile(state,key)['name']+' developed '+CHARACTER_SKILLS[target]['name']+' to rank '+str(state['characterSkills'][key][target])+'. The listed benefit is now active.')
            elif project['kind'] == 'principle':
                learn_for_character(state, key, target)
                summary.append(character_profile(state,key)['name'] + ' now understands ' + PRINCIPLE_NAMES[target] + '.')
            else:
                state['characterBuilds'][key]=character_builds.empty_build(key)
                state['characterSkills'][key]={skill:0 for skill in CHARACTER_SKILLS}
                development['learnedPractices'] = list(character_profile(state,key)['startingPractices'])
                development['preparedPractices'] = [item for item in development['preparedPractices'] if item in development['learnedPractices']]
                summary.append(character_profile(state,key)['name'] + ' completed retraining. Invested advancement is available again; knowledge and accomplishments are kept.')
            if project.get('teacherId'):
                state['lessonHistory'].append({'teacherId':project['teacherId'],'learnerId':key,'kind':project['kind'],'targetId':target,'dayNumber':state['dayNumber'],'phase':state['currentDayPhase'],**({k:project[k] for k in ('sourceOpportunityId','exerciseEvidence') if k in project})})
                state['lessonHistory']=state['lessonHistory'][-60:]
                release_teacher(state,project)
                add_journal(state,character_profile(state,key)['name']+' completed an agreed lesson with '+character_profile(state,project['teacherId'])['name']+'. Knowledge and advancement remain individual; no teaching reward was created.')
            import companion_participation
            companion_participation.trained(state,key,project)
            state['trainingProjects'][key] = None
            set_character_assignment(state, key, 'rest')


def copying_income(state):
    return house_shape.bonus(state,'copy') + int(lasting_rituals.active(state,'market-circle')) + spell_support.bonus(state,'founder','copy') + 4 + 2 * int(focus_effect_active(state, 'founder', 'copying-line')) + int(state['libraryIndexInstalled']) + int('archive-focus' in state['characterDevelopment']['founder']['preparedPractices']) + 2 * int(state['utilityArtifactPlacements']['scribe-stone']) + 2 * int(state['utilityArtifactPlacements'].get('reading-prism',False)) + int(state['utilityArtifactPlacements'].get('weather-screen',False)) + 2 * int(resident_specialties.active(state,'iona'))


MATERIALS['moon-glass'] = {'name': 'Moon glass', 'properties': ['vessel', 'heat-bearing'], 'price': 8}
EXPEDITION_SITES['hillfold-bindery'] = {
    'id': 'hillfold-bindery', 'name': 'Hillfold bindery',
    'description': 'The finished index points to an old bookbinder’s storehouse in the nearby hills. Mira has found a route in the margin of a supply ledger. Dusty kiln shelves and bundled cord suggest useful things left behind.',
    'approaches': {
        'survey': {'name': 'Read the kiln catalogue', 'description': 'Match storage marks to the old catalogue and recover intact moon-glass vessels. Two work phases, or one with prepared field notes or a warming lantern.', 'reward': 'Bring home 2 moon glass and 16 crowns. Moon glass can fill either a vessel or heat-bearing requirement.'},
        'salvage': {'name': 'Recover the binding supplies', 'description': 'Sort intact cord, a fireglass insert and ordinary fittings. One work phase.', 'reward': 'Bring home 4 binding thread, 1 fireglass and 12 shared crowns.'},
    },
}


# 0.6: a research catalogue, persistent reserves and explicit workshop orders.
RESEARCH_CATALOG = {
    'root-rhythms': {'name':'Steady growth cycles', 'costCrowns':12, 'requiredWorkPhases':5,
        'requiredPrinciples':['steady-hearth-wards','water-guidance'], 'principle':'steady-growth',
        'description':'Combine reliable warmth and guided water into a modest rhythm for a working garden.',
        'benefit':'Unlocks a root tender: small harvests even when Mira is elsewhere.'},
    'luminous-impressions': {'name':'Luminous impressions', 'costCrowns':14, 'requiredWorkPhases':5,
        'requiredPrinciples':['steady-hearth-wards','reference-binding'], 'principle':'luminous-copying',
        'description':'Let a stable impression guide a pen without replacing the scholar’s care and judgment.',
        'benefit':'Unlocks a scribe stone: +2 crowns per assigned copying commission.'},
    'shared-lessons': {'name':'Lessons that stay clear', 'costCrowns':10, 'requiredWorkPhases':4,
        'requiredPrinciples':['reference-binding','gentle-preservation'], 'principle':'clear-instruction',
        'description':'Preserve the structure of a worked example so another reader can follow it accurately.',
        'benefit':'Unlocks a lesson tablet: new personal principle studies take one phase instead of two.'},
}
UTILITY_ARTIFACTS = {
    'root-tender': {'roomId':'conservatory', 'benefit':'Without a gardener, produces 1 silver ivy or 2 crowns per Advance, using the garden priority. Staffed harvests keep their normal bonuses; the tender does not add a second harvest.'},
    'scribe-stone': {'roomId':'library', 'benefit':'Adds 2 crowns to each assigned scholar copying commission. Stacks with Patient scholarship and the living index; does not create unattended income.'},
    'lesson-tablet': {'roomId':'library', 'benefit':'New personal principle studies take one assigned phase instead of two. Already-started learning and practice training keep their original durations.'},
}
for recipe_id, name, principle, properties in [
    ('root-tender','Root tender','steady-growth',['botanical','vessel']),
    ('scribe-stone','Scribe stone','luminous-copying',['heat-bearing','vessel']),
    ('lesson-tablet','Lesson tablet','clear-instruction',['vessel','binding']),
]:
    RECIPES[recipe_id] = {'name':name, 'requiredPrinciple':principle, 'requiredProperties':properties,
        'requiredWorkPhases':3, 'description':UTILITY_ARTIFACTS[recipe_id]['benefit']}
PRINCIPLE_NAMES.update({'steady-growth':'Steady growth', 'luminous-copying':'Luminous copying', 'clear-instruction':'Clear instruction'})
for research_id, definition in RESEARCH_CATALOG.items():
    PRINCIPLE_GUIDE[definition['principle']] = {'source':'Complete '+definition['name']+' at the research desk.', 'view':'research', 'use':definition['benefit']}

def principle_study_phases(state):
    return 1 if state['utilityArtifactPlacements']['lesson-tablet'] else 2

def garden_harvest(state, assume_staffed=False):
    staffed = assume_staffed or any(character_assignment(state,who)=='garden' and character_at_castle(state,who) for who in household_members(state))
    automated = state['utilityArtifactPlacements']['root-tender'] and not staffed
    choice = state['gardenProductionChoice']
    if choice == 'stock-first':
        choice = 'silver-ivy' if state['materialInventory']['silver-ivy'] < state['materialReserveTargets']['silver-ivy'] else 'surplus-sales'
    amount = 0
    if assume_staffed or (room_available(state, 'conservatory') and (staffed or automated)):
        if not staffed:
            amount = 1 if choice == 'silver-ivy' else 2
        elif choice=='provisions':
            amount=8+2*int(state['wateringCharmInstalled'])
        elif choice == 'silver-ivy':
            amount = 1 + int(state['wateringCharmInstalled']) + int(state['utilityArtifactPlacements']['capillary-mat']) + int(state['utilityArtifactPlacements'].get('cistern-filter',False)) + int(resident_specialties.active(state,'sylva'))
        else:
            amount = 4 + 2 * int(state['wateringCharmInstalled']) + 2 * int(state['householdArtifactPlacements']['pantry-seal']) + 2 * int((resident_specialties.active(state,'tamsin') or resident_specialties.legacy(state,'zahra')))
    if amount and staffed:amount+=house_shape.bonus(state,'ivy' if choice=='silver-ivy' else 'garden-sales')
    if amount and staffed and lasting_rituals.active(state,'garden-circle'):amount+=1 if choice=='silver-ivy' else 2
    cooperation = friendship_milestones.bonus(state,'garden') if amount and staffed else 0
    amount += cooperation
    return {'output':choice, 'amount':amount, 'cooperation':cooperation, 'staffed':bool(staffed), 'automated':bool(automated),
        'reserveTarget':state['materialReserveTargets']['silver-ivy']}

def garden_summary(harvest):
    source = 'Garden harvest' if harvest['staffed'] else 'Root tender harvest'
    unit = 'provisions' if harvest['output']=='provisions' else 'silver ivy' if harvest['output'] == 'silver-ivy' else 'shared crowns from designated surplus'
    return f'{source}: +{harvest["amount"]} {unit}.' + (' Includes +'+str(harvest['cooperation'])+' from resident cooperation.' if harvest.get('cooperation') else '')

def research_blockers(state, research_id, leader_id):
    definition = RESEARCH_CATALOG[research_id]
    project = state['researchProjects'][research_id]
    blockers = []
    if not character_at_castle(state, 'founder') or not character_at_castle(state, leader_id):
        blockers.append('Return home to agree a research focus.')
    discovery=definition.get('requiredDiscovery')
    if discovery and discovery['approach'] not in discoveries_for(state,discovery['siteId']):
        blockers.append('Complete '+EXPEDITION_SITES[discovery['siteId']]['name']+' survey and bring the observations home first.')
    if research_id=='archive-foundations' and state.get('startType')!='fresh':
        blockers.append('The demonstration household uses Mira’s archive project for this discovery.')
    if research_id=='courteous-passage':
        if state.get('startType')=='fresh':
            if not state['libraryIndexInstalled']:blockers.append('Install a living index charm before researching Courteous passage.')
        elif state['spellRitual']['status']!='complete':
            blockers.append('Complete the concordant lesson ritual before researching Courteous passage.')
    if state['researchStatus'] != 'complete':
        blockers.append('Complete the introductory hearth study first.')
    for principle in definition['requiredPrinciples']:
        if principle not in character_principles(state, leader_id):
            blockers.append(character_profile(state,leader_id)['name']+' must understand '+PRINCIPLE_NAMES[principle]+'.')
    if project['status'] == 'not-started' and state['sharedFunds'] < definition['costCrowns']:
        blockers.append(f'Need {definition["costCrowns"] - state["sharedFunds"]} more crowns.')
    if project['status'] == 'complete':
        blockers.append('This research is already complete.')
    return blockers

def resolve_catalog_research(state, summary):
    research_id = state['activeResearchId']
    if research_id is None:
        return
    project, definition = state['researchProjects'][research_id], RESEARCH_CATALOG[research_id]
    remaining = definition['requiredWorkPhases'] - project['completedWorkPhases']
    phase_contributors=[]
    for character_id, assignment in [(who,'research' if who=='founder' else 'archive') for who in household_members(state)]:
        if character_assignment(state, character_id) != assignment or remaining == 0:
            continue
        work = min(remaining, work_contribution(state, character_id, 'archive-focus'))
        if work:
            phase_contributors.append(character_id)
            project['completedWorkPhases'] += work
            remaining -= work
            if character_id not in project['contributors']:
                project['contributors'].append(character_id)
            summary.append(definition['name']+f': +{work} contribution(s) from '+character_profile(state,character_id)['name']+'.')
    import living_stories
    cooperation=friendship_milestones.cooperation(state,'archive')
    extra=min(remaining,cooperation['amount']) if cooperation else 0
    if extra:
        project['completedWorkPhases']+=extra
        remaining-=extra
        for who in cooperation['participants']:
            if who not in project['contributors']:project['contributors'].append(who)
        summary.append(definition['name']+': +'+str(extra)+' work from resident cooperation ('+' & '.join(character_profile(state,w)['name'] for w in cooperation['participants'])+').')
    living_stories.record_shared_work(state,phase_contributors)
    if remaining == 0:
        project['status'] = 'complete'
        principle = definition['principle']
        if principle not in state['archivePrinciples']:
            state['archivePrinciples'].append(principle)
        for character_id in project['contributors']:
            award_advancement(state, character_id, 'research:'+research_id, 1, 'Contributed to '+definition['name'].lower())
            if character_at_castle(state, character_id):
                learn_for_character(state, character_id, principle)
        for character_id, assignment in [(who,'research' if who=='founder' else 'archive') for who in household_members(state)]:
            if character_assignment(state, character_id) == assignment:
                set_character_assignment(state, character_id, 'rest')
        state['activeResearchId'] = None
        summary.append('Research complete: '+PRINCIPLE_NAMES[principle]+'. '+definition['benefit'])

def work_order_view(state, order):
    recipe = RECIPES[order['recipeId']]
    required = {key:order['materials'].count(key) for key in dict.fromkeys(order['materials'])}
    missing = {key:max(0, count-state['materialInventory'][key]) for key, count in required.items()}
    cost = sum(count*MATERIALS[key]['price'] for key, count in missing.items())
    underway = bool(state['craftingProject'] and state['craftingProject'].get('workOrderId') == order['id'])
    complete = order['completedCount'] >= order['requestedCount']
    blockers = []
    if complete:
        blockers.append('This order is complete.')
    if state['craftingProject']:
        blockers.append('This copy is underway.' if underway else 'Finish the current artifact before starting another.')
    if not character_at_castle(state, 'founder') or not character_at_castle(state, order['crafterId']):
        blockers.append('Return home to start this copy.')
    if recipe['requiredPrinciple'] not in character_principles(state, order['crafterId']):
        blockers.append(character_profile(state,order['crafterId'])['name']+' must understand '+PRINCIPLE_NAMES[recipe['requiredPrinciple']]+'.')
    if cost:
        blockers.append('Buy or gather the missing components for this copy.')
    return {**deepcopy(order), 'missingMaterials':missing, 'purchaseCostCrowns':cost,
        'underway':underway, 'complete':complete, 'blockers':blockers,'delegationView':delegation_view(state,order)}

def apply_planning_action(state, action):
    kind = action.get('type')
    if kind == 'set-material-reserve':
        material_id, target = action.get('materialId'), action.get('target')
        require(material_id in MATERIALS, 'Choose a supported material.')
        require(type(target) is int and 0 <= target <= 999, 'Reserve target must be a whole number from 0 to 999.')
        state['materialReserveTargets'][material_id] = target
    elif kind == 'focus-research':
        research_id, leader_id = action.get('researchId'), action.get('leaderId')
        require(research_id in RESEARCH_CATALOG and leader_id in household_members(state), 'Choose a supported research project and lead researcher.')
        blockers = research_blockers(state, research_id, leader_id)
        require(not blockers, ' '.join(blockers))
        definition, project = RESEARCH_CATALOG[research_id], state['researchProjects'][research_id]
        if project['status'] == 'not-started':
            state['sharedFunds'] -= definition['costCrowns']
            project['status'] = 'in-progress'
            add_journal(state, f'Committed {definition["costCrowns"]} crowns to '+definition['name'].lower()+'.')
        state['activeResearchId'] = research_id
        project['leadId'] = leader_id
        set_character_assignment(state, leader_id, 'research' if leader_id == 'founder' else 'archive')
    elif kind == 'place-utility-artifact':
        artifact_id = action.get('artifactId')
        require(artifact_id in UTILITY_ARTIFACTS, 'Choose a supported utility artifact.')
        require(character_at_castle(state, 'founder'), 'Return home before changing an installation.')
        require(room_available(state, UTILITY_ARTIFACTS[artifact_id]['roomId']), 'Restore the destination room first.')
        require(state['craftedArtifacts'].get(artifact_id, 0) > 0, 'Craft this artifact before installing it.')
        require(type(action.get('installed')) is bool, 'Choose whether to install the artifact.')
        state['utilityArtifactPlacements'][artifact_id] = action['installed']
    elif kind == 'create-work-order':
        recipe_id, maker_id = action.get('recipeId'), action.get('crafterId')
        materials, count = action.get('materials'), action.get('requestedCount')
        require(len(state['workOrders']) < 12, 'Keep at most 12 work orders. Remove a finished or unstarted order to make space.')
        require(isinstance(recipe_id,str) and recipe_id in RECIPES and isinstance(maker_id,str) and maker_id in household_members(state), 'Choose a supported recipe and current household maker.')
        require(type(count) is int and 1 <= count <= 20, 'Choose a whole number of copies from 1 to 20.')
        require(isinstance(materials, list) and len(materials) == 2 and all(isinstance(item,str) and item in MATERIALS for item in materials), 'Choose two supported components.')
        for material, property_name in zip(materials, RECIPES[recipe_id]['requiredProperties']):
            require(property_name in MATERIALS[material]['properties'], 'The planned components must match the recipe’s properties.')
        order_id = 'order-'+str(state['nextWorkOrderNumber'])
        state['nextWorkOrderNumber'] += 1
        state['workOrders'].append({'id':order_id,'recipeId':recipe_id,'crafterId':maker_id,'materials':materials[:], 'requestedCount':count,'completedCount':0,'delegation':None})
    elif kind in ('buy-work-order-materials','start-work-order','remove-work-order'):
        order = next((item for item in state['workOrders'] if item['id'] == action.get('orderId')), None)
        require(order is not None, 'Work order not found.')
        view = work_order_view(state, order)
        require(not order.get('delegation') or order['delegation']['status'] in ('complete','revoked'), 'Revoke the delegated agreement before using manual order controls; revoking releases its remaining budget.')
        if kind == 'remove-work-order':
            require(not view['underway'], 'Finish the active copy before removing its work order.')
            state['workOrders'].remove(order)
        elif kind == 'buy-work-order-materials':
            require(not view['complete'] and not view['underway'], 'This order does not need components for its current copy.')
            cost = view['purchaseCostCrowns']
            require(cost > 0, 'The next copy already has its components.')
            require(state['sharedFunds'] >= cost, f'The missing components cost {cost} crowns.')
            state['sharedFunds'] -= cost
            for material_id, count in view['missingMaterials'].items():
                state['materialInventory'][material_id] += count
            add_journal(state, f'Bought the missing components for {order["id"]}: {cost} crowns. Nothing was started automatically.')
        else:
            require(not view['blockers'], ' '.join(view['blockers']))
            apply_action(state, {'type':'start-crafting','recipeId':order['recipeId'],'crafterId':order['crafterId'],'materials':order['materials'][:]})
            state['craftingProject']['workOrderId'] = order['id']
    else:
        return False
    return True


# 0.7: finite, optional neighbour requests. Deliveries are explicit and protect home stock.
NEIGHBOUR_REQUESTS = {
    'brook-lamps': {
        'name': 'A lamp for the footbridge', 'sender': 'The brook keepers',
        'description': 'A steady, enclosed light would make their evening inspections easier. They ask for one lantern and fresh cord for its bracket.',
        'unlockDescription': 'Complete the introductory hearth-ward research.',
        'artifacts': {'warming-lantern': 1}, 'materials': {'binding-thread': 2},
        'rewardCrowns': 24, 'rewardMaterials': {'porous-clay': 1},
        'letter': 'The lamp holds its warmth even in the brook mist. Thank you. We have enclosed a clay vessel and marked the public teaching beds at the fern nursery on your map; the keeper welcomes visitors who wish to study the old watering channels.',
    },
    'dry-shelves': {
        'name': 'Dry shelves at Reedbank', 'sender': 'The Reedbank storekeepers',
        'description': 'Their working store needs a pantry seal and fresh binding plants. A spare household artifact can keep a much larger shelf of provisions dry.',
        'unlockDescription': 'Bring the Reedbank storage-seal survey home.',
        'artifacts': {'pantry-seal': 1}, 'materials': {'silver-ivy': 2},
        'rewardCrowns': 28, 'rewardMaterials': {'moon-glass': 1},
        'letter': 'The seal is settled over the provision shelf. Nothing splendid, perhaps, but the flour is dry and the labels stay readable. We thought a piece of moon glass might be more useful to your workshop than another thank-you alone.',
    },
    'school-tablets': {
        'name': 'Lessons for a pair of desks', 'sender': 'The village evening school',
        'description': 'Two lesson tablets will let a tutor keep separate examples ready for two groups. These must be spare copies, beyond the library installation.',
        'unlockDescription': 'Complete Lessons that stay clear.',
        'artifacts': {'lesson-tablet': 2}, 'materials': {},
        'rewardCrowns': 44, 'rewardMaterials': {'fireglass': 2},
        'letter': 'Both tablets have found desks. Our students now leave with the right example in mind, which is a considerable improvement over leaving with the wrong one beautifully copied. Two pieces of fireglass come from our spare supplies.',
    },
    'nursery-exchange': {
        'name': 'A new mat for the teaching beds', 'sender': 'The fern nursery keeper',
        'description': 'Turn the channel notes into a capillary mat for the nursery’s demonstration bench. Their own bench will help the next visitor understand the principle.',
        'unlockDescription': 'Return with the fern nursery channel survey.',
        'artifacts': {'capillary-mat': 1}, 'materials': {},
        'rewardCrowns': 24, 'rewardMaterials': {'moon-glass': 2},
        'letter': 'Your mat now sits beneath the demonstration pots. The students can see the water climbing without a lecture first. I have sent two pieces of moon glass in thanks. You are welcome back whenever your own beds can spare you.',
    },
}
EXPEDITION_SITES['fern-nursery'] = {
    'id': 'fern-nursery', 'name': 'Fern nursery',
    'description': 'Beyond the footbridge, a modest teaching garden shelters beneath a low timber roof. Its keeper has opened the old demonstration beds and set aside reusable cuttings for visitors.',
    'approaches': {
        'survey': {'name': 'Trace the watering channels', 'description': 'Study how water climbs through woven fibres beneath the pots. Two work phases; a warming lantern or prepared field notes reduces this to one.', 'reward': 'Learn capillary wicking, unlocking a mat that adds 1 silver ivy to each staffed ivy harvest.'},
        'salvage': {'name': 'Collect the offered cuttings', 'description': 'Sort the keeper’s surplus cuttings and reusable clay fittings. One work phase; these supplies are freely offered.', 'reward': 'Bring home 4 silver ivy, 2 porous clay and 14 shared crowns.'},
    },
}
PRINCIPLE_NAMES['capillary-wicking'] = 'Capillary wicking'
PRINCIPLE_GUIDE['capillary-wicking'] = {'source': 'Deliver the brook keepers’ request, then survey the fern nursery and return.', 'view':'requests', 'use':'Capillary mat for the conservatory: +1 ivy per staffed ivy harvest.'}
RECIPES['capillary-mat'] = {'name':'Capillary mat', 'requiredPrinciple':'capillary-wicking',
    'requiredProperties':['botanical', 'binding'], 'requiredWorkPhases':3,
    'description':'A woven growing mat. Install it in the conservatory for +1 silver ivy per staffed ivy harvest. It does not improve surplus sales or unattended root-tender output.'}
UTILITY_ARTIFACTS['capillary-mat'] = {'name':'Capillary mat', 'roomId':'conservatory',
    'benefit':'+1 silver ivy per staffed ivy harvest; no bonus to sales or unattended production.'}

def site_unlock_hint(site_id,state=None):
    if site_id in first_patrol.SITES:return ' '.join(first_patrol.departure_blockers(state,site_id)) if state is not None else 'Review Chapter 7 for route preparation.'
    if site_id==roads_we_keep.SITE:return 'Conclude Chapter 5 and open The Roads We Keep.'
    if site_id==arms_of_our_own.SITE:return 'Complete the equipment review, test two effects and deliver the Chapter 5 commission.'
    import party_journeys
    if site_id in party_journeys.SITES:return 'Complete Hearth wards research to follow this expedition lead.'
    if site_id=='lantern-pavilion':return 'Complete Hearth wards research to follow the pavilion programme.'
    if site_id=='stormwatch-beacon':return 'Complete Hearth wards research to follow the keeper’s request for help.'
    if site_id==field_magic.SITE:return 'Complete Hearth wards research to open the aqueduct repair route.'
    import castle_chapter
    if site_id=='old-service-road':
        import service_road
        return service_road.hint()
    if site_id in castle_chapter.SITES:return castle_chapter.hint(site_id)
    return {'rainward-observatory':'Survey Hillfold bindery and return with its marked lens catalogue.', 'old-waterworks':'This path is already open.',
        'reedbank-waystation':'Survey the waterworks and return to reveal this path.',
        'hillfold-bindery':'Complete Arrange the first archive in a fresh campaign, or finish Mira’s archive story, to find the bindery.',
        'fern-nursery':'Deliver A lamp for the footbridge under Requests & letters to receive the nursery directions.'}[site_id]

def neighbour_request_unlocked(state, request_id):
    return {
        'brook-lamps': state['researchStatus'] == 'complete',
        'dry-shelves': 'survey' in state['waystationDiscoveries'],
        'school-tablets': state['researchProjects']['shared-lessons']['status'] == 'complete',
        'nursery-exchange': 'survey' in state['nurseryDiscoveries'],
    }[request_id]

def spare_artifact_count(state, artifact_id):
    committed = int(bool(state['utilityArtifactPlacements'].get(artifact_id)))
    committed += int(bool(state['householdArtifactPlacements'].get(artifact_id)))
    if artifact_id == 'warming-lantern':
        committed += int(state['lanternDisplayed']) + int(bool(state['expedition'] and state['expedition']['carriedLantern']))
    elif artifact_id == 'watering-charm':
        committed += int(state['wateringCharmInstalled'])
    elif artifact_id == 'index-charm':
        committed += int(state['libraryIndexInstalled'])
    return max(0, state['craftedArtifacts'].get(artifact_id, 0) - committed)

def neighbour_request_view(state, request_id):
    definition = NEIGHBOUR_REQUESTS[request_id]
    progress = state['neighbourRequestProgress'][request_id]
    unlocked = neighbour_request_unlocked(state, request_id)
    blockers = []
    if not unlocked:
        blockers.append(definition['unlockDescription'])
    if progress['status'] != 'accepted':
        blockers.append('Already delivered.' if progress['status'] == 'delivered' else 'Accept this request before delivering.')
    if not character_at_castle(state, 'founder'):
        blockers.append('Return home to arrange this delivery.')
    artifact_rows = []
    material_rows = []
    for key, count in definition['artifacts'].items():
        spare = spare_artifact_count(state, key)
        artifact_rows.append({'id':key, 'requiredCount':count, 'spareCount':spare, 'missingCount':max(0,count-spare)})
        if spare < count:
            blockers.append(f'Need {count} spare {RECIPES[key]["name"].lower()}; {spare} available. Installed and packed copies are protected.')
    for key, count in definition['materials'].items():
        available = max(0, state['materialInventory'][key] - state['materialReserveTargets'][key])
        material_rows.append({'id':key, 'requiredCount':count, 'availableCount':available, 'reserveTarget':state['materialReserveTargets'][key]})
        if available < count:
            blockers.append(f'Need {count} unreserved {MATERIALS[key]["name"].lower()}; {available} available. Gather more or explicitly lower the reserve.')
    return {**deepcopy(progress), 'unlocked':unlocked, 'artifacts':artifact_rows, 'materials':material_rows, 'blockers':blockers}

def household_invitations(state):
    definitions = [
        {'id':'first-letter', 'title':'A letter on the reading table', 'description':'Mira has left a neighbour’s reply beside two cups. She would like to read it with you.', 'ready':any(item['status']=='delivered' for item in state['neighbourRequestProgress'].values())},
        {'id':'green-fingers', 'title':'Notes among the green leaves', 'description':'With the nursery notes safely home, Mira has an observation about practical magic—and an invitation to linger.', 'ready':'survey' in state['nurseryDiscoveries'] and state['restorationStatus']=='complete'},
    ]
    for scene in definitions:
        scene['status'] = 'completed' if scene['id'] in state['completedHouseholdScenes'] else 'available' if scene.pop('ready') else 'locked'
        scene.pop('ready', None)
        scene['canJoin'] = scene['status']=='available' and character_at_castle(state,'founder') and character_at_castle(state,'mira')
    return definitions

def apply_neighbour_action(state, action):
    kind = action.get('type')
    if kind in ('accept-neighbour-request', 'defer-neighbour-request', 'deliver-neighbour-request'):
        request_id = action.get('requestId')
        require(request_id in NEIGHBOUR_REQUESTS, 'Choose a supported neighbour request.')
        definition = NEIGHBOUR_REQUESTS[request_id]
        progress = state['neighbourRequestProgress'][request_id]
        require(neighbour_request_unlocked(state, request_id), definition['unlockDescription'])
        require(character_at_castle(state, 'founder'), 'Return home before arranging a neighbour request.')
        if kind == 'accept-neighbour-request':
            require(progress['status'] == 'offered', 'This request is already accepted or delivered.')
            progress['status'] = 'accepted'
            add_journal(state, 'Accepted '+definition['name']+'. No goods are reserved and there is no deadline.')
        elif kind == 'defer-neighbour-request':
            require(progress['status'] == 'accepted', 'Only an accepted request can be put aside.')
            progress['status'] = 'offered'
            add_journal(state, 'Put aside '+definition['name']+'. It remains available without penalty.')
        else:
            blockers = neighbour_request_view(state, request_id)['blockers']
            require(not blockers, ' '.join(blockers))
            for key, count in definition['artifacts'].items():
                state['craftedArtifacts'][key] -= count
            for key, count in definition['materials'].items():
                state['materialInventory'][key] -= count
            state['sharedFunds'] += definition['rewardCrowns']
            for key, count in definition['rewardMaterials'].items():
                state['materialInventory'][key] += count
            progress['status'] = 'delivered'
            progress['deliveredOn'] = {'dayNumber':state['dayNumber'], 'phase':state['currentDayPhase']}
            add_journal(state, 'Delivered '+definition['name']+f'. Received {definition["rewardCrowns"]} crowns and the listed materials. A reply is saved under Requests & letters.')
    elif kind == 'join-household-scene':
        scene_id = action.get('sceneId')
        scene = next((item for item in household_invitations(state) if item['id']==scene_id), None)
        require(scene is not None and scene['canJoin'], 'This invitation is not available here. Completed scenes stay in your conversation; waiting scenes require both people home.')
        playful = 'shared-flirtation' in state['completedDevelopments']
        if scene_id == 'first-letter':
            lines = [
                ('Narrator', 'Mira smooths the folded reply with the back of her hand, leaving its worn crease intact.'),
                ('Mira', '“There is a particular pleasure in a useful thing reaching the right hands. Somewhere beyond our walls, somebody has one less small inconvenience.”'),
                ('You', '“And you saved the letter.”'),
                ('Mira', '“Of course. An archive should remember what the work was for.”'),
            ]
        else:
            lines = [
                ('Narrator', 'In the conservatory, Mira turns the channel sketch sideways. A leaf has pressed a pale mark into one corner.'),
                ('Mira', '“Water climbing a thread. No grand incantation, no thunder. Just understanding the shape of a small need.”'),
                ('You', '“You make that sound rather inviting.”' if playful else '“A lamp we can leave by the books without worrying about a flame. That is worth learning to make.”'),
                ('Mira', '“Then stay a little closer. I am certain the notes can survive being neglected for a minute.”' if playful else '“Then we should keep a bench here. Good ideas deserve somewhere comfortable to arrive.”'),
            ]
        state['conversation'].extend({'speaker':speaker, 'text':line} for speaker,line in lines)
        state['completedHouseholdScenes'].append(scene_id)
        add_journal(state, 'Shared an unhurried moment with Mira: '+scene['title']+'.')
    else:
        return False
    return True


# 0.8: personal signature tools, built and configured at home.
FOCUS_INSCRIPTIONS = {
    'scholarly-thread': {'name':'Scholarly thread', 'requiredPrinciple':'reference-binding', 'requiredProperties':['binding','vessel'], 'benefit':'+1 work contribution to assigned research and the living-index study. No learning-speed bonus.'},
    'steady-hand': {'name':'Steady hand', 'requiredPrinciple':'steady-hearth-wards', 'requiredProperties':['heat-bearing','binding'], 'benefit':'+1 work contribution when this character is the assigned artifact maker. Does not accelerate focus inscription work.'},
    'field-case': {'name':'Preservation case', 'requiredPrinciple':'gentle-preservation', 'requiredProperties':['vessel','binding'], 'benefit':'When prepared for expeditions, a new completed salvage lead brings home 1 extra binding thread per party. Multiple cases do not stack; surveys gain nothing.'},
    'copying-line': {'name':'Copying line', 'requiredPrinciple':'luminous-copying', 'requiredProperties':['vessel','heat-bearing'], 'benefit':'+2 crowns per phase spent on copying commissions. Applies to your character; Mira does not offer this task.'},
}

def focus_effect_active(state, character_id, inscription_id, context='household'):
    focus = state.get('signatureFocuses', {}).get(character_id)
    if 'armoury' in state and 'legacy:focus:'+character_id in armoury.state(state)['items']:
        return armoury.has(state,character_id,'legacy:'+inscription_id,context)
    return bool(focus and inscription_id in focus['inscriptions'] and inscription_id in focus[context+'Loadout'])

def focus_view(state, character_id):
    focus = state['signatureFocuses'][character_id]
    return {**deepcopy(focus), 'project':deepcopy(state['focusProjects'][character_id]),
        'canAlter':character_at_castle(state,'founder') and character_at_castle(state,character_id),
        'knownPrinciples':list(character_principles(state,character_id))}

def apply_focus_action(state, action):
    kind = action.get('type')
    if kind not in ('rename-focus','start-focus-inscription','upgrade-focus','configure-focus'):
        return False
    who = action.get('characterId')
    require(who in household_members(state), 'Choose an available character.')
    require(character_at_castle(state,'founder') and character_at_castle(state,who), 'Return home before agreeing a focus change.')
    focus = state['signatureFocuses'][who]
    if kind == 'rename-focus':
        focus['name'] = text_value(action.get('name'),40)
    elif kind == 'configure-focus':
        require(not state['publicWorkshop']['preparedItems'].get(who) or not action.get('inscriptions'), 'Stow the public focus before preparing baseline inscriptions.')
        context, selected = action.get('context'), action.get('inscriptions')
        require(context in ('household','expedition'), 'Choose household or expedition preparation.')
        require(isinstance(selected,list) and all(isinstance(key,str) and key in focus['inscriptions'] for key in selected), 'Prepare only inscriptions already completed on this focus.')
        require(len(selected)==len(set(selected)) and len(selected)<=focus['capacity'], 'Each inscription takes one slot; avoid duplicates and stay within capacity.')
        require(all((key == 'field-case') == (context == 'expedition') for key in selected), 'Use preservation cases in expedition preparation and work inscriptions in household preparation.')
        focus[context+'Loadout'] = selected[:]
    else:
        require(not state.get('toolUpgradeProjects',{}).get(who),'Finish or cancel this owner’s working-tool inscription first.')
        require(state['focusProjects'][who] is None, 'Finish this character’s current focus work first. It can be paused without losing progress.')
        inscription = action.get('inscriptionId')
        if kind == 'upgrade-focus':
            require(focus['capacity']==1, 'This focus already has its two-slot capacity.')
            principle, properties, cost, phases = 'reference-binding', ['vessel','vessel'], 18, 3
        else:
            require(inscription in FOCUS_INSCRIPTIONS, 'Choose a supported inscription.')
            require(inscription not in focus['inscriptions'], 'This inscription is already part of the focus.')
            definition = FOCUS_INSCRIPTIONS[inscription]
            principle, properties, cost, phases = definition['requiredPrinciple'], definition['requiredProperties'], 6, 2
        require(principle in character_principles(state,who), 'The focus owner must learn '+PRINCIPLE_NAMES[principle]+'.')
        components = action.get('materials')
        require(isinstance(components,list) and len(components)==2 and all(isinstance(key,str) and key in MATERIALS for key in components), 'Choose two supported components.')
        for key, property_name in zip(components,properties):
            require(property_name in MATERIALS[key]['properties'], 'A component must have the '+property_name+' property.')
        for key in set(components):
            require(state['materialInventory'][key]>=components.count(key), 'Not enough of the selected material; using the same component twice needs two copies.')
        require(state['sharedFunds']>=cost, f'This focus work requires {cost} shared crowns.')
        state['sharedFunds'] -= cost
        for key in components: state['materialInventory'][key] -= 1
        state['focusProjects'][who] = {'kind':'capacity' if kind=='upgrade-focus' else 'inscription',
            'inscriptionId':None if kind=='upgrade-focus' else inscription, 'materials':components[:],
            'requiredWorkPhases':phases, 'completedWorkPhases':0}
        set_character_assignment(state,who,'inscribing')
        add_journal(state, character_profile(state,who)['name']+' committed '+str(cost)+' crowns and components to '+focus['name']+'. Focus work progresses only on assigned Advance phases.')
    return True

def resolve_focus_work(state, summary):
    for who, project in state['focusProjects'].items():
        if not project or not character_at_castle(state,who) or character_assignment(state,who)!='inscribing':
            continue
        extra=min(spell_support.bonus(state,who,'focus'),project['requiredWorkPhases']-project['completedWorkPhases']-1)
        project['completedWorkPhases'] += 1+extra
        if extra:spell_support.consume(state,who,'focus',summary)
        focus = state['signatureFocuses'][who]
        summary.append(character_profile(state,who)['name']+': '+focus['name']+' inscription work +1 phase.')
        if project['completedWorkPhases']>=project['requiredWorkPhases']:
            if project['kind']=='capacity':
                focus['capacity']=2
                summary.append(focus['name']+' now supports two prepared inscriptions per configuration.')
            else:
                focus['inscriptions'].append(project['inscriptionId'])
                summary.append(FOCUS_INSCRIPTIONS[project['inscriptionId']]['name']+' completed on '+focus['name']+'. Prepare it explicitly for household or expedition use.')
            state['focusProjects'][who]=None
            set_character_assignment(state,who,'rest')


# 0.10: usable accommodation, explicit bedroom choices and future-bed planning.
HOUSING_ROOMS = {
    'bedchamber': {'name':'Guest chamber','capacityBeds':2,'costCrowns':0,'requiredWorkPhases':0,'description':'Two separate beds with a privacy screen, suitable for residents who accept a shared bedroom.'},
    'west-chamber': {'name':'West chamber','capacityBeds':1,'costCrowns':16,'requiredWorkPhases':2,'description':'Repair a small existing chamber and fit one bed, a plain chest and a closing door.'},
    'garden-chamber': {'name':'Garden chamber','capacityBeds':2,'costCrowns':24,'requiredWorkPhases':3,'description':'Restore a modest two-bed chamber looking toward the garden, with separate storage and a privacy screen.'},
}
for room_id in ('west-chamber','garden-chamber'):
    ROOMS[room_id] = {'name':HOUSING_ROOMS[room_id]['name'],'purpose':'Safe, comfortable accommodation.',
        'description':HOUSING_ROOMS[room_id]['description']+' Each chamber has its own illustration, furnishings and accepted image override.',
        'furnishings':['oak-bench','velvet-bench','none']}
    ORIGINAL_ASSETS[room_id] = f'/assets/{room_id}.webp'

def housing_summary(state):
    rooms={}
    for room_id, definition in HOUSING_ROOMS.items():
        progress=state['housingRooms'][room_id]
        occupants=[key for key,value in state['bedroomAssignments'].items() if value==room_id]
        capacity=definition['capacityBeds'] if progress['status']=='complete' else 0
        arrival=sum(item['reservedBeds'] for item in state.get('arrivalReservations',{}).values() if item['roomId']==room_id)
        rooms[room_id]={**deepcopy(progress),'occupants':occupants,'usableBeds':capacity,
            'plannedReservedBeds':progress['reservedBeds'],'arrivalReservedBeds':arrival,'reservedBeds':progress['reservedBeds']+arrival,
            'availableBeds':capacity-len(occupants)-progress['reservedBeds']-arrival}
    return {'rooms':rooms,'usableBeds':sum(row['usableBeds'] for row in rooms.values()),
        'occupiedBeds':len(state['bedroomAssignments']),'reservedBeds':sum(row['reservedBeds'] for row in rooms.values()),
        'availableBeds':sum(row['availableBeds'] for row in rooms.values()),
        'residentCount':len(household_members(state))-1,'founderCount':1}

def apply_housing_action(state, action):
    kind=action.get('type')
    if kind not in ('fund-housing','resume-housing','reserve-beds','choose-bedroom'): return False
    require(character_at_castle(state,'founder'), 'Return home before arranging accommodation.')
    room_id=action.get('roomId')
    require(room_id in HOUSING_ROOMS, 'Choose an existing housing room.')
    room=state['housingRooms'][room_id]; definition=HOUSING_ROOMS[room_id]
    if kind=='fund-housing':
        require(state['livingWingCompletedOn'] is not None, 'Complete the Proper Living Wing before expanding its accommodation.')
        require(room['status']=='not-started', 'This room is already funded or usable.')
        require(definition.get('region')!='annex' or state['estateAnnex']['status']=='complete', 'Complete the annex access and services before fitting its rooms.')
        require(state['sharedFunds']>=definition['costCrowns'], 'The treasury cannot cover this room’s listed restoration cost.')
        state['sharedFunds']-=definition['costCrowns'];room['status']='in-progress'
        state['activeHousingRoomId']=room_id;state['founderAssignment']='housing'
        add_journal(state,'Funded '+definition['name']+' for '+str(definition['costCrowns'])+' crowns, including its beds and basic furnishings.')
    elif kind=='resume-housing':
        require(room['status']=='in-progress', 'Select a funded, unfinished room.')
        state['activeHousingRoomId']=room_id;state['founderAssignment']='housing'
    elif kind=='reserve-beds':
        require(room['status']=='complete', 'Restore this room before reserving beds.')
        target=action.get('reservedBeds')
        occupied=len(housing_summary(state)['rooms'][room_id]['occupants'])
        require(type(target) is int and 0<=target<=definition['capacityBeds']-occupied-housing_summary(state)['rooms'][room_id]['arrivalReservedBeds'], 'Reserve only whole, unoccupied beds in this room.')
        room['reservedBeds']=target
    else:
        who=action.get('characterId')
        require(who in household_members(state) and character_at_castle(state,who), 'The person must be home to agree a bedroom choice.')
        require(room['status']=='complete', 'Restore this room before moving in.')
        require(character_profile(state,who).get('accommodationPreference')!='private-room' or definition['capacityBeds']==1, 'This person has agreed to a private one-bed room. Respect that preference.')
        if state['bedroomAssignments'][who]==room_id: return True
        require(not estate_expansion.placement_blockers(state,who,room_id),' '.join(estate_expansion.placement_blockers(state,who,room_id)))
        require(housing_summary(state)['rooms'][room_id]['availableBeds']>0, 'No unreserved bed is available here. Choose another room or explicitly release a planned reservation.')
        state['bedroomAssignments'][who]=room_id
        add_journal(state,(character_profile(state,who)['name']+' chose ' if who!='founder' else 'Your scholar moved to ')+definition['name']+'. Existing possessions and personal projects remain theirs.')
        if who=='mira':
            state['conversation'].append({'speaker':'Mira','text':'“'+definition['name']+'? Yes, that suits me. Leave room on the chest for the books I am definitely about to finish.”'})
    return True

def resolve_housing_work(state, summary):
    room_id=state['activeHousingRoomId']
    if not room_id or state['founderAssignment']!='housing' or not character_at_castle(state,'founder'): return
    room=state['housingRooms'][room_id];definition=HOUSING_ROOMS[room_id]
    work=character_approaches.work_step(state,'founder','housing',room['completedWorkPhases'],definition['requiredWorkPhases'],summary)
    room['completedWorkPhases']+=work
    summary.append(definition['name']+': +'+str(work)+' restoration phase(s).')
    if room['completedWorkPhases']>=definition['requiredWorkPhases']:
        room['status']='complete';state['activeHousingRoomId']=None;state['founderAssignment']='rest'
        summary.append(definition['name']+' is usable: '+str(definition['capacityBeds'])+' furnished beds. No occupant is moved automatically.')


# 0.11: bounded spell invention, personal preparation, and a cooperative ritual.
SPELL_FORMS = {
    'warm-twist': {'name':'Warm-twist binding', 'requiredPrinciple':'steady-hearth-wards',
        'requiredProperties':['heat-bearing','binding'], 'roomId':'common-room',
        'description':'Use controlled warmth to loosen silver-ivy fibres, then twist them into binding cord.',
        'effect':'Consume 1 silver ivy when scheduling; produce 2 binding thread after one assigned phase.',
        'castingInputs':{'silver-ivy':1}, 'materialOutput':{'binding-thread':2}, 'crownsOutput':0},
    'root-song': {'name':'Root-song tending', 'requiredPrinciple':'steady-growth',
        'requiredProperties':['botanical','binding'], 'roomId':'conservatory',
        'description':'Guide an established bed through its growth rhythm with attentive practical magic.',
        'effect':'Produce 2 silver ivy after one assigned phase. No casting components or mana fee.',
        'castingInputs':{}, 'materialOutput':{'silver-ivy':2}, 'crownsOutput':0},
    'luminous-copy': {'name':'Luminous transcription', 'requiredPrinciple':'luminous-copying',
        'requiredProperties':['vessel','heat-bearing'], 'roomId':'library',
        'description':'Make and check clean archive copies with a controlled light impression.',
        'effect':'Earn 6 shared crowns after one assigned phase. No casting components or mana fee.',
        'castingInputs':{}, 'materialOutput':{}, 'crownsOutput':6},
}

def spell_preparation_capacity(state,who='founder'):
    return base_spell_capacity(state,who)+int(state['personalAugmentations'][who]['active'])+int(who in household_members(state) and resident_specialties.active(state,'elowen'))

def spell_by_id(state, spell_id):
    require(isinstance(spell_id,str), 'Choose a saved spell.')
    spell=next((item for item in state['spellbook'] if item['id']==spell_id),None)
    require(spell is not None, 'Choose a saved spell.')
    return spell

def spell_blockers(state, spell, casting=False):
    who=spell['ownerId']; definition=SPELL_FORMS[spell['formId']]; blockers=[]
    if state['castingPlans'][who] and state['castingPlans'][who]['status'] in ('active','paused'):blockers.append('Cancel this person’s open casting plan before scheduling separate spell work.')
    if not character_at_castle(state,'founder') or not character_at_castle(state,who):
        blockers.append('Return home with the spell owner to agree this work.')
    for principle in definition['requiredPrinciples']:
        if principle not in character_principles(state,who):
            blockers.append('The owner must learn '+PRINCIPLE_NAMES[principle]+'.')
    if not room_available(state,definition['roomId']):
        blockers.append('Restore the '+ROOMS[definition['roomId']]['name'].lower()+' first.')
    if state['spellWork'][who] is not None:
        blockers.append('Finish this person’s pending spell work first, or cancel a pending casting.')
    if casting:
        if definition.get('field') not in (None,'heal','haste'):
            import combat_magic
            blockers.append('Use this prepared spell in the active field patrol’s combat actions.' if spell['formId'] in combat_magic.SPELLS else 'Use this spell through the expedition’s field-magic controls.')
        if spell['status']!='learned': blockers.append('Complete the two-phase spell test first.')
        if spell['id'] not in state['preparedSpells'][who]: blockers.append('Prepare this learned spell first.')
        for key,count in definition['castingInputs'].items():
            if state['materialInventory'][key]<count: blockers.append('Casting needs '+str(count)+' '+MATERIALS[key]['name']+'.')
    else:
        if spell['status']!='draft': blockers.append('This design has already entered testing.')
        if state['sharedFunds']<4: blockers.append('Testing requires 4 shared crowns.')
        for key in set(spell['materials']):
            count=spell['materials'].count(key)
            if state['materialInventory'][key]<count: blockers.append('Testing needs '+str(count)+' '+MATERIALS[key]['name']+'.')
    return blockers

def spell_view(state, spell):
    return {**deepcopy(spell), 'personalEffect':character_builds.output_description(state,spell['ownerId'],spell['formId']), 'testBlockers':spell_blockers(state,spell),
        'castBlockers':spell_blockers(state,spell,True)}

def spell_ritual_blockers(state):
    blockers=[]
    if state['spellRitual']['status']!='not-started': blockers.append('This one-time ritual has already begun.')
    if not all(character_at_castle(state,who) for who in RITUAL_PARTICIPANTS): blockers.append('Both participants must be home.')
    if state['libraryIndexInstalled'] is not True: blockers.append('Install the living index charm in the library.')
    if not all('reference-binding' in character_principles(state,who) for who in RITUAL_PARTICIPANTS): blockers.append('Both participants must have learned Reference binding.')
    if not any('clear-instruction' in character_principles(state,who) for who in RITUAL_PARTICIPANTS): blockers.append('At least one participant must have learned Clear instruction.')
    if state['sharedFunds']<18: blockers.append('The ritual requires 18 shared crowns.')
    return blockers

def validate_spell_materials(materials, properties):
    require(isinstance(materials,list) and len(materials)==len(properties) and all(isinstance(key,str) and key in MATERIALS for key in materials), 'Choose a supported material for each component slot.')
    for key,property_name in zip(materials,properties):
        require(property_name in MATERIALS[key]['properties'], 'A component must have the '+property_name+' property.')

def require_spell_home(state, who):
    require(isinstance(who,str) and who in household_members(state), 'Choose an available character.')
    require(character_at_castle(state,'founder') and character_at_castle(state,who), 'Return home with this person to agree spell work.')

def apply_spell_action(state, action):
    kind=action.get('type')
    if kind=='inscribe-spell':
        form_id=action.get('formId')
        require(isinstance(form_id,str) and form_id in SPELL_FORMS,'Choose a spell from the authored catalogue.')
        definition=SPELL_FORMS[form_id]
        action={'type':'draft-spell','characterId':action.get('characterId'),'formId':form_id,'name':definition['name'],'intent':definition['description'],'materials':action.get('materials')}
        kind='draft-spell'
    if kind not in ('draft-spell','discard-spell-draft','test-spell','prepare-spells','cast-spell','cancel-spell-casting','start-spell-ritual','resume-spell-ritual'): return False
    if kind in ('start-spell-ritual','resume-spell-ritual'):
        require(all(character_at_castle(state,who) for who in RITUAL_PARTICIPANTS), 'Both participants must be home for the ritual.')
        ritual=state['spellRitual']
        if kind=='start-spell-ritual':
            blockers=spell_ritual_blockers(state);require(not blockers,' '.join(blockers))
            materials=action.get('materials');validate_spell_materials(materials,['vessel','binding','vessel','binding'])
            for key in set(materials): require(state['materialInventory'][key]>=materials.count(key), 'Not enough components for both participants.')
            state['sharedFunds']-=18
            for key in materials: state['materialInventory'][key]-=1
            ritual['status']='in-progress'
            add_journal(state,'The scholar and Mira begin the concordant lesson: 18 crowns and four components committed. Both offer this practical memory exercise; it changes neither personality nor relationships.')
        else: require(ritual['status']=='in-progress','There is no unfinished concordant lesson.')
        for who in RITUAL_PARTICIPANTS: set_character_assignment(state,who,'ritual')
        return True
    if kind=='draft-spell':
        who=action.get('characterId');require_spell_home(state,who)
        form_id=action.get('formId');require(isinstance(form_id,str) and form_id in SPELL_FORMS,'Choose a supported spell form. Free prose cannot grant an unsupported effect.')
        require(not any(item['ownerId']==who and item['formId']==form_id for item in state['spellbook']), 'This person already has a design for that form. Use the existing design.')
        name=text_value(action.get('name'),60); intent=text_value(action.get('intent'),500)
        materials=action.get('materials');validate_spell_materials(materials,SPELL_FORMS[form_id]['requiredProperties'])
        spell={'id':'spell-'+str(state['nextSpellNumber']), 'ownerId':who, 'formId':form_id,
            'name':name, 'intent':intent, 'materials':materials[:], 'status':'draft', 'completedWorkPhases':0, 'castCount':0}
        state['spellbook'].append(spell);state['nextSpellNumber']+=1
        add_journal(state,character_profile(state,who)['name']+' drafted '+name+'. The selected spell form defines its exact effect; no resources committed.')
        return True
    if kind in ('prepare-spells','cancel-spell-casting'):
        who=action.get('characterId');require_spell_home(state,who)
        if kind=='prepare-spells':
            require(state['spellWork'][who] is None or state['spellWork'][who]['kind']!='cast','Resolve or cancel the pending casting before changing preparation.')
            selected=action.get('spellIds');require(isinstance(selected,list) and all(isinstance(key,str) for key in selected),'Choose learned spell identifiers.')
            require(len(selected)==len(set(selected)) and len(selected)+len(state['publicWorkshop']['preparedSpells'].get(who,[]))<=spell_preparation_capacity(state,who),'Prepare unique spells within your available slots.')
            for key in selected:
                spell=spell_by_id(state,key)
                require(spell['ownerId']==who and spell['status']=='learned','Only this person’s successfully tested spells can be prepared.')
            state['preparedSpells'][who]=selected[:]
            plan=state['castingPlans'][who]
            if plan and plan['status']=='active' and plan['spellId'] not in selected:
                plan['status']='paused'
                if character_assignment(state,who)=='spellwork':set_character_assignment(state,who,'rest')
                add_journal(state,character_profile(state,who)['name']+' put the agreed spell aside. Its casting plan is paused until explicitly resumed.')
        else:
            job=state['spellWork'][who];require(job is not None and job['kind']=='cast','There is no pending casting to cancel.')
            for key,count in job['committedInputs'].items(): state['materialInventory'][key]+=count
            state['spellWork'][who]=None
            if character_assignment(state,who)=='spellwork':set_character_assignment(state,who,'rest')
            add_journal(state,character_profile(state,who)['name']+' cancelled the pending casting. Committed casting inputs returned; no time passed.')
        return True
    spell=spell_by_id(state,action.get('spellId'));who=spell['ownerId'];require_spell_home(state,who)
    if kind=='discard-spell-draft':
        require(spell['status']=='draft','Only an uncommitted draft can be discarded.')
        state['spellbook'].remove(spell)
        return True
    casting=kind=='cast-spell';blockers=spell_blockers(state,spell,casting);require(not blockers,' '.join(blockers))
    definition=SPELL_FORMS[spell['formId']]
    if casting:
        target=None
        if definition.get('field')=='heal':
            target=action.get('targetId',who)
            require(isinstance(target,str) and target in household_members(state) and character_at_castle(state,target),'Choose a resident at home to heal.')
            require(field_magic.vitality(state,target)<6,'That person is already at full vitality.')
        if definition.get('support'):
            target=spell_support.target_for(state,definition,who,action.get('targetId'))
            spell_support.check(state,definition,target)
        inputs=definition['castingInputs']
        for key,count in inputs.items():state['materialInventory'][key]-=count
        state['spellWork'][who]={'kind':'cast','spellId':spell['id'],'committedInputs':deepcopy(inputs)}
        if target:state['spellWork'][who]['targetId']=target
        add_journal(state,character_profile(state,who)['name']+' scheduled '+spell['name']+' for one assigned phase. '+definition['effect'])
    else:
        state['sharedFunds']-=4
        for key in spell['materials']:state['materialInventory'][key]-=1
        spell['status']='testing'
        state['spellWork'][who]={'kind':'test','spellId':spell['id']}
        add_journal(state,character_profile(state,who)['name']+' committed 4 crowns and two components to test '+spell['name']+'. Two assigned phases required.')
    set_character_assignment(state,who,'spellwork')
    return True

def spell_ritual_ready(state):
    return state['spellRitual']['status']=='in-progress' and all(character_at_castle(state,who) and character_assignment(state,who)=='ritual' for who in RITUAL_PARTICIPANTS)

def spell_forecast(state):
    rows=[]
    for who,job in state['spellWork'].items():
        if not job:continue
        spell=spell_by_id(state,job['spellId'])
        active=character_at_castle(state,who) and character_assignment(state,who)=='spellwork'
        effect=character_builds.output_description(state,who,spell['formId']) if job['kind']=='cast' else '+1 of 2 testing phases.'
        rows.append(character_profile(state,who)['name']+' · '+spell['name']+': '+(effect if active else 'paused; resume assigned spell work at home.'))
    if state['spellRitual']['status']=='in-progress':rows.append('Concordant lesson: '+('+1 contribution from each participant.' if spell_ritual_ready(state) else 'paused; both participants must be home and assigned to the ritual.'))
    return rows

def resolve_spell_work(state, summary):
    for who,job in state['spellWork'].items():
        if not job or not character_at_castle(state,who) or character_assignment(state,who)!='spellwork':continue
        spell=spell_by_id(state,job['spellId']);definition=SPELL_FORMS[spell['formId']]
        if job['kind']=='test':
            spell['completedWorkPhases']+=1
            summary.append(character_profile(state,who)['name']+' tested '+spell['name']+': '+str(spell['completedWorkPhases'])+' / 2 phases.')
            if spell['completedWorkPhases']<2:continue
            spell['status']='learned'
            summary.append(spell['name']+' is learned. Prepare it explicitly before casting; testing grants no production or advancement.')
        else:
            if definition.get('support'):spell_support.resolve(state,definition,job.get('targetId',who),summary,who)
            if definition.get('field')=='heal':
                field_magic.heal(state,job.get('targetId',who),3+character_approaches.healing_bonus(state,who))
                summary.append('Mending light restored health to '+str(field_magic.vitality(state,job.get('targetId',who)))+'/6.')
            definition=character_builds.casting_output(state,who,spell['formId'])
            for key,count in definition['materialOutput'].items():state['materialInventory'][key]+=count
            state['sharedFunds']+=definition['crownsOutput'];spell['castCount']+=1
            output=', '.join(str(count)+' '+MATERIALS[key]['name'] for key,count in definition['materialOutput'].items()) or (str(definition['crownsOutput'])+' shared crowns' if definition['crownsOutput'] else 'enchantment resolved')
            summary.append(character_profile(state,who)['name']+' cast '+spell['name']+': '+output+'. '+('One agreed casting resolved.' if job.get('fromPlan') else 'Casting complete; repeat only when explicitly scheduled.'))
        continue_plan=False
        if job.get('fromPlan'):
            plan=state['castingPlans'][who];plan['completedCount']+=1
            if plan['completedCount']>=plan['requestedCount']:
                plan['status']='complete'
                summary.append(character_profile(state,who)['name']+' completed the agreed casting plan. No further castings are scheduled.')
            else:continue_plan=plan['status']=='active'
        state['spellWork'][who]=None;set_character_assignment(state,who,'spellwork' if continue_plan else 'rest')
    if spell_ritual_ready(state):
        ritual=state['spellRitual']
        for who in RITUAL_PARTICIPANTS:ritual['contributions'][who]+=1
        summary.append('Concordant lesson: each participant contributed one coordinated phase ('+str(ritual['contributions']['founder'])+' / 2 each).')
        if all(count>=2 for count in ritual['contributions'].values()):
            ritual['status']='complete'
            for who in RITUAL_PARTICIPANTS:set_character_assignment(state,who,'rest')
            summary.append('Concordant lesson complete. Each participant now has three base personal spell slots, plus any active personal blessing. Existing preparation is unchanged.')


# 0.12: a longer, persistent expedition and a recoverable optional complication.
EXPEDITION_SITES['rainward-observatory'] = {
    'id':'rainward-observatory', 'name':'Rainward observatory',
    'description':'The bindery catalogue marks an abandoned weather station above the brook. Its rain channels and clouded lenses may reveal how its keepers collected water and measured light.',
    'approaches':{
        'survey':{'name':'Recover the optical method','description':'Work through three connected encounters to understand the weather lenses. Completed steps and unfinished fieldwork persist across visits.','reward':'Return with Gentle refraction, unlocking a reading prism and glass-clarifying spell.'},
        'salvage':{'name':'Recover the spare lenses','description':'Follow a separate three-encounter route through the station’s accessible stores. Each lead awards its findings once.','reward':'Return with 3 moon glass, 3 binding thread and 24 crowns.'},
    },
}
OBSERVATORY_STEPS = [
    {'id':'rain-shutter','name':'The rain-bound shutter','description':'A narrow channel keeps the shutter swollen and its counterweight damp. Open it without damaging the frame.',
     'choices':{
         'drain-by-hand':{'name':'Clear the channels by hand','phases':2,'description':'A patient, always-available method. Two phases, no consumable cost.'},
         'guide-water':{'name':'Guide the trapped water','phases':1,'principle':'water-guidance','description':'One party member must learn Water guidance. One phase.'},
     }},
    {'id':'lens-rack','name':'The clouded lens rack','description':'The lenses are intact, but the alignment wheel is stiff. Choose how much of the mechanism to investigate.',
     'choices':{
         'clean-lenses':{'name':'Clean and mark the rack carefully','phases':2,'description':'Two phases. Leaves the stubborn auxiliary wheel alone.'},
         'warm-lenses':{'name':'Dry the lens mounts with the packed lantern','phases':1,'lantern':True,'description':'A carried warming lantern frees the mounts in one phase. No charge is consumed.'},
         'open-auxiliary':{'name':'Investigate the auxiliary lens','phases':1,'complication':True,'description':'One phase reveals an extra moon-glass lens, but leaves the rack misaligned. You must realign it before continuing: two manual phases, or one with personal Gentle preservation. The extra lens comes home only with this completed lead.'},
     }},
    {'id':'weather-notes','name':'The weather ledger','description':'Loose diagrams describe how the weather lenses bend and steady light. Cross-reference them before packing the findings.',
     'choices':{
         'copy-ledger':{'name':'Copy the diagrams patiently','phases':2,'description':'Two phases of careful transcription. No special preparation required.'},
         'bind-references':{'name':'Bind the diagram references','phases':1,'principle':'reference-binding','description':'One party member must learn Reference binding. One phase.'},
         'use-field-notes':{'name':'Compare prepared field notes','phases':1,'practice':'field-notes','description':'Prepared field notes on a party member reduce this work to one phase.'},
     }},
]
OBSERVATORY_RECOVERY = {'id':'realign-rack','name':'Realign the auxiliary rack',
    'description':'The extra lens is safe in its mount, but the rack must be aligned before the ledger can be read. This affects only the current fieldwork; the castle and belongings are unharmed.',
    'choices':{
        'align-by-hand':{'name':'Reseat the mounting rings by hand','phases':2,'description':'Two phases. Always available; no resources lost.'},
        'preserve-alignment':{'name':'Hold the rings in gentle preservation','phases':1,'principle':'gentle-preservation','description':'One phase with a party member who has learned Gentle preservation.'},
    }}
PRINCIPLE_NAMES['gentle-refraction']='Gentle refraction'
PRINCIPLE_GUIDE['gentle-refraction']={'source':'Complete the optical-method lead at Rainward observatory and return home.','view':'expeditions','use':'A reading prism for copying income and a spell that clarifies fireglass into moon glass.'}
UTILITY_ARTIFACTS['reading-prism']={'name':'Reading prism','roomId':'library','benefit':'Install in the library: +2 crowns per assigned scholar copying phase. Does not multiply spell income; extra copies do not stack.'}
RECIPES['reading-prism']={'name':'Reading prism','requiredPrinciple':'gentle-refraction','requiredProperties':['vessel','heat-bearing'],'requiredWorkPhases':3,'description':UTILITY_ARTIFACTS['reading-prism']['benefit']}
SPELL_FORMS['clarify-glass']={'name':'Gentle glass clarification','requiredPrinciple':'gentle-refraction','requiredProperties':['vessel','heat-bearing'],'roomId':'library',
    'description':'Separate a fireglass insert along its natural seams and clarify the two useful lenses with steady refraction.',
    'effect':'Consume 1 fireglass when scheduling; produce 2 moon glass after one assigned phase.',
    'castingInputs':{'fireglass':1},'materialOutput':{'moon-glass':2},'crownsOutput':0}

def expedition_party(state):
    expedition=state['expedition']
    if expedition and 'partyIds' in expedition:return expedition['partyIds'][:]
    return ['founder']+([expedition['companionId']] if expedition and expedition.get('companionId') else [])

def observatory_step(progress):
    if progress['complication']:return OBSERVATORY_RECOVERY
    return next((step for step in OBSERVATORY_STEPS if step['id'] not in progress['completedSteps']),None)

def encounter_choice_blockers(state, choice):
    party=expedition_party(state);blockers=field_magic.existing_blockers(state,choice)
    if choice.get('aptitude'):
        import character_approaches
        blockers += character_approaches.party_blockers(state, choice['aptitude'], party)
    if choice.get('principle') and not any(choice['principle'] in character_principles(state,who) for who in party):blockers.append('A party member must learn '+PRINCIPLE_NAMES[choice['principle']]+'. Archive notes or people left at home do not qualify.')
    if choice.get('practice') and not any(choice['practice'] in state['characterDevelopment'][who]['preparedPractices'] for who in party):blockers.append('A party member must have '+PRACTICES[choice['practice']]['name']+' prepared before departure.')
    if choice.get('skill') and not any(skill_rank(state,who,choice['skill'])>=choice['requiredRank'] for who in party):blockers.append('A party member needs '+CHARACTER_SKILLS[choice['skill']]['name']+' rank '+str(choice['requiredRank'])+'. Skills of people left at home do not qualify.')
    if choice.get('lantern') and not state['expedition']['carriedLantern']:blockers.append('Pack a crafted warming lantern before setting out. A lantern left on display is not with the party.')
    return blockers

def encounter_view(state):
    if first_patrol.active(state):return first_patrol.encounter_view(state)
    if roads_we_keep.active(state):return roads_we_keep.encounter_view(state)
    if arms_of_our_own.active(state):return arms_of_our_own.encounter_view(state)
    import party_journeys
    if party_journeys.active(state):return party_journeys.view(state)
    expedition=state['expedition']
    if expedition and expedition['siteId']=='lantern-pavilion':
        import lantern_adventure
        return lantern_adventure.view(state)
    if expedition and expedition['siteId']=='stormwatch-beacon':
        import beacon_expedition
        return beacon_expedition.view(state)
    if expedition and expedition['siteId']=='old-service-road':
        import service_road
        return service_road.view(state)
    if not expedition or expedition['siteId']!='rainward-observatory' or not expedition['chosenApproach']:return None
    progress=state['observatoryProgress'][expedition['chosenApproach']];step=observatory_step(progress)
    return {'progress':deepcopy(progress),'step':deepcopy(step), 'choices':{key:{**deepcopy(choice),'blockers':encounter_choice_blockers(state,choice)} for key,choice in step['choices'].items()} if step else {}}

def resume_observatory(state):
    expedition=state['expedition'];progress=state['observatoryProgress'][expedition['chosenApproach']]
    if progress['pendingWork']:
        step=observatory_step(progress);choice=step['choices'][progress['pendingWork']['methodId']]
        if encounter_choice_blockers(state,choice):expedition['stage']='encounter-choice'
        else:
            expedition['stage']='working';expedition['remainingWorkPhases']=progress['pendingWork']['remainingWorkPhases']
    elif observatory_step(progress) is None:
        expedition['stage']='ready-to-return';expedition['discoveryReady']=True
    else:expedition['stage']='encounter-choice'
    add_journal(state,'Rainward fieldwork selected: '+EXPEDITION_SITES['rainward-observatory']['approaches'][expedition['chosenApproach']]['name']+'. Completed steps and paid work time are retained.')

def apply_encounter_action(state, action):
    if action.get('type')!='choose-encounter-method':return False
    expedition=state['expedition']
    require(expedition is not None and expedition['siteId']=='rainward-observatory' and expedition['stage']=='encounter-choice','There is no encounter method waiting to be chosen.')
    progress=state['observatoryProgress'][expedition['chosenApproach']];step=observatory_step(progress);method=action.get('methodId')
    require(isinstance(method,str) and method in step['choices'],'Choose a method for the current encounter.')
    choice=step['choices'][method];blockers=encounter_choice_blockers(state,choice);require(not blockers,' '.join(blockers))
    field_magic.commit_existing(state,choice)
    progress['pendingWork']={'stepId':step['id'],'methodId':method,'remainingWorkPhases':choice['phases'],'magicPaid':choice.get('castForm')}
    expedition['remainingWorkPhases']=choice['phases'];expedition['stage']='working'
    add_journal(state,step['name']+': '+choice['name']+'. '+str(choice['phases'])+' assigned field phase(s).')
    return True

def resolve_observatory(state):
    expedition=state['expedition'];approach=expedition['chosenApproach']
    progress=state['observatoryProgress'].get(approach)
    if expedition['stage']=='working':
        job=progress['pendingWork'];job['remainingWorkPhases']-=1;expedition['remainingWorkPhases']=job['remainingWorkPhases']
        text='Rainward fieldwork: '+str(job['remainingWorkPhases'])+' phase(s) remain on this method.'
        if not job['remainingWorkPhases']:
            step=observatory_step(progress);choice=step['choices'][job['methodId']]
            if choice.get('complication'):
                progress['complication']='misaligned-rack';progress['bonusMoonGlass']=1
                text='The auxiliary lens is found. The rack is misaligned; choose a recovery method before continuing. No supplies were lost.'
            elif step['id']=='realign-rack':
                progress['complication']=None;progress['completedSteps'].append('lens-rack')
                text='The lens rack is aligned. The extra moon-glass lens is secured for the completed lead’s return.'
            else:
                progress['completedSteps'].append(step['id']);text=step['name']+' completed. Field progress is saved.'
            progress['pendingWork']=None
            if observatory_step(progress) is None:
                expedition['discoveryReady']=True;expedition['stage']='ready-to-return'
                text+=' This lead is complete; bring its findings home.'
            else:expedition['stage']='encounter-choice'
    else:
        rewards=[];party=expedition_party(state)
        if expedition['discoveryReady'] and approach not in state['observatoryDiscoveries']:
            state['observatoryDiscoveries'].append(approach)
            if approach=='survey':
                for who in party:learn_for_character(state,who,'gentle-refraction')
                rewards.append('Gentle refraction learned by the returning party and recorded in the archive. Reading prism and glass clarification are available.')
            else:
                state['materialInventory']['moon-glass']+=3;state['materialInventory']['binding-thread']+=3;rewards.append(distribute_expedition_wealth(state,24))
                rewards.append('3 moon glass and 3 binding thread deposited in shared stores; 24 crowns recovered.')
                if any(focus_effect_active(state,who,'field-case','expedition') for who in party):
                    state['materialInventory']['binding-thread']+=1;rewards.append('The party’s preservation case secured 1 extra binding thread; multiple cases do not stack.')
            if progress['bonusMoonGlass']:
                state['materialInventory']['moon-glass']+=progress['bonusMoonGlass'];rewards.append('1 auxiliary moon-glass lens brought home after realignment.')
            resident_specialties.field_reward(state,rewards)
            for who in party:award_advancement(state,who,'rainward-observatory:'+approach,2,'Completed the multi-stage '+EXPEDITION_SITES['rainward-observatory']['approaches'][approach]['name'].lower())
        else:rewards.append('Returned safely. Rainward encounter progress and unfinished work are saved; no discovery or field reward was deposited.')
        if expedition['restoreLanternDisplay']:state['lanternDisplayed']=True
        state['lastExpeditionReport']={'siteId':'rainward-observatory','approach':approach,'returnedDay':state['dayNumber'],'participants':party[:],'rewards':rewards}
        for who in party:set_character_assignment(state,who,'rest')
        state['expedition']=None
        if 'steady-hearth-wards' in state['archivePrinciples'] and 'steady-hearth-wards' not in state['founderKnownPrinciples']:
            learn_principle(state,'steady-hearth-wards');award_advancement(state,'founder','hearth-understood',1,'Understood steady hearth wards')
            rewards.append('Reviewed the household’s completed hearth research on returning home.')
        text='Your scholar returned safely. '+' '.join(rewards)
    state['lastPhaseSummary']=[line for line in state['lastPhaseSummary'] if not line.startswith('A restful phase.')]
    state['lastPhaseSummary'].append(text);add_journal(state,text)


# Personal investment, distinct from innate attributes and prepared practices.
CHARACTER_SKILLS = {
    'athletics':{'name':'Athletics','maxRank':2,'description':'Training in lifting, climbing and endurance. Each rank adds 2 to relevant optional expedition approach scores.'},
    'diplomacy':{'name':'Diplomacy','maxRank':2,'description':'Negotiation, tact and persuasive delivery. Each rank adds 2 to optional social approach scores. Ordinary conversation choices always remain.'},
    'channeling':{'name':'Channeling','maxRank':2,'description':'Practised magical control. Each rank adds 2 to concentration routes. At combined Resolve + twice Channeling of 9, prepared field boosts gain one charge.'},
    'scholarship':{'name':'Scholarship','maxRank':2,'description':'Each added rank gives +1 work contribution per assigned phase of shared research or living-index study. Does not accelerate personal learning, spell tests or rituals.'},
    'artifice':{'name':'Artifice','maxRank':2,'description':'Each added rank gives +1 work contribution when this person is the assigned artifact maker. Does not accelerate focus work, spell tests or ritual contributions.'},
    'fieldcraft':{'name':'Fieldcraft','maxRank':2,'description':'Rank 1 reduces ordinary two-phase surveys to one phase (does not stack with lanterns or field notes) and opens careful channel work at Rainward. Rank 2 opens precise lens handling there without a lantern. No automatic extra rewards.'},
}

def skill_rank(state,who,skill):
    return state.get('characterSkills',{}).get(who,{}).get(skill,0)

OBSERVATORY_STEPS[0]['choices']['trace-channels']={'name':'Trace a dry approach through the channels','phases':1,'skill':'fieldcraft','requiredRank':1,'description':'One phase with Fieldcraft rank 1 on a party member. Skill offers a practical alternative to Water guidance.'}
OBSERVATORY_STEPS[1]['choices']['handle-lenses']={'name':'Free the mounts with precise field handling','phases':1,'skill':'fieldcraft','requiredRank':2,'description':'One phase with Fieldcraft rank 2 on a party member. No packed lantern needed; leaves the auxiliary lens undisturbed.'}

ORIGINAL_ASSETS['rainward-observatory']='/assets/rooms/rainward-observatory.webp'


# Capacity-backed recruitment; authored sample content, never a canonical first recruit.
RITUAL_PARTICIPANTS=('founder','mira')
CHARACTERS['tamsin']={'name':'Tamsin','role':'Catfolk bookbinder · 20','startingPractices':['careful-assembly'],
    'ambition':'Build a repair notebook that other makers can actually use.'}
TAMSIN_TOPICS={
    'work':{'label':'Ask what work she wants to do','text':'“Binding, careful repair, and archive study. I will help with practical magical work I understand. I am not offering garden shifts or field expeditions at the moment.”'},
    'home':{'label':'Ask what she needs at home','text':'“A small room with one bed and a door I can close. Shared meals are lovely; shared sleeping space is not for me. My tools and clothes remain mine. I can add my professional preservation notes to the shared archive, but my private papers stay private.”'},
    'plans':{'label':'Ask about her own plans','text':'“I want to record repair methods before their makers retire and take the knowledge with them. Thread tension, replacement hinges, ways to dry a warped cover. A working library index would help us find the examples.”'},
}
TAMSIN_ASSIGNMENTS=('rest','archive','crafting','training','inscribing','spellwork','personal-project')

def initialize_recruitment(state):
    state['additionalResidents']={'tamsin':{'status':'unknown','assignment':'rest','knownPrinciples':['gentle-preservation'],
        'discussedTopics':[],'conversation':[], 'wardrobe':{'outerLayer':'none'},'savedStyles':[],
        'completedScenes':[],'sharedFlirtation':False,'relationshipDescription':'Household colleagues; no romance established', 'personalProject':{'status':'not-started','completedWorkPhases':0,'requiredWorkPhases':3}}}
    state['pendingResidentArrival']={}
    who='tamsin'
    state['characterDevelopment'][who]={'learnedPractices':['careful-assembly'],'preparedPractices':[],'advancementAwards':{}}
    state['trainingProjects'][who]=None
    state['characterSkills'][who]={key:0 for key in CHARACTER_SKILLS}
    state['signatureFocuses'][who]={'name':'Binder’s bodkin','capacity':1,'inscriptions':[],'householdLoadout':[],'expeditionLoadout':[]}
    state['focusProjects'][who]=None;state['preparedSpells'][who]=[];state['spellWork'][who]=None
    state['utilityArtifactPlacements'].setdefault('binding-press',False)

def household_members(state):
    return (['founder'] if state.get('startType')=='fresh' else ['founder','mira'])+[who for who,record in state.get('additionalResidents',{}).items() if record['status']=='resident']

def household_resident_room(state,who):
    import room_life
    return room_life.location(state,who)

def candidate_view(state):
    record=state['additionalResidents']['tamsin'];unlocked='salvage' in state['binderyDiscoveries']
    blockers=[]
    if not character_at_castle(state,'founder'):blockers.append('Return home to discuss a household invitation.')
    if record['status']!='contacted':blockers.append('Meet Tamsin before inviting her to live here.')
    if len(record['discussedTopics'])<len(TAMSIN_TOPICS):blockers.append('Discuss her work, home preferences and personal plans first.')
    rooms=[key for key,value in housing_summary(state)['rooms'].items() if HOUSING_ROOMS[key]['capacityBeds']==1 and value['availableBeds']>0]
    if not rooms:blockers.append('Provide an available, unreserved one-bed room. Tamsin does not agree to shared sleeping accommodation.')
    return {'unlocked':unlocked,'characterId':'tamsin','status':record['status'],'profile':deepcopy(character_profile(state,'tamsin')) if unlocked else None,
        'topics':deepcopy(TAMSIN_TOPICS) if unlocked else {},'discussedTopics':record['discussedTopics'][:],
        'conversation':deepcopy(record['conversation']), 'eligibleRoomIds':rooms,'invitationBlockers':blockers,
        'personalProject':deepcopy(record['personalProject']), 'currentRoomId':household_resident_room(state,'tamsin')}

def apply_recruitment_action(state,action):
    kind=action.get('type')
    if kind not in ('meet-candidate','talk-candidate','invite-candidate','assign-character','start-resident-project','resident-free-text','style-resident','save-resident-style','load-resident-style','join-resident-scene','move-arrival','cancel-arrival'):return False
    require(character_at_castle(state,'founder'),'Return your scholar home to agree household plans.')
    if kind in ('move-arrival','cancel-arrival'):
        who=action.get('characterId')
        require(who=='tamsin' and state['additionalResidents']['tamsin']['status']=='arriving','Choose an agreed arrival that has not happened yet.')
        if kind=='move-arrival':
            room=action.get('roomId')
            reserve_arrival(state,who,room,'recruitment','tamsin')
            state['pendingResidentArrival']['roomId']=room
            add_journal(state,'Tamsin’s arrival is now reserved in '+ROOMS[room]['name']+'. No time passed.')
        else:
            state['arrivalReservations'].pop('arrival:'+who,None)
            state['pendingResidentArrival']={}
            state['additionalResidents'][who]['status']='contacted'
            add_journal(state,'Tamsin’s arrival was put aside. The bed is released; her identity and conversations are kept. You can discuss the invitation again.')
        return True
    if kind=='assign-character':
        who=action.get('characterId');assignment=action.get('assignment')
        require(isinstance(who,str) and who in household_members(state),'Choose an existing household member.')
        if who in ('founder','mira'):
            return apply_management_action(state,{'type':'assign-founder' if who=='founder' else 'assign-resident','assignment':assignment})
        require(character_at_castle(state,who),'This resident is away; change their work after returning.')
        require(assignment in character_profile(state,who).get('offeredAssignments',TAMSIN_ASSIGNMENTS),'This resident has not offered that assignment.')
        require(assignment!='archive' or state['researchStatus']=='in-progress' or state['activeResearchId'] is not None,'There is no active research to help.')
        require(assignment!='crafting' or state['craftingProject'] is not None and state['craftingProject']['crafterId']==who,'Start an artifact with this person as its maker first.')
        require(assignment!='personal-project' or state['additionalResidents'][who]['personalProject']['status']=='in-progress','Agree the personal notebook project first.')
        validate_development_assignment(state,who,assignment);set_character_assignment(state,who,assignment)
        return True
    require(action.get('characterId','tamsin')=='tamsin','Choose the available bookbinder contact.')
    require(action.get('characterId','tamsin')=='tamsin','Choose Tamsin for this conversation or project.')
    record=state['additionalResidents']['tamsin']
    if kind in ('style-resident','save-resident-style','load-resident-style','join-resident-scene'):
        require(record['status']=='resident','Tamsin must have arrived before spending time together.')
        if kind=='style-resident':
            layer=action.get('outerLayer');require(layer in ('none','plum-shawl'),'Choose an offered outer layer.')
            record['wardrobe']['outerLayer']=layer
            import outfit_progression
            outfit_progression.clear_selection(state,'tamsin')
            import character_customization
            character_customization.clear_style(state,'tamsin')
            state.get('residentCurrentStyles',{}).pop('tamsin',None)
        elif kind=='save-resident-style':
            name=text_value(action.get('name'),40)
            existing=next((style for style in record['savedStyles'] if style['name']==name),None)
            require(existing is not None or len(record['savedStyles'])<20,'Keep up to twenty named styles per resident.')
            style={'name':name,'outerLayer':record['wardrobe']['outerLayer']}
            if existing is not None:existing.update(style)
            else:record['savedStyles'].append(style)
        elif kind=='load-resident-style':
            name=action.get('name');style=next((style for style in record['savedStyles'] if style['name']==name),None)
            require(style is not None,'Choose one of Tamsin’s saved styles.')
            record['wardrobe']['outerLayer']=style['outerLayer']
            import outfit_progression
            outfit_progression.clear_selection(state,'tamsin')
            import character_customization
            character_customization.clear_style(state,'tamsin')
            state.get('residentCurrentStyles',{}).pop('tamsin',None)
        else:
            scene=action.get('sceneId');require(scene in ('tea-and-margins','a-playful-margin'),'Choose an offered scene.')
            require(record['personalProject']['status']=='complete','Her notebook offers a reason to linger over tea after it is complete.')
            require(scene!='a-playful-margin' or 'tea-and-margins' in record['completedScenes'],'Share the offered tea first.')
            if scene in record['completedScenes']:return True
            record['completedScenes'].append(scene)
            if scene=='tea-and-margins':
                line='She sets two cups beside the finished notebook. “A margin is not wasted space. It is where the next reader gets to disagree.” You trade favourite annotations until the tea cools. Nothing needs to become a project.'
            else:
                line='“You keep finding reasons to sit at my end of the table,” Tamsin observes. You admit the company is part of the attraction. Her smile warms. “Good. Mine too. A little flirting suits me; let us see where it goes, without promises.”'
                record['sharedFlirtation']=True
                record['relationshipDescription']='Comfortable colleagues with a mutually welcomed flirtation; no further intimacy promised'
                state['resonancePoints']+=2
            record['conversation'].append({'speaker':'Tamsin','text':line})
            record['conversation']=record['conversation'][-60:]
            add_journal(state,'Shared '+('tea and marginal notes' if scene=='tea-and-margins' else 'a mutually welcomed flirtation')+' with Tamsin. The optional scene is remembered; repeating it grants nothing.')
        return True
    if kind=='resident-free-text':
        require(record['status']=='resident','This resident must have arrived before saving a conversation line.')
        line=text_value(action.get('text'))
        record['conversation'].append({'speaker':'You','text':line})
        record['conversation']=record['conversation'][-60:]
        return True
    if kind=='start-resident-project':
        require(record['status']=='resident','Tamsin must have arrived and agreed to stay first.')
        project=record['personalProject'];require(project['status']=='not-started','This personal project has already begun.')
        require(state['libraryIndexInstalled'],'Install the living index charm before beginning the repair notebook.')
        require(state['sharedFunds']>=8 and state['materialInventory']['binding-thread']>=2,'The notebook requires 8 crowns and 2 binding thread.')
        state['sharedFunds']-=8;state['materialInventory']['binding-thread']-=2
        project['status']='in-progress';set_character_assignment(state,'tamsin','personal-project')
        record['conversation'].append({'speaker':'Tamsin','text':'“Yes. Three quiet work phases, a little cord, and I can make this more useful than another stack of loose notes.”'})
        add_journal(state,'Tamsin began her repair notebook: 8 crowns and 2 binding thread committed. Her own assignment resolves its three phases.')
        return True
    require('salvage' in state['binderyDiscoveries'],'Recover the bindery supplies and bring their correspondence home to find this contact.')
    if kind=='meet-candidate':
        require(record['status']=='unknown','The introduction has already happened.')
        record['status']='contacted';record['conversation'].append({'speaker':'Tamsin','text':'“The bindery keeper passed along your note. I am Tamsin. I mend books, dislike waste, and prefer a workbench to a grand promise. Shall we see whether this would suit us both?”'})
        add_journal(state,'Met Tamsin, a bookbinder introduced through the recovered bindery correspondence. Her work, home preferences and plans need discussion before a household invitation.')
    elif kind=='talk-candidate':
        require(record['status'] in ('contacted','resident'),'Tamsin must be available for this conversation.')
        topic=action.get('topic');require(isinstance(topic,str) and topic in TAMSIN_TOPICS,'Choose an offered conversation topic.')
        if topic not in record['discussedTopics']:
            record['discussedTopics'].append(topic);record['conversation'].append({'speaker':'Tamsin','text':TAMSIN_TOPICS[topic]['text']})
    else:
        view=candidate_view(state);require(not view['invitationBlockers'],' '.join(view['invitationBlockers']))
        room=action.get('roomId');require(room in view['eligibleRoomIds'],'Offer an available private one-bed room.')
        reserve_arrival(state,'tamsin',room,'recruitment','tamsin')
        state['pendingResidentArrival']={'characterId':'tamsin','roomId':room}
        record['status']='arriving';record['conversation'].append({'speaker':'Tamsin','text':'“That room and those terms suit me. I would like to stay. Keep the bed for me; I will bring my things next phase.”'})
        add_journal(state,'Tamsin accepted the invitation. Her arrival bed is held separately from general reservations; she arrives on the next explicit Advance.')
    return True

def resolve_resident_arrivals(state):
    arrival=state['pendingResidentArrival']
    if not arrival:return
    who=arrival['characterId']
    blockers=arrival_blockers(state,'arrival:'+who)
    if blockers:
        state['lastPhaseSummary'].append(character_profile(state,who)['name']+' is waiting to arrive: '+' '.join(blockers))
        return
    state['arrivalReservations'].pop('arrival:'+who)
    state['additionalResidents'][who]['status']='resident'
    state['bedroomAssignments'][who]=arrival['roomId'];state['pendingResidentArrival']={}
    # The contact explicitly offers professional magical notes, not private memories.
    for principle in character_principles(state,who):
        if principle not in state['archivePrinciples']:state['archivePrinciples'].append(principle)
    text=character_profile(state,who)['name']+' arrived, unpacked in '+ROOMS[state['bedroomAssignments'][who]]['name']+' and joined the household. She is following her own routine; no work was assigned automatically.'
    state['lastPhaseSummary'].append(text);add_journal(state,text)

def resident_project_forecast(state):
    rows=[]
    for who,record in state.get('additionalResidents',{}).items():
        if who!='tamsin':continue
        if record['personalProject']['status']=='in-progress':rows.append(character_profile(state,who)['name']+' · repair notebook: '+('+1 work phase.' if character_at_castle(state,who) and character_assignment(state,who)=='personal-project' else 'paused; assign her personal project to continue.'))
    if state.get('pendingResidentArrival'):
        blockers=arrival_blockers(state,'arrival:'+state['pendingResidentArrival']['characterId'])
        rows.append('Arrival paused: '+' '.join(blockers) if blockers else 'Tamsin arrives and occupies her agreed, reserved bed. No assignment starts automatically.')
    return rows

def resolve_resident_project(state,summary):
    for who,record in state.get('additionalResidents',{}).items():
        if who!='tamsin':continue
        project=record['personalProject']
        if project['status']!='in-progress' or not character_at_castle(state,who) or character_assignment(state,who)!='personal-project':continue
        project['completedWorkPhases']+=1;summary.append(character_profile(state,who)['name']+' worked on her repair notebook: '+str(project['completedWorkPhases'])+' / 3 phases.')
        if project['completedWorkPhases']==project['requiredWorkPhases']:
            project['status']='complete';set_character_assignment(state,who,'rest');learn_for_character(state,who,'joined-fibres')
            award_advancement(state,who,'repair-notebook',2,'Completed her practical repair notebook')
            summary.append('Tamsin completed her repair notebook and recorded Joined fibres in the archive. She has learned the principle; others may study it. The binding press recipe is available.')

PRINCIPLE_NAMES['joined-fibres']='Joined fibres'
PRINCIPLE_GUIDE['joined-fibres']={'source':'Welcome Tamsin and complete her offered repair-notebook project.','view':'contacts','use':'A binding press for the library: +1 assigned artifact work contribution for its maker.'}
UTILITY_ARTIFACTS['binding-press']={'name':'Binding press','roomId':'library','benefit':'Install in the library: +1 artifact work contribution per assigned crafting phase from the active maker. Extra copies do not stack; spell testing and focus work are unchanged.'}
RECIPES['binding-press']={'name':'Binding press','requiredPrinciple':'joined-fibres','requiredProperties':['vessel','binding'],'requiredWorkPhases':3,'description':UTILITY_ARTIFACTS['binding-press']['benefit']}

ORIGINAL_ASSETS['tamsin']='/assets/portraits/tamsin.webp'




# Shared necessities and discretionary money remain distinct. All balances use crowns.
EXPEDITION_WEALTH_PLANS={
    'shared':{'name':'All cash to the household','householdPercent':100},
    'quarter-personal':{'name':'75% household · 25% party','householdPercent':75},
    'half-personal':{'name':'50% household · 50% party','householdPercent':50},
}
PERSONAL_PURCHASES={
    'scholar-journal':{'name':'A private field journal','ownerId':'founder','costCrowns':4,'description':'A personal notebook for thoughts that need not become household research.'},
    'poetry-book':{'name':'A collection of terrible poetry','ownerId':'mira','costCrowns':4,'description':'Mira has asked to add this cheerfully dubious little volume to her own shelf.'},
    'woven-bookmark':{'name':'A handwoven bookmark','ownerId':'tamsin','costCrowns':3,'description':'Tamsin has picked a plain violet woven bookmark for her own evening reading.'},
}

def money_entry(state,reason,amount,source,destination):
    state['moneyJournal'].append({'dayNumber':state['dayNumber'],'phase':state['currentDayPhase'],'reason':reason,'crowns':amount,'from':source,'to':destination})
    state['moneyJournal']=state['moneyJournal'][-80:]

def apply_finance_action(state,action):
    kind=action.get('type')
    if kind not in ('set-allowance-plan','set-expedition-wealth-plan','allocate-personal-funds','buy-personal-item','give-personal-item'):return False
    require(character_at_castle(state,'founder'),'Return home to agree financial plans and personal purchases.')
    if kind=='set-expedition-wealth-plan':
        plan=action.get('planId');require(isinstance(plan,str) and plan in EXPEDITION_WEALTH_PLANS,'Choose an offered standing wealth arrangement.')
        state['expeditionWealthPlan']=plan
        add_journal(state,'Agreed expedition cash arrangement: '+EXPEDITION_WEALTH_PLANS[plan]['name']+'. It is captured at departure; unusual materials and discoveries stay intact.')
        return True
    if kind=='set-allowance-plan':
        amounts=action.get('dailyCrowns');floor=action.get('minimumTreasuryCrowns')
        require(isinstance(amounts,dict) and set(amounts)==set(household_members(state)),'Set an allowance for each current household member.')
        require(all(type(value) is int and 0<=value<=10 for value in amounts.values()),'Daily allowances must be whole crowns from 0 to 10 per person.')
        require(type(floor) is int and 0<=floor<=1000,'Keep a shared treasury floor from 0 to 1000 whole crowns.')
        state['householdAllowancePlan']={'dailyCrowns':{who:amounts.get(who,0) for who in state['people']},'minimumTreasuryCrowns':floor}
        add_journal(state,'Updated discretionary allowances. They resolve together only when evening advances to morning; insufficient funds skip the whole payment without debt.')
        return True
    who=action.get('characterId')
    require(isinstance(who,str) and who in household_members(state),'Choose a current household member.')
    if kind=='allocate-personal-funds':
        amount=action.get('crowns')
        require(type(amount) is int and 1<=amount<=1000,'Allocate 1 to 1000 whole crowns.')
        require(state['sharedFunds']-amount>=state['householdAllowancePlan']['minimumTreasuryCrowns'],'This allocation would cross the protected shared treasury floor.')
        state['sharedFunds']-=amount;state['personalFunds'][who]+=amount
        money_entry(state,'Agreed discretionary allocation',amount,'household',who)
    else:
        item=action.get('itemId');require(isinstance(item,str) and item in PERSONAL_PURCHASES,'Choose a listed personal purchase.')
        definition=PERSONAL_PURCHASES[item]
        require(definition['ownerId']==who,'This purchase belongs to a different person’s offered interests.')
        require(character_at_castle(state,who),'Wait until this person is home to confirm the purchase.')
        require(item not in state['personalPossessions'][who],'This personal possession is already owned.')
        if kind=='give-personal-item':
            require(who!='founder','Choose another household member for a gift; your scholar has a personal purchase option.')
            require(state['sharedFunds']-definition['costCrowns']>=state['householdAllowancePlan']['minimumTreasuryCrowns'],'This gift would cross the protected discretionary treasury floor.')
            state['sharedFunds']-=definition['costCrowns']
            money_entry(state,'Gift for '+character_profile(state,who)['name']+': '+definition['name'],definition['costCrowns'],'household','market')
            text=character_profile(state,who)['name']+' accepted the offered '+definition['name'].lower()+' as a household gift.'
        else:
            require(state['personalFunds'][who]>=definition['costCrowns'],'This person needs enough discretionary money; shared funds are not spent automatically.')
            state['personalFunds'][who]-=definition['costCrowns']
            money_entry(state,definition['name'],definition['costCrowns'],who,'market')
            text=character_profile(state,who)['name']+' bought '+definition['name'].lower()+' with personal money.'
        state['personalPossessions'][who].append(item)
        add_journal(state,text+' It remains a personal possession; no ability, affection or Resonance was awarded.')
    return True

def allowance_forecast(state):
    amounts=state['householdAllowancePlan']['dailyCrowns'];total=sum(amounts[who] for who in household_members(state))
    if not total:return []
    if state['currentDayPhase']!='evening':return ['Personal allowances: '+str(total)+' crowns scheduled at the next morning boundary, not this phase.']
    return ['Personal allowances: '+str(total)+' shared crowns scheduled after this phase’s income, only if the full payment preserves the '+str(state['householdAllowancePlan']['minimumTreasuryCrowns'])+'-crown treasury floor. Otherwise everyone’s payment waits until another day; no debt accrues.']

def resolve_allowances(state):
    if state['currentDayPhase']!='evening':return
    plan=state['householdAllowancePlan'];members=household_members(state)
    total=sum(plan['dailyCrowns'][who] for who in members)
    if not total:return
    if state['sharedFunds']-total<plan['minimumTreasuryCrowns']:
        state['lastPhaseSummary'].append('Personal allowances skipped for everyone: the full payment would cross the protected treasury floor. No debt or missed-payment balance accrues.')
        return
    state['sharedFunds']-=total
    for who in members:
        amount=plan['dailyCrowns'][who]
        if amount:
            state['personalFunds'][who]+=amount;money_entry(state,'Daily discretionary allowance',amount,'household',who)
    state['lastPhaseSummary'].append('Transferred '+str(total)+' shared crowns to personal wallets under the daily allowance plan. This creates no new money.')

def distribute_expedition_wealth(state,total):
    expedition=state['expedition'];party=expedition_party(state)
    plan=EXPEDITION_WEALTH_PLANS[expedition.get('wealthPlan','shared')]
    # Divide the personal share into whole equal crowns; indivisible remainders stay shared.
    each=(total*(100-plan['householdPercent'])//100)//len(party)
    shared=total-each*len(party);state['sharedFunds']+=shared
    if shared:money_entry(state,'Returned expedition wealth',shared,'expedition','household')
    for who in party:
        if each:
            state['personalFunds'][who]+=each;money_entry(state,'Returned expedition share',each,'expedition',who)
    return str(total)+' expedition crowns allocated: '+str(shared)+' shared'+(', '+str(each)+' for each returning participant' if each else '')+'. Whole-crown remainders stay shared.'


# One bounded standing work agreement; money held here is not available to other spending.
def delegation_view(state,order):
    required={key:order['materials'].count(key) for key in set(order['materials'])}
    missing={key:max(0,count-max(0,state['materialInventory'][key]-state['materialReserveTargets'][key])) for key,count in required.items()}
    cost=sum(count*MATERIALS[key]['price'] for key,count in missing.items())
    agreement=order.get('delegation');blockers=[]
    if order['completedCount']>=order['requestedCount']:blockers.append('This order is complete.')
    if not character_at_castle(state,order['crafterId']):blockers.append('The agreed maker is away.')
    if RECIPES[order['recipeId']]['requiredPrinciple'] not in character_principles(state,order['crafterId']):blockers.append('The maker must learn the recipe.')
    if agreement:
        if agreement['status']!='active':blockers.append('The standing agreement is '+agreement['status']+'.')
        if character_assignment(state,order['crafterId'])!='crafting':blockers.append('The maker has another assignment; explicitly resume the agreement to continue.')
        if cost>agreement['remainingBudgetCrowns']:blockers.append('The next copy needs '+str(cost)+' crowns for missing unreserved components; '+str(agreement['remainingBudgetCrowns'])+' remain in its budget.')
    if state['craftingProject']:blockers.append('The shared workbench is occupied. The next copy waits.')
    return {'missingMaterials':missing,'nextPurchaseCostCrowns':cost,'blockers':blockers}

def release_delegation_budget(state,order,status):
    agreement=order['delegation'];amount=agreement['remainingBudgetCrowns']
    if amount:
        state['sharedFunds']+=amount
        money_entry(state,'Unused work-order budget returned',amount,order['id'],'household')
    agreement['returnedCrowns']+=amount;agreement['remainingBudgetCrowns']=0;agreement['status']=status
    add_journal(state,order['id']+' agreement '+status+'. '+str(amount)+' unspent crowns returned; completed items and committed work are kept.')

def apply_delegation_action(state,action):
    kind=action.get('type')
    if kind not in ('delegate-work-order','pause-delegation','resume-delegation','add-delegation-budget','revoke-delegation'):return False
    require(character_at_castle(state,'founder'),'Return home to change a standing work agreement.')
    order=next((item for item in state['workOrders'] if item['id']==action.get('orderId')),None)
    require(order is not None,'Choose a saved work order.')
    who=order['crafterId'];agreement=order.get('delegation')
    require(who in household_members(state),'The proposed maker is not a household member.')
    if kind=='revoke-delegation':
        require(agreement is not None and agreement['status'] in ('active','paused'),'There is no open agreement to revoke.')
        release_delegation_budget(state,order,'revoked')
        if not (state['craftingProject'] and state['craftingProject']['crafterId']==who) and character_assignment(state,who)=='crafting':set_character_assignment(state,who,'rest')
        return True
    require(character_at_castle(state,who),'Both people must be home to agree or resume this work.')
    if kind=='delegate-work-order':
        require(not any(item.get('delegation') and item['delegation']['status'] in ('active','paused') for item in state['workOrders']),'Only one standing work agreement is supported. Revoke or finish the existing one first.')
        require(order['completedCount']<order['requestedCount'],'This order is already complete.')
        require(RECIPES[order['recipeId']]['requiredPrinciple'] in character_principles(state,who),'The maker must learn this recipe before agreeing the work.')
        require(state['craftingProject'] is None,'Finish the active artifact before agreeing a delegated batch.')
        amount=action.get('budgetCrowns')
        require(type(amount) is int and 0<=amount<=1000,'Reserve a whole-crown budget from 0 to 1000.')
        require(state['sharedFunds']>=amount,'The shared treasury cannot cover this reserved project budget.')
        state['sharedFunds']-=amount
        order['delegation']={'status':'active','allocatedCrowns':amount,'remainingBudgetCrowns':amount,'spentCrowns':0,'returnedCrowns':0}
        if amount:money_entry(state,'Reserved agreed work-order budget',amount,'household',order['id'])
        set_character_assignment(state,who,'crafting')
        add_journal(state,character_profile(state,who)['name']+' agreed to finish '+order['id']+' within '+str(amount)+' reserved crowns. Missing unreserved components can be bought only within that budget. Advance resolves work; nothing starts offline.')
        return True
    require(agreement is not None and agreement['status'] in ('active','paused'),'This work order has no open agreement.')
    if kind=='add-delegation-budget':
        amount=action.get('budgetCrowns')
        require(type(amount) is int and 1<=amount<=1000 and agreement['allocatedCrowns']+amount<=1000,'Add whole crowns without exceeding the 1000-crown total agreement limit.')
        require(state['sharedFunds']>=amount,'The shared treasury cannot cover this additional budget.')
        state['sharedFunds']-=amount;agreement['remainingBudgetCrowns']+=amount;agreement['allocatedCrowns']+=amount
        money_entry(state,'Added agreed work-order budget',amount,'household',order['id'])
    elif kind=='pause-delegation':
        agreement['status']='paused'
        if character_assignment(state,who)=='crafting' and (not state['craftingProject'] or state['craftingProject'].get('workOrderId')==order['id']):set_character_assignment(state,who,'rest')
    else:
        require(not state['craftingProject'] or state['craftingProject']['crafterId']!=who or state['craftingProject'].get('workOrderId')==order['id'],'This maker has a different committed artifact. Finish it before resuming this agreement.')
        agreement['status']='active';set_character_assignment(state,who,'crafting')
    return True

def resolve_delegated_order(state):
    for order in state['workOrders']:
        agreement=order.get('delegation')
        if not agreement or agreement['status']!='active':continue
        view=delegation_view(state,order)
        if view['blockers']:return
        cost=view['nextPurchaseCostCrowns']
        agreement['remainingBudgetCrowns']-=cost;agreement['spentCrowns']+=cost
        for material,count in view['missingMaterials'].items():state['materialInventory'][material]+=count
        if cost:money_entry(state,'Components for delegated copy',cost,order['id'],'market')
        for material in order['materials']:state['materialInventory'][material]-=1
        state['craftingProject']={'recipeId':order['recipeId'],'materials':order['materials'][:],'completedWorkPhases':0,'crafterId':order['crafterId'],'workOrderId':order['id']}
        add_journal(state,order['id']+': components committed for one delegated copy, '+str(cost)+' reserved crowns spent. Protected stock and personal wallets were untouched.')
        return

def delegation_forecast(state):
    rows=[]
    for order in state['workOrders']:
        agreement=order.get('delegation')
        if not agreement or agreement['status'] not in ('active','paused'):continue
        project=state['craftingProject']
        if project and project.get('workOrderId')==order['id']:
            rows.append(order['id']+': committed copy progresses only while its maker is assigned; remaining budget '+str(agreement['remainingBudgetCrowns'])+' crowns.')
        else:
            view=delegation_view(state,order)
            rows.append(order['id']+': '+(' '.join(view['blockers']) if view['blockers'] else 'next Advance buys missing unreserved components for '+str(view['nextPurchaseCostCrowns'])+' budget crowns and works on one copy.'))
    return rows


# Agreed professional lessons: both people use their primary phase, never pooled mastery.
def release_teacher(state,project):
    teacher=project.get('teacherId')
    if teacher and character_assignment(state,teacher)=='teaching':set_character_assignment(state,teacher,'rest')

def lesson_involvement(state,who):
    return any(project and project.get('teacherId') and who in (learner,project['teacherId']) for learner,project in state['trainingProjects'].items())

def lesson_offers(state,learner):
    offers=[];sheet=character_sheet(state,learner)
    for teacher in household_members(state):
        if teacher==learner:continue
        subjects=[('principle',key) for key in character_principles(state,teacher) if key not in character_principles(state,learner)]
        subjects += [('skill',key) for key in sheet['offeredSkills'] if skill_rank(state,teacher,key)>skill_rank(state,learner,key)]
        for kind,target in subjects:
            blockers=[]
            if not all(character_at_castle(state,who) for who in ('founder',learner,teacher)):blockers.append('Everyone involved in planning must be home.')
            if state['trainingProjects'][learner] or state['trainingProjects'][teacher]:blockers.append('Finish or cancel existing learning projects first.')
            if lesson_involvement(state,learner) or lesson_involvement(state,teacher):blockers.append('One of these people already has an agreed lesson.')
            if kind=='skill' and sheet['availableAdvancement']<2:blockers.append('The learner needs 2 earned, unspent advancement.')
            offers.append({'teacherId':teacher,'kind':kind,'targetId':target,'name':PRINCIPLE_NAMES[target] if kind=='principle' else CHARACTER_SKILLS[target]['name']+' rank '+str(skill_rank(state,learner,target)+1),'blockers':blockers})
    return offers

def lesson_blockers(state,learner):
    project=state['trainingProjects'][learner];teacher=project['teacherId'];blockers=[]
    if not character_at_castle(state,learner) or not character_at_castle(state,teacher):blockers.append('Both people must be at the castle.')
    if character_assignment(state,learner)!='training' or character_assignment(state,teacher)!='teaching':blockers.append('Lesson paused: resume both agreed assignments.')
    if project['kind']=='principle' and project['targetId'] not in character_principles(state,teacher):blockers.append('The teacher no longer knows this principle.')
    if project['kind']=='skill' and skill_rank(state,teacher,project['targetId'])<project['targetRank']:blockers.append('The teacher must still have the rank being taught.')
    return blockers

def apply_lesson_action(state,action):
    kind=action.get('type')
    if kind not in ('start-lesson','resume-lesson'):return False
    require(character_at_castle(state,'founder'),'Return home to agree lesson plans.')
    learner=action.get('learnerId')
    require(isinstance(learner,str) and learner in household_members(state),'Choose a current household learner.')
    project=state['trainingProjects'][learner]
    if kind=='resume-lesson':
        require(project is not None and project.get('teacherId'),'This person has no agreed lesson to resume.')
        teacher=project['teacherId']
        require(character_at_castle(state,learner) and character_at_castle(state,teacher),'Both people must be home to resume.')
        require(state['trainingProjects'][teacher] is None,'The teacher must finish or cancel their own learning project first.')
        require(project['kind']!='skill' or skill_rank(state,teacher,project['targetId'])>=project['targetRank'],'The teacher no longer has the rank being taught. Cancel this lesson to release its reserved advancement.')
    else:
        teacher=action.get('teacherId');subject=action.get('subjectKind');target=action.get('targetId')
        offer=next((item for item in lesson_offers(state,learner) if item['teacherId']==teacher and item['kind']==subject and item['targetId']==target),None)
        require(offer is not None,'Choose a principle this teacher knows or a higher skill rank they have and the learner offers to study.')
        require(not offer['blockers'],' '.join(offer['blockers']))
        project={'kind':subject,'targetId':target,'teacherId':teacher,'completedWorkPhases':0,'requiredWorkPhases':1}
        if subject=='skill':project['targetRank']=skill_rank(state,learner,target)+1
        state['trainingProjects'][learner]=project
        add_journal(state,character_profile(state,teacher)['name']+' agreed to teach '+offer['name']+' to '+character_profile(state,learner)['name']+'. One shared phase uses both primary assignments; skill lessons reserve the learner’s normal 2 advancement.')
    set_character_assignment(state,learner,'training');set_character_assignment(state,teacher,'teaching')
    return True


# Finite practical-magic plans. Inputs are checked before this phase's production.
def casting_plan_view(state,who):
    plan=state['castingPlans'][who]
    if plan is None:return None
    spell=spell_by_id(state,plan['spellId']);definition=SPELL_FORMS[spell['formId']];blockers=[]
    if definition.get('support'):blockers.append('Work enchantments are cast individually with an explicit recipient.')
    if plan['status']!='active':blockers.append('Plan is '+plan['status']+'.')
    if not character_at_castle(state,who):blockers.append('The caster is away.')
    if character_assignment(state,who)!='spellwork':blockers.append('Another primary assignment is active; explicitly resume this plan.')
    if state['spellWork'][who]:blockers.append('A committed spell job must finish first.')
    if spell['status']!='learned' or spell['id'] not in state['preparedSpells'][who]:blockers.append('The agreed spell must be personally tested and prepared.')
    if any(p not in character_principles(state,who) for p in definition['requiredPrinciples']):blockers.append('The caster must learn every required principle.')
    if not room_available(state,definition['roomId']):blockers.append('The working needs its restored room.')
    for material,count in definition['castingInputs'].items():
        if state['materialInventory'][material]-state['materialReserveTargets'][material]<count:blockers.append('Need '+str(count)+' unreserved '+MATERIALS[material]['name']+' for the next casting.')
    return {**deepcopy(plan),'spellName':spell['name'],'effect':character_builds.output_description(state,who,spell['formId']),'blockers':blockers}

def apply_casting_plan_action(state,action):
    kind=action.get('type')
    if kind not in ('plan-castings','pause-casting-plan','resume-casting-plan','cancel-casting-plan'):return False
    who=action.get('characterId');require_spell_home(state,who)
    require(who in household_members(state),'Choose a current household caster.')
    plan=state['castingPlans'][who]
    if kind=='plan-castings':
        require(plan is None or plan['status'] in ('complete','cancelled'),'Finish or cancel this person’s existing casting plan first.')
        spell=spell_by_id(state,action.get('spellId'));count=action.get('requestedCount')
        require(spell['ownerId']==who and spell['status']=='learned' and spell['id'] in state['preparedSpells'][who],'Choose this person’s own tested and prepared spell.')
        require(state['spellWork'][who] is None,'Finish or cancel committed spell work first.')
        require(type(count) is int and 1<=count<=12,'Agree 1 to 12 castings, one per assigned phase.')
        definition=SPELL_FORMS[spell['formId']]
        require(not definition.get('support') and not definition.get('field'),'Cast field spells and work enchantments individually using their target controls.')
        require(room_available(state,definition['roomId']) and all(p in character_principles(state,who) for p in definition['requiredPrinciples']),'The caster needs the restored room and personal principle.')
        state['castingPlans'][who]={'spellId':spell['id'],'requestedCount':count,'completedCount':0,'status':'active'}
        set_character_assignment(state,who,'spellwork')
        add_journal(state,character_profile(state,who)['name']+' agreed '+str(count)+' castings of '+spell['name']+'. One per explicit Advance, using only unreserved inputs. No purchase authority or offline work was granted.')
    else:
        require(plan is not None and plan['status'] in ('active','paused'),'This person has no open casting plan.')
        if kind=='resume-casting-plan':
            spell=spell_by_id(state,plan['spellId']);definition=SPELL_FORMS[spell['formId']]
            require(spell['id'] in state['preparedSpells'][who] and spell['status']=='learned','Prepare the agreed spell before resuming.')
            require(state['spellWork'][who] is None,'Finish or cancel committed spell work before resuming.')
            require(room_available(state,definition['roomId']) and all(p in character_principles(state,who) for p in definition['requiredPrinciples']),'Restore the required room and personal understanding first.')
            plan['status']='active';set_character_assignment(state,who,'spellwork')
        else:
            plan['status']='paused' if kind=='pause-casting-plan' else 'cancelled'
            if character_assignment(state,who)=='spellwork' and state['spellWork'][who] is None:set_character_assignment(state,who,'rest')
            add_journal(state,character_profile(state,who)['name']+' '+plan['status']+' the casting plan after '+str(plan['completedCount'])+' completed castings. No future inputs were committed.')
    return True

def begin_planned_castings(state):
    # Commit all inputs before work resolves; no same-phase output feeds another plan.
    for who in household_members(state):
        view=casting_plan_view(state,who)
        if view is None or view['blockers']:continue
        spell=spell_by_id(state,view['spellId']);inputs=SPELL_FORMS[spell['formId']]['castingInputs']
        for material,count in inputs.items():state['materialInventory'][material]-=count
        state['spellWork'][who]={'kind':'cast','spellId':spell['id'],'committedInputs':deepcopy(inputs),'fromPlan':True}

def casting_plan_forecast(state):
    rows=[]
    for who in household_members(state):
        view=casting_plan_view(state,who)
        if view and view['status'] in ('active','paused'):
            rows.append(character_profile(state,who)['name']+' · casting plan '+str(view['completedCount'])+'/'+str(view['requestedCount'])+': '+(' '.join(view['blockers']) if view['blockers'] else 'one casting next Advance; inputs checked before this phase’s production.'))
    return rows


# Optional personal requests: no deadline, affection score or productivity reward.
PERSONAL_REQUESTS={
    'mira-reading-folio':{'ownerId':'mira','name':'A folio for the loose leaves','description':'Mira would like to bind her favourite loose poems and marginal notes into a plain cloth folio. She offers to do the work herself; this is a personal comfort, not an archive duty.',
        'unlockDescription':'Complete Mira’s living-archive ambition.', 'costCrowns':6,'materials':{'binding-thread':2},'requiredWorkPhases':2,
        'keepsakeName':'Mira’s cloth reading folio','note':'“The archive may insist on an index. These pages are allowed to be in exactly the wrong order.” Mira slips a pressed leaf between two poems and closes the cover. “A small shelf can hold a very particular sort of home.”'},
    'tamsin-repair-case':{'ownerId':'tamsin','name':'A case for the little offcuts','description':'Tamsin has saved scraps worth keeping and would like to make a small compartmented case. Her necessary tools are already supplied; this is a personal project she would enjoy finishing.',
        'unlockDescription':'Welcome Tamsin and complete her repair notebook.', 'costCrowns':8,'materials':{'binding-thread':1,'porous-clay':1},'requiredWorkPhases':2,
        'keepsakeName':'Tamsin’s offcut case','note':'“Needles here, thread below, spare clasps in the little compartment.” Tamsin sets a violet scrap beside them. “I should spend less time searching now. We shall see whether I actually put things back.”'},
}

def personal_request_view(state,key):
    definition=PERSONAL_REQUESTS[key];progress=state['personalRequests'][key];who=definition['ownerId']
    unlocked=(who in household_members(state) and (state['miraArchiveProject']['status']=='complete' if who=='mira' else state['additionalResidents'][who]['personalProject']['status']=='complete'))
    blockers=[]
    if not unlocked:blockers.append(definition['unlockDescription'])
    if not character_at_castle(state,'founder') or not character_at_castle(state,who):blockers.append('Both people must be home to agree this personal project.')
    if progress['status'] not in ('offered','deferred','accepted'):blockers.append('This request is already funded or complete.')
    for material,count in definition['materials'].items():
        if state['materialInventory'][material]-state['materialReserveTargets'][material]<count:blockers.append('Needs '+str(count)+' unreserved '+MATERIALS[material]['name']+'.')
    return {**deepcopy(progress),'unlocked':unlocked,'fundingBlockers':blockers,'canUseShared':state['sharedFunds']>=definition['costCrowns'],'canUsePersonal':state['personalFunds'].get(who,0)>=definition['costCrowns'],
        'working':progress['status']=='in-progress' and character_at_castle(state,who) and character_assignment(state,who)=='personal-request'}

def apply_personal_request_action(state,action):
    kind=action.get('type')
    if kind not in ('accept-personal-request','defer-personal-request','fund-personal-request','resume-personal-request','cancel-personal-request','read-personal-note','display-keepsake'):return False
    key=action.get('requestId');require(isinstance(key,str) and key in PERSONAL_REQUESTS,'Choose an offered personal request.')
    definition=PERSONAL_REQUESTS[key];who=definition['ownerId'];progress=state['personalRequests'][key]
    require(personal_request_view(state,key)['unlocked'],'This person has not offered this request yet.')
    require(character_at_castle(state,'founder') and character_at_castle(state,who),'Return home together to discuss this personal request.')
    if kind=='read-personal-note':
        require(progress['status']=='complete','Finish the personal project before reading its closing note.')
        progress['noteRead']=True;return True
    if kind=='display-keepsake':
        require(key in state['residentKeepsakes'][who],'Complete this personal keepsake first.')
        shown=action.get('displayed');require(type(shown) is bool,'Choose whether to display this person’s keepsake.')
        if shown and key not in state['displayedKeepsakes'][who]:state['displayedKeepsakes'][who].append(key)
        elif not shown and key in state['displayedKeepsakes'][who]:state['displayedKeepsakes'][who].remove(key)
        return True
    if kind in ('accept-personal-request','defer-personal-request'):
        require(progress['status'] in ('offered','deferred','accepted'),'A funded project must be paused or cancelled instead.')
        progress['status']='accepted' if kind=='accept-personal-request' else 'deferred'
        return True
    if kind=='fund-personal-request':
        require(progress['status']=='accepted','Discuss and accept this request before committing its resources.')
        view=personal_request_view(state,key);require(not view['fundingBlockers'],' '.join(view['fundingBlockers']))
        source=action.get('fundingSource');require(source in ('shared','personal'),'Choose shared funding or the owner’s personal wallet explicitly.')
        require(view['canUseShared'] if source=='shared' else view['canUsePersonal'],'The selected source cannot cover the exact cost; no other wallet will be charged.')
        require(not any(item['status']=='in-progress' and PERSONAL_REQUESTS[item_id]['ownerId']==who for item_id,item in state['personalRequests'].items()),'Finish this resident’s current personal request first.')
        if source=='shared':state['sharedFunds']-=definition['costCrowns']
        else:state['personalFunds'][who]-=definition['costCrowns']
        for material,count in definition['materials'].items():state['materialInventory'][material]-=count
        progress.update(status='in-progress',fundingSource=source,completedWorkPhases=0)
        money_entry(state,'Personal request committed: '+definition['name'],definition['costCrowns'],'household' if source=='shared' else who,key)
        set_character_assignment(state,who,'personal-request')
        add_journal(state,character_profile(state,who)['name']+' began '+definition['name'].lower()+'. Exact costs committed from '+('shared funds' if source=='shared' else 'her personal wallet')+' and unreserved materials. No relationship reward is promised.')
    elif kind=='resume-personal-request':
        require(progress['status']=='in-progress','Fund this request before resuming work.')
        set_character_assignment(state,who,'personal-request')
    else:
        require(progress['status']=='in-progress','Only an unfinished funded request can be cancelled.')
        source=progress['fundingSource']
        if source=='shared':state['sharedFunds']+=definition['costCrowns']
        else:state['personalFunds'][who]+=definition['costCrowns']
        for material,count in definition['materials'].items():state['materialInventory'][material]+=count
        money_entry(state,'Cancelled personal request: exact funding returned',definition['costCrowns'],key,'household' if source=='shared' else who)
        progress.update(status='accepted',completedWorkPhases=0,fundingSource=None)
        if character_assignment(state,who)=='personal-request':set_character_assignment(state,who,'rest')
        add_journal(state,'Cancelled the unfinished '+definition['name'].lower()+'. Exact money and materials returned; work progress discarded. The request may wait without penalty.')
    return True

def personal_request_forecast(state):
    rows=[]
    for key,progress in state['personalRequests'].items():
        if progress['status']=='in-progress':
            definition=PERSONAL_REQUESTS[key];who=definition['ownerId']
            rows.append(character_profile(state,who)['name']+' · '+definition['name']+': '+('+1 personal work phase.' if character_at_castle(state,who) and character_assignment(state,who)=='personal-request' else 'paused; progress and committed resources kept.'))
    return rows

def resolve_personal_requests(state,summary):
    for key,progress in state['personalRequests'].items():
        definition=PERSONAL_REQUESTS[key];who=definition['ownerId']
        if progress['status']!='in-progress' or not character_at_castle(state,who) or character_assignment(state,who)!='personal-request':continue
        progress['completedWorkPhases']+=1
        summary.append(character_profile(state,who)['name']+' worked on '+definition['name'].lower()+': '+str(progress['completedWorkPhases'])+' / '+str(definition['requiredWorkPhases'])+' phases.')
        if progress['completedWorkPhases']>=definition['requiredWorkPhases']:
            progress['status']='complete';state['residentKeepsakes'][who].append(key);set_character_assignment(state,who,'rest')
            summary.append(character_profile(state,who)['name']+' completed '+definition['keepsakeName']+'. It is her own possession. A closing note is available under Requests & letters; nothing was put in her room automatically.')
            add_journal(state,character_profile(state,who)['name']+' completed her optional personal request. No advancement, affection or Resonance was awarded.')


ROOM_DECORATION_CATALOG={
    'none':{'name':'Leave this slot clear'},
    'violet-runner':{'name':'Faded violet runner'},
    'ink-rug':{'name':'Ink-blue woven rug'},
    'reed-mat':{'name':'Woven reed mat'},
    'fern-study':{'name':'Pressed-fern study'},
    'star-chart':{'name':'Hand-drawn star chart'},
    'mending-sampler':{'name':'Small mending sampler'},
}

def decoration_slots(room):
    return {'floor':{'name':'Floor textile','choices':['none','reed-mat'] if room=='conservatory' else ['none','violet-runner','ink-rug']},
        'wall':{'name':'Wall display','choices':['none','fern-study','mending-sampler'] if room in HOUSING_ROOMS else ['none','fern-study','star-chart']}}

def apply_room_arrangement_action(state,action):
    kind=action.get('type')
    if kind not in ('decorate-room-slot','save-room-arrangement','load-room-arrangement','delete-room-arrangement'):return False
    room=action.get('roomId')
    require(isinstance(room,str) and room_available(state,room),'Open a restored room before arranging it.')
    if kind=='decorate-room-slot':
        slot=action.get('slotId');item=action.get('decorationId');slots=decoration_slots(room)
        require(isinstance(slot,str) and slot in slots,'Choose a supported room slot.')
        require(isinstance(item,str) and item in slots[slot]['choices'],'Choose a supported decoration for this slot.')
        state['roomDecorations'][room][slot]=item
        return True
    name=text_value(action.get('name'),40);saved=state['savedRoomArrangements'][room]
    if kind=='save-room-arrangement':
        require(name in saved or len(saved)<6,'Keep at most six arrangements per room. Delete one before saving another.')
        saved[name]={'furnishing':state['roomFurnishings'][room],'decorations':deepcopy(state['roomDecorations'][room])}
    elif kind=='load-room-arrangement':
        require(name in saved,'This room has no arrangement with that name.')
        arrangement=saved[name]
        require(arrangement['furnishing'] in ROOMS[room]['furnishings'],'The saved main furnishing is unavailable.')
        require(all(arrangement['decorations'].get(slot) in definition['choices'] for slot,definition in decoration_slots(room).items()),'The saved arrangement contains an unavailable decoration.')
        state['roomFurnishings'][room]=arrangement['furnishing']
        state['roomDecorations'][room]=deepcopy(arrangement['decorations'])
    else:
        require(name in saved,'This room has no arrangement with that name.')
        del saved[name]
    return True


def room_furnishing_view(state,room):
    rows=[];main=state['roomFurnishings'][room]
    if main!='none':
        effect='Decorative; no numerical bonus.'
        if room=='common-room' and main=='velvet-settee':
            effect='Supports +1 Resonance per established mutual flirtation on each Advance. Current contribution: +'+str(resonance_forecast(state))+'. Without an established flirtation: +0.'
        rows.append({'name':FURNISHING_NAMES[main],'effect':effect})
    for item in state['roomDecorations'][room].values():
        if item!='none':rows.append({'name':ROOM_DECORATION_CATALOG[item]['name'],'effect':'Decorative; no numerical bonus.'})
    if room=='common-room' and state['lanternDisplayed']:
        rows.append({'name':'Warming lantern','effect':'Warm household light; no numerical bonus while displayed here. Must be packed separately for an expedition.'})
    if room=='library' and state['libraryIndexInstalled']:
        rows.append({'name':'Library index charm','effect':'+1 work contribution per assigned research/archive worker, and +1 crown from the scholar’s copying phase.'})
    if room=='conservatory' and state['wateringCharmInstalled']:
        rows.append({'name':'Self-watering charm','effect':'+1 silver ivy or +2 crowns per staffed garden harvest. Does not increase the unattended harvest.'})
    for key,definition in UTILITY_ARTIFACTS.items():
        if definition['roomId']==room and state['utilityArtifactPlacements'][key]:
            rows.append({'name':RECIPES[key]['name'],'effect':definition['benefit']})
    for who in household_members(state):
        if state['bedroomAssignments'].get(who)==room:
            for key in state['displayedKeepsakes'][who]:
                rows.append({'name':PERSONAL_REQUESTS[key]['keepsakeName'],'effect':'Personal keepsake belonging to '+character_profile(state,who)['name']+'. No numerical bonus.'})
    return rows


def resident_moment_unlocked(state,key):
    definition=MOMENTS[key];requirement=definition['requirement']
    if any(who not in household_members(state) for who in definition['participants']):return False
    if requirement=='companion-project':return all(state['additionalResidents'][who]['personalProject']['status']=='complete' for who in definition['participants'])
    if requirement=='companion-return':return all(len(state.get('residency',{}).get(who,{}).get('arrivals',[]))>=2 for who in definition['participants'])
    mira_done=state['miraArchiveProject']['status']=='complete'
    tamsin_done=state['additionalResidents']['tamsin']['personalProject']['status']=='complete'
    mira_keepsake='mira-reading-folio' in state['residentKeepsakes']['mira']
    tamsin_keepsake='tamsin-repair-case' in state['residentKeepsakes']['tamsin']
    return {'refraction':'gentle-refraction' in state['archivePrinciples'],'resident':True,'conservatory':state['restorationStatus']=='complete',
        'mira-project':mira_done,'tamsin-project':tamsin_done,'both-projects':mira_done and tamsin_done,
        'mira-keepsake':mira_keepsake,'tamsin-keepsake':tamsin_keepsake,
        'mira-flirt':mira_keepsake and 'shared-flirtation' in state['completedDevelopments'],
        'tamsin-flirt':tamsin_keepsake and state['additionalResidents']['tamsin']['sharedFlirtation'],
        'iona-atlas':state.get('additionalResidents',{}).get('iona',{}).get('personalProject',{}).get('status')=='complete',
        'iona-keepsake':'iona-map-case' in state['residentKeepsakes'].get('iona',[]),
        'iona-return':len(state.get('residency',{}).get('iona',{}).get('arrivals',[]))>=2}[requirement]

def resident_moment_view(state,key):
    definition=MOMENTS[key];record=state['residentMoments'][key]
    unlocked=resident_moment_unlocked(state,key)
    home=all(character_at_castle(state,who) for who in ['founder']+definition['participants'])
    illustration=record.get('illustrationId',definition.get('illustrationId'))
    if record['status']!='complete' and illustration and len(definition['participants'])==1:
        who=definition['participants'][0]
        import outfit_progression
        chosen=outfit_progression.current(state,who)
        illustration=chosen['id'] if chosen else who
    return {'illustrationId':illustration,'title':definition['title'],'participants':definition['participants'],'invitation':definition['invitation'],
        **deepcopy(record),'unlocked':unlocked,'canJoin':unlocked and home and record['status']=='waiting',
        'waitingForReturn':unlocked and not home,'lines':deepcopy(definition['lines']) if record['status']=='complete' else []}

def resident_friendships(state):
    rows=[];shared=state['residentMoments'];members=household_members(state)
    if 'tamsin' in members:
        description='New housemates; their acquaintance is still taking shape.'
        if shared['shared-shelf']['status']=='complete':description='Comfortable enough to disagree about books and laugh about it.'
        if shared['shared-margins']['status']=='complete':description='Growing friends who exchange professional interests and enjoy a little argument over tea.'
        rows.append({'participants':['mira','tamsin'],'description':description})
    if 'iona' in members and shared['iona-mira-map']['status']=='complete':
        rows.append({'participants':['mira','iona'],'description':'They compare maps with the stories people tell about places; neither expects the other to agree on every margin.'})
    for key,definition in MOMENTS.items():
        if definition.get('friendshipDescription') and shared[key]['status']=='complete' and all(who in members for who in definition['participants']):
            rows.append({'participants':list(definition['participants']),'description':definition['friendshipDescription']})
    return rows

def apply_resident_moment_action(state,action):
    kind=action.get('type')
    if kind not in ('join-resident-moment','defer-resident-moment','restore-resident-moment'):return False
    key=action.get('momentId')
    require(isinstance(key,str) and key in MOMENTS,'Choose an offered household moment.')
    require(resident_moment_unlocked(state,key),'This conversation has not been offered yet.')
    record=state['residentMoments'][key];definition=MOMENTS[key]
    if kind=='join-resident-moment':
        if record['status']=='complete':return True
        require(resident_moment_view(state,key)['canJoin'],'Bring everyone home and restore a deferred invitation before joining.')
        illustration=resident_moment_view(state,key).get('illustrationId')
        if illustration:record['illustrationId']=illustration
        record.update(status='complete',completedOn={'dayNumber':state['dayNumber'],'phase':state['currentDayPhase']})
        resident_bonds.award(state, definition['participants'], 'resident-moment:' + key, definition['title'], 2)
        for who in definition['participants']:
            lines=state['conversation'] if who=='mira' else state['additionalResidents'][who]['conversation']
            lines.extend({'speaker':speaker,'text':text,'source':'authored-moment','momentId':key} for speaker,text in definition['lines'])
            del lines[:-60]
        add_journal(state,'Shared an optional household moment: '+definition['title']+'. Remembered without advancing time or awarding resources.')
    else:
        require(record['status']!='complete','This moment is already remembered; read it again from its saved card.')
        record['status']='deferred' if kind=='defer-resident-moment' else 'waiting'
    return True


# Advanced practices remain individual and use the existing two preparation slots.
PRACTICES.update({
    'comparative-study':{'name':'Comparative study','description':'+1 research or archive work contribution when prepared. Can combine with Patient scholarship; no copying-income bonus. Does not speed training, spell work or personal keepsakes.','discipline':'Advanced scholarship','requiredPractice':'archive-focus','requiredSkill':'scholarship','requiredRank':1},
    'measured-assembly':{'name':'Measured assembly','description':'+1 artifact work contribution when prepared by the maker. Can combine with Methodical assembly. Does not speed focus work, spell work or personal keepsakes.','discipline':'Advanced artifice','requiredPractice':'careful-assembly','requiredSkill':'artifice','requiredRank':1},
})

def practice_requirements(state,who,key):
    definition=PRACTICES[key];requirements=[];blockers=[]
    if definition.get('requiredPractice'):
        name=PRACTICES[definition['requiredPractice']]['name']
        requirements.append('Personally learned '+name)
        if definition['requiredPractice'] not in state['characterDevelopment'][who]['learnedPractices']:blockers.append('Learn '+name+' first.')
    if definition.get('requiredSkill'):
        name=CHARACTER_SKILLS[definition['requiredSkill']]['name'];rank=definition['requiredRank']
        requirements.append(name+' rank '+str(rank))
        if skill_rank(state,who,definition['requiredSkill'])<rank:blockers.append('Develop '+name+' to rank '+str(rank)+' first.')
    return {'requirements':requirements,'blockers':blockers}

def work_contribution_parts(state,who,practice):
    if not character_at_castle(state,who):return []
    development=state['characterDevelopment'][who];study=practice=='archive-focus'
    skill='scholarship' if study else 'artifice';advanced='comparative-study' if study else 'measured-assembly'
    rows=[{'name':'Base assigned work','amount':1}]
    bonuses=[(CHARACTER_SKILLS[skill]['name']+' ranks',skill_rank(state,who,skill)),
        (PRACTICES[practice]['name'],int(practice in development['preparedPractices'])),
        (PRACTICES[advanced]['name'],int(advanced in development['preparedPractices'])),
        ('Living index' if study else 'Binding press',int(state['libraryIndexInstalled'] if study else state['utilityArtifactPlacements'].get('binding-press',False))),
        ('Scholarly thread' if study else 'Steady hand',int(focus_effect_active(state,who,'scholarly-thread' if study else 'steady-hand')))]
    rows.extend({'name':name,'amount':amount} for name,amount in bonuses if amount)
    support=public_progression.bonus(state,who,practice)
    if support:
        if not study:rows=[row for row in rows if row['name']!='Binding press']
        rows.append(support)
    magic=spell_support.bonus(state,who,'research' if study else 'craft')
    if magic:rows.append({'name':'Prepared work enchantment','amount':magic})
    if lasting_rituals.active(state,'archive-circle' if study else 'maker-circle'):rows.append({'name':'Lasting household ritual','amount':1})
    shape_bonus=house_shape.bonus(state,'research' if study else 'craft')
    if shape_bonus:rows.append({'name':'Fitted household undertaking','amount':shape_bonus})
    rows.extend(character_builds.work_parts(state,who,practice))
    rows.extend(equipment.bonus(state,who,practice))
    if practice=='careful-assembly' and resident_specialties.active(state,'koharu'):rows.append({'name':'Koharu’s restoration bench','amount':1})
    if practice=='archive-focus' and resident_specialties.legacy(state,'tamsin'):rows.append({'name':'Tamsin’s working reference cabinet','amount':1})
    if practice=='careful-assembly' and headquarters.ready(state,'workshop') and state['headquarters']['stock'].get('sorting-bench',0):rows.append({'name':'Roadkeeper’s sorting bench','amount':1})
    if practice=='careful-assembly' and headquarters.ready(state,'workshop'):rows.append({'name':'Fitted headquarters workshop','amount':1})
    return rows

def preparation_set_blockers(state,who,items):
    learned=state['characterDevelopment'][who]['learnedPractices']
    return ['Learn '+PRACTICES[key]['name']+' again before loading this set.' for key in items if key not in learned]

def apply_preparation_set_action(state,action):
    kind=action.get('type')
    if kind not in ('save-preparation-set','load-preparation-set','delete-preparation-set'):return False
    who=action.get('characterId')
    require(isinstance(who,str) and who in household_members(state),'Choose a current household member.')
    require(character_at_castle(state,'founder') and character_at_castle(state,who),'Return home together before changing preparation sets.')
    name=text_value(action.get('name'),40);sets=state['practicePreparationSets'][who]
    if kind=='save-preparation-set':
        require(name in sets or len(sets)<6,'Keep at most six preparation sets per person. Delete one before saving another.')
        sets[name]=list(state['characterDevelopment'][who]['preparedPractices'])
    elif kind=='load-preparation-set':
        require(name in sets,'This person has no preparation set by that name.')
        require(not preparation_set_blockers(state,who,sets[name]),' '.join(preparation_set_blockers(state,who,sets[name])))
        require(len(sets[name])<=2,'This set exceeds the two practice slots.')
        state['characterDevelopment'][who]['preparedPractices']=list(sets[name])
    else:
        require(name in sets,'This person has no preparation set by that name.')
        del sets[name]
    return True


AUGMENTATION_MATERIALS={'moon-glass':1,'binding-thread':1}

def base_spell_capacity(state,who):
    return (3 if who in RITUAL_PARTICIPANTS and state['spellRitual']['status']=='complete' else 2)+character_builds.capacity_bonus(state,who)

def augmentation_view(state,who):
    record=state['personalAugmentations'][who];project=record['project'];blockers=[]
    offered=who=='founder' or (who=='mira' and state['miraArchiveProject']['status']=='complete') or (who=='tamsin' and state['additionalResidents']['tamsin']['personalProject']['status']=='complete')
    if not offered:blockers.append('This resident has not offered this development; finish her professional project first.')
    if not character_at_castle(state,'founder') or not character_at_castle(state,who):blockers.append('Both people must be home to agree the ritual.')
    if 'gentle-refraction' not in character_principles(state,who):blockers.append('Personally study Gentle refraction first.')
    if not room_available(state,'library'):blockers.append('A usable library is required.')
    if state['sharedFunds']<10:blockers.append('Needs 10 shared crowns.')
    for key,count in AUGMENTATION_MATERIALS.items():
        if state['materialInventory'][key]-state['materialReserveTargets'][key]<count:blockers.append('Needs '+str(count)+' unreserved '+MATERIALS[key]['name']+'.')
    work=[]
    if project:
        if not character_at_castle(state,who) or character_assignment(state,who)!='augmentation':work.append('Paused; the owner must be home and assigned to this ritual.')
        if project['kind']=='reverse' and len(state['preparedSpells'][who])+len(state['publicWorkshop']['preparedSpells'].get(who,[]))>base_spell_capacity(state,who):work.append('Put aside enough personal spells to fit '+str(base_spell_capacity(state,who))+' preparation slots before reversal can progress.')
    return {**deepcopy(record),'offered':offered,'startBlockers':blockers,'workBlockers':work,'baseCapacity':base_spell_capacity(state,who),'capacity':spell_preparation_capacity(state,who)}

def apply_augmentation_action(state,action):
    kind=action.get('type')
    if kind not in ('begin-augmentation','reverse-augmentation','resume-augmentation','cancel-augmentation'):return False
    who=action.get('characterId')
    require(isinstance(who,str) and who in household_members(state),'Choose a current household member.')
    require(character_at_castle(state,'founder') and character_at_castle(state,who),'Return home together to discuss this ritual.')
    record=state['personalAugmentations'][who];project=record['project']
    if kind=='begin-augmentation':
        require(not record['active'] and project is None,'Finish or cancel this person’s current ritual first; an active blessing cannot stack.')
        view=augmentation_view(state,who);require(not view['startBlockers'],' '.join(view['startBlockers']))
        state['sharedFunds']-=10
        for key,count in AUGMENTATION_MATERIALS.items():state['materialInventory'][key]-=count
        record['project']={'kind':'receive','completedWorkPhases':0,'requiredWorkPhases':2}
        set_character_assignment(state,who,'augmentation')
        add_journal(state,character_profile(state,who)['name']+' chose Lamplit sight: 10 shared crowns, 1 moon glass and 1 binding thread committed. Two personal ritual phases; no change of personality or relationship.')
    elif kind=='reverse-augmentation':
        require(record['active'] and project is None,'An active blessing and no unfinished ritual are required.')
        record['project']={'kind':'reverse','completedWorkPhases':0,'requiredWorkPhases':1}
        set_character_assignment(state,who,'augmentation')
    elif kind=='resume-augmentation':
        require(project is not None,'There is no unfinished personal ritual.')
        set_character_assignment(state,who,'augmentation')
    else:
        require(project is not None,'There is no unfinished personal ritual to cancel.')
        if project['kind']=='receive':
            state['sharedFunds']+=10
            for key,count in AUGMENTATION_MATERIALS.items():state['materialInventory'][key]+=count
        record['project']=None
        if character_assignment(state,who)=='augmentation':set_character_assignment(state,who,'rest')
        add_journal(state,character_profile(state,who)['name']+' cancelled an unfinished personal ritual. Any committed materials and crowns returned; the existing blessing state is unchanged.')
    return True

def resolve_augmentations(state,summary):
    for who in household_members(state):
        record=state['personalAugmentations'][who];project=record['project']
        if not project or augmentation_view(state,who)['workBlockers']:continue
        project['completedWorkPhases']+=1
        summary.append(character_profile(state,who)['name']+' · Lamplit sight '+project['kind']+': '+str(project['completedWorkPhases'])+' / '+str(project['requiredWorkPhases'])+' personal phases.')
        if project['completedWorkPhases']>=project['requiredWorkPhases']:
            record['active']=project['kind']=='receive';record['project']=None;set_character_assignment(state,who,'rest')
            text=character_profile(state,who)['name']+(' received Lamplit sight: a faint violet glint in the eyes and one extra personal spell-preparation slot.' if record['active'] else ' completed the reversal of Lamplit sight. Ordinary appearance and previous spell capacity restored.')
            summary.append(text);add_journal(state,text)


# Campaign-owned identity and named accommodation, shared by authored and reviewed people.
def character_profile(state, person_id):
    return state.get('people', {}).get(person_id, CHARACTERS.get(person_id, {}))


def initialize_person_registry(state):
    state['people'] = {}
    for person_id, template in CHARACTERS.items():
        state['people'][person_id] = {
            **deepcopy(template), 'personId': person_id, 'identityRevision': 1,
            'identitySource': 'authored-sample', 'adultAgeYears': {'founder':40,'mira':22,'tamsin':20}[person_id],
            'lifeStage': 'adult', 'ancestryLabel': 'Human',
            'accommodationPreference': 'private-room' if person_id == 'tamsin' else 'separate-bed',
        }
    for who, person in state['people'].items():
        if who != 'founder':summoning.validate_npc_profile(person)
    state['arrivalReservations'] = {}
    arrival = state.get('pendingResidentArrival', {})
    if arrival:
        who = arrival['characterId']
        # Preserve even an unusable old reservation. Arrival revalidation waits for repair.
        state['arrivalReservations']['arrival:'+who] = {
            'personId':who, 'roomId':arrival['roomId'], 'sourceType':'recruitment',
            'sourceId':who, 'reservedBeds':1,
        }


def known_people(state):
    """People already introduced, independently of membership and physical presence."""
    return (['founder'] if state.get('startType')=='fresh' else ['founder','mira']) + [who for who, record in state.get('additionalResidents',{}).items()
        if record['status'] != 'unknown']


def present_household_members(state):
    return [who for who in household_members(state) if character_at_castle(state,who)]


def arrival_blockers(state, reservation_id):
    reservation = state.get('arrivalReservations',{}).get(reservation_id)
    if not reservation:
        return ['The named bed reservation is missing. Agree an arrival room again.']
    room_id = reservation['roomId']
    definition = HOUSING_ROOMS.get(room_id)
    if not definition or state['housingRooms'][room_id]['status'] != 'complete':
        return ['The agreed room must be restored before arrival.']
    who = reservation['personId']
    region_blockers=estate_expansion.placement_blockers(state,who,room_id)
    if region_blockers:return region_blockers
    if character_profile(state,who).get('accommodationPreference') == 'private-room' and definition['capacityBeds'] != 1:
        return ['The agreed accommodation must be a private one-bed room.']
    if who in state['bedroomAssignments']:
        return ['This person already has a bedroom; resolve the existing placement before arrival.']
    room = housing_summary(state)['rooms'][room_id]
    if room['availableBeds'] < 0:
        return ['The agreed room has no space for every occupant and reservation. Move the arrival or release a planning reservation.']
    return []


def reserve_arrival(state, person_id, room_id, source_type, source_id):
    require(person_id in known_people(state), 'Introduce a known person before arranging an arrival.')
    require(isinstance(room_id,str) and room_id in HOUSING_ROOMS, 'Choose an existing bedroom.')
    require(state['housingRooms'][room_id]['status']=='complete', 'Restore the room before arranging an arrival.')
    require(person_id not in state['bedroomAssignments'], 'This person already occupies a bedroom.')
    require(character_profile(state,person_id).get('accommodationPreference')!='private-room' or HOUSING_ROOMS[room_id]['capacityBeds']==1,
        'This person has agreed to a private one-bed room.')
    require(not estate_expansion.placement_blockers(state,person_id,room_id),' '.join(estate_expansion.placement_blockers(state,person_id,room_id)))
    reservation_id='arrival:'+person_id
    existing=state['arrivalReservations'].get(reservation_id)
    available=housing_summary(state)['rooms'][room_id]['availableBeds']
    if existing and existing['roomId']==room_id:available+=existing['reservedBeds']
    require(available>=1, 'No unreserved bed is available in this room.')
    state['arrivalReservations'][reservation_id]={'personId':person_id,'roomId':room_id,
        'sourceType':source_type,'sourceId':source_id,'reservedBeds':1}


def arrival_reservation_views(state):
    return [{**deepcopy(item), 'id':key, 'personName':character_profile(state,item['personId'])['name'],
        'roomName':HOUSING_ROOMS.get(item['roomId'],{}).get('name','Unavailable room'),
        'blockers':arrival_blockers(state,key)} for key,item in state.get('arrivalReservations',{}).items()]


# Each new identity receives its own records once; membership never grants a second copy.
def initialize_character_records(state, who, principles, focus_name):
    require(who in state['people'], 'Establish an identity before initializing character records.')
    if who in state['characterDevelopment']:
        return
    profile=state['people'][who]
    if profile.get('ancestryLabel')=='Golem':
        principles=[];profile['startingPractices']=[]
    state['additionalResidents'][who]={'status':'contacted','assignment':'rest','knownPrinciples':list(principles),
        'discussedTopics':[],'conversation':[],'wardrobe':{'outerLayer':'none'},'savedStyles':[],
        'completedScenes':[],'sharedFlirtation':False,'relationshipDescription':'Introduced; no romance established',
        'personalProject':{'status':'not-offered','completedWorkPhases':0,'requiredWorkPhases':0}}
    defaults={
        'characterDevelopment':{'learnedPractices':list(profile['startingPractices']),'preparedPractices':[],'advancementAwards':{}},
        'characterBuilds':character_builds.empty_build(who),
        'characterSkills':{key:0 for key in CHARACTER_SKILLS},'trainingProjects':None,
        'signatureFocuses':{'name':focus_name,'capacity':1,'inscriptions':[],'householdLoadout':[],'expeditionLoadout':[]},
        'focusProjects':None,'preparedSpells':[],'spellWork':None,'castingPlans':None,
        'personalFunds':0,'personalPossessions':[],'residentKeepsakes':[],'displayedKeepsakes':[],
        'practicePreparationSets':{},'personalAugmentations':{'active':False,'project':None}}
    for key,value in defaults.items():state[key][who]=deepcopy(value)
    state['householdAllowancePlan']['dailyCrowns'][who]=0
    if profile.get('publicStarterId') and profile.get('ancestryLabel')!='Golem':
        starter=public_workshop.definition(profile['publicStarterId'])
        focus_id=next(ref['id'] for ref in starter['references'] if ref['id'] in public_workshop.records('equipment-concept'))
        instance=public_workshop.owned_object(state,{'recordId':focus_id,'ownerId':who,'kind':'equipment','id':'initial-provision:'+who},'equipment')
        state['signatureFocuses'][who]['publicItemId']=instance


RESEARCH_CATALOG['courteous-passage']={'name':'Courteous passage','costCrowns':12,'requiredWorkPhases':3,
    'requiredPrinciples':['clear-instruction','gentle-refraction'],'principle':'courteous-passage',
    'description':'Study a crossing that opens only through an agreed invitation, after the concordant lesson.',
    'benefit':'Unlocks the Open Threshold ritual, which introduces magical visitors. You can then invite a visit and discuss joining the household.'}
PRINCIPLE_NAMES['courteous-passage']='Courteous passage'
PRINCIPLE_GUIDE['courteous-passage']={'source':'Complete the concordant lesson, then research Courteous passage.',
    'view':'research','use':'Conduct the Open Threshold contact ritual.'}


PERSONAL_REQUESTS['iona-map-case']={
    'ownerId':'iona','name':'A case for the maps that wander',
    'description':'With her atlas finished, Iona would like a modest case for the loose maps she still wants to take on visits. It is a personal keepsake, not expedition equipment.',
    'unlockDescription':'Welcome Iona as a household member and finish her crossing atlas.',
    'costCrowns':6,'materials':{'binding-thread':1,'porous-clay':1},'requiredWorkPhases':2,
    'keepsakeName':'Iona’s travelling map case',
    'note':'“The atlas can stay on a shelf. These can come with me.” Iona closes the case around a stubborn corner of paper. “It is a good home that leaves room for coming back.”'}

ORIGINAL_ASSETS['iona']='/assets/portraits/iona.webp'

PERSONAL_PURCHASES['travel-tea-tin']={'name':'A travelling tea tin','ownerId':'iona','costCrowns':3,'description':'Iona has chosen a plain refillable tin for tea on her visits. It is a personal comfort, not equipment with a travel bonus.'}

ORIGINAL_ASSETS['aurelia']='/assets/portraits/aurelia.webp'
ORIGINAL_ASSETS['neris']='/assets/portraits/neris.webp'



ORIGINAL_ASSETS.update({who:'/assets/'+who+'.png' for who in containment.CASES})

# Expanded rooms are persistent fixed places. The shared studies are explicitly
# labelled representative illustrations; each room keeps independent choices.
HOUSING_ROOMS.update(estate_expansion.ROOMS)
for room_id,definition in estate_expansion.ROOMS.items():
    ROOMS[room_id]={'name':definition['name'],'purpose':'An ordinary home with personal space.',
        'description':definition['description'],'furnishings':['oak-bench','velvet-bench','none'],
        'illustrationIsRepresentative':True}
    ORIGINAL_ASSETS[room_id]='/assets/'+('west-chamber.webp' if definition['capacityBeds']==1 else 'garden-chamber.webp')

ORIGINAL_ASSETS.update({key:'/assets/'+key+'.webp' for key in local_encounters.PEOPLE})

# Personal working tools reuse property-based crafting and individual work budgets.
equipment.register(globals())

public_progression.register(globals())

# A solo route to archive knowledge avoids depending on a demonstration resident.
RESEARCH_CATALOG['archive-foundations']={
    'name':'Arrange the first archive','costCrowns':12,'requiredWorkPhases':3,
    'requiredPrinciples':['steady-hearth-wards'],'principle':'reference-binding',
    'description':'Study how references remain attached to the ideas and objects they describe. A solo route through your own archive notes.',
    'benefit':'Learn Reference binding, craft a living index charm, and open the Hillfold bindery lead.'}

# Additive headquarters catalogue; legacy room IDs and accepted art stay authoritative.
headquarters.register(globals())

# Reviewed v0.50 room-art defaults, after all room registration.
from room_art import ROOM_ASSETS
ORIGINAL_ASSETS.update(ROOM_ASSETS)

# Optional weatherproofing chapter uses the same work and expedition rules.
import castle_chapter
castle_chapter.register(globals())

# Persistent service-road journey and its optional workshop improvement.
import service_road
service_road.register(globals())

import resident_specialties
resident_specialties.register()
keeping_hearth.register()

# Reviewed v0.53 expedition, object and character defaults.
from art_catalogue import ART_ASSETS
ORIGINAL_ASSETS.update(ART_ASSETS)

# Register the complete authored spell catalogue after the base forms and principles.
import authored_spells
authored_spells.install(SPELL_FORMS)

import spell_support
spell_support.install(SPELL_FORMS)

import field_magic, sys
field_magic.install(sys.modules[__name__])

import lasting_rituals
import combat_magic
combat_magic.install(sys.modules[__name__])

field_magic.expand_existing(sys.modules[__name__])

# Authored raster icons share the normal accepted-art override and review system.
ORIGINAL_ASSETS.update({'spell-'+key:'/assets/spells/'+key+'.webp' for key in SPELL_FORMS})
ORIGINAL_ASSETS.update({'ritual-'+key:'/assets/spells/'+key+'.webp' for key in lasting_rituals.CATALOGUE})

import character_approaches
character_approaches.install_existing()

import beacon_expedition
EXPEDITION_SITES[beacon_expedition.SITE]=beacon_expedition.DEFINITION
# Field spell previews include the newly authored beacon applications.
for _beacon_step in beacon_expedition.STEPS:
    for _beacon_choice in _beacon_step['choices'].values():
        if _beacon_choice.get('castForm'):
            _form = SPELL_FORMS[_beacon_choice['castForm']]
            _form['effect'] += ' Stormwatch beacon: ' + _beacon_choice['name'] + ' through its listed encounter method (one phase; prepared caster and components required).'

# Additional fixed quest applications share each spell’s normal component cost.
import character_quest_content
for _quest_obstacle in character_quest_content.OBSTACLES.values():
    SPELL_FORMS[_quest_obstacle["spell"]]["effect"] += " Character quests: "+_quest_obstacle["name"].lower()+" in one assigned shared phase, with the listed casting components. This application replaces the ordinary casting effect."

for _quest_ritual in set(character_quest_content.QUEST_RITUALS.values()):
    _quest_uses=[character_quest_content.OBSTACLES[k]["name"].lower() for k,v in character_quest_content.QUEST_RITUALS.items() if v==_quest_ritual]
    lasting_rituals.CATALOGUE[_quest_ritual]["effect"] += " Character quests: ordinary methods take two phases instead of three for "+", ".join(_quest_uses)+". Duration is fixed when the method is chosen."

import lantern_adventure
EXPEDITION_SITES[lantern_adventure.SITE]=lantern_adventure.DEFINITION
for _lantern_step in lantern_adventure.STEPS:
    for _lantern_choice in _lantern_step["choices"].values():
        if _lantern_choice.get("castForm"):
            SPELL_FORMS[_lantern_choice["castForm"]]["effect"] += " Lantern pavilion: "+_lantern_choice["name"]+" in one assigned expedition phase, with the listed casting components."

# v0.66: fixed multi-route adventures and flexible resident parties.
import party_journeys
for _key,_journey in party_journeys.SITES.items():EXPEDITION_SITES[_key]=_journey['definition']
party_journeys.install(__import__(__name__))


# v0.81: equipment transactions share the existing campaign revision/idempotency gate.
EXPEDITION_SITES[arms_of_our_own.SITE]=arms_of_our_own.DEFINITION
ORIGINAL_ASSETS[arms_of_our_own.SITE]='/assets/expeditions/north-watch-road.webp'

def apply_action(state, action):
    kind=action.get('type','')
    if kind in ('assign-character','assign-founder','assign-resident') and action.get('assignment') in ('hunt','forage','procurement','road-patrol','food-ritual'):
        who=action.get('characterId') if kind=='assign-character' else 'founder' if kind=='assign-founder' else 'mira'
        return apply_action(state,{'type':'food-resume'} if action['assignment']=='food-ritual' and who=='founder' else {'type':'food-assign','characterId':who,'assignment':action['assignment']})
    if isinstance(kind,str) and (kind.startswith(('gear-','arms-')) or (kind=='choose-encounter-method' and arms_of_our_own.active(state))):
        staged=deepcopy(state)
        armoury.sync(staged)
        if not (armoury.apply(staged,action) or arms_of_our_own.apply(staged,action)):
            raise RuleError('Unknown equipment or chapter action.')
        state.clear();state.update(staged)
        return
    armoury.legacy_guard(state,action)
    if kind in armoury.LEGACY_CONFIG_ACTIONS:
        staged=deepcopy(state)
        result=_apply_action_legacy(staged,action)
        armoury.sync(staged)
        # Reject configuration changes that overbook slots or active channels.
        for who in armoury.state(staged)['loadouts']:
            for mode in armoury.MODES:
                proposed=armoury.loadout(staged,who,mode)
                if proposed!=armoury.loadout(state,who,mode):armoury.validate_loadout(staged,who,proposed)
        state.clear();state.update(staged)
        return result
    legacy_keys=('personalEquipment','preparedEquipment','signatureFocuses','publicWorkshop','headquarters','people')
    before={k:deepcopy(state.get(k)) for k in legacy_keys}
    result=_apply_action_legacy(state,action)
    if any(before[k]!=state.get(k) for k in legacy_keys):
        armoury.sync(state)
    if kind=='hq-equip-armour':
        armoury.legacy_armour_toggle(state,action['equipped'])
    return result


# v0.84: record only successful field actions, outside the existing transaction gates.
_apply_action_equipment = apply_action
def apply_action(state, action):
    import expedition_loop
    before=expedition_loop.snapshot(state,action)
    result=_apply_action_equipment(state,action)
    expedition_loop.record_success(state,action,before)
    return result

# Chapter six and provisions share the existing transaction boundary.
roads_we_keep.register(globals())
import velis_content
velis_content.register(globals())
first_patrol.register(globals())
import rhess_content
rhess_content.register(globals())
_apply_action_v084=apply_action
def apply_action(state,action):
    kind=action.get('type','')
    if isinstance(kind,str) and kind.startswith('cheat-'):
        import solo_tools
        staged=deepcopy(state)
        solo_tools.apply(staged,action)
        armoury.sync(staged)
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith('intimacy-'):
        import intimacy
        staged=deepcopy(state)
        if not intimacy.apply(staged,action):raise RuleError('Unknown closeness action.')
        state.clear();state.update(staged);return state
    if kind=='start-expedition' and action.get('siteId')==first_patrol.WARD:
        party=action.get('companionIds',[action.get('companionId')])
        require(isinstance(party,list) and 'rhess' in party,'Bring Rhess on the wardstone expedition.')
    assignment=action.get('assignment')
    if kind in ('assign-character','assign-founder','assign-resident') and assignment in ('hunt','forage','procurement','road-patrol','food-ritual'):
        who=action.get('characterId','mira' if kind=='assign-resident' else 'founder')
        if assignment=='food-ritual':
            require(who=='founder','Only the scholar conducts this ritual.')
            action={'type':'food-resume'}
        else:action={'type':'food-assign','characterId':who,'assignment':assignment}
        kind=action['type']
    if isinstance(kind,str) and (kind.startswith(('food-','roads-','patrol-','path-')) or kind=='evening-rest' or (kind=='choose-encounter-method' and (roads_we_keep.active(state) or first_patrol.active(state)))):
        staged=deepcopy(state)
        import expedition_loop
        before=expedition_loop.snapshot(staged,action)
        if not (personal_paths.apply(staged,action) or provisions.apply(staged,action) or roads_we_keep.apply(staged,action) or first_patrol.apply(staged,action) or household_rest.apply(staged,action)):raise RuleError('Unknown household supply action.')
        expedition_loop.record_success(staged,action,before)
        state.clear();state.update(staged);return state
    return _apply_action_v084(state,action)


# v0.94: shared, transactional Chapter 8 and independent field patrols.
import field_patrols
import castle_reawakening
castle_reawakening.install()
_apply_action_v093=apply_action
def apply_action(state,action):
    kind=action.get('type','')
    if kind in ('assign-character','assign-founder','assign-resident') and action.get('assignment') in ('external-commission','practical-project','castle-lamp'):
        import commissions
        who=action.get('characterId') if kind=='assign-character' else 'founder' if kind=='assign-founder' else 'mira'
        assignment=action['assignment']
        require(who in household_members(state),'Choose a household member.')
        if assignment=='external-commission':
            job=commissions.saved(state)['job']
            require(job and job['workerId']==who,'This worker has no unfinished external commission.')
            action={'type':'commission-resume'}
        elif assignment=='practical-project':action={'type':'practical-resume','characterId':who}
        else:
            require(who=='founder','The scholar must do the reading-lamp work.')
            action={'type':'castle-lamp-resume'}
        return apply_action(state,action)
    if isinstance(kind,str) and kind.startswith(('commission-','practical-','routine-','history-','castle-lamp-')):
        import commissions,practical_projects,household_routines,shared_history
        staged=deepcopy(state)
        if not any(module.apply(staged,action) for module in (commissions,practical_projects,household_routines,shared_history,castle_reawakening)):
            raise RuleError('Choose a listed household action.')
        state.clear();state.update(staged);return state
    if kind=='advance':
        import household_routines
        if not household_routines.saved(state):return _apply_action_v093(state,action)
        staged=deepcopy(state)
        notes=household_routines.before_advance(staged)
        _apply_action_v093(staged,action)
        staged['lastPhaseSummary']=notes+staged['lastPhaseSummary']
        for line in notes:add_journal(staged,line)
        household_routines.after_advance(staged)
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith('bestiary-'):
        import bestiary
        staged=deepcopy(state)
        require(bestiary.apply(staged,action),'Choose a listed bestiary action.')
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith('chapel-spirit-'):
        import chapel_spirit
        staged=deepcopy(state)
        chapel_spirit.apply(staged,action)
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith('world-'):
        import world_recruitment
        staged=deepcopy(state)
        world_recruitment.apply(staged,action)
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith('recruit-'):
        import recruitment_quests
        staged=deepcopy(state)
        recruitment_quests.apply(staged,action)
        state.clear();state.update(staged);return state
    if isinstance(kind,str) and kind.startswith(('watch-','trial-')):
        staged=deepcopy(state)
        field_patrols.apply(staged,action)
        state.clear();state.update(staged);return state
    return _apply_action_v093(state,action)

# Register creature components before creating or loading any campaign.
import bounty_contracts
bounty_contracts.install(globals())

foundation_chamber.register(globals())
_apply_action_v109 = apply_action
def apply_action(state, action):
    kind = action.get('type', '')
    if kind in ('assign-character', 'assign-founder', 'assign-resident') and action.get('assignment') in (foundation_chamber.ASSIGNMENT, foundation_chamber.RITUAL_ASSIGNMENT):
        who=action.get('characterId', 'mira' if kind=='assign-resident' else 'founder')
        if action['assignment']==foundation_chamber.ASSIGNMENT:
            require(who=='founder', 'The scholar is responsible for this investigation.')
            action={'type':'foundation-resume'}
        else:
            ritual=foundation_chamber.saved(state)['ritual']
            require(ritual and who in ('founder',ritual['partnerId']), 'This person has no arranged foundation ritual.')
            action={'type':'foundation-ritual-resume'}
        kind=action['type']
    if isinstance(kind,str) and kind.startswith('foundation-'):
        staged=deepcopy(state)
        foundation_chamber.apply(staged, action)
        state.clear();state.update(staged);return state
    return _apply_action_v109(state,action)

_apply_action_v110 = apply_action
def apply_action(state, action):
    kind=action.get('type','')
    if kind in ('assign-character','assign-founder','assign-resident') and action.get('assignment')==friendship_milestones.ASSIGNMENT:
        who=action.get('characterId','mira' if kind=='assign-resident' else 'founder')
        job=friendship_milestones.saved(state)['job']
        require(job and who in job['participants'],'This person has no arranged shared activity.')
        action={'type':'friendship-resume'};kind=action['type']
    if isinstance(kind,str) and kind.startswith('friendship-'):
        staged=deepcopy(state)
        friendship_milestones.apply(staged,action)
        state.clear();state.update(staged);return state
    return _apply_action_v110(state,action)

_apply_action_v112 = apply_action
def apply_action(state, action):
    kind = action.get('type', '')
    if isinstance(kind, str) and kind.startswith('thread-'):
        import companion_threads
        staged = deepcopy(state)
        require(companion_threads.apply(staged, action), 'Choose a listed conversation action.')
        state.clear(); state.update(staged)
        return state
    return _apply_action_v112(state, action)

# v0.114: explicit early lessons and a saved survey-room investigation.
_apply_action_v113=apply_action
def apply_action(state,action):
    kind=action.get('type','')
    if isinstance(kind,str) and (kind=='opening-equipment' or kind.startswith('survey-room-')):
        import early_lessons,survey_rooms
        staged=deepcopy(state)
        require(early_lessons.apply(staged,action) or survey_rooms.apply(staged,action),'Choose a listed progression action.')
        state.clear();state.update(staged);return state
    return _apply_action_v113(state,action)

import chapel_spirit
chapel_spirit.register(globals())
import companion_goals
companion_goals.register()
