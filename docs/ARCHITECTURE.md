# Arquitetura — Trading Bot Pessoal

**Modo:** PAPER TRADING — SEM DINHEIRO REAL  
**Fase atual documentada:** Fase 1 (Fundação)

## Visão geral

Monorepo com:

| Componente | Tecnologia | Papel |
|------------|------------|-------|
| Frontend | React + TypeScript + Vite | Dashboard e visualização |
| Backend API | Python + FastAPI | HTTP, health, (futuro) orquestração |
| Motor / domínio | Python puro | Estratégia, risco, execução simulada |
| Worker | Processo Python separado | Ingestão e paper loop (fases futuras) |
| Banco / Auth | Supabase (Cloud) | PostgreSQL + Auth (Fase 2+) |

## Princípios

1. Separação: dados → indicadores → estratégia → risco → execução paper → UI.
2. Estratégia não envia ordens; apenas gera sinais determinísticos.
3. LLM não decide operações.
4. Provedor de market data atrás de interface substituível (`MarketDataProvider`).
5. Valores financeiros em `Decimal`; indicadores matemáticos em `float` com testes de precisão.
6. Bloqueio técnico absoluto de ordens reais nesta versão (`LIVE_TRADING_ENABLED=false`, guardas na inicialização e em `execution/live_orders.py`).

## Diagrama lógico (alvo)

```text
Provedor → Adapter → Validação → DB / Indicadores → Estratégia → Risco
                                                          ↓
                                              Paper Broker → Carteira → DB
                                                          ↓
                                              FastAPI → React Dashboard
```

## Fase 1 (implementado)

- Estrutura do monorepo
- FastAPI com `GET /api/v1/health`
- Frontend com selo de simulação
- Configuração, lint, testes mínimos
- Stubs de pacotes para fases seguintes
- Worker placeholder (sem ingestão/trading)

## Fora da Fase 1

Integração Supabase, market data, indicadores, estratégia, backtest, paper broker funcional, dashboard completo.
