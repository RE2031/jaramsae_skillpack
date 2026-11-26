# Instagram Feed Skill Pack v0.8
한국어 보육기관 인스타그램 피드 제작용 Agent Skills + 렌더러. 원장의 자연어 요청을 받은 AI 에이전트가 콘텐츠 JSON을 작성하고, 로컬 렌더러가 편집 가능한 HTML/CSS와 PNG를 생성한다. 자체 서비스 홍보 및 자동 게시 기능은 범위 밖이다.

## 빠른 시작
Python 3.10+ 및 한국어 폰트(Noto Sans CJK KR 또는 맑은 고딕)를 설치한다.
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/pipeline.py examples/demo.json --out output/demo
```
Windows에서도 동일하게 실행한다. 시스템 Chromium을 사용하려면 `--browser /path/to/chromium`을 추가한다. `output/demo/preview.html`을 브라우저에서 열면 피드와 슬라이드를 확인할 수 있다.

## AI 에이전트 사용
저장소를 에이전트에서 열고 다음처럼 요청한다.
> skills/instagram-feed-creator/SKILL.md를 읽고 실행해. 우리 어린이집은 신입 원아 모집이 목적이고 따뜻하고 전문적인 피드를 원해. 9개 게시물을 만들어줘.

`AGENTS.md` 및 메인 스킬이 하위 스킬을 순서대로 안내한다. Codex, Claude Code, Antigravity 등에서 파일을 직접 읽는 방식으로 사용하도록 설계했다. 각 제품의 네이티브 자동 탐색/설치 방식은 버전별로 다르므로 이 저장소는 특정 경로를 강제하지 않는다. 실제 에이전트별 실행 호환성은 아직 검증하지 않았다.

## 원장님 최초 설정
처음에는 [최초 설정 질문지](prompts/onboarding.md)의 여섯 가지 질문(기관명, 연령대, 교육 철학, 강점, 운영 목적, 분위기)에 답변한다. [기관 설정 스킬](skills/institution-onboarding/SKILL.md)이 답변을 [프로필 스키마](schemas/brand-profile.schema.json)에 맞춰 정리한다. [햇살숲 예시](examples/brand-profile.json)는 가상 기관이다.

프로필 저장이 가능한 환경에서는 기관별 비공개 저장소에 저장하고 이후 게시물 제작 시 재사용한다. 저장 기능이 없는 환경에서는 JSON을 따로 보관해 다시 제공한다. 실제 고객 프로필은 Git에 커밋하지 않는다. 이 기능은 에이전트 지침과 데이터 형식이며 별도 서비스 UI/DB는 아직 구현하지 않았다. 기존 Signature Cover 및 렌더러는 그대로 사용한다.

## 스타일
- `bold-photo-editorial` (기본값): 풀블리드 사진, 하단 어두운 그라데이션, 대형 흰색 헤드라인을 사용하는 고밀도 사진형
- `editorial-hybrid`: 사진과 학부모 정보 전달을 균형 있게 구성하는 에디토리얼 혼합형
- `photo-lifestyle`: 실제 공간 사진 중심
- `emotional-editorial`: 여백과 감성적인 사진 중심
- `modern-magazine`: 강한 헤드라인과 편집형 구성
- `minimal-information`: 정보 전달 및 체크리스트

기본 `bold-photo-editorial`은 사진이 캔버스를 가득 채우고, 하단의 어두운 그라데이션 위에 작은 도입 문구 한 줄과 큰 흰색 제목 두 줄을 배치한다. 첫 장에는 보조 설명을 넣지 않는다. 사진 약 75% / 텍스트 약 25%를 시각적 출발점으로 삼는다. 모든 슬라이드에 승인된 사진이 필요하며, 이미지 안에 텍스트를 생성하지 않고 HTML/CSS로 편집 가능한 텍스트를 렌더링한다. 정보가 더 필요한 콘텐츠는 `editorial-hybrid`를 선택한다. 기관 고유 브랜드 가이드가 있으면 이를 우선한다.

브랜드의 일반적인 시각 문법을 참고했으며 제3자 로고·사진·고유 템플릿을 포함하지 않는다. 사진은 기관이 공개 홍보 권한을 확인한 로컬 파일만 사용한다. `bold-photo-editorial`은 승인된 사진이 없으면 실행하지 않는다. 사진이 없다면 기관에 사진을 요청하거나 `editorial-hybrid`/`minimal-information`으로 스타일을 변경한다.

## 결과물
`editable/index.html`, `editable/style.css`, `editable/feed.json`, `editable/assets/`, `png/post-01-slide-01.png` 등, `preview.html`, `captions.md`, `review-report.json`. JSON을 수정한 후 재실행하거나 HTML/CSS를 직접 수정할 수 있다. HTML 직접 수정 후에는 `--rerender`로 PNG를 재생성한다.

## 범위와 제한
AI 콘텐츠 생성은 에이전트가 담당한다. 렌더러 자체는 LLM이나 사진 검색 API를 호출하지 않는다. 데모는 가상 기관이며 게시 금지. 자동 검수는 규격·텍스트 넘침·이미지 로딩·구조 검사 중심이며, 실제 사실과 개인정보 및 디자인 품질은 사람이 승인해야 한다. 자동 게시하지 않는다. 출력 폴더는 새 경로를 사용한다(기존 폴더 덮어쓰기 방지).

## v0.6 Bold Photo Editorial 기본 스타일
기본 스타일을 `bold-photo-editorial`로 변경했다. 사용자가 제공한 피드 레퍼런스의 일반적 디자인 문법인 풀블리드 사진, 상단 중앙 브랜드, 하단 어두운 그라데이션, 작은 도입 문구, 큰 흰색 헤드라인, 짧은 보조 설명을 기관 콘텐츠에 맞게 재해석했다. 제3자 로고·사진·고유 카피는 복제하지 않는다. 모든 슬라이드에 승인된 사진이 필요하며 이미지 생성 텍스트 대신 HTML/CSS 텍스트 레이어를 사용한다. 사진/텍스트 시각 비중은 약 75:25를 출발점으로 한다. `editorial-hybrid`는 정보가 많은 콘텐츠의 대안으로 유지한다. CSS 프리셋, JSON 스키마, 렌더러 사진 검증, 스킬 및 디자인 검수 기준을 업데이트했다.

## v0.4 시각 품질 개선
캐러셀별 동적 레이아웃(fullbleed-photo, split-photo, detail-photo, text-interlude)을 추가했다. 사진은 장면/거리/각도를 다양화하고 반복적인 카드 구조를 줄인다. 미리보기 HTML은 PNG를 base64로 포함하여 preview.html 단독 전달 시에도 이미지가 표시되도록 만들었다. quality_check는 미리보기 내장 이미지 수와 상대경로 잔존 여부를 검사한다. 문구 품질은 기존 카피라이팅 스킬을 유지한다.

## v0.3 실행 자동화 파이프라인
AI 에이전트는 콘텐츠 JSON과 승인/생성 이미지 파일을 준비한 뒤 반드시 아래 명령으로 전체 과정을 실행한다.
```bash
python scripts/pipeline.py path/to/feed.json --out output/unique-job-name
```
파이프라인은 환경 사전 검사 → Chromium/의존성 확인 → JSON 검증 및 HTML/CSS 렌더링 → 개별 PNG 출력 → 결과물 검증 순으로 진행한다. 실패하면 0이 아닌 종료 코드를 반환하며 완료라고 보고하면 안 된다. HTML/CSS 수정 후에는 `python scripts/render.py --rerender --out output/unique-job-name` 및 `python scripts/quality_check.py --out output/unique-job-name`을 실행한다.

### 출력물과 이미지 생성의 경계
렌더러는 LLM 또는 이미지 생성/검색 API를 호출하지 않는다. 콘텐츠 JSON과 이미지 파일은 에이전트가 먼저 준비해야 한다. 에이전트에 이미지 생성 도구가 없으면 기관 승인 사진을 사용하거나 텍스트 중심 레이아웃으로 진행한다. 파이프라인 성공 시 편집 가능한 HTML/CSS/JSON, 캡션, 출처 메모, 개별 PNG와 미리보기를 만든다.

## v0.2 사진 중심 에디토리얼
승인된 디자인 방향은 references/sunlit-editorial.md. 신규 스타일 sunlit-editorial, quiet-premium, warm-lifestyle. 신규 레이아웃 hero-left-copy, hero-right-copy, split-editorial, photo-caption, quiet-cover, minimal-announcement. 1~9개 게시물을 지원한다. 대표 게시물 한 장부터 검토한다.
```bash
python scripts/pipeline.py examples/editorial-single.json --out output/editorial
```
위 예시는 사진 없는 데모. 사진형은 승인 사진 파일을 JSON 옆에 놓고 image, image_approved, image_kind, image_credit, image_position을 지정하고 hero-left-copy를 사용한다. 생성/스톡 이미지는 실제 기관이 아님을 표시한다. 렌더러 자체는 이미지 생성 API를 호출하지 않는다. 이미지 생성 가능 에이전트가 별도로 소재를 준비한다. Noto Serif CJK KR 또는 바탕 서체 권장.

## v0.7 Signature Cover — 사용자 승인 표지
기본 bold-photo-editorial의 각 게시물 첫 장(단일 게시물 포함)에 필수 적용한다. 기존 다른 스타일과 2장 이후의 정보형 레이아웃은 유지한다.
- 1080×1350, 4:5. 사진을 화면 끝까지 채운다. 흐린 좌우 확장 배경, contain, 사진 축소 금지.
- 상단 중앙에는 원장님이 입력한 institution을 그대로 표시한다. 임의 기관명 및 모든 추가 로고·아이콘·심볼 금지.
- 아이의 얼굴·손·활동 소재(블록 등)가 크게 보이도록 원본을 확대하고 초점을 조정한다. 배경 가구보다 활동이 중심이다. 필요한 경우 원본 사진을 다시 고르거나 크롭한다. 얼굴이나 손·소재를 가리지 않도록 검수한다.
- 하단에는 활동을 나타내는 작은 얇은 도입 문구 1줄(eyebrow, 예: 오늘의 놀이 기록, 오늘의 교육 활동)과 굵은 흰색 제목 정확히 2줄만 배치한다. title에 명시적 줄바꿈 하나를 넣는다. 넘치면 문구를 다시 쓰고 글씨를 작게 줄이지 않는다.
- 표지 body는 빈 문자열, details는 비워 둔다. 설명은 다음 장 또는 caption에 넣는다. 제목 아래 설명·슬라이드 번호·분류 반복 금지.
- 우측 하단은 출처 | Pexels처럼 실제 출처만 작게 표시한다. stock의 image_source에는 실제 플랫폼명을, image_credit에는 상세 출처/저작자 정보를 기록한다. 생성 사진은 출처 | AI 생성으로 명시한다. 기관 제공 사진은 실제 출처에 맞게 표시한다.
- 스톡 사진을 실제 원아나 활동 기록처럼 오인시키지 않도록 caption에 대체 사진임을 명시하고 사용 권한을 검증한다. Pinterest는 원본 권리 확인 없이 사용하지 않는다. 생성/스톡 표시 및 게시 승인 상태는 표지의 추가 본문이 아니라 캡션·검수 보고서에 기록한다.
- 하단 그라데이션을 제한해 얼굴과 활동을 밝고 선명하게 유지한다. PNG를 실제로 열어 아이와 소재가 충분히 큰지 확인한다.
- image_zoom(1~3), image_focus_x/y(0~100)를 필요에 맞게 조정할 수 있다. 기본 확대 1.15, 중심 초점 50/50은 출발값이며 사진마다 수정한다.

### 표지 입력 예시 (슬라이드 일부)
```json
{
  "title": "블록 하나로 만드는\n나만의 작은 세상",
  "eyebrow": "오늘의 놀이 기록",
  "body": "",
  "layout": "fullbleed-photo",
  "image": "assets/approved-photo.jpg",
  "image_approved": true,
  "image_kind": "stock",
  "image_source": "Pexels",
  "image_credit": "Pexels · 원본 작가 및 URL 기록",
  "image_zoom": 1.15,
  "image_focus_x": 50,
  "image_focus_y": 54
}
```


## 편집형 HTML 및 시안 선택
기본 4장 캐러셀은 시안 4개를 생성하고 `skills/editor-delivery/SKILL.md`에 따라 독립형 편집기 HTML을 만든다. 예: `python scripts/build_editor.py output/A output/B output/C output/D --out output/editor.html`. 선택한 시안을 저장하고 `python scripts/export_editor_selection.py selected.html --out output/selected-png`으로 PNG 4장을 다시 만든다. 기존 표지와 렌더링 파이프라인은 유지한다. 편집 데이터는 로컬 HTML에 저장되며 클라우드 저장이나 브라우저 직접 PNG 다운로드는 아직 지원하지 않는다.

## TIO 우선 매거진 시안 — 최신 우선 지침
`references/magazine-editions.md`를 먼저 읽는다. TIO(@tio_korea)는 표지 최우선 레퍼런스이며 기존 승인 Signature Cover는 A에 그대로 보존한다. MMM, Eyesmag, 생매거진, Our Expresso는 시안별 보조 레퍼런스다. B/C/D도 풀블리드, 상단 중앙 기관명, 하단 얇은 도입 문구, 정확히 두 줄 굵은 흰색 제목, 우측 하단 출처, 표지 본문 없음이라는 TIO 기반 구조를 유지하면서 타이포/명암/여백을 변주한다. 네 시안에서 사진·활동 사실·카피·브랜드는 동일하게 유지하고 실제 CSS 배치·서체·사진 영역을 다르게 한다. 본문은 승인된 사진 위·글 아래 기사형 구조를 기본으로 한다. 네 시안은 각 4장 한 줄, 총 16장 편집기로 제공한다. 단일 표지 요청에는 A를 기본으로 한다. 원본 권리 확인 및 실제 파이프라인 검수는 기존 규칙을 유지한다.

### 네 가지 실제 디자인 일괄 출력
`python scripts/make_editions.py INPUT.json --out output/four-editions` — 동일한 4장 콘텐츠를 A/B/C/D로 렌더링하고 editor.html을 생성한다. 본문은 기사형 공통 구조를 사용한다.


## 최신 필수 규칙: 로고 없는 기관명 · 기사형 본문
이 지침은 이전 로고 허용 및 본문 후보 지침보다 우선한다.
- 표지 상단 중앙에는 원장님이 입력한 기관명 문자열 그대로 흰색 굵은 HTML 텍스트만 배치한다. 기관 로고, AI 생성 로고, 아이콘, 심볼, 이모지, 워터마크, 이름 옆 장식 도형은 일절 추가하지 않는다. 기관이 로고 파일을 제공하더라도 이 게시물에는 삽입하지 않는다.
- 기존 TIO 표지 디자인을 유지한다. 놀이 기록 본문 2~4장은 `references/magazine-body.md`의 사진 위·글 아래 기사형 구조를 기본값으로 한다. 네 시안에서 활동 사실, 사진, 카피는 동일하게 두고 실제 디자인을 변주한다.
- 이미지 생성 도구는 글자가 없는 사진 소재에만 사용한다. 실제 HTML/CSS 파이프라인을 실행하고 편집 가능한 HTML과 PNG를 확인하기 전 완료로 처리하지 않는다. 네 시안×4장의 기본 편집기와 권한 검수 규칙은 유지한다.
