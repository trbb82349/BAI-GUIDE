# AGENTS.md — Codex Vibe Workspace Rules

이 파일은 Codex가 작업 전에 읽는 공통 지시 파일입니다. 자세한 절차는 `.codex/commands/`, 세부 규칙은 `.codex/rules/`에 둡니다.

## 먼저 읽기

작업을 시작하면 아래 파일을 먼저 확인합니다.

1. `README.md` — 사람용 워크스페이스 안내
2. 무엇을 만들지 막막할 때 `recipes.md` — 바로 써먹는 작업 예시
3. 코딩·저장·새 작업 폴더 생성 직전에 `.codex/rules/*.md`

사용자가 처음 시작한다면 Git 저장소와 `.githooks` 등록 여부를 확인합니다. 설정이 안 되어 있으면 사용자에게 터미널 명령을 먼저 시키지 말고 Codex가 `.codex/commands/start.md` 기준으로 초기 설정 스크립트를 실행합니다.

## 워크스페이스 목적

이 폴더는 Codex와 함께 작은 자동화, 문서 정리, 데이터 처리, 웹 화면, 스크립트를 빠르게 만들기 위한 개인 작업 공간입니다.

- 대상: Windows 또는 Mac + VSCode + Codex 사용자
- 말투: 한국어, 짧고 직접적으로
- 기본 방향: 로컬 파일, Markdown, Python, HTML, CSV처럼 눈으로 확인 가능한 결과부터
- 피할 것: 처음부터 외부 API, 로그인 자동화, 배포, 과한 프레임워크를 기본안으로 제안하지 않기

## 작업 시작 원칙

바로 구현하지 말고 짧게 정리합니다.

- 목표: 무엇을 끝내려는가
- 입력: 어떤 파일, 폴더, 사용자 답변이 필요한가
- 출력: 어떤 파일이나 결과가 생기는가
- 확인: 무엇을 보면 성공했다고 할 수 있는가

요구가 애매하면 위험한 추측을 하지 말고 질문합니다. 단순하고 되돌리기 쉬운 일은 합리적으로 진행합니다.

## 코딩 행동 기준

4원칙 — Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution. 자세한 기준은 `.codex/rules/coding-behavior.md`를 봅니다.

## 저장 위치

| 요청 유형 | 저장 위치 |
|---|---|
| 아이디어 메모 | `00-inbox/ideas/` |
| 구현 없는 작업 카드, 요구사항 정리 | `00-inbox/plans/` |
| 작업 기록, 회고 | `20-areas/daily/` |
| 조사 보고서, 레퍼런스 정리 | `30-resources/reports/` |
| 반복 설명, 사용자 선호, 작업 맥락 | `20-areas/context/` |
| 여러 파일로 된 작업 | 워크스페이스 루트의 `10-projects/작업이름/` |
| 완성된 단일 자동화 스크립트 | `scripts/` |

학생에게 설명할 때는 PARA라는 말보다 아래 표현을 우선합니다.

- `00-inbox/`: 아직 정리 전
- `10-projects/`: 지금 만드는 것
- `20-areas/`: 계속 관리하는 것
- `30-resources/`: 보고 따라 할 자료
- `40-archive/`: 끝난 것

마크다운 파일명은 `YYYY-MM-DD-짧은-주제.md`를 기본으로 합니다. 날짜는 KST 기준입니다.

## 워크스페이스 명령

Codex IDE/CLI의 공식 slash command 자동완성과 별개로, 이 워크스페이스에서는 사용자가 `/명령어`처럼 말하면 `.codex/commands/명령어.md`를 플레이북으로 읽고 실행합니다.

기본 명령:

- `/start`: 작업 환경 확인과 첫 작업 제안
- `/idea`: 아이디어 메모
- `/build`: 아이디어를 작업 카드, 작업 폴더, 첫 결과물로 변환
- `/plan`: 구현 없이 작업 카드만 정리
- `/review`: 저장/공유 전 점검
- `/daily`: 작업 기록과 다음 액션 정리
- `/save`: Git 저장 전 보안 확인
- `/goodbai`: Codex가 진행 보고를 정리해 BAI 피드에 전송

