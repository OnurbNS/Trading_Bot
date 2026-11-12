# Projeto: Trading Bot Pessoal — BTC e ETH (Spot)

Documento de arquitetura e implementação para o Cursor  
**Versão:** 1.0  
**Data:** 11/11/2026  
**Arquivo oficial:** `PROJECT_SPEC.md`

**Objetivo:** construir um robô pessoal de análise e negociação simulada de criptoativos, começando por BTC/USDT e ETH/USDT no mercado Spot.

---

## 0. Instruções prioritárias para o Cursor

Você é um engenheiro de software sênior responsável por implementar este projeto de forma incremental, segura, testável e documentada.

### Regras obrigatórias

1. Comece em PAPER TRADING. Não implemente envio de ordens reais nesta primeira versão.
2. Não habilite alavancagem, margem, futuros, empréstimos ou venda a descoberto.
3. Não prometa lucro nem trate sinais como certezas. O sistema calcula cenários segundo regras explícitas.
4. Não deixe uma LLM decidir diretamente abrir, alterar ou fechar ordens. A execução deve depender de regras determinísticas, validadas e testadas.
5. Nunca armazene chaves de API no frontend, no Git, em arquivos versionados ou no banco em texto puro.
6. Não solicite permissões de saque nas chaves de corretora. Quando houver integração futura, usar somente permissões estritamente necessárias.
7. Antes de implementar cada fase: leia este documento, inspecione o repositório, proponha um plano curto e implemente somente a fase autorizada pelo usuário.
8. Não sobrescreva arquivos existentes sem inspecioná-los. Preserve convenções e funcionalidades já presentes.
9. Use versões estáveis e compatíveis das dependências. Registre versões no lockfile.
10. Todo cálculo financeiro deve usar `Decimal`, nunca `float`, para valores monetários, quantidades e taxas. Indicadores matemáticos (EMA, RSI, ATR, médias de volume técnico) podem usar ponto flutuante, com testes de precisão documentados. Ver seção 0.1.
11. Toda decisão de estratégia deve registrar os dados de entrada, versão da estratégia, horário, motivo e resultado.
12. Em caso de dado atrasado, inválido, incompleto, desconectado ou inconsistente, não operar.
13. Inclua testes automatizados e documentação junto com cada funcionalidade.
14. Não invente endpoints, parâmetros ou comportamentos de APIs. Consulte a documentação oficial atual antes de integrar qualquer provedor.
15. O sistema deve iniciar com execução desabilitada por padrão e exigir configuração explícita para qualquer modo operacional.
16. Bloqueio técnico absoluto de envio de ordens reais nesta versão: `LIVE_TRADING_ENABLED` deve permanecer `false`; a aplicação deve recusar inicialização se detectar tentativa de habilitação; não deve existir endpoint, botão ou caminho de código funcional para ordens reais no MVP.
17. Arquitetura modular de market data: provedores atrás de interface, permitindo substituição sem alterar estratégia, risco ou execução.
18. Worker Python independente do frontend, com resiliência a falhas de API, dados desatualizados e interrupções inesperadas.
19. Auditoria completa de decisões e operações simuladas.
20. Preparação para testes em regimes de alta, baixa, lateralização e alta volatilidade (dados e cenários de backtest/paper).

### Escopo desta entrega

Construir a primeira versão funcional para:

- BTC/USDT e ETH/USDT;
- mercado Spot;
- ingestão de candles e cotações;
- indicadores técnicos;
- estratégia inicial transparente e configurável;
- backtesting;
- paper trading;
- simulador de carteira, taxas e slippage;
- gestão de risco;
- dashboard;
- histórico, auditoria, alertas e monitoramento.

**Fora do escopo inicial:** dinheiro real, execução automática em corretora, futuros, margem, copy trading, venda de sinais, recomendações personalizadas a terceiros e cobrança de assinaturas.

### 0.1 Ajustes técnicos aprovados (Fase 0 — 11/11/2026)

Estes ajustes complementam e, quando aplicável, esclarecem as regras acima. Não removem requisitos de segurança nem autorizam trading real.

| Tema | Decisão aprovada |
|------|------------------|
| Provedor de market data | Adapter modular; primeira implementação candidata: APIs públicas (ex.: Binance public REST), após consulta à documentação oficial vigente, limites e restrições regionais |
| Banco / Auth | Supabase Cloud (free tier) no início; migrations SQL versionadas no repositório |
| Indicadores | Implementação própria; `float` para cálculo matemático com testes de precisão; `Decimal` para dinheiro, quantidades, taxas, saldo e ledger |
| Gráficos (frontend) | `lightweight-charts` (TradingView) |
| Worker | Processo Python separado do frontend/API HTTP de UI; polling de candles fechados no MVP |
| Agendamento | Polling no MVP; WebSocket em fase futura se necessário |
| Notificações externas | Fora do MVP |
| Nome do arquivo de spec | `PROJECT_SPEC.md` |
| Ordens reais | Bloqueio técnico absoluto nesta versão |

---

## 1. Visão geral do produto

O produto será um aplicativo web pessoal com um motor de negociação em Python.

O usuário acompanha BTC/USDT e ETH/USDT. O sistema recebe dados de mercado, valida a qualidade dos dados, calcula indicadores, avalia uma estratégia e decide entre:

- **BUY:** abrir posição simulada, se todos os critérios e limites forem atendidos;
- **HOLD:** manter posição aberta;
- **EXIT:** fechar posição simulada por regra de saída;
- **NO_TRADE:** não operar;
- **KILL_SWITCH:** interromper novas operações e, conforme a política de segurança, solicitar fechamento simulado das posições.

