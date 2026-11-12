# Runbook — execução local (Fase 1 / 1.1)

## Pré-requisitos

- Python 3.11+
- Node.js 20+ (testado com 24)
- npm
- `uv` (gerenciador Python): `python -m pip install --user uv`
- Docker opcional (perfil `api` no compose)
- GNU Make opcional; no Windows use os scripts PowerShell em `scripts/`

## Caminho do projeto no Windows (importante)

O Python da Microsoft Store pode falhar ao ler instalação **editable** do `uv` quando o caminho contém acentos (ex.: `Área de Trabalho`), por causa do codec `cp1252` em arquivos `.pth`.

### Recomendação preferencial (ASCII)

Coloque o repositório em um path sem acentos, por exemplo:

```text
C:\dev\trading_bot
```

Exemplo de migração (PowerShell, ajuste a origem):

```powershell
New-Item -ItemType Directory -Force -Path C:\dev | Out-Null
Copy-Item -Recurse -Force "C:\Users\<voce>\OneDrive\Área de Trabalho\trading_bot" C:\dev\trading_bot
cd C:\dev\trading_bot
```

Depois disso, reinstale dependências em `C:\dev\trading_bot` e trabalhe a partir desse diretório.

### Mitigação se permanecer em path com acentos

Mantenha a mitigação atual (não removê-la):

```powershell
$env:UV_NO_EDITABLE = "1"
$env:PYTHONUTF8 = "1"
cd backend
uv sync --all-extras --no-editable
```

Os scripts em `scripts\*.ps1` e o `Makefile` já exportam `UV_NO_EDITABLE=1`.

## Configuração e arquivo `.env`

### Onde o `.env` deve ficar

O backend carrega variáveis via `pydantic-settings` com `env_file=".env"` (**caminho relativo ao diretório de trabalho do processo**), em `backend/app/core/config.py`.

| Cenário | Diretório de execução | Localização esperada do `.env` |
|---------|----------------------|--------------------------------|
| Recomendado (Fase 1) | raiz do repositório (`trading_bot/`) | `trading_bot/.env` (criado a partir de `.env.example`) |
| Se o processo subir em `backend/` | `trading_bot/backend/` | `trading_bot/backend/.env` **ou** exporte as variáveis no shell / use o `.env` da raiz com CWD na raiz |
| Docker Compose (perfil `api`) | container | `env_file: .env` na raiz + overrides em `environment:` (paper/live bloqueados) |

### Procedimento local

```powershell
# Na raiz do repositório
Copy-Item .env.example .env
```

Não é necessário preencher Supabase na Fase 1/1.1. Mantenha:

```text
APP_MODE=paper
TRADING_ENABLED=false
LIVE_TRADING_ENABLED=false
```

### Se o `.env` não existir

A aplicação **não falha** só por ausência do arquivo: usa defaults seguros do `Settings` (modo `paper`, `live_trading_enabled=false`, `trading_enabled=false`). Variáveis de ambiente do sistema/shell, quando presentes, têm precedência sobre o arquivo.

### Valores padrão seguros (resumo)

- `APP_MODE=paper` (único valor aceito nesta versão)
- `LIVE_TRADING_ENABLED=false` (`true` **rejeita** a inicialização)
- `TRADING_ENABLED=false`
- Credenciais Supabase / market data vazias até fases autorizadas

Nunca versione o arquivo `.env`. Nunca coloque `SUPABASE_SERVICE_ROLE_KEY` no frontend.

## Instalação

### Com Make

```bash
make install
```

### Windows (PowerShell)

```powershell
.\scripts\bootstrap.ps1
```

## Backend

```powershell
cd backend
uv sync --all-extras --no-editable
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

OpenAPI: `http://127.0.0.1:8000/docs`

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abrir `http://127.0.0.1:5173` e confirmar o selo **PAPER TRADING — SEM DINHEIRO REAL**.

## Testes e lint

```powershell
.\scripts\test.ps1
.\scripts\lint.ps1
```

Ou:

```powershell
cd backend; $env:UV_NO_EDITABLE="1"; uv run pytest -q; uv run ruff check app tests; uv run pyright
cd ..\frontend; npm run test -- --run; npm run lint; npm run typecheck
```

## Docker (opcional)

```powershell
docker compose --profile api up --build
```

## Troubleshooting

| Problema | Ação |
|----------|------|
| `LIVE_TRADING_ENABLED=true` | Remover/definir `false`; app recusa iniciar |
| `APP_MODE` diferente de `paper` | Corrigir para `paper`; valor inválido rejeita Settings |
| Porta 8000 em uso | Alterar `APP_PORT` ou encerrar processo |
| `uv` não encontrado | Reabrir o terminal após `pip install --user uv` |
| Erro Unicode / `.pth` / `cp1252` | Usar `UV_NO_EDITABLE=1` ou migrar para `C:\dev\trading_bot` |
| CORS no browser | Frontend em `localhost:5173` / `127.0.0.1:5173` |
| Make não existe no Windows | Usar `scripts\*.ps1` |

## O que NÃO fazer nesta fase

- Não conectar corretora
- Não habilitar live trading
- Não colocar secrets no frontend
- Não avançar para Fase 2 sem aprovação
