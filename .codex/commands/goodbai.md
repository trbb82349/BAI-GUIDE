# /goodbai — BAI 피드 진행 보고

오늘 작업을 BAI 피드에 올릴 진행 보고로 정리합니다. 태그, 링크, 프로젝트 연결은 학생에게 먼저 묻지 말고 Codex가 대화와 워크스페이스에서 수집합니다.

## 사용법

```text
/goodbai
```

또는:

```text
/goodbai 오늘 만든 모델 결과를 BAI 피드에 정리해줘
```

## 실행 순서

### 1단계: 조용히 스킬 확인

`.agents/skills/bai-feed-goodbai/SKILL.md`를 읽고 따릅니다. 이 단계의 파일 경로, 루트 확인, 설정 파일 존재 여부, 환경변수 확인 결과는 학생에게 먼저 길게 보여주지 않습니다.

로컬 설정은 아래 우선순위로 적용합니다. 뒤에 있는 값이 앞의 값을 덮어씁니다.

1. 사용자 홈의 `.bai-feed.env`
2. 워크스페이스 루트의 `.bai-feed.env`
3. `BAI_FEED_CONFIG`로 지정한 설정 파일
4. 환경변수 `BAI_FEED_*`

설정이 없어도 여기서 멈추지 말고 먼저 학생 진행 내용을 수집합니다. 설정 안내는 전송 직전 또는 사용자가 전송을 승인한 뒤에만 짧게 보여줍니다.

설정 안내를 보여줄 때는 `python scripts\bai_feed_config.py`만 단독으로 말하지 않습니다. 반드시 현재 워크스페이스의 절대 경로로 먼저 이동하는 명령까지 함께 보여줍니다. 실제 학생에게 답할 때는 `<현재 워크스페이스 절대경로>`를 그대로 쓰지 말고, 지금 열린 워크스페이스의 실제 절대 경로로 바꿉니다.

```powershell
cd "<현재 워크스페이스 절대경로>"
python scripts\bai_feed_config.py
```

이미 잘못된 값이 저장되어 401, invalid credentials, login 실패가 났다면 기존 설정을 덮어써야 하므로 아래처럼 `--force`를 붙입니다.

```powershell
cd "<현재 워크스페이스 절대경로>"
python scripts\bai_feed_config.py --force
```

학생에게 입력값을 안내할 때는 아래 내용을 반드시 포함합니다.

```text
BAI feed name: 본인 이름을 입력합니다. PowerShell 화면에 글자가 보입니다.
BAI feed API key: 선생님에게 받은 API key를 붙여넣습니다. PowerShell 화면에는 아무 글자도 보이지 않지만 정상입니다. 붙여넣고 Enter를 누르면 입력됩니다.
```

기본 설정은 BAI API key를 저장합니다. 기존 비밀번호 로그인 방식이 꼭 필요할 때만 아래처럼 legacy login 설정을 사용합니다.

```powershell
cd "<현재 워크스페이스 절대경로>"
python scripts\bai_feed_config.py --password
```

### 2단계: 학생 진행 내용 확인

학생에게는 아래 3가지만 묻습니다. `/goodbai`만 입력했고 학생 진행 내용이 아직 없다면, 아래 문구만 먼저 보여줍니다.

```text
BAI 피드에 올릴 오늘 진행 보고를 정리할게요.

아래 3가지만 답해 주세요.

1. 오늘 한 일이나 나온 결과는 무엇인가요?
2. 오늘 배운 것은 무엇인가요?
3. 막힌 점이나 질문은 무엇인가요?

태그와 링크는 제가 작업 내용을 보고 자동으로 정리하겠습니다.
```

중요: `/goodbai` 명령 자체를 실행하면서 Codex가 방금 확인한 파일 변경, dry-run 결과, 설정 상태, 이 명령의 구현 작업을 학생의 진행 보고로 쓰지 않습니다. 학생이 자기 프로젝트 진행 내용을 명시적으로 말하지 않았다면 payload를 만들지 말고 여기서 멈춰 아래 질문부터 합니다.

