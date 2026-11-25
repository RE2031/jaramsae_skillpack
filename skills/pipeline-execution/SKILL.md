---
name: pipeline-execution
description: 원장의 요청을 콘텐츠 JSON부터 HTML/CSS, 슬라이드별 PNG까지 실제 실행하고 검증한다.
---
# pipeline-execution

이 스킬은 작업 설명만 하고 끝내면 안 된다. 터미널 실행 기능이 있으면 파이프라인을 끝까지 실행한다.

## 실행 순서
1. 메인 스킬 및 필요한 하위 스킬을 읽고 게시물 콘텐츠를 작성한다.
2. AI 에이전트의 이미지 생성/검색 기능이 있으면 주제에 맞는 이미지 소재를 만든다. 각 이미지 파일을 작업 디렉터리에 저장하고, 이미지 권리/생성 출처를 확인한다. 도구가 없으면 기관 승인 사진을 요청하거나 사진 없는 quiet-cover/minimal-announcement로 진행한다. 이미지 생성이 불가능한 경우 이미지 생성 완료라고 말하지 않는다.
3. `schemas/feed.schema.json`을 준수하는 UTF-8 JSON을 만든다. `image`는 JSON 파일 기준 상대경로, `image_approved`는 true/false, 스톡/생성 이미지에는 `image_kind`와 `image_credit`를 기록한다. 확인되지 않은 모집 정보는 쓰지 않는다.
4. Python 실행이 가능한 경우 저장소 루트에서 아래 단일 명령을 실행한다.
   ```bash
   python scripts/pipeline.py path/to/feed.json --out output/unique-job-name
   ```
   Windows PowerShell에서도 동일하다. 출력 폴더는 매번 새로운 경로를 사용한다.
5. 파이프라인이 실패하면 오류 메시지를 읽고 환경 설치, JSON, 이미지 경로 또는 CSS를 수정한 뒤 재실행한다. 실패 상태를 성공으로 보고하지 않는다.
6. 파이프라인 성공 후 `output/.../preview.html`, `editable/index.html`, `editable/style.css`, `editable/feed.json`, `png/post-XX-slide-YY.png`, `captions.md`, `review-report.json` 존재 여부를 확인한다.
7. PNG를 열어 실제로 시각 검수한다. 자동 품질 검사는 픽셀/레이아웃 검증일 뿐 미감 승인이 아니다. 문제가 있으면 CSS/JSON을 수정하고 `python scripts/render.py --rerender --out output/unique-job-name`으로 재렌더한 후 `python scripts/quality_check.py --out output/unique-job-name`을 다시 실행한다.
8. 터미널/파일시스템 실행 도구가 없는 경우, JSON과 실행 명령을 제공하고 렌더링 파일이 생성됐다고 주장하지 않는다.

## 완료 조건
파이프라인 종료 코드 0, 개별 PNG 수가 JSON 슬라이드 수와 일치, 모든 PNG가 1080×1350, 편집 가능한 HTML/CSS/JSON이 존재해야 한다. 이 조건을 만족하지 않으면 미완료다.

## v0.4 미리보기 검사
파이프라인 성공 후 preview.html을 별도 파일로 열어 이미지가 독립적으로 보이는지 확인한다. quality_check는 preview의 이미지 데이터 URI 개수와 상대경로 잔존 여부를 검사해야 한다. 이 검사가 실패하면 완료 처리하지 않는다.
