import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { AlertCircle, CheckCircle2, TrendingUp, ShieldAlert, Target } from 'lucide-react'

const API_BASE = '/api'

export default function StrategyReadiness() {
  const { data, isLoading } = useQuery({
    queryKey: ['readiness'],
    queryFn: async () => (await axios.get(`${API_BASE}/readiness`)).data
  })

  if (isLoading) {
    return <div className="p-6 text-slate-400">Loading readiness report...</div>
  }

  if (data?.message) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center">
        <ShieldAlert className="w-16 h-16 text-slate-600 mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Insufficient Data</h2>
        <p className="text-slate-400 max-w-md">{data.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white">Strategy Readiness</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core Status */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-surface border border-slate-700/50 rounded-xl p-6 text-center">
            {data?.is_profitable ? (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-success/10 text-success mb-4">
                <CheckCircle2 className="w-8 h-8" />
              </div>
            ) : (
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-danger/10 text-danger mb-4">
                <AlertCircle className="w-8 h-8" />
              </div>
            )}
            <h2 className="text-xl font-bold text-white mb-1">
              {data?.is_profitable ? 'Strategy is Profitable' : 'Strategy is Unprofitable'}
            </h2>
            <div className={`text-2xl font-black ${data?.is_profitable ? 'text-success' : 'text-danger'} mb-4`}>
              {data?.net_profit_usd >= 0 ? '+' : ''}${data?.net_profit_usd?.toFixed(2)} Net
            </div>
            <p className="text-sm text-slate-400">
              Based on {data?.total_trades_analyzed} simulated trades.
            </p>
          </div>
        </div>

        {/* Filter Analysis & Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-primary" />
              Recommendations
            </h3>
            {data?.recommendations?.length > 0 ? (
              <ul className="space-y-3">
                {data.recommendations.map((rec: string, i: number) => (
                  <li key={i} className="flex items-start gap-3 bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
                    <TrendingUp className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                    <span className="text-slate-300 text-sm leading-relaxed">{rec}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-4 bg-success/10 border border-success/20 rounded-lg text-success text-sm flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                No critical adjustments recommended at this time.
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Best Performing Market Cap</h4>
              <div className="text-xl font-bold text-success">{data?.filter_analysis?.best_contributor}</div>
              <div className="text-xs text-slate-500 mt-1">Highest profit contribution</div>
            </div>
            <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Worst Performing Market Cap</h4>
              <div className="text-xl font-bold text-danger">{data?.filter_analysis?.worst_contributor}</div>
              <div className="text-xs text-slate-500 mt-1">Largest profit drag</div>
            </div>
          </div>
          
          {/* Signal Validation */}
          <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-lg font-semibold text-white mb-4">Untraded Signal Validation</h3>
            <p className="text-sm text-slate-400 mb-4">
              Performance of {data?.signal_validation?.total_untraded} BUY signals that were skipped (due to wallet constraints).
            </p>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                <div className="text-2xl font-bold text-white mb-1">{data?.signal_validation?.hit_10_pct_1h}</div>
                <div className="text-xs text-slate-400">Hit +10% in 1h</div>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                <div className="text-2xl font-bold text-white mb-1">{data?.signal_validation?.hit_50_pct_6h}</div>
                <div className="text-xs text-slate-400">Hit +50% in 6h</div>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                <div className="text-2xl font-bold text-white mb-1">{data?.signal_validation?.hit_100_pct_24h}</div>
                <div className="text-xs text-slate-400">Hit +100% in 24h</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
