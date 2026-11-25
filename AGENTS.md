# 작업 지침
기관 전용 한국어 인스타그램 제작 요청에는 `skills/instagram-feed-creator/SKILL.md`를 먼저 읽는다. 하위 스킬과 `references/design-rules.md`, `schemas/feed.schema.json`을 따른다. 실제 기관 정보와 공개 허가 사진만 사용하고 불명확한 사실은 초안으로 표시한다. 사용자 승인 전 자동 게시 금지. 결과물 생성 후 렌더링 결과를 확인하고 검수 결과를 보고한다.

## v0.2
style-direction → visual-curation → editorial-copywriting → post-composition → anti-ai-aesthetic → 렌더 → visual-critique 순서. references/sunlit-editorial.md 기준. 단일 게시물을 9개로 강제하지 않는다.


## 실행 필수 조건 (v0.3)
콘텐츠 제작 후 반드시 `skills/pipeline-execution/SKILL.md`를 읽고 실행한다. 터미널 도구가 있으면 `python scripts/pipeline.py INPUT.json --out output/고유명`을 실제 실행한다. 실행하지 않았거나 실패했다면 HTML/PNG 생성 완료라고 말하지 않는다. 파이프라인 성공 후 quality_check 결과와 파일을 확인한다.

## v0.4 시각 품질 규칙
캐러셀 내 레이아웃과 사진 구도 다양성을 확보한다. 사진/타이포그래피 중심 편집 디자인을 우선하며 의미 없는 장식을 넣지 않는다. 자연스러운 한국어 문구 톤을 유지한다. preview.html은 이미지 내장형이어야 하며 quality_check에서 이미지 수와 데이터 URI를 검사한다. 자동 검수와 미감 평가는 구분한다.


## v0.5 Editorial Hybrid 기본 방향
별도 요청이 없으면 `editorial-hybrid`를 기본 스타일로 사용한다. 사진과 텍스트를 균형 있게 배치하고(50:50은 시각적 가이드), 사진은 활동 맥락을, 텍스트는 학부모가 이해할 활동 내용과 의미를 전달한다. 기본 4장 흐름은 표지 → 활동 디테일 → 활동의 의미 → 마무리다. `references/styles/editorial-hybrid.json` 및 `references/design-rules.md`를 따른다. 카피라이팅의 자연스러운 톤은 유지하고 디자인·사진·정보 전달을 별도로 검수한다.
