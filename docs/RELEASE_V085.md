# v0.85 — The Roads We Keep

Food is a shared, low-pressure household resource from the beginning. Chapter 6 expands dependable trade and introduces Velis, an adult dark elf caravan broker whose associated room is the Supply Office.

## Playing

Open Stores for provisions, primary hunting/foraging assignments, optional automatic purchasing, and Conjure Sustenance. The home page and expedition preparation show pantry stock and days supplied. The kitchen links to the same controls. Gatherers bring back 6–10 provisions per assigned phase; personality adds a preferred-method bonus and Fieldcraft improves yield. Assignments can be saved in household work arrangements.

One provision feeds one resident for one day. A restored kitchen reduces total daily demand to 80%, rounded up. Travellers use the same stock. Meals happen only on evening-to-morning Advance. There is no spoilage or offline consumption. Fresh and upgraded saves begin with at least seven days supplied. Buying six provisions costs one crown; the garden and several earlier expeditions also provide food. Two assigned sustenance-ritual phases yield 18 provisions for one unreserved silver ivy and binding thread, requiring personally known Steady hearth wards. Cancelling refunds the inputs.

Automatic purchasing is off by default. It fills toward a configurable pantry target, respects a daily crown budget and treasury floor, and runs after free deliveries but before breakfast. The first two undersupplied days have no penalty. From the third, resting recovers at most one vitality per phase. A supplied morning clears the effect. There is no death, relationship penalty, permanent injury, or compounding hunger penalty.

## Chapter 6

Conclude Arms of Our Own, then read the overdue-wagon notice. The Hollow Road has five persistent obstacles: tracks, crossing, shelter defense, a disputed receipt, and wagon recovery. Every obstacle has a free ordinary route. Qualified active enchantments shorten work; prepared spells, Diplomacy, and a shield-bearing pair offer contextual alternatives. Returning early preserves progress. Rewards are once-only; cash respects the existing expedition wealth agreement.

Complete four undertakings: rescue the caravan, choose a supplier agreement, restore the Supply Office, and repair the roadside refuge. Food terms provide two free provisions per morning; material terms add five percentage points to delivery savings. Optional patrol assignments yield four provisions and two crowns per two assigned phases. Velis's recruitment remains separate from completing the chapter.

The Supply Office consolidates material plans. Available stock is deducted once while respecting reserves; recipe suggestions are editable. Reviewed orders cost 15% less than immediate material value before rounding and arrive in two Advance phases. Velis assigned to procurement raises the saving to 30%. Up to four funded orders may be pending; cancellation refunds exactly. Ordinary immediate purchases remain available on the same Stores page.

Velis's installed room specialty delivers four free provisions each morning, capped at the configured target. This is separate from paid top-ups and does not require leaving her assigned to procurement. It can combine with food supplier terms.

## Velis

Includes correspondence and voluntary visiting/residency, personal quest, two resident-story scenes, four household relationship beats, specialist conversations, room activity, pair conversations, a three-stage almanac friendship arc, personal disclosures, tastes, four mutual romance milestones, expedition perspectives and private camp interaction, and a signature walking-staff request. Wardrobe progression has three illustrated levels; full-body overview art is set in her Supply Office for every level.

Ten optimized WebP assets are included: three overview portraits, three portrait crops, Supply Office, Hollow Road, food icon and signature staff icon. Seven images were generated using the built-in image tool. The asset manifest records dimensions, byte counts and hashes. The existing artwork and bundled content archives remain intact.

## Cohesion and efficiency review

- Reused primary assignments, advance resolution, transactional actions, headquarters projects, existing material prices, reserve protection, recruitment, wardrobe and relationship systems.
- One provisions record and one management surface prevent duplicate food inventories and shops. The home strip is compact; purchase policy, workers and ritual details are collapsible.
- Added pantry information at departure and meal/gathering forecasts before Advance. Clarified garden forecasts so food is never described as crowns.
- Free supplier deliveries, Velis's passive specialty and paid automatic replenishment have distinct explanations. Procurement is offered only to Velis; other residents receive useful gathering/patrol assignments.
- Chapter 6 uses Chapter 4's barracks and Chapter 5's gear and enchantments; ordinary routes remain sufficient. Food rewards also occur in earlier expeditions.
- Recruitment does not force romance or residence. Custom characters with the same name are preserved.
- Paid deliveries, cancelled rituals, rewards and partial fieldwork have bounded and persistent accounting.

## Upgrade and validation

Run `python server.py`. Keep the complete existing `data/` directory when updating. Schema 61 creates a pre-migration SQLite backup, preserves prior progress and artwork, and grants the food buffer once. The archive excludes personal saves.

The included verification and regression reports record the final checks. Continuous solo and company routes complete all six chapters using earned resources. Headless UI checks exercise templates and controllers; they do not verify rendered layout. Browser screenshots and visual acceptance remain outstanding because the previous local preview was blocked and user screenshots are deferred.
