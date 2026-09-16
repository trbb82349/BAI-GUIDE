# Daily News Summary

## 지금 목표

한국 뉴스 RSS를 읽어서 한글 뉴스 요약 보고서 Markdown 파일을 자동으로 만듭니다.

## 작업 카드

목표: 한국 뉴스 사이트와 뉴스 RSS를 가져와 한글 보고서로 정리하는 자동화 예시 만들기
입력: `input/korean-news-feeds.csv`
출력: `output/korean-news-report.md`
성공 기준: Python 스크립트를 실행하면 최신 뉴스 제목, 출처, 게시 시각, 요약이 들어간 한글 보고서가 생성된다.
오늘 만들 최소 버전: 한겨레 RSS와 Google News RSS를 읽고 최신 뉴스 10개를 Markdown 보고서로 저장한다.

## 만들 기능

- [x] RSS 목록 CSV 만들기
- [x] RSS를 읽는 Python 스크립트 만들기
- [x] 기사 제목, 출처, 링크, 게시 시각 정리하기
- [x] 한글 Markdown 보고서 저장하기
- [ ] 원하는 언론사 RSS 주소로 바꾸기
- [ ] 이메일 발송 기능 붙이기
- [ ] Windows 작업 스케줄러에 매일 실행 등록하기

## 실행 방법

워크스페이스 루트에서 실행합니다.

```powershell
& "C:\Program Files\Python312\python.exe" 10-projects\daily-news-summary\src\main.py
```

보고서에 넣을 기사 수를 바꾸고 싶으면:

```powershell
& "C:\Program Files\Python312\python.exe" 10-projects\daily-news-summary\src\main.py --limit 5
```

## 확인 방법

실행 후 아래 파일을 엽니다.

```text
10-projects/daily-news-summary/output/korean-news-report.md
```

보고서 안에 `한국 뉴스 요약 보고서`, `한눈에 보기`, `주요 뉴스 요약`이 보이면 성공입니다.

## RSS 주소 바꾸기

아래 파일을 수정하면 수집 대상을 바꿀 수 있습니다.

```text
10-projects/daily-news-summary/input/korean-news-feeds.csv
```

형식은 아래처럼 유지합니다.

```csv
name,category,url
Google News Korea,종합,https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko
```

## Codex에게 다음에 요청할 말

```text
이 뉴스 보고서를 이메일로 보내는 기능을 추가해줘. 실제 비밀번호는 넣지 말고 설정 예시만 만들어줘.
```

```text
내가 보는 한국 언론사 RSS 주소로 feeds 파일을 바꿔줘.
```

```text
Windows 작업 스케줄러에 매일 오전 8시에 실행하는 방법을 notes에 정리해줘.
```

## 메모

현재 요약은 외부 AI API를 쓰지 않고 RSS의 제목과 설명을 짧게 정리합니다. 더 자연스러운 요약이 필요하면 나중에 별도 요약 모델이나 API를 연결할 수 있습니다.
