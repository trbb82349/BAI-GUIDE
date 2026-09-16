# /save — 작업 저장 전 점검

오늘 작업을 저장하기 전 변경 범위와 보안을 확인합니다.

## 실행 순서

### 1단계: Git 저장소 여부 확인

먼저 Codex가 직접 확인합니다.

```bash
git rev-parse --is-inside-work-tree
```

실패하면 이 폴더는 아직 Git 저장소가 아닙니다. 이때 Git 명령을 계속 실행하지 말고 아래 선택지를 제안합니다.

```text
아직 Git 저장소로 연결되어 있지 않아요.

선택할 수 있는 방법:
1. 오늘 기록만 `20-areas/daily/`에 남기기
2. 이 폴더에서 Git을 시작하기
3. GitHub 저장소를 만든 뒤 연결하기

어떤 방식으로 저장할까요?
```

사용자가 1번을 고르면 `.codex/commands/daily.md`를 읽고 기록만 남깁니다.

사용자가 2번을 고르면 실행 전 확인을 받은 뒤 아래를 진행합니다.

```bash
git init
git config core.hooksPath .githooks
```

사용자가 3번을 고르면 GitHub 빈 저장소 주소를 받은 뒤, 실행 전 확인을 받고 `git init`, `git remote add origin`, `git config core.hooksPath .githooks` 순서로 연결합니다.

### 2단계: 변경 파일 확인

Git 저장소이면 아래를 확인합니다.

```bash
git status --short
git diff --stat
```

변경 파일이 없으면 저장할 변경사항이 없다고 말하고 끝냅니다.

### 3단계: 보안 확인

`.codex/rules/security.md` 기준으로 확인합니다.

- `.env`류 파일이 포함되어 있지 않은가
- API key, token, password, secret이 없는가
- 개인 PC 절대경로나 민감한 파일명이 들어가지 않았는가

문제가 있으면 커밋하지 말고 어떤 파일이 위험한지만 말합니다. 실제 비밀값은 출력하지 않습니다.

### 4단계: 커밋 메시지 제안

변경 내용을 요약해서 커밋 메시지를 제안합니다.

```text
이 메시지로 저장할까요?

docs: 오늘 작업 기록 정리

변경 파일:
- 20-areas/daily/YYYY-MM-DD.md
```

사용자 확인 전에는 `git add`, `git commit`, `git push`를 실행하지 않습니다.

### 5단계: 저장 실행

사용자가 승인하면 아래 순서로 진행합니다.

```bash
git add .
git diff --cached --stat
git diff --cached -U0
git commit -m "커밋 메시지"
```

커밋 직전 staged diff에서도 보안 패턴을 다시 확인합니다.

원격 저장소가 있고 사용자가 push까지 승인하면 `git push`를 실행합니다. 첫 push가 필요하면 `git push -u origin main`을 제안하고 확인을 받습니다.

## 주의

- 사용자 확인 없이 커밋하지 않습니다.
- 사용자 확인 없이 push하지 않습니다.
- `.env`, token, password, API key가 보이면 즉시 중단합니다.
- Git이 없어도 기록은 남길 수 있게 안내합니다.
