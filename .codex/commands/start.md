# /start — 워크스페이스 시작

처음 열었을 때 현재 작업 환경을 확인하고 바로 시작할 작은 작업을 제안합니다.

## 실행 순서

### 1단계: 현재 맥락 확인

먼저 아래 파일을 읽습니다.

1. `AGENTS.md`
2. `README.md`
3. `recipes.md`
4. `20-areas/context/workspace-profile.md`

### 2단계: 환경 확인

가능한 범위에서 Codex가 직접 확인합니다.

- Git 저장소 여부 (`git rev-parse --is-inside-work-tree`)
  - Git 저장소가 아니거나 `.githooks`가 등록되지 않은 경우, 사용자에게 먼저 시키지 말고 Codex가 초기 설정 스크립트를 실행합니다.
    - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1`
    - Mac/Linux: `bash scripts/setup.sh`
  - 실행 후 `git rev-parse --is-inside-work-tree`와 `git config core.hooksPath`를 다시 확인합니다.
  - 실패하면 실패 이유를 짧게 말하고, Git 설치 여부나 권한 문제처럼 사용자가 확인해야 할 다음 행동만 안내합니다.
- Python 실행 가능 여부 (`.codex/rules/python.md` 기준)
- `00-inbox/`, `10-projects/`, `20-areas/`, `30-resources/`, `40-archive/`, `scripts/` 폴더 존재 여부

사용자에게 터미널 명령을 먼저 시키지 않습니다.

Python 확인 시 `python --version` 하나만 실패했다고 Python이 없다고 말하지 않습니다. 필요하면 `scripts/find-python.ps1`을 실행해 Anaconda, Python Launcher, 일반 Python 설치 경로를 함께 확인합니다.

### 3단계: 짧은 질문

질문은 한 번에 하나씩 묻습니다.

사용자가 "모르겠어", "아직 없어", "추천해줘"처럼 답하면 질문을 오래 끌지 말고 4단계의 기본 추천으로 넘어갑니다.

```text
Q1/4 — 지금 제일 먼저 만들고 싶은 것이 있나요?
```

```text
Q2/4 — 반복해서 귀찮은 작업이 있나요?
```

```text
Q3/4 — 결과를 어떤 형태로 보고 싶나요?
예: markdown, Python 스크립트, HTML 페이지, CSV/Excel 정리
```

```text
Q4/4 — 지금 쓸 수 있는 시간은 어느 정도인가요?
예: 15분, 30분, 1시간, 더 많이
```

### 4단계: 작업 맥락 저장

계속 유용한 선호나 반복 설명은 `20-areas/context/workspace-profile.md`에 반영합니다.

민감한 계정, 이메일, 토큰, 비밀번호는 기록하지 않습니다.

### 5단계: 첫 작업 제안

`recipes.md`와 답변을 참고해 바로 확인 가능한 작업 1개를 제안합니다.

답변이 막연하면 아래 3개 중 하나를 추천합니다. 사전 구현 스크립트는 `scripts/` 안에 있습니다.

1. `download-organize`: 다운로드 폴더 파일을 종류(PDF·이미지·ZIP 등)별로 자동 분류
2. `notes-to-summary`: 여러 메모 파일을 하나의 정리 문서로 합치기
3. `file-rename-dated`: 폴더 안 파일 이름 앞에 오늘 날짜 일괄 붙이기

제안 형식:

```text
바로 시작하기 좋은 작업은 이거예요.

작업:
이유:
첫 결과물:
예상 시간:

바로 `/build`로 작업 카드와 첫 결과물까지 만들까요?
```

동의하면 `.codex/commands/build.md`를 읽고 이어서 실행합니다.
