# 인스타그램 카드뉴스 스튜디오

브랜드, 매거진, 인터뷰 등 인스타그램 게시물을 만드는 로컬 스튜디오와 제작 스킬이다. 표시 이름과 주제를 입력하고 공통 표지 1장과 본문 3장을 만든다.

## 실행

Python 3.10 이상과 한국어 글꼴을 준비한다. 저장소에서 다음을 실행한다.

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python -X utf8 app/server.py --port 8772
```

[스튜디오](http://127.0.0.1:8772/)에서 표시 이름, 주제, 사진과 원고를 넣는다. 미리보기에서 본문 카드와 스타일을 선택한 뒤 **선택한 스타일 만들기** 또는 **4종 비교하기**를 누른다. **편집·저장**에서 문구와 사진 크롭을 수정하고 장 순서대로 저장한다.

| 본문 스타일 | 구성 |
| --- | --- |
| A · 아기자기 편집형 | 테두리 사진과 스티커, 사진 속 소재와 호응하는 말풍선 |
| B · 사진 오버레이형 | 풀블리드 정지 사진과 상단 고정 브랜드 로고 또는 표시 이름 |
| C · 영상 매거진형 | 제목과 본문, 16:9 영상 창, 화면 위 자막. 영상이 없으면 같은 창에 사진 사용 |
| D · 인터뷰 지면형 | 작은 발행호와 INTERVIEW 마스트헤드, 인물 소개와 원문에 근거한 큰 직접 인용 |

네 스타일은 1080×1350 Signature 표지를 공유한다. 정지 카드는 PNG, 영상 카드는 화면 문구와 자막이 합성된 MP4로 저장한다.

## 스킬과 CLI

[메인 스킬](skills/instagram-feed-creator/SKILL.md)과 [빠른 제작 규칙](references/quick-spec.md)에 입력과 제작 기준이 있다.

```powershell
python -X utf8 scripts/make_editions.py output/work/feed.json --out output/four
python -X utf8 scripts/make_editions.py output/work/feed.json --out output/one --style video
python -X utf8 scripts/export_editor_selection.py selected.html --out output/selected
```

이전 피드 JSON은 `scripts/pipeline.py`로 열 수 있다. 렌더 결과는 `output/`에 저장된다.
