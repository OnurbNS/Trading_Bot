# Trading Bot — comandos padronizados
# Em Windows sem GNU Make, use: powershell -File scripts\bootstrap.ps1 (etc.)

.PHONY: install install-backend install-frontend dev backend frontend test lint typecheck down help

export UV_NO_EDITABLE ?= 1
export PYTHONUTF8 ?= 1

help:
	@echo "Targets: install | dev | backend | frontend | test | lint | typecheck | down"

install: install-backend install-frontend

install-backend:
	cd backend && uv sync --all-extras --no-editable

install-frontend:
	cd frontend && npm install

dev:
	@echo "Inicie backend e frontend em terminais separados:"
	@echo "  make backend"
	@echo "  make frontend"

backend:
	cd backend && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest -q
	cd frontend && npm run test -- --run

lint:
	cd backend && uv run ruff check app tests
	cd frontend && npm run lint

typecheck:
	cd backend && uv run pyright
	cd frontend && npm run typecheck

down:
	docker compose down
