import type { HealthResponse } from '../types/health'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/v1/health`)
  if (!response.ok) {
    throw new Error(`Health check falhou: HTTP ${response.status}`)
  }
  return (await response.json()) as HealthResponse
}
