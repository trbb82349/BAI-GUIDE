---
name: auto-update-site
description: >
  자동 업데이트 웹사이트 시스템 구축 스킬. GitHub Actions(무료)로 정해진 스케줄에 데이터를 수집·분석하고, 정적 HTML을 생성해 GitHub Pages(무료)로 배포한다.
  사용자가 "자동으로 업데이트되는 웹사이트", "주기적으로 데이터를 가져와서 보여주는 페이지", "스케줄 자동 실행 사이트", "GitHub Pages 자동 배포", "매일/매주 새 글 긁어와서 보여주는 사이트"를 언급하면
  명시적으로 이 스킬을 요청하지 않았어도 먼저 이 스킬을 사용한다.
  핵심 패턴: collect.py(데이터 수집·AI분석) → data.json → build_site.py(HTML 생성) → docs/index.html → GitHub Actions(스케줄) → GitHub Pages 배포.
---

# Auto-Update Site 스킬

## Input — 시작 전 확인할 것

사용자에게 아래 5가지가 확정됐는지 확인한다. 하나라도 비어 있으면 임의로 정하지 말고 먼저 질문한다.

1. 무엇을 자동으로 보여줄 것인가 (주제·데이터 종류) — "인기/트렌드/신규"처럼 선별이 필요한 주제라면, 무엇을 기준으로 고를지(조회수순? 최신순? 특정 키워드?)도 같이 확정한다. 기준을 말하지 않았으면 임의로 정하지 말고 질문한다.
2. 데이터 원천이 어디인가 (공개 API / RSS / 특정 웹페이지)
3. 업데이트 주기 (하루 1회? 주 2회?)
4. GitHub 계정과 이 프로젝트용 저장소가 있는가
5. 데이터 원천이 인증(API 키)을 요구하는가

전제 조건: 이 스킬은 "정적 HTML + GitHub Actions 스케줄" 조합이 전제다. 로그인이 필요한 개인화 페이지, 초 단위 실시간 갱신처럼 이 전제를 벗어나는 요구는 이 스킬로 처리할 수 없다 — 임의로 우겨넣지 말고 사용자에게 "이 스킬 범위 밖"이라고 알린다.

무료 한도 (설계 전에 이 안에서 끝나는지 가늠):

| 서비스 | 비용 | 한도 |
|--------|------|------|
| Gemini 1.5 Flash | 무료 | 하루 1,500회 |
| 네이버 검색 API | 무료 | 하루 25,000회 |
| GitHub Actions | 무료 | 월 2,000분 |
| GitHub Pages | 무료 | - |

## Judgment — 판단 규칙

제약 3개:

1. 모든 구성요소는 무료 티어 안에서 해결한다. 유료 API가 필요한 요구라면 진행 전에 사용자에게 알리고 확인받는다.
2. `cron` 스케줄의 분(minute)은 0으로 설정하지 않는다. 정각은 GitHub가 공식적으로 밝힌 혼잡 시간대라 실행이 지연되거나 그 회차가 통째로 스킵된 사례가 있었다.
3. 페이지네이션 기반 증분 수집에서는 "한 페이지 안에 이미 아는 항목이 하나라도 섞여 있으면 그 페이지에서 멈춘다"(페이지 전체가 새 항목일 때만 다음 페이지로 진행) 안전장치를 반드시 넣는다. 없으면 몇 달 전 옛 글이 안전 상한까지 통째로 오탐되어 끌려올 수 있다(실제 사고 이력).

우선순위 (자료가 충돌할 때): 사용자가 이번 대화에서 명시한 요구사항 > 이 SKILL.md의 기본 패턴 > `references/github-setup.md`의 세부 절차.

미확정 항목은 결정하지 말고 OPEN으로 유지한다:

- 데이터 원천이 스크래핑 대상이면 이용약관·robots.txt 확인 여부가 불명확할 때 `[OPEN: 이용약관 확인 필요]`로 표시하고, 확인 전에는 수집 로직을 완성하지 않는다.
- 사용자가 업데이트 주기를 말하지 않았는데 "하루 1회"처럼 임의로 정하지 않는다 — Input 단계로 돌아가 질문한다.

## Steps — 순서

1. **data.json 설계** — 사용자 요구에 맞게 스키마 설계. 반드시 `meta.last_updated` 필드 포함:
   ```json
   {
     "meta": { "last_updated": "YYYY-MM-DD" },
     "items": [ { "id": "...", "name": "...", ... } ]
   }
   ```
