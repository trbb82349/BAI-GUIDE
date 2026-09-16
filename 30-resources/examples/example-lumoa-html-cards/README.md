# example-lumoa-html-cards

## 한 줄 목표

데이터 결과를 보기 좋은 카드 UI로 바꾸는 HTML 구현 예시입니다.

## 작업 카드

목표: 후보 데이터의 상태, 근거, 확인 필요 항목을 사용자가 읽기 좋은 카드형 HTML로 만든다.

입력: `input/sample-culture-cards.csv`

출력: `output/lumoa-cards.html`, `output/culture-card-summary.csv`

성공 기준: 작은 CSV를 읽어 카드형 결과 HTML을 생성하고, 근거와 확인 필요 항목이 화면에 구분되어 보인다.

오늘 만들 최소 버전: 카드 4개, 상태 배지, 근거 목록, 확인 필요 목록, 다음 행동 버튼을 정적 HTML로 생성

## 만들 기능

- [x] 샘플 문화공간 데이터 읽기
- [x] 상태별 카드 배지 만들기
- [x] 확인된 근거와 확인 필요 항목 분리 표시
- [x] 바로 열 수 있는 HTML 생성
- [x] 카드 요약 CSV 저장
- [ ] 실제 앱 컴포넌트로 옮기기
- [ ] 필터와 정렬은 필요할 때 추가

## 실행 방법

현재 폴더가 `30-resources/examples/example-lumoa-html-cards/`라면:

```powershell
python src/build_cards.py
```

워크스페이스 루트라면:

```powershell
python 30-resources/examples/example-lumoa-html-cards/src/build_cards.py
```

## 확인 방법

- `output/lumoa-cards.html`을 브라우저로 열어 카드 UI를 확인합니다.
- 각 카드에 상태, 근거, 확인 필요 항목이 분리되어 있는지 봅니다.
- `output/culture-card-summary.csv`를 열어 HTML에 들어간 핵심 데이터가 다시 기계적으로 읽히는지 확인합니다.

## Codex에게 다음에 요청할 말

```text
30-resources/examples/example-lumoa-html-cards/output/lumoa-cards.html을 보고, 데이터 결과를 더 신뢰감 있게 보여주는 카드 UI 개선안을 제안해줘. 단, 외부 호출 없이 정적 HTML 기준으로 말해줘.
```

## 메모

- Lumoa 전체 앱이 아니라 HTML 구현 감각만 떼어낸 예시입니다.
- 실제 외부 호출, 개인정보, 서비스 인증 정보는 포함하지 않습니다.
- 데이터 처리 결과를 사용자 친화적인 카드로 바꾸는 연습에 초점을 둡니다.
