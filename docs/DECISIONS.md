# Decisões técnicas (ADR leve)

## ADR-001 — Paper only no MVP

**Decisão:** Nenhuma integração de ordens reais; bloqueio técnico na config e em `execution/live_orders.py`.  
**Motivo:** Preservação de capital, segurança e escopo da especificação.  
**Status:** Aceito.

## ADR-002 — Supabase Cloud no início

**Decisão:** Usar Supabase Cloud (free tier) a partir da Fase 2; migrations no repositório.  
**Alternativa:** Supabase local via Docker (mais pesado para o setup inicial).  
**Status:** Aceito (implementação na Fase 2).

## ADR-003 — Adapter modular de market data

**Decisão:** Interface `MarketDataProvider`; candidato inicial Binance public REST após validação documental na Fase 3.  
**Motivo:** Substituir provedor sem reescrever estratégia/risco/execução.  
**Status:** Aceito (stub na Fase 1).

## ADR-004 — Decimal financeiro / float indicadores

**Decisão:** `Decimal` para dinheiro, quantidades e taxas; `float` para EMA/RSI/ATR/volume técnico com testes de precisão.  
**Motivo:** Evitar erros de arredondamento monetário sem tornar indicadores verbosos demais.  
**Status:** Aceito.

## ADR-005 — Worker Python independente

**Decisão:** Processo separado do frontend; polling de candles fechados no MVP.  
**Motivo:** Resiliência e desacoplamento da UI.  
**Status:** Aceito (placeholder na Fase 1).

## ADR-006 — Gráficos com lightweight-charts

**Decisão:** Usar TradingView Lightweight Charts no frontend (Fase 7 / entrega de dashboard).  
**Status:** Aceito (ainda não instalado na Fase 1 para evitar dependência prematura).

## ADR-007 — Gerenciador Python `uv`

**Decisão:** `uv` + `uv.lock` no backend.  
**Motivo:** Lockfile reproduzível alinhado à especificação.  
**Status:** Aceito.

## ADR-008 — Sem migrations definitivas na Fase 1

**Decisão:** Pasta `supabase/` preparada; schema/RLS apenas na Fase 2.  
**Status:** Aceito.

## ADR-009 — `uv sync --no-editable` no Windows com path acentuado

**Decisão:** Scripts e Makefile usam `--no-editable` por padrão.  
**Motivo:** Editable installs gravam `.pth` com path UTF-8; o Python da Microsoft Store falha ao ler com codec `cp1252` em pastas como `Área de Trabalho`.  
**Status:** Aceito.

## ADR-010 — Path ASCII preferencial no Windows (Fase 1.1)

**Decisão:** Recomendar `C:\dev\trading_bot` como localização preferencial; manter `UV_NO_EDITABLE=1` como mitigação se o path continuar com acentos.  
**Motivo:** Reduzir falhas operacionais sem remover a mitigação já validada.  
**Status:** Aceito (documentado no RUNBOOK).

## ADR-011 — Upgrade Vitest 5.1.0 (Fase 1.1)

**Decisão:** Atualizar `vitest` para `^5.1.0` (instalado 5.1.0), mantendo `vite@6.4.6`.  
**Motivo:** Eliminar CVEs em `tinypool` e `@vitest/mocker` sem `npm audit fix --force`.  
**Resultado:** `npm audit` e `npm audit --omit=dev` = 0 vulnerabilidades.  
**Status:** Aceito e aplicado.

## ADR-012 — pip-audit como dev dependency (Fase 1.1)

**Decisão:** Incluir `pip-audit` em `optional-dependencies.dev`.  
**Motivo:** Varredura automática de CVEs Python.  
**Status:** Aceito e aplicado. Remediação de `fastapi`/`starlette`/`pytest` autorizada e aplicada na consolidação da Fase 1 (ver ADR-013).

## ADR-013 — Remediação mínima FastAPI/Starlette/pytest (consolidação Fase 1)

**Decisão:** `fastapi>=0.133.1,<0.134.0`, `starlette>=1.3.1,<2`, `pytest>=9.0.3,<10`, `pytest-asyncio>=1.4.1.post1,<2`; manter `httpx>=0.27,<0.29`.  
**Resultado instalado:** FastAPI 0.133.1, Starlette 1.10.0, httpx 0.28.1, pytest 9.2.0, pytest-asyncio 1.4.1.post1.  
**pip-audit:** sem vulnerabilidades conhecidas nas deps atualizadas.  
**Status:** Aceito e aplicado.

## ADR-014 — Adiar migração para httpx2 (TestClient / Starlette 1.x)

**Contexto:** Starlette 1.10 emite `StarletteDeprecationWarning`: `Using httpx with starlette.testclient is deprecated; install httpx2 instead.`  
**Origem:** `fastapi.testclient` → `starlette.testclient` ainda aceita `httpx` 0.x; FastAPI 0.133.1 declara `httpx<1` nos extras `standard`.  
**Decisão nesta consolidação:** **não** migrar para `httpx2`. Manter `httpx 0.28.1`.  
**Motivo:** migração alteraria superfície de testes/deps além da correção mínima; risco desnecessário na fundação.  
**Pendência:** reavaliar `httpx2` em janela dedicada (após Fase 1 publicada), com matriz de compatibilidade FastAPI/Starlette.  
**Status:** Aceito (adiado).

## ADR-015 — Inteligência híbrida e LLM (diretriz futura — sem implementação)

**Decisão de planejamento (não implementar agora):**

1. **Inteligência híbrida** — combinar estratégias quantitativas, indicadores técnicos e LLM como camada **analítica/contextual** (não como autoridade de execução).
2. **Infraestrutura de LLM híbrida** — possibilidade futura de modelos em nuvem e locais, com alternância de provedores e **fallback seguro** se um modelo estiver indisponível.
3. **Separação de responsabilidades**
   - LLM: análise e recomendações.
   - Risk Engine: autoridade independente sobre risco (a LLM **nunca** pode ignorar limites de risco).
   - Execution Engine: execução somente após validações determinísticas.

**Restrições imediatas:** nenhuma integração com APIs de LLM; nenhuma dependência de IA adicionada nesta etapa; nenhuma ordem (paper ou real) decidida diretamente por LLM.  
**Status:** Aceito como diretriz futura. **Não implementado.**
