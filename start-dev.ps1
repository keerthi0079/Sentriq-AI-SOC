# Sentriq AI-SOC Development Launcher
$Root = $PSScriptRoot
if (-not $Root) { $Root = Get-Location }

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     SENTRIQ AI-SOC DEVELOPMENT RUNNER   " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Verify and start Docker Desktop PostgreSQL
Write-Host "`n[1/3] Ensuring Docker Desktop PostgreSQL is active..." -ForegroundColor Yellow
Set-Location -Path $Root
docker compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker Desktop is not running or failed to start database." -ForegroundColor Red
    exit 1
}
Write-Host "PostgreSQL container is active on port 5432." -ForegroundColor Green

# 2. Check and start Backend API
Write-Host "`n[2/3] Starting Sentriq FastAPI Backend on port 8000..." -ForegroundColor Yellow
$BackendDir = Join-Path $Root "backend"
$UvicornExe = Join-Path $BackendDir ".venv\Scripts\uvicorn.exe"

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "Backend is already running on port 8000 (PID: $($port8000.OwningProcess[0]))." -ForegroundColor Green
} else {
    $BackendProcess = Start-Process -FilePath $UvicornExe -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $BackendDir -WindowStyle Hidden -PassThru
    Write-Host "Backend started with Process ID: $($BackendProcess.Id)" -ForegroundColor Green
}
Write-Host "Interactive Swagger Documentation: http://localhost:8000/docs" -ForegroundColor Cyan

# 3. Check and start Frontend Dashboard
Write-Host "`n[3/3] Starting Sentriq React + Vite Frontend on port 5173..." -ForegroundColor Yellow
$FrontendDir = Join-Path $Root "frontend"

$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Write-Host "Frontend is already running on port 5173 (PID: $($port5173.OwningProcess[0]))." -ForegroundColor Green
} else {
    $FrontendProcess = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173" -WorkingDirectory $FrontendDir -WindowStyle Hidden -PassThru
    Write-Host "Frontend started with Process ID: $($FrontendProcess.Id)" -ForegroundColor Green
}
Write-Host "SOC Dashboard UI: http://localhost:5173" -ForegroundColor Cyan

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host " Sentriq AI-SOC is running successfully! " -ForegroundColor Green
Write-Host " Dashboard: http://localhost:5173        " -ForegroundColor White
Write-Host " Backend API: http://localhost:8000/docs " -ForegroundColor White
Write-Host " Database: PostgreSQL 16 on Docker:5432 " -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Green
