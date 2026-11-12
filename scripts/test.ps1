$ErrorActionPreference = "Stop"
$env:UV_NO_EDITABLE = "1"
$env:PYTHONUTF8 = "1"
$Root = Split-Path -Parent $PSScriptRoot

Set-Location "$Root\backend"
uv run pytest -q

Set-Location "$Root\frontend"
npm run test -- --run

Set-Location $Root
Write-Host "==> Testes OK"
