# example-kindergarten-dashboard

## 한 줄 목표

작은 유치원 샘플 CSV를 전처리하고 파생지표를 만든 뒤, HTML 대시보드로 확인합니다.

## 작업 카드

목표: 데이터 → 분석 → 화면으로 이어지는 개인 학습용 대시보드 흐름을 만든다.

입력: `input/sample-kindergartens.csv`

출력: `output/processed-kindergartens.csv`, `output/analysis-summary.md`, `output/dashboard.html`

성공 기준: Python 표준 라이브러리만으로 샘플 데이터를 읽고, 지표가 계산된 CSV와 바로 열 수 있는 HTML이 생성된다.

오늘 만들 최소 버전: 정원 대비 현원, 교사 1인당 원아 수, 돌봄 시간, 비용, 통학차량 여부를 한 화면에서 비교한다.

## 만들 기능

- [x] 샘플 CSV 읽기
- [x] 숫자 컬럼 정리와 파생지표 계산
- [x] 추천 점수와 주의 메모 생성
- [x] 처리된 CSV 저장
- [x] HTML 대시보드 생성
- [ ] 실제 데이터 컬럼 매핑 추가
- [ ] 차트나 지도는 필요할 때 별도 단계로 추가

## 실행 방법

현재 폴더가 `30-resources/examples/example-kindergarten-dashboard/`라면:

```powershell
python src/build_dashboard.py
```

워크스페이스 루트라면:

```powershell
python 30-resources/examples/example-kindergarten-dashboard/src/build_dashboard.py
```

## 확인 방법

- `output/dashboard.html`을 브라우저로 열어 카드와 비교 표가 보이는지 확인합니다.
- `output/processed-kindergartens.csv`에서 `occupancy_rate`, `students_per_teacher`, `study_score` 컬럼이 생겼는지 확인합니다.
- `output/analysis-summary.md`에서 상위 후보와 주의 메모를 읽습니다.

## Codex에게 다음에 요청할 말

```text
30-resources/examples/example-kindergarten-dashboard/output/processed-kindergartens.csv와 dashboard.html을 보고, 부모가 이해하기 쉬운 지표 설명과 개선할 화면 구성을 제안해줘.
```

## 메모

- 개인정보, 실제 주소, 외부 지도 호출은 포함하지 않습니다.
- 원본 프로젝트의 핵심만 학생 배포용으로 줄였습니다.
- 표준 라이브러리만 사용하므로 처음 Python 연습용으로도 적당합니다.
