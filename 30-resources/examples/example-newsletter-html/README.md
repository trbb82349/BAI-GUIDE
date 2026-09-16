# example-newsletter-html

## 한 줄 목표

신문/뉴스레터 톤("Paper & Ink")의 칼럼형 문서를 HTML 한 장으로 만드는 재사용 템플릿입니다.

## 이 템플릿의 구조

`template/newsletter-template.html` 하나에 CSS 디자인 시스템과 `{{이렇게 생긴}}` 자리표시자가 같이 들어 있습니다. 이전에 저장한 [example-meeting-notes-html](../example-meeting-notes-html/README.md)과는 완전히 다른 디자인 언어입니다 — 둥근 카드가 아니라 **각진 테두리 + 딱딱한 오프셋 그림자(box-shadow) + 레드 포인트 컬러**가 특징입니다.

색상은 `:root`의 `--red` 하나만 바꿔도 전체 포인트 컬러가 같이 바뀝니다. `--paper`(종이 배경)와 `--ink`(잉크색)를 바꾸면 톤 자체가 달라집니다.

미리 만들어둔 컴포넌트(클래스):

| 클래스 | 용도 |
|---|---|
| `.issue-head-meta` | 상단 번호(#01/64) + 시리즈명 |
| `.issue h1`, `.issue-tag` | 제목, 제목 아래 분류 태그 |
| `.issue-body h2/h3/h4` | 섹션 제목 (h2는 위쪽 굵은 선으로 구분) |
| `.issue-body blockquote` | 인용/핵심 문장 강조 |
| `.issue-body ol` | 번호 리스트 — 레드 카운터, 링크를 넣으면 화살표(→) 정렬 |
| `.issue-body ul` | 불릿 리스트 |
| `.issue-body table` | 표 |
| `.issue-outro` | 마무리 강조 박스 (오프셋 그림자) |
| `.issue-nav` | 이전/다음 글 내비게이션 |

CSS에는 이 외에도 **표지 페이지용 컴포넌트**가 함께 정의되어 있습니다(현재 템플릿 본문에서는 사용하지 않음, 필요할 때 가져다 쓰는 용도):

| 클래스 | 용도 |
|---|---|
| `.topbar` | 발행 정보 한 줄 (매체명 / 날짜) |
| `.hero`, `.stamp` | 표지 대형 타이틀 + 기울어진 도장 오브젝트 |
| `.ticker` | 레드 배경 흐르는 전광판 (내용을 두 번 반복해 넣어야 이어짐) |
| `.lead`, `.spec` | 소개문 + 영양성분표 스타일 스펙 카드 2단 그리드 |
| `.cta` | 구독/문의용 입력폼 박스 |
| `.toc` | 시리즈 회차 목록 (행 전체가 링크, 호버 시 흑백 반전) |
| `.footer` | 흑백 반전 푸터 |

## 사용 방법

1. `template/newsletter-template.html`을 복사해서 원하는 위치에 `YYYY-MM-DD-짧은-주제.html`로 저장
2. `{{...}}` 자리표시자를 실제 내용으로 교체
3. 표지가 필요하면 CSS에 이미 정의된 `.topbar`/`.hero`/`.ticker`/`.lead`/`.toc`/`.footer`를 body 앞뒤에 추가해서 조립
4. 필요 없는 컴포넌트(`ol`, `table`, `blockquote` 등)는 통째로 지워도 됨

## 확인 방법

완성한 HTML 파일을 브라우저로 열어서 오프셋 그림자·번호 리스트·인용 박스가 의도한 대로 보이는지, 좁은 화면(모바일 폭)에서도 레이아웃이 깨지지 않는지 확인합니다.

## 출처

`개발 초보자를 위한 글.html` 문서에서 디자인만 추출해 일반화했습니다. 원본 코드 주석에 따르면 `pentaport-2026-newsletter.naram.kim`(Naram Kim)의 디자인 언어를 참고해 재구성한 것이라고 합니다.
