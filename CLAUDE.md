# CLAUDE.md — Claude Code 작업 규칙

이 워크스페이스는 원래 Codex 전용으로 만들어졌습니다. 공통 규칙은 모두 `AGENTS.md`에 있고, Claude Code는 아래 import로 그 내용을 그대로 따릅니다.

@AGENTS.md

## 읽는 법

위 `AGENTS.md` 본문에 나오는 "Codex"는 모두 지금 작업 중인 AI 코딩 에이전트, 즉 Claude Code를 가리키는 것으로 읽습니다. 규칙·말투·저장 위치·보안 기준은 에이전트와 무관하게 동일하게 적용됩니다.

## Claude Code 전용 보충 정보

`AGENTS.md`의 절차 본문은 Codex 파일 경로를 기준으로 적혀 있습니다. Claude Code에서는 아래 위치의 위임 파일을 통해 같은 내용을 사용합니다.

- 슬래시 명령: `.claude/commands/*.md` — 각 파일은 `.codex/commands/*.md`의 동일한 명령을 그대로 따르도록 위임되어 있습니다. (`/start`, `/idea`, `/build`, `/plan`, `/review`, `/save`, `/daily`, `/goodbai`)
- 스킬: `.claude/skills/*/SKILL.md` — 각 파일은 `.agents/skills/*/SKILL.md`로 위임되어 있습니다. 실제 절차·스크립트·레퍼런스는 전부 `.agents/skills/` 쪽에 있습니다.
- MCP 서버: `.mcp.json`에 `fetch` 서버가 등록되어 있습니다. `.codex/config.toml`과 동일한 서버이며, Codex/Claude Code 둘 다 같은 `npx @modelcontextprotocol/server-fetch`를 씁니다.

새 명령이나 스킬을 추가할 때는 `.codex/commands/`·`.agents/skills/` 쪽에 먼저 만들고, `.claude/commands/`·`.claude/skills/`에는 위임 파일만 추가해 두 곳이 어긋나지 않게 합니다.
