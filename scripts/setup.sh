#!/bin/bash
# setup.sh — vibe-workspace 초기 설정 (Mac / Linux)
# ZIP으로 받은 경우 처음 한 번만 실행합니다.
# 실행 방법: bash scripts/setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo ""
echo "vibe-workspace 초기 설정을 시작합니다."
echo ""

# [1/3] Git 저장소 확인 및 초기화
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "[1/3] Git 저장소가 이미 있습니다. 건너뜁니다."
else
    echo "[1/3] Git 저장소를 초기화합니다..."
    git init
    echo "      완료: Git 저장소가 생성됐습니다."
fi

# [2/3] pre-commit 훅 실행 권한 부여
echo "[2/3] .githooks/pre-commit 실행 권한을 설정합니다..."
chmod +x .githooks/pre-commit
echo "      완료."

# [3/3] pre-commit 훅 등록
echo "[3/3] 보안 훅(.githooks)을 등록합니다..."
git config core.hooksPath .githooks
echo "      완료: 커밋 전 API 키 자동 검사가 활성화됐습니다."

echo ""
echo "설정 완료! 이제 Codex에게 이렇게 말해보세요:"
echo ""
echo "  /start"
echo ""
