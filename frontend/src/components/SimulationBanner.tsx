const BANNER = 'PAPER TRADING — SEM DINHEIRO REAL'

export function SimulationBanner() {
  return (
    <aside className="simulation-banner" role="status" aria-live="polite">
      <span className="simulation-banner__icon" aria-hidden="true" />
      <p className="simulation-banner__text">{BANNER}</p>
    </aside>
  )
}

export const SIMULATION_BANNER_TEXT = BANNER
