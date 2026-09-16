# Vibe Coding Workspace

Codex와 함께 아이디어를 빠르게 만들고, 실행하고, 다듬고, 저장하는 개인 작업 공간입니다.

이 폴더는 설명서가 아니라 실제 작업장입니다. 필요한 것은 작게 만들고, 바로 확인하고, 남길 것은 기록합니다.

---

## 처음 시작

GitHub에서 받은 워크스페이스를 VSCode에서 열고 Codex에게 이렇게 말하세요.

```text
/start
```

`/start`가 Codex의 공식 자동완성 목록에 보이지 않아도 괜찮습니다. 이 워크스페이스에서는 `/start` 같은 표현을 `AGENTS.md`가 `.codex/commands/start.md` 플레이북 실행 요청으로 해석합니다.

처음 실행할 때 Codex가 Git 저장소와 커밋 전 보안 훅을 확인하고, 필요하면 초기 설정 스크립트를 직접 실행합니다.

---

## 초기 설정 수동 실행

대부분은 `/start`가 알아서 처리합니다. Codex가 터미널을 실행하지 못하거나 설정에 실패했을 때만 아래 명령을 직접 실행합니다.

**Windows (PowerShell):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

**Mac / Linux (Terminal):**

```bash
bash scripts/setup.sh
```

이 스크립트가 Git 저장소 초기화와 커밋 보안 훅을 자동으로 등록합니다.

---

## Codex에게 처음 말하기

조금 더 길게 말하고 싶으면 이렇게 해도 됩니다.

```text
이 워크스페이스 시작해줘. README.md와 AGENTS.md를 읽고, 지금 바로 할 수 있는 작업을 추천해줘.
```

---

## 기본 흐름

```text
아이디어 메모
-> /build로 작업 카드 만들기
-> 10-projects/에 작업 폴더와 첫 결과물 만들기
-> 실행하고 확인하기
-> 기록하기
-> 저장하기
```

작업이 막히면 이렇게 물어보면 됩니다.

```text
현재 워크스페이스 상태를 보고, 다음에 할 일 하나를 정리해줘.
```

---

## 자주 쓰는 요청

| 요청 | 용도 | 저장 위치 |
|---|---|---|
| `/start` | 작업 환경 확인과 첫 작업 제안 | `20-areas/context/` |
| `/idea` | 아이디어 빠른 메모 | `00-inbox/ideas/` |
| `/build` | 아이디어를 작업 카드, 작업 폴더, 첫 결과물로 변환 | `10-projects/` |
| `/plan` | 구현 없이 작업 카드만 정리 | `00-inbox/plans/` |
| `/review` | 공유/저장 전 완성도와 보안 점검 | 점검 결과 |
| `/daily` | 오늘 한 일과 다음 액션 기록 | `20-areas/daily/` |
| `/save` | 보안 확인 후 Git 저장 | Git |
| `/goodbai` | Codex가 정리한 진행 보고를 BAI 피드에 전송 | BAI 피드 |

헷갈릴 때는 명령어를 외우지 말고 이렇게 말해도 됩니다.

```text
지금 이 아이디어를 작게 만들 수 있게 작업 카드와 첫 결과물까지 만들어줘.
```

---

## BAI 피드에 올리기

`/goodbai`는 학생이 웹사이트 글쓰기 화면에 직접 들어가지 않아도, Codex가 오늘 진행 보고를 정리해 BAI 피드에 올리는 명령입니다.

처음 한 번만 선생님에게 받은 BAI API key를 저장합니다. PowerShell에서는 먼저 이 워크스페이스 폴더로 이동한 다음 설정 명령을 실행합니다.

```powershell
cd "워크스페이스를 내려받은 폴더 경로"
python scripts\bai_feed_config.py
```

설정할 때 물어보는 값:

```text
BAI feed name: 본인 이름
BAI feed API key: 선생님에게 받은 API key
```

`BAI feed name`은 입력하면 PowerShell 화면에 보입니다. `BAI feed API key`는 비밀번호처럼 숨겨져서 붙여넣어도 화면에 아무 글자도 보이지 않습니다. 그대로 Enter를 누르면 정상 입력됩니다.

이미 잘못된 API key가 저장되어 전송에 실패했다면 기존 설정을 덮어씁니다.

```powershell
cd "워크스페이스를 내려받은 폴더 경로"
python scripts\bai_feed_config.py --force
```

그다음부터는 Codex에게 이렇게 말하면 됩니다.

```text
/goodbai
```

Codex가 아래 세 가지를 물어봅니다.

