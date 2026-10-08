# Reviewed visitors — v0.28

Open **Summoning → Propose & review a new visitor**. Describe a clearly adult exotic visitor. A configured text provider proposes an identity; the saved proposal cannot change campaign state. The three authored contacts continue to work offline.

## Review and admission

Read the proposed age, ancestry, appearance, personality, public origin, ambition, accommodation, willingness to stay and exact starting package. Check both review statements before approval. Structural validation does not replace human review of adulthood, coherence, independent preferences and the absence of unsupported promises in prose.

Approval fixes an enduring contact plan. It creates no person, spends no crowns, advances no time and reserves no bed. Choose the plan in Summoning and fund the ordinary 12-crown working with one vessel and one binding component, requiring two own conductor phases. Only completion introduces the person and initializes her independent records. Conversations, visits, two-sided membership, normal development/work, departure and same-person return follow the existing rules.

This implementation deliberately stages review before paid ritual preparation. Provider failure therefore cannot consume fictional ritual costs. There is no paid `awaiting-candidate` state in this version. Up to twelve reviewed plans are supported, alongside the authored catalogue. Permanent plan deletion and identity rewriting are not offered.

Visit-only candidates retain that preference; repeated household invitations cannot recruit them. Open-to-staying candidates still need both positive decisions during a visit. No proposal grants automatic romance or obedience.

## Bounded starting competence

| Package | Personally known principle | Starting practice |
|---|---|---|
| Archive reader | Gentle preservation | Patient scholarship |
| Light maker | Gentle refraction | Methodical assembly |
| Water worker | Water guidance | Methodical assembly |

Every package has zero starting skill ranks, zero earned advancement, no money or inventory grants, and one personal focus slot. A descriptive ancestry or occupation adds no mechanical power. Principles and practices remain separately learned, prepared and used.

Validation requires exactly the supported fields and rejects malformed JSON, duplicate or extra keys, non-integer ages or ages outside 18–25, common/unknown ancestries, unknown capability packages, unsupported accommodation/stay preferences and reserved or reused names. Eris, Selene and authored contact names are reserved even before introduction. Allowed ancestries currently include Demon, Seraph, Elemental, Vampire, Fae, Djinn, Dragonkin, Spirit, Dryad and Nymph.

## Recovery and continuity

Requests, provider results and reported usage are saved. Retrying the same request ID retrieves the result rather than making another provider call. Recover recent proposals through their separate draft-purpose filter. An interrupted processing record does not authorize an automatic second call.

If the campaign changes, **Recheck unchanged proposal** reruns validation against the current save without changing the proposal or calling the provider. It updates the review revision while retaining the original request revision for recovery. Approval is revision-checked and idempotent; losing its response cannot duplicate the plan.

Putting a preview aside keeps its saved draft. A 1,000–1,500 token output limit gives the structured response room; truncated or malformed results remain failed drafts. No live provider compatibility or quality guarantee is implied by fixture tests.

## Portraits, text and privacy

A reviewed plan has an explicitly labelled portrait placeholder. Use Illustration review to import and accept an image separately; previous accepted artwork can be restored. Artwork never grants ancestry powers or rewrites identity. The self-hosted app does not yet call an image provider.

Candidate prompts receive public cast names and ancestries, not private conversations or hidden castle truth. Profiles contain public authored/reviewed facts only. Personal dialogue later receives the introduced character’s own context. Generated names, roles and ambitions are escaped across generic screens. Reviewed-candidate prose has explicit provenance; provider outputs are not executable game instructions.

Schema 25 adds an empty reviewed-plan catalogue to older saves, without spending time or resources. Existing people and contact preparations are retained.

## Verification and remaining work

286 Python tests pass, including a real local HTTP route/filter/review test using a controlled provider response. Three connected headless UI suites pass: the full existing playthrough, companion-life controls, and candidate review/admission. The candidate flow tests explicit review, no-call recheck, paid contact, membership, malicious-markup escaping, personal dialogue, portrait review, departure and reload.

Actual browser layout and live provider calls remain unverified. Generated personal quests, custom mechanics, broader ability budgets, automated portrait generation and private-background generation remain outside this feature.


### v0.31 extension
The ancestry gate now accepts implemented common ancestries and Golem as well as the exotic list above. It assigns the arrival route from the validated ancestry, never from prose. Common plans cannot use summoning; constructed plans cannot open ordinary correspondence. See CHARACTER_POOL_AND_ARRIVALS.md for the current complete pool, compatibility checks, adult golem age exception and preserved ingredient provenance. Existing provider-only saved drafts remain reviewable. New UI proposals use curated ingredients and offer a provider-free composition path.
