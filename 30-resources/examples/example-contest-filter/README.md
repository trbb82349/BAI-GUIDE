# example-contest-filter

## 한 줄 목표

공모전 후보를 로컬 샘플 CSV와 HTML에서 모은 뒤 키워드로 걸러서 Markdown, CSV, Codex 검수 큐, Notion 확장용 초안을 함께 남깁니다.

## 작업 카드

목표: 작은 CSV 처리에서 시작해 나중에 웹 수집, 검수, 외부 업로드로 확장 가능한 파이프라인 뼈대를 만든다.

입력: `input/sample-contests.csv`, `input/sample-site.html`, `input/keywords.csv`

출력: `output/contests_raw.csv`, `output/contests_filtered.csv`, `output/contests_filtered.md`, `output/review_queue.md`, `output/summary_prompt.md`, `output/notion_export.md`

성공 기준: `python src/main.py` 실행 후 사람이 읽는 Markdown과 기계가 읽는 CSV가 함께 생성된다.

오늘 만들 최소 버전: 로컬 샘플 데이터 수집, 키워드 필터, 검수용 Markdown 큐, Notion 업로드 전 단계 파일 생성

## 만들 기능

- [x] 로컬 CSV와 로컬 HTML 샘플에서 후보 수집
- [x] 관심 키워드와 제외 키워드로 1차 필터
- [x] CSV와 Markdown을 동시에 저장
- [x] Codex에게 검수/요약을 요청할 수 있는 `review_queue.md`, `summary_prompt.md` 생성
- [x] 나중에 Notion으로 옮기기 쉬운 `notion_export.md`와 `notion_upload_stub.py` 제공
- [ ] 실제 웹 수집기는 별도 단계에서 추가
- [ ] 외부 서비스 업로드는 사용자 확인 후 별도 구현

## 실행 방법

현재 폴더가 `30-resources/examples/example-contest-filter/`라면:

```powershell
python src/main.py
```

워크스페이스 루트라면:

```powershell
python 30-resources/examples/example-contest-filter/src/main.py
```

Notion 확장 구조만 확인하려면:

```powershell
python 30-resources/examples/example-contest-filter/src/notion_upload_stub.py
```

## 확인 방법

- `output/contests_filtered.md`를 열어 통과한 공모전 목록을 확인합니다.
- `output/contests_filtered.csv`를 열어 CSV 컬럼이 유지되는지 확인합니다.
- `output/review_queue.md`를 Codex에게 붙여 넣고 “누락된 근거와 제외해야 할 후보를 검수해줘”라고 요청할 수 있습니다.
- `output/notion_export.md`는 실제 업로드 전 사람이 확인하는 중간 산출물입니다.

## Codex에게 다음에 요청할 말

```text
30-resources/examples/example-contest-filter/output/review_queue.md를 읽고, 공모전 후보를 유지/보류/제외로 검수해줘. 판단 근거가 부족한 항목은 추가 확인 질문으로 남겨줘.
```

## 메모

- 이 예시는 실제 API 키나 외부 쓰기 작업을 포함하지 않습니다.
- 외부 서비스 업로드는 마지막 단계로 분리해야 합니다.
- 사람/AI 검수용 중간 산출물은 Markdown으로 남기고, 재사용 가능한 결과는 CSV로 남깁니다.
