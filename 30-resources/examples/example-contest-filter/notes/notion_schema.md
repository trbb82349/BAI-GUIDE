# Notion 확장용 필드 초안

실제 외부 서비스 쓰기는 이 예시에 포함하지 않습니다. 나중에 개인 프로젝트로 확장할 때 아래처럼 필드를 맞추면 됩니다.

| 필드 | 타입 | 예시 값 |
|---|---|---|
| name | title | 공공데이터 활용 분석 공모전 |
| status | select | 검수 대기 |
| deadline | date | 2026-07-19 |
| source | text | csv |
| score | number | 6 |
| url | url | https://example.org/contest/public-data |
| summary | text | 공공데이터를 활용한 분석 보고서 모집 |

확장 순서:

1. 로컬 CSV와 Markdown 결과가 안정적인지 확인합니다.
2. 사람이 검수한 상태값을 CSV에 반영합니다.
3. 외부 업로드 코드는 별도 파일로 분리합니다.
4. 쓰기 작업은 기본 실행에 넣지 말고 명시 옵션으로만 실행합니다.
