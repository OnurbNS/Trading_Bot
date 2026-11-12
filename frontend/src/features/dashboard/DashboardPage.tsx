import { useEffect, useState } from 'react'
import { fetchHealth } from '../../lib/api'
import type { HealthResponse } from '../../types/health'

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ok'; data: HealthResponse }
  | { kind: 'error'; message: string }

export function DashboardPage() {
  const [state, setState] = useState<LoadState>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false
    fetchHealth()
      .then((data) => {
        if (!cancelled) setState({ kind: 'ok', data })
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : 'Falha ao consultar API'
          setState({ kind: 'error', message })
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="page">
      <section className="hero">
        <p className="meta">Robô pessoal · BTC/USDT e ETH/USDT · Spot simulado</p>
        <h1 className="brand">Trading Bot</h1>
        <p className="lede">
          Fundação da Fase 1: API local, health check e dashboard inicial. Nenhuma ordem real
          pode ser enviada nesta versão. Estratégia, backtest e paper trading virão nas fases
          autorizadas.
        </p>
      </section>

      <section className="panel-grid" aria-label="Estado do sistema">
        <article className="panel">
          <h2>Modo operacional</h2>
          <div className="status-row">
            <span className="status-dot is-ok" aria-hidden="true" />
            <strong>Paper · simulação</strong>
          </div>
          <p className="meta">Live trading bloqueado tecnicamente. Sem alavancagem ou futuros.</p>
        </article>

        <article className="panel">
          <h2>API / health</h2>
          {state.kind === 'loading' && (
            <div className="status-row">
              <span className="status-dot" aria-hidden="true" />
              <span>Consultando backend…</span>
            </div>
          )}
          {state.kind === 'ok' && (
            <>
              <div className="status-row">
                <span className="status-dot is-ok" aria-hidden="true" />
                <strong>Online · {state.data.status}</strong>
              </div>
              <p className="meta">
                Ambiente: {state.data.app_env} · modo: {state.data.app_mode}
                <br />
                Live: {String(state.data.live_trading_enabled)} · trading_enabled:{' '}
                {String(state.data.trading_enabled)}
                <br />
                Atualizado: {new Date(state.data.timestamp).toLocaleString('pt-BR')}
              </p>
            </>
          )}
          {state.kind === 'error' && (
            <>
              <div className="status-row">
                <span className="status-dot is-bad" aria-hidden="true" />
                <strong>Backend indisponível</strong>
              </div>
              <p className="meta">
                {state.message}. Inicie a API em <code>127.0.0.1:8000</code>.
              </p>
            </>
          )}
        </article>

        <article className="panel nav-preview">
          <h2>Próximas seções</h2>
          <ul>
            <li>Mercado, estratégias, backtests</li>
            <li>Paper trading, risco, configurações</li>
            <li>Estrutura de pastas já reservada em <code>src/features</code></li>
          </ul>
        </article>
      </section>
    </main>
  )
}
