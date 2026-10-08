# Development v0.57 — Conversations that continue

This release adds 106 authored conversations and 318 response choices, expanding how the scholar and all fourteen companions get to know each other. The earlier personal chapters, wardrobe invitations, shared activities and specialist stories remain available.

## Where to begin

Open **People → Life together → Conversations & friendships**, or use **Someone has time for you** on Home. Select a resident, then choose Ready to share, Personal arcs, Between residents, Life & magic, Everyday company, At the table, Remembered or Set aside.

Read the opening and choose the response that suits you. The answer stays visible after you choose. Follow-ups quote what you actually said, and the final chapters of all fourteen personal arcs and ten peer arcs contain a distinct opening based on the preceding choice. This is authored continuity, without a runtime model deciding relationship outcomes.

A later arc chapter requires at least one phase after its predecessor. Conversation itself does not advance time or change anyone's work assignment. Invitations never expire. **Later** places an invitation under **Set aside**; restore it whenever you want. Completed conversations can be reread, with their original choice and date intact.

## Content added

| Category | New conversations | Purpose |
|---|---:|---|
| Personal arcs | 42 | Three chapters for each of fourteen companions, with curiosity, warmth and disagreement all supported. |
| Resident relationships | 30 | Ten three-part arcs: friction or discovery, a negotiated change, and a later outcome. |
| Life and magic | 14 | Character-specific conversations unlocked by a real completed casting, returned expedition discovery or completed lasting circle. |
| Everyday company | 14 | Humour, songs, food, books, keepsakes and ordinary preferences. |
| At the table | 6 | Small gatherings with two or three residents, including room to participate quietly. |

The new scenes contain approximately 12,471 words before the additional branching follow-ups. Response options are specific to the conversation rather than generic affection buttons. Residents question, disagree, tease, apologise and develop shared references; not every discussion needs a tidy agreement.

## Personal arcs

## Relationships between residents

These relationships are shown through remembered exchanges, not a hidden affection score. The player can ask questions, offer company, suggest a compromise or step back while the residents retain distinct views. Later pair dialogue follows the actual previous choice. Current residents must be home together to participate; unrecruited or absent people cannot be made to join through an action request.

## Connections to existing play

New completed conversations count once toward the existing optional wardrobe invitations. Reading, deferring and restoring an invitation do not create additional memories. No portrait, outfit, romantic relationship, assignment or numerical ability changes automatically.

The Home page offers up to three ready invitations, prioritising follow-ups and unlocked gameplay reactions. It does not interrupt work or advance a story by itself. All other available conversations remain accessible in Life together.

Optional generated dialogue receives up to twelve completed conversations involving the speaking resident, including the player's actual response. It receives neither future scene outcomes nor other residents' private conversations. The authored content remains fully playable without a provider or network connection.

## Saves and upgrading

Schema 48 adds a social memory record and a list of set-aside invitations. Existing spells, rituals, accepted artwork, outfits, shared memories and all other progress are preserved. Stop the old server; extract v0.57 into a fresh folder; copy the complete existing `data` directory, including `data/assets`; run `python server.py`. The normal database migration backup is created automatically. Keep the old release and its backup for rollback. No offline phases pass.

The 159 bundled raster assets, including all 38 v0.56 spell and ritual icons, are unchanged. Existing portraits identify conversation participants.

## Verification

Tests exercise every conversation with all three choices, all 24 branching conclusions, phase gates, actual-event gates, absent participants, invalid actions, non-expiring deferral, unchanged resources and assignments, scoped dialogue memories, save migration and idempotent retries. Connected UI tests verify home invitations, displayed replies, callbacks, branches, later/restore, participant portraits, rereading and reload.

These are rules and connected headless UI checks. Browser layout review remains deferred; no visual-browser verification is claimed.

Final results: **614 Python tests and 33 connected headless UI suites pass**. All bundled artwork passes its existing hash and HTTP-serving checks.

