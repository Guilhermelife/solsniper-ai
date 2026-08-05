import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Activity, Zap, Clock, AlertTriangle } from 'lucide-react'

const API_BASE = '/api'

export default function LiveSignals() {
  const { data: rawData, isLoading, error } = useQuery({
    queryKey: ['live-signals'],
    queryFn: async () => {
      const res = await axios.get(`${API_BASE}/market/live-signals`)
      return res.data
    },
    refetchInterval: 3000
  })

  const signals = rawData?.signals || []

  // Helpers
  const formatCurrency = (val: number) => {
    if (!val) return '$0.00'
    if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`
    if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`
    if (val >= 1e3) return `$${(val / 1e3).toFixed(2)}K`
    if (val < 0.01) return `$${val.toPrecision(3)}`
    return `$${val.toFixed(2)}`
  }

  const formatAge = (mins: number) => {
    if (!mins) return 'Unknown'
    if (mins < 60) return `${Math.floor(mins)}m`
    if (mins < 1440) return `${Math.floor(mins / 60)}h ${Math.floor(mins % 60)}m`
    return `${Math.floor(mins / 1440)}d`
  }

  const getDecisionBadge = (decision: string) => {
    switch(decision) {
      case 'BUY_SIGNAL':
        return <span className="px-2 py-1 rounded bg-success/20 text-success text-xs font-bold whitespace-nowrap border border-success/30 animate-pulse">🚀 BUY NOW</span>
      case 'WATCH':
        return <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs font-bold whitespace-nowrap border border-primary/30">👀 WATCH</span>
      case 'IGNORE':
        return <span className="px-2 py-1 rounded bg-slate-800 text-slate-400 text-xs font-bold whitespace-nowrap border border-slate-700">IGNORE</span>
      default:
        return <span className="px-2 py-1 rounded bg-slate-800 text-slate-400 text-xs font-bold whitespace-nowrap">{decision}</span>
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success'
    if (score >= 60) return 'text-warning'
    return 'text-danger'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-primary" />
            Live Trading Radar
          </h1>
          <p className="text-slate-400 text-sm mt-1">Real-time analysis output directly from the AI brain (bypassing database latency).</p>
        </div>
        
        <div className="flex items-center gap-2 text-xs font-medium bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="text-slate-300">Live Sync</span>
        </div>
      </div>

      {error ? (
        <div className="bg-danger/10 border border-danger/20 rounded-xl p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-danger mx-auto mb-2" />
          <h3 className="text-danger font-semibold">Radar Offline</h3>
          <p className="text-danger/80 text-sm mt-1">Could not connect to the real-time cache.</p>
        </div>
      ) : (
        <div className="bg-surface border border-slate-700/50 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-800/50 border-b border-slate-700/50">
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Token</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">Action</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Priority</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">AI Score</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Freshness</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Price</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">M.Cap / Liq</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Volume 24h</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Age</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {isLoading && signals.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-slate-500">
                      <Zap className="w-6 h-6 mx-auto mb-2 opacity-50 animate-pulse" />
                      Scanning frequencies...
                    </td>
                  </tr>
                ) : signals.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-slate-500">
                      No active targets in radar range.
                    </td>
                  </tr>
                ) : (
                  signals.map((result: any, idx: number) => {
                    const token = result.token || {}
                    return (
                      <tr key={token.address || idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-white overflow-hidden">
                              {token.image ? <img src={token.image} alt="logo" className="w-full h-full object-cover" /> : token.symbol?.[0]}
                            </div>
                            <div>
                              <div className="font-bold text-white flex items-center gap-2">
                                {token.symbol || '???'}
                              </div>
                              <div className="text-xs text-slate-500 truncate max-w-[120px]">{token.address}</div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-center">
                          {getDecisionBadge(result.decision)}
                        </td>
                        <td className="p-4 text-right">
                          <div className={`font-bold text-lg ${getScoreColor(result.priority_score)}`}>
                            {result.priority_score?.toFixed(1) || '0.0'}
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-white font-medium">{result.ai_score?.toFixed(1) || '0.0'}</div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-slate-300 font-mono text-sm">{result.freshness_score?.toFixed(1) || '0.0'}</div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-white font-medium">{formatCurrency(token.price_usd)}</div>
                          <div className={`text-xs ${token.price_change_5m >= 0 ? 'text-success' : 'text-danger'}`}>
                            {token.price_change_5m >= 0 ? '+' : ''}{token.price_change_5m?.toFixed(2) || 0}% (5m)
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-slate-300 font-medium">{formatCurrency(token.market_cap)}</div>
                          <div className="text-xs text-slate-500">Liq: {formatCurrency(token.liquidity)}</div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-slate-300 font-medium">{formatCurrency(token.volume_24h)}</div>
                        </td>
                        <td className="p-4 text-right">
                          <div className="text-slate-400 font-mono text-sm flex items-center justify-end gap-1">
                            <Clock className="w-3 h-3" />
                            {formatAge(token.age_minutes)}
                          </div>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
