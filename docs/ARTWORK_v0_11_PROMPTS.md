# v0.11 — accommodation artwork provenance

Mode: built-in image generation, two independent generation calls; no API-key CLI fallback. Both returned images were inspected before being integrated. They were converted to local WebP assets without cropping or repainting. The app serves these local assets and does not call an image model at runtime.

## West chamber

App asset: `static/assets/west-chamber.webp`

Workspace path: `/workspace/scratch/97fdaeb54bba/stonework-and-spellcraft/static/assets/west-chamber.webp`

Generation prompt:

> Use case: stylized-concept. Asset type: landscape interior illustration for the self-hosted fantasy household RPG Stonework and Spellcraft. Create the WEST CHAMBER: a small, restored but humble single-person castle bedroom with exactly ONE narrow wooden bed, plain slightly rumpled linen, a dull plum wool blanket, rough old stone, low timber rafters, a deep window recess with one tiny violet glass bottle, a small writing desk with an open book, a worn coat hook. Natural eye-level perspective from the doorway, broad landscape composition. Handmade enchanted library-workshop, dark academia with warmth. Visibly hand drawn graphite underdrawing, fine uneven ink contours, watercolor and matte gouache on DARK GRAINY PAPER, dry brush and pencil accents, imperfect handmade linework. Predominantly midnight navy and near black, desaturated warm violet, tiny worn archival gold accents. The entire scene is DIM and restful, only a small low amber bedside lamp and faint lavender window light. Keep shadow details readable, low saturation and very restrained light. Welcoming lived-in practical magic, no palace grandeur. No people, no modern tools, no text or lettering, no logos, no decorative border. Avoid opulence, bright golden glow, chandeliers, lush brocade, glossy CGI, plastic, photorealism, excessive filigree, glowing magic circles or fantasy splash art.

## Garden chamber

App asset: `static/assets/garden-chamber.webp`

Workspace path: `/workspace/scratch/97fdaeb54bba/stonework-and-spellcraft/static/assets/garden-chamber.webp`

Generation prompt:

> Use case: stylized-concept. Asset type: landscape background illustration for a handmade fantasy household web game. Paint the GARDEN CHAMBER: humble restored castle guest bedroom with exactly TWO SEPARATE narrow wooden single beds, one along each side wall, each with its own bedside stool and closed personal chest, an open central aisle. Plain linen and thin faded lavender and moss-grey wool blankets. Two modest leaded windows in the rear rough stone wall overlook faint dark fern silhouettes; just one small potted fern indoors. Low exposed wooden ceiling, small practical shelf with books. Natural eye-level view from doorway, wide 16:9 landscape. Hand of the maker MUST be visible: visibly DRAWN uneven graphite and thin ink contours, matte watercolor and gouache washes, dry-brush edges, fine colored-pencil marks on dark grainy handmade paper. Simplify details into painterly shapes, avoid photographic texture and 3D render. Dim, inhabited, welcoming archive-workshop mood. Midnight navy, near-black, restrained violet, ghost lavender and muted grey green; only ONE small amber oil lamp in the middle provides a very small pool of warmth. Mostly dark, quiet, desaturated, not overlit. Beds clearly separate, cozy but not luxurious. No people, no modern objects, no readable text, no logos, no border. Avoid opulence, grand arches, rich carpets, velvet drapery, excessive ornament, bright golden lighting, sparkling magic, polished plastic, CGI, photorealism and fantasy splash-art clutter.

## Review and compatibility

Both images meet the intended modest scale, dim lighting and separate one-bed/two-bed room identities. These are painted room illustrations, not exact architectural plans or procedural furnishing renders. The runtime overlays furnishing controls separately. Character artwork was not regenerated. Default room paths are distinct, while existing accepted uploads and rollback histories remain in effect.
