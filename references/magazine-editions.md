# Jaramsae v0.8 — TIO-first magazine editions

## Reference hierarchy
1. Primary cover: [TIO](https://www.instagram.com/tio_korea/). The user's previously approved Signature Cover is the concrete visual acceptance baseline. Do not claim to have inspected the current Instagram feed if inaccessible.
2. Secondary references: [MMM](https://www.instagram.com/mmm_mag_official/), [Eyesmag](https://www.instagram.com/eyesmag/), 생매거진, [Our Expresso](https://www.instagram.com/ourexpresso/). These are user-selected inspiration, not exact reproductions or verified current-feed analyses. No third-party marks, assets or proprietary templates.

## Shared cover rules
Read signature-cover.md. All editions retain 1080×1350, a full-bleed subject-centered photograph, exact institution name at top center, one light eyebrow above two explicitly separated white bold headline lines at lower left, dark lower contrast treatment and small actual source at lower right. No extra body copy. A keeps the original CSS unchanged; B/C/D use restrained typography, contrast and spacing variations. Do not replace the cover with a bordered card or pale background.

## Four editions
| edition | Name | Secondary inspiration | Cover | Interior (article layout) |
|---|---|---|---|---|
| signature | A Signature | MMM | original approved cover | large photo above cream-paper article |
| modern | B Modern | Eyesmag | compact sans, crisp contrast | white editorial, large rectangular photograph, structured left-aligned typography |
| story | C Story | 생매거진 | softer gradient, spacious bold title | warm paper tone, serif headline, photo journal arrangement |
| creative | D Creative | Our Expresso | bolder condensed hierarchy, restrained accent line | large photo above institution-color article, restrained accent |

Use the same approved four distinct images, same copy and facts for all editions. Differences must be visible in rendered layout, not just names or rewritten copy. Use the approved photo-above-text article body in all editions. Preserve A's cover styling, not its former text-overlay interiors.

## Implementation and delivery
Use style=bold-photo-editorial and optional top-level editorial_variant (signature/modern/story/creative). Without this field, existing rendering is identical. For one approved four-slide post:
```bash
python scripts/make_editions.py path/to/feed.json --out output/four-editions
```
Runs the existing pipeline for A–D and combines them into editor.html. Use the existing local editing, selection, and PNG export features. Inspect all 16 rendered PNGs and compare each row at mobile size. If a title overflows, shorten the common headline for all editions or adjust the draft layout; never hide required facts. Publication approval remains manual.


## 최신 필수 규칙: 로고 없는 기관명 · 기사형 본문
이 지침은 이전 로고 허용 및 본문 후보 지침보다 우선한다.
- 표지 상단 중앙에는 원장님이 입력한 기관명 문자열 그대로 흰색 굵은 HTML 텍스트만 배치한다. 기관 로고, AI 생성 로고, 아이콘, 심볼, 이모지, 워터마크, 이름 옆 장식 도형은 일절 추가하지 않는다. 기관이 로고 파일을 제공하더라도 이 게시물에는 삽입하지 않는다.
- 기존 TIO 표지 디자인을 유지한다. 놀이 기록 본문 2~4장은 `references/magazine-body.md`의 사진 위·글 아래 기사형 구조를 기본값으로 한다. 네 시안에서 활동 사실, 사진, 카피는 동일하게 두고 실제 디자인을 변주한다.
- 이미지 생성 도구는 글자가 없는 사진 소재에만 사용한다. 실제 HTML/CSS 파이프라인을 실행하고 편집 가능한 HTML과 PNG를 확인하기 전 완료로 처리하지 않는다. 네 시안×4장의 기본 편집기와 권한 검수 규칙은 유지한다.
