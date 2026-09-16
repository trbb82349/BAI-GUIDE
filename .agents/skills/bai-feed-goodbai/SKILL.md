---
name: bai-feed-goodbai
description: Save BAI student progress updates from Codex to the BAI website feed. Use when the user runs /goodbai, asks to post a progress report to BAI, or wants Codex to collect did/learned/blocked plus inferred tags, links, and project context before calling scripts/bai_feed_save.py.
---

# BAI Feed Goodbai

Use this skill to turn a student's local Codex work into a BAI feed progress post.

## Workflow

1. Start with a student-friendly prompt when the user only runs `/goodbai` and no explicit progress content is present:

```text
BAI 피드에 올릴 오늘 진행 보고를 정리할게요.

아래 3가지만 답해 주세요.

1. 오늘 한 일이나 나온 결과는 무엇인가요?
2. 오늘 배운 것은 무엇인가요?
3. 막힌 점이나 질문은 무엇인가요?

태그와 링크는 제가 작업 내용을 보고 자동으로 정리하겠습니다.
```

2. Collect only the human-progress fields from the user or explicit recent student-authored chat:
   - `did`: 한 일/결과
   - `learned`: 배운 것
   - `blocked`: 막힌 점/질문
   If these fields are not clearly present, stop and ask the three questions before creating a payload or running dry-run. If the student says there is no blocker, set `blocked` to `없음`; do not leave it blank.
3. Infer these fields yourself from the workspace and conversation:
   - `tags`: short comma-separated Korean/English tags
   - `links`: GitHub, local artifact, report, output, or deployment URLs mentioned in chat or files
   - `project_id`: use `null` unless a reliable BAI project id is already known
4. Show the final payload before sending. Do not ask the student to fill tags, links, or project unless inference is impossible and the value is essential.
5. Run a dry-run first:

```bash
python scripts/bai_feed_save.py --input-json .codex/tmp/bai-feed-payload.json --dry-run --show-config
```

6. Send only after explicit confirmation:

```bash
python scripts/bai_feed_save.py --input-json .codex/tmp/bai-feed-payload.json --send
```

## Rules

- Do not print passwords or API keys.
- Keep the first user-facing response quiet and student-friendly. Do not lead with workspace roots, config search results, environment variables, payload file paths, or other diagnostics.
- If config is missing, collect the student's progress first. Mention setup only at the send step or after the user asks about setup.
- For missing config, do not only say `python scripts\bai_feed_config.py`. Always include the current workspace absolute path and a `cd` command first. Replace `<현재 워크스페이스 절대경로>` with the actual current workspace path in the response; do not show the placeholder to the student.

```text
전송하려면 BAI 계정 설정이 필요합니다.

PowerShell에서 아래 명령을 그대로 실행하세요.

cd "<현재 워크스페이스 절대경로>"
python scripts\bai_feed_config.py

입력할 값:
- BAI feed name: 본인 이름을 입력합니다. 이 값은 PowerShell 화면에 보입니다.
- BAI feed API key: 선생님에게 받은 API key를 붙여넣습니다. 이 값은 비밀번호처럼 화면에 보이지 않습니다. 붙여넣고 Enter를 누르면 정상 입력됩니다.

설정이 끝나면 여기로 돌아와 `전송해줘`라고 말하면 됩니다.
```

- If posting fails with 401, invalid credentials, or a login failure, tell the student to overwrite the existing config with `--force`:

```text
BAI 피드에 저장된 로그인 정보가 맞지 않아 전송에 실패했습니다.

PowerShell에서 아래 명령을 그대로 실행해 기존 설정을 다시 저장하세요.

cd "<현재 워크스페이스 절대경로>"
python scripts\bai_feed_config.py --force

입력할 값:
- BAI feed name: 본인 이름을 입력합니다. 이 값은 PowerShell 화면에 보입니다.
- BAI feed API key: 선생님에게 받은 API key를 붙여넣습니다. 이 값은 비밀번호처럼 화면에 보이지 않습니다. 붙여넣고 Enter를 누르면 정상 입력됩니다.

설정이 끝나면 여기로 돌아와 `전송해줘`라고 말하면 됩니다.
```

- Do not use command execution results, setup state, dry-run output, or this skill's implementation work as the student's progress report.
- Do not infer `did`, `learned`, or `blocked` from git status or recent files alone. Use files only to help infer tags and links after the student progress fields are known.
- Do not send partial progress posts. `did`, `learned`, and `blocked` must all be non-empty; use `없음` for `blocked` only when the student explicitly has no blocker.
- Prefer API key auth. When `BAI_FEED_API_KEY` is present, `/goodbai` posts to `/api/post`; legacy login is only a fallback when no API key is configured.
- Keep `project_id` as `null` in the first version unless an exact id is known.
- If config is missing, help the user create it with the full PowerShell command block above, including `cd "<현재 워크스페이스 절대경로>"`.
- If posting fails, report the HTTP status and server JSON error without exposing secrets.
- If posting fails with `Cloudflare Error 1010` or `browser_signature_banned`, explain that the BAI site's Cloudflare policy blocked the Python API request before Flask. Do not retry repeatedly. Recommend a site-side exception for the automation endpoint, preferably the API-key endpoint.
- Do not use browser automation for posting.
- Keep `/save` for Git saving; use `/goodbai` for BAI feed posting.

## Payload Shape

```json
{
  "did": "...",
  "learned": "...",
  "blocked": "...",
  "tags": "tag1, tag2",
  "links": "https://...",
  "project_id": null
}
```

For API details, read `references/api.md` only when changing the script or debugging API behavior.