O sistema deve explicar cada decisão com regras verificáveis. A IA generativa pode resumir o estado e explicar termos, mas não pode ser fonte de decisão operacional.

### 1.1 Princípios

- Preservação de capital antes de retorno.
- Nenhuma operação sem stop definido.
- Nenhuma operação se os dados estiverem atrasados.
- Limites de exposição e perda diária.
- Simulação realista de taxas e slippage.
- Estratégias versionadas e reproduzíveis.
- Auditoria de todas as decisões.
- Separação entre dados, estratégia, risco, execução e interface.

### 1.2 Métricas de sucesso

Não considerar lucro isolado como prova de qualidade. Avaliar:

- retorno líquido após taxas e slippage;
- drawdown máximo;
- fator de lucro;
- taxa de acerto;
- ganho médio e perda média;
- expectativa por operação;
- número de operações;
- exposição média;
- tempo em posição;
- desempenho por ativo e por regime de mercado;
- diferença entre backtest e paper trading.

---

## 2. Arquitetura proposta

### 2.1 Componentes

1. Frontend: React + TypeScript + Vite.
2. Backend/API: Python + FastAPI.
3. Motor de estratégia: Python, isolado da API HTTP.
4. Worker: processo separado para ingestão, indicadores e paper trading.
5. Banco: Supabase PostgreSQL.
6. Autenticação: Supabase Auth.
7. Migrações: SQL versionado no repositório.
8. Observabilidade: logs estruturados, health checks e auditoria.
9. Testes: pytest no backend e Vitest no frontend.
10. Execução local: Docker Compose, quando aplicável.

### 2.2 Diagrama lógico

```text
flowchart TD
    EX[Provedor de dados de mercado] --> ING[Market Data Adapter]
    ING --> VAL[Validação e normalização]
    VAL --> DB[(Supabase PostgreSQL)]
    VAL --> IND[Indicadores técnicos]
    IND --> STR[Motor de estratégia]
    STR --> RISK[Motor de risco]
    RISK --> DEC{Decisão permitida?}
    DEC -->|Não| AUD[Auditoria / NO_TRADE]
    DEC -->|Sim| PAPER[Paper Broker]
    PAPER --> PORT[Carteira simulada]
    PORT --> DB
    AUD --> DB
    DB --> API[FastAPI]
    API --> UI[React Dashboard]
    API --> ALERT[Serviço de alertas]
```

### 2.3 Fluxo de uma avaliação

1. Receber candle ou atualização de mercado.
2. Normalizar símbolo, horário, preço e volume.
3. Verificar integridade, duplicidade e atraso.
4. Persistir os dados.
5. Calcular indicadores usando somente candles fechados, salvo se a estratégia declarar explicitamente outra regra.
6. Gerar sinal bruto.
7. Aplicar filtros e limites de risco.
8. Se permitido, enviar ordem ao simulador.
9. Simular preenchimento, taxas e slippage.
10. Atualizar posição e saldo em transação consistente.
11. Registrar decisão e evento de execução.
12. Atualizar dashboard e alertas.

---

## 3. Estrutura de diretórios

Adotar monorepo:

```text
trading-bot/
├── README.md
├── PROJECT_SPEC.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── market_data/
│   │   ├── indicators/
│   │   ├── strategies/
│   │   ├── risk/
│   │   ├── execution/
│   │   ├── portfolio/
│   │   ├── backtesting/
│   │   ├── services/
│   │   └── workers/
│   └── tests/
├── frontend/
├── supabase/
├── docs/
└── scripts/
```

O Cursor deve adaptar a estrutura caso o repositório já exista, sem duplicar projetos ou configurações.

---

## 4. Configuração e ambientes

Criar três ambientes claramente separados:

- `development`: desenvolvimento local;
- `test`: testes automatizados;
- `production`: não habilitado nesta primeira versão.

O modo padrão será `paper`.

### 4.1 Variáveis de ambiente

Criar `.env.example` sem segredos (ver arquivo na raiz). Regras:

- `SUPABASE_SERVICE_ROLE_KEY` somente no backend e nunca no navegador.
- Não versionar `.env`.
- Validar configuração na inicialização.
- Se variável obrigatória estiver ausente, falhar com mensagem clara.
- `LIVE_TRADING_ENABLED` deve permanecer `false` e não deve existir endpoint de ativação real no MVP.
- Nenhuma credencial ou chave privada exposta no frontend.

---

## 5. Banco de dados — Supabase PostgreSQL

Usar Supabase como PostgreSQL e autenticação. O backend acessa o banco com credencial segura no servidor. O frontend nunca recebe service role key.

Criar migrações SQL versionadas. Não depender de alterações manuais no painel sem migração correspondente.

### 5.1 Tabelas

#### profiles

- `id` uuid primary key references auth.users(id)
- `display_name` text
- `created_at` timestamptz
- `updated_at` timestamptz

#### market_candles

- `id` bigserial primary key
- `provider` text not null
- `symbol` text not null
- `timeframe` text not null
- `open_time` timestamptz not null
- `close_time` timestamptz not null
- `open` numeric(30,12) not null
- `high` numeric(30,12) not null
- `low` numeric(30,12) not null
- `close` numeric(30,12) not null
- `volume` numeric(30,12) not null
- `is_closed` boolean not null
- `created_at` timestamptz default now()
- unique (provider, symbol, timeframe, open_time)

Validar: high >= low; high >= open/close; low <= open/close; volume >= 0.

#### strategy_versions

