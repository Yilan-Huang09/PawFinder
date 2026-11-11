#requires -Version 5.1
[CmdletBinding()]
param(
  [string]$DatabaseUrl = '',
  [int]$ApiPort = 5000,
  [int]$WebPort = 5173
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $projectRoot '.venv\Scripts\python.exe'))) { throw 'Missing .venv. Run scripts/setup.ps1 first.' }
if ($ApiPort -ne 5000) { throw 'backend/run.py currently uses port 5000. Keep ApiPort set to 5000.' }

$previousDatabaseUrl = $env:DATABASE_URL
if ($DatabaseUrl) { $env:DATABASE_URL = $DatabaseUrl }
try {
  $api = Start-Process -FilePath (Join-Path $projectRoot '.venv\Scripts\python.exe') -ArgumentList 'backend/run.py' -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
  $web = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev','--','--host','127.0.0.1','--port',"$WebPort" -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru
} finally {
  $env:DATABASE_URL = $previousDatabaseUrl
}

Write-Host "API: http://127.0.0.1:$ApiPort  PID=$($api.Id)"
Write-Host "Web: http://127.0.0.1:$WebPort  PID=$($web.Id)"
Write-Host "Stop services with: Stop-Process -Id $($api.Id),$($web.Id)"
