# Current public integration

See [CONTENT_INTEGRATION_V039.md](CONTENT_INTEGRATION_V039.md) for the current release. The v0.37 review-only checkpoint below is retained as history; its statements about disabled proposals are superseded by the v0.38 adapters and v0.39 content lifecycles.

# Public pack integration — v0.37

## Included and reviewed

The submitted public ZIP is bundled unchanged in `content/`. Its sixteen packs are validated on demand and stored in the campaign database. Private pack 13 is absent and was not accessed. The original foundations digest remains `95a4ac6af6c67709215604bb26923aeb1f1c42fdeb48c7e5c86797b655ec4831`.

| Pack | Content records | Disabled mechanics proposals |
| --- | ---: | ---: |
| ss-books-food-gardens-and-treasures | 124 | 0 |
| ss-communities-services-and-visitors | 64 | 1 |
| ss-encounters-and-care | 72 | 0 |
| ss-household-scenes-and-ambient-life | 160 | 0 |
| ss-materials-and-properties | 72 | 13 |
| ss-personal-arcs-and-relationships | 78 | 0 |
| ss-rituals-and-voluntary-augmentation | 42 | 42 |
| ss-tutorials-explanations-and-qa | 144 | 0 |
| ss-artifacts-and-recipes | 80 | 40 |
| ss-equipment-and-signature-items | 96 | 45 |
| ss-expeditions-and-discoveries | 126 | 0 |
| ss-magic-principles-and-spells | 126 | 69 |
| ss-rooms-furnishings-and-synergies | 120 | 60 |
| ss-art-and-visual-production | 93 | 0 |
| ss-backgrounds-training-and-perks | 102 | 48 |
| ss-letters-commissions-and-gifts | 100 | 1 |
| **Total** | **1,599** | **319** |

## Player controls

1. Open About & saves → Public expansion content.
2. Choose Validate & stage included public bundle. Staging does not activate foundations or alter campaign progress.
3. Inspect a pack, select a record, and choose Read record.
4. For household scene templates, select the required residents and record evidence for the scene context and established facts. Create an editable invitation.
5. In Household life, review/edit the wording, offer the invitation, and separately choose a reply or decline/defer.

All 80 scenes support composition. The 80 ambient-life records remain review-only. Imported `establishesFacts`, follow-ups, costs and effects are never interpreted as executable instructions. Consent and personal-context review cannot be proven from free-text notes; human review remains necessary. Invitations do not expire, award resources, change affection meters, or author Eris/Selene's actions.

## Integrity and persistence

Strict nested schemas cover all public record types. The validator checks declared exact-version dependencies, baseline room/ancestry references, typed cross-record references, stable IDs, public visibility, shared tag meanings and bounded input. Public bundle staging is transactional and repeatable; conflicting staged versions cause the whole operation to fail. Single-pack uploads retain immutable versions. Backups include staged records and frozen invitations.

No migration: schema 35 already contains the required scene structures. Existing campaign identities, progress, assignments and inventory are preserved. No proposed mechanics are enabled by import. Narrative seeds are candidates, not accepted history. Source metadata and full scene records are captured when composing; later pack changes cannot rewrite an invitation.

## Verification

407 Python tests pass, including real HTTP staging and scene creation, full counts and foundation digest, repeated imports, conflicting-import rollback, backup inclusion, all eighty scene compositions, malformed nested records, presence/ancestry/external-player checks, request retry, stale revision rejection, review/decline/restore/join and resource/time invariance. Fifteen connected Node headless UI suites pass, including the new staging-to-conversation flow. JavaScript syntax checks pass.

The supplied pack-16 scene-decline/reload scenario informed coverage of persistent deferral and no shared memory on decline; the scenario corpus itself was not executed. Its 64 records are reviewable test designs. No rendered-browser/layout, live-model, Docker-runtime or external-agent verification is claimed.

## Remaining implementation

Materials, equipment, artifacts, magic, rituals, furnishings, expedition/encounter content, communities, arcs, letters, books/gardens, visual prompts, tutorial copy, and background/perk proposals are reviewable but not installed as rules. Optional model drafting remains the existing reviewed scene workflow. The next mechanics expansion should implement a small, complete acquisition → crafting → ownership → useful bonus loop, with protected reserves and exact once-only cancellation refunds. Proposed fabrication perks must share the existing alternative support channel rather than stack with room support.
