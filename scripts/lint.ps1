$ErrorActionPreference = "Stop"
$env:UV_NO_EDITABLE = "1"
$env:PYTHONUTF8 = "1"
$Root = Split-Path -Parent $PSScriptRoot

Set-Location "$Root\backend"
uv run ruff check app tests
uv run pyright

Set-Location "$Root\frontend"
npm run lint
npm run typecheck

Set-Location $Root
Write-Host "==> Lint/typecheck OK"
