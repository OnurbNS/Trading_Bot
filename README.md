# Trading Bot Pessoal — BTC/USDT e ETH/USDT (Spot)

**PAPER TRADING — SEM DINHEIRO REAL**

Robô pessoal de análise e negociação **simulada**. Esta versão **não envia ordens reais**, não usa alavancagem, margem ou futuros.

Especificação oficial: [`PROJECT_SPEC.md`](./PROJECT_SPEC.md)

## Status

**Fase 1 — Fundação** concluída (health, dashboard com selo de simulação, lint/testes)

- Backend FastAPI com `GET /api/v1/health`
- Frontend React + Vite + TypeScript com selo de simulação
- Configuração, lint, testes mínimos e documentação inicial

## Pré-requisitos

- Python 3.11+
- Node.js 20+
- npm
- [uv](https://github.com/astral-sh/uv) (`python -m pip install --user uv`)
- Docker opcional
- GNU Make opcional (no Windows use `scripts\*.ps1`)

## Instalação rápida (Windows)

```powershell
Copy-Item .env.example .env
.\scripts\bootstrap.ps1
```

## Backend

```powershell
cd backend
uv sync --all-extras --no-editable
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```


Health: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)  
OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abrir [http://127.0.0.1:5173](http://127.0.0.1:5173) e confirmar o banner **PAPER TRADING — SEM DINHEIRO REAL**.

## Testes e lint

```powershell
.\scripts\test.ps1
.\scripts\lint.ps1
```

## Estrutura

```text
trading_bot/
├── PROJECT_SPEC.md
├── backend/          # FastAPI + motor Python
├── frontend/         # React + Vite + TypeScript
├── docs/             # Arquitetura, segurança, runbook, decisões
├── supabase/         # Migrations na Fase 2
├── scripts/          # bootstrap / lint / test
└── docker-compose.yml
```

## Segurança (resumo)

- `LIVE_TRADING_ENABLED` deve permanecer `false`
- Sem chaves no frontend ou no Git
- Service role do Supabase somente no backend (Fase 2+)
- Detalhes: [`docs/SECURITY.md`](./docs/SECURITY.md)

## Documentação

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)
- [`docs/SECURITY.md`](./docs/SECURITY.md)
- [`docs/RUNBOOK.md`](./docs/RUNBOOK.md)
- [`docs/DECISIONS.md`](./docs/DECISIONS.md)
- [`docs/API.md`](./docs/API.md)

## Aviso

Simulação educacional/pessoal. Não é recomendação de investimento. Não há garantia de lucro. Sinais futuros serão regras explícitas, não certezas.
