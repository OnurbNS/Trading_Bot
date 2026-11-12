export type HealthResponse = {
  status: string
  service: string
  version: string
  app_env: string
  app_mode: string
  trading_enabled: boolean
  live_trading_enabled: boolean
  simulation: string
  timestamp: string
}