이미 최근 대화에 학생이 직접 쓴 진행 내용이 충분히 있으면 3개 필드로 요약해 확인합니다. 충분하지 않으면 한 번에 3개 질문을 보여주고 답을 기다립니다.

막힌 점이 없다고 답한 경우에도 `blocked`를 빈칸으로 두지 말고 `없음`으로 저장합니다. 세 필드가 모두 채워져야 피드 카드의 전체 구조가 유지됩니다.

### 3단계: Codex가 자동 수집할 내용

학생에게 따로 묻지 말고 Codex가 직접 수집합니다.

- 태그: 학생 답변, 대화, 관련 작업 폴더명, README를 보고 2~5개 생성
- 링크: GitHub URL, 배포 URL, 산출물 파일 경로, 보고서/HTML/CSV 출력 경로
- 프로젝트: 정확한 BAI `project_id`를 모르면 `null`

최근 변경 파일은 링크/산출물 후보를 찾을 때만 참고합니다. `did`, `learned`, `blocked`를 최근 변경 파일만 보고 대신 작성하지 않습니다.

링크가 로컬 파일이면 학생이 확인할 수 있게 경로를 넣어도 됩니다. 공개 URL만 억지로 요구하지 않습니다.

### 4단계: payload 만들기

2단계의 `did`, `learned`, `blocked`가 모두 확인된 뒤에만 payload를 만듭니다.

`.codex/tmp/`가 없으면 만들고 아래 JSON을 저장합니다.

```text
.codex/tmp/bai-feed-payload.json
```

형식:

```json
{
  "did": "...",
  "learned": "...",
  "blocked": "...",
  "tags": "tag1, tag2",
  "links": "https://... 또는 로컬 산출물 경로",
  "project_id": null
}
```

### 5단계: 전송 전 확인

아래처럼 보여줍니다.

```text
BAI 피드 전송 전 확인:

- 한 일/결과:
- 배운 것:
- 막힌 점/질문:
- 태그: Codex가 수집
- 링크: Codex가 수집
- 프로젝트: 연결 안 함 또는 project_id

이 내용으로 BAI 피드에 올릴까요?
```

사용자가 명확히 승인하기 전에는 `--send`를 실행하지 않습니다.

### 6단계: dry-run

승인 전 또는 설정 점검 단계에서는 dry-run만 실행합니다. dry-run 결과를 보여줄 때도 내부 경로/환경변수 목록을 먼저 길게 나열하지 말고, payload와 설정 필요 여부만 짧게 요약합니다.

```bash
python scripts/bai_feed_save.py --input-json .codex/tmp/bai-feed-payload.json --dry-run --show-config
```

### 7단계: 전송

사용자가 "올려줘", "전송해", "좋아"처럼 명확히 승인하면 실행합니다.

```bash
python scripts/bai_feed_save.py --input-json .codex/tmp/bai-feed-payload.json --send
```

성공하면 응답의 `absolute_url` 또는 `url`과 `id`를 알려줍니다.

설정이 없어서 전송할 수 없으면 아래처럼 짧게 안내합니다.

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

기존 설정이 틀려서 전송이 실패했으면 아래처럼 안내합니다.

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

## 주의

- 비밀번호, API key, token 값을 출력하지 않습니다.
- 학생에게 처음 보여주는 응답에는 루트 경로, 설정 파일 탐색 결과, 환경변수 진단, payload 같은 내부 용어를 앞세우지 않습니다.
- 브라우저 자동 조작을 하지 않습니다.
- 실패하면 HTTP status와 서버 error JSON만 요약합니다.
- API key가 설정되어 있으면 기본 전송은 `/api/post`를 사용합니다. 비밀번호 로그인은 API key가 없을 때만 fallback으로 사용합니다.
- `Cloudflare Error 1010` 또는 `browser_signature_banned`가 나오면 비밀번호 문제가 아니라 BAI 사이트 보안 정책이 Python API 요청을 Flask 앞단에서 막은 것입니다. 반복 재시도하지 말고 사이트 관리자에게 `/api/post` 자동화 endpoint 예외를 요청합니다.
- `/save`는 Git 저장용으로 그대로 둡니다. BAI 피드 전송은 `/goodbai`만 사용합니다.
