# 건너뛴 스킬 — mattpocock

← [mattpocock-skills 정리로 돌아가기](2026-08-01-mattpocock-skills.md)

지금 워크스페이스는 실제 코드베이스나 git 협업 프로젝트가 없는 개인 자동화 공간이라, 아래 12개는 당장 체험하지 않아도 되는 스킬로 분류했습니다. 실제 코드 프로젝트를 시작하거나 TypeScript 강의 자료를 만들 일이 생기면 그때 다시 봐도 됩니다.

**2026-08-01 기준 실제 스킬 파일도 비활성화 처리됨:** `.agents/skills/`에서 `.agents/skills-disabled/mattpocock/`로 옮겼고, `.claude/skills/`의 심볼릭 링크와 `skills-lock.json` 항목도 함께 제거했습니다. 즉 지금은 이 12개 스킬이 실제로 동작하지 않습니다.

**2026-08-05 갱신:** 그 사이 나머지 mattpocock 스킬 29개도 전부 비활성화되면서(→ [mattpocock-skills 정리](2026-08-01-mattpocock-skills.md) 참고), 이 12개는 우선순위를 더 낮추기 위해 `.agents/skills-disabled/mattpocock/`에서 `.agents/skills-disabled-2/mattpocock/`으로 다시 옮겼습니다. 나중에 다시 쓰고 싶으면 `.agents/skills-disabled-2/mattpocock/<이름>`을 `.agents/skills/<이름>`으로 되돌리고, `.claude/skills/<이름>`에 같은 이름의 심볼릭 링크를 다시 만들면 됩니다.

## 이 워크스페이스와 성격이 안 맞음 (TypeScript/강의 제작 전용)
- `setup-pre-commit` — Husky pre-commit hook + lint-staged 설정 (JS/TS 프로젝트 전용)
- `setup-ts-deep-modules` — dependency-cruiser로 TypeScript deep module 구조 강제
- `migrate-to-shoehorn` — TS 테스트의 `as` 타입 단언을 `@total-typescript/shoehorn`으로 교체
- `scaffold-exercises` — 강의용 exercise 디렉토리 스캐폴딩 (Matt Pocock 강의 제작용)

## 실제 코드/git 프로젝트가 있을 때 의미 있음
- `tdd` — 테스트주도개발(red-green-refactor)
- `code-review` — 코딩 표준·스펙 두 축으로 병렬 서브에이전트 코드 리뷰
- `resolving-merge-conflicts` — 진행 중인 git merge/rebase 충돌 해결
- `wayfinder` — 여러 세션에 걸치는 대형 작업을 티켓 맵으로 나눠 하나씩 해결
- `request-refactor-plan` — 리팩터 계획을 인터뷰로 만들어 GitHub 이슈로 파일링 (GitHub 이슈 트래커 전제)
- `improve-codebase-architecture` — 코드베이스를 스캔해 HTML 리포트로 개선점 제시 후 논의
- `qa` — 대화형으로 버그를 보고받아 이슈로 파일링

## 사용 전 한 번 더 검토 필요 (주의)
- `diagnosing-bugs` — 어려운 버그·성능 저하 진단 루프. 설치 시 보안 스캔에서 **Snyk 기준 High Risk**로 표시됨. 실제로 쓰기 전에 `.agents/skills/diagnosing-bugs/SKILL.md` 내용을 한 번 훑어보는 걸 권장.
