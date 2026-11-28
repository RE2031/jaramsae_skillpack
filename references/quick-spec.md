# 카드뉴스 빠른 제작 규칙

## 입력과 기본 흐름

- 표시 이름과 이번 게시물 주제, 표지 사진 1장과 본문용 사진 3장, 카드별 제목·원고를 준비한다. 표시 이름과 주제는 스튜디오에서 매 게시물에 직접 입력한다.
- 사진마다 실제 제공 자료인지 예시 이미지인지 표시한다. 사용 권한과 필요 시 인물 공개 동의를 확인한다. 업로드한 자료의 공개와 재사용 권한을 확인한다.
- 사진은 같은 게시물의 네 스타일에서 공유한다. 선택한 스타일의 입력만 화면에 드러나며 다른 스타일에 입력한 자료도 유지된다. 본문은 인물·주제 소개, 핵심 장면, 결론이나 후속 질문으로 전개할 수 있다.

## 공통 표지

기존 A · Signature 그대로 렌더링한다. 1080×1350 풀블리드 사진, 상단 중앙 표시 이름, 하단 한 줄 도입 문구와 두 줄의 굵은 흰색 제목, 우측 하단 출처를 유지한다. 원고에는 줄바꿈 하나로 제목을 두 줄로 쓰고 본문과 details를 비운다. 제목이 넘치면 두 줄을 짧게 다듬는다. 사진, 크롭, 문구와 배치는 네 스타일에서 동일하다. 표지에는 로고나 장식 도형을 넣지 않는다.

## 2장 이후의 본문 스타일

| 스타일 | 제작 규칙 |
| --- | --- |
| A · 아기자기 편집형 | 사진을 풀블리드로 배치하고 상단 9%에 얇은 검은 테두리의 흰 사각 문구 두 개를 엇갈려 얹는다. 왼쪽 첫 문구는 굵은 `title` 뒤에 보통 굵기의 짧은 `aside`를 선택적으로 붙인다. 두 번째 문구는 한 단계 오른쪽에서 `body`로 받아친다. 사진의 피사체와 두 문구가 함께 한 장면을 이룬다. 본문 사진 출처는 출처 목록에 기록한다. |
| B · 사진 오버레이형 | 풀블리드 정지 사진 위에 제목·짧은 본문을 배치한다. 모든 본문 카드의 같은 상단 위치에 사용자 로고(`logo`)를 둔다. 로고가 없으면 표시 이름을 쓴다. |
| C · 영상 매거진형 | 필요한 본문 카드에 한 편의 짧은 영상(`video`, 최대 30초)과 화면 문구·자막(`subtitle`)을 붙인다. 앞뒤 정지 카드가 배경과 결론을 전한다. 사진은 영상 유무와 관계없이 가로 16:9 미디어 창의 정지 미리보기로 쓰인다. 자막은 영상 전체에 보여주는 한 문구이며 MP4 화면에 합성된다. 자막을 비우면 카드 제목을 쓴다. |
| D · 인터뷰 지면형 | 작은 발행호(`issue`), INTERVIEW 마스트헤드, 질문(`question`)과 지면에서 가장 크게 보이는 직접 인용(`quote`)을 조합한다. 인물·맥락 → 기억에 남는 답변 → 후속 질문이나 마무리. 인용은 `interview_source`의 연속된 문장을 그대로 쓴다. 원문이 없으면 간접 요약을 본문에 쓴다. |

레퍼런스에서는 편집 방식만 참고한다. 로고, 사진, 사실과 카피는 사용자 브랜드와 제공 자료를 바탕으로 제작한다. 모든 텍스트는 HTML/CSS 레이어에 넣는다.

## feed.json과 기존 데이터

`schemas/feed.schema.json`을 따른다. 새 피드에서 표시 이름은 `display_name`에 저장한다. 새 카드뉴스의 `style`은 `bold-photo-editorial`이고, 선택한 본문형은 `body_style`의 `playful`, `overlay`, `video`, `interview`로 표시한다. `make_editions.py`는 하나의 입력을 재사용해 요청된 본문형을 지정한다.

- 표지는 `image`, `image_zoom`, `image_focus_x`, `image_focus_y`, `eyebrow`, `title`과 빈 `body`를 쓴다.
- 본문은 `title`, `body`, `layout`, `image`를 쓴다. 스타일별 필드는 위 표를 따른다.
- `image`, `logo`, `video`는 feed.json 기준 상대 경로다. 승인된 사진에 `image_approved: true`, 사진 유형에 `image_kind`, 표기에 `image_source`와 `image_credit`를 쓴다. 새 유형 `provided`는 일반 사용자 제공 자료에 적용한다. 보관된 이전 JSON의 `institution`, 사진 유형과 `editorial_variant`도 단일 파이프라인에서 읽는다.

## 실행과 검수

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python -X utf8 app/server.py --port 8772
```

`http://127.0.0.1:8772/`에서 자료를 한 번 입력한 후 **선택한 스타일 만들기** 또는 **4종 비교하기**를 누른다. 결과의 **편집·저장**에서 문구를 수정하고 **선택안 PNG·MP4 저장**을 누른다. 정지 카드는 PNG, 영상 카드는 자막을 합성한 MP4로 저장한다. 파일명 앞의 장 번호가 원래 순서를 나타낸다.

```powershell
python -X utf8 scripts/make_editions.py output/work/feed.json --out output/four-editions
python -X utf8 scripts/make_editions.py output/work/feed.json --out output/one-edition --style video
python -X utf8 scripts/pipeline.py output/work/feed.json --out output/single
python -X utf8 scripts/export_editor_selection.py selected.html --out output/selected
```

새 출력 경로를 사용하고 실제 실행 결과를 확인한다. 공통 표지의 동일성, 1080×1350 규격, 모바일 가독성, 사진 출처를 살핀다. B는 모든 본문 로고 위치, C는 무음 재생과 자막 포함 MP4, D는 원문과 인용문의 일치를 확인한다. 자동 게시하지 않는다.
