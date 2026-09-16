#!/usr/bin/env python3
"""
커밋 보안 검사 — API 키 / 비밀번호 자동 차단
"""
import subprocess
import re
import sys


def run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout or ""


def check_env_files():
    staged = run("git diff --cached --name-only")
    env_files = [
        f for f in staged.splitlines()
        if re.match(r"^\.env", f) and f != ".env.example"
    ]
    if env_files:
        print()
        print("[위험] .env 파일을 커밋하려고 해요!")
        print()
        for f in env_files:
            print(f"   파일: {f}")
        print()
        print("[차단] 커밋이 차단됐습니다.")
        print("[도움말] .env 파일에는 API 키가 들어있어요. 절대 GitHub에 올리면 안 됩니다.")
        print("   .gitignore에 .env가 포함되어 있는지 확인하세요.")
        print()
        sys.exit(1)


def check_api_patterns():
    diff = run("git diff --cached -U0")
    added = []
    current_file = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if line.startswith("+++ "):
            current_file = None
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added.append((current_file or "(unknown)", line[1:]))

    patterns = [
        (r"sk-ant-[A-Za-z0-9_-]{10,}", "Anthropic API 키"),
        (r"sk-proj-[A-Za-z0-9_-]{10,}", "OpenAI 프로젝트 API 키"),
        (r"sk-[A-Za-z0-9_-]{32,}", "OpenAI 형식 API 키"),
        (r"AIza[A-Za-z0-9_-]{35}", "Google API 키"),
        (r"(OPENAI|ANTHROPIC|GEMINI)_API_KEY\s*=\s*['\"]?[^'\"\s#]+", "API 키 환경변수 할당"),
        (r"openai\.api_key\s*=\s*['\"][^'\"]+", "OpenAI API 키 직접 할당"),
        (r"(password|secret|token)\s*=\s*['\"][^'\"]{6,}", "민감정보 하드코딩"),
    ]

    findings = []
    for pattern, label in patterns:
        hits = [
            file_path for file_path, line in added
            if file_path != ".githooks/pre-commit.py"
            and re.search(pattern, line, re.IGNORECASE)
            and not line.lstrip().startswith("#")
        ]
        if hits:
            findings.append((label, sorted(set(hits))))

    if findings:
        print()
        print("[위험] 민감정보로 보이는 값이 발견됐어요!")
        print()
        for label, files in findings:
            print(f"   종류: {label}")
            for file_path in files[:5]:
                print(f"      파일: {file_path}")
            if len(files) > 5:
                print(f"      외 {len(files) - 5}개 파일")
        print()
        print("[차단] 커밋이 차단됐습니다.")
        print("[도움말] 실제 값은 출력하지 않았어요. 해당 파일에서 값을 제거하거나 .env로 옮기세요.")
        sys.exit(1)


print("[확인] 보안 검사 중...")
check_env_files()
check_api_patterns()
print("[통과] 보안 검사 통과! 커밋을 진행합니다.")
sys.exit(0)
