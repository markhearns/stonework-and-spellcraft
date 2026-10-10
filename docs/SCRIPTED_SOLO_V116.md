# Solo narrative direction — v0.116

The solo game does not require an LLM gamemaster. Authored scenes, bounded character creation and saved choices provide its narrative. The Python rules remain authoritative. This decision supersedes the runtime-gamemaster requirements in the original v0.1 specification; the original document remains a historical design record.

| Original gamemaster responsibility | Current scripted implementation |
| --- | --- |
| Introduce the opening companion and the castle mystery | The authored opening, chapter controllers and `castle_mystery.py` reveal a fixed sequence of evidence. Reloading or choosing another conversation does not rewrite the explanation. |
| Create coherent residents | `character_pool.py` combines compatible ancestry, background and temperament records into a persistent adult identity, bounded starting package, ambition, hobby, value and personal difficulty. Creation is available without a provider. |
| Contact, summon and recruit people | `candidate_proposals.py`, `arrivals.py` and `summoning.py` validate the reviewed identity, choose the ordinary, exotic or constructed route, check preparation and accommodation, and keep visiting and joining separate decisions. Koharu is a local kitsune and uses an ordinary local introduction. Ogrekin (formerly Oni), including Kaede, use ordinary recruitment; the ancestry pool and bundled content agree. |
| Give companions something meaningful to say | Authored companions retain their specific dialogue trees and remembered choices. `scripted_companions.py` gives eligible created residents work, values and company topics with three specific responses, saved replies and later callbacks. Compatible hobby/value text must still be present in the approved identity; edited identities are not silently overwritten. |
| Develop personal ambitions | `personal_stories.py` prepares bounded stories offline, with explicit funding, assigned work, completion and optional follow-up. Existing authored projects and personal paths remain. |
| Run household events and relationships | Existing household stories, invitations, resident friendships, routines and relationship controllers resolve explicit choices and phased work. The player can review and edit scene drafts. Narrative wording cannot create consent, membership or mechanical rewards. |
| Present expeditions, discoveries and chapter outcomes | Existing authored expedition and chapter controllers select scenes, enforce prerequisites and record choices and consequences. There is no promise of unlimited generated adventures. |
| Propose magic, artifacts and construction | Existing catalogues, research and construction controllers supply defined designs, costs and prerequisites. Unrecognized effects cannot be granted by prose. |
| Summarize resolved events | `scripted_narrative.py` creates an exact account of the last Advance through the existing recoverable draft/accept path. It reads recorded outcomes and adds no invented accomplishments or undiscovered lore. |
| Generate or correct illustrations | Bundled art, portrait imports, accepted revisions and history remain. New model-generated illustrations are optional and separate from game rules; scripts cannot create bespoke painted portraits. |
| Support corrections and review | Existing drafts, explicit acceptance, state revisions, validation, backups and portrait history remain the review mechanisms. There is no arbitrary natural-language command that rewrites campaign state. |

Optional text-model settings remain for players who want prose assistance. They are not required for the solo campaign, candidate creation, recruitment, personal-story preparation or phase accounts. These scripts provide curated variation, not unrestricted semantic understanding or an autonomous simulation of every possible personality.

Eris and Selene as separately controlled co-op founders remain deferred. This change neither simulates them nor claims an external-agent integration.

The user has requested replacing Bovinefolk as an ancestry. Dwarves, Goblins and Trollkin were proposed; selection is still pending. Bovinefolk remains available until a replacement is chosen and its mechanics, art and references can be changed together.