```text
1. 오늘 한 일이나 나온 결과는 무엇인가요?
2. 오늘 배운 것은 무엇인가요?
3. 막힌 점이나 질문은 무엇인가요?
```

막힌 점이 없으면 `없음`이라고 답합니다. Codex는 태그와 산출물 링크를 함께 정리한 뒤, 전송 전 내용을 한 번 보여주고 확인을 받습니다.

`/save`와 `/goodbai`는 서로 다른 명령입니다.

- `/save`: 내 작업을 Git에 저장
- `/goodbai`: BAI 피드에 진행 보고 전송

둘 중 하나를 실행해도 다른 하나가 자동으로 실행되지는 않습니다.

---

## 폴더 구조

이 워크스페이스는 PARA를 학생용으로 단순화해서 씁니다.

- `00-inbox/`: 아직 정리 전인 아이디어와 계획
- `10-projects/`: 지금 만들고 있는 작업
- `20-areas/`: 계속 관리하는 기록과 맥락
- `30-resources/`: 보고 따라 할 참고자료와 예시
- `40-archive/`: 끝난 작업 보관함

```text
vibe-workspace/
├── README.md
├── AGENTS.md                 # Codex 작업 규칙
├── recipes.md                # 바로 써먹는 작업 예시
├── 00-inbox/                 # 정리 전 아이디어와 계획
│   ├── ideas/
│   └── plans/
├── 10-projects/              # 진행 중인 작업
│   └── your-project/
├── 20-areas/                 # 계속 관리하는 기록과 맥락
│   ├── context/
│   └── daily/
├── 30-resources/             # 참고자료, 예시, 보고서
│   ├── examples/
│   └── reports/
├── 40-archive/               # 끝난 작업 보관
├── scripts/
│   ├── setup.ps1             # 초기 설정 (Windows)
│   ├── setup.sh              # 초기 설정 (Mac/Linux)
│   ├── bai_feed_config.py    # BAI 피드 로컬 계정 설정
│   ├── bai_feed_save.py      # BAI 피드 dry-run/전송
│   └── find-python.ps1       # Python 경로 탐색
├── .vscode/
│   └── extensions.json       # 추천 VSCode 익스텐션
└── .codex/
    ├── commands/             # 워크스페이스 플레이북
    ├── rules/                # 세부 작업 규칙
    └── references/           # README/품질 기준
```

---

## Codex 규칙 구조

이 워크스페이스는 `AGENTS.md`를 중심으로 작동합니다.

- `AGENTS.md`: Codex가 먼저 읽는 공통 작업 규칙
- `.codex/commands/`: 사용자가 `/명령어`처럼 말했을 때 따라갈 플레이북
- `.codex/rules/workspace.md`: 워크스페이스 운영 규칙
- `.codex/rules/coding-behavior.md`: 코딩 행동 기준
- `.codex/rules/security.md`: API 키, `.env`, Git 저장 전 보안 기준
- `.codex/rules/build-workflow.md`: 새 작업 폴더 생성 기준

핵심 원칙은 네 가지입니다.

1. 추측하지 말고 가정과 혼란을 드러내기
2. 요청받은 최소 범위만 만들기
3. 필요한 부분만 작게 고치기
4. 성공 기준과 확인 방법을 먼저 정하기

---

## 새 작업을 만들 때

```text
/build 유튜브 자막을 공부 노트로 정리하기
```

작업은 기본적으로 아래 구조로 만들어집니다.

```text
10-projects/작업이름/
├── README.md
├── src/
├── input/
├── output/
└── notes/
```

현재 위치가 하위 폴더여도 새 `10-projects/`를 만들지 말고, 워크스페이스 루트에 이미 있는 `10-projects/`를 사용합니다. `30-resources/examples/`는 참고용이라 새 작업을 넣지 않습니다.

처음부터 배포, 로그인, 외부 API를 기본으로 잡지 않습니다. 먼저 로컬 파일, Markdown, Python, CSV, HTML처럼 바로 확인 가능한 결과물로 시작합니다.

---

## 보안

기본 작업에서는 실제 API 키를 만들거나 코드에 넣지 않습니다.

- `.env` 파일은 Git에 올리지 않습니다.
- API key, password, token 값은 문서에 쓰지 않습니다.
- `/save`는 저장 전에 보안 패턴을 확인합니다.
- `/goodbai`는 `.bai-feed.env` 또는 사용자 홈 설정을 읽지만 비밀값을 출력하지 않습니다.
- 삭제, 대량 이동, Git push 같은 위험 작업은 먼저 확인을 받습니다.

자세한 기준은 `.codex/rules/security.md`에 있습니다.