## 새 작업 생성 기준

여러 파일로 구성되는 작업은 워크스페이스 루트의 `10-projects/작업이름/` 아래에 만듭니다. 현재 폴더가 `10-projects/` 안쪽이어도 새 `10-projects/`를 만들지 말고, 먼저 루트 폴더를 확인한 뒤 기존 `10-projects/`를 사용합니다.

필수 구조:

```text
작업이름/
├── README.md
├── src/
├── input/
├── output/
└── notes/
```

README는 짧은 소개가 아니라 다음 세션에 바로 이어서 실행할 수 있는 작업 카드여야 합니다. 자세한 기준은 `.codex/rules/build-workflow.md`와 `.codex/references/work-readme-guide.md`를 봅니다.

## 보안

`.env`·API 키·token 파일은 만들지 않고, 위험 작업(삭제·대량 이동·Git push·외부 서비스 쓰기)은 먼저 승인을 받습니다. 자세한 기준은 `.codex/rules/security.md`를 봅니다.

## Python 확인

Python이 필요하면 `python --version` 한 번 실패로 단정짓지 말고, `.codex/rules/python.md`의 순서대로 Python·Anaconda·Launcher 경로를 확인하고 결과를 `.codex/local-python.json`에 저장합니다.

## 사용자와의 대화

- 항상 한국어로 답합니다.
- 터미널 명령을 사용자에게 먼저 시키지 말고, Codex가 가능한 확인과 실행을 먼저 합니다.
- 실패하면 원인을 짧게 설명하고 다음 선택지를 제시합니다.
- 작업 후에는 저장된 경로, 실행 방법, 확인 방법을 남깁니다.

## 스킬 & MCP

이 워크스페이스에는 검증된 외부 스킬과 MCP 서버가 포함되어 있습니다.

**Agent Skills** (`.agents/skills/`) — 사용자가 `.docx`/`.pptx`/`.pdf`/`.xlsx`/`.csv` 파일이나 "웹 스크래핑", "새 스킬 만들기"를 언급하면 해당 스킬이 자동으로 활성화됩니다. 명시적인 호출은 필요하지 않습니다.

| 스킬 | 출처 | 용도 |
|---|---|---|
| `bai-feed-goodbai` | local | `/goodbai` 진행 보고를 BAI 피드에 dry-run 후 전송 |
| `docx` | included | Word 문서 읽기/생성 |
| `pptx` | included | PowerPoint 읽기/생성 |
| `pdf` | included | PDF 텍스트 추출 |
| `xlsx` | included | Excel 읽기/생성 |
| `web-scraper` | local | 공개 웹페이지 정적/동적 스크래핑 코드 생성 |
| `skill-creator` | B 벤치마킹 | 새 Agent Skill을 만들거나 기존 스킬을 개선할 때 사용하는 메타스킬 |

각 스킬 폴더에는 SKILL.md 외에, 비전공자도 이해할 수 있게 쉬운 말로 풀어 쓴 설명 파일도 같이 둡니다. 자세한 기준은 `.codex/rules/skills-plain-explanation.md`를 봅니다.

**MCP 서버** (`.codex/config.toml`) — Codex 전용입니다.

| 서버 | 용도 | 필요 조건 |
|---|---|---|
| `fetch` | 공개 웹페이지 본문 가져오기 | Node.js (자동) |

## Agent skills

`mattpocock/skills` 엔지니어링 스킬(`/tdd`, `/implement`, `/triage`, `/to-tickets` 등)이 참조하는 저장소별 설정입니다.

### Issue tracker

GitHub Issues 대신 로컬 마크다운(`.scratch/<feature-slug>/`)으로 이슈·스펙을 관리합니다. See `docs/agents/issue-tracker.md`.

### Triage labels

기본 5개 라벨(`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)을 그대로 사용합니다. See `docs/agents/triage-labels.md`.

### Domain docs

단일 컨텍스트: 루트의 `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

## 이 파일의 역할

`AGENTS.md`는 지도입니다. 너무 길어지면 안 됩니다. 세부 절차, 예시, 체크리스트는 `.codex/commands/`, `.codex/rules/`, `.codex/references/`로 분리합니다.
