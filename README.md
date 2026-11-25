# Instagram Feed Skill Pack
한국어 보육기관 인스타그램 피드 제작용 Agent Skills + 렌더러. 원장의 자연어 요청을 받은 AI 에이전트가 콘텐츠 JSON을 작성하고, 로컬 렌더러가 편집 가능한 HTML/CSS와 PNG를 생성한다. 자체 서비스 홍보 및 자동 게시 기능은 범위 밖이다.

## 빠른 시작
Python 3.10+ 및 한국어 폰트(Noto Sans CJK KR 또는 맑은 고딕)를 설치한다.
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/render.py examples/demo.json --out output/demo
```
Windows에서도 동일하게 실행한다. 시스템 Chromium을 사용하려면 `--browser /path/to/chromium`을 추가한다. `output/demo/preview.html`을 브라우저에서 열면 피드와 슬라이드를 확인할 수 있다.

## AI 에이전트 사용
저장소를 에이전트에서 열고 다음처럼 요청한다.
> skills/instagram-feed-creator/SKILL.md를 읽고 실행해. 우리 어린이집은 신입 원아 모집이 목적이고 따뜻하고 전문적인 피드를 원해. 9개 게시물을 만들어줘.

`AGENTS.md` 및 메인 스킬이 하위 스킬을 순서대로 안내한다. Codex, Claude Code, Antigravity 등에서 파일을 직접 읽는 방식으로 사용하도록 설계했다. 각 제품의 네이티브 자동 탐색/설치 방식은 버전별로 다르므로 이 저장소는 특정 경로를 강제하지 않는다. 실제 에이전트별 실행 호환성은 아직 검증하지 않았다.

## 스타일
- `photo-lifestyle`: 실제 공간 사진 중심
- `emotional-editorial`: 여백과 감성적인 사진 중심
- `modern-magazine`: 강한 헤드라인과 편집형 구성
- `minimal-information`: 정보 전달 및 체크리스트

브랜드의 일반적인 시각 문법을 참고했으며 제3자 로고·사진·고유 템플릿을 포함하지 않는다. 사진은 기관이 공개 홍보 권한을 확인한 로컬 파일만 사용한다. 사진이 없으면 도형 기반 디자인으로 대체한다.

## 결과물
`editable/index.html`, `editable/style.css`, `editable/feed.json`, `editable/assets/`, `png/post-01-slide-01.png` 등, `preview.html`, `captions.md`, `review-report.json`. JSON을 수정한 후 재실행하거나 HTML/CSS를 직접 수정할 수 있다. HTML 직접 수정 후에는 `--rerender`로 PNG를 재생성한다.

## 범위와 제한
AI 콘텐츠 생성은 에이전트가 담당한다. 렌더러 자체는 LLM이나 사진 검색 API를 호출하지 않는다. 데모는 가상 기관이며 게시 금지. 자동 검수는 규격·텍스트 넘침·이미지 로딩·구조 검사 중심이며, 실제 사실과 개인정보 및 디자인 품질은 사람이 승인해야 한다. 자동 게시하지 않는다. 출력 폴더는 새 경로를 사용한다(기존 폴더 덮어쓰기 방지).
