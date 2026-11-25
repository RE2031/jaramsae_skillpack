# Instagram Feed Skill Pack v0.5
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

## 스타일
- `editorial-hybrid` (기본값): 사진과 학부모 정보 전달을 균형 있게 구성하는 에디토리얼 혼합형
- `photo-lifestyle`: 실제 공간 사진 중심
- `emotional-editorial`: 여백과 감성적인 사진 중심
- `modern-magazine`: 강한 헤드라인과 편집형 구성
- `minimal-information`: 정보 전달 및 체크리스트

기본 `editorial-hybrid`는 사진으로 활동 맥락을 보여주고 큰 제목과 짧은 설명으로 학부모에게 의미를 전달한다. 기본 시각 비중은 사진 50% / 텍스트 50%를 출발점으로 삼되 슬라이드 목적에 맞게 조정한다. 4장 캐러셀은 표지 → 활동 디테일 → 활동의 의미 → 마무리 흐름을 기본 참고안으로 사용한다. 기관 고유 브랜드 가이드가 있으면 이를 우선한다.

브랜드의 일반적인 시각 문법을 참고했으며 제3자 로고·사진·고유 템플릿을 포함하지 않는다. 사진은 기관이 공개 홍보 권한을 확인한 로컬 파일만 사용한다. 사진이 없으면 텍스트 중심 디자인으로 전환한다.

## 결과물
`editable/index.html`, `editable/style.css`, `editable/feed.json`, `editable/assets/`, `png/post-01-slide-01.png` 등, `preview.html`, `captions.md`, `review-report.json`. JSON을 수정한 후 재실행하거나 HTML/CSS를 직접 수정할 수 있다. HTML 직접 수정 후에는 `--rerender`로 PNG를 재생성한다.

## 범위와 제한
AI 콘텐츠 생성은 에이전트가 담당한다. 렌더러 자체는 LLM이나 사진 검색 API를 호출하지 않는다. 데모는 가상 기관이며 게시 금지. 자동 검수는 규격·텍스트 넘침·이미지 로딩·구조 검사 중심이며, 실제 사실과 개인정보 및 디자인 품질은 사람이 승인해야 한다. 자동 게시하지 않는다. 출력 폴더는 새 경로를 사용한다(기존 폴더 덮어쓰기 방지).

## v0.5 Editorial Hybrid 기본 스타일
기본 스타일을 `editorial-hybrid`로 변경했다. 사진은 활동의 분위기와 과정을 보여주고, 큰 한국어 제목과 짧은 설명은 학부모에게 활동 내용과 의미를 전달한다. 50:50은 시각적 출발점이며 고정 비율이 아니다. 기본 4장 흐름은 표지 → 활동 디테일 → 활동의 의미 → 마무리다. 스킬 지침, JSON 스키마, CSS 프리셋, 디자인 검수 기준을 함께 업데이트했다. 자연스러운 카피라이팅 톤은 유지하고 디자인·사진·정보 전달력을 별도로 검수한다.

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