- `id` uuid primary key
- `name` text not null
- `version` text not null
- `description` text
- `parameters` jsonb not null
- `enabled` boolean default false
- `created_at` timestamptz default now()
- unique (name, version)

Uma versão usada em backtest ou operação nunca deve ser editada. Criar nova versão para alterações.

#### strategy_signals

- `id` uuid primary key
- `strategy_version_id` uuid references strategy_versions(id)
- `symbol` text not null
- `timeframe` text not null
- `candle_open_time` timestamptz not null
- `signal` text not null — BUY, HOLD, EXIT, NO_TRADE
- `reason` jsonb not null
- `indicators` jsonb not null
- `created_at` timestamptz default now()
- unique (strategy_version_id, symbol, timeframe, candle_open_time)

#### risk_events

- `id` uuid primary key
- `event_type` text not null
- `severity` text not null
- `symbol` text
- `details` jsonb not null
- `created_at` timestamptz default now()

#### paper_accounts

- `id` uuid primary key
- `user_id` uuid references auth.users(id)
- `name` text not null
- `quote_asset` text not null default 'USDT'
- `initial_balance` numeric(30,12) not null
- `cash_balance` numeric(30,12) not null
- `status` text not null
- `created_at` timestamptz default now()

#### paper_orders

- `id` uuid primary key
- `account_id` uuid references paper_accounts(id)
- `client_order_id` text unique not null
- `symbol` text not null
- `side` text not null — BUY, SELL
- `order_type` text not null
- `quantity` numeric(30,12) not null
- `requested_price` numeric(30,12)
- `average_fill_price` numeric(30,12)
- `fee` numeric(30,12) not null default 0
- `slippage` numeric(30,12) not null default 0
- `status` text not null
- `strategy_version_id` uuid references strategy_versions(id)
- `created_at` timestamptz default now()
- `filled_at` timestamptz

#### paper_positions

- `id` uuid primary key
- `account_id` uuid references paper_accounts(id)
- `symbol` text not null
- `quantity` numeric(30,12) not null
- `average_entry_price` numeric(30,12) not null
- `stop_price` numeric(30,12)
- `take_profit_price` numeric(30,12)
- `opened_at` timestamptz not null
- `updated_at` timestamptz not null
- unique (account_id, symbol)

#### trade_ledger

- `id` uuid primary key
- `account_id` uuid references paper_accounts(id)
- `order_id` uuid references paper_orders(id)
- `entry_type` text not null
- `asset` text not null
- `quantity` numeric(30,12) not null
- `unit_price` numeric(30,12) not null
- `fee` numeric(30,12) not null default 0
- `created_at` timestamptz default now()

O ledger deve ser imutável: correções por lançamentos compensatórios, nunca apagando o histórico financeiro.

#### backtest_runs

- `id` uuid primary key
- `strategy_version_id` uuid references strategy_versions(id)
- `symbol` text not null
- `timeframe` text not null
- `start_at` timestamptz not null
- `end_at` timestamptz not null
- `initial_balance` numeric(30,12) not null
- `final_balance` numeric(30,12)
- `metrics` jsonb
- `status` text not null
- `created_at` timestamptz default now()

#### audit_events

- `id` uuid primary key
- `actor` text not null
- `action` text not null
- `entity_type` text not null
- `entity_id` text
- `details` jsonb not null
- `created_at` timestamptz default now()

#### app_settings

- `key` text primary key
- `value` jsonb not null
- `updated_at` timestamptz default now()

### 5.2 Segurança e RLS

- Ativar RLS em tabelas expostas ao cliente.
- Usuário só pode consultar e alterar seus próprios profiles, paper_accounts e dados vinculados à própria conta.
- Dados públicos de mercado podem ser somente leitura.
- Estratégias globais do sistema podem ser somente leitura para usuário comum.
- O frontend não deve gravar diretamente ordens, ledger ou posições. Essas operações passam pelo backend.
- Service role key somente no servidor.
- Criar políticas explícitas e testes de acesso entre usuários.
- Não confiar em user_id enviado pelo cliente; obter identidade do token validado no backend.

---

## 6. Backend Python

### 6.1 Stack sugerida

- Python estável compatível com as bibliotecas escolhidas;
- FastAPI;
- Pydantic;
- SQLAlchemy ou cliente PostgreSQL/Supabase, escolhendo uma abordagem e mantendo consistência;
- Decimal para valores financeiros;
- float para indicadores matemáticos, com testes de precisão;
- pandas ou polars para análise histórica, se necessário;
- pytest;
- Ruff;
- mypy ou pyright;
- httpx;
- biblioteca de indicadores ou implementação própria validada por testes.

Antes de adicionar dependência, avaliar manutenção, licença e compatibilidade.

### 6.2 Camadas

- `api`: HTTP, validação e autenticação;
- `services`: coordenação dos casos de uso;
- `domain`: entidades e regras independentes;
- `market_data`: provedores e normalização (interface substituível);
- `indicators`: cálculos técnicos puros;
- `strategies`: geração de sinais;
- `risk`: autorização ou bloqueio de operações;
- `execution`: simulação de ordens (somente paper nesta versão);
- `portfolio`: saldo, posições e ledger;
- `backtesting`: simulação histórica.

O domínio não deve depender de FastAPI, Supabase ou React.

### 6.3 Endpoints iniciais

Todos sob `/api/v1`.

