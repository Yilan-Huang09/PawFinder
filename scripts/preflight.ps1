#requires -Version 5.1
[CmdletBinding()]
param(
  [switch]$SkipBackend,
  [switch]$SkipFrontend
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$requiredFiles = @(
  'README.md',
  '.env.example',
  'docker-compose.yml',
  'database/schema.sql',
  'database/objects.sql',
  'database/seed.sql',
  'database/bootstrap.sql',
  'docs/er-diagram.drawio',
  'docs/data-dictionary.md',
  'docs/demo-script.md',
  'docs/video-checklist.md'
)

foreach ($file in $requiredFiles) {
  if (-not (Test-Path -LiteralPath $file)) {
    throw "Missing required deliverable: $file"
  }
}
Write-Host 'Required delivery files: OK' -ForegroundColor Green

if (-not $SkipBackend) {
  $pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
  if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Missing .venv. Run scripts/setup.ps1 first, or use -SkipBackend.'
  }
  $previousTemp = $env:TEMP
  $previousTmp = $env:TMP
  $pytestTemp = Join-Path $projectRoot '.tmp\pytest'
  New-Item -ItemType Directory -Force -Path $pytestTemp | Out-Null
  try {
    $env:TEMP = $pytestTemp
    $env:TMP = $pytestTemp
    & $pythonPath -m pytest backend/tests -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
  } finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
  }
}

if (-not $SkipFrontend) {
  if (-not (Test-Path -LiteralPath 'frontend\node_modules')) {
    throw 'Missing frontend dependencies. Run npm install --prefix frontend, or use -SkipFrontend.'
  }
  $previousTemp = $env:TEMP
  $previousTmp = $env:TMP
  $frontendTemp = Join-Path $projectRoot '.tmp\frontend'
  New-Item -ItemType Directory -Force -Path $frontendTemp | Out-Null
  try {
    $env:TEMP = $frontendTemp
    $env:TMP = $frontendTemp
    & npm test --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
    & npm run build --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'Frontend production build failed.' }
  } finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
  }
}

Write-Host 'PawFinder preflight checks passed.' -ForegroundColor Green
