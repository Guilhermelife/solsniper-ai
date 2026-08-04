import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Search } from 'lucide-react'
import { format } from 'date-fns'

const API_BASE = '/api'

export default function Signals() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('ALL')
  
  const { data, isLoading } = useQuery({
    queryKey: ['signals'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/signals`)).data
  })

  const signals = data?.signals || []
  
  const filtered = signals.filter((s: any) => {
    if (filter !== 'ALL' && s.decision !== filter) return false
    if (!search) return true
    return s.symbol?.toLowerCase().includes(search.toLowerCase()) || 
           s.token_address?.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold tracking-tight text-white">Signals History</h1>
        
        <div className="flex items-center gap-3">
          <select 
            value={filter} 
            onChange={e => setFilter(e.target.value)}
            className="bg-surface border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
          >
            <option value="ALL">All Signals</option>
            <option value="BUY_SIGNAL">BUY_SIGNAL</option>
            <option value="WATCH">WATCH</option>
            <option value="IGNORE">IGNORE</option>
          </select>
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
                <th className="px-6 py-4 font-medium">Decision</th>
                <th className="px-6 py-4 font-medium">AI Score</th>
                <th className="px-6 py-4 font-medium">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoading ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">Loading signals...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-500">No signals found.</td></tr>
              ) : (
                filtered.map((sig: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                      {format(new Date(sig.created_at), 'yyyy-MM-dd HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-200">{sig.symbol || 'Unknown'}</div>
                      <div className="text-xs text-slate-500 font-mono mt-1 w-24 truncate">
                        {sig.token_address}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        sig.decision === 'BUY_SIGNAL' ? 'bg-success/10 text-success border border-success/20' : 
                        sig.decision === 'WATCH' ? 'bg-warning/10 text-warning border border-warning/20' : 
                        'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {sig.decision}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`font-bold ${sig.ai_score >= 80 ? 'text-success' : sig.ai_score >= 50 ? 'text-warning' : 'text-danger'}`}>
                        {sig.ai_score ? sig.ai_score.toFixed(1) : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400 max-w-md truncate" title={sig.reason}>
                      {sig.reason}
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
