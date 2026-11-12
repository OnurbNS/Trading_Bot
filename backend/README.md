# Backend — Trading Bot

API FastAPI e motor Python. **Somente paper trading nesta versão.**

## Comandos

```bash
uv sync --all-extras --no-editable
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
uv run pytest -q
uv run ruff check app tests
uv run pyright
```

Use `--no-editable` em paths Windows com acentos (ver `docs/RUNBOOK.md`).


Health: `GET http://127.0.0.1:8000/api/v1/health`
