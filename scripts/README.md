# scripts

완성된 단일 자동화 스크립트와 워크스페이스 초기 설정 스크립트가 저장되는 폴더입니다.

## 초기 설정 스크립트

처음 한 번만 실행합니다. Git 저장소 초기화와 커밋 보안 훅을 등록합니다.

| 파일 | 대상 | 실행 방법 |
|---|---|---|
| `setup.ps1` | Windows | PowerShell에서 `.\scripts\setup.ps1` |
| `setup.sh` | Mac / Linux | 터미널에서 `bash scripts/setup.sh` |

Windows에서 `이 시스템에서 스크립트를 실행할 수 없습니다` 오류가 뜨면:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 유틸리티

| 파일 | 설명 |
|---|---|
| `find-python.ps1` | Windows에서 Python 설치 경로를 자동으로 탐색하고 `.codex/local-python.json`에 저장 |
| `bai_feed_config.py` | `/goodbai`용 BAI 피드 API key를 로컬 설정 파일에 저장 |
| `bai_feed_save.py` | `/goodbai` payload를 dry-run하거나 BAI 피드 API로 전송 |

## BAI 피드 설정

`/goodbai`를 쓰려면 학생이 처음 한 번만 선생님에게 받은 API key를 저장합니다. PowerShell에서는 먼저 워크스페이스 폴더로 이동합니다.

```powershell
cd "워크스페이스를 내려받은 폴더 경로"
python scripts\bai_feed_config.py
```

`BAI feed name`은 PowerShell 화면에 보입니다. `BAI feed API key`는 비밀번호처럼 숨겨져서 붙여넣어도 보이지 않습니다. 붙여넣고 Enter를 누르면 정상 입력됩니다.

이미 잘못된 값이 저장되어 다시 설정해야 할 때는 기존 설정을 덮어씁니다.

```powershell
cd "워크스페이스를 내려받은 폴더 경로"
python scripts\bai_feed_config.py --force
```

저장된 `.bai-feed.env`는 Git에 올라가지 않습니다. 여러 워크스페이스를 쓰는 경우 워크스페이스의 `.bai-feed.env`가 사용자 홈의 기본 설정보다 우선합니다.

## 바로 쓰는 템플릿

`/start`가 처음 추천하는 작은 작업 3개입니다. 그대로 실행하거나 복사해서 변형합니다.

| 파일 | 용도 | 기본 입력 | 결과 |
|---|---|---|---|
| `download-organize.py` | 다운로드 폴더 파일을 종류별로 분류 | `~/Downloads` | 분류된 하위 폴더 생성 |
| `notes-to-summary.py` | 여러 마크다운 메모를 하나로 합침 | `00-inbox/ideas/` | `10-projects/summary-output/output/summary.md` |
| `file-rename-dated.py` | 파일명 앞에 오늘 날짜 일괄 추가 | 현재 폴더 | 같은 폴더에서 in-place |
| `remove-background.py` | 사진 폴더의 배경을 지워 투명 PNG(누끼)로 저장 | 지정한 폴더 (기본: 현재 폴더) | `입력폴더/누끼-결과/*.png` |

실행 방법은 각 파일 상단 docstring을 참고합니다. `remove-background.py`는 처음 실행 전 `pip install rembg pillow` 설치가 필요합니다.

## 내 자동화 스크립트

여러 파일로 된 작업은 `10-projects/` 폴더에, 한 파일로 완성되는 스크립트는 이 폴더에 저장합니다.

예: `organize-downloads.py`, `rename-files.py`
