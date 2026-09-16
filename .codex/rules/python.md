# python.md — Windows Python 탐지 규칙

## 핵심 원칙

Python은 워크스페이스 폴더 안에 설치되어 있지 않아도 정상입니다. 대부분은 `C:\ProgramData\anaconda3`, 사용자 홈의 `anaconda3`, `miniconda3`, `AppData`, conda, 또는 Python Launcher를 통해 실행됩니다.

Codex는 `python --version` 하나만 실패했다고 Python이 없다고 말하지 않습니다.

## 확인 순서

Python이 필요하면 아래 순서로 확인합니다.

1. `.codex/local-python.json`이 있으면 먼저 읽고, 저장된 경로가 아직 실행되는지 확인
2. `py -0p`로 Python Launcher에 등록된 Python 확인
3. `python --version` 확인
4. `where python` 확인
5. `where conda` 확인 후 conda 설치 폴더의 `python.exe` 확인
6. 흔한 설치 경로 확인

   Windows:
   - `C:\ProgramData\anaconda3\python.exe`
   - `%USERPROFILE%\anaconda3\python.exe`
   - `%USERPROFILE%\miniconda3\python.exe`
   - `%LOCALAPPDATA%\anaconda3\python.exe`
   - `%LOCALAPPDATA%\miniconda3\python.exe`
   - `%LOCALAPPDATA%\Programs\Python\Python*\python.exe`
   - `%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe`

   Mac / Linux:
   - `~/anaconda3/bin/python`
   - `~/miniconda3/bin/python`
   - `/opt/homebrew/bin/python3` (Apple Silicon Mac)
   - `/usr/local/bin/python3` (Intel Mac, Homebrew)
   - `/usr/bin/python3` (시스템 기본)

## 찾았을 때

실제로 실행되는 경로를 찾으면 아래 파일에 저장합니다.

```text
.codex/local-python.json
```

예:

```json
{
  "python": "C:\\ProgramData\\anaconda3\\python.exe",
  "checked_at": "YYYY-MM-DD",
  "note": "Local machine setting. Do not commit this file."
}
```

이후 Python 스크립트를 실행할 때는 저장된 경로를 우선 사용합니다.

## 못 찾았을 때

위 순서를 모두 확인한 뒤에만 Python 설치가 필요하다고 말합니다.

설치 안내를 할 때도 먼저 이렇게 말합니다.

```text
이 PC에서 실행 가능한 Python을 찾지 못했어요. Python 또는 Anaconda를 설치해야 합니다.
```

## 금지

- 워크스페이스 폴더 안에 `python.exe`가 없다는 이유로 Python이 없다고 말하지 않습니다.
- `python --version` 실패만으로 설치를 권하지 않습니다.
- Microsoft Store용 `WindowsApps\python.exe`가 실제 실행 가능한 Python인지 확인하지 않고 사용하지 않습니다.
