# example-meeting-editorial-html

## 한 줄 목표

발언자별로 색을 구분해 보여주는 잡지 지면풍 회의록을 HTML 한 장으로 만드는 재사용 템플릿입니다. 다크모드를 자동 지원합니다.

## 다른 회의록 템플릿과의 차이

이 워크스페이스에는 이미 회의록/뉴스레터 템플릿이 두 개 더 있습니다. 셋 다 디자인이 다릅니다.

| | [example-meeting-notes-html](../example-meeting-notes-html/README.md) | [example-newsletter-html](../example-newsletter-html/README.md) | example-meeting-editorial-html (이 문서) |
|---|---|---|---|
| 톤 | 부드러운 카드형 노트 | 신문/뉴스레터(Paper & Ink) | 잡지 지면형 회의록 |
| 모서리 | 둥근 모서리 | 각짐(0) | 살짝 둥근(3px) |
| 색 구분 방식 | 강조색 하나(`--accent`) | 잉크/레드 2색 | 발언자·섹션마다 다른 색(teal/indigo/plum/moss/clay) |
| 특이 기능 | 체크리스트, 목차 | 오프셋 그림자, 티커 | **다크모드 자동 대응**, sticky 발언자 이름 |

## 이 템플릿의 구조

`template/meeting-editorial-template.html` 하나에 CSS와 `{{자리표시자}}`가 같이 들어 있습니다.

미리 만들어둔 컴포넌트(클래스):

| 클래스 | 용도 |
|---|---|
| `.masthead`, `.roster` | 상단 제목/부제 + 참여자 롤콜(태그 목록) |
| `section.s-teal/indigo/plum/moss/clay` | 섹션마다 다른 색 배정 (클래스 생략 시 teal이 기본) |
| `.lede` | 결론/요약 강조 박스 |
| `.speakers`, `.speaker` | 발언자 카드 — 좌측 이름/역할 고정, 우측 괘선 본문. 발언자별로도 `.speaker.s-xxx`로 색 지정 가능 |
| `.flag` | "검증 필요" 같은 짧은 라벨 |
| `.table-wrap table` | 역할분담표 등 |
| `.notice` | 공지/마감 안내 박스 |
| `.open` | 미해결·확인 필요 항목 번호 리스트 |

### 다크모드

`:root`에 라이트 색상을, `@media (prefers-color-scheme: dark)`와 `:root[data-theme="dark"]`에 다크 색상을 각각 정의해뒀습니다. 시스템이 다크모드면 자동으로 전환되고, `<html data-theme="dark">`를 직접 지정해도 강제로 전환됩니다. 새 색을 추가할 때는 반드시 세 곳(`:root`, 다크 미디어쿼리, `data-theme="dark"`)에 다 넣어야 다크모드에서도 깨지지 않습니다.

### 폰트에 대해

원본 문서는 Pretendard 서브셋 폰트를 base64로 파일 안에 통째로 내장하고 있었습니다(오프라인에서도 폰트가 깨지지 않게 하려는 목적으로 추정). 템플릿에서는 파일 용량이 너무 커지는 문제로 CDN 링크 방식으로 바꿨습니다. 인터넷 연결 없이 폰트까지 완전히 고정해야 하는 경우에만 원본처럼 base64 내장을 다시 고려하세요.

## 사용 방법

1. `template/meeting-editorial-template.html`을 복사해서 원하는 위치에 `YYYY-MM-DD-짧은-주제.html`로 저장
2. `{{...}}` 자리표시자를 실제 내용으로 교체
3. 발언자/섹션이 늘어나면 `<article class="speaker">` 블록이나 `<section>` 블록을 통째로 복사해서 늘리고, `s-teal/indigo/plum/moss/clay` 중 하나로 색만 바꿔주기

## 확인 방법

브라우저로 열어서 라이트/다크 모드 전환(OS 설정 변경 또는 `data-theme` 속성 테스트) 양쪽에서 색이 다 잘 보이는지, 발언자 카드가 모바일 폭에서 세로로 잘 접히는지 확인합니다.

## 출처

`2026-08-12-회의록.html` 문서에서 디자인만 추출해 일반화했습니다.
