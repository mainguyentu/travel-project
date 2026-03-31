Param(
    [switch]$SkipSecurity
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit code: $LASTEXITCODE)"
    }
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host "`n==> $Name" -ForegroundColor Cyan
    & $Action
    Write-Host "OK: $Name" -ForegroundColor Green
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"

Invoke-Step -Name "Backend tests with coverage gate" -Action {
    Push-Location $backendDir
    try {
        Invoke-CheckedCommand -Command { python -m pip install --upgrade pip } -FailureMessage "Failed to upgrade pip"
        Invoke-CheckedCommand -Command { pip install -r requirements.txt } -FailureMessage "Failed to install backend dependencies"
        Invoke-CheckedCommand -Command { pytest tests -q --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=70 } -FailureMessage "Backend tests failed"
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Frontend build and tests" -Action {
    Push-Location $frontendDir
    try {
        & npm ci
        if ($LASTEXITCODE -ne 0) {
            Write-Host "npm ci failed, retrying once after 3 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            Invoke-CheckedCommand -Command { npm ci } -FailureMessage "Failed to install frontend npm dependencies"
        }

        Invoke-CheckedCommand -Command { npm run build } -FailureMessage "Frontend build failed"
        Invoke-CheckedCommand -Command { composer install --no-interaction --prefer-dist --no-progress } -FailureMessage "Failed to install frontend composer dependencies"
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
        }
        Invoke-CheckedCommand -Command { php artisan key:generate --force } -FailureMessage "Failed to generate Laravel app key"
        Invoke-CheckedCommand -Command { vendor/bin/phpunit --configuration phpunit.xml --coverage-clover build/logs/clover.xml } -FailureMessage "Frontend tests failed"
    }
    finally {
        Pop-Location
    }
}

if (-not $SkipSecurity) {
    Invoke-Step -Name "Dependency and image security scan" -Action {
        $reportDir = Join-Path $repoRoot "security-reports"
        if (-not (Test-Path $reportDir)) {
            New-Item -Path $reportDir -ItemType Directory | Out-Null
        }

        Invoke-CheckedCommand -Command { pip install pip-audit } -FailureMessage "Failed to install pip-audit"
        Invoke-CheckedCommand -Command { pip-audit -r (Join-Path $backendDir "requirements.txt") -f json -o (Join-Path $reportDir "pip-audit.json") } -FailureMessage "pip-audit scan failed"

        Push-Location $frontendDir
        try {
            Invoke-CheckedCommand -Command { composer audit --format=json | Out-File -FilePath (Join-Path $reportDir "composer-audit.json") -Encoding utf8 } -FailureMessage "composer audit failed"
            Invoke-CheckedCommand -Command { npm audit --json | Out-File -FilePath (Join-Path $reportDir "npm-audit.json") -Encoding utf8 } -FailureMessage "npm audit failed"
        }
        finally {
            Pop-Location
        }

        Invoke-CheckedCommand -Command { docker build -t travel-project-backend-local-scan:latest $backendDir } -FailureMessage "Backend image build for security scan failed"
    }
}

Write-Host "`nRepository quality checks completed." -ForegroundColor Green