| Método | Rota | Finalidade |
|--------|------|------------|
| GET | `/health` | Saúde do serviço |
| GET | `/market/symbols` | Símbolos habilitados |
| GET | `/market/candles` | Consultar candles |
| GET | `/market/status` | Estado e atraso dos dados |
| GET | `/strategies` | Listar estratégias |
| GET | `/strategies/{id}` | Detalhes e parâmetros |
| POST | `/backtests` | Criar backtest |
| GET | `/backtests/{id}` | Consultar resultado |
| GET | `/paper/account` | Consultar conta simulada |
| POST | `/paper/account/reset` | Resetar conta simulada, com confirmação |
| GET | `/paper/orders` | Histórico de ordens |
| GET | `/paper/positions` | Posições abertas |
| GET | `/paper/performance` | Métricas de desempenho |
| GET | `/risk/status` | Estado dos limites |
| POST | `/risk/kill-switch` | Interromper novas operações |
| GET | `/settings` | Configurações não secretas |
| PATCH | `/settings` | Atualizar configurações permitidas |

Não criar rotas para ordens reais no MVP.

### 6.4 Contratos e validação

- Validar símbolo e timeframe por allowlist.
- Validar intervalo máximo de datas para backtest.
- Paginar históricos.
- Definir timeout e retry limitado para provedores externos.
- Usar idempotência para criação de ordens simuladas.
- Retornar erros padronizados sem expor stack trace ou segredos.
- Documentar API com OpenAPI gerado pelo FastAPI.

---

## 7. Dados de mercado

Criar uma interface `MarketDataProvider` para não acoplar o projeto a uma corretora.

Operações esperadas:

- listar símbolos suportados;
- buscar candles históricos;
- obter ticker;
- obter horário do servidor, quando disponível;
- obter metadados de precisão e filtros do símbolo.

O primeiro adaptador poderá usar dados públicos de um provedor de criptoativos. Binance pode ser avaliada como primeira opção, mas o Cursor deve consultar a documentação oficial vigente e confirmar disponibilidade regional, limites de requisição, licenciamento e condições de uso antes de implementar.

### 7.1 Timeframes iniciais

Começar com 5m e 1h. Não misturar candles de timeframes diferentes na mesma avaliação.

### 7.2 Qualidade dos dados

Bloquear sinal se:

- candle estiver incompleto quando a estratégia exigir candle fechado;
- timestamp estiver fora de sequência;
- houver lacuna inesperada;
- preço ou volume for negativo ou inválido;
- cotação estiver velha além do limite configurado;
- provedor estiver desconectado;
- houver divergência relevante entre fontes, se mais de uma for utilizada.

Registrar a causa do bloqueio.

---

## 8. Estratégia inicial — Trend Momentum v1

Esta estratégia é um ponto de partida experimental, não uma recomendação de investimento e não deve ser considerada lucrativa sem testes rigorosos.

### 8.1 Indicadores

- EMA 20;
- EMA 50;
- RSI 14;
- ATR 14;
- média de volume de 20 candles.

Implementar cálculos com testes de referência e tratar período de aquecimento. Não gerar sinais antes de existir histórico suficiente.

### 8.2 Regra experimental de entrada

Avaliar apenas candle fechado no timeframe de 5 minutos:

Condições candidatas:

1. EMA 20 acima da EMA 50;
2. fechamento acima da EMA 20;
3. RSI dentro de faixa configurável, inicialmente 50 a 68;
4. volume acima de um limiar configurável da média;
5. ATR dentro de limites de volatilidade definidos;
6. nenhum bloqueio de risco ativo;
7. não existir posição aberta no mesmo símbolo.

Se todas as condições forem verdadeiras, gerar sinal candidato BUY. O motor de risco ainda precisa aprovar.

### 8.3 Regra experimental de saída

- stop inicial baseado em múltiplo configurável do ATR;
- alvo baseado em relação risco/retorno configurável;
- saída por cruzamento/condição de tendência contrária, se habilitada;
- saída por tempo máximo em posição, se habilitada;
- stop e alvo sempre processados pelo simulador;
- se stop e alvo forem tocados no mesmo candle histórico e não houver dados intrabar suficientes para saber a ordem, assumir o resultado conservador (stop primeiro) e registrar essa limitação.

Parâmetros iniciais apenas para experimento:

- risco máximo por operação: 0,5% do patrimônio simulado;
- perda diária máxima: 1% do patrimônio inicial do dia;
- exposição máxima total: 20% do patrimônio;
- uma posição por símbolo;
- sem alavancagem;
- máximo de duas posições simultâneas.

Esses limites são conservadores para iniciar testes, mas não eliminam risco. Torná-los configuráveis com validação de limites máximos.

### 8.4 Sem overfitting

- separar dados em treino, validação e teste fora da amostra;
- evitar otimizar parâmetros repetidamente no mesmo período;
- incluir períodos de alta, baixa e lateralização (e alta volatilidade);
- testar taxas e slippage;
- registrar todas as configurações;
- comparar com estratégia passiva de referência;
- não usar dados futuros no cálculo de indicadores.

---

## 9. Gestão de risco

O RiskEngine deve ser independente da estratégia.

Antes de permitir qualquer ordem, verificar:

1. trading habilitado;
2. dados válidos e recentes;
3. mercado e símbolo permitidos;
4. saldo suficiente;
5. quantidade mínima e precisão do ativo;
6. risco estimado dentro do limite;
7. perda diária abaixo do limite;
8. drawdown abaixo do limite;
9. exposição total abaixo do limite;
10. ausência de kill switch;
11. ausência de ordem duplicada;
12. stop definido e válido.

Se qualquer condição falhar, retornar DENY com código e motivo. Não tentar contornar bloqueios automaticamente.

### 9.1 Kill switch

O kill switch deve:

