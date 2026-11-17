#requires -Version 5.1
[CmdletBinding()]
param(
  [string]$MySqlHost = '127.0.0.1',
  [int]$MySqlPort = 3306,
  [string]$MySqlUser = 'root',
  [switch]$Seed,
  [switch]$SkipDependencies,
  [switch]$EmptyPassword
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path '.env')) {
  Copy-Item '.env.example' '.env'
  Write-Host 'Created .env. Review the database URL and JWT secret before starting.' -ForegroundColor Yellow
}

if (-not $SkipDependencies) {
  if (-not (Test-Path '.venv')) { python -m venv .venv }
  & (Join-Path $projectRoot '.venv\Scripts\python.exe') -m pip install -r backend/requirements-dev.txt
  npm install --prefix frontend
  npm install
}

if ($EmptyPassword) {
  $credential = $null
  $plainPassword = ''
} else {
  $securePassword = Read-Host "MySQL password for $MySqlUser (press Enter for an empty password)" -AsSecureString
  $credential = New-Object System.Net.NetworkCredential('', $securePassword)
  $plainPassword = $credential.Password
}

function Invoke-MySqlFile([string]$path) {
  Write-Host "Running $path"
  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = 'mysql'
  $startInfo.Arguments = "--host=$MySqlHost --port=$MySqlPort --user=$MySqlUser --default-character-set=utf8mb4 --execute=`"source $path`""
  $startInfo.WorkingDirectory = $projectRoot
  $startInfo.UseShellExecute = $false
  if ($plainPassword) { $startInfo.EnvironmentVariables['MYSQL_PWD'] = $plainPassword }
  $process = [System.Diagnostics.Process]::Start($startInfo)
  $process.WaitForExit()
  if ($process.ExitCode -ne 0) { throw "MySQL failed while running $path" }
}

Invoke-MySqlFile 'database/schema.sql'
Invoke-MySqlFile 'database/objects.sql'
if ($Seed) { Invoke-MySqlFile 'database/seed.sql' }

$plainPassword = $null
$credential = $null
Write-Host 'PawFinder setup complete. Next run scripts/start-dev.ps1.' -ForegroundColor Green
