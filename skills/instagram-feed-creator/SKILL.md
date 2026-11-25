---
name: instagram-feed-creator
description: 기관의 자연어 요청을 받아 한국어 인스타그램 피드와 카드뉴스를 제작한다.
---
# instagram-feed-creator

1. `brand-identity`, `reference-analysis`를 읽고 기관명·목표·대상·톤·자료를 정리한다. 필수 정보가 없으면 기관명/목표/공개 허가 사진 여부를 한 번에 확인하거나 가상 초안으로 명시한다.
2. `feed-planning`으로 9개 게시물을 계획한다. `cardnews-copywriting`과 `cardnews-design`으로 각 게시물의 슬라이드를 작성한다.
3. `schemas/feed.schema.json`과 `examples/demo.json` 형식에 맞는 JSON을 작업 폴더에 저장한다. 사진 파일은 JSON 위치 기준 상대 경로로 지정한다. `feed-review`로 사전 검수한다.
4. `export`를 실행한다. 실제 PNG와 피드 미리보기를 열어 검수하고 실패 시 수정 후 새 폴더로 다시 출력한다.
5. 사용자에게 결과물 경로, 미확인 사실, 검수 결과, 게시 승인 필요 여부를 전달한다. 자동 게시하지 않는다.
