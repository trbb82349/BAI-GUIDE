# 설명 obra/superpowers

- 출처: https://github.com/obra/superpowers
- 설치일: 2026-08-01 (이 프로젝트에 `claude plugin install superpowers@superpowers-marketplace --scope project`로 설치)
- 비활성화/재활성화 이력: 2026-08-05에 `brainstorming`만 끄려다 플러그인 단위로만 켜고 끌 수 있다는 걸 확인하고 전체를 껐다가(`claude plugin disable ...`), 같은 날 다시 `claude plugin enable superpowers@superpowers-marketplace`로 원복함. 현재 `.claude/settings.json`의 `enabledPlugins`는 `true`(활성).

## 정체

"AI 코딩 에이전트를 위한 완전한 소프트웨어 개발 방법론"을 표방하는 저장소예요. `mattpocock/skills`처럼 낱개 스킬을 골라 쓰는 게 아니라, 브레인스토밍부터 PR까지 개발 과정 전체를 하나로 엮은 프레임워크입니다.

## 핵심 7단계 흐름

1. `brainstorming` — 설계를 검증
2. `using-git-worktrees` — 격리된 작업 환경 구성
3. `writing-plans` — 작은 단위로 계획 수립
4. `subagent-driven-development` — 하위 작업을 서브에이전트에 분업
5. `test-driven-development` — RED-GREEN-REFACTOR 순환
6. `requesting-code-review` — 코드 리뷰
7. `finishing-a-development-branch` — 병합/PR 마무리

## 설치 범위

Claude Code뿐 아니라 Cursor, Gemini, GitHub Copilot CLI 등 11개 플랫폼 지원. MIT 라이선스.

## 규모

⭐ 264k / Fork 23.6k (mattpocock/skills보다 큼)

## 실제 파일 위치 (이 프로젝트 기준)

- 스킬 파일 전체(14개, 위 7단계 + 추가 6개): `C:\Users\trbb8\.claude\plugins\cache\superpowers-marketplace\superpowers\6.2.0\skills\`
- 마켓플레이스 등록 정보: `C:\Users\trbb8\.claude\plugins\marketplaces\superpowers-marketplace`
- 이 프로젝트 안에 남는 건 `.claude/settings.json`의 `enabledPlugins` 스위치 한 줄뿐 — 실제 스킬 파일은 프로젝트 폴더가 아니라 PC 홈 디렉토리에 전역 저장됨(mattpocock/skills와 반대).