- impedir novas entradas imediatamente;
- cancelar tarefas pendentes de avaliação;
- preservar logs e posições;
- registrar ator, horário e motivo;
- exigir ação explícita para reativar o paper trading.

No MVP, não há ordens reais para cancelar.

---

## 10. Paper broker e simulação

O simulador precisa ser realista o suficiente para não criar resultados ilusórios.

Considerar:

- taxa maker/taker configurável;
- slippage configurável em basis points;
- spread, quando houver dado;
- preenchimento parcial, se modelado;
- filtros de quantidade e notional mínimo;
- atraso simulado entre sinal e execução;
- arredondamento segundo metadados do ativo;
- rejeição de ordens inválidas;
- saldo reservado e liberado;
- idempotência.

Não assumir que toda ordem é preenchida exatamente no preço de fechamento do candle que gerou o sinal. Usar preço do próximo evento/candle disponível e aplicar slippage e taxas.

O simulador deve produzir eventos:

- ORDER_CREATED;
- ORDER_ACCEPTED;
- ORDER_PARTIALLY_FILLED;
- ORDER_FILLED;
- ORDER_REJECTED;
- POSITION_OPENED;
- POSITION_UPDATED;
- POSITION_CLOSED.

---

## 11. Backtesting

O backtest deve reutilizar a mesma estratégia, motor de risco e regras de execução do paper trading sempre que possível.

Entradas:

- estratégia e versão;
- símbolo;
- timeframe;
- intervalo histórico;
- saldo inicial;
- taxas;
- slippage;
- parâmetros.

Saídas:

- curva de patrimônio;
- retorno total e anualizado, quando aplicável;
- drawdown máximo;
- fator de lucro;
- taxa de acerto;
- payoff médio;
- expectativa por trade;
- quantidade de operações;
- custos totais;
- tabela de operações;
- períodos sem operação;
- comparação com benchmark.

Regras:

- evitar look-ahead bias;
- evitar survivorship bias quando aplicável;
- tratar gaps;
- não usar candle incompleto;
- documentar limitações de dados;
- salvar configuração e versão exatas para reprodução.

---

## 12. Frontend — React

### 12.1 Páginas

1. Dashboard — saldo simulado, patrimônio, P&L, drawdown, status, qualidade dos dados, posições.
2. Mercado — BTC/USDT e ETH/USDT, candles, timeframe, indicadores, último sinal.
3. Estratégias — versão, parâmetros, ativar/desativar paper, histórico.
4. Backtests — formulário, métricas, curva, operações, comparação.
5. Paper Trading — ordens, posições, saldo, taxas, eventos.
6. Risco — limites, exposição, kill switch.
7. Configurações — ativos, timeframe, taxas, slippage, preferências.

### 12.2 Requisitos de UX

- Exibir claramente **SIMULAÇÃO — SEM DINHEIRO REAL** / **PAPER TRADING — SEM DINHEIRO REAL**.
- Mostrar horário da última atualização e status dos dados.
- Nunca usar somente verde/vermelho para transmitir estado; incluir texto/ícone.
- Confirmação antes de resetar conta ou alterar parâmetros importantes.
- Exibir motivo de cada sinal e de cada bloqueio.
- Mostrar valores em USDT e, se houver conversão, indicar cotação e horário.
- Interface responsiva.
- Não exibir chaves ou segredos.

---

## 13. Autenticação e autorização

Mesmo sendo uso pessoal, implementar autenticação.

- Supabase Auth para login.
- Backend valida JWT e identidade.
- Toda consulta de conta é escopada pelo usuário autenticado.
- Não aceitar user_id arbitrário do frontend.
- Rate limit em endpoints sensíveis.
- Sessões e tokens tratados conforme documentação oficial.
- RLS como camada adicional, não substituto da autorização do backend.

---

## 14. Logs, auditoria e alertas

Logs estruturados em JSON com:

- timestamp UTC;
- nível;
- serviço;
- request/correlation ID;
- símbolo;
- estratégia e versão;
- evento;
- motivo;
- duração.

Nunca registrar:

- senha;
- token JWT;
- API key;
- secret;
- dados pessoais desnecessários.

Alertas possíveis: dados parados; worker indisponível; erro no provedor; ordem simulada rejeitada; limite de risco; kill switch; backtest concluído.

Notificações externas (Telegram/WhatsApp) ficam para fase posterior.

---

## 15. Testes obrigatórios

### 15.1 Unitários

EMA, RSI, ATR, volume; stop e alvo; sizing; taxas e slippage; arredondamento; saldo e ledger; regras de entrada/saída; limites de risco; dados atrasados; idempotência; precisão de indicadores em float vs valores financeiros em Decimal.

### 15.2 Integração

PostgreSQL/Supabase; candles; autenticação; isolamento entre usuários; ordem simulada; posição; backtest; kill switch.

### 15.3 Cenários de segurança

- usuário A não acessa conta do usuário B;
- cliente não consegue enviar ordem real;
- ausência de credenciais não permite iniciar integração privada;
- dados inválidos bloqueiam operações;
- duplicação de evento não duplica ordem;
- reinício do worker não duplica execução;
- falha no banco não gera estado financeiro parcial.

### 15.4 Critérios de qualidade

Lint sem erros; type checking sem erros críticos; testes passando; migrations aplicáveis; README reproduzível; nenhuma credencial no repositório; paper trading desligado até configuração explícita.

---

## 16. Execução local e desenvolvimento

Comandos padronizados no Makefile (`install`, `dev`, `test`, `lint`, `migrate`, `seed`, `down`). Em Windows sem GNU Make, usar scripts equivalentes em `scripts/`.

