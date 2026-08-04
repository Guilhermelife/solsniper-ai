import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'

const API_BASE = '/api'

export default function OpenPositions() {
  const { data: posData, isLoading: isLoadingPos } = useQuery({
    queryKey: ['positions'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/positions`)).data
  })

  const { data: marketData } = useQuery({
    queryKey: ['market_latest'],
    queryFn: async () => (await axios.get(`${API_BASE}/market/latest`)).data
  })

  const openPositions = posData?.positions?.filter((p: any) => p.status === 'OPEN') || []
  const tokens = marketData?.tokens || []

  // Helper to find live price
  const getLivePrice = (address: string) => {
    const token = tokens.find((t: any) => t.address === address)
    return token ? token.price_usd : null
  }

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white">Open Positions</h1>
      </div>

      <div className="flex-1 bg-surface border border-slate-700/50 rounded-xl overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-medium">Token</th>
                <th className="px-6 py-4 font-medium">Entry Price</th>
                <th className="px-6 py-4 font-medium">Current Price</th>
                <th className="px-6 py-4 font-medium">Amount</th>
                <th className="px-6 py-4 font-medium">Live PnL</th>
                <th className="px-6 py-4 font-medium">Highest Price</th>
                <th className="px-6 py-4 font-medium">Trailing Stop</th>
                <th className="px-6 py-4 font-medium">Dist to Stop</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoadingPos ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">Loading positions...</td></tr>
              ) : openPositions.length === 0 ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No open positions right now.</td></tr>
              ) : (
                openPositions.map((pos: any, i: number) => {
                  const livePrice = getLivePrice(pos.token_address)
                  let pnlPct = 0
                  let pnlUsd = 0
                  let distToStop = 0
                  
                  if (livePrice && pos.entry_price) {
                    pnlPct = ((livePrice - pos.entry_price) / pos.entry_price) * 100
                    pnlUsd = (pnlPct / 100) * pos.amount_usd
                  }

                  if (livePrice && pos.trailing_stop_price) {
                     distToStop = ((livePrice - pos.trailing_stop_price) / pos.trailing_stop_price) * 100
                  }

                  return (
                    <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-200">{pos.symbol || 'Unknown'}</div>
                        <div className="text-xs text-slate-500 mt-1">
                          {format(new Date(pos.created_at), 'HH:mm:ss')}
                          {pos.reentry_count > 0 && <span className="ml-2 text-blue-400">Re-Entry #{pos.reentry_count}</span>}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-mono">
                        ${Number(pos.entry_price).toFixed(8)}
                      </td>
                      <td className="px-6 py-4 font-mono">
                        {livePrice ? (
                          <span className={livePrice > pos.entry_price ? 'text-success' : livePrice < pos.entry_price ? 'text-danger' : 'text-slate-300'}>
                            ${Number(livePrice).toFixed(8)}
                          </span>
                        ) : (
                          <span className="text-slate-500">Waiting for tick...</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-slate-300">
                        ${Number(pos.amount_usd).toFixed(2)}
                      </td>
                      <td className="px-6 py-4">
                        {livePrice ? (
                          <div className={`font-bold ${pnlPct >= 0 ? 'text-success' : 'text-danger'}`}>
                            {pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%
                            <div className="text-xs font-normal opacity-80 mt-0.5">
                              {pnlUsd >= 0 ? '+' : ''}${pnlUsd.toFixed(2)}
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-500">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-mono">
                        ${Number(pos.highest_price || pos.entry_price).toFixed(8)}
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-mono">
                        ${Number(pos.trailing_stop_price || 0).toFixed(8)}
                      </td>
                      <td className="px-6 py-4">
                         {livePrice ? (
                            <span className="text-slate-300 font-mono">
                              +{distToStop.toFixed(2)}%
                            </span>
                         ) : (
                            <span className="text-slate-500">-</span>
                         )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
