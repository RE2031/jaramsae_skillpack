# Jaramsae v0.8 — TIO-first magazine editions

## Reference hierarchy
1. Primary cover: [TIO](https://www.instagram.com/tio_korea/). The user's previously approved Signature Cover is the concrete visual acceptance baseline. Do not claim to have inspected the current Instagram feed if inaccessible.
2. Secondary references: [MMM](https://www.instagram.com/mmm_mag_official/), [Eyesmag](https://www.instagram.com/eyesmag/), 생매거진, [Our Expresso](https://www.instagram.com/ourexpresso/). These are user-selected inspiration, not exact reproductions or verified current-feed analyses. No third-party marks, assets or proprietary templates.

## Shared cover rules
Read signature-cover.md. All editions retain 1080×1350, a full-bleed subject-centered photograph, exact institution name at top center, one light eyebrow above two explicitly separated white bold headline lines at lower left, dark lower contrast treatment and small actual source at lower right. No extra body copy. A keeps the original CSS unchanged; B/C/D use restrained typography, contrast and spacing variations. Do not replace the cover with a bordered card or pale background.

## Four editions
| edition | Name | Secondary inspiration | Cover | Interior (provisional) |
|---|---|---|---|---|
| signature | A Signature | MMM | original approved cover | original interior |
| modern | B Modern | Eyesmag | compact sans, crisp contrast | white editorial, large rectangular photograph, structured left-aligned typography |
| story | C Story | 생매거진 | softer gradient, spacious bold title | warm paper tone, serif headline, photo journal arrangement |
| creative | D Creative | Our Expresso | bolder condensed hierarchy, restrained accent line | asymmetrical photo placement, alternating composition, institutional accent |

Use the same approved four distinct images, same copy and facts for all editions. Differences must be visible in rendered layout, not just names or rewritten copy. Body layouts B/C/D are review candidates pending the user's detailed direction. Do not change A's existing cover or interior styling.

## Implementation and delivery
Use style=bold-photo-editorial and optional top-level editorial_variant (signature/modern/story/creative). Without this field, existing rendering is identical. For one approved four-slide post:
```bash
python scripts/make_editions.py path/to/feed.json --out output/four-editions
```
Runs the existing pipeline for A–D and combines them into editor.html. Use the existing local editing, selection, and PNG export features. Inspect all 16 rendered PNGs and compare each row at mobile size. If a title overflows, shorten the common headline for all editions or adjust the draft layout; never hide required facts. Publication approval remains manual.
