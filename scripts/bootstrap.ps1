$ErrorActionPreference = "Stop"
$env:UV_NO_EDITABLE = "1"
$env:PYTHONUTF8 = "1"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Backend: uv sync"
Set-Location "$Root\backend"
uv sync --all-extras --no-editable

Write-Host "==> Frontend: npm install"
Set-Location "$Root\frontend"
npm install

Set-Location $Root
if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "==> Criado .env a partir de .env.example"
}

Write-Host "==> Bootstrap concluído"
