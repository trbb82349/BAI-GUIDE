# Youtube Transcript Study Note

## 지금 목표

유튜브 자막 텍스트를 붙여 넣으면 공부 노트 Markdown으로 정리하는 작은 로컬 도구를 만든다.

## 작업 카드

목표: 유튜브 자막을 읽기 쉬운 공부 노트로 바꾸기
입력: `input/transcript.txt`에 저장한 유튜브 자막 텍스트
출력: `output/study-note.md` Markdown 공부 노트
성공 기준: 샘플 자막을 실행하면 제목, 핵심 요약, 키워드, 복습 질문이 있는 노트가 생성된다.
오늘 만들 최소 버전: 외부 API 없이 로컬 Python 스크립트로 샘플 자막 1개를 공부 노트로 변환한다.

## 만들 기능

- [x] 작업 폴더 구조 만들기
- [x] 샘플 자막 파일 만들기
- [x] 자막 텍스트를 Markdown 노트로 변환하는 Python 스크립트 만들기
- [x] 샘플 결과 파일 만들기
- [x] 실제 유튜브 자막을 넣고 결과 품질 다듬기
- [ ] 단원별 제목을 더 자연스럽게 나누기

## 실행 방법

워크스페이스 루트에서 실행합니다.

```powershell
python 10-projects\youtube-transcript-study-note\src\make_study_note.py
```

Python 명령이 잡히지 않으면 이 PC에서 확인된 Python 경로를 직접 써도 됩니다.

```powershell
& "C:\Program Files\Python312\python.exe" 10-projects\youtube-transcript-study-note\src\make_study_note.py
```

내 자막을 쓰려면 유튜브 자막을 복사해서 아래 파일에 붙여 넣습니다.

```text
10-projects/youtube-transcript-study-note/input/transcript.txt
```

그다음 실행하면 결과가 아래 파일에 저장됩니다.

```text
10-projects/youtube-transcript-study-note/output/study-note.md
```

## 확인 방법

1. `output/study-note.md`를 연다.
2. `한 줄 요약`, `핵심 포인트`, `키워드`, `복습 질문`이 있는지 확인한다.
3. `input/transcript.txt` 내용을 바꾼 뒤 다시 실행해서 결과가 갱신되는지 확인한다.

## Codex에게 다음에 요청할 말

```text
이 프로젝트에 실제 유튜브 자막을 넣었어. 공부 노트 품질을 더 좋게 다듬어줘.
```

## 메모

- 첫 버전은 외부 API를 쓰지 않습니다.
- 이번에는 `yt-dlp`로 영상 파일 없이 자동자막만 받아 `input/transcript.txt`에 넣었습니다.
- 사용한 영상: https://www.youtube.com/watch?v=DGolK4QzmZY
- 자막에 포함된 `00:00`, `[00:00]`, `00:00:03` 같은 시간표시는 자동으로 제거합니다.
- VTT 형식의 YouTube 자동자막도 기본 정리합니다.
