# GitHub 배포 가이드

## 1. GitHub 저장소 만들기

1. github.com → 우측 상단 **+** → **New repository**
2. Repository name: `프로젝트명` (영문 소문자·하이픈)
3. **Public** 선택 (Pages 무료 사용)
4. **"Add a README file" 체크 해제** (로컬 파일과 충돌 방지)
5. Create repository

## 2. 로컬 폴더를 GitHub에 올리기

```bash
cd 프로젝트폴더
git init
git add .
git commit -m "init: 초기 설정"
git branch -M main
git remote add origin https://github.com/[내아이디]/[저장소명].git
git push -u origin main
```

## 3. API 키 등록 (GitHub Secrets)

저장소 → **Settings** → 왼쪽 **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름 | 값 | 발급처 |
|---|---|---|
| `GEMINI_API_KEY` | `AIza...` | aistudio.google.com → Get API key (무료) |
| `NAVER_CLIENT_ID` | 영문+숫자 | developers.naver.com (선택) |
| `NAVER_CLIENT_SECRET` | 영문+숫자 | developers.naver.com (선택) |

### 네이버 API 발급 (필요 시)
1. developers.naver.com → Application 등록
2. 사용 API: **검색** 선택
3. 비로그인 오픈 API: **WEB** → URL에 `https://github.com` 입력

## 4. GitHub Pages 활성화

저장소 → **Settings** → 왼쪽 **Pages** → Source: `Deploy from a branch` → Branch: `main` / folder: `/docs` → **Save**

> **주의**: Custom domain 칸은 반드시 비워두세요.

몇 분 후 `https://[내아이디].github.io/[저장소명]` 에서 사이트 확인.

## 5. 첫 수동 실행 (테스트)

저장소 → **Actions** 탭 → **자동 업데이트** → **Run workflow** (한 번만)

초록 ✅ 뜨면 완료. 이후 설정한 스케줄에 따라 자동 실행됨.

## 6. (권장) 외부 스케줄러로 예약 실행 안정화

GitHub Actions의 `schedule` 트리거는 공식 문서에서도 "혼잡 시간대에는 지연되거나 아예
건너뛰어질 수 있다"고 안내한다. 실제로 개인 계정의 저장소에서 며칠씩 예약 실행이
통째로 안 도는 사례가 있었다(정각을 피해 분을 옮겨도 마찬가지였음). `update.yml`에
이미 있는 `workflow_dispatch` 트리거를 외부의 더 안정적인 무료 스케줄러가 대신 눌러주게
만들면 이 문제를 우회할 수 있다. **네이티브 `schedule` 트리거는 그대로 남겨둬도 된다**
(어쩌다 정상 작동하면 보너스이고, `concurrency` 설정 덕분에 겹쳐 실행돼도 안전하다).

### 6-1. GitHub 토큰 발급

1. https://github.com/settings/tokens?type=beta → **Generate new token**
2. **Repository access**: "Only select repositories" → 이 프로젝트 저장소 **하나만** 선택
   (절대 "All repositories"로 하지 않는다 — 다른 저장소까지 건드릴 권한을 줄 필요 없음)
3. **Permissions → Repository permissions → Actions**: `Read and write`
   (그 외 항목은 전부 손대지 않고 기본값(No access)으로 둠. `Metadata: Read-only`는
   GitHub이 자동으로 강제하는 필수 항목이라 신경 안 써도 됨)
4. **Generate token** → `github_pat_...`로 시작하는 값이 딱 한 번 보임 → 즉시 복사해서
   안전한 곳에 보관 (다시 못 봄, 잃어버리면 재발급)

### 6-2. cron-job.org에 작업 등록

1. https://cron-job.org 무료 가입
2. **Create cronjob**:
   - **URL**: `https://api.github.com/repos/[내아이디]/[저장소명]/actions/workflows/update.yml/dispatches`
   - **Execution schedule**: 원하는 시각으로 "Every day at HH:MM" 선택. **Advanced 탭의
     Time zone을 `Asia/Seoul`로 맞추면 UTC로 환산할 필요 없이 한국시간 그대로 입력 가능**
   - **Advanced 탭 → Request method**: `POST` (기본값 GET에서 반드시 바꿀 것 — 흔히 빠뜨림)
   - **Advanced 탭 → Request body**: `{"ref":"main"}`
   - **Advanced 탭 → Headers** 3개 추가:

     | Key | Value |
     |---|---|
     | `Authorization` | `Bearer 실제_토큰_값` |
     | `Accept` | `application/vnd.github+json` |
     | `Content-Type` | `application/json` |

3. 저장 후 **TEST RUN**으로 바로 확인 → 저장소 **Actions** 탭에 새 실행이 뜨면 성공

### 자주 하는 실수: 401 Unauthorized

거의 대부분 **Authorization 값이 실제 토큰으로 완전히 안 바뀐 경우**다. Value 칸을
**전체 선택(Ctrl+A) 후 Delete로 완전히 비우고** `Bearer `를 새로 입력한 뒤 토큰을
붙여넣는다 — 기존 값 위에 이어붙이면 뒤에 글자가 섞여서 인증에 실패한다.

### 보안 메모

토큰은 이 저장소 하나 + Actions 권한만 갖도록 최소 권한으로 만들었지만, 그래도
스크린샷이나 채팅 등으로 한 번이라도 노출됐다면 https://github.com/settings/tokens
에서 즉시 삭제하고 새로 발급받는다.

## 주의사항

- "Re-run jobs"는 **이전 workflow 파일**로 실행됨. 코드 수정 후에는 반드시 **Run workflow** 사용.
- `docs/` 폴더에 `.nojekyll` 빈 파일 필수 (없으면 GitHub Pages 404 발생).
- 동시에 여러 번 Run workflow 클릭 금지 → `concurrency` 설정으로 방지됨.
