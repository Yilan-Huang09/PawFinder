#requires -Version 5.1
[CmdletBinding()]
param(
  [string]$DatabaseUrl = '',
  [int]$ApiPort = 5000,
  [int]$WebPort = 5173
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$vitePath = Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'
if (-not (Test-Path $pythonPath)) { throw 'Missing .venv. Run scripts/setup.ps1 first.' }
if (-not (Test-Path $vitePath)) { throw 'Missing frontend dependencies. Run scripts/setup.ps1 first.' }
if ($ApiPort -ne 5000) { throw 'backend/run.py currently uses port 5000. Keep ApiPort set to 5000.' }

$previousDatabaseUrl = $env:DATABASE_URL
$previousFlaskDebug = $env:FLASK_DEBUG
if ($DatabaseUrl) { $env:DATABASE_URL = $DatabaseUrl }
$env:FLASK_DEBUG = '0'
try {
  $api = Start-Process -FilePath $pythonPath -ArgumentList 'backend/run.py' -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
  $web = Start-Process -FilePath (Get-Command node.exe).Source -ArgumentList $vitePath,'--host','127.0.0.1','--port',"$WebPort",'--force' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru
} finally {
  $env:DATABASE_URL = $previousDatabaseUrl
  $env:FLASK_DEBUG = $previousFlaskDebug
}

Write-Host "API: http://127.0.0.1:$ApiPort  PID=$($api.Id)"
Write-Host "Web: http://127.0.0.1:$WebPort  PID=$($web.Id)"
Write-Host "Stop services with: Stop-Process -Id $($api.Id),$($web.Id)"
