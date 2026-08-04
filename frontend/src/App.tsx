import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'

import Overview from './pages/Overview'
import LiveMarket from './pages/LiveMarket'
import Signals from './pages/Signals'
import OpenPositions from './pages/OpenPositions'
import ClosedPositions from './pages/ClosedPositions'
import Analytics from './pages/Analytics'
import Readiness from './pages/StrategyReadiness'
import Configuration from './pages/Configuration'
import Logs from './pages/Logs'
import System from './pages/System'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/overview" replace />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/market" element={<LiveMarket />} />
          <Route path="/signals" element={<Signals />} />
          <Route path="/positions/open" element={<OpenPositions />} />
          <Route path="/positions/closed" element={<ClosedPositions />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/readiness" element={<Readiness />} />
          <Route path="/config" element={<Configuration />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/system" element={<System />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
