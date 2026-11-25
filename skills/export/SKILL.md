---
name: export
description: 편집 원본과 PNG를 출력한다.
---
# export

python scripts/render.py INPUT.json --out output/새폴더 실행. HTML/CSS 수정 후 python scripts/render.py --rerender --out output/기존폴더 실행. sources.md, preview.html, PNG, editable, captions.md, review-report.json 제공. 실제 사진과 기관 정보 별도 승인. visual-critique 실행.

## 필수 실행 파이프라인
새 작업은 다음을 실행한다.
```bash
python scripts/pipeline.py INPUT.json --out output/고유한-폴더명
```
실패하면 성공으로 보고하지 않는다. HTML/CSS를 수정한 경우 다음 두 명령을 실행한다.
```bash
python scripts/render.py --rerender --out output/고유한-폴더명
python scripts/quality_check.py --out output/고유한-폴더명
```
완료 조건은 JSON에 정의된 슬라이드별 PNG가 각각 생성되고, PNG가 1080×1350이며, 편집 가능한 HTML/CSS/JSON이 존재하는 것이다.
