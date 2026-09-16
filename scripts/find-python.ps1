param()

$ErrorActionPreference = "SilentlyContinue"

$candidates = New-Object System.Collections.Generic.List[string]

function Add-Candidate($Path) {
    if ($Path -and (Test-Path -LiteralPath $Path)) {
        $resolved = (Resolve-Path -LiteralPath $Path).Path
        if (-not $candidates.Contains($resolved)) {
            $candidates.Add($resolved)
        }
    }
}

$localConfig = Join-Path (Get-Location) ".codex\local-python.json"
if (Test-Path -LiteralPath $localConfig) {
    $saved = Get-Content -LiteralPath $localConfig -Encoding UTF8 | ConvertFrom-Json
    Add-Candidate $saved.python
}

$pyList = py -0p 2>$null
if ($LASTEXITCODE -eq 0 -and $pyList) {
    foreach ($line in $pyList) {
        if ($line -match "([A-Z]:\\.*python\.exe)") {
            Add-Candidate $Matches[1]
        }
    }
}

$wherePython = where.exe python 2>$null
if ($LASTEXITCODE -eq 0 -and $wherePython) {
    foreach ($path in $wherePython) {
        Add-Candidate $path
    }
}

$whereConda = where.exe conda 2>$null
if ($LASTEXITCODE -eq 0 -and $whereConda) {
    foreach ($path in $whereConda) {
        $condaDir = Split-Path -Parent $path
        $baseDir = Split-Path -Parent $condaDir
        Add-Candidate (Join-Path $baseDir "python.exe")
    }
}

Add-Candidate "C:\ProgramData\anaconda3\python.exe"
Add-Candidate (Join-Path $env:USERPROFILE "anaconda3\python.exe")
Add-Candidate (Join-Path $env:USERPROFILE "miniconda3\python.exe")
Add-Candidate (Join-Path $env:LOCALAPPDATA "anaconda3\python.exe")
Add-Candidate (Join-Path $env:LOCALAPPDATA "miniconda3\python.exe")

$localPrograms = Join-Path $env:LOCALAPPDATA "Programs\Python"
if (Test-Path -LiteralPath $localPrograms) {
    Get-ChildItem -LiteralPath $localPrograms -Filter python.exe -Recurse | ForEach-Object {
        Add-Candidate $_.FullName
    }
}

foreach ($candidate in $candidates) {
    $version = & $candidate --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $version -match "Python") {
        $out = [PSCustomObject]@{
            python = $candidate
            version = ($version -join " ")
            checked_at = (Get-Date -Format "yyyy-MM-dd")
            note = "Local machine setting. Do not commit this file."
        }

        $configDir = Join-Path (Get-Location) ".codex"
        if (-not (Test-Path -LiteralPath $configDir)) {
            New-Item -ItemType Directory -Path $configDir | Out-Null
        }

        $out | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $configDir "local-python.json") -Encoding UTF8
        $out | ConvertTo-Json -Depth 3
        exit 0
    }
}

Write-Output "No runnable Python found."
exit 1
