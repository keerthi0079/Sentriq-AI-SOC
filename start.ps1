# ==============================================================================
# Sentriq AI-SOC: Autonomous AI Security Operations Center
# Windows Master Startup Script (PRD Phase 8)
# ==============================================================================

param (
    [switch]$Docker,
    [switch]$Dev,
    [switch]$Seed
)

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "         SENTRIQ: AUTONOMOUS AI-POWERED SECURITY SOC              " -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " [PRD Phase 8]: Production Multi-Container & Local Dev Launcher   " -ForegroundColor DarkGray
Write-Host ""

# Check Docker status
Write-Host "[*] Checking Docker Desktop Engine..." -ForegroundColor Yellow
$dockerProcess = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker is not running or not found in PATH." -ForegroundColor Red
    Write-Host "    Please ensure Docker Desktop is running before launching containerized services." -ForegroundColor DarkYellow
} else {
    Write-Host "[+] Docker Desktop is active and ready." -ForegroundColor Green
}

if ($Docker) {
    Write-Host ""
    Write-Host "[*] Starting Full Multi-Container Stack (DB + Backend + Frontend)..." -ForegroundColor Cyan
    docker compose up --build -d
    Write-Host ""
    Write-Host "[+] Sentriq is deployed on Docker Desktop!" -ForegroundColor Green
    Write-Host "    Frontend Dashboard: http://localhost:80 (or http://localhost:5173)" -ForegroundColor White
    Write-Host "    FastAPI Backend:    http://localhost:8000" -ForegroundColor White
    Write-Host "    API Documentation:  http://localhost:8000/docs" -ForegroundColor White
    exit 0
}

# Default / Dev Mode: Check PostgreSQL on Docker
Write-Host "[*] Ensuring PostgreSQL 16 container is running on port 5432..." -ForegroundColor Yellow
docker compose up -d db
Start-Sleep -Seconds 2

# Seed demonstration data if requested
if ($Seed) {
    Write-Host "[*] Ingesting authentic UNSW-NB15 benchmark and Section 12 scenarios..." -ForegroundColor Yellow
    $env:PYTHONPATH = "."
    Set-Location -Path "backend"
    .venv\Scripts\python scripts\seed_data.py --simulate-scenario brute_force --seed-benchmark
    Set-Location -Path ".."
    Write-Host "[+] Database seeded successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "             SENTRIQ AI-SOC SERVICES RUNNING                      " -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  Frontend Web UI:   http://localhost:5173" -ForegroundColor White
Write-Host "  FastAPI REST API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Docker DB:         localhost:5432 (sentriq_soc)" -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tip: Run 'powershell .\start.ps1 -Docker' to build and run in full container mode." -ForegroundColor DarkGray
Write-Host ""

