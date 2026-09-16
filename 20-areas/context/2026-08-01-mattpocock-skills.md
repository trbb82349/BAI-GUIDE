# mattpocock/skills 설치 정리

- 출처: https://github.com/mattpocock/skills
- 설치일: 2026-08-01
- 설치 명령: `npx skills@latest add mattpocock/skills`
- 설정 파일: `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`, `AGENTS.md`의 `## Agent skills` 섹션

이 문서는 정리·참고용입니다. 실제 스킬을 켜고 끄거나 옮기려면 `.agents/skills/` 쪽 파일 자체를 건드려야 하며, 이 문서를 옮긴다고 스킬 동작이 바뀌지는 않습니다.

## 2026-08-05 기준 상태 — 전부 비활성화됨

아래 1~4단계·기타에 적힌 29개는 2026-08-01엔 활성 상태였지만, 2026-08-05에 전부 비활성화 처리했습니다. `.agents/skills/`에서 `.agents/skills-disabled/mattpocock/`로 옮겼고, `.claude/skills/`의 심볼릭 링크와 `skills-lock.json` 항목도 함께 제거했습니다. 즉 아래 목록은 지금 "체험 추천 순서"가 아니라 "비활성화된 스킬 29개 + 원래 켜져 있던 순서 기록"으로 읽어야 합니다.

기존에 이미 꺼져 있던 12개(`.agents/skills-disabled/mattpocock/`, → [건너뛴 스킬-mattpocock](2026-08-01-건너뛴-스킬-mattpocock.md))는 `.agents/skills-disabled-2/mattpocock/`으로 다시 옮겨서, 앞으로도 잘 안 쓸 것 같은 스킬과 나중에 다시 켤 가능성이 있는 스킬을 구분해뒀습니다.

- `.agents/skills-disabled/mattpocock/` (29개) — 최근까지 켜져 있었고 다시 켤 가능성 있음. 원래대로 켜려면 `.agents/skills-disabled/mattpocock/<이름>`을 `.agents/skills/<이름>`으로 옮기고, `.claude/skills/<이름>`에 같은 이름의 심볼릭 링크를 다시 만들면 됩니다.
- `.agents/skills-disabled-2/mattpocock/` (12개) — 거의 안 쓸 것 같아서 우선순위를 더 아래로 둔 것.

## 체험 추천 순서 (가벼운 것부터)

### 1단계 — 대화만으로 끝남
- `ask-matt` — 지금 상황에 어떤 스킬이 맞는지 물어보면 골라주는 라우터
- `grill-me` — 아이디어·계획을 집요한 인터뷰로 검증
- `teach` — 모르는 개념을 눈높이에 맞춰 가르쳐줌

### 2단계 — 대화 + 짧은 결과물
- `to-questionnaire` — 혼자 결정 못 내리는 문제를 설문지로 변환
- `handoff` — 지금까지 대화를 인수인계 문서로 요약 저장
- `claude-handoff` — 지금 대화를 백그라운드 에이전트에게 즉시 넘김
- `writing-fragments` — 글쓰기 재료를 구조 없이 모으기(탐색 단계)
- `writing-beats` — 모은 재료를 흐름(beats)으로 배열
- `writing-shape` — beats를 문단 단위 글로 완성
- `edit-article` — 완성된 글의 구조·문장을 다듬기
- `grilling` — grill-me보다 더 집요한 버전
- `batch-grill-me` — 여러 질문을 라운드별로 한 번에 던짐

### 3단계 — 실제 파일/조사 결과물
- `research` — 주제를 조사해 마크다운 보고서로 저장
- `prototype` — 버리는 셈 치고 빠르게 프로토타입 코드로 확인
- `design-an-interface` — API/인터페이스 여러 버전을 병렬로 설계
- `wizard` — 외부 서비스 설정 같은 수동 절차를 대화형 bash 마법사로 생성
- `obsidian-vault` — Obsidian 노트 검색·생성·관리 (Obsidian 사용 시에만 의미 있음)
- `loop-me` — 이 워크스페이스 안에서 만들 워크플로우의 스펙을 인터뷰로 정리

### 4단계 — 오늘 설정한 로컬 이슈 트래커를 실제로 쓰는 흐름 (제일 무거움)
- `grill-with-docs` — 인터뷰하면서 ADR·용어집을 자동으로 남김
- `domain-modeling` — 프로젝트 도메인 모델/ADR 구축
- `ubiquitous-language` — 대화에서 도메인 용어집 추출
- `codebase-design` — 모듈 설계를 위한 공통 어휘
- `to-spec` — 대화를 스펙으로 정리해 이슈 트래커(`.scratch/`)에 발행
- `to-tickets` — 스펙을 블로킹 관계가 있는 티켓들로 쪼갬
- `triage` — 이슈를 5단계 상태머신으로 분류
- `implement` — 스펙/티켓 기반으로 실제 구현

## 건너뛴 스킬

지금 워크스페이스(실제 코드/git 프로젝트가 없는 개인 자동화 공간)엔 안 맞거나, 나중에 필요할 때 보는 게 나은 12개는 따로 정리했습니다.
→ [건너뛴 스킬-mattpocock](2026-08-01-건너뛴-스킬-mattpocock.md)

이 12개는 2026-08-01에 실제 스킬 파일도 `.agents/skills-disabled/mattpocock/`으로 옮겨 비활성화했습니다. 위 1~4단계 체험 목록에는 영향 없습니다.

## 기타 (참고용 / 이미 완료)

- `setup-matt-pocock-skills` — 리포별 초기 설정 스킬. 2026-08-01에 이미 실행 완료(로컬 마크다운 이슈 트래커, 기본 triage 라벨, 단일 컨텍스트 도메인 문서로 설정됨). 재실행은 이슈 트래커를 바꾸고 싶을 때만.
- `writing-great-skills` — 스킬을 직접 쓰거나 고칠 때 보는 레퍼런스 문서. 체험용이 아니라 참고용.
- `git-guardrails-claude-code` — 위험한 git 명령(push, reset --hard 등)을 막는 훅을 설정하는 스킬. 지금 당장 필요하진 않지만, 나중에 이 워크스페이스에서 git 작업이 늘어나면 한 번 돌려볼 만함.
