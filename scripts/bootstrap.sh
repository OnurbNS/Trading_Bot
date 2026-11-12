#!/usr/bin/env bash
set -euo pipefail
export UV_NO_EDITABLE=1
export PYTHONUTF8=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend" && uv sync --all-extras --no-editable
cd "$ROOT/frontend" && npm install
cd "$ROOT"
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Criado .env a partir de .env.example"
fi
echo "Bootstrap concluído"
