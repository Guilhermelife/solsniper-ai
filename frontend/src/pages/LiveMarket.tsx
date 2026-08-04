import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Search, Copy, CheckCircle2 } from 'lucide-react'
import { TokenDetailModal } from '../components/TokenDetailModal'

const API_BASE = '/api'

function formatAge(minutes: number) {
  if (!minutes || minutes < 0) return '-';
  if (minutes < 60) return `${Math.floor(minutes)}m`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ${Math.floor(minutes % 60)}m`;
  return `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h`;
}

export default function LiveMarket() {
  const [search, setSearch] = useState('')
  const [copied, setCopied] = useState<string | null>(null)
  const [selectedToken, setSelectedToken] = useState<string | null>(null)
  
  const { data, isLoading } = useQuery({
    queryKey: ['market_latest'],
    queryFn: async () => (await axios.get(`${API_BASE}/market/latest`)).data,
    refetchInterval: 10000 // refresh every 10 seconds
  })

  const tokens = data?.tokens || []
  
  const filteredTokens = tokens.filter((t: any) => 
    t.symbol?.toLowerCase().includes(search.toLowerCase()) || 
    t.address?.toLowerCase().includes(search.toLowerCase())
  )

  const handleCopy = (e: React.MouseEvent, address: string) => {
    e.stopPropagation()
    navigator.clipboard.writeText(address)
    setCopied(address)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold tracking-tight text-white">Live Market</h1>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search symbol or address..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-surface border border-slate-700/50 rounded-lg text-sm focus:outline-none focus:border-primary transition-colors text-white w-64"
          />
        </div>
      </div>

      <div className="flex-1 bg-surface border border-slate-700/50 rounded-xl overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-medium">Token</th>
                <th className="px-6 py-4 font-medium">Price</th>
                <th className="px-6 py-4 font-medium">Market Cap</th>
                <th className="px-6 py-4 font-medium">Liquidity</th>
                <th className="px-6 py-4 font-medium">Vol 24h</th>
                <th className="px-6 py-4 font-medium">Age</th>
                <th className="px-6 py-4 font-medium">DEX</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    <div className="animate-pulse flex flex-col items-center">
                      <div className="h-4 w-32 bg-slate-700 rounded mb-4"></div>
                      <div className="h-4 w-48 bg-slate-700 rounded"></div>
                    </div>
                  </td>
                </tr>
              ) : filteredTokens.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No tokens found. Waiting for next scan cycle...
                  </td>
                </tr>
              ) : (
                filteredTokens.map((token: any, i: number) => (
                  <tr 
                    key={i} 
                    className="hover:bg-slate-800/30 transition-colors cursor-pointer"
                    onClick={() => setSelectedToken(token.address)}
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-200">{token.symbol || 'Unknown'}</div>
                      <div 
                        className="text-xs text-slate-500 font-mono mt-1 flex items-center gap-2 hover:text-slate-300 transition-colors"
                        onClick={(e) => handleCopy(e, token.address)}
                        title={token.address}
                      >
                        {token.address ? `${token.address.slice(0, 4)}...${token.address.slice(-4)}` : ''}
                        {copied === token.address ? (
                          <CheckCircle2 className="w-3 h-3 text-success" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-300 font-mono">
                      ${Number(token.price_usd || 0).toFixed(8)}
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      ${Number(token.market_cap || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      ${Number(token.liquidity || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      ${Number(token.volume_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {formatAge(token.age_minutes)}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {token.dex || '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedToken && (
        <TokenDetailModal 
          address={selectedToken} 
          onClose={() => setSelectedToken(null)} 
        />
      )}
    </div>
  )
}
