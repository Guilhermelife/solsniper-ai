import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Download, Search } from 'lucide-react'
import { format } from 'date-fns'

const API_BASE = '/api'

export default function ClosedPositions() {
  const [search, setSearch] = useState('')
  
  const { data: posData, isLoading } = useQuery({
    queryKey: ['positions'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/positions`)).data
  })

  const closedPositions = posData?.positions?.filter((p: any) => p.status === 'CLOSED') || []
  
  const filtered = closedPositions.filter((p: any) => {
    if (!search) return true
    return p.symbol?.toLowerCase().includes(search.toLowerCase()) || 
           p.token_address?.toLowerCase().includes(search.toLowerCase())
  })

  const handleExport = () => {
    window.open(`${API_BASE}/analytics/export/positions`, '_blank')
  }

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold tracking-tight text-white">Trade History</h1>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-primary/20"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search symbol..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 bg-surface border border-slate-700/50 rounded-lg text-sm focus:outline-none focus:border-primary text-white w-48"
            />
          </div>
        </div>
      </div>

      <div className="flex-1 bg-surface border border-slate-700/50 rounded-xl overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium">Token</th>
                <th className="px-6 py-4 font-medium">Entry/Exit</th>
                <th className="px-6 py-4 font-medium">Highest Price</th>
                <th className="px-6 py-4 font-medium">Result</th>
                <th className="px-6 py-4 font-medium">Exit Reason</th>
                <th className="px-6 py-4 font-medium">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">Loading history...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-500">No closed trades yet.</td></tr>
              ) : (
                filtered.map((pos: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                      {format(new Date(pos.closed_at), 'yyyy-MM-dd HH:mm')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-200">{pos.symbol || 'Unknown'}</div>
                      <div className="text-xs text-slate-500 mt-1">Score: {pos.signal_score?.toFixed(0)}</div>
                      {pos.reentry_count > 0 && <div className="text-xs text-blue-400 mt-1">Re-Entry #{pos.reentry_count}</div>}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-slate-300 font-mono text-xs">In: ${Number(pos.entry_price).toFixed(8)}</div>
                      <div className="text-slate-300 font-mono text-xs mt-1">Out: ${Number(pos.exit_price).toFixed(8)}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-slate-300 font-mono text-xs">High: ${Number(pos.highest_price || pos.entry_price).toFixed(8)}</div>
                      <div className="text-success font-mono text-xs mt-1">Max ROI: {pos.max_roi ? `+${pos.max_roi.toFixed(1)}%` : '-'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`font-bold ${pos.is_win ? 'text-success' : 'text-danger'}`}>
                        {pos.is_win ? 'WIN' : 'LOSS'}
                        <div className="text-xs font-normal opacity-80 mt-0.5">
                          {pos.profit_loss >= 0 ? '+' : ''}${pos.profit_loss.toFixed(2)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-300 text-xs">
                      {pos.exit_reason || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {pos.holding_time?.toFixed(1)} mins
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
