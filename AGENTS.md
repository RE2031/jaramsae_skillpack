# 작업 지침
기관 전용 한국어 인스타그램 제작 요청에는 `skills/instagram-feed-creator/SKILL.md`를 먼저 읽는다. 하위 스킬과 `references/design-rules.md`, `schemas/feed.schema.json`을 따른다. 실제 기관 정보와 공개 허가 사진만 사용하고 불명확한 사실은 초안으로 표시한다. 사용자 승인 전 자동 게시 금지. 결과물 생성 후 렌더링 결과를 확인하고 검수 결과를 보고한다.

## 기본 스타일 v0.6
별도 요청이 없으면 `bold-photo-editorial`을 기본값으로 사용한다. 풀블리드 사진, 상단 중앙의 작은 기관명, 하단의 어두운 그라데이션, 작은 도입 문구, 크고 굵은 흰색 제목, 짧은 보조 문구, 작은 출처 표기를 사용한다. 사진은 약 75%, 텍스트는 약 25%의 시각적 비중을 출발점으로 한다. 모든 슬라이드에 승인된 사진이 필요하며 사진 안에 생성된 글자나 로고를 사용하지 않고 HTML/CSS 텍스트 레이어를 사용한다. 상세 기준은 `references/styles/bold-photo-editorial.json`을 따른다. 정보 중심 요청에는 `editorial-hybrid` 또는 `minimal-information`을 사용할 수 있다.

## 실행 순서
style-direction → visual-curation → editorial-copywriting → post-composition → anti-ai-aesthetic → 렌더 → visual-critique 순서. 단일 게시물을 9개로 강제하지 않는다.

## 실행 필수 조건
콘텐츠 제작 후 반드시 `skills/pipeline-execution/SKILL.md`를 읽고 실행한다. 터미널 도구가 있으면 `python scripts/pipeline.py INPUT.json --out output/고유명`을 실제 실행한다. 실행하지 않았거나 실패했다면 HTML/PNG 생성 완료라고 말하지 않는다. 파이프라인 성공 후 quality_check 결과와 파일을 확인한다.

## 이미지와 권한
기본 `bold-photo-editorial`은 모든 슬라이드에 승인된 사진을 요구한다. 실제 아동 사진은 보호자 동의와 기관의 공개 권한 및 외부 AI 전송 권한을 확인한다. AI/스톡 이미지는 실제 원아/기관 사진인 것처럼 표현하지 않는다. 이미지 생성은 글자/로고 없이 수행하고, 텍스트는 HTML/CSS로 렌더링한다.
