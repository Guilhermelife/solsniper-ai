import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Search, ExternalLink, ChevronLeft, ChevronRight, Info } from 'lucide-react'
import { format } from 'date-fns'

const API_BASE = '/api'
const ITEMS_PER_PAGE = 20

export default function Signals() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('ALL')
  const [currentPage, setCurrentPage] = useState(1)
  
  const { data, isLoading } = useQuery({
    queryKey: ['signals'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/signals`)).data,
    refetchInterval: 10000 // auto-refresh every 10s
  })

  const signals = data?.signals || []
  
  const filtered = useMemo(() => {
    return signals.filter((s: any) => {
      if (filter !== 'ALL' && s.decision !== filter) return false
      if (!search) return true
      return s.symbol?.toLowerCase().includes(search.toLowerCase()) || 
             s.token_address?.toLowerCase().includes(search.toLowerCase())
    })
  }, [signals, filter, search])

  // Reset page when filter/search changes
  useMemo(() => {
    setCurrentPage(1)
  }, [filter, search])

  // Pagination logic
  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE))
  const paginatedSignals = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE
    return filtered.slice(start, start + ITEMS_PER_PAGE)
  }, [filtered, currentPage])

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
                <th className="px-6 py-4 font-medium">Date & Price</th>
                <th className="px-6 py-4 font-medium">Token</th>
                <th className="px-6 py-4 font-medium">Decision</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">AI Score</th>
                <th className="px-6 py-4 font-medium">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoading ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">Loading signals...</td></tr>
              ) : paginatedSignals.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-500">No signals found.</td></tr>
              ) : (
                paginatedSignals.map((sig: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                      <div>{format(new Date(sig.created_at), 'yyyy-MM-dd HH:mm:ss')}</div>
                      {sig.price_usd > 0 && (
                        <div className="text-xs text-slate-500 mt-1">
                          Entry: ${sig.price_usd.toFixed(6)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-200">{sig.symbol || 'Unknown'}</div>
                      <a
                        href={`https://solscan.io/token/${sig.token_address}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-slate-500 font-mono mt-1 flex items-center gap-1 hover:text-primary transition-colors group"
                        title="View on Solscan"
                      >
                        {sig.token_address.slice(0, 8)}...{sig.token_address.slice(-6)}
                        <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </a>
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
                      {sig.decision === 'BUY_SIGNAL' ? (
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          ['OPEN', 'CLOSED_WIN'].includes(sig.confirmation_status) ? 'bg-success/10 text-success border border-success/20' : 
                          ['REJECTED', 'CLOSED_LOSS', 'EXPIRED'].includes(sig.confirmation_status) ? 'bg-danger/10 text-danger border border-danger/20' : 
                          sig.confirmation_status === 'BUYING' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse' :
                          'bg-warning/10 text-warning border border-warning/20'
                        }`}>
                          {sig.confirmation_status || 'DETECTED'}
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className={`font-bold ${sig.ai_score >= 80 ? 'text-success' : sig.ai_score >= 50 ? 'text-warning' : 'text-danger'}`}>
                        {sig.ai_score ? sig.ai_score.toFixed(1) : '-'}
                      </div>
                      {(sig.priority_score > 0 || sig.freshness_score > 0) && (
                        <div className="text-xs text-slate-500 mt-1">
                          Pri: {sig.priority_score?.toFixed(1) || 0}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-400 max-w-xs group relative">
                      <div className="truncate flex items-center gap-2">
                        <span>{sig.reason}</span>
                        {sig.reason?.length > 40 && (
                          <div className="relative inline-block cursor-help group/tooltip">
                            <Info className="w-4 h-4 text-slate-500 hover:text-slate-300" />
                            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:block w-64 p-2 bg-slate-800 text-slate-200 text-xs rounded-lg shadow-xl border border-slate-700 z-10 whitespace-normal">
                              {sig.reason}
                            </div>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Controls */}
        <div className="border-t border-slate-700/50 p-4 flex items-center justify-between text-sm text-slate-400">
          <div>
            Showing <span className="text-slate-200 font-medium">{filtered.length === 0 ? 0 : (currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to <span className="text-slate-200 font-medium">{Math.min(currentPage * ITEMS_PER_PAGE, filtered.length)}</span> of <span className="text-slate-200 font-medium">{filtered.length}</span> results
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent transition-colors text-slate-300"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="px-3 py-1 bg-slate-800/50 rounded-md font-medium text-slate-300">
              Page {currentPage} of {totalPages}
            </div>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1 rounded hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent transition-colors text-slate-300"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
