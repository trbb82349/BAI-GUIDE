# example-meeting-notes-html

## 한 줄 목표

회의록/과제 안내처럼 "제목 + 목차 + 여러 섹션 + 강조 박스"로 구성된 문서를 예쁜 HTML 한 장으로 만드는 재사용 템플릿입니다.

같은 목적의 다른 디자인 템플릿: [example-newsletter-html](../example-newsletter-html/README.md)(신문/뉴스레터 톤), [example-meeting-editorial-html](../example-meeting-editorial-html/README.md)(발언자별 색 구분 + 다크모드 지원 회의록).

## 이 템플릿의 구조

`template/meeting-notes-template.html` 파일 하나에 CSS 디자인 시스템과 `{{이렇게 생긴}}` 자리표시자가 같이 들어 있습니다. CSS는 그대로 두고 자리표시자만 실제 내용으로 바꾸면 같은 스타일의 새 문서가 됩니다.

미리 만들어둔 컴포넌트(클래스):

| 클래스 | 용도 |
|---|---|
| `.eyebrow`, `h1.title`, `.meta` | 문서 상단 제목/라벨/날짜 |
| `nav.toc` | 목차 (섹션 id와 `href="#id"`를 맞춰야 함) |
| `.part-head` | 문서를 여러 파트(PART 1, PART 2...)로 나눌 때의 구분 배너 |
| `h3` / `h4` | 섹션 / 소제목 |
| `.q` | 핵심 질문 하나를 크게 강조 |
| `.quote` | 회의 중 나온 말이나 결론 인용 |
| `.note` | 주의사항 (노란 박스) |
| `.tip` | 팁/조언 (초록 박스) |
| `.flow` | 화살표(↓)로 이어지는 절차 |
| `.prompt` | AI에게 그대로 던질 질문 예시 (어두운 코드 박스) |
| `.task` | 번호 붙은 과제/할 일 카드 |
| `.tblwrap table` | 표 |
| `.check` | 문서 맨 끝 체크리스트 |

색상은 `:root`의 `--accent` 하나만 바꿔도 전체 톤이 같이 바뀝니다.

## 사용 방법

1. `template/meeting-notes-template.html`을 복사해서 `10-projects/작업이름/` 아래(또는 결과물이 하나뿐이면 바로 원하는 위치)에 `YYYY-MM-DD-짧은-주제.html`로 저장
2. `{{...}}`로 표시된 자리표시자를 실제 내용으로 교체
3. 섹션(`h3`)을 추가/삭제할 때마다 `nav.toc`의 목차 항목도 같이 맞추기
4. 필요 없는 컴포넌트(`.flow`, `.prompt`, `.task` 등)는 통째로 지워도 됨 — CSS는 안 쓰는 클래스가 있어도 문제없음

## 확인 방법

완성한 HTML 파일을 브라우저로 열어서 목차 링크가 각 섹션으로 잘 이동하는지, 강조 박스들이 의도한 대로 보이는지 확인합니다.

## 출처

`2026-08-05` 회의록 문서에서 디자인만 추출해 일반화했습니다.
