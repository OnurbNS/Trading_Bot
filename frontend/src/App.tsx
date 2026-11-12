import './App.css'
import { SimulationBanner } from './components/SimulationBanner'
import { DashboardPage } from './features/dashboard/DashboardPage'

export default function App() {
  return (
    <div className="app-shell">
      <SimulationBanner />
      <DashboardPage />
    </div>
  )
}
