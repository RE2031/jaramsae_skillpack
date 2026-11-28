# 작업 지침

기본 제작 경로는 `references/quick-spec.md`다. 일반 게시물은 화면에서 입력한 표시 이름을 사용하고, 저장된 기관 프로필은 기존 설정으로 계속 사용할 수 있다.

- 사실과 인용은 제공 자료에 근거한다. 사진 사용 권한을 확인하고 스톡·AI 사진은 예시로 명시한다. 실제 아동 사진의 보호자 동의, 기관 공개 권한, 외부 AI 전송 권한을 확인한다.
- 새 본문 스타일은 2장 이후에만 적용한다. 표지는 기존 A · Signature 렌더러를 쓰고 표시 이름은 텍스트로 올린다. 본문 로고는 B의 같은 상단 위치에 적용한다.
- `python -X utf8 app/server.py --port 8765`로 스튜디오를 실행한다. CLI 제작은 `scripts/make_editions.py` 또는 `scripts/pipeline.py`를 실행한다.
- 결과의 카드 순서, 규격, 모바일 가독성, 사진 출처와 편집 반영을 확인한다. C는 재생과 자막 포함 MP4를, D는 원문과 인용문의 일치를 확인한다. 실행하거나 확인하지 않은 작업은 실제 상태를 보고한다.
- 실제 프로필·사진·결과물은 Git에 넣지 않는다. 게시 권한과 실제 게시 여부는 사용자가 결정한다.

## 더 읽기

| 상황 | 파일 |
| --- | --- |
| 표지 확대, 초점과 예외 | `references/signature-cover.md` |
| 기존 기관 설정 | `skills/institution-onboarding/SKILL.md`, `prompts/onboarding.md` |
| 카피 톤과 문장 길이 | `skills/editorial-copywriting/SKILL.md` |
| 전체 제작 스킬 | `skills/instagram-feed-creator/SKILL.md` |
| 기존 레이아웃과 프리셋 | `references/magazine-body.md`, `references/styles/*.json` |
