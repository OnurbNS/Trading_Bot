# Segurança — Trading Bot Pessoal

## Política operacional (resumo)

1. Modo inicial e único nesta versão: **paper**.
2. Recusar inicialização se configuração incompatível com paper / live habilitado.
3. Não existe endpoint, botão ou caminho funcional para ordens reais no MVP.
4. Simulador não é corretora e não promete lucro.
5. Sem credenciais reais em testes, fixtures ou screenshots.
6. Logs sem senhas, JWT, API keys ou secrets.
7. Alterações de risco auditáveis (Fase 6+).
8. Worker interrompível; estado persistido consultável (Fases futuras).
9. Inconsistência financeira → pausar e reconciliar.
10. Dinheiro real = projeto separado com revisão técnica/regulatória.

## Segredos

| Segredo | Onde pode existir | Onde é proibido |
|---------|-------------------|-----------------|
| `.env` | Máquina local / secrets do host | Git |
| `SUPABASE_SERVICE_ROLE_KEY` | Somente backend | Frontend, Git, banco em texto puro |
| `SUPABASE_ANON_KEY` | Backend / cliente Auth conforme docs | Repositório versionado com valor real |
| Chaves de corretora | Fora do escopo desta versão | Qualquer lugar do MVP |

## Bloqueio de ordens reais (Fase 1)

- `LIVE_TRADING_ENABLED` validado como `false` em `Settings`.
- `assert_paper_only()` na inicialização da API.
- `app.execution.live_orders.submit_live_order()` sempre levanta erro.
- Health e UI reportam `live_trading_enabled: false` e o selo de simulação.

## Frontend

- Não armazenar nem exibir chaves.
- Não aceitar `user_id` arbitrário como fonte de autorização (Auth na Fase 2).
- Variáveis `VITE_*` apenas para URL pública da API / anon key futura — nunca service role.
