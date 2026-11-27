Param(
    [switch]$SkipSecurity
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host "`n==> $Name" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Name failed (exit code: $LASTEXITCODE)" }
    Write-Host "OK: $Name" -ForegroundColor Green
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"

Invoke-Step -Name "Compose config (static validation)" -Action {
    Push-Location $repoRoot
    try { docker compose config }
    finally { Pop-Location }
}

Invoke-Step -Name "Backend tests" -Action {
    Push-Location $backendDir
    try { python -m pytest -q }
    finally { Pop-Location }
}

Invoke-Step -Name "Frontend tests" -Action {
    Push-Location $frontendDir
    try { php vendor/bin/phpunit }
    finally { Pop-Location }
}

if (-not $SkipSecurity) {
    Invoke-Step -Name "Dependency audit (advisory)" -Action {
        Push-Location $backendDir
        try { pip install pip-audit 2>&1 | Out-Null; python -m pip_audit -r requirements.txt 2>&1 | Select-Object -First 10 }
        finally { Pop-Location }
    }
}

Invoke-Step -Name "Post-deploy SLO check (local stack)" -Action {
    Push-Location $repoRoot
    try { python scripts/slo_check.py --base-url http://127.0.0.1:8080 }
    finally { Pop-Location }
}

Write-Host "`nRepository quality checks completed." -ForegroundColor Green
