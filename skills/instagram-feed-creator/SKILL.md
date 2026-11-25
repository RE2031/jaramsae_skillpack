---
name: instagram-feed-creator
description: 기관 전용 한국어 인스타그램을 사진 중심 전문 편집 디자인으로 제작한다.
---
# instagram-feed-creator

1. brand-identity와 style-direction으로 기관 목적, 독자, 브랜드 및 확인된 사실을 정리한다.
2. reference-analysis와 references/sunlit-editorial.md를 읽는다. 기본 스타일은 sunlit-editorial, 기관 요청 우선.
3. visual-curation으로 사진을 확보한다. 이미지 생성 도구가 있으면 글자 없는 배경 사진을 생성한다. 생성 사진은 실제 기관으로 오인시키지 않는다. 없으면 텍스트 중심으로 전환한다.
4. feed-planning, editorial-copywriting, post-composition을 적용한다. 단일 요청에는 1개, 전체 피드에는 기본 9개. 대표 표지 한 장의 완성도를 먼저 확보한다.
5. anti-ai-aesthetic를 적용하여 JSON 작성. schemas/feed.schema.json을 따른다. 사진은 JSON 기준 상대 경로, image_approved는 사용 권한을 확인한 경우만 true.
6. pipeline-execution을 반드시 읽고 실행한다. AI 콘텐츠 JSON과 이미지 파일을 준비한 뒤 `python scripts/pipeline.py INPUT.json --out output/고유한-작업명`을 실제 터미널에서 실행한다.
7. 파이프라인 성공 및 quality_check 통과를 확인한다. visual-critique와 feed-review로 실제 PNG를 열어 검토하고 발견된 문제를 수정한다.
8. PNG 개수와 1080×1350 크기, HTML/CSS 존재를 확인한 후 결과물 경로와 사진 출처, 검수 상태를 전달한다. 자동 게시 금지.

## v0.4 품질 지침
캐러셀 안에서 레이아웃과 사진 거리/각도를 다양화한다. 사용자가 좋다고 평가한 자연스러운 한국어 카피 톤은 유지한다. preview.html은 이미지가 base64로 내장된 독립 파일이어야 한다. 이미지 표시 누락 시 완료 처리하지 않는다.