2. **collect.py 작성** — 이 단계에 도달하면 `assets/templates/collect_template.py`를 읽고 그 구조를 기반으로 작성한다. 핵심: 외부에서 수집 → Gemini로 분석 → 기존 data.json 로드 → 신규 항목만 추가 → 저장. (`fetch_raw_data`의 페이지네이션 안전장치 주석 참고 — Judgment 제약 3과 동일 이슈)
3. **build_site.py 작성** — `assets/templates/build_site_template.py`를 읽고 그 구조를 기반으로 작성한다. 핵심: data.json 읽기 → KST 시각 생성(`datetime.now(timezone(timedelta(hours=9)))`) → f-string으로 HTML 생성(JS 중괄호는 `{{` `}}` 이스케이프) → `docs/index.html` 저장.
4. **update.yml 작성** — `assets/templates/update.yml`을 복사해 `cron` 스케줄(분은 0 아님)과 `env`의 Secret 이름만 교체한다.
5. **GitHub 배포** — 이 단계에 도달하면 `references/github-setup.md`를 읽고 그 순서(저장소 생성 → push → Secrets 등록 → Pages 활성화 → 수동 실행 테스트 → 필요시 외부 스케줄러 연결)를 그대로 따른다.

## Output — 결과 모양

**좋은 예시**:
```
프로젝트/
├── data/data.json          ← meta.last_updated 포함, 주석 없는 순수 JSON
├── src/collect.py          ← 안전장치 있는 증분 수집
├── src/build_site.py       ← docs/index.html 생성
├── docs/
│   ├── index.html
│   └── .nojekyll            ← 빈 파일, 필수
└── .github/workflows/update.yml   ← cron 분이 0이 아님
```

**피해야 할 예시**: `data.json`에 `// 최근 추가` 같은 주석을 넣는 것. JSON 표준에 주석이 없어 파싱이 그 즉시 깨지고, build_site.py가 실패해 사이트 전체가 갱신되지 않는다. 메모가 필요하면 `"_comment"` 키를 쓴다.

## QA — 끝났다고 판단하는 기준

- [ ] `data.json`이 유효한 JSON이고 `//` 주석이 없다
- [ ] `docs/.nojekyll` 파일이 존재한다
- [ ] `update.yml`의 `cron` 분이 0이 아니다
- [ ] 페이지네이션을 쓴다면 "페이지 전체가 새 항목일 때만 다음 페이지" 안전장치가 들어 있다
- [ ] GitHub Actions **Actions** 탭에서 `workflow_dispatch` 수동 실행이 초록불로 성공했다

## Failure repair — 못 끝낼 때

채울 수 없는 항목은 `[미확인: 이유]`로 표시하고 그 부분만 비워둔 채 나머지를 진행한다. 예: 데이터 원천의 인증 방식을 모르면 `[미확인: API 인증 방식]`이라고 collect.py에 남기고, 사용자에게 확인을 요청한 뒤 멈춘다. 모르는 상태로 인증 로직을 지어내지 않는다.

자주 재발하는 실패와 조치:

- **push 거부 (non-fast-forward)**: update.yml의 커밋&푸시 단계를 `git push` 실패 시 `git fetch origin main && git rebase origin/main && git push`로 재시도하도록 바꾼다.
- **GitHub Pages 404**: `docs/.nojekyll` 빈 파일 누락이 원인. 추가한다.
- **JSON 파싱 오류**: `data.json`의 `//` 주석이 원인. 제거하거나 `"_comment"` 키로 바꾼다.
- **예약 실행이 그 회차만 건너뛰어짐**: `cron` 분이 0인지 먼저 확인(Judgment 제약 2). 분을 옮겨도 며칠씩 안 도는 경우가 실제로 있었다 — GitHub `schedule` 트리거 자체가 개인 계정 저장소에서 신뢰도가 낮은 편이라, 근본 해결은 `references/github-setup.md`의 외부 스케줄러(cron-job.org) 연결 절차를 따른다.
- **페이지네이션에서 옛 항목이 통째로 딸려옴**: Judgment 제약 3의 안전장치 누락이 원인. `assets/templates/collect_template.py`의 `fetch_raw_data` 패턴대로 고친다.