O `docker-compose.yml` deve subir os serviços locais necessários. Se utilizar Supabase Cloud, documentar as variáveis e migrações.

O README deve explicar pré-requisitos, instalação, `.env`, backend, frontend, Supabase, migrações, testes, paper trading e troubleshooting.

---

## 17. Roadmap por fases

### Fase 0 — Inspeção e planejamento

Inspecionar repositório; identificar arquivos; confirmar ambiente; propor plano; não alterar código ainda.  
**Aceite:** diagnóstico e plano aprovados.

### Fase 1 — Fundação

Monorepo; FastAPI; React; configuração; lint; testes; health check; documentação inicial.  
**Aceite:** frontend e backend iniciam localmente; health check responde.

### Fase 2 — Supabase

Schema; migrações; autenticação; RLS; seeds; testes de isolamento.  
**Aceite:** usuário autenticado acessa somente seus dados.

### Fase 3 — Market data

Adapter público modular; candles BTC/USDT e ETH/USDT; normalização; validação; persistência; status.  
**Aceite:** candles consultáveis e sem duplicidade.

### Fase 4 — Indicadores e estratégia

EMA, RSI, ATR, volume; Trend Momentum v1; sinais explicáveis; versionamento.  
**Aceite:** resultados determinísticos e cobertos por testes.

### Fase 5 — Backtesting

Engine; taxas; slippage; métricas; relatório reproduzível; regimes de mercado.  
**Aceite:** backtest sem look-ahead e com custos considerados.

### Fase 6 — Paper trading

Paper broker; carteira; ordens; posições; ledger; limites; kill switch; worker resiliente.  
**Aceite:** simulação contínua, reiniciável e sem duplicidade.

### Fase 7 — Dashboard

Páginas; gráficos; histórico; risco; explicação de sinais.  
**Aceite:** usuário acompanha todo o estado do simulador.

### Fase 8 — Validação prolongada

Paper em diferentes condições; comparação com backtest; revisão; limitações.  
**Aceite:** evidências documentadas. Sem aprovação automática para dinheiro real.

### Fase futura — Integração real

Não implementar nesta entrega. Exigiria análise regulatória, segurança, docs oficiais, permissões mínimas, limites, reconciliação, aprovação explícita e ambiente de demonstração quando disponível.

---

## 18. Definição de pronto do MVP

O MVP estará pronto quando:

- [ ] usuário consegue autenticar;
- [ ] sistema coleta candles BTC/USDT e ETH/USDT;
- [ ] dados inválidos ou atrasados bloqueiam sinais;
- [ ] indicadores são calculados corretamente;
- [ ] estratégia gera sinais reproduzíveis;
- [ ] backtest considera taxas e slippage;
- [ ] paper broker executa ordens simuladas;
- [ ] saldo, posição e ledger permanecem consistentes;
- [ ] limites de risco funcionam;
- [ ] kill switch impede novas entradas;
- [ ] dashboard mostra status, posições e desempenho;
- [ ] logs e auditoria explicam cada decisão;
- [ ] testes e documentação estão atualizados;
- [ ] nenhuma ordem real pode ser enviada.

---

## 19. Decisões técnicas ainda abertas / aprovadas

| Tema | Status |
|------|--------|
| Provedor de dados | Aprovado: adapter modular; candidato inicial Binance public (validar docs oficiais na Fase 3) |
| Supabase Cloud ou local | Aprovado: Cloud no início |
| Biblioteca de gráficos | Aprovado: lightweight-charts |
| Indicadores | Aprovado: implementação própria (float + testes); Decimal no financeiro |
| Worker | Aprovado: processo Python separado; polling no MVP |
| Notificações | Pendente (fase posterior) |

Não escolher serviços pagos sem informar custos e alternativas gratuitas.

---

## 20. Prompt inicial para colar no Cursor

Leia integralmente o arquivo `PROJECT_SPEC.md`.

Primeiro, inspecione o repositório atual e identifique estrutura, linguagens, funcionalidades, dependências, banco, testes e riscos. Não faça alterações ainda. Compare com a especificação e produza um plano por fases. Aguarde aprovação antes da Fase 1. Respeite paper trading exclusivo.

---

## 21. Plano detalhado da primeira entrega — Backtesting + Paper Trading (BTC/ETH)

Esta seção detalha a primeira entrega funcional do projeto. Ela complementa o roadmap da seção 17 e deve ser usada pelo Cursor como escopo de implementação inicial do motor de estratégia, backtesting e paper trading.

### 21.1 Objetivo da primeira entrega

Entregar um sistema local capaz de:

1. carregar dados históricos de BTC/USDT e ETH/USDT;
2. validar e normalizar os candles;
3. calcular indicadores técnicos;
4. executar a estratégia Trend Momentum v1 sobre dados históricos;
5. simular entradas, saídas, taxas e slippage;
6. gerar métricas e relatório de backtest;
7. executar a mesma estratégia em paper trading com dados novos;
8. manter saldo, posições, ordens e ledger consistentes;
9. explicar por que cada operação foi aberta, mantida, bloqueada ou encerrada.

Não faz parte desta entrega: enviar ordens reais, conectar chaves privadas de corretora, operar futuros, usar alavancagem ou disponibilizar recomendações a terceiros.

### 21.2 Escopo funcional

#### A. Ativos e mercado

