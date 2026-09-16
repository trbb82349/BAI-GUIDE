# setup.ps1 — vibe-workspace 초기 설정 (Windows)
# ZIP으로 받은 경우 처음 한 번만 실행합니다.
# 실행 방법: PowerShell에서 .\scripts\setup.ps1
#
# 만약 "이 시스템에서 스크립트를 실행할 수 없습니다" 오류가 뜨면
# 아래 명령을 PowerShell에서 한 번만 실행한 뒤 다시 시도하세요.
#     Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Set-Location $root

Write-Host ""
Write-Host "Starting vibe-workspace setup." -ForegroundColor Cyan
Write-Host ""

# [1/2] Git 저장소 확인 및 초기화
$isGitRepository = $false
try {
    $gitCheck = git rev-parse --is-inside-work-tree 2>$null
    $isGitRepository = ($LASTEXITCODE -eq 0 -and $gitCheck -eq "true")
} catch {
    $isGitRepository = $false
}

if (-not $isGitRepository) {
    Write-Host "[1/2] Initializing Git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: git init failed. Please check that Git is installed." -ForegroundColor Red
        exit 1
    }
    Write-Host "      Done: Git repository created." -ForegroundColor Green
} else {
    Write-Host "[1/2] Git repository already exists. Skipping." -ForegroundColor Green
}

# [2/2] pre-commit 훅 등록
Write-Host "[2/2] Registering security hook (.githooks)..." -ForegroundColor Yellow
git config core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: git config failed." -ForegroundColor Red
    exit 1
}
Write-Host "      Done: pre-commit API key check is enabled." -ForegroundColor Green

Write-Host ""
Write-Host "Setup complete. Now tell Codex:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  /start" -ForegroundColor White
Write-Host ""
