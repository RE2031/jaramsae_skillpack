# 작업 지침 — 토큰 최소 경로

기관 인스타그램 제작 요청의 **기본 경로는 `references/quick-spec.md` 한 장**이다. 그것만 읽고 실행한다.
아래 "더 읽기"에 해당할 때만 그 파일을 추가로 연다. 규칙을 이미 알고 있으면 다시 읽지 않는다.

## 반드시 지킬 것
1. 실제 기관 정보와 사용 승인 사진만 사용한다. 불명확한 사실은 초안으로 표시하거나 한 번만 질문한다.
2. 기관명은 원장이 입력한 표기를 그대로 쓴다. 로고·아이콘·이모지·워터마크·장식 도형을 넣지 않는다.
3. 표지 제목은 정확히 2줄(`\n` 하나), `body`는 빈 문자열. 넘치면 글자를 줄이지 말고 카피를 다시 쓴다.
4. 사진 안에 글자를 생성하지 않는다. 모든 텍스트는 HTML/CSS 레이어로 렌더링한다.
5. `python scripts/make_editions.py`(4시안) 또는 `python scripts/pipeline.py`(단일)를 **실제로 실행**한다. 실행하지 않았거나 실패했으면 완료라고 말하지 않는다.
6. Windows에서 cp1252 인코딩 오류(`UnicodeEncodeError`)가 보이면 `export PYTHONIOENCODING=utf-8`을 붙인다.
7. 스톡·AI 사진을 실제 원아 사진으로 오인시키지 않는다. 실제 아동 사진은 보호자 동의·기관 공개 권한·외부 AI 전송 권한을 확인한다. 캡션과 출처에 표시한다.
8. 자동 게시 금지. 게시 승인은 사람이 한다.
9. 실제 기관 프로필·사진·결과물은 Git에 커밋하지 않는다(`profiles/`, `output/`는 gitignore).
10. 결과물을 만든 뒤 렌더 결과와 검수 상태를 함께 보고한다.
11. 이미 답한 정보는 다시 묻지 않는다. 프로필을 저장할 수 없는 환경이면 미저장이라고 보고한다.
12. 즉시 제작 요청이면 필요한 정보만 확인하고, 선택 항목이 없다는 이유로 작업을 막지 않는다.
13. 실행 순서: style-direction → visual-curation → editorial-copywriting → post-composition → anti-ai-aesthetic → 렌더 → visual-critique. 게시물 수를 9개로 강제하지 않는다.

## 기본 흐름
1. `references/quick-spec.md`를 읽는다.
2. 사진은 `output/work-<작업명>/photos/`에 두고 `feed.json`을 같은 폴더에 만든다.
3. `python scripts/make_editions.py output/work-<작업명>/feed.json --out output/four-editions-<작업명>` 실행.
4. 종료 코드 0, PNG 1080×1350, `quality_check` `passed: true`, `editor.html` 존재를 확인한다.
5. 결과 경로·사진 출처·검수 상태를 보고한다.

## 더 읽기 (해당할 때만)
| 상황 | 파일 |
|---|---|
| 4시안 레퍼런스·디자인 근거 | `references/magazine-editions.md` |
| 표지 확대·초점·예외 | `references/signature-cover.md` |
| 본문 디자인 수치 | `references/magazine-body.md` |
| 최초 기관 설정(6문항) | `skills/institution-onboarding/SKILL.md`, `prompts/onboarding.md` |
| 카피 톤·문장 길이 | `skills/editorial-copywriting/SKILL.md` |
| 편집기 전달·선택 PNG | `skills/editor-delivery/SKILL.md` |
| 실행·검수 규칙 상세 | `skills/pipeline-execution/SKILL.md` |
| 전체 실행 순서·검수 기준 | `skills/instagram-feed-creator/SKILL.md` |
| 스타일 프리셋 | `references/styles/*.json` |

## 토큰 원칙
- 같은 규칙을 여러 파일에 복사하지 않는다. 규칙은 `references/`와 `quick-spec.md`에만 두고, 스킬 파일은 포인터만 둔다.
- 새 규칙은 `references/quick-spec.md`에 먼저 반영한다.
- 문서를 읽을 때는 필요한 절만 읽는다(전체 파일 통독 금지).

## 부속 도구
- `app/server.py` — 로컬 스튜디오(사진 4칸 + 설명 → 4시안 렌더, 시안 PNG 저장). `python app/server.py --port 8765`.
