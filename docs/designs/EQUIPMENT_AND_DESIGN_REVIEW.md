# Equipment and design review — v0.35

## Personal working tools

Open **Focus & equipment → Personal working tools**. Craft a Scholar’s working folio or Maker’s alignment gauge in the workshop, assign a finished copy to a household member, then prepare it. Both recipes require a vessel and a binding component and three base work contributions. Existing artifice, focus and facility bonuses can shorten actual crafting time.

The folio requires Reference binding; the gauge requires Clear instruction. Existing crafting rules determine whose knowledge and assignment apply. There is no extra purchase cost for claiming or preparing a finished item.

| Tool | Prepared benefit | Exclusions |
| --- | --- | --- |
| Scholar’s working folio | +1 assigned research/archive contribution | No learning, copying income, personal-story or automatic knowledge reward |
| Maker’s alignment gauge | +1 assigned artifact crafting contribution | No inscription, testing, training or passive output |

One working tool can be prepared per person. Preparing another replaces it. These bonuses add to the existing signature-focus and other applicable contributions; they cannot stack with a second working tool. The detailed contribution display includes the item’s personal name. Away characters contribute no household work.

Each person may own eight tools. Renaming preserves identity. Transfers require both owners to agree, both to be household members, and the founder and involved people to be home. A transferred item is stowed and records its ownership history. Ownership changes do not consume a phase or manufacture another shared copy. Departures do not erase ownership. There is no sale, destruction, arbitrary equipment effect or return-to-shared-stock action in this release.

## Household scene drafts

Compose an invitation from the active character pack in **Household → Open household life**. The normal editable offline text remains available. The optional model-written scene uses the configured provider and may incur usage. It receives the scene seed, reviewed prerequisites, participant identity and current saved clothing; it does not receive private conversations or castle lore.

The model must return exactly a title, invitation, opening and one reply per existing choice. It cannot add executable actions, costs, rewards or choices. Human prose review remains necessary to catch invented events or inappropriate assumptions; JSON validation alone does not establish semantic quality.

Requests are saved before the provider call. Checking/retrying the same request does not call the provider twice. Recover searches drafts for this exact scene. Failed drafts may already have incurred usage; a deliberately new request can incur new usage. Applying a reviewed draft updates the editable scene only. Offering the invitation and joining it are separate actions. Campaign changes invalidate acceptance; suitable wording can still be copied manually from a saved preview, or a new draft requested.

Five exact prerequisite statements can be verified by current rules: optional non-expiring invitations, separate clothing changes, library reading space, common-room leisure space and common shared space. The server recomputes this evidence. Consent, book ownership, access to private material and voluntary participation are never inferred from those facts.

## Expansion design packs

**About & saves → Equipment & magic design packs** accepts the exact handoff 01–04 ZIP formats:

- `ss-materials-and-properties`
- `ss-equipment-and-signature-items`
- `ss-artifacts-and-recipes`
- `ss-magic-principles-and-spells`

The first release is a staging and inspection workflow. It never installs proposed mechanics, property IDs, prices, recipes or spells into the rules. Remaining handoffs 05–17 are not supported by this reviewer yet.

ZIP safety limits are shared with character-pack import: 6 MB compressed/expanded, at most 100 entries, regular UTF-8 JSON/Markdown only, no extraction or unsafe paths. Checks cover exact wrappers/fields, bounded plain text, declared counts, unique local IDs, types, vocabulary, ancestry restrictions, references and exact dependency versions. Quantity shortfalls are warnings. Staged foundations packs can provide dependency IDs; expansion dependencies must already be staged. Different content cannot reuse a staged pack ID/version. The same digest can be submitted again safely.

Up to twelve design versions are retained per campaign in SQLite and complete save backups. Staging does not advance time, revise the campaign, grant inventory or alter any rule catalogue. The browser shows records and nested proposals as readable fields. Validation is structural; balance, coherence and fit still require implementation review.

`static/examples/expansion-design-fixture.zip` is a two-record fixture, not a production content pack. The original 17 handoffs and reference snapshot remain unchanged as a historical baseline.

## Verification and limits

v0.35 adds ownership/crafting/persistence tests, mocked-provider scene review tests, malformed-pack/dependency tests and real local HTTP coverage. Connected headless UI tests exercise the new controls through Python/SQLite. These checks do not substitute for rendered-browser layout inspection or live-provider evaluation. No rendered-browser, live-provider, Docker or external-agent run is claimed.
