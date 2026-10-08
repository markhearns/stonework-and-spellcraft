# Development v0.59 — Someone to share the work

Companions can now suggest useful expedition approaches, take complementary roles, and invite you to discuss actual training and journeys. Suggestions and conversations wait for your choice; nothing takes over the party or advances time automatically.

## Where to begin

Open **Expeditions → Stormwatch beacon** after completing Hearth wards research. Before departure, expand **Compare the party** to see resident portraits, all six attributes, trained skills, prepared spells, availability and the beacon roles each person can fill. Choose a companion using the existing field-companion selector; travelling alone remains supported. Existing fieldwork agreements are still required.

At eligible Cinder aqueduct or Stormwatch encounters, **A companion has an idea** presents up to two valid suggestions in that companion's voice. Each suggestion uses the existing authoritative action and shows its approach and time or requirements. You may accept it or choose any other method. Suggestions do not spend components, grant progress or change a relationship merely by appearing.

## Stormwatch beacon

A storm has damaged a coastal warning station. Six connected encounters offer **26 methods**: six free patient methods, seven individual specialist methods, six ordinary teamwork methods, five individual spell methods and two spell/team combinations.

| Encounter | Ordinary solution | Examples of alternate solutions |
|---|---|---|
| Fallen pine | Clear branches over three phases | Use leverage; brace the trunk while a partner releases it; cast Giant's grasp |
| Broken bridge | Follow the lower path over three phases | Traverse braces; anchor a partner's crossing; use Borne flight; anchor a Windstep caster |
| Suspicious keeper | Listen and agree repairs over two phases | Negotiate a credible agreement; explain the technical fault; combine a scholar's explanation with a diplomat's delivery |
| Flooded gear | Drain the inspection pit over three phases | Repair the bypass; brace a service arm for precise tool work; use Undertide breath; clear the pin with Water jet while a partner withdraws it |
| Warning echo | Observe its quiet intervals over three phases | Complete the old watch report; sustain a countertone while a partner speaks; quiet the echo with Calming tide |
| Turning lens | Mark each stop over three phases | Reconstruct alignment; turn the cradle while a partner reads the light; use Lucid sight |

Additional methods take one assigned phase. Individual specialist requirements use the v0.58 score of 9, including eligible companion help. Team roles each require 8 in their own attribute + twice skill, without sharing the same actor between both roles. The interface names the two actual people who qualify. Spell/team combinations require the prepared caster to fill the designated casting role, personally know the principles and have the components. Spell costs are shown before agreement and paid once.

No route inflicts injury or requires random success. Every encounter retains a no-cost, no-attribute, no-companion method. A solo character with minimum attributes can complete the entire expedition. There is no timer or penalty for choosing the patient route.

Departure and return each take one phase. Completed encounters and paid unfinished methods persist on retreat. A saved team method requires its original participants and role qualifications to resume; otherwise the patient route remains available as a replacement. Methods record the people who actually contributed working phases. Supplies committed to saved spell work are not charged again when it resumes.

The first completed return deposits 30 crowns according to the existing wealth plan, 2 moon glass and 3 binding thread. Each returning participant receives 3 advancement once. An unfinished return grants no field reward. A completed site cannot be repeated to farm rewards.

## Practice conversations

Completing a resident's attribute or skill training creates a non-expiring **Practice & journeys together** invitation on their character sheet and in **Life together → Conversations & friendships**. Completing a companion-taught skill lesson for the founder creates an invitation with the teacher too. Home highlights up to three ready invitations.

All fourteen established companions have individual practice voices. Mira distinguishes recognising an explanation from using it; Kaede reflects on letting someone see an imperfect attempt; Tamsin stops postponing her own learning; Brakka wants the careful parts of competence noticed. Generated residents have a neutral fallback rather than borrowing another person's identity.

Each invitation names the actual subject and attained score or rank, and records an actual teacher when applicable. Choose to ask what changed, rehearse an explanation together, or recognise the work and take a break. These are social scenes, not a second numerical training reward. No advancement, assignment, currency or time changes from conversation alone.

Each person/learner/subject/rank invitation is created once. Retraining and relearning the same rank do not duplicate it. An unfinished or cancelled training project creates no invitation. Older completed training is not retrospectively invented as a new event.

## Conversations after the journey

A companion who returns from Stormwatch can invite you to discuss returning early or restoring the beacon. All fourteen companions have distinct return voices. The conversation draws on that person's actual completed work, including the specific method used, teamwork and spell preparation when applicable.

Choose to thank them, discuss what to do differently next time, or put the report aside and ask how the experience felt. An early return is acknowledged as unfinished; a person left at home receives no journey invitation or private memory. Only completed conversations are supplied to that resident's optional generated dialogue context.

**Later** sets an invitation aside without expiry. Restore it when ready. The chosen reply stays visible immediately after sharing; past scenes remain under **Remembered & set aside**. Repeated requests or rereading never produce a second reward or rewrite the memory.

## Usability changes and review status

- Portrait-led party comparison with attributes, skills, prepared spells and concrete beacon roles.
- Companion suggestions above aqueduct methods, with other approaches retained.
- Actual role holders shown for qualified team approaches.
- Spell icons and component explanations on magical encounter choices.
- Beacon magic presented among its encounter methods rather than misleading Cinder-only casting controls.
- Correct travel descriptions for both the six-encounter beacon and twelve-encounter aqueduct.
- Newly chosen practice/return responses remain visible instead of immediately disappearing into collapsed history.

A rendered review was attempted. Playwright is present but its Chromium executable is not installed, and the cloud browser rejects access to the local test server with `net::ERR_BLOCKED_BY_CLIENT`. No visual browser review or screenshot verification is claimed. The temporary review server was stopped. Connected UI tests exercise the real templates/controllers and Python store, including the complete new expedition; they do not substitute for visual browser inspection.

## Saves and installation

Release **0.59**, save schema **50**. Migration adds empty beacon progress and companion-participation records; it preserves existing attributes, skills, spells, images, inventory, relationships, unfinished work and social memories. No retrospective completed training or journey is fabricated.

Stop the old server, extract this release into a fresh directory and copy the complete existing `data` directory, including `data/assets`, before running `python server.py`. A pre-migration database backup is created automatically. Keep the old release and its backup for rollback. No offline time passes.

All existing artwork and the 38 spell/ritual icons remain bundled. The new beacon uses existing portraits and spell icons; no new site illustration is claimed.

## Verification

**646 Python tests and 35 connected UI suites pass.** See `VERIFICATION_V059.json`, `UI_REGRESSION_V059.json` and `BROWSER_REVIEW_V059.json` for final results and the precise review boundary. Tests cover every beacon method, minimum-attribute solo completion, distinct team roles, caster ownership and exact costs, retreat/resume, changed or retrained parties, once-only return rewards, actual training and teaching invitations, private context, deferred scenes, save migration, retries and a connected UI journey from preparation to remembered debrief.
