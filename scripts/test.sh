#!/usr/bin/env bash
set -euo pipefail
export UV_NO_EDITABLE=1
export PYTHONUTF8=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend" && uv run pytest -q
cd "$ROOT/frontend" && npm run test -- --run
echo "Testes OK"