- Símbolos iniciais: BTC/USDT e ETH/USDT.
- Mercado: Spot.
- Timeframes iniciais: 5m e 1h.
- Posição comprada (long) apenas.
- Sem margem, empréstimo ou venda a descoberto.
- A conta simulada começa com saldo configurável em USDT.
- O valor inicial padrão deve ser configurável; usar 100 USDT apenas como valor de demonstração, sem exigir depósito real.

#### B. Estratégia inicial

Implementar Trend Momentum v1 conforme a seção 8 deste documento. Todos os parâmetros devem estar em configuração versionada, não espalhados pelo código.

A estratégia deve retornar um objeto de sinal contendo, no mínimo:

- símbolo;
- timeframe;
- timestamp do candle de referência;
- ação: BUY, HOLD, EXIT ou NO_TRADE;
- identificador e versão da estratégia;
- indicadores calculados;
- condições verdadeiras e falsas;
- explicação legível;
- preço de referência;
- stop proposto;
- alvo proposto;
- instante em que o sinal foi gerado.

A estratégia não pode enviar ordens. Ela apenas produz um sinal. O RiskEngine decide se o sinal pode ser aceito e o PaperBroker simula a execução.

#### C. Backtesting

O usuário deve conseguir selecionar:

- BTC/USDT ou ETH/USDT;
- timeframe;
- data inicial e final;
- versão da estratégia;
- saldo inicial;
- taxa;
- slippage;
- parâmetros permitidos.

O backtest deve:

1. carregar candles ordenados cronologicamente;
2. verificar lacunas e dados duplicados;
3. calcular indicadores sem utilizar dados futuros;
4. avaliar sinais somente no momento permitido pela estratégia;
5. simular a execução no próximo preço disponível após o sinal, aplicando slippage;
6. debitar taxas;
7. aplicar regras de stop e alvo;
8. atualizar saldo e posição;
9. registrar todas as operações;
10. calcular métricas;
11. salvar a configuração completa para reprodução.

#### D. Paper trading contínuo

O paper trading deve usar o mesmo código de estratégia, risco, sizing e execução do backtest, evitando duas implementações divergentes.

O worker deve:

- buscar ou receber candles novos;
- processar somente candles fechados para a estratégia inicial;
- evitar processar o mesmo candle duas vezes;
- verificar estado da conta e kill switch;
- avaliar sinais;
- validar limites de risco;
- simular ordens;
- atualizar posição e ledger em transação consistente;
- registrar erros e permitir retomada após reinício.

O worker não pode criar uma segunda ordem se receber novamente o mesmo evento. Usar chave de idempotência baseada em conta, estratégia, símbolo, timeframe, candle e ação.

### 21.3 Regras de execução simulada

#### Entrada

- Executar no primeiro preço simulado disponível após o candle que gerou o sinal, não no fechamento conhecido retrospectivamente.
- Aplicar slippage desfavorável à operação.
- Debitar taxa de negociação.
- Validar saldo, notional mínimo e precisão.
- Rejeitar a ordem se o stop calculado for inválido ou estiver do lado incorreto do preço.

#### Saída

Fechar a posição quando ocorrer uma condição de saída válida:

- stop-loss;
- take-profit;
- regra de saída da estratégia;
- limite de risco ou encerramento administrativo configurado.

Aplicar taxa e slippage também na saída.

#### Ambiguidade intrabar

Se, em um candle histórico, stop e take-profit forem ambos tocados e não houver dados de granularidade suficiente para determinar qual ocorreu primeiro, assumir o resultado conservador: stop primeiro. Registrar a ocorrência no relatório.

#### Ledger

Cada preenchimento gera lançamentos imutáveis. O saldo deve ser reconstruível a partir do saldo inicial e do ledger. Não atualizar saldo sem registrar o evento financeiro correspondente.

### 21.4 Parâmetros de simulação

Valores iniciais para testes, todos configuráveis:

| Parâmetro | Valor inicial de demonstração |
|-----------|------------------------------:|
| Saldo inicial | 100 USDT |
| Taxa por execução | 0,10% |
| Slippage | 5 bps |
| Risco máximo por operação | 0,5% do patrimônio |
| Perda diária máxima | 1% do patrimônio no início do dia |
| Exposição máxima total | 20% do patrimônio |
| Posições simultâneas | 2 |
| Posições por símbolo | 1 |
| Alavancagem | Desabilitada |
| Mercado | Spot |
| Modo | Paper |

Esses valores são parâmetros de engenharia para simulação, não uma recomendação de investimento nem uma garantia de segurança ou rentabilidade. Confirmar taxas reais e regras do provedor antes de qualquer integração futura.

### 21.5 Interface mínima desta entrega

Construir páginas ou seções:

#### Dashboard

- selo persistente PAPER TRADING — SEM DINHEIRO REAL;
- estado do worker;
- última atualização dos dados;
- saldo inicial;
- saldo disponível;
- patrimônio estimado;
- P&L realizado e não realizado;
- drawdown;
- posições abertas;
- alertas de risco.

#### Backtesting

- formulário de ativo, timeframe e período;
- parâmetros e custos;
- botão para iniciar backtest;
- estado da execução;
- resumo de métricas;
- curva de patrimônio;
- lista de operações;
- avisos sobre limitações dos dados.

#### Paper Trading

- iniciar e pausar o simulador;
- visualizar ordens e posições;
- visualizar decisões e seus motivos;
- visualizar taxas e slippage;
- botão de kill switch;
- reset da conta com confirmação explícita e preservação/auditoria do histórico anterior.

#### Estratégia

- nome e versão;
- parâmetros ativos;
- indicadores;
- critérios de entrada e saída;
- habilitada/desabilitada;
- histórico de versões.

