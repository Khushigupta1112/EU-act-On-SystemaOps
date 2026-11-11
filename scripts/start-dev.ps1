# =============================================================================
# SystemaOps AI Compliance Platform — Development Startup Script (Windows PowerShell)
# =============================================================================
# Usage: .\scripts\start-dev.ps1 [-NoMigrate] [-Rebuild]
#
# Parameters:
#   -NoMigrate   Skip running Alembic database migrations
#   -Rebuild     Force rebuild of Docker images before starting
# =============================================================================

param(
    [switch]$NoMigrate,
    [switch]$Rebuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─── Colours helper ──────────────────────────────────────────────────────────
function Write-Color {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Cyan -NoNewline
    Write-Host ""
}

function Write-Success { param([string]$Msg) Write-Host "  ✓ $Msg" -ForegroundColor Green }
function Write-Warn    { param([string]$Msg) Write-Host "  ⚠ $Msg" -ForegroundColor Yellow }
function Write-Fail    { param([string]$Msg) Write-Host "  ✗ $Msg" -ForegroundColor Red }

# ─── Banner ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║     SystemaOps AI Compliance Platform          ║" -ForegroundColor Cyan
Write-Host "  ║     Development Environment Startup            ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─── Locate repo root ────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir   = Split-Path -Parent $ScriptDir
Set-Location $RootDir

# ─── Step 1: Check prerequisites ─────────────────────────────────────────────
Write-Step "1/6" "Checking prerequisites..."

function Test-Command {
    param([string]$Cmd, [string]$InstallHint)
    $found = Get-Command $Cmd -ErrorAction SilentlyContinue
    if (-not $found) {
        Write-Fail "'$Cmd' not found. Install from: $InstallHint"
        exit 1
    }
    Write-Success "$Cmd found at $($found.Source)"
}

Test-Command "docker" "https://docs.docker.com/get-docker/"

# Determine docker compose command (v2 plugin vs standalone)
$DockerCompose = $null
try {
    docker compose version 2>&1 | Out-Null
    $DockerCompose = @("docker", "compose")
    Write-Success "docker compose (v2 plugin) available"
} catch {
    $dc = Get-Command "docker-compose" -ErrorAction SilentlyContinue
    if ($dc) {
        $DockerCompose = @("docker-compose")
        Write-Success "docker-compose (v1 standalone) available"
    } else {
        Write-Fail "Neither 'docker compose' nor 'docker-compose' found."
        Write-Fail "Install Docker Desktop: https://docs.docker.com/desktop/windows/"
        exit 1
    }
}

# Node — optional (frontend local dev)
$nodeCmd = Get-Command "node" -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVer = & node --version
    Write-Success "node $nodeVer"
} else {
    Write-Warn "node not found (only needed for local frontend dev outside Docker)"
}

# Python — optional (backend local dev)
$pyCmd = Get-Command "python" -ErrorAction SilentlyContinue
if ($pyCmd) {
    $pyVer = & python --version 2>&1
    Write-Success "$pyVer"
} else {
    Write-Warn "python not found (only needed for local backend dev outside Docker)"
}

# ─── Step 2: Copy .env if not exists ─────────────────────────────────────────
Write-Step "2/6" "Configuring environment..."

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success ".env created from .env.example"
    Write-Warn "Review .env and update secrets (SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD) before continuing."
    Start-Sleep -Seconds 3
} else {
    Write-Success ".env already exists"
}

# ─── Step 3: Build / Start Docker Compose ────────────────────────────────────
Write-Step "3/6" "Starting Docker services..."

if ($Rebuild) {
    Write-Host "  Rebuilding images (-Rebuild flag)..." -ForegroundColor Blue
    & $DockerCompose[0] $DockerCompose[1..($DockerCompose.Length-1)] build --no-cache
    if ($LASTEXITCODE -ne 0) { Write-Fail "Image build failed"; exit 1 }
}

& $DockerCompose[0] $DockerCompose[1..($DockerCompose.Length-1)] up -d --remove-orphans
if ($LASTEXITCODE -ne 0) { Write-Fail "docker compose up failed"; exit 1 }

Write-Success "Docker services started"

# ─── Step 4: Wait for health checks ──────────────────────────────────────────
Write-Step "4/6" "Waiting for services to be healthy..."

function Wait-Healthy {
    param([string]$Service, [int]$MaxAttempts = 30)

    Write-Host "  Waiting for $($Service.PadRight(20))" -NoNewline

    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        try {
            $id = (& $DockerCompose[0] $DockerCompose[1..($DockerCompose.Length-1)] ps -q $Service 2>$null)
            if ($id) {
                $status = (docker inspect --format='{{.State.Health.Status}}' $id 2>$null)
                if ($status -eq "healthy") {
                    Write-Host " healthy" -ForegroundColor Green
                    return
                }
            }
        } catch {}
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }

    Write-Host " TIMEOUT" -ForegroundColor Red
    Write-Fail "Service '$Service' did not become healthy in time."
    Write-Warn "Check logs: docker compose logs $Service"
    exit 1
}

Wait-Healthy "postgres" 30
Wait-Healthy "redis" 15

# ─── Step 5: Run Alembic migrations ──────────────────────────────────────────
if (-not $NoMigrate) {
    Write-Step "5/6" "Running database migrations..."
    & $DockerCompose[0] $DockerCompose[1..($DockerCompose.Length-1)] exec -T backend alembic upgrade head
    if ($LASTEXITCODE -ne 0) { Write-Fail "Migrations failed"; exit 1 }
    Write-Success "Migrations applied"
} else {
    Write-Step "5/6" "Skipping migrations (-NoMigrate)"
}

# ─── Step 6: Print startup summary ───────────────────────────────────────────
Write-Host ""
Write-Host "  [6/6] SystemaOps is ready!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "  │  Service URLs                               │" -ForegroundColor Cyan
Write-Host "  ├─────────────────────────────────────────────┤" -ForegroundColor Cyan
Write-Host "  │  Frontend    →  http://localhost:3000        │" -ForegroundColor Cyan
Write-Host "  │  Backend API →  http://localhost:8000        │" -ForegroundColor Cyan
Write-Host "  │  API Docs    →  http://localhost:8000/docs   │" -ForegroundColor Cyan
Write-Host "  │  Adminer     →  http://localhost:8080        │" -ForegroundColor Cyan
Write-Host "  └─────────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Useful commands:" -ForegroundColor White
Write-Host "    make logs           # Follow all service logs"
Write-Host "    make logs-backend   # Follow backend logs only"
Write-Host "    make migrate        # Re-run migrations"
Write-Host "    make test-backend   # Run backend test suite"
Write-Host "    make stop           # Stop all services"
Write-Host ""
