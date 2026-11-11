[CmdletBinding()]
param(
  [string]$MySqlHost = '127.0.0.1',
  [int]$MySqlPort = 3306,
  [string]$MySqlUser = 'root',
  [switch]$Seed,
  [switch]$SkipDependencies
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path '.env')) {
  Copy-Item '.env.example' '.env'
  Write-Host '已创建 .env，请在启动前检查数据库连接与 JWT 密钥。' -ForegroundColor Yellow
}

if (-not $SkipDependencies) {
  if (-not (Test-Path '.venv')) { python -m venv .venv }
  & '.\.venv\Scripts\python.exe' -m pip install -r backend/requirements-dev.txt
  npm install --prefix frontend
  npm install
}

$securePassword = Read-Host "请输入 MySQL 用户 $MySqlUser 的密码（空密码直接回车）" -AsSecureString
$plainPassword = [System.Net.NetworkCredential]::new('', $securePassword).Password

function Invoke-MySqlFile([string]$path) {
  Write-Host "执行 $path"
  $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
  $startInfo.FileName = 'mysql'
  $startInfo.ArgumentList.Add("--host=$MySqlHost")
  $startInfo.ArgumentList.Add("--port=$MySqlPort")
  $startInfo.ArgumentList.Add("--user=$MySqlUser")
  $startInfo.ArgumentList.Add('--default-character-set=utf8mb4')
  $startInfo.RedirectStandardInput = $true
  $startInfo.UseShellExecute = $false
  if ($plainPassword) { $startInfo.Environment['MYSQL_PWD'] = $plainPassword }
  $process = [System.Diagnostics.Process]::Start($startInfo)
  $process.StandardInput.Write((Get-Content -Raw -Encoding UTF8 $path))
  $process.StandardInput.Close()
  $process.WaitForExit()
  if ($process.ExitCode -ne 0) { throw "MySQL 执行失败：$path" }
}

Invoke-MySqlFile 'database/schema.sql'
Invoke-MySqlFile 'database/objects.sql'
if ($Seed) { Invoke-MySqlFile 'database/seed.sql' }

$plainPassword = $null
Write-Host 'PawFinder 初始化完成。下一步运行 scripts/start-dev.ps1。' -ForegroundColor Green
