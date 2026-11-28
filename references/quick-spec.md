# 빠른 계약 (기본 경로)

이 한 장과 마지막의 실행 명령만으로 4장 캐러셀을 만들 수 있다. 아래 "더 읽기"는 예외 상황에서만 연다.

## 0. 입력
- 기관명: 기관 프로필 값 그대로 표기(임의 변경·추가 금지). 프로필은 `profiles/<id>/brand-profile.json`.
- 활동·반, 사진 4장(표지 + 1~3), 사진별 한 줄 설명. 제목·본문은 선택(없으면 설명에서 만든다).
- 사진 구분: 기관 제공(공개·동의 확인) / 스톡 / AI 생성. 확인되지 않으면 예시로 표시한다.
- 실제 아동 사진은 보호자 동의 + 기관 공개 권한 + 외부 AI 전송 권한을 모두 확인한 경우만 쓴다.

## 1. 표지 (1장)
- 1080×1350, 4:5, 풀블리드. 외곽 여백·카드 프레임·밝은 배경 금지.
- 사진 약 75% / 텍스트 약 25%를 시각 비중 출발점으로 한다.
- 상단 중앙: 기관명 문자열만 흰색 굵은 HTML 텍스트. 로고·아이콘·심볼·이모지·워터마크·장식 도형 금지(기관이 로고 파일을 제공해도 넣지 않는다).
- 하단: 도입 문구(eyebrow) 1줄 8~18자 + 흰색 굵은 제목 정확히 2줄(각 10자 내외, `\n` 하나).
- `body`는 빈 문자열, `details` 없음. 설명은 2장 이후나 캡션에 쓴다.
- 우측 하단: `출처 | 기관 제공` / `출처 | 예시 이미지` / `출처 | AI 생성`.
- 제목이 넘치면 글자를 줄이지 말고 카피를 다시 쓴다.

## 2. 본문 (2~4장)
- 상단 55~65% 큰 사진, 하단 밝은 단색 영역(아이보리/흰색/종이색)에 라벨 → 소제목 2줄 → 본문 2~3문장(≤180자) → 페이지 번호 → 작은 출처.
- 사진과 글은 겹치지 않는다. 기관명·로고를 반복하지 않는다.
- 흐름: 2장 놀이의 시작 / 3장 아이들이 해본 일 / 4장 이어진 놀이.
- 4시안 모두 같은 사진·사실·문구를 쓰고 레이아웃만 다르게 한다.
- 표지 한 장만 요청받으면 A(Signature)를 기본으로 한다.

## 3. 카피
- 확인된 사실만. 발달 효과 단정, 모집 보장, 없는 발언 인용, 과장 금지.
- 한 장에 메시지 하나. 제목은 사진 묘사가 아니라 그 장면의 의미를 말한다.
- 스톡·AI 사진이면 캡션에 "사진은 실제 기관 활동을 촬영한 것이 아닌 예시 이미지입니다."를 넣는다.
- 캡션: 도입 1문장 + 사진 설명 + (예시 고지) + 해시태그.
- 정보 중심(모집·일정·준비물)이면 `editorial-hybrid`/`minimal-information`을 검토한다. `make_editions.py`는 bold 전용이므로 그때는 `pipeline.py`로 단일 시안을 만든다.

## 4. feed.json 최소형
```json
{
  "institution": "햇살숲",
  "goal": "학부모에게 오늘의 활동 전달",
  "style": "bold-photo-editorial",
  "brand": {"primary": "#2E332B", "background": "#F6F1E7", "accent": "#B4843C"},
  "draft": true,
  "posts": [{
    "category": "오늘의 놀이 기록",
    "purpose": "블록 놀이 기록",
    "caption": "캡션 본문",
    "hashtags": ["#햇살숲", "#놀이기록"],
    "slides": [
      {"title": "블록으로 만든\n우리들의 마을", "eyebrow": "오늘의 놀이 기록", "body": "",
       "layout": "fullbleed-photo", "image": "photos/photo-01.jpg", "image_approved": true,
       "image_kind": "institution", "image_source": "기관 제공", "image_credit": "기관 제공 사진",
       "image_zoom": 1.15, "image_focus_x": 50, "image_focus_y": 45},
      {"title": "무엇을 만들지\n먼저 정했어요", "eyebrow": "놀이의 시작", "body": "본문 2~3문장.",
       "layout": "fullbleed-photo", "image": "photos/photo-02.jpg", "image_approved": true,
       "image_kind": "institution", "image_source": "기관 제공", "image_credit": "기관 제공 사진"}
    ]
  }]
}
```
- 슬라이드는 필요한 수만큼 같은 모양으로 반복한다(4장 캐러셀이면 4개).
- `image`는 feed.json 기준 상대 경로. `image_zoom`/`image_focus_*`는 표지에만 적용된다.
- 전체 필드·enum은 `schemas/feed.schema.json`.

## 5. 실행 (Windows 포함)
```bash
export PYTHONIOENCODING=utf-8
python scripts/make_editions.py output/work/feed.json --out output/four-editions   # 4시안 16장 + editor.html
python scripts/pipeline.py output/work/feed.json --out output/single               # 단일 시안
```
- 출력 폴더는 매번 새 경로. 이미 있으면 실패한다.
- 완료 조건: 종료 코드 0, PNG가 슬라이드 수와 일치, 모두 1080×1350, `quality_check` `passed: true`, `editor.html` 존재.
- 실패하면 오류를 읽고 JSON·경로·CSS를 고쳐 재실행한다. 실행 전에는 완료라고 말하지 않는다.
- `quality_check`는 규격·넘침만 본다. 얼굴·손 가림과 미감은 PNG를 열어 사람이 확인한다.
- 자동 게시 금지.

## 더 읽기 (해당할 때만)
| 상황 | 파일 |
|---|---|
| 4시안 레퍼런스·디자인 근거 | `references/magazine-editions.md` |
| 표지 확대·초점·예외 처리 | `references/signature-cover.md` |
| 본문 디자인 수치 | `references/magazine-body.md` |
| 최초 기관 설정(6문항) | `skills/institution-onboarding/SKILL.md`, `prompts/onboarding.md` |
| 카피 톤·문장 길이 규칙 | `skills/editorial-copywriting/SKILL.md` |
| 편집기 전달·선택 PNG | `skills/editor-delivery/SKILL.md` |
| 전체 파이프라인 설명 | `skills/instagram-feed-creator/SKILL.md` |
| 다른 스타일(editorial-hybrid 등) | `references/styles/*.json` |
