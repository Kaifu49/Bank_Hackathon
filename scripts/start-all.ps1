# start-all.ps1 — launch the full FinIntel stack (Windows / PowerShell)
#
#   Usage:   ./scripts/start-all.ps1
#   Opens one window per Python ML service + the Rust gateway.
#   Assumes: PostgreSQL running, conda env 'finintel', migrations applied.
#
# If `conda activate` fails in the child windows, run `conda init powershell`
# once, restart the terminal, then re-run this script. Override the env with
# -CondaEnv, or the graph/report deps note: `pip install reportlab` for PDF.

param(
    [string]$CondaEnv = "finintel"
)

$root = Split-Path -Parent $PSScriptRoot
$ml   = Join-Path $root "ml-services"

$services = @(
    @{ name = "ocr";         port = 8001 },
    @{ name = "standardize"; port = 8002 },
    @{ name = "entity";      port = 8003 },
    @{ name = "validation";  port = 8004 },
    @{ name = "graph";       port = 8005 },
    @{ name = "anomaly";     port = 8007 },
    @{ name = "temporal";    port = 8008 },
    @{ name = "trail";       port = 8009 },
    @{ name = "report";      port = 8010 }
)

Write-Host "Launching FinIntel services (conda env: $CondaEnv)..." -ForegroundColor Cyan

foreach ($s in $services) {
    $dir = Join-Path $ml $s.name
    $cmd = "cd '$dir'; conda activate $CondaEnv; uvicorn main:app --port $($s.port)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd | Out-Null
    Write-Host ("  {0,-12} -> http://localhost:{1}" -f $s.name, $s.port)
    Start-Sleep -Milliseconds 500
}

# Rust API gateway
$backend = Join-Path $root "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backend'; cargo run" | Out-Null
Write-Host "  backend      -> http://localhost:8080" -ForegroundColor Green

Write-Host ""
Write-Host "Swagger UI:      http://localhost:8080/docs"       -ForegroundColor Yellow
Write-Host "Services health: http://localhost:8080/services/health"
