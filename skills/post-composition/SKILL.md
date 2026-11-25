---
name: post-composition
description: 사진의 구도에 맞추어 레이아웃을 설계한다.
---
# post-composition

1080×1350. hero-left-copy: 전체 배경 사진과 왼쪽 밝은 공간에 큰 명조 제목. hero-right-copy: 반대. split-editorial: 큰 사진과 별도 제목 영역. photo-caption: 사진과 짧은 캡션. quiet-cover: 사진 없는 명조 중심. minimal-announcement: 날짜 및 모집 정보 중심. image_position으로 크롭 조정. 같은 표지 레이아웃 3회 연속 금지. 필요하면 편집 HTML/CSS를 직접 수정하되 .slide 및 ID 유지.

## v0.4 동적 편집 디자인
한 캐러셀 안에서 동일 레이아웃을 반복하지 않는다. fullbleed-photo는 전체 사진과 하단 그라데이션, split-photo는 큰 사진과 분리된 제목, detail-photo는 손·작품 클로즈업, text-interlude는 사진 없는 명조 제목과 여백으로 구성한다. 기존 hero-left-copy, hero-right-copy, quiet-cover도 활용한다. 4장 기본 구성은 주제와 사진 구도에 맞춰 조합하며 순서를 기계적으로 강제하지 않는다. 한 장의 핵심 시각 요소는 하나로 제한한다.