### 21.6 Métricas e interpretação

Calcular, no mínimo:

- saldo inicial e final;
- lucro/prejuízo bruto;
- taxas totais;
- slippage estimado total;
- lucro/prejuízo líquido;
- retorno percentual;
- drawdown máximo;
- número de operações;
- operações vencedoras e perdedoras;
- taxa de acerto;
- ganho médio;
- perda média;
- payoff;
- fator de lucro;
- expectativa por operação;
- tempo médio em posição;
- exposição média.

Exibir aviso quando a amostra for pequena. Não classificar uma estratégia como validada com base em poucas operações ou apenas em um período favorável.

### 21.7 Testes de aceite da primeira entrega

A primeira entrega só será aceita se todos os itens abaixo forem demonstrados:

- [ ] BTC/USDT e ETH/USDT podem ser carregados sem misturar os ativos.
- [ ] Timeframes 5m e 1h são identificados e tratados separadamente.
- [ ] Candles duplicados são ignorados ou rejeitados de forma auditável.
- [ ] Candles incompletos não geram sinais quando a estratégia exige candle fechado.
- [ ] Indicadores têm testes com valores conhecidos.
- [ ] Estratégia gera o mesmo resultado com os mesmos dados e parâmetros.
- [ ] Backtest não utiliza informação futura.
- [ ] Execução ocorre após o sinal, com taxas e slippage.
- [ ] Caso stop e alvo sejam tocados no mesmo candle sem granularidade, aplica-se a regra conservadora documentada.
- [ ] Saldo, posição e ledger permanecem consistentes após cada ordem simulada.
- [ ] Evento repetido não gera ordem duplicada.
- [ ] Reiniciar o worker não duplica operações.
- [ ] Limites de risco bloqueiam entradas quando atingidos.
- [ ] Kill switch impede novas entradas.
- [ ] Falha ou atraso dos dados bloqueia novas entradas.
- [ ] Dashboard mostra claramente que o modo é simulado.
- [ ] Não existe caminho de código que envie ordens reais.
- [ ] Testes automatizados, lint e documentação passam.

### 21.8 Sequência de implementação recomendada

O Cursor deve implementar em pequenas entregas revisáveis:

**Entrega 1 — Base executável**

- estrutura backend;
- configuração;
- modelos de domínio;
- health check;
- testes;
- conexão com banco.

**Entrega 2 — Dados históricos**

- interface de provedor;
- adaptador de dados públicos;
- candles BTC/USDT e ETH/USDT;
- validação, normalização e persistência.

**Entrega 3 — Indicadores e sinais**

- EMA, RSI, ATR e volume;
- estratégia Trend Momentum v1;
- explicações estruturadas;
- testes determinísticos.

**Entrega 4 — Backtesting**

- motor cronológico;
- execução simulada;
- custos;
- métricas e relatório.

**Entrega 5 — Paper broker**

- conta;
- saldo;
- ordens;
- posições;
- ledger;
- idempotência;
- gestão de risco e kill switch.

**Entrega 6 — Dashboard**

- mercado;
- backtests;
- paper trading;
- risco;
- histórico e auditoria.

**Entrega 7 — Validação**

- testes integrados;
- cenários de falha;
- comparação entre backtest e paper trading;
- documentação de limitações.

Ao concluir cada entrega, o Cursor deve informar:

1. arquivos criados e alterados;
2. decisões técnicas tomadas;
3. comandos executados;
4. testes executados e resultados;
5. limitações conhecidas;
6. riscos ou pendências;
7. próxima entrega sugerida.

Não avançar para a próxima entrega sem revisão do usuário.

### 21.9 Prompt específico para iniciar a primeira entrega

Depois de aprovar o diagnóstico do repositório e o plano geral, usar:

> Implemente a primeira entrega do projeto conforme as seções 8, 9, 10, 11, 15, 17 e 21 de `PROJECT_SPEC.md`.
>
> O escopo é exclusivamente BTC/USDT e ETH/USDT em Spot simulado, com backtesting e paper trading. Comece pela base executável e avance somente até a entrega que eu autorizar.
>
> Reutilize a mesma estratégia, motor de risco, cálculo de posição e regras de execução no backtest e no paper trading.
>
> Não implemente integração de ordens reais, futuros, margem ou alavancagem. Não adicione chaves privadas de corretora. Mantenha `LIVE_TRADING_ENABLED=false`.
>
> Antes de alterar arquivos, mostre o plano da entrega. Depois implemente, rode testes, lint e type checking, e apresente os resultados e limitações. Não declare a estratégia lucrativa sem evidências fora da amostra e validação prolongada em paper trading.

---

## 22. Política de segurança operacional

Esta política prevalece sobre qualquer configuração de estratégia.

1. O modo inicial é sempre paper.
2. O sistema deve recusar inicialização se detectar configuração incompatível com o modo paper.
3. Não criar botão escondido, variável de ambiente ou endpoint que habilite execução real nesta versão.
4. O simulador não pode ser apresentado como corretora ou como fonte de lucro.
5. Não inserir credenciais reais em testes, fixtures ou screenshots.
6. Não compartilhar dados privados ou credenciais em logs.
7. Toda alteração de parâmetros de risco deve ser auditada.
8. O usuário deve conseguir interromper o worker e consultar o estado persistido.
9. Em inconsistência de saldo, posição ou ledger, pausar o simulador e exigir reconciliação.
10. A passagem futura para dinheiro real será um projeto separado, com revisão técnica, de segurança e regulatória.

---

*Fim do PROJECT_SPEC.md — Versão 1.0*
