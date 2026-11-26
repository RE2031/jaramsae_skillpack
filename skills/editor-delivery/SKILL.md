---
name: editor-delivery
description: 원장님이 4개 시안을 비교하고 슬라이드를 직접 편집하는 독립형 HTML을 제공한다.
---
# editor-delivery

기본 게시물 제작 요청에는 한 게시물 4장 × 시안 4개를 제공한다. 사용자가 개수나 표지만 요청하면 그 요청이 우선하며, 4×4 편집기는 네 장짜리 시안 네 개에만 적용한다. 기존 Signature Cover v0.7을 A에 그대로 유지한다. 네 시안은 동일한 내용과 사진을 사용하되 실제 매거진 디자인을 다르게 한다. 본문 B~D는 검토용 후보이다. 활동 사실, 사진 출처, 기관명과 브랜드는 일치해야 한다. 동일한 시안을 이름만 바꿔 제공하지 않는다.

1. 각 시안별 JSON과 승인 이미지로 기존 pipeline.py를 실행하고 고유 출력 폴더 4개를 생성한다. 실제 PNG를 열어 확인한다.
2. `python scripts/build_editor.py output/A output/B output/C output/D --out output/editor.html --names "A · Signature" "B · Modern" "C · Story" "D · Creative"` 실행. 각 폴더에 editable/index.html, style.css, assets가 있어야 한다.
3. 원장님에게는 기존 3×3 피드 미리보기 대신 editor.html을 기본으로 제공한다. 각 시안은 4:5 슬라이드 네 장을 한 행에 배치하며 좁은 화면에서는 가로 스크롤한다. 4개 행을 비교할 수 있다.
4. 편집 패널은 기관명, 도입 문구, 제목, 본문, 출처, 제목 크기, 사진 교체, 확대 및 위치를 수정할 수 있다. 수정한 결과는 즉시 보인다. 사진이 내장된 프로젝트 HTML을 저장하고 다시 열면 편집을 계속할 수 있다. 수정 시 공개·사용 권한이 확인된 사진만 교체하고 출처도 갱신한다.
5. 선택안 HTML 저장은 선택한 네 장의 편집된 HTML을 출력한다. 저장된 프로젝트/선택안 HTML은 원장님 로컬에만 보관되며 서비스 DB 저장 기능은 아니다.
6. 게시 PNG가 필요하면 `python scripts/export_editor_selection.py jaramsae-selected-version-1.html --out output/approved-png`으로 다시 렌더링한다. 브라우저 안에서 직접 PNG 저장은 아직 지원하지 않는다. 글자 넘침 검사 후 실제 시각 검수와 원장님 승인을 받는다.
7. 편집기 파일의 실제 열기, 16장 표시, 텍스트 수정, 시안 선택, 저장 및 다시 열기를 검증하고 테스트하지 못한 항목은 명시한다.

기존 자동 렌더링/기술 검수 및 이미지 권한 규칙은 유지한다. 기존 출력 preview.html은 호환성용으로 유지하되 4개 시안 제작 시 기본 전달 파일은 editor.html이다.

## TIO 우선 매거진 시안 — 최신 우선 지침
`references/magazine-editions.md`를 먼저 읽는다. TIO(@tio_korea)는 표지 최우선 레퍼런스이며 기존 승인 Signature Cover는 A에 그대로 보존한다. MMM, Eyesmag, 생매거진, Our Expresso는 시안별 보조 레퍼런스다. B/C/D도 풀블리드, 상단 중앙 기관명, 하단 얇은 도입 문구, 정확히 두 줄 굵은 흰색 제목, 우측 하단 출처, 표지 본문 없음이라는 TIO 기반 구조를 유지하면서 타이포/명암/여백을 변주한다. 네 시안에서 사진·활동 사실·카피·브랜드는 동일하게 유지하고 실제 CSS 배치·서체·사진 영역을 다르게 한다. 본문은 아직 사용자 최종 승인 전인 후보 디자인이며 기존 A를 유지한다. 네 시안은 각 4장 한 줄, 총 16장 편집기로 제공한다. 단일 표지 요청에는 A를 기본으로 한다. 원본 권리 확인 및 실제 파이프라인 검수는 기존 규칙을 유지한다.

## Four-edition command
동일한 원본 4장 JSON이 준비되면 `python scripts/make_editions.py INPUT.json --out output/고유명`으로 네 개의 실제 디자인을 생성한다. 선택 및 편집 기능은 동일하다.
