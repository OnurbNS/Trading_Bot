import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App'
import { SIMULATION_BANNER_TEXT } from '../src/components/SimulationBanner'

describe('Dashboard inicial', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('exibe o selo PAPER TRADING — SEM DINHEIRO REAL', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          status: 'ok',
          service: 'trading-bot-backend',
          version: '0.1.0',
          app_env: 'development',
          app_mode: 'paper',
          trading_enabled: false,
          live_trading_enabled: false,
          simulation: SIMULATION_BANNER_TEXT,
          timestamp: new Date().toISOString(),
        }),
      }),
    )

    render(<App />)
    expect(screen.getByText(SIMULATION_BANNER_TEXT)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Trading Bot' })).toBeInTheDocument()
  })

  it('mostra erro quando a API está indisponível (network failure)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Failed to fetch')),
    )

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('Backend indisponível')).toBeInTheDocument()
    })
    expect(screen.getByText(/Failed to fetch/i)).toBeInTheDocument()
    expect(screen.getAllByText(SIMULATION_BANNER_TEXT).length).toBeGreaterThan(0)
  })

  it('mostra erro quando a API responde HTTP de erro', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({ error: 'unavailable' }),
      }),
    )

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('Backend indisponível')).toBeInTheDocument()
    })
    expect(screen.getByText(/Health check falhou: HTTP 503/i)).toBeInTheDocument()
  })
})
